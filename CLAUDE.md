# euclid-style-linter

Automated LaTeX linter for the Euclid Consortium Editorial Board (ECEB) Style
Guide V4.0. Extracted from the [EUDF-DR1](https://github.com/hjmcc/EUDF-DR1)
pipeline as a stand-alone tool.

## Working Rules

- This is a **zero-dependency, single-file** Python project. Do not add external
  dependencies. Everything must work with Python 3.9+ stdlib only.
- The linter has been **validated against published ECEB papers** with 100%
  precision on non-debatable findings. Every change to a rule must preserve this
  precision — add a regression test (EXPECT or EDGE marker) before modifying
  rule logic.
- False-positive suppression is critical. When adjusting regex patterns, check
  that the change does not regress on the synthetic test file or real papers.
- Rules are grouped into 6 categories (N, E, U, T, R, S). New rules must follow
  the existing naming convention: `check_XX` method + entry in `_LINE_RULES`
  and `_CATEGORY_MAP`.

---

## Quick Start

```bash
# Run the linter
python3 lint_euclid_style.py paper.tex

# Run the test suite
python3 -m pytest tests/ -v

# JSON output (for editors/CI)
python3 lint_euclid_style.py --json paper.tex

# Filter by category or severity
python3 lint_euclid_style.py --category naming --severity warning paper.tex
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | No issues found |
| 1 | Warnings or suggestions only |
| 2 | Errors found (or file not found) |

---

## File Organization

```
euclid-style-linter/
├── lint_euclid_style.py              # Main linter (single file, ~1350 lines)
├── README.md                         # User-facing documentation
├── LICENSE                           # MIT
├── CLAUDE.md                         # This file
├── .claude/skills/check-style/       # Claude Code skill for /check-style
│   └── SKILL.md
├── docs/                             # Reference material (not committed)
│   ├── Euclid_Style_Guide_V4.0.pdf  # ECEB Style Guide V4.0
│   └── euclid_template/             # A&A template for EC papers
└── tests/
    ├── test_lint_euclid_style.py     # pytest regression suite (114 cases)
    ├── test_lint_euclid_style.tex    # Synthetic test file with markers
    ├── validation_report.md          # Triage of findings on real papers
    └── run_eceb_validation.sh        # Cross-validation script
```

---

## Architecture

The linter is a single-file, line-by-line processor with five layers:

1. **Text processing** — `_strip_comments`, `_remove_math`, `_clean_text_line`:
   LaTeX-aware extraction of prose from raw source lines.
2. **Context tracking** — `TexContext` class: maintains an environment stack
   (math, verbatim, tabular), preamble state, and document-level flags.
3. **Rule methods** — `StyleChecker.check_N01` through `check_S05` (44 rules):
   each receives `(lineno, raw_line, cleaned_text, ctx)` and returns a list of
   `Violation` namedtuples.
4. **Rule registry** — `_LINE_RULES`, `_RAW_LINE_RULES`, `_CATEGORY_MAP`:
   dispatch tables that map rule IDs to methods and categories.
5. **Output** — terminal (ANSI coloured) or JSON; CLI via `argparse`.

### Key design decisions

- **No AST parsing**: regex-based, operating on single lines. Fast and simple
  but cannot detect multi-line constructs.
- **Per-rule false-positive suppression**: context-aware guards (e.g. E01 skips
  proper nouns; U05 skips catalogue IDs; T02 skips ORCIDs).
- **Validation-driven development**: every FP fix during paper validation gets a
  corresponding EDGE regression test.

---

## Testing

### Test file markers (`tests/test_lint_euclid_style.tex`)

| Marker | Meaning |
|--------|---------|
| `% EXPECT: <rule_id>` | Line **must** trigger this rule |
| `% CLEAN: <rule_id>` | Line must **not** trigger this rule |
| `% EXPECT_DOC: <rule_id>` | Document-level rule (checked at end of file) |
| `% EDGE: <label>` | Edge case that must produce **no** violations |

### Adding a new test case

1. Add a line to `tests/test_lint_euclid_style.tex` with the appropriate marker.
2. Run `python3 -m pytest tests/ -v` to confirm the new case passes.
3. For false-positive regressions, use `% EDGE:` with a descriptive label.

### Cross-validation on real papers

```bash
# Place paper tarballs in tests/eceb_papers/, then:
bash tests/run_eceb_validation.sh
```

---

## Adding a New Rule

1. Add a `check_XX` method to `StyleChecker` following the existing pattern.
2. Add the rule ID to `_LINE_RULES` (or `_DOC_RULES` for document-level checks).
3. Add the rule ID to `_RAW_LINE_RULES` if it needs the unstripped raw line.
4. Add the rule ID to the appropriate category in `_CATEGORY_MAP`.
5. Add at least one `EXPECT` and one `CLEAN` line to the test file.
6. Update the rules table in `README.md`.
7. Run the full test suite and, if possible, validate on a real paper.
