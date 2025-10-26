#!/usr/bin/env bash
# Validate all Mermaid diagrams in docs/diagrams using mermaid-cli (mmdc) and check_mermaid.js
# Usage:
#   scripts/validate_diagrams.sh              # validate all diagram markdown files
#   scripts/validate_diagrams.sh changed      # validate only staged diagram files
#   scripts/validate_diagrams.sh file1.md ... # validate specific files
#
# Requirements:
#   - Node available
#   - Either global mmdc or npx will fetch @mermaid-js/mermaid-cli@11.12.0
#   - check_mermaid.js present at repo root (lightweight static checks)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIAGRAM_DIR="$REPO_ROOT/docs/diagrams"
CHECK_SCRIPT="$REPO_ROOT/check_mermaid.js"
MERMAID_VERSION="11.12.0"
MMDCCMD=${MMDCCMD:-"npx @mermaid-js/mermaid-cli@${MERMAID_VERSION}"}

if [[ ! -d "$DIAGRAM_DIR" ]]; then
  echo "Diagram directory not found: $DIAGRAM_DIR" >&2
  exit 1
fi
if [[ ! -f "$CHECK_SCRIPT" ]]; then
  echo "check_mermaid.js not found at repo root. Aborting." >&2
  exit 1
fi

# Collect target files
mapfile -t FILES < <(case "${1:-all}" in
  changed)
    git diff --name-only --cached | grep '^docs/diagrams/.*\.md$' || true ;;
  all)
    find "$DIAGRAM_DIR" -maxdepth 1 -type f -name '*.md' | sort ;;
  *)
    for f in "$@"; do
      if [[ -f "$f" ]]; then echo "$f"; elif [[ -f "$DIAGRAM_DIR/$f" ]]; then echo "$DIAGRAM_DIR/$f"; else echo "Skip missing $f" >&2; fi
    done ;;
 esac)

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No diagram files selected." >&2
  exit 0
fi

failures=0

validate_file() {
  local file="$1"
  echo "\n==> Validating: $file" >&2
  # Run static checker (JS script) - non-fatal warnings allowed
  node "$CHECK_SCRIPT" "$file" || { echo "check_mermaid.js reported issues for $file" >&2; }
  # Extract mermaid code fences and pipe to mmdc
  local tmp
  tmp="$(awk '/```mermaid/{flag=1;next}/```/{if(flag){flag=0}}flag' "$file")"
  if [[ -z "$tmp" ]]; then
    echo "No mermaid block found, skipping mmdc." >&2
    return 0
  fi
  # Feed to mermaid-cli
  if ! printf '%s\n' "$tmp" | eval "$MMDCCMD" -i /dev/stdin -o /dev/null 2>"$file.mmdc.log"; then
    echo "ERROR: mermaid-cli parse failed: $file" >&2
    sed -e '1,120p' "$file.mmdc.log" >&2 || true
    failures=$((failures+1))
  else
    echo "OK: $file" >&2
    rm -f "$file.mmdc.log"
  fi
}

for f in "${FILES[@]}"; do
  [[ -n "$f" ]] || continue
  validate_file "$f"
done

if [[ $failures -ne 0 ]]; then
  echo "\nValidation completed with $failures failure(s)." >&2
  exit 1
fi

echo "\nAll selected diagrams passed validation." >&2
