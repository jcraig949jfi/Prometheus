"""AC-01R / AC-01D frozen corpus construction (deterministic, hashed).  No representation is fitted here.

Universe: full T_7 = {cycle, swap01, collapse01} acting on maps [7] -> [7] (universe/monoid.py, generators from uc1_seed.pch_generators).
Targets: the 63 restricted-growth maps of rank 2.  Corpus states: rank >= 3.

AC-01D rows: every reachable (state, target) pair (D >= 0).  Per row the chart gives: exact D; for each of the three
actions the successor id, successor D (UNREACH allowed) and shortest-path membership (D[succ] + 1 == D).
AC-01R rows: every (state, target) pair of the corpus with the reachability label (kernel refinement, verified by BFS).
Kernel id is stored in a SEPARATE audit array and is never part of the primary input.

Masks (deterministic):
  state role   sha256("AC01|T7|state|<7 digits>")[:12]/16^12 -> train < 0.6 <= val < 0.8 <= test
  target role  sha256("AC01|target|<7 digits>") ordering; the first 13 of 63 are held out (universe-independent key)
  pair role    splitmix64(state*64 + target) -> fit (80%) / held (20%), applied within train-state x train-target
Evaluation sets: HELD_STATES = test states x train targets; HELD_TARGETS = train states x test targets;
HELD_PAIRS = train x train pairs with pair role 'held'; HELD_BOTH = test states x test targets; VAL = val states x train targets.

Storage denominator (M1): lzma of the canonical sparse COO of the AC-01D chart, (state int32, target uint8, D uint8) in
row-major order, and separately of the action table (succ D int8 x3, on-shortest-path bits).
"""
from __future__ import annotations
import hashlib, json, lzma, os, zlib
import numpy as np
from ..universe.monoid import build_monoid, kernel_compatible, map_str
from ..universe.uc1_seed import pch_generators
from ..universe.directed_rewriting import sha256_arrays

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = 7; HELD_TARGETS = 13


def _bucket(key: str) -> float:
    return int(hashlib.sha256(key.encode()).hexdigest()[:12], 16) / 16 ** 12


def splitmix(x: np.ndarray) -> np.ndarray:
    z = (x.astype(np.uint64) + np.uint64(0x9E3779B97F4A7C15))
    z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return z ^ (z >> np.uint64(31))


def build():
    U = build_monoid("PCH", N, pch_generators(N), target_rank=2)
    NS = U["NS"]; F = U["F"]; D = U["D"]; targets = np.array(U["targets"])
    # successor table (NS, 3): nominal edge order is generator-major, state-minor
    succ = U["dst"].reshape(3, NS).T.copy()
    corpus = U["rank"] >= 3
    # masks
    words = ["".join(map(str, row)) for row in F.tolist()]
    sb = np.array([_bucket(f"AC01|T7|state|{w}") for w in words])
    state_role = np.where(sb < 0.6, 0, np.where(sb < 0.8, 1, 2)).astype(np.int8)  # 0 train 1 val 2 test
    tw = [words[t] for t in targets.tolist()]
    order = sorted(range(len(tw)), key=lambda j: _bucket(f"AC01|target|{tw[j]}"))
    target_role = np.zeros(len(tw), dtype=np.int8); target_role[order[:HELD_TARGETS]] = 1  # 1 = held-out target
    sidx = np.arange(NS, dtype=np.int64)
    pair_role = np.zeros((NS, len(tw)), dtype=np.int8)  # 1 = held pair; computed in row chunks to bound peak memory (values identical)
    tj_u = np.arange(len(tw))[None, :].astype(np.uint64)
    for a in range(0, NS, 65536):
        b = min(NS, a + 65536)
        pair_role[a:b] = ((splitmix(sidx[a:b, None].astype(np.uint64) * np.uint64(64) + tj_u) % np.uint64(100)) >= np.uint64(80)).astype(np.int8)
    reach = D >= 0
    live = reach & corpus[:, None]
    # kernel audit array and reachability label check
    kc = np.stack([kernel_compatible(U, sidx, int(t)) for t in targets], axis=1)
    assert np.array_equal(kc & corpus[:, None], live), "kernel theorem violated"
    # evaluation-set sizes (AC-01D = reachable pairs; AC-01R = all corpus pairs)
    tr_s, va_s, te_s = state_role == 0, state_role == 1, state_role == 2
    tr_t, te_t = target_role == 0, target_role == 1
    def count(mask_s, mask_t, pair=None, base=live):
        m = base & mask_s[:, None] & mask_t[None, :]
        if pair is not None: m &= (pair_role == pair)
        return int(m.sum())
    sets = {"FIT": {"D": count(tr_s, tr_t, 0), "R": count(tr_s, tr_t, 0, corpus[:, None] & np.ones_like(reach))},
            "HELD_PAIRS": {"D": count(tr_s, tr_t, 1), "R": count(tr_s, tr_t, 1, corpus[:, None] & np.ones_like(reach))},
            "VAL": {"D": count(va_s, tr_t), "R": count(va_s, tr_t, None, corpus[:, None] & np.ones_like(reach))},
            "HELD_STATES": {"D": count(te_s, tr_t), "R": count(te_s, tr_t, None, corpus[:, None] & np.ones_like(reach))},
            "HELD_TARGETS": {"D": count(tr_s, te_t), "R": count(tr_s, te_t, None, corpus[:, None] & np.ones_like(reach))},
            "HELD_BOTH": {"D": count(te_s, te_t), "R": count(te_s, te_t, None, corpus[:, None] & np.ones_like(reach))}}
    # storage denominators
    si, tj = np.nonzero(live)
    coo = si.astype(np.int32).tobytes() + tj.astype(np.uint8).tobytes() + D[live].astype(np.uint8).tobytes()
    sd = np.stack([D[succ[si, r], tj] for r in range(3)], axis=1).astype(np.int8)
    onsp = np.stack([(D[succ[si, r], tj] + 1 == D[si, tj]) & (D[succ[si, r], tj] >= 0) for r in range(3)], axis=1)
    act = sd.tobytes() + np.packbits(onsp, axis=1).tobytes()
    def sizes(b): return {"raw_bytes": len(b), "zlib9_bytes": len(zlib.compress(b, 9)), "lzma_bytes": len(lzma.compress(b, preset=6))}
    manifest = {
        "universe": "T_7 {cycle, swap01, collapse01}; generators " + json.dumps(U["gens"]), "states": NS, "corpus_states_rank_ge_3": int(corpus.sum()),
        "targets": tw, "held_out_targets": [tw[j] for j in order[:HELD_TARGETS]],
        "state_roles": {"train": int(tr_s.sum()), "val": int(va_s.sum()), "test": int(te_s.sum())},
        "AC01D_reachable_pairs": int(live.sum()), "AC01R_pairs": int(corpus.sum()) * len(tw), "AC01R_positive_fraction": float(live.sum() / (corpus.sum() * len(tw))),
        "evaluation_sets": sets,
        "hashes": {"F": sha256_arrays(F), "D": sha256_arrays(D), "succ": sha256_arrays(succ), "targets": sha256_arrays(targets), "state_role": sha256_arrays(state_role),
                   "target_role": sha256_arrays(target_role), "pair_role": sha256_arrays(pair_role), "kernel_audit": sha256_arrays(U["kmask"]),
                   "coo_D": hashlib.sha256(coo).hexdigest(), "coo_actions": hashlib.sha256(act).hexdigest()},
        "storage_denominators": {"AC01D_distance_chart_COO": sizes(coo), "AC01D_action_table": sizes(act),
                                 "note": "M1 denominator = lzma_bytes of the distance chart COO (primary) and of the action table (secondary); raw bytes reported beside"},
        "shortest_path_action_fraction": float(onsp.any(axis=1).mean()), "mean_on_shortest_path_actions_per_row": float(onsp.sum(axis=1).mean()),
        "distance_histogram": {str(k): int(v) for k, v in zip(*np.unique(D[live], return_counts=True))},
    }
    return U, {"succ": succ, "state_role": state_role, "target_role": target_role, "pair_role": pair_role, "live": live, "corpus": corpus}, manifest


def save(U, M, manifest):
    out = os.path.join(HERE, "results", "ac01d"); os.makedirs(out, exist_ok=True)
    data = os.path.join(HERE, "data"); os.makedirs(data, exist_ok=True)
    np.savez(os.path.join(data, "AC01_T7_corpus.npz"), F=U["F"], D=U["D"], succ=M["succ"], targets=np.array(U["targets"]), state_role=M["state_role"],
             target_role=M["target_role"], pair_role=M["pair_role"], kernel_audit=U["kmask"], rank=U["rank"], C=U["C"])
    with open(os.path.join(out, "CORPUS_MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    return os.path.join(out, "CORPUS_MANIFEST.json")


if __name__ == "__main__":
    U, M, man = build(); p = save(U, M, man)
    print(json.dumps({k: man[k] for k in ("states", "corpus_states_rank_ge_3", "AC01D_reachable_pairs", "AC01R_pairs", "state_roles", "held_out_targets", "evaluation_sets", "storage_denominators", "shortest_path_action_fraction", "mean_on_shortest_path_actions_per_row")}, indent=1))
    print("manifest", p); print("hashes", man["hashes"])
