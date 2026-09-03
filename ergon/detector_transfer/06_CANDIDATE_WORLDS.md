# 06 - CANDIDATE MODERN-COLLIDER WORLDS

Nominated from ACTUAL inspection of the current stack, not from what a world
would ideally look like. Nothing was executed.

Sources inspected:
    SerendipityFoundry/SerendipityFoundryEngine/sfe/executors.py
    SerendipityFoundry/SerendipityFoundryEngine/sfe/api.py
    SerendipityFoundry/stackvm_admission/STACKVM_ADMISSION_SPEC.md

FIRST STRUCTURAL FINDING. The SFE is an EXPERIMENT ORCHESTRATION engine --
worlds, hypotheses, predictions, budgets, forks, observations, failures, work
claim/heartbeat/complete. It is NOT itself a genotype substrate. The substrate
is whatever implements the Executor ABC. So "SFE" is not a candidate world;
Executors are.

---------------------------------------------------------------------------
CANDIDATE A -- bitstring-onemax (sfe.executors.BitStringExecutor)
---------------------------------------------------------------------------
genotype            bitstring, default length 24
alphabet            A = 2
phenotype P(g)      per-position MATCH VECTOR against the hidden target
scalar s(g)         score = fraction of matching positions
projection pi       s = |P| / L  -- a TRUE world-applied projection. The world
                    computes exactly this. Seam S1 is SATISFIED natively.
determinism         BIT_DETERMINISTIC by construction; target derived by
                    SHA-256 from the world seed, so identical landscape iff
                    identical seed
neighbourhood       substitution only, |N1| = L*(A-1) = 24. Trivially exhaustive.
invalid class       empty (any bitstring is valid)
cost                24 evaluations per genotype. Negligible.

DEGENERACY: 2^24 match vectors collapse onto 25 scalar levels -- far more
extreme than Avida's 512 -> 26.

VERDICT: CALIBRATION ONLY. DO NOT USE AS THE TEST.

REASON, and it is the most useful finding of this pass. On onemax the answer is
ANALYTICALLY KNOWN WITHOUT RUNNING ANYTHING. If g currently mismatches k
positions, then all k improving flips yield the SAME scalar (+1/L) while
producing k DIFFERENT match vectors. So

    RESIDUAL(g) for the improving class = log2(k)   exactly

RESIDUAL is positive by construction, for every genotype, always. A world that
guarantees a positive cannot test a hypothesis. It can only qualify the
implementation -- which is genuinely valuable, and is what it should be used
for. This is precisely the trap contract A4 exists to prevent.

---------------------------------------------------------------------------
CANDIDATE B -- stackvm-v1 (foundry/engines/gp/stackvm/vm.py)
---------------------------------------------------------------------------
genotype            byte string, create_random length uniform in [16, 96]
alphabet            A = 256 (opcode = byte % 33; 33 opcodes)
observables         steps, halt class (end/steps/wall), output (signed stack
                    top), |opcodes_executed|, |memory_written|, final stack depth
determinism         bit-deterministic in (code, inputs, max_steps) EXCEPT the
                    wall-clock backstop; halt == "wall" is a declared
                    nondeterminism channel and the spec itself says exclude it
neighbourhood       substitution |N1| = L*255, i.e. 4,080 (L=16) to 24,480 (L=96)
invalid class       EMPTY BY DESIGN -- "every byte sequence is a legal program"
cost                ~2.4e4 evaluations per genotype at max length. Tractable.

BLOCKING SEAM: NO NATURAL SCALAR SELECTION CHANNEL. The spec states plainly
that "Task success is not an available observable, because task definitions
come from the corpus." All canonical observables are INTRINSIC execution
measures. There is no selection rule, hence no world-applied pi, hence any
scalar the analyst picks is INVENTED -- which triggers PROJECTION_INVENTED and
voids the experiment before it starts.

VERDICT: STRONGEST SUBSTRATE, NOT YET USABLE. Requires a declared selection
rule that is part of the world rather than of the analysis. That is a Daedalus
or SFE decision, not Ergon's to make.

Its empty invalid class is also a physics difference from Avida worth stating:
the BOTTOM machinery in the contract will be exercised nowhere here.

---------------------------------------------------------------------------
CANDIDATE C -- NondeterministicExecutor (sfe.executors)
---------------------------------------------------------------------------
Deliberately nondeterministic; exists so tests can prove the Foundry does not
falsely claim deterministic reproduction.

VERDICT: NEGATIVE CONTROL ONLY. It is the ready-made instrument for the
EXECUTION_STOCHASTICITY_DOMINATES class. The detector run against it MUST
return NONDETERMINISM_DETECTED. If it returns a residual instead, the detector
is broken. Use it as a fail-closed test, never as a world.

---------------------------------------------------------------------------
RECOMMENDATION
---------------------------------------------------------------------------
Prefer the simplest world that can KILL the hypothesis cleanly. None of the
three can yet, and the honest recommendation is therefore a sequence:

  1. Run A as CALIBRATION. Confirm the implementation reproduces
     RESIDUAL = log2(k) analytically. Confirm b6 (scalar neighbourhood
     summary) ALSO separates the improving class perfectly -- on onemax it
     does, which is exactly why A cannot test the hypothesis.
  2. Run C as a FAIL-CLOSED test. Expect NONDETERMINISM_DETECTED.
  3. Do NOT run B until a world-applied selection rule exists. Requesting one
     is the single highest-value integration ask (seam S1).

FIRST EXECUTION CANDIDATE: none is ready. The first EXECUTION should be
calibration A plus fail-closed C, which spend almost nothing and can only
qualify or falsify the implementation. The first SCIENTIFIC execution must wait
on B acquiring a declared selection rule.
