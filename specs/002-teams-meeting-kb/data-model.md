# Data Model: Teams Meeting Knowledge Base Agent

Generated: 2025-10-31
Branch: `002-teams-meeting-kb`

## Goals
Provide normalized, version‑stable entities for ingestion, processing (chunking, masking, embedding), indexing, retention enforcement, and search responses. Model must support:
- Idempotent ingestion & retries
- Partial artifact availability (transcript delayed)
- Feature flags disabling certain artifact types
- Retention windows (90d recordings, 365d textual artifacts)
- Security trimming via channel membership
- Masking sensitivity flags

## Conventions
- All IDs are opaque strings (UUID v4 unless otherwise stated)
- Date/time fields in UTC ISO 8601
- Hash fields: lowercase hex SHA256
- Optional fields omitted when not applicable

## Entities

### MeetingSeries
Represents recurring series metadata (single program channel scope for Phase 1).
Fields:
- id: string (seriesId)
- channelId: string
- teamId: string
- title: string
- createdAt: datetime
- active: boolean
- tags: map<string,string> (owner, costCenter)

### MeetingOccurrence
Single occurrence of meeting within the series.
Fields:
- id: string (occurrenceId)
- seriesId: string (FK MeetingSeries.id)
- startTime: datetime
- endTime: datetime
- harvestedAt: datetime? (set when harvest completes excluding transcript wait)
- transcriptStatus: enum { PENDING, AVAILABLE, TIMEOUT, DISABLED }
- recordingStatus: enum { NOT_REQUESTED, METADATA_ONLY, DISABLED }
- artifactCounts: object { chat:int, files:int, transcriptSegments:int }
- version: int (increment on re-harvest)
- orchestrationInstanceId: string (Durable instance)

### RawArtifact (Polymorphic Base)
Common metadata for any ingested artifact.
Fields:
- id: string
- occurrenceId: string (FK MeetingOccurrence.id)
- type: enum { CHAT_MESSAGE, FILE, TRANSCRIPT_SEGMENT, RECORDING_METADATA }
- sourceId: string (Graph/SharePoint identifier)
- createdTime: datetime (original timestamp)
- fetchedTime: datetime (ingestion timestamp)
- author: string? (AAD user id or display name if allowed)
- correlationIds: array<string> (meeting/recording correlation refs)
- piiFlags: array<enum { EMAIL, PHONE, ID }> (raw detection results)
- masked: boolean (true if masking applied to textual content)
- retentionClass: enum { SHORT, LONG } (SHORT=recordings 90d, LONG=text 365d)

Specializations:
- ChatMessageArtifact (extends RawArtifact)
  - replyToMessageId: string?
  - importance: enum { NORMAL, HIGH }?
  - mentions: array<object { userId:string, type:string }>
  - text: string (original raw text)
  - textMasked: string? (masked text if masking applied)

- FileArtifact (extends RawArtifact)
  - fileName: string
  - fileExtension: string
  - fileSizeBytes: int
  - driveItemId: string
  - sharepointPath: string
  - extractionPerformed: boolean
  - extractedText: string? (raw extracted text pre-chunking)
  - extractionError: string? (set if extraction failed)

- TranscriptSegmentArtifact (extends RawArtifact)
  - speaker: string?
  - startOffsetMs: int
  - endOffsetMs: int
  - segmentText: string
  - segmentTextMasked: string?

- RecordingMetadataArtifact (extends RawArtifact)
  - recordingStartTime: datetime
  - recordingEndTime: datetime?
  - downloadUrl: string?

### Chunk
Normalized unit for embedding + indexing.
Fields:
- id: string
- occurrenceId: string
- sourceArtifactId: string (FK RawArtifact.id)
- sequence: int (ordering within artifact)
- content: string (masked if masking applied)
- contentHash: string (SHA256(content + occurrenceId + sourceArtifactId))
- contentLength: int
- speaker: string? (for transcript segments)
- author: string? (for chat/file attribution)
- artifactType: enum (mirror RawArtifact.type)
- createdAt: datetime (chunk creation)
- embeddingModel: string
- embeddingVector: float[1536]? (nullable until embedding step succeeds)
- embeddingStatus: enum { PENDING, COMPLETE, ERROR }
- piiFlags: array<enum { EMAIL, PHONE, ID }>
- sensitivityFlags: array<enum { PII_PRESENT }> (aggregated)
- parentSpan: object { startOffset:int?, endOffset:int? } (for transcript/file paragraph splits)

### IndexDocument (Logical Projection)
Represents final document submitted to Azure AI Search.
Fields:
- id: string (mirrors Chunk.id)
- meetingSeriesId: string
- meetingDate: date (from occurrence.startTime)
- artifactType: enum
- speaker: string?
- author: string?
- content: string
- contentVector: float[1536]
- sourceRef: string (composition: occurrenceId:sourceArtifactId:sequence)
- sensitivityFlags: array<string>
- language: string? (ISO 639-1; detection phase later)
- createdAt: datetime

### PurgeLogEntry
Retention enforcement audit.
Fields:
- id: string
- timestamp: datetime
- action: enum { DELETE, DRY_RUN }
- targetType: enum { CHUNK, ARTIFACT }
- occurrenceId: string?
- artifactId: string?
- chunkId: string?
- reason: enum { RETENTION_EXPIRED }
- retentionClass: string

### HarvestExecution
Tracks orchestrator runs (may span retries).
Fields:
- id: string
- occurrenceId: string
- startedAt: datetime
- completedAt: datetime?
- status: enum { RUNNING, SUCCEEDED, PARTIAL, FAILED }
- errorCode: string?
- retries: int
- disabledArtifacts: array<enum { TRANSCRIPTS, RECORDINGS }> (feature flags snapshot)

### MembershipCacheEntry
### HarvestIdentity
Represents the non-interactive bot/application identity used for scheduled harvest.
Fields:
- id: string (identityId)
- appId: string (BOT_APP_ID)
- scopes: array<string>
- lastTokenIssue: datetime?
- tokenExpiry: datetime?
- enabled: boolean

Used for operational diagnostics only; not indexed in AI Search.
Used for security trimming queries.
Fields:
- id: string (channelId)
- retrievedAt: datetime
- memberIds: array<string>
- ttlSeconds: int

## Relationships
- MeetingSeries 1..* MeetingOccurrence
- MeetingOccurrence 1..* RawArtifact
- RawArtifact 1..* Chunk
- Chunk 1..1 IndexDocument
- MeetingOccurrence 1..* HarvestExecution
- MeetingOccurrence 1..* PurgeLogEntry (indirect via artifacts/chunks)

## State & Transitions
### TranscriptStatus
PENDING → AVAILABLE (transcript segments ingested) or TIMEOUT (24h) or DISABLED (feature flag).

### EmbeddingStatus
PENDING → COMPLETE (vector stored) or ERROR (retry queue) with maxRetries (configurable, default 3) then flagged for manual inspection.

### HarvestExecution.status
RUNNING → SUCCEEDED (all artifact types processed) → PARTIAL (some non-critical errors) → FAILED (critical error: e.g., Graph permission failure).

## Validation Rules
- Chunk.contentLength <= 5000 (guard against oversized index docs)
- RecordingMetadataArtifact.downloadUrl only stored if transcripts disabled OR explicit config `STORE_RECORDING_URL` true.
- Purge operation must not delete artifacts with status TIMEOUT < 24h grace after marking.
- EmbeddingVector length must match model dimension (1536) else ERROR.
- MembershipCacheEntry.ttlSeconds <= 3600.

## Indexing Constraints
- IndexDocument.id unique
- contentVector non-null only when embeddingStatus=COMPLETE
- Filterable fields: meetingSeriesId, meetingDate, artifactType, speaker, author, sensitivityFlags
- Sortable fields: meetingDate, createdAt
- Key field: id

## Security & Masking
- Masking pipeline populates textMasked/segmentTextMasked and sets masked=true on RawArtifact
- Chunk.content always masked version when masked=true
- sensitivityFlags derived from piiFlags > 0

## Retention Logic
- SHORT retentionClass purge after 90d (RecordingMetadataArtifact + associated chunks if created)
- LONG retentionClass purge after 365d (ChatMessageArtifact, FileArtifact, TranscriptSegmentArtifact & chunks)
- PurgeLogEntry recorded for each deletion (or DRY_RUN)

## Feature Flag Impact
- ENABLE_TRANSCRIPTS=false → no TranscriptSegmentArtifact creation; transcriptStatus=DISABLED
- ENABLE_RECORDINGS=false → recordingStatus=DISABLED; no RecordingMetadataArtifact

## Error Handling
- Each Activity returns standardized result object `{ status, errorCode?, retryable }`
- Orchestrator increments HarvestExecution.retries and routes retryable failures to delay queue.

## Open Questions (Deferred)
- Language detection & multi-language segmentation (Phase 2)
- Per-user ACL index field (not needed Phase 1)
- Summarization artifact entity (Phase 2 when summaries enabled)

## Rationale Summary
Model separates raw artifacts from chunks to allow re-chunking or re-embedding without re-fetching original Graph/SharePoint content. IndexDocument aligns 1:1 with Chunk for simplicity. PurgeLogEntry ensures auditability for retention compliance. Feature flags allow phased activation without schema changes.

## Next Steps
- Implement Pydantic models (mirroring these entities)
- Define hashing & validation helpers
- Create factories for orchestration activities
