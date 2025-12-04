# Shell Script Conventions

## Best Practices

### Script Headers

Always start scripts with shebang and error handling:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- `set -e`: Exit on error
- `set -u`: Exit on undefined variable
- `set -o pipefail`: Exit on pipe failure

### Variable Naming

- Use UPPERCASE for environment variables
- Use lowercase for local variables
- Use descriptive names

```bash
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
local branch_name="feature/example"
```

### Error Handling

Always check exit codes and provide meaningful error messages:

```bash
if ! command -v jq >/dev/null 2>&1; then
    echo "Error: jq is required but not installed" >&2
    exit 1
fi
```

### Functions

Use functions for reusable logic:

```bash
function validate_branch_name() {
    local branch_name="$1"
    if [[ ${#branch_name} -gt 244 ]]; then
        echo "Error: Branch name exceeds 244 bytes" >&2
        return 1
    fi
}
```

### Quoting

Always quote variables to prevent word splitting:

```bash
# Good
echo "$variable"
cp "$source" "$dest"

# Bad
echo $variable
cp $source $dest
```

### Path Handling

Use absolute paths or resolve relative paths:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"
```

### Temporary Files

Use `mktemp` for temporary files:

```bash
TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT
```

### Logging

Use appropriate log levels:

```bash
log_info() {
    echo "[INFO] $*" >&2
}

log_error() {
    echo "[ERROR] $*" >&2
    exit 1
}
```

### Input Validation

Always validate inputs:

```bash
if [[ -z "${INPUT_VAR:-}" ]]; then
    echo "Error: INPUT_VAR is required" >&2
    exit 1
fi
```

## Script Organization

1. Shebang and error handling
2. Constants and configuration
3. Function definitions
4. Main script logic
5. Cleanup (if needed)

## Common Patterns

### Check command availability

```bash
if ! command -v tool >/dev/null 2>&1; then
    echo "Error: tool is required" >&2
    exit 1
fi
```

### Parse command-line arguments

```bash
while [[ $# -gt 0 ]]; do
    case $1 in
        --flag)
            FLAG=true
            shift
            ;;
        --value=*)
            VALUE="${1#*=}"
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done
```

### JSON Processing

Use `jq` for JSON processing:

```bash
BRANCH_NAME=$(echo "$JSON" | jq -r '.branch_name')
```

## Related Rules

- See [spec-kit.md](spec-kit.md) for Spec Kit script patterns
- See [github-actions.md](github-actions.md) for workflow script patterns

