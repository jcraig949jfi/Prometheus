# HT-37e311ce05 / W6 -- design notes (Pass 3 v2)

Prompt: hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...bd461).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md. Layer: an
implemented candidate with controls only; no treatment exists.

## What the world tests

Mechanisms M2 (selection for transverse null spaces) and M9 (coherence
minimisation as division of labour), lens L1 (null-space cartography).
Pairs decode a 3-sparse environment (n=32) by OMP from their stacked rows,
5 host rows plus 5 symbiont rows taken from a palette of 24 coherence
classes (a base row and a near-copy, cos about 0.95). A symbiont row
coherent with one of its host's rows adds almost nothing to the stacked
matrix. The claim: under vertical transmission selection makes each
symbiont complementary to ITS OWN host (low R_own, while R_other, its
redundancy with the other hosts, stays high: specificity D > 0), and cuts
own-partner redundancy to at most half of what horizontal transmission
with identical selection reaches.

## Why it avoids the earlier failures of this program

- W1: an unattainable difference clause and a positive control that did
  not need the mechanism. Here the positive control is a population that is
  complementary and partner-specific by construction, and it meets both
  clauses (D 0.211, ratio 0.0) while the twin meets neither (D -0.001,
  ratio 0.922).
- W4: conjoined mechanisms and a twin that already satisfied one conjunct.
  Here both clauses read one quantity family (redundancy geometry), and
  each was checked for discrimination separately.
- An earlier unprobed design for this mechanism in the program used exact
  index duplication as its redundancy measure, which a symbiont can avoid
  without any geometry; the coherence classes here make near-copies count as
  redundant (stupid explanation 3 is therefore testable, not built in).
- Self-contained: no reference to any other world.

## Controls

- POSITIVE_CONTROL: 50 pairs, host and symbiont each 5 distinct classes,
  disjoint within a pair, drawn independently across pairs (base or copy
  chosen at random).
- NULL_TWIN: horizontal transmission, truncation of the top half of pairs on
  success over 8 common signals per generation, symbionts re-paired at random
  every generation; NULL_TWIN_B is an independent replicate (different
  evolution stream, same world and signals) used as the twin's own S2
  reference.
- CHEAT: injected R_own 0, R_other 0.3 with the twin's genomes stored; the
  audit recomputes redundancy from stored genomes and flags 10/10 CHEAT rows
  and 0 control rows; the ruler also fires on CHEAT.

## Ambiguities resolved

1. S2 compares the treatment with the twin. Its "twin value" is the twin's
   ratio against an independent twin replicate (0.92); its "positive value"
   is PC R_own / twin R_own (0.0). treatment_must_reach is the number
   0.5 x twin R_own = 0.0518 on these rows; the probe recomputes it from its
   own rerun twin in the same code path.
2. The horizontal twin is not a random baseline: it evolved population-level
   complementarity (R_own 0.10 vs about 0.21 for random pairs). That is
   recorded as a finding about the control, and it is why S2 compares with
   the twin rather than with random pairs.
3. Redundancy is measured on the final population as paired at the end of
   the last generation (after re-pairing in the twin).
4. The vertical treatment is the same generation loop without the re-pairing
   line; that loop is not written here.

## Known risks for the treatment (not repaired, stated)

- Truncation selection over 200 generations may coalesce a vertical
  population onto a few lineages. Then R_other approaches R_own and D can be
  near 0 even if every pair is complementary; the world would read F1
  (no specificity) while S2 might pass. That reading is correct for the
  hypothesis as written (partner-specific complementarity), and the
  probe should report S2 separately.
- Stupid explanation 2 (clonal family structure raising R_other) predicts
  D > 0 without selection; a vertical arm with random selection is the
  falsifier for Pass 4, not part of this world.
