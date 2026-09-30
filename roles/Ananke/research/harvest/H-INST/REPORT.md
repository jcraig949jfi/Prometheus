<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/H-INST; sha256(report)=45fb6f9f739ffa87; delimited; see REPORT.provenance.json -->
# H-INST REPORT: what PTE cannot see, and the primitives that would let it

Worker H-INST (Ananke inference harvest, 2026-09-30). Worktree F:/Prometheus-worktrees/ananke-base-role. Writes only under `roles/Ananke/research/harvest/H-INST/`. No engine or lens edits, no git writes, no campaigns.

Compute:
- About 0.1 core-hours in total, CPU only, 2 threads.
- One GPU incident, disclosed under OPERATIONS below.

Context read:
- `engine.py`, `lens.py`, `plants.py`, `envs.py`, `rng.py`.
- The W-V, W-S, W-K, W-D, W-M, W-P, W-R, W-T, W-Y, W-C, W-E, W-G, W-J, W-X, W-Z, W-U, W-N, W-L and W-I reports (headers and results).
- `CORRECTIONS_2026-09-29_SWAP_AUDIT`, `SYNTHESIS_2026-09-29`, `PTE_ENGINE_CARD`, `TEMPORAL_INTERVENTION_COVERAGE`, `CROSS_ENGINE_THREADS`, the instrument notes, and the operator directive.
- I read principal interpretations before designing. This was an inference-and-design brief, and I declare the context contamination here.

## 0. Key facts the design rests on (derived from engine.py)

**F1. Cross-site influence has exactly one path: a delivered packet.**
- A site's program reads only its own S, inbox (Acc), SENSE, E, Kp and r.
- Every random stream is a hash of (world seed, stream, tick, site) and never depends on state.
- Consequence: with identical Controls, a site of world B can start to differ from its lockstep twin A in only three ways:
  - a differing arrival;
  - a differing SENSE input;
  - an external hook.
- This makes an exact causal-difference tracer possible. It also gives a free correctness certificate: the "closure" counter, described in section 2.

**F2. Mail superposes by integer SUM.**
- With collision none or aloha, and no clamp hit, per-emitter contributions to Msum/Mcnt and to Acc_sum/Acc_cnt decompose exactly.
- Saturate is nonlinear, so it does not decompose.

**F3. Nothing in the record distinguishes "applied" from "reached the readout" from "used".**
- `lens.applied_ticks` compares a whole-batch digest per tick.
- `cue_arrival_profile` looks only at the actuator's mailbox.
- Swaps act at array granularity.

## 1. GAP TABLE

| # | Gap | Exists? (and its limits) | Consequence in the record | Primitive | Priority |
|---|---|---|---|---|---|
| G1 | Causal-edge tracing: which emitter's packet, emitted at tick te, carried a difference to which recipient at tick ta | Partial. **W-S LogWorld** logs mirror-different copies, but re-implements the routing draws, asserts no dup, noise or global topology, and was checked only for readout-bound traffic. **W-I twin_profile** gives per-tick component differences but no edges. **lens.cue_arrival_profile** covers the actuator only (its own F1). | W-S's frozen P3 "cone" primary failed (.16-.39 strict) because it counted cue-bearing copies the readout ignores; the correct rule (P8) was found post hoc. W-T: "copy counts are not causal weight" (W-V disagreement). | **diff_trace** with exact edges (IMPLEMENTED) | HIGH |
| G2 | Intervention reachability at the specimen's readout | Partial. **lens.verify_reach** has two parts: applied_ticks (batch digest, any state, any tick, any world) and a plant through the same hook at plant physics. **W-K**: no single check is universal. | A null reads NOT_VERIFIED when it could be certified NOT_REACHED. An edit to an inert store or a far site reads "applied". REACHED only means "this hook code can hit SOME pathway" (W-K: K2 misses TARGET, PROBE and FORCED). C1 D-A window miss (W-D 1a). | **reach_certificate**, per world (IMPLEMENTED) | HIGH |
| G3 | Local vs transported causal influence on a readout | No. Site vs channel swaps are reader-side, at one tick. A "SITE" verdict can be a latch that was itself transported earlier (W-I: CCCCSSS, the CHANNEL->LATCH motif R4). | Census classes read as mechanism classes. W-I showed that the mid-tick class is a PHASE reading. | **L/X path flags** in diff_trace (IMPLEMENTED) | HIGH |
| G4 | Information provenance (which emission carries the bit to the readout) | Partial. **W-V TagWorld** has fixed sensor groups, readout recipients only, and **in-flight only (no inbox)**, and uses no emission epochs. | W-Y found the readout's **inbox Acc_sum** was the unseen third carrier (KA-A UNRESOLVED at o10q1; the champion's o14q1 SITE_R .50). T-INS-17 ("cue-flip each source emission separately") is unbuilt. | **ProvenanceWorld** (group x epoch, inbox leg, invariant) + provenance_swap / provenance_follow (IMPLEMENTED) | HIGH |
| G5 | Write authority: who can and who did write Kp, r and w | No dynamic tool. Static decompiles are ad hoc (W-Y decompile; W-A, W-B disasm). | W-Y: "Kp differs 78-98%" (W-V) was entirely Kp[0], which never enters the readout. W-J: code change is receiver-gated (a claim made from code reading, not measured). | **component_causes()** in diff_trace (IMPLEMENTED, dynamic); a static dataflow map is designed only | MED |
| G6 | Distributed state retention (which SET of sites holds a trace jointly) | Partial. W-E and W-G have per-carrier global twin divergence plus decoders. W-P truth tables work over arrays, not site sets. | Retention "NO" verdicts are power-limited (W-E). "Two independent inert stores" (W-G 0ad7dc00) is not spatially resolved, so a distributed store needing k sites jointly would be invisible to single-world decoders. | Per-site diff maps (diff_trace.site_hook) + a **site-subset swap** truth table (designed) | MED |
| G7 | Direction-sensitive communication | No. | Routing "never carried the bit" (18/18) was measured by swapping w only. Direction of transfer (toward or away from the actuator, port asymmetry) is unmeasured. W-S: routing decides WHETHER the source hits the readout in c16d5231. | Edge direction profile from diff_trace edges (u-v displacement) + a reflection intervention (designed) | LOW-MED |
| G8 | Partial heredity (copying of Kp or code values between sites) | No. PTE has no individuals (engine card), but WIMM with IN operands lets a receiver copy sender content into Kp. | None in the record. The hazard is the fleet's "similarity is not copying" lesson. | A Kp lineage detector gated on diff_trace TRANSPORTED Kp writes (designed; must use donor-written bytes) | LOW |
| G9 | Self-maintained communication machinery (cue-independent in-flight or state infrastructure a mechanism needs across trials) | Partial. The C1b ITI flush control and the sham_positive plant. | Carryover waves (relay_flood about 48 ticks). The "normal_from1" logic in c1b needs a reach check. | reach_certificate with an ITI hook evaluated on later trials (IMPLEMENTED as a test pattern) | MED |
| G10 | Phase / clock-stratified reading | Ad hoc (W-R fork.phase_of). | 15/16 of 4781b0a1's offsets changed class under phase split (W-R). | Builder proposal B3 | HIGH (fleet) |

## 2. PRIMITIVE DESIGNS

### P1. `diff_trace(ph, genome, sch_a, sch_b, ws, T, hooks_b=None, ctrl_a=None, ctrl_b=None, edges=True) -> DiffTrace`

**Mechanism.** Two batches, A and B, run in lockstep with identical world seeds. B differs from A by schedule (single-cue twins via `twin_trace`), by hooks, or by Controls; edges are recorded only when the Controls are equal.

**Recorded per tick t, per world, per site:**
- a component-difference bitmask (S, inbox, Kp, r, w, E), taken after the step and again after hooks;
- whether the arrivals, SENSE input or emissions differ;
- whether a hook changed B's site arrays or the mail B will receive.

**Edges.** Each edge is a row (b, v, te, u, ta). They are recovered exactly by re-running the engine's own `World._emit` for the k-th differing emitter of every world into scratch mailboxes, with t_dev reset to te and stats restored. This supports dup, noise, jitter, loss, sample routing and plastic w by construction; dup and noise were not tested.

**Invariants (closure).**
- `unexplained_site == 0`: every new site difference has a differing arrival, SENSE input or hook.
- `unexplained_flight == 0`: every newly differing mailbox entry is a recorded edge target.
- Both hold only with equal Controls. Together they certify the tracer and engine locality (F1) at once.

**Derived quantities.**
- L and X flags per (tick, site) node:
  - L: an edge-free difference path from a SENSE or hook leaf exists.
  - X: a path crossing at least one packet edge exists.
- `path_class`: LOCAL, TRANSPORTED, BOTH or NO_DIFF.
- `readout_table(ep, trial)`.
- `cone(b, u, t)`: the backward difference cone (nodes, edges, and leaves ENV, HOOK_SITE, HOOK_FLIGHT).
- `cone_cut(cone, tau)`: held sites vs in-flight edges at tau. This is W-S's P3, generalized and exact.
- `component_causes()`: for each event where a component starts to differ, the input class that could have written it (SENSED, TRANSPORTED, CARRIED or HOOK). This is the dynamic write-authority measure.

**Semantics (must not be stretched).**
- These are DIFFERENCE paths. Outside the cone means "cannot carry the contrast" (sound).
- Inside the cone does not mean "used" (the engine card's PRESENT-BUT-UNUSED; W-S's P3 failure).
- Verdicts about USE still need interventions.

**Cost.**
- Two worlds, plus per tick 2 × max_b(number of differing emitters) scratch `_emit` calls, plus a diff over [LM, B, N].
- Small plants (N=24, M=16, 76-160 ticks): about 0.6-1.3 s on CPU.
- Dense champions (N=144, many differing emitters) scale about linearly in the differing-emitter count. Use M=32-64 per call; `edges=False` gives the cheap mode.

### P2. `reach_certificate(ph, genome, env, seeds, hooks, trial) -> {verdict, applied, touched, output, first_touch_lag, path}`

**Mechanism.** A is normal; B is normal plus hooks (same schedule and Controls). Per world:
- APPLIED: a hook changed B's state or mail.
- TOUCHED: the readout site's node became active between the hook and the readout tick.
- OUTPUT: the readout S0 differs.

**Batch verdicts:**
- **UNAPPLIED:** no world's state changed.
- **NOT_REACHED:** exact. The null carries no information about that readout.
- **ABSORBED:** the readout site was touched but its value did not change. This is the only informative-null candidate.
- **REACHED_OUTPUT:** the readout changed in at least one world, with a LOCAL / TRANSPORTED / BOTH path count.

**Relation to lens.verify_reach.** The certificate replaces the applied half of verify_reach. The plant half is still needed for a different question: "could this hook code hit a pathway at all?" (W-K K2).

**Cost.** One diff_trace call up to the trial's readout.

### P3. `ProvenanceWorld(World)`, `provenance_swap`, `provenance_follow`

**Tags.** Exact first-hop tags on mail addressed to a recipient set (default: the readout sites), keyed by key = group + G × epoch.
- `groups` is any [B, N] map.
- Epochs are cut at `epoch_bounds` on the emit tick.

**Inbox leg.** Tags follow the mail into the inbox (Acc) using the engine's own rules:
- drop_packets_at, aloha erasure, the wake-clear via `last_awake`;
- reset_state_at with 'inbox', flush_inflight_at;
- a clamp-hit counter.
Saturate and distractor_chan raise.

**Invariant.** `check()`: tags summed over keys equal Msum/Mcnt and Acc_sum/Acc_cnt at the recipients, exactly, every tick. Physics digest equals that of a plain World.

**Swap.** `provenance_swap(world, tags, keys)` gives each world its mirror partner's key-selected contribution, in flight and in the inbox. This is exact under SUM. `provenance_follow` forks after tick τ and runs to the readout, returning the follow rate per key set plus an `identical` flag.

**Scope limit.** Provenance is FIRST-HOP (emitter). Relay provenance, meaning which original source's bit rides in a relay's packet, is diff_trace's cone, not tags.

**Cost.** G extra `_emit` calls per tick, plus LM × B × A × K × C × P int32 of tags.

### Designed, not implemented

**D-G5 static authority map.**
- `authority_map(ph, genome)`: forward dataflow over the reduced instruction fields (`g_op`, `g_d`, `g_a`, `g_b`, per rule).
- Marks which registers flow into Kp (WIMM A→index, B→value), r (SETRULE A), w (RPORT/RVAL) and EMIT/PAY, with a taint class for each source: arrival (IN*/CNT*), SENSE, state, or constant.
- Invariant: any Kp, r or w difference that diff_trace classifies TRANSPORTED at a site must have an arrival-tainted path in the static map.
- Positive control: rule_switch_hold (r ← SENSE only). Negative control: echo_hold (no WIMM or SETRULE).
- W-Y's Kp[0]/Kp[7] confusion is the motivating case.

**D-G6 site-subset swap.**
- `site_swap(world, site_mask[B,N], arrays)`, plus a truth table over K spatial blocks chosen from diff_trace's held set at τ (the cone_cut 'held' sites).
- This distinguishes a LOCALIZED store (one site decides) from a DISTRIBUTED one (AND/OR over sites), reusing W-P's cube logic over sites.
- Known answers: hold_latch (1 site) vs a 2-site AND plant (to be built).

**D-G7 direction.**
- `edge_direction_profile(dt, geometry)`: a histogram of cone edges by signed displacement or port.
- Intervention: a reflection hook that mirrors ring positions of the in-flight mail (a recipient permutation), plus a reach_certificate.
- Known answer: route_relay (distance-2 ports open on + cue) must be direction/distance sensitive; relay_flood with dest all must be symmetric.

**D-G8 heredity.**
- A Kp lineage event is a Kp[u] component difference caused TRANSPORTED by an edge from v whose payload was computed from v's Kp. This requires a v-side Kp→PAY taint in the static map.
- Never infer it from value equality: the fleet's "similarity is not copying" lesson.

## 3. IMPLEMENTED

- **Module:** `roles/Ananke/research/harvest/H-INST/pte_trace.py`. It imports `prometheus.ananke` (engine, envs); engine files are untouched.
- **Tests:** `roles/Ananke/research/harvest/H-INST/test_pte_trace.py`, 23 tests built on `plants.py` (echo_hold, hold_latch, null, relay_flood, rule_switch_hold, route_relay, sham_positive_hold). Each has a positive control, a negative (absence) control and an inline must-fail input.
- **Command (worktree root):** `CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python -m pytest roles/Ananke/research/harvest/H-INST/test_pte_trace.py -q -p no:cacheprovider`
- **Result:** 23 passed in 44.6 s, RC=0 (`H-INST/logs/pytest.log`). The first run had 2 failures, both test-design errors I fixed:
  - I required live inbox tags under aloha cap 1, but both echoes collide there, so aloha correctly erases the inbox. The inbox-mass requirement moved to a new `p2` variant.
  - A swap test sampled a tick with an empty inbox. It now steps to the first live-inbox tick.

Known answers verified:

**Closure.** 0/0 unexplained on:
- echo twins;
- echo at period 2 with aloha;
- echo async;
- relay_flood with sample routing, loss .2, jitter 2 and period 2;
- route_relay with plastic w.

Must-fail: recomputing edges one tick late gives 44-503 unexplained flight entries in every case.

**Edges and cone (echo_hold, trial 5, t0=65).**
- The readout cone is exactly {s→s±1 at t0 (arriving t0+5), s±1→s at t0+5 (arriving at the readout t0+10)}, with a single leaf ENV(t0, s).
- At mid-gap the cut is 2 edges in flight and nothing held.
- For hold_latch the cut is {s} held, with no edges.
- Negative: a site 12 hops away has an empty cone.
- Must-fail: the cone at readout−1 differs.

**Local vs transported.**
- hold_latch: LOCAL 16/16.
- echo_hold: TRANSPORTED 16/16.
- relay_flood (delay == delta): TRANSPORTED 16/16.
- null genome: NO_DIFF 16/16, with no output difference and 0 edges.

**Write authority.**
- rule_switch_hold: r written only when SENSED.
- route_relay: w only SENSED (at the sensor), S only TRANSPORTED.
- echo_hold: no r, w or Kp differences.

**Reach certificate (hold_latch, hook at trial 5 mid):**

| Hook | Verdict | Detail |
|---|---|---|
| swap S | REACHED_OUTPUT | LOCAL 16 |
| +7 to the readout's unused S1 | ABSORBED | touched 1.0, output 0 |
| +7 to S0 at every non-readout site | NOT_REACHED | applied 1.0 |
| swap w | UNAPPLIED | |

Echo_hold with a flush:
- flush at mid: REACHED_OUTPUT, TRANSPORTED (output .375: without an echo S0 keeps its previous sign);
- flush at the readout tick: applied but NOT_REACHED.

**verify_reach evaluation (test).** For the "S0 elsewhere" hook:
- `lens.applied_ticks` = 85 > 0, so `verify_reach(plant=None)` returns NOT_VERIFIED;
- the certificate proves NOT_REACHED.

**Self-maintained machinery.** A flush at trial 0's ITI:
- sham_positive_hold: REACHED_OUTPUT on trials 1 and 3, TRANSPORTED;
- echo_hold: UNAPPLIED (nothing in flight at the ITI).

**Provenance.**
- Tags sum exactly (max deviation 0) on plain, p2, p2+aloha, drop, flush, reset(S, inbox) at period 3, and async. The digest equals a plain World's.
- Must-fail: a non-partition group map gives a mismatch above 0.
- Echo readout mail comes only from s±1 (1920 + 1920 counts), and the rest contributes 0. Must-fail: recipient s+12 gets 0 from the neighbours.

**Provenance follow (echo, mid).**

| Arm | Follow |
|---|---|
| LR | 1.00 |
| L alone | .375 |
| R alone | .375 |
| rest | identical to normal |
| none | identical to normal |
| epoch ≥ t0+5 | 1.00 |
| older epochs | identical to normal |

**Swap exactness.** With all keys selected (all-site recipients, period 2, live inbox), the swap is digest-equal to a raw swap of Msum, Mcnt, Acc_sum and Acc_cnt between partners. Must-fail: a single live key is not equal.

## 4. EVALUATION OF lens.verify_reach (asked for)

1. **applied_ticks is not reach.**
   - It is a whole-batch sha256 digest over every state array, including ticks after the readout, inert stores and non-readout sites.
   - One changed world out of M counts as applied, so it is not per world.
   - Demonstrated in the test above: 85 applied ticks, yet NOT_REACHED.
2. **REACHED certifies the hook code, not the specimen.**
   - REACHED = applied in the specimen AND a plant, possibly at other physics, fired under the same hook.
   - It does not show that the change reached the specimen's readout pathway.
   - Specimen-level reach should be exact via reach_certificate. Keep the plant for W-K's reasons (unwired or inert code).
3. **There is no per-trial timing.**
   - A hook after the readout of the trial being read counts as applied.
   - Demonstrated on echo: a flush at the readout tick has applied 1.0 and NOT_REACHED.
4. **Minor:**
   - applied_ticks always builds A with `Controls()`, so a specimen evaluated under a non-default base ctrl is compared to the wrong reference.
   - plant_fired's "fired" requires a drop (hi_d < −.10) or a FLIP, so an intervention whose correct signature is a gain cannot verify.

**Recommendation.** In new preregistrations, report reach_certificate next to verify_reach:
- NOT_REACHED → WINDOW_OR_TARGET_UNREACHABLE;
- ABSORBED → an admissible null;
- UNAPPLIED → no-op.
Do not retro-edit frozen C1b semantics.

## 5. BUILDER-EXPERIMENT PROPOSALS (cross-engine)

### B1. Pooled statistics confounded by group base rates / strata
- **Problem:** a pooled rate or class mixes strata with different base rates, so the pooled reading matches no stratum (Simpson).
- **Observed:**
  - W-R: the pooled class changes under phase split in 15/16 of 4781b0a1's offsets; 0/17 pooled mixed readings resolve in both phases.
  - W-O: "42 transfers" are 20 dependent groups (W-Q).
  - W-V vs W-T: copy counts vs causal share.
  - W-M: pair-level sums near 1 while the per-trial identity is broken.
- **API:** `stratified(table, unit_key, strata_keys, stat, ci) -> {pooled, per_stratum, simpson_flag, dependence_units}`.
- **Invariant:** a pooled verdict is reportable only if it is (a) consistent with every stratum having at least n_min, or (b) explicitly labelled MIXED_ACROSS_STRATA. The CI is computed over the declared independence unit, never over rows.
- **Positive control:** a synthetic two-stratum table with opposite effects and unequal weights must raise simpson_flag.
- **Negative control:** a homogeneous table must not.
- **Must never silently change:** the preregistered unit of analysis or the verdict thresholds. It only adds flags and per-stratum columns.

### B2. Instrument identities forced by design (vacuous relations)
- **Problem:** a relation among instrument outputs holds for any input, so it is not evidence.
- **Observed:**
  - W-M: site_acc + chan_acc ≈ 1 is forced by the mirror design.
  - W-P lemma: N requires both a site and a channel component.
  - W-Y MF-SHUF: the REDUNDANT branch reads REDUNDANT on shuffled labels.
  - W-D 4 (AETH-03 forced) and W-K FORCED-B.
  - W-X: boundary truths built to sit exactly at z = ±1/2.
- **API:** `identity_audit(instrument, relation, null_generators=[shuffle_pairs, independent_synthetic, constant_policy]) -> {forced: bool, null_rate}`.
- **Invariant:** any relation or branch used in a verdict has a null rate at most alpha under at least 2 null generators, or else it is labelled FORCED and excluded as evidence.
- **Positive control:** the site + chan sum on shuffled pairs must read forced.
- **Negative control:** the FLIP verdict on a hold_latch S swap under shuffled pair labels must fall to chance.
- **Must never:** alter the instrument's outputs; it only annotates them.

### B3. Phase / clock stratification as a required key
- **Problem:** the sync update period p > 1 plus the trial period Pd define hidden phases.
- **Observed:** W-R (8/9 specs sync, p = 2; odd Pd alternates phase); W-S (the mixed phase is one jitter draw); E1/E2 with even Pd have an empty stratum.
- **API:** `phase_keys(ph, env, trial, offset) -> {wake_phase, arrival_phase...}`, derived from the physics only. Every census call must accept it and report per phase.
- **Invariant:** for sync physics with update_period > 1, a class without a phase index is flagged. For async physics a phase split must show no effect (a negative control).
- **Positive control:** the direct-carrier plant P1_J1 (W-T), mixed in q0 and clean in q1.
- **Negative control:** 369f5a5b (async) or an async hold_latch must show no phase effect.
- **Must never:** re-bin the preregistered primary; the stratified table is an added output.

### B4. Seed and namespace sensitivity near thresholds
- **Problem:** verdicts whose CI lies near a bar flip under a new namespace.
- **Observed:**
  - W-Z consistency 92.7% vs a 95% bar.
  - W-N p_min tables (P32 K3 needs .91).
  - W-O: 90 CHANCE → FLIP at 512 worlds.
  - W-G: e79e72df "L1.5" not replicated.
  - Fleet: the HOME battery hashseed dependence.
- **API:** `margin(ci, bars) -> distance in CI half-widths`, plus `replicate_if_marginal(fn, ns_list, margin<1)`.
- **Invariant:** a verdict whose CI is within one half-width of any bar needs agreement in 2 independent namespaces, otherwise it is labelled MARGINAL.
- **Positive control:** a synthetic statistic at the bar must be labelled MARGINAL at least 90% of the time.
- **Negative control:** a statistic 5 half-widths from the bar must never be flagged.
- **Must never:** change the bar or the rule; it only adds a replication gate and a label.

### B5. Difference ≠ use (needs a paired intervention)
- **Problem:** cue-dependent differences (decoders, copies, cones, scars) get read as carriers.
- **Observed:**
  - W-S P3 failed.
  - W-T: copies ≠ weight.
  - W-E / W-G: frozen signed scars, EFFECTIVE = 0.
  - Engine card: pay0 decodes at .85 with no swap effect.
- **API:** `difference_vs_use(dt: DiffTrace, arm_results)`. Every difference-based candidate carrier set must be paired with an intervention result on that same set.
- **Invariant:** outside the cone implies no effect (a hard check: an effect outside the cone is an instrument bug). Inside the cone requires an intervention verdict before any carrier claim.
- **Positive control:** the echo cone contains the carrier and the flush reaches the output.
- **Negative control:** hold_latch's neighbours are outside the cone, and swaps there must be identical.
- **Must never:** convert a cone into a carrier verdict.

### B6. Intervention reach (fleet form of X-4)
- **Problem:** nulls from interventions that could not fire (W-D: 5 kinds over 4 seats).
- **API:** each engine implements `lockstep(A, B_with_intervention) -> per-unit {applied, touched_readout, output_changed}`, which is what reach_certificate is for PTE. It requires common random numbers.
- **Invariant:** a null is admissible only if ABSORBED (touched, unchanged). NOT_REACHED and UNAPPLIED are reported as non-tests.
- **Positive control:** a window-miss plant must read NOT_REACHED (echo flush at the readout tick).
- **Negative control:** an in-window flush must read REACHED_OUTPUT.
- **Must never:** relabel a frozen verdict class; the certificate is added beside it.

## 6. OPEN QUESTIONS

1. **Edge cost on dense champions.** 4781b0a1 (5 sensors, dense traffic) has not been traced. Estimated at M=64: about 1-3 min per trial on CPU. Worth running once as a cone-vs-swap cross-check. W-V said ALL5 = FLA, so the readout cone should hold sensor edges only after o10.
2. **Should the cone use "last effective write" pruning?** W-S's P3 over-counts re-broadcast copies the readout overwrites. A pruned cone keeps an edge only if removing its difference changes the readout. That needs per-edge counterfactuals, which gives an intervention-based causal cone (cost: E forks).
3. **Controls-difference edges.** Tracing with different Controls in A and B (for example shuffle_dest) disables edges. Emitter-level attribution under Controls interventions is not designed yet.
4. **Should reach_certificate replace verify_reach's applied half in the promoted lens?** That would be a principal decision, and C1b semantics are frozen.
5. **Is the "L alone = .375" echo partial effect a clean known answer for a 2-carrier AND?** It depends on the previous trial's sign, so it is not a fixed number; I did not assert a value.

## 7. DISAGREEMENTS

- **COMMON_RULES_ARC3 s5** ("run every engine process with CUDA_VISIBLE_DEVICES=").
  - On this host an empty value does NOT hide the GPU: `torch.cuda.is_available()` is True. `CUDA_VISIBLE_DEVICES=-1` works.
  - World defaults to device="cuda", so a script that omits device silently uses the GPU. W-Y's 2 s GPU touch is the same mechanism.
  - Proposed fix: set "-1", and/or have World default to cpu in worker harnesses.
- **INSTRUMENT_REACH_VERIFICATION.md.** "REACHED" is a stronger name than the check supports; see section 4.

## OPERATIONS

- **GPU incident.** One exploratory `ProvenanceWorld` construction ran on cuda:0 for under 1 s. The cause was that `CUDA_VISIBLE_DEVICES=` was set but ineffective, and I had not forced device="cpu" there. I then fixed the code and environment: `ProvenanceWorld` defaults to cpu, and the tests force "-1" when the variable is empty. It was not leased.
- **Compute.** Every other run was CPU with 2 threads; total about 0.1 core-hours.
- **Processes.** One pytest run looped on a test bug (unbounded while). It was stopped with TaskStop after about 2 min, and the loop is now bounded.
- **Leftover python processes.** Three unrelated python PIDs remain; none are mine: 7340 and 7620 date from 09-25, and 19152 started 18:03, apparently a sibling harvest worker.
- **Hygiene.** No pycache, no git writes, no edits outside H-INST/.
