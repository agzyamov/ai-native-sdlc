# Shell Script Conventions

## PATH Management for CLI Tools

### Critical Rule: Always Use PATH, Never Hardcode Paths

**ALWAYS** ensure CLI tools are in PATH and run them from PATH, never using hardcoded paths.

#### Setup PATH at Start of Every Terminal Session

When running terminal commands, **ALWAYS** set up PATH first to include common CLI tool locations:

```bash
# macOS Homebrew (Apple Silicon)
export PATH="/opt/homebrew/bin:$PATH"

# macOS Homebrew (Intel)
export PATH="/usr/local/bin:$PATH"

# User local bin
export PATH="$HOME/.local/bin:$PATH"

# Common system paths (usually already in PATH)
# /usr/bin:/bin:/usr/sbin:/sbin
```

#### Detect and Add Missing Paths Automatically

Before running any CLI tool, check if it's in PATH. If not found, detect common installation locations and add them:

```bash
# Example: Ensure az CLI is in PATH
if ! command -v az >/dev/null 2>&1; then
    # Try common locations
    for brew_path in "/opt/homebrew/bin" "/usr/local/bin"; do
        if [ -x "$brew_path/az" ]; then
            export PATH="$brew_path:$PATH"
            break
        fi
    done
fi
```

#### Never Use Hardcoded Paths

❌ **BAD** - Using hardcoded paths:
```bash
/opt/homebrew/bin/az account show
/usr/local/bin/terraform plan
```

✅ **GOOD** - Using PATH:
```bash
export PATH="/opt/homebrew/bin:$PATH"
az account show
terraform plan
```

#### Standard PATH Setup Pattern

For every terminal command that uses CLI tools, use this pattern:

```bash
# Setup PATH first
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"

# Then run CLI tools normally
az --version
terraform --version
python --version
```

#### Verify Tools Are Available

After setting PATH, verify tools are accessible:

```bash
export PATH="/opt/homebrew/bin:$PATH"
if ! command -v az >/dev/null 2>&1; then
    echo "Error: az CLI not found in PATH" >&2
    exit 1
fi
az --version
```

### Common CLI Tool Locations

| Tool | macOS (Apple Silicon) | macOS (Intel) | Linux |
|------|----------------------|---------------|-------|
| Homebrew | `/opt/homebrew/bin` | `/usr/local/bin` | `/home/linuxbrew/.linuxbrew/bin` |
| User local | `$HOME/.local/bin` | `$HOME/.local/bin` | `$HOME/.local/bin` |
| System | `/usr/bin` | `/usr/bin` | `/usr/bin` |

### PATH Priority Order

1. User-specific paths (e.g., `$HOME/.local/bin`)
2. Package manager paths (e.g., `/opt/homebrew/bin`)
3. System paths (e.g., `/usr/bin`)

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

