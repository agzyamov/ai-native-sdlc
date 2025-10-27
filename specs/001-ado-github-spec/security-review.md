# Security Review Checklist: Azure DevOps → GitHub Spec Generation

**Feature**: Azure Function-based spec generation automation
**Created**: 2025-10-27
**Status**: Pre-deployment review

## Authentication & Authorization

- [X] GitHub PAT (`GH_WORKFLOW_DISPATCH_PAT`) scoped minimally (Actions: RW, Contents: R)
- [X] Azure DevOps PAT (`ADO_WORK_ITEM_PAT`) scoped minimally (Work Items: Read)
- [X] Azure Function uses Function Key authentication (auth_level=FUNCTION)
- [ ] (Optional) HMAC signature validation for Service Hook payloads (deferred - Backlog)
- [ ] PAT rotation schedule documented (90 days policy in quickstart)
- [X] Secrets stored in Azure App Settings (encrypted at rest)
- [ ] (Production) Migrate secrets to Azure Key Vault with managed identity

## Input Validation

- [X] Request body parsed defensively (try/except for malformed JSON)
- [X] Work item ID extracted with defensive checks (missing field handled)
- [X] Event type validated (only `workitem.updated` accepted)
- [X] Work item type validated (only `Feature` accepted)
- [X] Assignee validated (configurable match, case-insensitive)
- [X] Board column validated (configurable match, exact)
- [X] No SQL injection risk (no database; REST APIs only)
- [X] No command injection risk (no shell execution; Python requests library only)

## Network Security

- [X] All outbound HTTP requests include explicit timeout (15s)
- [X] HTTPS enforced for GitHub API calls
- [X] HTTPS enforced for ADO REST API calls
- [X] Function endpoint requires function key (not anonymous)
- [ ] (Production) Configure allowed CIDR ranges for Service Hook source IPs
- [ ] (Production) Enable Azure Front Door or App Gateway for DDoS protection

## Data Handling

- [X] No sensitive data logged (PATs never logged)
- [X] Work item IDs logged (non-sensitive)
- [X] Correlation IDs used for traceability
- [X] Error messages don't expose internal details (generic 500 messages)
- [ ] (Production) Enable Application Insights for monitoring
- [ ] (Production) Configure log retention policy (30/90 days)

## Secrets Management

- [X] PATs not hardcoded in source code
- [X] PATs retrieved from environment variables
- [X] `.env` files excluded from git (`.gitignore` configured)
- [ ] (Production) Use Azure Key Vault references instead of App Settings
- [ ] (Production) Enable Managed Identity for Key Vault access

## Error Handling

- [X] Exceptions caught and logged without exposing stack traces to clients
- [X] Validation failures return 403 (not 500)
- [X] Malformed requests return 400 (not 500)
- [X] Retry logic only applies to transport errors (not validation failures)
- [X] Max retry attempts bounded (3 attempts)

## Rate Limiting & DoS Protection

- [ ] (Production) Implement debounce hash to prevent duplicate rapid triggers
- [ ] (Production) Configure Azure Function consumption plan scale limits
- [ ] (Production) Monitor for abnormal request patterns
- [ ] (Production) Set up alerts for excessive 403/500 errors

## Compliance & Audit

- [X] Structured JSON logs for audit trail (correlation_id, work_item_id, outcome)
- [X] All dispatch attempts logged (success and failure)
- [ ] (Production) Log Analytics workspace configured
- [ ] (Production) Alerts configured for security events (repeated 403, unusual latency)

## Deployment Security

- [X] Infrastructure as Code (Terraform) used for reproducibility
- [X] Terraform state not committed to git (`.gitignore` configured)
- [ ] (Production) Terraform state stored in encrypted remote backend (Azure Storage)
- [ ] (Production) Terraform plan reviewed before apply
- [ ] (Production) RBAC configured for function app (least privilege)

## Incident Response

- [ ] Documented rollback procedure (invoke manual workflow or resurrect pipeline)
- [ ] PAT rotation procedure documented (quickstart.md)
- [ ] Escalation path defined for security incidents
- [ ] (Production) Runbook for common failure scenarios

## Remaining Risks

| Risk | Impact | Likelihood | Mitigation Status |
|------|--------|------------|-------------------|
| PAT compromise | High | Low | Rotate regularly; migrate to GitHub App (Backlog) |
| Service Hook payload manipulation | Medium | Low | HMAC validation (Backlog) |
| Excessive dispatch volume (abuse) | Medium | Low | Debounce + rate limiting (Backlog) |
| ADO REST API unavailability | Medium | Medium | Retry logic implemented; consider circuit breaker (Future) |

## Approval

- [ ] Security reviewer: _____________________ Date: _______
- [ ] Architect reviewer: ____________________ Date: _______

## Notes

MVP scope intentionally excludes advanced hardening (HMAC, Key Vault, debounce) to accelerate pilot. Promote these to active implementation once pilot validates functional requirements and observes real-world attack surface.
