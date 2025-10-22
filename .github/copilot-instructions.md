These GitHub Copilot rules will automatically enables Copilot to:

-Follow PEP 8
-Validate code with flake8 and pylint
-Add timeouts to HTTP requests
-Properly organize imports
-Use docstrings and type hints

# GitHub Copilot Instructions for Python Development

## Code Quality Standards

When writing Python code, always:

1. **Follow PEP 8** style guidelines
2. **Use type hints** where appropriate
3. **Add docstrings** to all functions, classes, and modules
4. **Keep line length** to 100 characters maximum

## Linting Requirements

All Python code must pass these linters without errors:

- **flake8** with `--max-line-length=100`
- **pylint** with `--max-line-length=100`

### Common Issues to Avoid

- No trailing whitespace on blank lines
- No blank line at end of file (only newline)
- Import order: standard library → third-party → local
- Always add `timeout` parameter to HTTP requests
- Remove f-strings without placeholders

## Code Formatting

- Use 4 spaces for indentation
- Blank lines: 2 between top-level definitions, 1 between methods
- Consistent quote style (prefer single quotes unless needed)

## Best Practices

- Add timeout to all network requests (e.g., `requests.get(..., timeout=30)`)
- Use context managers for file operations
- Handle exceptions explicitly
- Validate user input
- Log important operations

Always run linters before committing code!

## Documentation Rules

**Do NOT create documentation** for:
- Simple utility functions
- Self-explanatory code
- Small helper scripts
- Experimental or temporary code

Documentation is only needed for:
- Public APIs
- Complex algorithms that require explanation
- When explicitly requested by the user

## Mermaid Diagram Validation

**Always validate Mermaid diagrams** before committing:

When creating or modifying Mermaid diagrams:

1. **Run validation script** after creation:
   ```bash
   node check_mermaid.js <filename>
   ```

2. **Check for common issues:**
   - Single diagram type per code block (graph TD, flowchart, mindmap, etc.)
   - No mixed diagram types in one block
   - Balanced quotes, brackets, parentheses
   - Valid node IDs (no special characters)
   - Proper arrow syntax (-->, -.->)

3. **Test rendering** in Mermaid Live Editor: https://mermaid.live/

**Before committing:**
- ✅ Script validation passes
- ✅ Diagram renders correctly in VS Code preview
- ✅ No parse errors in console

**Never commit broken Mermaid diagrams!**

## GitHub Actions Workflow Validation

**Always validate GitHub Actions workflows** before committing:

When creating or modifying `.github/workflows/*.yml` files:

1. **Run yamllint first** to catch YAML syntax errors:
   ```bash
   yamllint .github/workflows/<workflow-file>.yml
   ```

2. **Run actionlint** for GitHub Actions-specific validation:
   ```bash
   actionlint .github/workflows/<workflow-file>.yml
   ```

3. **Check for common issues:**
   - Valid YAML syntax (proper indentation, no tabs)
   - Correct trigger syntax (`on:` section)
   - Valid action versions (e.g., `actions/checkout@v4`)
   - Required permissions specified
   - Proper environment variable syntax (`${{ }}` for expressions, `$VAR` for shell)
   - No deprecated actions or syntax

4. **Test workflow locally** (if possible):
   - Use `act` tool for local testing: https://github.com/nektos/act
   - Or trigger workflow manually via GitHub UI

**Before committing:**
- ✅ yamllint passes without errors (YAML syntax)
- ✅ actionlint passes without errors (GitHub Actions validation)
- ✅ All actions use pinned versions
- ✅ Workflow triggers are correctly configured

**Install tools:**
```bash
# macOS
brew install yamllint actionlint

# Linux
pip install yamllint
go install github.com/rhysd/actionlint/cmd/actionlint@latest
```

**Never commit broken GitHub Actions workflows!**