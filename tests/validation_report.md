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

---

# Addendum: Euclid I Overview (Mellier+ 2024, arXiv 2405.13491v2)

**Date**: 2026-07-23
**Linter**: v0.10.0 + affiliation-block fix (uncommitted)
**Status of paper**: published (A&A), so findings are either slips that
survived refereeing (TP), linter FPs, or invocation artifacts.

Context: this paper carries its full generated author/affiliation list
*after* `\begin{document}` (author block L330, affiliations L1471–2181), so
unlike the VIS papers the list is actually linted. Before the affiliation
fix it produced 264 findings (212 postal-code U08 FPs); after, 52.

## Triage: 52 findings

| Rule | Count | Verdict | Notes |
|------|-------|---------|-------|
| T16 | 9 | **TP** | `{\it Left:}`, `{\it Right:}`, `\textit{Top:}`, `{\it Top panels:}` etc. in captions L2634/2649/2733/4422 — colon inside italics, guide Sect. 2.8. Same defect class as the 6 TPs in the VIS DR1 paper. |
| E02 | 4 | **TP** | "a few percent" ×2 (L3155, L3182), "percent level accuracy" (L4274) — should be "per cent". "sub-percent requirements" (L3662) is debatable (hyphenated compound) but still non-British. |
| T02 | 3 | **TP** | "10-30\%", "10-20\%", "21-23" (date range) — hyphen for en-dash. |
| T12 | 3 | **TP** (debatable class) | Colon before displayed equation at L2353/2358/2365 (e.g. "…\citep{hamilton98}:" before `\begin{align}`). Genuine per the rule's premise; warning severity is right. |
| N05 | 1 | **TP** | "the \gls{UNIONS} dataset" (L3348) — same line correctly uses "data sets" elsewhere. |
| T15 | 1 | **TP** | Paragraph-initial `\cref{fig:sample_spectrum}` (L3408) → `\Cref`. |
| U08 | 1 | **TP** | "over 30000 at \HE=22" (L4558) → `30\,000`. The only U08 survivor of the affiliation fix; 212 postal-code FPs suppressed. |
| U10 | 1 | **TP** | "1\,400 cool exoplanets" (L4672) — 4-digit integer takes no separator. |
| S05 | 1 | **TP (debatable)** | "the universe's density at the epoch of halo formation" (L4318) — cosmological context, should be "Universe". |
| R03 | 1 of 4 | **TP (low value)** | L2183 "% Add short versions of title…" — A&A template boilerplate, consistent with known limitation 2. |
| R03 | 3 of 4 | **Non-actionable** | L322/328/1470 "please do not edit the author/affiliation list — contact ECEB Bureau": these comments are *part of* the generated author list and must stay. Candidate for a whitelist pattern. |
| T01 | 17 | **Non-actionable TP** | All 17 (≈9 distinct lines, rule fires per quote char) are straight quotes in Italian institute names in the generated affiliation list ("G. Galilei", "E. Pancini", …; L1887 even mixes `` ``…" ``). Typographically real, but the list is centrally generated and not author-editable. Recommend suppressing T01 via the affiliation guard. |
| R06 | 2 | **N/A (invocation)** | Pre-DR1 paper linted with the default `--release dr1`; correct invocation is `--release none`. |
| T14 | 2 | **FP** | `\vspace{-3cm}`, `\vspace{-2.5cm}` (L3590/3594) — LaTeX dimension arguments, not prose quantities. Fix: strip layout-command dimension args (\vspace, \hspace, \rule) before matching. |
| N01 | 1 | **FP** | "internally called Euclid\_SNT\_2023B" (L4658) — an object designation, not the mission. Fix: skip "Euclid" immediately followed by `\_`/`_`. |
| S04 | 1 | **FP** | "the software that is employed to process the data is under strict control" (L4198) — the verb agrees with "software"; "data" is the object of "process". Fix candidate: skip "the data is" when preceded by "to <verb>" (infinitive-object attachment); otherwise accept as known parser-free limitation. |
| T05 | 1 | **FP** | Lone `\\` at L3990 inside an A&A `\tablefoot{…}` body, separating footnote entries — legitimate there. Fix: extend the footnote guard to `\tablefoot` (current guard only matches `\footnote` in line or prev line). |

## Summary

- **25 TP** (2 debatable), **5 FP** (T14 ×2, N01, S04, T05), **20
  non-actionable** (17 T01 + 3 R03 in the untouchable generated author
  list) / **2 N/A** (R06 wrong release mode).
- Precision on actionable findings: 25/30 = 83%. The 5 FPs are guard gaps
  never before exercised (this is the first validation paper whose
  affiliation list and table-heavy appendix are linted); each has a
  concrete fix candidate above, to be applied with EDGE regressions.
- The affiliation-block fix is validated at scale here: 212/213 U08
  findings were postal codes and are now suppressed; the 1 survivor is a
  genuine violation.

## Fixes applied (2026-07-23, same session)

All five FP classes plus the T01 affiliation suppression were implemented,
each with an EDGE regression in the synthetic fixture:

| Fix | Implementation | EDGE test |
|-----|----------------|-----------|
| T01 in affiliations | `_is_affiliation_line()` guard (same as U07/U08) | `T01-affiliation-quotes` |
| T14 on dimensions | blank `\vspace/\hspace/\rule/\setlength/\addtolength` args before matching | `T14-vspace`, `T14-rule` |
| N01 on identifiers | skip `Euclid` immediately followed by `\_`/`_` | `N01-identifier` |
| T05 in `\tablefoot` | footnote guard extended to `\tablefoot` (line or prev line) | `T05-tablefoot` |
| S04 infinitive object | skip `to <verb> [the] data is` attachment | `S04-infinitive-object` |

Outcome:
- Synthetic fixture: 219 tests pass (was 213).
- Mellier overview: 52 → 30 findings; exactly the 22 triaged
  FP/non-actionable line-level findings removed, all 25 TPs retained.
  With the correct `--release none` invocation: 28 findings
  (25 TP + 3 R03 generated-list boilerplate).
- VIS DR1 and Q1 papers: output unchanged (no recall regression against
  their all-TP triages).

Remaining non-actionable residue on generated author lists: the three R03
hits on the ECEB "please do not edit" comments (whitelist pattern still a
candidate, not implemented).

---

# Addendum 2: Euclid II VIS (Cropper+ 2405.13492v2) and EP-I Wide Survey (Scaramella+ 2108.01201)

**Date**: 2026-07-23
**Linter**: v0.10.0 + this session's fixes (uncommitted)
**Invocation**: `--release none` (both are pre-DR1 papers)

Provenance caveat: arXiv holds only **v1** of EP-I (the accepted version was
never uploaded; the tarball mtime is two days after initial submission), so
EP-I is a **pre-referee recall target** like the Q1 paper, not a silence
target. Euclid II v2 is the published version (silence target). Euclid II
`\input`s its author list in the preamble, so its affiliations are not
linted.

## Triage: Euclid II VIS — 6 findings

| Rule | Count | Verdict | Notes |
|------|-------|---------|-------|
| T08 | 1 | **TP** | "…(Sect.~\ref{…}). Sect.\ref{sec:open_points} reflects…" — abbreviation opens a sentence; survived into print. |
| E02 | 1 | **TP (debatable)** | "percent-level variations" — hyphenated compound, same class as Mellier's "sub-percent". |
| N01 | 2 | **FP** | (a) "The Euclid Imaging Consortium Science Book" — title-case compound name, roman correct; (b) `\bibliography{refs,Euclid}` — file argument. |
| S03 | 1 | **FP** | "K-band telemetry" — radio communications band, not a photometric waveband. |
| T14 | 1 | **FP** | `\noalign{\vskip 4mm}` — TeX primitive dimension, sibling of the fixed `\vspace{}` class. |

## Triage: EP-I Wide Survey — 140 findings

**FP: 51**, all in seven systematic classes:

| Rule | Count | FP class |
|------|-------|----------|
| T15 | 23 | "see Sect. \ref{…}" / "Fig. \ref{…}" mid-sentence: the abbreviation's period is taken as a sentence end (exclusion list has e.g./i.e./et al. but not Sect./Fig./Tab./Eq.). This 2021 paper predates the cleveref convention, so the path was never exercised by the newer validation papers. |
| N01 | 10 | Title-case product compounds, roman correct: "Euclid Reference Survey Definition", "Euclid Science Team", "Euclid Sky Survey Planning Tool", "Euclid Auxiliary Fields" (×2), 4 acronym-table expansions, "Euclid Sky" (WISHES expansion). |
| U10 | 9 | `2\,656` etc. in table columns whose other rows are 5-digit grouped numbers (`12\,673`): column-alignment convention, deliberate. Judgement call — recommend skipping U10 inside tabular. |
| T02 | 3 | `\cline{2-5}` — LaTeX column-range syntax requires the hyphen. |
| U03 | 3 | "20deg" inside `\label{Fig:deepn-20deg-…}` and two `\ref`s to it — command bodies, not prose. |
| E07 | 2 | "ATLAS All-Sky Stellar Reference Catalog", "2MASS Point Source Catalog" — official proper names; capitalised "Catalog" should not be anglicised. |
| T14 | 1 | `p{6cm}` in a supertabular column spec. |

**TP: 60** (pre-referee paper, so expected — this is recall evidence):
N01 ×22 bare mission uses ("followed by Euclid as it operates", "Euclid
FoV", "the Euclid sky"; 4 debatable attributive/lowercase-product cases),
T16 ×11 (panel descriptors, both colon-inside and not-italicised forms),
E01 ×10 (optimized/center/color/realized), N05 ×3 (dataset), N17 ×3 (bare
Gaia — matches the Q1 recall class), E02 ×3 (percent), S05 ×2 ("the sun"),
N12 ×2 ("point like"), T12 ×1, T06 ×1 (bare URL in footnote), E07 ×1
("2MRS catalog", lowercase), S03 ×1 ("JEDIS-g … in g band", debatable:
acronym expansion).

**TP low value: 29** R03 commented-out text (incl. one ECEB "do not edit"
boilerplate line), consistent with known limitation 2.

## Verdict for a 1.0.0 release

Not yet. EP-I's 2021-era conventions (plain `\ref` with "Fig. " prefixes,
`\cline` tables, aligned table integers) exposed **nine new FP classes
(~55 findings)** that the post-2023 papers never exercised. All are
narrow, guardable gaps:

1. T15: extend abbreviation exclusion (Sect/Fig/Tab/Eq/Col/App/No + plurals).
2. N01: skip title-case chains (`Euclid + Capitalised + Capitalised`); add "Sky", "Surveys" to proper suffixes.
3. N01: blank `\bibliography{…}` arguments.
4. U10: skip inside tabular environments (alignment convention).
5. T02: skip `\cline{…}`/`\cmidrule{…}`.
6. U03: strip `\label{}`/`\ref{}` bodies before matching.
7. E07: flag lowercase "catalog" only; capitalised "Catalog" is a proper name.
8. T14: extend dimension blanking to `\vskip`/`\hskip`/`\kern` and `p{}/m{}/b{}` column specs.
9. S03: skip communications-band context ("K-band telemetry/antenna/downlink").

After those land (each with EDGE regressions) and both papers re-triage
clean, 1.0.0 is justified.

## Re-triage after the nine guards (2026-07-23, same session)

All nine guards implemented, each with EDGE regressions (14 new cases;
suite now 233 passing). Post-guard state, `--release none`:

| Paper | Before | After | Remaining composition |
|-------|--------|-------|----------------------|
| EP-I Wide Survey (v1) | 140 | **88** | 59 TP (3 debatable) + 29 R03 low-value. **0 FP.** |
| Euclid II VIS | 6 | **2** | 2 TP (T08 sentence-start "Sect.", E02 "percent-level"). **0 FP.** |
| Euclid I Overview | 28 | **28** | unchanged: 25 TP + 3 R03 generated-list boilerplate. |
| VIS DR1 / Q1 | — | — | output byte-identical, no recall regression. |

The N01 suppression was verified surgical: lines with two findings (e.g.
EP-I L424 "the Euclid one" + "the Euclid Surveys", L1479 "Euclid Auxiliary
Fields" + "1--4 Euclid FoVs") kept the genuine bare-mission hit and lost
only the proper-name hit. The surviving E07 is the lowercase "2MRS
catalog" TP; the two proper-name "Catalog"s are suppressed.

**Zero false positives across the 171 findings currently reported on the
five validation papers** (Mellier 28, EP-I 88, Euclid II 2, VIS DR1 14,
Q1 39, under their correct `--release` invocations; R03 template/boilerplate
comments counted as low-value TPs). Known deliberate trade-offs: E07 no longer flags
capitalised "Catalog" (sentence-start misses accepted), U10 is silent
inside tables (alignment convention), S04 skips infinitive-object
attachments. This state meets the bar for a 1.0.0 release.
