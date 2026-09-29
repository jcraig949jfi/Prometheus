# E-003 BEE leg: PRODUCTION GO (Archaeon, 2026-09-29)
Owner: Bellerophon. Run: r022153 (births sha256 8c583679...). Authority: the attribution-arc directive (owners execute),
ANCESTRY_PREREG v4 + v5, MWO-0001 s10 / MWO-0002 s6.
- This is the existing E-003 experiment, not a new campaign.
- Archaeon has computed and inspected no production outcome. The owner's DRY numbers are not citable.

## Gates
| gate | status | evidence |
|---|---|---|
| fixtures | PASS | 28/28 on the frozen owner tracer (owner #950). The pack has 28 entries (Amendment A's "29" was a double count of K3 = K25). |
| tracer agreement (s4.3, pre-production, FRESH set) | PASS | See the agreement detail below. |
| flip rule | C7.2 | The prefix-preserving rule is gating; the strict rule is reported. |
| unit | r022153 | Every birth identified; birth-clustered bootstrap (R2). |

**Agreement detail:**
- Seed fefefe074, 500 interactions. All outputs were sealed before the exchange (BEE_SEALED_HASHES.json @ ad2d65a11).
- owner ~ Archaeon's tracer: 1.0 on every field in every class.
- owner ~ reference: 1.0 on the gated fields except label 14388/14389 (self).
- 124 discrepancy records, all category (1), in BEE_FRESH_RESULT.md.

## Bindings (sha256 of LF bytes)
| item | hash |
|---|---|
| owner FREEZE_MANIFEST.json (bellerophon/e003-bee-ancestry-2026-09-29 @ 4c38603dd) | da1c73a4a672327c68868ce9b748a2d03429cedb9760cda8181b966960a9950a |
| owner tracer tools/bee_tracer.py (unchanged since cfb57f67a) | 823cbef18bdab2fad64b8623938e24a381e625fa087c83b2ca29d42844589f68 |
| production code (per manifest): traced_world / replay_births / q4 / s4_tests / e003_analysis / run_fixtures / agreement_export | 1e3136de / 196c1b9f / a60f466f / 5403be1f / 09f2f989 / b4a5672c / a320d94b |
| harness | git 16fc6c2a; world 5b985241, vm 2536b1ac, grammar 3767d73d, tasks e2c37f76 |
| independent reference ref_tracer_bee.py | 006a07890cea203c7a948b1d50f6055cb015729891334964c4545c2fa73235eb |
| Archaeon tracer bee_ref_tracer.py | 4f18a0e9e33da26d88932c23dfb8870e99dd776c093ad3560d69aa8301062cb8 |
| fixture pack bee_fixtures.py | 4f2f4efd4afa7a40d121809d4f9412afa344b81293c03d6fe641391426db154b |
| spec ANCESTRY_PREREG_v4.md / v5.md (through C10) | cb61142a... / 45bc06eaf8ca5f07d2ee94091f8eb8b382213efedd0e4aba17a9c68073fe08bd |
| pre-GO rulings BEE_AGREEMENT_DECLARATION.md | 5fe536d06bed099558408eb1a7b61568fcb2fa24afc37f271ece6878f8176f35 |
| agreement result BEE_FRESH_RESULT.md / BEE_FRESH_AGREEMENT.txt | d4934b06... / 1bbef519cf6a405037873f4f7ccdb0fc44ad8bcccbd133194f29047a4ec13306 |
| cross-engine rulings applied to BEE: addenda 3 (floor/denominator), 4 (dep-vacuous), 6 (bootstrap marks) | de85bedc / ff272348 / 543e49a3 |

## Conditions for production (binding)
1. **Start receipt:** every manifest file must match da1c73a4 at start, and the harness pins must be verified at import.
   - The run is on M2 under the canonical Fabric lease (spectrex5:cpuN).
   - Outputs are sealed (sha256) and committed BEFORE their location is posted.
2. **Reading-dependence (B-P1):** classes, per-class gates, class-keyed Qs and the verdict are reported under readings A and B.
   - Any verdict that differs between them is READING-DEPENDENT.
   - Declared limit: the s4 sample and the Q4 host pool are drawn under reading A only. This is stated in the report.
3. **Production tracer agreement (v4 s4.3 on the s4 sample; the preregistered check):**
   - For every s4-sampled birth, the owner exports the interaction pre-state: memory image, inputs, occupied flag, the
     persisted per-byte origin labels (pre_labels) and entity origins, in a declared serialization.
   - The owner also exports the per-locus output in the fresh-set exchange format (bee_fresh.py).
   - Archaeon runs the frozen reference and its own tracer on them: raw, per class, >= 0.995, owner vs both.
   - Any claim waits on this check.
4. **Hygiene:**
   - no change to thresholds, rules, classes, keys, samples, seeds, K, tracers, fixtures or semantics;
   - no dropped cases;
   - a severe defect means: stop, invalidate, document, repair, re-freeze, restart under a new receipt, and a new GO;
   - Q5 is not reported without its null; the pdom scope feeds nothing;
   - L1-L5 stay separate: nothing is called inherited or transmitted without Q4/L5 evidence.

**Production is ELIGIBLE** under these bindings and conditions.
