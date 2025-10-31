# Phase 0 Research: Teams Meeting Knowledge Base Agent

**Branch**: `002-teams-meeting-kb`
**Generated**: 2025-10-31
**Purpose**: Resolve all "NEEDS CLARIFICATION" items & research objectives (R-001 – R-013) to unblock Phase 1 design.

## Format Legend
Each objective below follows:
- Decision: Final selection
- Rationale: Why chosen (constraints, capabilities, trade‑offs)
- Alternatives considered: Rejected options & reasons
- References: Key Microsoft Docs (URL)

---
## R-001 Graph Permission Set (Least Privilege)
**Decision**: Use application permissions: `OnlineMeetingTranscript.Read.All`, `ChannelMessage.Read.All`, `Chat.Read.All` (for meeting chats only), `Files.Read.All` (read file content during meeting window), `Group.Read.All` (team/channel enumeration), `Channel.ReadBasic.All` (metadata), plus `TeamsTab.Create` (future KB tab automation). Avoid write scopes initially.
**Rationale**: Application permissions enable unattended scheduled harvest; transcript & recording APIs require `OnlineMeetingTranscript.Read.All`. Channel messages & files ingestion mandate broad read scopes; restricting by time window enforced in application logic. Adding `TeamsTab.Create` prepares for automated KB tab provisioning without later consent churn.
**Alternatives considered**:
- Delegated permissions via bot user → rejected (requires user context, breaks passive activation & timer runs).
- Resource-specific consent (RSC) for transcripts only → insufficient for channel messages/files aggregate, increases complexity.
**References**: Transcripts change notifications (OnlineMeetingTranscript.*); App cert examples (ProdPad, DocketAI) with similar permission sets.

## R-002 Transcript Availability & Polling Strategy
**Decision**: Poll transcript list endpoint for meeting (`communications/onlineMeetings/{id}/transcripts`) every 10 min with exponential backoff (factor 2, max interval 60 min) until transcript appears or 24h cutoff; treat single transcript as final snapshot; if missing after 24h mark HARVEST_TRANSCRIPT_TIMEOUT.
**Rationale**: Transcripts accessible only after generation latency; docs show potential delay. Single transcript per meeting simplifies idempotency. Backoff reduces Graph pressure & risk of throttling.
**Alternatives considered**:
- Change notifications subscription per meeting → subscription must be created before transcription starts; operational overhead high.
- Constant fixed interval polling → less adaptive, increases rate-limit risk.
**References**: Microsoft Graph transcript subscription documentation (latency & limitations).

## R-003 Recording Metadata Retrieval
**Decision**: Use `communications/onlineMeetings/{id}/recordings` list (application) during first harvest pass; store metadata + retrieval URL (no binary download). Do not ingest media content; rely on link for future playback.
**Rationale**: KB search centers on textual artifacts; storing binary increases cost & complexity. Metadata adequate for citation & retention compliance.
**Alternatives considered**:
- Download & transcode recording → heavy storage & processing; transcript already provides textual narrative.
- Skip recording entirely → loses provenance & context indicator.
**References**: Recording API docs (Get-MgCommunicationOnlineMeetingRecording).

## R-004 Chat Message Scope & Threading
**Decision**: Use `channelMessages` APIs for channel meetings; derive meeting window (`startUtc`,`endUtc + grace`) and filter messages by timestamp; capture parent message ID for threads; no ingestion of non-meeting window messages. Deleted messages excluded (avoid retention complexity) – store deletion count metric only.
**Rationale**: Minimizes data volume & privacy exposure; thread context enough for retrieval relevance; simplifying deletion handling reduces schema complexity.
**Alternatives considered**:
- Include deleted messages marked as deleted → adds sensitive retention implication.
- Ingest entire channel history with post-filtering → unnecessary volume, costs.
**References**: ChatMessage schema docs.

## R-005 File Attachment Ingestion & Text Extraction
**Decision**: Retrieve file attachment metadata via chatMessage attachments; fetch underlying SharePoint file with `Files.Read.All`; perform text extraction only for Office formats & PDF using Azure Document Intelligence Read model; store extracted text chunks; for binaries (images, archives) store metadata only.
**Rationale**: Office/PDF content carries high semantic value; Document Intelligence supports multi-format OCR & layout; limiting extraction scope manages cost.
**Alternatives considered**:
- Full OCR for images → deferred (cost versus value for meeting context).
- No extraction (metadata only) → lowers search relevance drastically.
**References**: Document Intelligence Read model supported formats.

## R-006 Chunking & Deduplication Heuristics
**Decision**: Target chunk size ~1500 characters (aligned with embedding token efficiency for 1–2K tokens); boundaries: transcript speaker change OR chat message OR file paragraph. Dedup key = SHA256(normalized_text + meetingOccurrenceId + sourceType). If duplicate encountered discard later instance. Large paragraphs >3000 chars split by sentence boundary with simple heuristic; store original span offsets.
**Rationale**: 1500 char balances embedding cost vs recall; speaker boundaries preserve context; hashing ensures idempotent ingestion/retries.
**Alternatives considered**:
- Fixed token count via model tokenizer upfront → additional processing overhead; heuristic adequate.
- Very small chunks (<=500 chars) → increases index document count & latency.
**References**: Azure AI Search vector quickstart (embedding dimension & hybrid search patterns), RAG schema tutorial (chunk-parent considerations).

## R-007 Search Index Schema (Azure AI Search)
**Decision**: Single hybrid index with fields: `id (key)`, `meetingSeriesId (filterable)`, `meetingDate (Edm.DateTimeOffset filterable/sortable)`, `artifactType (filterable facetable)`, `speaker (searchable filterable)`, `author (searchable filterable)`, `content (searchable retrievable)`, `contentVector (vector dims 1536)`, `sourceRef (retrievable)`, `sensitivityFlags (filterable)`, `language (filterable)`, `createdAt (sortable)`. Semantic config enabled; hybrid queries (keyword + vector). Keep minimal filterable subset to avoid over-attribution.
**Rationale**: Unified index simplifies query & avoids join complexity; dedicated parent index not needed until multi-series scaling. Attributes chosen per retrieval & security trimming needs; minimal to control storage.
**Alternatives considered**:
- Parent-child dual index setup → premature complexity for single program channel.
- Multiple indexes per artifact type → increases operational overhead & query orchestration complexity.
**References**: Index schema checklist; performance tips (avoid over-attribution); RAG index design tutorial.

## R-008 Retention Enforcement Strategy
**Decision**: Store per-artifact `ingestedAt`. Nightly purge function scans index & storage metadata for: recordings >90d (remove metadata), transcripts/chat/file textual content >365d (delete index docs & storage text), maintain deletion audit log. Summaries deferred; retention config via Key Vault secret or app settings; dry-run mode for governance validation.
**Rationale**: Time-based purge straightforward; avoids embedding of retention windows into document itself beyond metadata. Dry-run reduces accidental mass deletion risk.
**Alternatives considered**:
- Soft-delete flag & delayed physical removal → unnecessary complexity for dev sandbox; can add later.
- Immediate purge on threshold crossing during search → increases query latency.
**References**: Success criteria & retention FR-010.

## R-009 Sensitive Data Masking
**Decision**: Pre-index regex pipeline for email, phone, simple ID patterns; replace with token `<PII:EMAIL>` etc; retain raw in secure storage blob encrypted (optional toggle). Masking executed before embedding to avoid semantic drift leakage; store `sensitivityFlags` enumerating categories present.
**Rationale**: Minimizes exposure in search results; embedding masked content reduces risk of vector leakage; keeping raw optional preserves audit capability.
**Alternatives considered**:
- Full contextual PII detection (ML) → higher complexity; regex baseline sufficient.
- Drop sensitive segments entirely → may reduce context quality.
**References**: Data platform security trimming guidance (use filters & metadata).

## R-010 Access Control & Security Trimming
**Decision**: Application-level filtering by verifying caller’s Teams membership (channel/team). Query adds filter on `meetingSeriesId` plus optional participant lists (future). For now, single designated channel; service rejects requests from non-members; maintain membership cache (TTL 15 min) to reduce Graph calls.
**Rationale**: Document-level ACL complexity not required for single-program; membership caching balances performance vs freshness.
**Alternatives considered**:
- Per-chunk ACL field with user IDs → oversized index & update churn.
- Rely solely on Teams front-end UI access → insufficient if future API endpoints exposed.
**References**: Security trimming docs in Azure AI Search.

## R-011 Orchestration Pattern (Timers vs Durable Functions)
**Decision**: Use Durable Functions orchestrator for harvest workflow (fan-out: recording metadata, transcript poll, chat, files; fan-in index). Durable timers for polling cycles; benefits: checkpointing, simplified backoff timers. Storage provider uses queues ensuring reliability.
**Rationale**: Complex multi-step with retries; Durable provides state & resilience; simpler than custom queue triggers for each sub-task.
**Alternatives considered**:
- Plain Timer trigger + chained queue messages → manual state handling & retry complexity.
- External workflow engine (Logic Apps) → additional cost & dependency.
**References**: Durable Functions patterns (monitor/backoff, fan-out/fan-in, orchestrator reliability).

## R-012 Embedding Model Selection
**Decision**: Azure OpenAI `text-embedding-3-large` (if available) else `text-embedding-ada-002` (1536 dims) for cost vs quality; dimension 1536 matches documented sample. Evaluate compression later; store original embedding to allow reindex swap. Abstraction layer for embedding provider.
**Rationale**: Balanced semantic quality; widely supported; dimension aligns with search sample & vector limits. Large model fallback ensures quality for multi-language transcripts.
**Alternatives considered**:
- `text-embedding-3-small` → lower quality risk for meeting nuance.
- Custom local model → operational overhead & not Azure-native.
**References**: Vector search docs (embedding dimension examples; vector limits table).

## R-013 Capacity & Scaling Plan
**Decision**: Start with Basic tier Azure AI Search (1 partition, 1 replica). Expect <50k chunks first 3 months (< few hundred MB). Monitor P95 latency & throttling; upgrade to S1 before vector quota pressure (Basic 5GB vector quota per partition). If query throttling appears & chunk count >100k, move to S1 and add a second replica. Capacity worksheet produced after initial pilot ingestion (1–5% sample). Index over-attribution avoided to reduce size.
**Rationale**: Cost efficiency early phase; gradual scale path; aligns with vector limits & performance tips.
**Alternatives considered**:
- Start at S1 → unnecessary cost before validating usage.
- Multi-index sharding from start → premature optimization.
**References**: Capacity planning, vector quota table, performance tips, cost management guidance.

## KB Location Inside Teams Channel
**Decision**: Use SharePoint document library (existing Files tab root) + Add custom Teams Tab (either Website pointing to minimal knowledge view or future SPFx tab) that lists curated summary pages & search UI deep link. Index lives in Azure AI Search (not directly inside Teams). Optionally pin OneNote for free-form notes (not used for canonical KB storage).
**Rationale**: Document library natively connected to channel; easy tab addition; supports file-based summary artifacts & governance; avoids custom storage duplication. OneNote optional for human editing but not indexed initially (scope control). SPFx tab expansion later for integrated search panel.
**Alternatives considered**:
- OneNote as primary KB → weak file governance & granular retention, harder structured updates.
- Custom tab only (no library) → loses native file management & versioning.
- Wiki tab → deprecated / limited configuration.
**References**: SharePoint + Teams integration docs, document library tab configuration, overview of Teams/SharePoint connected sites.

---
## Summary of Resolved Unknowns
All research objectives R-001..R-013 resolved. No remaining NEEDS CLARIFICATION items.

## Design Implications
- Single hybrid index simplifies data-model; no parent index required Phase 1.
- Durable orchestration commits us to adding `requirements.txt` dependency `azure-functions-durable` & adjusting Function host config.
- Need secure storage for raw unmasked content if masking toggle enabled (Blob container with restricted access).
- Data-model will reflect unified `IndexDocument` referencing original artifact type & meeting occurrence.

## Risks Post-Research
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Transcript fails to appear within 24h | Incomplete narrative | Flag status, potential manual re-run command later |
| Embedding model availability changes | Reindex needed | Version tagging, abstraction layer |
| Durable Functions scaling under heavy backlog | Delay ingestion | Metrics & scale plan upgrade to Premium if VNet needed |
| PII regex false negatives | Sensitive leakage | Iterative pattern enhancement, add ML later |

## Next Steps (Phase 1)
1. Draft `data-model.md` with entities and field constraints.
2. Produce OpenAPI contract for internal endpoints.
3. Extend Terraform: Azure AI Search service, Key Vault secrets for Graph app credentials, function settings.
4. Implement ingestion orchestrator skeleton with stubs.

## References Catalog
(See inline references; consolidate later into bibliography section if required.)

---
**Completion Criteria**: This document plus updated `plan.md` (technical context) removes all unknowns and permits advancement to Phase 1 design.
