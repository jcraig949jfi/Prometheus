"""Lean 4 proof-checker oracle — the verdict lane the arsenal scan asked for (2026-08-21).

Arsenal scan item C proposed installing Lean as a CHECKING SERVICE, not a prover model:
machine-checkable claims become a verdict class, and canon R9 (lemma invention) needs exactly
this per canon §7. The spike found Lean 4.30.0 already present via elan on M1, so this is a
wrap, not a procurement (Standing Order #1).

What this is NOT: a theorem prover, an autoformalizer, or an LLM. It answers one question —
*does this Lean source compile, and does this theorem check?* — and returns a typed verdict
with the checker's own diagnostics. The value is that its NO is trustworthy: the smoke test
that motivated this module is Lean refusing `2 + 2 = 5`.

Verdicts are deliberately three-valued: PROVED / REFUTED / ERROR. A syntax error is not a
refutation, and conflating them would be exactly the phantom-failure pathology canon R6 warns
about (a checker that reports "false" when it means "I could not tell").
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

__all__ = ["LeanVerdict", "lean_available", "check_lean_source", "check_theorem",
           "check_with_lemma", "DEFAULT_TOOLCHAIN"]

DEFAULT_TOOLCHAIN = "leanprover/lean4:v4.30.0"

#: Diagnostic fragments that mean "the checker actively determined the claim is FALSE",
#: as opposed to "the checker could not finish". Kept explicit and narrow.
_REFUTATION_MARKERS = (
    "proved that the proposition",   # `decide` refuting a decidable prop
    "is false",
)


@dataclass(frozen=True)
class LeanVerdict:
    """PROVED / REFUTED / ERROR, plus the checker's own words."""

    status: str                  # "PROVED" | "REFUTED" | "ERROR"
    diagnostics: str
    toolchain: str
    source_sha: str = ""

    @property
    def proved(self) -> bool:
        return self.status == "PROVED"

    @property
    def refuted(self) -> bool:
        """True ONLY when the checker actively determined falsity — never on an error."""
        return self.status == "REFUTED"


def lean_available() -> bool:
    """Is a Lean binary reachable? Callers should degrade to abstention, never to a guess."""
    return _lean_binary() is not None


def _lean_binary() -> Optional[str]:
    direct = shutil.which("lean")
    if direct:
        return direct
    elan = Path.home() / ".elan" / "bin" / ("lean.exe" if os.name == "nt" else "lean")
    return str(elan) if elan.exists() else None


def check_lean_source(
    source: str,
    toolchain: str = DEFAULT_TOOLCHAIN,
    timeout_s: int = 300,
) -> LeanVerdict:
    """Compile a Lean source fragment and classify the result.

    A `lean-toolchain` file is written beside the source because elan resolves the toolchain
    from the working directory; without it the shim picks a stale nightly (found the hard way
    on M1, where the default was a 2023 nightly that rejects modern syntax).
    """
    import hashlib

    binary = _lean_binary()
    if binary is None:
        return LeanVerdict("ERROR", "no Lean binary found (elan not installed?)", toolchain)

    sha = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
    with tempfile.TemporaryDirectory(prefix="pm_lean_") as td:
        d = Path(td)
        (d / "lean-toolchain").write_text(toolchain + "\n", encoding="utf-8")
        src = d / "claim.lean"
        src.write_text(source, encoding="utf-8")
        try:
            proc = subprocess.run(
                [binary, str(src)], cwd=str(d), capture_output=True, text=True,
                timeout=timeout_s,
            )
        except subprocess.TimeoutExpired:
            return LeanVerdict("ERROR", f"lean timed out after {timeout_s}s", toolchain, sha)

    out = (proc.stdout + proc.stderr).strip()
    lowered = out.lower()
    if "error" not in lowered:
        return LeanVerdict("PROVED", out, toolchain, sha)
    if all(m in lowered for m in _REFUTATION_MARKERS):
        return LeanVerdict("REFUTED", out, toolchain, sha)
    return LeanVerdict("ERROR", out, toolchain, sha)


def check_theorem(
    statement: str,
    proof: str = "by decide",
    preamble: str = "",
    toolchain: str = DEFAULT_TOOLCHAIN,
    timeout_s: int = 300,
) -> LeanVerdict:
    """Check one theorem: `theorem pm_claim : <statement> := <proof>`.

    The generated name is fixed so diagnostics are stable across calls, and the preamble slot
    exists for imports/definitions the statement depends on.
    """
    body = f"{preamble}\ntheorem pm_claim : {statement} := {proof}\n"
    return check_lean_source(body, toolchain=toolchain, timeout_s=timeout_s)


def check_with_lemma(
    lemma_name: str,
    lemma_statement: str,
    lemma_proof: str,
    goal_statement: str,
    goal_proof: str,
    preamble: str = "",
    toolchain: str = DEFAULT_TOOLCHAIN,
    timeout_s: int = 300,
) -> "LeanVerdict":
    """Check a lemma AND a goal whose proof may invoke it (canon R9 support, cycle 016).

    Emits:
        <preamble>
        theorem <lemma_name> : <lemma_statement> := <lemma_proof>
        theorem pm_goal : <goal_statement> := <goal_proof>

    Both must check for a PROVED verdict, which is the point: an invented lemma that does not
    itself hold is not a contribution, however useful it would have been.
    """
    lines = [
        preamble,
        f"theorem {lemma_name} : {lemma_statement} := {lemma_proof}",
        f"theorem pm_goal : {goal_statement} := {goal_proof}",
        "",
    ]
    body = "\n".join(lines)
    return check_lean_source(body, toolchain=toolchain, timeout_s=timeout_s)
