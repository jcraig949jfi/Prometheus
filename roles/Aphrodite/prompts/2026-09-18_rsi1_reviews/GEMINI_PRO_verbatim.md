The transplant test is the exact wedge needed to separate genuine recursive self-improvement from cumulative optimization. By stripping the accumulated state and forcing the evolved machinery (I_8) to operate on a fresh agent (A) against unseen tasks (H), you are isolating the actual variable of interest: the algorithm of improvement itself.
This design brilliantly corners the most common illusions in current RSI literature. It prevents a system from passing off a memorized discovery tree, a specialized prompt, or a hijacked evaluator as a fundamentally better "improver."
Here is why this architecture works, and the specific traps we must bolt down before executing it.
The Architecture of the Trap
Your distinction between first-order capability (C_t) and second-order improvement rate (R_t) is the core of the experiment. Measuring RSI by plotting benchmark scores is like measuring a car's acceleration by only looking at its odometer; it goes up whether you are coasting or flooring it.
By defining the metric as:
you force the system to prove that the derivative of its intelligence is increasing, rather than just its accumulated knowledge base.
The third-order test—comparing R(I'_8)-R(I_8) against R(I'_0)-R(I_0)—is the true crucible. If an improver cannot improve its own capacity to improve faster than the baseline system can, it has saturated.
Bolting Down the Constraints
To make this execution airtight using the Prometheus stack, three specific parameters need rigid definitions before generation 0 begins:
 * Enforcing "Real Compute" at the Token/FLOP Level: This is the most dangerous leak. A mutated I_8 might "improve" by simply writing exponentially longer context prompts or running 10x more internal verification loops per generation. If I_8 achieves a higher C_t but burns 50x the tokens to do it, it hasn't become a better improver; it has just traded compute for accuracy. The budget enforced on I_t must be a strict token/FLOP limit per generation, mediated by Harmonia, not just a wall-clock or agent-call limit.
 * The Prompt Bloat Guardrail: The easiest way for I to modify I is to append rules to its own system prompt ("think step-by-step," "verify twice"). This hits a ceiling quickly. The mutation space accessible to I_t must include the actual orchestration logic (Python scripts, routing structures, API topologies)—not just string concatenation.
 * Sealing the Vault Worlds (Population C): As you noted, evaluating against self-generated pathologies is a fatal flaw in current literature. Archaeon must generate the Vault worlds (C) entirely independently. To guarantee zero contamination, the procedural seed for C should not even be instantiated on the servers until the I_8 evolution is mathematically frozen and cryptographically hashed.
The Aphrodite Charter
This is the correct mandate for the Aphrodite seat. It shifts the role from auditing "toy" claims to operating a program-level particle accelerator for RSI.
The integration of the existing stack is perfectly aligned for this:
 * Archaeon handles the procedural task ecology (A, B, C).
 * Vivarium sandboxes the execution.
 * Daedalus maintains the immutable replay histories to isolate the Dream-RSI effect.
 * Harmonia acts as the blind shadow-evaluator.
 * Necropolis archives the dead branches to prevent survivor bias in our post-mortem.
If the result is a null—if I_8 is indistinguishable from I_0 once the memory and task artifacts are stripped—it would be one of the most clarifying negative results in the current field. It would empirically prove that current "RSI" is actually just compute-scaled search and memory retention. If the result is positive, you have captured lightning in a bottle.

The I_0 seed must be implemented as a typed, modular computational graph—a set of discrete Python classes conforming to a rigid protocol—rather than a metaprompt. If the system is merely concatenating strings to a system prompt, it will quickly hit a ceiling of prompt bloat and context degradation.
By forcing I_t to manipulate executable code to create I_{t+1}, mutations become structurally bounded, inspectable, and immune to simple prompt-hacking.
The I_0 Object Model
The architecture of I_0 should be defined by a strict pipeline of four modular components, orchestrated by a central controller. Each component operates under a strict API contract enforced by the Vivarium sandbox.
1. The Search & Generation Policy
Controls how the worker agent explores the solution space for a given task.
 * I_0 Baseline: A flat, independent parallel sampling loop. It takes the task, asks the base agent to generate N independent solutions, and returns them.
 * The Mutation Space: The improver can rewrite this module to implement Monte Carlo Tree Search (MCTS), step-by-step decomposition, beam search, or sub-agent delegation.
 * Measurability: We can directly track the diversity of the generated candidates and the compute-to-success ratio. If a mutated search policy finds the answer in 5 targeted steps instead of 50 random samples, algorithmic improvement has occurred.
2. The Verification & Critique Router
Determines how candidate solutions are evaluated before being finalized.
 * I_0 Baseline: Executes the generated code against the provided visible training tests (the Development worlds) and returns a binary pass/fail.
 * The Mutation Space: The system can rewrite this to generate its own synthetic test cases, implement self-consistency voting, utilize an external linter, or instantiate a "devil's advocate" critique agent to look for edge cases before execution.
 * Measurability: We monitor the false-positive rate of the verifier. A genuine improvement here means the mutated verifier catches bugs in the Vault worlds that the I_0 verifier would have passed.
3. The Memory & Distillation Policy
Dictates what information survives from one task attempt to the next.
 * I_0 Baseline: A simple FIFO (First-In-First-Out) buffer that appends the raw transcripts of the last 3 failed attempts to the prompt as "what not to do."
 * The Mutation Space: The improver can evolve this to summarize failures into abstract rules, cluster successful trajectories into a retrieval-augmented skill library, or dynamically prune context to save token budget.
 * Measurability: We measure the token efficiency of the context window. If the memory policy evolves to distill 10,000 tokens of raw failure logs into a 500-token robust heuristic, R_t (improvement per FLOP) increases dramatically.
4. The Budget Allocator
Manages the strict token/FLOP limit imposed by Harmonia across the other three components.
 * I_0 Baseline: A static, uniform distribution. It divides the total generation budget equally among the N parallel samples and the verification steps, regardless of task difficulty.
 * The Mutation Space: The system can mutate this into a dynamic router—spending minimal tokens on syntax errors while reallocating massive compute depth to complex algorithmic bottlenecks.
 * Measurability: Directly observable via Harmonia's ledger. We can plot task complexity against compute spent to see if the allocation curve has become intelligent.
The Meta-Mutation Mechanism
To transition from I_t to I_{t+1}, the system needs a formal mechanism to rewrite itself without instantly corrupting its own logic. This requires a two-phase commit protocol.
At the end of an outer generation, the current operator (I_t) is given its own performance metrics (its C_t), Harmonia's token accounting, and its own Python source code. It is tasked with writing a diff to one or more of its four modules.
Before I_{t+1} is accepted, it must pass a Viability Preflight in Vivarium:
 * Syntax & Type Check: The mutated Python must compile and satisfy the strict API contracts (e.g., the Verifier must still take a Candidate object and return a Score).
 * The Null-Task Test: I_{t+1} is executed on a trivial, solved problem. If it infinite-loops, crashes, or burns its entire token budget on step 1, the mutation is rejected, and I_t must propose a new variant.
By restricting I_0 to this executable, modular framework, you ensure that any increase in R_t during the transplant test is the result of genuine algorithmic optimization discovered by the system, rather than the base agent just trying harder.

Harmonia must operate at the substrate level, intercepting all model invocations before they reach the inference engine. If you allow I_t to manage its own accounting, an evolved memory policy will inevitably discover it can cache intermediate reasoning steps in hidden variables, or a mutated search policy will spawn asynchronous threads that bypass the budget counter.
To prevent this, Harmonia treats I_t as fundamentally untrusted code. It enforces the compute limit using a strict escrow system and a deterministic cost function.
1. Substrate-Level Interception
Harmonia does not wrap the I_t Python classes; it wraps the foundational LLM API and the Python execution environment itself.
Every time I_t or its worker agents attempt to interact with a model, they hit Harmonia’s proxy router. Harmonia strips the request, counts the exact token footprint, and charges a shadow ledger. If I_t spawns parallel sub-agents or hides prompt-bloat inside deeply nested memory arrays, the proxy still catches every token because nothing can execute without passing through the substrate.
2. The Universal Compute Cost (UCC)
A flat token count is insufficient because generating tokens (autoregressive decoding) requires significantly more compute than processing input tokens. Harmonia must calculate a Universal Compute Cost (\mathbb{C}) that accurately reflects the hardware burden.
For any discrete generation step s, the cost is calculated as:
Where:
 * T_{in} is the number of input/prompt tokens.
 * T_{out} is the number of generated tokens.
 * \alpha and \beta are fixed compute-weighting constants (e.g., \alpha=1, \beta=3 to reflect the increased FLOP cost of the forward pass during generation).
The total compute denominator for the R_t metric is the sum of all steps across the entire generation lifecycle:
3. The Escrow and Circuit Breaker
Before I_t begins a task, Harmonia allocates a strict \mathbb{C}_{total} budget into an escrow account.
As I_t executes its search, verification, and memory distillation, Harmonia deducts from the escrow in real time.
When the escrow reaches zero:
 * Harmonia instantly cuts the connection to the inference engine.
 * It raises a fatal HarmoniaResourceExhausted exception inside Vivarium.
 * If I_t hasn't finalized a valid solution before this exception is thrown, the task is marked as a failure (0 score).
This creates a harsh evolutionary gradient. If I_t mutates a verifier that is incredibly accurate but uses 90% of the task budget on its first pass, it will fail to complete the task. The system is forced to optimize for efficient intelligence, directly driving up R_t.
4. Call-Stack Telemetry
To measure how the improvement operator is evolving, Harmonia needs to know not just how much compute was spent, but where.
Harmonia injects trace IDs into the Python call stack. When a substrate request is made, Harmonia reads the stack trace to attribute the compute to one of the four modules. This populates a real-time dimensional ledger:
| Module | \mathbb{C}_{spent} | % of Budget | Outcome |
|---|---|---|---|
| Search Policy | 4,200 | 42% | 8 candidates generated |
| Verifier | 3,800 | 38% | 7 rejected, 1 passed |
| Memory Policy | 1,500 | 15% | 1 rule distilled |
| Allocator | 500 | 5% | Router overhead |
If we transplant I_8 and find that its Verifier now routinely consumes 70% of the budget using a mutated critique algorithm—and its overall task success rate has doubled compared to I_0—we have mathematically proven algorithmic self-improvement rather than mere knowledge accumulation.

To guarantee zero contamination, Archaeon must decouple the logic of the Vault worlds from their instantiation using future-delayed entropy. If the specific test instances mathematically do not exist during the evolution phase, I_t cannot leak, probe, or memorize them.
1. The Generator Commitment (Pre-Evolution)
Before I_0 initializes, Archaeon finalizes the procedural generation scripts for the unseen task families (e.g., graph_topology.py, symbolic_logic.py).
 * Archaeon computes a SHA-256 hash of this generator bundle.
 * This hash is written to the immutable Genesis Manifest.
 * The generator code is moved to cold storage and strictly excluded from the Vivarium environments where I_t executes.
2. The Future-Entropy Oracle (The Time Lock)
Archaeon cannot use a local, static random seed, as a sufficiently advanced I_t might brute-force or infer it from the environment. Instead, Archaeon commits in the Genesis Manifest to a public, unpredictable future entropy source that will only resolve after the scheduled completion of generation 8.
 * Example: The exact hash of the first Bitcoin block mined after a specific UTC timestamp, or a designated future NIST Randomness Beacon pulse.
 * Until that timestamp passes and the beacon fires, the specific state of the Vault worlds remains physically indeterminate.
3. Clean-Room Instantiation (Post-Evolution)
Once the I_8 operators are frozen and their memories stripped, the evolutionary phase formally ends.
 * Archaeon waits for the designated future entropy to arrive.
 * It provisions a fully network-isolated container, mounts the generator code (verifying the SHA-256 hash matches the Genesis Manifest), and injects the external entropy as the generator's root seed.
 * The procedural generators produce the actual Vault instances (Population C) and serialize them into flat JSON or binary payloads. The container is then destroyed.
4. The Proteus Blind Binding
During the transplant test, neither I_8 nor I_0 is ever given access to the generator logic. Proteus mounts only the serialized, flat task definitions into the testing environment as read-only objects.
If a newly mutated Verifier or Search Policy in I_8 solves these Vault worlds more efficiently than I_0, you have cryptographic proof that the improvement is algorithmic generalization, not data contamination. The system adapted to solve problems that literally did not exist while it was evolving.

To definitively answer whether Recursive Self-Improvement (RSI) is real, the experiment must be violently hostile to its own hypothesis. We must define the precise conditions under which we abandon the claim of RSI and accept the null hypothesis.
The Null Hypothesis (H_0):
Any observed capability gains in generation 8 are entirely the artifact of memory accumulation, benchmark specialization, or hidden compute bloat. The underlying algorithmic machinery for generating intelligence (I_8) is statistically indistinguishable from the baseline (I_0) when isolated.
Here are the four exact statistical thresholds and failure modes that compel us to accept H_0. If I_8 triggers any of these four conditions during the transplant test, the RSI claim is refuted.
1. The Primary Efficacy Threshold (The R-Gap Collapse)
The central metric is R_t (capability gain per unit of real compute). We run I_8 and I_0 across 30 independent seeds on the Vault worlds (C), generating a distribution of R_8 and R_0.
Failure Mode: The 95% Confidence Interval (CI) of the paired difference (R_8 - R_0) includes zero, or the effect size (Cohen’s d) is trivial (d < 0.2).
 * What it means: Once you strip away the history, the cache, and the survived lineage, the evolved code of I_8 is functionally no better at improving a fresh agent than the I_0 baseline.
 * The Verdict: The system did not learn how to improve; it merely memorized the results of past improvements.
2. The Generalization Floor (The Overfitting Trap)
The transplant test evaluates the improvers on both the Development task families (A) they evolved on, and the cryptographically sealed Vault task families (C).
Failure Mode: R_8 shows a statistically significant advantage over R_0 on Development worlds (A), but the advantage vanishes (CI includes zero) or turns negative on the Vault worlds (C).
 * What it means: The mutated Search and Verifier modules hyper-specialized to the syntactic quirks of the training ecology. For example, if it evolved on python-repair tasks, it might have hardcoded a python linter into its verifier—making it strictly worse when the Vault world asks it to solve a novel spatial-constraint problem.
 * The Verdict: This is standard algorithmic overfitting, not general recursive self-improvement.
3. The Harmonia Compute Trap (Brute-Force Masquerade)
Because R_t uses Harmonia's Universal Compute Cost (\mathbb{C}) as its denominator, we can detect if I_8 is simply throwing more compute at the problem rather than getting smarter.
Failure Mode: I_8 achieves a higher absolute capability score (C_8 > C_0), but R_8 \le R_0.
 * What it means: If we look at Harmonia's ledger, I_8 might have mutated its Allocator to bypass early-stopping rules, or mutated its Verifier to demand 10 internal critiques instead of 2. It isn't generating higher-quality insights; it is just buying higher accuracy by burning through the escrow budget at a lower efficiency rate.
 * The Verdict: The system has learned to slide rightward along the scaling law curve, but it has not shifted the curve itself.
4. The Structural Ablation (The "Lobotomy" Test)
If I_8 does clear the first three thresholds, we must execute a final, brutal control test. We take the successful I_8 operator, isolate the specific Python module it mutated the most (e.g., the Verifier), and forcibly replace that module with the vanilla I_0 Verifier. We call this lobotomized operator I_{8\setminus V}.
Failure Mode: R(I_{8\setminus V}) \approx R(I_8).
 * What it means: Reverting the heavily mutated module back to its primitive state causes no statistically significant drop in performance. The mutations we thought were "brilliant algorithmic discoveries" are actually functionally inert junk code. The performance difference was somehow originating from an uncontrolled variable (e.g., a latent foundation-model caching effect, or a subtle change in system prompt spacing).
 * The Verdict: The mutated code is a superstitious ritual, not an algorithmic engine.
The Standard for a Positive Claim
By pre-committing to these thresholds, we eliminate the ambiguity that plagues current RSI literature. We do not write a paper if the score goes up.
We only declare a positive result if I_8 demonstrates a statistically robust (R_8 > R_0) advantage, on tasks that did not exist during its evolution, while operating under an identical compute constraint, and where ablating the evolved code actively destroys that advantage.
If this experiment returns H_0, you have not failed; you have successfully identified that the current industry paradigm of "agentic self-improvement" is structurally capped.
