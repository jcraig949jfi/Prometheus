"""Terminal disposition scorer for Campaign 2 (CRIUS_C2_TERMINAL_PREREG.md s V-VI).

Reads the rung C and rung D receipts (gate_<rung>_v2/GATE.json, search_<rung>_*/
candidates.jsonl, qualify_qual/SUMMARY.json) and evaluates the disposition
rule mechanically, clause by clause:

  a. gate v2 TRUE for the rung
  b. R4 / R5 scored against their frozen text
  c. a selectable PARTIAL: an ancestry step of a qualified top whose edit
     newly executes a recorder or invoker op, BEFORE that lineage ever invokes
     an own-made block, re-evaluated parent-vs-child on the same sealed streams
     (child beats parent on the mean and on >= 2 of 3) -- per seed of each arm
  d. reproducible ACC > FRESH on the three sealed qualification streams
     (reuse_gain > 5 pct of FRESH cost and ACC solved >= FRESH solved, 3/3)
  e. ARTIFACT_TRANSPLANT cheaper than CODE_ONLY and ablation removes it
  f. content test: deferred to exploit_probe on every candidate that passes d
  g. incremental acquisition: the largest single edit in the ancestry of a
     candidate that passes d is <= 8 instructions

Nothing here lowers a floor: the numbers are the ones in the receipts; the
verdict is CONTINUE only if every clause holds, else CLOSED.

CLI: python -m crius.c2_terminal [--rungs c2c c2d] [--out crius/runs/C2_TERMINAL_DISPOSITION.json]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re

from . import receipts
from .c2_path import OPS, _has, _trace

RUNS = os.path.join("crius", "runs")
TYPED = tuple(o for ops in OPS.values() for o in ops)


def _load_cands(run_dir):
    cands = {}
    with receipts.open_text(os.path.join(run_dir, "candidates.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            cands[r["candidate_id"]] = r
    return cands


def _ancestry(cands, cid):
    chain = []
    seen = set()
    while cid and cid in cands and cid not in seen:
        seen.add(cid)
        chain.append(cands[cid])
        cid = cands[cid]["parent_id"]
    chain.reverse()
    return chain


def _edit_size(mod: str) -> int:
    """instructions one modification string can account for: splice@i<-donor[a:b] = b-a, duplicate@a+ln->i = ln, others 1 each"""
    n = 0
    for a, b in re.findall(r"splice@\d+<-donor\[(\d+):(\d+)\]", mod):
        n += int(b) - int(a)
    for ln in re.findall(r"duplicate@\d+\+(\d+)->", mod):
        n += int(ln)
    n += len(re.findall(r"(?:^|\+)(?:replace|arg|const|insert|delete|swap)@", mod))
    return n


def _takeovers(run_dir):
    p = os.path.join(run_dir, "takeovers.jsonl")
    if not os.path.exists(p):
        return {}
    out = {}
    with open(p, "r", encoding="ascii") as f:
        for line in f:
            r = json.loads(line)
            out[r["child"]] = r
    return out


def _qual_rows(run_dir):
    p = os.path.join(run_dir, "qualify_qual", "SUMMARY.json")
    if not os.path.exists(p):
        return {}
    by = {}
    for r in receipts.read_json(p)["rows"]:
        if r["role"] != "baseline":
            by.setdefault(r["label"], []).append(r)
    return by


def _repro(rows):
    """clause d: reuse_gain > 5 pct of FRESH charged cost and ACC solved >= FRESH solved on all three streams"""
    return len(rows) >= 3 and all(r["reuse_gain_total"] > 0.05 * 50 * r["mean_cost"]["FRESH"] and r["successes"]["ACCUMULATED"] >= r["successes"]["FRESH"] for r in rows)


def _causal(rows):
    """clause e: ARTIFACT_TRANSPLANT mean cost < 0.95 x CODE_ONLY and ABLATION_ALL within 5 pct of CODE_ONLY, all streams"""
    ok = True
    for r in rows:
        c = r["causal_mean_cost"]
        ok = ok and c["ARTIFACT_TRANSPLANT"] < 0.95 * c["CODE_ONLY"] and abs(c["ARTIFACT_ABLATION_ALL"] - c["CODE_ONLY"]) <= 0.05 * c["CODE_ONLY"]
    return ok


_EVAL_CACHE = {}


def _paired_fitness(cfg, program, seeds):
    """mean campaign fitness of a program under ACCUMULATED on the sealed qualification streams (same tasks for every program)"""
    from . import evaluate, streams, vm
    from .player import VMPlayer
    key = json.dumps(program)
    if key not in _EVAL_CACHE:
        vm.set_substrate(cfg.get("substrate", {}))
        out = []
        for s in seeds:
            life = evaluate.run_lifetime(VMPlayer(vm.program_from_json(program)), streams.lifetime(cfg, s, "qual"), cfg, "ACCUMULATED", seed=s)
            out.append((life["metrics"]["fitness"], life["metrics"]["successes"]))
        _EVAL_CACHE[key] = out
    return _EVAL_CACHE[key]


def _partial_steps(cands, takeovers, cid, cfg, seeds, cap=10):
    """clause c: every ancestry step whose edit newly executes a recorder or invoker op, before the lineage's first
    own invocation, RE-EVALUATED parent-vs-child on the same sealed streams (the search's own fitness values are not
    paired: a parent carries fitness from earlier paired streams, and the takeover check compares the child with the
    displaced member, ties counting as takeover). A step is SELECTABLE if the child beats the parent on the mean and
    on >= 2 of the 3 streams. Returns the list of steps (capped) and whether any was selectable."""
    chain = _ancestry(cands, cid)
    steps = []
    for i in range(1, len(chain)):
        par, ch = chain[i - 1], chain[i]
        tp, tc = _trace(par), _trace(ch)
        if sum(p["artifacts_invoked_total"] for p in ch["per_seed"].values()) > 0 and _has(tc, OPS["recorder"]):
            break            # complete machinery from here on; only steps before it can be a selectable partial
        newly = [n for n in ("recorder", "invoker") if _has(tc, OPS[n]) and not _has(tp, OPS[n])]
        if not newly:
            continue
        if len(steps) >= cap:
            steps.append({"capped": True})
            break
        ep, ec = _paired_fitness(cfg, par["program"], seeds), _paired_fitness(cfg, ch["program"], seeds)
        fp, fc = [x[0] for x in ep], [x[0] for x in ec]
        d = [round(c - p, 4) for p, c in zip(fp, fc)]
        ds = [c[1] - p[1] for p, c in zip(ep, ec)]
        t = takeovers.get(ch["candidate_id"], {})
        steps.append({"iteration": ch["iteration"], "candidate": ch["candidate_id"], "ops": newly, "paired_delta": d, "solved_delta": ds,
                      "selectable": sum(fc) > sum(fp) and sum(1 for x in d if x > 0) >= 2, "takeover": t.get("outcome")})
    return steps, any(s.get("selectable") for s in steps)


def score_run(run_dir, cfg=None):
    cands = _load_cands(run_dir)
    takeovers = _takeovers(run_dir)
    best = receipts.read_json(os.path.join(run_dir, "best.json"))
    meta = receipts.read_json(os.path.join(run_dir, "RUN_META.json"))
    cfg = cfg or receipts.load_config(meta["config_path"])
    seeds = cfg["seeds"]["qualification"]
    by = _qual_rows(run_dir)
    out = {"run": best["run_id"], "arm": best["arm"], "qualified": len(by), "repro_positive": [], "causal_ok": [], "partial_steps": {}, "partial_selectable": {}, "max_edit": {}}
    for label, rows in by.items():
        if _repro(rows):
            out["repro_positive"].append(label)
            if _causal(rows):
                out["causal_ok"].append(label)
    # partial-step and edit-size checks on the final-population tops (top1..3) and the best-ever candidate
    hashes = {label.split("_", 1)[1]: label for label in by if label.startswith(("top", "bestever"))}
    id_by_hash = {r["candidate_id"][:16]: r["candidate_id"] for r in cands.values()}
    for h, label in hashes.items():
        cid = id_by_hash.get(h)
        if not cid:
            continue
        out["partial_steps"][label], out["partial_selectable"][label] = _partial_steps(cands, takeovers, cid, cfg, seeds)
        out["max_edit"][label] = max([_edit_size(r["modification"]) for r in _ancestry(cands, cid)[1:]] or [0])
    # invocation census: candidates that invoked an own-made block at all
    out["own_invocation_candidates"] = sum(1 for r in cands.values() if _has(_trace(r), OPS["recorder"]) and sum(p["artifacts_invoked_total"] for p in r["per_seed"].values()) > 0)
    out["candidates"] = len(cands)
    return out


def score_rung(rung):
    g = os.path.join(RUNS, "gate_%s_v2" % rung, "GATE.json")
    gate = receipts.read_json(g) if os.path.exists(g) else None
    runs = [score_run(d) for d in sorted(glob.glob(os.path.join(RUNS, "search_%s_*" % rung))) if os.path.exists(os.path.join(d, "best.json"))]
    return {"rung": rung, "gate_v2_all_pass": bool(gate and gate["all_pass"]), "gate_version": gate and gate.get("gate_version"),
            "witnesses": gate and {k: gate["witnesses"][k]["pass"] for k in "ABCDEFGH"}, "runs": runs}


def disposition(rungs):
    R = {r["rung"]: r for r in rungs}
    c, d = R.get("c2c"), R.get("c2d")
    verdict = {"a_gate_C": bool(c and c["gate_v2_all_pass"])}
    # R4: rung C seeded/recombination arms assemble nothing reproducible
    c_hits = [(run["run"], run["repro_positive"]) for run in (c["runs"] if c else []) if run["arm"] in ("seeded", "recombination") and run["repro_positive"]]
    verdict["R4_survives"] = not c_hits
    verdict["R4_hits"] = c_hits
    # R5: rung D recombination arm produces >= 1 reproducible lineage with competence kept
    d_hits = [(run["run"], run["repro_positive"]) for run in (d["runs"] if d else []) if run["arm"] == "recombination" and run["repro_positive"]]
    verdict["R5_survives"] = bool(d_hits)
    verdict["R5_hits"] = d_hits
    # c: selectable partial in >= 2 of 3 seeds of some arm (any rung searched this round)
    per_arm = {}
    for rung in (c, d):
        for run in (rung["runs"] if rung else []):
            has = any(run["partial_selectable"].values())
            per_arm.setdefault((rung["rung"], run["arm"]), []).append(has)
    verdict["c_partial_seeds_by_arm"] = {"%s/%s" % k: sum(v) for k, v in per_arm.items()}
    verdict["c_partial_ok"] = any(sum(v) >= 2 for v in per_arm.values())
    # d/e: any reproducible candidate that is also causal
    all_runs = [run for rung in (c, d) if rung for run in rung["runs"]]
    verdict["d_repro_candidates"] = sum(len(run["repro_positive"]) for run in all_runs)
    verdict["e_causal_candidates"] = sum(len(run["causal_ok"]) for run in all_runs)
    # g: incremental acquisition for causal candidates
    big = []
    for run in all_runs:
        for label in run["causal_ok"]:
            if run["max_edit"].get(label, 0) > 8:
                big.append((run["run"], label, run["max_edit"][label]))
    verdict["g_single_large_edit"] = big
    verdict["f_content_test"] = "REQUIRED for %d candidate(s); run exploit_probe" % verdict["e_causal_candidates"] if verdict["e_causal_candidates"] else "not applicable (no candidate reached e)"
    cont = verdict["a_gate_C"] and verdict["R4_survives"] and verdict["R5_survives"] and verdict["c_partial_ok"] and verdict["e_causal_candidates"] > 0 and not big
    verdict["disposition"] = "UNPARK -> CONTINUE (pending content test f)" if cont else "CLOSED -- ACCESSIBILITY FRONTIER MAPPED"
    return verdict


def render(rungs, verdict):
    L = []
    P = L.append
    P("C2 TERMINAL DISPOSITION (mechanical; CRIUS_C2_TERMINAL_PREREG s V-VI)")
    for r in rungs:
        P("RUNG %s  gate v%s all_pass=%s  %s" % (r["rung"].upper(), r["gate_version"], r["gate_v2_all_pass"],
          " ".join("%s=%s" % (k, "P" if v else "F") for k, v in (r["witnesses"] or {}).items())))
        P("  run                           cands ownInv qual repro causal | recorder/invoker steps re-evaluated paired: n / selectable | max edit")
        for run in r["runs"]:
            n_steps = sum(len([s for s in v if "ops" in s]) for v in run["partial_steps"].values())
            n_sel = sum(1 for v in run["partial_steps"].values() for s in v if s.get("selectable"))
            me = ",".join("%s=%d" % (k.split("_")[0], v) for k, v in run["max_edit"].items())
            P("  %-29s %5d %6d %4d %5d %6d | %3d / %-3d | %s" % (run["run"][:29], run["candidates"], run["own_invocation_candidates"], run["qualified"],
                                                        len(run["repro_positive"]), len(run["causal_ok"]), n_steps, n_sel, me))
            for label, v in run["partial_steps"].items():
                for st in v:
                    if "ops" in st:
                        P("      %-24s it%3d %-16s paired fitness delta %s solved delta %s%s" % (label[:24], st["iteration"], "+".join(st["ops"]), st["paired_delta"], st["solved_delta"], "  SELECTABLE" if st["selectable"] else ""))
    P("VERDICT")
    for k, v in verdict.items():
        P("  %-24s %s" % (k, json.dumps(v)))
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", nargs="*", default=["c2c", "c2d"])
    ap.add_argument("--out", default=os.path.join(RUNS, "C2_TERMINAL_DISPOSITION.json"))
    args = ap.parse_args(argv)
    rungs = [score_rung(r) for r in args.rungs]
    verdict = disposition(rungs)
    text = render(rungs, verdict)
    receipts.write_json(args.out, {"rungs": rungs, "verdict": verdict})
    with open(args.out[:-5] + ".md", "w", encoding="ascii", newline="\n") as f:
        f.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
