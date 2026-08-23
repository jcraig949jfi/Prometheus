# Dispositions for the cycle-049 audit omissions — O-2, O-3, O-4

**Cycle 051.** Cycle 049 found four things committed to and never done. O-1 (Band H) was
**built** at cycle 050. The remaining three are closed here — each either done, withdrawn in
writing, or re-scoped, because the fault in O-3 was never the missed work. It was that a
commitment which became impossible was left standing silently. **Going quiet is not a
withdrawal**, so each of these gets a written disposition even where the disposition is "no".

## O-2 — the second pass restarted at R3, not R0 — CLOSED as a recorded deviation

`LOOP_CHARTER.md` Track 2: *"R0→R12, then Band H (H1, H2), then restart at R0."*
R0-R12 completed at cycle 021 (`b08fa6db`); cycle 022 opened the second pass at **R3**.

**Disposition: closed, no further action.** The ladder track was explicitly superseded at
cycle 041 — *"I've spent the last dozen cycles building tools to check my tools. That was
worth doing for a while and it isn't any more"* — and that regime change was announced in
writing at the time, unlike the skip itself. Re-running R0-R2 now would be completing a
sequence whose purpose was retired twenty-nine cycles ago.

**What remains true and is worth keeping:** the deviation was silent when it happened. The
charter said R0 and I started at R3 without a line saying so. That is the same defect as O-3
in a smaller form, and it is now in the traps ledger.

## O-3 — the R0 baseline lane — WITHDRAWN, and handed off rather than done

HITL #2 (cycle 001): *"should the R0 retrieval circuit become a permanent baseline lane in
the grading oracle? My stand: yes ... will wire it in a later cycle unless you object."*
`harmonia/services/grading_oracle.py` has never referenced it.

**Disposition: WITHDRAWN by Techne, with a handoff.** James lifted the read-only constraint on
2026-08-23 (#221), so I *can* now edit `harmonia/services/`. I am not going to, and the reason
is the boundary that came with the ruling: **cross-role fixes are permitted; cross-role science
is not.** Adding a permanent baseline lane to the grading oracle changes *what the oracle
measures* and how every reasoner's staircase is reported downstream. That is Harmonia's
experimental call, not a defect I am repairing.

**The handoff, so the withdrawal costs nothing:** the circuit exists and is tested at
`techne/ladder_circuits/r0_pattern.py` (exact-AST retrieval, abstains on isomorphs). The
argument for it is unchanged and is Band E's counter-baseline discriminator — every reasoner's
score should be reported as **lift over retrieval**, because a system that has memorised the
answer and a system that derived it are indistinguishable without that lane. **Harmonia owns
the decision.** If Harmonia wants it wired, I will wire it on request.

**The actual lesson, recorded:** this should have been withdrawn at cycle 002, the moment it
was clear the constraint made it impossible. It sat live and unactioned for 47 cycles because
nobody was tracking it, including me. An unwithdrawn commitment is worse than a refused one —
it reads as in-progress.

## O-4 — the Lane A/B reading experiment — RE-SCOPED, not withdrawn

Pre-registered at cycle 041 (`LANE_AB_READING_EXPERIMENT.md`), queued into the 20% at cycle
045, never run. The premise: *incidental review has never caught the guard-on-a-proxy class of
bug, but nobody has ever tried looking for it on purpose* — so does deliberate targeted reading
beat executable probes at finding them?

**Disposition: RE-SCOPED and returned to the queue, because the reason it was rejected has
dissolved.** Cycle 045 rejected it from the 80% budget on stated grounds: *"methodology on my
own modules — NOT real substrate; in the 80% it would be the instrument-eating-itself failure
mode wearing the regime change as a costume."* That reasoning was correct **under the read-only
constraint**, where my own modules were the only ones I could act on.

**#221 dissolved it.** The experiment can now run against real cross-role substrate, where a
found bug is a bug someone else depends on — which is exactly what cycle 045 said it lacked.

**And the case for running it got stronger, not weaker.** The proxy-trap count is now **five**:
cycles 043, 045, cycle 049's near-miss (top-level imports as a proxy for "wraps the library"),
ergon's `ledger_id`-prefix leak gate, and cycle 051's own — I predicted the `(x-2)^3` case would
be *hard* and it was trivially easy, because I used "repeated root" as a proxy for "ill-
conditioned M" when the real precondition is "repeated root **on the unit circle**". Five
instances, one of them in another role's code. That is a class, and no executable probe has
ever caught one of them.

**Not run this cycle** — cycle 051's budget went to the #266 build, and starting a second
pre-registered experiment inside it is the smuggling cycle 045 forbade. Queued as the next
non-build cycle's subject, with the target changed from "my own modules" to real cross-role
substrate.

*— Techne, cycle 051.*
