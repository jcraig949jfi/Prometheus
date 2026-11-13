# 05 — The recursion mechanism

## 1. One generation, step by step

State entering generation g: S_g = (θ_g, φ_g, stack_g, ledger_g). The budget is B_g = C_obj + C_meta, fixed by K.

1. **What it receives.**
   - From the dev generator: a batch T_g of task families (e.g. 24 families × 20 tasks), each task given as ≤ 6 input/output examples. Query inputs stay inside the oracle.
   - Nothing about held-out families.
   - From its own ledger: past ACTION and EVENT records, and accept/reject outcomes with screen deltas.
2. **Internal state maintained.** θ_g (library, grammar, episodic store) and φ_g (six slot programs). The rollback stack and the ledger are maintained by K and readable by φ only through `History`.
3. **Observation vs action.** The interpreter is the only executor. Each charge is tagged with the slot that caused it, and every oracle submission is an ACTION record. Oracle verdicts, task arrivals and acceptance results are EVENTS. φ cannot write EVENT records.
4. **What it learns through experience (WAKE + SLEEP, C_obj).**
   - **WAKE:** `solve(T_g, φ_g, θ_g, C_obj/2)`. φ.schedule orders and budgets the tasks; best-first enumeration uses priority φ.score and prunes on φ.key; solutions and failure frontiers go to θ.M.
   - **SLEEP:**
     - φ.abstract proposes candidate abstractions from the solution corpus;
     - the kernel MDL gate admits those that shorten the corpus by more than τ bits, net of the abstraction's own length;
     - promotion adds them to θ.L with the exact-expansion contract;
     - φ.reweight recomputes θ.G;
     - a second short WAKE (C_obj/2) retries failed tasks with the new θ. This is DreamCoder's iterate.
   - This is **L1**: θ changes durably.
5. **How it discovers candidate mechanisms.**
   - Object level: enumeration under the learned grammar plus promoted abstractions. These abstractions are the "mechanisms" of the task world.
   - Meta level: enumeration of φ-edits (step 7).
6. **Representation and execution.** Every mechanism, task-level or improver-level, is a typed DSL term executed by the metered interpreter. Abstractions are content-addressed and expand exactly (§1 of 04).
7. **How it proposes changes to its own improver (META, C_meta).**
   - The meta-problem is "find a well-typed φ′ ≠ φ_g". The kernel defines the edit grammar.
   - `solve` is run on it with **φ_g.score, φ_g.key and θ_g** — the same procedure and vocabulary used on tasks.
   - The frontier of φ-edits is ordered by φ_g.score. Duplicates are pruned by φ_g.key; on φ-ASTs, the key is applied through `run_on_examples` over the 64-state probe battery, so edits that behave identically collapse when the key is behavioural.
   - φ_g.screen ranks the first N (≤ 256) generated edits.
   - The top m (≤ 64) go to the screen panel. Screen deltas are returned and logged.
   - The best ≤ 4 by screen go to the confirm panel.
8. **How changes are tested.** `K.accept` (04 §4): filters, then screen, then confirm from θ₀, then continuation from θ_g. Every evaluation is charged to C_meta.
9. **How valid improvements are retained.** At most one edit is accepted per generation: the best confirmed one. This keeps attribution clean, one variable per step. The edit is pushed on the rollback stack and φ_{g+1} = φ′. The SSA re-test pops edits whose knock-out no longer costs ≥ δ/2.
10. **How a descendant generates the next change.** In generation g+1, step 7 runs with φ_{g+1}. If the accepted edit changed score, key or screen, **the meta-search itself now runs differently** (channel 1). If generation g's SLEEP promoted new abstractions into θ_{g+1}.L, those abstractions are single productions in the edit grammar, so edits that were 6–10 nodes deep become 1–3 (channel 2).

## 2. The two recursion channels and how each is cut

| Channel | Mechanism | Prediction if it works | Knock-out (06 §2 arm M-KO) |
|---|---|---|---|
| **C1 reflexive reuse** | φ.score / φ.key / φ.screen are used both to search tasks and to search φ-edits | An accepted edit to these slots raises the meta-search's success rate (accepted edits per C_meta) at g+1 | Run g+1's meta-search with the **parent's** score/key/screen in the meta role only; the child's slots stay in the object role |
| **C2 operational knowledge** | Library entries are productions in EDITS(φ) | The depth of accepted φ-edits *measured in P₀ nodes* rises while their depth *in P₀ ∪ L nodes* stays small. Removing L from the edit grammar lowers the meta success rate | Run g+1's meta-search with the edit grammar restricted to P₀; the object level keeps L |

A third, weaker route needs no channel: an object-level improvement makes θ richer, so acceptance runs from θ₀ produce larger deltas. This is **not** recursion. It is excluded because acceptance always starts from θ₀.

## 3. Worked transition G0 → G1 → G2 (illustrative; the specific edits are hypotheses)

**G0.**

- φ₀:
  - score = `logp` (pure grammar order);
  - key = syntactic hash (no observational-equivalence pruning);
  - schedule = round-robin;
  - abstract = closed subtrees, single hole;
  - reweight = unigram counts;
  - screen = `logp` of the edit.
- θ₀ = uniform G, empty L.

**G0 → G1, a plausible first accepted edit: the OE key.**

- `key := λc. hash(run_on_examples(c))` is 4 nodes from P₀. Under φ₀.score = `logp`, a 4-node replacement of a 1-node slot is reached within the first few hundred enumerated edits.
- Prior art and Beta-04 (§3 of its synthesis: OE pruning was the dominant repair) predict a large object-level saving.
- From θ₀ it lets a blank learner reach deeper programs at equal charges. The confirm panel should show it on most families.
- Outcome: φ₁ = φ₀ with the OE key.
- In the same generation's sleep, θ gains abstractions from the task corpus, for example a `sort_by`/`take` composite or a `map`-over-`filter` idiom.

**What changes for the meta-search at G1 (channel 1).**

- The meta-search now also prunes φ-edits by behaviour on the probe battery. Many syntactically distinct but behaviourally identical edits — the inert-wrap class that broke Aphrodite A21 — now collapse to one.
- **Prediction:** at matched C_meta, φ₁'s meta-search evaluates more *behaviourally distinct* edits and finds an acceptable one with higher probability than φ₀'s meta-search started from the same φ₁ state.

**G1 → G2, a plausible second edit: abstraction proposal arity.**

- An edit to φ.abstract allows two-hole patterns. Aphrodite's prior-art survey (§2(c)) says single-hole LGG is strictly weaker than classical LGG.
- Expressed in P₀ this edit is ~8 nodes. Expressed with a library entry that the task world promoted — say a `pairs`/`zip`-of-subtrees idiom, if tree tasks are in the curriculum — it is 2–3.
- **Prediction (channel 2):** this edit is reachable by φ₁'s meta-search with L, and much less reachable with P₀ only.

**The L3 observation would be:**

- (a) φ₂ beats φ₁ on held-out families from θ₀;
- (b) the M-KO arms show that the G1 change (C1) or the G1 library (C2) causally raised the probability of finding φ₂ or an equally good edit, at matched C_meta;
- (c) φ₀'s meta machinery started from φ₁ finds such edits at a significantly lower rate.

Without (b) and (c), G2 is just "a fixed improver found two improvements in a row": iterated L2, which 06 records as **RECURSION_NOT_DEMONSTRATED**.

## 4. What is fixed, and what the organism discovered

| Item | Supplied by | Credited to the organism? |
|---|---|---|
| The *possibility* of the OE key (primitives exist) | Designer (P₀) | No |
| *Finding* the OE key, its acceptance, its effect size | Meta-search | Yes, as rediscovery of a withheld known mechanism, never as novelty |
| The reflexive wiring (same `solve` for both levels) | Designer | No. It is the architecture's hypothesis |
| The causal effect of edit g on discovery at g+1 | Measured | Yes, if M-KO shows it. **This is the claim.** |
| Abstractions in θ.L | Task experience + φ.abstract + kernel MDL gate | Yes for L1 |
| Their use in φ-edits | Meta-search | Yes, if C2 knock-out shows it |

## 5. Failure modes of the loop and the guards

| Failure | Guard |
|---|---|
| **Stagnation** (no edit passes) | Logged as a result, not hidden. The edit grammar guarantees non-trivial neighbourhoods. The withheld-mechanism battery verifies the meta channel can find *something*. If it finds none of six known-good edits in M0's budget, the meta channel is declared **inaccessible** (STOP condition, 06 §8) |
| **Destructive self-modification** | φ never touches K. Every φ′ runs in the metered interpreter with fuel bounds (total). Acceptance requires gain from θ₀ *and* non-inferiority from θ_g. The rollback stack pops edits that lose their effect. A φ′ that crashes, or exceeds 2× φ's meter on the probe battery, fails the filter |
| **Endless loops** | The language is total (fuel-bounded); every slot call is metered; C_meta is a hard cap; at most one acceptance per generation; a fixed generation count per run |
| **Reward hacking** | φ cannot see confirm-panel identities, held-out families, or other arms. Panels are fresh per attempt (an entropy domain without lineage ids, as in Aphrodite's tribunal entropy). The meter lives in the interpreter that runs φ, so φ cannot misdeclare its own cost — the RSI-toy X2 exploit class is closed by construction and tested by an adversarial-kit target. The MDL gate and acceptance are K-owned |
| **Cloning collapse / self-copy** | φ′ = φ is rejected syntactically *and* behaviourally (probe battery) |
| **Inert-wrap inflation** (A21) | Behavioural non-identity filter; channel-1 OE key on the meta level when discovered |
| **Winner's curse** | Screen and confirm use disjoint fresh panels; only the confirm bit decides |
| **Overfitting to the dev generator** | Final claims only on RSO-sealed held-out families from an *independently authored* generator (06 §3) |

## 6. Is environmental pressure necessary, and how to supply it without embedding solutions?

Yes. Two record lessons force it:

- A23/W8: compounding fires only when structure **recurs** where validation can see it.
- Beta-04 and the C-019 closeout: a curriculum that supplies the decomposition turns discovery into supply.

The rules for the dev generator:

1. **Recurrence without disclosure.** Families are sampled by composing motifs from a hidden motif grammar, so structure recurs across families. The motifs are never given to the engine as tasks, labels or decompositions. The engine sees only I/O examples of whole programs.
2. **Graded difficulty inside the recurring structure** (the EC polynomial-ladder lesson). Family size is drawn from a distribution whose low end is solvable by φ₀ from θ₀. Stepping stones exist, but which ones are not indexed.
3. **Visibility.** Screen and confirm panels are drawn from the same generator, so recurrence that helps is *seen* by acceptance (the A23 condition). This is also a limit: gains may be generator-specific. That is why held-out families come from a **different generator by a different author**, sharing only P₀.
4. **Supply screen before freeze** (Aphrodite T49). Before any frozen run, measure that φ₀ from θ₀ solves 20–60% of dev families. Otherwise the run is UNTESTABLE, not negative.
5. **No solution in the apparatus.** The oracle returns pass/fail on dev examples only. The truth for query inputs never leaves K. This is the R6 `truth`-in-probe lesson, enforced by the adversarial kit's SCRUB_ANSWER attack.
