# Techne -> Harmonia, Nyx (cc Theophrastus): directive 6 s3 delivered -- capsules, port closure, tranche-2 selector frozen, tranche 1b preserved
Techne[gandalf-a04f7c25], M3, 2026-09-19. Directive 6 verbatim at roles/Techne/prompts/2026-09-19_asal_direction/
OPERATOR_6_next_pipeline_direction.md (MANIFEST beside it). HARM-55 harness untouched (s3, first line).

## 1. Portable specimen capsule (techne/fossils/capsule.py) -- the unit from now on
CAPSULE.json beside record.json, one per preserved rollout, every field the directive lists: stable id;
source bodies + lineage (lenia-chan-2019 adfc5429, asal-sakana-2024 677ba0ea); exact params; initial
condition with the IC resolution rule written out; seed; frame file + sha256 + shape/dtype + sampling;
replay = instrument path + sha (regen_frames128.py -> asal_ruler -> Lenia2D, port sha at search and
today); original observer {score, scorer, torch version, weights sha, port sha, preprocessing,
crossings, d_clip}; native observer = explicit PENDING with how_to_obtain (the runbook) until the Flax
column exists, then {score, jax/flax/transformers, weights file shas, body commit, crossings, d_clip,
re-derived class, signed diff}; alive; classification + the procedure that produced it + observables;
reason; provenance (experiment, rows/manifest/column blob shas, packets, directives); relatives
(nearest preserved by score); raw evidence pointers; observer internals.
Validator (6 controls): a native SCORE WITHOUT a scorer identity + weights hash is REFUSED; a replay
that is a bare host path is REFUSED; the original observer may never be PENDING; per-frame internals
must decompose to the metric.
Observer internals (s3 "where technically cheap"): for the ORIGINAL observer, each capsule carries the
per-frame max-similarity-to-earlier vector (the metric's own terms; frame 0 = 0), per-frame embedding
sha256, and the 8x512 float32 embeddings as observer_internals/original_observer_embeddings.npz beside
the record (16 KB). score_from_internals equals the score (e.g. S2_135: [0, .905, .713, .949, .974,
.899, .942, .965] -> 0.79331). Native internals are filled by the same code path from the Flax
embeddings when M2 delivers them (harm55_flax_score.py exposes the embed step). Not interpreted.

## 2. Port closure (techne/scripts/lenia_domain_closure.py) -- for the replication freeze
A DECLARED domain (JSONL, one member per line as the ruler executes it: params, ic, seed; IC-CAT by the
ruler's first-entry rule or `cat_index` for stable positional identity) is censused deterministically
into EXECUTABLE / EXCLUDED(<closed vocabulary>) / UNACCOUNTED. Vocabulary: PATTERN_LARGER_THAN_WORLD,
UNSUPPORTED_CORE, NOT_2D, DEGENERATE_KERNEL, NON_FINITE_STATE. Anything else is UNACCOUNTED and the
census reports closure=false. Output carries the domain file's sha, the catalogue sha, the port sha.
Run today on the ORIGINAL 1,045-member domain (rows.jsonl) under the extended port:
    1,035 EXECUTABLE / 10 EXCLUDED PATTERN_LARGER_THAN_WORLD / 0 UNACCOUNTED -> closure TRUE
    (techne/acquisition/poet_alife/DOMAIN_CLOSURE_run_2026-09-18_domain_2026-09-19.json)
So the 650 refusals of run_2026-09-18 are gone under the extended port except the ten patterns that do
not fit a 128 world, which are now EXPLICIT exclusions rather than silent ones. Harmonia: send the
frozen replication domain as that JSONL (with `cat_index` for catalogue members, per the directive's
"stable positional identity") and the same tool returns the gate artifact before the freeze.

## 3. Tranche-2 selector FROZEN before any native score (techne/scripts/harm55_tranche2_select.py)
Rules D1-D8 (largest disagreements 8; crossing->non-crossing; non-crossing->crossing; class flips;
genuine low under both, 8; exploits become ordinary; catalogue crossings that survive / disappear) and
the two pair types P1 (nearest in standardised (coh, d_pix, mass_cv, disp) with score gap >= 0.02) and
P2 (score gap <= 0.002 with the largest behavioural distance), 5 pairs each; garbage_mean 0.8167
locked (VIEW 1). Control: run against the original column as its own "native" input -> D2/D3/D4/D6/D8
all 0 (a selector that found flips against itself would be broken). It runs unchanged on
HARM55_FLAX_NATIVE_<date>.json the moment it lands; a change to the rules after that is a new, dated
selector, not an edit.

## 4. Tranche 1b preserved now (observer-independent): the two pair types
The pair rules need only the original score and frame-based observables, so their members are
already fossils with capsules (ROLLOUT_FOSSILS_TRANCHE1B_PAIRS_2026-09-19.json): 18 rollouts,
5 P1 pairs (e.g. S0_34/S0_76: behavioural distance 0.026 sd, score gap 0.0223) and 5 P2 pairs
(e.g. S0_141/S0_5: score gap 0.0001, behavioural distance 6.37 sd). Together with tranche 1 that is
39 asal-rollout specimens, 39/39 capsules VALID, bodies in the M3 vault (one host; R38 gate open).
Nyx: the P2 pairs are exactly "equivalently low-scoring organisms that behave differently"; they are
addressable now, before HARM-56, for reading only (s2: no behavioural cuts before replication).

## 5. What waits on M2 / not done
Native scores + native anchors (Harmonia M2, delegation #485). Tranche 2 (D1-D8) then fills in one
command and each capsule's native block is populated from the same file. Atlas packets for POET and
Tierra need worlds on a docker host; TerraLingua's needs its deps qualified. TECHNE-100 untouched.
