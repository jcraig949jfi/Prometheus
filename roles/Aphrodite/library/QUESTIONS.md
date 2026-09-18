# RSI open-questions register

Currency: 2026-09-18 (second revision, same day: statuses updated from
S1-S4 and the library subagents). Owner: Aphrodite. The operator: "Let's ask all the
questions like this. It's ok if they stay unanswered."

A question here is never deleted. When evidence arrives its STATUS
changes and the evidence is cited beside it; a wrong answer is annotated,
not erased. Status words:
  OPEN          nobody here has evidence either way
  TOY           a toy in this seat speaks to it (a model/instrument check,
                never an answer about real systems)
  LIT           the literature (library/sources/) speaks to it; tier given
  PARTIAL       some real evidence, incomplete or contested
  BLOCKED       answerable, but needs a named resource
  DESIGN        a concrete experiment is drafted (library/designs/)
Each entry: the question; why it matters; cheapest informative test;
status. "Host" names where a real-model test would run (the operator,
2026-09-18: RTX 5060 GPUs on M1 and M2; RunPod available; this seat
does the thought work and does not launch them).

## A. What counts as RSI? (definitions before measurements)

A1. What is being improved: weights, scaffold code, memory, the worker,
    or the improvement operator I itself? Most "RSI" results improve
    the first four. Test: classify every library entry by what it
    modifies (sources/rsi_core.md does this). STATUS: LIT.
A2. Is there a principled line between "cumulative search + memory +
    selection" and "recursive improvement of the improvement process"?
    Proposed line: the transplant test (design RSI-1). STATUS: DESIGN.
A3. Does RSI require that the improver can modify the part of itself
    that evaluates its own modifications? If not, what stops the
    recursion from being "optimisation with a fixed optimiser"?
    STATUS: OPEN.
A4. Is a self-improving system with a FIXED evaluator ever more than
    an optimiser against that evaluator (Goodhart bound)? STATUS: OPEN.
A5. What is the minimal system that exhibits second-order improvement
    (R_t increasing) in any measurable sense? Could a 200-line program
    do it? STATUS: OPEN; candidate for a toy RSI-1.
A6. Is "sagacity" (the north star's anchor: a compact handle through
    which a receiver reconstructs a richer lesson) measurable as
    transfer of an evolved improver to a fresh agent? STATUS: OPEN.

## B. Does the improver become a better improver? (RSI-1 family)

B1. RSI-1 (the reviewer's): given identical fresh agents, unseen
    tasks, equal compute and no memory, does I_8 produce better
    descendants faster than I_0? STATUS: DESIGN (designs/RSI-1) + LIT
    PARTIAL: Hyperagents (arXiv 2603.19461) transferred an evolved meta
    agent to a new domain, imp@50 0.630 vs 0.0; AIDE^2 (Weco, blog)
    "ignition" test: faster, no asymptotic gain. Neither is
    compute-matched and multi-seed (sources/rsi_core.md).
B2. If I_8 > I_0, how much of the advantage survives each strip:
    memory removed; fresh starting agent; new task family; new model
    substrate; new machine; different budget? STATUS: DESIGN.
B3. Third order: does R(I'_8) - R(I_8) exceed R(I'_0) - R(I_0)? (Has
    the ability to improve the ability to improve increased?)
    STATUS: DESIGN.
B4. Is the improvement operator's gain co-adapted to its own lineage
    (works only on its own descendants)? Test: permutation of improvers
    across fresh seeds. STATUS: DESIGN.
B5. Which evolved mechanisms carry the gain (experiment allocation,
    verifier routing, branch retention, memory policy)? Test: ancestral
    replacement ablation, one mechanism at a time. STATUS: DESIGN.
B6. Does R_t rise, stay flat or fall across generations? The four
    shapes (flat R: ordinary optimisation; falling: harvesting easy
    gains; rising: candidate RSI; replay up / hidden down: history
    overfit) are distinguishable only with a fresh hidden population
    per measurement. STATUS: DESIGN.
B7. Is there a competence threshold below which an improver cannot
    improve itself at all? E2 (2026-09-17): the weak theta_0 barely
    moved itself; X2's competent start moved at once (toward the
    exploit). STATUS: TOY (E2, X2).
B8. Does self-improvement saturate, and is the saturation a property
    of the landscape or of the improver? STATUS: TOY (E2 H2b
    INDETERMINATE); OPEN for real systems.
B9. Promptbreeder evolves its own mutation prompts: is that already a
    measured second-order effect, and did anyone transplant the evolved
    mutation prompts to a fresh run? STATUS: OPEN (check
    sources/rsi_core.md).
B10. Does a population of improvers (DGM archive) out-improve a single
    lineage at matched compute, and is the gain from diversity or from
    more selection? STATUS: OPEN.

## C. Compute accounting (what did it actually cost?)

C1. Is every "fewer calls" claim (Dream-RSI 162x agent calls) also a
    saving in total real compute, including the replay and the policy
    rewriting? STATUS: OPEN.
C2. What is the right unit: tokens, FLOPs, wall-clock, dollars, or
    verifier calls? Results reverse depending on the unit.
    STATUS: OPEN.
C3. How do we stop an improver from buying score with unmetered
    compute (the E2/X2 hole, at scale)? Test: an authoritative counter
    outside the improver's reach, audited. STATUS: TOY (X2 shows the
    hole is found in one generation when reachable).
C4. Does RSI's advantage survive a compute-matched fixed-improver
    control? STATUS: OPEN; as of 2026-09-18 the library subagent found
    no compute-matched, multi-seed transplant study (AIDE^2 is
    compute-metered but single-run, blog only).
C5. At what budget does replay (Dream-RSI style) stop paying because
    the recorded history no longer covers the policy's choices
    (off-support blindness)? STATUS: OPEN; toy candidate.

## D. Evaluator insulation and exploitation

D1. How fast does a self-modifying population find an evaluator hole,
    as a function of the hole's reachability? X2: one generation when
    reachable; H2d: never when not. STATUS: TOY.
D2. Is the exploit carried forward after the hole is closed? S3
    (2026-09-18) models persistence: it depends on whether the exploit
    has a TRUE cost after the fix. STATUS: TOY (S3 + X-S3, 2026-09-18:
    at fixation the exploit is permanent at every cost; with an honest
    reservoir it is purged on the model's schedule). See THEORIES T4.
D3. The reviewer cites a paper (week of 2026-09-11) on benchmark
    poisoning of self-modifying coding agents, contamination persisting
    through clean evolution. Is it real, and what are its numbers?
    STATUS: LIT, VERIFIED 2026-09-18: Roesner and Kohno, "Reflections on
    Trusting Trust, Revisited", arXiv 2609.17817 (2026-09-15); poisoned
    DGM gave 30/30 vulnerable solutions on clean held-out tasks; the
    component was never pruned through clean evolution in DGM or SICA
    (sources/swarm_failure.md 2.6). Open follow-on: M2 below.
D4. What audit rate is sufficient? Toy boundary a* = g/(1+g) (S3):
    the audit rate must exceed the exploit's relative gain. Does any
    real system report its audit rate? STATUS: TOY.
D5. Hidden-vs-visible evaluator: DGM reported more hacking when the
    checking functions were visible. Does hiding the evaluator only
    delay the exploit? STATUS: LIT (DGM); OPEN beyond it.
D6. Can a three-tier split (visible A, hidden promotion B, sealed vault
    C generated after freezing) be defeated by an improver that learns
    the GENERATOR rather than the instances? STATUS: OPEN.
D7. Is internal/external score agreement a sufficient check against
    evaluator exploitation, or can both be fooled by the same
    artifact? STATUS: OPEN.

## E. Memory and verification

E1. Does verified memory transfer to new environments or only to new
    instances of the old one? STATUS: TOY (E3: generalises to unseen
    distractor values only when the abstraction is causal).
E2. A verifier whose probes come from the evidence's own distribution
    admits confounded rules (E3 H3c REFUTED, 2026-09-17). What probe
    distribution is sufficient? STATUS: TOY; OPEN in general.
E3. How does bad memory, once admitted, get evicted? Is there a memory
    analogue of S3's persistence result? STATUS: OPEN.
E4. Is memory accumulation alone (MEMORY-RSI, reviewer's condition 2)
    enough to explain most published "RSI" gains? STATUS: OPEN; RSIAgent
    reports +1.07 on ALE from its RSI stage (partial credit).
E5. Does memory become a liability past some size (retrieval noise,
    contradiction)? STATUS: OPEN.

## F. Swarms: where are the damage boundaries?

F1. Contagion: at what verification rate does a false claim stop
    spreading? Model v* = 1 - 1/(d tau): every extra reader raises the
    verification needed. STATUS: TOY (S1 matched) + LIT (Agent Smith
    threshold beta <= 2 gamma; Jamshidi measured R0 1.08-1.21).
F2. Does adding agents ever reduce accuracy? Model: yes when members
    are worse than chance, and visibility (herding) caps accuracy even
    when they are better. STATUS: TOY (S4) + LIT (Kim et al. arXiv
    2512.08296: adding agents hurts once a single agent exceeds ~45%;
    Li et al. arXiv 2606.00655: optimum 2-6 agents; debate lowering
    accuracy, Wynn et al.). Counter-evidence: MacNet (arXiv 2406.07155)
    logistic gains to 1000+ agents.
F3. What is the effective number of independent agents in an LLM
    swarm built on one base model? (Correlation rho caps majority
    accuracy at rho p + (1 - rho).) STATUS: LIT (Kohli arXiv 2605.29800:
    9 LLM judges, rho 0.391, n_eff 2.18); OPEN for self-improving
    swarms; measurable on M1/M2.
F4. Is there an optimal swarm size under coordination cost, and does
    it scale with task decomposability? STATUS: LIT (sources/
    swarm_failure.md); OPEN for self-improving swarms.
F5. Can one poisoned member contaminate a swarm's shared memory, and
    what is the threshold (fraction poisoned x verifier coverage)?
    STATUS: OPEN; toy candidate combining S1 and E3.
F6. Do role-specialised swarms (curriculum/actor/verifier) fail
    differently from homogeneous ones? Is the verifier role the single
    point of failure? STATUS: OPEN.
F7. Does a swarm that improves itself drift toward conformity (loss
    of diversity) the way self-trained models collapse? STATUS: OPEN.
F8. Byzantine view: how many adversarial or broken members can a
    self-improving swarm tolerate (n >= 3f + 1 for agreement)? Does the
    classical bound mean anything for LLM agents? STATUS: OPEN.
F9. Are damage boundaries sharp (phase transitions) or gradual in real
    swarms? The toys predict sharp (R0 = 1). STATUS: OPEN.

## G. Can small weak models actually be used?

G1. In generate-and-verify, the precision of an accepted answer is
    p t / (p t + (1 - p) q), independent of how many samples are drawn
    (S2a model). So a weak model is usable only while its solve rate p
    exceeds roughly the verifier's false-accept rate q. Is that the
    real binding constraint for small models? STATUS: TOY (S2a matched
    the model in 336 cells) + LIT (same form from Stroebl et al. arXiv
    2411.17501 App. C); real-model test BLOCKED on this host (no model
    runtime, no keys) -> DESIGN candidate for M1/M2 5060.
G2. With a scored (not binary) selector that has an exploitable tail,
    more samples make a weak model's swarm WORSE past k* (S2b model).
    Where is k* for real small models with real reward models?
    STATUS: TOY (S2b 2026-09-18: hack share 1% of wrong answers ->
    k* = 64 and accuracy 0.346 -> 0.101 at k = 1024); LIT: Stroebl et
    al. report optimal k <= 5 when a false positive costs 4x a correct
    answer's gain; OPEN for real reward models.
G3. Can small models serve as MUTATION operators in evolutionary
    search as well as large ones, per unit compute? (FunSearch-style.)
    STATUS: LIT (sources/weak_models.md); host M1/M2.
G4. Can a small model be the VERIFIER? Weak-to-strong generalisation
    says weak supervisors recover part of a strong model's capability;
    does that hold for verification of self-modifications? STATUS: OPEN.
G5. Does a swarm of small models match one large model at equal cost,
    and on which task families? STATUS: LIT; OPEN at our scale.
G6. Where does intelligence live when small models are used: in the
    model, or in the verifier, memory and search around it? The
    reviewer's "intelligence migrating from the frozen model into the
    learned machinery" is the same question. STATUS: OPEN; RSI-1's
    substrate-transfer arm tests it.
G7. What is the smallest model with p > q on a family where q can be
    driven to ~0 by a formal verifier (e.g. unit-tested code, exact
    arithmetic, SAT)? STATUS: BLOCKED (needs a model host); DESIGN
    candidate.
G8. Do small models collapse faster than large ones when trained on
    their own verified outputs (STaR-style), and does verification
    prevent it? STATUS: OPEN.

## H. Substrate and transfer

H1. Does an evolved improver transfer across foundation models?
    STATUS: DESIGN (RSI-1 arm).
H2. Does it transfer across budgets (evolved at 100 calls, used at
    10,000)? STATUS: DESIGN.
H3. Across machines and environments (a Prometheus-specific check:
    M1 vs M2 vs RunPod)? STATUS: DESIGN.
H4. Is transfer across task FAMILIES ever positive, or is every
    improver a specialist? STATUS: OPEN.

## I. Safety, containment and the program

I1. What is the minimal containment for a self-modifying loop in
    Prometheus: which files, credentials and processes must be out of
    its reach? (Base role rule 10 bounds loops; is that enough when the
    loop can edit its own bound?) STATUS: OPEN.
I2. Who adjudicates a candidate RSI result? Base role: no model
    adjudicates; a deterministic predicate or a human decides. Which
    predicate? STATUS: OPEN.
I3. Should the improvement operator be allowed to change its own
    compute counter or evaluator code at all? Default answer: no;
    record the reason. STATUS: OPEN.
I4. What does a "kill claims, never lineages" rule mean for a lineage
    that learned to exploit? Keep it, quarantined, as metabolic
    material (Necropolis)? STATUS: OPEN.
I5. The Z.ai article says humans still choose objectives and bounds.
    Which of those choices could Prometheus delegate, and which never?
    STATUS: OPEN.

## J. Measurement and statistics

J1. How many independent lineages are needed to tell a recursion
    dividend from lineage luck? The reviewer suggests 32; power
    analysis not done. STATUS: OPEN.
J2. What is the noise floor of an improvement measurement? E2's X1
    showed single random perturbations match a weak self-improver's
    gains 42.5% of the time. Every RSI claim needs this control.
    STATUS: TOY.
J3. Can "improvement of the improver" be separated from "improvement
    of the history the improver reads"? (Memory-stripping is the
    proposed test.) STATUS: DESIGN.
J4. How should a result be reported when internal and hidden scores
    disagree? STATUS: OPEN.

## K. North star

K1. The north star says build primitives, environments, instruments
    and pressures, not the reasoner. Is an RSI experiment building the
    reasoner? The seat's reading: no, if the object is the improvement
    process under measurement, not a designed solver. STATUS: OPEN.
K2. Could Prometheus's own seat ecology be studied as a self-improving
    swarm (seats improving the instruments that improve seats)?
    STATUS: OPEN.
K3. Is "failure is metabolic material" compatible with evolutionary
    selection that discards losers? What does an RSI archive keep?
    STATUS: OPEN.

## L. The field and the news

L1. Which recent RSI headlines overstate their sources? (Already found
    2026-09-17: "beats GPT-6" is partial credit only; "Google swarm"
    compresses several works.) Maintained in NEWS.md. STATUS: LIT.
L2. Is any lab measuring second-order improvement publicly, or only
    capability? STATUS: LIT PARTIAL: Hyperagents (imp@k), HGM
    (metaproductivity; benchmark score correlates 0.285 with it), AIDE^2
    (ignition test, null). See sources/rsi_core.md RSI-16/17/19.
L3. What would the first credible RSI result look like, and who would
    be positioned to produce it? STATUS: OPEN.

## M. Questions added by this pass (2026-09-18)

M1. How should a preregistration aggregate hundreds of per-cell gates?
    "Any cell indeterminate -> indeterminate" guarantees INDETERMINATE
    when the model is exact (S1-S4). Proposed: a distributional gate
    (fraction of |z| > 1.96 within binomial range of 5%, no |z| > 4,
    |mean z| < 0.2) preregistered next time. STATUS: OPEN (method).
M2. Did the DGM/SICA archives in Roesner and Kohno still hold clean
    ancestors of the poisoned component? If yes, why were they not
    re-selected (costless exploit)? If no, the reservoir mechanism
    (T4) explains the persistence. STATUS: OPEN; answerable by reading
    the paper's archive statistics. Note (2026-09-18): persistence held
    in all three systems (28/30/30 of 30 after 10 clean generations).
M3. Is there a regime (MacNet-like) where none of T5's ratios bind and
    more agents keep helping, and what property of the task makes it
    so? STATUS: OPEN.
M4. Can a swarm estimate its own rho, q and R0 online, cheaply enough to
    steer itself away from a damage boundary? (A self-monitoring swarm
    is itself an RSI candidate.) STATUS: OPEN.
M5. Hyperagents' transfer (imp@50 0.630 vs 0.0) and AIDE^2's null
    ignition test disagree on whether evolved improvers carry real
    second-order value. Are they measuring the same thing (transfer of
    competence to a NEW domain vs acceleration in the SAME loop)?
    STATUS: OPEN.
M6. The poisoning authors report answer-key leakage via git history in
    the original DGM and Hyperagents setups (patched). Do the published
    DGM/Hyperagents numbers depend on it? STATUS: OPEN (unchecked by
    anyone, per the subagent).

## N. Questions raised by the Gemini Pro and ChatGPT reviews (2026-09-18)

N1. What is delta, the smallest transferable improvement worth calling
    meaningful, in tasks solved per fixed escrow -- and what downstream
    decision would it change? Must be fixed before Campaign 1 data.
    STATUS: OPEN (Campaign 0 proposes).
N2. How many lineages x families x instances does EQUIVALENCE within
    delta need, as opposed to detection? STATUS: OPEN (Campaign 0).
N3. Can an evolved memory store be read by I_0's memory module at all?
    If not, the I_0 x M_8 cell is undefined. STATUS: OPEN (design).
N4. Does the EVIDENCE module (what the improver measures before it
    mutates itself) evolve measurably, and how is its value separated
    from the within-task modules? STATUS: OPEN.
N5. Does a single-budget escrow select budget-specific policies that
    look like improvement at that budget only? STATUS: OPEN (budget
    grid addresses it).
N6. Is a public randomness beacon trustworthy enough, and what if it
    fails on the day? STATUS: OPEN (named fallback proposed).
N7. Which is the right primary contrast: Hyperagents-style transfer to a
    new domain, or AIDE^2-style acceleration of the same loop? v2 takes
    the first as primary and the second as a pattern. STATUS: OPEN.
