<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-AC; sha256(report)=c6fe74e182173dcc; delimited; see REPORT.provenance.json -->
# W2-AC: C1 headline counts re-derived at the correct independence units (Ananke Wave 2, 2026-10-01)

Worker: W2-AC. Directory: `roles/Ananke/research/harvest/wave2/W2-AC/`.

The work used numpy only on CPU: no engine runs, no torch, no git writes and no leases.

**Scripts.** Run each from the worktree root.
- `ac_c1_units.py`: C1 rows. Writes `out/c1_units.json`.
- `ac_b2_shared.py`: tests whether the shared B2 seeds couple families. Writes `out/b2_shared.json`.
- `ac_swap_units.py`: W-O audit, 733 rows. Writes `out/swap_units.json`. It recomputes the W-O label from n512/s512 and asserts 733/733 match.
- `ac_wz_units.py`: W-Z group classes. Writes `out/wz_units.json`.

## 0. Verdict

**Which unit is right.** Only one frame gives a rate:
- **A1 rows.** These are 352 distinct physics points with 352 distinct search seeds. Held worlds are keyed by each row's own seed. So the A1 row is already the correct unit.
- **Pooled counts.** The all-wave counts (50/196, 19/162, 97/155) are not rates. They mix targeted follow-ups, and their effective n is roughly 18–60.
- **Dependence in RELAY.** The 50 RELAY SIGNAL rows are only 6 independent discoveries (lineages). One lineage contributes 32 rows and another 14. Two of the 6 came from C-wave re-evolves at the top HOLD physics, not from the random frame.

**What survives.**

| Claim | Status |
|---|---|
| All existence claims | Survive |
| P4 (≤5% of A1 COMM_DEPENDENT) | Survives even at the one-sided 99% bound (8/352, upper 4.88%) |
| "84% of swap verdicts stay CHANCE" | Survives as "most". The number itself is row-weighted: specimen-weighted it is 72% [63, 80] |
| "One hop" | Survives only as a description of what was found. As a comparative law it is not supported: A1 one-hop 3/32 vs multi-hop 1/39, Fisher p = .32 |
| W-Z Pb "HELD" (25–45% band) | Becomes "consistent with the band": the specimen-clustered 95% CI is [18.6%, 41.3%] |

**Namespace and family effect (W2-N F7, r = .037).**
- It cannot touch any C1 SIGNAL or COMM_DEPENDENT count. All 789 evolve, transfer and adjudicate seeds are unique, so no held worlds are shared.
- On the W-O count, which ran in one namespace, it inflates the noise variance by 1.02 (worst case 1.46). The noise SD is about 3 against a between-specimen SD of 11.8, so it is negligible.
- B2 is different: cross-family reproductions use 100% identical seeds. The coupling there is measured at about 0, and the effects are ≥10 SE or deterministic. So the cross-family agreement is not a seed artefact. It is a common cause in the code (one decay rule acting on hand-written plants), which means it is not several independent confirmations either.

## 1. Main table

Notes on the table:
- n_eff is n / deff, with deff = cluster-bootstrap variance ÷ binomial variance.
- The ANOVA ICC is unusable here (negative) because cluster sizes are wildly unequal.
- All CIs are 95%.

| Claim | Rows | Independent units | Effective n | Rate at the correct unit (95% CI) | Survives? |
|---|---|---|---|---|---|
| RELAY 50/196 SIGNAL (L3, all waves) | 196 evolve (A 71, B 72, B2 33, C 11, D 8, E 1). The 50 SIGNAL rows are 17 conditions, 14 physics points and 6 lineages (86fc0105: 32; c939c3c7: 14) | Lineage for discovery; A1 row for the rate | 18 (lineage, deff 11.1); 47 (condition, deff 4.1) | Pooled ratio .255, lineage-cluster [.026, .409], which is not a rate. **A1: 4/71 = 5.6% [2.2, 13.6]** (BOOTT 3/71) | Count: no. As a rate: no. "RELAY SIGNAL exists and reproduces": yes (6 lineages; D replicates 6/8) |
| MAJ 19/162 | 162. The 19 SIGNAL rows are 10 conditions, 6 physics points and 5 lineages (57650798: 11) | Lineage / A1 row | 58 (lineage, deff 2.8) | Pooled .117 [.024, .182]. **A1: 3/70 = 4.3% [1.5, 11.9]** | Existence: yes. The SIGNAL is mostly a search draw: P(second search SIGNAL \| first SIGNAL) = .30, D replicates 3/8. E-W15 also applies |
| HOLD 97/155 | 155. The 97 SIGNAL rows are 50 conditions and 35 lineages (d49fdac8: 48; 13127335: 16) | Lineage / A1 row | 25 (lineage, deff 6.3) | Pooled .626 [.416, .760]. **A1: 34/70 = 48.6% [37.3, 60.0]**, identical 17/35 in both frames | "HOLD is commonly solved": yes. Quote the A1 rate, not 97/155. 7 of the 97 are lottery-eligible (setrule=0, rules>1; W2-Q) |
| A1 RELAY 4/71 | 71 | A1 row (already independent) | 71 | 5.6% [2.2, 13.6]; uniform 2/36, living 2/35; BOOTT 3/71 [0.9, 11.9]; t 2/71 | Yes. Estimand: P(one A1-budget search at a random physics finds SIGNAL). It mixes viability with search luck (E-W14) |
| A1 MAJ 3/70 | 70 | A1 row | 70 | 4.3% [1.5, 11.9]; uniform 1/35, living 2/35; unchanged under BOOTT | Yes, same estimand caveat |
| One-hop 48/50 | 50 SIGNAL rows: 15 of 17 conditions all one-hop; 4 of 6 lineages all one-hop; 3 of 4 A1 discoveries one-hop | Lineage (6), or the A1 contrast for any rate claim | 6 lineages; the A1 contrast is 32 vs 39 rows | A1 one-hop 3/32 = 9.4% [3.2, 24.2] vs multi-hop 1/39 = 2.6% [0.5, 13.2]. Difference +6.8 pp, Newcombe [−5.5, +21.8], Fisher p = .32. Global topology (one-hop by construction) is 0/11 in A1 | As a description of the lineages found: yes. "Evolved transport is one hop" as a law: no (multi-hop rarer, not shown absent) |
| COMM_DEPENDENT, A1 8/352 (P4) | 352. The 8 are RELAY 4 + MAJ 3 + HOLD 1 | A1 row | 352 | 2.3%, Clopper-Pearson (CP) [1.0, 4.4]; one-sided upper 4.06% (95%), 4.88% (99%); BOOTT 7/352; comm families 7/282 [1.0, 5.05] | P4 HELD survives at the right unit. But COMM_DEPENDENT is an exact alias of SIGNAL in RELAY/MAJ/XOR (asserted on all evolve rows), so it is not separate causal evidence |
| COMM_DEPENDENT, pooled (RELAY 50, MAJ 19, HOLD 3) | Same as the SIGNAL rows | As the SIGNAL rows above | As above | RELAY 50/50 and MAJ 19/19 are SIGNAL counts. HOLD 3/97 are all forced (zero_comm = .5, W2-E N6) | Only as SIGNAL counts at the lineage or A1 unit |
| "84% stay CHANCE" (W-O) | 733 rows = 430 measurements (138 exact + 165 mirror merges within specimen × offset) on 87 specimens, one namespace (0x600) | Specimen (normal run shared, r .993) | 239 rows (deff 3.1); 204 measurements (deff 2.1) | Rows 83.9% [78.9, 88.3]; measurements 80.9% [75.2, 86.0]; **specimen-equal 72% [63, 80]**. 47 specimens are all-CHANCE, 18 have none | "Most stay CHANCE": yes. "84%" as a general rate: no. Strata (measurements): W-F 67% [57, 76], W-I 89% [85, 94], HOLD 47% [26, 65], W-F\|HOLD 21% [3, 41] |
| 615 / 90 / 28 (CHANCE / FLIP / NO-EFFECT) | 733 → measurements 348 / 65 / 17 | Specimen | about 230 | FLIP: rows 12.3% [8.6, 17.0]; **specimen-equal 24% [16, 33]**; 17 specimens all-FLIP. NO-EFFECT 3.9% [1.5, 6.7] | Yes, but row weighting halves the per-specimen FLIP prevalence. The most-audited specimens are W-I RELAY, which are CHANCE-heavy |
| REL2 170 / 81 / 376 / 106 (FLIP_REL / NO_EFFECT_REL / CHANCE_REL / INDETERMINATE) | → measurements 117 / 52 / 201 / 60 | Specimen | FLIP_REL 109 (deff 3.9) | FLIP_REL: rows 23%, measurements 27% [20, 37], **specimen-equal 48% [39, 58]** (32 specimens all-FLIP_REL, 32 with none) | The class counts are right. Any share must state its weighting |
| W-Z Pb 35/124 CARRIER-NAMED | 124 groups, 59 specimens, 31 specimens with ≥1 | Specimen | about 60 (deff 2.1) | 28.2%, cluster [18.6, 41.3]; AMBIG 1/31 vs REST 34/93 | "HELD" (band 25–45%) becomes "point inside the band; the CI crosses 25%". The rate depends on which groups were selected |
| "Decay boundary reproduced in several families" (B2) | B2 seeds shared 100% across families: RELAY/FLIP/HOLD decay at base 0 used the same 12 seeds; economy RELAY/MAJ 9; rules MAJ/FLIP/XOR/HOLD 9. 21 cross-family census pairs have bit-identical random genome sets | One decay rule × hand-written plants | 1 phenomenon (HOLD counted 4× = 1) | Measured coupling: residual r, plant .034 (permutation p .75), sens .021, emit −.18 (p .12), random acc .011; null SD ~.1. Effects: RELAY ≥10 SE, HOLD deterministic (SE 0) | Not a seed artefact: yes. "Independent reproductions" of a physics boundary: no. The common cause is in the code (E-W13: RELAY decay is plant design) |
| D: "fresh seeds reproduce in 3 of 4 RELAY cells" | 8 replicate searches | Condition (4) | 4 | Replicates SIGNAL 6/8; conditions 3/4. MAJ 3/8 searches, HOLD 6/8. Replicate concordance P(second \| first) is RELAY .68, MAJ .30, HOLD .83 | Yes, as 3/4 conditions; per-search reproduction is 75% (RELAY) |

## 2. Recommended wording

Each item is NEUTRAL. No label is changed.
1. **L3 line:** "Unbiased A1 rates (one search per random physics): RELAY 4/71 (5.6%, 95% CI 2.2–13.6), MAJ 3/70 (4.3%, 1.5–11.9), HOLD 34/70 (49%, 37–60), XOR 0/71 (≤5.1%), FLIP 0/70 (≤5.1%). All-wave totals (RELAY 50/196, MAJ 19/162, HOLD 97/155) pool follow-ups targeted at winners and are not rates. The 50 RELAY SIGNAL rows are 6 independent lineages (17 distinct conditions), 32 of them from one A1 cell."
2. **Headline "rare (A1: 8/352 COMM_DEPENDENT)":** "rare: 8/352 A1 searches (2.3%, 95% CI 1.0–4.4; P4's 5% bound holds at one-sided 99%). In RELAY and MAJ, COMM_DEPENDENT is identical to SIGNAL (zero_comm is forced to .500)."
3. **One hop:** "The RELAY SIGNAL lineages found are one-hop (4 of 6 lineages entirely; 15 of 17 conditions). In the unselected A1 frame, one-hop tasks gave 3/32 SIGNAL vs 1/39 multi-hop (difference +7 pp, 95% CI −5 to +22; p = .32), and one-hop global tasks gave 0/11. Multi-hop competence is rarer, not shown absent."
4. **84%:** "Of the 733 recorded CHANCE verdicts (430 distinct measurements, 87 specimens), 84% of rows stay CHANCE at 512 worlds; per specimen the mean is 72% (95% CI 63–80). W-F 67% vs W-I 89% of measurements; HOLD 47% (26–65). This rules out sample size as the cause of CHANCE, not what CHANCE is."
5. **615/90/28:** add "per specimen, 24% (16–33) of audited verdicts become FLIP; 17 specimens flip in every audited arm."
6. **REL2 classes:** quote counts with their unit ("170 rows / 117 measurements / specimen-mean 48% FLIP_REL").
7. **W-Z Pb:** "35/124 groups (28%; specimen-clustered 95% CI 19–41%); point inside the preregistered 25–45% band, interval not."
8. **Cross-family boundaries:** "The decay gate reproduces across RELAY, HOLD and FLIP plants on the same (shared) fresh seeds. The agreement reflects one integer-decay rule acting on plants that store the bit in S0, not independent physics replications."
9. **D wave:** "Fresh-seed replicate searches give SIGNAL in 6/8 (RELAY), 3/8 (MAJ) and 6/8 (HOLD). A per-cell SIGNAL is one search draw."

## 3. Findings

**F1 [V] Pooled L3 ratios have n_eff ≈ 18–60.** Confidence: high.
- Check: `ac_c1_units.py`. The lineage root is found by following `parent` to wave A, asserted to terminate.
- Lineage deff: RELAY 11.1, MAJ 2.8, HOLD 6.3.
- Two of the 6 RELAY lineages (13127335, 12c2b57f) are C-wave re-evolves at top-ranked HOLD physics, so they come from a selected frame.
- Objection: lineage may over-cluster, because B-wave rows vary a dial rather than replicate. Even condition-level clustering gives deff 4.1 for RELAY.
- Unresolved: there is no unbiased estimand for the pooled ratio at all.

**F2 [V] A1 is the correct unit, and its rates stand.** Confidence: high.
- Asserted 352 distinct physics points and 352 distinct seeds.
- The uniform and living-A0 frames agree (RELAY 2/36 vs 2/35; HOLD 17/35 vs 17/35).
- Objection: one search per physics point conflates physics viability with search success. D replicates show per-search reproduction of .75 (RELAY) and .375 (MAJ).
- Unresolved: per-physics attainability.

**F3 [V] P4 holds at the 99% bound, but it counts an alias.**
- 8/352: one-sided 99% CP upper bound .0488. BOOTT gives 7.
- The alias SIGNAL == COMM_DEPENDENT is asserted over all evolve rows in RELAY/MAJ/XOR.
- Confidence: high.

**F4 [V] One-hop: the evidence is the A1 contrast, not 48/50.**
- Rows → conditions → lineages: 48/50 → 15/17 → 4/6.
- My A1 split (3/32 vs 1/39) uses all 71 rows. W2-G's 3/18 vs 1/26 omitted global (0/11) and random one-hop (0/3). Same conclusion.
- Objection: the hop rule for smallworld/random graphs is taken from W2-G (it reproduces 48/50).

**F5 [V] The C1 counts are immune to the namespace/family effect.**
- Evolve seeds 678/678 are unique; with transfer and adjudicate rows, 789/789. Held, final and train worlds are keyed by these seeds.
- Only B2 shares seeds: 69 seeds over 180 rows (150 census, 30 evolve). The shared evolve rows share only plant-viability worlds (namespace 0x9147), never held worlds.
- Answers W2-N NQ3: no inflation of "RELAY 50/196" from shared namespaces.

**F6 [V] W-O 84%: specimen clustering matters; namespace does not.**
- Check: `ac_swap_units.py`.
- The predictive expectation of stay-CHANCE on a fresh namespace (f = 1) is 350.9, against 348 observed measurements. So the rows are self-consistent.
- Noise SD: 3.13 independent; 3.16 with ρ = .037 within family; 3.79 in the worst case. The cluster-bootstrap SD is 11.8.
- Objection: the dedup (exact or mirrored 512-world triples within specimen × offset) is coarser than pair-array dedup. Rows and measurements give the same conclusion, and my 41% merge rate is close to W2-N's 40% (301 → 182).

**F7 [V] B2 cross-family agreement is not seed-made, and it is not independent.**
- Check: `ac_b2_shared.py`, with a permutation null over rep labels.
- Power is limited: only |r| ≳ .2 is detectable. But the effect sizes are 10–30 SE (RELAY) or exact (HOLD .25, SE 0), so even r = .2 could not manufacture them.
- New detail: 21 cross-family census pairs draw bit-identical random-genome sets (same rules × prog_len), because `random_genomes` is keyed only by the seed.
- The B2 key also omits the track. HOLD evo base 1 shares its seeds with HOLD phys base 1, and RELAY evo delta shares its seeds with RELAY phys delta. These are same-family pairs that share task geometry, which is exactly W2-N's r .037 mechanism. The effects there (delta plant +.40, SE .024) dwarf it.

**F8 [V] W-Z Pb is "HELD" only at the point estimate.**
- Specimen-clustered CI [.186, .413].
- The class rate depends on group priority (AMBIG 1/31 vs REST 34/93).

**F9 [I] Lottery cells (W2-Q) do not change any count at the unit level.**
- They are 7 of 97 HOLD SIGNAL rows and 1 MAJ row.
- But for them the "rate" estimand is a per-world mixture.
- Confidence: medium.

## 4. Proposed fixes

- **NEUTRAL wording:** section 2.
- **NEUTRAL tooling, no diff written:** report.py could emit a unit table (rows / conditions / lineages / A1-rate with Clopper-Pearson CI) beside every count.
- **SEMANTIC, future only:** key B2 seeds by family and track (this is W2-H P2; I concur, with the added evidence of track sharing and identical genomes). Swap audits should report specimen-weighted shares as well as row-weighted ones.

## 5. Disagreements

- **W2-N F7's design-effect formula 1 + (G−1)·.037** applies to the latent pair-level noise. For label counts the correlation is attenuated by φ(a_i)φ(a_j), because most rows are far from the cut. The measured noise deff on the W-O count is 1.02, not the ~2.7 the formula gives for 47 RELAY specimens.
- **W2-H F11** says cross-family boundary statements are "not independent". I agree, and the sharing is total (100% of each cross-family reproduction's seeds), not partial. But the measured coupling is ≈ 0, so the non-independence that matters is the common cause in the code, not the seeds.
- **W-O summary.json** reports only row-weighted shares (its cluster99 for CHANCE, [.771, .896], is consistent with mine). The specimen-weighted figure is 72%, and per-specimen FLIP is 24%, not 12%.
- **W-Z REPORT "Pb HELD"** should read as point-in-band only (F8).

## 6. Next questions (ranked)

1. Estimate per-physics attainability (k of n searches SIGNAL) at A1 physics points with ≥3 seeds each. That separates viability from search luck in the 4/71 and 3/70 rates.
2. Make the one-hop vs multi-hop contrast powered: how many A1-style multi-hop RELAY searches are needed to bound the multi-hop rate below a third of the one-hop rate? About 150 per arm by normal approximation; needs authorization.
3. Why does global topology (one-hop by construction) give 0/11 A1 RELAY SIGNAL, when pooled waves found 4 global SIGNAL rows? Is it search, or a plant/latency gate?
4. Re-derive the W-O shares with pair-array deduplication (only W-Z's 365 rows have arrays). Does the specimen-weighted 72% hold?
5. Re-run the 3 cross-family SUPPORTED transects on family-keyed B2 seeds to remove the shared-seed caveat formally. Small census compute.
6. For W-Z Pb, the 125 uncovered groups: does the specimen-level CARRIER-NAMED rate change once groups are not selected by AMBIG priority?
7. Restate P2 (HOLD decay 1: 3/9) at the condition unit. B reps share conditions, so the 9 are fewer independent units.

## 7. Inference ledger

```
L3 pooled ratios | ac_c1_units lineage/condition cluster bootstrap | not rates; n_eff 18 (RELAY), 58 (MAJ), 25 (HOLD); 50 RELAY SIGNAL rows = 6 lineages | high | lineage may over-cluster dial transects | no estimand for the pooled ratio | quote A1
A1 rates | 352 distinct physics/seeds asserted; Wilson/CP | RELAY 4/71 [2.2,13.6], MAJ 3/70 [1.5,11.9], HOLD 34/70 [37,60] | high | conflates viability with search luck | per-physics attainability | NQ1
P4 / COMM_DEP | CP one-sided; alias assertion | 8/352, 99% upper 4.88% -> HELD; COMM_DEP == SIGNAL | high | BOOTT 7/352 | - | wording
one-hop | rows -> conditions -> lineages; A1 Fisher/Newcombe | 48/50 -> 15/17 -> 4/6; A1 3/32 vs 1/39, p .32; global 0/11 | high counts / medium reading | hop rule taken from W2-G | power | NQ2, NQ3
namespace on C1 | seed uniqueness over 789 rows | no shared held worlds; only B2 shares (plant worlds) | high | - | - | -
W-O 84% | ac_swap_units, specimen cluster, dedup, noise model | rows 84% [79,88], specimen-equal 72% [63,80]; namespace noise deff 1.02 | high / medium (dedup) | no pair arrays | pair-level dedup | NQ4
swap class counts | same | FLIP specimen-equal 24% vs rows 12%; FLIP_REL 48% vs 23% | high | weighting is a choice | - | wording
W-Z Pb | ac_wz_units | 28% [18.6,41.3]; CI crosses 25% | high | groups selected | uncovered 125 groups | NQ6
B2 cross-family | ac_b2_shared residual r + permutation; genome identity | 100% seed sharing; r ~0 (detectable only above .2); 21 identical genome sets; agreement is code common cause | medium-high | low power vs small r | family-keyed rerun | NQ5
lottery | W2-Q list vs HOLD SIGNAL rows | 7/97 HOLD, 1 MAJ; no count change | medium | - | - | -
```

## 8. Compute used

About 1 CPU-minute in total (numpy only; every script under 30 s), roughly 0.005 core-h against the 0.2 cap. No GPU (CUDA_VISIBLE_DEVICES=-1; torch was never imported), no searches, no leases, no git writes. Files were written only in W2-AC/ (scripts and out/*.json).
