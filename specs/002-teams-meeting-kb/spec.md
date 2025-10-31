# Feature Specification: Teams Meeting Knowledge Base Agent

**Feature Branch**: `002-teams-meeting-kb`  
**Created**: 2025-10-31  
**Status**: Draft  
**Input**: User description: "Create an AI agent that authenticates via Azure Bot Service credentials, ingests Microsoft Teams channel recurring meeting series content (recordings, transcripts, chat messages, file attachments), processes & analyzes meeting data, and builds an internal knowledge base organized with Teams-compatible structures (Channels, Tabs, SharePoint doc library, OneNote) using only Azure services for storage and retrieval. Enforce governance (security, retention, access control), incremental ingestion, semantic search, summarization, action item extraction, and Q&A over accumulated meeting knowledge. Provide Terraform-managed Azure infrastructure (Bot Service registration, Azure OpenAI / AI Foundry, Storage, Cognitive Search, Key Vault, Functions or App Service, Event Grid) while avoiding external non-Teams KB tools."

## User Scenarios & Testing *(mandatory)*

<!-- Guidance: User stories below are intentionally visible; do not comment them out. -->
### User Story 1A - Passive Channel Activation (Priority: P1)
For a designated program channel, the agent is always active across all chats (no manual enable step) and automatically treats every scheduled meeting occurrence in that channel as in-scope for ingestion.

**Why this priority**: Eliminates setup friction; simpler lifecycle for a single program of projects.

**Independent Test**: Create a new meeting occurrence in the designated channel; verify ingestion triggers post-meeting without any activation command.

**Acceptance Scenarios**:
1. **Given** a designated program channel **When** a meeting concludes **Then** ingestion workflow initiates automatically.
2. **Given** ad-hoc chat messages unrelated to a meeting **When** they occur **Then** they are ignored unless within a meeting time window (scope boundary).
3. **Given** channel reassignment (program ends) **When** deactivation flag is set **Then** subsequent meetings are not ingested.

---

### User Story 1B - Scheduled Recording & Transcript Harvest (Priority: P1)
After each meeting ends the system captures recording metadata and, on a configurable harvesting schedule (e.g., every 10 minutes until transcript appears or max window), ingests the transcript once Teams / Copilot makes it available.

**Why this priority**: Recordings and transcripts form the canonical narrative content.

**Independent Test**: End a meeting with recording and transcript; verify metadata appears in first scheduled harvest run and transcript text appears in a later scheduled harvest once available.

**Acceptance Scenarios**:
1. **Given** a completed meeting **When** first harvest run executes **Then** recording metadata is stored with meeting occurrence ID.
2. **Given** transcript delay **When** subsequent scheduled harvest runs until transcript availability **Then** transcript is ingested exactly once; no duplicate segments.
3. **Given** transcript never appears before max harvest window **When** window elapses **Then** warning status logged and surfaced in health metrics.
4. **Given** harvest schedule interval change **When** new interval configured **Then** future runs adhere to updated interval without overlapping prior timers.

---

### User Story 1C - Chat Message Ingestion (Priority: P1)
All chat messages (including replies / threads) posted during the meeting window are captured with authorship and temporal ordering.

**Why this priority**: Chat often contains decisions or shared context absent from transcript.

**Independent Test**: Post several threaded and unthreaded messages during a test meeting; verify ordering, authors, and thread IDs preserved.

**Acceptance Scenarios**:
1. **Given** threaded replies **When** ingestion runs **Then** parent-child relationships are retained.
2. **Given** deleted messages **When** ingestion executes **Then** deleted items are either excluded or marked as deleted (policy consistent across set).
3. **Given** large volume (>500 messages) **When** ingestion runs **Then** pagination / batching completes without data loss.

---

### User Story 1D - File Attachment Ingestion (Priority: P2)
Files shared in the meeting chat during the session are captured with metadata and (where supported) extracted text for indexing.

**Why this priority**: Attached documents contain key context not present in transcript/chat.

**Independent Test**: Share a supported text-based file and an unsupported binary; verify text extracted for supported file and fallback metadata only for unsupported.

**Acceptance Scenarios**:
1. **Given** a supported file (e.g., DOCX) **When** ingestion runs **Then** extracted text is chunked and stored with reference to the file.
2. **Given** an unsupported binary file **When** ingestion runs **Then** only metadata (name, size, type) is stored and flagged as non-indexed-text.
3. **Given** duplicate upload of same file hash **When** ingestion runs **Then** second instance is de-duplicated.

---

### User Story 1E - Indexing & Deduplication (Priority: P2)
Normalized artifacts are chunked, de-duplicated, and indexed for semantic / keyword search with consistent metadata (speaker, timestamp, type).

**Why this priority**: High-quality retrieval depends on normalized, deduplicated index entries.

**Independent Test**: Ingest artifacts with intentional duplicates; ensure index contains only unique canonical chunks.

**Acceptance Scenarios**:
1. **Given** duplicate transcript segment content across retries **When** indexing occurs **Then** only one index entry persists.
2. **Given** mixed artifact types **When** indexing completes **Then** each chunk has required metadata fields (type, meetingDate, sourceRef).
3. **Given** a chunk exceeding size threshold **When** processing runs **Then** it is split without semantic boundary loss beyond configured tolerance.

---

### User Story 1F - Resilience & Retry (Priority: P2)
Transient ingestion failures (rate limits, temporary unavailability) are retried with backoff; persistent failures are surfaced for operator action.

**Why this priority**: Ensures reliability under real-world platform fluctuations.

**Independent Test**: Simulate Graph 429 responses; verify exponential backoff and eventual success or flagged failure after max attempts.

**Acceptance Scenarios**:
1. **Given** a 429 response **When** retry policy triggers **Then** subsequent attempt delay increases exponentially within max cap.
2. **Given** repeated 5xx responses exceeding attempt ceiling **When** ceiling reached **Then** ingestion status for artifact marks FAILED with diagnostic code.
3. **Given** partial success (some artifacts ingested) **When** workflow completes **Then** successful artifacts are not retried.

---

<!-- Story 1G removed per simplification: industrial-grade access audit not required for single-program usage. Basic tenant/channel membership filtering retained in requirements (FR-009) without dedicated story. -->

### (Deferred) Future Stories
Summarization / action extraction, conversational Q&A, weekly digest, and relevance feedback are deferred to a subsequent phase and removed per request.

### Edge Cases

- Meeting recording not yet available at ingestion trigger (latency / processing delay).
- Transcript partially redacted or missing speakers.
- File attachment type unsupported for text extraction (binary / image without OCR permission).
- Duplicate upload of same file version inside a meeting.
- User revokes bot permissions mid-series.
- Large transcript exceeding single processing size limit.
- Rate limiting from Graph API.
- Meeting canceled (no artifacts) but placeholder event exists.
- Multi-language meeting (mixed English + another language).
- Time zone differences for due dates in action items.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The system MUST authenticate the bot / agent using Azure Bot Service credentials and securely obtain Microsoft Graph delegated or application permissions within approved least-privilege scopes.
- **FR-002**: The system MUST ingest meeting recordings metadata (produced & governed by native Microsoft Teams), transcripts generated by Microsoft 365 Copilot / Teams live transcription services (system does not generate its own transcript), chat messages, and file attachments for configured recurring meeting series in a Teams channel.
- **FR-003**: The system MUST perform incremental ingestion (only new or changed artifacts) with idempotent processing to avoid duplicates.
- **FR-004**: The system MUST extract and normalize text content (transcript segments, chat messages, file text) preserving timestamps and speaker/author identity where available.
- **FR-005 (Deferred)**: The system MUST generate structured summaries including: overall summary, decisions, action items (owner, description, due date if provided), risks, and open questions. (Deferred – not in current iteration scope.)
- **FR-006**: The system MUST store all knowledge base artifacts using only Microsoft 365 / Teams-compatible or Azure-native services (e.g., SharePoint document library, Azure Storage, Azure AI Search index, Azure Table / Cosmos / or similar) and NOT rely on external knowledge tools (e.g., Confluence, Notion).
- **FR-007**: The system MUST provide semantic and keyword search across accumulated content returning ranked results with citation metadata (meeting date, artifact type, source link).
- **FR-008 (Deferred)**: The system MUST support conversational Q&A in Teams channel messages, grounding responses in retrieved artifacts and including citations. (Deferred – not in current iteration scope.)
- **FR-009**: The system MUST enforce access control so only members entitled to the underlying meeting series can access its content via the agent.
- **FR-010**: The system MUST apply retention and deletion policies: meeting recordings retained 90 days, transcripts & chat content retained 365 days, derived summaries retained indefinitely (until meeting series is archived or manually purged by governance policy), with configurable overrides per tenant.
- **FR-011**: The system MUST handle multilingual transcripts with language detection while storing only the original language content (no automatic translation); queries in other languages will return matches only if overlapping language content exists.
- **FR-012**: The system MUST detect and mask sensitive data categories (e.g., PII patterns) prior to indexing when policy is enabled.
- **FR-013**: The system MUST log ingestion, processing, access, and Q&A events for auditing with correlation IDs.
- **FR-014**: The system MUST retry transient failures (e.g., Graph 429/5xx) with exponential backoff within a max attempt budget.
- **FR-015**: The system MUST expose health status indicators (ingestion lag, last successful run, indexing backlog size) to authorized operators.
- **FR-016**: The infrastructure MUST be provisioned and managed via Terraform including Bot registration, identity, storage, search, key management, and compute components.
- **FR-017 (Removed)**: Enrollment UI not required; passive activation model replaces manual enable/disable.
- **FR-018 (Deferred)**: The system SHOULD generate delta updates to summaries when late artifacts (e.g., updated transcript) arrive, recording version lineage.
- **FR-019 (Deferred)**: The system SHOULD provide relevance feedback loop (user marks answer useful/not) improving retrieval weighting.
- **FR-020 (Deferred)**: The system SHOULD produce exportable, human-readable weekly digest summarizing key outcomes across the series.

### Key Entities *(include if feature involves data)*
 
- **MeetingArtifact**: Represents a single ingested resource (recording metadata, transcript segment batch, chat message collection, file). Attributes: id, meetingSeriesId, meetingOccurrenceDateTime, type, sourceUri, hash, createdAt, ingestionStatus.
- **TranscriptSegment**: Speaker-attributed text snippet with startTime, endTime, speakerId (nullable), language, text, confidence.
- **ChatMessage**: Message with messageId, parentThreadId, authorId, timestamp, contentText, attachmentsRefs.
- **FileDocument**: Extracted document text with fileId, originalName, mediaType, size, extractionStatus, textContent (token-limited), checksum.
- **SummarySet**: Generated summary collection with summaryId, meetingOccurrenceDateTime, overallSummary, decisions[], actionItems[], risks[], openQuestions[], generationModelVersion, generatedAt, supersedesSummaryId (for lineage).
- **ActionItem**: Description, owner (UPN), dueDate (optional), status, confidenceScore, sourceReferences[].
- **Decision**: Statement, rationale (optional), sourceReferences[], confidenceScore.
- **KnowledgeIndexEntry**: Search index logical record linking canonical content chunk to entity id, chunkText, embeddingsVectorRef, metadata (type, meeting date, speaker, sensitivity flags).
- **AccessAuditEvent**: userId, actionType (ingest, query, view), timestamp, resourceRef, outcome, correlationId.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 95% of eligible meeting artifacts (recording metadata, transcript, chat messages, file metadata/content) ingested and indexed within 15 minutes of meeting end (assuming artifacts available).
- **SC-002**: Index deduplication accuracy ≥ 99% (duplicate content not appearing more than once across randomly sampled 500 chunk audit).
- **SC-003**: Scheduled harvest adherence: ≥ 95% of harvest runs execute within ±10% of configured interval over pilot week.
- **SC-004**: Ingestion pipeline resilience: ≥ 90% of transient 429/5xx incidents resolved automatically within retry budget (without manual intervention) over pilot period.
- **SC-005**: Ingestion error rate (non-transient, unresolved) remains < 1% of total artifact count per month.
- **SC-006**: Search latency for keyword queries over last 3 months of data (≤ 50k chunks) ≤ 2.5s P95.

Deferred success metrics (summarization accuracy, Q&A latency, digest generation) will be defined in future phase when corresponding features enter scope.

### Assumptions

- Organization permits necessary Microsoft Graph permissions for meeting content (recordings metadata, transcripts produced by Microsoft 365 Copilot / Teams transcription services, chat messages, files) under compliance review.
- Licensing for Microsoft 365 Copilot / Teams transcription features is already in place; feature scope excludes enabling or provisioning those services.
- If transcript availability is delayed (post-processing), ingestion workflow will poll until transcript status is final or timeout (handled under retry logic FR-014).
- Azure OpenAI / AI Foundry model access approved for embedding generation to power semantic search (summarization models deferred).
- SharePoint document library is acceptable storage for derived summaries visible to channel members.
- Sensitive data masking patterns initially limited to generic PII (emails, phone numbers) extensible later.
- Retention durations finalized: recordings 90 days, transcripts & chat 365 days, summaries indefinite (until archival); Terraform policies will parameterize these values.
- No automatic translation required; multilingual support limited to storage of original language and language metadata.
- Passive activation model eliminates per-series enrollment; a single configuration flag defines designated program channel; minimal audit limited to ingestion outcomes (no enable/disable events).

### Out of Scope

- Retroactive ingestion of historical meetings before feature enablement (initial release processes only future meetings forward).
- Live real-time transcription assistance (focus is post-meeting processing).
- External publishing outside Teams / M365 ecosystem.
- Summarization, action item extraction, decision/risk/open-question generation (deferred – FR-005/018).
- Conversational Q&A interface (deferred – FR-008/019).
- Weekly digest reporting (deferred – FR-020).
- Manual enrollment / multi-channel management features (removed – replaced by passive activation).

### Clarifications Resolution

All previously identified clarification points (retention durations, translation strategy, enrollment governance) have been resolved and integrated into FR-010, FR-011, and FR-017.

### Risks & Mitigations

- Graph API rate limits: Implement adaptive backoff and batching; monitor backlog metric (FR-015).
- Data sensitivity exposure: Apply masking prior to indexing; enforce access filter at retrieval stage.
- Model hallucination: Ground responses strictly with retrieved citations; withhold answer if confidence below threshold.
- Late availability of recording/transcript: Retry schedule with exponential backoff up to 24h or until artifact status indicates final failure.
- Cost escalation (embedding large transcripts): Chunking + compression heuristics; skip low-value filler segments (e.g., intros) based on configurable rules.

### Dependencies

- Azure Bot Service registration & Teams channel installation.
- Microsoft Graph permissions (application or delegated with appropriate consent).
- Azure AI Search (or successor) for indexing & retrieval.
- Azure Storage / SharePoint for artifact persistence.
- Azure Key Vault for secret & key management.
- Azure Functions / App Service for ingestion & processing workflows.
- Azure Event Grid / Scheduler for trigger orchestration.

### Confidentiality & Compliance Considerations

- All processing remains within tenant boundaries; no external third-party SaaS for content storage.
- Audit logs retained ≥ 1 year for compliance review.
- Sensitive segments tagging allows future data minimization requests.

### Acceptance for MVP Readiness

- Stories 1A, 1B, 1C delivered (mandatory). Stories 1D, 1E, 1F delivered or partially delivered per agreed priority (P2 recommended). Story 1G removed.
- Success Criteria SC-001 through SC-006 meet thresholds in staging environment.
- No unresolved critical clarification items.
