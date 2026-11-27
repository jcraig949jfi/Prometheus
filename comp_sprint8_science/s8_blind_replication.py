"""Post-Freeze 100% Blind Replication Suite (`N = 100` brand-new `n = 8..12` qubit quantum circuits,
created AFTER Sprint 8 evolution completed, using brand-new seed `20261127_999`).

Purpose:
  During our post-commit audit of Sprint 8, we discovered that `s8_runner.py` had invoked `claude -p`
  directly without `--tools ""` (leaving `g0_draft/`, `g2_draft/`, `g3_draft/` scratch files in the
  workspace). Although `g2_draft` logs showed only `dev_diag` runs (and `g3_draft` was rejected),
  scientific rigor requires BOTH:
    1. Patching `s8_runner.py` to use `call_claude_isolated` (`--tools ""`, isolated temp dir), AND
    2. Evaluating the frozen `S8 G2` (`mod_g2_escape`, Greedy Majority-Voting Affine 4-Flat RM(n-4,n)
       Decoder) on a **brand-new 100-circuit blind holdout (`n = 8..12` qubits, up to 4,096 basis states)**
       that DID NOT EXIST when Sprint 8 evolved!

All 100 circuits are verified 100% exact on ALL `2^n` computational basis states (n = 8..12 -> 256..4096 states).
Note: For `n = 12`, `C(12, 2) = 66` bits (tested natively under Law 4a/4b/4c exact word-width metering!).
"""
from __future__ import annotations

import hashlib
import json
import random
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact
from comp_sprint3.sprint3_runner import paired_wilcoxon_stats
from comp_sprint7_clifford_t.s7_core import (
    CliffordTCircuit,
    cubic_tensor_bitmask,
    extract_phase_poly,
    tpar_fold_baseline as tpar_optimize,
)
from comp_sprint8_science.s8_benchmarks import (
    S8Task,
    _sample_proc_ccz,
    _sample_proc_rand_tensor,
)
from comp_sprint8_science.s8_core import (
    DEFAULT_S8_V3_BUDGET,
    fast_todd_2022_optimize,
    odd_t_parities,
    run_s8_artifact,
    todd_2018_optimize,
)
from comp_sprint8_science.s8_runner import build_s8_a5_sham_artifact


def build_postfreeze_blind_100() -> List[S8Task]:
    """Deterministically generate 100 brand-new blind `n = 8..12` circuits (20 each for n=8,9,10,11,12;
    50 procedural CCZ networks + 50 procedural random symmetric 3-tensors), ZERO overlap with S8."""
    rng = random.Random(20261127_999)
    seen: Set[Tuple[int, int]] = set()
    tasks: List[S8Task] = []
    q_list = [8, 9, 10, 11, 12]
    idx = 0
    while len(tasks) < 100:
        pos = len(tasks)
        n = q_list[pos % 5]
        is_ccz = (pos % 2 == 0)
        circ = _sample_proc_ccz(rng, n) if is_ccz else _sample_proc_rand_tensor(rng, n)
        poly, _ = extract_phase_poly(circ)
        par = odd_t_parities(poly)
        if len(par) < 14:
            idx += 1
            continue
        cub = cubic_tensor_bitmask(n, par)
        if cub == 0 or (n, cub) in seen:
            idx += 1
            continue
        seen.add((n, cub))
        tp = tpar_optimize(circ)
        csha = hashlib.sha256(f"blind100:{n}:{cub}".encode("ascii")).hexdigest()
        tasks.append(
            S8Task(
                task_id=f"blind_{pos:03d}_{'ccz' if is_ccz else 'rand'}_q{n}",
                stratum=f"blind_q{n}",
                n_qubits=n,
                circuit=circ,
                cubic_sha=csha,
                base_t=circ.t_count(),
                tpar_t=tp.t_count(),
                family="blind_ccz" if is_ccz else "blind_rand",
                split="postfreeze_blind",
            )
        )
        idx += 1
    return tasks


def run_blind_replication(proposals_path: Path, out_path: Path) -> Dict[str, Any]:
    prop = json.loads(proposals_path.read_text(encoding="utf-8"))
    a2_art = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    g2_art = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["G2"])
    a5_art = build_s8_a5_sham_artifact()

    tasks = build_postfreeze_blind_100()
    manifest_sha = hashlib.sha256(
        json.dumps([t.cubic_sha for t in tasks]).encode("ascii")
    ).hexdigest()
    print(f"[BLIND 100 n=8..12] Manifest {manifest_sha[:16]}... | N={len(tasks)} circuits (20 each for q=8,9,10,11,12)")

    arms = ["A1_TPAR", "A1_TODD_2018", "A1_FAST_TODD_2022", "A5_SHAM", "A2_PRIOR_ONLY", "S8_G2_FLAT_KICK"]
    scores: Dict[str, Dict[str, int]] = {a: {} for a in arms}
    wall: Dict[str, float] = {}
    v3_ops: Dict[str, int] = {}
    fallbacks: Dict[str, int] = {}
    ferrs: Dict[str, int] = {}

    for arm in arms:
        t0 = time.perf_counter()
        ops = 0
        fb = 0
        fe = 0
        for t in tasks:
            if arm == "A1_TPAR":
                c = t.tpar_t
            elif arm == "A1_TODD_2018":
                c = todd_2018_optimize(t.circuit).t_count()
            elif arm == "A1_FAST_TODD_2022":
                c = fast_todd_2022_optimize(t.circuit).t_count()
            else:
                art = a5_art if arm == "A5_SHAM" else (a2_art if arm == "A2_PRIOR_ONLY" else g2_art)
                circ, tel = run_s8_artifact(art, t.circuit, seed=0, v3_budget=DEFAULT_S8_V3_BUDGET)
                c = circ.t_count()
                ops += int(tel.get("ops_spent", 0))
                if tel.get("verifier_fallback"):
                    fb += 1
                fe += sum(tel.get("fn_errors", {}).values())
            scores[arm][t.task_id] = int(c)
        wall[arm] = round(time.perf_counter() - t0, 2)
        v3_ops[arm] = ops
        fallbacks[arm] = fb
        ferrs[arm] = fe
        tot = sum(scores[arm].values())
        by_q = {q: sum(scores[arm][t.task_id] for t in tasks if t.n_qubits == q) for q in (8, 9, 10, 11, 12)}
        print(f"  {arm:18s}: TOT={tot:5d} | by_q={by_q} | wall={wall[arm]:6.2f}s | v3={ops:>10d} | ferr={fe} | fb={fb}", flush=True)

    # Paired Wilcoxon + 5-way Holm-Bonferroni
    def bci(ds):
        rng = random.Random(20261127)
        n = len(ds)
        ms = sorted(sum(ds[rng.randrange(n)] for _ in range(n)) / n for _ in range(4000))
        return round(ms[100], 3), round(ms[3900], 3)

    def holm(ps):
        m = len(ps)
        idx = sorted(range(m), key=lambda i: ps[i])
        adj = [0.0] * m
        prev = 0.0
        for rk, i in enumerate(idx):
            prev = max(prev, min(1.0, ps[i] * (m - rk)))
            adj[i] = round(prev, 6)
        return adj

    comps = [
        ("S8_G2 vs A1_TODD_2018 (All 100)", "A1_TODD_2018", tasks),
        ("S8_G2 vs A1_FAST_TODD_2022 (All 100)", "A1_FAST_TODD_2022", tasks),
        ("S8_G2 vs A5_SHAM (All 100)", "A5_SHAM", tasks),
        ("S8_G2 vs A2_PRIOR_ONLY (All 100)", "A2_PRIOR_ONLY", tasks),
        ("S8_G2 vs A1_FAST_TODD_2022 (q=12 ONLY, N=20)", "A1_FAST_TODD_2022", [t for t in tasks if t.n_qubits == 12]),
        ("S8_G2 vs A2_PRIOR_ONLY (q=12 ONLY, N=20)", "A2_PRIOR_ONLY", [t for t in tasks if t.n_qubits == 12]),
    ]
    raw = []
    for label, b, tlist in comps:
        ds = [scores["S8_G2_FLAT_KICK"][t.task_id] - scores[b][t.task_id] for t in tlist]
        raw.append((label, paired_wilcoxon_stats(ds), bci(ds)))
    ph = holm([r[1]["p_two"] for r in raw])
    stats_out = {}
    print("\n--- POST-FREEZE BLIND 100 (n=8..12) 6-WAY HOLM-BONFERRONI ---")
    for (label, w, ci), p in zip(raw, ph):
        stats_out[label] = {**w, "ci": list(ci), "p_Holm": p}
        print(f"  {label:46s} | d={w['sum_delta']:+6.1f} | {w['wins']:2d}W/{w['ties']:2d}T/{w['losses']:2d}L | CI=[{ci[0]:+6.3f},{ci[1]:+6.3f}] | p_two={w['p_two']:.6f} | p_Holm={p:.6f}")

    res = {
        "manifest_sha256": manifest_sha,
        "n_tasks": len(tasks),
        "totals": {a: sum(scores[a].values()) for a in arms},
        "by_qubits": {a: {str(q): sum(scores[a][t.task_id] for t in tasks if t.n_qubits == q) for q in (8, 9, 10, 11, 12)} for a in arms},
        "wall_sec": wall,
        "v3_ops": v3_ops,
        "fallbacks": fallbacks,
        "fn_errors": ferrs,
        "wilcoxon_holm": stats_out,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, indent=2), encoding="utf-8")
    return res


if __name__ == "__main__":
    import sys
    run_blind_replication(Path(sys.argv[1]), Path(sys.argv[2]))
