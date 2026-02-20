# ECEB Style Linter Validation Report

**Date**: 2026-02-20
**Linter**: `lint_euclid_style.py` (44 rules, 6 categories)
**Test papers**: 3 ECEB-reviewed papers + 1 user paper + 1 synthetic test file

## Summary

| Paper | Errors | Warnings | Suggestions | Total |
|-------|--------|----------|-------------|-------|
| EP-I: Wide Survey (2108.01201) | 19 | 59 | 31 | 109 |
| Euclid II: VIS (2405.13492) | 1 | 4 | 0 | 5 |
| Euclid I: Overview (2405.13491) | 6 | 29 | 4 | 39 |
| User paper (aa54594-25) | 6 | 3 | 1 | 10 |
| Synthetic test file | 45 EXPECT, 0 FP on CLEAN | | | 114 tests |

---

## Triage: EP-I Wide Survey (2108.01201)

This is an older paper (2021) that pre-dates strict ECEB style enforcement.
Most findings are genuine issues that were not corrected at time of publication.

### Errors (19 total)

| Rule | Count | Verdict | Notes |
|------|-------|---------|-------|
| E01 | 10 | **TP** | US spellings: "optimized" x3, "realized" x2, others |
| E02 | 3 | **TP** | "percent" → "per cent" |
| E07 | 3 | **TP** | "catalog" → "catalogue" |
| N05 | 3 | **TP** | "dataset" → "data set" |

### Warnings (59 total)

| Rule | Count | Verdict | Notes |
|------|-------|---------|-------|
| N01 | 33 | **TP** | Bare "Euclid" not italicised (pre-dates \Euclid macro) |
| N12 | 2 | **TP** | "point like" → "point-like" |
| S03 | 1 | **TP** | Waveband letter not italicised |
| S05 | 2 | **TP** | "the sun" → "the Sun" |
| T01 | 5 | **Debatable** | Straight quotes in institution names |
| T02 | 4 | **TP** | Hyphen in number ranges → en-dash |
| T06 | 1 | **TP** | URL not wrapped in \url{} |
| T08 | 1 | **TP** | Abbreviation at sentence start |
| T12 | 1 | **TP** | Colon before displayed equation |
| U03 | 3 | **TP** | Missing thin space before unit |
| U07 | 6 | **Debatable** | Thousands separator (some may be intentional) |

### Suggestions (31 total)

| Rule | Count | Verdict | Notes |
|------|-------|---------|-------|
| R03 | 31 | **Debatable** | Commented-out text (mostly editorial instructions) |

---

## Triage: Euclid II VIS (2405.13492)

Very clean paper — only 5 findings.

| Rule | Count | Severity | Verdict | Notes |
|------|-------|----------|---------|-------|
| E02 | 1 | error | **TP** | "percent" → "per cent" |
| N01 | 2 | warning | **TP** | Bare "Euclid" not italicised |
| S03 | 1 | warning | **TP** | Waveband letter not italicised |
| T08 | 1 | warning | **TP** | Abbreviation at sentence start |

---

## Triage: Euclid I Overview (2405.13491)

### Errors (6 total — all True Positives)

| Line | Rule | Verdict | Notes |
|------|------|---------|-------|
| 3155 | E02 | **TP** | "percent" in caption text — should be "per cent" |
| 3182 | E02 | **TP** | "percent" in body text — should be "per cent" |
| 3662 | E02 | **TP** | "percent" in body text — should be "per cent" |
| 4274 | E02 | **TP** | "percent" in body text — should be "per cent" |
| 3348 | N05 | **TP** | "dataset" — should be "data set" |
| 4198 | S04 | **TP** | "data is" — should be "data are" |

### Warnings (29 total)

| Rule | Count | Verdict | Notes |
|------|-------|---------|-------|
| N01 | 2 | **TP** | Bare "Euclid" in caption/body |
| S05 | 1 | **TP** | "the universe" → "the Universe" |
| T01 | 17 | **Debatable** | Straight quotes in Italian institution names |
| T02 | 5 | **TP** (4) / **Debatable** (1) | Number ranges; 1 is programme name "2020-2025" |
| T05 | 1 | **TP** | Bare `\\` as paragraph break |
| T12 | 3 | **TP** | Colon before displayed equation |

### Suggestions (4 total)

| Rule | Count | Verdict | Notes |
|------|-------|---------|-------|
| R03 | 4 | **Debatable** | ECEB editorial instructions in comments |

---

## Triage: User Paper (aa54594-25)

| Line | Rule | Severity | Verdict | Notes |
|------|------|----------|---------|-------|
| * | E02 (x3) | error | **TP** | "percent" — should be "per cent" |
| * | N02 | warning | **TP** | Italicised Euclid in proper-noun phrase |
| * | N05 (x3) | error | **TP** | "dataset" — should be "data set" |
| * | R03 | suggestion | **Debatable** | Commented-out text |
| * | T01 | warning | **TP** | Straight double quote |
| * | T02 | warning | **TP** | Hyphen in number range |

---

## False Positives Fixed During Validation

| Issue | Rule | Root Cause | Fix | Regression test |
|-------|------|-----------|-----|-----------------|
| ORCID IDs (0000-0002-...) | T02 | Regex matching digit-hyphen-digit | `(?<![-\\\d])` lookbehind + skip `\orcid{}`/`\inst{}` lines | EDGE: T02-orcid |
| Postal codes (277-8583) | T02 | Digit-hyphen-digit in addresses | Skip lines with `\label{aff` | EDGE: T02-address |
| LaTeX umlauts (`\"o`) | T01 | `\"` is accent, not straight quote | `(?<!\\)` lookbehind | (inherent in regex) |
| "practice" (noun) | E01 | Noun form valid in BrE | Removed from `_US_UK_SPELLINGS` dict | (inherent) |
| `\begin{center}` | E01 | "center" in LaTeX command | Added `begin`/`end` to `_remove_commands` | EDGE: (tested via block) |
| "Center for X" (institution) | E01 | Capitalised proper noun | Skip if followed by institutional preposition | EDGE: E01-institution |
| "R.A." detection | S01 | Trailing `\b` fails after `.` | Changed to `(?=\s\|$\|[^A-Za-z])` lookahead | EXPECT: S01 |
| `{\tt Euclid Emulator}` | N01 | Software name in monospace | Skip if `\tt`/`\texttt` in context | EDGE: N01-tt |
| "HE Space" (company) | N04 | Not a band name | Skip if followed by capitalised word | (inherent) |
| V9E 2E7 (postal code) | U05 | Catalogue ID with "E" | Skip if preceded by letter / `\label{aff` | EDGE: U05-postal |
| 1E0657 (cluster name) | U05 | Catalogue ID with "E" | Skip if followed by 3+ digits | (inherent) |
| Affiliation `\\` (EP-I) | T05 | `\\` in `\institute{}` block | Skip `$^{`, `\inst{`, `\orcid{` lines | EDGE: T05-affiliation |
| supertabular `\\` (EP-I) | T05 | `supertabular` not in `_TABULAR_ENVS` | Added to `_TABULAR_ENVS` | (inherent) |
| `\multicolumn` `\\` (EP-I) | T05 | Table header outside env | Skip `\multicolumn`, `\tablehead` etc. | (inherent) |
| `\footnote{}` `\\` (EP-I) | T05 | Line break inside footnote | Skip if `\footnote` on line/prev line | (inherent) |
| "the galaxy" (generic) | S05 | Any specific galaxy, not Milky Way | Removed "galaxy" from target list | EDGE: S05-generic-galaxy |
| "power law with" (noun) | N12 | Standalone noun, not compound adj | Positive noun-follow list for "power law" etc. | EDGE: N12-noun |

---

## Precision & Recall Metrics

### EP-I: Wide Survey (after fixes)

**Excluding debatable (T01 institution names, R03 editorial, U07 separators):**

- True Positives: 67 (N01 x33, E01 x10, E02 x3, E07 x3, N05 x3, N12 x2, S03 x1, S05 x2, T02 x4, T06 x1, T08 x1, T12 x1, U03 x3)
- False Positives: 0
- Debatable: 42 (T01 x5, R03 x31, U07 x6)
- **Precision: 100%** (67/67 non-debatable are genuine)

### Euclid II: VIS

- True Positives: 5 (E02 x1, N01 x2, S03 x1, T08 x1)
- False Positives: 0
- **Precision: 100%** (5/5)

### Euclid I: Overview (after fixes)

**Excluding debatable (T01 Italian names, R03 editorial, T02 programme name):**

- True Positives: 17 (E02 x4, N01 x2, N05 x1, S04 x1, S05 x1, T02 x4, T05 x1, T12 x3)
- False Positives: 0
- Debatable: 22 (T01 x17, R03 x4, T02 x1)
- **Precision: 100%** (17/17 non-debatable)

### User Paper (aa54594-25)

- True Positives: 9 (E02 x3, N02 x1, N05 x3, T01 x1, T02 x1)
- False Positives: 0
- Debatable: 1 (R03)
- **Precision: 100%** (9/9 non-debatable)

### Synthetic Test File

- 45 EXPECT lines: 45/45 detected (100% recall)
- 44 CLEAN lines: 0/44 false triggers (100% precision)
- 27 edge cases: 0/27 false positives
- 1 document-level rule: detected
- **114 total test cases, all passing**

### Coverage

Rules with at least 1 TP across all test files: E01, E02, E03, E04, E05, E06,
E07, E08, N01, N02, N03, N04, N05, N06, N07, N08, N09, N10, N11, N12, U01,
U02, U03, U05, U07, T01, T02, T04, T05, T06, T08, T09, T10, T11, T12, R02,
R03, R05, S01, S02, S03, S04, S05 = **43/44**
(R04 fires on synthetic only = 44/44 including synthetic)

**Coverage: 100%** (all rules have at least 1 TP in the test suite)

---

## Remaining Known Limitations

1. **T01 Italian institution names**: Straight quotes in official institution
   names (e.g., Dipartimento di Fisica "G. Galilei") are flagged. These are
   technically incorrect LaTeX but are present in ECEB-approved papers as-is.
   Could be addressed by skipping lines with `\label{aff` for T01.

2. **R03 editorial comments**: Comments like "please do not edit the author
   list" are flagged as dead text. These are instructions, not dead text.
   Low severity (suggestion) so acceptable.

3. **Multi-line inline math**: The parser is single-line; inline math spanning
   lines is not handled. This is a known limitation.

4. **`\ac{}` variants**: The linter handles `\ac{}`, `\acl{}`, `\acf{}`,
   `\acp{}`, `\acs{}` but not all acronym package variants.

5. **S05 "galaxy" omitted**: "the galaxy" is too ambiguous in astronomy papers
   (usually means a specific galaxy, not the Milky Way). Only "the universe",
   "the sun", and "the solar system" are checked.
