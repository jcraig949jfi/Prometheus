"""T-P11. PAIR_EXECUTION copy causality, with negative controls run against the predecessor.

Every fixture is a real pair interaction on the repaired z8: two hand-assembled halves
on one tape, organism a (offset 0) executing first, then b (offset n). Copy mutation is
off so the outcome is exact. For each fixture the test computes

  * the PREDECESSOR verdict: final victim fidelity to donor >= 0.90, victim fidelity to
    its own prior bytes < 0.90, donor writes_other >= n/4 - read off the same interaction;
  * the P-11 verdict: the predecessor criterion AND the randomized-victim assay.

The directive's seven cases are required outcomes. A NEGATIVE control counts only if the
predecessor ACCEPTS it: a control the old detector already rejects cannot show that the
old detector is defective. Where a directed case cannot catch the predecessor by
construction, the test says so rather than counting it.

Then CRITERION-CAN-FIRE: each of C2, C4, C5 is removed in turn from the assay (the
mutant), and a fixture that only that criterion rejects must flip the ASSAY to PASS under
the mutant. The assay is compared alone, without the predecessor prefilter in front of
it, so a fixture the prefilter happens to refuse cannot hide whether the criterion
works. A criterion no fixture can make fire would be a guard that cannot fire.

Run:  python tests/test_p11.py         Exit: 0 all demonstrated, 1 otherwise.
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import p11                    # noqa: E402
import z8                     # noqa: E402
from constants import C       # noqa: E402

N = 96                        # Z8_SHARED / Z8_SEPARATED half length
TAPE = 256                    # _pow2(2 * 96): the 64 bytes above 192 are tape padding
MASK = 0x01 | 0x02 | 0x08 | 0x20   # ALLOC/BIRTH, SELF, SENSE, LDIR - PRIMITIVE x BLOCK
BUDGET = 1000                 # generous: tests the criterion, not the slice budget
FRESH = (None, 0, 0)          # registers as a newly placed organism has them


def rnd(seed, k):
    r = random.Random(seed)
    return bytes(r.randrange(256) for _ in range(k))


def prog(src, fill_seed, n=N):
    code, _ = z8.asm(src)
    return code + rnd(fill_seed, n - len(code))


def observe(ga, gb, victim_side, donor_disabled=False):
    """Run the observed interaction; return the predecessor verdict and its numbers."""
    tape, prov, lit, wo = p11.interact(z8, n=N, tape_len=TAPE, ga=ga, gb=gb, st_a=FRESH,
                                       st_b=FRESH, budget=BUDGET, ops_mask=MASK, cmr=0.0,
                                       rng=random.Random(0), victim_side=victim_side,
                                       donor_disabled=donor_disabled)
    v0 = 0 if victim_side == 0 else N
    old = ga if victim_side == 0 else gb
    donor = gb if victim_side == 0 else ga
    new = bytes(tape[v0:v0 + N])
    fo, fs = p11.fidelity(donor, new), p11.fidelity(old, new)
    dw = wo[1 - victim_side]
    return {"fid_other": round(fo, 4), "fid_self": round(fs, 4), "donor_wrote": dw,
            "predecessor": p11.predecessor_accepts(fo, fs, dw, N)}


def verdict(ga, gb, victim_side, donor_disabled=False, **kw):
    ob = observe(ga, gb, victim_side, donor_disabled)
    a = p11.assay(z8, n=N, tape_len=TAPE, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                  budget=BUDGET, ops_mask=MASK, cmr=0.0, victim_side=victim_side,
                  seed=("T-P11", ga.hex(), gb.hex(), victim_side), **kw)
    return dict(ob, p11=bool(ob["predecessor"] and a["pass"]), assay=a)


# ------------------------------------------------------------------ the fixtures
BLOCK_COPIER = "SELF\nLD DE,96\nLDIR\nHALT"                     # a -> b, whole genome
BYTE_COPIER = ("SELF\nLD DE,96\nloop:\nLD A,(HL)\nLD (DE),A\nINC HL\nINC DE\nDEC BC\n"
               "LD A,B\nOR C\nJRNZ loop\nHALT")
REL_COPIER_B = "SELF\nLD DE,0\nLDIR\nHALT"                      # b -> a, whole genome


def fx_block():
    return prog(BLOCK_COPIER, 11), rnd(12, N), 1


def fx_bytewise():
    return prog(BYTE_COPIER, 21), rnd(22, N), 1


def fx_similar_no_copy():
    """Victim already shares most bytes with the donor and PULLS the rest itself; the donor
    copies nothing into it, only 30 bytes into the tape padding (writes_other = 30 >= 24)."""
    donor = prog("LD HL,0\nLD DE,192\nLD BC,30\nLDIR\nHALT", 31)
    code, _ = z8.asm("LD HL,12\nLD DE,108\nLD BC,30\nLDIR\nHALT")
    victim = bytearray(donor)
    victim[0:len(code)] = code
    victim[12:42] = rnd(32, 30)
    return donor, bytes(victim), 1


def fx_unrelated_writes():
    """Donor writes 30 bytes INTO the victim half, all zeros from the padding. The victim
    then overwrites those very positions from the donor itself. The donor's writes are
    many and inside the victim, and are not why the victim matches."""
    donor = prog("LD HL,192\nLD DE,108\nLD BC,30\nLDIR\nHALT", 41)
    code, _ = z8.asm("LD HL,12\nLD DE,108\nLD BC,30\nLDIR\nHALT")
    victim = bytearray(donor)
    victim[0:len(code)] = code
    victim[12:42] = rnd(42, 30)
    return donor, bytes(victim), 1


def fx_partial_plus_similarity():
    """A GENUINE partial copy: the donor really copies 30 of its bytes into the victim, and
    the other 66 already matched. Authorship on the observed event is 100% donor; only the
    randomized victim exposes that 30 bytes cannot rebuild a genome."""
    donor = prog("LD HL,12\nLD DE,108\nLD BC,30\nLDIR\nHALT", 51)
    victim = bytearray(donor)
    victim[0] = 0x76                       # the victim halts at once
    victim[12:42] = rnd(52, 30)
    return donor, bytes(victim), 1


def fx_random_victim_rebuilt():
    """b is a whole-genome copier writing onto a; a is random bytes and runs first."""
    return rnd(61, N), prog(REL_COPIER_B, 62), 0


def fx_loader():
    """CAN-FIRE fixture for C4. The donor writes only a 12-byte loader into the victim's
    start; the victim, running that loader, copies the donor into itself. The victim ends a
    donor copy, but the donor authored only the loader."""
    loader, _ = z8.asm("LD HL,0\nLD DE,96\nLD BC,96\nLDIR\nHALT")
    donor = prog("LD HL,20\nLD DE,96\nLD BC,%d\nLDIR\nHALT" % len(loader), 71)
    donor = donor[:20] + loader + donor[20 + len(loader):]
    return donor, rnd(72, N), 1


PULL_VICTIM = prog("LD HL,0\nLD DE,96\nLD BC,96\nLDIR\nHALT", 81)   # C5 can-fire injection


def main():
    ok = True
    rows = []

    def check(name, cond, detail):
        nonlocal ok
        ok &= bool(cond)
        rows.append({"check": name, "pass": bool(cond), "detail": detail})
        print("%-6s %-46s %s" % ("PASS" if cond else "FAIL", name, detail))

    def brief(v):
        a = v["assay"]
        d = a["draws"][0]
        return ("pred=%s p11=%s fo=%.3f fs=%.3f dw=%d | draws %d/%d  fid=%.3f auth=%.2f "
                "lit=%.2f dis=%.3f" % (v["predecessor"], v["p11"], v["fid_other"],
                                       v["fid_self"], v["donor_wrote"], a["draws_passed"],
                                       C["P11_DRAWS"], d["fid_final"], d["donor_authored_share"],
                                       d["donor_last_wrote_share"], d["fid_donor_disabled"]))

    print("T-P11 directed cases (operator directive 2026-09-23, S2)")
    print("-" * 110)
    cases = [
        ("genuine block copier", fx_block, True, False),
        ("genuine bytewise copier", fx_bytewise, True, False),
        ("already-similar halves, no copying", fx_similar_no_copy, False, False),
        ("donor writes many unrelated bytes", fx_unrelated_writes, False, False),
        ("partial overwrite + pre-existing similarity", fx_partial_plus_similarity, False, False),
        ("randomized victim rebuilt by donor", fx_random_victim_rebuilt, True, False),
        ("same case, donor writes disabled", fx_random_victim_rebuilt, False, True),
    ]
    for name, fx, want, disabled in cases:
        ga, gb, vs = fx()
        v = verdict(ga, gb, vs, donor_disabled=disabled)
        check(name + (": PASS" if want else ": FAIL"), v["p11"] == want, brief(v))

    print()
    print("NEGATIVE CONTROLS against the predecessor detector (must be ACCEPTED by it)")
    print("-" * 110)
    for name, fx, disabled in (("already-similar halves, no copying", fx_similar_no_copy, False),
                               ("donor writes many unrelated bytes", fx_unrelated_writes, False),
                               ("partial overwrite + pre-existing similarity",
                                fx_partial_plus_similarity, False)):
        ga, gb, vs = fx()
        v = verdict(ga, gb, vs, donor_disabled=disabled)
        check("predecessor fooled: " + name, v["predecessor"] and not v["p11"], brief(v))
    ga, gb, vs = fx_random_victim_rebuilt()
    v = verdict(ga, gb, vs, donor_disabled=True)
    rows.append({"check": "donor-disabled case vs predecessor", "pass": None,
                 "detail": "NOT A CATCH: the predecessor also rejects it (donor_wrote=%d, "
                           "fid_other=%.3f). Its write-count clause already refuses a donor "
                           "that wrote nothing; C5's ability to fire is shown below instead."
                           % (v["donor_wrote"], v["fid_other"])})
    print("n/a    donor-disabled case vs predecessor         " + rows[-1]["detail"])

    print()
    print("CRITERION CAN FIRE - drop one criterion, the fixture only it rejects must flip")
    print("-" * 110)
    ga, gb, vs = fx_partial_plus_similarity()
    base, mut = verdict(ga, gb, vs), verdict(ga, gb, vs, drop=("C2",))
    check("C2 fires: partial overwrite", (not base["assay"]["pass"]) and mut["assay"]["pass"]
          and base["assay"]["C4_majority"] and base["assay"]["C5_majority"],
          "assay full=%s  without C2=%s" % (base["assay"]["pass"], mut["assay"]["pass"]))
    ga, gb, vs = fx_loader()
    base, mut = verdict(ga, gb, vs), verdict(ga, gb, vs, drop=("C4",))
    check("C4 fires: donor writes a loader, victim copies",
          (not base["assay"]["pass"]) and mut["assay"]["pass"]
          and base["assay"]["C2_majority"] and base["assay"]["C5_majority"],
          "assay full=%s  without C4=%s  auth=%.2f" % (base["assay"]["pass"], mut["assay"]["pass"],
                                                  base["assay"]["draws"][0]["donor_authored_share"]))
    ga, gb, vs = fx_block()
    base = verdict(ga, gb, vs, victim_override=[PULL_VICTIM])
    mut = verdict(ga, gb, vs, victim_override=[PULL_VICTIM], drop=("C5",))
    check("C5 fires: a victim able to pull the donor alone",
          (not base["assay"]["pass"]) and mut["assay"]["pass"]
          and base["assay"]["C2_majority"] and base["assay"]["C4_majority"],
          "assay full=%s  without C5=%s  dis=%.3f" % (base["assay"]["pass"], mut["assay"]["pass"],
                                                base["assay"]["draws"][0]["fid_donor_disabled"]))

    print()
    print("AUTHORSHIP READING - why prov (last value change) and not prov_lit (last write)")
    print("-" * 110)
    ga, gb, vs = fx_block()
    v = verdict(ga, gb, vs)
    d = v["assay"]["draws"][0]
    check("block copier: victim re-copies itself, same values",
          d["donor_authored_share"] >= 0.9 and d["donor_last_wrote_share"] < 0.9,
          "prov share=%.2f  prov_lit share=%.2f  (under prov_lit a genuine copier would FAIL)"
          % (d["donor_authored_share"], d["donor_last_wrote_share"]))

    print("-" * 110)
    print("T-P11:", "PASS" if ok else "FAIL", " (%d checks, %d failed)"
          % (sum(1 for r in rows if r["pass"] is not None),
             sum(1 for r in rows if r["pass"] is False)))
    (HERE.parent / "T_P11_RECEIPT.json").write_text(json.dumps(
        {"gate": "T-P11", "ok": ok, "constants": dict(C), "checks": rows}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
