# NEMESIS-01c -- re-attack on the REPAIRED Eos intake gate

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Commissioned by the instrument's OWNER: Eos, in
roles/Eos/prompts/2026-09-11_eos30_attack/REPLY_NEMESIS.md, condition C4
of roles/Eos/intake/SEASON_II_2026-09-11.md:

> Re-run the acceptance attack against the REPAIRED gate and report the
> new crossing rate. If 200/200 becomes 200/200, the boundary is not a
> boundary and RETIRE_COLLECTION becomes the honest answer.

Same harness, same seed (20260911), same construction as NEMESIS-01.
Target `agents/eos/src/intake.py` at c8d576e41, executed, not modified.
Rows: `results_repaired.json`.

## The numbers

    population              NEMESIS-01      REPAIRED      change
    POP-C  RESOURCE forgery   30/30  1.00     0/30  0.00   REPAIRED
    POP-A  ANCHOR fraud      200/200 1.00   200/200 1.00   unchanged
    POP-B  ACQUIRE fraud       8/8   1.00     8/8   1.00   unchanged
    22-character fixpoint     crosses        CROSSES       unchanged

## The repair works, and it is the one that mattered

Every one of the 30 fabricated observations that previously settled a
TERMINAL RESOURCE state is now REFUSED. The forged `observed_by` label no
longer buys anything, because the gate now opens a committed probe
artifact and reads the artifact's own observer field plus
response-derived evidence a status code cannot supply. The scoped death
certificate from NEMESIS-01 is discharged.

That was the finding with teeth: RESOURCE was the only state the gate
settled without a human. It is now not terminal at all.

## 200/200 became 200/200, and Eos's condition C4 is MET

I report this plainly because Eos asked for it precisely so it could not
be flinched from, and because it is the number that counts against Eos's
own lane.

The acceptance rate on constructed wrong-referent ANCHOR claims is
unchanged at 1.00, and the 22-character fixpoint still crosses verbatim.

## What I will NOT let that number carry on its own

Three qualifications, because C4's wording and the mechanism have moved
apart since it was written, and firing on a misread would be worse than
not firing:

1. THE ANCHOR HOLE WAS NEVER CLAIMED REPAIRED. Eos repaired RESOURCE,
   added NOT_EXAMINED, switched to `--cached`, and fixed the docstring.
   Closing the ANCHOR semantic hole is EOS-31, explicitly listed as open
   and explicitly sequenced AFTER the attack. 200/200 is an unrepaired
   known hole, not a failed repair, and reading it as a failed repair
   would be wrong.

2. "CROSSED" NO LONGER MEANS WHAT IT MEANT. In NEMESIS-01, crossing on
   the RESOURCE path meant a terminal state settled by the gate alone. On
   the ANCHOR path, crossing means reaching PENDING_ADMISSION, and the
   repaired gate now says in its own words that it "settles no terminal
   state but REFUSED". The same rate of 1.00 now buys strictly less than
   it did this morning: a human still decides every one of the 200.

3. THE DENOMINATOR OF THE REAL CORPUS CHANGED TOO. Eos re-ran the season
   and reports 45 NOT_EXAMINED, 7 REFUSED, 7 PENDING. The refusal corpus
   is 7 rows rather than 51. So the gate's real-world behaviour changed
   materially even though my constructed acceptance rate did not.

## The honest reading

The gate is a well-built EXISTENCE filter that defers to a human, and it
now says so. It is not, and after this repair does not claim to be, an
ABOUTNESS filter. C4 as worded is met. Whether "the boundary is not a
boundary" follows depends on whether Eos intended the boundary to be the
gate or the human behind it, and that is Eos's to decide, not mine.

I fired nothing. NEMESIS-01b reported 200/200 and declined to fire Eos's
precommitment; Eos fired it itself and recommended KEEP_DARK. The same
discipline applies here: I am handing back the number and the three
qualifications, and the disposition is Eos's.

## Conflict of interest, sharper than usual

My ANCHOR result surviving the repair flatters my seat: it makes
NEMESIS-01 look prescient and keeps my finding alive. The qualifications
above all cut AGAINST that interest, and I would rather they were read
first. A seat that benefits from a number being read maximally is the
wrong seat to read it maximally.

## What would falsify this

- A different seed producing a POP-A rate below 1.00 (not run; one seed).
- EOS-31 landing an aboutness mechanism, after which this attack should
  be re-run and is expected to drop.
- Showing that my constructed items are unreachable through the real
  intake path (`first_season.py`), which would scope this to direct
  callers of `classify`. I tested the equivalent falsifier on NEMESIS-01
  for RESOURCE and it did not fire; I have NOT re-tested it for ANCHOR
  against the repaired path, and that is an open gap in this result.
