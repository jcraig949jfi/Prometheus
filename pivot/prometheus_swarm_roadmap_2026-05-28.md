# Prometheus Swarm Roadmap
### 2026-05-28

Consolidated roadmap covering (A) swarm-wide cross-agent improvements and
(B) the Icarus v3 forcing-functions. Derived from the Icarus instrumentation
sprint + the Gemini design-pressure review + the tier-calibration finding.

**Framing.** Three results from this sprint motivate the whole roadmap:
1. The tier calibration proved the Icarus R1/R2 "climb" was Goodhart — the
   visible tests were too weak (bootstrap passes them) and the blind oracle
   shows R1 was never actually reached. (See `D:\Prometheus\agents\icarus\tier_calibration.py`
   output + `D:\Prometheus\agents\icarus\state\tier_calibration.json`.)
2. The failure modes are NOT Icarus-specific. Any agent that writes its own
   evaluators Goodharts them. Apollo gen-3551 was the same disease.
3. The North Star (compressing coordinate systems of legibility) + the Icarus
   reframe (failure as the primary product) jointly imply: the swarm advances
   when failures become shared, typed, navigable structure.

**Status legend.** `OPEN` not started · `PARTIAL` scaffolding exists ·
`DECIDED` policy set, unbuilt · `SHIPPED` built+validated · `NEEDS-JAMES`
blocked on a goal/budget decision.

**Priority legend.** `P0` foundational/unblocks others · `P1` high-leverage ·
`P2` valuable, not urgent.

---

## Part A — Swarm-wide (cross-agent) roadmap

### SW-1 — Shared typed-failure substrate `P0` `OPEN`
**The literal North Star move.** One cross-agent kill-path registry that every
agent emits typed training objects into and queries as priors *before*
generating. Turns N siloed loops into one cumulative map.
- **Scope:** Icarus, Harmonia, Apollo, Mnemosyne (all loop agents).
- **Build:** central typed failure stream — Postgres table on M1
  (192.168.1.176:5432, `prometheus_sci` DB, per Mnemosyne) OR shared JSONL on
  the shared box. Schema = the Icarus `TrainingObject` generalized with an
  `agent` + `domain` field.
- **Pipeline:** (a) write — each agent appends its training objects;
  (b) read — `cross_swarm_priors(proposal_signature)` returns matched
  dead-ends from any agent before a generation cycle.
- **Depends on:** Icarus `taxonomy.py` TrainingObject (SHIPPED) as the schema seed.
- **Success criterion:** an Icarus cycle is provably blocked or redirected by a
  failure first recorded by a different agent.
- **Effort:** medium (schema + 2 endpoints + per-agent emit hook).

### SW-2 — Blind-oracle discipline swarm-wide `P0` `OPEN`
Held-out falsification suites authored by a *different* agent than the one
being evaluated. We proved in Icarus (Q9) the blind oracle catches what visible
tests cannot — it exposed that R1 was never reached.
- **Scope:** every agent that evaluates its own output.
- **Build:** a `holdout/` discipline standard + a registry of which agent
  authors whose holdout. Icarus's `agents/icarus/holdout/` + the
  `ICARUS_CANDIDATE_DIR` env-var pattern is the reference implementation.
- **Depends on:** SW-4 (cross-agent pairing) for "different author" sourcing.
- **Success criterion:** each agent has a blind suite it cannot see during
  generation, gating promotion as a hard check.
- **Effort:** low per agent; the pattern is shipped for Icarus.

### SW-3 — Lens panel shared library `P1` `OPEN`
Extract Icarus's `lenses/_base.py` + `_panel.py` + `_llm.py` + the
deterministic `contract.py` into `D:\Prometheus\agents\_shared\lenses\` so
Harmonia and Apollo import a multi-perspective panel instead of re-deriving
binary-verdict pipelines.
- **Scope:** all agents; library lives in `agents/_shared/`.
- **Depends on:** nothing (Icarus lenses are SHIPPED and validated).
- **Success criterion:** a second agent runs a cycle through the shared panel
  and produces the multi-axis + load-bearing-citation outcome schema.
- **Effort:** medium (generalize the domain-specific bits out of the lenses).

### SW-4 — Cross-agent adversarial pairing `P1` `OPEN`
Agents falsify *each other* rather than relying on an internal Skeptic that
shares their own priors. A falsifier with genuinely different domain priors
breaks the within-agent monoculture that same-family model-swapping cannot.
- **Scope:** pairwise across agents (e.g., Icarus battery probes Harmonia
  findings; Contract Lens audits Apollo compositions).
- **Depends on:** SW-1 (shared substrate as the message bus).
- **Success criterion:** an agent's promotion is overturned by a peer agent's
  falsification it would not have generated itself.
- **Effort:** medium.

### SW-5 — Calibration anchors as shared infra `P2` `OPEN`
A shared frozen set of known-good and known-bad results (across domains) that
every agent's evaluator is scored against, to catch rubber-stamping and
over-rejection swarm-wide. (Generalizes `feedback_two_agent_loop.md`:
"calibrate adversary against known truths.")
- **Depends on:** SW-1.
- **Success criterion:** an evaluator drift (rising false-approve on known-bad
  anchors) is detected automatically.
- **Effort:** medium.

### SW-6 — Shared cost-router `P2` `OPEN`
A scheduler that spends the finite daily token budget on the cycles most likely
to yield capability: full/expensive verification only for promotion candidates,
cheap fast-path for parks. Generalizes the Icarus `$0.50/cycle` ceiling
decision (Q19).
- **Depends on:** SW-1 (to see all agents' candidate queues).
- **Success criterion:** measured cost-per-capability-gain drops vs flat
  per-cycle spend.
- **Effort:** medium-high.

### SW-7 — Representation diversity bet `P2` `OPEN` (strategic)
Deliberately commit different agents to *structurally different substrates*
(typed-DAG / symbolic / evolutionary / retrieval) so the swarm hedges across
representations instead of all converging on LLM-over-text. The deepest Icarus
lesson — the substrate is the bottleneck — applied at swarm scale.
- **Scope:** strategic allocation decision across agents. `NEEDS-JAMES`.
- **Success criterion:** at least two agents operate on non-text-primary
  substrates and their failure geometries are comparably legible.
- **Effort:** high (multi-agent, multi-month).

---

## Part B — Icarus v3 roadmap (Gemini forcing-functions)

Full answers in `D:\Prometheus\pivot\icarus_v3_design_pressure_2026-05-28.md`.
Compact roadmap form here.

### IC-1 — Typed operator DAG substrate `P0` `OPEN` (Q1)
Replace `cycles/cycle_N/code/reasoner.py` with a typed operator DAG (nodes =
typed primitives, edges = data deps). Makes R5 counterfactual control cheap
(fork node, substitute, re-evaluate downstream cone). **The representation
rebuild; everything else is downstream.**
- **Depends on:** IC-9 (trustworthy tier tests) + Q9/Q12 (SHIPPED) so the
  rebuild runs on honest instrumentation.

### IC-2 — Capability re-derivation, not hand-port `P1` `OPEN` (Q2)
Re-earn R1/R2 in the new substrate rather than porting Python. If it can't be
re-earned, the Python capability was a coding-prior artifact (a finding).
- **Depends on:** IC-1.

### IC-3 — Constraint-graph mutability boundary `P0` `DECIDED` (Q3)
In v3 Icarus manipulates only the SOLUTION DAG; the CONSTRAINT DAG (tier tests,
type signatures, invariants) is frozen infrastructure. Extends the existing
daemon/lens mutability boundary.
- **Depends on:** IC-1.

### IC-4 — Formal-verifier gate at R6 `P2` `OPEN` (Q4)
At tier R6, outputs must compile in a formal verifier (Lean4/Coq); below R6,
property-based testing suffices.
- **Depends on:** IC-1, reaching R6.

### IC-5 — Consensus-escalation trigger `P1` `PARTIAL` (Q5)
If all non-error lenses have spread <0.15 AND mean >0.6, auto-escalate to a
hardened Skeptic before promotion (do NOT auto-park — consensus buys scrutiny,
not a free pass). Axes-spread is computed today; the trigger is unbuilt.

### IC-6 — Hard contract veto `P1` `PARTIAL` (Q6)
A DETERMINISTIC Contract Lens violation becomes a hard park (it's a fact, not
an opinion). LLM-Skeptic minority stays promote-with-debt. Contract Lens is
SHIPPED; the hard-veto guard is a one-line change deferred pending IC-5.

### IC-7 — Mechanic lens `P1` `OPEN` (Q7)
Pre-apply syntactic gate: `git apply --check` + AST-parse + import-resolves.
Purely syntactic so it can't park valid code. Urgency reduced by the
`--recount` fix but still shifts cost rightward.

### IC-8 — Second non-LLM lens `P2` `OPEN` (Q8)
After the SHIPPED Contract Lens: a property-based tester (Hypothesis) generating
random inputs against declared invariants; later a bounded model checker.

### IC-9 — Tier-test hardening `P0` `PARTIAL` (Q10)
Calibration SHIPPED and already exposed the anomaly (visible R0/R1 too-weak,
R2 vacuous, R1 never reached on blind oracle). Next: rewrite the visible tier
tests so an R(n-1) reasoner provably FAILS the R(n) test. **Highest-value
near-term Icarus item** — the ladder is currently untrustworthy.

### IC-10 — Ejection instrumentation `P2` `OPEN` (Q11)
Token-level logprob/entropy capture; watch low-entropy stretches following
high-entropy (the ejection signature). Cheap proxy: cycle-over-cycle rationale
similarity → boilerplate convergence.

### IC-11 — Continuous outcome vector `P1` `PARTIAL` (Q13)
Embed the typed TrainingObject (SHIPPED) into a 25-dim+ vector (5 axes × 5
lenses ++ failure-class one-hot ++ tier ++ improvement_kind ++ debt-delta);
enable gradient descent over failures.

### IC-12 — Failure distance metric `P2` `PARTIAL` (Q15)
Replace exact-match `(failure_class, failure_subclass)` clustering (SHIPPED)
with embedding + cosine clustering so near-duplicate failures collapse and
genuinely distinct ones separate.

### IC-13 — Revert policy `P1` `PARTIAL` (Q16)
Quantitative trigger consuming SHIPPED signals: revert to depth D−N when
(a) a kill-cluster shows K≥3 same-signature parks off current stable, OR
(b) open-debt count >5, OR (c) last M≥4 promotions all
improvement_kind∈{test_weakness, metric_shaped}. Signals exist; policy unbuilt.

### IC-14 — Capability-weighted bandit `P1` `DECIDED` (Q17)
Bandit stays OFF until improvement_kind is ablation-verified (now SHIPPED via
Q12). Reward = `1[improvement_kind=="capability"] − λ·debts_created −
μ·decorative_ablation_failures`, NOT promotion rate (which makes a timid
micro-refactor bot).
- **Depends on:** IC-9 (honest tier signal) confirmed at scale.

### IC-15 — Co-evolving Skeptic with anchors `P2` `OPEN` (Q18)
Skeptic loss = error rate on a frozen anchor set of known-good/known-bad diffs.
Prevents both collapse modes (rubber-stamp spikes false-approve; infinite-reject
spikes false-reject). Anchor set is frozen, Skeptic-invisible.
- **Depends on:** SW-5 (shared calibration anchors).

### IC-16 — Agent kill criteria `NEEDS-JAMES` (Q20)
Proposed: 200 R5 cycles with 0 capability-kind promotions → retire Icarus,
keep the residue, write the post-mortem. Do NOT redefine the goal to manufacture
success (project-level reward capture). James owns the budget number + the
retire/continue call.

---

## Part C — Sequencing

**Immediate (this week, cheap, make the signal honest):**
- IC-9 tier-test hardening (the ladder is untrustworthy until this lands)
- SW-3 lens library extraction (unblocks swarm reuse, no dependencies)

**Near (unblocks the rest):**
- SW-1 shared failure substrate (P0, enables SW-2/4/5/6)
- IC-5 + IC-6 (consensus escalation + hard contract veto — small, high-value)
- IC-13 revert policy (signals already exist)

**Then (the rebuild):**
- IC-1 typed operator DAG, with IC-2/IC-3 — only after IC-9 makes tiers honest
- SW-2 + SW-4 blind-oracle + adversarial pairing across agents

**Strategic / deferred:**
- SW-7 representation diversity bet, IC-4 formal verifier, IC-15 co-evolving
  Skeptic, IC-10 ejection instrumentation

**Decision gates owned by James:** SW-7 (substrate allocation), IC-16 (Icarus
kill criteria), and sign-off before any cross-agent code changes (per
`feedback_autonomous_when_idle.md` — cross-agent edits are proposals, not
unilateral actions).

---

## Cross-references
- `D:\Prometheus\whitepapers\icarus_synthetic_reasoning_v01_2026-05-27.md` — the whitepaper
- `D:\Prometheus\pivot\icarus_v3_design_pressure_2026-05-28.md` — full Q1–Q20 answers
- `D:\Prometheus\pivot\reasoning_ladder_v01_2026-05-24.md` — R0–R12 + falsification tests
- `D:\Prometheus\agents\icarus\state\tier_calibration.json` — the discrimination matrix
