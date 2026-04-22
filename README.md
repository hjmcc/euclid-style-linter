---
title: ECEB Style Linter
emoji: 🔭
colorFrom: blue
colorTo: indigo
sdk: gradio
app_file: app.py
pinned: false
license: mit
---

# euclid-style-linter

Lint LaTeX files against the [Euclid Consortium Editorial Board (ECEB) Style Guide V4.0](https://www.euclid-ec.org/).

Checks 44 rules across 6 categories: naming/terminology, British English,
units/numbers, LaTeX typesetting, references/citations, and Euclid-specific
conventions. Reports violations with line number, rule ID, severity, and the
relevant Style Guide section.

This tool is not an official product of the ECEB. 

## Installation

No dependencies beyond Python 3.9+. Just clone and run:

```bash
git clone https://github.com/<you>/euclid-style-linter.git
cd euclid-style-linter
```

## Usage

```bash
# Basic usage
python3 lint_euclid_style.py paper.tex

# Only show warnings and errors (skip suggestions)
python3 lint_euclid_style.py --severity warning paper.tex

# JSON output (for editors/CI)
python3 lint_euclid_style.py --json paper.tex

# Check only specific categories
python3 lint_euclid_style.py --category naming --category english paper.tex
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | No issues found |
| 1 | Warnings or suggestions only |
| 2 | Errors found (or file not found) |

### Example output

```
paper.tex

  Line 47   [E01] ERROR      US spelling "color" → British "colour" (Sect. 2.4.1)
  Line 112  [N05] ERROR      "dataset" → "data set" (two words, no hyphen) (Sect. 2.4.34)
  Line 203  [U01] ERROR      "km/s" → use exponent notation "km\,s$^{-1}$" (Sect. 2.2.8)
  Line 15   [N01] WARNING    "Euclid" should be italicised as \Euclid or \textit{Euclid} (Sect. 3.6)

Summary: 3 errors, 1 warnings (4 total)
```

## Rules

| ID | Category | Severity | Description | Section |
|:--:|:---------|:---------|:------------|:------:|
| N01 | Naming | warning | *Euclid* (mission/spacecraft) should be italicised | 3.6 |
| N02 | Naming | warning | *Euclid* should NOT be italicised in proper-noun phrases | 3.6 |
| N03 | Naming | error | Do not use `\textsc` for instrument names | -- |
| N04 | Naming | warning | Euclid band names should use subscript-E notation | 3.5 |
| N05 | Naming | error | "dataset"/"data-set" should be "data set" | 2.4.34 |
| N06 | Naming | error | "comprised of" should be "composed of" or "comprises" | 2.4.39 |
| N07 | Naming | error | "publically" should be "publicly" | 2.4.40 |
| N08 | Naming | warning | "S/N ratio" is redundant -- use "S/N" alone | 2.4.44 |
| N09 | Naming | error | "modelisation" should be "modelling" | 2.4.8 |
| N10 | Naming | error | "associated to" should be "associated with" | 2.4.9 |
| N11 | Naming | warning | "allow to [verb]" — transitive verb needs an object | 2.4 |
| N12 | Naming | warning | Compound adjective missing hyphen ("point like" etc.) | 2.4 |
| E01 | British English | error | US spellings that should be British (50+ words) | 2.4.1 |
| E02 | British English | error | "percent" should be "per cent" | 2.4.1 |
| E03 | British English | error | "gray" should be "grey" | 2.4.1 |
| E04 | British English | error | "acknowledgment" should be "acknowledgement" | 2.4.1 |
| E05 | British English | error | "modeling" should be "modelling" | 2.4.1 |
| E06 | British English | error | "labeled" should be "labelled" | 2.4.1 |
| E07 | British English | error | "catalog" should be "catalogue" | 2.4.1 |
| E08 | British English | error | "favor" should be "favour" | 2.4.1 |
| U01 | Units | error | Compound units with "/" should use exponents | 2.2.8 |
| U02 | Units | error | Plural unit abbreviations (units are never pluralised) | 2.2.2 |
| U03 | Units | warning | Missing thin space (`\,`) before unit | 2.2.6 |
| U05 | Units | warning | Powers of 10: use `$3 \times 10^{5}$`, not `3e5` | 2.5.13 |
| U07 | Units | warning | Thousands separator: use `\,` or `{,}`, not bare comma | 2.5.22 |
| T01 | Typesetting | warning | Straight double quotes -- use ` `` ` and `''` | 2.5.3 |
| T02 | Typesetting | warning | Hyphen in number range -- use en-dash `--` | 2.5.4 |
| T04 | Typesetting | warning | Math operators without backslash (e.g. `log` not `\log`) | 2.5.10 |
| T05 | Typesetting | warning | `\\` used as paragraph break -- use blank lines | 2.5.1 |
| T06 | Typesetting | warning | URL not wrapped in `\url{}` or `\href{}` | 2.9 |
| T08 | Typesetting | warning | Abbreviation at sentence start (write out in full) | 2.3.19 |
| T09 | Typesetting | error | `\includegraphics` with both width and height (stretching) | 2.8 |
| T10 | Typesetting | warning | Adjacent parentheses `)(` — merge or use semicolon | 2.5 |
| T11 | Typesetting | error | `\acknowledgement{}` command — use environment instead | 3.4 |
| T12 | Typesetting | warning | Colon before displayed equation — equations are sentences | 2.5 |
| R02 | References | warning | EC citation should use "Euclid Collaboration:" format | 2.6.7 |
| R03 | References | suggestion | Commented-out text (arXiv source is public) | 2.3.17 |
| R04 | References | suggestion | Missing `\AckEC` acknowledgements macro | 3.4 |
| R05 | References | warning | "arXiv e-prints" redundancy in bibliography | 2.6 |
| S01 | Style | error | "DEC" should be "Dec", "R.A." should be "RA" | 2.3.10 |
| S02 | Style | error | "non" before capitals needs hyphen ("non-Gaussian") | 2.4.41 |
| S03 | Style | warning | Waveband letters should be italicised | 2.4.28 |
| S04 | Style | error | "data is/was/has" -- data is plural in Euclid style | 2.4.35 |
| S05 | Style | warning | "the universe/galaxy/sun" — capitalise when referring to ours | 3.3 |

## Categories

Filter rules by category with `--category`:

| Flag | Rules |
|------|-------|
| `naming` | N01--N12 |
| `english` | E01--E08 |
| `units` | U01, U02, U03, U05, U07 |
| `typesetting` | T01, T02, T04--T06, T08--T12 |
| `references` | R02--R05 |
| `style` | S01--S05 |

## Testing

```bash
python3 -m pytest tests/ -v
```

The test suite includes 114 regression tests: 45 expected violations, 44 clean
counterparts, 27 edge cases, and 1 document-level rule. All tests verify both
that violations fire where expected and that false positives are suppressed.

## Claude Code integration

This repo includes a [Claude Code](https://claude.com/claude-code) skill
definition at `.claude/skills/check-style/SKILL.md`. After cloning, use:

```
/check-style paper.tex
```

This runs the automated linter and adds a manual review of items that cannot
be automated (figure quality, cross-references, citation format).

## Validation

The linter has been validated against published ECEB-reviewed papers:
- EP-I: Wide Survey (arXiv:2108.01201)
- Euclid II: VIS (arXiv:2405.13492)
- Euclid I: Overview (arXiv:2405.13491)
- One additional published EC paper

Results: **100% precision** on non-debatable findings across all papers, with
17 false-positive fixes applied during validation. See
`tests/validation_report.md` for the full triage.

## Versioning

The linter follows [Semantic Versioning](https://semver.org):

- **MAJOR** — ECEB style-guide version bump, rule removal/renaming, or
  any CLI-incompatible change.
- **MINOR** — new rules, new CLI flags, or behavioural changes that
  may make a previously-clean paper newly report violations.
- **PATCH** — false-positive fixes, bug fixes, refactoring with no
  intended change to rule output.

The current version is in `__version__` in `lint_euclid_style.py`
(also reported by `python3 lint_euclid_style.py --version`). See
[`CHANGELOG.md`](CHANGELOG.md) for release notes.

## License

MIT
