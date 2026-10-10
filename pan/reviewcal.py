"""PAN-37 part 2: seeded-bug calibration set for agent-run code reviews (rules frozen in
pan/tests/reviewcal_prereg.json). Small realistic mutations go into PAN-34 task functions; a mutant is kept
only if the program's own test file catches it, so each one is a known bug with ground truth. Items and the
answer key live in the M2 lake only; their sha256 are committed (reviewing agents can search the repository).

python -m pan reviewcal build      generate and kill-check (CPU; take a Fabric CPU lease)
"""
import ast
import copy
import datetime as dt
import hashlib
import json
import random
import re
import time

from . import PKG, lake

PREREG = PKG / "tests" / "reviewcal_prereg.json"
CMP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
       ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Is: ast.IsNot, ast.IsNot: ast.Is}


def sites(fn_src):
    """All applicable (operator, node path) sites in one function's source. Node path = index in ast.walk
    order, which is deterministic for a given source."""
    tree = ast.parse(fn_src)
    out = []
    for i, node in enumerate(ast.walk(tree)):
        if isinstance(node, ast.Compare) and type(node.ops[0]) in CMP:
            out.append(("cmp_flip", i))
        elif isinstance(node, ast.BoolOp):
            out.append(("bool_flip", i))
        elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            out.append(("arith_flip", i))
        elif isinstance(node, ast.Constant) and type(node.value) is int:
            out.append(("off_by_one", i))
        elif isinstance(node, (ast.If, ast.While)):
            out.append(("negate_if", i))
        elif isinstance(node, ast.Return) and node.value is not None and not (
                isinstance(node.value, ast.Constant) and node.value.value is None):
            out.append(("return_none", i))
    return out


def mutate(fn_src, op, idx):
    """(mutant_source, line, original_segment, mutated_segment) -- the target expression's source segment is
    replaced by the unparsed mutated expression; all other characters are unchanged."""
    tree = ast.parse(fn_src)
    node = list(ast.walk(tree))[idx]
    target = node.test if op == "negate_if" else (node.value if op == "return_none" else node)
    seg = ast.get_source_segment(fn_src, target)
    if seg is None:
        return None
    m = copy.deepcopy(target)
    if op == "cmp_flip":
        m.ops = [CMP[type(m.ops[0])]()] + m.ops[1:]
    elif op == "bool_flip":
        m.op = ast.Or() if isinstance(m.op, ast.And) else ast.And()
    elif op == "arith_flip":
        m.op = ast.Sub() if isinstance(m.op, ast.Add) else ast.Add()
    elif op == "off_by_one":
        m.value = m.value + 1
    elif op == "negate_if":
        m = ast.UnaryOp(op=ast.Not(), operand=m)
    elif op == "return_none":
        m = ast.Constant(value=None)
    new = ast.unparse(m)
    if op == "negate_if":
        new = "not ({})".format(ast.unparse(target))
    lines = fn_src.splitlines(keepends=True)
    l0, c0, l1, c1 = target.lineno - 1, target.col_offset, target.end_lineno - 1, target.end_col_offset
    # col offsets are UTF-8 byte offsets: slice on bytes
    head = "".join(lines[:l0]) + lines[l0].encode("utf-8")[:c0].decode("utf-8", errors="replace")
    tail = lines[l1].encode("utf-8")[c1:].decode("utf-8", errors="replace") + "".join(lines[l1 + 1:])
    mutant = head + new + tail
    if mutant == fn_src:
        return None
    try:
        ast.parse(mutant)
    except SyntaxError:
        return None
    return mutant, target.lineno, seg, new


def build(workers=4, out=print):
    from . import repobench as rb
    pr = json.loads(PREREG.read_text(encoding="utf-8"))
    man, base, dirs = rb.load(workers=workers, out=out)
    ex = rb.excluded()
    tasks = [t for t in man["tasks"] if t["task_id"] not in ex]
    rng = random.Random(37)
    order = tasks[:]
    rng.shuffle(order)
    t0 = time.time()
    mutants, used, tried, survived = [], set(), 0, 0
    i = 0
    while len(mutants) < 40 and i < len(order):
        batch = []
        while len(batch) < workers * 2 and i < len(order):
            t = order[i]
            i += 1
            text = (base / t["module"]).read_text(encoding="utf-8")
            fn = rb.function_source(text, t)
            ss = sites(fn)
            if not ss:
                continue
            op, idx = ss[rng.randrange(len(ss))]
            mu = mutate(fn, op, idx)
            if mu is None:
                continue
            batch.append((t, fn, op, mu))
        jobs = [(t, mu[0], None) for t, fn, op, mu in batch]
        tried += len(jobs)
        for (t, fn, op, mu), (ok, detail) in zip(batch, rb.verdicts(dirs, jobs)):
            if ok:                            # survived (tests pass): not a known-detectable bug
                survived += 1
                continue
            if len(mutants) >= 40:
                continue
            used.add(t["task_id"])
            mutants.append(dict(item=None, task_id=t["task_id"], module=t["module"], function=t["name"],
                                start=t["start"], end=t["end"], kind="mutant", code=mu[0],
                                answer=dict(op=op, line_in_function=mu[1], line_in_module=t["start"] + mu[1] - 1,
                                            original=mu[2], mutated=mu[3], test=t["test"], killed_by=detail)))
        out("  {} candidates tried -> {} killed mutants ({:.0f}s)".format(tried, len(mutants), time.time() - t0))
    rest = [t for t in order if t["task_id"] not in used]
    clean = []
    for t in rest[:20]:
        text = (base / t["module"]).read_text(encoding="utf-8")
        clean.append(dict(item=None, task_id=t["task_id"], module=t["module"], function=t["name"], start=t["start"],
                          end=t["end"], kind="clean", code=rb.function_source(text, t), answer=dict(op=None)))
    items = mutants + clean
    rng.shuffle(items)                        # reviewers must not infer kind from position
    for k, it in enumerate(items, 1):
        it["item"] = "RC-{:03d}".format(k)
    shown = [{k: v for k, v in it.items() if k not in ("answer", "kind")} for it in items]
    key = [dict(item=it["item"], kind=it["kind"], **it["answer"]) for it in items]
    d = lake() / "reviewcal"
    d.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    pi, pk = d / "ITEMS_{}.json".format(stamp), d / "ANSWERS_{}.json".format(stamp)
    bi = json.dumps(shown, indent=1).encode("utf-8")
    bk = json.dumps(key, indent=1).encode("utf-8")
    pi.write_bytes(bi)
    pk.write_bytes(bk)
    summary = dict(stamp=stamp, items=len(items), mutants=len(mutants), clean=len(clean), candidates_tried=tried,
                   survivors=survived, ops={o: sum(1 for m in mutants if m["answer"]["op"] == o)
                                                        for o in pr["operators"]},
                   items_sha256=hashlib.sha256(bi).hexdigest(), answers_sha256=hashlib.sha256(bk).hexdigest(),
                   items_path=str(pi), answers_path=str(pk), seconds=round(time.time() - t0, 1))
    out(json.dumps(summary))
    return summary


INSTRUCTIONS = ("You are reviewing one Python function from a research codebase. Decide whether it contains a bug "
                "(code that does not do what its name, docstring and surrounding logic intend). Reply with ONLY one "
                "JSON object: {\"bug\": true or false, \"line\": <line number within the function, counting the def "
                "line as 1, or null>, \"scenario\": \"<one sentence: input or state -> wrong result>\"}.")


def latest(kind):
    ps = sorted((lake() / "reviewcal").glob("{}_*.json".format(kind)))
    if not ps:
        raise SystemExit("no {} file in {}".format(kind, lake() / "reviewcal"))
    return ps[-1]


def packets():
    """Reviewer packets: (item id, prompt) with the code only -- no module path, no task id, no module line
    numbers (prereg A1). The function's lines are numbered from 1 so findings can cite them."""
    items = json.loads(latest("ITEMS").read_text(encoding="utf-8"))
    out = []
    for it in items:
        numbered = "\n".join("{:>3}  {}".format(i, ln) for i, ln in enumerate(it["code"].splitlines(), 1))
        out.append((it["item"], INSTRUCTIONS + "\n\n```python\n" + numbered + "\n```"))
    return out


def score(findings, answers=None):
    """findings: {item: {"bug": bool, "line": int|None}}. Scoring as frozen: hit = mutant item with bug true
    and a line within +-2 of the mutated line; false alarm = clean item with bug true."""
    from .codebench import wilson
    key = answers if answers is not None else json.loads(latest("ANSWERS").read_text(encoding="utf-8"))
    hits = misses = fa = clean = 0
    for a in key:
        f = findings.get(a["item"]) or {}
        flagged = bool(f.get("bug"))
        if a["kind"] == "mutant":
            line = f.get("line")
            ok = flagged and isinstance(line, int) and abs(line - a["line_in_function"]) <= 2
            hits += ok
            misses += not ok
        else:
            clean += 1
            fa += flagged
    n_mut = hits + misses
    return dict(hits=hits, mutants=n_mut, recall=round(hits / n_mut, 3) if n_mut else None,
                recall_wilson95=wilson(hits, n_mut), false_alarms=fa, clean=clean,
                false_alarm_rate=round(fa / clean, 3) if clean else None, false_alarm_wilson95=wilson(fa, clean),
                unreliable_for_unsupervised=(wilson(hits, n_mut)[1] < 0.5) if n_mut else None)


# ---------------------------------------------------------------- chance floors (prereg A3)

def site_lines(code):
    """Line numbers (within the function, def = 1) of every applicable mutation site under the frozen operators --
    public information (the operator list is in the committed prereg)."""
    tree = ast.parse(code)
    nodes = list(ast.walk(tree))
    out = []
    for op, idx in sites(code):
        n = nodes[idx]
        t = n.test if op == "negate_if" else (n.value if op == "return_none" else n)
        out.append(getattr(t, "lineno", getattr(n, "lineno", 1)))
    return out


def heuristic_line(code, window=2):
    """The line whose +-window neighbourhood holds the most mutation sites (ties -> earliest); 1 if none.
    Uses the item's code only, never the answer key."""
    import textwrap
    lines = site_lines(textwrap.dedent(code))
    n = len(code.splitlines())
    if not lines:
        return 1
    return max(range(1, n + 1), key=lambda L: (sum(1 for x in lines if abs(x - L) <= window), -L))


TELLS = (re.compile(r"\breturn None\b"), re.compile(r"\bnot \("))


def tell_line(code):
    """First line carrying a textual signature of the frozen operators (`return None` from return_none, `not (` from
    ast.unparse in negate_if), or None. Reads the item's code only."""
    for i, ln in enumerate(code.splitlines(), 1):
        if any(rx.search(ln) for rx in TELLS):
            return i
    return None


def floors(write=True, out=print, seed=37, draws=10000):
    """What a reviewer scores WITHOUT reviewing, under the frozen rule (one finding per item; hit = mutant item
    flagged with a line within +-2 of the mutated line; false alarm = clean item flagged):
      silent       never flags: recall 0, false-alarm rate 0
      random line  always flags, line uniform over the function: expected recall = mean window coverage
      middle line  always flags the middle line
      site density always flags the line whose +-2 window holds the most sites of the frozen operators
    A reviewer abstaining at random keeps recall/false-alarm on the line recall = R_floor x FA, so a reviewer is
    better than a floor only above that line. Writes aggregates only (no item lines: the key stays secret)."""
    import numpy as np
    from . import REPO
    items = {it["item"]: it for it in json.loads(latest("ITEMS").read_text(encoding="utf-8"))}
    key = json.loads(latest("ANSWERS").read_text(encoding="utf-8"))
    mut = [a for a in key if a["kind"] == "mutant"]
    n_lines = {i: len(items[i]["code"].splitlines()) for i in items}
    cover = [len([L for L in range(1, n_lines[a["item"]] + 1) if abs(L - a["line_in_function"]) <= 2]) / n_lines[a["item"]]
             for a in mut]
    rng = np.random.default_rng(seed)
    mc = float(np.mean([np.mean([abs(int(rng.integers(1, n_lines[a["item"]] + 1)) - a["line_in_function"]) <= 2 for a in mut])
                        for _ in range(200)]))
    res = {}
    for name, pick in (("middle_line", lambda it: (len(it["code"].splitlines()) + 1) // 2),
                       ("site_density", lambda it: heuristic_line(it["code"])),
                       ("surface_tell", lambda it: tell_line(it["code"])),
                       ("tell_else_density", lambda it: tell_line(it["code"]) or heuristic_line(it["code"]))):
        f = {i: dict(bug=pick(it) is not None, line=pick(it)) for i, it in items.items()}
        sc = score(f, key)
        by_op = {}
        for a in mut:
            ok = f[a["item"]]["bug"] and abs(f[a["item"]]["line"] - a["line_in_function"]) <= 2
            d = by_op.setdefault(a["op"], [0, 0])
            d[0] += ok
            d[1] += 1
        res[name] = dict(recall=sc["recall"], recall_wilson95=sc["recall_wilson95"], hits=sc["hits"],
                         false_alarm_rate=sc["false_alarm_rate"], false_alarms=sc["false_alarms"],
                         unreliable_by_frozen_rule=sc["unreliable_for_unsupervised"], by_operator={k: "{}/{}".format(*v) for k, v in by_op.items()})
    silent = score({}, key)
    oracle = score({a["item"]: dict(bug=a["kind"] == "mutant", line=a.get("line_in_function")) for a in key}, key)
    off3 = score({a["item"]: dict(bug=True, line=(a["line_in_function"] or 0) + 3) for a in mut}, key)
    lens = sorted(n_lines[a["item"]] for a in mut)
    doc = dict(control="PAN-37 reviewer chance floors (prereg A3)", items=latest("ITEMS").name,
               mutants=len(mut), clean=len(key) - len(mut),
               mutant_function_lines=dict(min=lens[0], median=lens[len(lens) // 2], max=lens[-1]),
               share_mutants_window_covers_half_or_more=round(float(np.mean([c >= 0.5 for c in cover])), 3),
               floors=dict(silent=dict(recall=silent["recall"], false_alarm_rate=silent["false_alarm_rate"]),
                           random_line=dict(expected_recall=round(float(np.mean(cover)), 3), monte_carlo=round(mc, 3),
                                            false_alarm_rate=1.0),
                           **res))
    checks = [
        dict(kind="POSITIVE", name="the answer key itself scores recall 1, false alarms 0",
             ok=oracle["recall"] == 1.0 and oracle["false_alarms"] == 0, detail="{} / {}".format(oracle["recall"], oracle["false_alarms"])),
        dict(kind="NEGATIVE", name="a silent reviewer scores 0 and 0; a line 3 away from every bug scores 0",
             ok=silent["hits"] == 0 and silent["false_alarms"] == 0 and off3["hits"] == 0,
             detail="silent {}/{}; off-by-3 hits {}".format(silent["hits"], silent["false_alarms"], off3["hits"])),
        dict(kind="CHEAT", name="the analytic random-line floor equals a 200x Monte Carlo of it within 0.02",
             ok=abs(mc - float(np.mean(cover))) <= 0.02, detail="{:.3f} vs {:.3f}".format(float(np.mean(cover)), mc)),
    ]
    doc["checks"] = checks
    doc["verdict"] = "PASS" if all(c["ok"] for c in checks) else "FAIL"
    if write:
        at = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        p = REPO / "roles" / "Pan" / "reports" / "controls" / "REVIEWCAL_FLOORS_{}.json".format(at)
        p.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        out("wrote " + str(p))
    out(json.dumps(doc["floors"], indent=1))
    out("mutant functions: lines {mutant_function_lines}; window covers >= half the function for {share_mutants_window_covers_half_or_more} of mutants".format(**doc))
    for c in checks:
        out("{:<8} {:<5} {}  ({})".format(c["kind"], "PASS" if c["ok"] else "FAIL", c["name"], c["detail"]))
    out(doc["verdict"])
    return doc
