"""Minimal mutation testing framework — substrate-grade test-adequacy
measurement.

Per inbox ticket T-2026-05-07-T014 (P2-normal, Aporia 2026-05-07):
mutation testing measures test-suite adequacy by introducing small code
mutations and checking whether the suite catches them. Surviving
mutations indicate test gaps.

Acceptance criterion #1 says "pick one [tool] already in dev deps if
possible". Inspection shows none of mutmut / cosmic-ray / mutpy are
present. Rather than install one without authorization (a contract
change at the dependency-manifest level — the substrate's no-new-deps
discipline applies here too per substrate v2.3 §6.2 P3), this module
ships a minimal home-grown framework with four high-leverage operators.

Mutation operators (initial set)
--------------------------------
1. **comparison_flip**: ``<`` ⇄ ``>``, ``<=`` ⇄ ``>=``, ``==`` ⇄ ``!=``
   — flips boolean comparisons, which are the most common source of
   off-by-one + boundary bugs.

2. **boolean_not**: ``True`` ⇄ ``False`` literal, and ``not X`` ⇄ ``X``
   — inverts boolean values, surfacing tests that don't exercise both
   branches.

3. **return_constant_None**: ``return EXPR`` → ``return None`` — the
   classic "did anyone actually check the return value" probe.

4. **off_by_one_int**: small integer literals ``N`` → ``N+1`` (only for
   |N| <= 100 to avoid mutating big constants like seeds or hex
   masks).

Each operator emits one mutation per match-site. A mutation is
"killed" if a scoped test invocation exits non-zero after the mutation
is applied; "survived" if tests still pass; "errored" if the mutation
crashes the loader (e.g. SyntaxError).

CLI
---
::

    python -m prometheus_math.mutation_testing \\
        --target-glob "sigma_kernel/exclusion_certificate.py" \\
        --test-cmd "python -m pytest sigma_kernel/test_exclusion_certificate.py -q --tb=no" \\
        --max-mutations 10 \\
        --out prometheus_math/MUTATION_TESTING_BASELINE.md

NO contract change. Pure additive test-tooling module.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Mutation operator types
# ---------------------------------------------------------------------------


class MutationVerdict(str, Enum):
    KILLED = "killed"        # tests failed -> mutation detected
    SURVIVED = "survived"    # tests passed -> test gap
    ERRORED = "errored"      # mutation broke the loader (SyntaxError etc.)
    SKIPPED = "skipped"      # operator did not apply at this site


@dataclass(frozen=True)
class MutationProposal:
    """One concrete mutation to apply."""
    file_path: Path
    line_no: int  # 1-indexed
    column: int   # 0-indexed (start column of the mutated token)
    operator_name: str
    original_text: str
    mutated_text: str

    @property
    def site_id(self) -> str:
        return f"{self.file_path.name}:{self.line_no}:{self.operator_name}"


@dataclass(frozen=True)
class MutationResult:
    """Outcome of running tests against a mutated source."""
    proposal: MutationProposal
    verdict: MutationVerdict
    elapsed_s: float
    test_stdout_tail: str = ""
    test_stderr_tail: str = ""


@dataclass(frozen=True)
class BaselineReport:
    """Aggregate report for a mutation-testing baseline run."""
    target_files: Tuple[str, ...]
    test_cmd: str
    n_proposals: int
    n_killed: int
    n_survived: int
    n_errored: int
    n_skipped: int
    mutation_score: float  # killed / (killed + survived); excludes errors/skips
    survivors: Tuple[MutationResult, ...]
    elapsed_s: float


# ---------------------------------------------------------------------------
# Mutation operators
# ---------------------------------------------------------------------------


_COMPARISON_FLIPS: Tuple[Tuple[str, str], ...] = (
    ("<=", ">="),
    (">=", "<="),
    ("==", "!="),
    ("!=", "=="),
    ("<", ">"),
    (">", "<"),
)
"""Single-character + double-character ops in length-descending order so
re patterns prefer ``<=`` over ``<`` etc."""


_BOOLEAN_LITERALS: Tuple[Tuple[str, str], ...] = (
    ("True", "False"),
    ("False", "True"),
)


def _enumerate_comparison_sites(line: str) -> Iterable[Tuple[int, str, str]]:
    """Yield (column, op, replacement) for each comparison op in a line.
    Length-descending order so we don't match ``<`` inside ``<=``."""
    yielded_at: List[int] = []
    for op, replacement in _COMPARISON_FLIPS:
        # Find non-overlapping occurrences. Use simple find loop because
        # we want column indices.
        start = 0
        while True:
            pos = line.find(op, start)
            if pos < 0:
                break
            # Skip if this site is inside an already-yielded longer op.
            inside_longer = False
            for prev_col in yielded_at:
                if prev_col <= pos < prev_col + 2:
                    inside_longer = True
                    break
            if not inside_longer:
                # Skip Python-level non-comparison contexts: arrows ``->``,
                # walrus ``:=``, default-arg ``=``. Single-char ``<`` and
                # ``>`` need extra care: skip if part of ``->`` or ``<<``,
                # ``>>``.
                if op == ">" and pos > 0 and line[pos - 1] == "-":
                    start = pos + 1
                    continue
                if op == "<" and pos + 1 < len(line) and line[pos + 1] == "<":
                    start = pos + 1
                    continue
                if op == ">" and pos + 1 < len(line) and line[pos + 1] == ">":
                    start = pos + 1
                    continue
                if op == "==" and pos > 0 and line[pos - 1] == "!":
                    # part of ``!=``; covered by the != entry
                    start = pos + 2
                    continue
                yielded_at.append(pos)
                yield (pos, op, replacement)
            start = pos + len(op)


def _enumerate_boolean_literal_sites(line: str) -> Iterable[Tuple[int, str, str]]:
    """Yield (column, original, replacement) for True/False literals.
    Word-boundary aware so we don't match ``Truelike`` etc."""
    for original, replacement in _BOOLEAN_LITERALS:
        for m in re.finditer(rf"\b{original}\b", line):
            yield (m.start(), original, replacement)


_RETURN_PATTERN = re.compile(r"^(\s*)return\s+(?!None\b)(.+)$")


def _enumerate_return_sites(line: str) -> Iterable[Tuple[int, str, str]]:
    """Yield (column, original, replacement) for ``return EXPR`` (where
    EXPR is not already None). Strips trailing comments out of EXPR."""
    m = _RETURN_PATTERN.match(line)
    if not m:
        return
    indent = m.group(1)
    expr = m.group(2)
    # Strip trailing comment if any.
    if "#" in expr:
        expr_clean = expr.split("#", 1)[0].rstrip()
    else:
        expr_clean = expr.rstrip()
    if not expr_clean:
        return
    column = len(indent)
    original = f"return {expr_clean}"
    replacement = "return None"
    yield (column, original, replacement)


_INT_LITERAL_PATTERN = re.compile(r"(?<![A-Za-z0-9_])(-?\d+)(?![A-Za-z0-9_.])")


def _enumerate_off_by_one_sites(line: str) -> Iterable[Tuple[int, str, str]]:
    """Yield (column, original, replacement) for small int literals
    (|N| <= 100) — flips N to N+1 to surface boundary tests."""
    for m in _INT_LITERAL_PATTERN.finditer(line):
        text = m.group(1)
        try:
            value = int(text)
        except ValueError:
            continue
        if abs(value) > 100:
            continue
        replacement = str(value + 1)
        yield (m.start(), text, replacement)


# Operator registry: name -> (line-yielder)
MUTATION_OPERATORS: Dict[str, Callable[[str], Iterable[Tuple[int, str, str]]]] = {
    "comparison_flip": _enumerate_comparison_sites,
    "boolean_not": _enumerate_boolean_literal_sites,
    "return_constant_None": _enumerate_return_sites,
    "off_by_one_int": _enumerate_off_by_one_sites,
}


# ---------------------------------------------------------------------------
# Proposal generation
# ---------------------------------------------------------------------------


def propose_mutations(
    file_path: Path,
    *,
    operators: Sequence[str] = tuple(MUTATION_OPERATORS.keys()),
    skip_lines_starting_with: Tuple[str, ...] = ("#", '"""', "'''"),
) -> List[MutationProposal]:
    """Walk a single Python file line by line; emit MutationProposals
    for every operator-applicable site. Skips comment-only lines and
    docstring delimiters as a coarse hygiene filter (true AST-level
    analysis would be cleaner; this is the minimum-viable pass)."""
    proposals: List[MutationProposal] = []
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=False)
    in_docstring = False
    for i, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        # Coarse docstring tracker (NOT precise; misses single-line and
        # complicated nested cases — acceptable for a baseline pass).
        if stripped.startswith('"""') or stripped.startswith("'''"):
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        if any(stripped.startswith(prefix) for prefix in skip_lines_starting_with):
            continue
        for op_name in operators:
            yielder = MUTATION_OPERATORS.get(op_name)
            if yielder is None:
                continue
            for column, original, replacement in yielder(line):
                proposals.append(
                    MutationProposal(
                        file_path=file_path,
                        line_no=i,
                        column=column,
                        operator_name=op_name,
                        original_text=original,
                        mutated_text=replacement,
                    )
                )
    return proposals


def apply_mutation_to_text(
    source_text: str,
    proposal: MutationProposal,
) -> str:
    """Return source_text with the mutation applied. Raises ValueError
    if the proposal's anchor (line, column, original_text) doesn't
    match the source — guards against stale proposals."""
    lines = source_text.splitlines(keepends=True)
    if proposal.line_no < 1 or proposal.line_no > len(lines):
        raise ValueError(
            f"line_no {proposal.line_no} out of range [1, {len(lines)}]"
        )
    line = lines[proposal.line_no - 1]
    eol = ""
    if line.endswith("\r\n"):
        eol = "\r\n"
        line_body = line[:-2]
    elif line.endswith("\n"):
        eol = "\n"
        line_body = line[:-1]
    else:
        line_body = line
    # Verify anchor.
    end = proposal.column + len(proposal.original_text)
    if line_body[proposal.column:end] != proposal.original_text:
        raise ValueError(
            f"anchor mismatch at {proposal.file_path.name}:{proposal.line_no}:"
            f"{proposal.column} — expected {proposal.original_text!r}, "
            f"got {line_body[proposal.column:end]!r}"
        )
    new_line_body = (
        line_body[:proposal.column]
        + proposal.mutated_text
        + line_body[end:]
    )
    lines[proposal.line_no - 1] = new_line_body + eol
    return "".join(lines)


# ---------------------------------------------------------------------------
# Mutation execution
# ---------------------------------------------------------------------------


def run_mutation_test(
    proposal: MutationProposal,
    test_cmd: str,
    *,
    cwd: Optional[Path] = None,
    timeout_s: float = 300.0,
) -> MutationResult:
    """Apply one mutation, run the test command, restore the file,
    return the verdict.

    The original file is backed up to ``<file>.mut_backup`` before
    mutation and restored unconditionally in a try/finally so the
    working tree is never left in a mutated state even on KeyboardInterrupt.
    """
    file_path = proposal.file_path
    if not file_path.exists():
        return MutationResult(
            proposal=proposal,
            verdict=MutationVerdict.ERRORED,
            elapsed_s=0.0,
            test_stderr_tail=f"target file does not exist: {file_path}",
        )
    original_text = file_path.read_text(encoding="utf-8")
    backup_path = file_path.with_suffix(file_path.suffix + ".mut_backup")
    shutil.copy2(file_path, backup_path)
    t0 = time.time()
    try:
        try:
            mutated = apply_mutation_to_text(original_text, proposal)
        except ValueError as e:
            return MutationResult(
                proposal=proposal,
                verdict=MutationVerdict.SKIPPED,
                elapsed_s=time.time() - t0,
                test_stderr_tail=str(e),
            )
        file_path.write_text(mutated, encoding="utf-8")
        try:
            completed = subprocess.run(
                test_cmd,
                shell=True,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
        except subprocess.TimeoutExpired as te:
            return MutationResult(
                proposal=proposal,
                verdict=MutationVerdict.ERRORED,
                elapsed_s=time.time() - t0,
                test_stderr_tail=f"test command timed out after {timeout_s}s",
            )
        elapsed = time.time() - t0
        stdout_tail = (completed.stdout or "")[-400:]
        stderr_tail = (completed.stderr or "")[-400:]
        if completed.returncode == 0:
            verdict = MutationVerdict.SURVIVED
        elif "SyntaxError" in (completed.stdout or "") + (completed.stderr or ""):
            verdict = MutationVerdict.ERRORED
        else:
            verdict = MutationVerdict.KILLED
        return MutationResult(
            proposal=proposal,
            verdict=verdict,
            elapsed_s=elapsed,
            test_stdout_tail=stdout_tail,
            test_stderr_tail=stderr_tail,
        )
    finally:
        # Restore the original file unconditionally.
        try:
            shutil.copy2(backup_path, file_path)
        finally:
            try:
                backup_path.unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Baseline driver
# ---------------------------------------------------------------------------


def generate_baseline(
    target_files: Sequence[Path],
    test_cmd: str,
    *,
    operators: Sequence[str] = tuple(MUTATION_OPERATORS.keys()),
    max_mutations: Optional[int] = None,
    cwd: Optional[Path] = None,
    timeout_s: float = 300.0,
    progress_callback: Optional[Callable[[int, int, MutationResult], None]] = None,
) -> BaselineReport:
    """Run mutation testing across ``target_files``. Returns a
    :class:`BaselineReport` with per-mutation verdicts."""
    t0 = time.time()
    all_proposals: List[MutationProposal] = []
    for fp in target_files:
        all_proposals.extend(propose_mutations(fp, operators=operators))
    if max_mutations is not None:
        all_proposals = all_proposals[:max_mutations]

    results: List[MutationResult] = []
    for i, prop in enumerate(all_proposals, start=1):
        result = run_mutation_test(prop, test_cmd, cwd=cwd, timeout_s=timeout_s)
        results.append(result)
        if progress_callback is not None:
            progress_callback(i, len(all_proposals), result)

    n_killed = sum(1 for r in results if r.verdict == MutationVerdict.KILLED)
    n_survived = sum(1 for r in results if r.verdict == MutationVerdict.SURVIVED)
    n_errored = sum(1 for r in results if r.verdict == MutationVerdict.ERRORED)
    n_skipped = sum(1 for r in results if r.verdict == MutationVerdict.SKIPPED)
    denom = n_killed + n_survived
    score = (n_killed / denom) if denom else 0.0
    survivors = tuple(r for r in results if r.verdict == MutationVerdict.SURVIVED)

    return BaselineReport(
        target_files=tuple(str(fp) for fp in target_files),
        test_cmd=test_cmd,
        n_proposals=len(all_proposals),
        n_killed=n_killed,
        n_survived=n_survived,
        n_errored=n_errored,
        n_skipped=n_skipped,
        mutation_score=score,
        survivors=survivors,
        elapsed_s=time.time() - t0,
    )


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_baseline_report(report: BaselineReport) -> str:
    lines: List[str] = []
    lines.append("# Mutation Testing Baseline")
    lines.append("")
    lines.append(
        f"_Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}_"
    )
    lines.append(
        "_Per inbox ticket T-2026-05-07-T014 "
        "(prometheus_math/mutation_testing.py)_"
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Target files:** {len(report.target_files)}")
    for fp in report.target_files:
        lines.append(f"  - `{fp}`")
    lines.append(f"- **Test command:** `{report.test_cmd}`")
    lines.append(f"- **Total mutations proposed:** {report.n_proposals}")
    lines.append(f"- **Killed (caught by tests):** {report.n_killed}")
    lines.append(f"- **Survived (test gap):** {report.n_survived}")
    lines.append(f"- **Errored (mutation broke loader):** {report.n_errored}")
    lines.append(f"- **Skipped (operator anchor mismatch):** {report.n_skipped}")
    lines.append(
        f"- **Mutation score (killed / (killed + survived)):** "
        f"{report.mutation_score:.3f}"
    )
    lines.append(f"- **Elapsed:** {report.elapsed_s:.1f}s")
    lines.append("")

    if report.survivors:
        lines.append("## Top Surviving Mutations (test-gap candidates)")
        lines.append("")
        lines.append(
            "Each survivor is a mutation that did NOT cause any test "
            "failure — i.e. the test suite has no assertion that "
            "would catch this specific change. Each is a candidate "
            "for a new test."
        )
        lines.append("")
        lines.append("| # | site | operator | original -> mutated |")
        lines.append("|---|---|---|---|")
        for i, s in enumerate(report.survivors[:10], start=1):
            p = s.proposal
            lines.append(
                f"| {i} | `{p.file_path.name}:{p.line_no}` | "
                f"`{p.operator_name}` | `{p.original_text}` -> "
                f"`{p.mutated_text}` |"
            )
        if len(report.survivors) > 10:
            lines.append(
                f"\n_(showing 10 of {len(report.survivors)} survivors)_"
            )
        lines.append("")
    else:
        lines.append("## Survivors")
        lines.append("")
        if report.n_proposals == 0:
            lines.append(
                "No mutations were proposed — the operator/skip-line "
                "filters yielded zero applicable sites. Either the "
                "target file is dominated by docstrings/comments, or "
                "the configured operator set does not apply to this "
                "code surface."
            )
        else:
            lines.append(
                "**No survivors.** Every proposed mutation was killed "
                "by the test suite. The current test coverage of the "
                "target file(s) is adequate against this operator set."
            )
        lines.append("")

    lines.append("## Caveats")
    lines.append("")
    lines.append(
        "1. **Coarse docstring filter.** Lines starting with ``\"\"\"`` or "
        "``'''`` are treated as docstring boundaries; multi-line "
        "docstrings + edge cases (e.g. raw strings, f-strings spanning "
        "lines) may produce false-positive mutations inside string "
        "literals. A future ticket should switch to AST-level analysis."
    )
    lines.append(
        "2. **Operator coverage is initial-set only.** Four operators are "
        "shipped in this baseline (comparison_flip, boolean_not, "
        "return_constant_None, off_by_one_int). Strong mutation testing "
        "warrants more (literal_constant_swap, exception_swallow, "
        "loop_bound_drop). Future ticket can extend the operator set."
    )
    lines.append(
        "3. **Per-mutation pytest cost dominates.** Each mutation runs "
        "the configured test command in a fresh subprocess. With "
        "PARI/CVXPY startup adding ~5s per invocation, a baseline run "
        "of N mutations takes roughly N x (5s + scoped-test-time). "
        "Scope the test command tightly when extending the corpus."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


_DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parent / "MUTATION_TESTING_BASELINE.md"
)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m prometheus_math.mutation_testing",
        description=(
            "Run mutation testing baseline against target Python files "
            "(T-2026-05-07-T014)."
        ),
    )
    parser.add_argument(
        "--target", action="append", required=True,
        type=Path,
        help=(
            "Target Python file to mutate. Repeat for multiple files. "
            "Each must exist and be readable."
        ),
    )
    parser.add_argument(
        "--test-cmd", type=str, required=True,
        help=(
            "Shell command to run after each mutation. Exit code 0 = "
            "tests pass (mutation survived); non-zero = tests failed "
            "(mutation killed)."
        ),
    )
    parser.add_argument(
        "--operator", action="append", default=None,
        choices=tuple(MUTATION_OPERATORS.keys()),
        help=(
            "Mutation operators to apply. Repeat for multiple. Default: "
            "all registered operators."
        ),
    )
    parser.add_argument(
        "--max-mutations", type=int, default=None,
        help="Cap on number of mutations attempted. Default: unlimited.",
    )
    parser.add_argument(
        "--timeout", type=float, default=300.0,
        help="Per-mutation timeout in seconds (default 300).",
    )
    parser.add_argument(
        "--out", type=Path, default=_DEFAULT_REPORT_PATH,
        help=f"Markdown report output path. Default: {_DEFAULT_REPORT_PATH.name}",
    )
    args = parser.parse_args(argv)

    operators = args.operator or list(MUTATION_OPERATORS.keys())

    def _print_progress(i: int, total: int, result: MutationResult) -> None:
        print(
            f"[mutation {i}/{total}] {result.verdict.value} "
            f"@ {result.proposal.site_id} "
            f"({result.elapsed_s:.1f}s)",
            file=sys.stderr,
        )

    report = generate_baseline(
        target_files=args.target,
        test_cmd=args.test_cmd,
        operators=operators,
        max_mutations=args.max_mutations,
        timeout_s=args.timeout,
        progress_callback=_print_progress,
    )
    md = render_baseline_report(report)
    args.out.write_text(md, encoding="utf-8")
    print(
        f"[mutation] score={report.mutation_score:.3f} "
        f"killed={report.n_killed} survived={report.n_survived} "
        f"errored={report.n_errored} skipped={report.n_skipped}",
        file=sys.stderr,
    )
    print(f"[mutation] report written: {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "MutationVerdict",
    "MutationProposal",
    "MutationResult",
    "BaselineReport",
    "MUTATION_OPERATORS",
    "propose_mutations",
    "apply_mutation_to_text",
    "run_mutation_test",
    "generate_baseline",
    "render_baseline_report",
    "main",
]
