#!/usr/bin/env python
"""Mutation harness — tests the tests.

    python attacks/mutation_harness.py <source.py> <test_file.py> [max_mutants]

Deliberately corrupts a module one AST node at a time and re-runs that module's own
test file. A mutant that SURVIVES — tests still green on deliberately broken code —
is a hole in the suite. Mutation score = killed / tested.

**Why this instrument and not a review:** there is no judgment anywhere in the verdict
path. The verdict is pytest's exit code on code that is known-broken. It cannot be
flattered, cannot be sycophantic, and does not care who wrote the tests.

**What it does NOT tell you** (state this whenever you quote a score):

1. *Equivalent mutants.* Some mutations do not change behaviour; they are unkillable
   and depress the score without indicating a real hole. Read survivors individually.
2. *It measures the tests against the implementation, never against the intent.* A
   100% score means "the tests notice when this code changes," not "this code does
   the right thing." A module that implements the wrong concept perfectly will score
   perfectly.
3. *It cannot catch a check that is vacuous by construction.* If a member is
   `return True`, mutating it to `return False` gets killed by a test asserting the
   tautology, and the suite looks healthy. That failure mode needs the DUAL
   instrument — the structural-constancy probe in `prometheus_math.battery`, which
   asks whether a member reads its arguments at all and can ever fire.

Use both. Mutation testing catches tests that do not notice broken code; the
constancy probe catches code that cannot fail. Neither catches a circuit that is
merely beaten by a trivial baseline — for that, run the baseline.

**Safety:** the target file is rewritten in place per mutant and restored in a
`finally`. A `.mutation_bak` copy is written first. Never run this concurrently with
a commit, and never on a dirty working tree.
"""
import ast
import atexit
import pathlib
import signal
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]

CMP_SWAP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt,
            ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Is: ast.IsNot,
            ast.IsNot: ast.Is, ast.In: ast.NotIn, ast.NotIn: ast.In}
BIN_SWAP = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div, ast.Div: ast.Mult}
FUNC_NAMES = []


class Mutator(ast.NodeTransformer):
    """Applies exactly the `target`-th mutation encountered in traversal order."""

    def __init__(self, target_index):
        self.target = target_index
        self.seen = 0
        self.applied = None

    def _hit(self):
        match = (self.seen == self.target)
        self.seen += 1
        return match

    def visit_Return(self, node):
        self.generic_visit(node)
        if node.value is not None and not (
                isinstance(node.value, ast.Constant) and node.value.value is None):
            if self._hit():
                self.applied = f"line {node.lineno}: return <expr> -> return None"
                return ast.copy_location(ast.Return(value=ast.Constant(value=None)), node)
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in FUNC_NAMES and len(FUNC_NAMES) > 1:
            if self._hit():
                alt = [f for f in FUNC_NAMES if f != node.id][0]
                self.applied = f"line {node.lineno}: {node.id} -> {alt}"
                return ast.copy_location(ast.Name(id=alt, ctx=ast.Load()), node)
        return node

    def visit_Compare(self, node):
        self.generic_visit(node)
        if len(node.ops) == 1 and type(node.ops[0]) in CMP_SWAP:
            old = type(node.ops[0])
            if self._hit():
                node.ops = [CMP_SWAP[old]()]
                self.applied = f"line {node.lineno}: {old.__name__} -> {CMP_SWAP[old].__name__}"
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if self._hit():
            old = type(node.op).__name__
            node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
            self.applied = f"line {node.lineno}: {old} -> {type(node.op).__name__}"
        return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Not) and self._hit():
            self.applied = f"line {node.lineno}: removed `not`"
            return node.operand
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if type(node.op) in BIN_SWAP:
            old = type(node.op)
            if self._hit():
                node.op = BIN_SWAP[old]()
                self.applied = f"line {node.lineno}: {old.__name__} -> {BIN_SWAP[old].__name__}"
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, bool):
            if self._hit():
                self.applied = f"line {node.lineno}: {node.value} -> {not node.value}"
                return ast.copy_location(ast.Constant(value=not node.value), node)
        elif isinstance(node.value, int):
            if self._hit():
                self.applied = f"line {node.lineno}: {node.value} -> {node.value + 1}"
                return ast.copy_location(ast.Constant(value=node.value + 1), node)
        return node


def _restore(src, original, bak):
    """Idempotent restore — runs from finally, atexit, and signal handlers alike."""
    try:
        if src.read_text(encoding="utf-8") != original:
            src.write_text(original, encoding="utf-8")
            print(f"[restored {src.name} from mutation]")
        bak.unlink(missing_ok=True)
    except Exception:
        pass


def run_tests(test_file):
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-q", "--no-header",
         "-x", "-p", "no:cacheprovider"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    return r.returncode


def count_sites(original: str) -> int:
    """How many mutable sites exist, so a run can report sampled/total honestly."""
    n = 0
    while True:
        m = Mutator(n)
        m.visit(ast.parse(original))
        if m.applied is None:
            return n
        n += 1


def mutation_test(src: pathlib.Path, test_file: pathlib.Path, cap: int = 0,
                  sample_ok: bool = False):
    """cap=0 means ENUMERATE ALL SITES (the default, deliberately).

    A truncated run takes the first N sites in AST traversal order — i.e. the TOP of the
    file — which systematically misses the verdict-bearing functions that live lower down.
    Measured 2026-08-23: canon_r6_falsification reads 100% at cap=20 and 85.2% on full
    enumeration, with survival 0/20 inside the sampled window and 9/41 outside it
    (Fisher p=0.024). Truncation here is not neutral; it flatters. A score from a truncated
    run is therefore refused unless sample_ok is set, and always prints sampled/total.
    """
    # STARTUP RESTORE — the only recovery that survives a hard kill. Signal/atexit handlers
    # do NOT run when the process is terminated (MEASURED on Windows 2026-08-23: a 600s tool
    # timeout left ergon/probe/analysis.py mutated in the working tree despite both being
    # registered). If a .mutation_bak is on disk, a previous run died mid-mutation: restore
    # from it before touching anything.
    stale = src.with_suffix(".mutation_bak")
    if stale.exists():
        prior = stale.read_text(encoding="utf-8")
        if src.read_text(encoding="utf-8") != prior:
            src.write_text(prior, encoding="utf-8")
            print(f"[RECOVERED {src.name} — a previous run died mid-mutation and left it "
                  f"corrupted; restored from {stale.name}]")
        stale.unlink(missing_ok=True)

    original = src.read_text(encoding="utf-8")
    tree = ast.parse(original)
    FUNC_NAMES[:] = [n.name for n in ast.walk(tree)
                     if isinstance(n, ast.FunctionDef) and not n.name.startswith("__")]

    if run_tests(test_file) != 0:
        print(f"BASELINE RED ({src.name}) — cannot mutation-test a failing suite.")
        return None

    total_sites = count_sites(original)
    n = total_sites if cap in (0, None) else min(cap, total_sites)
    truncated = n < total_sites
    if truncated and not sample_ok:
        print(f"REFUSED: {src.name} has {total_sites} mutable sites; a cap of {cap} would "
              f"sample only the first {n} in AST order (top of file) and flatter the score. "
              f"Re-run with cap=0 for full enumeration, or pass sample_ok=True to accept a "
              f"sampled run — which must be reported as {n}/{total_sites}, never as a bare score.")
        return None

    bak = src.with_suffix(".mutation_bak")
    bak.write_text(original, encoding="utf-8")
    # a hard kill does not run `finally`; this does
    atexit.register(_restore, src, original, bak)
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, lambda *_: (_restore(src, original, bak), sys.exit(130)))
        except (ValueError, OSError):
            pass  # not on the main thread / unsupported platform

    killed = survived = invalid = 0
    survivors = []
    t0 = time.time()
    try:
        for i in range(n):
            m = Mutator(i)
            new_tree = m.visit(ast.parse(original))
            if m.applied is None:
                break  # ran out of mutable sites
            ast.fix_missing_locations(new_tree)
            try:
                src.write_text(ast.unparse(new_tree), encoding="utf-8")
            except Exception:
                invalid += 1
                continue
            if run_tests(test_file) == 0:
                survived += 1
                survivors.append(m.applied)
                print(f"  SURVIVED  {m.applied}")
            else:
                killed += 1
    finally:
        _restore(src, original, bak)

    tested = killed + survived
    score = killed / tested if tested else 0.0
    scope = "FULL" if not truncated else f"SAMPLED {n}/{total_sites}"
    print(f"{src.name}  killed={killed} survived={survived} score={score:.1%} "
          f"[{scope} of {total_sites} sites] ({time.time() - t0:.0f}s)")
    if tested < 10:
        print(f"  NOTE: only {tested} mutable sites — a high score on a thin module is a "
              f"weak statement. Report the denominator, always.")
    return {"module": src.name, "killed": killed, "survived": survived,
            "score": score, "survivors": survivors, "sites_tested": tested,
            "total_sites": total_sites, "truncated": truncated}


if __name__ == "__main__":
    _cap = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    mutation_test(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), _cap,
                  sample_ok="--sample" in sys.argv)
