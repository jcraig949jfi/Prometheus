"""Forge Runner — orchestrates Builder -> Tester loop, enforces all 5 Iron Laws.

This script:
1. Invokes the Builder (NO battery access) to generate candidates
2. Runs AST-level ban-pattern checks (Law 2)
3. Invokes the Tester (NO tool modification) to evaluate candidates
4. Enforces diversity (Law 4), thresholds (Law 3), and null baseline (Law 5)
5. Logs everything

The Builder and Tester run as SEPARATE processes via subprocess.
"""
import sys, os, io, json, ast, re, subprocess, argparse, hashlib
from pathlib import Path
from datetime import datetime

if __name__ == "__main__" and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
FORGE = Path(__file__).resolve().parent
CANDIDATES = FORGE / "candidates"
VERDICTS = FORGE / "verdicts"
QUARANTINE = FORGE / "tester_quarantine"
LOG_FILE = FORGE / "runner.log"

sys.path.insert(0, str(ROOT))

from forge.thresholds import THRESHOLDS

# ── Banned patterns (Law 2) — AST dataflow analysis ───────────────────


def log(msg):
    """Log to both stdout and log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


class _CandidateTaintTracker(ast.NodeVisitor):
    """Walk AST and track which variables are derived from the 'candidates' parameter.

    A variable is 'tainted' if it:
      - IS the 'candidates' parameter of evaluate()
      - Is assigned from iterating over a tainted variable (for c in candidates)
      - Is assigned from indexing a tainted variable (c = candidates[i])
      - Is assigned from calling a method on a tainted variable (c.lower(), c.strip())
      - Is assigned from a tainted variable directly (x = c)

    Any string comparison (in, ==, !=) where one operand is tainted is a violation.
    String comparisons against non-tainted variables (prompt, self.data, etc.) are ALLOWED.
    """

    def __init__(self):
        self.tainted = set()  # variable names derived from candidates
        self._string_collection_vars = set()  # vars iterating over string lists
        self.violations = []

    def _name_of(self, node):
        """Get the string name of a Name node."""
        if isinstance(node, ast.Name):
            return node.id
        return None

    def visit_FunctionDef(self, node):
        """Detect the 'evaluate' method and taint 'candidates' parameter."""
        if node.name == 'evaluate':
            # Taint the candidates parameter (typically the 3rd arg: self, prompt, candidates)
            for arg in node.args.args:
                if arg.arg == 'candidates':
                    self.tainted.add('candidates')
        self.generic_visit(node)

    def visit_For(self, node):
        """Track 'for x in tainted_var' — x becomes tainted."""
        iter_name = self._name_of(node.iter)
        if iter_name and iter_name in self.tainted:
            target = self._name_of(node.target)
            if target:
                self.tainted.add(target)
        # Also handle tuple unpacking: for i, x in enumerate(candidates)
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'enumerate':
                if node.iter.args:
                    arg_name = self._name_of(node.iter.args[0])
                    if arg_name and arg_name in self.tainted:
                        if isinstance(node.target, ast.Tuple):
                            for elt in node.target.elts:
                                t = self._name_of(elt)
                                if t:
                                    self.tainted.add(t)
        # Track variables iterating over string collections
        # e.g., `for word in ["paradox", "reverse"]:`
        if self._is_string_list(node.iter):
            target = self._name_of(node.target)
            if target:
                self._string_collection_vars.add(target)
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Track assignments from tainted sources."""
        tainted_rhs = self._is_tainted_expr(node.value)
        if tainted_rhs:
            for target in node.targets:
                t = self._name_of(target)
                if t:
                    self.tainted.add(t)
        self.generic_visit(node)

    def _is_tainted_expr(self, node):
        """Check if an expression derives from a tainted variable."""
        if isinstance(node, ast.Name) and node.id in self.tainted:
            return True
        # x.lower(), x.strip(), etc.
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                return self._is_tainted_expr(node.func.value)
            if isinstance(node.func, ast.Name):
                # str(x), list(x)
                if node.args:
                    return self._is_tainted_expr(node.args[0])
        # x[i]
        if isinstance(node, ast.Subscript):
            return self._is_tainted_expr(node.value)
        # f-string or concatenation
        if isinstance(node, ast.BinOp):
            return self._is_tainted_expr(node.left) or self._is_tainted_expr(node.right)
        return False

    def _is_string_list(self, node):
        """Check if a node is a list/tuple/set of string literals."""
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return all(isinstance(e, ast.Constant) and isinstance(e.value, str)
                       for e in node.elts) and len(node.elts) > 0
        return False

    def _check_comprehension_taint(self, node):
        """Check list/set/generator comprehensions for tainted iteration.

        Catches patterns like:
            any(word in c.lower() for c in candidates)
            [x for x in candidates if "answer" in x]
        """
        generators = getattr(node, 'generators', [])
        for gen in generators:
            if self._is_tainted_expr(gen.iter):
                # The comprehension target variable is tainted
                target_name = self._name_of(gen.target)
                if target_name:
                    self.tainted.add(target_name)
            # Track variables iterating over string collections
            # e.g., `for word in ["paradox", "reverse"]`
            if self._is_string_list(gen.iter):
                target_name = self._name_of(gen.target)
                if target_name:
                    self._string_collection_vars.add(target_name)

    def visit_ListComp(self, node):
        self._check_comprehension_taint(node)
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self._check_comprehension_taint(node)
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self._check_comprehension_taint(node)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self._check_comprehension_taint(node)
        self.generic_visit(node)

    def _is_from_string_collection(self, node):
        """Check if a Name variable iterates over a hardcoded string list/set.

        Detects: `for word in ["paradox", "reverse", ...]` — word is from a string collection.
        """
        if isinstance(node, ast.Name) and node.id in self._string_collection_vars:
            return True
        return False

    def visit_Compare(self, node):
        """Flag string comparisons where one operand is tainted (candidate-derived)."""
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(op, (ast.Eq, ast.NotEq, ast.In, ast.NotIn)):
                left_tainted = self._is_tainted_expr(node.left)
                right_tainted = self._is_tainted_expr(comparator)

                if left_tainted or right_tainted:
                    # Case 1: OTHER operand is a string literal
                    other = comparator if left_tainted else node.left
                    if isinstance(other, ast.Constant) and isinstance(other.value, str):
                        self.violations.append(
                            f"Line {node.lineno}: string literal "
                            f"'{other.value[:50]}' compared against candidate-derived variable"
                        )
                    # Case 2: tainted expr used as container for `in` check
                    # e.g., `word in c.lower()` where c is tainted
                    elif isinstance(op, (ast.In, ast.NotIn)) and right_tainted:
                        # Right side is the container and it's tainted.
                        # Check if left side derives from a hardcoded string list
                        if self._is_from_string_collection(node.left):
                            self.violations.append(
                                f"Line {node.lineno}: string-collection variable "
                                f"checked against candidate-derived container"
                            )
        self.generic_visit(node)

    def visit_Call(self, node):
        """Flag re.search/re.match/re.findall calls on tainted variables."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 're':
                if node.func.attr in ('search', 'match', 'findall', 'sub'):
                    # Check if the string argument (2nd arg) is tainted
                    if len(node.args) >= 2 and self._is_tainted_expr(node.args[1]):
                        self.violations.append(
                            f"Line {node.lineno}: re.{node.func.attr}() on candidate-derived variable"
                        )
        self.generic_visit(node)


def check_banned_patterns(tool_path):
    """AST dataflow check: flag string comparisons against candidate-derived variables only.

    ALLOWED: if "increase" in prompt.lower()    — prompt parsing
    ALLOWED: if "rate" in self.structure          — internal state
    BANNED:  if "reverse" in candidate.lower()   — answer-key matching
    BANNED:  if "reverse" in c  (where c iterates over candidates)
    """
    source = Path(tool_path).read_text(encoding='utf-8')
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["SYNTAX ERROR — tool does not parse"]

    tracker = _CandidateTaintTracker()
    tracker.visit(tree)
    return tracker.violations


def check_composition_requirements(tool_path, tier):
    """Check that the tool imports and calls required primitives (Law 2)."""
    source = Path(tool_path).read_text(encoding='utf-8')
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["Tool has syntax errors"]

    primitive_imports = []
    amino_imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if "forge_primitives" in module:
                    primitive_imports.append(alias.name)
                elif "amino_acids" in module:
                    amino_imports.append(alias.name)

    issues = []
    if tier == 2:
        if len(primitive_imports) < 3:
            issues.append(f"T2 requires >= 3 T1 primitives, found {len(primitive_imports)}: {primitive_imports}")
        if len(amino_imports) < 1:
            issues.append(f"T2 requires >= 1 amino acid, found {len(amino_imports)}")
    elif tier == 3:
        if len(primitive_imports) < 2:
            issues.append(f"T3 requires >= 2 T1 primitives, found {len(primitive_imports)}")
        if len(amino_imports) < 1:
            issues.append(f"T3 requires >= 1 amino acid, found {len(amino_imports)}")

    return issues


def verify_builder_isolation():
    """Verify the Builder script never touches quarantine (Law 1)."""
    builder_path = FORGE / "builder.py"
    source = builder_path.read_text(encoding='utf-8')
    violations = []

    # Check for imports or file opens that reference quarantine or battery generators
    # Only check actual code lines, not comments or docstrings
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(term in mod for term in ["trap_generator", "test_harness", "tester_quarantine"]):
                violations.append(f"Builder imports from '{mod}' — firewall violation")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ("generate_t2_battery", "generate_t3_battery"):
                    violations.append(f"Builder calls '{node.func.id}' — firewall violation")
            # Check for open() calls to quarantine paths
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "quarantine" in arg.value or "trap_generator" in arg.value:
                            violations.append(f"Builder opens quarantine file — firewall violation")

    return violations


def verify_tester_isolation():
    """Verify the Tester script never modifies tools (Law 1)."""
    tester_path = FORGE / "tester.py"
    source = tester_path.read_text(encoding='utf-8')
    violations = []

    # AST check: Tester should not write to candidates/ directory
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for open() with 'w' mode on candidates paths
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "candidates" in arg.value:
                            violations.append(f"Tester opens candidates file for writing")

    return violations


def get_existing_tool_paths(tier):
    """Get paths of existing passing tools for diversity checks."""
    paths = []
    for f in VERDICTS.glob(f"t{tier}_*_verdict.json"):
        try:
            v = json.loads(f.read_text())
            if v.get("verdict") == "PASS":
                tool_file = CANDIDATES / f"{v['tool_id']}.py"
                if tool_file.exists():
                    paths.append(str(tool_file))
        except Exception:
            pass
    return paths


def run_null_baselines(tier):
    """Run null baselines via the Tester subprocess (Law 5)."""
    log(f"Running null baselines for T{tier}...")
    result = subprocess.run(
        [sys.executable, str(FORGE / "tester.py"), "--tier", str(tier), "--baselines"],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=str(ROOT),
    )
    log(f"  Tester stdout: {result.stdout.strip()}")
    if result.returncode != 0:
        log(f"  Tester stderr: {result.stderr.strip()}")
    return result.returncode == 0


def evaluate_candidate(tool_path, tier):
    """Evaluate a candidate tool via the Tester subprocess."""
    existing = get_existing_tool_paths(tier)
    cmd = [
        sys.executable, str(FORGE / "tester.py"),
        "--tool", str(tool_path),
        "--tier", str(tier),
    ]
    if existing:
        cmd.extend(["--existing"] + existing)

    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=str(ROOT),
    )
    log(f"  Tester stdout: {result.stdout.strip()}")
    if result.returncode != 0:
        log(f"  Tester stderr: {result.stderr.strip()}")

    # Read verdict
    tool_id = Path(tool_path).stem
    verdict_path = VERDICTS / f"{tool_id}_verdict.json"
    if verdict_path.exists():
        return json.loads(verdict_path.read_text())
    return None


def process_candidate(tool_path, tier):
    """Full pipeline for a single candidate: check laws, evaluate, report."""
    tool_id = Path(tool_path).stem
    log(f"\nProcessing candidate: {tool_id}")

    # Law 1: Verify isolation
    builder_violations = verify_builder_isolation()
    if builder_violations:
        log(f"  LAW 1 VIOLATION (Builder isolation): {builder_violations}")
        return {"verdict": "REJECTED_LAW1", "violations": builder_violations}

    # Law 2: Check banned patterns
    ban_violations = check_banned_patterns(str(tool_path))
    if ban_violations:
        log(f"  LAW 2 VIOLATION (banned patterns): {len(ban_violations)} violations")
        for v in ban_violations[:5]:
            log(f"    {v}")
        return {"verdict": "REJECTED_LAW2_BANNED", "violations": ban_violations}

    # Law 2: Check composition requirements
    comp_issues = check_composition_requirements(str(tool_path), tier)
    if comp_issues:
        log(f"  LAW 2 VIOLATION (composition): {comp_issues}")
        return {"verdict": "REJECTED_LAW2_COMPOSITION", "violations": comp_issues}

    # Evaluate via Tester subprocess (Laws 3, 4, 5 checked by Tester)
    log(f"  Passed law checks. Sending to Tester...")
    verdict = evaluate_candidate(tool_path, tier)

    if verdict:
        log(f"  Verdict: {verdict['verdict']} (score={verdict.get('overall_score', 0):.1%})")
        if verdict.get("promising_primitives"):
            log(f"  Promising primitives captured: {verdict['promising_primitives']}")
    else:
        log(f"  ERROR: No verdict returned from Tester")

    return verdict


def run_battery_difficulty_check(tier):
    """Post-generation 1 battery difficulty check (safeguard from architecture review)."""
    verdicts = []
    for f in VERDICTS.glob(f"t{tier}_*_verdict.json"):
        try:
            verdicts.append(json.loads(f.read_text()))
        except Exception:
            pass

    if not verdicts:
        log("  No verdicts to analyze for difficulty check")
        return

    # Check per-category pass rates
    cat_pass = {}
    cat_total = {}
    for v in verdicts:
        for cat, result in v.get("per_category", {}).items():
            cat_total[cat] = cat_total.get(cat, 0) + 1
            if result.get("pass"):
                cat_pass[cat] = cat_pass.get(cat, 0) + 1

    log(f"\n  Battery difficulty check (T{tier}):")
    all_pass = True
    none_pass = True
    for cat in sorted(cat_total.keys()):
        passed = cat_pass.get(cat, 0)
        total = cat_total[cat]
        rate = passed / total if total > 0 else 0
        log(f"    {cat:40s} {passed}/{total} = {rate:.0%}")
        if rate < 0.8:
            all_pass = False
        if passed > 0:
            none_pass = False

    if all_pass:
        log("  WARNING: All categories pass at >80% — battery may be too easy")
    if none_pass:
        log("  WARNING: No tools pass any category — battery may be too hard or descriptions too vague")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forge Runner — orchestrator")
    parser.add_argument("--tier", type=int, required=True, help="Tier (2 or 3)")
    parser.add_argument("--baselines", action="store_true", help="Run null baselines (Phase 1)")
    parser.add_argument("--evaluate", type=str, help="Evaluate a specific candidate tool path")
    parser.add_argument("--evaluate-all", action="store_true", help="Evaluate all candidates in forge/candidates/")
    parser.add_argument("--difficulty-check", action="store_true", help="Run battery difficulty check")
    args = parser.parse_args()

    log(f"\n{'='*60}")
    log(f"Forge Runner — T{args.tier} — {datetime.now().isoformat()}")
    log(f"{'='*60}")

    if args.baselines:
        run_null_baselines(args.tier)

    elif args.evaluate:
        process_candidate(Path(args.evaluate), args.tier)

    elif args.evaluate_all:
        prefix = f"t{args.tier}_"
        candidates = sorted(CANDIDATES.glob(f"{prefix}*.py"))
        candidates = [c for c in candidates if "_meta" not in c.stem and "_REASONING" not in c.stem]
        log(f"Found {len(candidates)} T{args.tier} candidates")
        for tool_path in candidates:
            process_candidate(tool_path, args.tier)
        run_battery_difficulty_check(args.tier)

    elif args.difficulty_check:
        run_battery_difficulty_check(args.tier)

    else:
        log("Use --baselines, --evaluate PATH, --evaluate-all, or --difficulty-check")
