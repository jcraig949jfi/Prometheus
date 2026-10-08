# O1 repair: observation of promoted applications (Beta-03, qualification on EXPOSED W9-H pilot data)

Representation lead. Branch `aphrodite/b03-w5p`. Exposed data only: W9-H pilot seeds 0-2, which the ecology lead's
discovery pilot already used. Nothing here is confirmatory.

## 0. Frozen before any O1 run (committed before the runs; see git history of this file)

### 0.1 Design

O1 is the donor option `donor_w5p(..., o1=True)`. It defaults to **OFF**.

- **O1 entry.** For every ORDERED pair (Q, P) of promoted primitives in the donor's registry, Q == P included and
  taken in id order, form the promoted-form schema `Q.schema[{H} := P({H})]`. The entry's bodies are the
  **W5P instantiations** of these schemas: the same `promote.instantiate` filler set (LEVEL1 + P(atom)) and the
  same depth/shape rule every W5P candidate entry uses. Bodies already present in a START entry are dropped,
  because the ordinary walk covers them. inits = H1 and finals = FINAL_SPACE, as `a17.schema_entry`.
- **Where the contexts come from.** They are the arm's OWN promoted schemas, which are the only one-hole contexts
  an arm possesses. No generic context set, no motif and no truth enters. An empty registry (pristine, gen-1)
  gives no entry, no walk and no charge, so O1 is a no-op for pristine.
- **Placement: a deviation from the letter of the request, decided on arithmetic before any run.** For the
  oracle start, the START library holds 6 × 57,960 + 151,920 = **499,680** candidates per observation walk. An O1
  entry placed "after the start entries, before the W5 fallback" inside the same walk therefore begins at
  candidate 499,681. At escrow 300k (or 30k) it is **never reached**, so that literal variant is identical to
  O1-off by arithmetic. O1 is implemented instead as follows:
  - After each ordinary observation walk, a **second walk per observation cell** is made over the O1 entry ONLY,
    with no fallback.
  - It uses the **same escrow value** (`a17.ESCROW`), the same max-hits and the standard keyed order and charge
    rule (`walk.iter_hits`, which is conformant to `fair.search_collect` and `a18.fast_cost`).
  - Its hits join the observations.
  - The ordinary observation walk is untouched, so every O1-off observation is still made.
  - Charges go to `meta_charges` and to both cost ledgers (phase `observe_o1`).
- **Size.** Oracle-start O1 entries hold 1,214 / 1,224 / 1,242 bodies on seeds 0 / 1 / 2, which is
  437,040 / 440,640 / 447,120 candidates. A 300k walk with no hit covers about 68% of it.
- **Everything downstream is unchanged:** certification (coverage = START), W5P derivation, candidates and
  selection.

### 0.2 Qualification protocol

- **Runner and roles.** The ecology lead's runner and roles: `w9h_pilot_discovery.py`, `discovery/ROLES.json`
  (W9H-R1).
- **Known-positive gen-2 control.** START = the seed's 6 TRUE level-1 mechanisms (`oracle_start`), then PRISTINE.
  Rule g11 (g10 minus MEMORISE), promotion ON, **o1=True**, escrow **300k** for observation, the O1 walk and
  `Cell.cost`. Seeds 0, 1, 2. At most 2 workers, `OMP_NUM_THREADS=1`.
- **Secondary runs** (reported, not part of the criterion):
  - the same at escrow 30k;
  - gen-1 (pristine start, 30k) with o1=True, which is expected to be byte-equal to the recorded `gen1_30k` rows on
    every output key.
- **Truth timing.** Truth (`W9H_TRUTH.json`) is read only by the scorer, after the donors have run.

### 0.3 PASS criterion (frozen)

A seed PASSES iff ALL of the following hold for the 300k O1 oracle donor.

- **(S1) Non-trivial depth-2 selection.** The selected schema contains a promoted node, `dag_depth_selected >= 2`,
  and it is not a bare `P_x({H})`.
- **(S2) Matches a true composition.** The selected schema equals a TRUE composition `S_b ∘ S_a` of that seed, up
  to W5 canonicalisation. That means either of:
  - `identity.normalise(parse(expansion))` equals the same for the truth composition schema, with `{H}` as one
    variable; or
  - its W5P instantiation set equals the W5P instantiation set of `P_b-schema[{H} := P_a({H})]` under the run's
    registry.
- **(S3) Transfer.** The selected library (`selected_entries`) reaches at least 1 of the seed's admitted L2
  families, where reaching means:
  - in ≥ 1 of the 2 W9H-tx cells;
  - cap 1M, T4 v1a qualifier (`w9h_admit.walk_cell`);
  - with a first qualified program whose body is **outside G5**;
  - on a family PRISTINE reaches in **0** of the same cells (`W9H_FOUNDRY` `PRISTINE_TX`).
  - Transfer walks are run only for seeds that pass S1 and S2. This is cost control, declared here.

**O1_QUALIFIES** iff ≥ 2 of 3 seeds PASS **and** total CPU for this task ≤ 2.0 core-h. Otherwise **O1_FAILS**.

The first broken link is reported as the earliest failing stage on the majority of seeds:
- **CANDIDACY:** no derived schema satisfies S2;
- **SELECTION:** one does, but it was not selected (S1 + S2 fail);
- **TRANSFER:** S3 fails;
- **BUDGET:** CPU exceeds 2.0 core-h.

No parameter is tuned after the outcome is seen.

RESULTS
