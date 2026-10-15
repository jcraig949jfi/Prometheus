"""The evaluator registered as rso.adversary targets and attacked with the kit's five attacks (C-019-T040 item 6).

    python -m rso.gen5.ananke.eval.adversary_target [--json OUT]      exit code = rso.adversary.core.exit_code

Registration is in THIS package (the packet owns rso/gen5/ananke/eval/ only): `register()` adds two entries to the
in-memory rso.adversary.targets.TARGETS and one recorded limitation to rso.adversary.limitations.LIMITATIONS, then the
kit's own runner (core.run_variants, core.judge, attacks.*) executes them. Making them permanent in rso/adversary/ is a
two-line change for its owner (README s6). Nothing here edits a committed file; every attack works on in-memory copies.

Targets:
  ananke_c4_ka      ka_table.reduce_rows over the committed known-answer rows (runs/ka/) and owner.load
  ananke_access     access.compare_arms over a synthetic paired search table with a known answer
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys

import numpy as np

from rso.adversary import attacks as X
from rso.adversary import core as KC
from rso.adversary import limitations as LIM
from rso.adversary import targets as TG

from . import access as A
from . import ka_table as KT
from . import owner

HERE = os.path.dirname(os.path.abspath(__file__))
KA_DIR = os.path.join(HERE, "runs", "ka")
LIMIT_ID = "argus-c019t040-ka-replay-sample"
LIMITATION = {
    "source": "rso/gen5/ananke/eval/README.md",
    "marker": "consistent rewrite of the per-trial arrays of a row outside the replay sample",
    "summary": "ka_table.reduce recomputes every reading from the stored per-trial arrays and re-executes only a "
               "plan-fixed sample of rows; a row outside the sample whose arrays were rewritten consistently (pt_sha "
               "recomputed) and whose recomputed verdict is unchanged is not detected (C-019-T040).",
}
_CACHE: dict = {}


def _ka():
    if "ka" not in _CACHE:
        _CACHE["ka"] = (owner.cells(), owner.admission(), owner.library(), owner.dlib(), KT.load_rows(KA_DIR))
    return _CACHE["ka"]


def _reduce(rows, replay_k=0, rule=None):
    cells, adm, lib, dl, _ = _ka()
    return KC.call(KT.reduce_rows, rows, cells, adm, lib, dl, replay_k=replay_k, rule=rule)


def _verdict(res):
    return res["verdict"] == "PASS", "; ".join(res["problems"][:3]) or "PASS"


def _ka_drop():
    rows = _ka()[4]
    att = X.drop(rows, 0)
    ok, why = _verdict(_reduce(att))
    return KC.judge(ok, why, X.fingerprint(att) != X.fingerprint(rows))


def _ka_duplicate():
    rows = _ka()[4]
    att = X.duplicate(rows, 0, 1)
    ok, why = _verdict(_reduce(att))
    return KC.judge(ok, why, X.fingerprint(att) != X.fingerprint(rows))


def _idx(rows, pred):
    return next(i for i, r in enumerate(rows) if pred(r))


def _ka_rewrite_status():
    """A row's verdict rewritten (FALSE -> TRUE) with its pass flag kept consistent."""
    rows = _ka()[4]
    i = _idx(rows, lambda r: r["kind"] == "ALONE")
    att = X.rewrite_derived(rows, lambda rs: rs[i].update(status="TRUE"), lambda rs: rs[i].__setitem__("pass", True))
    ok, why = _verdict(_reduce(att))
    return KC.judge(ok, why, X.fingerprint(att) != X.fingerprint(rows))


def _permute_pairs(row):
    pt = KT.decode_pt(row["pt"])
    p = pt.reshape(pt.shape[0], -1, 2, pt.shape[2])[:, ::-1].reshape(pt.shape)          # reverse the pair order
    row["pt"] = KT.encode_pt(p); row["pt_sha"] = KT._sha(p)


def _ka_rewrite_arrays(in_sample: bool):
    """Per-trial arrays rewritten (mirror pairs reversed) and pt_sha recomputed: the readings of a row with no owner
    numbers (ALONE) are unchanged, so only re-execution can see it."""
    def run():
        cells, adm, lib, dl, rows = _ka()
        planned = [ck["check_id"] for ck in KT.plan_checks(cells, adm, lib, dl)]
        sample = KT.replay_sample(planned, 2)
        pick = (lambda r: r["check_id"] in sample) if in_sample else \
            (lambda r: r["kind"] == "ALONE" and r["check_id"] not in sample)
        i = _idx(rows, pick)
        att = copy.deepcopy(rows)
        _permute_pairs(att[i])
        ok, why = _verdict(_reduce(att, replay_k=2))
        return KC.judge(ok, f"{rows[i]['check_id']}: {why}", X.fingerprint(att) != X.fingerprint(rows),
                        None if in_sample else LIMIT_ID)
    return run


def _ka_constant(value):
    det = X.constant_detector(value)

    def rule(role, pt, ep):
        return {"status": det(pt)}

    def run():
        rows = _ka()[4]
        res = _reduce(rows, replay_k=0, rule=rule)
        ok, why = _verdict(res)
        return KC.judge(ok, f"constant {value} ruler: {why}", True)
    return run


def _ka_scrub_rows():
    rows = _ka()[4]
    i = _idx(rows, lambda r: r["kind"] == "ADM")
    att = X.scrub_answer(rows[i], ["pt"], "remove")
    new = list(rows); new[i] = att
    ok, why = _verdict(_reduce(new))
    return KC.judge(ok, why, X.fingerprint(new) != X.fingerprint(rows))


def _owner_scrub():
    """The owner's admission record corrupted on the way in (a recorded mean changed): owner.load must refuse."""
    path = owner.C4 + "admission_R4.json"
    real = owner._git
    data = real("show", f"{owner.OWNER_SHA}:{path}")
    bad = data.replace(b"0.9599609375", b"0.9699609375", 1)

    def fake(*args):
        return bad if args[:1] == ("show",) and args[1].endswith(path) else real(*args)
    owner._git = fake
    try:
        try:
            KC.call(owner.load, path)
            accepted, why = True, "loaded"
        except KC.ComponentRaised as e:
            accepted, why = False, str(e.args[0])[:160]
    finally:
        owner._git = real
    return KC.judge(accepted, why, bad != data)


# ------------------------------------------------------------------ access target (synthetic, known answer)
def _table():
    rows = []
    for idx in range(16):
        for arm, hit_at in (("CONTROL", None), ("REUSE", 12 if idx < 6 else None)):
            cks = [{"gen": g, "status": "TRUE" if hit_at is not None and g >= hit_at else "FALSE"} for g in range(6, 37, 6)]
            rows.append({"arm": arm, "cell": "c0", "idx": idx, "ran": True, "budget": 36, "checkpoints": cks,
                         "hit": hit_at is not None, "time": hit_at if hit_at is not None else 36})
    return rows


def _acc(att, rows):
    try:
        out = KC.call(A.compare_arms, att, "REUSE", "CONTROL")
        return KC.judge(True, f"compared: {out['arm1']['hits']}/{out['arm1']['n']} vs {out['arm0']['hits']}/{out['arm0']['n']}",
                        X.fingerprint(att) != X.fingerprint(rows))
    except KC.ComponentRaised as e:
        return KC.judge(False, str(e.args[0])[:160], X.fingerprint(att) != X.fingerprint(rows))


def _acc_drop():
    rows = _table(); return _acc(X.drop(rows, 3), rows)


def _acc_duplicate():
    rows = _table(); return _acc(X.duplicate(rows, 1, 3), rows)          # a REUSE hit copied over another REUSE search


def _acc_rewrite():
    rows = _table()
    i = _idx(rows, lambda r: r["arm"] == "CONTROL")
    att = X.rewrite_derived(rows, lambda rs: rs[i].update(hit=True, time=6), lambda rs: None)
    return _acc(att, rows)


def _acc_scrub():
    rows = _table()
    i = _idx(rows, lambda r: r["arm"] == "REUSE" and r["hit"])
    new = list(rows); new[i] = X.scrub_answer(rows[i], ["checkpoints"], "remove")
    return _acc(new, rows)


def register():
    LIM.LIMITATIONS.setdefault(LIMIT_ID, LIMITATION)
    TG.TARGETS["ananke_c4_ka"] = {
        "campaign": "C-019", "source": "rso/gen5/ananke/eval/ka_table.py (reduce_rows, recheck_row); owner.py (load)",
        "summary": "the independent PTE-C4 evaluator's known-answer table and its owner-artifact custody",
        "variants": [("DROP", "row-0", _ka_drop), ("DUPLICATE", "row-0-over-row-1", _ka_duplicate),
                     ("REWRITE_DERIVED", "status-FALSE-to-TRUE", _ka_rewrite_status),
                     ("REWRITE_DERIVED", "arrays-replayed-row", _ka_rewrite_arrays(True)),
                     ("REWRITE_DERIVED", "arrays-unreplayed-row", _ka_rewrite_arrays(False)),
                     ("CONSTANT", "ruler-always-TRUE", _ka_constant("TRUE")),
                     ("CONSTANT", "ruler-always-FALSE", _ka_constant("FALSE")),
                     ("SCRUB_ANSWER", "row-per-trial-arrays-removed", _ka_scrub_rows),
                     ("SCRUB_ANSWER", "owner-admission-corrupted", _owner_scrub)],
        "not_applicable": {},
    }
    TG.TARGETS["ananke_access"] = {
        "campaign": "C-019", "source": "rso/gen5/ananke/eval/access.py (validate_searches, compare_arms)",
        "summary": "the accessibility comparison over a paired search table (synthetic, known answer 6/16 vs 0/16)",
        "variants": [("DROP", "search-3", _acc_drop), ("DUPLICATE", "REUSE-hit-over-REUSE-miss", _acc_duplicate),
                     ("REWRITE_DERIVED", "CONTROL-miss-to-hit", _acc_rewrite),
                     ("SCRUB_ANSWER", "checkpoints-removed", _acc_scrub)],
        "not_applicable": {"CONSTANT": "compare_arms contains no detector: hits are recomputed from checkpoint statuses "
                                       "issued by the ruler, whose CONSTANT attack is target ananke_c4_ka"},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--json")
    x = ap.parse_args(argv)
    register()
    rows = []
    for name in ("ananke_c4_ka", "ananke_access"):
        rows += KC.run_target(name)
    for r in rows:
        print(f"{r['target']:14s} {r['attack']:16s} {r['variant']:30s} {r['verdict']:14s} {r['limitation'] or ''} | {str(r['detail'])[:110]}")
    code = KC.exit_code(rows)
    print("exit", code)
    if x.json:
        with open(x.json, "w", newline="\n") as f:
            json.dump({"schema": "argus.c019t040.adversary.v1", "rows": rows, "exit_code": code}, f, indent=1)
    return code


if __name__ == "__main__":
    sys.exit(main())
