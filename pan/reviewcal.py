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
    mutants, used, tried = [], set(), 0
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
            if ok or len(mutants) >= 40:      # survived (tests pass): not a known-detectable bug
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
                   survivors=tried - len(mutants), ops={o: sum(1 for m in mutants if m["answer"]["op"] == o)
                                                        for o in pr["operators"]},
                   items_sha256=hashlib.sha256(bi).hexdigest(), answers_sha256=hashlib.sha256(bk).hexdigest(),
                   items_path=str(pi), answers_path=str(pk), seconds=round(time.time() - t0, 1))
    out(json.dumps(summary))
    return summary
