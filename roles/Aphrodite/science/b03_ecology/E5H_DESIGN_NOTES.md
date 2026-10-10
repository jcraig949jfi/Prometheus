# E5-H design notes: W9-H × W5P integration (D5), W08 discovery pilot, recommended frozen E5-H

Ecology lead, branch `aphrodite/b03-eco` (merged coordinator branch `aphrodite/beta01-2026-10-04`: W5P @1e169a577,
W9-H @dbde4556f). All data here is **EXPOSED development data** (W9-H pilot seeds 0–2). None of it is confirmatory.
The machinery was not changed. The W5P donor is `engine/w5p/harness.run` (rule g11, promotion ON, meter off).
No donor read `W9H_TRUTH.json`; truth is joined only in `w9h_pilot_discovery.py score`.

Files:
- `w9h_w5p_cert.py` → `pilot/W9H_W5P_CERT.jsonl`, `pilot/W9H_W5P_CERT_SUMMARY.json`
- `w9h_pilot_discovery.py` → `discovery/ROLES.json`, `discovery/<stage>.jsonl`, `discovery/SCORE.json`

## 0. CPU used (hard budget 1.5 core-h; ≤2 workers; OMP_NUM_THREADS=1)

| item | CPU s |
|---|---|
| D5 W5P certification walks (50 families × 2 libs × 2 cells @1M) | 329 |
| D5 static coverage check | ~50 |
| roles + organ-observability count + 4 scoring passes | ~250 (estimate, not metered) |
| (a) gen1_30k, 3 donors | 120 |
| (b) cand_300k, 3 candidacy probes (full g11 at 300k not needed: 0 candidates) | 479 |
| (c) oracle_30k, 3 donors | 214 |
| (c) oracle_cand_300k, 3 probes | 1065 |
| (c) oracle_300k, 3 full g11 donors | 1862 (seed 0 alone 1120; 263M charges) |
| (c) oracle_tx, 47 L2 families × 2 cells @1M | 301 |
| **total** | **≈ 4,670 s ≈ 1.30 core-h** (≤ 2 workers throughout) |

Per-donor CPU comes from `time.process_time` in the worker. Walls were similar.

## 1. D5: certification with W5P's actual promotion machinery

**Method.**
- Every inner mechanism S_a is promoted with `Promoted.from_schema`.
- PROMOTED_A entries are the W5P `schema_entry` (`promote.instantiate`) of `S_x[H := P_a({H})]`, one per seed
  mechanism x. PROMOTED_ORACLE is the entry of `S_b[H := P_a({H})]`.
- Both are walked on the same 2 transfer cells at cap 1M, with the T4 v1a qualifier.
- PRISTINE and FLAT are reused, because the cells are identical.
- Scope: 50 T4-qualified L2 families, 47 of them admitted.

**Result: NOT ACCEPTED AS-IS.** Verdicts match on **31/47** admitted L2 families (34/50 T4-qualified).

| | expansion (W9-H) | W5P |
|---|---|---|
| CERTIFIED_DEPTH2 (admitted L2) | 44 | **28** |
| oracle-certified | 44 | 28 |
| witness body inside the promoted entries (static) | 47/47 | 21/47 |
| mean promoted bodies per library | 1384 | 196 |

- **All 16 mismatches go one way:** certified by expansion, not by W5P. W5P never certifies a family that expansion
  rejects.
- **All 16 are explained by W5P's instantiation rule** (`g5p_admissible`: depth ≤ 3 counting P as one node, and every
  binary node has an atom child, with fillers = LEVEL1 + P(atom)). In every mismatch the witness `S_b[P_a(e)]` with
  non-atom filler e is not in W5P's instantiation set (0 mismatches have the witness statically inside the entry).
  Many of these mismatched families come from W2/W2S outer mechanisms.
- 8 of the 28 W5P-certified families are reached through an equivalent program, not the witness body itself.
- **W5P-certified families still cover all 8 certified compositions** (per seed: 6 / 11 / 11 of 15 / 11 / 18
  expansion-certified).

**Consequence.** For any E5-H run under W5P, the depth-2 positive set must be **W5P-certified**: certified with the
W5P library builder, not by my unrestricted expansion. Either restrict TRANSFER/residual L2 families to W5P-certified
ones, or (preferred, decision E-3) make the generator draw L2 fillers only where `S_b[P_a(e)]` is
`g5p_admissible`. Here W5P's shape rule, not reachability, is the binding constraint.

## 2. Role rule W9H-R1 (D4): minimal, arm-neutral change

The A19 OBSERVE floor (0 < p_PRISTINE ≤ .75) has pools of **3 / 6 / 1** families on seeds 0 / 1 / 2. A19 + T12 extras
needs 4 + 6 = 10, so the A19 rule is unfillable on every seed, and on 2 of 3 seeds even the base 4 cannot be filled.
This is structural: W9-H removes organ-equivalent L1/L2 bodies precisely so that pristine cannot reach them.

**W9H-R1:**
- Pool = the seed's admitted families. W9-H admission already applies the A19 window p_PRISTINE ≤ .75.
- Seeded shuffle `APHRODITE/W9H/ROLES/<seed>`; OBSERVE 10, VALIDATE 12 (the O10/V12 widths of A19 + extras),
  TRANSFER = the rest (23/22/24).

The only change is that the p > 0 floor is dropped. The rule:
- reads only foundry fields, never generator truth or any treatment outcome;
- is applied before any donor, and identically for every arm;
- keeps the A19 widths.

Its effect is to give the pristine learner OBSERVE tasks it mostly cannot solve. **That is the gen-1 discovery
problem, measured below, and not hidden.** Realised OBSERVE composition (L0/L1/L2): 3/4/3, 2/4/4, 2/4/4.

## 3. W08 discovery pilot (seeds 0–2, W5P g11, promotion ON)

**(a) GEN-1 at escrow 30k** (pristine start)

| seed | observed programs (of 20 cells) | classes | derived schemas | selected | true mechanism? | CPU s |
|---|---|---|---|---|---|---|
| 0 | 3 | 2 | 0 | INHERITED | no | 62 |
| 1 | 1 | 1 | 0 | INHERITED | no | 50 |
| 2 | 0 | 0 | 0 | INHERITED | no | 9 |

**(b) GEN-1 at escrow 300k**, applied identically to observation, selection and Cell.cost. Recommended as the single
raised escrow: it is the smallest round value that walks the whole PRISTINE organ entry (151,920 candidates).
- A candidacy probe ran first, with the selector stubbed (no validation walks). It found **0 derived schemas on all
  3 seeds** (observed programs 6 / 6 / 3, 2 classes each).
- So no true mechanism was ever a candidate, and the full g11 donor at 300k was not run: there was nothing to select.
- CPU: 167 / 188 / 124 s.

**Verdict on gen-1: gen-1 W5P donors cannot derive level-1 mechanisms from a pristine start at 30k or at 300k.**
The first broken link is **CANDIDACY**, caused by **SEARCH_BUDGET at observation**.
- PRISTINE observes almost none of the L1/L2 OBSERVE families at either escrow (foundry: 1/60 L1 families reachable
  at 30k, 9/60 at 1M).
- With ≤ 2 classes there is no LGG pair from the same mechanism, so nothing is derived.

This is a result, not a tuning target. The world was built so that pristine cannot reach level-1 families. That is
what creates the learning opportunity, and it also starves a pristine learner of observations of those families.

**(c) Known-positive gen-2 control** (START = all 6 TRUE level-1 mechanisms of the seed as schema entries, so W5P P1
promotes all 6, then PRISTINE; rule g11)

| | seed 0 | seed 1 | seed 2 |
|---|---|---|---|
| 30k: observed / classes / derived (with P) | 4 / 2 / 2 (1) | 0 / 0 / 0 (0) | 4 / 2 / 4 (2) |
| 30k: selected | INHERITED | INHERITED | `((acc + {H}) + v)` = true M0, depth 1 |
| 30k: non-trivial depth-2 derived | 0 (only bare P({H})) | 0 | 1: `P_M0(gcd(H, first))` |
| 30k: non-trivial depth-2 SELECTED | no | no | no |
| 300k probe: observed / classes / derived (with P) | 24 / 9 / 26 (12) | 13 / 6 / 9 (4) | 16 / 7 / 7 (3) |
| 300k: non-trivial depth-2 candidates | 9 (all `P_M4(...)`) | 3 | 2 |
| any equal to a TRUE composition S_b∘P_a? | no | no | no |
| 300k full g11: selected | INHERITED | `(gcd(acc, last - {H}) + v)`, depth 1, not a true mechanism (a base-form re-spelling of M3 with H := last - H) | `((acc + {H}) + v)` = M0, depth 1 |
| 300k: non-trivial depth-2 SELECTED | **no** | **no** | **no** |
| 300k full g11: CPU s (search charges) | 1120 (263M) | 395 (105M) | 347 (106M) |

Transfer of the 30k oracle-selected libraries (2 cells × 1M, admitted L2 families; PRISTINE on identical cells):

| seed | L2 families | selected-library reach | pristine reach | reached by selected, not pristine | of which EXTEND (body ∉ G5) |
|---|---|---|---|---|---|
| 0 | 15 | 10 | 0 | 10 | 0 (REORDER through the flat mechanism entries) |
| 1 | 14 | 3 | 3 | 0 | 0 |
| 2 | 18 | 7 | 0 | 7 | **5** |

The 5 EXTEND families on seed 2 are reached through W5P's filler rule. With a non-empty registry, the instantiation
of the selected **depth-1** schema M0 includes fillers P_x(atom), which give depth-2 compositions outside G5. Under
D4 / A1 these do **not** count as a depth-2 mechanism, because the selected schema has dag_depth 1. Tribunal false
positives on these walks: 0.

**Verdict on (c): the known-positive gen-2 control FAILS at both 30k and 300k on the D4/A1 criterion.**
- Even with the true level-1 mechanisms promoted, the W5P donor never selects a non-trivial depth-2 schema.
- At 30k the first broken link is CANDIDACY. A start library of 6 schema entries holds ~350k candidates (each entry is
  2 × 161 × 180 = 57,960), so observation at 30k never leaves the first entry, and observation is unchanged under
  promotion (W5P D1).
- At 300k candidates do appear: depth-2 schemas are derived on 3/3 seeds. But none is a true composition. They are
  `P_outer(base-inner)` forms, built from G5 bodies that happened to fold. The g11 selection instead picked a
  re-derived depth-1 mechanism.
- So at 300k the link that breaks is the match between **CANDIDACY and SELECTION**: the true compositions are never
  candidates, because L2 bodies are outside G5 and observation cannot see them (W5P limitation 1).
- Libraries that inherit the true mechanisms do reach many L2 families that pristine does not (17 of 47), but almost
  all by REORDER.

## 4. Recommended frozen E5-H (structured-world R8 under promotion)

**Recommendation: do not launch a confirmatory E5-H in its current form.** On exposed data its own known-positive
control already fails (§3c). Under the E5N rules it would therefore return INSTRUMENT_UNVALIDATED, or a NO that the
assay could not have avoided. The two blockers are both instrument-side:
1. **Observation cannot see depth-2 structure** (W5P D1, frozen in E5N). True compositions never become candidates.
2. **The level-1 mechanisms are invisible to a pristine learner.** This follows from the W9-H learning-opportunity
   design combined with escrow.

If the coordinator still wants an E5-H confirmatory, this is the design that is the most defensible and cheapest.
Freeze it only after a pre-freeze known-positive gate passes on fresh exposed seeds:

| item | frozen value |
|---|---|
| world | W9-H CONFIG v2 (new sha). v1 plus: L2 fillers restricted to those with `S_b[P_a(e)]` g5p_admissible (decision E-3), and level quotas L0 16 / L1 40 / L2 40 (96 families). Admission as v1. TRANSFER and residual L2 restricted to **W5P-certified** families |
| seeds | fresh block **W9H:100–107** (8 seeds). Pilot 0–2 stays exposed and excluded |
| roles | W9H-R1 (OBSERVE 10 / VALIDATE 12 / rest TRANSFER) |
| escrow | **300k** for observation, selection and Cell.cost in every arm; transfer cap 1M; T4 v1a |
| machinery | W5P donor, rule g11, promotion ON, compose OFF, held = [] |
| arms | PRISTINE; L_gen1 (the g11 donor's selected library from a pristine start on the same seed); **L_ORACLE** (start = the seed's true level-1 mechanisms; the known-positive control, never a treatment); L_SHAM (start = the same number of mechanisms drawn by the W9-H mechanism grammar from a disjoint seed stream `APHRODITE/W9H/SHAM/<seed>`, screened identically) |
| endpoint | new acquisition on the common residual (E5N §4.2): residual L2 TRANSFER families that no START library reaches, counted when the recipient's selected library reaches them in ≥ 1 of 2 cells at 1M. Every acquisition split into REORDER/EXTEND |
| depth-2 attribution | E5N A1.1: a seed counts only if the SELECTED schema is non-trivial depth-2 AND ≥ 1 acquired residual family's first qualified program is EXTEND and comes from a promoted-form entry of the selected library |
| known-positive gate (pre-freeze, mandatory) | L_ORACLE must select a non-trivial depth-2 schema with attributed EXTEND acquisition on ≥ 3 of 8 seeds. Otherwise INSTRUMENT_UNVALIDATED, and the treatment contrasts are not interpreted |
| primary test | L_gen1 − L_SHAM on residual acquisition, exact sign-flip over seeds, one-sided 0.05. L_ORACLE − L_SHAM is reported as the control |

**Projected cost** (from pilot timings; contended host):
- World: gen + foundry + W5P certification ≈ 0.5 core-h per seed (96 families).
- Donors at 300k: gen-1 ≈ 0.05–0.3 h (0.05 when nothing is derived); oracle ≈ 0.15–0.5 h (probe 3–11 min, then full g11 6–19 min; it scales with the derived-candidate count, 7–26 here); sham ≈ 0.15–0.3 h.
- Transfer: 4 libraries × ~25 families × 2 × 1M ≈ 0.25 h.
- Total ≈ 1.1–1.6 core-h per seed, so **≈ 9–13 core-h for 8 seeds**.
- The pre-freeze known-positive gate alone, on 3 fresh exposed seeds, costs ≈ 1.5 core-h.

**What the pilot predicts.** Unless the observation channel changes, the known-positive gate will fail as it did here.
The options below are **design decisions for the coordinator, not changes I made**:
- **(O1)** Admit OBSERVE-time promoted-application entries, reversing W5P D1. This is a freeze amendment, and it
  changes observation for every arm.
- **(O2)** Add an "observable" L1 tier: mechanism instances behaviourally equal to PRISTINE-organ bodies. They exist
  for 16 of 18 pilot mechanisms, with 3–44 fillers each, and are observable once the organ is walked (≤152k < 300k).
  These are exactly what my v1 organ-equivalence screen removed. Untested: their organ representatives may not
  share S's syntax, in which case LGG would not recover S.
- **(O3)** Accept the result: a structured world with certified, attainable depth-two mechanisms exists (W9-H, 28
  W5P-certified families), but the current learner's observation channel cannot discover them, at any affordable
  escrow, from either a pristine or an oracle start.

## 5. Decisions that must be frozen before any E5-H confirmatory
- **E-1:** whether to run E5-H at all, given §3 (my recommendation: not before O1 or O2 is decided and a known-positive
  gate passes on fresh exposed seeds).
- **E-2:** escrow (300k recommended; 30k fails the oracle at candidacy).
- **E-3:** W9-H CONFIG v2 (g5p-admissible L2 fillers, quotas), with sha frozen.
- **E-4:** the depth-2 positive set (W5P-certified only).
- **E-5:** role rule W9H-R1 (widths 10/12).
- **E-6:** the L_SHAM construction (disjoint grammar stream, same screens).
- **E-7:** the known-positive gate threshold (≥ 3/8 seeds).
- **E-8:** the observation channel (W5P D1 as frozen, vs O1 / O2).
- **E-9:** the seed block (100–107).
- **E-10:** whether L_ORACLE also serves as the second-generation donor for an R8-style chain (not recommended: it
  is a control).
