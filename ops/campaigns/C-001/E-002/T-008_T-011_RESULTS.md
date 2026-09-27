# E-002 T-008 .. T-011 -- results (Artemis, ubu002, 2026-09-27)

Criterion under test: T-007_CRITERION.md, which states C-OP (the candidate), C-MAJ (the frozen v0.2.1 rule), failure modes F1-F4
and meaningfulness tests M1-M3. Code: archaeon/causal_lens/e002_continuity.py (stdlib) and e002_pte.py (numpy + torch CPU; PTE
engine read-only). Outputs: out/*.json. Tests: archaeon/tests/test_e002_continuity.py.

## T-008 -- synthetic recombination fixtures (out/T-008_fixtures.json)
All 15 corpus_v02 fixtures were read under C-MAJ, and under C-OP with the operator {undeclared | exchangeable | privileged}.
- **No fixture declares an operator.** The four recombination fixtures (v01 50/50, v02 60/40, v12 34/33/33, v14 many-to-many
  50/50) record realized shares only. So C-OP's verdict on them is fixed entirely by a declaration the fixtures do not contain:
  * undeclared: NOT_IDENTIFIABLE (4/4);
  * exchangeable: ILL_POSED (4/4);
  * privileged: equal to C-MAJ.
  v02 flips between `hA` and ILL_POSED. The corpus expectation "v02 -> hA" was written under a declared MAJORITY *rule*, which is not
  an operator declaration (F3 confirmed).
- v09/v10 (donor/victim) carry asymmetric roles implicitly (executor_body vs host_body), so the privileged reading is the right
  one there. It equals C-MAJ.
- The 9 single-contributor fixtures give the same answer under every reading. v13 has no complete share evidence (NI, unchanged).
- Every C-OP value, ILL_POSED included, is **representable in the frozen v0.2 validator with 0 violations**. C-OP needs no schema
  change, only a declared operator and a rule kind that `continuity()` does not implement.

## T-009 -- the preserved PTE cases
### Reproduction first (out/T-009_repro.json)
The regress_v02.pte_arch recipe (same group, seed 20260927, same genome set, frozen behavioural criterion) was re-run on ubu002:
Linux, numpy 2.3.5, torch 2.9.1 CPU. M2 is Windows.
- Result: **48/48 children identical to out_v02/PTE_ARCH_V02.json** (from_a, hu_continuity, arch, degenerate); parent signatures
  identical; 24 s, 363 MB.
- The in-GA replay behind out_v02/PTE_V02.json reproduced all 16 crossover mask counts (out/T-009_ga.json; 27 s).
- The specimen's genome is 1 rule x 16 instructions x 5 fields; the GA cell's is 64 instructions.

### C-OP on PTE
PTE's crossover (search.py:76-78, `m = g.random < 0.5`) is exchangeable in (a, b), and search.evolve draws both parents the same way
(:119-121). So C-OP says ILL_POSED for every crossover child between distinct genomes.

### What the preserved record did not show (from the kept masks and parents)
- **4 of the 16 GA crossovers are self-crosses (a == b).** At pop 16, truncation keeps 4 parents, so the chance is 1/4, as observed.
  The record's "1/16 exact tie -> ILL_POSED" (32/32) **is one of these self-crosses.** Its child is its single parent plus mutation,
  so continuity is trivially well-posed. In the other 3 self-crosses, C-MAJ "decided" a or b, two labels of one genome. C-OP's
  distinct-HU clause gets all 4 right.
- The 12 real GA crossovers differ at only 10-28 of 64 instructions in 7 cases; the parents are close relatives.

## T-010 -- where does each criterion invent an answer?
**C-MAJ invents continuity.** Across the 16 GA crossovers:
- **M1 fails in 10 of the 15 "decided" answers**: flipping only causally inert mask bits (positions where a == b, where the child is
  byte-identical either way) can reverse the answer.
- The one flow margin that clears the operator's null (45/19, p = 0.0016) is **5/5 on the differing instructions**. Its
  "significance" is entirely inert bits.
- On difference-making shares, **0/16 clear M2**.
- C-MAJ over differing instructions only disagrees with C-MAJ over flow in 4/12 real crossovers.

**C-OP invents ill-posedness at the extremes (F1 confirmed).** A controlled sweep on the same specimen took, for each pair and each
k = 0..16, 6 children with exactly k instructions from a (204 children, 85 s). Its three results:
- k = 16 and k = 0 are exact parent copies, and behave identically to that parent (12/12 and 12/12). C-OP still calls them
  ILL_POSED.
- Near the ends, the child keeps its majority parent's exact behaviour: pair 2 k = 14: 4/6, k = 15: 3/6 (parent a). The one
  non-ceiling identity, parent b's imperfect vector, survives at k = 1: 2/6 and k = 2: 1/6, and **never at k >= 3**.
- Every exact behavioural identity with a non-ceiling parent occurred with that parent as the majority material contributor. No case
  contradicts the majority at the extremes.

**Privileged operators (F2).** The evidence in Git is limited, and none of it shows a thin margin:
- Archaeon's block-13 sample (200 events, fixtures_v03): its 15 two-source events are all >= 27/32.
- NPE (34 births, out_v02/NPE_V02.json) is decided only at donor share >= 0.906 with fid_init ~ 0. The 25 undecided births carry
  0.44-0.84 same-value mass, and the v0.2 NPE adapter already returns NI for them. That is the M1 logic, applied by that adapter,
  though not by the PTE adapter.
- The full Archaeon block-13 margins (53,185 events) and BEE's per-birth margins (845 runs) are **not in Git** (M2:
  C:\Prometheus-data\evidence\portability01_2026-09-26\). F2's breadth is unresolved.

## T-011 -- material continuity vs architecture-level continuity (out/T-009_arch.json)
- **The preserved "3/48" does not measure agreement.**
  * Pair 1's parents are two different perfect champions with identical signatures (all 1.0). Behaviour cannot distinguish a from
    b for any of its 24 children (NI by B7).
  * In pair 2, parent a is at the ceiling (all 1.0), so all 3 preserved matches (same_as_a at from_a 14, 13, 9) mean "perfect",
    which is the same B7 ceiling reading.
  * Informative agreements: 0. Informative contradictions: 0. The 45 new_class children say nothing either way.
- **A graded behavioural criterion is not usable.** "Nearer parent by L1 of the accuracy vectors" picks the weaker parent b for
  5-6/6 children at every k <= 12. A broken child (mean accuracy ~ 0.5, the zero-genome control level) is simply nearer the
  imperfect parent. The distance measures performance, not organisation. On the preserved pair-2 children it agrees with C-MAJ
  11/21, which is chance.
- **Mixing mostly destroys the organisation.** Pair 2 at k = 3..13:
  * 0/66 keep b's identity;
  * 5/66 are "perfect" (a's ceiling);
  * 7/66 are degenerate (equal to the zero-genome control).
  Pair 1 at k = 3..13: 13/66 mosaics of two perfect programs are themselves perfect, which is behaviourally "both parents". That is the
  ruling's "ILL_POSED continuity + meaningful architecture class" shape. But the class is the performance ceiling, so it is not an
  architecture identity under B7.
- Conclusion: in this specimen, the only architecture-level continuity is exact behavioural identity with a non-ceiling parent. It
  exists only for children with <= 2/16 foreign instructions. Where it exists it names the material majority. Where material
  continuity is ill-posed, architecture offers no rescue: its reading is NOT_IDENTIFIABLE, not a positive class.
