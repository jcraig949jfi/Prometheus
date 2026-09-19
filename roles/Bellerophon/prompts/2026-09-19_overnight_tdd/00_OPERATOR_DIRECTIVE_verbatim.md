BELLEROPHON -- WORLDS KERNEL OVERNIGHT TDD / PLAYTEST LOOP
DURATION: 8 wall-clock hours from receipt of this directive
MODE: AUTONOMOUS ITERATION
OPERATOR: OFFLINE -- DO NOT WAIT FOR HUMAN INPUT

The Phase 1/Phase 2 foundation is accepted as the starting point.

From this point forward, treat the Prometheus Worlds Kernel as something we develop primarily through TDD plus repeated playtesting.

The objective tonight is NOT to race through the roadmap.

The objective is to repeatedly try to use the kernel, discover where the abstraction fails, encode those discoveries as tests, improve the kernel, and try again.

You have broad authority to iterate test -> implement -> playtest -> diagnose -> test again for the full 8-hour window.

1. OPERATING LOOP

Repeat until the 8-hour wall-clock window expires:

1. Choose the smallest consequential capability, defect, ambiguity, or usability problem currently blocking richer worlds or experiments.
2. Before changing production code, create a failing executable test, invariant, conformance fixture, property test, or playtest that demonstrates the desired behavior or exposes the defect.
3. Confirm RED for the intended reason.
    A test that fails accidentally does not count.
4. Implement the smallest coherent change that makes it pass.
5. Confirm GREEN:
    * targeted tests
    * toolbox test suite
    * base-role self-tests
    * replay/integrity checks affected by the change
6. REFACTOR if the evidence says the design is becoming awkward.
    Do not preserve an abstraction merely because we wrote it yesterday.
7. PLAYTEST the resulting kernel by expressing and actually executing experiments through its public contracts.
8. Inspect the detailed rows, receipts, traces, series and failures -- not merely the summary.
9. Record every discovered defect, awkwardness, missing degree of freedom, semantic leak, false-green test, or surprising behavior.
10. Turn the important discovery into the next failing test.

Then repeat.

TDD is the ratchet.
Playtesting is the steering mechanism.

2. PLAYTEST BEFORE ROADMAP ADVANCEMENT

Do not automatically begin the next architectural slice simply because it appears in the design document.

First try to break and inconvenience the kernel we already have.

Use it as an experiment designer would.

Construct multiple small but genuinely different experiments and ask:

* Can the experiment be described without smuggling implementation details into the Experiment?
* Can worlds vary independently from players?
* Can substrates vary independently from worlds?
* Can interventions alter conditions without rewriting the world?
* Can controls be mechanically generated and adjudicated?
* Can observations be added without contaminating execution semantics?
* Can state persist at different scopes?
* Can replay reproduce the scientifically relevant record?
* Can unexpected events be retained rather than normalized away?
* Can receipts survive destruction of Redis/process-local state?
* Can one failed capability or unsupported target remain local rather than poisoning unrelated experiments?
* Can the same experiment meaningfully branch across parameter combinations and seeds?
* Does anything in the kernel force experiments back into one familiar evolutionary/search shape?

Prefer playtests that are awkward, adversarial, composition-heavy, or alien to the original reference experiment.

EXP-001 should become a regression fixture, not the mold from which all later experiments are cast.

3. U3 RULING -- SERIES ARE DURABLE SCIENTIFIC DATA

Resolve U3 as follows:

Per-episode observation series are FIRST-CLASS RECEIPT DATA.

The StateDevice may carry, index, cache, stream, rank, expire, or accelerate series during execution, but it must never be the sole authoritative copy of scientifically relevant observations.

Rule:

Redis is never the sole copy.

A completed receipt must contain, directly or by immutable content-addressed artifact reference whose integrity is covered by the receipt, enough information to recover the declared observation series after the execution environment and StateDevice are gone.

Design this under test.

Test at least:

* series survives StateDevice destruction;
* series participates in receipt integrity;
* series identity/replay semantics are explicit;
* empty/disabled series are distinguishable from missing/corrupt series;
* bounded-size behavior is deterministic and reported;
* large-series handling does not silently truncate scientific evidence.

Do not allow receipt size convenience to weaken forensic recoverability.

4. NEXT CAPABILITIES ARE CANDIDATES, NOT MANDATORY ORDER

The currently proposed slice remains useful:

* substrate.kv.v1
* statemachine.v2
* workspace operations
* EXP-002 comparing flat / kv / stream
* per-episode series
* Transform slot
* admission for substrate / observer / control
* Redis acceptance
* Daedalus/Nestor bridge packets

But this is now a hypothesis about what the kernel needs.

Playtesting may reorder it.

If a more fundamental defect appears, fix that first.

If substrate.kv.v1 reveals the StateDevice contract is wrong, change the contract.

If statemachine.v2 requires ugly world knowledge, stop and repair the separation.

If EXP-002 can be expressed without adding a proposed abstraction, do not add the abstraction merely because it was planned.

Architecture follows demonstrated pressure.

5. EXP-002 SHOULD BE A REAL PLAYTEST

When sufficiently supported by tests, build EXP-002.

Its purpose is not merely to demonstrate that three substrate names compile.

It should create a pressure where workspace capability can matter.

Use comparable players/populations across:

* flat
* kv
* stream

and vary enough starting conditions, budgets, delays, capacities or environmental parameters that the result is not a single-point demo.

Exercise:

* lifetime state
* addressable unfinished state
* reuse
* mutation/variation where appropriate
* bounded resource behavior
* state survival and expiry
* observation series
* controls
* replay

EXP-002 is a kernel playtest first and a scientific experiment second.

Failures of ergonomics or expressivity are valuable results.

6. TEST VARIETY

Do not rely only on example-based unit tests.

Where appropriate, add:

* property tests
* randomized/fuzzed compositions
* serialization round trips
* snapshot/restore tests
* corrupted receipt tests
* replay divergence tests
* capability-negotiation tests
* TTL boundary tests
* scope-transition tests
* resource-bound tests
* permutation/metamorphic tests
* control-arm invariants
* multiple-seed playtests

When a bug is found, preserve the smallest reproducer permanently.

Every repaired defect should become difficult to resurrect.

7. FALSE GREENS ARE FIRST-CLASS DEFECTS

You already caught three cases where rows exposed mistakes that summary-level success concealed.

Continue aggressively looking for this class.

For every important test ask:

What incorrect implementation would still make this test green?

Strengthen tests until plausible wrong implementations fail.

Where useful, deliberately perturb the implementation or fixture to demonstrate that the test can actually detect the targeted fault.

A green suite whose tests cannot catch believable mistakes is not strong evidence.

8. KEEP THE KERNEL GENERAL

Do not bend the IR to SFE, NPE, EXP-001, Proteus, or any existing runtime.

Adapters bend.

The kernel contracts do not.

Likewise, do not assume:

* evolution must use generations;
* populations must have one representation;
* worlds are stationary;
* observations are scalar;
* rewards are singular;
* execution is synchronous;
* state is flat;
* a player is a conventional agent;
* one episode implies one uninterrupted computation;
* one experiment implies one parameterization.

Protect the ability to construct machinery we have not anticipated.

9. REDIS / STATEDEVICE

If Redis becomes available during the window, exercise RedisStateDevice against the same behavioral suite as InProcessStateDevice.

The acceptance target is semantic equivalence of the declared StateDevice contract, not implementation similarity.

If Redis is unavailable on the current host, continue development without blocking.

Do not install infrastructure or modify unrelated machines solely to make one test green unless existing operator authorization clearly covers it.

Keep Redis optional.

10. BRIDGES

Do not distort the kernel to achieve green SFE/NPE lowering.

For every bridge mismatch, classify it:

* kernel defect;
* adapter defect;
* target-runtime limitation;
* target-schema limitation;
* unsupported semantic;
* unknown because interface unavailable.

TARGET_UNSUPPORTED and UNAVAILABLE_INTERFACE are valid outcomes.

A clean refusal is better than a dishonest lowering.

You may improve bridge packets during tonight's loop if playtesting reaches them naturally, but kernel quality has priority.

11. AUTONOMY

Do not stop to ask the operator ordinary design questions during this window.

Make the best reversible engineering decision available and record:

* decision;
* competing alternatives;
* evidence;
* tests supporting it;
* reopen condition.

You may:

* add tests;
* add playtests;
* modify kernel implementation;
* refactor internals;
* revise provisional extension contracts;
* add experimental adapters;
* add observers/controls/substrates/worlds needed for playtesting;
* discard an approach that proves wrong;
* revisit earlier decisions when evidence contradicts them.

Exercise more caution around already-admitted/frozen core IDs. Preserve compatibility where reasonable; if evidence shows a frozen contract is fundamentally wrong, do not silently mutate it. Record the conflict and build/version the replacement explicitly.

12. DO NOT OPTIMIZE FOR LINE COUNT

Do not spend the night maximizing:

* number of modules;
* number of IDs;
* number of integrations;
* roadmap boxes checked;
* experiment count.

Optimize for:

* defects exposed;
* assumptions falsified;
* contracts clarified;
* adversarial cases survived;
* experiment expressivity;
* forensic recoverability;
* replay fidelity;
* isolation of failures;
* useful compositions made possible.

Deleting a bad abstraction is valid progress.

13. CONTINUOUS LEDGER

Maintain an append-only overnight development/playtest ledger.

For every cycle record at minimum:

* cycle number;
* elapsed time;
* target pressure/question;
* failing test/playtest;
* why RED was correct;
* implementation change;
* regression result;
* playtest executed;
* defects/surprises found;
* resulting design decision;
* commit/hash where applicable;
* next pressure selected.

Do not rewrite history when a design fails.

Failed approaches are evidence.

14. STOP CONDITIONS

Continue iterating for the full 8-hour window unless one of these occurs:

* repository integrity cannot be established;
* repeated tests indicate possible corruption of authoritative scientific records;
* required action would exceed existing machine/repository authority;
* continuing would require guessing an external frozen contract in a way that could contaminate another system;
* an invariant classified as safety/integrity-critical cannot be restored.

Ordinary failing tests, broken experimental branches, unsupported bridges, unavailable Redis, or bad architectural ideas are NOT stop conditions.

They are work.

If blocked in one lane, preserve the reproducer and move to another pressure.

15. END-OF-WINDOW RETURN

At the end of 8 hours, stop beginning new development cycles.

Finish or safely revert the current atomic cycle, run the strongest feasible regression suite, and return one consolidated report containing:

1. starting commit;
2. ending commit;
3. clean/dirty tree state;
4. total TDD/playtest cycles attempted;
5. tests added;
6. final test counts;
7. playtests executed;
8. defects discovered;
9. false greens discovered;
10. abstractions changed or discarded;
11. new kernel capabilities actually demonstrated;
12. EXP-002 status and evidence, if reached;
13. U3 implementation/status;
14. Redis acceptance status;
15. SFE/NPE bridge status if touched;
16. unresolved failures with smallest reproducers;
17. major architectural discoveries;
18. next three pressures suggested by the evidence.

Include representative receipt IDs and exact paths/hashes sufficient to reproduce the important results.

Most importantly, distinguish:

THINGS THE DESIGN DOCUMENT SAID SHOULD WORK

from

THINGS WE ACTUALLY TRIED TO DO AND OBSERVED WORKING.

For tonight, the second category is the authority.

Begin immediately and run the test/development/playtest loop for eight wall-clock hours from receipt.
