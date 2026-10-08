# EXP-01 RESULT -- LOCAL SYSID on DISCOVERY batch 0 (EXPLORATORY; 2026-10-08)

Data: EXP-01_discovery_b0.jsonl (120 worlds, 30/family; sha256 b11925ebe1ea9225...). Analysis exactly as preregistered
(exp01_analyse.py): EXP-01_analysis_A.json / _B.json. Discovery only: no confirmation data exists.

## Preregistered decisions
- H-LOCAL / C4-L-0001: SURVIVED_PROVISIONAL by the rule (U vs T2a .193; 0 families below T2a).
- C4-L-0003: SURVIVED_PROVISIONAL by the rule (U vs T2a .286; 0 families below T2a). Higher mean within-family BA
  than L-0001, so L-0003 is the single candidate carried forward (ADDENDUM 1). L-0001 recorded, not discarded.
- L-0002 (open logistic on LOCAL coords) does not beat L-0001 (gap -.04): the specific composition is not FAILED.

## What the rule hides (read this before the verdicts)
| family | n (FUNCTIONAL) | L-0001 | L-0003 | T3-DOWN | T2a |
|---|---|---|---|---|---|
| rnn | 26 (20) | .90 | 1.00 | .50 | .50 |
| graph | 27 (13) | .68 | .86 | .79 | .50 |
| stig | 30 (27) | .50 | .50 | 1.00 | .50 |
| theseus_sediment | 30 (30) | undefined | undefined | undefined | undefined |
(within-family BA under LOFO, Certificate A labels; B labels give the same picture; A/B agreement .97-1.00)
1. The FOREIGN family tested nothing: under its natural distribution every world is FUNCTIONAL, so no BA is
   defined and it drops out. The preregistered "sediment alone fails" check was vacuous. => the authorship-
   independence purpose of the foreign family is NOT YET SERVED. A challenge proposal is required.
2. stig: both LOCAL laws predict all-FUNCTIONAL (BA .5); T3-DOWN is perfect. All 3 PASSIVE worlds have v = 2,
   k = 2: the agent moves out of its own 3-cell sensing window before the query. Usability is set by CAUSAL
   REACHABILITY of a moving sensor. INSTRUMENT DEFECT co-located: resample perturbations teleport the integer
   agent position, so lam > 1 (up to 2.33) in a decaying field and vis up to 55. The local linear description
   is FRAME-DEPENDENT: in agent-centred coordinates the field is a pure shift (linear, non-normal) that J could
   represent; in absolute coordinates it is not. => the LOCAL vocabulary is not invariant to nonlinear,
   physics-preserving re-encodings (T-C1).
3. Mean within-family uplift of L-0003 over T3-DOWN is +.024 (A labels): over the families that carry
   information, the local law barely beats the zero-parameter certificate rule; it wins on rnn (1.00 vs .50),
   loses on stig (.50 vs 1.00), and is close on graph (.86 vs .79).
4. Literature prediction (notes/LITERATURE_2026-10-08.md) half wrong: L-0003 is best on rnn as predicted, but
   GOOD on the threshold graph family, where linear response was expected to fail.

## Classification
H-LOCAL: SURVIVED_PROVISIONAL (rule) / evidence base = 2 informative families (rnn, graph), both Cosmos/C3-authored.
stig: FAILED for the local laws (reachability) + INSTRUMENT_DEFECT (frame-dependent linearization).
foreign family: NOT_REACHED (uninformative under P).
Next: EXP-02 (DISCOVERY batch 1) with label-blind challenge proposals so sediment and stig carry information;
an egocentric re-encoding test of the LOCAL description (T-C1).
