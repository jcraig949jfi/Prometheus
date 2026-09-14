# NEM-14 -- the instrument attack-surface map

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Preregistered in PREREGISTRATION_NEM14.md (commit
0548bde84) before any instrument was classified. Rows:
`classification.json` (53), evidence: `census_screen.json`. Built from
488a9b36c in D:\Prometheus-worktrees\nemesis-adopt on branch
nemesis/nem14-floor-census-2026-09-11.

The commission: "find out how many of Prometheus's numbers are presently
being interpreted without knowing what nothing scores."

## The answer

    Tier 1 instruments (index truth)                    53   across 10 seats
      emit no headline number (NA, plumbing/IO/schema)  16
      emit a headline number                            37

    Of the 37 that emit a number, HOW MANY KNOW WHAT NOTHING SCORES:

      a CHANCE floor (null draw, permutation, random arm)  12   32.4%
      no chance floor                                      25   67.6%

**Two thirds of the numbers this program's current instruments emit are
interpreted without a chance floor beside them.**

## Two of my three predictions LOST, both in the same direction

    Q1  F0+F1 >= 50 per cent of scoring instruments     LOST  (35.1%)
    Q2  my screen over-calls: <60% of keyword-positive
        modules reach F2/F3                             LOST  (70.6%)
    Q3  >=1 TERMINAL instrument sits at F0/F1           HELD  (3 of them)

I expected a worse program and a worse tool than I found. The seat's prior
was pessimistic and the data disagreed twice, which is worth more than the
one prediction that held. Recorded in CALIBRATION.md.

The headline finding survives both losses because it is not what Q1
measured. Q1 counted instruments with no baseline OF ANY KIND (13 of 37).
The commission asked about the CHANCE floor specifically, and that count
is 12 of 37 -- because the state and the KIND came apart.

## The distinction the preregistration did not anticipate

A floor-shaped number is not a chance floor. Three kinds were found, and
merging them is exactly the error this seat exists to catch:

    CHANCE     12   what NOTHING scores: a null draw, a permutation, a
                    random arm, a degenerate responder
    CHANNEL     6   a positive and/or cheat control proving the MEASUREMENT
                    CHANNEL can see success and catch a fraud -- excellent
                    practice, and it is not a baseline for the headline
    RELEVANCE   5   the smallest effect that would MATTER if real
                    (Harmonia's relevance_floor, smd 0.2/0.5). A
                    materiality threshold says nothing about chance
    ANALYTIC    1   a simulated/closed-form floor rate
    WITHDRAWN   1   a null that was calibrated and then correctly declared
                    inapplicable, leaving the headline without one
    NONE       12

A seat can hold a rigorously specified relevance floor and still not know
what nothing scores. Five instruments are in exactly that position.

## The map

P1 terminal and no baseline at all. P2 terminal, baseline weak or withdrawn.
P3 non-terminal, no baseline published. P4 relevance floor only. P5 has a
floor; no action from this census.

"Cheapest known shortcut" is NOT filled per row: deriving it requires an
attack, and this pass is a census. It is derived only where an attack has
run. NOT_DERIVED is written rather than guessed, so the gap is visible.

| P | instrument | headline metric | floor | kind | terminal |
|---|---|---|---|---|---|
| P1 | `Harmonia/conformance_check.py` | four-state conformance verdict (DRIFT/UNREACHABLE/INCO | F0 | NONE | YES |
| P1 | `Harmonia/s2_ablation_honesty.py` | ablation honesty | F0 | NONE | YES |
| P2 | `Harmonia/d3_dossier_adjudication.py` | D3 fires / eligible | F1 | WITHDRAWN | YES |
| P2 | `Harmonia/s6_selection_bias.py` | promotion rate under selection | F2 | RELEVANCE | YES |
| P3 | `Harmonia/s10_second_organism.py` | second-organism effect | F1 | NONE | - |
| P3 | `Harmonia/s13_family_reconciliation.py` | family reconciliation outcome | F1 | NONE | - |
| P3 | `Harmonia/s15_fossilization_boundary.py` | fossilization boundary | F1 | NONE | - |
| P3 | `Harmonia/s3_player_classes_and_replay.py` | player-class effect | F1 | NONE | - |
| P3 | `Harmonia/s4_interactions_and_truncation.py` | interaction / truncation effect | F1 | NONE | - |
| P3 | `Harmonia/s8_does_c7_transport.py` | does C7 transport (effect d) | F1 | NONE | - |
| P3 | `Hermes/convergence/record.py` | convergence record counts | F1 | NONE | - |
| P3 | `Hermes/convergence/signature.py` | signature collision behaviour | F1 | NONE | - |
| P3 | `Kairos/claim_lint.py` | lint findings by severity | F1 | NONE | - |
| P3 | `Polyhymnia/lincode_decoders.py` | decoder success rate | F1 | NONE | - |
| P4 | `Harmonia/c3size.py` | floor rate after aggregating repeats | F2 | ANALYTIC | - |
| P4 | `Harmonia/s11_v6_redteam.py` | red-team survival | F2 | RELEVANCE | - |
| P4 | `Harmonia/s12_organism2_estimation.py` | organism-2 effect d | F2 | RELEVANCE | - |
| P4 | `Harmonia/s16_boundary_inventory.py` | boundary inventory counts | F2 | RELEVANCE | - |
| P4 | `Harmonia/s9_expressiveness.py` | expressiveness coverage | F2 | RELEVANCE | - |
| P5 | `Arachne/branch_fitness.py` | child_greater rate over eligible branches | F3 | CHANCE | - |
| P5 | `Arachne/emergence.py` | emergence/ARI statistics | F3 | CHANCE | - |
| P5 | `Arachne/specimen.py` | reconstructed lineage counts | F3 | CHANCE | - |
| P5 | `Clymene/model_audit.py` | model integrity pass rate | F3 | CHANNEL | - |
| P5 | `Clymene/weights_probe.py` | weights reachability | F3 | CHANNEL | - |
| P5 | `Coeus/trace_defects.py` | F4 selection-trace effect vs matched noise | F3 | CHANCE | - |
| P5 | `Harmonia/d3_live_corpus_calibration.py` | D3 fire rate on the live corpus | F3 | CHANCE | - |
| P5 | `Harmonia/s14_truthful_records_false_science.py` | false-positive science rate | F3 | CHANCE | - |
| P5 | `Harmonia/s17_prospective_fragility.py` | fragility ranking top-1 | F3 | CHANCE | - |
| P5 | `Harmonia/s18_fossil_directed_selection.py` | policy-C selection yield | F3 | CHANCE | - |
| P5 | `Harmonia/s1_known_null_campaign.py` | celebrated cells on a null grid | F3 | CHANCE | - |
| P5 | `Harmonia/s5_hidden_moderators.py` | sign-flip count across 36 cells | F3 | CHANCE | - |
| P5 | `Harmonia/s7_transportability.py` | transported effect d | F3 | CHANCE | - |
| P5 | `Harmonia/se1_first_preregistered_experiment.py` | hill-climb effect d | F3 | CHANCE | - |
| P5 | `Hermes/convergence/probe.py` | convergence collision rate | F3 | CHANNEL | - |
| P5 | `Hypatia/seam_contract_test.py` | seam contract confirmed | F3 | CHANNEL | - |
| P5 | `Talos/characterize_corpus.py` | corpus duplication / characterisation | F3 | CHANNEL | - |
| P5 | `Talos/semantic_faithfulness.py` | semantic faithfulness rate | F3 | CHANNEL | - |

## Audit the auditor (operator requirement)

Any instrument inspection that enumerates the FILESYSTEM inherits
sparse-checkout visibility, and D-23 mandates the worktree topology that
produces it. Measured in this worktree at 488a9b36c:

    instrument-shaped modules in the INDEX      376
    instrument-shaped modules ON DISK            40
    visible fraction                           10.6%
    missed by a filesystem-enumerating auditor  336

An auditor standing here and walking the filesystem would have reported
89.4 per cent of the instrument population as absent, in the same words it
uses for a genuine absence. This census therefore takes membership and
content from `git ls-files` and `git show HEAD:` only, and
`floor_census._forbid_filesystem()` raises if it is ever handed a path
that is not in the index. That control is not decorative: it is the same
defect class as NEMESIS-01's second finding, where Eos's
`capability_absent` greps the working tree and reported 43 files where the
index held 97.

Nemesis can manufacture ABSENCE by standing in the wrong worktree. So can
every other seat that greps for what the program does not have.

## Coverage limits, stated rather than implied

- TIER 1 ONLY. 53 seat-owned modules under roles/*/science and
  roles/*/contracts. The legacy population under agents/ is excluded and
  it is large: 15 instrument-shaped modules there by index truth, and 376
  repo-wide. This census covers roughly 14 per cent of the
  instrument-shaped modules in the tree.
- HARMONIA IS 28 OF 53. A census landing hardest on one seat looks like an
  attack on that seat; it is not. Harmonia owns more instruments than
  anyone and also owns 9 of the 12 chance floors. The seat with the most
  exposure here is the seat doing the most nulls.
- CLASSIFICATION IS A HAND-READ of the module and its emitted keys, not a
  proof. Every row carries the evidence that decided it so it can be
  disputed; `classification.json` is the object to argue with.
- NO INSTRUMENT WAS ATTACKED in this pass. An F3 row means a floor is
  published, NOT that the floor is correct.

## NEMESIS-02: selected

    roles/Harmonia/contracts/conformance_check.py

Highest consequence with no defensible baseline. It emits a four-state
verdict (DRIFT / UNREACHABLE / INCOMPLETE / OK) and it is TERMINAL in the
strongest sense in this program: D-22 and WORKING_CONTRACT s8 require
every consumer to run it before work and to HALT on DRIFT or a wrong
engine_instance_id. It carries no floor vocabulary at all in 276 lines.

The question NEMESIS-02 asks is the one this census cannot:

> What is the cheapest engine state that this gate certifies as OK while
> the property it certifies is false?

Runner-up, not selected: `s2_ablation_honesty.py` (F0, terminal, no floor
vocabulary in 240 lines). It is second because its consequence is scoped
to one Harmonia loop, where conformance_check gates every consumer in the
program.

Not selected and worth naming: `d3_dossier_adjudication.py` withdrew its
own null in place, in print, and kept reporting the fire count. That is
honest behaviour that leaves a headline uncovered, and it is a different
problem from never having had a null. It is a repair, not an attack.

## What I would NOT conclude from this

- NOT that 25 instruments are wrong. An absent chance floor is an absent
  BASELINE. It makes a number uninterpretable, not false.
- NOT that the program is careless. 12 instruments compute real nulls, 6
  ship cheat or positive controls on their measurement channel, and one
  withdrew its own null rather than keep using an inapplicable one. Two of
  my three predictions lost because the practice here is better than this
  seat assumed.
- NOT that this census is complete. See the coverage limits.
