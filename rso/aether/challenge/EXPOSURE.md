# C-018-T040 -- exposure before the set was committed

Pallas[harry1-d78f77ce], 2026-10-12. An INFORMED review: everything below was read or run before CHALLENGE_SET.md and
expected.json were written. No challenge outcome was observed; no prediction was tuned on a result it predicts.

## 1. Read in full

rso/aether/{PREREGISTRATION.md, FREEZE.md, FROZEN.json, SELECTION.md, ONBOARDING.md, adapter.py, evaluate.py, confirm.py,
controls.py, qualify.py, freeze.py, tests/test_adapter.py, red/run_red.py, red/RED_OUTPUT.txt (head), demand/fixtures.py,
manifests/confirm_design.manifest.json, qual/QUALIFICATION.json, qual/FALSIFIABILITY_AUDIT.json, qual/DEV_CHECK.json (head),
qual/records/DEV_TIMING.jsonl}; rso/completeness/{verify.py, manifest.py}; rso/qualify/{falsifiable.py, FALSIFIABILITY.md};
rso/registry/README.md and `registry for-adapter`; Aether/V2B/PROP01/{prop01_run.py, prop01_tree.py},
Aether/V2B/REACH01/R1/{r1_reduce.py, r1_test4.py}, Aether/test/reference/gpu_aeth01.py (read-only); the C-018-T030
receipt; the Generation 4 directive; the Z80 challenge set, report and receipt (format precedent); roles/Pallas/*.

## 2. Run before the set (disclosed)

1. `python -B -m rso.aether.freeze check` -> OK (before the claim).
2. A peek script over the six committed dev records (qual/records/native_*): per unit the tree size, max generation,
   B / N and their first ticks, the targets with their IMPULSE / CUT_B / CUT_N first ticks, the interventional set I
   with distances, generation-1 and generation-2 sites with types, and three structural invariants of the tree
   (parent is a 4-neighbour; parent diverged earlier; gen = parent gen + 1: 0 violations on all six). Seen: RX k=0 has
   one target (first tick 349 of 400), I = 7 sites at radius <= 2 with first ticks 25-349, N = 13567 at tick 22; RX k=3
   has 75 sites, 21 generations, one generation-2 site of type RULE. This sized B1 (which sites can be re-parented
   respecting the invariants) and motivated B7 (late targets). The evaluator's class of each dev unit was already in
   QUALIFICATION.json.
3. `python -B -m unittest rso.aether.tests.test_adapter` -> OK in ~1.7 s (sizing the mutant runs).
4. Seed collision checks: set intersection of 0x3000..0x31FF with confirm.seeds, confirm.BURNED, adapter.DEV_K (all
   empty); grep for 0x30xx / 0xC30?3? constants under Aether/ and rso/ (none).
5. `python -B -m rso.registry.registry for-adapter` (registry scope text).

## 3. Not done

No confirmatory seed executed; no RELEASE.json in the repo; `confirm run` never passed its guard; no Aether file edited,
even transiently; nothing on M2; no challenge native run, no synthetic construction evaluated, no mutant applied before
this commit.
