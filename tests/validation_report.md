# ECEB Style Linter Validation Report

**Date**: 2026-07-22
**Linter**: `lint_euclid_style.py` v0.7.0 (56 rules, 6 categories, ECEB Style Guide V5)
**Test papers**: VIS DR1 paper (post-A&A-editorial ground truth), its Q1
predecessor (pre-editorial), and the synthetic test fixture.

The previous report (2026-02-20, 44 rules, validated against EP-I Wide Survey,
Euclid I Overview, Euclid II VIS, and one user paper; 100% precision on
non-debatable findings) is preserved in git history and remains valid for the
rules it covered. This pass validates the v0.6.0/v0.7.0 increments: the V5
section remap, the four editor-derived rules (N17, T15, T16, T17), and the
N01/N02 product-name changes.

---

## Why these targets

The VIS DR1 paper (`DR1-OUVIS.tex`) went through A&A editorial review in
July 2026 and was then fixed against ~30 explicit editor comments, so it is
fresh ground truth in both directions: the linter should be **quiet** on
everything the editor made the authors fix, and anything it still flags should
be a genuine leftover. The Q1 predecessor (`q1-ouvis.tex`, same Overleaf
project) predates those fixes, so the editor-derived rules should **fire** on
it — a recall check on real prose.

---

## Triage: VIS DR1 paper (post-editorial)

19 findings, **all true positives, zero false positives**.

| Rule | Count | Verdict | Notes |
|------|-------|---------|-------|
| R03 | 12 | **TP** (low value) | Dead/template comments: A&A template boilerplate ("Now you can add appendices"), two internal Redmine issue URLs, one commented-out paragraph, one dead `\textbf` note. All genuinely worth removing before arXiv, but half are template boilerplate every paper carries. Suggestion severity is right. |
| T16 | 6 | **TP** | `\emph{Top row:}`, `\emph{Middle row:}`, `\emph{Bottom row:}`, `\emph{Left:}`, `\emph{Top panel:}`, `\emph{Bottom panel:}` — colon inside the italics; guide Sect. 2.8 item 6 explicitly puts the colon outside. Line 182 even mixes wrong `\emph{Left:}` with correct `\emph{Right}:` in one caption. Multi-line caption tracking verified on the real 4-line caption at L180–183. |
| T17 | 1 | **TP** | L284: `\end{equation}` + blank line + "where $\alpha$ and $\delta$ denote…" — spurious paragraph indent mid-sentence. The paper's other equation continuation (L301–304) uses the correct `%` glue line, confirming the authors know the convention; this one survived editorial review. |

### Silence checks (the important part)

- **N17 (Gaia italic)**: 0 findings on a paper with ~25 `\Gaia`/`\Gaia\`
  usages, `\textit{Gaia}` in a caption, `\alpha_{\rm Gaia}` in math, and the
  `\providecommand{\Gaia}` definition. All correctly skipped. True negative —
  the paper fixed editor comment #17 and the linter agrees.
- **T15 (`\cref` at sentence start)**: 0 findings against 21 mid-sentence
  `\cref` and 9 sentence-initial `\Cref`. True negative — editor comment #20
  fixed, linter agrees.
- **N01 (Euclid italic)**: 0 findings after this pass's guard fixes (see
  below); the paper's ~30 `\Euclid` usages and the roman product names are
  all accepted.
- **N02, U10**: silent — "Euclid DR1" roman and `42\,092`-style separators
  are all correct in the fixed paper.

---

## Triage: Q1 predecessor (pre-editorial)

37 findings after the FP fixes below; all triaged as true positives.

| Rule | Count | Verdict | Notes |
|------|-------|---------|-------|
| N17 | 25 | **TP** | Bare "Gaia DR3 reference catalogue", "Gaia sources", "Gaia filter response functions", "Gaia synthetic magnitudes", "Gaia colours", "(Gaia SourceID …)" — exactly the defect class the A&A editor later flagged on DR1 (#17). Recall confirmed on real prose. |
| N05 | 3 | **TP** | "dataset" → "data set". |
| E02 | 3 | **TP** | "percent" → "per cent". |
| N02 | 2 | **TP** | `\Euclid Deep Field` (guide: roman) and `\Euclid Q1` (product name, caught by this pass's extension). |
| T16 | 2 | **TP** | `\textit{Left panel:}` etc., colon inside italics. |
| T01 | 1 | **TP** | `` `` goal" `` — opened with TeX quotes, closed with a straight `"`. |
| R03 | 1 | **TP** | Commented-out text. |

---

## False positives found and fixed in this pass

Each fix has a regression marker in `tests/test_lint_euclid_style.tex`.

| Issue | Rule | Root cause | Fix | Regression test |
|-------|------|-----------|-----|-----------------|
| "the Euclid \ac{DR1}" / "\acl{DR1}" (DR1 paper ×2) | N01 | Acronym macro after "Euclid" invisible to the proper-noun guard | Skip `Euclid \ac…{` | CLEAN: N01 ×2 |
| "VIS Euclid DR1" (DR1 paper) | N01 | "DR1" not in proper-noun suffixes | Skip `Euclid (DR\|Q)\d` | CLEAN: N01 |
| "Euclid Ultra-Deep Field" (DR1 paper) | N01 | `\w+` suffix match stops at the hyphen | Allow hyphenated suffix; add "Ultra-Deep" | CLEAN: N01 |
| Gaia SourceID 1440758225532172032 (Q1 paper) | U08 | 19-digit identifier treated as a quantity | Skip integers ≥ 10 digits and integers after ID-designator words | EDGE: U08-gaia-source-id, U08-long-integer, U08-source-id, U08-ident |
| "\ac{CCD} 6-2" detector designation (Q1 paper) | T02 | Acronym guard accepted `\ac{CCD}6-2` but not the spaced form | Allow `}` between acronym and space | EDGE: T02-ccd-space |

Also closed in the same pass (a false-**negative**, found while triaging the
N01 hits): editor comment #2 ("Euclid DR1" must be roman) was credited to N02
in the 0.7.0 notes, but N02's suffix list had no product names, so
`\Euclid DR1` went undetected. N02 now flags `\Euclid DR1`, `\Euclid\ Q1`,
`\textit{Euclid} \ac{DR1}`, and "Ultra-Deep Field(s)" (EXPECT: N02 ×3,
CLEAN: N02 ×1).

---

## Editor-comments coverage (VIS DR1, ~30 comments)

- **Caught by existing rules**: #3 4-digit separator → U10.
- **Caught by the v0.7.0 rules**: #2 "Euclid DR1" roman → N02 (extension this
  pass); #17 *Gaia* italic → N17; #20 "Fig. 9" at sentence start → T15;
  #16 panel words in `\emph` → T16; #10 no indent after equation → T17.
- **Deliberately not built** (heuristic, high FP risk; revisit only with a
  flag-for-review severity): #4 Oxford comma, #6/#15 term case/hyphen
  consistency, #8 "Sect. N of \cite" lowercase, #9/#13 "wide survey" → EWS,
  #25/#26 word-pair en-dash, #30 `.bib` collaboration colon (needs `.bib`
  input support).
- **Not automatable in LaTeX**: #14/#23 semicolons, #22 punctuation,
  #24 parentheses, #18 redundant "mag" in prose.
- **Wrong layer**: #18/#27 axis-label units live in matplotlib scripts, not
  the `.tex` source.

## Drafted rules: decisions

- **T16** — **built** (see above). Confirmed to be an actual ECEB V5 rule
  (Sect. 2.8, Figures, item 6: "typing `\emph{Left}:` … the colon is outside
  the brackets"), not merely an A&A editorial preference, so it carries a
  section citation.
- **T17** — **built** (see above). Grounded in Sect. 2.5 item 1 (a blank
  line always starts a new paragraph); validated by a surviving defect in the
  post-editorial DR1 paper (L284) and a correct counter-example (L302 `%`
  glue).
- **R02 extensions** (`\authorrunning` format, `.bib` collaboration-colon
  mode) — **deferred**: needs `.bib` input support, a new input mode for a
  single-file `.tex` linter. Revisit if a second DR1-era paper shows the
  same defects.
- **R04 extension** (`\AckDRone` + `\cite{DR1cite}` presence) — **not
  built**: too release-specific for a general ECEB linter.

---

## Precision & recall summary

- **VIS DR1 (post-editorial)**: 19/19 true positives, 0 FP.
  **Precision: 100%.** All five editor-derived defect classes that the paper
  fixed are correctly silent; the three finding classes it still contains
  (dead comments, colon-inside descriptors, one blank-line-after-equation)
  are genuine leftovers.
- **Q1 (pre-editorial)**: 37/37 true positives after fixes, 0 FP.
  N17 recall on real prose: 25/25 bare-Gaia mission references found, with
  no FP on author lists, `\providecommand` definitions, math subscripts, or
  file paths.
- **Synthetic fixture**: 201 tests pass — 75 EXPECT, 75 CLEAN, 49 EDGE,
  1 document-level.

## Remaining known limitations

1. **Included files are not followed**: `\input{authors}` etc. are not
   linted; run the linter per file. Author-list `.tex` files are mostly
   preamble-like and report little.
2. **R03 flags template boilerplate**: about half its hits on a real paper
   are A&A-template comments every paper carries. Acceptable at suggestion
   severity.
3. **T16 covers descriptor-with-colon forms only**: a caption that describes
   panels in running prose without colons ("the middle panel in the second
   row corresponds to…") is what the guide asks authors to avoid, but it is
   not machine-separable from legitimate prose, so it is not flagged.
4. **`.bib` files are not linted** (blocks the R02 collaboration-colon
   extension).
5. **Multi-line inline math** spanning source lines is not parsed (known
   single-line-parser limitation).
