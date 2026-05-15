# Charon BACKLOG — Atlas Continuous Attack Roadmap

**Filed:** 2026-05-15
**Author:** Charon (revival session)
**Companion to:** `pivot/atlas_continuous_attack_roadmap_2026-05-15.md`, `roles/Charon/CHARTER.md`, `roles/Charon/RESPONSIBILITIES.md`
**Cron slot:** :07 (offset from Techne :17, Harmonia :37, Ergon :47, Aporia :57)

---

## Posture (read first)

- **v10 battery FROZEN.** 25 tests across 4 tiers (A Detection F1-F14, B Robustness F15-F18, C Representation F19-F23, D Magnitude F24/F24b). No new tests under battery freeze. Gaps surface as P2-medium tickets to Aporia; never as v11 escalation without a dialogue ticket.
- **Specialization:** number-theoretic / arithmetic problem attack via the v10 battery, biased toward EXACTNESS_BARRIER and REPRESENTATION_GAP hardness types.
- **Per-attempt output discipline:** every attack emits at least one substrate block. Default shape: `kill_ledger` entry with rich KillVector metadata. Conditional: `anti_anchor` candidate when the attack reveals a clipped-qualifier or boundary-condition failure that a downstream LLM would reproduce. Rare: `primitive_proposal` when a novel attack vector survives ablation.
- **Hard stops:** v11 expansion / kernel contract change / `--writeable` upgrade / multiprocessing scaling / LoRA work → STOP and file a ticket asking.
- **Schemas:** anti_anchor / primitive_proposal / catalog_edit follow `aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md` §2.1 / 2.6. Use `AA-XXX` placeholder ids; ingest assigns canonical AA-NNN at register time.
- **HARD-2 vigilance:** every backlog item must trace to a behavior delta. If I find myself producing scaffolding instead of attacks, that's the gravitational-well failure mode — file a ticket and re-orient.
- **HARD-5 vigilance:** distinct coordinates stay distinct. Rank / rank-bar / symmetric-rank / cactus-rank / border-rank are five separate primitives, not one. Same discipline on every attack: if the attack collapses two coordinates, the kill_ledger entry names which two and why.

---

## Item schema

Each backlog item below carries:

- `id` — `BL-C-NNN` numbered sequentially within Charon's backlog
- `phase` — 0 / 1 / 2 / 3 per roadmap §4
- `title` — problem name + attack vector
- `hardness_signature` — EXACTNESS_BARRIER / REPRESENTATION_GAP / METHOD_GAP / COUPLED_DIFFICULTY / CONCEPTUAL_ABSENCE (used by Aporia's hardness-signature-driven assignment lever)
- `dependencies` — upstream items (other BL-C-NNN or external substrate prerequisites)
- `effort_per_attempt` — rough hours (S = ≤2h, M = 2-6h, L = 6-12h, XL = multi-day)
- `attack_vector` — which v10 battery tiers/tests apply
- `substrate_block_emission` — expected block shape(s) per attempt
- `notes` — caveats, anti-gravitational-well flags, kill-history pointers

---

## Phase 0 — Revival + first 10 number-theoretic attacks (Weeks 1-4)

Aporia files `aporia/meta/problem_queue/charon.jsonl` with priority-ordered seed candidates. Items below are Charon's pre-pull preparation: domain framing, attack-vector hypothesis, and expected substrate-block shape. The queue is the source of truth on assignment; this section is the "I am prepared to attack X when X lands in the queue" inventory.

### BL-C-001 — Lehmer's conjecture continuation

- **phase:** 0
- **hardness_signature:** EXACTNESS_BARRIER (exact infimum of Mahler measure over monic integer polynomials with M > 1)
- **dependencies:** existing Lehmer negative-space tensor at `charon/lehmer_negative_space_tensor.json`; Dubickas-Smyth bounds literature
- **effort_per_attempt:** M (4-6h: polynomial-family generation + battery run + KillVector emission)
- **attack_vector:** v10 Tier A (F1-F14 detection on random polynomial families seeded near Lehmer's polynomial M ≈ 1.1762); Tier C representation-stress (F19-F23) on Mahler vs height vs trace coordinates; Tier D magnitude (F24/F24b) against the conditional Smyth lower bound
- **substrate_block_emission:** kill_ledger (every attempt); anti_anchor candidate when family search hits a boundary-condition failure (e.g. degree-vs-coefficient-bound clipping that LLMs typically misstate); primitive_proposal if a novel polynomial-family generator survives ablation
- **notes:** This is an EXACTNESS_BARRIER classic. The negative-space tensor already accumulates kill geometry; revival continues the same loop. Watch for the LLM-narrative trap of "Lehmer is close to being settled" — Dubickas-Smyth bounds are real, but the conjecture is not within striking distance.

### BL-C-002 — BSD rank distribution at higher conductor

- **phase:** 0
- **hardness_signature:** REPRESENTATION_GAP (analytic rank vs Mordell-Weil rank; Bhargava-Shankar moment averages vs individual-curve predictions)
- **dependencies:** LMFDB elliptic curve dataset (devmirror.lmfdb.xyz); existing rank statistics from `cartography/v2/`
- **effort_per_attempt:** L (6-12h: dataset slicing at conductor > 10^7 + Tier A/D battery + KillVector emission)
- **attack_vector:** v10 Tier A (F1-F14) on rank-vs-conductor distributions at progressively higher conductor; Tier D (F24/F24b) magnitude probe on the 50/50 rank-0/rank-1 split prediction; Tier C representation-stress on analytic-rank vs Mordell-Weil-rank coordinates (HARD-5: never collapse these)
- **substrate_block_emission:** kill_ledger (every attempt); anti_anchor candidate when canonical-LLM emission would say "BSD rank distribution is 50/50 above conductor N" without conditioning on isogeny class / family (this is a known boundary-condition failure)
- **notes:** "50/50 rank-0/rank-1" is the modal LLM emission; the truth is more nuanced (Goldfeld conjecture, density vs rank). Watch for HARD-5 collapse of analytic-rank into rank-via-BSD.

### BL-C-003 — Mahler measure spectrum gaps

- **phase:** 0
- **hardness_signature:** EXACTNESS_BARRIER (gaps in the spectrum of M(α) over algebraic integers α)
- **dependencies:** BL-C-001 (shares the polynomial-family generator); Boyd's tables of small Mahler measures
- **effort_per_attempt:** M (4-6h)
- **attack_vector:** v10 Tier A (F1-F14) on gap-detection in the spectrum below threshold T; Tier B robustness (F15-F18) to confirm gaps are not detection artifacts; Tier C representation on whether gap structure depends on degree, signature, or Galois group
- **substrate_block_emission:** kill_ledger; anti_anchor candidate when LLM emission claims a gap that has been filled by recent computation (Boyd / Mossinghoff continuations); primitive_proposal if a new gap-detection statistic survives ablation
- **notes:** Adjacent to BL-C-001 but the question is about the SPECTRUM, not the infimum. Keep these coordinates distinct.

### BL-C-004 — Schinzel-Zassenhaus follow-on (post-Dimitrov)

- **phase:** 0
- **hardness_signature:** EXACTNESS_BARRIER (exact decay rate of max |root| - 1 for monic integer polynomials with no root on unit circle)
- **dependencies:** Dimitrov 2019 (arXiv:1912.12545); follow-on literature
- **effort_per_attempt:** S (≤2h: literature is well-mapped, attack is targeted)
- **attack_vector:** v10 Tier A (F1-F14) on whether Dimitrov's 1/(4 deg) bound is tight; Tier C representation-stress on degree vs signature vs coefficient bound coordinates
- **substrate_block_emission:** anti_anchor candidate is the EXPECTED primary emission: "Schinzel-Zassenhaus is open" is the LLM modal emission; the conjecture proper was settled by Dimitrov 2019. False-form: "Schinzel-Zassenhaus is open." True-form must name Dimitrov 2019, the 1/(4 deg) bound, and the open follow-on questions (tightness of constant, which polynomials achieve the bound)
- **notes:** This is one of the cleanest first-week wins. The conjecture-vs-open-question confusion is exactly the kind of LLM error the substrate's anti_anchor registry is designed to pin down. Likely AA-XXX promotion-eligible.

### BL-C-005 — abc conjecture status (post-Mochizuki controversy)

- **phase:** 0
- **hardness_signature:** REPRESENTATION_GAP (rad(abc) vs quality q(a,b,c) representations) + METHOD_GAP (IUT not accepted)
- **dependencies:** Mochizuki IUT status; explicit unconditional bounds (Stewart-Yu)
- **effort_per_attempt:** M (4-6h)
- **attack_vector:** v10 Tier A on the unconditional Stewart-Yu bound vs the conjectured bound; Tier C representation-stress on rad / q / log forms of the conjecture
- **substrate_block_emission:** anti_anchor candidate primary: "abc was proved by Mochizuki" is a known LLM error. True-form must name IUT non-acceptance state, Stewart-Yu unconditional bound, and the distinction between strong-abc and weak-abc
- **notes:** Highly contentious territory. Stay clinical — the substrate's job is to record the kill geometry, not to take a stance on IUT. The TRUE state is "Mochizuki claims IUT proves abc; the broader mathematical community has not accepted the proof; Stewart-Yu unconditional bounds are accepted."

### BL-C-006 — Beal's conjecture (Tijdeman-Zagier follow-on)

- **phase:** 0
- **hardness_signature:** EXACTNESS_BARRIER (exact form of "common factor" condition for A^x + B^y = C^z with x,y,z ≥ 3)
- **dependencies:** computational verification status (current ~10^9 upper bound on solutions); Frey-curve adjacent literature
- **effort_per_attempt:** M
- **attack_vector:** v10 Tier A on small-exponent classification; Tier B robustness on parametric family searches; Tier C representation-stress on Beal vs Tijdeman-Zagier formulations (these are NOT identical — HARD-5)
- **substrate_block_emission:** kill_ledger; anti_anchor candidate when LLM conflates Beal with Fermat or with Tijdeman-Zagier
- **notes:** Adjacent to FLT but distinct. Watch for collapse-to-FLT in LLM emission.

### BL-C-007 — Catalan-Mihailescu adjacent (Pillai's conjecture)

- **phase:** 0
- **hardness_signature:** EXACTNESS_BARRIER (gaps in the sequence of perfect powers; Pillai's conjecture about |a^x - b^y| > c(epsilon) * max(a^x, b^y)^(1-epsilon))
- **dependencies:** Mihailescu 2002 (Catalan settled); current Pillai computational bounds
- **effort_per_attempt:** S
- **attack_vector:** v10 Tier A on perfect-power gap detection; Tier C representation-stress on Pillai vs Catalan vs generalized-Catalan (Tijdeman) coordinates
- **substrate_block_emission:** anti_anchor candidate is primary: "Catalan's conjecture is open" is a known LLM error (Mihailescu 2002 settled it unconditionally). True-form: Mihailescu 2002 proof + remaining Pillai's conjecture open
- **notes:** Companion to BL-C-004 (Schinzel-Zassenhaus) — both are conjectures-recently-settled with adjacent open follow-ons that LLMs misclassify.

### BL-C-008 — Vinogradov mean value adjacent (post-Wooley / BDG)

- **phase:** 0
- **hardness_signature:** REPRESENTATION_GAP (l-adic vs p-adic vs real Vinogradov; exact constants)
- **dependencies:** Wooley efficient congruencing (2016); Bourgain-Demeter-Guth decoupling (2016)
- **effort_per_attempt:** M
- **attack_vector:** v10 Tier A on the Wooley/BDG main conjecture statement vs open follow-on questions; Tier C representation-stress on exact-constant variants
- **substrate_block_emission:** anti_anchor candidate primary: "Vinogradov mean value is open" is now wrong (Wooley + BDG settled main conjecture in 2016). True-form: settled main conjecture + open variants (exact constants, l-adic analogues, p-adic versions)
- **notes:** Another "recently-settled-LLM-thinks-it-is-still-open" pattern.

### BL-C-009 — Goldbach exceptional set bound

- **phase:** 0
- **hardness_signature:** EXACTNESS_BARRIER (exact exponent θ in #{N ≤ X : N not Goldbach} = O(X^θ))
- **dependencies:** Pintz current best bound; Helfgott ternary Goldbach (separate problem)
- **effort_per_attempt:** M
- **attack_vector:** v10 Tier A on the current θ bound (Pintz: θ < 0.72); Tier C representation-stress on binary-Goldbach vs ternary-Goldbach (HARD-5: these are different conjectures with different states)
- **substrate_block_emission:** anti_anchor candidate when LLM conflates binary and ternary Goldbach (ternary settled by Helfgott 2013; binary remains open with exceptional-set bounds)
- **notes:** The binary-vs-ternary collapse is a classic LLM error. Pin both states explicitly.

### BL-C-010 — Twin prime gaps (post-Zhang-Maynard-Tao)

- **phase:** 0
- **hardness_signature:** EXACTNESS_BARRIER (gap H such that infinitely many p with p_{n+1} - p_n ≤ H; current H = 246 by Polymath 8b)
- **dependencies:** Zhang 2013 + Maynard 2013 + Polymath 8 / 8b
- **effort_per_attempt:** S
- **attack_vector:** v10 Tier A on the exact-H state; Tier C representation-stress on bounded-gaps vs twin-primes vs Hardy-Littlewood-k-tuples (three distinct problems — HARD-5)
- **substrate_block_emission:** anti_anchor candidate primary: "Zhang proved twin primes" is the modal LLM error. True-form: Zhang proved bounded gaps (H ≤ 70 million originally, now H ≤ 246), NOT twin primes (H = 2); twin prime conjecture proper remains open
- **notes:** One of the most common conjecture-vs-result confusions in LLM emissions. High anti_anchor yield expected.

### BL-C-011 — Daily cron at :07 establishment

- **phase:** 0
- **hardness_signature:** N/A (infrastructure)
- **dependencies:** existing Aporia cron-scheduling protocol; `pivot/atlas_continuous_attack_roadmap_2026-05-15.md` §7
- **effort_per_attempt:** S (one-shot setup)
- **attack_vector:** N/A
- **substrate_block_emission:** N/A (this is infrastructure, not an attack)
- **notes:** Per the roadmap, Charon at :07 (offset from Techne :17, Harmonia :37, Ergon :47, Aporia :57 to avoid contention). Cron fires the daily attack-pull cycle: read `aporia/meta/problem_queue/charon.jsonl`; pick top priority item; run battery; emit substrate blocks; file attack-summary ticket to `aporia/meta/queue/aporia_inbox.jsonl`. Awaiting James confirmation on cron setup mechanism (CronCreate tool vs OS-level cron).

### BL-C-012 — Daily attack-summary ticket protocol

- **phase:** 0
- **hardness_signature:** N/A (infrastructure)
- **dependencies:** BL-C-011 cron
- **effort_per_attempt:** S (auto-generated; one file write per fire)
- **attack_vector:** N/A
- **substrate_block_emission:** JSONL ticket to `aporia/meta/queue/aporia_inbox.jsonl` per attack day
- **notes:** Ticket format per the revival prompt: `{id, source: "charon", target: "aporia", type: "daily-attack-summary", priority: "P3-low", payload: {date, problems_attempted, substrate_blocks_emitted, near_misses, anti_anchor_candidates}}`. Aporia coordinates cross-agent flow without per-attempt micromanagement.

---

## Phase 1 — Steady-state attack loop expansion (Weeks 5-12)

Target: 50+ attempts/month, ~5-10 anti_anchor candidates/month surfaced. Per-domain attack-vector library updates as each domain reaches saturation.

### BL-C-013 — Sato-Tate variants (higher symmetric powers)

- **phase:** 1
- **hardness_signature:** REPRESENTATION_GAP (Sato-Tate for sym^k for k > 4; genus-2 Sato-Tate)
- **dependencies:** Newton-Thorne 2021 sym^k for all k (settled non-CM elliptic curves); Fité-Kedlaya-Rotger-Sutherland genus-2 Sato-Tate groups
- **effort_per_attempt:** M
- **attack_vector:** v10 Tier A on sym^k angle distributions; Tier C representation-stress on elliptic vs genus-2 vs higher-genus Sato-Tate (each is a distinct coordinate)
- **substrate_block_emission:** kill_ledger; anti_anchor when LLM conflates "Sato-Tate proved" (true for non-CM elliptic) with "Sato-Tate proved for all symmetric powers" (now true post-Newton-Thorne) with "Sato-Tate proved for higher genus" (false — only 52 Sato-Tate groups identified for genus 2)
- **notes:** Three distinct conjectures with three distinct states. HARD-5 minefield.

### BL-C-014 — Modular form coefficient growth (Lehmer's tau conjecture)

- **phase:** 1
- **hardness_signature:** EXACTNESS_BARRIER (does τ(p) ≠ 0 for all primes p? Ramanujan tau function non-vanishing)
- **dependencies:** computational verification status (current ~10^15 bound on p with τ(p) ≠ 0 verified); Deligne bound proven
- **effort_per_attempt:** M
- **attack_vector:** v10 Tier A on small-prime non-vanishing search; Tier C representation-stress on tau vs general modular coefficient vs Hecke eigenvalue coordinates
- **substrate_block_emission:** kill_ledger; anti_anchor when LLM conflates "Lehmer's conjecture for tau" (this) with "Lehmer's conjecture for Mahler measure" (BL-C-001; entirely different conjecture)
- **notes:** Two Lehmer conjectures — this one (tau function) and BL-C-001 (Mahler measure) — are completely unrelated. High HARD-5 collision risk.

### BL-C-015 — Riemann zero pair correlation (Montgomery's conjecture)

- **phase:** 1
- **hardness_signature:** REPRESENTATION_GAP (zeros-of-zeta as eigenvalues-of-random-matrix; GUE statistics)
- **dependencies:** Montgomery 1973 conjecture; Odlyzko computational verification (50 trillion zeros computed); Katz-Sarnak conjectures
- **effort_per_attempt:** L (zero-spacing data is substantial)
- **attack_vector:** v10 Tier A on local pair-correlation vs GUE prediction at small scale; Tier C representation-stress on zero-spacing-statistic representations (sin^2(πx)/(πx)^2 vs naive uniform vs random-matrix)
- **substrate_block_emission:** kill_ledger; primitive_proposal candidate if a new pair-correlation statistic survives ablation; anti_anchor when LLM emission conflates "GUE statistics match" (empirical) with "Montgomery's conjecture proven" (still conjectural)
- **notes:** Empirical match is very strong (Odlyzko); theoretical proof is not in sight. The conjecture itself is conditional on RH for the pair-correlation statement, which makes the state extra-confusing for LLMs.

### BL-C-016 — Erdős-Straus conjecture computational frontier

- **phase:** 1
- **hardness_signature:** EXACTNESS_BARRIER (4/n = 1/a + 1/b + 1/c for all n ≥ 2)
- **dependencies:** current computational verification (Salez 2014: ≤ 10^14)
- **effort_per_attempt:** S
- **attack_vector:** v10 Tier A on residue-class obstruction patterns; Tier C representation-stress on Erdős-Straus vs Sierpiński (5/n) vs Schinzel general (k/n)
- **substrate_block_emission:** kill_ledger; anti_anchor when LLM emission collapses Erdős-Straus to general unit-fraction representation
- **notes:** Likely modest yield; problem is heavily computer-verified and unlikely to fall to substrate attacks. Useful for breadth-of-coverage and HARD-5 discipline.

### BL-C-017 — Mertens function bounds

- **phase:** 1
- **hardness_signature:** REPRESENTATION_GAP (Mertens conjecture disproved 1985; current bounds on M(x))
- **dependencies:** Odlyzko-te Riele 1985 disproof; current upper bounds on |M(x)|
- **effort_per_attempt:** M
- **attack_vector:** v10 Tier A on |M(x)| growth rate; Tier C representation-stress on Mertens vs Riemann hypothesis equivalences (HARD-5: Mertens conjecture is disproved but RH-equivalent bounds remain)
- **substrate_block_emission:** anti_anchor candidate primary: "Mertens conjecture is open" is the modal LLM error (Odlyzko-te Riele 1985 disproved it). True-form: Mertens conjecture disproved (counterexample at x ~ 10^14); weaker M(x) = O(sqrt(x)) bound is equivalent to RH
- **notes:** Another recently-disproved-LLM-still-thinks-open pattern.

### BL-C-018 — Heilbronn triangle problem (post-Cohn-Drmota-Steiner)

- **phase:** 1
- **hardness_signature:** EXACTNESS_BARRIER (exact constant in H(n) = min over n points of max-area triangle)
- **dependencies:** Cohn-Drmota-Steiner 2024 improvement on Komlós-Pintz-Szemerédi
- **effort_per_attempt:** M
- **attack_vector:** v10 Tier A on point-configuration optimization; Tier D magnitude probe on the Cohn-Drmota-Steiner constant
- **substrate_block_emission:** kill_ledger; anti_anchor when LLM emission cites pre-2024 bounds as current
- **notes:** Cohn-Drmota-Steiner is recent (2024); LLM emissions trained on older data will miss it. High anti_anchor yield expected.

### BL-C-019 — Per-domain attack-vector library update: elliptic curves

- **phase:** 1
- **hardness_signature:** META (library maintenance)
- **dependencies:** accumulated kill_ledger entries from BL-C-002 + BL-C-013 + adjacent EC work
- **effort_per_attempt:** L (consolidate ~10-15 attack vectors into one library doc per domain)
- **attack_vector:** N/A (meta)
- **substrate_block_emission:** primitive_proposal candidates if novel attack vectors survive ablation across multiple problems
- **notes:** Weekly cadence per the roadmap. Output: `charon/attack_vectors/elliptic_curves.md` (new file). Captures what worked, what didn't, what HARD-5 collisions surfaced.

### BL-C-020 — Per-domain attack-vector library update: modular forms

- **phase:** 1
- **hardness_signature:** META
- **dependencies:** kill_ledger from BL-C-014 + adjacent MF work
- **effort_per_attempt:** L
- **attack_vector:** N/A
- **substrate_block_emission:** primitive_proposal candidates
- **notes:** `charon/attack_vectors/modular_forms.md` (new file).

### BL-C-021 — Per-domain attack-vector library update: prime gaps

- **phase:** 1
- **hardness_signature:** META
- **dependencies:** kill_ledger from BL-C-009 + BL-C-010 + BL-C-016 + adjacent
- **effort_per_attempt:** L
- **attack_vector:** N/A
- **substrate_block_emission:** primitive_proposal candidates
- **notes:** `charon/attack_vectors/prime_gaps.md` (new file).

### BL-C-022 — Per-domain attack-vector library update: Mahler measure / polynomial heights

- **phase:** 1
- **hardness_signature:** META
- **dependencies:** kill_ledger from BL-C-001 + BL-C-003 + BL-C-004 + BL-C-014 (tau)
- **effort_per_attempt:** L
- **attack_vector:** N/A
- **substrate_block_emission:** primitive_proposal candidates
- **notes:** `charon/attack_vectors/mahler_heights.md` (new file). Critical HARD-5 discipline doc since multiple Lehmer / Schinzel / Smyth conjectures share names but not coordinates.

### BL-C-023 — Weekly attack-summary roll-up to Aporia

- **phase:** 1
- **hardness_signature:** META (coordination)
- **dependencies:** BL-C-012 daily tickets
- **effort_per_attempt:** S (one ticket per week)
- **attack_vector:** N/A
- **substrate_block_emission:** JSONL ticket to `aporia/meta/queue/aporia_inbox.jsonl`, type=`weekly-attack-summary`
- **notes:** Aggregates daily tickets into weekly rollup. Aporia uses for cross-agent ticket-flow coordination.

---

## Phase 2 — Arena MVP support + continued steady-state (Weeks 13-18)

Target: continue ~50+ attempts/month + supply Forger-role expertise to first Arena rounds when problems land in arithmetic territory.

### BL-C-024 — Arena Forger-role specialization spec

- **phase:** 2
- **hardness_signature:** META (Arena protocol)
- **dependencies:** Aporia's `aporia/doctrine/arena_protocol.md` (not yet authored; Phase 2 deliverable)
- **effort_per_attempt:** M (one-shot spec authoring)
- **attack_vector:** N/A
- **substrate_block_emission:** N/A (doc artifact)
- **notes:** Charon supplies Forger-role: given a problem, generate aggressive attack proposals that the Skeptic role then tests. Spec authored in coordination with Aporia.

### BL-C-025 — Arena round participation: first arithmetic problem

- **phase:** 2
- **hardness_signature:** depends on assigned problem
- **dependencies:** BL-C-024 + Aporia's first 2-team-of-3 round trigger
- **effort_per_attempt:** XL (weekend-scale Arena round)
- **attack_vector:** full v10 battery + cross-team adversarial verification
- **substrate_block_emission:** kill_ledger entries (multiple); anti_anchor candidates (multiple); primitive_proposal if a novel attack vector emerges from team interplay
- **notes:** First-Arena-round commitment. Heavy lift; coordinate with Aporia on timing.

### BL-C-026 — BSD higher-rank curves systematic attack

- **phase:** 2
- **hardness_signature:** EXACTNESS_BARRIER + REPRESENTATION_GAP (rank ≥ 4 elliptic curves over Q; current record rank 28)
- **dependencies:** BL-C-002 + Elkies records
- **effort_per_attempt:** L
- **attack_vector:** v10 Tier A on rank-frequency at rank ≥ 4; Tier C representation-stress on rank-distribution coordinates
- **substrate_block_emission:** kill_ledger; anti_anchor when LLM emission confuses "rank distribution" with "rank record"
- **notes:** Distinct from BL-C-002 (which is about rank-0/rank-1 split); this is about high-rank tail.

### BL-C-027 — Galois representations / Serre's conjecture adjacent

- **phase:** 2
- **hardness_signature:** REPRESENTATION_GAP
- **dependencies:** Khare-Wintenberger 2009 (Serre's conjecture settled); Fontaine-Mazur conjecture (open)
- **effort_per_attempt:** L
- **attack_vector:** v10 Tier C representation-stress (highly applicable — domain is literally about representations); Tier A on modularity-vs-non-modularity boundary
- **substrate_block_emission:** kill_ledger; anti_anchor when LLM conflates Serre (settled) with Fontaine-Mazur (open)
- **notes:** Another "recently-settled-LLM-still-thinks-open" pattern at higher technical complexity.

---

## Phase 3 — Steady-state + deep per-domain specialization (Months 5-8)

Target: per-domain attack vector libraries deepen; specialization stabilizes; ~50+ attempts/month sustained; ~5-10 anti_anchor candidates/month.

### BL-C-028 — Per-domain attack-vector library: BSD / elliptic curves (v2)

- **phase:** 3
- **hardness_signature:** META
- **dependencies:** BL-C-019 (v1) + Phase 1+2 kill_ledger accumulation
- **effort_per_attempt:** L
- **attack_vector:** N/A
- **substrate_block_emission:** primitive_proposal candidates (multiple); refinements to existing primitives
- **notes:** Second-pass library update. Phase 3 is where the libraries stabilize as the canonical reference for arithmetic attacks.

### BL-C-029 — Per-domain attack-vector library: Mahler / polynomial heights (v2)

- **phase:** 3
- **hardness_signature:** META
- **dependencies:** BL-C-022 (v1) + Phase 1+2 kill_ledger accumulation
- **effort_per_attempt:** L
- **attack_vector:** N/A
- **substrate_block_emission:** primitive_proposal candidates
- **notes:** Second-pass library update.

### BL-C-030 — Tier-add proposal candidates (NOT v11)

- **phase:** 3
- **hardness_signature:** META (substrate evolution)
- **dependencies:** accumulated v10 gap-tickets to Aporia from Phases 0-2; Aporia adjudication
- **effort_per_attempt:** XL (cross-agent dialogue; multi-day)
- **attack_vector:** N/A
- **substrate_block_emission:** P2-medium tickets to Aporia per gap; dialogue tickets if a v11 review is genuinely warranted
- **notes:** Battery freeze persists by default. This item is a placeholder for the cross-agent dialogue ticket Aporia would need to author before any v10-to-v11 conversation. STAY UNDER FREEZE unless the dialogue is explicitly opened.

### BL-C-031 — Phase boundary review participation (Phase 3 → 4)

- **phase:** 3
- **hardness_signature:** META (roadmap review)
- **dependencies:** roadmap phase-boundary review trigger (end of month 8)
- **effort_per_attempt:** M (review doc authoring)
- **attack_vector:** N/A
- **substrate_block_emission:** session-review doc; Charon's input to Aporia's phase-review ticket
- **notes:** Per roadmap §10, phase boundaries are review points. Charon contributes: what landed, what slipped, anti_anchor yield vs target, any v10 gaps surfaced.

---

## Standing flags

- **HARD-2 risk on this backlog itself.** 31 items × phase clustering × structured schema is exactly the kind of artifact that produces "we have a plan, we're making progress" without behavior delta. The discipline: BL-C-001 through BL-C-010 must produce 5+ substrate blocks each by end of Phase 0, or the backlog itself is the wrong shape and gets re-authored.
- **HARD-5 minefields concentrated.** This backlog is dense with HARD-5 collisions: Lehmer (tau) vs Lehmer (Mahler); Schinzel-Zassenhaus vs Schinzel (general); Catalan vs Tijdeman-Zagier vs Pillai; Sato-Tate (EC) vs Sato-Tate (sym^k) vs Sato-Tate (genus-2); binary vs ternary Goldbach; bounded gaps vs twin primes vs Hardy-Littlewood k-tuples; Mertens conjecture vs M(x) = O(sqrt x). Per HARD-5 discipline every kill_ledger entry names which coordinates are stressed.
- **Verify-upstream-attributions before promotion.** Per `feedback_verify_upstream_attributions.md`: internal Aporia/Techne catalogs are themselves Tier-2-or-worse anchors. Before any anti_anchor candidate gets promoted to v1.0 corpus seed, citation must pin to primary literature (arXiv ID or DOI matching the regex in SUBSTRATE_SHAPED_PROMPTS §2.1).
- **Adversarial axes against canonicality.** Per `feedback_adversarial_axes_against_canonicality.md`: canonicality_in_pretraining > era > specificity hypothesis must beat alternative predictors (lexical rarity, citation-form familiarity, object arity) before any "X is recoverable" claim becomes substrate law.
- **No multiprocessing scaling.** Per the revival prompt's hard stop. If the v10 battery becomes too slow on Phase 1+ volume, surface as a P2 ticket to Aporia, not as a unilateral parallelization change.
- **No LoRA work.** Per hard stop. If a result looks LoRA-relevant, file a ticket to Ergon; Charon stays in attack-mode.

---

## Open questions for James / Aporia

1. **Cron mechanism.** CronCreate tool (in-harness) vs OS-level Windows Task Scheduler vs Aporia-mediated cron? The :07 slot is reserved; the activation mechanism is not specified.
2. **Problem queue file format.** `aporia/meta/problem_queue/charon.jsonl` — schema needed. Suggested fields: `id`, `priority`, `problem_name`, `hardness_signature`, `dependencies`, `seed_attack_vector`, `target_substrate_block_shape`, `assigned_date`, `due_date_optional`. Aporia files; Charon pulls.
3. **Substrate-block emission path.** Per SUBSTRATE_SHAPED_PROMPTS the schemas are designed for Gemini Deep Research returns + Aporia-mediated ingestion. Charon attack outputs are not Gemini-mediated. Does Charon emit blocks directly to `aporia/docs/staged_substrate_blocks/<DATE>/<type>.jsonl` (bypassing Gemini) or via Aporia inbox tickets that Aporia stages? Defer until BL-C-001 first attempt; surface specific case to Aporia then.
4. **kill_ledger location and format.** Current Charon kill_ledger lives partially in `charon/lehmer_negative_space_tensor.json` and partially in `cartography/v2/` outputs. Roadmap implies a canonical `techne/registry/kill_ledger.jsonl` or similar. Confirm location before Phase 0 attacks begin emitting blocks.
5. **BL-C-011 cron prompt content.** What does the :07 fire prompt say? Likely shape: read queue → pick top item → run battery → emit blocks → file daily-summary ticket → stand down. Awaiting Aporia's canonical cron prompt format (parallel to her own loop-state files).

These five questions gate Phase 0 execution. Once answered, BL-C-001 attempts can begin.

---

## Closing posture

The battery is the tool. The roadmap is the assignment. The substrate-block emission is the output discipline.

Most cargo doesn't come back. The crossings that do are real. The drownings that don't are data. The instrument that judges crossings is data.

— Charon, 2026-05-15
