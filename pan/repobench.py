"""PAN-34: in-house code benchmark. Can a local model rewrite one of the program's OWN
functions so that the program's OWN tests still pass? Protocol frozen in
pan/tests/repobench_prereg.json (1e5276818, amendment A1) before mining and before any
model ran. Uncontaminated by construction: the repository's first commit is 2026-03-22.

python -m pan repobench mine         sandbox tree + task set (CPU; take a Fabric CPU lease)
python -m pan repobench controls     POSITIVE / CHEAT / NEGATIVE on the frozen task set
python -m pan repobench run MODEL [--budget N]

Every verdict is the program's own test file, executed; never a model's opinion.
"""
import ast
import datetime as dt
import hashlib
import json
import os
import queue
import random
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import PKG, REPO, host, lake

PREREG = PKG / "tests" / "repobench_prereg.json"
DATA_EXT = {".json", ".jsonl", ".csv", ".txt", ".toml", ".ini", ".cfg", ".yaml", ".yml", ".npz", ""}
TEST_RE = re.compile(r"(^|/)test_[^/]*\.py$")
# CLAUDE.md: never read key / secret / credential / .env files -- not even into a sandbox
CRED_RE = re.compile(r"secret|credential|\.env($|/)|(^|/)[^/]*key[^/]*$", re.I)
MOD_TOKENS = ("psycopg2", "psycopg", "requests", "redis", "httpx", "aiohttp", "urllib.request", "socket", "sqlalchemy",
              "duckdb", "boto3", "openai", "anthropic", "ollama", "transformers", "torch", "tensorflow", "jax",
              "subprocess", "multiprocessing", "keys")
SUBSTR_TOKENS = ("EW_DB_HOST", "192.168.", "D:/", "D:\\", "C:/", "C:\\", "/d/", "Prometheus-data")
SUFFIX = ("\n\nWrite the complete function `{name}` (signature included) so that the module works as its author "
          "intended. Reply with ONLY one Python code block containing the function. No explanation, no tests.")
CTX_CHARS = 12000
NUM_CTX = 8192


def root():
    return lake() / "repobench"


def unit_of(path):
    parts = path.split("/")
    return "/".join(parts[:2]) if parts[0] == "roles" and len(parts) > 2 else parts[0]


def violation(src):
    """The A1 exclusion rule: the first offending token, or None."""
    for t in SUBSTR_TOKENS:
        if t in src:
            return t
    if re.search(r"\bget_key\b", src):
        return "get_key"
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return "syntax"
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            names = [node.module] + [node.module + "." + a.name for a in node.names]
        for n in names:
            for t in MOD_TOKENS:
                if n == t or n.startswith(t + "."):
                    return "import " + t
    return None


def imported_modules(test_path, src, files):
    """Repository module files a test imports directly (absolute imports resolved against the
    sandbox root and every ancestor directory of the test, as pytest's prepend mode and the
    tests' own sys.path edits allow; relative imports against the test's package)."""
    tree = ast.parse(src)
    tdir = test_path.split("/")[:-1]
    bases = [tdir[:i] for i in range(len(tdir), -1, -1)]
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update((b, a.name) for a in node.names for b in map(tuple, bases))
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = tdir[:len(tdir) - (node.level - 1)] if node.level > 1 else tdir
                stem = ([node.module] if node.module else [])
                mods.add((tuple(base), ".".join(stem)) if stem else (tuple(base), ""))
                mods.update((tuple(base), ".".join(stem + [a.name])) for a in node.names)
            elif node.module:
                for b in map(tuple, bases):
                    mods.add((b, node.module))
                    mods.update((b, node.module + "." + a.name) for a in node.names)
    out = set()
    for base, m in mods:
        if not m:
            continue
        p = "/".join(list(base) + m.split("."))
        for cand in (p + ".py", p + "/__init__.py"):
            if cand in files and not TEST_RE.search(cand) and not cand.endswith("conftest.py"):
                out.add(cand)
    return out


def functions(src):
    """Top-level, non-async, non-dunder defs with 3..60 body lines after the docstring:
    (name, start (decorators included), end, body_start, indent) -- 1-based lines."""
    out = []
    for node in ast.parse(src).body:
        if not isinstance(node, ast.FunctionDef) or (node.name.startswith("__") and node.name.endswith("__")):
            continue
        body = node.body
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            body = body[1:]
        if not body:
            continue
        b0 = body[0].lineno
        if b0 <= node.lineno:                     # body on the def line
            continue
        n = node.end_lineno - b0 + 1
        if 3 <= n <= 60:
            start = min([d.lineno for d in node.decorator_list] + [node.lineno])
            out.append((node.name, start, node.end_lineno, b0, body[0].col_offset))
    return out


def replace_body(text, t, line):
    """The module with lines body_start..end of task t replaced by one indented `line`."""
    lines = text.splitlines(keepends=True)
    return "".join(lines[:t["body_start"] - 1]) + " " * t["indent"] + line + "\n" + "".join(lines[t["end"]:])


def function_source(text, t):
    return "".join(text.splitlines(keepends=True)[t["start"] - 1:t["end"]])


def prompt_for(text, t):
    masked = replace_body(text, t, "...")
    if len(masked) > CTX_CHARS:
        lines = masked.splitlines(keepends=True)
        tree_head = []
        for ln in lines:                          # import header: up to the first top-level def/class
            if re.match(r"(def|class|async def|@)\b", ln):
                break
            tree_head.append(ln)
        head = "".join(tree_head)[:3000]
        lo = hi = t["start"] - 1                  # the masked function spans start..start+(body_start-start)
        hi = t["body_start"]                      # exclusive end, after the "..." line
        budget = CTX_CHARS - len(head) - 40
        cur = sum(len(x) for x in lines[lo:hi])
        while True:
            grew = False
            if lo > len(tree_head) and cur + len(lines[lo - 1]) <= budget:
                lo -= 1
                cur += len(lines[lo])
                grew = True
            if hi < len(lines) and cur + len(lines[hi]) <= budget:
                cur += len(lines[hi])
                hi += 1
                grew = True
            if not grew:
                break
        masked = head + "\n# ... (module truncated) ...\n\n" + "".join(lines[lo:hi])
    return "```python\n{}```".format(masked if masked.endswith("\n") else masked + "\n") + SUFFIX.format(name=t["name"])


def extract(response, name):
    """(code, error): the last ```python block, dedented; it must parse and define `name` at top level."""
    m = re.findall(r"```(?:python|py)?\s*\n(.*?)```", response or "", re.S)
    code = textwrap.dedent(m[-1] if m else (response or ""))
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return None, "syntax error in block: {}".format(e.msg)
    if not any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name for n in tree.body):
        return None, "block does not define {} at top level".format(name)
    return code, None


def run_test(sandbox, test_rel, timeout=120):
    """(passed, detail): the test file under pytest in a scrubbed environment."""
    tmp = root() / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(tmp)) as d:
        sysroot = os.environ.get("SYSTEMROOT", r"C:\Windows")
        env = dict(SYSTEMROOT=sysroot, PATH=os.pathsep.join([os.path.dirname(sys.executable), sysroot + r"\System32"]),
                   PYTHONPATH=str(sandbox), HOME=d, USERPROFILE=d, TEMP=d, TMP=d, PYTHONHASHSEED="0",
                   PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", MPLBACKEND="Agg")
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                                str(Path(sandbox) / test_rel)], cwd=d, env=env, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "timeout"
    tail = [ln for ln in (r.stdout or "").splitlines() if ln.strip()][-1:] or ["rc={}".format(r.returncode)]
    return r.returncode == 0, tail[0][:200]


def swapped(sandbox, module, new_text):
    """Write new_text over a module in this sandbox; returns restore() (callers use try/finally)."""
    p = Path(sandbox) / module
    orig = p.read_bytes()
    p.write_bytes(new_text.encode("utf-8"))
    return lambda: p.write_bytes(orig)


def spliced(sandbox, t, code):
    """`code` written over task t's lines (decorators included) in this sandbox; returns restore()."""
    lines = (Path(sandbox) / t["module"]).read_text(encoding="utf-8").splitlines(keepends=True)
    return swapped(sandbox, t["module"],
                   "".join(lines[:t["start"] - 1]) + code.rstrip("\n") + "\n" + "".join(lines[t["end"]:]))


# ----------------------------------------------------------------------------------------------- mining

def materialize(dest, paths_sizes, sha_of, out=print):
    from .chunker import BlobReader
    br = BlobReader()
    n = b = 0
    try:
        for path, size in paths_sizes:
            data = br.read(sha_of[path])
            if data is None:
                continue
            f = dest / path
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
            n += 1
            b += len(data)
    finally:
        br.close()
    out("  materialized {} files, {:.1f} MB -> {}".format(n, b / 1e6, dest))
    return n


def mine(workers=4, target=160, out=print):
    from . import db
    pr = json.loads(PREREG.read_text(encoding="utf-8"))
    assert any(a["id"] == "A1" for a in pr.get("amendments", [])), "prereg amendment A1 missing"
    t0 = time.time()
    with db.cursor() as cur:
        cur.execute("select repo_sha from pan.artifact where source='git' limit 1")
        tree_sha = cur.fetchone()[0]
        cur.execute("""select path, blob_sha, size_bytes, ext from pan.artifact where source='git'""")
        rows = cur.fetchall()
    tests = sorted(p for p, _, _, _ in rows if TEST_RE.search(p))
    units = {unit_of(p) for p in tests}
    keep = [(p, s) for p, _, s, e in rows
            if (unit_of(p) in units or "/" not in p) and not CRED_RE.search(p)
            and ((e or "") == ".py" or ((e or "") in DATA_EXT and s <= 131072))]
    sha_of = {p: b for p, b, _, _ in rows}
    base = root() / "tree_{}".format(tree_sha[:12])
    funnel = dict(tree_sha=tree_sha, test_files=len(tests), units=len(units))
    if not (base / ".complete").exists():
        if base.exists():
            shutil.rmtree(base)
        materialize(base, keep, sha_of, out)
        (base / ".complete").write_text(tree_sha)
    files = {p for p, _ in keep}
    # 1. static exclusion (A1 semantics) on the test file and its directly imported modules
    cand, dropped = [], {}
    for tp in tests:
        if tp not in files:
            dropped["not materialized"] = dropped.get("not materialized", 0) + 1
            continue
        src = (base / tp).read_text(encoding="utf-8", errors="replace")
        v = violation(src)
        mods = set()
        if not v:
            try:
                mods = imported_modules(tp, src, files)
            except SyntaxError:
                v = "syntax"
        for m in sorted(mods):
            if v:
                break
            mv = violation((base / m).read_text(encoding="utf-8", errors="replace"))
            v = mv and "module " + mv
        if v:
            key = v.split()[0] if v.startswith("import") else v
            dropped[key] = dropped.get(key, 0) + 1
        elif mods:
            cand.append((tp, sorted(mods)))
        else:
            dropped["imports no repository module"] = dropped.get("imports no repository module", 0) + 1
    funnel.update(static_dropped=dropped, static_kept=len(cand))
    out("  static: kept {} of {} test files".format(len(cand), len(tests)))
    # 2. baseline: the test file passes in the sandbox
    with ThreadPoolExecutor(workers) as ex:
        base_ok = list(ex.map(lambda c: run_test(base, c[0]), cand))
    passing = [c for c, (ok, _) in zip(cand, base_ok) if ok]
    funnel.update(baseline_pass=len(passing), baseline_fail=len(cand) - len(passing))
    out("  baseline: {} of {} pass ({:.0f}s)".format(len(passing), len(cand), time.time() - t0))
    # 3. candidate functions, shuffled with the preregistered seed, capped
    cands = []
    for tp, mods in passing:
        for m in mods:
            text = (base / m).read_text(encoding="utf-8")
            try:
                fns = functions(text)
            except SyntaxError:
                continue
            for name, start, end, b0, ind in fns:     # referenced or not: the stub gate decides
                cands.append(dict(test=tp, module=m, unit=unit_of(m), name=name, start=start, end=end,
                                  body_start=b0, indent=ind))
    random.Random(34).shuffle(cands)
    funnel["candidates"] = len(cands)
    workers_dirs = sandboxes(base, workers, out)
    pool = queue.Queue()
    for w in workers_dirs:
        pool.put(w)
    per_module, per_test, per_unit, tasks, gate_fail = {}, {}, {}, [], dict(a=0, b=0, capped=0)
    seen_fn = set()

    def gate(t):
        w = pool.get()
        try:
            ok_a, det_a = run_test(w, t["test"])
            if not ok_a:
                return t, "a", det_a
            text = (Path(w) / t["module"]).read_text(encoding="utf-8")
            restore = swapped(w, t["module"], replace_body(text, t, "raise NotImplementedError('PAN-34 stub')"))
            try:
                ok_b, det_b = run_test(w, t["test"])
            finally:
                restore()
            return t, ("b" if ok_b else None), det_b
        finally:
            pool.put(w)

    i = 0
    with ThreadPoolExecutor(workers) as ex:
        while len(tasks) < target and i < len(cands):
            batch = []
            while len(batch) < workers * 2 and i < len(cands):
                t = cands[i]
                i += 1
                key = (t["module"], t["name"])
                if key in seen_fn or per_module.get(t["module"], 0) >= 2 or per_test.get(t["test"], 0) >= 3 \
                        or per_unit.get(t["unit"], 0) >= 12:
                    gate_fail["capped"] += 1
                    continue
                seen_fn.add(key)
                batch.append(t)
            for t, failed, det in ex.map(gate, batch):
                if failed:
                    gate_fail[failed] += 1
                    continue
                if len(tasks) >= target or per_module.get(t["module"], 0) >= 2 or per_test.get(t["test"], 0) >= 3 \
                        or per_unit.get(t["unit"], 0) >= 12:
                    gate_fail["capped"] += 1
                    continue
                per_module[t["module"]] = per_module.get(t["module"], 0) + 1
                per_test[t["test"]] = per_test.get(t["test"], 0) + 1
                per_unit[t["unit"]] = per_unit.get(t["unit"], 0) + 1
                tasks.append(t)
            out("  gated {} candidates -> {} tasks ({:.0f}s)".format(i, len(tasks), time.time() - t0))
    funnel.update(candidates_examined=i, gate_a_flaky=gate_fail["a"], gate_b_blind=gate_fail["b"],
                  capped=gate_fail["capped"], tasks=len(tasks), seconds=round(time.time() - t0, 1))
    for k, t in enumerate(tasks, 1):
        text = (base / t["module"]).read_text(encoding="utf-8")
        t["task_id"] = "RB-{:03d}".format(k)
        t["fn_sha256"] = hashlib.sha256(function_source(text, t).encode("utf-8")).hexdigest()
        t["module_blob"] = sha_of[t["module"]]
        t["test_blob"] = sha_of[t["test"]]
    manifest = dict(prereg=str(PREREG.relative_to(REPO)).replace("\\", "/"), tree_sha=tree_sha,
                    sandbox=str(base), created=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                    funnel=funnel, tasks=tasks)
    d = REPO / "roles" / "Pan" / "reports" / "repobench"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "TASKS_{}.json".format(tree_sha[:12])
    p.write_text(json.dumps(manifest, indent=1), encoding="utf-8", newline="\n")
    out(json.dumps(funnel))
    out("wrote {}".format(p))
    return manifest


def sandboxes(base, n, out=print):
    """n worker copies of the base tree (each verdict edits its own copy and restores it)."""
    dirs = []
    for k in range(n):
        w = Path(str(base) + "_w{}".format(k))
        if not (w / ".complete").exists():
            if w.exists():
                shutil.rmtree(w)
            shutil.copytree(base, w)
        dirs.append(w)
    out("  {} worker sandboxes ready".format(n))
    return dirs


# ----------------------------------------------------------------------------------------- evaluation

def load(verify=True, workers=4, out=print):
    """The committed manifest, with every task's module and test re-fingerprinted in every sandbox
    (a sandbox left edited by a killed run is rebuilt, never trusted)."""
    ps = sorted((REPO / "roles" / "Pan" / "reports" / "repobench").glob("TASKS_*.json"))
    man = json.loads(ps[-1].read_text(encoding="utf-8"))
    base = Path(man["sandbox"])
    dirs = sandboxes(base, workers, out)
    if verify:
        for w in [base] + dirs:
            for t in man["tasks"]:
                text = (w / t["module"]).read_text(encoding="utf-8")
                if hashlib.sha256(function_source(text, t).encode("utf-8")).hexdigest() != t["fn_sha256"]:
                    if w == base:
                        raise SystemExit("base sandbox does not match the manifest: {}".format(t["task_id"]))
                    out("  {} drifted in {}; rebuilding".format(t["task_id"], w))
                    shutil.rmtree(w)
                    shutil.copytree(base, w)
                    break
    return man, base, dirs


def verdicts(dirs, jobs):
    """jobs: [(task, code or None, err)] -> [(ok, detail)], each run in a free worker sandbox."""
    pool = queue.Queue()
    for w in dirs:
        pool.put(w)

    def one(job):
        t, code, err = job
        if code is None:
            return False, err
        w = pool.get()
        try:
            restore = spliced(w, t, code)
            try:
                return run_test(w, t["test"])
            finally:
                restore()
        finally:
            pool.put(w)

    with ThreadPoolExecutor(len(dirs)) as ex:
        return list(ex.map(one, jobs))


def controls(workers=4, out=print):
    man, base, dirs = load(workers=workers, out=out)
    tasks = man["tasks"]
    src = {t["task_id"]: function_source((base / t["module"]).read_text(encoding="utf-8"), t) for t in tasks}

    def wrapped(code):
        return "```python\n{}```".format(code)

    res = {}
    t0 = time.time()
    jobs = [(t,) + extract(wrapped(src[t["task_id"]]), t["name"]) for t in tasks]
    pos = verdicts(dirs, jobs)
    res["POSITIVE_original"] = dict(passed=sum(ok for ok, _ in pos), of=len(tasks),
                                    failing=[t["task_id"] for t, (ok, _) in zip(tasks, pos) if not ok])
    jobs = []
    for t in tasks:
        text = (base / t["module"]).read_text(encoding="utf-8")
        fn = function_source(replace_body(text, t, "pass"), dict(t, end=t["body_start"]))
        jobs.append((t,) + extract(wrapped(textwrap.dedent(fn)), t["name"]))
    ch = verdicts(dirs, jobs)
    res["CHEAT_pass_body"] = dict(passed=sum(ok for ok, _ in ch), of=len(tasks),
                                  passing=[t["task_id"] for t, (ok, _) in zip(tasks, ch) if ok])
    jobs = []
    for k, t in enumerate(tasks):
        other = next(o for o in tasks[k + 1:] + tasks[:k] if o["module"] != t["module"])
        code = re.sub(r"\bdef\s+{}\s*\(".format(re.escape(other["name"])), "def {}(".format(t["name"]),
                      textwrap.dedent(src[other["task_id"]]), count=1)
        jobs.append((t,) + extract(wrapped(code), t["name"]))
    ng = verdicts(dirs, jobs)
    res["NEGATIVE_other_function"] = dict(passed=sum(ok for ok, _ in ng), of=len(tasks),
                                          passing=[t["task_id"] for t, (ok, _) in zip(tasks, ng) if ok])
    n = len(tasks)
    res["verdict"] = dict(positive_all=res["POSITIVE_original"]["passed"] == n,
                          cheat_le_10pct=res["CHEAT_pass_body"]["passed"] <= 0.10 * n,
                          negative_le_20pct=res["NEGATIVE_other_function"]["passed"] <= 0.20 * n)
    res["seconds"] = round(time.time() - t0, 1)
    p = REPO / "roles" / "Pan" / "reports" / "repobench" / "CONTROLS_{}.json".format(
        dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    p.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    for k in ("POSITIVE_original", "CHEAT_pass_body", "NEGATIVE_other_function"):
        out("{:<26} {}/{}".format(k, res[k]["passed"], res[k]["of"]))
    out(json.dumps(res["verdict"]))
    return res


def excluded():
    """Task ids the prereg's amendments remove from the PRIMARY set (A2: pass-body passers)."""
    pr = json.loads(PREREG.read_text(encoding="utf-8"))
    return {x for a in pr.get("amendments", []) for x in a.get("excluded_tasks", [])}


def first_param(fn_src):
    a = ast.parse(textwrap.dedent(fn_src)).body[0].args
    names = [x.arg for x in a.posonlyargs + a.args] + ([a.vararg.arg] if a.vararg else []) + \
        [x.arg for x in a.kwonlyargs] + ([a.kwarg.arg] if a.kwarg else [])
    return names[0] if names else None


def controls_cheat2(workers=4, out=print):
    """A2's CHEAT2 on the primary set: the body returns the first parameter unchanged (None if none)."""
    man, base, dirs = load(workers=workers, out=out)
    ex = excluded()
    tasks = [t for t in man["tasks"] if t["task_id"] not in ex]
    jobs = []
    for t in tasks:
        text = (base / t["module"]).read_text(encoding="utf-8")
        p = first_param(function_source(text, t))
        fn = function_source(replace_body(text, t, "return {}".format(p or "None")), dict(t, end=t["body_start"]))
        jobs.append((t,) + extract("```python\n{}```".format(textwrap.dedent(fn)), t["name"]))
    t0 = time.time()
    vs = verdicts(dirs, jobs)
    k = sum(ok for ok, _ in vs)
    res = dict(CHEAT2_return_first_param=dict(passed=k, of=len(tasks),
                                              passing=[t["task_id"] for t, (ok, _) in zip(tasks, vs) if ok]),
               verdict=dict(cheat2_le_10pct=k <= 0.10 * len(tasks)), seconds=round(time.time() - t0, 1),
               primary_n=len(tasks), excluded=sorted(ex))
    p = REPO / "roles" / "Pan" / "reports" / "repobench" / "CONTROLS_CHEAT2_{}.json".format(
        dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    p.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    out("CHEAT2_return_first_param  {}/{}".format(k, len(tasks)))
    out(json.dumps(res["verdict"]))
    return res


def run(model, think=False, budget=1024, workers=4, out=print):
    from psycopg2.extras import execute_values
    from . import db
    from .codebench import wilson
    from .modelbench import HF_MAP, generate, ollama_version, strip_thinking
    man, base, dirs = load(workers=workers, out=out)
    tasks = man["tasks"]
    cfg = "@{}{}".format("think" if think else "nothink", budget)
    run_id = "repobench-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    with db.cursor() as cur:
        cur.execute("insert into pan.run (run_id, kind, host, params) values (%s,'repobench',%s,%s)",
                    (run_id, host(), json.dumps(dict(model=model, think=think, budget=budget, n=len(tasks),
                                                     num_ctx=NUM_CTX, manifest_tree=man["tree_sha"],
                                                     ollama=ollama_version()))))
    t0 = time.time()
    gens = []
    for i, t in enumerate(tasks):
        text = (base / t["module"]).read_text(encoding="utf-8")
        s = time.time()
        try:
            g = generate(model, prompt_for(text, t), think=think, budget=budget, num_ctx=NUM_CTX)
            resp = strip_thinking(g.get("response", ""))
            ev, evd = g.get("eval_count") or 0, (g.get("eval_duration") or 0) / 1e9
            gens.append((t, resp, ev, ev / evd if evd else None, time.time() - s, None))
        except Exception as e:
            gens.append((t, "", 0, None, time.time() - s, "{}: {}".format(type(e).__name__, e)[:200]))
        if (i + 1) % 40 == 0:
            out("  {} {}/{} generated, {:.0f}s".format(model, i + 1, len(tasks), time.time() - t0))
    jobs = [(g[0],) + ((None, g[5]) if g[5] else extract(g[1], g[0]["name"])) for g in gens]
    vs = verdicts(dirs, jobs)
    rows = []
    for (t, resp, ev, tps, lat, err), (ok, detail) in zip(gens, vs):
        if ev >= budget:
            detail = "TRUNCATED at {} tokens; {}".format(ev, detail)
        rows.append((run_id, "ollama:" + model + cfg, HF_MAP.get(model), t["task_id"], ok, detail, lat, ev, tps,
                     resp[:12000]))
    with db.cursor() as cur:
        execute_values(cur, """insert into pan.code_bench (run_id, model, hf_repo, task_id, ok, detail, latency_s,
                               eval_tokens, tok_per_s, response) values %s""", rows)
        ex = excluded()
        prim = [r for r in rows if r[3] not in ex]          # A2: primary = discriminating tasks
        k = sum(1 for r in prim if r[4])
        k_all = sum(1 for r in rows if r[4])
        tps = sorted(r[8] for r in rows if r[8])
        summ = dict(model=model, config=cfg, passed=k, of=len(prim), pass_at_1=round(k / len(prim), 3),
                    wilson95=wilson(k, len(prim)),
                    secondary_all=dict(passed=k_all, of=len(rows), pass_at_1=round(k_all / len(rows), 3)),
                    truncated=sum(1 for r in prim if (r[5] or "").startswith("TRUNCATED")),
                    median_tok_s=round(tps[len(tps) // 2], 1) if tps else None, seconds=round(time.time() - t0, 1))
        cur.execute("update pan.run set finished_at=now(), status='OK', counts=%s where run_id=%s",
                    (json.dumps(summ), run_id))
    subprocess.run(["ollama", "stop", model], capture_output=True, timeout=60)
    out(json.dumps(summ))
    return summ


def shape(ok, detail, response):
    """One failure-shape label per row (reading order: empty, no definition, syntax, timeout, test)."""
    if ok:
        return "pass"
    d = re.sub(r"^TRUNCATED at \d+ tokens; ", "", detail or "")
    if not (response or "").strip():
        return "empty response"
    if d.startswith("block does not define"):
        return "no definition"
    if d.startswith("syntax error"):
        return "syntax error"
    if d == "timeout":
        return "test timeout"
    return "test failed"


def mcnemar_p(b, c):
    """Exact two-sided McNemar (binomial on the discordant pairs)."""
    from math import comb
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def analyze(out=print):
    """Latest run per configuration -> failure shapes, the A2 primary Wilson table, the preregistered
    secondary (exact McNemar, Holm over all pairs measured so far) and agreement across configurations.
    Reads stored rows only; never changes a verdict."""
    from . import db
    from .codebench import wilson
    ex = excluded()
    with db.cursor() as cur:
        cur.execute("""select distinct on (b.model) b.model, r.run_id from pan.run r join pan.code_bench b using (run_id)
                       where r.kind = 'repobench' and r.status = 'OK' order by b.model, r.started_at desc""")
        runs = cur.fetchall()
        rows = {}
        for model, rid in runs:
            cur.execute("select task_id, ok, detail, response from pan.code_bench where run_id = %s", (rid,))
            rows[model] = {t: (ok, shape(ok, d, resp)) for t, ok, d, resp in cur.fetchall()}
    res = dict(runs={m: r for m, r in runs}, configs={}, pairs=[], agreement={})
    prim = sorted({t for r in rows.values() for t in r if t not in ex})
    for m, r in rows.items():
        k = sum(r[t][0] for t in prim)
        shapes = {}
        for t in prim:
            shapes[r[t][1]] = shapes.get(r[t][1], 0) + 1
        res["configs"][m] = dict(passed=k, of=len(prim), pass_at_1=round(k / len(prim), 3), wilson95=wilson(k, len(prim)),
                                 shapes=shapes)
    ms = sorted(rows)
    pairs = []
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            a, b = ms[i], ms[j]
            only_a = sum(1 for t in prim if rows[a][t][0] and not rows[b][t][0])
            only_b = sum(1 for t in prim if rows[b][t][0] and not rows[a][t][0])
            wa, wb = res["configs"][a]["wilson95"], res["configs"][b]["wilson95"]
            pairs.append(dict(a=a, b=b, only_a=only_a, only_b=only_b, p=mcnemar_p(only_a, only_b),
                              wilson_separable=wa[0] > wb[1] or wb[0] > wa[1]))
    m_tests = 10                                          # Holm over the 10 preregistered pairs, even before all exist
    for rank, pr in enumerate(sorted(pairs, key=lambda x: x["p"])):
        pr["holm_threshold"] = round(0.05 / (m_tests - rank), 5)
    stop = False
    for pr in sorted(pairs, key=lambda x: x["p"]):
        pr["holm_reject"] = (not stop) and pr["p"] <= pr["holm_threshold"]
        stop = stop or not pr["holm_reject"]
    res["pairs"] = pairs
    solved = {t: sum(rows[m][t][0] for m in ms) for t in prim}
    res["agreement"] = dict(solved_by_none=sum(1 for v in solved.values() if v == 0),
                            solved_by_all=sum(1 for v in solved.values() if v == len(ms)), configs=len(ms))
    p = REPO / "roles" / "Pan" / "reports" / "repobench" / "ANALYSIS_{}.json".format(
        dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    p.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    for m in ms:
        c = res["configs"][m]
        out("{:<34} {:>3}/{} {:.3f} [{:.3f}, {:.3f}]  {}".format(m, c["passed"], c["of"], c["pass_at_1"], *c["wilson95"],
                                                               ", ".join("{} {}".format(k, v) for k, v in
                                                                         sorted(c["shapes"].items(), key=lambda kv: -kv[1]))))
    for pr in pairs:
        out("  {} vs {}: only {} / only {}  McNemar p={:.4f} Holm {} ; Wilson {}".format(
            pr["a"].split(":", 1)[1], pr["b"].split(":", 1)[1], pr["only_a"], pr["only_b"], pr["p"],
            "REJECT" if pr["holm_reject"] else "keep", "separable" if pr["wilson_separable"] else "overlap"))
    out(json.dumps(res["agreement"]))
    out("wrote {}".format(p))
    return res
