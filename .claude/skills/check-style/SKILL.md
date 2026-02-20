---
name: check-style
description: Check a LaTeX file against the Euclid Consortium Editorial Board (ECEB) Style Guide V4.0. Use when the user asks to check style, lint, or review a .tex file for ECEB compliance.
user-invocable: true
allowed-tools: Bash(python3:*), Read, Glob, Grep
argument-hint: <path-to-tex-file>
---

# ECEB Style Guide Checker

Run the automated style linter and provide a contextual review of a LaTeX
file against the Euclid Consortium Editorial Board Style Guide V4.0.

## Workflow

### Step 1: Run the automated linter

Run the linter on the target file:

```bash
python3 lint_euclid_style.py <FILE>
```

Also run with `--json` to capture structured output for analysis:

```bash
python3 lint_euclid_style.py --json <FILE>
```

### Step 2: Review for false positives

Read each flagged line in context (5 lines before and after). Dismiss
false positives where the flagged text is:
- Inside a custom macro definition (`\newcommand`, `\def`)
- Part of a proper noun or institution name
- Inside a code listing or verbatim block the linter may have missed
- A deliberate stylistic choice with good reason (e.g. matching an
  external catalogue's naming convention)

### Step 3: Check items that cannot be automated

The linter does not check everything. Manually review for:

**Structural completeness:**
- Abstract present and within word limit (~250 words)
- All figures referenced in text
- All tables referenced in text
- Acknowledgements section present with `\AckEC`

**Figure quality:**
- Axis labels legible at print size
- Colour-blind-safe colour maps (no rainbow/jet)
- All figures have captions
- Font sizes consistent across figures

**Cross-figure consistency:**
- Same quantity plotted with same axis range across figures
- Consistent colour coding (e.g. bands always same colours)
- Consistent symbol/line styles

**Physics consistency:**
- Units consistent throughout (same unit for same quantity)
- Magnitude systems stated (AB vs Vega)
- Coordinate frames stated when relevant

**Citation format:**
- EC papers use "Euclid Collaboration: Author et al. (year)" format
- arXiv references use correct bibcode format
- All citations resolve (no `??` in compiled output)

### Step 4: Produce the report

Present findings in a prioritised list:

1. **Critical** (errors from linter) — must fix before submission
2. **Warnings** (warnings from linter + manual findings) — should fix
3. **Suggestions** (suggestions + style improvements) — consider fixing

For each finding, include:
- Line number and rule ID (for automated findings)
- The problematic text (quoted)
- The suggested fix
- Style Guide section reference

End with a summary count: `N critical, M warnings, K suggestions`.

## Rule categories

The linter checks 6 categories with 44 rules:

| Category | ID prefix | Examples |
|----------|-----------|----------|
| Naming & Terminology | N01-N12 | Euclid italicisation, instrument names, data set, compound hyphens |
| British English | E01-E08 | US→UK spellings, per cent, catalogue |
| Units & Numbers | U01-U07 | Exponent notation, thin spaces, thousands separator |
| LaTeX Typesetting | T01-T12 | TeX quotes, en-dashes, paragraph breaks, figure stretching |
| References & Citations | R02-R05 | EC citation format, \AckEC, commented text, arXiv redundancy |
| Style Guide Specific | S01-S05 | Dec/RA, data plural, waveband italics, Universe capitalisation |

## Example output format

```
## Style Check: paper.tex

### Critical (3)
1. **Line 47 [E01]**: "color" → "colour" (Sect. 2.4.1)
2. **Line 112 [N05]**: "dataset" → "data set" (Sect. 2.4.34)
3. **Line 203 [U01]**: "km/s" → "km s^{-1}" (Sect. 2.2.8)

### Warnings (2)
1. **Line 15 [N01]**: "Euclid" should be italicised (Sect. 3.6)
2. **Figure 3**: Axis label font too small for print

### Suggestions (1)
1. **Line 250 [R03]**: Commented-out paragraph — remove before arXiv

**Summary**: 3 critical, 2 warnings, 1 suggestion
```

## Notes

- The linter script is at `lint_euclid_style.py` (top-level)
- Reference: ECEB Style Guide V4.0
- Some rules are warnings because they have legitimate exceptions
- The `--category` flag can focus on specific rule groups
- Return code: 0 = clean, 1 = warnings only, 2 = errors found
