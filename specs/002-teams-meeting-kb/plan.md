# Implementation Plan: Teams Meeting Knowledge Base Agent

**Branch**: `002-teams-meeting-kb` | **Date**: 2025-10-31 | **Spec**: `specs/002-teams-meeting-kb/spec.md`
**Input**: Feature specification from `specs/002-teams-meeting-kb/spec.md`

**Note**: Generated after Phase 0 research (see `research.md`). Updated to reflect constraint: avoid tenant-wide admin consent; prefer Azure subscription-scoped resources and Resource-Specific Consent (RSC) where possible.

## Summary

Create an internal knowledge base for a recurring program Teams channel meeting series. Scope (Phase 1) focuses on reliable ingestion of channel meeting artifacts (chat messages, shared files, transcripts when accessible, and meeting metadata) and indexing into Azure AI Search for hybrid (keyword + vector) retrieval via an internal API and Teams tab UI. Azure Bot Service is present only as a non-interactive identity used for scheduled, daily harvest authentication (no chat command interface). Activation is passive (no enrollment workflow) and harvest runs on a timer/orchestrated workflow.

Initial deployment will prioritize use of Azure subscription resources (Functions, Storage, Key Vault, AI Search, Document Intelligence, OpenAI) and avoid tenant-wide application permissions that require global admin consent. Where Graph access is needed, we will start with Resource-Specific Consent (RSC) for channel messages and files. Transcript/recording ingestion is designed but will remain dormant until required application permissions are approved.

Durable Functions orchestrator coordinates polling (transcripts), parallel artifact retrieval, chunking, masking, embedding, and indexing. Retention: recordings metadata 90 days, textual artifacts 365 days with nightly purge job. Security trimming enforced through channel membership validation (single program channel in Phase 1). Embeddings use Azure OpenAI (`text-embedding-3-large` or fallback `text-embedding-ada-002`, 1536 dims). Chunking heuristic ~1500 chars with speaker/message/paragraph boundaries.

## Technical Context

**Language/Version**: Python 3.11 (Azure Functions Premium Plan)  
**Primary Dependencies**: Azure Functions Durable, Azure Storage SDK, Azure Key Vault SDK, Azure OpenAI, Azure AI Search SDK, Azure Document Intelligence (Form Recognizer), Azure Bot Service (non-interactive identity), Microsoft Graph (RSC + optional future application scopes)  
**Storage**: Azure Blob Storage (raw artifacts + optional unmasked secure container), Azure AI Search index (hybrid), Key Vault (secrets, configuration)  
**Testing**: pytest (unit), integration harness for orchestrator activities, contract tests for API endpoints  
**Target Platform**: Azure Functions (Linux Premium for potential VNet & stable execution)  
**Project Type**: Serverless backend feature within existing repo (`function_app/`)  
**Performance Goals**: P95 search latency < 800ms with Basic tier AI Search; ingestion completion (excluding transcript wait) < 15 min after meeting end; index consistency (no duplicate chunks)  
**Constraints**: Avoid tenant-wide admin consent initially; only channel-level RSC permissions; budget-conscious (Basic AI Search tier, minimal vector recomputation); secure masking of PII before embedding; transcript polling capped at 24h  
**Scale/Scope**: Single program meeting series, expected < 50k indexed chunks in first 3 months; low QPS (< 5 concurrent queries) early phase

### Permission Strategy & Admin Consent Constraint (Minimal)
Goal: Avoid any permission requiring global admin consent for initial transcript access proof. We start with the absolute minimum:

1. Azure Bot Service registration (App ID + secret) for identity only.
2. If team owner can grant RSC for channel messages/files without admin consent, request only `ChannelMessage.Read.Group` (messages) and omit tabs & settings in Phase 1.
3. Skip `TeamsTab.Read.Group` / `TeamsTab.Create.Group` until UI integration needed.
4. Transcript access requires application permission `OnlineMeetingTranscript.Read.All`. If admin consent cannot be granted, the project HALTS before ingestion implementation (no manual export fallback). Transcript API success is a hard gate for proceeding.

Justification:
- Reduces consent friction; focuses on verifying transcript ingestion feasibility first.
- Defers non-essential scopes to later phases when UI/search surface is ready.
- Provides manual export fallback ensuring progress even without transcript API scope.

Escalation Plan:
- When admin consent becomes feasible, add `OnlineMeetingTranscript.Read.All` and enable automated polling.
- Introduce tab creation scopes only when KB visualization requires automatic provisioning.

Risk: Manual export introduces human step; mitigated by documenting clear process and automating detection of new transcript files in the channel folder.
### Bot Integration (Non-Interactive Harvest Identity)
Azure Bot Service is configured solely to provide an application identity aligned with Teams scope for daily scheduled harvest operations (e.g., authenticating to Microsoft Graph with bot registration credentials). There is no conversational command surface: users do not interact with the bot. All user queries use internal UI components (Teams tab / future web panel) that call backend HTTP APIs.

Daily Harvest Flow:
1. Timer (Durable orchestrator starter) triggers at configured window after meeting end.
2. Bot identity credentials retrieved from Key Vault to obtain access token (RSC or application scopes).
3. Orchestrator executes artifact retrieval (chat, files, transcripts if enabled, recordings metadata) under bot identity.
4. Index updated; retention purge handled separately.

Security: Identity restricted to read scopes only; no channel posting permissions required. Removal of conversational features reduces complexity and attack surface.

Non-functional target: Harvest kickoff within 5 minutes of scheduled time; completion (excluding transcript wait) <15 minutes.

Transcript and recording APIs currently require application permissions (`OnlineMeetingTranscript.Read.All`, etc.) that need admin consent. We design ingestion steps modularly; those activities remain disabled until consent granted. Configuration flag `ENABLE_TRANSCRIPTS` and `ENABLE_RECORDINGS` (Key Vault) will gate activation. The orchestrator will skip disabled artifact types.

No fallback for missing transcripts: transcript API availability is required. If unavailable after consent attempts, project pauses and escalation is documented.

Abstraction layer (`graph_client.py`) will route calls; upgrading to application permissions later will not require refactoring orchestrator logic.

## Constitution Check

*Re-validated after Phase 0 research.*

| Gate | Pass Criteria | Status | Notes |
|------|---------------|--------|-------|
| Spec Exit Integrity | No open clarification issues; acceptance checklist passed | OK | Research resolved all R-001..R-013 |
| Story Independence | User stories 1A–1F testable separately | OK | Each artifact type ingestion + resilience isolated |
| Minimal State Model | Uses existing workflow states only | OK | No new states introduced |
| Quality Automation | Diagram & workflow validation (mermaid-cli, actionlint) integrated | OK | Existing repo scripts reused |
| Complexity Justification | No unjustified deviations | OK | Durable Functions chosen (see research) |

All gates PASS; no remediation required.
## Project Structure

### Documentation (feature-specific)

```text
specs/002-teams-meeting-kb/
├── plan.md
├── research.md
├── data-model.md            # (to be created Phase 1)
├── quickstart.md            # (to be created Phase 1)
├── contracts/               # (OpenAPI yaml/json Phase 1)
└── tasks.md                 # (Phase 2 via /speckit.tasks)
```

### Source Code (augmentation inside existing repo)

```text
function_app/
├── orchestrators/           # Durable Functions orchestrator(s)
├── activities/              # Activity functions (chat, files, transcripts, embeddings, indexing, purge)
├── graph/                   # Graph client abstraction (RSC vs application)
├── indexing/                # Chunking, dedup, masking, embedding, search push
├── models/                  # Pydantic models for artifacts & index documents
├── api/                     # HTTP-trigger functions (search, status, purge, health)
└── config/                  # Settings, feature flags (ENABLE_TRANSCRIPTS, ENABLE_RECORDINGS)

tests/
├── unit/                    # Chunking, masking, hashing tests
├── integration/             # Orchestrator end-to-end (with mocks)
└── contract/                # API contract tests against OpenAPI spec
```

**Structure Decision**: Extend existing `function_app` with dedicated subfolders for orchestration and ingestion concerns; avoids introducing a separate service while keeping responsibilities grouped, supporting test isolation and future scaling (possible extraction into its own Function App if multiple series or load increases).
directories captured above]

## Complexity Tracking

No current violations. Durable Functions chosen over plain timers for stateful polling/backoff and fan-out/fan-in reliability. This is justified by multi-artifact parallelism and transcript latency management. Simpler alternative (single timer + queues) rejected due to manual state coordination overhead and retry complexity.

## Phase 0.5: Transcript Access Proof

Objective: Before building full ingestion pipeline, confirm automation can read a Microsoft Copilot 365 generated meeting transcript via Microsoft Graph using approved application read permissions (no alternative export path).

### Scope
Single test meeting occurrence with transcript enabled. Retrieve transcript metadata + content, store raw text in a temporary blob (not indexed), log speaker segmentation counts.

### Preconditions
- Key Vault feature flag `ENABLE_TRANSCRIPTS=true` (temporary for test)
- Consent granted for `OnlineMeetingTranscript.Read.All` (or RSC equivalent when available)
- Meeting ID and occurrence timestamps captured

### Minimal Implementation Artifacts
1. `function_app/activities/transcript_probe.py` (activity: fetch transcript list, pick latest, download content)
2. `function_app/orchestrators/transcript_probe_orch.py` (starter triggered manually via HTTP or timer)
3. Temporary output blob container `transcript-proofs` (private)
4. Logging: number of segments, total characters, first 200 chars sample

### Execution Steps
1. Invoke HTTP trigger `/api/transcript-proof?meetingId={id}` (manual for test phase)
2. Orchestrator calls probe activity with retry/backoff (3 attempts, exponential)
3. Activity stores transcript raw text in blob `proof-{occurrenceId}.txt`
4. Returns metrics JSON

### Success Criteria
| Criterion | Target |
|-----------|--------|
| Transcript fetched | HTTP 200 with metrics |
| Segment count > 0 | > 10 (example meeting) |
| Storage persisted | Blob exists with > 1KB content |
| No PII leakage log | Masking prototype optional; not required for proof |

### Failure Modes & Actions
- 404 transcript: verify meeting supports transcription; re-run after generation delay.
- 401/403 permissions: confirm admin consent & scope; capture error code.
- Throttling: backoff intervals respected; escalate if >3 failures.

### Exit
On success, disable `ENABLE_TRANSCRIPTS` until full ingestion implemented. Proof artifacts may be purged manually.

## Execution Order (Priority)

1. Permission & Access Test (Phase 0.5): Validate ability to obtain transcript via Graph transcript API. Failure to access halts progression.
2. Adjust Permission Strategy: If API access fails, document fallback and proceed with manual file ingestion design.
3. Terraform Extension (AI Search, Key Vault flags) AFTER permission test passes (avoid provisioning unused resources prematurely).
4. Orchestrator Skeleton (Durable) implementing transcript probe + basic logging.
5. Chat/File ingestion activities (only after transcript path clarified).
6. Masking pipeline & embedding integration.
7. Retention purge job.
8. Search API & Teams tab UI integration.

Explicitly deferring infrastructure spend and code complexity until permission viability is confirmed reduces rework risk.
