# Techne -- forensic dossier (Tityos Phase 3 intake)

Crawler: Tityos worker g3 (Techne/Pheme), with three read-only sub-crawls (fossils/donors; substrate/Theseus;
lib/tests/cartography/loop). Worktree read: F:/Prometheus-worktrees/tityos-phase3. The brief named origin/main
5c98f59f1; the worktree HEAD at crawl time was 36ffe8073. Paths are repo-relative. Short SHAs are cited. Epistemic
labels per the Tityos brief. Two claims below were checked by direct execution or recomputation in this crawl and are
marked "[verified this crawl]".

## 0. Summary

Techne ("the Toolsmith") is the seat that built more measuring and verifying machinery than almost any other, through
five distinct incarnations in five months:
1. Apr 2026 toolsmith: wrapped PARI/SnapPy/LMFDB maths into techne/lib + prometheus_math, with "authority" tests
   (math-tdd skill) (7232ddde5, 0b90496fc).
2. May 2026 substrate owner: sigma_kernel (7-opcode claim/falsify/promote ledger), the Lehmer discovery_pipeline with a
   12-component KillVector, cross-domain RL envs, synthetic modal-collapse nulls, and operation of the Theseus
   substrate-generation daemon (658.5M records, 2,351 "promoted", 0 verified findings) (3205f0ea9, 0751491d7).
3. Aug 2026 self-audit loop: 62 hourly cycles studying its own instruments (measurement_guard, claim_record,
   control_certifier), plus a literature "cartography" campaign and E1 evolution-as-learning (both ended in
   instrument failure / not-adjudicable).
4. Early Sep: donor foundry (wrapping cvc5/discopy/egglog/pyribs/tensorly) and H0-H5 tool acquisition; adapters retired
   with 0 external importers (e2378a163).
5. Sep 12-30: Mechanism Archaeology "fossil vault" for Nyx: 189 specimen records (historic software 1960-present,
   ALife/QD prior art), FOSSIL_PACKET schema, run receipts, preservation controls, ASAL/CLIP experiment TECHNE-107,
   prior-art raid (Voyager/SIMA2/Genie3).
What it policed: correctness of computations, then promotion of mathematical "discoveries", then the integrity of its
own instruments, then the provenance/runnability of donor bodies. Strength of machinery, honestly: its best
instruments were NULL GENERATORS and CHEAT CONTROLS that killed its own headlines (modal-collapse synthetic null killed
the six-domain RL "transport" claim; F2 planted-relation calibration killed the Theseus corpus signal; the promotion
replay showed 2,351 promotions were confirm-by-assertion). Its GATES were mostly form-only or caller-asserted: the
kernel's FALSIFY oracle is a stub over a caller-supplied number; the discovery pipeline writes a synthetic CLEAR verdict
by SQL; two of four pipeline falsifiers are vacuous/tautological; the FOSSIL_PACKET validator accepts arbitrary hashes
and evidence strings. Almost every instrument was written, run, scored and reviewed by the same model family; Techne
says so itself repeatedly. No search/RL loop it ran ever demonstrated detection of a planted positive (0/36 withheld
rediscovered). Terminal state: READY, awaiting Aporia dispatch (roles/Techne/WORK_STATE.json, eab47ea82, 2026-09-30).

## 1. Charter and role evolution

- Canonical name Techne; self-styled "The Toolsmith"; instances signed "Techne[<host>-<id>]": m1-bbd0df6c, m2-04bd52c0
  (SPECTREX5, shut down 09-17, ce1aade47), gandalf-a04f7c25, gandalf-5983e3f7, gandalf-4c0c7e64 (M3/GANDALF, i7-920, no
  AVX/GPU) [IMPLEMENTATION FACT: journal file names, commit signatures].
- Original charter 2026-04-21 (roles/Techne/CHARTER.md, 7232ddde5): "I do not discover. I do not measure. I do not
  kill. I forge." Standing order 2 "Test against authority ... If no authority exists, document that the tool is
  unverified" [DESIGN INTENT].
- 2026-04-25 Perpetual Arsenal Mandate (0b90496fc): prometheus_math unified API, ARSENAL_ROADMAP, CI smoke tests
  [DESIGN INTENT].
- 2026-05-05 Substrate Mandate (3205f0ea9): owner of sigma_kernel, discovery_pipeline, kill_vector, navigator,
  cross-domain envs, Lehmer tooling, modal-collapse falsification; "Calibration discipline": synthetic null before any
  cross-domain claim, smoke catches, >=3-path triangulation, caveat-as-metadata; lead author of a negative-results
  methodology paper (pivot/methodology_paper_draft_v0.md) [DESIGN INTENT]. Note the charter text contradicts the seat's
  own first line ("I do not measure ... I do not kill") -- the role silently became a measurement seat.
- 2026-05-18..06-23 Theseus operation (theseus/, 0bd7b5c27 .. 7637b7f42); paused after external reviews 05-30
  [HISTORICAL CLAIM, roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-21.md].
- 2026-08-12 revival assessment (ce4f78f76): prometheus_math did not import (cypari missing) [REPORTED RESULT --
  UNVERIFIED].
- 2026-08-21 operator-authorised autonomous loop (techne/loop/LOOP_CHARTER.md) [HISTORICAL CLAIM].
- 2026-09-11 base-role adoption; operator rulings "verify the property, never the label" elevated fleet-wide from
  Techne's adoption pass; publication clause annotated superseded (8ec1fef1c) [IMPLEMENTATION FACT].
- 2026-09-12 fossil harvest + global archaeology charter; 2026-09-16 Mechanism Archaeology Pipeline Founding Charter +
  Amendment 2 (bc92fd942): Techne recovers bodies, Nyx cuts mechanisms, Harmonia adjudicates, Theophrastus admits to
  "soup"; "Techne does not decompose" [DESIGN INTENT].
- 2026-09-18 directive 4 ("refinery"): freeze census at 121, "No new broad fossil census until at least 10 mechanisms
  have received Harmonia verdicts" (roles/Techne/prompts/2026-09-18_refinery/OPERATOR_4_refinery.md) [DESIGN INTENT].
- 2026-09-21 directive 7 prior-art raid (roles/Techne/prompts/2026-09-21_prior_art_raid/) [DESIGN INTENT].
- Terminal: READY under MWO-0004 / CWO-2026-09-30C, no self-promotion (roles/Techne/resume.md, WORK_STATE.json)
  [IMPLEMENTATION FACT].
- Relations: Aporia (reviewer/dispatcher), Ergon (corpus/Learner consumer; Techne attacked Ergon's leakage gate),
  Charon (attacked Techne; ATK series), Nyx (consumer of fossils), Harmonia (adjudicator of Nyx cuts), Theophrastus
  (admission), Archaeon (H3 retention stream), Herakles, Vivarium.

## 2. Code/system architecture

Engines/subsystems (detail in engine.jsonl fragment):
- techne/lib/ (27 registered tools in techne/inventory.json, stale since 06-22 6d97e3412): mahler_measure,
  class_number, regulator, analytic_sha, selmer_rank, root_number, conductor, galois_group, alexander_polynomial,
  smith_normal_form, lll_reduction, tropical_rank, gpd_tail_fit, etc.; plus Aug epistemic controls
  measurement_guard.py (53864d612), claim_record.py (2e9e88af9), coefficient_domain [IMPLEMENTATION FACT].
- prometheus_math/ (shared with other seats; Techne-owned modules listed in RESPONSIBILITIES): discovery_pipeline.py,
  kill_vector.py, kill_vector_learner.py, kill_vector_navigator.py, modal_collapse_synthetic.py /
  _continuous.py, lehmer_brute_force.py + path_a/b/c, catalog_consistency.py (5 catalogs), discovery_promotion.py,
  domain envs (bsd_rank, modular_form, knot_trace_field, genus2, oeis_sleeping, mock_theta) [IMPLEMENTATION FACT].
- sigma_kernel/ (1,514-line sigma_kernel.py, d2ce08cfa 04-29 .. 6eeb1c823 05-09): RESOLVE/CLAIM/FALSIFY/GATE/PROMOTE/
  ERRATA/TRACE (+REWRITE/EQUIV d17a2ff8c); SQLite default (":memory:"), optional Postgres; migrations 001-006;
  omega_oracle.py (FALSIFY subprocess); triangulation_protocol.py + method_spec.py; exclusion_certificates/
  [IMPLEMENTATION FACT].
- theseus/ (daemon.py, bandit/yield_proportional.py, scoring/metrics_schema.py, training_weight.py,
  content_aware_promote.py, generators registry 63 entries / 55 active): JSONL corpus, signature_index.sqlite, Redis
  agora:discoveries; no generator imports sigma_kernel [IMPLEMENTATION FACT]. theseus/synth/ (09-30) is a separate
  Theseus-seat successor, not Techne's.
- techne/loop/ (88 files; cycles 001-062, 08-21..08-25), techne/ladder_circuits/ (36 modules; reasoning-ladder
  "circuits" R0-R12 + control_certifier.py), techne/cartography/ (87 files; OpenAlex/Crossref/arXiv/DBLP paper
  "genomes", lexical mechanism tagger, 864-cell archive, predicates P1-P6, frozen_tests.py), techne/research/
  evolution-as-learning/ (E1), techne/h3_retention/ (stream contract, pyribs adapter, archaeon_seam.py),
  techne/attacks/ (attack on Ergon), techne/acquisition/ (acquire.py receipts, license_audit, tool_check),
  techne/lib/donors/ (Gen-0 adapters, partly retired) [IMPLEMENTATION FACT].
- techne/fossils/ (~1,371 tracked files): harvest.py (acquire/run/verify/restore/mirror/repin), record.py,
  packet.py (FOSSIL_PACKET techne.fossil.packet/1), capsule.py, scaffold_control.py, world_manifest.py, landed.py,
  catalog.py, WORLDS.json, CATALOG.json (189 rows), specimens/<id>/ (record.json, UPSTREAM_HASHES.txt, recipe.json,
  receipts/), batches/batch01..batch17; bodies themselves gitignored in host-local vault/ [IMPLEMENTATION FACT].
- Scale: Theseus 273 batches / 658.5M records [REPORTED RESULT -- UNVERIFIED]; Lehmer deg-14 97.4M polynomials
  (726bde923) [REPORTED RESULT -- UNVERIFIED]; fossils 189 records, 4 packets, ~68 bodies on M3 [IMPLEMENTATION FACT
  for records; host counts REPORTED].

## 3. Inputs and outputs

- Inputs: researcher requests (techne/queue/), LMFDB/OEIS/Mossinghoff/knotinfo catalogs, RL env rollouts, Theseus
  generator outputs, open literature APIs (cartography), upstream source repositories and archives (fossils), operator
  directives (committed verbatim with MANIFEST under roles/Techne/prompts/).
- Outputs: tools + tests; sigma_kernel claims/verdicts; KillVectors; Theseus corpus JSONL; *_RESULTS.md per pilot;
  calibration verdicts (pivot/calibration_v*); loop cycle reports; fossil records/receipts/packets/capsules for Nyx;
  review packets (roles/Techne/REVIEW_PACKET_*.txt); attacks on other seats' gates.

## 4. Claim class it was meant to police

- "This function returns the mathematically correct value" (toolsmith; math-tdd authority tests).
- "This polynomial/object is a new discovery" (discovery_pipeline: in-band, reciprocal, irreducible, not in 5 catalogs,
  survives F1/F6/F9/F11).
- "This RL agent learned structure in domain X" (synthetic null control).
- "This generated relation is a real cross-catalog coupling" (Theseus F1/F2 gates).
- "This measurement is valid" (measurement_guard; claim_record provenance path).
- "This donor body is authentically the historical artifact, runs, and is preserved" (fossil record/packet/receipts,
  R19 provenance grades).
- It explicitly did NOT police "this is a mechanism" -- that was Nyx (nyx/atlas/mechanisms.py) [DESIGN INTENT].

## 5. Measurement methodology

- Tools: comparison to hard-coded authority values (LMFDB, Cohen tables, Mossinghoff, theorems); tolerance asserts
  (e.g. analytic_sha TOL=0.01) [IMPLEMENTATION FACT].
- Lehmer: numpy companion-matrix M filter in band (1+1e-6, 1.18), mpmath recheck at dps 30, then multi-path
  "triangulation" [IMPLEMENTATION FACT/REPORTED].
- KillVector: per-falsifier margins squashed with constants "picked by intuition" (KILL_VECTOR_SPEC.md:206-208)
  [DESIGN INTENT]; navigator ranks operators by expected kill-vector norm per region.
- Theseus reward: yield_score = info_density x diversity / learner_delta_steps (default 99) x saturation premium x
  duplicate penalty; info_density a fixed lookup on verdict/kill string [IMPLEMENTATION FACT]; reward never
  calibrated (deferred "until Ergon resumes", theseus/CHARTER.md) [DESIGN INTENT].
- Theseus F2: hold rate vs random re-pairing, contrast >= 0.10, 95% self-tautology guard [IMPLEMENTATION FACT per
  sub-crawl].
- Fossils: run recipes with expect blocks (exit/stdout_contains/regex); body re-hash after every run
  (body_preserved, since 7c5bfcb08); scaffold-strip control; rematerialize-on-second-host comparison [IMPLEMENTATION
  FACT per sub-crawl].
- ASAL/TECHNE-107: open-endedness score through CLIP ViT-B/32 on 7 arms (GARBAGE, HUECYCLE, LENIA Orbium, CYCLE2,
  NOISE, DRIFT_SYN, STATIC), 6 preregistered predictions (prereg 99cf4b33a, cited in the run commit as 7f4f51f6a -> run 44d109558) [IMPLEMENTATION FACT
  for commits; values REPORTED].
- Cartography: lexical tagger + deterministic predicates P1-P6 as the only route to CONFIRMED [IMPLEMENTATION FACT].

## 6. Null/control generation

- Modal-collapse synthetic null (prometheus_math/modal_collapse_synthetic.py, _continuous.py): x~N(0,I_20),
  y=w.x+b+noise, 21 bins, 0/100 reward; same trainers as domain envs; learnability check (least squares >= 60%) shows
  the null is solvable -- a VALID null with a positive control [REPORTED RESULT -- UNVERIFIED; code not read in full].
- F1 permutation null (discovery_pipeline.py:208): 30 coefficient shuffles, fixed seed; shuffling breaks the palindrome
  so the null is almost always higher M -- WEAK [CODE-INFERRED CAPABILITY].
- Theseus F2 calibration suite (pivot/calibration_v0..v3c): planted TRUE relations (Murasugi; EC torsion), parity and
  codomain decoys, stratified/marginal permutations; v3 independent-null via a1 uniform sampling [REPORTED RESULT --
  UNVERIFIED].
- Fossils: cheat controls in tests (one appended byte must DIFFER; a dropped catalog row must be detected); scaffold
  control baseline; destructive negative control for mirror-verify [IMPLEMENTATION FACT per sub-crawl].
- TECHNE-107: GARBAGE/NOISE/STATIC arms as negative-ish arms; cheat control "exact" [REPORTED RESULT -- UNVERIFIED].
- Cartography / crucible: random and majority baselines (exp3: every structured representation below random 83.3% and
  majority 0.81) [REPORTED RESULT -- UNVERIFIED].

## 7. Positive controls

- Lehmer's polynomial reproduced by brute force (asserted) [REPORTED RESULT -- UNVERIFIED].
- Modal-collapse: least-squares learnability authority on V3.
- F2: planted TRUE relations promoted (5bc1fa66b, 72c15b5e2) -- the ONLY gate in the substrate shown to detect a
  planted positive [REPORTED RESULT -- UNVERIFIED].
- measurement_guard: a value is unreadable until a positive control passes [IMPLEMENTATION FACT]; but "5/6 past failures
  caught" was later admitted circular (CAMPAIGN_ESCAPE_RATE_PREREG.md s3) [LATER CORRECTION].
- claim_check: planted control document expecting exactly 3 issues (techne/tests/claim_check_control.md)
  [IMPLEMENTATION FACT].
- Missing: no RL/search loop recovered a planted or withheld positive: withheld benchmark 0/36 in 3,000 episodes;
  D14_W5 "failed to find even the catalog witness" (prometheus_math/WITHHELD_BENCHMARK_RESULTS.md) [REPORTED RESULT
  -- UNVERIFIED]. The 05-30 GPT-5 review made "Can Theseus recover planted structure at better-than-null rates?" the
  decisive question; it was never answered before the pause [HISTORICAL CLAIM].

## 8. Negative controls

- Synthetic null (above); F2 decoys; fossils cheat controls; TECHNE-107 GARBAGE arm; claim_check negative docs.
- Vacuous negatives: F9 "simpler explanation" returns True unconditionally (discovery_pipeline.py ~272-282)
  [IMPLEMENTATION FACT, verified this crawl]; F11 "cross-validation" compares M(p) with M(reversed p), which are equal
  for every polynomial (reciprocal invariance of Mahler measure) and uses the same function [IMPLEMENTATION FACT,
  verified this crawl].

## 9. Neutral/intermediate controls

- Kernel WARN verdict (near miss |diff|<1.0) is promotable (sigma_kernel.py:822-934 per sub-crawl) [IMPLEMENTATION FACT].
- Fossil run classes (RUNNABLE_*/SOURCE_ONLY/NOT_ATTEMPTED/BUILDS_BUT_NOT_RUN) and TECHNE_STATE lattice
  (BODY_RECOVERED .. BEHAVIOR_REPRODUCED / PARTIALLY_REPRODUCED + 4 blocked states) [IMPLEMENTATION FACT].
- Scaffold control NOT_REQUIRED / REQUIRED / UNDECIDED (15/4/1 of 20) [REPORTED RESULT -- UNVERIFIED].
- Cartography NOT_ADJUDICABLE verdicts (TX-003, TX-004) [REPORTED RESULT].
- ORGAN0 (inspected fossil, no usable mechanism) kept in the denominator per operator directive 4 [DESIGN INTENT].

## 10. Qualification criteria / gates / thresholds

- Lehmer band 1.001 < M < 1.18; catalog match within 1e-5 [IMPLEMENTATION FACT].
- Kernel auto-caveat dps < 60 or convergence failed [IMPLEMENTATION FACT].
- Triangulation P6: >= 3 paths, >= 1 proof-bearing, >= 1 different independence_class -- class is a self-declared
  enum label (method_spec.py:286) [IMPLEMENTATION FACT per sub-crawl].
- Theseus F1 training_weight >= 0.6 (shape-only); F2 contrast >= 0.10 [IMPLEMENTATION FACT per sub-crawl].
- Fossil packet: >= 2 VERIFIED copies with distinct failure_domain labels unless PRESERVATION_GATE_OPEN (R38); receipt
  paths exist; capability matrix equals WORLDS.json [IMPLEMENTATION FACT].
- Operator: no new census until >= 10 mechanisms have Harmonia verdicts (directive 4); MKW-1 central wager
  ("falsified if no qualifying interaction after 50 resurrected cuts") never frozen
  (roles/Theophrastus/INBOX_TECHNE_MKW1_FREEZE_2026-09-16.md) [IMPLEMENTATION FACT].
- Reachability failures: E1 TAU_MATCH unsatisfiable (468a1f9ba); TX-003 pass threshold above ceiling; two own H0-H5
  gates "unreachable until I measured them" (8a03fdb1a) [REPORTED RESULT].

## 11. Statistical methods

- Mostly point thresholds and lifts vs uniform random; p<0.05 lifts in the May six-domain table without a
  majority-class baseline [HISTORICAL CLAIM]. Shuffle nulls with sigma (ladder cycle 003: TT rank 45 vs 52.5 +/- 0.95,
  "7.9 sigma", 9627bc1b7) [REPORTED RESULT -- UNVERIFIED]. KL with Laplace smoothing (127,000x figure, 72d061bc2).
  Preregistration with frozen predictions from loop cycle 042 onward and in TECHNE-107/E1/cartography
  [IMPLEMENTATION FACT]. Mutation assays (claim_record sensitivity 0.75, dd3a0d677) [REPORTED RESULT]. No multiple-
  testing correction found for Theseus' 658.5M-record search [UNKNOWN / AMBIGUOUS; not found].

## 12. Independence assumptions

- Five-catalog novelty check: Mossinghoff and lehmer_literature share source papers and curator and are compared with
  the same techne.lib.mahler_measure; 16 arXiv probe-corpus rows were promoted into the catalog (circular hit rate);
  LMFDB/OEIS/arXiv fail open (error = miss) [IMPLEMENTATION FACT per sub-crawl, MOSSINGHOFF_REFRESH_NOTES.md].
- Lehmer "triangulation": independence by declared label; all paths re-examine the same 17 entries from one numpy
  filter; Paths C and D rest on Mossinghoff-derived knowledge [IMPLEMENTATION FACT/CODE-INFERRED].
- Theseus: verdicts assigned by the generator that wrote the record (no sigma_kernel call); H4 pairs share the knot
  catalog [IMPLEMENTATION FACT].
- LLM reviewers: May "convergent" reviews by Claude, Gemini, ChatGPT and Aporia (Claude-family); Aporia flagged
  shared-prior risk (roles/Techne/APORIA_FEEDBACK_2026-05-05.md); REVIVAL_ASSESSMENT s3.2 forbids another LLM program
  review on the same grounds [HISTORICAL CLAIM].
- Authority tests: test_mahler_batch.py uses the seat's own scalar mahler_measure as "gold standard" (self-consistency);
  LMFDB values partly computed by PARI, which some tools wrap (partial circularity) [IMPLEMENTATION FACT / UNKNOWN].
- Cartography: reference labels from the same model, no second annotator, no kappa (146917ac4) [REPORTED RESULT].
- Batch 17 fossil facts written by ten same-model reader agents; conflict declared
  (REVIEW_PACKET_TECHNE_BATCH17_2026-09-30.txt) [IMPLEMENTATION FACT].
- Fossil pipeline: Techne -> Nyx -> Harmonia is separated by seat, but all are Claude instances with shared doctrine;
  Harmonia's ASAL port-identity check reproduced Techne's port byte-for-byte (ca23e97fa) -- identity of
  implementation, not independent re-implementation [IMPLEMENTATION FACT / CODE-INFERRED].
- Genuinely external correctors: Charon (ATK series, census audit), Ergon (M0.5 corrections), operator.

## 13. Provenance tracking

- Wins: verbatim operator directives with sha256 MANIFESTs (roles/Techne/prompts/*); fossil UPSTREAM_HASHES +
  TREE_SHA256 detected 23/57 bodies dirtied by in-place builds while receipts said PASS (VAULT_INTEGRITY_2026-09-12,
  7c5bfcb08) and 11 CRLF-hashed records on rematerialize (47e13ef65); 260 destroyed pins restored (fd5fa9fcf);
  promotion replay exposed the "formula fossil" (b092b86ac/1f86b2590); R19 provenance grades distinguish
  ORIGINAL_ARTIFACT / RECONSTRUCTION / DERIVED_RECOVERY_ARTIFACT (roles/Techne/prompts/2026-09-30_r19_grades/)
  [IMPLEMENTATION FACT / REPORTED].
- Failures: (a) 39 in-house Lenia rollouts labelled ORIGINAL_AUTHORITATIVE_RELEASE -- Harmonia ruled them
  DERIVED_RECOVERY_ARTIFACT (c7b9e10f9, 2026-09-30) [LATER CORRECTION]; (b) PAYLOAD_MANIFEST_ID of gzip/spacewar/lisp
  packets is sha256 of the CRLF-converted checkout, not of the committed blob (gzip d36d57f2... vs LF blob 86ba4fe2...)
  while the asal packet uses LF -- [IMPLEMENTATION FACT, verified this crawl by recomputation]; not recorded anywhere
  as noticed; (c) signature_index collapses 413M records into 3,311 shape classes, so promotions cannot be replayed on
  content (M05 findings); (d) lineage edge key drift "to" vs "target" across 158 edges (3906341d7); (e) NO_NETWORK_
  FETCH_DETECTED label on 48 records where no scan could run (fixed as NO_RECIPE, 05e918221); (f) stitch reproduction
  graded against a SECOND_HAND_EXPECTED_VALUE (8a03fdb1a); (g) committed acquire.py could not have produced the
  committed receipt (3463f9003).

## 14. Known defects (selected; see failures.md fragment)

- sigma_kernel FALSIFY oracle stub: compares caller-supplied true_mean (sigma_kernel/omega_oracle.py:39-69)
  [IMPLEMENTATION FACT, verified this crawl].
- discovery_pipeline writes a synthetic CLEAR verdict by SQL UPDATE, bypassing FALSIFY (lines ~478-510); terminal
  state hard-coded SHADOW_CATALOG; DISCOVERY_PIPELINE_VALIDATION.md:149 says "PROMOTED" [IMPLEMENTATION FACT, verified].
- F9 vacuous, F11 tautological [verified]. F1 weak.
- PROMOTE accepts WARN; caller chooses tier [IMPLEMENTATION FACT per sub-crawl].
- Exclusion certificate lehmer_deg14 has PLACEHOLDER hashes, strength=COMPLETE [IMPLEMENTATION FACT per sub-crawl].
- mpmath.polyroots cannot converge on repeated roots at any precision -> 17 (later 22 of 43) Lehmer entries
  "unverifiable" (388dff92f, a88b0d44f) [LATER CORRECTION].
- FOSSIL_PACKET validator form-only: accepts tree_sha256 "0"*64, fabricated FOSSIL_WORLD_ID, evidence "x", receipt path
  README.md, two "failure domains" on one host; crashes on wrong types [IMPLEMENTATION FACT per sub-crawl in-memory
  probes].
- Full test suite cannot collect on M2/M3 (17 collection errors); a test sat red 14 days (TECHNE-128) [REPORTED].
- Several lib tools (gpd_tail_fit, singularity_classifier, measurement_guard, claim_record, claim_check, sampling_lint)
  have no test file importing them [CODE-INFERRED per sub-crawl grep; FORENSIC_INVENTORY_2026-09-11.txt].

## 15. Historical audits performed (by and on this seat)

- By Techne: attack on Ergon leakage gate (techne/attacks/ATTACK_ergon_measurements_2026-08-25.md, f2a6719d4: manifest
  stamp does not cover renderer; zero-variance null wrote 12 PASS; ATK-016..018); ATK-014 tautology in Ergon's
  H(kp|cell)=0 (106c0bd5f); loop catches: Ergon load_prepass silent 100% drop (2f86c977c), 48 impossible knot volumes
  (95497b2eb); FORENSIC_INVENTORY_2026-09-11 (44 instruments with caller/test counts); promotion replay M0.5
  (b092b86ac); POET/ALife autopsy ledger (28 claims graded); vault integrity censuses.
- On Techne: Aporia feedback/handoff (05-05/06); 3-LLM advisory board 05-22 killed five celebrated metrics; GPT-5 review
  05-30 (pause); Charon ATK-020 (canary harness no false-alarm denominator, 3e15c54e8); Charon/Ergon corrections to
  M0.5; Elenchus METHOD-FLAW on SCS OPTIMAL at 188% error (retro corpus P13; d3ce43c24); Harmonia rulings (R19 rollout
  grade c7b9e10f9; ASAL adjudication 850fec325); Nyx flags on R38 preservation (INBOX_NYX_RE_313_AMENDMENT3_2026-09-16.md).

## 16. Historical findings (outcome labels on the record)

- Six-domain RL lifts +1.37x..+18x (05-02) -- LATER OVERTURNED (class-prior recovery; 7339269a1).
- 127,000x kill-vector distinguishability (72d061bc2) -- REPORTED POSITIVE, never retracted; ratio over a near-zero,
  smoothing-dependent denominator from one cell [CODE-INFERRED weakness].
- Lehmer deg-14 +/-5: INCONCLUSIVE (726bde923) -> "H5_CONFIRMED-local-lemma" by triangulation (05-05) -> verifier
  false-negative found (388dff92f) -> H1_LOCAL_LEMMA with precondition (a88b0d44f) -- LATER OVERTURNED / MIXED.
- "Precision axis is FLAT; strategy discriminates" (sprint) -- LATER OVERTURNED (built on the verifier bug).
- Theseus 2,351 promoted -- LATER OVERTURNED (confirm-by-assertion; formula fossil; 1,991 parity tautologies 1321ba7c3).
- Theseus corpus cross-catalog signal (v2: 198/1,068 groups) -- LATER OVERTURNED (mutation inheritance ~91%,
  category error; c59d782de, 962012725).
- c5 exploration premium "a mirage" then "over-corrected" (e05463ec6, b37c074ba) -- INCONCLUSIVE.
- Withheld benchmark 0/36 -- REPORTED NEGATIVE/NULL.
- Cartography TX-001 PASS (6.0% -> 57.3% placement) -- MIXED (cycle-041 audit: do not apply, n=13); TX-003/TX-004
  NOT_ADJUDICABLE; tagger 1.9% correct placement -- INSTRUMENT FAILURE.
- E1 evolution-as-learning -- INSTRUMENT FAILURE (n_pairs=0 every arm; 468a1f9ba).
- H3 retention agreement pyribs vs Archaeon -- LATER OVERTURNED (coincidental equal-width bins; erratum in
  H3_ALPHA_RECEIPT_2026-09-10.md), then forced by construction.
- Preservation thesis strong form -- REPORTED NEGATIVE (0c2735579).
- Spacewar! BEHAVIOR_REPRODUCED -> PARTIALLY_REPRODUCED (17443dcc8 -> feab5d00e) -- LATER OVERTURNED (downgraded).
- TECHNE-107 ASAL through CLIP: garbage 0.817 more "open-ended" than living Lenia 0.847; 6/6 predictions pass -- REPORTED
  POSITIVE (metric pathology); morning "recurrence reading" retracted same day (44d109558).
- ASAL legit search (Harmonia 850fec325): best legitimate alive Lenia 0.7665 does not cross garbage; but raw catalogue
  crosses (I0 PREDICTION_FAILED) and a genuine coherent rollout crosses the 2-sd line (0.7933); 650/1,045 draws
  refused by Techne's port -- MIXED.
- Donor foundry: 0 importers outside techne/ after 11 days -- REPORTED NEGATIVE (closeout 54e91768d).
- Voyager source autopsy; SIMA 2 / Genie 3 NO_PUBLIC_SOURCE by quote -- REPORTED (descriptive).

## 17. Later corrections (timelines)

1. Six-domain lift: claim 05-02 -> challenge Aporia/Gemini/ChatGPT (modal collapse) -> synthetic null 05-04 (REINFORCE
   4.91% vs random 4.84%) -> retraction 7339269a1 -> NOT propagated: DISCOVERY_PIPELINE_VALIDATION.md:61-65,358,
   GENUS2/MODULAR_FORM/MOCK_THETA/KNOT_TRACE_FIELD _RESULTS.md still headline lifts [LATER CORRECTION / CONTRADICTION].
2. Lehmer deg-14: 05-04 INCONCLUSIVE -> 05-05 H5_CONFIRMED-local-lemma -> 08-24 cycle 052/053 repeated-root bug ->
   08-24 af5073620 retracts cycle 053's side claim of catalog mislabel -> 08-27 a88b0d44f H1_LOCAL_LEMMA under
   cyclotomic-free precondition. theseus/scoring/info_density.py:6 still cites the old example.
3. Theseus promotions: 05-25 1321ba7c3 parity tautologies -> retune 90+ fires 0 promotions -> 06-23 M0.5 replay
   (confirm-by-assertion, formula fossil) -> fixes recommended, apparently unshipped.
4. Theseus h2: 99.99% kill rate -> advisory board "applicability failure" -> h2 audit 9f0cab7f1 ran a SUBSTITUTED test
   (re-implemented r^2 mapping on synthetic lines instead of the preregistered 100 mathlib theorems) and booked
   CALIBRATED_OK [LATER CORRECTION, aimed beside the claim].
5. P149 magnitude tautology (Aporia c9af3911b, aporia/docs/CYCLE_150N_MAGNITUDE_TAUTOLOGY_2026-08-24.md): Theseus corpus
   outcome measures unit comparability (abs_diff_le_N between a small knot invariant and a 4-digit conductor can never
   hold; generator identity predicts ~98%) -> killed Aporia's 147-K/148-L arc -> Charon 99b05311c extended to Diomedes'
   75% headline -> codified as attacks/preflight.py degenerate_strata (lines ~70-83).
6. P150 "corpus closed" (06ea3ae14) -> Charon f93f91fd1 five minutes later (census missed c1 and .gz) -> Charon 69f161ecf
   census instrument near-tautological, v2 NOT-EARNED -> Aporia accepted 66e06e027.
7. measurement_guard "caught 5/6 past failures" -> CAMPAIGN_ESCAPE_RATE_PREREG.md s3 "a fit statistic, not a
   generalization estimate"; escape rate for plausible errors "close to 1" (s2).
8. claim_record: cycle 060 "cannot block anything" (d36f8c3fe) -> 061 retracted (7181c2390, blocked 2/5) -> 062 mutation
   assay sensitivity 0.75; six-order-of-magnitude corruption still PROMOTABLE (dd3a0d677): "a PROVENANCE gate, not a
   truth gate".
9. Loop cycle corrections 08-24: "cross-role" population 87.5% one role (b7edca829); "2.3x" cost was 1% (504418e43);
   "7 of 8" detection was 4/8 (53864d612).
10. ASAL rollout fossils grade ORIGINAL_AUTHORITATIVE_RELEASE -> Nyx #1074 -> Harmonia c7b9e10f9 DERIVED_RECOVERY_
    ARTIFACT; correction to the 39 records assigned to Techne (TECHNE-129 open at terminal state).
11. Spacewar! downgraded; gzip packet PRESERVATION contradiction with R38 flagged twice by Nyx, unaddressed at HEAD.
12. SDP fixture "ground truth" 33,332x too large (d3ce43c24, 09-11).

## 18. Pivots

toolsmith (04-21) -> arsenal (04-25) -> substrate/discovery + calibration (05-01..05) -> Theseus generation engine
(05-18..05-30, paused) -> dormancy/revival assessment (06-23, 08-12) -> self-audit loop (08-21..25) -> GEN-0 donors
(08-31) -> cartography (08-31..09-01) -> crucible/E1 (09-01..04) -> H0-H5 acquisition (09-09..11) -> donor adapters
retired (09-12) -> fossil vault (09-12..) -> mechanism archaeology pipeline (09-16) -> ALife/ASAL refinery (09-17..19)
-> prior-art raid (09-21) -> reset (09-25) -> batch 17 + READY (09-30). Each pivot abandoned rather than closed its
predecessor's open calibration questions (e.g. Theseus planted-recovery question; escape-rate campaign 17/20 cycles
unrun; cartography 43/96 cycles; E1 v3 never frozen) [HISTORICAL CLAIM].

## 19. Journals / TODOs / backlogs

- roles/Techne/journal/ (12 files 2026-09-11 .. 09-30; RESET log 2026-09-25_gandalf-a04f7c25_RESET.md is the best index).
- roles/Techne/BACKLOG_H0H5.md: open TECHNE-122 (prior-art raid sections II-IX, XL), 123 (GPU-blocked), 65/100
  (off-host mirror; waiting one operator line since 09-12), 89 (packets for 118 bodies), 92 (MKW-1 freeze), 98
  (remove 15 decorative accommodations), 128 (runnable test list), 129 (rollout grade), 131 (scorer successor), 133
  (bodies not read-only).
- roles/Techne/resume.md, WORK_STATE.json (terminal READY).
- techne/PROJECT_BACKLOG_1000.md (paused since 05-02), techne/BACKLOG.md (May plan, superseded), techne/TDD_LOG.md (494
  self-scored rows), techne/ARSENAL_ROADMAP.md.
- roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-21.md (13,802 lines; Fires #34-#236; pause), other SUBSTRATE_FIRE_LOG_*.

## 20. Research reports

- roles/Techne/SPRINT_2026-05-01_to_2026-05-05.md -- sprint arc incl. retractions and the unretracted 127,000x.
- pivot/methodology_paper_draft_v0.md -- "Negative Results in AI for Mathematical Discovery: ... Reward Pathology and
  Self-Falsifying Systems" (N=1 case study, May RL, not the Theseus bandit).
- prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md, NATIVE_KILL_VECTOR_PILOT_RESULTS.md,
  LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md, WITHHELD_BENCHMARK_RESULTS.md, DISCOVERY_PIPELINE_VALIDATION.md (stale).
- pivot/calibration_v0..v2, calibration_v3_VERDICT_2026-06-03.md, v3c -- Theseus F2 calibration.
- roles/Techne/M05_PROMOTION_REPLAY_FINDINGS_2026-06-23.md -- confirm-by-assertion audit.
- roles/Techne/REVIVAL_ASSESSMENT_2026-08-12.md -- dormancy, Organism-Zero proposal (never built).
- techne/loop/CAMPAIGN_ESCAPE_RATE_PREREG.md, EPISTEMIC_CONTROLS_2026-08-25.md, REVIEW_PACKET_049_059.md.
- roles/Techne/CARTOGRAPHY_FROZEN_TESTS_2026-09-01.md; techne/cartography/exp3_results.json, gate_tagger_metrics.json.
- techne/research/evolution-as-learning/E1_PREREGISTRATION_v2.md, E1_RESULT_INSTRUMENT_FAILURE.md.
- roles/Techne/H3_ALPHA_RECEIPT_2026-09-10.md (+ erratum), H0H5_TOOL_ACQUISITION_2026-09-09.md.
- roles/Techne/FORENSIC_INVENTORY_2026-09-11.txt, DONOR_FOUNDRY_CLOSEOUT_2026-09-12.md.
- roles/Techne/POET_ALIFE_GATHER_2026-09-17.md, POET_ALIFE_AUTOPSY_LEDGER_2026-09-17.md.
- techne/acquisition/poet_alife/TECHNE107_RESULTS_2026-09-17.md -- ASAL/CLIP metric pathology.
- roles/Techne/prompts/2026-09-21_prior_art_raid/FIRST_RETURN_2026-09-21.md -- Voyager autopsy, SIMA 2/Genie 3.
- roles/Techne/prompts/2026-09-30_r19_grades/RULING_R19_GRADE_BY_SOURCE_TYPE.md -- provenance grade ruling.

## 21. Failure cases

False positives (with the instrument that let them through):
- Caller-asserted verdicts accepted as falsification (omega_oracle stub; synthetic CLEAR; Theseus self-verdicts).
- Shape-only promotion gate (training_weight) -> 2,351 promotions.
- Lift vs uniform random instead of majority class -> six-domain claim.
- Mutation inheritance / selection bias in generated corpora; claim-shape category error.
- Outcome variable measuring units (P149) -- corpus Techne's generators produced.
- Ratio over near-zero denominators (127,000x).
- Catalog circularity (probe corpus promoted into catalog).
- Declared-label independence (triangulation).
- Audit aimed beside the claim (h2 substituted test).
- Coincidental implementation agreement (H3 bins).
- Gates widened after seeing output (minpack smoke harness twice; FOSSIL_HANDOFF_NYX_2026-09-12.md); Spacewar pixel
  band [20,20000] judged by eye.
- Provenance mislabel (in-house rollouts as original release).
Plausible false negatives:
- Numerical verifier blind on repeated roots at any precision; coarse float filter before exact verification.
- M-value catalog matching hides novel polynomials with a known M; cyclotomic precondition excludes classes.
- RL modal collapse cannot reach rare targets (0/36).
- Over-correction from single samples (c5 premium).
- Retuned gate makes everything unpromotable (90+ fires at 0).
- Unsatisfiable gates (E1 TAU_MATCH, TX-003, LIM-003 fix creating false PERSISTENT_COVERAGE_HOLE 683467597).
- Census from failing tests misses importorskip-skipped tests (156 hidden tests, f98d8670e).
- control_certifier certifies relative to a fixed 5-shape taxonomy (missed a hang).
- 69 NOT_ATTEMPTED specimens; scaffold "decorative" judged by smoke pass, not output equivalence.
- ASAL port refused 650/1,045 draws (coverage defect), shaping what the legit search could find.

## 22. Mechanism archaeology

- What constitutes a mechanism: Founding Charter s2 "mechanisms under pressures ... Historical names are provenance.
  They are not ontology" [DESIGN INTENT]; operationally defined by Nyx (nyx/atlas/mechanisms.py, d8741f71a: "A
  MECHANISM IS NOT A PACKET"; persistent id accumulating evidence; dispositions PROPOSED .. SURVIVED_TRANSPLANT)
  [IMPLEMENTATION FACT]. Techne was forbidden to decompose.
- Donor/fossil selection: operator directives (fossil harvest 09-12; global archaeology charter "HIGH RECALL ... False
  positives are cheap", diversity of lineage and selection pressure, "Do not let LLM semantic similarity discard
  specimens", ~1960-present); Techne picked specimens batch by batch; later batches operator-named (ALife six,
  prior-art raid, batch 17 "find some stuff to download ... for Nyx to chop up") [DESIGN INTENT / HISTORICAL CLAIM].
  No sampling frame, no inclusion/exclusion ledger against a defined population was found -- selection is curatorial
  [UNKNOWN / AMBIGUOUS: absence after search of README, charters, batch scripts].
- Families represented: SAT/CDCL/local search, planning, Netlib numerics, compression, ECC, Lisp/Scheme/Forth/Prolog/
  APL, BSD/TCP stacks, concurrency-failure fixtures, distributed consensus, controllers (PID/MPC/L1/Kalman), HDL cores,
  pre-1970 programs (ELIZA, LISP 1.5, Spacewar!), ALife/QD/open-endedness (Avida, Tierra, Lenia, POET, ASAL,
  MAP-Elites, QDax, pyribs, NEAT, FunSearch, OpenEvolve, DGM, AI-Scientist-v2) [IMPLEMENTATION FACT from records].
  Heavily weighted to engineered software, not evolved/biological mechanisms.
- Decomposition: FOSSIL_PACKET 13 Techne fields + 13 downstream (Nyx/Harmonia/Theophrastus/operator) fields; Nyx made
  123 cut records, Stage A frozen 120/121 (ab389760a), "15 recurrence candidates by reading" (aca5cf4c6) -- descriptive,
  reading-based [IMPLEMENTATION FACT / CODE-INFERRED].
- Causal lesions: prediction packets freeze interventions/cheats/positive controls/falsifiers (nyx/atlas/predictions/
  *.FREEZE); only ~5 packets issued; Techne's own causal-style measurements without editing bodies (ld --wrap Level-3
  fraction 4603b27c7; EISPACK cache NULL 4747bdcbb; scaffold-strip ablation 15/20 decorative). The scaffold control is
  the closest thing to a lesion study and it lesions BUILD accommodations, not mechanisms [REPORTED RESULT].
- Transplantability: nyx/atlas/gates/MECHANISMS.json lists 7 mechanisms, 0 SURVIVED_TRANSPLANT, one transplant OFFERED
  (MECH-ASAL-OE-SCORE) [IMPLEMENTATION FACT per sub-crawl]. No transplant was executed.
- Correlation-only?: the POET novelty cut was adjudicated "EXECUTED STRUCTURAL IDENTITY; NOT CONFIRMATORY"; most cuts
  are boundary annotations by reading; the only executed interventional verdicts are on ASAL (metric exploit vs
  genuine) and particles (Nyx/Harmonia lane) [REPORTED RESULT -- UNVERIFIED].
- Throughput mismatch: operator 09-18 "107/121 inspected, but only one adjudicated cut"; the gzip pilot packet never got
  past Nyx (all Harmonia/Theophrastus fields null); MKW-1 wager never frozen.
- Prior-art corpus: POET/ALife gather (30 papers, 8 repos, FIND+PIN only), autopsy ledger (28 claims: 13
  VERIFIED_SOURCE, 6 VERIFIED_API, 2 MEASURED, 5 PAPER_ONLY, 1 CORRECTED, 1 NOT_VERIFIED); prior-art raid section XV
  only (Voyager fossilized @55e45a88, 457 files; SIMA 2 and Genie 3 NO_PUBLIC_SOURCE by primary quote); sections
  I.B-XIV not done (TECHNE-122) [REPORTED RESULT -- UNVERIFIED].

## 23. Novelty/prior-art audit

- Mathematical novelty (May): "novel" = not found in 5 catalogs (Mossinghoff, lehmer_literature, LMFDB, OEIS, arXiv
  probe). Blind spots: catalogs share curator/sources; network failures count as misses (absence-of-match treated as
  novelty); M-value matching; probe corpus promoted into catalog. The terminal state of any survivor was SHADOW_CATALOG,
  never PROMOTED -- the code itself refused to call anything new to science [IMPLEMENTATION FACT]. Docs contradict
  (DISCOVERY_PIPELINE_VALIDATION.md:149).
- Engineering novelty (Sep): the prior-art raid's premise is the inverse -- "DO NOT REINVENT A WHEEL" -- i.e. absence of
  prior art was treated as a defect of Prometheus' search, not as novelty [DESIGN INTENT]. Grading vocabulary
  (VERIFIED_SOURCE / VERIFIED_API / PRIMARY_QUOTE / NO_PUBLIC_SOURCE) distinguishes "searched and not found" from "lab
  says no public source" [IMPLEMENTATION FACT]. Convergence noted: Voyager skill schema = Techne CAPSULE/HANDOFF = Nyx
  mechanism ledger shape -- an "unfamiliar to Prometheus" design was in fact prior art.
- "Unfamiliar to Prometheus" vs "new to science": Theseus' "2,351 promoted" and the 127,000x figure were internal
  proxies; the 3-LLM board killed five such metrics. Cartography could not even place papers correctly (1.9%), so it
  could not have supported a novelty claim.

## 24. Lens inventory

- Arbitrary-precision number-theory toolkit (techne/lib, prometheus_math): reusable, authority-tested in places,
  resolution limited by numerical verifier pathologies (repeated roots) and untested modules; partial circularity with
  PARI/LMFDB.
- Synthetic-null harness for RL claims (modal_collapse_*): reusable pattern; the strongest instrument the seat built;
  validated only on linear tasks.
- F2 planted-relation contrast gate: reusable for relation-mining corpora; only gate with planted-positive detection
  shown; v0->v1 transfer reported, not independently checked.
- sigma_kernel claim ledger: a typed provenance/claim schema; as a truth instrument toy-grade (stub oracle, assertion
  promotion, demo scale 0-5 symbols).
- Fossil vault (harvest/receipts/hash-preservation/rematerialize): a genuine preservation instrument for software
  bodies with demonstrated detection of drift (23/57, 11 CRLF, 260 pins); packet validator form-only; 2-host
  preservation not achieved; ~half of specimens never executed.
- Ancestry/observer instruments for ALife (TECHNE-107 CLIP arms, Lenia port, harm55_flax_score.py, capsule.py):
  calibrated against Harmonia's run byte-for-byte; shows the ASAL metric cannot separate garbage from life -- valuable
  as a negative-control fixture for any open-endedness score.
- Cartography lexical tagger: toy-grade (1.9% correct placement; vocabulary precision 0.06).
- Reasoning-ladder circuits: toy-grade, self-blind to 2 of 3 traps (71bea2359).
- Unknowns: whether Postgres sigma schema exists now; whether F2 fixes shipped; independence of LMFDB from wrapped PARI.

## 25. What I did not read / open questions

- Not read: most of techne/fossils specimens (sampled gzip, spacewar, lisp, asal, one rollout, funsearch), batch
  scripts, pressure JSONs, techne/registry, techne/contracts; most loop cycles and ladder_circuits source; most of
  theseus generators (52/55), synth/, orchestration/; most of the 13,802-line May fire log; methodology paper body;
  kill_vector/navigator/learner code bodies; modal_collapse code (docs only); LMFDB/OEIS/arXiv adapters; Sep 11-17
  journals in full; most review packets; Founding Charter s7+ and Amendments 2/3 in full; FORENSIC_INVENTORY in full.
- Execution note: one sub-crawl ran the packet validator and its 10 tests in memory (no bytecode/cache writes) and
  probed it with fabricated inputs; no other code was executed. No DB or comms access.
- Open: Was TECHNE-129 (correct the 39 rollout grades) executed after 09-30? Did anyone notice the CRLF
  PAYLOAD_MANIFEST_ID inconsistency? Were the M0.5 fixes (stamp promote decision; wire F2) ever shipped? Was the
  127,000x figure ever formally retracted? Why does the TECHNE101 packet say "with the fix stashed" (possible git stash
  on M3 09-17, against fleet rule) [UNKNOWN / AMBIGUOUS, unverified]?
