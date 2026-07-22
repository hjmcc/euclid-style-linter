---
name: check-style
description: Check a LaTeX file against the Euclid Consortium Editorial Board (ECEB) Style Guide V5. Use when the user asks to check style, lint, or review a .tex file for ECEB compliance.
user-invocable: true
allowed-tools: Bash(python3:*), Read, Glob, Grep
argument-hint: <path-to-tex-file>
---

# ECEB Style Guide Checker

Run the automated style linter and provide a contextual review of a LaTeX
file against the Euclid Consortium Editorial Board Style Guide V5. The
target file is the skill argument.

## Workflow

### Step 1: Run the automated linter

Run the linter once with `--json` (it carries everything the terminal
output does, in a form you can parse — do not also run the plain form):

```bash
python3 lint_euclid_style.py --json <FILE>
```

Two caveats that produce silently-incomplete results:

- The linter only checks content **inside
  `\begin{document}` … `\end{document}`**. A bare snippet reports almost
  nothing and looks deceptively clean.
- `\input{}` / `\include{}` files are **not followed**. If the paper is
  split across files, run the linter on each included `.tex` file too.

### Step 2: Review for false positives

Read each flagged line in context (a few lines either side). A finding is
suspect where the flagged text is:
- Inside a custom macro definition (`\newcommand`, `\def`)
- Part of a proper noun or institution name
- Inside a code listing or verbatim block the linter may have missed
- A deliberate stylistic choice with good reason (e.g. matching an
  external catalogue's naming convention)

This is the linter's own repository and its rules are validated to 100%
precision on real papers, so a genuine false positive is rare — and it is
a **linter defect, not something to dismiss silently**. Report it as such
in your findings and propose the fix: a guard in the rule method plus a
regression marker (`% CLEAN:` or `% EDGE:`) in
`tests/test_lint_euclid_style.tex`.

### Step 3: Check items that cannot be automated

The linter does not check everything. Manually review for:

**Structural completeness:**
- Abstract present and within word limit (~250 words)
- All figures referenced in text
- All tables referenced in text

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

Rules are grouped by ID prefix. The rule table in `README.md` is the
authoritative, always-current list — rules are added regularly, so do not
rely on remembered counts or ID ranges.

| Prefix | Category | Examples |
|--------|----------|----------|
| N | Naming & Terminology | Euclid/Gaia italicisation, instrument names, data set, compound hyphens |
| E | British English | US→UK spellings, per cent, catalogue |
| U | Units & Numbers | Exponent notation, thin spaces, thousands separators |
| T | LaTeX Typesetting | TeX quotes, en-dashes, \Cref at sentence start, caption panel descriptors |
| R | References & Citations | EC citation format, \AckEC, commented text |
| S | Style Guide Specific | Dec/RA, data plural, waveband italics |

## Example output format

```
## Style Check: paper.tex

### Critical (3)
1. **Line 47 [E01]**: "color" → "colour" (Sect. 2.4)
2. **Line 112 [N05]**: "dataset" → "data set" (Sect. 2.4)
3. **Line 203 [U01]**: "km/s" → "km s^{-1}" (Sect. 2.2)

### Warnings (2)
1. **Line 15 [N01]**: "Euclid" should be italicised (Sect. 3.6)
2. **Figure 3**: Axis label font too small for print

### Suggestions (1)
1. **Line 250 [R03]**: Commented-out paragraph — remove before arXiv

**Summary**: 3 critical, 2 warnings, 1 suggestion
```

## Notes

- The linter script is at `lint_euclid_style.py` (top-level)
- Reference: ECEB Style Guide V5
- Some rules are warnings because they have legitimate exceptions
- `--category` focuses on specific rule groups; `--severity` filters by
  level; `--dialect us` skips the British-English (E) rules for non-ECEB
  papers (the ECEB mandates British English, so the default is `gb`);
  `--release none` disables the DR1-specific checks (R06: `\AckDRone`
  and `\cite{DR1cite}` presence) for papers not based on DR1 data
- Return code: 0 = clean, 1 = warnings/suggestions only, 2 = errors found
