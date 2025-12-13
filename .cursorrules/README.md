# Cursor Rules

This directory contains modular cursor rules organized by technology stack and domain concerns. Cursor automatically reads all `.md` files in this directory.

## Organization Structure

### Core Rules
- **[00-project-context.md](00-project-context.md)** - Project overview, architecture, and key principles

### Technology-Specific Rules
- **[python.md](python.md)** - Python coding standards (PEP 8, type hints, docstrings, linting)
- **[terraform.md](terraform.md)** - Terraform conventions, CAF compliance, security requirements
- **[github-actions.md](github-actions.md)** - GitHub Actions workflow validation, YAML standards
- **[shell.md](shell.md)** - Bash script conventions, PATH management, and best practices
- **[git-workflow.md](git-workflow.md)** - Git workflow, branch protection, PR requirements

### Domain-Specific Rules
- **[azure-functions.md](azure-functions.md)** - Azure Functions deployment, configuration, patterns
- **[azure-infrastructure.md](azure-infrastructure.md)** - Azure resource security, networking, managed identity
- **[validation.md](validation.md)** - Mermaid diagram validation, workflow validation requirements
- **[documentation.md](documentation.md)** - Documentation standards, when to document, markdown conventions

### Integration Rules
- **[ado-integration.md](ado-integration.md)** - Azure DevOps integration patterns, webhook handling
- **[spec-kit.md](spec-kit.md)** - Spec Kit workflow conventions, branch naming, spec structure

## Quick Reference

| Concern | File |
|---------|------|
| Python code style | [python.md](python.md) |
| Terraform infrastructure | [terraform.md](terraform.md) |
| GitHub Actions workflows | [github-actions.md](github-actions.md) |
| Bash scripts | [shell.md](shell.md) |
| Git workflow & PRs | [git-workflow.md](git-workflow.md) |
| Azure Functions deployment | [azure-functions.md](azure-functions.md) |
| Azure security/networking | [azure-infrastructure.md](azure-infrastructure.md) |
| Mermaid diagrams | [validation.md](validation.md) |
| When to document | [documentation.md](documentation.md) |
| ADO webhooks | [ado-integration.md](ado-integration.md) |
| Spec Kit workflows | [spec-kit.md](spec-kit.md) |
| Project architecture | [00-project-context.md](00-project-context.md) |

## How to Add New Rules

1. **Identify the category**: Technology, domain, or integration?
2. **Choose or create file**: Add to existing file if related, or create new file if distinct concern
3. **Follow naming**: Use kebab-case for new files (e.g., `new-concern.md`)
4. **Cross-reference**: Link to related rules in other files where appropriate
5. **Update this README**: Add entry to Quick Reference table

## File Processing Order

Files are processed in alphabetical order. Use numeric prefixes (e.g., `00-`) to control processing order if needed. The project context file uses `00-` prefix to ensure it's loaded first.

## Notes

- Each file should be self-contained but can reference other files
- Keep rules actionable and specific to this project's needs
- Rules should complement, not duplicate, existing documentation

