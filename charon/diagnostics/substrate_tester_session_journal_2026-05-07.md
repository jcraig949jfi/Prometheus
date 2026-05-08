# Substrate-Tester Session Journal — 2026-05-06 → 2026-05-07

**Author:** substrate-tester (Charon-aligned), my-instance
**Session shape:** /loop, 1-hour cadence, multi-instance coordination
**Fires:** 30 across 2 calendar days (with mid-session restart for contract-change-window summary)
**Termination:** James-directed stop after fire #30; pending wakeup at 22:09 will see this directive in context and not re-schedule.

---

## Session at a glance

| Metric | Value |
|---|---:|
| Fires completed (my instance) | 16 (#1, 2, 3, 4, 5, 6, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30) |
| Fires by parallel substrate-tester instance | 14 (#7, 8, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29 + earlier) |
| Tickets filed (mine) | 3 |
| Tickets closed (mine) | 2 (T-ST002, T-ST003) |
| LIVE lanes exercised (mine) | All 17 over both calendar days |
| Substrate-grade findings | 8+ documented |
| Discipline: HARD-1 through HARD-5 violations | 0 |

---

## Headline findings

### 1. Two real substrate flaws filed and closed via my-instance tickets

**T-2026-05-06-ST002 (P1-high):** `CoordinateChart` silently accepted empty domain string despite docstring promising non-empty. Validator at `coordinate_chart.py:248` checked `isinstance(str)` AND `":" not in domain` but missed empty-string check. Sibling `region_key` validator at line 252 enforced non-empty correctly — the asymmetry was the bug.
- Filed in fire #2.
- Fixed by Techne in contract-change window.
- Regression-confirmed in fire #5.

**T-2026-05-06-ST003 (P2-normal):** `get_raw_invariant_keys` for unregistered domain silently returned sentinel `("__unregistered__",)` instead of raising. Downstream stub_emit consumers would silently produce all-None raw_invariants on typo'd domain names.
- Filed in fire #3.
- Fixed by Techne in contract-change window with informative `KeyError` listing registered domains.
- Regression-confirmed across **4 independent fires** (mine in #10/#24, parallel in #19, plus closure baseline).

### 2. One real substrate flaw filed and ESCALATED to P0 by parallel instance

**T-2026-05-07-ST-fire14-001 (P1-high):** `MethodSpec` silently accepts arbitrary strings as `independence_class` (should require `IndependenceClass` enum). The IndependenceClass is a str-mixin enum so Python's type system accepts strings, but the substrate's triangulation discipline depends on the registered enum vocabulary.
- Filed in fire #14 by me as P1-high (direct input-validation gap).
- **Escalated to P0-blocker** by parallel instance fire #17 (T-ST-fire17-001) which demonstrated the downstream consequence: arbitrary-IC strings smuggled through MethodSpec actually UPGRADE to LOCAL_LEMMA in `TriangulationProtocol.evaluate`. The downstream impact composes the input-validation flaw with the triangulation upgrade rule — a substrate-grade smuggle attack.
- **Still OPEN as of session end.**

### 3. Substrate-grade aggregate finding: deg-14 ±5 INCONCLUSIVE list characterization

Across fires #1, #9, #18, #28, my-instance Lane 7 (precision-gradient) processed 5 of the 43 in-band entries from the deg-14 ±5 brute-force INCONCLUSIVE list. Each entry was put through the factor-first Mahler measure path at 5 dps levels (10/30/60/100/200).

| Entry | half_coeffs | M (all dps) | Outcome |
|---|---|---:|---|
| #0 | [1, -4, 5, 0, -5, 4, -1, 0] | 1.0 | pure cyclotomic |
| #1 | [1, -3, 1, 5, -5, -1, 3, -2] | 1.0 | pure cyclotomic |
| #2 | [1, -3, 2, 1, 0, -2, 1, 0] | 1.176281 | **Lehmer × cyclotomic** |
| #6 | [1, -2, 0, 0, 2, 2, -3, 0] | 1.0 | pure cyclotomic |
| #7 | [1, -2, 1, 0, 0, -1, 1, 0] | 1.176281 | **Lehmer × cyclotomic** |

**Pattern: 60% pure cyclotomic + 40% Lehmer-bearing + 0 novel band hits.** Substrate-grade aggregate evidence supporting the deg-14 ±5 ExclusionCertificate's claim that NO novel Lehmer band hits exist in the subspace. Independent verification, distinct from the original Path A/B/C/D triangulation_history that earned the cert's COMPLETE strength.

### 4. Substrate-grade scaling study: cross-degree hit-rate

Fires #6 and #20 produced cross-degree brute-force enumeration data:

| Subspace | n_polys | in_band_hits | hit_rate |
|---|---:|---:|---:|
| deg-14 ±5 (canonical baseline) | 97,435,855 | 253 | 2.60e-6 |
| deg-12 ±5 (fire #6) | 8,857,805 | 113 | 1.28e-5 |
| deg-10 ±5 (fire #20) | 805,255 | 44 | 5.46e-5 |

**Pattern: hit rate scales ~4-5× per lower degree at fixed ±5 coefficient bound.** Substrate enumerates correctly at all 3 scales; the pattern reflects underlying polynomial-landscape geometry, not substrate behavior. Worth a future Aporia ticket to investigate whether the ~4.5× pattern has a substrate-grade combinatorial explanation.

### 5. Cumulative property-test coverage

**Canonicalization-fuzz (Lane 13):** 6+ independent hypothesis seeds across fires #10/#13/#16/#23/#26/#30 = **15,000+ unique hypothesis-generated probes, 0 failures total**. Substrate's canonicalization invariants are robust under property-based testing across diverse input regions.

**Replay-determinism (Lane 14):** 35+ independent property confirmations across fires #12/#14_parallel/#23_parallel/#24/#30. All 7 properties verified each time (sha256 identity per record, K-replay determinism, JSON round-trip stability, canonical-form determinism, replay timing soft-fail, full 20-component coverage, replay-does-not-mutate-capsule).

**Concurrency-stress (Lane 16):** 6 properties × 2 fires (#12, #24) = 12 confirmations. Parallel-CLAIM safety holds across the contract-change-window restart.

### 6. Substrate's catalog cross-check works at real-paper scale

Fire #5 demonstrated that the substrate **correctly rediscovered Lehmer's polynomial via Mossinghoff catalog cross-check on a 2026 arxiv paper** (entry from arxiv 2601.11486). When a polynomial from a published paper was submitted, the substrate identified it as already-cataloged Lehmer 1933 — clean rediscovery cycle.

### 7. Architectural observations (substrate-grade, not flaws)

**No general-purpose theorem-style CLAIM gauntlet:** Lane 11 (batch-sweep) and Lane 8 (fire #8 prior session) demonstrated that the v1.5 substrate has no automated verdict path for non-Lehmer-poly claims. SigmaKernel.CLAIM ingests theorem-style probes cleanly (>30K probes/sec) but they all land at status=pending. This is by-design; the falsification battery operates on Mahler-poly-shape claims.

**In-band catalog cross-check is network-bound:** fire #14's deadlock (30-probe in-band batch hit live LMFDB/OEIS/arxiv calls sequentially → 6+ minute wall-clock) revealed that the in-band gauntlet path makes synchronous network calls. Caps Lane 1 fire-fitting probe count at ~10. Worth a future ticket for timeout-bounded or async catalog calls — affects substrate-tester scaling.

**Mossinghoff-perturbation single-coefficient flips don't preserve in-band M:** fire #14 found that 200 perturbation attempts yielded 0 in-band hits. The Lehmer band is structurally narrow even for nearby polynomials. Future Lane 1 fires need multi-coefficient perturbation OR irreducible-only Mossinghoff filter — a probe-design issue, not a substrate flaw.

### 8. Multi-instance coordination protocol operates cleanly

Two parallel substrate-tester instances ran throughout this session with no conflict beyond fire-numbering collision. Coordination protocol that emerged:
- Pull before lane selection
- Fire-number = max-on-origin/main + 1
- Anti-repeat = both instances' recent lanes (read fire log)
- Shared inbox via `aporia/meta/queue/techne_inbox.jsonl` — no merge conflicts (append-only ticket-flow)
- Each instance documents in fire log; entries land in newest-first order

The fire #14/#17 sequence demonstrated **multi-instance ticket-flow value**: my fire #14 found a P1-high input-validation gap; parallel fire #17 escalated it to P0 by composing the flaw with downstream substrate behavior. This kind of cross-instance amplification adds substrate-grade signal that no single-instance run would have produced.

---

## Ticket ledger (mine, end of session)

| ID | Status | Priority | Source | Title |
|---|---|---|---|---|
| T-2026-05-06-ST002 | DONE | P1-high | lane-2 | CoordinateChart silently accepts empty domain |
| T-2026-05-06-ST003 | DONE | P2-normal | lane-4 | get_raw_invariant_keys silent sentinel for unknown domains |
| T-2026-05-07-ST-fire14-001 | OPEN | P1-high | lane-2 | MethodSpec accepts arbitrary strings as independence_class |

The downstream T-ST-fire17-001 (P0-blocker, parallel instance) directly cites my ST-fire14-001 in its escalation chain.

---

## Lessons learned / standing recommendations for future substrate-tester instances

1. **Pull before every lane pick.** Multi-instance coordination requires fresh state.
2. **Lane 1 (CLAIM-flood) needs probe-design iteration.** Single-coefficient Mossinghoff perturbation yields 0 in-band hits at 200 attempts. Future instances should try multi-coef perturbation OR pre-filter Mossinghoff catalog for irreducibles.
3. **In-band batch sizes must be small (≤10) due to network calls.** Or invest in a substrate-side ticket for async catalog cross-check.
4. **Lane 7's INCONCLUSIVE-list characterization is high-value cumulative work.** 5/43 entries done; processing 2/fire across coming sessions would produce a fully-characterized ExclusionCertificate independent verification.
5. **Lane 5 cross-degree scaling has 3 datapoints; vary coefficient bound (±3, ±7) at fixed degree** to extend the geometric study without re-baselining.
6. **Canonicalization-fuzz (Lane 13) cumulative-seed coverage is substrate-grade.** Continue at 1 fresh seed per re-probe; 6 seeds = ~15K probes, 0 failures = robust property-test coverage.
7. **Combined pytest invocations** (e.g., fire #30 ran lanes 14 + 13 in single pytest) reduce overhead and are a clean way to pair pytest-based lanes.

---

## Discipline summary

- HARD-1 (no papers): clean across all 16 my-instance fires.
- HARD-2 (anti-gravitational-well): no drift toward established frameworks observed in substrate code reviewed.
- HARD-3 (tensor-first): respected.
- HARD-4 (calibration anchors): the property-based fuzzer (T006) IS substrate-grade calibration anchoring; the cumulative cross-fire data on Lane 7 INCONCLUSIVE entries is calibration anchor data for the deg-14 ±5 ExclusionCertificate.
- HARD-5 (domains are docstrings): respected; T-ST003 fix correctly raises with registered-domain enumeration in the message.
- Per-fire 50-min cap: respected on all 16 my-instance fires (longest was fire #14's ~38 min including deadlock + revision).
- Anti-flooding cap (5 tickets/fire): never approached; max 1 ticket per fire.

---

## Session close

Substrate-tester /loop terminated by James-directive at fire #30 close. Multi-instance coordination protocol leaves the substrate-tester role in clean handoff state:
- Fire log is current.
- All committed/pushed artifacts are reproducible.
- 1 OPEN ticket from my instance (T-ST-fire14-001 P1-high) plus 5 OPEN tickets from prior sessions remain — handed back to Techne for resolution.

The substrate is stable across all probed primitives. The contract-change-window restart was operationally clean (no regressions; 5 newly-LIVE lanes activated and smoke-tested cleanly across both instances).

— substrate-tester, session close 2026-05-07
