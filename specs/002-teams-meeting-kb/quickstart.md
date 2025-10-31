# Quickstart: Teams Meeting Knowledge Base Agent

## Scope
Phase 1 deployment for ingestion (chat messages, files, optional transcripts/recordings) and search over Azure AI Search using subscription-scoped services and RSC permissions where possible. Azure Bot Service is provisioned only as a non-interactive identity for scheduled daily harvest (no chat commands, no user interactions).

## Prerequisites
- Azure subscription with permissions to create: Resource Group, Function App (Premium plan optional), Storage, Key Vault, Azure AI Search (Basic), Azure OpenAI / AI Foundry workspace (for embeddings), Document Intelligence resource.
- Team owner rights for target Teams channel (to grant Resource-Specific Consent) without needing tenant-wide admin consent.
- Python 3.11 local environment for development.

## 1. Provision Infrastructure (Terraform)
Ensure `infra/` extended to include Azure AI Search, OpenAI (or AI Foundry) and Feature flags in Key Vault.

```bash
# From repo root
cd infra
terraform init
terraform plan -var='env=dev' -var='location=westeurope'
terraform apply -var='env=dev' -var='location=westeurope'
```

Key Vault Secrets to create (if not Terraform-managed yet):
- `GRAPH_CLIENT_ID` (bot or app registration id)
- `GRAPH_CLIENT_SECRET` (only if using application permissions for transcripts later)
- `ENABLE_TRANSCRIPTS` = false
- `ENABLE_RECORDINGS` = false

## 2. Register Azure Bot (Non-Interactive Identity)
1. Create Bot Channels Registration in Azure (subscription-scoped)
2. Generate Microsoft App ID & secret; store in Key Vault (`BOT_APP_ID`, `BOT_APP_SECRET`)
3. (Optional) Disable messaging endpoint if not required; or set placeholder endpoint returning 404.
4. Grant only read Graph scopes (RSC + future transcript scopes when approved).
5. Verify identity by obtaining token via backend (no channel message required).

## 3. Grant Resource-Specific Consent (RSC)
As Team owner:
1. Add custom app (manifest) with required RSC permissions (channel message & tab read/create).
2. Grant permissions inside the channel.
3. Capture granted scope in configuration (`RSC_ENABLED=true`).

## 4. Configure Function App Settings
Set application settings (via Azure Portal or Terraform):
- `ENABLE_TRANSCRIPTS=false`
- `ENABLE_RECORDINGS=false`
- `EMBEDDING_MODEL=text-embedding-3-large`
- `SEARCH_INDEX_NAME=kb-meetings`
- `RETENTION_RECORDINGS_DAYS=90`
- `RETENTION_TEXT_DAYS=365`

## 5. First Harvest Trigger
Call internal endpoint (once implemented):
```bash
curl -X POST "$FUNC_BASE_URL/api/harvest/trigger" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"seriesId":"program-series-1","startTime":"2025-10-31T09:00:00Z","endTime":"2025-10-31T10:00:00Z"}'
```
Check status:
```bash
curl "$FUNC_BASE_URL/api/harvest/status/{occurrenceId}" -H "Authorization: Bearer $TOKEN"
```

## 6. Search Usage
```bash
curl -X POST "$FUNC_BASE_URL/api/search/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"query":"release plan decisions","top":5}'
```

## 7. Retention Dry-Run
```bash
curl -X DELETE "$FUNC_BASE_URL/api/admin/purge/program-series-1?execute=false" \
  -H "Authorization: Bearer $TOKEN"
```

## 8. Enabling Transcripts Later
1. Request admin consent for `OnlineMeetingTranscript.Read.All` and related scopes.
2. Set Key Vault secret `ENABLE_TRANSCRIPTS=true`.
3. Re-run harvest for new occurrences; orchestrator picks up transcript polling activities.

## 9. Operational Monitoring
- Application Insights: ingestion latency, retry counts, transcript timeout rate
- Log Analytics: durable orchestration history
- Purge logs: retention compliance (PurgeLogEntry)

## 10. Next Steps
- Add summarization artifacts (Phase 2)
- Introduce language detection & multi-language chunking
- Optimize transcript retrieval (batching & caching)

## Troubleshooting
| Symptom | Possible Cause | Action |
|---------|----------------|--------|
| No transcript after 24h | Permission not granted | Verify `ENABLE_TRANSCRIPTS` & consent status |
| Harvest not running daily | Timer misconfiguration | Check Function CRON setting and Application Insights logs |
| Duplicate chunks | Hash collision unlikely | Inspect chunk creation logs for logic error |
| Slow search (>800ms) | AI Search throttling | Scale to S1 tier / add replica |
| No recording metadata | Feature disabled | Set `ENABLE_RECORDINGS=true` after consent |

## Security Notes
- No tenant-wide permissions required in Phase 1; all RSC grants by team owner.
- Secrets stored only in Key Vault references; never in source code.
- PII masked before embedding; raw optional storage restricted.
