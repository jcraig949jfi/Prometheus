# Cosmos THREADS (live)

Currency: 2026-09-29 (MWO-0001 adoption). Format is machine-checked (`python -m prometheus.cosmos.research_check`): each
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
- status: BLOCKED
- zone: Z1
- question: Does the frozen C3 claim predict holdout D, run blind on the far side of a structural firewall?
- instruments: prometheus/cosmos/c3/ (certificate), D successor seal (Nestor), Harmonia adjudication
- first_experiment: the single D adjudication, after: original seal on main, opaque successor seal, independent firewall check, freeze, pre-result review, operator authorization
- kill_criterion: fixed in the C3 freeze file before D is opened; D is spent either way
- depends_on: independent D2 firewall RE-AUDIT PASS (Fabric; Odysseus adjudicates); moved coordinate-layer audit (Fabric, public-side, fresh replicas; must return before the freeze); operator authorization. Done: #788 executed; original seal merged 7c018d92b; D2 sealed 95b31a30d; first audit FAILED 982819f8b; v2 repairs 7d759a203, f4cde414d
- notes: D2 protocol (Nestor #828/#861): Cosmos commits protocol/PREDICTION_COMMITMENT.json ONLY after a governing FIREWALL_AUDIT_<n>.json with verdict PASS is on main, in one commit with no merge that touches the file, then posts the file's LF sha256 to Nestor on comms. Cosmos stays BLIND to D2 material. PRE-RESULT REVIEW INPUT (public certificate, from Artemis R-10, a worker claim): per task shape, the v3 P1/P2 gate passed at V=4,k=6, but at V=2,k=8 a weak planted system certified 3/5 FUNCTIONAL (one INCOHERENT); for periodic-update engines a single swap at t=k may not suffice. D_CONTRACT allows V>=2, k in {2,4,8}, so the reviewer should check the certificate's calibration for each task shape. Recorded only; no method change before D (operator 2026-09-25). 2026-09-29 04Z: v2 re-audit governing verdict FAIL (Odysseus f8eedbbce; Harmonia record c5304317d); a v3 repair and re-audit are needed. HAZARD for Cosmos's own commitment (DEF-HARM-D2-001): the protocol refuses any record that a merge commit touches under git log --full-history, and ordinary integration merges do that. So PREDICTION_COMMITMENT.json would fail after the first branch integration unless the custodian fixes the gate. Do not work around it: record and wait. 2026-09-29 05Z: DEF-HARM-D2-001 CLOSED by Nestor v3 742243972 (added-once = one blob across full history; Harmonia verified by execution, 1db39bbbc), so the merge hazard to Cosmos's future commitment is RESOLVED. v3 re-audit FAIL (2d7517600); v4 repairs b6f28bd43; v4 re-audit running. S1 root of trust OPEN with the operator (#925).

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
