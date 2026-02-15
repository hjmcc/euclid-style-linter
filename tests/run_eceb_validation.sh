#!/bin/bash
# run_eceb_validation.sh — Cross-validate the ECEB style linter against
# published Euclid papers.
#
# Prerequisites:
#   - Paper tarballs placed in tests/eceb_papers/ (user-supplied)
#   - The linter at lint_euclid_style.py
#
# Usage:
#   bash tests/run_eceb_validation.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LINTER="$PROJECT_ROOT/lint_euclid_style.py"
PAPERS_DIR="$SCRIPT_DIR/eceb_papers"
PYTHON="${PYTHON:-python3}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

extract_tar() {
    local tarball="$1"
    local dest="$2"
    mkdir -p "$dest"
    tar xf "$tarball" -C "$dest" 2>/dev/null
}

find_main_tex() {
    local dir="$1"
    # Try common names first
    for name in main.tex paper.tex ms.tex; do
        if [[ -f "$dir/$name" ]]; then
            echo "$dir/$name"
            return
        fi
    done
    # Fall back to largest .tex file
    find "$dir" -maxdepth 1 -name '*.tex' -type f -printf '%s %p\n' 2>/dev/null \
        | sort -rn | head -1 | awk '{print $2}'
}

lint_paper() {
    local label="$1"
    local texfile="$2"

    if [[ ! -f "$texfile" ]]; then
        printf "%-45s  %-7s %-9s %-11s %s\n" "$label" "---" "---" "---" "FILE NOT FOUND"
        return
    fi

    local json
    json=$("$PYTHON" "$LINTER" --json "$texfile" 2>/dev/null || true)

    local total errors warnings suggestions
    total=$(echo "$json" | "$PYTHON" -c "import json,sys; d=json.load(sys.stdin); print(d['total'])")
    errors=$(echo "$json" | "$PYTHON" -c "
import json,sys; d=json.load(sys.stdin)
print(sum(1 for v in d['violations'] if v['severity']=='error'))")
    warnings=$(echo "$json" | "$PYTHON" -c "
import json,sys; d=json.load(sys.stdin)
print(sum(1 for v in d['violations'] if v['severity']=='warning'))")
    suggestions=$(echo "$json" | "$PYTHON" -c "
import json,sys; d=json.load(sys.stdin)
print(sum(1 for v in d['violations'] if v['severity']=='suggestion'))")

    printf "%-45s  %7s %9s %11s %5s\n" "$label" "$errors" "$warnings" "$suggestions" "$total"

    # Save detailed JSON
    local outfile="$PAPERS_DIR/$(echo "$label" | tr ' /()' '____').json"
    echo "$json" > "$outfile"
}

# ---------------------------------------------------------------------------
# Extract papers from tarballs (if any)
# ---------------------------------------------------------------------------

echo "ECEB Style Linter Cross-Validation"
echo "==================================="
echo ""

# Euclid I: Overview (arXiv 2405.13491)
EUCLID_I_TAR="$PAPERS_DIR/arXiv-2405.13491v2.tar"
EUCLID_I_DIR="$PAPERS_DIR/euclid_i"
if [[ -f "$EUCLID_I_TAR" && ! -f "$EUCLID_I_DIR/main.tex" ]]; then
    echo "Extracting Euclid I overview paper..."
    extract_tar "$EUCLID_I_TAR" "$EUCLID_I_DIR"
fi

# Add more papers here as tarballs become available:
# EUCLID_II_TAR="$PAPERS_DIR/arXiv-2405.13492.tar"
# EUCLID_II_DIR="$PAPERS_DIR/euclid_ii"
# if [[ -f "$EUCLID_II_TAR" && ! -f "$EUCLID_II_DIR/main.tex" ]]; then
#     extract_tar "$EUCLID_II_TAR" "$EUCLID_II_DIR"
# fi

# ---------------------------------------------------------------------------
# Run linter on each paper
# ---------------------------------------------------------------------------

echo ""
printf "%-45s  %7s %9s %11s %5s\n" "Paper" "Errors" "Warnings" "Suggestions" "Total"
printf "%-45s  %7s %9s %11s %5s\n" "-----" "------" "--------" "-----------" "-----"

# Euclid I: Overview
EUCLID_I_TEX=$(find_main_tex "$EUCLID_I_DIR" 2>/dev/null || echo "")
lint_paper "Euclid I: Overview (2405.13491)" "$EUCLID_I_TEX"

# Add more papers here:
# lint_paper "Euclid II: VIS (2405.13492)" "$(find_main_tex "$PAPERS_DIR/euclid_ii")"

echo ""
echo "Acceptance criteria: 0 errors, <10 warnings per paper"
echo "  (Errors on a published paper are likely FPs to fix in the linter)"
echo ""
echo "Detailed JSON saved to: $PAPERS_DIR/"
