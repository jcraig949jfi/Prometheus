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
pilot used sha **`<PILOT_SHA>`**. For a confirmatory run the coordinator freezes CONFIG (by sha) in the amendment
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

<PILOT_RESULTS>

## 6. Per-seed foundry cost

<COST>

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
