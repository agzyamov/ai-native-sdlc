# Validation Requirements

## Mermaid Diagram Validation

**Always validate Mermaid diagrams** before committing:

When creating or modifying Mermaid diagrams:

1. **Run validation script** after creation:
   ```bash
   node check_mermaid.js <filename>
   ```

2. **Check for common issues**:
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

### Additional Automated Validation (mermaid-cli)

To strengthen validation, also run `@mermaid-js/mermaid-cli` (mmdc) against every changed diagram file in `docs/diagrams/` before committing:

1. Install (or use npx):
   ```bash
   npm install --save-dev @mermaid-js/mermaid-cli
   # or just use npx mmdc ... without installing
   ```

2. For markdown diagram files that contain a single mermaid code fence, you can validate via pipe:
   ```bash
   awk '/```mermaid/{flag=1;next}/```/{flag=0}flag' docs/diagrams/<file>.md \
     | npx mmdc -i /dev/stdin -o /dev/null
   ```

3. (Optional) Create (or use existing) helper script `scripts/validate_diagrams.sh` to validate all modified diagrams:
   ```bash
   set -euo pipefail
   CHANGED=$(git diff --name-only --cached | grep '^docs/diagrams/.*\.md$' || true)
   [ -z "$CHANGED" ] && exit 0
   for f in $CHANGED; do
     echo "Validating $f (mermaid-cli)" >&2
     awk '/```mermaid/{flag=1;next}/```/{flag=0}flag' "$f" \
       | npx @mermaid-js/mermaid-cli -i /dev/stdin -o /dev/null || {
           echo "Mermaid validation failed for $f" >&2
           exit 1
         }
   done
   ```

4. (Optional) Add a pre-commit hook (`.git/hooks/pre-commit`) invoking the script so commits fail if any diagram does not parse.

Success criteria:
- ✅ `mmdc` exits with status 0 for every changed diagram
- ✅ No warnings or parse errors printed
- ✅ Existing `check_mermaid.js` script also passes

If either validation fails, fix the diagram before committing.

Existing repository helper:

```bash
scripts/validate_diagrams.sh            # validate all diagrams
scripts/validate_diagrams.sh changed      # only staged diagrams
```

## GitHub Actions Workflow Validation

See [github-actions.md](github-actions.md) for detailed workflow validation requirements.

## Terraform Validation

Before committing Terraform code:

1. Run `terraform fmt` to format code
2. Run `terraform validate` to check syntax
3. Run `terraform plan` to verify resource arguments
4. Review network configuration for security compliance

## Python Code Validation

Before committing Python code:

1. Run `flake8` with `--max-line-length=100`
2. Run `pylint` with `--max-line-length=100`
3. Ensure all tests pass

See [python.md](python.md) for detailed Python validation requirements.

## Related Rules

- See [github-actions.md](github-actions.md) for workflow validation
- See [python.md](python.md) for Python linting
- See [terraform.md](terraform.md) for Terraform validation

