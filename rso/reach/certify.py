"""Independent certification of a search hit (C-013-T010, Argus; operator ruling s3 bullet 1).

A training-perfect genome is a CANDIDATE, never a result. certify() ignores the search's fitness entirely and
recomputes, on lives the search never saw:

  1. SELECTION   lives SELECT0 .. SELECT0+63 (unsealed, disjoint from training and from reach.py's 1000..1063):
                 at least 90% of BUILD probes correct (the reach.py confirm() rule, reach.py:172-181).
  2. SEALED      lives SEALED0 .. SEALED0+63 (sealed block, disjoint from reach.py's SEALED_BASE+60000 block):
                 the BUILD class-exclusion ruler (rulers.class_exclusion, rulers.py:139-172) must return PASS --
                 the probe score is outside what ANY no-carry policy can reach (alpha 1e-6).
  3. ORACLE      the sealed counts (every trial type) and the training probe score are recomputed with the
                 independent pure-Python implementation (oracle.py, I1 independence -- see its own docstring) and must
                 equal the compiled kernel's exactly. Disagreement = VOID: the instrument, not the genome, failed.

status: CERTIFIED (1, 2, 3 all hold) | NOT_CERTIFIED | VOID (oracle disagreement).
"""
import numpy as np

from rso.reach._proto import oracle, org, ru, wm

P = ru.Params()
TRAIN0, N_TRAIN = 0, 16
SELECT0, N_SELECT = 2000, 64
SEALED0, N_SEALED = ru.SEALED_BASE + 130_000, 64


def _numba_sealed_counts(prog, store0):
    return ru.evaluate(prog, store0, P, SEALED0, N_SEALED)["counts"]


def _oracle_counts(prog, store0, life0, nlives):
    prog_l = [tuple(int(x) for x in row) for row in np.asarray(prog)]
    st = [int(x) for x in store0]
    c = np.zeros((wm.NTYPES, 2), dtype=np.int64)
    for life in range(life0, life0 + nlives):
        rows, _, _ = oracle.run_life(prog_l, st, P.seed, life, P.K, P.R, P.E, P.T, P.F, P.cap)
        for (_ep, _t, ttype, _s, _a, ok) in rows:
            c[ttype, 0] += 1
            c[ttype, 1] += ok
    return c


def certify(prog, store0=None, claimed_training_fit=None):
    """claimed_training_fit is accepted and IGNORED (recorded only), so a caller cannot make it matter."""
    prog = np.ascontiguousarray(prog, dtype=np.int64)
    store0 = org.empty_store(P.S) if store0 is None else np.asarray(store0, dtype=np.int64)
    out = dict(claimed_training_fit=claimed_training_fit, select_lives=[SELECT0, N_SELECT],
               sealed_lives=[SEALED0, N_SEALED])
    tr_oracle = _oracle_counts(prog, store0, TRAIN0, N_TRAIN)
    tr_numba = ru.evaluate(prog, store0, P, TRAIN0, N_TRAIN, sealed=False)["counts"]
    out["training_fit_recomputed"] = int(tr_oracle[wm.T_PROBE, 1])
    sel = ru.evaluate(prog, store0, P, SELECT0, N_SELECT, sealed=False)["counts"]
    out["selection_probe"] = [int(sel[wm.T_PROBE, 0]), int(sel[wm.T_PROBE, 1])]
    out["selection_ok"] = 10 * int(sel[wm.T_PROBE, 1]) >= 9 * int(sel[wm.T_PROBE, 0])
    sealed = _numba_sealed_counts(prog, store0)
    v = ru.class_exclusion(int(sealed[wm.T_PROBE, 0]), int(sealed[wm.T_PROBE, 1]), P.R)
    out["sealed_probe"] = [int(sealed[wm.T_PROBE, 0]), int(sealed[wm.T_PROBE, 1])]
    out["sealed_verdict"] = v["verdict"]
    sealed_oracle = _oracle_counts(prog, store0, SEALED0, N_SEALED)
    out["oracle_agrees"] = bool(np.array_equal(sealed_oracle, sealed) and np.array_equal(tr_oracle, tr_numba))
    if not out["oracle_agrees"]:
        out.update(status="VOID", certified=False)
    elif out["selection_ok"] and v["verdict"] == ru.PASS:
        out.update(status="CERTIFIED", certified=True)
    else:
        out.update(status="NOT_CERTIFIED", certified=False)
    return out
