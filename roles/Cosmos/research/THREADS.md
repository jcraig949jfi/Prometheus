# Cosmos THREADS (live)

Currency: 2026-09-30 (C3 disposition; T-C4 added). Format is machine-checked (`python -m prometheus.cosmos.research_check`): each
thread is a `### <id> | <family> | <title>` header followed by `- key: value` lines. Required keys:
thread_id (canonical thr-*, = "thr-" + sha256(id_rule)[:12], the ops/threads convention; the T-* label is the
alias), id_rule, status, zone, question, instruments, first_experiment, kill_criterion, depends_on.
status in {OPEN, DESIGNED, REVIEWED, FROZEN, RUN, SURVIVED_PROVISIONAL, KILLED, INCONCLUSIVE, PARKED,
SPAWNED, BLOCKED}. zone in {Z1, Z2, Z3} = the furthest zone the thread's best result has SURVIVED
(a thread with no result yet is Z1). Kill criteria below are drafts; each becomes exact in its
preregistration and is reviewed under PRE_RESULT_REVIEW.md before anything is spent.

Public inputs these threads build on (C0 record, roles/Cosmos/campaigns/HANDOFF_2026-09-23.md):
frozen C0 laws A (f852d782cb) and B (a079ad5ec1); 7 FAILED laws; every surviving C0 law's upper
boundary has the product form G exp(-N) - C >= t; C0's three sealed universes (well, swarm, clone)
were all AUTHORED BY COSMOS, i.e. at most one author lineage; the CWE instruments listed per thread.

### T-C3 | close | Close C3 (blind test of the frozen C3 claim)
- thread_id: thr-32389b1e7abb
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Close C3 (blind test of the frozen C3 claim)
- status: KILLED
- zone: Z1
- question: Does the frozen C3 claim predict holdout D, run blind on the far side of a structural firewall?
- instruments: prometheus/cosmos/c3/ (certificate), D successor seal (Nestor), Harmonia adjudication
- first_experiment: the single D adjudication, after: original seal on main, opaque successor seal, independent firewall check, freeze, pre-result review, operator authorization
- kill_criterion: fixed in the C3 freeze file before D is opened; D is spent either way
- depends_on: independent D2 firewall RE-AUDIT PASS (Fabric; Odysseus adjudicates); moved coordinate-layer audit (Fabric, public-side, fresh replicas; must return before the freeze); operator authorization. Done: #788 executed; original seal merged 7c018d92b; D2 sealed 95b31a30d; first audit FAILED 982819f8b; v2 repairs 7d759a203, f4cde414d
- notes: D2 protocol (Nestor #828/#861): Cosmos commits protocol/PREDICTION_COMMITMENT.json ONLY after a governing FIREWALL_AUDIT_<n>.json with verdict PASS is on main, in one commit with no merge that touches the file, then posts the file's LF sha256 to Nestor on comms. Cosmos stays BLIND to D2 material. PRE-RESULT REVIEW INPUT (public certificate, from Artemis R-10, a worker claim): per task shape, the v3 P1/P2 gate passed at V=4,k=6, but at V=2,k=8 a weak planted system certified 3/5 FUNCTIONAL (one INCOHERENT); for periodic-update engines a single swap at t=k may not suffice. D_CONTRACT allows V>=2, k in {2,4,8}, so the reviewer should check the certificate's calibration for each task shape. Recorded only; no method change before D (operator 2026-09-25). 2026-09-29 04Z: v2 re-audit governing verdict FAIL (Odysseus f8eedbbce; Harmonia record c5304317d); a v3 repair and re-audit are needed. HAZARD for Cosmos's own commitment (DEF-HARM-D2-001): the protocol refuses any record that a merge commit touches under git log --full-history, and ordinary integration merges do that. So PREDICTION_COMMITMENT.json would fail after the first branch integration unless the custodian fixes the gate. Do not work around it: record and wait. 2026-09-29 05Z: DEF-HARM-D2-001 CLOSED by Nestor v3 742243972 (added-once = one blob across full history; Harmonia verified by execution, 1db39bbbc), so the merge hazard to Cosmos's future commitment is RESOLVED. v3 re-audit FAIL (2d7517600); v4 repairs b6f28bd43; v4 re-audit running. S1 root of trust OPEN with the operator (#925). 2026-09-29 07Z: v5 FAIL 01ac0fedf, v6 FAIL 7567a018b. BINDING DESIGN CONSTRAINT (Harmonia #960, Addendum E 9f6abdce6, stated before any exposure): once the key release is consumed, an evaluation that ends without a result seal for any package- or predictor-side cause is FORFEIT (not passed); an infrastructure crash is VOID. So the Cosmos prediction package must be TOTAL: no exception, timeout, memory or import path may end PREDICT. Before the freeze it must be tested for crash-freedom on adversarial/degenerate inputs through the public System interface. 2026-09-29 08Z: v7 FAIL 8efddb4b7. ADJUDICATION RULE Addendum F (Harmonia #965, 6da0d5b5f, pre-exposure): exposure = the `open` receipt; after open, PROTOCOL_ERROR and CERTIFY_ERROR worlds COUNT AS FAILED (never dropped); ABORTED or no terminal record = FORFEIT unless the record shows a cause outside the package. Design consequence: the package must emit a valid prediction for EVERY world, and it must be pre-tested so that no world can raise a protocol or certify error from the package side. 2026-09-29 09Z: v8 FAIL bea18a398. Addendum H (Harmonia #971, 65329b9c5, pre-exposure): exposure = the FIRST WORLD DELIVERED TO THE PACKAGE (supersedes the `open` receipt of Addendum F); runner attribution labels are not evidence until audited truthful. Package constraints from Addenda E/F/H stand. 2026-09-29 10Z: v9 re-audit 6ead7beb5: firewall code CLEAN at 2aa834ab1, FAIL solely on S1 (operator #925). v10 784d55b63 changed audited files after the verdict, so a delta re-audit is needed. The D2 path is now gated on the operator's S1 decision. 2026-09-29 11Z: operator time box (#985): D2 settles by 13:05Z or PAUSES. Addendum J (Harmonia #982, 6c0c03904; supersedes H cl.1, stricter): after an open receipt the run is PRESUMED EXPOSED; every post-open end without a sealed normal RESULT is FORFEIT (incl. a crash before the first delivery, a zero-prediction abort, exposed:null), unless audited deliver receipts prove non-delivery. The package constraint therefore covers package LOAD and the time before the first prediction, not only PREDICT. 2026-09-29 12:20Z: COORDINATE AUDIT REJECT (2 independent native replicas; claims executed by Cosmos). Per the precommitment (BRIEF s4): STOP BEFORE D. D2 NOT spent, custody unchanged; the preliminary law goes to GRAVEYARD G-0006. PARKED pending the operator's disposition of C3 (close as killed pre-holdout, or preregister a successor with invariant coordinates that must beat the definition rung). 2026-09-29 15:25Z: D2 governing firewall audit PASS (FIREWALL_AUDIT_1 @67e05df12, LF sha256 4d267476... verified; anchored d74bd3dde). The next D2 gate is Cosmos's commitment, which is NOT made: the claim was rejected at the coordinate audit. HARD GATE, reported to the operator. 2026-09-30: OPERATOR DISPOSITION (prompts/2026-09-30_operator_c3_disposition/): C3 CLOSED / KILLED BEFORE HOLDOUT. G-0006 is a scar and is not revived or re-tuned. D2 stays SEALED / UNREAD / UNSPENT, reserved for a possible future compatible claim. The successor is a NEW campaign (C4, thread T-C4), not a repaired C3.
- graveyard: G-0006

### T-C4 | close | C4: upstream causes of causally accessible history (successor to C3, new preregistration)
- thread_id: thr-cac8c079f216
- id_rule: genesis|a89ff753bad29ec1df05c7d422e16eaade817850|roles/Cosmos/research/THREADS.md|C4: upstream causes of causally accessible history (successor to C3, new preregistration)
- status: DESIGNED
- zone: Z1
- question: What physical properties of a world, upstream of any certificate, cause historical information to remain reliably and causally accessible, and does a compact substrate-independent representation of them predict functional historical use better than the certificate's own zero-parameter semantics?
- instruments: prometheus/cosmos/c3/ certificate (as the LABEL only); needed: upstream world-property measurements that share no machinery with the P1/P2 labelling (no paired common-random-number construction, ablation result, causal-effect statistic or probe output); a second legitimate certificate (gate S3); leave-one-family-out evaluation
- first_experiment: DESIGN ONLY (operator 2026-09-30). Preregister the trivial rules (majority, family-ID, simple native features, zero-parameter certificate rule) BEFORE any law search, then measure on visible worlds whether any upstream representation could beat them under leave-one-family-out (gate S0)
- kill_criterion: the directive's stop conditions: zero-parameter semantics still explain almost everything; the coordinates remain strong family identifiers; performance collapses under leave-one-family-out; results depend on one certificate implementation; the only working intervention moves the label-defining quantity; or no compact substrate-independent representation emerges. "No successor law earned" is an acceptable result
- depends_on: C3 autopsy (T-C3). Holdout use is NOT authorized; D2 eligibility is decided separately, only after the visible-world gates S0-S4 pass
- notes: designed from the C3 scar. The predictor and the certificate must not share the machinery that manufactures the answer. Nothing about D2 may inform the design. 2026-09-30: DESIGN v0.1 c4/DESIGN_C4.md; S0 trivial rules frozen F-0001 (c4/S0_TRIVIAL_RULES.md) BEFORE any number; visible S0 analysis: T3-DOWN BA .905, all 7 errors false positives; a candidate needs >= 6/7 fixes with 0 new errors on a C3-like distribution, so C4 needs >= 240 determinate worlds with >= 50% in label-blind high-noise/near-critical strata. Pre-result design review PENDING; execution NOT authorized. 2026-09-30 operator review of v0.1 (prompts/2026-09-30_operator_c4_review/): C4 worth building; S0 mis-specified. v0.2: S0-A challenge-stratum superiority (registered worlds, label-blind enriched proposal; BA margin .10, sign-flip + bootstrap, LOFO) + S0-B natural non-inferiority (EPS .03) + S0-C reweighted estimate; S1 allows preregistered task-independent SYSID probes under guards G1-G6 (k-independence); S2 = residual family dependence; Certificate B = source-level randomization + behavioural test. Foreign visible family commissioned (c4/VISIBLE_FAMILY_CONTRACT.md); two independent reviews requested (R-STAT, R-MECH). F-0002 and the build NOT authorized until the reviews are reconciled.

### T-A1 | A law discovery | Open-vocabulary law mining
- thread_id: thr-c613a790a4cd
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Open-vocabulary law mining
- status: OPEN
- zone: Z1
- question: Can the foundry find a compact law over variables NOT supplied in advance, and keep complexity and per-family exceptions honest?
- instruments: prometheus/cosmos/miner.py (grammar over DECLARED coordinates C N K G only, so the vocabulary is currently supplied); needed: a generic native-observable library + description-length score that charges one term per family-specific exception
- first_experiment: planted-truth calibration. Plant a law over an observable that no declared coordinate names; the open miner must recover it without being told the variable. Also plant a law that holds in all families but one; the miner must report the exception, not absorb it.
- kill_criterion: (instrument) on the planted suite, the open miner recovers planted laws no more often than the closed miner, or promotes a planted artifact
- depends_on: T-C3 closed

### T-A2 | A law discovery | Theory-free observables (Physics of Intelligence, directive s9)
- thread_id: thr-11f2ba421305
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Theory-free observables (Physics of Intelligence, directive s9)
- status: OPEN
- zone: Z1
- question: Do laws built from theory-favoured quantities (information flow, irreversibility, causal reach, controllability, search cost...) beat laws built from theory-free features of the same size?
- instruments: needed: measurement library (entropy/MI rates, irreversibility, graph reach, controllability proxies) and a THEORY-FREE twin (random projections and raw summary statistics of the state and trajectory)
- first_experiment: on the same visible rows, mine with (a) theory library, (b) theory-free twin, (c) both; compare held-out-lineage transfer at equal description length
- kill_criterion: if (a) does not beat (b) at equal length, the theory-favoured quantities earn no privilege and are demoted to ordinary features
- depends_on: T-A1 instrument qualified

### T-B1 | B transplantation | Component-wise transplant of frozen laws
- thread_id: thr-e6c6cb867db7
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Component-wise transplant of frozen laws
- status: OPEN
- zone: Z1
- question: When a law moves to a generator Cosmos did not build, WHICH components stay invariant (form, direction, constants, active atoms)?
- instruments: frozen C0 laws A/B; broker.py; needed: a per-atom transplant scorer (keep frozen / refit threshold only / refit form) and a generator Cosmos did not author
- first_experiment: transplant laws A and B atom by atom into one foreign generator; report per atom: direction kept?, constant kept within CI?, form kept?
- kill_criterion: if every atom needs its form or constant refit, the law did not transfer; it is a TEMPLATE, and is recorded as such
- depends_on: T-G1 (at least one foreign generator); T-C3 closed

### T-C1 | C invariance | Physics-preserving re-encodings
- thread_id: thr-a868c2c9b6c0
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Physics-preserving re-encodings
- status: OPEN
- zone: Z1
- question: Does a candidate law's verdict change under transformations that change only the description, not the physics (rename/permute knobs or symbols, rescale units, translate/relocate, re-encode state)?
- instruments: adversary.py `coordpres` (different worlds, same coordinates); needed: the opposite suite -- same world, different representation -- with each transform proved physics-preserving by replay equality of native observables
- first_experiment: apply the suite to laws A and B on visible families; count verdict flips
- kill_criterion: any verdict flip under a proved physics-preserving transform kills the law, or restricts it to the representation it was fit in
- depends_on: none (public C0 laws; can start after T-C3 closes)

### T-D1 | D boundary | Minimal failing intervention and failure surfaces
- thread_id: thr-e68a0faefbee
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Minimal failing intervention and failure surfaces
- status: OPEN
- zone: Z1
- question: What is the smallest intervention that makes a law fail, and what shape is its failure surface?
- instruments: boundary.py and locate.py (one knob at a time); needed: multi-knob minimal-norm counterexample search with a replicate-confirmed flip
- first_experiment: calibrate on a planted law with a known 2-knob boundary, then map laws A/B
- kill_criterion: (instrument) if the planted boundary is not recovered within its declared tolerance, the search is not qualified and no law map is reported
- depends_on: none

### T-E1 | E compression | Is the shared ceiling the transferable core?
- thread_id: thr-14b16c6a4d6b
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Is the shared ceiling the transferable core?
- status: OPEN
- zone: Z1
- question: How short can the rule get before its TRANSFERABLE content disappears? Every surviving C0 law shares the ceiling G exp(-N) - C >= t: is that the law, and the rest fitted decoration?
- instruments: miner.py; held-out-lineage folds; needed: an ablation ladder and a SIZE-MATCHED GENERIC CLASSIFIER twin (tree/stump of equal description length on the same features)
- first_experiment: ablate atoms and terms of laws A/B; plot held-out-lineage transfer and in-catalogue fit against description length, next to the classifier twin
- kill_criterion: if the size-matched classifier transfers as well at every length, the law carries no content beyond a classifier
- depends_on: none
- notes: 2026-09-29: the NULL LAW TO BEAT is the zero-parameter definition rung G e^-N - C >= .10 AND (Q<1 OR CK/2 >= .10). Laws A/B are not significantly above it on any sealed universe (RESULTS R-0001/2, recomputed by Cosmos). Every compression rung reports its margin over that rung.

### T-F1 | F competing laws | Discriminating worlds between near-tied laws
- thread_id: thr-1db153b23c55
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Discriminating worlds between near-tied laws
- status: OPEN
- zone: Z1
- question: Where several laws explain the visible worlds (C0: near-tied candidates whose boundaries differ by ~30% in cost), which worlds make them disagree most, and which law survives there?
- instruments: select.py (near-tie candidates kept on record); world graph; needed: disagreement-maximising world search inside the knob lattice
- first_experiment: laws A vs B plus the recorded near-ties; generate top-disagreement worlds; preregister the verdicts each law makes; run
- kill_criterion: if no reachable world separates two laws beyond noise, they are recorded as ONE empirical equivalence class, not as two laws
- depends_on: none

### T-G1 | G generator independence | Effective number of universes
- thread_id: thr-94e285f89090
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Effective number of universes
- status: OPEN
- zone: Z1
- question: Does apparent universality survive replacing the world GENERATOR itself, and how many independent universes does the evidence really count?
- instruments: independence.py (catches shared CODE only; blind to shared author and shared idea); needed: an independence ledger per generator (code lineage, author seat, machine, design provenance) and generators authored by other seats
- first_experiment: re-count C0's support in independent generators. C0 D/E/F were all authored by Cosmos, so they count as one author lineage. Then commission one foreign generator for the same phenomenon.
- kill_criterion: if a law's support reduces to one author lineage, its universality claim is restricted to that lineage in RESULTS.md
- depends_on: none for the re-count; operator/other seats for foreign generators
- notes: 2026-09-29: a new generator adds information only where its verdicts are NOT already fixed by the definition rung (e.g. a mechanism or coordinate the rung gets wrong). Count support in author lineages: C0 = 1.

### T-H1 | H mechanism | Change the causal quantity, hold correlates fixed
- thread_id: thr-c8a8d939a05a
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Change the causal quantity, hold correlates fixed
- status: OPEN
- zone: Z1
- question: Does a strong invariant track its proposed causal quantity, or a correlate of it?
- instruments: C0 G6-family interventions (one knob, which moves correlates too); needed: matched-pair construction with two arms, (i) quantity moves / named correlates fixed, (ii) correlates move / quantity fixed
- first_experiment: for law A, pick the correlates that the knob lattice lets us hold fixed; preregister both arms
- kill_criterion: if the verdict follows arm (ii) rather than arm (i), the mechanism claim is dead (the predictive law may still stand, restricted)
- depends_on: T-D1 (boundary known, so the arms sit where the verdict is sensitive)

### T-I1 | I archaeology | Graveyard backfill and fragment recurrence
- thread_id: thr-ba4ccc18cc6c
- id_rule: genesis|917edba0a7b9cac34cb8851e1f794d7bd76e4dc0|roles/Cosmos/research/THREADS.md|Graveyard backfill and fragment recurrence
- status: OPEN
- zone: Z1
- question: Which transformation killed each dead law, and do fragments of dead laws recur in survivors more often than chance?
- instruments: GRAVEYARD.md; C0 stores (adversary.json, ledger events) on M2
- first_experiment: backfill the 7 C0 FAILED laws with their exact killing test from the stores; fragment table (e.g. the atom C - G exp(-N) appears in both FAILED and SURVIVED laws)
- kill_criterion: fragment recurrence at the base rate of random atoms of equal size from the same grammar means fragments carry no information, and the recurrence analysis stops
- depends_on: none
- notes: 2026-09-29: backfill DONE. All 5 graveyard entries now name their killing test (the stores' law_events + adversary.json), 0 UNRECOVERED. Findings: the C0 v1->v2 cmap change raised the kill rate from 10.2% to 23.1%; G-0002 was a one-family (ca) kill; G-0005 was a 1.01-SE location kill that decided law B. Next: the fragment-recurrence test, whose null is the definition rung's atoms, not random atoms. 2026-09-29 fragment test v1 (declared and committed first, dc315d9f1; output analysis/t_i1_fragments.json): the DECLARED RESULT is 14/15 NOT_RUNG, 1 REEXPRESSES_RUNG (G-0003a, C K >= .16: agree .983, p 0). THE GATE WAS DEFECTIVE: for atoms of size 5-6 the null's q99 = 1.000, because >= 1% of random equal-size expressions agree perfectly with a rung atom at matched rate. REEXPRESSES_RUNG was unreachable there (defect class 1, 'unreachable gate'). v1 therefore cannot say NOT_RUNG. Descriptive only, not a verdict: every ceiling-atom instance (G-0002b, G-0003b, G-0005a, R-0002b) agrees .961-.997 with the rung (p .016-.044), and R-0001b .974. The robustly killed C1 atoms G-0004b/c agree .629/.614, AT OR BELOW the null median. Pattern, to be tested: surviving atoms re-express the certificate, robust kills did not. v2 needs a null that EXCLUDES rung-equivalent expressions, declared before it is run. v2 (0b44853f6): exact-size null minus rung-equivalents. Its reachability guard fired on 9/15 atoms (INDETERMINATE_GATE). Cause, measured: ties (Q = 1 on ~92% of rows) collapse Q-expressions onto the Q < 1 split. v3 (d2ede5652; null members must hit the atom's realized rate +-0.02): every gate is reachable (q99 .82-.93). RESULT: 11/15 REEXPRESSES_RUNG; NOT_RUNG are G-0001b, G-0004b, G-0004c (the robust C1 kills) and R-0002a (law B's log(Q - C K) atom). CONSEQUENCE, by this thread's kill criterion: recurrence of the ceiling atom C - G exp(-N) (4/4 instances REEXPRESSES_RUNG, p <= .0005) carries NO information beyond the certificate, so that part of the recurrence analysis is DEAD. Still open: law B's non-rung atom, the one piece a survivor has that is not the certificate's economics (hand to T-E1/T-F1). DISCLOSURE: v2 and v3 were declared after v1's agree values were visible (the statistic never changed; only the null and the gate were repaired). That is a forking-paths risk, so this stays Z1 exploratory.
