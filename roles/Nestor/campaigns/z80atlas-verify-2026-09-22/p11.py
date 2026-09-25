"""P-11. PAIR_EXECUTION copy causality: a matched randomized-victim assay.

WHY. The predecessor credited a pair-tape replication when the victim half ended >= 0.90
similar to the donor, < 0.90 similar to its own prior self, and the donor's context had
made at least n/4 writes outside its own span. That last clause counts WRITES, not whether
the writes carried the donor's bytes into the victim. It is satisfied by writes to the
tape padding, by writes of unrelated values that the victim later overwrites, and by a
genuine partial copy riding on similarity that was already there. All 1,031 admissible
spontaneous replicators in the 72-hour record come through this one clause, so it is
load-bearing. Specification: `P11_SPEC.md`; operator directive 2026-09-23 (S2).

THE ASSAY. For a candidate event the pair interaction is re-executed from the exact
pre-interaction state (both genomes, both register files and flags, execution order,
slice budget, world-op mask, copy-mutation rate), in a private tape, with a private RNG,
so the world's own trajectory is untouched. Per draw k of C["P11_DRAWS"]:

  1. the victim's n-byte half is replaced by uniform random bytes; its initial fidelity
     to the donor is recorded;
  2. PASS2 iff the victim half's final fidelity to the donor >= C["P11_FINAL_FIDELITY"];
  3. D = positions where the initial victim byte differed from the donor byte and the
     final victim byte equals it (donor-directed changes);
  4. PASS4 iff at least C["P11_AUTHORSHIP"] of D were authored by the donor during the
     interaction (per-position provenance, see AUTHORSHIP below); an empty D fails;
  5. the same draw is re-executed with the donor's writes outside its own half blocked
     (z8 OWN policy, same victim bytes, same copy RNG); PASS5 iff the victim's final
     fidelity to the donor stays < C["P11_CONTROL_MAX"].

A draw passes iff PASS2 and PASS4 and PASS5. The event is P-11 causal iff it satisfies
the predecessor criterion unchanged (phenotype and write-count prefilter) AND at least
C["P11_MAJORITY"] draws pass.

AUTHORSHIP. z8 records, per tape position, the context that last CHANGED the byte's value
(`ctx.prov`) and, separately, the context that last wrote it at all (`ctx.prov_lit`). The
criterion reads `prov`. A write that stores the value already present changes nothing and
so does not transfer authorship. This matters: a genuine block copier copies itself into
the victim, and the victim - now running the copied code - re-copies those same bytes
onto itself; under last-write-at-all it would become the "author" of bytes the donor
placed. `prov_lit` is reported beside every verdict so the reading can be checked.

Donor fidelity is measured against the donor's PRE-interaction genome, exactly as the
predecessor did. The assay reads the tape immediately after the interaction, before the
world applies its post-interaction mutation: it tests the interaction, not the mutation
operator.
"""
from __future__ import annotations

import hashlib
import json
import random

from constants import C


def fidelity(a, b):
    """Byte identity over the longer length; identical to world._fidelity."""
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    same = sum(1 for i in range(n) if a[i] == b[i])
    return same / max(len(a), len(b))


def event_seed(*parts):
    h = hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()
    return int(h[:16], 16)


def interact(z8, *, n, tape_len, ga, gb, st_a, st_b, budget, ops_mask, cmr, rng,
             victim_side=None, victim_bytes=None, donor_disabled=False):
    """One pair interaction, re-executed exactly as world._pair_epoch runs it.

    st_a / st_b are (regs, fz, fc) captured BEFORE the interaction. Organism a (tape
    offset 0, sense 0) runs first, then b (offset n, sense 1). Returns the final tape,
    the two provenance arrays (1 = a, 2 = b, 0 = untouched) and each side's writes_other.
    """
    tape = bytearray(tape_len)
    tape[0:len(ga)] = ga
    tape[n:n + len(gb)] = gb
    if victim_bytes is not None:
        v0 = 0 if victim_side == 0 else n
        tape[v0:v0 + n] = bytes(victim_bytes)[:n]
    prov = bytearray(tape_len)
    prov_lit = bytearray(tape_len)
    wo = [0, 0]
    for who, start, st in ((0, 0, st_a), (1, n, st_b)):
        donor = victim_side is not None and who != victim_side
        pol = z8.OWN if (donor_disabled and donor) else z8.ARENA
        ctx = z8.Ctx(tape, start, n, policy=pol, rng=rng, copy_mut_rate=cmr, sense=who)
        regs, fz, fc = st
        ctx.regs, ctx.fz, ctx.fc = (list(regs) if regs is not None else None), fz, fc
        ctx.prov, ctx.prov_lit, ctx.who = prov, prov_lit, who + 1
        z8.run(ctx, start, budget, ops_enabled=ops_mask)
        wo[who] = ctx.writes_other
    return tape, prov, prov_lit, wo


def directed_authorship(donor, init_half, final_half, prov_half, lit_half, donor_id):
    m = min(len(donor), len(init_half), len(final_half))
    D = [i for i in range(m) if init_half[i] != donor[i] and final_half[i] == donor[i]]
    auth = sum(1 for i in D if prov_half[i] == donor_id)
    auth_lit = sum(1 for i in D if lit_half[i] == donor_id)
    return D, auth, auth_lit


def assay(z8, *, n, tape_len, ga, gb, st_a, st_b, budget, ops_mask, cmr, victim_side,
          seed, victim_override=None, drop=()):
    """The randomized-victim assay for one candidate event.

    `victim_override` (tests only) supplies the "randomized" victim bytes per draw, so a
    test can prove a criterion is able to fire. `drop` (tests only) removes named
    criteria to build the mutant detectors the negative-control matrix runs against.
    """
    donor = bytes(gb if victim_side == 0 else ga)
    donor_id = 2 if victim_side == 0 else 1
    v0 = 0 if victim_side == 0 else n
    draws = []
    for k in range(C["P11_DRAWS"]):
        if victim_override is not None:
            vb = bytes(victim_override[k % len(victim_override)])[:n]
        else:
            vr = random.Random(event_seed(seed, "victim", k))
            vb = bytes(vr.randrange(256) for _ in range(n))
        cseed = event_seed(seed, "copy", k)
        kw = dict(n=n, tape_len=tape_len, ga=ga, gb=gb, st_a=st_a, st_b=st_b, budget=budget,
                  ops_mask=ops_mask, cmr=cmr, victim_side=victim_side, victim_bytes=vb)
        tape, prov, lit, wo = interact(z8, rng=random.Random(cseed), **kw)
        final = bytes(tape[v0:v0 + n])
        D, auth, auth_lit = directed_authorship(donor, vb, final, prov[v0:v0 + n],
                                                lit[v0:v0 + n], donor_id)
        tape_d, _, _, wo_d = interact(z8, rng=random.Random(cseed), donor_disabled=True, **kw)
        fid_init = fidelity(donor, vb)
        fid_final = fidelity(donor, final)
        fid_dis = fidelity(donor, bytes(tape_d[v0:v0 + n]))
        share = (auth / len(D)) if D else 0.0
        c2 = fid_final >= C["P11_FINAL_FIDELITY"] or "C2" in drop
        c4 = (bool(D) and share >= C["P11_AUTHORSHIP"]) or "C4" in drop
        c5 = fid_dis < C["P11_CONTROL_MAX"] or "C5" in drop
        draws.append({"k": k, "fid_init": round(fid_init, 4), "fid_final": round(fid_final, 4),
                      "n_directed": len(D), "donor_authored": auth,
                      "donor_authored_share": round(share, 4),
                      "donor_last_wrote_share": round(auth_lit / len(D), 4) if D else 0.0,
                      "fid_donor_disabled": round(fid_dis, 4),
                      "donor_writes_other": wo[1 - victim_side],
                      "C2": bool(c2), "C4": bool(c4), "C5": bool(c5),
                      "pass": bool(c2 and c4 and c5)})
    npass = sum(d["pass"] for d in draws)
    return {"pass": npass >= C["P11_MAJORITY"], "draws_passed": npass, "draws": draws,
            "C2_majority": sum(d["C2"] for d in draws) >= C["P11_MAJORITY"],
            "C4_majority": sum(d["C4"] for d in draws) >= C["P11_MAJORITY"],
            "C5_majority": sum(d["C5"] for d in draws) >= C["P11_MAJORITY"]}


def predecessor_accepts(fid_other, fid_self, donor_wrote, n):
    """The predecessor pair-tape criterion, verbatim in logic, thresholds from C."""
    return (fid_other >= C["PAIR_FID_OTHER_MIN"] and fid_self < C["PAIR_FID_SELF_MAX"]
            and donor_wrote >= C["PAIR_DONOR_WROTE_SHARE"] * n)


def ordinary_diagnostics(z8, *, n, tape_len, ga, gb, st_a, st_b, budget, ops_mask, cmr,
                         victim_side, seed, final_half, prov_half, lit_half):
    """Diagnostics on the OBSERVED event (not criteria): authorship of the donor-directed
    changes against the real victim, and the donor-disabled fidelity with the real victim."""
    donor = bytes(gb if victim_side == 0 else ga)
    old = bytes(ga if victim_side == 0 else gb)
    old_half = (old + bytes(n))[:n]
    donor_id = 2 if victim_side == 0 else 1
    D, auth, auth_lit = directed_authorship(donor, old_half, final_half, prov_half, lit_half,
                                            donor_id)
    tape_d, _, _, _ = interact(z8, n=n, tape_len=tape_len, ga=ga, gb=gb, st_a=st_a, st_b=st_b,
                               budget=budget, ops_mask=ops_mask, cmr=cmr,
                               rng=random.Random(event_seed(seed, "ordinary")),
                               victim_side=victim_side, donor_disabled=True)
    v0 = 0 if victim_side == 0 else n
    return {"fid_init_ordinary": round(fidelity(donor, old_half), 4),
            "n_directed_ordinary": len(D),
            "donor_authored_share_ordinary": round(auth / len(D), 4) if D else 0.0,
            "donor_last_wrote_share_ordinary": round(auth_lit / len(D), 4) if D else 0.0,
            "fid_donor_disabled_ordinary": round(fidelity(donor, bytes(tape_d[v0:v0 + n])), 4)}
