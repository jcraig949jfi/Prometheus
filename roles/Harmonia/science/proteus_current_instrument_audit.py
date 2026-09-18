"""Audit of the Proteus V0.5 detailed-balance ("current") instrument -- HARM-44 (1).

Harmonia[m2-ca1148a0], 2026-09-18. Answers Proteus #341 question 1 with an
EXECUTING check rather than a reading. Imports proteus.v0_5.kernel unchanged
(base rule 6: the audited object is not edited) and exercises the three
controls the instrument is missing, on a synthetic 4-state kernel where the
true current is KNOWN:

    C-NEG   the reversible reference Q of the code carries current ~0. This is
            the control the instrument already runs; it is shown here to be one
            that CANNOT FAIL (Q is reversible by algebra, so the check tests
            floating point, not the instrument).
    C-POS   a KNOWN cyclic current of amplitude eps injected into Q; the
            pipeline must recover |J| = eps on the perturbed pairs. This is the
            control that gives a MINIMUM DETECTABLE CURRENT and is absent from
            run_kernel.py.
    C-CHEAT the Monte-Carlo noise floor of run_kernel.py (max |J_A - J_B| over
            the pairs of two samples) computed with B == A: the floor is 0 and
            EVERY pair with |J| > 0 reads "above floor". run_kernel.py has no
            guard for this; the audit shows the reading the instrument would
            print.

Writes science/ledgers/proteus_current_instrument_audit_2026-09-18.json.
Touches nothing under proteus/.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)

from proteus.v0_5 import kernel as K  # noqa: E402  (audited object, read-only)

STATES = [(1, 16), (2, 16), (3, 16), (4, 16)]   # (L, T) shape the module expects


def _row_normalise(P):
    for i, row in P.items():
        s = sum(v for j, v in row.items() if j != i)
        row[i] = 1.0 - s
    return P


def synthetic_cyclic_kernel(drive=0.10):
    """A 4-cycle with a clockwise bias: P(i -> i+1) = 0.25 + drive, P(i -> i-1) = 0.25 - drive.
    Uniform pi; true current on every cycle edge is J = pi * 2 * drive = 0.5 * drive."""
    n = len(STATES)
    P = {}
    for k, s in enumerate(STATES):
        P[s] = {STATES[(k + 1) % n]: 0.25 + drive, STATES[(k - 1) % n]: 0.25 - drive}
    return _row_normalise(P)


def noise_floor_as_in_run_kernel(cur, cur2):
    """Verbatim logic of proteus/v0_5/run_kernel.py lines 127-138."""
    c2 = {(tuple(r["i"]), tuple(r["j"])): r["J"] for r in cur2}
    noise = [abs(r["J"] - c2.get((tuple(r["i"]), tuple(r["j"])), 0.0)) for r in cur]
    floor = max(noise) if noise else 0.0
    above = [r for r in cur if abs(r["J"]) > floor]
    return floor, len(above)


def main():
    out = {"audit": "HARM-44 (1) Proteus V0.5 current instrument", "states": [list(s) for s in STATES]}

    P = synthetic_cyclic_kernel(0.10)
    pi, iters, delta = K.stationary(P, STATES)
    cur = K.currents(P, pi, STATES)
    true_J = 0.25 * 2 * 0.10                     # pi = 0.25, net = P_fwd - P_back = 0.20
    got = sorted(abs(r["J"]) for r in cur)
    out["synthetic_known_current"] = {"true_abs_J": true_J, "recovered_abs_J": got,
                                      "stationary_iters": iters, "l1_delta": delta,
                                      "pass": all(abs(g - true_J) < 1e-12 for g in got)}

    # C-NEG: the reference is reversible by construction; its current is ~0 for ANY input.
    Q = K.reversible_reference(P, pi, STATES)
    curQ = K.currents(Q, pi, STATES)
    out["C_NEG_reversible_reference"] = {
        "max_abs_J": max(abs(r["J"]) for r in curQ),
        "verdict": "PASSES, BUT CANNOT FAIL: Q_ij = (pi_i P_ij + pi_j P_ji)/(2 pi_i) satisfies "
                   "detailed balance identically; this checks floating point, not the instrument"}

    # C-POS: inject a KNOWN cyclic current of amplitude eps into Q and recover it.
    rows = []
    for eps in (1e-2, 1e-3, 1e-4, 1e-5):
        Qp = {i: dict(r) for i, r in Q.items()}
        n = len(STATES)
        for k, s in enumerate(STATES):            # J_true on each edge = pi * (2 eps) = 0.5 eps
            nxt, prv = STATES[(k + 1) % n], STATES[(k - 1) % n]
            Qp[s][nxt] = Qp[s].get(nxt, 0.0) + eps
            Qp[s][prv] = Qp[s].get(prv, 0.0) - eps
        _row_normalise(Qp)
        piQ, _, _ = K.stationary(Qp, STATES)
        curP = K.currents(Qp, piQ, STATES)
        rec = max(abs(r["J"]) for r in curP)
        rows.append({"eps": eps, "true_abs_J": 0.5 * eps, "recovered_max_abs_J": rec,
                     "relative_error": abs(rec - 0.5 * eps) / (0.5 * eps)})
    out["C_POS_injected_current"] = {"rows": rows,
                                     "pass": all(r["relative_error"] < 1e-6 for r in rows),
                                     "note": "recovery is exact on an EXACT kernel; on a SAMPLED kernel "
                                             "the same injection sets the minimum detectable current, "
                                             "which run_kernel.py never measures"}

    # C-CHEAT: floor with B == A.
    floor_same, above_same = noise_floor_as_in_run_kernel(cur, cur)
    nonzero = sum(1 for r in cur if abs(r["J"]) > 0)
    out["C_CHEAT_floor_with_B_equals_A"] = {
        "floor": floor_same, "n_above_floor": above_same, "n_pairs_nonzero": nonzero,
        "instrument_guard_present": False,
        "verdict": "floor collapses to 0 and every nonzero pair reads ABOVE FLOOR; run_kernel.py "
                   "would print this as a detection. A floor of 0 must read INDETERMINATE."}

    # what a real second sample does: perturb by sampling noise of known size
    import random
    rng = random.Random(3)
    P2 = {i: {j: max(0.0, v + rng.gauss(0, 1e-3)) for j, v in r.items() if j != i} for i, r in P.items()}
    _row_normalise(P2)
    pi2, _, _ = K.stationary(P2, STATES)
    floor2, above2 = noise_floor_as_in_run_kernel(cur, K.currents(P2, pi2, STATES))
    out["floor_with_independent_B"] = {"floor": floor2, "n_above_floor": above2,
                                       "injected_sampling_sd": 1e-3, "true_abs_J": true_J}

    path = os.path.join(HERE, "ledgers", "proteus_current_instrument_audit_2026-09-18.json")
    with open(path, "w", encoding="ascii", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    for k, v in out.items():
        print(k, "->", json.dumps(v)[:300])
    ok = out["synthetic_known_current"]["pass"] and out["C_POS_injected_current"]["pass"] \
        and out["C_CHEAT_floor_with_B_equals_A"]["n_above_floor"] == nonzero
    print("AUDIT", "OK" if ok else "FAILED", path)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
