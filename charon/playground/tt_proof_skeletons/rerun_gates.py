"""Re-score Gate 3' and the minimal-skeleton probe on v2 and v3 archives
using DETERMINISTIC evaluation (genome-hash-seeded RNG).

Tests the hypothesis: how much of the v2 'fragile composition' finding was
genuine operator counterproductivity vs. stochastic-evaluation noise?
"""

import json
import random
from pathlib import Path
from hashlib import sha256

import numpy as np

import evolve_tt_v3 as core  # reuse operators and utilities


HERE = Path(__file__).parent


def genome_hashseed(genome):
    s = repr(tuple((name, tuple(sorted(params.items()))) for name, params in genome))
    return int(sha256(s.encode()).hexdigest()[:8], 16)


def evaluate_det(genome):
    """Deterministic evaluate: seed both module RNGs from genome hash."""
    h = genome_hashseed(genome)
    saved_np = core.rng
    saved_py = random.getstate()
    core.rng = np.random.default_rng(core.SEED ^ h)
    random.seed(core.SEED + h)
    try:
        state = core.apply_sequence(genome)
        tr = core.sample_err(state, core.X_TRAIN, core.F_TRAIN, core.F_TRAIN_NORM)
        va = core.sample_err(state, core.X_VAL, core.F_VAL, core.F_VAL_NORM)
        r = core.max_rank(state)
        if not (np.isfinite(tr) and np.isfinite(va)):
            return None
        return r, tr, va, state
    except Exception:
        return None
    finally:
        core.rng = saved_np
        random.setstate(saved_py)


def reconstitute_genome(raw):
    """Archive cells store params as dict (via json.dump default=str).
    Some numeric values may have survived; normalize back."""
    fixed = []
    for op in raw:
        name = op[0]
        params = dict(op[1]) if op[1] else {}
        for k, v in list(params.items()):
            if isinstance(v, str):
                try:
                    params[k] = int(v)
                except ValueError:
                    try:
                        params[k] = float(v)
                    except ValueError:
                        pass
        fixed.append((name, params))
    return fixed


def ablation_scan_det(genome):
    base = evaluate_det(genome)
    if base is None: return None
    _, _, va, _ = base
    drops = []
    for i in range(len(genome)):
        trial = [op for j, op in enumerate(genome) if j != i]
        r = evaluate_det(trial)
        drops.append(None if r is None else r[2] - va)
    return va, drops


def minimal_skeleton_det(genome, tol=1.10, max_iters=30):
    current = list(genome)
    base = evaluate_det(current)
    if base is None: return current, float("inf"), 0
    _, _, orig_va, _ = base
    best_va = orig_va
    dropped = 0
    for _ in range(max_iters):
        if len(current) <= 1: break
        # greedy: drop the op whose removal yields best (lowest) val, if within tol of ORIGINAL
        best_i = -1
        best_new = best_va
        for i in range(len(current)):
            trial = current[:i] + current[i + 1:]
            r = evaluate_det(trial)
            if r is None: continue
            va_new = r[2]
            if va_new <= orig_va * tol and va_new < best_new:
                best_new = va_new
                best_i = i
        if best_i < 0: break
        current = current[:best_i] + current[best_i + 1:]
        best_va = best_new
        dropped += 1
    return current, best_va, dropped


def score_archive(archive_path, label):
    print(f"\n{'='*60}")
    print(f"RE-SCORING {label}: {archive_path}")
    print(f"{'='*60}")
    with open(archive_path) as f:
        data = json.load(f)
    cells = list(data["cells"].values())
    # Parse genome fields: they're stored as list of [name, {params}]
    for c in cells:
        c["genome"] = reconstitute_genome(c["genome"])
    # Rank by stored val_err, take top-3
    top3 = sorted(cells, key=lambda v: v["val_err"])[:3]

    print("\n--- Gate 3' (DETERMINISTIC) ---")
    total_load = 0
    total_harm = 0
    total_neutral = 0
    total_ops = 0
    for idx, t in enumerate(top3):
        res = ablation_scan_det(t["genome"])
        if res is None:
            print(f"  elite #{idx+1}: eval failed")
            continue
        va, drops = res
        ops = [op[0] for op in t["genome"]]
        n_load = n_harm = n_neutral = 0
        print(f"  elite #{idx+1}: val={va:.2e} (archive stored {t['val_err']:.2e}) len={len(ops)}")
        for i, (op, d) in enumerate(zip(ops, drops)):
            if d is None: continue
            rel = d / max(va, 1e-15)
            if rel > 0.1:
                n_load += 1; label_op = "LOAD"
            elif rel < -0.1:
                n_harm += 1; label_op = "HARM"
            else:
                n_neutral += 1; label_op = "---"
            print(f"    {i:2d} {op:12s}: dval={d:+.2e} ({rel:+.2f}x) {label_op}")
        print(f"    summary: load={n_load}/{len(ops)}  harmful={n_harm}  neutral={n_neutral}")
        total_load += n_load
        total_harm += n_harm
        total_neutral += n_neutral
        total_ops += len(ops)
    if total_ops > 0:
        print(f"\n  aggregate across top-3: load={total_load}/{total_ops} "
              f"({100*total_load/total_ops:.0f}%) "
              f"harmful={total_harm} ({100*total_harm/total_ops:.0f}%) "
              f"neutral={total_neutral} ({100*total_neutral/total_ops:.0f}%)")

    print("\n--- Minimal-skeleton probe (DETERMINISTIC) ---")
    for idx, t in enumerate(top3):
        orig = t["genome"]
        minimal, mva, ndrop = minimal_skeleton_det(orig, tol=1.10,
                                                   max_iters=len(orig))
        min_ops = [op[0] for op in minimal]
        orig_ops = [op[0] for op in orig]
        print(f"  elite #{idx+1}: {len(orig)} -> {len(minimal)} ops "
              f"(dropped {ndrop})")
        print(f"    original: {orig_ops}")
        print(f"    minimal:  {min_ops}  val={mva:.2e}")


if __name__ == "__main__":
    score_archive(HERE / "archive_v2.json", "V2 (single family)")
    score_archive(HERE / "archive_v3.json", "V3 (two families)")
