# HITL #78 — ROOT-CAUSED / UNREPAIRED / CURRENTLY UNCONTAMINATED

**Status set cycle 044. This closes #78 to further read-only investigation.**

## Why it is being closed rather than continued

Detection has done everything it can. The full arc it was capable of:

    symptom -> live reproduction -> blast radius -> schema mismatch
            -> writer-side localization -> confirmation of no current contamination

And the defect persists: **1035 rows, 0 accepted** as of cycle 044, up from 998 / 956 / 859 / 821.

The distinction that settles it:

> **epistemic closure ≠ operational closure**

I have epistemic closure — what is wrong, where, why, which side owns the fix, and what has not
yet been damaged. I cannot obtain operational closure, because the intervention is forbidden to me
by a standing constraint. **The read-only boundary, not detection capability, is now the binding
limit on #78.** Another read-only cycle answering "is it still broken?" has essentially zero
expected value.

Seventeen cycles of escalation did not fail for lack of evidence. They are waiting on an
authority I do not have.

## The finding, frozen

- `ergon/probe/assemble.py:load_prepass` filters `int(d.get("rep", -1)) != 1`.
- `ergon/probe/ledgers/campaign/p1_prepass.jsonl` writes `key: [rep, uid]` and has **no flat
  `rep`/`uid`**, so the `-1` default fails on every row.
- `campaign.py:best()` reads `tuple(r["key"])` correctly — two readers of one file, one right.
- **Writer-side by triangulation**: of three producers feeding this loader, two emit the flat
  schema it expects (`probe_prepass.jsonl`, `nearmiss_mix-M30_prepass.jsonl`, both loading
  correctly at a legitimate 50% rep-2 filter) and only the campaign writer deviates. **De facto
  contract, not canonical — no field-level schema exists anywhere in the repo.**
- Blast radius, pre-registered and held: `F-prom-retrieved` would ship ~58 tokens of *"no residue
  exists at this distance"* instead of ~2,070 tokens of residue — a null contrast presented as a
  treatment.
- **Not yet contaminated.** The append-only phase log holds exactly one record (P1); `Arms` is
  constructed in P3; no `p1_bandread.json` exists.

## Reactivation conditions — reopen ONLY on one of these

1. **The writer changes.** `ergon/probe/campaign.py` (`p1` / `push_jobs`) is modified.
2. **P1 advances to Arms.** A P3 or P4 record appears in `campaign_log.jsonl`, or
   `p1_bandread.json` appears. **This one is urgent**: it converts a latent defect into active
   contamination, and the arm affected is the one the campaign exists to measure.
3. **Patch authority becomes available.** James lifts the read-only constraint on ergon, or ergon
   picks it up.

The seven pinned tests in `techne/ladder_circuits/tests/test_hitl78_blast_radius.py` are built to
go **RED** when the seam is repaired. They are the standing detector for condition 1 and cost
0.2 s to run. Condition 2 is a two-line check on the phase log.

## What this changes about the loop's gate

"Real substrate" turned out not to be a sufficient bar. A read-only audit earns its cycle only if
its result can change something:

> **real substrate + actionable intervention** — or, where read-only by design,
> **real substrate + PREDECLARED DECISION CONSEQUENCE.**

An audit is worth running if its outcome can stop an experiment, distrust an arm, quarantine a
dataset, or trigger someone else's patch. If nothing downstream changes whatever the result, the
expected value collapses — and that is the state #78 reached several cycles ago.

The 80% real-substrate budget moves to targets where the loop can complete the whole arc:
**detect → intervene → measure postcondition.**
