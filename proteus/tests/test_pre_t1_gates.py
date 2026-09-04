"""Regression gates from the pre-T1 hardening pass (2026-09-04).

Each gate exists because a specific defect actually occurred during or around Harmonia's first
end-to-end integration. None of them is speculative, and none of them changes behaviour: they
fail the suite if a known defect recurs or if a recorded blast radius grows.

  G1  the `random` blast radius in v0_6/equilibrium.py stays exactly where it was measured
  G2  the numerical replay contract never touches the nondeterministic path
  G3  the protected deterministic surface (foundry + integration) admits NO exemptions
  G4  generated artifacts (.pyc / __pycache__) cannot be tracked again by the -f workflow
  G5  the living consumer document cannot deny the registry while the registry exists
"""
from __future__ import annotations

import ast
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EQUILIBRIUM = os.path.join(ROOT, "proteus", "v0_6", "equilibrium.py")
RUN_REPLAY = os.path.join(ROOT, "proteus", "v0_6", "run_replay.py")
CONSUMER_DOC = os.path.join(ROOT, "roles", "Proteus", "CONSUMER_SURFACE_V0_6.md")
REGISTRY_JSON = os.path.join(ROOT, "proteus", "integration", "PLAYER_REGISTRY.json")

#: The single function permitted to use `random`, as measured on 2026-09-04.
PERMITTED_RANDOM_HOST = "stationary_empirical"


def _tree(path):
    with open(path, encoding="utf-8") as f:
        return ast.parse(f.read())


def _random_use_lines(tree):
    """Lines where the `random` module is actually USED (not merely imported)."""
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id == "random":
            lines.append(node.lineno)
        elif isinstance(node, ast.Name) and node.id == "random" \
                and not isinstance(getattr(node, "ctx", None), ast.Store):
            lines.append(node.lineno)
    return sorted(set(lines))


def _function_spans(tree):
    spans = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            spans[node.name] = (node.lineno, getattr(node, "end_lineno", node.lineno))
    return spans


# ------------------------------------------------------------------ G1

def test_random_blast_radius_is_exactly_where_it_was_measured():
    """G1. `random` may be used ONLY inside stationary_empirical().

    The V0.6 packet states the blast radius of this known defect: the empirical-occupancy check
    and the trajectory arm, both non-adjudicated. That claim is only true while every use of
    `random` sits inside the one function those two call. If someone later reaches for
    random.Random() elsewhere in equilibrium.py, a published bounded-blast-radius statement
    silently becomes false. This gate makes that impossible to do quietly.
    """
    tree = _tree(EQUILIBRIUM)
    spans = _function_spans(tree)
    assert PERMITTED_RANDOM_HOST in spans, f"{PERMITTED_RANDOM_HOST}() no longer exists"
    lo, hi = spans[PERMITTED_RANDOM_HOST]
    stray = [ln for ln in _random_use_lines(tree) if not (lo <= ln <= hi)]
    assert not stray, (
        f"`random` used outside {PERMITTED_RANDOM_HOST}() at line(s) {stray}. The published "
        f"blast radius (empirical-occupancy check + trajectory arm, both non-adjudicated) is no "
        f"longer accurate. Either revert, or re-measure and amend the record.")


# ------------------------------------------------------------------ G2

def test_replay_contract_never_touches_the_nondeterministic_path():
    """G2. The numerical replay contract must not call the function that uses `random`.

    The cross-runtime byte-identity result rests on this. It was true by inspection; now it is
    enforced.
    """
    with open(RUN_REPLAY, encoding="utf-8") as f:
        src = f.read()
    assert PERMITTED_RANDOM_HOST not in src, (
        f"run_replay.py references {PERMITTED_RANDOM_HOST}; the replay contract would then "
        f"depend on `random` and the byte-identity claim would need re-establishing.")
    assert "stationary_power" in src, "replay must still use the adjudicated solver"


# ------------------------------------------------------------------ G3

def test_protected_deterministic_surface_admits_no_exemptions():
    """G3. foundry + integration are the surfaces consumers bind to and players run on.

    proteus/v0_6 is analysis code and carries one recorded exemption (G1). The protected surface
    carries none, and this asserts the exemption list can never quietly grow to include it.
    """
    from proteus.tests.test_package_import_hygiene import EXEMPTIONS
    protected = ("proteus/foundry/", "proteus/integration/")
    leaked = [k for k in EXEMPTIONS if k[0].startswith(protected)]
    assert not leaked, (
        f"exemption(s) recorded on the PROTECTED deterministic surface: {leaked}. "
        f"Nothing on foundry/ or integration/ may be exempted from the import rules.")


# ------------------------------------------------------------------ G4

def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                          timeout=60).stdout


def test_no_generated_artifacts_are_tracked():
    """G4. `git add -f <dir>` swept six __pycache__/*.pyc files into the repo once already.

    .gitignore lists them, but -f overrides .gitignore, and -f is exactly what the preservation
    workflow uses to commit run logs the directive requires. So .gitignore cannot prevent a
    recurrence and this gate is the actual control.
    """
    tracked = [ln for ln in _git("ls-files", "proteus", "roles/Proteus").splitlines()
               if "__pycache__" in ln or ln.endswith(".pyc") or ln.endswith(".pyo")]
    assert not tracked, (
        f"generated artifacts are tracked again: {tracked[:10]}. The preservation workflow uses "
        f"`git add -f`, which overrides .gitignore; add paths explicitly rather than a directory.")


# ------------------------------------------------------------------ G5

def test_consumer_document_cannot_deny_the_registry_while_it_exists():
    """G5. The document said 'there is no registry' for a day while sitting beside the registry.

    A sibling seat found it, not Proteus. Every surviving mention must now be explicitly marked
    historical, quoted, or superseded, so the denial cannot read as current guidance.
    """
    assert os.path.exists(REGISTRY_JSON), "registry missing; this gate assumes it exists"
    with open(CONSUMER_DOC, encoding="utf-8") as f:
        lines = f.readlines()
    markers = ("AMENDED", "Historical", "historical", "SUPERSEDED", "~~", "which was true on",
               "original sentence")
    subject = ("registr", "dictionary", "catalog", "enumeration")
    denial = ("no registr", "does not exist", "not exist", "no dictionary", "no catalog",
              "no enumeration")
    offenders = []
    for i, ln in enumerate(lines, 1):
        low = ln.lower()
        # a denial only counts when it is ABOUT the registry; the document also legitimately
        # discusses things that do not exist in general terms.
        if any(t in low for t in subject) and any(d in low for d in denial):
            window = "".join(lines[max(0, i - 12):i + 2])
            if not any(m in window for m in markers):
                offenders.append((i, ln.strip()[:90]))
    assert not offenders, (
        f"unqualified registry denial(s) in the living consumer document: {offenders}. "
        f"Mark them historical/superseded or remove them; the registry exists.")
