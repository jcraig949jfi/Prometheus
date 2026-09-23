"""Slice 2C reachability certificate. RUN BEFORE ANY LINEAGE.

For every load-bearing capability class, establish that at least one valid
solution exists inside the exact grammar version, allowed primitives,
depth/structure bounds and escrow budget. Record the grammar hash, the
witness complexity and the search cost.

If any load-bearing class is unreachable, the slice STOPS here and no
evolutionary search is run.

The witness is NOT given to the improver: it is recorded in this certificate
and never enters engine.base_image(), the mutation grammar, the development
instances, or any privileged representation. Validation uses a CERTIFICATE
entropy domain that is neither development nor tribunal, so no tribunal
exists at this point in the protocol.
"""
import hashlib
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as E  # noqa: E402

CERT_BUDGET = 50 * 10 ** 6         # generous: this measures COST, it is not the run budget
VALIDATION_N = 400


def cert_entropy(cls_: str, i: int) -> int:
    return int(hashlib.sha256(
        ("APHRODITE/ENGINE/CERT/v1/%s/%d" % (cls_, i)).encode()).hexdigest()[:16], 16)


def cert_instances(cls_, n):
    out = []
    for i in range(n):
        rng = random.Random(cert_entropy(cls_, i))
        p, g = E._task(cls_, rng)
        out.append({"family": cls_, "prompt": p, "gold": g, "key": "cert-%s-%d" % (cls_, i)})
    return out


def _examples(cls_):
    """The development-shaped instances a lineage would search against."""
    return E.tasks(family=cls_, n=E.DEV_PER_FAMILY, seed=E.dev_entropy("CERT-PROBE", 0))


def _vectors(ex):
    import re
    return ([[int(v) for v in re.findall(r"-?\d+", t["prompt"])] for t in ex],
            [t["gold"] for t in ex])


def certify(cls_):
    ex = _examples(cls_)
    vectors, golds = _vectors(ex)
    rec = {"class": cls_, "development_instances": len(ex)}

    # 1. composition-only witness
    esc = E.Escrow(CERT_BUDGET)
    t0 = time.perf_counter()
    got = E._compose_v2(vectors, golds, esc, CERT_BUDGET)
    rec["composition"] = ({"witness": got[0], "size": got[1], "charges": got[2],
                           "seconds": round(time.perf_counter() - t0, 2)}
                          if got else {"witness": None, "charges": esc.spent,
                                       "seconds": round(time.perf_counter() - t0, 2)})

    # 2. structural (helper) witness, if composition alone does not reach it
    esc2 = E.Escrow(CERT_BUDGET)
    t1 = time.perf_counter()
    st = E._structural_search(ex, esc2, CERT_BUDGET, random.Random(0))
    rec["structural"] = ({"e1": st[0], "e2": st[1], "answer": st[2], "charges": esc2.spent,
                          "seconds": round(time.perf_counter() - t1, 2)}
                         if st else {"witness": None, "charges": esc2.spent,
                                     "seconds": round(time.perf_counter() - t1, 2)})

    # 3. validate whichever witness exists on independent CERT instances
    inst = cert_instances(cls_, VALIDATION_N)
    rec["validation"] = {}
    if got:
        src = E._discovered_solver_source(cls_, got[0])
        art = E.Artifact.from_modules(dict(E.base_image(),
                                           search=E.base_image()["search"] + src))
        r = E.Recipient.fresh(seed=1)
        r.load(art)
        rec["validation"]["composition_accuracy"] = r.run_tasks(inst, E.Escrow(10 ** 7))["accuracy"]
    if st:
        src = E.helper_solver_source(cls_, st[0], st[1], st[2])
        art = E.Artifact.from_modules(dict(E.base_image(),
                                           search=E.base_image()["search"] + src))
        r = E.Recipient.fresh(seed=1)
        r.load(art)
        rec["validation"]["structural_accuracy"] = r.run_tasks(inst, E.Escrow(10 ** 7))["accuracy"]

    best = max([v for v in rec["validation"].values()] or [0.0])
    rec["reachable_exactly"] = best >= 0.999
    rec["best_validation_accuracy"] = best

    # 4. THE DECIDING QUESTION: does a LOAD-BEARING structural witness exist?
    # A helper only counts if (a) it enables an exact solution and (b) no
    # substantially simpler surrogate preserves that capability. Established
    # here, before any lineage runs, so the slice is not asked to find
    # something the grammar cannot contain.
    rec["load_bearing_structural_witness"] = None
    rec["enabling_helpers_examined"] = 0
    rec["enabling_but_not_load_bearing"] = []
    import re as _re
    vecs, gds = vectors, golds
    pairs = [(v[0], v[1]) for v in vecs]
    atoms = ["x", "y"]
    exprs = list(atoms)
    for _n, (_f, tmpl) in E.PRIMITIVES.items():
        for a in atoms:
            for b in atoms:
                exprs.append(tmpl.format(a, b))
    seen_vec = set()
    for e1 in exprs:
        for e2 in exprs:
            vals = E._helper_values(e1, e2, pairs)
            if vals is None or vals in seen_vec:
                continue
            if all(v == vals[0] for v in vals):
                continue
            if any(vals == tuple(v[i] for v in vecs) for i in range(E.TERMINALS)):
                continue
            seen_vec.add(vals)
            esc3 = E.Escrow(5 * 10 ** 6)
            got3 = E._compose_v2(vecs, gds, esc3, 5 * 10 ** 6,
                                 extra=[("h(nums[0], nums[1])", vals)])
            if not got3 or "h(" not in got3[0]:
                continue
            rec["enabling_helpers_examined"] += 1
            src = E.helper_solver_source(cls_, e1, e2, got3[0])
            art = E.Artifact.from_modules(
                dict(E.base_image(), search=E.base_image()["search"] + src))
            batt = E.surrogate_battery(art, cls_, inst)
            entry = {"e1": e1, "e2": e2, "answer": got3[0],
                     "original_accuracy": batt["original_accuracy"],
                     "defeated_by": [s["surrogate"] for s in
                                     batt["surrogates_that_preserved_capability"]][:6]}
            if batt["load_bearing"] and batt["original_accuracy"] >= 0.999:
                rec["load_bearing_structural_witness"] = entry
                break
            rec["enabling_but_not_load_bearing"].append(entry)
        if rec["load_bearing_structural_witness"]:
            break
    return rec


def main():
    classes = list(E.HEADROOM_FAMILIES)
    rows = [certify(c) for c in classes]
    out = {
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "grammar_version": E.GRAMMAR_VERSION,
        "grammar_hash": E.grammar_hash(),
        "engine_sha256": E.source_hash(),
        "max_size": E.MAX_SIZE,
        "primitives": sorted(E.PRIMITIVES),
        "certificate_budget": CERT_BUDGET,
        "classes": rows,
        "all_load_bearing_classes_reachable": all(r["reachable_exactly"] for r in rows),
        "classes_with_a_load_bearing_structural_witness":
            [r["class"] for r in rows if r["load_bearing_structural_witness"]],
        "structural_success_criterion_satisfiable":
            any(r["load_bearing_structural_witness"] for r in rows),
    }
    p = HERE / "REACHABILITY_CERTIFICATE_2026-09-21.json"
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    if not out["all_load_bearing_classes_reachable"]:
        print("\nSTOP: a load-bearing class is UNREACHABLE. No evolutionary search is run.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
