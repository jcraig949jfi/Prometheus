# Discovery via Rediscovery — Same Loop, Different Oracle States

**Date:** 2026-05-03
**Source:** `harmonia/memory/architecture/discovery_via_rediscovery.md` + ChatGPT pressure-cycle response captured in `stoa/discussions/2026-05-03-chatgpt-on-discovery-via-rediscovery.md`
**Originating epiphany:** James Craig (HITL), 2026-05-03

## The unification

If the architecture can rediscover existing mathematics — and Techne demonstrated it can on 2026-05-02 by reaching M=1.458 in the Salem cluster band — then by the same architecture's structural logic (mutation operators against the same falsification battery) it should be able to discover *adjacent* undiscovered mathematics.

**Rediscovery and discovery are the same loop with different oracle states.**

The field treats them as separate:
- Rediscovery = "can the system find what we already know?" (capability test)
- Discovery = "can the system find what we don't know?" (research goal)

In the Prometheus architecture, they are the same loop. A discovery candidate is a rediscovery target whose catalog entry doesn't exist yet. Mossinghoff's 178-entry snapshot is a proxy for the universe of small-Mahler-measure polynomials; any polynomial the agent finds in band that's not in the snapshot is either:

- (a) a numerical artifact (floating-point drift, near-cyclotomic case)
- (b) a known polynomial in non-canonical form
- (c) genuinely new

The pipeline distinguishes (a)/(b)/(c) using machinery that already exists or is being built.

## The pipeline

Rediscovery loop (already running):
```
agent → generative_action → BIND/EVAL → reward (matches catalog) → policy gradient
```

Discovery loop (one extra gate):
```
agent → generative_action → BIND/EVAL → catalog_check
   if HIT:  reward fires (rediscovery — calibration evidence)
   if MISS: CLAIM into kernel
            → falsification battery (F1+F6+F9+F11)
            → residual classification (signal/noise/instrument_drift)
            → cross-modality verification (PARI/GP + SAT + symbolic)
            → if signal-class survives: PROMOTE as discovery_candidate@v1
            → if noise/drift: archive with typed reason
```

The architectural difference is one additional gate (catalog miss → claim → battery → classify) plus one comparator (run the null in parallel and compare survivor rates).

## ChatGPT's sharpening — three-stage validation ladder

When this unification was sharpened by external review, ChatGPT pushed back: **rediscovery competence is necessary but not sufficient for discovery competence.** A system can be excellent at closed-world search and fail completely at open-world search.

The honest framing is a three-stage validation ladder:

1. **Rediscovery (closed world).** Can the system recover known results? Calibration / sanity check. Techne's M=1.458 result lives here.
2. **Withheld rediscovery (blind test).** Can the system rediscover results intentionally hidden from it? Hold out part of the catalog before training/exploration; see if the system finds the held-out entries anyway. **This is the bridge layer.** Strongest test of generalization under controlled blindness.
3. **Open discovery + null baseline.** Can the system produce candidates that (a) are not in catalogs, (b) survive the falsification battery, AND (c) outperform null-generator baselines under adversarial verification?

The third condition is the one most ML "discovery" papers skip. Without a null comparator, "we found a polynomial in band that's not in the catalog" might be exactly what uniform random sampling produces; the system's contribution is then zero. **Discovery means *better-than-random* survival under the same battery.**

## Why this matters for Ergon specifically

Ergon's role in the unified pipeline is as one of multiple parallel `agent` types — the others being Techne's REINFORCE baseline (LLM-driven) and a future Silver-class learner if one ever plugs in.

The five-counts diagnostic in Trial 3 (Ergon MVP Days 18–22) explicitly compares three agent classes — uniform random, Ergon's MAP-Elites (structural), and a third (symbolic) — running against the same env, the same battery, the same null world. **This is the substrate's first empirical anchor on the bottled-serendipity thesis:** do prior-shaped mutators outperform uniform random by enough to justify the LLM cost?

If yes — confirms the LLM-as-mutation-operator framing.
If no — mechanical evolutionary search achieves discovery without LLM priors, and the substrate's economics shift dramatically.

Either result is substrate-grade.

## What's built vs what's missing

| Component | Status |
|---|---|
| Generative env (action space, sparse reward) | Shipped (`prometheus_math/discovery_env.py`) |
| BIND/EVAL kernel primitives | Shipped 2026-05-02 (`sigma_kernel/bind_eval.py`) |
| Catalog cross-check (Mossinghoff only) | Shipped |
| CLAIM into kernel (v0.1) | Shipped |
| Falsification battery (F1–F20) | Shipped |
| Residual classification | Shipped 2026-05-03 (`sigma_kernel/residuals.py`) |
| ObstructionEnv (cross-domain validation) | Shipped 2026-05-03 |
| OEIS-data rediscovery validation | Shipped 2026-05-03 |
| `DISCOVERY_CANDIDATE` → substrate CLAIM | Partial integration |
| Cross-catalog absence-verifier (LMFDB ∩ OEIS ∩ arXiv ∩ Mossinghoff ∩ Boyd) | **Not yet built** — Aporia Scout #10 specified the architecture |
| Null-world generator | **Not yet built** — Aporia Scout #9 specified the architecture; K=10 publishable / K=5 interesting |
| Withheld-catalog benchmark | **Not yet built** — Aporia open task to curate `withheld_mossinghoff_v1.jsonl` |
| Cross-modality verification | Spec stage |

The pipeline becomes operational pending three pieces: (i) promote `DISCOVERY_CANDIDATE` from a log line to a substrate CLAIM, (ii) Techne's residual primitive 5-day MVP, (iii) a withheld-catalog benchmark + null-generator scaffolding.

## The discovery-claim discipline gate

Per Aporia's scouting work (consolidated across 13 scout docs in `aporia/scouting/QUEUE.md`), a candidate is **not** a defensible discovery claim until ALL of the following hold:

1. **Survives null-world comparison at K ≥ 10** (Scout #9 threshold)
2. **Passes three-catalog absence quorum** (Scout #10 threshold)
3. **Classifies as `genuine_novelty` under the 6-class typology** with mechanical decision rules (Scout #12 threshold; expected base rate <5%)
4. **Operates within type-compatibility-masked action space** if the agent uses tree search (Scout #13 threshold)
5. **CECM-Mossinghoff catalog scrape (not arXiv paper parsing) is the actual ingestion target** for the Lehmer domain (Scout #11 finding)

These five thresholds together form the operational discipline gate. Ergon's MVP Trial 3 is the first end-to-end exercise of the gate at small scale.

## Operator-perspective addendum (Ergon's distinct angle)

Ergon's session journal (2026-05-03) filed three pieces of pushback on the unification framing:

1. **BIND still bypasses CLAIM/FALSIFY/PROMOTE.** Yesterday's substrate hygiene concern is now blocking — the discovery pipeline can't compound cleanly until it lands. Sharpened priority: this week, not "in production."

2. **ChatGPT's stage-3 standard is correctly cautious but slightly too lenient.** Agent > null is necessary; agent's PROMOTE rate uncorrelated with the prior's likely training coverage is the harder bar. Permutation-distance and frequency-weighted-recall as candidate stage-3.5 proxies.

3. **The mad-scientist-byproduct discipline differs by operator class.** LLM-driven exploration needs aggressive CLAIM-on-every-side-thought; Ergon's MAP-Elites archive captures byproducts structurally. Different capture economics; should be documented as such.

The implication for Ergon's MVP: the §6.2 four-counts pilot should be three-arm (LLM-REINFORCE / Ergon's MAP-Elites / uniform random), not two-arm. Uniform random is a strawman null; Ergon's evolutionary search is the substantive null. If A > B with significance, the LLM prior is contributing something selection pressure doesn't. If A ≈ B, the bottled-serendipity thesis is partially wrong and mechanical evolutionary search achieves discovery without LLM priors. **Either result is substrate-grade.**

This reframes Ergon's pivot-doc commitments: the week-4 port-MAP-Elites-onto-Techne's-env work upgrades from "validate the env shape" to "supply the load-bearing comparison arm for the substrate's first empirical anchor on the bottled-serendipity thesis." Same engineering, higher load.

## Where to find more

- Foundational doc: `harmonia/memory/architecture/discovery_via_rediscovery.md`
- ChatGPT pressure-cycle response: `stoa/discussions/2026-05-03-chatgpt-on-discovery-via-rediscovery.md` (if filed)
- Ergon's operator-perspective addendum: `stoa/discussions/2026-05-03-ergon-on-discovery-via-rediscovery.md`
- Aporia scouting consolidated discipline gate: `aporia/scouting/QUEUE.md`
- Bottled serendipity parent thesis: `harmonia/memory/architecture/bottled_serendipity.md`
