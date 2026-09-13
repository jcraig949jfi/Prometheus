"""S6 phase 1: freeze the eligible endgame FROM S5 ARTIFACTS ONLY (no new producer runs).
(a) per-N table of G's exact decision-state myopia from the S5 run-2 decision rows (both L; these were read in S5);
(b) the endgame universe: every distinct evidence state (fossil set) that G reached in S5 run 2 at some depth, with
    its feasible-target count N, reconstructed from the world fossils and G's per-target probe/score trajectories.
    Written per L; L 9 is written but NOT summarised here (held-out discipline: no S6 quantity is read at L 9 before
    the repair ladder is frozen).
Run from the repository root: python archaeon/docs/h0h5/S6_EXTRACT_ENDGAME_2026-09-13.py"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from archaeon.producer import fossil_inference as FI  # noqa: E402

HERE = Path(__file__).parent


def snapshot(fossils):
    canon = sorted({(b, s) for b, s in fossils})
    return "evs:" + hashlib.sha256(repr(canon).encode()).hexdigest()[:16], canon


def main():
    table = defaultdict(lambda: [0, 0, 0.0])
    universe = {8: {}, 9: {}}
    for L in (8, 9):
        r = json.loads((HERE / f"S5_RESULTS_RUN2_L{L}_SLIM_2026-09-13.json").read_text(encoding="utf-8"))
        for d in r["decision_states"]:
            if d["arm"] != "G":
                continue
            t = table[(L, d["N"])]; t[0] += 1; t[1] += int(d["myopic_exact"]); t[2] += d["delta"]
        for w in r["worlds"]:
            base = [tuple(x) for x in w["fossils"]]
            for row in w["arms"]["G"]:
                probes = [p for p in row["probes"] if p]; scores = row["scores"][:len(probes)]
                for k in range(0, len(probes) + 1):
                    E = base + list(zip(probes[:k], scores[:k]))
                    sid, canon = snapshot(E)
                    if sid in universe[L]:
                        universe[L][sid]["visits"] += 1; continue
                    fs = [FI.Fossil(b, s) for b, s in canon]
                    try:
                        st = FI.infer(fs)
                    except FI.Contradiction:
                        continue
                    universe[L][sid] = {"eid": sid, "L": L, "root": w["state_id"], "depth": k, "fossils": canon, "N": st.feasible_targets, "visits": 1}
        (HERE / f"S6_ENDGAME_UNIVERSE_L{L}_2026-09-13.json").write_text(json.dumps(sorted(universe[L].values(), key=lambda x: (x["N"], x["eid"])), indent=0), encoding="utf-8")
    rows = [{"L": L, "N": N, "decisions": v[0], "myopic": v[1], "rate": v[1] / v[0], "mean_delta": v[2] / v[0]} for (L, N), v in sorted(table.items())]
    (HERE / "S6_MYOPIA_BY_N_FROM_S5_2026-09-13.json").write_text(json.dumps(rows, indent=0), encoding="utf-8")
    print("G decision-state myopia by N (S5 run 2 rows; both L):")
    byN = defaultdict(lambda: [0, 0])
    for x in rows:
        byN[x["N"]][0] += x["decisions"]; byN[x["N"]][1] += x["myopic"]
    for N in sorted(byN):
        d, m = byN[N]; print("  N %2d  decisions %5d  myopic %4d  rate %.3f" % (N, d, m, m / d))
    print("endgame universe (distinct evidence states reached by G):")
    for L in (8, 9):
        u = universe[L]; cnt = defaultdict(int)
        for s in u.values():
            cnt["N<=4" if s["N"] <= 4 else ("5..8" if s["N"] <= 8 else ("9..16" if s["N"] <= 16 else ">16"))] += 1
        print("  L", L, "states", len(u), dict(cnt), "(L 9 counts only; nothing else read)")


if __name__ == "__main__":
    main()
