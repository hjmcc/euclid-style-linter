# Changelog

All notable changes to `euclid-style-linter` will be documented here. The
project follows [Semantic Versioning](https://semver.org):

- **MAJOR** — breaking changes (ECEB style-guide version bump, rule
  removal/renaming, CLI-incompatible changes).
- **MINOR** — new rules, new CLI flags, behaviour changes that can make
  a previously-clean paper report new violations.
- **PATCH** — false-positive fixes, bug fixes, internal refactoring
  with no intended change to rule output.

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
