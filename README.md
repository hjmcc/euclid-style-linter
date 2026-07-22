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

Lint LaTeX files against the [Euclid Consortium Editorial Board (ECEB) Style Guide V5](https://www.euclid-ec.org/).

Checks 57 rules across 6 categories: naming/terminology, British English,
units/numbers, LaTeX typesetting, references/citations, and Euclid-specific
conventions (54 line-level, 2 paragraph-level, 1 document-level). Reports
violations with line number, rule ID, severity, and the relevant Style
Guide section.

This tool is not an official product of the ECEB.

## Try it in the browser

A hosted version runs as a Hugging Face Space (no installation needed;
paste LaTeX source or upload a `.tex` file):
<https://huggingface.co/spaces/insoluble/euclid-style-linter>

## Installation

The linter has no dependencies beyond Python 3.9+. Just clone and run:

```bash
git clone https://github.com/hjmcc/euclid-style-linter.git
cd euclid-style-linter
```

(The optional Gradio web app, `app.py`, powers the Hugging Face Space;
running it locally additionally needs `pip install gradio`.)

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

# American English (skip the British-English rules E01--E08, for
# non-ECEB papers; the ECEB mandates British English, so gb is default)
python3 lint_euclid_style.py --dialect us paper.tex

# Legacy line-ordered output (no severity grouping)
python3 lint_euclid_style.py --flat paper.tex

# Suppress the ±1 line source context shown below each finding
python3 lint_euclid_style.py --no-context paper.tex
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | No issues found |
| 1 | Warnings or suggestions only |
| 2 | Errors found (or file not found) |

### Example output

Findings are grouped by severity (errors → warnings → suggestions),
with ±1 line of source context and a caret pointing at the offending
column. A "By rule" footer surfaces your top offenders:

```
paper.tex

  ERRORS  (2)
  Line 47   [E01] ERROR      US spelling "color" → British "colour" (Sect. 2.4)
           46 │ The previous line.
        →  47 │ The color is wrong.
              │     ^
           48 │ Next line.

  Line 112  [N05] ERROR      "dataset" → "data set" (two words, no hyphen) (Sect. 2.4)
           ...

  WARNINGS  (1)
  Line 15   [N01] WARNING    "Euclid" should be italicised as \Euclid or \textit{Euclid} (Sect. 3.6)
           ...

Summary: 2 errors, 1 warnings (3 total)
By rule: E01 ×1, N05 ×1, N01 ×1
```

Use `--flat` for the legacy line-ordered output, or `--no-context` to
omit the source snippets.

## Rules

| ID | Category | Severity | Description | Section |
|:--:|:---------|:---------|:------------|:------:|
| N01 | Naming | warning | *Euclid* (mission/spacecraft) should be italicised | 3.6 |
| N02 | Naming | warning | *Euclid* should NOT be italicised in proper-noun phrases | 3.6 |
| N03 | Naming | error | Do not use `\textsc` for instrument names | 2.3 |
| N04 | Naming | warning | Euclid band names should use subscript-E notation | 3.5 |
| N05 | Naming | error | "dataset"/"data-set" should be "data set" | 2.4 |
| N06 | Naming | error | "comprised of" should be "composed of" or "comprises" | 2.4 |
| N07 | Naming | error | "publically" should be "publicly" | 2.4 |
| N08 | Naming | warning | "S/N ratio" is redundant -- use "S/N" alone | 2.4 |
| N09 | Naming | error | "modelisation" should be "modelling" | 2.4 |
| N10 | Naming | error | "associated to" should be "associated with" | 2.4 |
| N11 | Naming | warning | "allow to [verb]": transitive verb needs an object | 2.4 |
| N12 | Naming | warning | Compound adjective missing hyphen ("point like" etc.) | 2.4 |
| N13 | Naming | warning | `<x>` in math should be `\langle x \rangle` or `\ave{x}` | 2.5 |
| N14 | Naming | warning | `>>` / `<<` in math should be `\gg` / `\ll` | 2.5 |
| N15 | Naming | warning | Compound adjective spanning a line break (paragraph-level) | 2.4 |
| N16 | Naming | warning | Common noun over-capitalised after proper noun ("Fourier Transform") | 2.4 |
| N17 | Naming | warning | *Gaia* (mission) should be italicised as `\Gaia` | 3.6 |
| E01 | British English | error | US spellings that should be British (50+ words) | 2.4 |
| E02 | British English | error | "percent" should be "per cent" | 2.4 |
| E03 | British English | error | "gray" should be "grey" | 2.4 |
| E04 | British English | error | "acknowledgment" should be "acknowledgement" | 2.4 |
| E05 | British English | error | "modeling" should be "modelling" | 2.4 |
| E06 | British English | error | "labeled" should be "labelled" | 2.4 |
| E07 | British English | error | "catalog" should be "catalogue" | 2.4 |
| E08 | British English | error | "favor" should be "favour" | 2.4 |
| U01 | Units | error | Compound units with "/" should use exponents | 2.2 |
| U02 | Units | error | Plural unit abbreviations (units are never pluralised) | 2.2 |
| U03 | Units | warning | Missing thin space (`\,`) before unit | 2.2 |
| U05 | Units | warning | Powers of 10: use `$3 \times 10^{5}$`, not `3e5` | 2.5 |
| U07 | Units | warning | Thousands separator: use `\,` or `{,}`, not bare comma | 2.5 |
| U08 | Units | warning | Integer > 4 digits in prose needs thin-space (`100\,000`) | 2.5 |
| U09 | Units | warning | Scientific notation: use `\times`, not `\,` or `\cdot` before `10^N` | 2.5 |
| U10 | Units | warning | 4-digit integer takes no thousands separator (drop it: `1900`) | 2.5 |
| T01 | Typesetting | warning | Straight double quotes -- use ` `` ` and `''` | 2.5 |
| T02 | Typesetting | warning | Hyphen in number range -- use en-dash `--` | 2.5 |
| T04 | Typesetting | warning | Math operators without backslash (e.g. `log` not `\log`) | 2.5 |
| T05 | Typesetting | warning | `\\` used as paragraph break -- use blank lines | 2.5 |
| T06 | Typesetting | warning | URL not wrapped in `\url{}` or `\href{}` | 2.10 |
| T08 | Typesetting | warning | Abbreviation at sentence start (write out in full) | 2.3 |
| T09 | Typesetting | error | `\includegraphics` with both width and height (stretching) | 2.8 |
| T10 | Typesetting | warning | Adjacent parentheses `)(`: merge or use a semicolon | 2.5 |
| T11 | Typesetting | error | `\acknowledgement{}` command: use the environment instead | 3.4 |
| T12 | Typesetting | warning | Colon before displayed equation (equations are sentences) | 2.5 |
| T13 | Typesetting | warning | `''` used as opening quote (correct opener is `` `` ``) | 2.5 |
| T14 | Typesetting | warning | Number directly attached to physical unit (e.g. `1.5keV`) | 2.2 |
| T15 | Typesetting | warning | Lowercase `\cref`/`\ref` at sentence start: use `\Cref` | 2.3 |
| T16 | Typesetting | warning | Panel descriptor in caption: `\emph{Left}:` (colon outside) | 2.8 |
| T17 | Typesetting | warning | Blank line after equation but sentence continues lowercase | 2.5 |
| R02 | References | warning | EC citation should use "Euclid Collaboration:" format | 2.7 |
| R03 | References | suggestion | Commented-out text (arXiv source is public) | 2.6 |
| R04 | References | suggestion | Missing `\AckEC` acknowledgements macro | 3.4 |
| R05 | References | warning | "arXiv e-prints" redundancy in bibliography | 2.7 |
| S01 | Style | error | "DEC" should be "Dec", "R.A." should be "RA" | 2.3 |
| S02 | Style | error | "non" before capitals needs hyphen ("non-Gaussian") | 2.4 |
| S03 | Style | warning | Waveband letters should be italicised | 2.4 |
| S04 | Style | error | "data is/was/has" -- data is plural in Euclid style | 2.4 |
| S05 | Style | warning | "the universe/galaxy/sun": capitalise when referring to ours | 2.3 |

## Categories

Filter rules by category with `--category`:

| Flag | Rules |
|------|-------|
| `naming` | N01--N17 |
| `english` | E01--E08 |
| `units` | U01, U02, U03, U05, U07--U10 |
| `typesetting` | T01, T02, T04--T06, T08--T17 |
| `references` | R02--R05 |
| `style` | S01--S05 |

## Testing

```bash
python3 -m pytest tests/ -v
```

The test suite includes 202 regression tests: 75 expected violations, 75 clean
counterparts, 49 edge cases, a document-level rule check, and CLI-behaviour
tests (e.g. `--dialect`). All tests verify both that violations fire where
expected and that false positives are suppressed.

## Claude Code integration

This repo includes a [Claude Code](https://claude.com/claude-code) skill
definition at `.claude/skills/check-style/SKILL.md`. After cloning, use:

```
/check-style paper.tex
```

This runs the automated linter and adds a manual review of items that cannot
be automated (figure quality, cross-references, citation format).

## Validation

The linter has been validated in two rounds against real EC papers:

- **Published ECEB-reviewed papers** (EP-I: Wide Survey, arXiv:2108.01201;
  Euclid I: Overview, arXiv:2405.13491; Euclid II: VIS, arXiv:2405.13492;
  plus one additional published EC paper): **100% precision** on
  non-debatable findings, with 17 false-positive fixes applied during
  validation.
- **A paper fresh from A&A editorial review** (VIS DR1, 2026), used as
  ground truth in both directions: the linter is silent on everything the
  editor made the authors fix, and every finding it still reports is a
  genuine leftover (zero false positives). Its pre-editorial predecessor
  served as the recall check for the editor-derived rules.

See `tests/validation_report.md` for the current triage (the earlier round
is preserved in git history).

## Versioning

The linter follows [Semantic Versioning](https://semver.org):

- **MAJOR**: ECEB style-guide version bump, rule removal/renaming, or
  any CLI-incompatible change.
- **MINOR**: new rules, new CLI flags, or behavioural changes that
  may make a previously-clean paper newly report violations.
- **PATCH**: false-positive fixes, bug fixes, refactoring with no
  intended change to rule output.

The current version is in `__version__` in `lint_euclid_style.py`
(also reported by `python3 lint_euclid_style.py --version`). See
[`CHANGELOG.md`](CHANGELOG.md) for release notes.

## License

MIT
