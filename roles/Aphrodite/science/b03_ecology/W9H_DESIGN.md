# W9-H — hierarchical second-level task ecology (Beta-03, E4)

Branch `aphrodite/b03-eco`. Ecology lead, task side only. **No treatment library was walked to build, admit or
certify anything here.** The only libraries walked are PRISTINE, the generator's own mechanisms as flat schemas,
and expansion-based promoted controls built from generator truth.

Files (all new, `roles/Aphrodite/science/b03_ecology/`):

| file | role |
|---|---|
| `w9h_grammar.py` | generator: CONFIG (to be frozen), mechanism / composition grammar, family stream → `W9H_SUPPLIES.json` + sealed `W9H_TRUTH.json` |
| `w9h_admit.py` | foundry (A1–A5), admission (A6), certification incl. the known-positive sensitivity control (`certify_family`) |
| `w9h_report.py` | pilot metrics → `W9H_PILOT_METRICS.json` |
| `pilot/` | pilot outputs (3 seeds × 48 families) |

## 1. Grammar (hierarchical)

Base DSL: W5 (`a17.g5_bodies`, depth-3 bodies), atoms `acc v first last 0 1`, the 7 engine PRIMITIVES
(add sub mul fdiv mod gcd powr). Fillers `e` = W8's E1 (p=.5 atom, else `op(atom, atom)`), i.e. `fair.LEVEL1`.

**Level-1 mechanism** = one-hole body schema `S(H)`, drawn as a tree:

* `W1` `op(x, H)` (weight .2), `W2` `op1(x, op2(y, H))` (.45), `W2S` `op1(op2(x, y), H)` (.35);
  every operator, atom and argument order uniform. No motif is named anywhere.
* **Stratum** from the operator set: ADD (only add/sub), MUL, DIV (fdiv/mod), GCD, POW, MIX (≥2 non-additive classes).
* **Quota per seed** (K1 = 6): one mechanism each for ADD, MUL, DIV, GCD, MIX, plus one ANY slot (any stratum, natural
  draw). Filled by rejection sampling of the uniform draw. This stratification exists so non-additive families are
  measurable. **It says nothing about natural frequency**: 400 uniform draws gave 9 passing mechanisms (6 ADD, 2 MUL,
  1 DIV, 0 GCD/MIX/POW). Non-additive mechanisms are rare under the uniform grammar.
* Mechanism screens (task-free, outcome-free):
  * not degenerate: no REDUNDANT node (replacing a node by one of its children leaves the 12-filler behaviour
    signature unchanged **up to sign**, which kills `(1 * v)`, `pow(x, 1)`, `gcd(x, 0)` = abs, `(0 - x)`) and no
    CONSTANT hole-free subterm (`(first - first)`);
  * ≥20% of the 258 LEVEL1 instantiations accumulating (ruler v2), ≥8 distinct accumulating behaviour vectors,
    ≤50% of instantiations behaviourally equal to their own filler;
  * ≥8 in-W5 instantiations (`T3D.instantiate`), so the mechanism is learnable as a flat W5 schema by the base engine;
  * feasibility: ≥3 of 24 fixed fillers give a body that is T4 task-side admissible for some init ∈ H1 and final ∈
    {acc, acc+last, acc*first, first-acc};
  * distinct from the seed's other mechanisms (string and 12-filler signature).

**Level-2 composition** `S_b ∘ S_a := S_b[H := S_a[H]]` (outer b, inner a, b ≠ a), K2 = 3 ordered pairs per seed,
uniform without replacement over the 30 ordered pairs. Each must pass the same schema screen (without the W5
requirement) and be **irreducible**: its signature differs from every level-1 mechanism of the seed. A level-2
family body is `S_b[H := S_a[H := e]]`. Its dependency depth is 2. Its expansion may leave W5. Per-composition
`w5_share` (the fraction of LEVEL1 instantiations that land in W5) is recorded.

**Family stream** (lineage-style recurrence). Level quotas per seed: L0 = 10 background (W8's PCFG, W5-canonical),
L1 = 20, L2 = 18. At each proposal a level is drawn with weight equal to its remaining quota. Within the level, the
source is drawn uniformly among the *least-filled* live sources. That balances recurrence without favouring any
source. A source is retired after 400 draws. Per family:

* a fresh filler (no repeat per source) that is not constant;
* L1 bodies must be in W5;
* the body must be accumulating;
* L1/L2 bodies must not be behaviourally equal to any PRISTINE organ body (H2). Such bodies are shallow, because
  PRISTINE exhausts the organ entry within 152k candidates;
* init ~ H1, final ~ acc-finals, with ≤4 redraws until the T4 task-side profile is admissible;
* behaviour-level de-duplication within the seed.

Names are letters only (`y` + 5 letters). They never collide with W8 (`w…`) or A18/T51 (`q…`).

**Output** `W9H_SUPPLIES.json` has exactly the W8 shape: `{"W9H:<seed>": {"families": [[name, init, body, final], ...],
"stats": {...}}}`. `b02.stage_supply`-style code can consume it by swapping the key prefix `LIN:` → `W9H:`.
**`W9H_TRUTH.json` is sealed.** It holds the mechanisms, compositions and per-family level/source/filler. Only the
admission and certification stages may read it. A treatment must never read it.

## 2. Generator config to be frozen

`python w9h_grammar.py config` prints CONFIG and its sha256. Every supply/truth record carries `config_sha`. The
pilot used sha **`2334bb7480bd5d12d085f38ce4d9e143b4f5fa2f5c1cf631e2a77ef4e6768b4a`. Reproducibility was checked: regenerating W9H:0 reproduces the families and truth byte-for-byte**. For a confirmatory run the coordinator freezes CONFIG (by sha) in the amendment
**before any treatment run**. Recommended production changes, all of which change the sha and so must be decided
before the freeze:

* `level_quota`: L0 24 / L1 60 / L2 60 (144 families, the W8 size), giving ~10 L1 families per mechanism and ~20
  L2 families per composition. In the pilot, recurrence (≥2 qualified siblings) was the main L1/L2 admission loss;
* `K2`: 3 → 4–6, if certified compositions per seed are the binding quantity (see pilot numbers);
* seeds: fresh block, never used in pilot (pilot = 0–2).

## 3. Admission (per family; `w9h_admit.py foundry` then `admit`)

| | criterion | instrument |
|---|---|---|
| A1 | valid executable witness | generator screens (accumulating, T4 task-side profile) |
| A2 | Q2 qualification | `a18_c1.qualify_family` (exact-fast Q2), unchanged |
| A3 | tribunal coverage | T4 v1 on the witness artifact (same call) |
| A4 | pristine reachability, **measured** | `p_PRISTINE`: 4 dev cells at escrow 30k (qualify_family); `PRISTINE_TX`: 2 transfer cells at cap 1,000,000, walked to the first T4-v1a-qualified program (v2b D endpoint, `walk.iter_hits`) |
| A5 | independent dev / transfer entropy | separate labels for dev, transfer and pilot cells; checked: no shared prompt, distinct search seeds |
| A6 | learning opportunity (generator truth only) | L1: mechanism has ≥2 T4-qualified L1 families in the seed. L2: inner and outer each ≥2 qualified L1 families and composition ≥2 qualified L2 families. All levels: `p_PRISTINE ≤ 0.75` (A19 window) |

Admission never consults any treatment outcome. The certification below is reported **alongside** admission and is
not part of it. The coordinator may decide to restrict TRANSFER to certified families (open decision D3).

## 4. Certification and the known-positive sensitivity control (`certify_family`)

The representation lead's promoted-primitive API (`aphrodite/b03-w5p`) was not available to me. Certification is
therefore by **EXPANSION**. A promoted primitive `P_a(x) := S_a[H := x]` is represented by its *expanded*
instantiations in the base DSL, as an ordinary KLib entry with an explicit `bodies` list. These bodies are not
limited to W5. `walk.iter_hits` and `fasteval` execute any body expression. Libraries are walked on the same cells
(common random numbers): 4 dev cells at 30k and 2 transfer cells at 1M. The endpoint is the first program that T4
v1a qualifies (DIRECT, with positives confirmed through ARTIFACT).

| library | entries (in order) | meaning |
|---|---|---|
| PRISTINE | organ | baseline |
| FLAT | every seed mechanism as a flat W5 schema entry (hash order), then PRISTINE | level-1 knowledge, no promotion |
| PROMOTED_A | `S_x ∘ P_a` expanded over LEVEL1 for **every** seed mechanism x (hash order), then FLAT, then PRISTINE | the correct inner primitive is promoted; the library does not know which outer mechanism uses it |
| PROMOTED_ORACLE | `S_b ∘ P_a` only, then FLAT, then PRISTINE | attainability given the right depth-2 schema |
| SHAM_C | as PROMOTED_A with a wrong inner P_c (seeded, c ≠ a) | specificity control |

`CERTIFIED_DEPTH2(f)` holds iff f is admitted, PROMOTED_A reaches f at 1M in ≥1 of 2 transfer cells, and PRISTINE
reaches it in 0 of 2. For L1 families the analogue is PRISTINE vs FLAT_A, where FLAT_A is the correct mechanism as
a flat schema.

Every qualified endpoint is checked against the witness with `identity.behavior_id` (B1) and `audit_id` (B2). A
qualified program that differs from the witness is a tribunal FALSE POSITIVE. Every dev-consistent program that the
tribunal rejects but that equals the witness on B1 is a FALSE NEGATIVE.

## 5. Pilot results

Pilot: seeds 0–2, 48 families per seed (L0 10 / L1 20 / L2 18), CONFIG sha `2334bb74…`. The full numbers are in
`pilot/W9H_PILOT_METRICS.json`. Inputs and outputs are `pilot/W9H_SUPPLIES.json`, `W9H_TRUTH.json`,
`W9H_FOUNDRY.jsonl` and `W9H_CERTIFY.jsonl`. Logs are `gen.log`, `foundry.log` and `certify.log`. No treatment was
run.

**GENERATOR_ADMISSION_YIELD**

| level | generator proposals | generated | Q2 | T4-qualified | admitted | admitted/generated | admitted/proposal |
|---|---|---|---|---|---|---|---|
| L0 | 1402 | 30 | 29 | 29 | 28 | 0.93 | 0.020 |
| L1 | 1954 | 60 | 60 | 60 | 60 | 1.00 | 0.031 |
| L2 | 1236 | 54 | 54 | 50 | 47 | 0.87 | 0.038 |
| all | 4592 | 144 | 143 | 139 | 135 | 0.94 | 0.029 |

Losses after generation: L0 lost 1 to Q2 and 1 to the window; L2 lost 4 to T4 and 3 to the window (all 3 window
losses are in W9H:1 C0). No family failed recurrence or entropy. All 139 T4-qualified families had disjoint
dev/transfer/pilot prompt sets and distinct search seeds. The ~3% per-proposal yield is dominated by generator
rejections. In L1, the largest are non-accumulating bodies and constant fillers. In L2, they are constant fillers,
then T4 task-side profile and organ-equivalence. Per-level reasons are in each supply's `stats.by_level`.

**Stratum sizes** (generated → admitted). L1: ADD 14→14, MUL 13→13, DIV 10→10, GCD 10→10, MIX 13→13. L2 (outer>inner):
ADD>MIX 14→13, ADD>MUL 6→6, GCD>DIV 7→7, GCD>MIX 6→3, GCD>MUL 6→6, MIX>DIV 3→3, MIX>GCD 6→3, MIX>MUL 6→6.
L0 30→28. These are **quota** sizes. Natural frequency under the uniform grammar is far lower (R1).

**PRISTINE_REACHABILITY** (admitted families, first T4-v1a-qualified program)

| level | n | escrow 30k: families p>0 (cells) | cap 1M: families reached (cells) |
|---|---|---|---|
| L0 | 28 | 7 (9/112) | 14 (24/56) |
| L1 | 60 | 1 (1/240) | 9 (11/120) |
| L2 | 47 | 2 (3/188) | 3 (6/94) |

**PROMOTED_REACHABILITY: the sensitivity control** (47 admitted L2 families, same cells for every library)

| library | 30k: cells (family share) | 1M: cells (family share) |
|---|---|---|
| PRISTINE | 8/188 (0.06) | 6/94 (0.06) |
| FLAT (all seed mechanisms, unpromoted) | 0/188 (0.00) | 34/94 (0.36) |
| **PROMOTED_A** (correct inner primitive promoted, outer unknown) | 4/188 (0.04) | **94/94 (1.00)** |
| PROMOTED_ORACLE (S_b o P_a) | 110/188 (0.89) | 94/94 (1.00) |
| SHAM_C (wrong inner primitive) | 0/188 (0.00) | 34/94 (0.36) |

For level 1 (60 admitted L1), FLAT_A, the correct mechanism as a flat W5 schema, reaches 133/240 cells at 30k
(0.93 of families) and 120/120 at 1M. PRISTINE reaches 2/240 and 11/120. Level-1 mechanisms are learnable
targets: once learned, they pay off at the standard escrow.

**The control passes at the 1M transfer cap.** Promoting the correct primitive takes depth-2 reachability from
6% (PRISTINE) to 100% of families. The wrong primitive (SHAM_C) does no better than unpromoted FLAT. FLAT's 36%
comes from L2 families that a flat W5 instantiation of some seed mechanism happens to express. **At escrow 30k the
control does not pass for PROMOTED_A (4/188 cells).** Only the oracle depth-2 schema pays off at 30k (R3).

**DEPTH_TWO_WITNESS_COUNT**

* generated 54, T4-qualified 50, admitted 47, of which 46 have expansions outside W5;
* **CERTIFIED_DEPTH2 = 44 / 47** (Wilson 95% [0.83, 0.98]); 43 of these are outside W5. Per seed: 15 / 11 / 18.
  The certified families cover 8 of the 9 compositions. W9H:1 C0 has 3 admitted and 0 certified, because PRISTINE
  reaches them;
* **CERTIFIED_STRICT = 30 / 47.** This adds two conditions: FLAT 0/2 and SHAM_C 0/2 at 1M, so promotion of the
  correct primitive is *necessary* as well as sufficient. 29 of the 30 are outside W5. Per seed: 5 / 11 / 14.
  They cover 8 compositions;
* the oracle verdict (PROMOTED_ORACLE instead of PROMOTED_A) also gives 44.

So the world **does contain independently certified, attainable depth-two mechanisms**: 44 families (30 strict) on
8 distinct compositions across 3 seeds.

**FALSE_POSITIVE_RATE (tribunal T4 v1a)**. There were 727 qualified endpoints across foundry and certification
walks. 1 was not behaviourally equal to the witness on B1 or B2, a rate of 0.0014 (Wilson 95% [0, 0.008]). That case
is family `ydnbaa` (W9H:1 C0, not admitted, because PRISTINE reaches it). Its filler `(1 % last)` is 1 except when
last = 1, and the PROMOTED_ORACLE endpoint dropped that edge case. The tribunal also rejected 1344 dev-consistent
spurious programs, and none of them was B1-equal to the witness (0 false negatives).

**SEMANTIC_CLASS_DIVERSITY** (admitted). Seed 0: 45 families, 45 behaviour classes, 35 body-vector classes,
fclass ADD/AFF/OTHER 4/19/22. Seed 1: 44, 44, 40, 4/22/18. Seed 2: 46, 46, 36, 8/5/33. Behaviour classes equal
family counts by construction (behaviour de-duplication). Body-vector classes show that 10–25% of families share a
body semantics and differ only in init/final.

**Distribution shift vs W8 LIN 0–7** (1152 families) → W9H admitted (135)

| | W8 LIN | W9H admitted | TVD |
|---|---|---|---|
| fclass ADDITIVE / AFFINE / OTHER | .58 / .28 / .14 | .12 / .34 / .54 | 0.46 |
| W8-audit additive one-hole share (`acc ± X`, `X + v` at root) | .63 | .38 | |
| top op add / sub / mul / mod / gcd | .41 / .49 / .08 / .01 / .01 | .37 / .17 / .21 / .08 / .17 | 0.36 |
| all ops | | | 0.22 |
| body depth 1 / 2 / 3 / 4 / 5 | .12 / .56 / .32 / 0 / 0 | .03 / .30 / .33 / .15 / .19 | 0.36 |

W9H moves mass from additive one-hole structure to non-additive (fclass OTHER ×3.9) and puts 34% of bodies beyond
W5 depth. That is the intended shift. It is a stratified design, not a natural-frequency claim.

## 6. Per-seed foundry cost

Measured in the pilot (single core, OMP=1): generator 189–321 s per seed (48 families); foundry 27.5 CPU-s per
family; certification 10.8 CPU-s per L1 family and 22.8 CPU-s per L2 family. The pilot total was ≈1.8 CPU-h
(gen 0.23 + foundry 1.10 + certify 0.50) and ran ~70 min wall at 2 workers.

Per-seed estimate at the recommended production size (144 families: L0 24 / L1 60 / L2 60):

| stage | CPU | note |
|---|---|---|
| generator | ~10–20 min | one-time, rejection-dominated |
| foundry (A2–A5) | 144 × 27.5 s ≈ **66 min** | same per-family cost as a W8 foundry row plus 2 PRISTINE 1M walks |
| certification | 60 × 10.8 + 60 × 22.8 s ≈ **34 min** | optional for L1 |
| **total** | **≈ 1.8–2.0 CPU-h per seed** | 8 seeds ≈ 15–16 core-h, ~8 h wall at 2 workers, within the 48 core-h/24 h cap |

Every single job is < 1.5 CPU-min, well under the 15-minute limit.

## 7. Interface expected from W5P (representation lead)

What this ecology assumes, and what the coordinator should check when W5P lands:

1. **Promotion call.** `promote(schema: str) -> Primitive`, where the schema has exactly one `{H}`. The primitive
   must carry `expand(arg_src: str) -> str` = `schema.replace("{H}", arg_src)`. Certification uses only this
   expansion. Any W5P whose expansion differs (re-canonicalisation, different hole convention) must ship an
   adapter. A conformance check: for every W9H composition, `expand` of W5P's `S_b[H := P_a(H)]` instantiated over
   LEVEL1 must equal `w9h_admit.expand(compose(S_b, S_a))` as a set, modulo W5 canonicalisation.
2. **Library entry form.** A promoted-primitive library entry must be expressible as KLib data:
   `{"name", "inits", "bodies" (expanded, explicit), "finals"}`. Alternatively, W5P can provide its own
   `candidates(seed)` with the **same keyed-order discipline** (`fair.keyed`, seed-only keys). If W5P walks
   promoted bodies through a *new* proposal grammar instead of explicit expansions, the coordinator must rerun
   `certify_family` with W5P's library builder substituted for `libraries_l2`. The verdict rule stays unchanged.
3. **Depth.** Expansions reach depth ≤5 (outer hole depth ≤2 + inner hole depth ≤2 + filler depth 1). W5P must
   evaluate them. `fasteval.fn` and `basis_v4.run_program` already do.
4. **No truth leakage.** W5P and every treatment donor must read only `W9H_SUPPLIES.json` and their own
   observations, never `W9H_TRUTH.json`.

## 8. Known risks

* **R1: the non-additive world is narrow, and the tribunal is the reason.** Under the uniform mechanism grammar, about
  2% of draws pass the screens. Pure gcd/mod/fdiv accumulators are history-forgetting, and T4's task-side profile
  rejects them correctly (MIDDLE_INSENSITIVE, FIXED_POINT_DYNAMICS, CONSTANT_OR_NEAR_CONSTANT). Admissible
  non-additive mechanisms are therefore mostly *accumulate-a-non-additive-transform* forms (`v + (acc % H)`,
  `v + gcd(H, acc)`, `acc * (v // H)`). The stratum quota makes them present. It cannot make them natural. The same
  mechanism shapes can recur across seeds (seed 0 was redrawn identically after the family-screen change, because
  mechanisms are drawn before families).
* **R2: W5 asymmetry.** G5 contains `prim(atom, G4-body)` but not `prim(G4-body, atom)` for non-commutative ops. A
  mechanism like `((x op H) - 1)` therefore has only atom-filler instantiations in W5, and the `≥8 W5
  instantiations` screen removes it. Level-1 learnability is defined relative to this engine asymmetry.
* **R3: 30k is too small for promoted libraries.** One promoted entry is H1 × ≤258 bodies × 180 finals ≈ 93k
  candidates. At escrow 30k even PROMOTED_ORACLE reaches a family only when the keyed order happens to put it early.
  PROMOTED_A walks K1 such entries (~0.56M) before FLAT. Certification is therefore defined at the 1M transfer cap.
  If donor selection stays at 30k, a W5P donor will rarely *see* depth-2 savings during selection. This is a
  coordinator decision (D2), not an ecology fix.
* **R4: "L2" is not semantic depth 2 for every filler.** Constant fillers and organ-equivalent bodies are screened
  out, but a composition can still collapse for particular fillers (for example, gcd-based outer mechanisms with
  small outputs). The certification verdict, not the generator label, is the evidence of depth-2 attainability.
  Use certified families wherever depth two matters.
* **R5: tribunal FP measurement is endpoint-only.** FP/FN are counted on walk endpoints (first qualified program)
  and on spurious dev-consistent hits before them, not on a designed adversarial battery. B1/B2 equality is
  stricter than task-domain equality, so a "FP vs B2" can be a harmless out-of-domain difference.
* **R6: pilot size.** 3 seeds × 48 families. All rates carry wide intervals (Wilson 95% is reported where used).
* **R7: cost of generation.** 3–6 min per seed, dominated by T4 task-side profiles and behaviour ids during
  rejection. Production (144 families) is estimated at ~10–20 min per seed. Generation is a one-time cost.

## 9. Open decisions (coordinator)

* **D1: freeze.** Adopt CONFIG as is (sha `2334bb74...`), or with the production level quotas (s2). Either way,
  freeze before any treatment run, on a fresh seed block (not 0-2).
* **D2: budget regime.** The depth-2 control passes at 1M and fails at 30k for PROMOTED_A. If W5P donors select at
  escrow 30k, a correctly promoted primitive will rarely show depth-2 savings during selection. The options are:
  raise the selection escrow for E4; make depth-2 savings visible through the composition move (the oracle-like
  S_b o P_a entry is what pays at 30k); or accept that E4 tests selection on level-1 savings plus 1M transfer.
* **D3: transfer pool.** Draw TRANSFER from CERTIFIED (44) or CERTIFIED_STRICT (30) L2 families rather than from all
  admitted families. Strict isolates "promotion necessary"; plain certified keeps more power.
* **D4: role rule.** The A19/T51 role rule (OBSERVE needs 0 < p_PRISTINE <= .75) leaves almost no OBSERVE floor in
  W9H, because L1 p_PRISTINE > 0 holds for only 1 of 60. OBSERVE should be drawn from L1 families by mechanism
  (>= 2 per mechanism, so LGG can recover S_a) without the p > 0 floor, or the floor should be computed with FLAT_A.
* **D5: W5P conformance.** When aphrodite/b03-w5p lands, rerun `certify_family` with W5P's own promoted library
  builder (s7) on the pilot families. Accept W5P only if its PROMOTED_A verdicts match these at 1M.

## 10. Addendum (D5, after the W5P merge)
The certification was re-run with W5P's actual machinery (`w9h_w5p_cert.py`). Verdicts match on 31/47 admitted L2
families. **W5P certifies 28; expansion certifies 44.** All 16 mismatches are expansion-only and caused by W5P's
`g5p_admissible` instantiation rule (non-atom fillers under W2/W2S outer mechanisms). The 28 W5P-certified families
still cover all 8 certified compositions. For W5P experiments, use the W5P-certified set. Details are in
E5H_DESIGN_NOTES.md s1.
