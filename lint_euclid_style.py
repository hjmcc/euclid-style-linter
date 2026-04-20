#!/usr/bin/env python3
"""
Lint a LaTeX file against the Euclid Consortium Editorial Board (ECEB)
Style Guide V4.0.

Checks 44 rules covering naming/terminology, British English,
units/numbers, LaTeX typesetting, references/citations, and style-guide-
specific conventions.  Reports violations with line number, rule ID,
severity, and the relevant Style Guide section.

Usage:
    python3 lint_euclid_style.py paper.tex
    python3 lint_euclid_style.py --severity warning paper.tex
    python3 lint_euclid_style.py --json paper.tex
    python3 lint_euclid_style.py --category naming paper.tex
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import namedtuple
from pathlib import Path

__version__ = "0.3.0"

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

Violation = namedtuple(
    "Violation", ["line", "col", "rule_id", "severity", "message", "sg_section"]
)

# ---------------------------------------------------------------------------
# Minimal LaTeX-aware context tracker
# ---------------------------------------------------------------------------

# Environments where most text rules should be suppressed
_VERBATIM_ENVS = {
    "verbatim", "lstlisting", "minted", "alltt", "Verbatim",
}
_MATH_ENVS = {
    "equation", "equation*", "align", "align*", "gather", "gather*",
    "multline", "multline*", "eqnarray", "eqnarray*", "math", "displaymath",
    "flalign", "flalign*",
    # Sub-environments that appear inside math
    "aligned", "gathered", "split", "cases", "pmatrix", "bmatrix",
    "vmatrix", "Vmatrix",
}
_TABULAR_ENVS = {"tabular", "tabular*", "tabularx", "longtable", "array",
                  "supertabular", "supertabular*", "mpsupertabular",
                  "mpsupertabular*", "xtabular", "xtabular*"}

_BEGIN_RE = re.compile(r"\\begin\{(\w[\w*]*)\}")
_END_RE = re.compile(r"\\end\{(\w[\w*]*)\}")


class TexContext:
    """Track LaTeX state across lines."""

    def __init__(self):
        self.env_stack: list[str] = []
        self.in_preamble = True
        self.has_ackec = False
        self.custom_commands: set[str] = set()
        self.prev_raw_line: str = ""

    # --- environment queries ------------------------------------------------
    @property
    def in_math_env(self) -> bool:
        return any(e in _MATH_ENVS for e in self.env_stack)

    @property
    def in_verbatim(self) -> bool:
        return bool(self.env_stack and self.env_stack[-1] in _VERBATIM_ENVS)

    @property
    def in_tabular(self) -> bool:
        return any(e in _TABULAR_ENVS for e in self.env_stack)

    # --- per-line update ----------------------------------------------------
    def update(self, line: str, prev_line: str = "") -> None:
        """Update context from a raw source line."""
        self.prev_raw_line = prev_line
        # Detect \begin{document}
        if r"\begin{document}" in line:
            self.in_preamble = False

        # Track \AckEC
        if r"\AckEC" in line:
            self.has_ackec = True

        # Track custom command definitions (to ignore their bodies)
        if re.search(r"\\(new|renew|provide)command", line):
            m = re.search(r"\\(?:new|renew|provide)command\*?\{\\(\w+)\}", line)
            if m:
                self.custom_commands.add(m.group(1))

        # Environment tracking
        for m in _BEGIN_RE.finditer(line):
            self.env_stack.append(m.group(1))
        for m in _END_RE.finditer(line):
            env = m.group(1)
            if not self.env_stack:
                continue
            if self.env_stack[-1] == env:
                self.env_stack.pop()
            elif env in self.env_stack:
                # Mismatched \end{foo}: pop everything above the matching
                # begin, then the matching begin itself, to keep the stack
                # consistent rather than silently desyncing.
                idx = len(self.env_stack) - 1 - self.env_stack[::-1].index(env)
                del self.env_stack[idx:]


# ---------------------------------------------------------------------------
# Line-level helpers
# ---------------------------------------------------------------------------

def _strip_comments(line: str) -> str:
    """Remove LaTeX comment (% to end-of-line), respecting escaped \\%.

    A % is escaped only when preceded by an odd number of backslashes:
    ``\\%`` is escaped, but ``\\\\%`` is a literal backslash followed by a
    comment.
    """
    result = []
    i = 0
    while i < len(line):
        if line[i] == "%":
            # Count contiguous backslashes immediately before this %
            j = i - 1
            backslashes = 0
            while j >= 0 and line[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                break
        result.append(line[i])
        i += 1
    return "".join(result)


def _is_comment_line(line: str) -> bool:
    return line.lstrip().startswith("%")


# Inline math spans: $...$ (not $$...$$)
_INLINE_MATH_RE = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)")
# Also \(...\)
_PAREN_MATH_RE = re.compile(r"\\\(.*?\\\)")
# Display math \[...\]
_BRACKET_MATH_RE = re.compile(r"\\\[.*?\\\]")


def _remove_math(text: str) -> str:
    """Remove inline and display math from text."""
    text = _INLINE_MATH_RE.sub(" MATH ", text)
    text = _PAREN_MATH_RE.sub(" MATH ", text)
    text = _BRACKET_MATH_RE.sub(" MATH ", text)
    return text


_BRACE_GROUP = r"\{(?:[^{}]|\{[^{}]*\})*\}"


def _remove_commands(text: str, commands: list[str]) -> str:
    """Remove content inside specific LaTeX commands like \\url{...}, \\texttt{...}.

    Handles commands with up to two brace-delimited arguments (e.g. \\href{url}{text}).
    """
    for cmd in commands:
        # Match one or two brace groups after the command
        pattern = re.compile(
            r"\\" + re.escape(cmd) + _BRACE_GROUP + r"(?:" + _BRACE_GROUP + r")?"
        )
        text = pattern.sub(" ", text)
    return text


def _clean_text_line(line: str) -> str:
    """Strip comments, math, and command bodies that shouldn't be checked."""
    text = _strip_comments(line)
    text = _remove_math(text)
    text = _remove_commands(
        text,
        ["url", "href", "fnurl", "texttt", "verb", "lstinline",
         "definecolor", "colorlet", "color", "includegraphics",
         "bibliographystyle", "bibliography", "label", "ref", "cref",
         "Cref", "cite", "citep", "citet", "citealt", "citeauthor",
         "citeyear", "eqref", "pageref", "input", "include",
         "usepackage", "graphicspath", "SI", "si", "ang",
         "begin", "end"],
    )
    return text


# ---------------------------------------------------------------------------
# Rule implementations
# ---------------------------------------------------------------------------

class StyleChecker:
    """Collection of ECEB style-guide rules.

    Each check_* method takes (lineno, raw_line, cleaned_text, ctx)
    and returns a list of Violation objects.
    """

    # ===== Category 1: Naming & Terminology ================================

    @staticmethod
    def check_N01(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Euclid (mission/spacecraft) should be italicised."""
        violations = []
        # Proper-noun phrases where Euclid should NOT be italicised
        proper_suffixes = (
            "Consortium", "Collaboration", "Survey", "Deep", "Catalogue",
            "Wide", "Legacy", "Flagship",
            # Geographical terms (e.g. "Euclid Avenue")
            "Avenue", "Street", "Road", "Boulevard",
        )
        # Patterns that indicate correct usage
        correct_patterns = [
            r"\\Euclid\b",          # euclid.sty macro
            r"\\textit\{Euclid\}",  # manual italic
            r"\\emph\{Euclid\}",    # emphasis
            r"\{\\it\s+Euclid\}",   # old-style
            r"\\textit\{\\Euclid\}",  # double-wrapped (harmless)
        ]
        # Skip if the Euclid on this line is via \Euclid or \textit{Euclid}
        stripped = _strip_comments(raw)
        # Find bare 'Euclid' occurrences not preceded by macro backslash
        for m in re.finditer(r"(?<!\\)(?<!\{)\bEuclid\b", stripped):
            pos = m.start()
            # Check it isn't part of a correct pattern
            context_before = stripped[max(0, pos - 20):pos]
            context_after = stripped[pos:pos + 40]
            # Is it inside a proper-noun compound?
            after_word = re.match(r"Euclid\s+(\w+)", context_after)
            if after_word and after_word.group(1) in proper_suffixes:
                continue
            # Is Euclid at the tail of a Title-Cased compound name?
            # E.g. "Cosmology Likelihood for Observables in Euclid"
            # (detected by a capitalised word followed by a small
            # preposition immediately before Euclid).
            if re.search(
                r"\b[A-Z][A-Za-z]+\s+(?:in|of|for|with|on|to|from)\s+$",
                context_before,
            ):
                continue
            # Is it preceded by \textit{ or \emph{?
            if re.search(r"\\textit\{$", context_before):
                continue
            if re.search(r"\\emph\{$", context_before):
                continue
            # Is it preceded by \Euclid (already checked by (?<!\\) but be safe)?
            if re.search(r"\\$", context_before):
                continue
            # Is it inside a \newcommand or \def definition line?
            if re.search(r"\\(new|renew|provide)command", stripped):
                continue
            # Is it inside \ac{} or \acl{} etc?
            if re.search(r"\\ac[lsfp]*\{[^}]*$", context_before):
                continue
            # Is it inside monospace/code font (software names)?
            if re.search(r"\\(?:tt|texttt)\b", context_before):
                continue
            violations.append(Violation(
                lineno, pos, "N01", "warning",
                '"Euclid" should be italicised as \\Euclid or \\textit{Euclid} '
                "(mission/spacecraft name)",
                "3.6",
            ))
        return violations

    @staticmethod
    def check_N02(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Euclid should NOT be italicised in proper-noun phrases."""
        violations = []
        stripped = _strip_comments(raw)
        pattern = re.compile(
            r"(\\textit\{\\?Euclid\}|\\emph\{\\?Euclid\}|\\Euclid)\s*"
            r"(Consortium|Collaboration|Survey|Deep\s+Fields?|Catalogue|Wide\s+Survey|Legacy)"
        )
        for m in pattern.finditer(stripped):
            violations.append(Violation(
                lineno, m.start(), "N02", "warning",
                f'"Euclid {m.group(2)}" is a proper noun — '
                "do not italicise Euclid here",
                "3.6",
            ))
        return violations

    @staticmethod
    def check_N03(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        r"""\\textsc on instrument names (instruments should be upright caps)."""
        violations = []
        instruments = r"VIS|NISP|ACS|WFC3|SPIRE|VLT|DES|HST|JWST|ALMA|NIS"
        pattern = re.compile(r"\\textsc\{[^}]*?(" + instruments + r")[^}]*?\}")
        for m in pattern.finditer(_strip_comments(raw)):
            violations.append(Violation(
                lineno, m.start(), "N03", "error",
                f"Do not use \\textsc for instrument name '{m.group(1)}' "
                "— use upright capitals",
                "CLAUDE.md",
            ))
        return violations

    @staticmethod
    def check_N04(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Euclid band names should use subscript-E notation."""
        violations = []
        # Look for IE, YE, JE, HE as bare text (not in a macro)
        stripped = _strip_comments(raw)
        # Remove known macros \IE \YE \JE \HE
        cleaned = re.sub(r"\\[IYJH]E\b", "", stripped)
        # Remove math subscript notation $_\mathrm{E}$
        cleaned = re.sub(r"_\{?\\mathrm\{E\}\}?", "", cleaned)
        # Remove text inside \ac{} which might contain IE etc.
        cleaned = re.sub(r"\\ac[lsfp]*\{[^}]*\}", "", cleaned)
        # Look for bare IE, YE, JE, HE in text context
        for m in re.finditer(r"\b([IYJH])E\b", cleaned):
            # Skip if inside braces of a command definition
            if re.search(r"\\(new|renew|provide)command", stripped):
                continue
            # Skip if preceded by backslash (it's a macro like \IE)
            pos = m.start()
            if pos > 0 and cleaned[pos - 1] == "\\":
                continue
            # Skip if followed by a capitalised word (company/org name, e.g. "HE Space")
            after = cleaned[m.end():]
            if re.match(r"\s+[A-Z]", after):
                continue
            # Skip catalogue/star names where the letters are a prefix
            # followed by digits, e.g. "HE 0107-5240", "HE~0107", "HE\,0107".
            if re.match(r"(?:\s+|~|\\,)\d", after):
                continue
            violations.append(Violation(
                lineno, pos, "N04", "warning",
                f"Band name '{m.group(0)}' — use Euclid subscript-E notation "
                f"(\\{m.group(0)} or ${m.group(1)}_{{\\mathrm{{E}}}}$)",
                "3.5",
            ))
        return violations

    @staticmethod
    def check_N05(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'dataset' or 'data-set' should be 'data set'."""
        violations = []
        for m in re.finditer(r"\b(dataset|data-set)\b", text, re.IGNORECASE):
            violations.append(Violation(
                lineno, m.start(), "N05", "error",
                f'"{m.group(0)}" \u2192 "data set" (two words, no hyphen)',
                "2.4.34",
            ))
        return violations

    @staticmethod
    def check_N06(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'comprised of' should be 'composed of' or 'comprises'."""
        violations = []
        for m in re.finditer(r"\bcomprised\s+of\b", text, re.IGNORECASE):
            violations.append(Violation(
                lineno, m.start(), "N06", "error",
                '"comprised of" \u2192 "composed of" or "comprises"',
                "2.4.39",
            ))
        return violations

    @staticmethod
    def check_N07(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'publically' should be 'publicly'."""
        violations = []
        for m in re.finditer(r"\bpublically\b", text, re.IGNORECASE):
            violations.append(Violation(
                lineno, m.start(), "N07", "error",
                '"publically" \u2192 "publicly"',
                "2.4.40",
            ))
        return violations

    @staticmethod
    def check_N08(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'S/N ratio' is redundant (S/N already means ratio)."""
        violations = []
        for m in re.finditer(r"S/N\s+ratio", text):
            violations.append(Violation(
                lineno, m.start(), "N08", "warning",
                '"S/N ratio" is redundant \u2192 use "S/N" alone',
                "2.4.44",
            ))
        return violations

    @staticmethod
    def check_N09(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'modelisation' should be 'modelling'."""
        violations = []
        for m in re.finditer(r"\bmodeli[sz]ation\b", text, re.IGNORECASE):
            violations.append(Violation(
                lineno, m.start(), "N09", "error",
                f'"{m.group(0)}" \u2192 "modelling"',
                "2.4.8",
            ))
        return violations

    @staticmethod
    def check_N10(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'associated to' should be 'associated with'."""
        violations = []
        for m in re.finditer(r"\bassociated\s+to\b", text, re.IGNORECASE):
            violations.append(Violation(
                lineno, m.start(), "N10", "error",
                '"associated to" \u2192 "associated with"',
                "2.4.9",
            ))
        return violations

    @staticmethod
    def check_N11(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """"allow to [verb]" / "permit to [verb]" — transitive verb needs object."""
        violations = []
        for m in re.finditer(r"\b(allow|permit|enable)s?\s+to\s+[a-z]", text, re.IGNORECASE):
            word = m.group(1)
            violations.append(Violation(
                lineno, m.start(), "N11", "warning",
                f'"{word} to [verb]" — "{word}" is transitive and needs an '
                f'object (e.g. "{word} one to" or "{word} the detection of")',
                "2.4",
            ))
        return violations

    @staticmethod
    def check_N12(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Compound adjective missing hyphen."""
        violations = []
        # Conservative list of compound adjectives common in astronomy.
        # "point like" and "star forming" are always adjectival.
        # Others require a following noun (not a preposition) to avoid
        # flagging the standalone noun form ("a power law with slope").
        _NOUN_FOLLOW = (
            r"(?=spectr|slope|distribut|model|index|profile|form|function|"
            r"fit|behaviour|behavior|exponent|tail|decay|dependenc|relat|"
            r"natur|approximat|regime|luminosit|structur|survey|pattern|"
            r"cluster|feature|map|simulat|environment|correlat|statistic|"
            r"fluctuat|power|variat|galaxi|emission|stellar|popul)"
        )
        compounds = [
            (r"\bpoint like\b", "point-like"),
            (r"\bstar forming\b", "star-forming"),
            (r"\bpower law\s+" + _NOUN_FOLLOW, "power-law"),
            (r"\btwo point\s+" + _NOUN_FOLLOW, "two-point"),
            (r"\blarge scale\s+" + _NOUN_FOLLOW, "large-scale"),
            (r"\bsmall scale\s+" + _NOUN_FOLLOW, "small-scale"),
        ]
        for pat, fix in compounds:
            for m in re.finditer(pat, text, re.IGNORECASE):
                violations.append(Violation(
                    lineno, m.start(), "N12", "warning",
                    f'Compound adjective "{m.group(0).rstrip()}" '
                    f'should be hyphenated \u2192 "{fix}"',
                    "2.4",
                ))
        return violations

    # ===== Category 2: British English =====================================

    # US -> UK spelling pairs (lowercase); checked case-insensitively
    _US_UK_SPELLINGS = {
        "analyze": "analyse",
        "analyzed": "analysed",
        "analyzing": "analysing",
        "behavior": "behaviour",
        "center": "centre",
        "centered": "centred",
        "centering": "centring",
        "color": "colour",
        "colored": "coloured",
        "coloring": "colouring",
        "customize": "customise",
        "defense": "defence",
        # "dialog" omitted: valid in BrE for software/UI contexts
        # ("dialog box"), where "dialogue" would be wrong.
        "favor": "favour",
        "favorable": "favourable",
        "favored": "favoured",
        "fiber": "fibre",
        "flavor": "flavour",
        "fulfill": "fulfil",
        "gray": "grey",
        "honor": "honour",
        "humor": "humour",
        "initialize": "initialise",
        "initialized": "initialised",
        "judgment": "judgement",
        "labor": "labour",
        # "license" omitted: in BrE the verb is "license" and the noun is
        # "licence"; detecting noun/verb reliably is not possible here.
        "maneuver": "manoeuvre",
        "maximize": "maximise",
        "minimize": "minimise",
        "modeling": "modelling",
        "modeled": "modelled",
        "neighbor": "neighbour",
        "neighboring": "neighbouring",
        "normalize": "normalise",
        "normalized": "normalised",
        "optimize": "optimise",
        "optimized": "optimised",
        "optimizing": "optimising",
        "organization": "organisation",
        "organize": "organise",
        "organized": "organised",
        "paralyze": "paralyse",
        "parameterize": "parameterise",
        "parameterized": "parameterised",
        "polarize": "polarise",
        "polarized": "polarised",
        # "practice" omitted: noun form is correct in BrE; only the verb
        # should be "practise" but detecting noun/verb is unreliable.
        "program": "programme",
        "realize": "realise",
        "realized": "realised",
        "recognize": "recognise",
        "recognized": "recognised",
        "summarize": "summarise",
        "summarized": "summarised",
        "theater": "theatre",
        "utilize": "utilise",
        "utilized": "utilised",
    }

    # Words where the US spelling is also valid in British English in
    # specific contexts (e.g. "program" for software, not "programme")
    _US_EXCEPTIONS = {
        "program",    # computer program (valid in BrE)
        "programs",   # computer programs
    }

    @staticmethod
    def check_E01(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """US spellings that should be British."""
        violations = []
        # Also remove content inside \definecolor, \texttt etc. from text
        check_text = _remove_commands(text, ["definecolor", "colorlet", "texttt"])
        for us, uk in StyleChecker._US_UK_SPELLINGS.items():
            if us in StyleChecker._US_EXCEPTIONS:
                continue
            pattern = re.compile(r"\b" + re.escape(us) + r"\b", re.IGNORECASE)
            for m in pattern.finditer(check_text):
                # Preserve original case for the suggestion
                found = m.group(0)
                # Skip if inside a LaTeX command or path-like context
                before = check_text[max(0, m.start() - 5):m.start()]
                if "\\" in before or "/" in before or "_" in before:
                    continue
                # Skip proper nouns (capitalised, likely institution names)
                if found[0].isupper():
                    before_word = check_text[max(0, m.start() - 20):m.start()]
                    after_word = check_text[m.end():m.end() + 15]
                    # Preceded by another capitalised word
                    if re.search(r"[A-Z]\w*\s+$", before_word):
                        continue
                    # Followed by institutional preposition (e.g. "Center for")
                    if re.match(r"\s+(?:for|of|and|at)\s+", after_word,
                                re.IGNORECASE):
                        continue
                violations.append(Violation(
                    lineno, m.start(), "E01", "error",
                    f'US spelling "{found}" \u2192 British "{uk}"',
                    "2.4.1",
                ))
        return violations

    @staticmethod
    def check_E02(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'percent' should be 'per cent'."""
        violations = []
        for m in re.finditer(r"\bpercent\b", text, re.IGNORECASE):
            # Skip \percent macro or \\% context
            before = text[max(0, m.start() - 2):m.start()]
            if "\\" in before:
                continue
            violations.append(Violation(
                lineno, m.start(), "E02", "error",
                '"percent" \u2192 "per cent" (two words in British English)',
                "2.4.1",
            ))
        return violations

    # E03-E08 are covered by E01's word list; keep individual IDs for
    # specific cases that need special handling.

    @staticmethod
    def check_E03(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'gray' should be 'grey' (outside \\definecolor etc.)."""
        violations = []
        check_text = _remove_commands(text, ["definecolor", "colorlet", "color"])
        for m in re.finditer(r"\bgray\b", check_text, re.IGNORECASE):
            before = check_text[max(0, m.start() - 3):m.start()]
            if "\\" in before:
                continue
            violations.append(Violation(
                lineno, m.start(), "E03", "error",
                '"gray" \u2192 "grey" (British spelling)',
                "2.4.1",
            ))
        return violations

    @staticmethod
    def check_E04(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'acknowledgment' should be 'acknowledgement'."""
        violations = []
        for m in re.finditer(r"\backnowledgment\b", text, re.IGNORECASE):
            violations.append(Violation(
                lineno, m.start(), "E04", "error",
                '"acknowledgment" \u2192 "acknowledgement"',
                "2.4.1",
            ))
        return violations

    @staticmethod
    def check_E05(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'modeling' should be 'modelling'."""
        violations = []
        for m in re.finditer(r"\bmodeling\b", text, re.IGNORECASE):
            violations.append(Violation(
                lineno, m.start(), "E05", "error",
                '"modeling" \u2192 "modelling"',
                "2.4.1",
            ))
        return violations

    @staticmethod
    def check_E06(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'labeled' should be 'labelled'."""
        violations = []
        for m in re.finditer(r"\blabeled\b", text, re.IGNORECASE):
            violations.append(Violation(
                lineno, m.start(), "E06", "error",
                '"labeled" \u2192 "labelled"',
                "2.4.1",
            ))
        return violations

    @staticmethod
    def check_E07(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'catalog' should be 'catalogue'."""
        violations = []
        for m in re.finditer(r"\bcatalog\b", text, re.IGNORECASE):
            # Skip if in a path or code context
            before = text[max(0, m.start() - 5):m.start()]
            if "/" in before or "_" in before or "\\" in before:
                continue
            violations.append(Violation(
                lineno, m.start(), "E07", "error",
                '"catalog" \u2192 "catalogue"',
                "2.4.1",
            ))
        return violations

    @staticmethod
    def check_E08(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'favor' should be 'favour'."""
        violations = []
        for m in re.finditer(r"\bfavor\b", text, re.IGNORECASE):
            before = text[max(0, m.start() - 2):m.start()]
            if "\\" in before:
                continue
            violations.append(Violation(
                lineno, m.start(), "E08", "error",
                '"favor" \u2192 "favour"',
                "2.4.1",
            ))
        return violations

    # ===== Category 3: Units & Numbers =====================================

    @staticmethod
    def check_U01(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Compound units with '/' should use exponents."""
        violations = []
        # Only flag in text context, not in math
        # Common astronomy compound units with slash
        patterns = [
            (r"\bkm/s\b", "km\\,s$^{-1}$"),
            (r"\bm/s\b", "m\\,s$^{-1}$"),
            (r"\bMpc/h\b", "Mpc\\,$h^{-1}$"),
            (r"\berg/s\b", "erg\\,s$^{-1}$"),
            (r"\bphotons/s\b", "photons\\,s$^{-1}$"),
            (r"\bcounts/s\b", "counts\\,s$^{-1}$"),
        ]
        for pat, fix in patterns:
            for m in re.finditer(pat, text):
                violations.append(Violation(
                    lineno, m.start(), "U01", "error",
                    f'"{m.group(0)}" \u2192 use exponent notation "{fix}"',
                    "2.2.8",
                ))
        return violations

    @staticmethod
    def check_U02(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Plural unit abbreviations (units are never pluralised)."""
        violations = []
        for m in re.finditer(r"\b(arcsecs|arcmins|yrs|secs|mins|hrs|kms|Mpcs)\b", text):
            singular = m.group(0).rstrip("s")
            violations.append(Violation(
                lineno, m.start(), "U02", "error",
                f'Unit abbreviation "{m.group(0)}" should not be pluralised '
                f'\u2192 "{singular}"',
                "2.2.2",
            ))
        return violations

    @staticmethod
    def check_U03(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        r"""Missing thin space (\,) before unit."""
        violations = []
        # Number directly followed by unit without \, or ~ separator
        units = r"(?:km|arcsec|arcmin|Mpc|GHz|MHz|kHz|mas|deg|kpc|pc|Gyr|Myr|yr|mag|dex)"
        # Must have a digit immediately followed by the unit (no space or \,)
        pattern = re.compile(r"[0-9]\}" + units + r"\b|[0-9]" + units + r"\b")
        stripped = _strip_comments(raw)
        # Remove math regions for this check
        check = _remove_math(stripped)
        for m in pattern.finditer(check):
            # Skip if preceded by \, or ~ or \; or thin space
            before = check[max(0, m.start() - 3):m.start() + 1]
            if "\\," in before or "~" in before or "\\;" in before:
                continue
            violations.append(Violation(
                lineno, m.start(), "U03", "warning",
                f'Missing thin space before unit \u2192 insert "\\," '
                f"before the unit",
                "2.2.6",
            ))
        return violations

    @staticmethod
    def check_U05(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Powers of 10 in wrong format (should use \\times 10^{})."""
        violations = []
        # Skip affiliation lines (postal codes contain digit-E-digit)
        stripped_raw = _strip_comments(raw)
        if r"\label{aff" in stripped_raw:
            return violations
        # Match patterns like 1e5, 3e-4 in text (not code)
        for m in re.finditer(r"[0-9][eE][+-]?[0-9]", text):
            # Skip if preceded by a letter (postal codes like V9E)
            if m.start() > 0 and text[m.start() - 1].isalpha():
                continue
            # Skip catalogue IDs (e.g. 1E0657) — many trailing digits
            after = text[m.end():]
            if re.match(r"\d{2,}", after):
                continue
            violations.append(Violation(
                lineno, m.start(), "U05", "warning",
                "Powers of 10 should use LaTeX notation "
                "(e.g. $3 \\times 10^{5}$), not 'e' notation",
                "2.5.13",
            ))
        return violations

    @staticmethod
    def check_U07(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Thousands separator should not use comma."""
        violations = []
        stripped = _strip_comments(raw)
        # Find digit,3-digits pattern but NOT inside .bib references or {,}
        for m in re.finditer(r"[0-9],[0-9]{3}(?![0-9])", stripped):
            # Skip the TeX {,} thin-space idiom: e.g. 10{,}000
            before = stripped[max(0, m.start() - 1):m.start()]
            after = stripped[m.end():m.end() + 1]
            if before == "{" and "}" in stripped[m.start():m.start() + 6]:
                continue
            # Check for LaTeX-safe thousands separators
            context = stripped[max(0, m.start() - 3):m.end() + 3]
            if "\\," in context:
                continue
            violations.append(Violation(
                lineno, m.start(), "U07", "warning",
                "Use thin space (\\,) or {,} for thousands separator, "
                "not a bare comma",
                "2.5.22",
            ))
        return violations

    # ===== Category 4: LaTeX Typesetting ===================================

    @staticmethod
    def check_T01(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Straight double quotes instead of TeX quotes."""
        violations = []
        stripped = _strip_comments(raw)
        # Remove content inside \url, \href, \texttt, \verb
        check = _remove_commands(stripped, ["url", "href", "texttt", "verb", "lstinline"])
        # Remove math
        check = _remove_math(check)
        for m in re.finditer(r'(?<!\\)"', check):
            violations.append(Violation(
                lineno, m.start(), "T01", "warning",
                'Straight double quote " \u2192 use `` and \'\' (TeX quotes)',
                "2.5.3",
            ))
        return violations

    @staticmethod
    def check_T02(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Hyphen used as number range dash (should be --)."""
        violations = []
        stripped = _strip_comments(raw)
        # Skip author/affiliation lines (ORCIDs, addresses, postal codes)
        if r"\orcid{" in stripped or r"\inst{" in stripped or r"\label{aff" in stripped:
            return violations
        check = _remove_math(stripped)
        # Pattern: digit-digit (single hyphen between numbers).
        # (?<![-\\\d]) ensures we match the full first digit group.
        # (?![\d-]) ensures the second group is complete (no ORCID segments).
        for m in re.finditer(r"(?<![-\\\d])(\d+)-(\d+)(?![\d-])", check):
            # Skip page ranges in cite keys, \ref, etc.
            before = check[max(0, m.start() - 20):m.start()]
            if re.search(r"\\(cite|ref|label|cref|Cref|eqref|pageref)\{[^}]*$", before):
                continue
            # Skip if in a filename or path context
            if "/" in before or "_" in before:
                continue
            # Skip model/part numbers: letter or closing brace immediately
            # adjacent to the first digit, e.g. CCD273-84, \ac{CCD}6-2
            char_before = check[m.start() - 1] if m.start() > 0 else ""
            if char_before.isalpha() or char_before == "}":
                continue
            # Skip catalogue/star names: UPPERCASE prefix followed by
            # whitespace immediately before the digits, e.g. "HE 0107-5240",
            # "SDSS J0100-1234", "2MASS 0451-23".
            if re.search(r"\b[A-Z0-9]{2,}\s+$", before):
                continue
            violations.append(Violation(
                lineno, m.start(), "T02", "warning",
                f'"{m.group(0)}" \u2192 use en-dash "{m.group(1)}--{m.group(2)}" '
                "for number ranges",
                "2.5.4",
            ))
        return violations

    @staticmethod
    def check_T04(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Math operators without backslash in math mode."""
        violations = []
        stripped = _strip_comments(raw)
        op_re = re.compile(
            r"(?<!\\)\b(ln|log|sin|cos|tan|exp|det|min|max|lim)\s*[({\\]"
        )

        def scan(content: str, offset: int) -> None:
            for m in op_re.finditer(content):
                op = m.group(1)
                violations.append(Violation(
                    lineno, offset + m.start(), "T04", "warning",
                    f'Math operator "{op}" should use \\{op} in math mode',
                    "2.5.10",
                ))

        # Inline math: $...$, \(...\), \[...\]
        for math_match in _INLINE_MATH_RE.finditer(stripped):
            scan(math_match.group(1), math_match.start())
        for math_match in _PAREN_MATH_RE.finditer(stripped):
            # Strip leading \( and trailing \) for offset maths to line up
            scan(math_match.group(0)[2:-2], math_match.start() + 2)
        for math_match in _BRACKET_MATH_RE.finditer(stripped):
            scan(math_match.group(0)[2:-2], math_match.start() + 2)
        # Inside a display math environment, the whole line is math content.
        if ctx.in_math_env:
            scan(stripped, 0)
        return violations

    @staticmethod
    def check_T05(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        r"""\\ used as paragraph break (outside tabular/align/equation)."""
        violations = []
        if ctx.in_tabular or ctx.in_math_env:
            return violations
        stripped = _strip_comments(raw).rstrip()
        # Check for \\ at end of line (paragraph break misuse)
        if stripped.endswith("\\\\") and not stripped.endswith("\\\\["):
            # Skip if inside any environment that legitimately uses \\
            _NEWLINE_OK_ENVS = (
                _TABULAR_ENVS | _MATH_ENVS | {"itemize", "enumerate",
                "description", "center", "flushleft", "flushright",
                "titlepage", "abstract", "title"}
            )
            if any(e in _NEWLINE_OK_ENVS for e in ctx.env_stack):
                return violations
            # Skip affiliation/author block lines (use \\ for separators)
            if re.search(
                r"^\s*\$\^\{|\\inst\{|\\orcid\{|\\and\b|\\institute\{|"
                r"\\affil\b|\\label\{aff",
                stripped,
            ):
                return violations
            # Skip \\ inside \footnote{} (line break in footnote)
            if r"\footnote" in stripped or r"\footnote" in ctx.prev_raw_line:
                return violations
            # Skip \\ in supertabular header/footer commands and
            # \multicolumn lines (table context not tracked as env)
            if re.search(
                r"\\(?:multicolumn|tablefirsthead|tablehead|"
                r"tabletail|tablelasttail)\b",
                stripped,
            ):
                return violations
            violations.append(Violation(
                lineno, len(stripped) - 2, "T05", "warning",
                r"Do not use \\ for paragraph breaks — use blank lines",
                "2.5.1",
            ))
        return violations

    @staticmethod
    def check_T06(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        r"""URL not wrapped in \url{} or \href{}."""
        violations = []
        stripped = _strip_comments(raw)
        # Remove URLs already inside \url{} or \href{}
        check = _remove_commands(stripped, ["url", "href", "fnurl"])
        for m in re.finditer(r"https?://\S+", check):
            violations.append(Violation(
                lineno, m.start(), "T06", "warning",
                "URL should be wrapped in \\url{} or \\href{}",
                "2.9",
            ))
        return violations

    @staticmethod
    def check_T08(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Abbreviation at sentence start."""
        violations = []
        stripped = _strip_comments(raw)
        # Common abbreviations that should be written out at sentence start
        abbrevs = r"(?:Sect\.|Fig\.|Eq\.|Tab\.|Ref\.|App\.)"
        # Line-start case: only a genuine sentence start if the previous
        # non-blank line ends with sentence-terminating punctuation, or if
        # the previous line is blank (paragraph break).  A wrapped line in
        # the source is not a sentence boundary.
        m = re.match(r"^\s*(" + abbrevs + r")", stripped)
        if m:
            prev = _strip_comments(ctx.prev_raw_line).rstrip()
            prev_is_sentence_end = (not prev) or prev[-1] in ".?!"
            # But "et al.", "e.g.", "i.e.", "cf.", "vs." end in "." without
            # ending a sentence — check the last word.
            if prev_is_sentence_end and prev:
                tail = prev[-10:]
                if re.search(r"\b(al|etc|e\.g|i\.e|cf|vs)\.\s*$", tail):
                    prev_is_sentence_end = False
            if prev_is_sentence_end:
                violations.append(Violation(
                    lineno, m.start(1), "T08", "warning",
                    f'"{m.group(1)}" at sentence start — write out in full '
                    '(Section, Figure, Equation, etc.)',
                    "2.3.19",
                ))
        # After sentence-ending punctuation (same line)
        for m in re.finditer(r"\.\s+(" + abbrevs + r")", stripped):
            # Skip if previous word is an abbreviation itself (e.g. "et al. Fig.")
            before = stripped[max(0, m.start() - 10):m.start()]
            if re.search(r"\b(al|etc|e\.g|i\.e|cf|vs)\s*$", before):
                continue
            violations.append(Violation(
                lineno, m.start(1), "T08", "warning",
                f'"{m.group(1)}" appears to start a sentence — '
                "write out in full",
                "2.3.19",
            ))
        return violations

    @staticmethod
    def check_T09(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        r"""\includegraphics with both width and height (anisotropic stretching)."""
        violations = []
        stripped = _strip_comments(raw)
        m = re.search(r"\\includegraphics\s*\[([^\]]*)\]", stripped)
        if m:
            opts = m.group(1)
            has_width = bool(re.search(r"\bwidth\s*=", opts))
            has_height = bool(re.search(r"\bheight\s*=", opts))
            if has_width and has_height:
                violations.append(Violation(
                    lineno, m.start(), "T09", "error",
                    "\\includegraphics specifies both width and height "
                    "\u2192 anisotropic stretching; use only one dimension",
                    "2.8",
                ))
        return violations

    @staticmethod
    def check_T10(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Adjacent closing/opening parentheses )( — merge or use semicolon."""
        violations = []
        stripped = _strip_comments(raw)
        for m in re.finditer(r"\)\s*\(", stripped):
            violations.append(Violation(
                lineno, m.start(), "T10", "warning",
                "Adjacent parentheses \")(...)(\" \u2192 merge into one "
                "group or use semicolon \"(...; ...)\"",
                "2.5",
            ))
        return violations

    @staticmethod
    def check_T11(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        r"""\acknowledgement{} command instead of \begin{acknowledgements}."""
        violations = []
        stripped = _strip_comments(raw)
        if re.search(r"\\acknowledgement\s*\{", stripped):
            violations.append(Violation(
                lineno, 0, "T11", "error",
                "Use \\begin{acknowledgements} environment, "
                "not \\acknowledgement{} command (affects formatting)",
                "3.4",
            ))
        return violations

    @staticmethod
    def check_T12(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        r"""Colon before displayed equation — equations are part of sentences."""
        violations = []
        stripped = _strip_comments(raw)
        # Check if this line starts a display math environment
        display_envs = (
            r"\\begin\{equation\*?\}",
            r"\\begin\{align\*?\}",
            r"\\begin\{gather\*?\}",
            r"\\begin\{multline\*?\}",
            r"\\begin\{eqnarray\*?\}",
            r"\\begin\{flalign\*?\}",
            r"\\\[",  # \[
        )
        is_display_start = any(re.search(p, stripped) for p in display_envs)
        if is_display_start:
            # Check previous line for trailing colon
            prev = _strip_comments(ctx.prev_raw_line).rstrip()
            if prev.endswith(":"):
                violations.append(Violation(
                    lineno, 0, "T12", "warning",
                    "Colon before displayed equation \u2192 equations are "
                    "part of sentences; remove the colon",
                    "2.5",
                ))
        return violations

    # ===== Category 5: References & Citations ==============================

    @staticmethod
    def check_R02(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """EC citation should use 'Euclid Collaboration:' format."""
        violations = []
        stripped = _strip_comments(raw)
        if re.search(r"Euclid\s+Collaboration\s+(et\s+al|&)", stripped):
            violations.append(Violation(
                lineno, 0, "R02", "warning",
                "EC citation format: use 'Euclid Collaboration: Author' "
                "with a colon, not 'et al.'",
                "2.6.7",
            ))
        return violations

    @staticmethod
    def check_R03(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Commented-out text (arXiv source is public)."""
        violations = []
        stripped = raw.strip()
        if stripped.startswith("%"):
            # Only flag if there's substantial prose (not just %--- or % blank)
            comment_text = stripped.lstrip("% \t")
            # Heuristic: looks like real prose → at least four words and
            # either ends/contains a full stop or is clearly long-form
            # (>=8 words).  Catches short commented-out sentences like
            # "% We remove this for now." while ignoring single-word
            # notes and decorative dividers.
            word_count = len(re.findall(r"\b\w+\b", comment_text))
            has_period = "." in comment_text
            if (word_count >= 4 and (has_period or word_count >= 8)
                    and not re.match(r"^[-=~*]+$", comment_text)
                    and not re.match(r"^(TODO|FIXME|NOTE|XXX|HACK)\b", comment_text, re.IGNORECASE)
                    and not re.match(r"^\\", comment_text)):
                violations.append(Violation(
                    lineno, 0, "R03", "suggestion",
                    "Commented-out text — arXiv source is public; "
                    "remove dead text before submission",
                    "2.3.17",
                ))
        return violations

    @staticmethod
    def check_R05(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """"arXiv e-prints" redundancy in bibliography entries."""
        violations = []
        stripped = _strip_comments(raw)
        if re.search(r"arXiv\s+e-prints?", stripped, re.IGNORECASE):
            violations.append(Violation(
                lineno, 0, "R05", "warning",
                '"arXiv e-prints, arXiv:..." is redundant \u2192 '
                'use just "arXiv:..." (delete the \\journal line in .bib)',
                "2.6",
            ))
        return violations

    @staticmethod
    def check_R04_document(ctx: TexContext) -> list[Violation]:
        r"""Check for \AckEC acknowledgements macro in the document."""
        if not ctx.has_ackec:
            return [Violation(
                0, 0, "R04", "suggestion",
                "No \\AckEC acknowledgements macro found — "
                "required for EC papers",
                "3.4",
            )]
        return []

    # ===== Category 6: Style Guide Specific ================================

    @staticmethod
    def check_S01(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'DEC' or 'R.A.' should be 'Dec' and 'RA'."""
        violations = []
        for m in re.finditer(r"\bDEC\b", text):
            # Skip if inside an acronym definition or all-caps context
            violations.append(Violation(
                lineno, m.start(), "S01", "error",
                '"DEC" \u2192 "Dec" (declination abbreviation)',
                "2.3.10",
            ))
        for m in re.finditer(r"\bR\.A\.(?=\s|$|[^A-Za-z])", text):
            violations.append(Violation(
                lineno, m.start(), "S01", "error",
                '"R.A." \u2192 "RA" (right ascension abbreviation)',
                "2.3.10",
            ))
        return violations

    @staticmethod
    def check_S02(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'non' without hyphen before certain words."""
        violations = []
        # "non" before a capital letter should have a hyphen
        for m in re.finditer(r"\bnon([A-Z])", text):
            violations.append(Violation(
                lineno, m.start(), "S02", "error",
                f'"non{m.group(1)}..." \u2192 "non-{m.group(1)}..." '
                "(hyphenate non- before capitals)",
                "2.4.41",
            ))
        return violations

    @staticmethod
    def check_S03(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """Waveband letters should be italicised."""
        violations = []
        # Look for " X band" or " X-band" where X is a waveband letter
        for m in re.finditer(r"(?<![\\$])\b([ugrizJHKYBVRI])[- ]band\b", text):
            band = m.group(1)
            # Skip if preceded by $ or \ (already in math/italic)
            before = text[max(0, m.start() - 2):m.start()]
            if "$" in before or "\\" in before:
                continue
            violations.append(Violation(
                lineno, m.start(), "S03", "warning",
                f'Waveband letter "{band}" should be italicised '
                f'\u2192 "$\\textit{{{band}}}$ band" or "${{\\it {band}}}$-band"',
                "2.4.28",
            ))
        return violations

    @staticmethod
    def check_S04(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """'data is/was/has' — data is plural."""
        violations = []
        for m in re.finditer(r"\bdata\s+(is|was|has)\b", text, re.IGNORECASE):
            # Skip when "data" is the object of a preposition (not the subject)
            # e.g. "on Euclid data is the..." → "is" agrees with earlier subject
            before = text[max(0, m.start() - 30):m.start()]
            if re.search(
                r"\b(on|with|of|from|in|for|about|into|through|within|using)\s+"
                r"(\S+\s+)*$",
                before,
            ):
                continue
            verb = m.group(1)
            plural = {"is": "are", "was": "were", "has": "have"}
            violations.append(Violation(
                lineno, m.start(), "S04", "error",
                f'"data {verb}" \u2192 "data {plural[verb.lower()]}" '
                '("data" is plural in Euclid style)',
                "2.4.35",
            ))
        return violations

    @staticmethod
    def check_S05(lineno: int, raw: str, text: str, ctx: TexContext) -> list[Violation]:
        """"the universe/galaxy/sun" should be capitalised when referring to ours."""
        violations = []
        # Only flag when the target word is lowercase after "the"
        # "galaxy" omitted: "the galaxy" almost always refers to a specific
        # galaxy under discussion, not the Milky Way.  Too many FPs.
        targets = [
            ("universe", "Universe"),
            ("sun", "Sun"),
            ("solar system", "Solar System"),
        ]
        for lower, upper in targets:
            # Match "the <lowercase-word>" — case-sensitive for the target
            pat = re.compile(r"\bthe\s+" + re.escape(lower) + r"\b")
            for m in pat.finditer(text):
                # Skip if preceded by "of the" in multiverse context etc.
                before = text[max(0, m.start() - 20):m.start()]
                if re.search(r"\b(a|another|different|parallel|observable)\s+$",
                             before, re.IGNORECASE):
                    continue
                violations.append(Violation(
                    lineno, m.start(), "S05", "warning",
                    f'"the {lower}" \u2192 "the {upper}" when referring '
                    f"to ours specifically",
                    "3.3",
                ))
        return violations


# ---------------------------------------------------------------------------
# Rule registry
# ---------------------------------------------------------------------------

# Rules that run per-line on text content
_LINE_RULES: list[str] = [
    "check_N01", "check_N02", "check_N03", "check_N04",
    "check_N05", "check_N06", "check_N07", "check_N08",
    "check_N09", "check_N10", "check_N11", "check_N12",
    "check_E01", "check_E02", "check_E03", "check_E04",
    "check_E05", "check_E06", "check_E07", "check_E08",
    "check_U01", "check_U02", "check_U03", "check_U05",
    "check_U07",
    "check_T01", "check_T02", "check_T04", "check_T05",
    "check_T06", "check_T08", "check_T09", "check_T10",
    "check_T11", "check_T12",
    "check_R02", "check_R03", "check_R05",
    "check_S01", "check_S02", "check_S03", "check_S04",
    "check_S05",
]

_CATEGORY_MAP = {
    "naming": [r for r in _LINE_RULES if r.startswith("check_N")],
    "english": [r for r in _LINE_RULES if r.startswith("check_E")],
    "units": [r for r in _LINE_RULES if r.startswith("check_U")],
    "typesetting": [r for r in _LINE_RULES if r.startswith("check_T")],
    "references": [r for r in _LINE_RULES if r.startswith("check_R")],
    "style": [r for r in _LINE_RULES if r.startswith("check_S")],
}

# ---------------------------------------------------------------------------
# Main linting logic
# ---------------------------------------------------------------------------

def lint_file(
    path: Path,
    categories: list[str] | None = None,
    min_severity: str = "suggestion",
) -> list[Violation]:
    """Lint a .tex file and return a list of violations."""
    severity_order = {"suggestion": 0, "warning": 1, "error": 2}
    min_sev = severity_order.get(min_severity, 0)

    # Determine which rules to run
    if categories:
        active_rules = []
        for cat in categories:
            active_rules.extend(_CATEGORY_MAP.get(cat, []))
    else:
        active_rules = list(_LINE_RULES)

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    ctx = TexContext()
    checker = StyleChecker()
    violations: list[Violation] = []

    prev_line = ""
    for i, raw_line in enumerate(lines, start=1):
        ctx.update(raw_line, prev_line)

        # Skip preamble, verbatim, and math environments
        if ctx.in_preamble or ctx.in_verbatim:
            continue

        is_comment = _is_comment_line(raw_line)
        cleaned = _clean_text_line(raw_line)

        for rule_name in active_rules:
            method = getattr(checker, rule_name)

            # For comment lines, only run R03
            if is_comment and rule_name != "check_R03":
                continue

            # Skip text rules in math environments (except T04/T05/T12)
            if ctx.in_math_env and rule_name not in {"check_T04", "check_T05", "check_T12"}:
                continue

            results = method(i, raw_line, cleaned, ctx)

            for v in results:
                if severity_order.get(v.severity, 0) >= min_sev:
                    violations.append(v)

        prev_line = raw_line

    # Document-level checks
    if not categories or "references" in categories:
        for v in checker.check_R04_document(ctx):
            if severity_order.get(v.severity, 0) >= min_sev:
                violations.append(v)

    return violations


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

# ANSI colour codes
_COLOURS = {
    "error": "\033[1;31m",    # bold red
    "warning": "\033[1;33m",  # bold yellow
    "suggestion": "\033[1;36m",  # bold cyan
    "reset": "\033[0m",
    "dim": "\033[2m",
    "bold": "\033[1m",
    "rule": "\033[1;35m",     # bold magenta
}


def _format_terminal(violations: list[Violation], path: Path) -> str:
    """Format violations for coloured terminal output."""
    if not violations:
        return f"\u2713 {path}: no issues found\n"

    lines = [f"\n{_COLOURS['bold']}{path}{_COLOURS['reset']}\n"]
    for v in sorted(violations, key=lambda x: (x.line, x.col)):
        sev_colour = _COLOURS.get(v.severity, "")
        reset = _COLOURS["reset"]
        rule_colour = _COLOURS["rule"]
        dim = _COLOURS["dim"]
        line_str = f"  Line {v.line:<5}" if v.line > 0 else "  Doc   "
        lines.append(
            f"{line_str}{rule_colour}[{v.rule_id}]{reset} "
            f"{sev_colour}{v.severity.upper():<10}{reset} "
            f"{v.message} "
            f"{dim}(Sect. {v.sg_section}){reset}"
        )

    # Summary
    counts = {"error": 0, "warning": 0, "suggestion": 0}
    for v in violations:
        counts[v.severity] = counts.get(v.severity, 0) + 1
    total = len(violations)
    summary_parts = []
    if counts["error"]:
        summary_parts.append(f"{_COLOURS['error']}{counts['error']} errors{_COLOURS['reset']}")
    if counts["warning"]:
        summary_parts.append(f"{_COLOURS['warning']}{counts['warning']} warnings{_COLOURS['reset']}")
    if counts["suggestion"]:
        summary_parts.append(f"{_COLOURS['suggestion']}{counts['suggestion']} suggestions{_COLOURS['reset']}")
    lines.append(f"\nSummary: {', '.join(summary_parts)} ({total} total)\n")
    return "\n".join(lines)


def _format_json(violations: list[Violation], path: Path) -> str:
    """Format violations as JSON."""
    records = []
    for v in sorted(violations, key=lambda x: (x.line, x.col)):
        records.append({
            "file": str(path),
            "line": v.line,
            "column": v.col,
            "rule_id": v.rule_id,
            "severity": v.severity,
            "message": v.message,
            "style_guide_section": v.sg_section,
        })
    return json.dumps({"violations": records, "total": len(records)}, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Lint a LaTeX file against the ECEB Style Guide V4.0.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument("file", type=Path, help="Path to the .tex file to lint")
    parser.add_argument(
        "--severity",
        choices=["suggestion", "warning", "error"],
        default="suggestion",
        help="Minimum severity to report (default: suggestion)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--category",
        action="append",
        choices=list(_CATEGORY_MAP.keys()),
        help="Only check rules in this category (can be repeated)",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"\u2717 File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    violations = lint_file(args.file, categories=args.category, min_severity=args.severity)

    if args.json:
        print(_format_json(violations, args.file))
    else:
        print(_format_terminal(violations, args.file))

    # Return codes: 0 = clean, 1 = warnings/suggestions only, 2 = errors
    has_errors = any(v.severity == "error" for v in violations)
    has_warnings = any(v.severity in ("warning", "suggestion") for v in violations)
    if has_errors:
        sys.exit(2)
    elif has_warnings:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
