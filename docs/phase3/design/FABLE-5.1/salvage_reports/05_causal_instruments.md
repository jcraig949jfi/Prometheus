# Salvage worker report: scope 5, causal, lineage and intervention instruments

Deposited by Dionysus[m1-3815a3b9] on 2026-10-01. Extracted by script
(process/deposit_worker_reports.py) from the coordinator's session transcript:
the worker's final message, recorded 2026-10-01T15:32:04.504Z. The text is the worker's,
unchanged except that XML escapes from the notification wrapper are undone
and trailing whitespace is stripped.

The same worker sent an earlier message (2026-10-01T15:22:15.374Z). This one
replaced it after the coordinator's search-rule correction. The earlier text
is not deposited.

Brief: roles/Dionysus/prompts/2026-10-01_salvage_workers/00_COMMON.md and
05_SCOPE_causal_instruments.md. Worker model: opus, read-only.
Worker usage as reported by the harness: 677,910 tokens, 197 tool uses, about
35.7 minutes (totals for the worker, all messages).

This is a worker's fact sheet. Its claims are the worker's, graded by its own
VERIFIED BY ME lines. Where SALVAGE_MATRIX.md relies on one, it says so.

----------------------------------------------------------------------

I applied the coordinator's correction. Under the corrected exclusion the question A and B searches, the staircase, opt-out and HALFBLANK searches and the importer checks returned the same displayed output as before; the one changed query (Cosmos c3 importers) still finds no code importer. No conclusion changes. My earlier listing of prometheus/cosmos/tests did take in the file names there, test_holdout_isolation.py presumably among them; nothing was printed and nothing was opened. Item 8 of SURPRISES has the full audit of my earlier searches.

===BEGIN REPORT===
SALVAGE FACT-FINDING, SCOPE 5: CAUSAL, LINEAGE AND INTERVENTION INSTRUMENTS
Worker for Dionysus. Worktree HEAD e3d7c7034. Read-only: no git writes, no file edits, no tests or engines run.
- I opened no path containing "holdout" or "nestor_secrets" and no credential file.
- My early searches used the brief's directory pattern only. After the coordinator's correction, I re-ran every search behind a conclusion with ':!**/*holdout*/**' ':!**/*holdout*' ':!**/nestor_secrets/**'. Results are identical. SURPRISES 8 has the full audit.
- Unless a sheet says otherwise, dossier numbers come from docs/phase3/intake/<crawler>/seats/<Seat>.md.

----------------------------------------------------------------------
COMPONENT: Ananke carrier-swap lens (mirror-pair interchange, temporal reach, reach verification, S/C/N census, REL4 relative certificate)
PATHS: prometheus/ananke/lens.py, lens_swap.py, swap_rel.py; assays.py (twin_assay); engine.py (state_arrays, digest, checkpoint); tests/test_lens_instruments.py, test_lens_swap.py, test_swap_rel.py; roles/Ananke/research/instruments/INSTRUMENT_CARRIER_SWAP.md
OWNER / DATES: Ananke. lens.py 2026-09-27 to 09-28; lens_swap.py 09-29 to 09-30; swap_rel.py 09-30.
WHAT IT REALLY DOES: Worlds 2p and 2p+1 are mirror partners. They share every exogenous random draw, and their cue signs are negated; the cue sign is the known latent. Between ticks the lens copies one named World array into the partner (S, E, r, Kp, inbox, w, Msum, Mcnt, or one payload component), or it delays or rolls the in-flight packets. It then asks whether the readout follows the partner.
- lens.py verdicts: FLIP if hi99 < .40; NO-EFFECT if lo99 >= normal lo99 - .05; CHANCE otherwise. The thresholds were declared in SPIKES_2026-09-27_PLAN.md, not derived.
- lens_swap.py adds single-trial arms and an S/C/N census per (pair, trial). Frozen classes: fS or fC >= .80, identity >= .90, eligible >= 20.
- swap_rel.py issues FLIP_REL, NO_EFFECT_REL or CHANCE_REL from a studentized pair bootstrap with a floor on the SD; it needs P >= 32 pairs.
- verify_reach counts lockstep digest differences ("applied") and runs a must-flip plant through the same hook.
SIZE: 988 lines. 42 test functions (11 + 20 + 11).
DEMONSTRATED CORRECTNESS: Four designed carriers were recovered, and the wrong-carrier negatives were rejected:
- echo_hold: channel content and pay0 FLIP; counts, pay1, site and w NO-EFFECT;
- hold_latch: S FLIP;
- rule_switch_hold: r FLIP;
- route_relay: w FLIP.
Each of the three verdicts is shown reachable. swap_rel's largest false-certificate rate on a synthetic grid is .991%. The same seat wrote the plants and the instrument. Known false-accept and false-reject modes:
- a joint swap flips anything;
- presence reads as content;
- "applied" is not "reached": one edit counted 85 applied ticks and never reached the readout (W2-F API table);
- in RELAY and MAJ the mirror design makes the site and channel arms one measurement: the identity is exact at offset >= 1 in 93/93 groups (W2-F F4);
- absolute FLIP needs normal >= .662 (P32 K12) or .624 (P256 K11) for 50% power;
- NO_EFFECT_REL is forced on no-op arms: 24 of 98 W-Z arms (W2-B);
- intervals are about 2x too narrow across seed namespaces: 20 flips observed against 8.3 expected (W2-F F6).
INTERFACE: Python call on (Physics, genome, EnvSpec, seeds, ticks). Integer torch state on CPU or CUDA; deterministic; confidence intervals are floats. Tied to PTE: it names the World arrays and needs the mirror layout built by envs.build. World.state_arrays() is a named 9-array partition with digest, checkpoint and restore. No model call.
THROUGHPUT / SCALE: Throughput not recorded. Used at 64 to 512 worlds per arm (dossier).
COUPLING: Imports prometheus.ananke engine, envs, assays, physics, plus torch and numpy. git grep finds 0 importers outside roles/Ananke (re-checked under the corrected rule).
FIT TO SLOT: Interchange and lesion; carrier localisation.
- Meets CAUS-03 nearly word for word on PTE; meets CAUS-02 in part.
- Fails ORG-01 and ORG-02 (PTE arrays), ORG-10 (array level only), CAUS-05 (no coverage receipt), MEAS-01 and MEAS-02 (an instrument card, but no datasheet and no gate in code) and MEAS-07 (floats).
MODIFICATION COST: M. Work items:
- swap over protocol-declared components between paired runs that differ in one declared latent;
- rational decision arithmetic;
- arm-identity and namespace-replication guards;
- a datasheet built from the REL4 tables;
- re-qualification on WM and PN plants.
Rebuild: M for the code (about 400 lines), L to rediscover the documented failure modes F1 to F8. Port those modes as fixtures either way.
VERIFIED BY ME: Code, thresholds, plants, tests and the swap_rel TABLE in source. Failure counts taken from the W2-F and W2-B reports, not recomputed.

----------------------------------------------------------------------
COMPONENT: Ananke Wave-2 certification stack (explib, attainability certifier, cheap adversaries, light-cone ceilings, PTE difference tracer). Never promoted.
PATHS: roles/Ananke/research/harvest/wave2/W2-F/explib/ (plus tests/, adapters/pte.py, API.md); wave2/W2-B/attain.py, analytic.py, adversaries.py; harvest/H-PLANT/lightcone.py; harvest/H-INST/pte_trace.py; wave2/W2-AE/ (package, INCOMPLETE)
OWNER / DATES: Ananke Wave-2 workers, 2026-09-30: W2-F 752326104, W2-B 701c79bca, H-PLANT b8ab2aa65, H-INST 29fd80308. W2-AE 2026-10-01 e0f21332d.
WHAT IT REALLY DOES: explib is pure numpy and imports no engine (checked).
- LockstepEngine protocol: make, step, trace; optional intervene, inputs, arrivals, inflight, edges, readout.
- It runs arm A and arm B in lockstep and checks common random numbers (crn_check) and a closure invariant.
- It certifies each unit as UNAPPLIED, NOT_REACHED, ABSORBED, REACHED or INCONSISTENT.
- Control identity audit: A1 not a no-op, A2 not constant, A3 no mirror identity, A4 a witness can reverse it. Verdicts COMPETENT, FORCED, NO_OP.
- Gate certification: G1 null false-pass rate with an exact Clopper-Pearson bound; G2 committed adversaries; G3 a plant passes; G4 eligible-cell count from ceilings.
- Also difference-vs-use, mutation adequacy, plan-precedes provenance and independence units.
W2-B runs programs by role (null, adversary, plant) and returns UNREACHABLE, DEGENERATE, CHEATABLE, SOUND or NO_PLANT. lightcone.py bounds any program by its fastest-transport reach.
SIZE: explib 1,998 lines, 40 tests (35 run engine-free). W2-B 1,303 lines; H-PLANT 483; pte_trace 657 lines with 14 tests.
DEMONSTRATED CORRECTNESS: API.md maps 20 historical PTE defects to a test that fires on each; 9 of them use the real engine, rows or git. Its guards caught two of its own bugs during the build. It reproduces H-INST's four reach verdicts on hold_latch. It was never run on a fresh campaign. One seat built it in one night. The W2-AE packaging says "do not cite".
INTERFACE: Generic protocol; floats; seeded; no model call.
THROUGHPUT / SCALE: 40 tests in 53.5 s (report claim); otherwise not recorded.
COUPLING: explib has none. adapters/pte.py and W2-B import prometheus.ananke.
FIT TO SLOT: Exact twins. CAUS-02's "counts only if it changed state" is UNAPPLIED versus REACHED. MEAS-02 qualification gate: G1 to G4, with A4 as the fire test. Part of MEAS-01. Fails MEAS-07; no runner calls it.
MODIFICATION COST: S to M to promote the explib core: review, rational arithmetic, an adapter to the organism protocol. Rebuild: M to L. The PTE-specific ceilings and adversaries stay as worked examples.
VERIFIED BY ME: Imports, lockstep.py and attainable.py read in full; test counts; the INCOMPLETE note. The defect table and pass counts come from API.md and REPORT.md, not rerun.

----------------------------------------------------------------------
COMPONENT: Archaeon taint VM and attributed lineage core (per-byte material, four identities per birth)
PATHS: archaeon/lineage/taint_vm.py, core.py, assay_block.py, audit_envgate01.py; archaeon/tests/test_lineage_attribution.py
OWNER / DATES: Archaeon; one commit, 2026-09-24 (87f51c5ee).
WHAT IT REALLY DOES: At each birth it re-executes the executor on a label-carrying shadow of the frozen z80atlas VM. Every byte and register carries where its VALUE came from:
- an executor byte (E,p);
- a neighbour byte (N,q);
- an input, a constant or a zero;
- a computed value X with a conservative set of E/N sources.
Every result field must equal vm.execute; otherwise the AssertionError refuses the attribution. core.py gives each organism 32 material ids and records four identities per birth: executor, executed material, per-byte child contributors, and ecological host. A child continues the template's lineage if the template contributed >= G/2 copied bytes; otherwise it ORIGINATES a new one. It traces only and intervenes on nothing. Only data flow is tracked, not control or address dependence: it records material, not information.
SIZE: 639 lines. 12 tests, one of them slow and opt-in.
DEMONSTRATED CORRECTNESS: Designed fixtures with known answers:
- a hand-written replicator;
- an inert host running a resident copier (the host is not the ancestor);
- a host mutation that contributes no bytes;
- a half-and-half recombination program (16 + 16 bytes);
- a mutation byte becomes new material;
- an inserted control cannot become random through hosting;
- 23 host labels collapse to one lineage.
A differential test on 6,000 random tapes compares results, not labels.
INTERFACE: Pure Python, integers, deterministic; z80atlas-specific. A fast path handles trivial self-copies.
THROUGHPUT / SCALE: Block-13 replay to epoch 14,800 took 1,518 s for 54,616 births (PORTABILITY01_REPORT s1).
COUPLING: Imports archaeon.z80atlas (vm, engine, grammar, tasks) and proteus.foundry.prng. test_09 reads archaeon/envgate/LINEAGES.json.
FIT TO SLOT: Material tracing. Meets CAUS-06 and PROV-09 inside z80atlas; test_08 is close to PROV-09's check. Fails ORG-01.
MODIFICATION COST: M per substrate: a shadow interpreter for WM's roughly thirty instructions plus a material-id ledger; the lineage rules port almost unchanged. Rebuild: M.
VERIFIED BY ME: taint_vm.py, core.py and the tests read in full. Throughput from the report.

----------------------------------------------------------------------
COMPONENT: Archaeon causal lineage lens and attribution v0 (cross-engine heredity schema), plus COPIER-CENSUS-01
PATHS: archaeon/causal_lens/ (CAUSAL_LINEAGE_CONTRACT_v0.2.md, schema_v02.py, schema_v03.py, adapters/, FALSE_FRIENDS.md, PORTABILITY01_REPORT.md); archaeon/attribution/ (schema.py, classify.py, fixtures.py); archaeon/z80atlas/census/copier_census.py, RESULTS.json
OWNER / DATES: Archaeon. Lens 2026-09-26 to 09-28; attribution 09-28; census 09-23.
WHAT IT REALLY DOES:
- The lens maps each engine's preserved records into one event graph. Nodes: MATERIAL, BODY, IDENTITY, EXECUTION, TRANSFORMATION, HU, ARCH, ENV, LOCATION, CF_TEST.
- Ancestry follows only copies_from and contributes_material. Location, hosting, labels, resemblance and value matches never license descent.
- Values are YES, NO, NOT_IDENTIFIABLE, NOT_APPLICABLE or ILL_POSED.
- Attribution v0 adds a record validator, rules A1 to A17.
- The census sorts 10,000,000 uniform random tapes per stratum by behaviour, with no search.
SIZE: Lens 3,444 lines in 29 files; attribution 1,412 lines; 20 lens tests and 19 attribution tests; census 317 lines.
DEMONSTRATED CORRECTNESS:
- The Archaeon fossils A1 to A5 agree with native taint; PTE serves as the non-copy negative.
- The contract caught its own adapter defect (12 I2/I3 violations).
- BEE's resemblance-based native labels disagree with traced provenance on 847,000 births; 33.1% of BEE births are NOT_IDENTIFIABLE.
- Reviews withdrew a BEE/NPE "material" assay that had read source addresses and value matches as descent.
- Census: vmcopy32 had 96 exact copiers in 10,000,000 tapes (1 ungated, 95 gated); z80_32 had 0 in 10,000,000. A hand replicator is the ruler.
INTERFACE: Pure Python over JSON records; deterministic.
THROUGHPUT / SCALE: 28,964,089 BEE births mapped in LIGHT mode.
COUPLING: The BEE leg read 845 logs from a host-local directory outside the repo. Importers: archaeon and ops review scripts only.
FIT TO SLOT: Material tracing as a record format and rule set (CAUS-06 and PROV-09 semantics). The census gives a SRCH-03 random-hit rate. The lens is not a tracer itself.
MODIFICATION COST: M to adopt the v0.3 schema and validator as the kernel's heredity receipt; S to generalise the census. Rebuild: M.
VERIFIED BY ME: Contract sections 0 to 4, PORTABILITY01 sections 1 to 3, census header and RESULTS counts in source. False friends and review withdrawals from the dossier.

----------------------------------------------------------------------
COMPONENT: Nestor z8taint material tags (H3 ruler R3)
PATHS: roles/Nestor/campaigns/z80atlas-verify-2026-09-22/z8taint.py, tests/test_h3_material.py, H3_RULER_TOURNAMENT.json, PREREGISTRATION.md (A-24); npe-frontier-2026-09-30/x_mat_internalize/dense_taint.py
OWNER / DATES: Nestor. z8taint 2026-09-24 (cfe635933); dense_taint 2026-09-30.
WHAT IT REALLY DOES: A line-for-line copy of z8.run that tags each byte with the NICHE where its value was made.
- Loads, register copies, stores and LDIR carry tags.
- Any computed value becomes new material in the executor's niche, and so does a copy-mutation flip.
- R3 certifies a crossing when the genome is >= 0.50 easy-niche material.
- It traces only; no intervention.
SIZE: 361 + 94 lines. Script-style test: 9 adversarial fixtures plus a 400-program equivalence check.
DEMONSTRATED CORRECTNESS: In the tournament through the real pair code, R3 scored 9/9; founder fidelity 7, id 4, causal-edge window 4. Bit-identical to z8.run on 400 random programs. Documented limits:
- tags record WHERE, not WHOSE (FF-13);
- tags depend on an alignment heuristic under indels;
- material is not function;
- in C9 the easy niche was itself not competent, so R3 could only return near zero (a built-in false reject).
INTERFACE: Pure Python, integers, deterministic; Z8-specific.
THROUGHPUT / SCALE: Not recorded.
COUPLING: z8. Used by Nestor campaigns only.
FIT TO SLOT: Material tracing (CAUS-06) at niche granularity only. Weaker than Nestor's own later shadow tracer (SURPRISES 3).
MODIFICATION COST: Retire. A per-origin material ledger in a WM tracer is S to M from scratch.
VERIFIED BY ME: Header, test main and tournament scores in source. Limits taken from roles/Nestor/inference_harvest_2026-09-30/dossiers/C_origins_forensics_c9.md.

----------------------------------------------------------------------
COMPONENT: Nestor P-11 randomized-victim causal-copy assay
PATHS: roles/Nestor/campaigns/z80atlas-verify-2026-09-22/p11.py, P11_SPEC.md, tests/test_p11.py, T_P11_RECEIPT.json
OWNER / DATES: Nestor, 2026-09-23 (f28e5fd72). The specification was written before the 1,031 cases were read.
WHAT IT REALLY DOES: It re-executes a pair interaction from its exact pre-state on a private tape, with the victim half replaced by random bytes. There are 3 draws, seeded from sha256. A draw passes when all three hold:
- the victim ends >= 0.90 identical to the donor;
- >= 0.90 of the donor-directed changes were last value-changed by the donor;
- the same draw with the donor's foreign writes blocked stays below 0.90.
The event is causal if the predecessor criterion holds and >= 2 of 3 draws pass. It perturbs the victim and never the donor.
SIZE: 178 lines. Receipt: 15 checks, 14 pass, 1 n/a.
DEMONSTRATED CORRECTNESS: It catches the predecessor's three false accepts (padding writes, overwritten writes, partial copy on prior similarity). Each of C2, C4 and C5 is shown able to fire.
- False accepts (Artemis panel): all four zero-bit painters pass, at rates 0.90 to 1.00. Unsound for heredity.
- False rejects: complement child, host-executed guest, two cooperating tapes, and a budget-limited bytewise copier (C2 0/20, against a painter at 20/20).
- A copier on side 1 can be hijacked by its partner.
- C5 is nearly implied by C2 and C4 (spec s4).
- From a fresh state only 6 of 57 survivors re-pass.
- Per-draw files are gitignored (R-05).
INTERFACE: Z8-specific (z8.Ctx, OWN/ARENA, prov arrays). Integer counts with 0.90 ratios; deterministic.
THROUGHPUT / SCALE: 57 donors from a fresh state in 9.5 s wall (Artemis RESULT).
COUPLING: z8, constants.py. Used by Nestor, Artemis (from git-archive copies) and the Archaeon NPE adapter.
FIT TO SLOT: None for heredity. A template for checks of the form "randomize one party, block one channel" (construction causality).
MODIFICATION COST: Retire as a heredity ruler. Rebuilding the idea is S.
VERIFIED BY ME: p11.py, P11_SPEC.md, the test main and the receipt counts in source. Painter results from roles/Artemis/challenge/p11/RESULT.md.

----------------------------------------------------------------------
COMPONENT: Bellerophon bee_tracer (E-003 BEE shadow tracer)
PATHS: roles/Bellerophon/e003_2026-09-29/tools/bee_tracer.py, traced_world.py, run_fixtures.py, s4_tests.py, e003_analysis.py; E003_BEE_RESULT.md; ERRATA_2026-09-30.md
OWNER / DATES: Bellerophon, 2026-09-29 (5a1a20dce to 9128ed44c). Errata 09-30.
WHAT IT REALLY DOES: A label-carrying twin of BEE's frozen vm.execute, written from the ANCESTRY_PREREG v4/v5 text without reading the reference tracer.
- Every value carries a data label (E, INPUT, CONST, COMPUTED, COMPUTED_FROM) and a transitive set of pointer dependences.
- Each stored locus also records ctrl (dependences of every evaluated condition), exec dependences and the performer.
- Every run is value-checked against the frozen VM.
- The analysis adds a flip test: perturb a source locus and check that the child locus changes.
SIZE: bee_tracer 274 lines; tools 1,665 lines in 11 files; script tests only.
DEMONSTRATED CORRECTNESS: 32,827 births replayed bit for bit; 123,210 interactions value-equal; Archaeon's 28-fixture pack passes 28/28. Documented failures:
- raw agreement with the other tracer FAILED at 0.974, because the two read constant-only computations differently. It was cleared only by Amendment C11, adopted after production.
- "VALIDATED" rested on rules adopted after exposure. The confirmatory verdict is ALTERED; the verdict of record is OPEN (errata X1).
- The post-dominator ctrl scope is not implemented.
INTERFACE: Python, integers, deterministic; BEE-ISA-specific.
THROUGHPUT / SCALE: 123,210 interactions in one run; time not recorded.
COUPLING: A hard-coded host-local harness extracted outside the repo. The fixture pack is read with git show from 028f2eff8 on origin/archaeon/attribution-arc-2026-09-28, which is not on main.
FIT TO SLOT: Material tracing. The strongest dependence semantics in the tree: data, address and control. CAUS-06 and PROV-09 are possible. Fails ORG-01 and cannot be re-run from main.
MODIFICATION COST: The code does not port. Porting the semantics to WM is M, after the spec is merged (a decision). Rebuild: M.
VERIFIED BY ME: Tracer header, run_fixtures, README, result s0 to s2 and the errata read. The numbers are from those files, not rerun.

----------------------------------------------------------------------
COMPONENT: Artemis CVT-2 / CVT-R counterfactual variant transmission certificate
PATHS: roles/Artemis/challenge/p11/certs.py, specimens.py, tv.py, run_panel.py, RESULT.md; challenge/cvtr_nestor/; roles/Nestor/inference_saturation_wave2/W2-36_cvtr_audit/REPORT.md
OWNER / DATES: Artemis, 2026-09-28 (2af325f7b; 77bc0dbce to d050937ec). Audited by a Nestor worker 2026-09-30 (8f3a26ead).
WHAT IT REALLY DOES: For each parental byte i it tries variants x^0x01, x^0x80 and one hash-random value (all 255 values for toy specimens). It runs 4 generations x 3 draws against common random victims and records the offspring difference signature. A signature counts as defined if it appears in >= 2 of 3 draws.
- CVT-2 accepts when a variant gives defined differences at generations 1 and 2.
- CVT-R accepts when the generation-2 signature recurs at generation 3 or 4.
- TB = log2(1 + number of distinct transmitted classes).
SIZE: certs.py 115 lines; panel 1,187 lines; no pytest.
DEMONSTRATED CORRECTNESS: 17 constructed specimens with known heritable bits: painters (0 bits), 1-bit and 4-bit positives, copiers, a hash scrambler and a counter copier. Every cell matched the preregistered prediction, and TB calibrated exactly. False accepts found by W2-36:
- HALFBLANK, built never to reproduce itself, passes on 9/9 seeds;
- rescue mutants inside collapsing lineages pass;
- a single seed is a coin flip: 6 recorded verdicts flip against an 8-seed majority.
The proposed repair R* (inheritance, a lineage-fidelity floor, K = 8 seeds, three outcomes) is not adopted.
INTERFACE: certs.cvt(stepfn(G,g,k), G0, sid). Substrate-agnostic for byte genomes; integer counts; deterministic.
THROUGHPUT / SCALE: Constructed panel 60 s wall. W2-36 took about 34 CPU-min for 128 genomes x 8 seeds.
COUPLING: certs.py is stdlib only. The adapters load Nestor code from git-archive copies in scratch.
FIT TO SLOT: Heredity by intervention. An interventional alternative to material tracing for CAUS-06.
MODIFICATION COST: S to M: adopt R*, integer verdicts, a genome-protocol adapter. Rebuild: S to M.
VERIFIED BY ME: certs.py read in full; the RESULT confusion table and the W2-36 report read. Not rerun.

----------------------------------------------------------------------
COMPONENT: Ares carriers.py (edge- and SCC-aware lesion, transplant, swap, mutational opportunity)
PATHS: ares/carriers.py, ares/cycle2.py, ares/tests/test_carriers.py, ares/DESIGN_C2.md
OWNER / DATES: Ares. carriers.py 2026-09-23 (ab137f52b); ares/ 2026-09-19 to 09-25.
WHAT IT REALLY DOES: On an evolved graph it cuts each cross-step carrier class separately:
- self-loops, all recurrent edges, the keep coefficient, plasticity;
- every SCC and every recurrent edge;
- everything at once (state reset every step).
It compares rollout fitness against the intact organism. Collapse means (v - floor) <= 0.25 x gain. Classes: RECUR, KEEP, PLAST, MIXED, REDUNDANT, NONE.
- transplant splices a carrier into 64 random hosts against a matched random subcircuit; PORTABLE if the gap is >= 25% of gain.
- swap grafts a donor lineage's carrier into a host whose own carrier was cut.
- opportunity measures the chance that one mutation creates a carrier.
SIZE: 343 lines; 9 tests.
DEMONSTRATED CORRECTNESS: Hand-wired RECUR and KEEP carriers are classified and told apart, and the single carrier edge is found. An output-node self-loop is invisible to node ablation but caught here, and it moves under transplant. This is the W4 defect: node-only lesions could not remove output node 15, which closes the 3-node loop (Nyx #574). Known defects:
- a float32 argmax-tie residue contaminates the KEEP census (Artemis R-17);
- the W15 "redundancy" was MIXED 6 of 10;
- gate C was first reported as best-of-9; the per-pair median was 0.02.
INTERFACE: numpy float32; deterministic with balanced seeds; Ares substrate only. Population.copy() serves as the snapshot.
THROUGHPUT / SCALE: Not recorded.
COUPLING: ares.search, ares.substrate. Imported by nyx/readings/ares_w4_reading.py and an Artemis D001-08 script.
FIT TO SLOT: Lesion; carrier localisation. CAUS-05 shown on the output-loop case; CAUS-01 transplant against a sham. Fails MEAS-07, ORG-10 (no motif level) and CAUS-03 (no latent swap).
MODIFICATION COST: Port M. Rebuild for PN S to M; the graph cuts are generic code.
VERIFIED BY ME: carriers.py and the tests read in full. The defects come from the dossier.

----------------------------------------------------------------------
COMPONENT: Cosmos C3 P1/P2 memory certificate (decodability plus full-state interchange)
PATHS: prometheus/cosmos/c3/ (system.py, certify.py, probe.py, calib.py, gate.py, task.py); roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md; runs/GATE_v3_PASS_seeds6to10.json
OWNER / DATES: Cosmos; one commit, 2026-09-24 (940b486f2).
WHAT IT REALLY DOES: It defines a generic System protocol: init, noise, step, readout_features, full_state. The harness draws the noise, so paired episodes can share it.
- P1: the held-out cross-entropy gain, in bits, of (state, obs) over obs alone, against 49 permutations within obs strata. Held if p <= 0.02.
- P2: two episodes share every noise draw but carry different cues. The WHOLE state is swapped at t = k. Effect = accuracy intact minus accuracy swapped. Held if the effect exceeds 3 bootstrap SE.
- Classes: NONE, PASSIVE, FUNCTIONAL, INCOHERENT, INDETERMINATE.
SIZE: 461 lines. No pytest; gate.py is the test.
DEMONSTRATED CORRECTNESS: Six planted systems each got their expected class on 5 of 5 fresh seeds: no memory, a passive register, a functional register, a delay line, a misleading correlate, a noisy register. The v2 gate failed; seeds 1 to 5 informed amendment A2. Artemis R-10 ran C3 on PTE through an adapter (report verified):
- the verdict depends on which arrays are declared;
- starting one tick later flips PASSIVE to FUNCTIONAL;
- the noisy register was FUNCTIONAL on only 3 of 5 seeds at V=2, k=8.
The certificate localises nothing.
INTERFACE: numpy floats; scipy logistic probes; seeded and deterministic.
THROUGHPUT / SCALE: 30 certify calls of 3.38 to 24.4 s each, 292.86 s in total (GATE_v3 JSON).
COUPLING: numpy, scipy. No .py importer outside c3 (git grep, re-checked under the corrected rule).
FIT TO SLOT: Interchange (CAUS-02 and CAUS-03, at whole-state level). A planted-system gate written in code (the MEAS-02 pattern). Fails ORG-10, CAUS-05 and MEAS-07.
MODIFICATION COST: S: per-component swaps and a sweep of swap ticks. Rebuild: S to M.
VERIFIED BY ME: All six files, the gate JSON and the R-10 report read.

----------------------------------------------------------------------
COMPONENT: Tyche shortcut audits (causality audit, LEAD cheat control, TSD twins, keyed-PRF negatives) and natural-history tracer
PATHS: tyche/audits.py, tyche/worlds.py, tyche/v2/certify.py, tyche/v2/history_v2.py, tyche/tests/test_v0.py
OWNER / DATES: Tyche, 2026-09-30 (075e5fc21) to 2026-10-01.
WHAT IT REALLY DOES:
- causality_audit replaces all observations after each of 5 cuts with random values; the lens output up to the cut must be bit-identical.
- cheat_control builds a world where Y[t] = X[t+1] and a lens that uses the forbidden LEAD op. The cheat must reach z >= 4 and fail the audit, while an honest delay lens passes. Otherwise the instrument is void.
- TSD twins apply the same law to an independent hidden copy of the inputs.
- PRF worlds label each step with a keyed SHA-256 bit of a 24-step window. A significant gain on either is flagged FALSE_GRADIENT.
- history_v2 combines genealogy, the answer key and mutual information above a permutation null. It finds the first ancestor carrying each precursor and why each ancestor persisted (elite, significant case, noise case, reserve, drift).
None of these intervenes on an organism.
SIZE: 723 lines across the four modules; 35 tests in tyche/tests.
DEMONSTRATED CORRECTNESS: Tests named test_lead_cheat_is_caught, test_random_lenses_are_causal and test_planted_attainable_and_twin_dead (names read, tests not run). Needle size was never measured; my grep found only VOID_INITIAL_ACCESS checks.
INTERFACE: numpy; exact; the audit works on any function of a time series.
THROUGHPUT / SCALE: Not recorded.
COUPLING: Internal to tyche/.
FIT TO SLOT: Not a causal ruler. A fire-tested leak probe (the MEAS-02 fire-test pattern) and twin worlds (WLD-05).
MODIFICATION COST: Port S. Rebuild S.
VERIFIED BY ME: audits.py read in full; the TSD and PRF code, the docstrings and the test names.

----------------------------------------------------------------------
COMPONENT: Aether one-bit twin propagation assay and counterfactual-parent audit
PATHS: Aether/observatory/aeth03_propagation.py, aeth03_assay_audit.py; Aether/test/test_aeth03_propagation.py, test_aeth03_assay_audit.py; Aether/AETH-03/PROPAGATION_ASSAY_AUDIT.md
OWNER / DATES: Aether. Propagation 2026-09-26 to 09-30; audit 09-27.
WHAT IT REALLY DOES: It forks two copies of a warmed lattice world that differ in ONE bit at one site, under the same law and a shared hash-keyed noise stream.
- Each tick a newly differing site gets generation = 1 + the minimum generation of its differing neighbours.
- A new difference with no differing neighbour inside the law's declared radius is a locality violation and voids the result.
- SUSTAINED means generation >= 5, radius >= 5, and still adding after tick 50.
The parent audit replaces only ONE neighbour's state, steps once, and asks whether that change alone reproduces the new difference (a sufficient parent). This yields the exact causal generation.
SIZE: 702 lines; 8 tests.
DEMONSTRATED CORRECTNESS:
- a null twin (bit flipped twice) never differs;
- a designed relay chain gives one generation per hop with its content intact;
- an undeclared radius-2 effect is caught;
- a hidden flag breaks a bytes-only predicate but not the assay.
Adjacency generation equals causal generation in 100% of v1 events, 99% of add, 96.5% of mov and of rcv with perturbation off, and 84% of rcv with perturbation on. Joint causes: 2 of 2,793 events. The docstring at HEAD still claims exactness.
INTERFACE: numpy integers; deterministic, exact; lattice-specific and radius-specific.
THROUGHPUT / SCALE: 27,000 light-cone flips (dossier). Time not recorded.
COUPLING: Aether observatory only; outside Aether it is referenced only by docs and Fabric attempt receipts.
FIT TO SLOT: Exact twins (CAUS-02). Single-component sufficiency (an interchange primitive). Fails ORG-01.
MODIFICATION COST: S to M; it needs a declared causal radius per component. Rebuild: S.
VERIFIED BY ME: Docstrings, test names and the audit numbers.

----------------------------------------------------------------------
COMPONENT: Crius workspace content controls and neutral-edit null
PATHS: crius/evaluate.py, crius/exploit_probe.py, crius/c2_terminal.py, crius/workspace.py, crius/tests/
OWNER / DATES: Crius, 2026-09-18 to 09-23.
WHAT IT REALLY DOES: The same program runs one 50-task lifetime under each of these conditions:
- ACCUMULATED;
- FRESH (empty store);
- WORKSPACE_RESET and WORKSPACE_SCRAMBLED;
- ARTIFACT_ABLATION (blocks removed by id);
- ARTIFACT_TRANSPLANT and FULL_WORKSPACE_TRANSPLANT (forked from a snapshot);
- CODE_ONLY;
- ID_ONLY: empty blocks with the same ids, asking whether competence lives in the id counter.
reuse_gain = FRESH cost minus ACCUMULATED cost, on 3 sealed streams. The neutral-edit null re-scores up to 8 ancestry steps that add no typed op, giving the rate at which a neutral edit looks "selectable".
SIZE: About 1,000 lines for these parts; 41 tests in crius/tests.
DEMONSTRATED CORRECTNESS: The hand-written PROCEDURE_REUSE_C1 scores 46.1 against FRESH 20.7. TABLE_MEMO and NOCAL replay 0. Exploit clocks were caught by the ID-only controls (dossier). Known weaknesses:
- the typed calibration artifact gives every typed candidate a reuse_gain of about 7;
- empty records cost nothing;
- the null cannot separate +0.001 steps.
INTERFACE: Deterministic in (player, tasks, cfg, seed); float metrics; store snapshot, restore and scramble.
THROUGHPUT / SCALE: Not recorded.
COUPLING: Internal.
FIT TO SLOT: Store-level lesion and transplant for BUILD claims: ORG-02; DEV-05 (forks from a snapshot); CAUS-01 (ID_ONLY as the sham). Not search power.
MODIFICATION COST: S to M to re-express the conditions as protocol operations on persistent stores. Rebuild: S to M.
VERIFIED BY ME: Conditions and module headers in source. Numbers from the dossier.

----------------------------------------------------------------------
COMPONENT: Proteus mutation-kernel crucible (exact structural state enumeration), PROTEUS-46 falsifier, Boolean universe
PATHS: proteus/v0_5/kernel.py; proteus/v0_6/ (space.py, livekernel.py, PREREG_V0_6.md); proteus/round2/falsifier_46.py, PROTEUS-46_FALSIFIER.md; proteus/eval/boolean_universe.py
OWNER / DATES: Proteus. Kernel 2026-09-03; v0_6 09-03 to 09-11; falsifier 09-18; universe 09-16.
WHAT IT REALLY DOES:
- The crucible enumerates 2,044 valid structural states (genome length x tape words). Closure is proven: 817,600 proposals, 0 escapes. It measures the unselected one-mutation kernel by drawing a fresh random genome at each state, then reports the stationary distribution, currents and entropy production. Content is marginalised out.
- PROTEUS-46 applies K = 400 single edits per operator to a designed parent (one_value, scoring 3/6). It classifies each child against a designed target (two_key 6/6) as USEFUL, GRADED_DOWN, DESTROYED or NEUTRAL. It adds 200 random and 100 greedy 3-step walks.
- The Boolean universe computes the exact minimal expression size of every n-input truth table by dynamic programming.
SIZE: v0_5 1,342 lines; v0_6 2,142; falsifier 227; universe 224. 40 tests.
DEMONSTRATED CORRECTNESS: Closure proof; dual kernels; cross-runtime replay. Harmonia admitted the crucible as a detector, not as an absence instrument; its reversible-reference check cannot fail. PROTEUS-46: 0 of 4,267 (v0.4) and 0 of 4,881 (graph) edits were USEFUL; walks reached 6/6 in 0/200 and 0/100.
INTERFACE: Pure Python, SplitMix64, deterministic; Proteus grammar only.
THROUGHPUT / SCALE: Not recorded.
COUPLING: proteus.foundry.
FIT TO SLOT: Next to search power only: one-step reach from one planted parent, at one budget. The universe gives exact needle size (SRCH-03) for Boolean expression tasks. Not SRCH-02.
MODIFICATION COST: Retire as examples. A kernel estimator for a new grammar is S.
VERIFIED BY ME: Docstrings, PREREG_V0_6 numbers and the PROTEUS-46 result file.

----------------------------------------------------------------------
COMPONENT: Ergon E4 retention instrument with the D-5 expressible/reachable/findable split
PATHS: ergon/gen3/ (p3_common.py, gatefire_p3.py, cheat_control_n100.py, mde_p3.py, REVIEW_PACKET_P3_2026-09-11.txt); agent_d5_blind/ (PREREG-TASKS.md, VERDICT.md, reachability_oracle/, controls/, results/)
OWNER / DATES: Ergon, gen3 2026-09-11. D-5 by "Agent D-5", 2026-08-27 to 09-01.
WHAT IT REALLY DOES: D-5 sorts each task three ways.
- EXPRESSIBLE: a constructive witness of <= 24 instructions, or found by bounded synthesis.
- REACHABLE: by the R == E theorem every witness of length L is reachable within L+2 edits; checked on ablated physics.
- FINDABLE: CFR = solved / expressible, per budget rung (1,000, 3,000, 10,000, 30,000) and per stratum of witness length W*.
E4 compares retention policies by per-lineage CFR over 42 tasks at 30,000 evaluations.
- MDE80 was computed in advance: 1.22 pp at n 100.
- Five constructed gate-fire worlds go through the exact decide() path.
- An oracle witness planted in the library is the cheat control.
SIZE: gen3 926 lines; D-5 2,285 lines; 7 validation cases.
DEMONSTRATED CORRECTNESS: Gate-fire 5/5. Determinism 30/30 tied. The planted witness was detected at n 100 (+3.38 pp, CI [+2.31, +4.43]) and failed at n 30; the failure was kept. D-5 validation 7/7. No independent verification.
INTERFACE: Python with a Numba path bit-identical to the reference VM on 2,402-program orbits; deterministic.
THROUGHPUT / SCALE: 200 lineage-runs in 13.9 min wall on 8 workers.
COUPLING: agent_d5_blind.
FIT TO SLOT: Search power: the closest design in scope (SRCH-02 by budget rung and W*; SRCH-03 through minimal witness length). MEAS-02 pattern.
MODIFICATION COST: The method ports; the code is bound to RM-D5. Rebuild for WM: M.
VERIFIED BY ME: PREREG-TASKS s4 to s8, VERDICT, result JSONs and review packet s4 to s8.

----------------------------------------------------------------------
COMPONENT: Diomedes decomposition ladder, K0 coordinate census, proxy-reconstruction audit
PATHS: roles/Diomedes/coordinate_census.py, review_response_run.py, review_round2_run.py, cycle001_run.py
OWNER / DATES: Diomedes, 2026-08-24 to 09-13. Census 08-26.
WHAT IT REALLY DOES: A ladder of per-state AUC for ranking one-step substitutions:
- chance;
- recorded Z(x), which is exactly .5 by construction;
- the state-independent ceiling: actions ranked by their pooled label rate, computed on the evaluation labels;
- Z(x,a);
- the oracle, 1.0.
The K0 census makes this five arithmetic checks:
- headroom = oracle - ceiling, with a floor of 0.05;
- the gate lies inside the attainable range;
- the gate exceeds its own error;
- a cluster bootstrap;
- an identifiability ceiling, sum_s P(s)/|A(s)|.
Verdicts: ADEQUATE, INADEQUATE, VACUOUS. The proxy audit rebuilds the withheld variable from the companion features (about 41% ridge, 45% GBM, dossier).
SIZE: 388 + 361 + 296 lines; a self-test, no pytest.
DEMONSTRATED CORRECTNESS: Planted controls: CHEAT gives headroom exactly 0.5, absorbed to 0 when parity is declared as context; NEGATIVE gives 0; VACUOUS gives None. A differential test against an independent script agrees to 1e-9. Defects found by Nyx:
- the bootstrap has zero width when the cluster count is a power of two;
- None headroom labels VACUOUS as INADEQUATE.
INTERFACE: stdlib; exact AUC on integer scores; generic (actions, labels) dicts.
THROUGHPUT / SCALE: Not recorded.
COUPLING: The census has none. The runs read theseus/corpus.
FIT TO SLOT: Class exclusion for state-independent rankers (an in-sample plug-in, not a proof), plus an exact identifiability ceiling. The proxy is an impostor control (MEAS-04).
MODIFICATION COST: S to port and fix. Rebuild: S.
VERIFIED BY ME: The census code and planted controls in source. Ladder numbers from the dossier.

----------------------------------------------------------------------
WHOLE-SCOPE QUESTION A: SEARCH POWER
No component in this scope measures how often a search recovers planted targets as a function of distance from the founders and of budget. What each lead actually measures:
- Ergon E4 / D-5: CFR over known-expressible targets.
  - A frozen ladder of 1,000, 3,000, 10,000 and 30,000 evaluations, stratified by W* (EASY <= 4, MEDIUM 5 to 8, HARD 9 to 14, VERY_HARD >= 15). By R == E, W* stands in for edit distance from the seed.
  - The recorded curves are engineering runs only, 5 tasks per depth: depth 1 solved 4/5, depth 2 2/5, depth 3 1/5, with first-solve evaluation counts. Budget curve at 8,000: NAV-HC reach 0.35, NAV-POP 0.55.
  - E4 itself uses one budget and does not stratify by distance.
- Ananke: the plants (P-FLIP .978 at d9cc; XOR parity .850 inside 4222a5f7's genome) witness expressibility without search. They are compared with a single GA champion (.479 and .503).
  - verify_reach is about whether an intervention reaches a readout, not whether a search reaches a target.
  - T-REDISCOVER is PARKED and T-REACH-GAP OPEN; W2-G says no rediscovery search was run.
- Tyche: needle size was never measured. There are only initial-access void checks: a world is VOID if the best initial lens gains >= 0.03; in v1 the best of 4,560 initial pairs had to stay <= 0.061.
- Crius: a base rate for neutral edits; 0 complete mechanisms found; R-07's neutral path is an unverified claim.
- Proteus: a structural kernel with content marginalised out, and one planted pair at one budget (0/4,267 and 0/4,881 useful edits).
- Archaeon census: a random-hit rate only (96 exact copiers in 10,000,000 vmcopy32 tapes).
- Ares opportunity(): the rate at which one mutation creates a carrier.
Outside this scope: agent_d4_blind ("Agent D-4", 2026-08-27).
- It measures hit rate on 36 reachable targets per substrate, drawn from the substrate's own 150-step walks and stratified near/mid/far by phenotype remoteness.
- Budget 1,200 evaluations, with Wilson and target-cluster CIs, first-passage cost and re-findability. It is validated on synthetic geometry controls (8 per its verdict; the synthetic.py docstring lists C1 to C7).
- Example: S4_MEM far stratum 0.53 (32 of 60); median first passage 149 evaluations.
- Remoteness is phenotype distance, not edit distance, and there is one budget.
How I searched: git grep -l -i over *.py for findab|first.solve|recovery.rate|rediscover|search.power|planted...distance; then I read the D-4 metrics, PREREG s5 and the VERDICT. Re-run with ':!**/*holdout*' added: identical output.

----------------------------------------------------------------------
WHOLE-SCOPE QUESTION B: CLASS EXCLUSION
Yes, in pieces. None is generic, none ships with a world, and all are computed in floating point.
- Ananke (PTE):
  - Light-cone bound: an analytic bound on ANY program, from fastest transport per sampled world (256 worlds per cell; asynchronous waking treated optimistically). For XOR, acc <= .5 + f/2, where f is the fraction of scored trials in reach.
  - MAJ k-sensor ceilings by exact binomial: k <= 2 gives .70, k = 3 gives .784, k = 5 gives .837 (i.i.d. flips, p .3).
  - XOR: all 16 two-input Boolean readouts enumerated; every non-parity readout agrees on at most 3/4 of combinations, so .75. Proved for uniform inputs, but the real PTE environment gives .763, so the bound does not hold there.
  - FLIP copy-class (W2-L F5): a hand proof of exactly .75, attained by a constructed relay latch.
  - All of these were used only in post-hoc audits.
- Diomedes: the state-independent ceiling is measured in-sample on evaluation labels. The identifiability ceiling is exact for enumerable populations.
Outside this scope, found by grep:
- Ensorain: exact Bayes predictors in closed form or by forward filtering (ensorain/arc3/suff/worlds.py). The best order-k window predictor on the Even process by exhaustive context enumeration (replication/even_representational_floor.py): excess .2516 bits at k=0, falling to .0157 at k=8. Learners are scored against exact Bayes.
- Ludus: exact minimax or dynamic-programming value (bench/core.py solve). gap(k) for depth-k lookahead computed exhaustively over reachable states (depth_profile.py). The cheap-policy class is a hand-built ladder: Nim was admitted although Bouton's xor rule is optimal.
- primordial/metric/floors.py: the best constant action by exhaustive enumeration over 8^W actions.
No code computes the best memoryless or best k-state POLICY in an agent-environment loop.
How I searched: git grep -l -i over *.py for best memoryless|memoryless (policy|ceiling|bound|baseline)|k-state|best constant|optimal constant|state-independent ceiling|copy.policy|copy-class. Re-run with ':!**/*holdout*' added: the same 27 paths.

----------------------------------------------------------------------
COMPARISON
  SLOT: interchange and lesion
  1 Ananke lens stack     latent swap qualified on 4 designed carriers; PTE-bound, floats
  2 Cosmos C3 P2          generic System protocol + coded planted gate; whole state only
  3 Ares carriers.py      edge/SCC lesions, matched sham transplant; Ares float32
  4 Crius conditions      store reset/scramble/transplant/ID_ONLY; Crius-bound
  5 Aether parent audit   single-site sufficiency; lattice-bound
  SLOT: exact counterfactual twins
  1 Aether twin assay     exact, locality checked every tick, null twin
  2 W2-F explib reach     generic lockstep, CRN check, UNAPPLIED/REACHED; draft
  3 Ananke mirror twins   shared draws, but the design forces identities
  4 Nestor P-11 re-exec   exact re-execution; perturbs the victim only
  SLOT: material tracing (heredity, reuse)
  1 Bellerophon bee_tracer data+address+control deps; BEE-only, spec not on main
  2 Archaeon taint + core  per-byte ids, 4 identities, designed fixtures; data flow only
  3 Archaeon lens schema   neutral heredity record and rules; needs tracers
  4 Artemis CVT-R          interventional, substrate-agnostic; false accepts, R* pending
  5 Nestor z8taint         niche tags, WHERE not WHOSE
    Nestor P-11            retire: construction, not heredity
  SLOT: carrier localisation
  1 Ananke lens_swap+REL4 S/C/N census, FC <= 1%; mirror identity caveat
  2 Ares carriers.py      class/SCC/edge, covers output loops
  3 W2-F explib authority difference-vs-use; draft
  4 Cosmos C3             decodes but does not localise
  SLOT: search power (no in-scope fit)
  1 Ergon E4 / D-5 E/R/F  budget ladder + witness strata; engineering n = 5
  2 Proteus 46/universe   one planted pair; exact minimal sizes
  3 Archaeon census       random-hit rate only
  4 Ares opportunity      one-step creation rate
  5 Ananke plants         expressibility only
  6 Tyche, Crius          access checks and neutral base rates
    (out of scope: agent_d4_blind is the nearest)
  SLOT: class exclusion
  1 Ananke ceilings       per-task proofs; PTE-only; one bound fails in the real env
  2 Diomedes K0           generic headroom and identifiability; in-sample
    (out of scope: Ensorain, Ludus, primordial floors)
  SLOT: qualification / fire tests (MEAS-02)
  1 W2-F explib           G1-G4, identity audit A1-A4, mutation adequacy
  2 Cosmos C3 gate.py     planted systems, 5 of 5 seeds
  3 Ergon gate-fire       exact decide() path plus planted witness
  4 Tyche LEAD cheat      fires and is caught
  5 Diomedes controls     CHEAT/NEGATIVE/VACUOUS exact

----------------------------------------------------------------------
COULD NOT DETERMINE
- ANCESTRY_PREREG v1 to v5 and its reference tracers exist only on origin/archaeon/attribution-arc-2026-09-28. I did not read them, so I cannot say whether that spec could serve as the kernel's tracer specification.
- Nestor's shadow tracer: I read only its header and FIXTURES_RESULT.json.
- Not opened: W2-C pte_mut, Archaeon's WSE reachability table, the C4/C5 neutral walks, and Ananke W-H's "0/4 reproduction". The WSE table and the walks may bear on question A.
- Throughput for the lens, Ares, Tyche, Aether, Crius, Proteus and Diomedes is not recorded in any file I read.
- MEAS-12 (adaptive staircases) and CAUS-07 (carrier-noise opt-out): no implementation in any scoped component. A repo-wide grep returned only filenames in unrelated grading, SFE and WSE code, which I did not open.
- Unverified worker claims: Crius R-07 and Proteus D002-03q (neutral paths exist).
- Odysseus d2_audit refers to the D2 holdout. Not opened.
- Several count-only listings listed in SURPRISES 8(d) cannot be checked for holdout-named members, because checking would mean counting them. None of those numbers is used in this report.

----------------------------------------------------------------------
SURPRISES
1. W2-F explib is unpromoted, yet it is already a substrate-generic intervention and qualification library: a LockstepEngine protocol, 40 tests, and a table of 20 historical PTE defects it catches. It is closer to the RULERS layer than any promoted code. Its W2-AE packaging is INCOMPLETE.
2. The tracing spec, the reference tracers and the 28-fixture BEE pack live only on the arc branch, 85 commits ahead of origin/main. bee_tracer reads its fixtures with git show and runs a host-local harness, so it cannot be re-run from main.
3. Nestor has a second, stronger tracer for the same spec, outside this scope list: roles/Nestor/campaigns/ancestry-replay-2026-09-28/tracer/z8shadow.py. It has data labels, address sets, ctrl and mutation labels, 26 fixtures (9 inapplicable) and catches all its mutants. For CAUS-06 it is better than z8taint.
4. Ananke's lens.py matches CAUS-03 almost word for word and is qualified on designed carriers. But its own Wave 2 found two defects: the mirror design makes the site and channel swaps a single measurement, and the absolute rule cannot reach FLIP below normal accuracy .62 to .66.
5. Ananke's XOR .75 class bound is violated (.763) in its own environment.
6. Cosmos C3's System interface is the closest existing shape to ORG-01 for interchange, and it has already been run cross-substrate once (R-10 on PTE). That run showed that verdicts depend on the declared state boundary and on the swap tick.
7. The nearest existing SRCH-02 instrument is agent_d4_blind, which none of the dossier leads names.
8. Search-rule audit after the coordinator's correction (holdout-named FILES).
   Before the correction my git grep commands carried ':!**/*holdout*/**' ':!**/nestor_secrets/**' only, and several git ls-files listings carried no pathspec exclusion. Every command ran as "cd <worktree> && timeout N <command>"; below I quote the command without that prefix.
   What did NOT happen: no file whose name contains "holdout", and no nestor_secrets file, was opened, read, parsed or line-counted. No command output that I saw contained such a path.
   (a) A listing that covered the named file:
       - git ls-files prometheus/cosmos/tests | grep -i c3
       Returned nothing (empty). Inside the pipe it enumerated the file names in that directory, presumably including test_holdout_isolation.py. Names only.
   (b) Repo-wide content scans that also searched the contents of holdout-named files lying outside holdout directories. Paths only were returned; no returned path contains "holdout".
       Complete outputs, so no holdout-named file matched:
       - git grep -l -E 'from prometheus.ananke|import prometheus.ananke|prometheus\.ananke\.' -- ':!prometheus/ananke/**' ':!roles/Ananke/**' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -20  (6 paths)
       - git grep -l -E 'tyche\.audits|from \. import audits|from tyche import audits' -- ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head  (3)
       - git grep -l -E 'from ares|import ares' -- ':!ares/**' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head  (5)
       - git grep -l 'HALFBLANK' -- ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -20  (7)
       - git grep -l -i -E 'best memoryless|memoryless (policy|ceiling|bound|baseline)|k-state (policy|predictor)|best constant|optimal constant|best k-state|finite-state (bound|ceiling)|state-independent ceiling|copy.policy|copy-class' -- '*.py' ':!**/*holdout*/**' ':!**/nestor_secrets/**' ':!docs/phase3/**' | head -40  (27)
       - git grep -l -i -E 'opt.out|opt_out|optout' -- '*.py' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -10  (7)
       Truncated by head, but the shown, sorted list already runs past "prometheus/", so test_holdout_isolation.py did not match:
       - git grep -l -E 'archaeon\.causal_lens|archaeon\.attribution' -- ':!archaeon/**' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head  (10 shown)
       - git grep -l -E 'cosmos\.c3' -- ':!prometheus/cosmos/c3/**' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head  (10 shown)
       - git grep -l -E 'cosmos\.c3\.|from prometheus\.cosmos\.c3 import|cosmos/c3/' -- ':!prometheus/cosmos/c3/**' ':!**/*holdout*/**' ':!**/nestor_secrets/**' ':!docs/phase3/**' | head  (10 shown)
       Truncated before "prometheus/". Whether a holdout-named file matched past the cut is unknown; nothing past the cut was displayed:
       - git grep -l -E 'archaeon\.lineage|from archaeon\.lineage' -- ':!archaeon/lineage/**' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head
       - git grep -l -E 'aeth03_propagation' -- ':!Aether/observatory/aeth03_propagation.py' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head
       - git grep -l -i -E 'search.power|power curve|recovery rate|rediscover|planted (target|witness|solution).{0,40}(distance|edit)|distance from (the )?founder|edits? from (the )?(founder|seed)|time.to.(first|solve).{0,30}(depth|distance)' -- '*.py' '*.md' ':!**/*holdout*/**' ':!**/nestor_secrets/**' ':!docs/phase3/design/**' ':!docs/phase3/intake/**' | head -40
       - git grep -l -i -E 'search.power|recovery.rate|rediscover|planted.{0,30}(depth|distance)|distance.{0,20}founder|first.solve|time.to.first|findab' -- '*.py' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -40
       - git grep -l -i -E 'staircase|psychometric|just.noticeable' -- '*.py' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -10
       Count only:
       - git grep -n -E 'ananke(\.| import ).*(lens|swap_rel|lens_swap)' -- ':!prometheus/ananke/**' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | grep -v '^roles/Ananke/research/harvest/wave2/W2-.*/scratch' | awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -20
         20 per-file counts shown, all under roles/Ananke; rows past 20 not shown.
       Seat-scoped scans with the old tail. Their scopes could hold holdout-named files; none appeared in the output:
       - git grep -n -i -E 'z8taint|dense_taint|R3 material|material certificate' -- 'roles/Nestor/*.md' 'roles/Nestor/**/*.md' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -30  (30 lines shown, truncated)
       - git grep -n -i -E 'rediscover|REACH-GAP|search.power|recovery rate|planted.{0,30}(search|distance)' -- 'roles/Ananke/*.md' 'roles/Ananke/research/*.md' 'roles/Ananke/research/BACKLOG_V2.md' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -30  (17 lines)
       - git grep -n -i -E 'copy.{0,20}(ceiling|polic)' -- 'roles/Ananke/research/harvest/wave2/W2-L/*' 'roles/Ananke/research/harvest/wave2/W2-S/*' 'roles/Ananke/research/harvest/wave2/W2-AE/pkg/prometheus/ananke/audit/flip_b.py' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -30  (5)
       - git grep -n -i -E 'findab|R == E|R==E|expressible' -- 'agent_d5_blind/*' 'ergon/gen0/*' 'ergon/gen1/*' 'ergon/gen1a/*' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -40  (agent_d5_blind markdown lines only)
       - git grep -n -i -E 'gate.fire|gate_fire|MDE80|planted' -- 'ergon/gen3/*' 'ergon/gen2/*' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | grep -v '_results/' | head -30  (ergon gen2/gen3 lines only)
       - git grep -n -i -E 'needle|hit rate|random program|initial pairs|VOID' -- 'tyche/*.py' 'tyche/**/*.py' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -20  (10)
       - git grep -l -i -E 'exact bayes|bayes-optimal|bayes optimal' -- 'docs/phase3/intake/*' ':!**/*holdout*/**' ':!**/nestor_secrets/**' | head -20  (3)
       Two narrow scans with no exclusion at all; they returned lines only from PREREG_V0_6.md, run_space_audit.py and the falsifier file:
       - git grep -n -E '2,?044|ESCAPED_VALID' -- 'proteus/v0_6/*.py' 'proteus/v0_6/*.md' | head -8
       - git grep -n -E 'USEFUL' -- 'proteus/round2/PROTEUS-46_FALSIFIER.md' | head -8
   (c) Name-only listings without pathspec exclusions, filtered by grep. The whole index, or a whole seat tree, passed through the pipe undisplayed; that stream also carried any nestor_secrets path names and the credential-named file names under Aether/runpod.
       - git ls-files | grep -i -E 'bee_fixtures|bee_ref_tracer|ref_tracer_bee|npe_fixtures' | grep -v -i holdout | head  (1 path)
       - git ls-files | grep -i 'ANCESTRY_PREREG' | grep -v -i holdout | head  (nothing)
       - git ls-files | grep -i 'bee_tracer\|e003\|E-003' | grep -v -i holdout | grep -v nestor_secrets | head -30  (30 paths)
       - git ls-files roles/Nestor | grep -E 'z8taint|dense_taint|p11|P11' | grep -v -i holdout | grep -v nestor_secrets | head -40  (14)
       - git ls-files roles/Nestor | grep -i 'H3_RULER_TOURNAMENT' | head -1  (1)
       - git ls-files roles/Nestor/campaigns/z80atlas-forensics-2026-09-23 | grep -i gitignore  (1)
       - git ls-files roles/Cosmos/c3 | grep -v -i holdout | head -20  (7)
       - git ls-files roles/Cosmos/c3 | grep -i 'GATE_v3' | head -1  (1)
       - git ls-files prometheus/cosmos/c3/ | grep -v -i holdout  (7)
       - git ls-files Aether | grep -i 'PROPAGATION_ASSAY_AUDIT' | head -1  (1)
       - git ls-tree -r --name-only origin/archaeon/attribution-arc-2026-09-28 | grep -i -E 'ANCESTRY_PREREG|bee_fixtures|bee_ref_tracer|ref_tracer' | head -10  (10)
       Seat-scoped name listings were shown in full or truncated by head; none showed a holdout-named path. Scopes: prometheus/ananke, roles/Ananke/research and harvest, archaeon lineage/causal_lens/attribution/census, Nestor tests and tracer, Bellerophon e003, Artemis challenge, ares, crius, tyche, proteus, ergon gen0 to gen3, agent_d4_blind, agent_d5_blind, ensorain/arc3/suff, Aether/test.
   (d) Count-only listings:
       - git ls-files archaeon/lineage archaeon/causal_lens archaeon/attribution | wc -l  (70)
       - git ls-files theseus/corpus | wc -l  (3)
       - git ls-files roles/Ananke/research/harvest | grep -v '/out/' | grep '\.py$' | grep -v scratch_apply | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -60  (per-directory counts)
       - git ls-files agent_d5_blind | wc -l  (53; all 53 names were shown, none holdout-named)
       - git ls-files roles/Ananke/research/workers/W-Z/out/pairs | wc -l  (0)
       None of these numbers appears in this report.
   (e) Also: I grepped the Cosmos dossier (docs/phase3/intake/tantalus/seats/Cosmos.md, not a holdout path) with "holdout" among the search terms. It returned dossier lines that name the holdout directories; I opened none of them.
   (f) Re-run under the corrected exclusions: the question A and B searches, staircase, opt-out, HALFBLANK and the prometheus.ananke and ares importer checks returned the same displayed output as before; tyche returned its same 3 in-package importers. Also checked: no .py file outside c3 imports prometheus.cosmos.c3; the lens modules have 0 importers outside roles/Ananke; archaeon.lineage is referenced outside archaeon only by an ops review script and two documents. No conclusion in this report changes.
===END REPORT===
