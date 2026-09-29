"""T-004 Archaeon side (ops C-001/E-001): location vs material of executed code in Archaeon's frozen VM, on real specimens.

Archaeon's taint VM (archaeon/lineage/taint_vm.py) counts, per execution, BOTH:
  location   exec_foreign = steps whose pc lies in the neighbour region (pc >= G)       -- WHERE
  material   ex_self / ex_nbr / ex_other = steps whose fetched byte carries label E (the executor's material), N (the neighbour's),
             or other (computed / input / constant) -- labels travel with writes                   -- WHAT
For each birth-producing execution (neighbour window written >= copy_min_frac), the aggregates reveal divergence:
  SELF_CODE_IN_NEIGHBOUR_REGION  ex_self > steps - exec_foreign   (executor material ran from the neighbour region: self-copied code)
  FOREIGN_CODE_IN_OWN_REGION     ex_nbr > exec_foreign            (neighbour material ran from the executor's own region)
Aggregates can only UNDER-detect divergence (a step of each kind can cancel); a positive is a proof of divergence.
Specimens: every copier in archaeon/z80atlas/census/HITS.json x 256 inputs x {zero neighbour, one seeded random neighbour}, plus the
ENVGATE-01 block-15 host panel (inert founders hosting the resident). Also asserts taint result == frozen VM result per execution.
    python archaeon_b6_check.py --out out.json      (run from a checkout root; stdlib + repo modules only)
"""
import hashlib
import json
import sys
import time
from collections import Counter

sys.path.insert(0, ".")
from proteus.foundry.prng import SplitMix64, seed_from          # noqa: E402
from archaeon.z80atlas import vm                               # noqa: E402
from archaeon.z80atlas.grammar import FROZEN as F              # noqa: E402
from archaeon.lineage.taint_vm import execute_taint            # noqa: E402

G = 32; CAP = F["budgets"]["late"]["step_cap"]; MINF = F["copy_min_frac"]
RESIDENT15 = bytes.fromhex("c180094094938d528ef73c4ab400de8e7eb7a99cab37f38650832a8d607194a5")


def classify(tape, nbr, x):
    r = vm.execute(tape, nbr, (x,), CAP, True, -1.0)
    if sum(r["nbr_mask"]) / G < MINF: return None
    rt, wl, ex = execute_taint(tape, nbr, (x,), CAP, True, -1.0)
    assert rt == r, "taint shadow disagrees with the frozen VM"
    steps = r["steps"]; loc_nbr = r["exec_foreign"]; loc_own = steps - loc_nbr
    k = []
    if ex["self"] > loc_own: k.append("SELF_CODE_IN_NEIGHBOUR_REGION")
    if ex["nbr"] > loc_nbr: k.append("FOREIGN_CODE_IN_OWN_REGION")
    return {"child": r["nbr_window"], "steps": steps, "loc_own": loc_own, "loc_nbr": loc_nbr, "mat_self": ex["self"], "mat_nbr": ex["nbr"], "mat_other": ex["other"],
            "divergence": "+".join(k) or "NONE_DETECTED"}


def main():
    out_path = sys.argv[sys.argv.index("--out") + 1]
    t0 = time.time()
    raw = json.load(open("archaeon/z80atlas/census/HITS.json", encoding="utf-8"))["hits"]
    hits = raw["vmcopy32"]                          # HITS.json groups copiers by representation; only vmcopy32 is this 32-byte VM
    rr = SplitMix64(seed_from("t004.nbr", 0)); rnd = bytes(rr.randbelow(256) for _ in range(G))
    c = Counter(); by_class = Counter(); n = 0; ex_rows = []
    for h in hits:
        tape = bytes.fromhex(h["tape"])
        for nb_name, nb in (("zero", bytes(G)), ("random", rnd)):
            for x in range(256):
                n += 1; r = classify(tape, nb, x)
                if r is None: continue
                r.pop("child"); c[r["divergence"]] += 1; by_class[(h["class"], nb_name, r["divergence"])] += 1
                if r["divergence"] != "NONE_DETECTED" and len(ex_rows) < 20: ex_rows.append(dict(r, tape=h["tape"], nbr=nb_name, x=x))
    L = json.load(open("archaeon/envgate/LINEAGES.json", encoding="utf-8"))["lineages"]
    hosts = [bytes.fromhex(r["founder_tape"]) for r in L if r["block"] == 15 and r["arm"] == "U" and r["founder_class"] == "INERT"]
    hp = Counter(); hosting = 0; mat = Counter()
    for hst in hosts:
        for x in range(256):
            r = classify(hst, RESIDENT15, x)
            if r is None: continue
            ch = r.pop("child"); kind = "child=resident" if ch == RESIDENT15 else ("child=host" if ch == hst else "child=other")
            maj = "exec_material_majority=" + ("nbr(resident)" if r["mat_nbr"] > r["mat_self"] + r["mat_other"] else ("self(host)" if r["mat_self"] > r["mat_nbr"] + r["mat_other"] else "mixed"))
            hosting += 1; hp[(kind, r["divergence"])] += 1; mat[(kind, maj, r["divergence"])] += 1
    res = {"task": "T-004 archaeon side", "copier_tapes": len(hits), "executions": n, "births": sum(c.values()), "divergence": dict(c),
           "by_class": {" | ".join(k): v for k, v in by_class.most_common()}, "block15_host_panel": {"hosts": len(hosts), "hosting_births": hosting, "divergence": {" | ".join(k): v for k, v in hp.most_common()},
                                   "by_material": {" | ".join(k): v for k, v in mat.most_common()}},
           "examples": ex_rows, "wall_s": round(time.time() - t0, 1)}
    res["result_sha256"] = hashlib.sha256(json.dumps({k: v for k, v in res.items() if k != "wall_s"}, sort_keys=True).encode()).hexdigest()
    json.dump(res, open(out_path, "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: res[k] for k in ("executions", "births", "divergence", "block15_host_panel", "wall_s", "result_sha256")}))


if __name__ == "__main__":
    main()
