# PROPOSAL V2-T06 (arm B)

## Hypothesis
Transplanting the *mechanism* behind Agent D-5's +10.95pp CFR findability advantage
(accumulated, ecology-adapted executable artifacts, content- not order-dependent)
into the Ludus arena will NOT reproduce a comparable advantage. Specifically:
(a) the literal D-5 artifact (a register-machine genotype over a frozen 14-opcode
alphabet) has no admissible consumer anywhere in Ludus's current worlds — this is
already established, not hypothesized (techne/donor_d5_compat_2026-08-31.json:
OVERALL "NO_COMPATIBLE_CONSUMER"); and (b) even a faithful re-instantiation of the
mechanism on a Ludus-native artifact type (small decision programs / parameterized
policies for the arena's own games) will show an M1-M0 CFR delta well below D-5's
+10.95pp, plausibly indistinguishable from the ~39%-retained generic
diversity-injection component D-5's own G9 ablation already isolated (≈+4.3pp),
because the substrate change breaks the content-ecology match the effect depends on.

## Motivating evidence
- agent_d5_blind/VERDICT.md: M1−M0 = +10.95pp CFR (p=0.0007, task n=42); G9 causal
  decomposition shows shuffled-history retains 100% of the advantage but a
  size-matched random-walk library retains only 39% — the effect is
  library-CONTENT, not order, and a genuine ~39% slice of it is generic
  diversity injection rather than ecology-specific structure.
- G7 (same VERDICT): frozen alien zero-shot transfer of the D-5 library to a
  different task family, WITHIN THE SAME SUBSTRATE, was NOT ESTABLISHED
  (+5pp, p=0.26). This is the closest existing "transplant" measurement D-5
  itself ran, and it did not clear significance even at minimal substrate
  distance.
- techne/donor_d5_compat_2026-08-31.json: all five installed Gen-0 donors are
  NO_COMPATIBLE_CONSUMER against the D-5 slot; the slot is strictly
  program-shaped (variable-length instruction sequences, 14 opcodes, typed
  arguments) and no adapter path exists without either a bespoke encoder or a
  semantic widening of the assay. Only Family A/B program-synthesis donors
  would natively match, and that acquisition decision is explicitly Lexis's,
  not resolved (roles/Lexis/ROLE.md:313 still lists Ruler/Enumo→babble as
  conditional on "if a substrate is chosen").
- roles/Ludus/REVIEW_PACKET_4_2026-09-01_arena.md: five arena worlds
  (tic-tac-toe, NIM, PIG, RPS, KUHN_POKER) exist behind one World/State/Player
  interface, none is W8 experiment-ready, and PIG is explicitly flagged as
  "the cheapest available executable instance" of the bench's blocked r0003
  hold-or-bank shape — the only candidate substrate currently cheap enough for
  a pilot of this kind.

## Prospective predictions
1. A literal-genotype transplant arm (import D-5's raw RM library into any
   Ludus world) is INADMISSIBLE and will be blocked at ingestion by a type
   check, not merely underperform — predict 0/0 artifacts accepted.
2. A re-instantiated arm (Ludus-native decision-program library, same M0 /
   M1 / M1-shuffled / M1-random design as D-5, on a parameterized PIG battery)
   will show M1−M0 CFR delta in [0pp, +6pp], point estimate ≈ +4pp — i.e. on
   the same order as D-5's own 39%-retained random-library floor, not its
   full +10.95pp ceiling.
3. The G9-style ablation on that delta will show LESS shuffled-retention than
   D-5's 100%, because Ludus's PIG parameterizations (varying target,
   bust_face, sides) are a much thinner, more homogeneous task ecology than
   D-5's 78 tasks — predict shuffled-retention in [40%, 90%], wide because n
   is small.
4. Whatever raw delta is observed will be dominated by the random-library
   (diversity-injection) control, not by ecology-specific content — predict
   random-library retention ≥ 60% of the raw M1−M0 delta.

## Experiment
Pilot substrate: F:\Prometheus\ludus\arena (PIG world only; already verified,
20/20 checks, deterministic). Do NOT attempt literal RM-genotype ingestion
(ruled out by prediction 1 above) — instead build a Ludus-native "artifact":
a short decision program over PIG's own observation keys (score, turn total,
target, bust probability) — e.g. a small typed if/threshold tree or a
tuple-of-rules genotype, capped at a comparable size to D-5's (≤24 elements).
Ground truth: exact DP-optimal hold-at-N policy per PIG parameterization
(closed form, already usable per REVIEW_PACKET_4 §12 item 5).

Task battery: 24–30 PIG parameterizations (bust_face ∈ {4,6,8,10,20} ×
target ∈ {20,50,100} × a few sides variants), each an independent "task"
exactly as D-5 treated its 78 tasks — one CFR outcome per task per arm.

Arms (mirroring D-5 exactly, so the comparison is apples-to-apples):
- M0: fresh random/evolutionary search per task, empty library, frozen.
- M1: library accumulates admitted solving/near-solving genotypes across
  tasks in a fixed task order.
- M1-shuffled: identical library content, permuted task order.
- M1-random: size-matched random-walk genotype library (no task history).

Metric: task-level CFR = fraction of seeds per task in which the arm's
search finds a policy within a preregistered epsilon of the DP-optimal
hold-at-N value (not merely "any legal policy"), under an identical metered
evaluation budget across all four arms.

## Controls
- M0 empty-library comparator (frozen, same as D-5's primary baseline).
- M1-shuffled and M1-random ablations, mandatory, not optional — this is the
  one design element in D-5 that actually discriminated content-effect from
  order-effect from generic diversity, and D-8's contradictory NO_EFFECT
  result (see below) shows the base mechanism does not survive substrate
  change unexamined.
- A structureless CTRL task family (PIG parameterizations with no closed-form
  advantage, e.g. degenerate target=1) mirroring D-5's G8, to catch a
  non-selective advantage.
- Ground-truth DP oracle used only to score, never as a search comparator
  (avoids REVIEW_PACKET_4's F2 finding: an oracle that sees privileged state
  is not a valid comparator against observation-limited search).

## Confound defenses
- Pre-hash the analysis script before any arm's rows are read, exactly as
  D-5's results/compute_gates.py was hashed before evidence — blocks
  post-hoc threshold shopping.
- Explicit, checkable type contract on the library-ingestion slot (reuse the
  donor_d5_compat pattern: reject-with-message on malformed genotypes) so a
  "successful" transplant cannot silently be a coercion artifact.
- Task-level unit of analysis (n = number of PIG parameterizations, not
  per-episode or per-seed rows), matching D-5's n=42 convention — prevents
  the per-row SE inflation already documented elsewhere in this program.
- Identical metered evaluation budget across all four arms per task (no
  budget asymmetry).
- Reuse Ludus's structural guarantee that the World cannot call the Player
  (core.py) so the search harness cannot leak privileged state into what the
  "library" or its consumer sees, keeping the CFR comparable to D-5's
  observation-limited framing.
- Report the CI beside every verdict; do not choose a gate line closer to
  the observed value than its own SE.

## Preregistered falsifiers (numeric thresholds)
1. Literal-genotype arm: if the RM library ingests into Ludus without a
   rejected/coerced record for ≥1 artifact, treat as instrument failure (the
   NO_COMPATIBLE_CONSUMER finding was wrong or bypassed) — investigate before
   trusting any downstream number.
2. Re-instantiated arm FAILS to transplant if M1−M0 CFR delta < +3pp OR
   one-sided permutation p > 0.05 at n≥24 tasks.
3. Even if #2 clears, call the effect "NOT ecology-specific" (i.e., not a
   real re-run of D-5's finding) if M1-random-library retains ≥ 60% of the
   raw M1−M0 delta.
4. Call the effect "order-dependent, not content-dependent" (a DIFFERENT
   mechanism than D-5's) if M1-shuffled retention < 70%.
5. Full success requires ALL of: delta ≥ +3pp with p ≤ 0.05, shuffled
   retention ≥ 70%, AND random-library retention ≤ 60% — i.e., the same
   three-way signature D-5 itself required, not just a raw CFR gap.

## Stopping rule
Run the pilot (24–30 PIG tasks, 4 arms, 5 seeds/task/arm minimum per this
program's replication doctrine) once, analyze against the pre-hashed script,
and stop. Do not scale to the other four arena worlds, and do not iterate on
task-battery composition after seeing arm-level results — a battery redesign
after a null is a second experiment, pre-registered separately. If falsifier
#1 fires, halt immediately; do not proceed to the re-instantiated arm's
statistics until the ingestion-contract failure is understood.

## Expected failure modes
- Most likely (per the wiki contradiction below): a clean null on the
  re-instantiated arm, indistinguishable from zero at this task-battery size
  — PIG's parameter families may simply be too homogeneous to give library
  content anything ecology-specific to adapt to, unlike D-5's 78
  structurally varied tasks.
- Underpowered floor-clearance: D-5's own +10.95pp was only 0.95pp above its
  preregistered floor at SE 3.4pp: a true PIG effect of similar fragility
  could easily land inside noise at n=24-30.
- Silent oracle leakage: an "optimal" policy library that was seeded or
  cross-checked using DP internals rather than discovered by the search
  would inflate CFR without measuring anything about library content.
- PIG may be too easy in the wrong way: hold-at-N is a scalar-threshold
  policy space small enough that M0 alone may already saturate CFR, leaving
  no room for M1 to show an advantage (a ceiling effect, not a content null).

## Compute estimate
Pure-Python, CPU-only, no GPU, no external donor library, no paid API calls.
Arena's own verify.py runs ~19,830 episodes in ~20s on this machine. At
comparable per-episode cost: 4 arms × ~28 tasks × 5 seeds × a D-5-scale
metered budget (5,000–10,000 evaluations/task/arm) ≈ 3–5.6M short PIG
rollouts. Order-of-magnitude estimate: low single-digit hours wall-clock on
one machine, single-threaded; parallelizable trivially across tasks if
needed. No lane/token budget consumed.

## Prior evidence that materially changed this design (or 'none found')
- techne/donor_d5_compat_2026-08-31.json changed the design from "port D-5's
  raw genotypes into Ludus" (the naive transplant) to "re-instantiate the
  mechanism on a Ludus-native artifact type with an explicit, checkable type
  contract," and added falsifier #1 as a hard gate before any downstream
  statistic is trusted.
- Evidence Wiki contradiction R-e68c9331eca2 (C-3a1c49fa5a78, D-8 blind S0
  NO_EFFECT vs C-3d12c440f087, D-5 blind SUPPORTED +10.95pp; classified
  APPARENT_UNDER_DIFFERING_CONDITIONS on substrate) directly lowered the
  point prediction from D-5's raw +10.95pp to ≈+4pp and made the full
  three-part G9 ablation (falsifiers #3–#5) mandatory rather than optional:
  the same "accumulated history helps search" mechanism already flipped from
  SUPPORTED to NO_EFFECT once under a substrate change even within closely
  related program-execution ecologies (RM vs stack-VM), which is a closer
  analogy than a fresh guess would have supported.
- C-aba202675bd8 (D6-A: relational-history-as-derived-causal-signal not
  confirmed, +0.010pp vs a ≥+0.20 requirement, p=0.4875) reinforced setting
  the falsifier floor conservatively (+3pp, not something more optimistic)
  and predicting that any surviving effect traces mostly to generic
  diversity injection rather than ecology-matched content.
- C-6c7e06892e46 (identity-level library composition carries no recoverable
  policy signature; Jaccard divergence indistinguishable between- vs
  within-policy) ruled out "compare library fingerprints across runs" as a
  confound defense and confirmed the G9 shuffled/random ablation is the
  correct (and only) discriminating design here.
- roles/Ludus/REVIEW_PACKET_4_2026-09-01_arena.md supplied PIG as the actual
  pilot substrate (its hold-or-bank structure is explicitly flagged as
  r0003-shaped) and its F2 finding (an oracle that sees privileged state is
  not a valid comparator) is carried into this design's Controls section.

## Unresolved uncertainty
- The Family A vs Family B program-abstraction-library decision (Lexis's
  call, still open per roles/Lexis/ROLE.md:313) is not resolved. If it
  resolves toward Family A, stitch_core could in principle mine reusable
  abstractions from a program corpus and might eventually bridge D-5's real
  genotypes toward a Ludus-native library builder — this design does not
  wait for that and treats it as a possible future arm, not a dependency.
- Whether a PIG-only pilot generalizes to the rest of the arena is open by
  the arena's own admission: its proposed interface already broke on 3/5
  worlds once (F1), so a PIG result — positive or null — may not transfer to
  RPS/Kuhn/negotiation-shaped worlds without a separate test.
- Whether 24–30 tasks give adequate power is itself uncertain: D-5's own
  floor clearance at n=42 was knife-edge (0.95pp over SE 3.4pp), so a smaller
  PIG battery could fail to detect even a real but modest effect, and this
  design does not currently include a formal power calculation for PIG's
  outcome variance.

## Evidence Wiki consultation log (queries + object ids retrieved)
1. search_evidence("D-5 executable artifact library findability transfer
   alien", k=5) → C-2fa98cdd22b5, C-162e315bd67f, C-aba202675bd8,
   C-6c7e06892e46, C-cd8ef5fb0a65
2. get_counterevidence("C-2fa98cdd22b5") → no counter_relations, no
   negative_evidence recorded against the core D-5 content-effect claim
   itself (the relevant negative evidence instead showed up as a
   substrate-level contradiction, not direct counterevidence — see below)
3. contradictions() → R-e68c9331eca2 (C-3a1c49fa5a78 D-8 NO_EFFECT
   CONTRADICTS C-3d12c440f087 D-5 SUPPORTED, APPARENT_UNDER_DIFFERING_
   CONDITIONS); R-2dc413ddca43 (C-1d99d0adac44 FAILS_TO_REPLICATE
   C-7d559fe50c7a, not used — different topic, not opened further)
4. get_claim("C-3d12c440f087") → D-5's +10.95pp claim, restated with
   claim_ceiling detail (floor clearance <1 SE, disclosed)
5. get_claim("C-aba202675bd8") → D6-A null detail (+0.010, p=0.4875 vs
   ≥+0.20 requirement; ENDOGENOUS_SIGNAL_FOUND but NOT CAUSAL)

## Evidence that changed this design (ids -> concrete decision; 'retrieved but did not affect design' is valid)
- C-162e315bd67f -> confirmed (independently of the repo-side donor_d5_compat
  read) that D-5's slot has no primitive-extension site; hardened the
  decision to forbid literal genotype transplant and require a Ludus-native
  re-instantiation instead.
- R-e68c9331eca2 / C-3a1c49fa5a78 (D-8 NO_EFFECT) -> lowered the point
  prediction from +10.95pp to ≈+4pp and made the G9 three-way ablation
  (falsifiers #3-#5) mandatory, not optional.
- C-aba202675bd8 (D6-A null) -> set the falsifier floor at +3pp rather than a
  more optimistic threshold, and grounded the prediction that any surviving
  effect is mostly generic diversity injection.
- C-6c7e06892e46 -> ruled out cross-run library-fingerprint comparison as a
  confound defense; retrieved but redirected a defense, did not change the
  headline prediction.
- C-2fa98cdd22b5 -> retrieved as the canonical restatement of the VERDICT.md
  numbers already read from the repo; did not by itself change the design
  beyond confirming the repo reading was accurate.
- C-cd8ef5fb0a65 (emitted-vs-external findability gap) -> retrieved but did
  not affect this design; it concerns D-5's own internal task construction,
  not the transplant question.

## Operation log (numbered; ops used / 15, documents opened / 12)
1. Grep "findability" over F:\Prometheus (files_with_matches) — repo search
2. Grep "Ludus" over F:\Prometheus, *.md (files_with_matches) — repo search
3. Read F:\Prometheus\agent_d5_blind\VERDICT.md — document opened (1)
4. Read F:\Prometheus\techne\DONOR_INVENTORY.md — document opened (2)
5. Read F:\Prometheus\techne\donor_d5_compat_2026-08-31.json — document opened (3)
6. Read F:\Prometheus\roles\Ludus\REVIEW_PACKET_4_2026-09-01_arena.md — document opened (4)
7. ew.search_evidence(...) — wiki call
8. ew.get_counterevidence("C-2fa98cdd22b5") — wiki call (negative-evidence query)
9. ew.contradictions() — wiki call
10. ew.get_claim("C-3d12c440f087") — wiki call, document opened (5)
11. ew.get_claim("C-aba202675bd8") — wiki call, document opened (6)
12. Grep "Family A|Family B|stitch|Ruler" in F:\Prometheus\roles\Lexis\ROLE.md — document opened (7)

Ops used: 12 / 15. Documents opened: 7 / 12. Early stop: consultation
minimum (search_evidence, negative-evidence query, contradictions()) was met
at ops 7-9; stopped at 12 once the design decisions were all traceable to
specific retrieved evidence, with 3 ops and 5 documents held in reserve
unused.
