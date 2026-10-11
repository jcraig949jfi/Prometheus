"""The executable domain for the negative-space evaluation (frozen in pan/tests/negspace_prereg.json).

A MECHANISM is Python source defining `class Mechanism` with `__init__(self, world)` and `step(self, x) -> int`.
`world` is a dict owned by the runner: a mechanism may store history in itself or in the world (environmental
storage). The CONTRACT is delay recall: y_t = x_{t-DELAY} for t >= DELAY, else 0.

The INTERVENTION SUITE is a frozen list of input streams over the alphabet 0..9. The CONTRACT is judged on the short
streams without intervention (contract_streams); the intervention streams -- three WORLD WIPES (the runner clears
`world` before step WIPE_AT) and one 200-step stream -- are outside the contract and reveal how a mechanism
satisfies it (internal vs environmental storage; a horizon cap). Mechanisms run in a separate `python -I` subprocess with a step budget and a timeout; the runner records
outputs and the line numbers of the mechanism source that executed (coverage), so an evaluator can tell "no input
distinguished them" from "the inputs never exercised the code that would".
"""
import json
import random
import subprocess
import sys
import textwrap

DELAY = 3
ALPHABET = 10
WIPE_AT = 12
TIMEOUT_S = 20


def contract_output(stream):
    return [stream[t - DELAY] if t >= DELAY else 0 for t in range(len(stream))]


def suite(seed=20261011):
    """[(stream_id, stream, wipe_at or None)] -- frozen by the prereg (seed and composition)."""
    rng = random.Random(seed)
    out = []
    for i in range(10):
        out.append(("rand{:02d}".format(i), [rng.randrange(ALPHABET) for _ in range(24)], None))
    for v in (0, 5, 9):
        out.append(("const{}".format(v), [v] * 24, None))
    for p in (2, 3):
        for j in range(2):
            base = [rng.randrange(ALPHABET) for _ in range(p)]
            out.append(("per{}_{}".format(p, j), (base * 24)[:24], None))
    for k in (0, 7, 15):
        s = [0] * 24
        s[k] = 1
        out.append(("imp{:02d}".format(k), s, None))
    for i in range(3):
        out.append(("wipe{}".format(i), [rng.randrange(ALPHABET) for _ in range(24)], WIPE_AT))
    out.append(("long200", [rng.randrange(ALPHABET) for _ in range(200)], None))
    return out


RUNNER = textwrap.dedent('''
    import json, sys
    src = sys.stdin.readline()
    streams = json.loads(sys.stdin.readline())
    lines = set()
    def tracer(frame, event, arg):
        if frame.f_code.co_filename == "<mechanism>":
            if event == "line":
                lines.add(frame.f_lineno)
            return tracer
        return None
    ns = {"__builtins__": __builtins__}
    try:
        exec(compile(json.loads(src), "<mechanism>", "exec"), ns)
    except Exception as e:
        print(json.dumps({"error": "compile: " + type(e).__name__ + ": " + str(e)[:200]})); sys.exit(0)
    Mech = ns.get("Mechanism")
    if Mech is None:
        print(json.dumps({"error": "no class Mechanism"})); sys.exit(0)
    results = {}
    sys.settrace(tracer)
    try:
        for sid, stream, wipe in streams:
            world = {}
            m = Mech(world)
            ys = []
            for t, x in enumerate(stream):
                if wipe is not None and t == wipe:
                    world.clear()
                y = m.step(x)
                ys.append(int(y) if isinstance(y, (int, bool)) else None)
            results[sid] = ys
    except Exception as e:
        sys.settrace(None)
        print(json.dumps({"error": "run: " + type(e).__name__ + ": " + str(e)[:200]})); sys.exit(0)
    sys.settrace(None)
    print(json.dumps({"outputs": results, "lines": sorted(lines)}))
''')


def run(src, streams=None, timeout=TIMEOUT_S):
    """{'outputs': {stream_id: [y...]}, 'lines': [executed line numbers]} or {'error': ...}."""
    streams = streams if streams is not None else suite()
    payload = json.dumps(src) + "\n" + json.dumps(streams) + "\n"
    try:
        p = subprocess.run([sys.executable, "-I", "-c", RUNNER], input=payload, capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"error": "no output: " + (p.stderr or "")[-200:]}


def executable_lines(src):
    """Line numbers of statements inside methods of class Mechanism (the lines a complete suite should execute)."""
    import ast
    tree = ast.parse(src)
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Mechanism":
            for fn in node.body:
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for st in ast.walk(fn):
                        if isinstance(st, ast.stmt) and st is not fn:
                            out.add(st.lineno)
    return out


def contract_streams():
    """The TASK: short streams without interventions (rand, const, per, imp). The intervention streams (wipe*,
    long200) are not part of the contract; they reveal HOW a contract-satisfying mechanism works."""
    return [(sid, s, w) for sid, s, w in suite() if w is None and len(s) <= 24]


def satisfies_contract(result):
    """True when the outputs on every contract stream equal the delay-recall contract."""
    if "outputs" not in result:
        return False
    return all(result["outputs"].get(sid) == contract_output(s) for sid, s, _ in contract_streams())


ALLOWED_IMPORTS = {"collections", "itertools", "math", "functools"}
FORBIDDEN_NAMES = {"open", "exec", "eval", "compile", "__import__", "globals", "locals", "vars", "input", "breakpoint",
                   "getattr", "setattr", "delattr", "memoryview", "exit", "quit"}


def static_guard(src):
    """None if the source may run, else the reason it may not: only small pure-Python mechanisms are executed
    (imports limited to ALLOWED_IMPORTS; no file, process, reflection or dunder access). Applied to every mechanism,
    including calibration sources, before `run`."""
    import ast
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return "syntax: {}".format(e.msg)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            bad = [a.name for a in node.names if a.name.split(".")[0] not in ALLOWED_IMPORTS]
            if bad:
                return "import not allowed: {}".format(bad)
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in ALLOWED_IMPORTS:
                return "import not allowed: {}".format(node.module)
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            return "name not allowed: {}".format(node.id)
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return "dunder attribute not allowed: {}".format(node.attr)
    if not any(isinstance(n, ast.ClassDef) and n.name == "Mechanism" for n in tree.body):
        return "no top-level class Mechanism"
    return None
