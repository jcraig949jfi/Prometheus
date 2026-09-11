"""TALOS-24: does the recorded natural-language spec correspond to the
implementation or test behaviour? Per family, never as one population.

PRE-REGISTERED before the first run (operator directive 2026-09-11,
roles/Talos/prompts/2026-09-11_talos04_24_directive/). No LLM adjudicates:
every judgement below is a deterministic predicate over the docstring text,
the snippet's AST, the current tree, and pytest's own result lines.

SAMPLE. Seed 20260911; per family min(100, rows) rows drawn without
replacement from roles/Talos/ledgers/corpus_shards_2026-09-11/ using the
family cut declared in characterize_corpus.py (first prefix wins).

STAGE A -- LOCATE the row in the current tree (source_path, function_name):
  LOCATED_SAME      a def with that name exists in that file and its
                    whitespace-normalised source equals the snippet
  LOCATED_CHANGED   a def with that name exists but its text differs
  NOT_FOUND         file absent, unparseable, or no def with that name

STAGE B -- SPEC CLAIMS extracted from the docstring by a fixed grammar,
each checked against the snippet's AST:
  RAISES(X)     X = any token matching [A-Z]\\w*(Error|Exception|Warning)
                in the docstring. SATISFIED if X appears in a `raise` or in
                pytest.raises(...)/raises(...) in the body; UNSATISFIED
                otherwise.
  RETURNS(K)    the docstring says "return(s) [a|an|the] K" with K in
                {None, True, False, bool, int, float, str, dict, list,
                tuple, Path/path, set}. SATISFIED if a return statement's
                literal kind or the return annotation matches K;
                UNSATISFIED if there are return statements whose kinds are
                all determinable and none matches, or if K != None and the
                body has no value-returning statement; INDETERMINATE if
                every return is a Name/Call/Attribute whose kind the AST
                cannot give.
  MENTIONS(id)  an identifier in the docstring (backticked, or containing
                an underscore, or CamelCase of length >= 4) that is not
                the function's own name. SATISFIED if it appears in the
                code part of the snippet (docstring removed) or is a
                parameter; UNSATISFIED otherwise. Stop-words are the
                exception/kind tokens already used above.
Row outcome from its claims:
  UNMEASURABLE_NO_SPEC              docstring empty
  UNMEASURABLE_NO_CHECKABLE_CLAIM   docstring present, zero claims
  UNMEASURABLE_INDETERMINATE        claims present, none UNSATISFIED, at
                                    least one INDETERMINATE
  FAITHFUL                          every claim SATISFIED
  UNFAITHFUL                        at least one claim UNSATISFIED
A row's snippet is checked as it was extracted (May text), not the
current tree: the question is whether the recorded pair is faithful.

STAGE C -- EXECUTION, only for rows that are pytest test functions and
LOCATED_SAME: one pytest invocation per family over the node ids
(file::[Class::]name), `-q -rA --tb=no -p no:cacheprovider`, 900 s per
family. Per row: PASS / FAIL / ERROR / TIMEOUT / NOT_COLLECTED (pytest
did not report the node) / NOT_RUN (not a test or not LOCATED_SAME).
A test that PASSES shows the recorded check is executable against the
current tree; it does not show the docstring is true of the code -- that
is Stage B's question, and the two are reported separately.

STAGE D -- ORACLE and SHARED PARTS (the door Archaeon named in #60,
measured, not asserted): for every non-test row in the family, whether
any test file in the tree references the function name (HAS_ORACLE), and
for the whole prometheus_math_modules family, the call-graph overlap:
free names of each row that are names of other functions in the family
(SHARED_PART_OUT) and functions used by >= 2 other rows (SHARED_PART_IN).

STAGE E -- RESIDUE TAGS, structural, several may apply, none is a claim:
  TEST_EXECUTABLE     Stage C PASS
  PROPERTY            name or docstring contains "property"/"invariant"
                      or the body uses hypothesis' `given`
  EDGE_OR_CONSTRAINT  name/docstring contains edge|raises|reject|invalid|
                      must not|boundary, or the body has pytest.raises
  REGRESSION_OR_CE    name/docstring contains regression|counterexample
                      |known_failure|bug
  IMPL_WITH_ORACLE    non-test, LOCATED_*, HAS_ORACLE
  IMPL_NO_ORACLE      non-test, LOCATED_*, no test references it

WHAT COUNTS AS "SEMANTICALLY REAL" (declared now): a row is counted only
if its Stage B outcome is FAITHFUL, or it is a test with Stage C PASS.
UNMEASURABLE rows are reported as their own column and are never folded
into either side. No threshold or gate is set: this is characterization.

CONTROLS run first and abort on failure: positive (planted docstring
claims satisfied -> FAITHFUL), cheat (same docstring, body contradicts
-> UNFAITHFUL with the two unsatisfied claims named), negative (empty
docstring -> NO_SPEC; "Helper." -> NO_CHECKABLE_CLAIM), indeterminate
(returns a Name -> INDETERMINATE), and execution (a temporary test file
with one passing and one failing test yields PASS and FAIL through the
same runner and parser).
"""
from __future__ import annotations

import ast
import collections
import hashlib
import json
import random
import re
import subprocess
import sys
import tempfile
import textwrap
import time
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SHARDS = REPO / "roles" / "Talos" / "ledgers" / "corpus_shards_2026-09-11"
OUT = REPO / "roles" / "Talos" / "ledgers" / "SEMANTIC_SAMPLE_2026-09-11.json"
SEED = 20260911
PER_FAMILY = 100
FAMILIES = [
    ("hephaestus_forge_tools", "agents/hephaestus/forge"),
    ("hephaestus_humanreadable", "agents/hephaestus/humanreadable/"),
    ("hephaestus_code_from_claude", "agents/hephaestus/code_from_claude/"),
    ("hephaestus_other", "agents/hephaestus/"),
    ("prometheus_math_tests", "prometheus_math/tests/"),
    ("prometheus_math_modules", "prometheus_math/"),
    ("charon_diagnostics", "charon/diagnostics/"),
    ("theseus_scripts", "theseus/scripts/"),
    ("scripts_agora_persist", "scripts/"),
]
EXC_RE = re.compile(r"\b([A-Z]\w*(?:Error|Exception|Warning))\b")
RET_RE = re.compile(r"\breturn(?:s|ed|ing)?\s+(?:a\s+|an\s+|the\s+)?(None|True|False|bool(?:ean)?|int(?:eger)?|float|str(?:ing)?|dict(?:ionary)?|list|tuple|path|set)\b", re.IGNORECASE)
IDENT_BT_RE = re.compile(r"`+([A-Za-z_][\w\.]*)`+")
IDENT_US_RE = re.compile(r"\b([a-z][a-z0-9]*_[a-z0-9_]+)\b")
IDENT_CC_RE = re.compile(r"\b([A-Z][a-z]+[A-Z][A-Za-z]{2,})\b")
KIND_WORDS = {"none": "None", "true": "True", "false": "False", "bool": "bool", "boolean": "bool", "int": "int",
              "integer": "int", "float": "float", "str": "str", "string": "str", "dict": "dict", "dictionary": "dict",
              "list": "list", "tuple": "tuple", "path": "Path", "set": "set"}


def family_of(path):
    for name, prefix in FAMILIES:
        if path.startswith(prefix):
            return name
    return "unclassified"


def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def parse_snippet(snippet):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for text in (snippet, textwrap.dedent(snippet)):
            try:
                tree = ast.parse(text)
                if tree.body and isinstance(tree.body[0], (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return tree.body[0], text
            except SyntaxError:
                continue
    return None, None


def strip_docstring(fn):
    body = fn.body
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        return body[1:]
    return body


def return_kinds(fn):
    """Kinds of every `return <value>` in fn (not nested defs). 'unknown' when the AST cannot say."""
    kinds = []
    for node in ast.walk(fn):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not fn:
            continue
        if isinstance(node, ast.Return):
            v = node.value
            if v is None:
                kinds.append("None")
            elif isinstance(v, ast.Constant):
                kinds.append({type(None): "None", bool: "True" if v.value is True else "False", int: "int", float: "float",
                              str: "str"}.get(type(v.value), "unknown"))
            elif isinstance(v, (ast.Dict, ast.DictComp)):
                kinds.append("dict")
            elif isinstance(v, (ast.List, ast.ListComp)):
                kinds.append("list")
            elif isinstance(v, ast.Tuple):
                kinds.append("tuple")
            elif isinstance(v, (ast.Set, ast.SetComp)):
                kinds.append("set")
            elif isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id in ("dict", "list", "tuple", "set", "int", "float", "str", "bool", "Path"):
                kinds.append(v.func.id)
            elif isinstance(v, ast.Compare) or (isinstance(v, ast.BoolOp)):
                kinds.append("bool")
            elif isinstance(v, ast.JoinedStr):
                kinds.append("str")
            else:
                kinds.append("unknown")
    return kinds


def raised_names(fn):
    names = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Raise) and node.exc is not None:
            e = node.exc
            if isinstance(e, ast.Call):
                e = e.func
            if isinstance(e, ast.Name):
                names.add(e.id)
            elif isinstance(e, ast.Attribute):
                names.add(e.attr)
        if isinstance(node, ast.Call):
            f = node.func
            fname = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if fname == "raises":
                for a in node.args:
                    if isinstance(a, ast.Name):
                        names.add(a.id)
                    elif isinstance(a, ast.Attribute):
                        names.add(a.attr)
                    elif isinstance(a, ast.Tuple):
                        for el in a.elts:
                            if isinstance(el, ast.Name):
                                names.add(el.id)
    return names


def claims_for(row, fn, code_text):
    """Return (claims, outcome). claims: list of dicts {kind, target, result}."""
    doc = (row.get("docstring") or "").strip()
    if not doc:
        return [], "UNMEASURABLE_NO_SPEC"
    claims = []
    raised = raised_names(fn)
    for x in sorted(set(EXC_RE.findall(doc))):
        claims.append({"kind": "RAISES", "target": x, "result": "SATISFIED" if x in raised else "UNSATISFIED"})
    kinds = return_kinds(fn)
    ann = None
    if fn.returns is not None:
        ann = fn.returns.id if isinstance(fn.returns, ast.Name) else (fn.returns.value if isinstance(fn.returns, ast.Constant) else None)
    for m in sorted(set(k.lower() for k in RET_RE.findall(doc))):
        k = KIND_WORDS.get(m, m)
        if ann is not None and str(ann) == k:
            res = "SATISFIED"
        elif k in kinds or (k == "bool" and ("True" in kinds or "False" in kinds)):
            res = "SATISFIED"
        elif kinds and all(kk == "unknown" for kk in kinds):
            res = "INDETERMINATE"
        elif kinds and any(kk == "unknown" for kk in kinds):
            res = "INDETERMINATE"
        elif not kinds:
            res = "SATISFIED" if k == "None" else "UNSATISFIED"
        else:
            res = "UNSATISFIED"
        claims.append({"kind": "RETURNS", "target": k, "result": res})
    params = {a.arg for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs}
    if fn.args.vararg:
        params.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        params.add(fn.args.kwarg.arg)
    idents = set(IDENT_BT_RE.findall(doc)) | set(IDENT_US_RE.findall(doc)) | set(IDENT_CC_RE.findall(doc))
    stop = set(EXC_RE.findall(doc)) | {fn.name}
    for ident in sorted(idents):
        base = ident.split(".")[0]
        if ident in stop or base in stop or len(base) < 3:
            continue
        found = base in params or re.search(r"\b" + re.escape(base) + r"\b", code_text) is not None
        claims.append({"kind": "MENTIONS", "target": ident, "result": "SATISFIED" if found else "UNSATISFIED"})
    if not claims:
        return claims, "UNMEASURABLE_NO_CHECKABLE_CLAIM"
    results = [c["result"] for c in claims]
    if "UNSATISFIED" in results:
        return claims, "UNFAITHFUL"
    if "INDETERMINATE" in results:
        return claims, "UNMEASURABLE_INDETERMINATE"
    return claims, "FAITHFUL"


def code_without_docstring(fn, text):
    """Source of fn minus its docstring, for MENTIONS checks."""
    body = strip_docstring(fn)
    if not body:
        return ""
    lines = text.splitlines()
    start = body[0].lineno - 1
    end = max(getattr(n, "end_lineno", n.lineno) for n in body)
    header = " ".join(lines[fn.lineno - 1: fn.body[0].lineno - 1]) if fn.body else ""
    return header + "\n" + "\n".join(lines[start:end])


class Located:
    def __init__(self, status, cls=None, is_test=False, lineno=None):
        self.status, self.cls, self.is_test, self.lineno = status, cls, is_test, lineno


_file_cache = {}


def locate(row):
    path = REPO / row["source_path"]
    if not path.exists():
        return Located("NOT_FOUND")
    if path not in _file_cache:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(text)
            _file_cache[path] = (text, tree)
        except SyntaxError:
            _file_cache[path] = None
    if _file_cache[path] is None:
        return Located("NOT_FOUND")
    text, tree = _file_cache[path]
    target = norm_ws(row["snippet"])
    candidates = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == row["function_name"]:
            candidates.append(node)
    if not candidates:
        return Located("NOT_FOUND")
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    best = None
    for c in candidates:
        seg = ast.get_source_segment(text, c) or ""
        if norm_ws(seg) == target:
            best = (c, "LOCATED_SAME")
            break
    if best is None:
        best = (candidates[0], "LOCATED_CHANGED")
    node, status = best
    par = parents.get(node)
    cls = par.name if isinstance(par, ast.ClassDef) else None
    nested = isinstance(par, (ast.FunctionDef, ast.AsyncFunctionDef))
    is_test = row["source_path"].split("/")[-1].startswith("test") and node.name.startswith("test") and not nested
    return Located(status, cls, is_test, node.lineno)


def run_pytest(node_ids, timeout=900):
    """One pytest invocation PER FILE (repair 2026-09-11, first run: a node id
    into a module-level-skipped file is a pytest usage error that aborted the
    whole batch, leaving 90 tests unreported). A file whose run reports no
    node marks its rows NOT_COLLECTED with pytest's own reason line."""
    if not node_ids:
        return {}, "no tests"
    by_file = collections.defaultdict(list)
    for n in node_ids:
        by_file[n.split("::")[0]].append(n)
    out_map, tails = {}, []
    for f, ids in sorted(by_file.items()):
        m, tail = _run_pytest_batch(ids, timeout=min(timeout, 600))
        out_map.update(m)
        tails.append("## {}\n{}".format(f, tail[-600:]))
    return out_map, "\n".join(tails)[-6000:]


def _run_pytest_batch(node_ids, timeout):
    cmd = [sys.executable, "-m", "pytest", "-q", "-rA", "--tb=no", "-p", "no:cacheprovider", "--continue-on-collection-errors", *node_ids]
    try:
        r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=timeout)
        out = r.stdout + "\n" + r.stderr
    except subprocess.TimeoutExpired:
        return {n: "TIMEOUT" for n in node_ids}, "timeout"
    reason = ""
    for line in out.splitlines():
        if line.startswith("SKIPPED [") or "found no collectors" in line or line.startswith("ERROR"):
            reason = line.strip()[:160]
            break
    res = {}
    for line in out.splitlines():
        m = re.match(r"^(PASSED|FAILED|ERROR|XFAIL|XPASS|SKIPPED)\s+(\S+)", line.strip())
        if m:
            status, nid = m.group(1), m.group(2)
            nid = nid.split(" ")[0]
            key = nid.replace("\\", "/")
            res[key] = {"PASSED": "PASS", "FAILED": "FAIL", "ERROR": "ERROR", "XFAIL": "FAIL", "XPASS": "PASS", "SKIPPED": "NOT_COLLECTED"}[status]
    out_map = {}
    for n in node_ids:
        k = n.replace("\\", "/")
        hit = res.get(k)
        if hit is None:
            # pytest may print parametrised or differently-rooted ids; match on the tail
            tail = k.split("/")[-1]
            for rk, rv in res.items():
                if rk.endswith(tail):
                    hit = rv
                    break
        out_map[n] = hit or ("NOT_COLLECTED: " + reason if reason else "NOT_COLLECTED")
    return out_map, out[-2000:]


def residue_tags(row, fn, loc, exec_status, has_oracle):
    doc = (row.get("docstring") or "").lower()
    name = row["function_name"].lower()
    code = row["snippet"]
    tags = []
    if exec_status == "PASS":
        tags.append("TEST_EXECUTABLE")
    if "property" in doc or "invariant" in doc or "property" in name or re.search(r"@given\b|\bgiven\(", code):
        tags.append("PROPERTY")
    if re.search(r"\b(edge|raises?|reject|invalid|must not|boundary)\b", doc + " " + name) or "raises(" in code:
        tags.append("EDGE_OR_CONSTRAINT")
    if re.search(r"regression|counterexample|known_failure|\bbug\b", doc + " " + name):
        tags.append("REGRESSION_OR_CE")
    if not loc.is_test and loc.status != "NOT_FOUND":
        tags.append("IMPL_WITH_ORACLE" if has_oracle else "IMPL_NO_ORACLE")
    return tags


def build_oracle_index():
    """function names referenced anywhere in test files under prometheus_math, charon, theseus, agents/hephaestus."""
    names = collections.Counter()
    for pat in ("prometheus_math/**/test*.py", "prometheus_math/**/tests/*.py", "charon/**/test*.py", "theseus/**/test*.py",
                "agents/hephaestus/**/test*.py", "tests/**/*.py"):
        for f in REPO.glob(pat):
            try:
                txt = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for tok in set(re.findall(r"\b[A-Za-z_]\w{2,}\b", txt)):
                names[tok] += 1
    return names


def shared_parts(rows):
    """Call-graph overlap inside one family: free names that are other rows' function names."""
    names = collections.Counter(r["function_name"] for r in rows)
    out_deg, in_deg = {}, collections.Counter()
    for r in rows:
        fn, text = parse_snippet(r["snippet"])
        if fn is None:
            continue
        called = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                f = node.func
                nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
                if nm and nm in names and nm != r["function_name"] and not nm.startswith("test"):
                    called.add(nm)
        out_deg[r["fingerprint"]] = sorted(called)
        for c in called:
            in_deg[c] += 1
    rows_with_out = sum(1 for v in out_deg.values() if v)
    helpers_in_ge2 = sum(1 for v in in_deg.values() if v >= 2)
    return {"rows_calling_another_family_function": rows_with_out, "rows_total_parsed": len(out_deg),
            "family_functions_called_by_ge2_rows": helpers_in_ge2, "top_shared_helpers": in_deg.most_common(15)}


def controls():
    def row(doc, snip, name="f", path="x/test_x.py"):
        return {"fingerprint": hashlib.sha1(snip.encode()).hexdigest()[:16], "function_name": name, "docstring": doc,
                "snippet": snip, "source_path": path, "lineno": 1, "stream": "ctl"}
    good = "def f(x, alpha_beta):\n    \"\"\"Raises ValueError when x < 0 and uses `alpha_beta`. Returns a dict.\"\"\"\n    if x < 0:\n        raise ValueError('neg')\n    return {'x': x, 'ab': alpha_beta}"
    bad = "def f(x, y):\n    \"\"\"Raises ValueError when x < 0 and uses `alpha_beta`. Returns a dict.\"\"\"\n    if x < 0:\n        raise TypeError('neg')\n    return [x, y]"
    ind = "def f(x):\n    \"\"\"Returns a dict.\"\"\"\n    return helper(x)"
    checks = {}
    fn, text = parse_snippet(good)
    c, o = claims_for(row("Raises ValueError when x < 0 and uses `alpha_beta`. Returns a dict.", good), fn, code_without_docstring(fn, text))
    checks["positive_FAITHFUL"] = (o == "FAITHFUL" and len(c) == 3)
    fn, text = parse_snippet(bad)
    c, o = claims_for(row("Raises ValueError when x < 0 and uses `alpha_beta`. Returns a dict.", bad), fn, code_without_docstring(fn, text))
    unsat = sorted(x["kind"] for x in c if x["result"] == "UNSATISFIED")
    checks["cheat_UNFAITHFUL_names_three_unsatisfied"] = (o == "UNFAITHFUL" and unsat == ["MENTIONS", "RAISES", "RETURNS"])
    fn, text = parse_snippet(good)
    checks["negative_NO_SPEC"] = claims_for(row("", good), fn, code_without_docstring(fn, text))[1] == "UNMEASURABLE_NO_SPEC"
    checks["negative_NO_CHECKABLE_CLAIM"] = claims_for(row("Helper.", good), fn, code_without_docstring(fn, text))[1] == "UNMEASURABLE_NO_CHECKABLE_CLAIM"
    fn, text = parse_snippet(ind)
    checks["indeterminate_return_of_a_call"] = claims_for(row("Returns a dict.", ind), fn, code_without_docstring(fn, text))[1] == "UNMEASURABLE_INDETERMINATE"
    # execution control through the same runner and parser
    d = Path(tempfile.mkdtemp(prefix="talos_ctl_", dir=str(REPO / "roles" / "Talos" / "science")))
    f = d / "test_ctl.py"
    f.write_text("def test_pass():\n    assert 1 == 1\n\ndef test_fail():\n    assert 1 == 2\n", encoding="utf-8")
    rel = f.relative_to(REPO).as_posix()
    res, _ = run_pytest([rel + "::test_pass", rel + "::test_fail"], timeout=300)
    checks["execution_PASS_and_FAIL_parsed"] = (res.get(rel + "::test_pass") == "PASS" and res.get(rel + "::test_fail") == "FAIL")
    import shutil
    shutil.rmtree(d, ignore_errors=True)    # pytest leaves __pycache__ beside the control file
    return checks


def main():
    t0 = time.time()
    ctl = controls()
    if not all(ctl.values()):
        print("CONTROLS FAILED", ctl)
        sys.exit(2)
    rows = []
    for name in ("hephaestus_forge", "prometheus_substrate"):
        raw = (SHARDS / (name + ".jsonl")).read_bytes().decode("utf-8")
        rows += [json.loads(l) for l in raw.splitlines() if l.strip()]
    fam_rows = collections.defaultdict(list)
    for r in rows:
        fam_rows[family_of(r["source_path"])].append(r)
    rng = random.Random(SEED)
    oracle_idx = build_oracle_index()
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(REPO), capture_output=True, text=True).stdout.strip()
    result = {"generated_from": "roles/Talos/science/semantic_faithfulness.py", "tree_head": head, "seed": SEED,
              "per_family_cap": PER_FAMILY, "controls": ctl, "families": {}, "door_shared_parts": {}}
    for fam in sorted(fam_rows, key=lambda k: -len(fam_rows[k])):
        pool = fam_rows[fam]
        sample = pool if len(pool) <= PER_FAMILY else rng.sample(pool, PER_FAMILY)
        per_row = []
        node_ids = {}
        for r in sample:
            fn, text = parse_snippet(r["snippet"])
            loc = locate(r)
            if fn is None:
                claims, outcome = [], "UNMEASURABLE_UNPARSEABLE"
            else:
                claims, outcome = claims_for(r, fn, code_without_docstring(fn, text))
            rec = {"fingerprint": r["fingerprint"], "source_path": r["source_path"], "function_name": r["function_name"],
                   "located": loc.status, "enclosing_class": loc.cls, "is_test": loc.is_test,
                   "spec_outcome": outcome, "claims": claims, "exec": "NOT_RUN",
                   "has_oracle": (not loc.is_test) and oracle_idx.get(r["function_name"], 0) > 0}
            if loc.is_test and loc.status == "LOCATED_SAME":
                nid = r["source_path"] + ("::" + loc.cls if loc.cls else "") + "::" + r["function_name"]
                node_ids[nid] = rec
            per_row.append((r, fn, loc, rec))
        exec_res, exec_tail = run_pytest(list(node_ids), timeout=900)
        for nid, rec in node_ids.items():
            rec["exec"] = exec_res.get(nid, "NOT_COLLECTED")
        for r, fn, loc, rec in per_row:
            rec["residue_tags"] = residue_tags(r, fn, loc, rec["exec"], rec["has_oracle"]) if fn is not None else []
        recs = [rec for _, _, _, rec in per_row]
        counts = lambda key: dict(collections.Counter(x[key] for x in recs))
        claim_counter = collections.Counter((c["kind"], c["result"]) for x in recs for c in x["claims"])
        sem_real = sum(1 for x in recs if x["spec_outcome"] == "FAITHFUL" or x["exec"] == "PASS")
        result["families"][fam] = {
            "population": len(pool), "sampled": len(sample),
            "located": counts("located"), "spec_outcome": counts("spec_outcome"),
            "exec": dict(collections.Counter(x["exec"].split(":")[0] for x in recs)),
            "exec_not_collected_reasons": dict(collections.Counter(x["exec"] for x in recs if x["exec"].startswith("NOT_COLLECTED:"))),
            "claims_by_kind_and_result": {"{}|{}".format(k, v): n for (k, v), n in sorted(claim_counter.items())},
            "residue_tags": dict(collections.Counter(t for x in recs for t in x["residue_tags"])),
            "has_oracle_nontest": sum(1 for x in recs if x["has_oracle"]),
            "nontest_rows": sum(1 for x in recs if not x["is_test"]),
            "semantically_real_rows": sem_real,
            "unmeasurable_rows": sum(1 for x in recs if x["spec_outcome"].startswith("UNMEASURABLE") and x["exec"] != "PASS"),
            "pytest_tail": exec_tail if node_ids else None,
            "rows": recs,
        }
        print(fam, "sampled", len(sample), "spec", counts("spec_outcome"), "exec", result["families"][fam]["exec"], "real", sem_real, flush=True)
    result["door_shared_parts"]["prometheus_math_modules"] = shared_parts(fam_rows["prometheus_math_modules"])
    result["door_shared_parts"]["prometheus_math_tests"] = shared_parts(fam_rows["prometheus_math_tests"])
    result["elapsed_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
    print("wrote", OUT.relative_to(REPO), "elapsed", result["elapsed_s"])


if __name__ == "__main__":
    main()
