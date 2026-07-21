# Changelog

All notable changes to `euclid-style-linter` will be documented here. The
project follows [Semantic Versioning](https://semver.org):

- **MAJOR** — breaking changes (ECEB style-guide version bump, rule
  removal/renaming, CLI-incompatible changes).
- **MINOR** — new rules, new CLI flags, behaviour changes that can make
  a previously-clean paper report new violations.
- **PATCH** — false-positive fixes, bug fixes, internal refactoring
  with no intended change to rule output.

## 0.7.0 — 2026-07-22

Four new rules distilled from the A&A editor's comments on the VIS DR1 paper
(the ones that are cleanly machine-detectable; several other comments are
heuristic or need human judgement and were left out deliberately), plus
false-positive fixes found in a validation pass against the post-editorial
VIS DR1 paper and its Q1 predecessor.

### Added

- **N17** (warning, Sect. 3.6): *Gaia* (mission name) should be italicised as
  `\Gaia` or `\textit{Gaia}` — the *Gaia* sibling of N01/N02 for *Euclid*.
  Skips `\Gaia`, `\textit{Gaia}`, "Gaia Collaboration/Consortium" (roman proper
  nouns), `\ac{}`, monospace software names, and filenames/URLs in
  `\includegraphics`/`\url`/`\href`.
- **T15** (warning, Sect. 2.3): a lowercase `\cref`/`\ref`/`\eqref` at a
  sentence start should be the capitalised `\Cref` (which renders
  "Figure/Section", not lowercase/abbreviated). Extends T08's sentence-boundary
  logic (via `ctx.prev_raw_line`) to reference macros; guarded against "et al."
  / "e.g." false boundaries. Accepts `\Cref` and mid-sentence `\cref`.
- **T16** (warning, Sect. 2.8): panel descriptors in captions should be
  italicised with the colon outside the italics — `\emph{Left}:`, not bare
  `Left:` and not `\emph{Left:}`. Only descriptor-with-colon forms inside
  `\caption{}` are flagged (prose such as "the right panel shows" stays
  roman); multi-line captions are tracked by brace depth.
- **T17** (warning, Sect. 2.5): a blank line between a displayed equation and
  continuation text that starts lowercase creates a spurious paragraph
  indent — remove the blank line (or glue with a `%` line). Silent when the
  following text starts a genuine (capitalised) paragraph.

### Fixed

- **N01** no longer flags roman "Euclid" in data-product/release names —
  "Euclid DR1", "Euclid Q1", "Euclid \ac{DR1}"/"\acl{DR1}" — per the A&A
  editorial ruling on the VIS DR1 paper, nor in "Euclid Ultra-Deep Field"
  (proper-noun field name, same class as "Euclid Deep Fields").
- **N02** now conversely flags *italicised* Euclid in those product names
  (`\Euclid DR1`, `\Euclid\ Q1`, `\textit{Euclid} \ac{DR1}`), and covers
  "Ultra-Deep Field(s)". This closes a gap: editor comment #2 ("Euclid DR1"
  must be roman) was previously credited to N02 but not actually detected.
- **U08** no longer flags long integers that are identifiers, not
  quantities: integers of 10+ digits (e.g. 19-digit Gaia source IDs) and
  integers preceded by an ID-designator word ("SourceID", "IDENT", "ID").
- **T02** no longer flags detector designations in acronym-macro form with a
  space, e.g. "\ac{CCD} 6-2" (the guard accepted "\ac{CCD}6-2" but missed
  the spaced form).
- **README rule table**: the per-rule Section column still showed V4
  three-level numbers (e.g. `2.4.1`, `2.5.10`); reconciled all 41 stale rows
  to the two-level V5 sections the code emits (audited via `ast`, not regex).

### Notes

- 201 tests pass (34 new EXPECT/CLEAN/EDGE cases in the fixture).
- Validation: on the post-editorial VIS DR1 paper the linter reports 19
  findings, all true positives (12 R03 dead comments, 6 T16 colon-inside
  descriptors, 1 T17 spurious paragraph) and zero false positives; N17/T15
  correctly stay silent on heavy `\Gaia`/`\cref` usage. See
  `tests/validation_report.md`.
- Editor comment #3 (4-digit thousands separator) was already covered by
  **U10**.

## 0.6.0 — 2026-07-17

Reconciled all style-guide section references from **ECEB V4.0** to **V5**.
Rule *logic* is unchanged — a previously-clean paper stays clean; only the
`(Sect. …)` citation in each finding changed. Bundled here per the policy that
an ECEB version bump is a major change.

### Added

- **U10** (warning, Sect. 2.5): 4-digit integers must not carry a thousands
  separator — the inverse of U08. Flags `1\,900`, `1{,}900`, a bare-comma
  `1,900`, and a space-separated `3 000` (a reference-word guard skips
  cross-references such as "Sect. 4 300"); numbers typeset in math such as
  `$4\,352$` are still checked, while 5+-digit numbers and `\num{}` arguments
  are left alone. **U07** now defers 4-digit bare-comma numbers to U10 (it
  only fires on 5+-digit numbers) so the two rules never give contradictory
  advice.

### Changed

- V5 numbers sections at two levels (e.g. `2.4`, `2.5`); the V4 third-level
  rule numbers (`2.4.34`, `2.5.10`, …) no longer exist, so all `sg_section`
  values are now two-level V5 sections.
- Four rules moved section in V5, remapped accordingly:
  - **R02, R05** (citations) `2.6 → 2.7` (References is now 2.7).
  - **T06** (wrap bare URL in `\url`) `2.9 → 2.10` (Active links).
  - **R03** (commented-out text) `2.3 → 2.6` (General recommendations).
  - **S05** (survey-name capitalisation) `3.3 → 2.3`.
- **N04** (Euclid subscript-E band notation) stays at **3.5** (The Euclid
  photometric system) — verified, not moved.
- Version strings, argparse/help text, and the bundled PDF reference updated
  to "Style Guide V5"; `docs/Euclid_Style_Guide_V5.pdf` added (gitignored, as
  with V4.0).

### Fixed

- **N03** (instrument name in `\textsc`) had a stray `"CLAUDE.md"` in its
  `sg_section` field — a long-standing bug that made it print
  "(Sect. CLAUDE.md)". Set to **2.3** (name/abbreviation capitalisation).
  Caught during the V5 audit.

### Notes

- Reconciled against `Euclid_Style_Guide-5.pdf` (V5.1, uploaded 2026-07-07).
- Every one of the 52 rules was audited (via `ast`) to a valid V5 section.
- Three topic→section mappings are judgement calls where V5 has no dedicated
  rule (R03 → 2.6, N03 → 2.3, S05 → 2.3); revisit if a later V5 revision adds
  explicit rules.
- The `check-style` skill (`claude-skills-dotfiles`) still says "V4.0" in its
  prose — a separate repo, not updated here.

## 0.5.1 — 2026-05-29

Documentation-only release. No change to rule logic, CLI, or output.

### Fixed

- **`check-style` skill** (`SKILL.md`) was stale against v0.5.0: it
  advertised "44 rules" and outdated category ranges (N01-N12,
  U01-U07, T01-T12).  Corrected to **52 rules** with current ranges
  (N01-N16, U01-U09, T01-T14) and refreshed examples for the newer
  rules.  Documented the `--severity` flag and the v0.5.0 terminal
  output behaviour (severity grouping, source context, `By rule:`
  footer).
- Confirmed `README.md` and `CLAUDE.md` already matched the true
  count of 52 rules (49 line + 2 paragraph-level + 1 document-level
  `R04`, which lives outside `_LINE_RULES`/`_PARA_RULES`).

## 0.5.0 — 2026-05-24

UX overhaul of the terminal and Gradio output to make scanning long
reports easier.  Rule logic and JSON output are unchanged.

### Changed

- **Terminal output** now groups findings by severity
  (errors → warnings → suggestions) instead of one flat
  chronological list.  Each finding is followed by ±1 line of source
  context with a caret pointing at the offending column.  A trailing
  `By rule:` footer lists rule IDs by frequency (top offenders first)
  so you can see at a glance whether you have one systemic problem
  or many independent ones.
- **Gradio app** mirrors the same layout: sections per severity, a
  rule-frequency line at the top, and an HTML context block per
  finding with the offending character highlighted.

### Added

- `--flat` CLI flag — restore the legacy line-ordered output.
- `--no-context` CLI flag — omit the ±1 line source-context snippet.

### Notes

- JSON output (`--json`) is unchanged for stability of CI/editor
  consumers.

## 0.4.1 — 2026-05-24

False-positive fixes from a user-reported review of the linter's
output.

### Fixed

- **N01** — no longer flag `Euclid` when it appears inside an
  `\includegraphics{...}` or `\graphicspath{...}` filename or path
  (e.g. `\includegraphics{Figures/Euclid.pdf}`). Graphics-command
  bodies are now blanked out before the rule scans the line.
- **T02** — broaden the catalogue-name exception to accept Title-case
  prefixes (e.g. `Abell 1689-23`, `Hickson 92-3`, `Markarian 421-12`)
  in addition to all-caps prefixes (`NGC`, `ESO`, `SDSS`, `2MASS`).
- **U08** — `\num{15000}`, `\qty{15000}{km}` etc. (siunitx number
  macros) are no longer flagged. `num`, `numlist`, `numrange`, `qty`,
  `qtylist`, `qtyrange` were added to the command-strip list used by
  `_clean_text_line`.

### Changed

- **U08** — suggestion text now mentions `\num{N}` (siunitx) as an
  alternative to the `\,` thin-space form.

### Added

- Six new EDGE regression markers covering the three fixes above.
  Test count: 152 → 158.

## 0.3.0 — 2026-04-20

Incorporates feedback from an Euclid Consortium Editorial Board (ECEB)
editor on early output from the linter.

### Fixed (ECEB editor feedback)

- **N01** — do not flag `Euclid` when it sits at the tail of a
  Title-cased compound project name (e.g. *Cosmology Likelihood for
  Observables in Euclid*, *Likelihood Tool for Euclid*). Previously
  N01 only inspected the word *after* `Euclid`.
- **T08** — a LaTeX source line wrap is not a sentence boundary.
  Abbreviations such as `Sect.` / `Fig.` at the start of a source line
  are now only flagged when the previous non-blank line ends in
  sentence-terminating punctuation (and not with `et al.`, `e.g.`,
  `i.e.`, `cf.`, `vs.`).

### Fixed (other)

- **T04** — now scans operators (`log`, `sin`, etc.) inside `\(...\)`,
  `\[...\]`, and `equation` / `align` / other math environments, not
  just inline `$...$`.
- **N04 / T02** — skip catalogue and star names such as `HE 0107-5240`,
  `SDSS J0100-1234`, `2MASS …`.
- **R03** — commented-out-text heuristic rewritten from a bare
  40-character threshold to *≥ 4 words and (contains a full stop or
  ≥ 8 words)*. Catches short prose comments while still ignoring
  `TODO:` markers and decorative dividers.
- **E01** — removed `license → licence` (noun/verb ambiguity in BrE)
  and `dialog → dialogue` (valid in software/UI contexts) from the US
  → UK spelling map. Deduplicated a double-entered `minimize` key.
- **`_strip_comments`** — correctly counts trailing backslashes so
  `\\%` (even number) begins a comment while `\%` (odd number) is
  escaped.
- **`TexContext`** — mismatched `\end{...}` now unwinds the
  environment stack to the matching `\begin`, rather than silently
  desyncing subsequent math-mode detection.
- **`app.py`** — `demo.launch()` is guarded by
  `if __name__ == "__main__":` so the module can be imported without
  starting the Gradio server.
- Removed a dead `_RAW_LINE_RULES` dispatch branch in `lint_file`.

### Added

- `__version__` constant in `lint_euclid_style.py` and a `--version`
  CLI flag.
- Linter version shown in the Gradio header on the Hugging Face Space.
- Nine new EXPECT / EDGE regression markers for the cases above.
  Test count: 114 → 123.

## 0.2.0 — 2026-02

- Added 8 new rules derived from the ECEB template and validated on
  three published Euclid papers. Total: 44 rules across 6 categories.
  (`dfe700e`)

## 0.1.0 — 2026-02

- Initial release: 36 rules, regression test suite, CLI. (`41a19bd`)
