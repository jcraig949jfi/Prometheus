# Cosmos THREADS (live)

Currency: 2026-09-28. Format is machine-checked (`python -m prometheus.cosmos.research_check`): each
thread is a `### <id> | <family> | <title>` header followed by `- key: value` lines. Required keys:
status, zone, question, instruments, first_experiment, kill_criterion, depends_on.
status in {OPEN, DESIGNED, REVIEWED, FROZEN, RUN, SURVIVED_PROVISIONAL, KILLED, INCONCLUSIVE, PARKED,
SPAWNED, BLOCKED}. zone in {Z1, Z2, Z3} = the furthest zone the thread's best result has SURVIVED
(a thread with no result yet is Z1). Kill criteria below are drafts; each becomes exact in its
preregistration and is reviewed under PRE_RESULT_REVIEW.md before anything is spent.

Public inputs these threads build on (C0 record, roles/Cosmos/campaigns/HANDOFF_2026-09-23.md):
frozen C0 laws A (f852d782cb) and B (a079ad5ec1); 7 FAILED laws; every surviving C0 law's upper
boundary has the product form G exp(-N) - C >= t; C0's three sealed universes (well, swarm, clone)
were all AUTHORED BY COSMOS, i.e. at most one author lineage; the CWE instruments listed per thread.

### T-C3 | close | Close C3 (blind test of the frozen C3 claim)
- status: BLOCKED
- zone: Z1
- question: Does the frozen C3 claim predict holdout D, run blind on the far side of a structural firewall?
- instruments: prometheus/cosmos/c3/ (certificate), D successor seal (Nestor), Harmonia adjudication
- first_experiment: the single D adjudication, after: original seal on main, opaque successor seal, independent firewall check, freeze, pre-result review, operator authorization
- kill_criterion: fixed in the C3 freeze file before D is opened; D is spent either way
- depends_on: Nestor comms #788 (seal merge + opaque successor); operator authorization
- notes: all other threads wait for T-C3 to close, except design work that uses only public material

### T-A1 | A law discovery | Open-vocabulary law mining
- status: OPEN
- zone: Z1
- question: Can the foundry find a compact law over variables NOT supplied in advance, and keep complexity and per-family exceptions honest?
- instruments: prometheus/cosmos/miner.py (grammar over DECLARED coordinates C N K G only, so the vocabulary is currently supplied); needed: a generic native-observable library + description-length score that charges one term per family-specific exception
- first_experiment: planted-truth calibration. Plant a law over an observable that no declared coordinate names; the open miner must recover it without being told the variable. Also plant a law that holds in all families but one; the miner must report the exception, not absorb it.
- kill_criterion: (instrument) on the planted suite, the open miner recovers planted laws no more often than the closed miner, or promotes a planted artifact
- depends_on: T-C3 closed

### T-A2 | A law discovery | Theory-free observables (Physics of Intelligence, directive s9)
- status: OPEN
- zone: Z1
- question: Do laws built from theory-favoured quantities (information flow, irreversibility, causal reach, controllability, search cost...) beat laws built from theory-free features of the same size?
- instruments: needed: measurement library (entropy/MI rates, irreversibility, graph reach, controllability proxies) and a THEORY-FREE twin (random projections and raw summary statistics of the state and trajectory)
- first_experiment: on the same visible rows, mine with (a) theory library, (b) theory-free twin, (c) both; compare held-out-lineage transfer at equal description length
- kill_criterion: if (a) does not beat (b) at equal length, the theory-favoured quantities earn no privilege and are demoted to ordinary features
- depends_on: T-A1 instrument qualified

### T-B1 | B transplantation | Component-wise transplant of frozen laws
- status: OPEN
- zone: Z1
- question: When a law moves to a generator Cosmos did not build, WHICH components stay invariant (form, direction, constants, active atoms)?
- instruments: frozen C0 laws A/B; broker.py; needed: a per-atom transplant scorer (keep frozen / refit threshold only / refit form) and a generator Cosmos did not author
- first_experiment: transplant laws A and B atom by atom into one foreign generator; report per atom: direction kept?, constant kept within CI?, form kept?
- kill_criterion: if every atom needs its form or constant refit, the law did not transfer; it is a TEMPLATE, and is recorded as such
- depends_on: T-G1 (at least one foreign generator); T-C3 closed

### T-C1 | C invariance | Physics-preserving re-encodings
- status: OPEN
- zone: Z1
- question: Does a candidate law's verdict change under transformations that change only the description, not the physics (rename/permute knobs or symbols, rescale units, translate/relocate, re-encode state)?
- instruments: adversary.py `coordpres` (different worlds, same coordinates); needed: the opposite suite -- same world, different representation -- with each transform proved physics-preserving by replay equality of native observables
- first_experiment: apply the suite to laws A and B on visible families; count verdict flips
- kill_criterion: any verdict flip under a proved physics-preserving transform kills the law, or restricts it to the representation it was fit in
- depends_on: none (public C0 laws; can start after T-C3 closes)

### T-D1 | D boundary | Minimal failing intervention and failure surfaces
- status: OPEN
- zone: Z1
- question: What is the smallest intervention that makes a law fail, and what shape is its failure surface?
- instruments: boundary.py and locate.py (one knob at a time); needed: multi-knob minimal-norm counterexample search with a replicate-confirmed flip
- first_experiment: calibrate on a planted law with a known 2-knob boundary, then map laws A/B
- kill_criterion: (instrument) if the planted boundary is not recovered within its declared tolerance, the search is not qualified and no law map is reported
- depends_on: none

### T-E1 | E compression | Is the shared ceiling the transferable core?
- status: OPEN
- zone: Z1
- question: How short can the rule get before its TRANSFERABLE content disappears? Every surviving C0 law shares the ceiling G exp(-N) - C >= t: is that the law, and the rest fitted decoration?
- instruments: miner.py; held-out-lineage folds; needed: an ablation ladder and a SIZE-MATCHED GENERIC CLASSIFIER twin (tree/stump of equal description length on the same features)
- first_experiment: ablate atoms and terms of laws A/B; plot held-out-lineage transfer and in-catalogue fit against description length, next to the classifier twin
- kill_criterion: if the size-matched classifier transfers as well at every length, the law carries no content beyond a classifier
- depends_on: none

### T-F1 | F competing laws | Discriminating worlds between near-tied laws
- status: OPEN
- zone: Z1
- question: Where several laws explain the visible worlds (C0: near-tied candidates whose boundaries differ by ~30% in cost), which worlds make them disagree most, and which law survives there?
- instruments: select.py (near-tie candidates kept on record); world graph; needed: disagreement-maximising world search inside the knob lattice
- first_experiment: laws A vs B plus the recorded near-ties; generate top-disagreement worlds; preregister the verdicts each law makes; run
- kill_criterion: if no reachable world separates two laws beyond noise, they are recorded as ONE empirical equivalence class, not as two laws
- depends_on: none

### T-G1 | G generator independence | Effective number of universes
- status: OPEN
- zone: Z1
- question: Does apparent universality survive replacing the world GENERATOR itself, and how many independent universes does the evidence really count?
- instruments: independence.py (catches shared CODE only; blind to shared author and shared idea); needed: an independence ledger per generator (code lineage, author seat, machine, design provenance) and generators authored by other seats
- first_experiment: re-count C0's support in independent generators. C0 D/E/F were all authored by Cosmos, so they count as one author lineage. Then commission one foreign generator for the same phenomenon.
- kill_criterion: if a law's support reduces to one author lineage, its universality claim is restricted to that lineage in RESULTS.md
- depends_on: none for the re-count; operator/other seats for foreign generators

### T-H1 | H mechanism | Change the causal quantity, hold correlates fixed
- status: OPEN
- zone: Z1
- question: Does a strong invariant track its proposed causal quantity, or a correlate of it?
- instruments: C0 G6-family interventions (one knob, which moves correlates too); needed: matched-pair construction with two arms, (i) quantity moves / named correlates fixed, (ii) correlates move / quantity fixed
- first_experiment: for law A, pick the correlates that the knob lattice lets us hold fixed; preregister both arms
- kill_criterion: if the verdict follows arm (ii) rather than arm (i), the mechanism claim is dead (the predictive law may still stand, restricted)
- depends_on: T-D1 (boundary known, so the arms sit where the verdict is sensitive)

### T-I1 | I archaeology | Graveyard backfill and fragment recurrence
- status: OPEN
- zone: Z1
- question: Which transformation killed each dead law, and do fragments of dead laws recur in survivors more often than chance?
- instruments: GRAVEYARD.md; C0 stores (adversary.json, ledger events) on M2
- first_experiment: backfill the 7 C0 FAILED laws with their exact killing test from the stores; fragment table (e.g. the atom C - G exp(-N) appears in both FAILED and SURVIVED laws)
- kill_criterion: fragment recurrence at the base rate of random atoms of equal size from the same grammar means fragments carry no information, and the recurrence analysis stops
- depends_on: none
