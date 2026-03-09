# AI-Native SDLC

> Automating a lean, AI-augmented Specification → Planning → Validation workflow with GitHub Copilot & Spec Kit

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-blue?logo=github-actions)](https://github.com/features/actions)
[![Copilot](https://img.shields.io/badge/GitHub-Copilot-purple?logo=github)](https://github.com/features/copilot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Overview

This repository demonstrates a **lean AI-native feature lifecycle** powered by GitHub Actions + Copilot CLI. It couples:

1. A minimized Azure DevOps (or similar) Feature state model: **New → Specification → Planning → Validation → Ready**
2. Specification + clarification handled inside a single `Specification` state (clarification questions become child Issues, not extra states)
3. Lightweight Planning + gated Plan Validation (boolean approval flag vs extra states)
4. Optional generation workflows (spec initiation, spec refinement, code generation, Q&A)

The goal: **Reduce process drag while safely injecting AI assistance** without proliferating micro-states or “AI vs Human” ownership distinctions.

Full lifecycle details live in `docs/workflow.md`.

## 📚 Documentation Overview

| Path | Status | Summary |
|------|--------|---------|
| `docs/workflow.md` | Active | Implementation guide: lean states (New → Specification → Planning → Validation → Ready), board model, clarification via Issues, optional rules, migration notes. |
| `docs/diagrams/` | Updated | Core diagrams (02 data flow, 03 feature states, 10 clarification loop) now lean; remaining diagrams under routine review. |

Removed legacy GitHub App documentation files; focus now is only on the lean Spec + Plan + Validate flow. Core diagrams (02,03,10) reflect the current model; remaining diagrams are reviewed opportunistically.

## ✨ Key Capabilities

- 🧭 **Lean Feature Flow**: Single specification loop (no Spec Draft / Clarify / Ready micro-states)
- 🗂️ **Description-as-Spec**: Canonical spec text lives in the work item (no custom spec field required)
- 🧩 **Clarification via Issues**: Questions surfaced as child Issues; closing them drives spec completeness
- 🧪 **Planning & Validation**: Plan enrichment + approval using a simple flag instead of extra states
- 🤖 **Automated Code Generation**: Trigger Copilot-powered code generation for features or ad‑hoc prompts
- 🔄 **Pull Request Automation**: Branch + PR creation with labels and structured content
- 🧱 **Spec Kit Workflows**: Initialize & (re)generate specs from repository prompts/components
- 📝 **Q&A & Research**: Store AI answers in-version for traceability

## 📋 Prerequisites

- GitHub repository with Actions enabled
- GitHub Copilot subscription
- A PAT for workflows (code generation, Q&A, spec kit)

## 🛠️ Setup

### 1. Configure Repository Settings

1. Go to `Settings` → `Actions` → `General`
2. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**

<!-- Secrets & label creation section removed as not required in minimal setup -->

### 2. Branch Creation & Naming Convention

#### Automated Feature Branch Creation via Azure DevOps Integration

Feature branches are created automatically when a Feature work item in Azure DevOps is assigned to **"AI Teammate"** and moved to the **"Specification – Doing"** board column.

**Trigger:** Azure DevOps Service Hook → GitHub Actions Workflow

**Integration Flow:**
1. **Azure DevOps**: Product Owner assigns Feature to "AI Teammate" and moves to "Specification – Doing"
2. **Service Hook**: ADO sends webhook payload to GitHub repository dispatch endpoint
3. **GitHub Actions**: Workflow `spec-kit-specify.yml` is triggered automatically
4. **Workflow Execution**:
   - **Step 1**: GitHub Copilot generates short branch name from Feature description
   - **Step 2**: Script `.specify/scripts/bash/create-new-feature.sh` creates feature branch:
     - Scans `specs/` directory for highest feature number (e.g., 001, 002)
     - Increments to get next number (e.g., 003)
     - Combines with short name: `003-oauth2-api`
     - Validates branch name length (≤244 bytes, GitHub limit)
     - Runs `git checkout -b {branch-name}` to create new branch
     - Creates directory structure: `specs/{branch-name}/`
     - Copies spec template: `.specify/templates/spec-template.md` → `specs/{branch-name}/spec.md`
     - Sets environment variable: `SPECIFY_FEATURE={branch-name}`
     - Returns JSON with branch name, spec file path, and feature number
   - **Step 3-6**: Copilot generates full specification using Spec Kit prompts
   - **Step 7**: Commits specification to feature branch
   - **Step 8**: Overwrites ADO Feature Description with generated spec (bidirectional sync)

**See:** `specs/001-ado-github-spec/` for detailed integration specification and webhook contract

#### Manual Workflow Trigger (Testing/Debug)

For testing or one-off spec generation without ADO integration:

**Workflow:** `.github/workflows/spec-kit-specify.yml`

**Steps:**
1. Navigate to `Actions` → `Spec Kit - Specify Feature`
2. Click `Run workflow`
3. Provide inputs:
   - **feature_description** (required): "Add user authentication system"
   - **create_branch** (optional): `true` (default)
   - **work_item_id** (optional): Azure DevOps work item ID for Description sync

#### Branch Naming Convention

**Pattern:** `{feature-number}-{feature-slug}`

- **Feature Number**: Auto-incremented 3-digit number (001, 002, 003, ...)
  - Scans `specs/` directory for highest existing number
  - Increments by 1 for new feature
  
- **Feature Slug**: 
  - Generated by Copilot from feature description (Step 1)
  - 2-4 meaningful words in kebab-case
  - Filters common stop words (a, the, to, for, of, etc.)
  - Total branch name limited to 244 bytes (GitHub limit)

**Examples:**
- `"Add user authentication system"` → `001-user-authentication`
- `"Implement OAuth2 API integration"` → `002-oauth2-api-integration`
- `"Fix payment processing bug"` → `003-payment-processing-bug`

**What gets created:**
- Git branch: `{number}-{slug}`
- Feature directory: `specs/{branch-name}/`
- Spec file: `specs/{branch-name}/spec.md`
- Checklists: `specs/{branch-name}/checklists/` (if generated)
- Initial commit with feature specification

#### Manual Branch Creation (Advanced)

For advanced users or testing, you can run the script manually:

```bash
.specify/scripts/bash/create-new-feature.sh --short-name "oauth2-api" "Implement OAuth2 integration"
```

**Note:** This only creates the branch scaffold; you'll need to generate the spec separately using Copilot.

## 💻 Usage Overview

High-level lifecycle (see `docs/workflow.md` for full detail):

1. Create Feature (state: New → Specification)
2. Run spec generation (stays in Specification – Doing; clarifications become Issues)
3. Close clarification Issues → move to Specification – Done (still Specification)
4. Enter Planning (state: Planning) → enrich plan
5. Move to Validation (state: Validation) → approve (PlanApproved=true) → state transitions to Ready
6. Decompose into Stories / Tasks; proceed with normal development and optional code generation support

<!-- Archived workflow usage sections removed -->

## 📖 Feature-Specific Guides

For detailed setup and usage of specific integrations (e.g., Azure DevOps → GitHub spec generation), see:
- `specs/001-ado-github-spec/quickstart.md` - ADO → GitHub integration guide

##  Workflows

Current workflow files (see `.github/workflows/`):

| File | Purpose | Auth Mode |
|------|---------|-----------|
| `spec-kit-specify.yml` | Generate / refine specification artifacts using Spec Kit | PAT |

For feature-specific integration guides (such as Azure DevOps → GitHub integration), see `specs/[feature-id]/quickstart.md` in each feature directory.

> Archived / disabled former workflows are stored under `.github/workflows/archive/` and suffixed with `.disabled` (e.g. previous feature, QA, query, init demos). Reactivate by moving them back and removing the suffix.

### `spec-kit-specify.yml`
Primary (active) workflow: invokes Spec Kit to generate or refine specification artifacts using repository context. See its YAML for inputs.

<!-- Removed example output & use cases tied to archived feature/qa workflows -->

<!-- stray command reference removed -->
## 🔍 Validation & Quality

- **Python linting**: [ruff](https://docs.astral.sh/ruff/) — replaces flake8 + pylint + isort in one fast tool
- YAML / GitHub Actions lint: use `actionlint` or `@action-validator/cli`
- Mermaid diagrams: run `scripts/validate_diagrams.sh` (internally uses `check_mermaid.js` + mermaid-cli)
- Pre-commit: hooks configured in `.pre-commit-config.yaml` (ruff check + format, diagrams, actionlint)
- See `docs/workflow.md` for governance and optional edit control patterns

### Python Code Quality (ruff)

Install dev dependencies and set up pre-commit hooks:

```bash
pip3 install -r requirements-dev.txt
pre-commit install
```

Run ruff manually:

```bash
# Lint (and auto-fix safe issues)
ruff check . --fix

# Format check
ruff format --check .

# Format (apply changes)
ruff format .
```

Configuration lives in `pyproject.toml` under `[tool.ruff]`. Rules enabled:
`E`/`W` (pycodestyle), `F` (pyflakes), `I` (isort), `B` (bugbear), `UP` (pyupgrade), `PLE` (pylint errors), `RUF` (ruff-native).
Max line length: **100** characters (per project style guidelines).

### Mermaid Diagram Validation

Validate all diagrams:

```bash
scripts/validate_diagrams.sh
```

Only staged (changed) diagrams:

```bash
scripts/validate_diagrams.sh changed
```

Sample `.git/hooks/pre-commit` snippet (make executable):

```bash
#!/usr/bin/env bash
set -euo pipefail
scripts/validate_diagrams.sh changed
actionlint || { echo "actionlint failed" >&2; exit 1; }
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [GitHub Copilot](https://github.com/features/copilot) - AI pair programmer
- [GitHub Actions](https://github.com/features/actions) - CI/CD platform
- [@github/copilot](https://www.npmjs.com/package/@github/copilot) - Copilot CLI

## 📚 Additional Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub CLI Documentation](https://cli.github.com/manual/)

## 🐛 Troubleshooting

### Workflow fails with "COPILOT_TOKEN not found"
- Ensure you've created a PAT with Copilot scope
- Add it as a secret named `COPILOT_TOKEN` in repository settings

### PR creation fails
- Check that "Allow GitHub Actions to create and approve pull requests" is enabled
- Verify workflow has `pull-requests: write` permission

<!-- Removed troubleshooting subsection for labels (labels feature deprecated in this trimmed setup) -->

---

Made with ❤️ using a lean AI-native workflow (Copilot CLI + Spec Kit)