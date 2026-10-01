"""Exhaustive 2-line READOUT completion (abstract, exact integer ISA semantics of engine.py), vectorised.
Question: given the actuator-side latches an 8-line sign-coded SB program can hold (S1 = '+'-cue amplitude,
S2 = '-'-cue amplitude, both decaying), is there ANY 2-instruction suffix writing S0 whose sign is
 '+' for (fresh, stale) and (stale, fresh), '-' for (fresh, fresh)?
Ranges at the readout tick from the 8-line SB scale: fresh 100..600 (incl. 2-packet sums), stale 0..50.
Readable registers at the actuator at the readout tick (non-sensor, no arrival that tick): S1, S2, S0_old,
ENERGY=1000 and zeros (S3, T*, EMIT, CHAN, RPORT, RVAL, PAY*, IN*, CNT0, SENSE, ZERO all equal 0).
S0_old (prior readout; read by SEL/NOP or as an operand) is tested (a) equal to the wanted sign, (b) opposite.
Line 1 writes a scratch T or S0; line 2 writes S0 and may read T and S0. RAND excluded (stochastic);
SETRULE/WIMM leave the destination unchanged (= NOP for the value)."""
import json, time, pathlib
import numpy as np
RM = 32767
t0 = time.process_time()
FR = [100, 150, 200, 300, 450, 600]
ST = [0, 5, 15, 30, 50]
cases = [(f, s, 1) for f in FR for s in ST] + [(s, f, 1) for f in FR for s in ST] + [(f, g, -1) for f in FR for g in FR]
S1 = np.array([c[0] for c in cases], np.int64); S2 = np.array([c[1] for c in cases], np.int64)
W = np.array([c[2] for c in cases], np.int64); K = len(cases)
Z = np.zeros(K, np.int64); E = np.full(K, 1000, np.int64)
cl = lambda x: np.clip(x, -RM, RM)

def all_outputs(regs, old):
    """every single-instruction output vector (deduplicated) given register vectors and old dst value."""
    outs = []
    R = list(regs.values())
    for A in R:
        outs.append(A)
        for imm in range(-128, 128):
            outs.append(cl(A + imm))
        for sh in range(16):
            outs.append(A >> sh)
        for B in R:
            outs += [cl(A + B), cl(A - B), cl((A * B) >> 8), (A > B).astype(np.int64) * 256, np.maximum(A, B),
                     cl(A ^ B), np.remainder(A, np.abs(B) + 1)]
    for imm in range(-128, 128):
        for sh in range(8):
            outs.append(np.full(K, int(cl(imm << sh)), np.int64))
    return np.unique(np.stack(outs), axis=0)

def line2_hits(T, S0b):
    """T, S0b: [n, K]. Count rows for which SOME line-2 instruction yields sign == W on all cases."""
    n = T.shape[0]
    regs = [np.broadcast_to(S1, (n, K)), np.broadcast_to(S2, (n, K)), np.broadcast_to(Z, (n, K)),
            np.broadcast_to(E, (n, K)), T]
    ok = np.zeros(n, bool)
    good = lambda v: np.all(np.sign(v) == W, axis=1)
    pos, neg = W > 0, W < 0
    for A in regs:
        ok |= good(A)                                                   # MOV / NOP-like
        lo = -A[:, pos].min(1); hi = -A[:, neg].max(1)                  # ADDI: need lo < imm < hi
        a = np.maximum(lo + 1, -128); b = np.minimum(hi - 1, 127)
        ok |= a <= b
        for sh in range(16):
            ok |= good(A >> sh)
        for B in regs:
            for v in (cl(A + B), cl(A - B), cl((A * B) >> 8), np.maximum(A, B), cl(A ^ B)):
                ok |= good(v)
            # GT, MOD are >= 0 and CONST is constant: they can never produce both signs -> skipped (sound)
    return ok

res = {}
for mode in ("feedback_free",):
    base = {"S1": S1, "S2": S2, "Z": Z, "E": E}
    V1 = all_outputs(base, Z)                   # line 1 -> scratch (writing S0 first is overwritten by line 2)
    hT = line2_hits(V1, None)
    res[mode] = {"line1_distinct": int(V1.shape[0]), "hits": int(hT.sum()),
                 "example_rows": [V1[i].tolist()[:6] for i in np.flatnonzero(hT)[:3]]}
    print(mode, res[mode], round(time.process_time() - t0, 1), flush=True)
res.update({"cases": K, "fresh": FR, "stale": ST, "cpu_s": round(time.process_time() - t0, 1)})
pathlib.Path(__file__).with_name("out").joinpath("readout_enum_static.json").write_text(json.dumps(res, indent=1))
