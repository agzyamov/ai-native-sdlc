# Git Workflow and Branch Protection

## Branch Protection

**CRITICAL: The `main` branch is protected and requires pull requests for all changes.**

### Rules

1. **NEVER push directly to `main`**:
   - ❌ `git push origin main` - FORBIDDEN
   - ✅ Always create a feature branch and open a PR

2. **Always use feature branches**:
   ```bash
   git checkout -b fix/description-of-fix
   # or
   git checkout -b feat/new-feature-name
   ```

3. **Create PRs for all changes**:
   - After committing changes to a feature branch
   - Push the branch: `git push -u origin fix/branch-name`
   - Create PR: `gh pr create` or via GitHub UI

4. **Branch naming conventions**:
   - `fix/` - Bug fixes and error handling improvements
   - `feat/` - New features
   - `refactor/` - Code refactoring
   - `docs/` - Documentation updates
   - `infra/` - Infrastructure changes

5. **Language requirements**:
   - **ALL commit messages MUST be in English only**
   - **ALL PR titles and descriptions MUST be in English only**
   - Use conventional commit format: `type: description`
   - Examples:
     - `fix: resolve issue with ADO work item assignment`
     - `feat: add markdown support for ADO work items`
     - `refactor: extract Python logic from bash script`
   - Chat/conversation can be in any language (Russian/English)

### Workflow

1. **Start from main**:
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b fix/your-fix-name
   ```

3. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "fix: description of fix"
   ```

4. **Push and create PR**:
   ```bash
   git push -u origin fix/your-fix-name
   gh pr create --title "fix: Description" --body "Details..."
   ```

5. **After PR is merged**:
   ```bash
   git checkout main
   git pull origin main
   git branch -d fix/your-fix-name  # Clean up local branch
   ```

### Exceptions

- **Emergency hotfixes**: Still require PR, but can be fast-tracked
- **Documentation-only changes**: Still require PR (maintains review process)

## Related Rules

- See [github-actions.md](github-actions.md) for workflow standards
- See [spec-kit.md](spec-kit.md) for feature branch naming conventions

