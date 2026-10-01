"""s3 controls. python -B s3_controls.py -> s3_controls.json

Positive control: redundant setters. Layout (bytes 0..6): 1E 40 | 2E 00 | 1E 40 | E5, passengers 7..63 uniform random.
  setter A = LD E,0x40 at 0-1, setter B = LD E,0x40 at 4-5, LD L,0 at 2-3, copy op E5 at 6.
  Setter knockout positions are the opcode bytes (0 and 4): a random opcode leaves 0x40 to execute as LD B,B.
  (The operand byte of the LAST setter is not redundant by construction: a wrong value there is the last write to E.)
  Checks: (1) COMPETENT and STATE_FREE; (2) sufficiency: NOP-out (00 00) setter A alone, B alone -> function kept,
  both -> function lost; (3) protocol: single random-value knockouts at 0 and 4 dispensable (kept >= 2/3), pair
  (0,4) lethal with confirmation re-assay.  Five passenger seeds; the control PASSES if every check passes on the
  pre-designated construct (seed 0); the other seeds are reported as robustness.
Negative control: 2E 00 1E 40 E5 + 59 random passengers (3 passenger seeds). Full pipeline over positions 5..63
  (passengers): dispensable set, 200 sampled passenger pairs, lethal rate vs additive null; PASS iff pooled rate
  <= 2x null (pooled over the 3 seeds; per-seed shown).
Function for both controls = COMPETENT and STATE_FREE (both carry LD L,0 for state-freedom). Cell 7ae3, dense VM.
"""
import json
import random
import time

import s3_common as S
import s3_pipeline as P

CELL = "7ae3"
t0 = time.process_time()
fn = lambda m, suf="": S.function(CELL, m, True, True, suf)
out = {"positive": [], "negative": []}
for seed in range(5):
    rng = random.Random(1000 + seed)
    g = bytearray(bytes.fromhex("1E402E001E40E5") + bytes(rng.randrange(256) for _ in range(57)))
    g = bytes(g)
    rec = {"seed": seed, "hex": g.hex(), "competent": S.competent(CELL, g), "state_free": S.state_free(CELL, g)}
    def nop(ps):
        m = bytearray(g)
        for p in ps:
            m[p] = 0
        return bytes(m)
    rec["nop_A_kept"] = fn(nop([0, 1])); rec["nop_B_kept"] = fn(nop([4, 5])); rec["nop_AB_kept"] = fn(nop([0, 1, 4, 5]))
    sg = P.singles(CELL, g, True, True, [0, 4])
    rec["single_kept"] = {str(p): v for p, v in sg.items()}
    rec["A_dispensable"] = sum(sg[0]) >= 2; rec["B_dispensable"] = sum(sg[4]) >= 2
    rec["pair_lethal"], rec["pair_confirmed"] = P.pair_call(CELL, g, True, True, 0, 4)
    rec["pair_draws_kept"] = [fn(m) for m in S.pair_mutants(g, 0, 4)]
    rec["PASS"] = bool(rec["competent"] and rec["state_free"] and rec["nop_A_kept"] and rec["nop_B_kept"]
                       and not rec["nop_AB_kept"] and rec["A_dispensable"] and rec["B_dispensable"]
                       and rec["pair_lethal"] and rec["pair_confirmed"])
    out["positive"].append(rec); print("POS", rec, round(time.process_time() - t0, 1), flush=True)
tot_l = tot_n = tot_null = 0
for seed in range(3):
    rng = random.Random(2000 + seed)
    g = bytes.fromhex("2E001E40E5") + bytes(rng.randrange(256) for _ in range(59))
    rec = {"seed": seed, "hex": g.hex(), "competent": S.competent(CELL, g), "state_free": S.state_free(CELL, g)}
    if rec["competent"] and rec["state_free"]:
        sg = P.singles(CELL, g, True, True, range(64))
        rec["single_kept"] = {str(p): v for p, v in sg.items()}
        disp = [p for p in range(5, 64) if sum(sg[p]) >= 2]
        rec["core_nondisp"] = [p for p in range(5) if sum(sg[p]) < 2]
        rec["n_disp_passengers"] = len(disp)
        pairs = P.sample_pairs(g, disp, 200)
        pf = {p: 1 - sum(sg[p]) / 3 for p in disp}
        nl = [S.null_lethal(pf[i], pf[j]) for i, j in pairs]
        calls = [(i, j) + P.pair_call(CELL, g, True, True, i, j) for i, j in pairs]
        leth = [(i, j) for i, j, l, c in calls if l and c]
        rec.update({"n_pairs": len(pairs), "n_lethal_raw": sum(c[2] for c in calls), "n_lethal": len(leth),
                    "lethal_pairs": leth, "rate": len(leth) / len(pairs), "null": sum(nl) / len(nl)})
        rec["excess"] = rec["rate"] / rec["null"] if rec["null"] > 0 else None
        tot_l += len(leth); tot_n += len(pairs); tot_null += sum(nl)
    out["negative"].append(rec)
    print("NEG", {k: v for k, v in rec.items() if k != "single_kept"}, round(time.process_time() - t0, 1), flush=True)
out["negative_pooled"] = {"rate": tot_l / tot_n if tot_n else None, "null": tot_null / tot_n if tot_n else None}
np_ = out["negative_pooled"]
np_["excess"] = np_["rate"] / np_["null"] if tot_n and np_["null"] else None
np_["PASS"] = bool(tot_n and np_["rate"] <= 2 * np_["null"])
out["positive_PASS"] = out["positive"][0]["PASS"]
out["cpu_s"] = round(time.process_time() - t0, 1)
json.dump(out, open("s3_controls.json", "w"), indent=1)
print("positive_PASS", out["positive_PASS"], "negative", np_, "cpu", out["cpu_s"])
