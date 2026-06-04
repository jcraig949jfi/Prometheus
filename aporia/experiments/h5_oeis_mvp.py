"""H5a OEIS MVP — run exactly once under the FROZEN failure_signal_protocol_v0.1.

Question (Central Law): do void candidates (preregistered convergence events in the
repair field) recover WITHHELD OEIS occupants -- ones NOT trivially operator-
reachable from visible wells -- better than null?

Pipeline (protocol §9): typed field -> void candidates (§5) -> held-out recovery
(§6, operator-closure sealed) -> null comparison (§8). Mechanical C = exact 12-term
prefix signature (§12.1). Reports the frozen k-curve (§12.3) and honest control
verdicts. Stubbed controls are marked STUB, never PASS (feedback_instrument_vs_
architectural_pass).

Run:  PGPASSWORD=... python -m aporia.experiments.h5_oeis_mvp
Emits aporia/results/h5_oeis_mvp_<date>.json
"""
from __future__ import annotations
import json, math, random, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from agents.arachne.landscapes import _pg

SIG_LEN = 12
MIN_TERMS = 16
WORKING_SET = 12000
N_BROKEN = 40000
K_VALUES = [10, 25, 50, 100]
K_MIN, M_MIN = 3, 2          # §5: >=k independent broken points, >=m move families
SEED = 20260604

# ---- operators (repair moves): seq -> seq -------------------------------------
def _diff(s):     return [s[i+1]-s[i] for i in range(len(s)-1)]
def _psum(s):
    o, a = [], 0
    for x in s: a += x; o.append(a)
    return o
def _bis_e(s):    return s[::2]
def _bis_o(s):    return s[1::2]
def _drop1(s):    return s[1:]
def _drop2(s):    return s[2:]
OPERATORS = {"diff": _diff, "psum": _psum, "bisect_e": _bis_e,
             "bisect_o": _bis_o, "drop1": _drop1, "drop2": _drop2}

def sig(seq):
    seq = seq[:SIG_LEN]
    return tuple(int(x) for x in seq) if len(seq) >= SIG_LEN else None


# ---- moves (broken-point generators): (well, rng, pool) -> seq ----------------
def _perturb(w, rng, pool):
    s = list(w); i = rng.randrange(min(len(s), SIG_LEN)); s[i] += rng.choice([-3,-1,1,3,7]); return s
def _trunc(w, rng, pool):   return w[1:]
def _interleave(w, rng, pool):
    o = rng.choice(pool); return [v for p in zip(w, o) for v in p]
def _modp(w, rng, pool):    P = rng.choice([7, 9, 11, 100]); return [x % P for x in w]
def _diffmove(w, rng, pool):return _diff(w)
MOVES = {"perturb": _perturb, "trunc": _trunc, "interleave": _interleave,
         "modp": _modp, "diffmove": _diffmove}


def load_sequences(conn, n, min_terms):
    cur = conn.cursor()
    cur.execute("SELECT oeis_id, first_terms FROM analysis.oeis "
                "WHERE array_length(first_terms,1) >= %s AND oeis_id IS NOT NULL "
                "ORDER BY seq_id LIMIT %s;", (min_terms, n))
    rows = [(r[0], [int(x) for x in r[1]]) for r in cur.fetchall()]
    cur.close()
    return rows


def operator_closure_sigs(hidden_full, operators):
    """Signatures one operator-hop from any hidden sequence (to seal leakage)."""
    closure = set()
    for terms in hidden_full:
        for op in operators.values():
            try:
                e = sig(op(terms))
                if e: closure.add(e)
            except Exception:
                pass
    return closure


def build_field(well_full, visible_sigs, operators, moves, rng, n_broken):
    """Generate broken points, repair them, collect non-visible endpoints with
    support (distinct broken points) and move-families."""
    pool = defaultdict(lambda: {"support": 0, "families": set()})
    op_items = list(operators.items())
    move_items = list(moves.items())
    for bp in range(n_broken):
        w = rng.choice(well_full)
        mname, mfn = rng.choice(move_items)
        try:
            B = mfn(w, rng, well_full)
        except Exception:
            continue
        if sig(B) in visible_sigs:        # not actually broken
            continue
        for oname, ofn in op_items:
            try:
                e = sig(ofn(B))
            except Exception:
                continue
            if e is None or e in visible_sigs:
                continue
            pool[e]["support"] += 1
            pool[e]["families"].add(mname)
    return pool


def candidates_ranked(pool):
    cands = [(e, d["support"]) for e, d in pool.items()
             if d["support"] >= K_MIN and len(d["families"]) >= M_MIN]
    cands.sort(key=lambda x: -x[1])
    return [e for e, _ in cands]


def _ci(p, k):
    if k == 0: return [0.0, 0.0]
    h = 1.96 * math.sqrt(max(p*(1-p), 1e-9) / k)
    return [round(max(0, p-h), 4), round(min(1, p+h), 4)]


def score(pool, hidden_sigs, ks):
    cands = candidates_ranked(pool)
    pool_keys = list(pool.keys())
    pool_hidden = sum(1 for e in pool_keys if e in hidden_sigs)
    baseline = pool_hidden / max(1, len(pool_keys))     # hidden fraction among all endpoints
    total_hidden_in_pool = pool_hidden
    out = {"n_candidates": len(cands), "pool_size": len(pool_keys),
           "pool_baseline_precision": round(baseline, 6),
           "hidden_reachable_in_pool": total_hidden_in_pool, "by_k": {}}
    for k in ks:
        topk = cands[:k]
        hit = sum(1 for e in topk if e in hidden_sigs)
        prec = hit / max(1, len(topk))
        rec = hit / max(1, total_hidden_in_pool)
        out["by_k"][str(k)] = {
            "precision": round(prec, 4), "recall": round(rec, 4),
            "hits": hit, "lift_over_baseline": round(prec / baseline, 3) if baseline > 0 else None,
            "precision_ci95": _ci(prec, len(topk))}
    return out


def run_once(well_full, hidden_full, operators, moves, rng, n_broken, label):
    visible_sigs = {sig(w) for w in well_full if sig(w)}
    hidden_sigs = {sig(h) for h in hidden_full if sig(h)} - visible_sigs
    pool = build_field(well_full, visible_sigs, operators, moves, rng, n_broken)
    s = score(pool, hidden_sigs, K_VALUES)
    s["label"] = label
    s["n_visible"] = len(visible_sigs); s["n_hidden_sigs"] = len(hidden_sigs)
    return s


def shuffled_operators(operators, rng):
    """Operator-label shuffle null (§3/§12.2 Null-2): names keep, fns permuted."""
    names = list(operators.keys()); fns = list(operators.values())
    rng.shuffle(fns)
    return dict(zip(names, fns))


def main():
    conn = _pg.connect("prometheus_sci")
    if conn is None:
        print(json.dumps({"verdict": "INVALID_CONTROL_FAILURE",
                          "error": "no OEIS connection (PGPASSWORD?)"}, indent=2)); return 2
    rng = random.Random(SEED)
    seqs = load_sequences(conn, WORKING_SET, MIN_TERMS)

    # 10% holdout (random; family metadata absent in analysis.oeis -- noted limitation),
    # then SEAL operator-closure: drop visible wells that are one operator-hop from a
    # hidden sequence, so recovery cannot be trivial operator-closure (§6.1).
    rng.shuffle(seqs)
    n_hidden = len(seqs) // 10
    hidden = seqs[:n_hidden]
    rest = seqs[n_hidden:]
    hidden_full = [t for _, t in hidden]
    closure = operator_closure_sigs(hidden_full, OPERATORS)
    visible = [(oid, t) for (oid, t) in rest if sig(t) not in closure]
    sealed = len(rest) - len(visible)
    well_full = [t for _, t in visible]

    # REAL run
    real = run_once(well_full, hidden_full, OPERATORS, MOVES, random.Random(SEED+1),
                    N_BROKEN, "real")

    # NULL: operator-label shuffle
    shuf_ops = shuffled_operators(OPERATORS, random.Random(SEED+2))
    null_shuffle = run_once(well_full, hidden_full, shuf_ops, MOVES, random.Random(SEED+3),
                            N_BROKEN, "operator_shuffle_null")

    # CONTROL: synthetic no-void landscape (random integer seqs, random holdout).
    # The field must NOT enrich for the random "hidden" set; if it does -> fabrication.
    rng_s = random.Random(SEED+4)
    synth = [[rng_s.randint(0, 50) for _ in range(MIN_TERMS)] for _ in range(len(seqs))]
    s_hidden = synth[:n_hidden]; s_rest = synth[n_hidden:]
    s_closure = operator_closure_sigs(s_hidden, OPERATORS)
    s_visible = [t for t in s_rest if sig(t) not in s_closure]
    synth_novoid = run_once(s_visible, s_hidden, OPERATORS, MOVES, random.Random(SEED+5),
                            N_BROKEN, "synthetic_no_void")

    # ---- verdict ----------------------------------------------------------------
    def lift100(r):
        v = r["by_k"]["100"]["lift_over_baseline"]
        return v if v is not None else 0.0
    real_lift = lift100(real)
    shuffle_lift = lift100(null_shuffle)
    synth_lift = lift100(synth_novoid)
    # control: no-void synthetic must not enrich
    synth_ok = synth_lift <= 1.5
    # real must beat both baseline (lift>1, CI lower bound > baseline implicitly) and the shuffle null
    p100 = real["by_k"]["100"]["precision"]
    ci_lo = real["by_k"]["100"]["precision_ci95"][0]
    beats = (real_lift > 1.0 and ci_lo > real["pool_baseline_precision"]
             and real_lift > 1.3 * max(1.0, shuffle_lift))
    if not synth_ok:
        verdict = "INVALID_CONTROL_FAILURE"
    elif beats:
        verdict = "BEATS_NULL"
    else:
        verdict = "NULL"

    result = {
        "protocol_version": "failure_signal_protocol_v0.1",
        "frozen_before_run": True,
        "experiment": "H5a_oeis_mvp",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "params": {"working_set": len(seqs), "sig_len": SIG_LEN, "min_terms": MIN_TERMS,
                   "n_broken": N_BROKEN, "k_values": K_VALUES, "k_min": K_MIN, "m_min": M_MIN,
                   "seed": SEED},
        "visible_wells": real["n_visible"], "hidden_wells": real["n_hidden_sigs"],
        "operator_closure_removed": sealed,
        "negative_controls": {
            "operator_label_shuffle": "PASS" if shuffle_lift < real_lift else "FAIL",
            "synthetic_no_voids": "PASS" if synth_ok else "FAIL",
            "synthetic_planted_voids": "STUB",       # H5b, deferred
            "randomized_labels": "STUB",
            "degree_preserving_rewire": "STUB",
        },
        "recovery_real": real,
        "null_operator_shuffle": null_shuffle,
        "control_synthetic_no_void": synth_novoid,
        "summary": {"real_lift@100": real_lift, "shuffle_null_lift@100": shuffle_lift,
                    "synth_novoid_lift@100": synth_lift},
        "verdict": verdict,
        "notes": ("Family metadata absent in analysis.oeis: holdout is random + "
                  "operator-closure-sealed (a documented simplification of the "
                  "family-level holdout). 3 of 5 negative controls STUB (H5b/graph "
                  "controls deferred). Mechanical C = exact 12-term prefix (no embeddings)."),
    }
    out_dir = REPO / "aporia" / "results"; out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"h5_oeis_mvp_{datetime.now(timezone.utc).strftime('%Y_%m_%d')}.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in
                      ("verdict", "visible_wells", "hidden_wells",
                       "operator_closure_removed", "negative_controls", "summary")}, indent=2))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
