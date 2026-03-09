# GitHub Copilot Instructions

Detailed topic-specific instructions live in `.github/instructions/`:

| File | Scope (`applyTo`) | Topics |
|------|-------------------|--------|
| [python-development.instructions.md](.github/instructions/python-development.instructions.md) | `**/*.py` | PEP 8, linting, type hints, docstrings, best practices |
| [azure-functions-deployment.instructions.md](.github/instructions/azure-functions-deployment.instructions.md) | `function_app/**` | Remote build, deployment steps, Premium plan pitfalls |
| [github-actions.instructions.md](.github/instructions/github-actions.instructions.md) | `.github/workflows/**`, `docs/diagrams/**` | Mermaid validation, GHA workflow validation, run debugging |
| [azure-infrastructure.instructions.md](.github/instructions/azure-infrastructure.instructions.md) | `infra/**` | Network security, IP rotation, Terraform CAF standards |

## Active Technologies
- GitHub Actions composite environment (YAML) + Bash; Spec Kit CLI (Python runtime 3.11 in workflow). (001-ado-github-spec)
- None (stateless; spec stored in Git + ADO work item Description). (001-ado-github-spec)
- Bash (shell scripts), Python 3.11 (for marker extraction script), YAML (GitHub Actions workflow) (003-preserve-clarification-markers)

## Recent Changes
- 001-ado-github-spec: Added GitHub Actions composite environment (YAML) + Bash; Spec Kit CLI (Python runtime 3.11 in workflow).
