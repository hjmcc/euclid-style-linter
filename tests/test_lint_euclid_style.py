"""
Regression test suite for the ECEB style linter (lint_euclid_style.py).

Runs lint_file() on tests/test_lint_euclid_style.tex and checks that:
  - Every ``% EXPECT: <rule_id>`` line produces a violation with that rule ID.
  - No ``% CLEAN: <rule_id>`` line produces a violation with that rule ID.
  - Document-level ``% EXPECT_DOC: <rule_id>`` rules fire at line 0.
  - Edge-case lines produce no violations at all.

Usage:
    python3 -m pytest tests/test_lint_euclid_style.py -v
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import pytest

# Add project root to sys.path so we can import the linter
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from lint_euclid_style import lint_file  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TEX_FILE = Path(__file__).resolve().parent / "test_lint_euclid_style.tex"

# Regex for parsing marker comments
_EXPECT_RE = re.compile(r"%\s*EXPECT:\s*(\w+)")
_CLEAN_RE = re.compile(r"%\s*CLEAN:\s*(\w+)")
_EXPECT_DOC_RE = re.compile(r"%\s*EXPECT_DOC:\s*(\w+)")
_EDGE_RE = re.compile(r"%\s*EDGE:\s*(\S+)")


def _parse_markers(path: Path) -> dict:
    """Parse the synthetic .tex file and return marker mappings."""
    expects = {}      # {lineno: rule_id}
    cleans = {}       # {lineno: rule_id}
    expect_docs = []  # [rule_id, ...]
    edges = {}        # {lineno: label}

    for i, line in enumerate(path.read_text().splitlines(), start=1):
        m = _EXPECT_RE.search(line)
        if m:
            expects[i] = m.group(1)
            continue
        m = _CLEAN_RE.search(line)
        if m:
            cleans[i] = m.group(1)
            continue
        m = _EXPECT_DOC_RE.search(line)
        if m:
            expect_docs.append(m.group(1))
            continue
        m = _EDGE_RE.search(line)
        if m:
            edges[i] = m.group(1)

    return {
        "expects": expects,
        "cleans": cleans,
        "expect_docs": expect_docs,
        "edges": edges,
    }


@pytest.fixture(scope="module")
def lint_results():
    """Run the linter once and cache results for all tests."""
    violations = lint_file(TEX_FILE, min_severity="suggestion")
    # Build lookup: {lineno: [rule_id, ...]}
    by_line = defaultdict(list)
    for v in violations:
        by_line[v.line].append(v.rule_id)
    return violations, by_line


@pytest.fixture(scope="module")
def markers():
    """Parse markers from the .tex file once."""
    return _parse_markers(TEX_FILE)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def _get_expect_params():
    """Generate parametrised test cases for EXPECT lines."""
    m = _parse_markers(TEX_FILE)
    return [(lineno, rule_id) for lineno, rule_id in m["expects"].items()]


def _get_clean_params():
    """Generate parametrised test cases for CLEAN lines."""
    m = _parse_markers(TEX_FILE)
    return [(lineno, rule_id) for lineno, rule_id in m["cleans"].items()]


def _get_edge_params():
    """Generate parametrised test cases for EDGE lines."""
    m = _parse_markers(TEX_FILE)
    return [(lineno, label) for lineno, label in m["edges"].items()]


def _get_doc_params():
    """Generate parametrised test cases for document-level rules."""
    m = _parse_markers(TEX_FILE)
    return m["expect_docs"]


@pytest.mark.parametrize("lineno,rule_id", _get_expect_params(),
                         ids=[f"EXPECT-L{ln}-{rid}" for ln, rid in _get_expect_params()])
def test_expect_detected(lineno, rule_id, lint_results):
    """Each EXPECT line must produce a violation with the specified rule ID."""
    _, by_line = lint_results
    found_rules = by_line.get(lineno, [])
    assert rule_id in found_rules, (
        f"Line {lineno}: expected rule {rule_id} to fire, "
        f"but only found: {found_rules or '(none)'}"
    )


@pytest.mark.parametrize("lineno,rule_id", _get_clean_params(),
                         ids=[f"CLEAN-L{ln}-{rid}" for ln, rid in _get_clean_params()])
def test_clean_not_flagged(lineno, rule_id, lint_results):
    """No CLEAN line should produce a violation with the specified rule ID."""
    _, by_line = lint_results
    found_rules = by_line.get(lineno, [])
    assert rule_id not in found_rules, (
        f"Line {lineno}: rule {rule_id} should NOT fire on CLEAN line, "
        f"but it did (all rules on this line: {found_rules})"
    )


@pytest.mark.parametrize("rule_id", _get_doc_params(),
                         ids=[f"EXPECT_DOC-{rid}" for rid in _get_doc_params()])
def test_document_level_rule(rule_id, lint_results):
    """Document-level rules (line=0) must fire."""
    violations, _ = lint_results
    doc_rules = [v.rule_id for v in violations if v.line == 0]
    assert rule_id in doc_rules, (
        f"Document-level rule {rule_id} expected but not found "
        f"(found: {doc_rules or '(none)'})"
    )


@pytest.mark.parametrize("lineno,label", _get_edge_params(),
                         ids=[f"EDGE-L{ln}-{lbl}" for ln, lbl in _get_edge_params()])
def test_edge_case_clean(lineno, label, lint_results):
    """Edge-case lines should produce no violations at all."""
    _, by_line = lint_results
    found_rules = by_line.get(lineno, [])
    assert not found_rules, (
        f"Line {lineno} (edge case {label}): expected no violations, "
        f"but found: {found_rules}"
    )


# ---------------------------------------------------------------------------
# Summary report (runs as a test so it always prints)
# ---------------------------------------------------------------------------

def test_summary_report(lint_results, markers):
    """Print precision/recall summary (always passes — informational)."""
    violations, by_line = lint_results
    expects = markers["expects"]
    cleans = markers["cleans"]

    # Per-rule stats
    rule_tp = defaultdict(int)  # True positives (EXPECT detected)
    rule_fn = defaultdict(int)  # False negatives (EXPECT missed)
    rule_fp = defaultdict(int)  # False positives (CLEAN triggered)

    for lineno, rule_id in expects.items():
        if rule_id in by_line.get(lineno, []):
            rule_tp[rule_id] += 1
        else:
            rule_fn[rule_id] += 1

    for lineno, rule_id in cleans.items():
        if rule_id in by_line.get(lineno, []):
            rule_fp[rule_id] += 1

    all_rules = sorted(set(list(expects.values()) + list(cleans.values())))

    print("\n" + "=" * 65)
    print("ECEB Linter Regression Summary")
    print("=" * 65)
    print(f"{'Rule':<8} {'TP':>4} {'FN':>4} {'FP':>4} {'Precision':>10} {'Recall':>8}")
    print("-" * 65)

    total_tp = total_fn = total_fp = 0
    for rule in all_rules:
        tp = rule_tp[rule]
        fn = rule_fn[rule]
        fp = rule_fp[rule]
        total_tp += tp
        total_fn += fn
        total_fp += fp
        prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        print(f"{rule:<8} {tp:>4} {fn:>4} {fp:>4} {prec:>10.1%} {rec:>8.1%}")

    prec_all = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 1.0
    rec_all = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0
    print("-" * 65)
    print(f"{'TOTAL':<8} {total_tp:>4} {total_fn:>4} {total_fp:>4} "
          f"{prec_all:>10.1%} {rec_all:>8.1%}")
    print(f"\nTotal violations in test file: {len(violations)}")
    print(f"EXPECT markers: {len(expects)} | CLEAN markers: {len(cleans)}")
    print("=" * 65)
