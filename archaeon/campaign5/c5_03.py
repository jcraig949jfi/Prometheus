"""C5-03 -- REPRESENTATION QUALIFICATION (campaign 5, Phase B). Preregistration: C5-03/DESIGN.md.

    python -m archaeon.campaign5.c5_03 [--dry-run] [--self-test]

Fixtures F1-F8 over representation B (archaeon/campaign5/repb). No fitness anywhere except the
F1 identity check. Disposition REPRESENTATION_QUALIFIED or REPRESENTATION_FAILURE.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry.prng import SplitMix64                                  # noqa: E402
from archaeon.wse.evolve import evaluate, FOUNDRY                            # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5                                     # noqa: E402
from archaeon.campaign5.repb import gen_b, grammar_b                         # noqa: E402
from archaeon.campaign5.repb.evaluate_b import evaluate_b                    # noqa: E402
from archaeon.campaign5.repb.vm_b import static_validity, REP_VERSION        # noqa: E402

ID = "C5-03"
N_POP = 200
POP_SEED = 1
KS = (1, 2, 4)
BINS = ((0, 0), (1, 3), (4, 15), (16, 63), (64, 10 ** 9))
OLD_VM = REPO / "proteus" / "foundry" / "vm.py"


def _lf_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _bin(x: int) -> int:
    for i, (lo, hi) in enumerate(BINS):
        if lo <= x <= hi:
            return i
    return len(BINS) - 1


def _stable(r: dict) -> str:
    """a02 harness fix: the meter's wall_s/cpu_s are volatile (as in C4-01) and are not part of the result."""
    m = {k: v for k, v in r["meter"].items() if k not in ("wall_s", "cpu_s")}
    return json.dumps({**r, "meter": m}, sort_keys=True)


SITE_BINS = ((0, 0), (1, 2), (3, 4), (5, 8), (9, 10 ** 9))


def _sbin(x: int) -> int:
    for i, (lo, hi) in enumerate(SITE_BINS):
        if lo <= x <= hi:
            return i
    return len(SITE_BINS) - 1


def tvd_sites(a: List[int], b: List[int]) -> float:
    ca, cb = Counter(_sbin(x) for x in a), Counter(_sbin(x) for x in b)
    return round(0.5 * sum(abs(ca.get(i, 0) / max(1, len(a)) - cb.get(i, 0) / max(1, len(b))) for i in range(len(SITE_BINS))), 4)


def tvd(a: List[int], b: List[int]) -> float:
    ca, cb = Counter(_bin(x) for x in a), Counter(_bin(x) for x in b)
    return round(0.5 * sum(abs(ca.get(i, 0) / max(1, len(a)) - cb.get(i, 0) / max(1, len(b))) for i in range(len(BINS))), 4)


def f1_identity(parents: list) -> dict:
    ok = {"parent_env": 0, "W0": 0}; mism = []
    eps_w0 = C1.episodes("W0", 16)
    for p in parents:
        m = p["parent"]; c = gen_b.canonicalize(m)
        for env_name, eps in (("parent_env", C1.episodes(C1.PARENT_ENV[p["stratum"]], 16)), ("W0", eps_w0)):
            a = evaluate(m, eps, rng_seed=3); b = evaluate_b(c, eps, rng_seed=3, mode="FAIL")
            good = (a["reward_per_ask"] == b["reward_per_ask"] and a["meter"]["ops"] == b["meter"]["ops"]
                    and all(a["statuses"][k] == b["statuses"][k] for k in ("halt", "yield", "budget")) and b["faults"] == 0 and b["static"]["all_valid"])
            ok[env_name] += good
            if not good:
                mism.append({"organism": p["organism_id"][:12], "env": env_name, "old": a["reward_per_ask"], "new": b["reward_per_ask"], "faults": b["faults"]})
    return {"n": len(parents), "ok": ok, "mismatches": mism[:10], "pass": ok["parent_env"] == len(parents) and ok["W0"] == len(parents)}


def f2_static(pops: dict) -> dict:
    res = {}
    for name, pop in pops.items():
        sv = [static_validity(m) for m in pop]
        res[name] = {"all_valid_share": round(sum(s["all_valid"] for s in sv) / len(sv), 4), "mean_invalid": round(sum(s["invalid"] for s in sv) / len(sv), 3)}
        if name.startswith("injected"):
            k = int(name.split("_k")[1]); res[name]["invalid_eq_k_share"] = round(sum(s["invalid"] == k for s in sv) / len(sv), 4)
    ok = (res["raw"]["all_valid_share"] <= 0.01 and res["valid"]["all_valid_share"] == 1.0
          and all(res["injected_k%d" % k]["all_valid_share"] == 0.0 and res["injected_k%d" % k]["invalid_eq_k_share"] >= 0.99 for k in KS))
    res["pass"] = ok
    return res


def f3_f6_dynamic(pops: dict, eps: list) -> dict:
    evs = {}
    for name in ("raw", "valid", "injected_k2"):
        F = [evaluate_b(m, eps, rng_seed=3, mode="FAIL") for m in pops[name]]
        Z = [evaluate_b(m, eps, rng_seed=3, mode="FIZZLE") for m in pops[name]]
        Z2 = [evaluate_b(m, eps, rng_seed=3, mode="FIZZLE") for m in pops[name]]
        F2 = [evaluate_b(m, eps, rng_seed=3, mode="FAIL") for m in pops[name]]
        evs[name] = {"F": F, "Z": Z, "det": all(_stable(x) == _stable(y) for x, y in zip(Z, Z2)) and all(_stable(x) == _stable(y) for x, y in zip(F, F2))}
    trap = {n: round(sum(r["trapped"] for r in e["F"]) / len(e["F"]), 4) for n, e in evs.items()}
    faults = {n: [r["faults"] for r in e["Z"]] for n, e in evs.items()}
    hist = {n: {"%d-%d" % b: sum(1 for x in faults[n] if _bin(x) == i) for i, b in enumerate(BINS)} for n in faults}
    pair = {"raw_vs_valid": tvd(faults["raw"], faults["valid"]), "valid_vs_injected2": tvd(faults["valid"], faults["injected_k2"]),
            "raw_vs_injected2": tvd(faults["raw"], faults["injected_k2"])}
    sites = {n: [r["fault_sites"] for r in e["Z"]] for n, e in evs.items()}
    site_hist = {n: {"%d-%d" % b: sum(1 for x in sites[n] if _sbin(x) == i) for i, b in enumerate(SITE_BINS)} for n in sites}
    pair_sites = {"raw_vs_valid": tvd_sites(sites["raw"], sites["valid"]), "valid_vs_injected2": tvd_sites(sites["valid"], sites["injected_k2"]),
                  "raw_vs_injected2": tvd_sites(sites["raw"], sites["injected_k2"])}
    # a01 rule (count histograms for all three pairs) and the a02 AMENDED rule (D5-008: the raw-vs-injected2 pair on DISTINCT SITES)
    pass_a01 = trap["raw"] >= 0.95 and trap["valid"] <= 0.10 and trap["injected_k2"] >= 0.50 and all(v >= 0.5 for v in pair.values())
    pass_a02 = (trap["raw"] >= 0.95 and trap["valid"] <= 0.10 and trap["injected_k2"] >= 0.50 and pair["raw_vs_valid"] >= 0.5
                and pair["valid_vs_injected2"] >= 0.5 and pair_sites["raw_vs_injected2"] >= 0.5)
    f3 = {"trap_share": trap, "fault_hist": hist, "mean_faults": {n: round(sum(f) / len(f), 2) for n, f in faults.items()}, "tvd": pair,
          "site_hist": site_hist, "tvd_sites": pair_sites, "pass_a01_rule": pass_a01, "pass_a02_rule": pass_a02, "pass": pass_a02}
    coh = {n: sum(1 for f, z in zip(e["F"], e["Z"]) if f["trapped"] == (z["faults"] > 0)) / len(e["F"]) for n, e in evs.items()}
    inj_answer_fizzle = sum(1 for z in evs["injected_k2"]["Z"] if z["answered_share"] > 0) / len(evs["injected_k2"]["Z"])
    trapped_answer = sum(1 for f in evs["injected_k2"]["F"] if f["trapped"] and f["answered_share"] > 0)
    f4 = {"coherence": {n: round(v, 4) for n, v in coh.items()}, "injected2_answer_under_fizzle": round(inj_answer_fizzle, 4), "trapped_that_answered": trapped_answer,
          "pass": all(v == 1.0 for v in coh.values()) and inj_answer_fizzle >= 0.05 and trapped_answer == 0}
    # F5 over injected k=1,2,4 with code_writable False
    f5 = {}
    for k in KS:
        rows = [(m, evaluate_b(m, eps, rng_seed=3, mode="FIZZLE")) for m in pops["injected_k%d" % k]]
        nw = [z for m, z in rows if not m["code_writable"]]; w = [z for m, z in rows if m["code_writable"]]
        f5["k%d" % k] = {"not_writable_n": len(nw), "sites_le_k_share": round(sum(z["fault_sites"] <= k for z in nw) / max(1, len(nw)), 4),
                         "writable_n": len(w), "writable_sites_gt_k_share": round(sum(z["fault_sites"] > k for z in w) / max(1, len(w)), 4)}
    f5["pass"] = all(f5["k%d" % k]["sites_le_k_share"] == 1.0 for k in KS)
    f6 = {"deterministic": {n: e["det"] for n, e in evs.items()}, "pass": all(e["det"] for e in evs.values())}
    return {"F3": f3, "F4": f4, "F5": f5, "F6": f6}


def f7_undefined(pops: dict, eps: list) -> dict:
    n = 0
    for m in pops["raw"]:
        if evaluate(m, eps, rng_seed=3)["answered_share"] > 0 and evaluate_b(m, eps, rng_seed=3, mode="FAIL")["trapped"]:
            n += 1
    return {"raw_answer_old_but_trap_new": n, "n": len(pops["raw"]), "pass": n > 0}


def f8_grammar(pops: dict) -> dict:
    rng = SplitMix64(5); cross = Counter(); total = Counter()
    for i in range(1200):
        ch, rec = grammar_b.mutate_b(pops["valid"][i % len(pops["valid"])], rng)
        total[rec["operator"]] += 1; cross[rec["operator"]] += 0 if static_validity(ch)["all_valid"] else 1
    return {"children": 1200, "by_operator": {k: {"n": total[k], "crossed": cross[k], "rate": round(cross[k] / total[k], 4)} for k in sorted(total)},
            "overall_rate": round(sum(cross.values()) / 1200, 4), "grammar_b_hash": grammar_b.GRAMMAR_B_HASH}


def controls(eps: list) -> dict:
    prog = {"schema_version": "proteus.player_manifest.v0", "n_regs": 4, "tape_words": 32, "code_writable": False, "persist": "none", "tick_budget": 64, "out_cap": 4,
            "genome": [3, 0, 7, 0, 99, 0, 0, 0, 23, 0, 1, 0, 1, 0, 0, 0]}      # LDC r0=7; <invalid opcode 99>; OUT r0 ch r1; HALT
    F = evaluate_b(prog, eps, rng_seed=3, mode="FAIL"); Z = evaluate_b(prog, eps, rng_seed=3, mode="FIZZLE")
    pos = {"fail_trapped": F["trapped"], "fail_trap_at": F["trap_at"], "fail_reward": F["reward_per_ask"], "fizzle_faults": Z["faults"], "fizzle_sites": Z["fault_sites"],
           "fizzle_out_writes": Z["meter"]["out_writes"], "fizzle_answered": Z["answered_share"]}
    pos["pass"] = bool(F["trapped"] and F["trap_at"] == {"episode": 0, "tick": 0} and F["reward_per_ask"] == 0.0 and Z["faults"] >= 1 and Z["fault_sites"] == 1 and Z["meter"]["out_writes"] > 0)
    valid = gen_b.population("valid", FOUNDRY, 9, 20)
    cheat = {"relabelled_valid_invalid_eq_1_share": round(sum(static_validity(m)["invalid"] == 1 for m in valid) / len(valid), 4)}
    cheat["pass"] = cheat["relabelled_valid_invalid_eq_1_share"] < 0.99
    return {"positive": pos, "cheat": cheat, "pass": pos["pass"] and cheat["pass"]}


def run_all(parents: list) -> dict:
    t0 = time.time()
    eps4 = C1.episodes("W0", 16)[:4]
    pops = {"raw": gen_b.population("raw", FOUNDRY, POP_SEED, N_POP), "valid": gen_b.population("valid", FOUNDRY, POP_SEED, N_POP)}
    for k in KS:
        pops["injected_k%d" % k] = gen_b.population("injected", FOUNDRY, POP_SEED, N_POP, k=k)
    out = {"representation": REP_VERSION, "old_vm_digest_before": _lf_digest(OLD_VM), "controls": controls(eps4), "F1": f1_identity(parents), "F2": f2_static(pops)}
    out.update(f3_f6_dynamic(pops, eps4))
    out["F7"] = f7_undefined(pops, eps4)
    out["F8"] = f8_grammar(pops)
    out["old_vm_digest_after"] = _lf_digest(OLD_VM)
    fx = ["F1", "F2", "F3", "F4", "F5", "F6"]
    out["fixtures_pass"] = {f: out[f]["pass"] for f in fx} | {"F7": out["F7"]["pass"], "controls": out["controls"]["pass"]}
    out["qualified"] = all(out[f]["pass"] for f in fx) and out["F7"]["pass"] and out["controls"]["pass"] and out["old_vm_digest_before"] == out["old_vm_digest_after"]
    out["disposition"] = "REPRESENTATION_QUALIFIED" if out["qualified"] else "REPRESENTATION_FAILURE"
    out["wall_s"] = round(time.time() - t0, 1)
    return out


def self_test() -> int:
    parents = C1.parents_from_population()[:5]
    eps4 = C1.episodes("W0", 16)[:4]
    c = controls(eps4); f1 = f1_identity(parents)
    print(json.dumps({"controls": c, "F1": f1}, indent=1))
    return 0 if c["pass"] and f1["pass"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5-03")
    if a.self_test:
        return self_test()
    from archaeon.campaign5.c5base import harness                            # noqa: PLC0415

    class Qualification(harness()):
        ID = "C5-03"
        TITLE = "representation qualification (narrow encoding, FAIL/FIZZLE, fixtures without fitness)"
        PARENTS = ["C4-01", "C4-03"]
        ARM_FIELD = "arm"
        METRICS = ("pass", "trap_share", "tvd_min")

    X = Qualification(dry_run=a.dry_run, procs=1)
    design = (C5 / "C5-03" / "DESIGN.md").read_text(encoding="utf-8")
    parents = C1.parents_from_population()
    X.seal({
        "question": "Is representation B (narrow in-table encoding, FAIL/FIZZLE) a qualified instrument: does it preserve the old programs' meaning, and do "
                    "raw, generator-valid and controlled-invalid populations separate WITHOUT fitness, with countable recovery?",
        "parent_evidence": "C4-01: total interpreter, 932/932 out-of-table words reinterpreted; C4-03: REPRESENTATION_BLOCKED, proxy only.",
        "why_this_slot": "Phase B cannot start without a representation in which a local failure exists.",
        "assay_capability_requirement": "positive control (hand-made fault program) and cheat control (relabelled valid population) as in DESIGN.md",
        "positive_control": "controls arm: pass >= 1.0",
        "reachability_estimate": {"note": "not a reach experiment"},
        "arms": ["controls", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"],
        "crn_policy": "fixed population seed 1, evaluation seed 3, four W0 episodes",
        "budget": {"populations": ["raw", "valid"] + ["injected_k%d" % k for k in KS], "n_per_population": N_POP, "parents": len(parents), "grammar_children": 1200},
        "primary_observable": "fixtures F1-F6 pass, F7 > 0 (F8 recorded); disposition REPRESENTATION_QUALIFIED / REPRESENTATION_FAILURE",
        "claim_ceiling": "an instrument qualification; nothing about evolution, discovery or robustness",
        "falsification_condition": "any of F1-F6 failing its fixed threshold, or F7 = 0",
        "kill_condition": "control failure -> INSTRUMENT_INVALID; old VM digest changed -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["REPRESENTATION_FAILURE", "INSTRUMENT_INVALID"],
        "expected_machine_telemetry": ["static validity counts", "fault counts and sites", "trap positions", "grammar crossing by operator"],
        "machine_changes_exercised": ["PlayerB", "evaluate_b", "gen_b", "grammar_b"],
        "replacement_condition": "none: a REPRESENTATION_FAILURE is a result (directive)",
        "ancestry": "original (Phase B, slot 1)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 1, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "F3", "control": "F2", "metric": "pass", "min_effect": 0.0}},
    })
    X.decision("D5-008: a02 AMENDMENT (post-hoc, a01 preserved): F3 raw-vs-injected2 measured on distinct fault SITES; F6 compares results with volatile timings stripped; failing fixtures recorded FALSIFIED")
    X.decision("D5-007: representation B boundary = encoding only (opcode word < 25, read register fields < n_regs); addresses and offsets stay modulo tape; FAIL = whole evaluation")
    X.open("cmp5-c5-03")
    wid = X.world("representation-qualification", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    res = run_all(parents)
    grouped = [{"arm": "controls", "pass": float(res["controls"]["pass"]), "n": 1}]
    for f in ("F1", "F2", "F3", "F4", "F5", "F6", "F7"):
        row = {"arm": f, "pass": float(res[f]["pass"]), "n": 1}
        if f == "F3":
            row["trap_share"] = res["F3"]["trap_share"]["raw"]; row["tvd_min"] = min(res["F3"]["tvd"].values())
        grouped.append(row)
        X.record(wid, row, {"arm": f}, {k: v for k, v in res[f].items()}, "SURVIVED" if res[f]["pass"] else "FALSIFIED", key_parts=(f,))
    X.record(wid, {"arm": "F8"}, {"arm": "F8"}, res["F8"], "SURVIVED", key_parts=("F8",))
    X.att.write("QUALIFICATION.json", res)
    X.publish(wid, "qualification", "cmp5.c503_qualification.v1", res, {"info_kind": "artifact", "label": "C5-03 representation B qualification"})
    out = X.close(grouped, addendum={"disposition": res["disposition"], "fixtures": json.dumps(res["fixtures_pass"])})
    print(json.dumps({"disposition": res["disposition"], "fixtures": res["fixtures_pass"], "F3": res["F3"], "F7": res["F7"], "F8_overall": res["F8"]["overall_rate"], "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
