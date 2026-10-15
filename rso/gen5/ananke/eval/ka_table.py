"""Known-answer qualification table for the independent evaluator (C-019-T040 item 2).

    python -m rso.gen5.ananke.eval.ka_table plan
    python -m rso.gen5.ananke.eval.ka_table run --cells 0,2 --out DIR     (resumable; one JSONL row per check)
    python -m rso.gen5.ananke.eval.ka_table reduce DIR OUT.json [--replay K]   (exit 1 on any problem)

Checks per C4 cell (R4 physics; the owner's world seeds where the owner recorded a value, so numbers are comparable):
  ADM   admission (c4_admission.py): RELAY1H relay_flood TRUE / null FALSE; HOLD hold_latch TRUE / null FALSE;
        GATE gate_plant TRUE / null FALSE / relay_flood FALSE; FLIP P_FLIP TRUE / null FALSE / RELAY_LATCH FALSE
        (FLIP-0099: RELAY_LATCH recorded INDETERMINATE, the reason FLIP is not admitted there). Every recorded
        mean / lo99 must be reproduced to 1e-9 and every recorded status exactly.
  NEW   hold_latch on GATE must be FALSE (not checked by the owner; true by construction: it ignores the cue).
  DLIB_LIVE  build_dlib.py: line ablation on 32 worlds H(C4_NS, 0xD11B, cell_key) marks all 15 plant lines live.
  DLIB  on 128 held worlds H(C4_NS, 0xD11C, cell_key): plant TRUE; the two halves re-assembled at their own lines give
        identical per-trial outputs (TRUE); CONTEXT half alone FALSE; CUE half alone FALSE (DLIB_C4.json checks).
  ALONE each of the 8 frozen LIBRARY_C4 modules alone in a NOP genome (placed from line 0, identity register naming;
        the owner's placement is not recorded) is not TRUE on GATE (4 cells) or FLIP (3 admitted cells): 56 checks on
        64 worlds H(C4_NS, 0x1AB, cell_key).

EVIDENCE CONTRACT. A row carries the per-trial arrays of every genome it evaluated (codes 0 / 5 / 1 for 0, .5, 1) bound
by pt_sha. `reduce` re-derives every expectation from the owner's pinned artifacts (owner.py), recomputes every ruler
reading from the arrays, and compares the row's own claims instead of trusting them; DROP / DUPLICATE / UNPLANNED rows
are refused. A deterministic sample of K rows (fixed by the PLAN: smallest sha256(check_id)) is re-executed on the
oracle. LIMITATION (recorded): a consistent rewrite of the per-trial arrays of a row outside the replay sample, with its
pt_sha recomputed, is not detected without replaying that row (argus-c019t040-ka-replay-sample, README s5).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

from . import evaluate as E
from . import owner, ruler, worlds

TOL = 1e-9
CODE = {0.0: "0", 0.5: "5", 1.0: "1"}
DECODE = {"0": 0.0, "5": 0.5, "1": 1.0}


def _sha(pt) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(pt, dtype=np.float64)).tobytes()).hexdigest()[:16]


def encode_pt(pt) -> dict:
    pt = np.asarray(pt, dtype=np.float64)
    return {"shape": list(pt.shape), "codes": "".join(CODE[float(v)] for v in pt.ravel())}


def decode_pt(d) -> np.ndarray:
    v = np.array([DECODE[c] for c in d["codes"]], dtype=np.float64)
    if v.size != int(np.prod(d["shape"])):
        raise ValueError("per-trial code length does not match its shape")
    return v.reshape(d["shape"])


def plan_checks(cells, adm, lib, dl) -> list:
    out = []
    dmods = {}
    for m in dl["modules"]:
        dmods.setdefault(m["cell_id"], {})[m["name"]] = m
    for ci, c in enumerate(cells):
        cid = c["cell_id"]
        for task in worlds.TASKS:
            rec = adm[f"{cid}|{task}"]
            out.append(dict(kind="ADM", ci=ci, task=task, name="plant", expect=rec["plant"]["status"], recorded=rec["plant"]))
            out.append(dict(kind="ADM", ci=ci, task=task, name="null", expect="FALSE", recorded=rec["null"]))
            for an, ar in rec["adversaries"].items():
                out.append(dict(kind="ADM", ci=ci, task=task, name=an, expect=ar["status"], recorded=ar))
        out.append(dict(kind="NEW", ci=ci, task="GATE", name="hold_latch", expect="FALSE"))
        if adm[f"{cid}|GATE"]["admitted"]:
            out.append(dict(kind="DLIB_LIVE", ci=ci, task="GATE", name="plant_line_ablation", expect="ALL_15_LIVE"))
            out.append(dict(kind="DLIB", ci=ci, task="GATE", name="plant+reassembled+ctx+cue",
                            expect=["TRUE", "TRUE", "FALSE", "FALSE"], dmods=dmods[cid]))
        for task in ("GATE", "FLIP"):
            if not adm[f"{cid}|{task}"]["admitted"]:
                continue
            for m in lib:
                out.append(dict(kind="ALONE", ci=ci, task=task, name=f"LIB{m['id']}_{m['task']}", expect="NOT_TRUE",
                                lines=m["lines"]))
    for ck in out:
        ck["check_id"] = f"{ck['kind']}|{cells[ck['ci']]['cell_id']}|{ck['task']}|{ck['name']}"
    return out


def _genome(name, task, ph, adm, cid):
    if name == "plant":
        return np.asarray(adm[f"{cid}|{task}"]["plant_genome"], dtype=np.int64)
    if name == "null":
        return E.null_genome(ph)
    if name == "relay_flood":
        return np.asarray(adm[f"{cid}|RELAY1H"]["plant_genome"], dtype=np.int64)
    if name == "hold_latch":
        return np.asarray(adm[f"{cid}|HOLD"]["plant_genome"], dtype=np.int64)
    if name == "relay_latch":
        return E.relay_latch(ph)
    raise KeyError(name)


def setup(ck, cells, adm):
    """Everything a check needs except the dynamics (physics, env, seeds, genomes), derived from the plan and the
    owner's pinned artifacts -- never from a row."""
    c = cells[ck["ci"]]; cid = c["cell_id"]; task = ck["task"]
    ph = worlds.rep_physics(c["physics"], "R4"); env = worlds.task_env(c["env"], task)
    if ck["kind"] in ("ADM", "NEW"):
        seeds = E.admission_seeds(task, c["cell_key"])
        genomes = [_genome(ck["name"], task, ph, adm, cid)]
    elif ck["kind"] == "DLIB_LIVE":
        seeds = worlds.world_seeds(E.H(E.C4_NS, E.DLIB_LIVE_KEY, c["cell_key"]), 32)
        g = _genome("plant", task, ph, adm, cid)
        genomes = [g]
        for i in range(g.shape[1]):
            v = g.copy(); v[0, i] = 0; genomes.append(v)
    elif ck["kind"] == "DLIB":
        seeds = E.dlib_held_seeds(c["cell_key"])
        g = _genome("plant", task, ph, adm, cid)
        ctx, cue = ck["dmods"]["GATE_CONTEXT_HALF"], ck["dmods"]["GATE_CUE_HALF"]
        both = E.place_at(ph, list(zip(ctx["source_lines"], ctx["lines"])) + list(zip(cue["source_lines"], cue["lines"])))
        genomes = [g, both, E.place_at(ph, list(zip(ctx["source_lines"], ctx["lines"]))),
                   E.place_at(ph, list(zip(cue["source_lines"], cue["lines"])))]
    elif ck["kind"] == "ALONE":
        seeds = E.module_alone_seeds(c["cell_key"])
        genomes = [E.place(ph, ck["lines"], 0)]
    else:
        raise KeyError(ck["kind"])
    return ph, env, seeds, genomes


def judge(ck, pt, ep, genomes, rule=None) -> dict:
    """The verdict of one check from its per-trial arrays pt [G, M, trials] and the plan's expectation.
    `rule` (default ruler.competence) is injectable so the adversarial kit can substitute a constant detector."""
    rule = rule or ruler.competence
    role = worlds.ROLE[ck["task"]]
    v = {}
    if ck["kind"] in ("ADM", "NEW", "ALONE"):
        r = rule(role, pt[0], ep)
        v["status"] = r["status"]
        ok = (r["status"] != "TRUE") if ck["kind"] == "ALONE" else (r["status"] == ck["expect"])
        if ck.get("recorded"):
            diffs = [abs(r[comp][k] - ck["recorded"][comp][k]) for comp in ("all", "late", "B")
                     if comp in ck["recorded"] and comp in r for k in ("mean", "lo99")]
            v["max_abs_diff_vs_owner"] = max(diffs) if diffs else None
            v["recorded_status"] = ck["recorded"]["status"]
            ok = ok and diffs != [] and max(diffs) <= TOL and r["status"] == ck["recorded"]["status"]
        v["ruler"] = E.slim(r) if "all" in r else {"status": r["status"]}
    elif ck["kind"] == "DLIB_LIVE":
        live = [i for i in range(pt.shape[0] - 1) if not np.array_equal(pt[i + 1], pt[0])]
        v["live"] = live
        ok = live == list(range(15))
    else:                                                                   # DLIB
        st = [rule(role, pt[k], ep)["status"] for k in range(4)]
        ident = bool(np.array_equal(pt[0], pt[1]))
        v.update(status=st, reassembled_identical=ident, genome_equal=bool(np.array_equal(genomes[0], genomes[1])))
        ok = st == ck["expect"] and ident
    v["pass"] = bool(ok)
    return v


def run_check(ck, cells, adm) -> dict:
    ph, env, seeds, genomes = setup(ck, cells, adm)
    t0 = time.time()
    pt, ep = E.eval_programs(ph, env, seeds, genomes)
    row = {"check_id": ck["check_id"], "kind": ck["kind"], "cell_id": cells[ck["ci"]]["cell_id"], "task": ck["task"],
           "name": ck["name"], "expect": ck["expect"]}
    row.update(judge(ck, pt, ep, genomes))
    row["pt"] = encode_pt(pt); row["pt_sha"] = _sha(pt)
    row["worlds"] = len(seeds); row["world_episodes"] = len(seeds) * len(genomes)
    row["sec"] = round(time.time() - t0, 2)
    row["T"] = env.T(); row["n_sites"] = int(ph["n_sites"])
    return row


def recheck_row(ck, row, cells, adm, replay=False, rule=None) -> list:
    """Problems with one row: recomputed from the plan and the row's per-trial arrays (and, with replay, by
    re-running the dynamics). Row-carried verdict fields are compared, never trusted."""
    ph, env, seeds, genomes = setup(ck, cells, adm)
    try:
        pt = decode_pt(row["pt"])
    except (KeyError, ValueError, TypeError) as e:
        return [f"{ck['check_id']}: per-trial arrays missing or unreadable ({e})"]
    want = [len(genomes), len(seeds), env.trials]
    if list(pt.shape) != want:
        return [f"{ck['check_id']}: per-trial shape {list(pt.shape)} != planned {want}"]
    probs = []
    if _sha(pt) != row.get("pt_sha"):
        probs.append(f"{ck['check_id']}: pt_sha does not bind the per-trial arrays")
    ep = worlds.build(ph, env, seeds)
    v = judge(ck, pt, ep, genomes, rule=rule)
    for k in ("status", "live", "pass", "reassembled_identical", "recorded_status"):
        if k in v and row.get(k) != v[k]:
            probs.append(f"{ck['check_id']}: row says {k}={row.get(k)!r}, recomputed {v[k]!r}")
    if not v["pass"]:
        probs.append(f"{ck['check_id']}: known answer FAILED (recomputed)")
    if replay:
        pt2, _ = E.eval_programs(ph, env, seeds, genomes)
        if not np.array_equal(pt2, pt):
            probs.append(f"{ck['check_id']}: REPLAY MISMATCH: re-executed per-trial arrays differ from the row")
    return probs


REPLAY_KINDS = ("ADM", "NEW", "ALONE")       # single-genome checks: a replay costs one evaluation, not 4 or 25


def replay_sample(ids, k: int) -> list:
    """The k planned single-genome check ids with the smallest sha256(check_id): fixed by the plan, not steerable by
    row edits."""
    ids = [i for i in ids if i.split("|", 1)[0] in REPLAY_KINDS and not i.endswith("|null")]
    # null genomes are excluded: their outputs (.5 everywhere) do not depend on the dynamics, so replaying one checks nothing
    return sorted(ids, key=lambda i: hashlib.sha256(i.encode()).hexdigest())[:k]


def reduce_rows(rows_list, cells, adm, lib, dl, replay_k=0, rule=None) -> dict:
    planned = {ck["check_id"]: ck for ck in plan_checks(cells, adm, lib, dl)}
    rows, problems = {}, []
    for r in rows_list:
        cid = r.get("check_id")
        if cid in rows:
            problems.append(f"DUPLICATE row {cid}")
            continue
        rows[cid] = r
    problems += [f"MISSING row {p}" for p in planned if p not in rows]
    problems += [f"UNPLANNED row {x}" for x in rows if x not in planned]
    replayed = replay_sample(list(planned), replay_k)
    for cid, ck in planned.items():
        if cid in rows:
            problems += recheck_row(ck, rows[cid], cells, adm, replay=cid in replayed, rule=rule)
    by_kind = {}
    for cid, ck in planned.items():
        k = by_kind.setdefault(ck["kind"], {"planned": 0, "rows": 0})
        k["planned"] += 1; k["rows"] += int(cid in rows)
    good = [r for r in rows.values() if r.get("check_id") in planned]
    we = sum(r.get("world_episodes", 0) for r in good)
    secs = sum(r.get("sec", 0) for r in good) or 1.0
    site_ticks = sum(r.get("world_episodes", 0) * r.get("T", 0) * r.get("n_sites", 0) for r in good)
    return {"schema": "argus.c019t040.ka_table.v2", "owner_sha": owner.OWNER_SHA, "planned": len(planned),
            "rows": len(rows), "problems": problems, "replayed": replayed, "by_kind": by_kind,
            "throughput": {"world_episodes": we, "cpu_sec": round(secs, 1), "world_episodes_per_sec": round(we / secs, 3),
                           "site_ticks_per_sec": round(site_ticks / secs)},
            "verdict": "PASS" if not problems else "FAIL"}


def load_rows(out_dir) -> list:
    out = []
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("ka_rows_") and fn.endswith(".jsonl"):
            out += [json.loads(l) for l in open(os.path.join(out_dir, fn)) if l.strip()]
    return out


def cmd_run(cells_sel, out_dir):
    cells, adm, lib, dl = owner.cells(), owner.admission(), owner.library(), owner.dlib()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "ka_rows_%s.jsonl" % "_".join(str(i) for i in cells_sel))
    done = set()
    if os.path.exists(path):
        done = {json.loads(l)["check_id"] for l in open(path) if l.strip()}
    checks = [ck for ck in plan_checks(cells, adm, lib, dl) if ck["ci"] in cells_sel and ck["check_id"] not in done]
    print(f"pid {os.getpid()} cells {cells_sel}: {len(checks)} checks to run, {len(done)} done", flush=True)
    for ck in checks:
        row = run_check(ck, cells, adm)
        with open(path, "a", newline="\n") as f:
            f.write(json.dumps(row) + "\n")
        print(row["check_id"], row.get("status", row.get("live")), "PASS" if row["pass"] else "FAIL", row["sec"], flush=True)
    print("DONE", flush=True)
    return 0


def cmd_reduce(out_dir, out_json, replay_k=4):
    cells, adm, lib, dl = owner.cells(), owner.admission(), owner.library(), owner.dlib()
    rows = load_rows(out_dir)
    res = reduce_rows(rows, cells, adm, lib, dl, replay_k=replay_k)
    by_id = {r["check_id"]: r for r in rows}
    res["table"] = [{k: by_id[ck["check_id"]].get(k) for k in ("check_id", "status", "live", "expect", "pass",
                     "max_abs_diff_vs_owner", "recorded_status", "reassembled_identical", "sec", "pt_sha")}
                    for ck in plan_checks(cells, adm, lib, dl) if ck["check_id"] in by_id]
    with open(out_json, "w", newline="\n") as f:
        json.dump(res, f, indent=1)
    print(res["verdict"], res["by_kind"], "problems", len(res["problems"]))
    for p in res["problems"][:20]:
        print("  ", p)
    return 0 if res["verdict"] == "PASS" else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("run"); a.add_argument("--cells", required=True); a.add_argument("--out", required=True)
    b = sp.add_parser("reduce"); b.add_argument("dir"); b.add_argument("out"); b.add_argument("--replay", type=int, default=4)
    sp.add_parser("plan")
    x = ap.parse_args(argv)
    if x.cmd == "run":
        return cmd_run([int(v) for v in x.cells.split(",")], x.out)
    if x.cmd == "reduce":
        return cmd_reduce(x.dir, x.out, x.replay)
    cells, adm, lib, dl = owner.cells(), owner.admission(), owner.library(), owner.dlib()
    for ck in plan_checks(cells, adm, lib, dl):
        print(ck["check_id"], ck["expect"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
