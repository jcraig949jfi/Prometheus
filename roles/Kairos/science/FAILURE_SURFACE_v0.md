# Failure surface v0 -- from binary falsification to a map (Kairos, 2026-09-11)

Status: PROPOSAL (schema and vocabulary; no engine change requested). The
reader/classifier that consumes it is KAIROS-06 in roles/Kairos/BACKLOG_H0H5.md.
Written on the reactivation pass (roles/Kairos/prompts/2026-09-11_reactivation/).

## 1. The object

A failure surface is the answer to: given hypothesis H and experiment E,
along which dimensions can E be perturbed, and in which regions of that
space does the claimed phenomenon

    SURVIVES        the preregistered statistic clears its gate
    WEAKENS         effect present, magnitude below the relevance floor
                    or shrinking monotonically along the axis
    DISAPPEARS      effect indistinguishable from its null
    REVERSES        statistic changes sign / ordering inverts
    UNMEASURABLE    the instrument's ceiling, floor or resolution makes
                    the region unreadable (a fact about the apparatus)
    IMPLEMENTATION_DEPENDENT
                    the outcome changes with the executor, the build, or
                    a config the design did not name (attestation
                    divergence, or two faithful executors disagree)
    UNTRIED         the region was named and not run (always reported;
                    "not tried" is a row, never an omission)

A FALSIFIED outcome with no surface is INCOMPLETE work under the Kairos
charter. The surface is what lets a failed experiment name its
neighbours instead of ending the search.

## 2. Why it fits the engine as it is (no new engine object)

The SFE already holds every part, by design (SCIENTIFIC_PROVENANCE.md):

- a FAMILY of kind `comparison` or `campaign` is the container; its
  `manifest` is sealed at creation and may carry the perturbation axes;
- each perturbed E is a MEMBER experiment with a sealed `spec_hash`; the
  arm is sealed separately from the execution spec (v7), so two axes
  points can share an execution hash and still be told apart;
- outcomes are the experiment's FALSIFIED / SURVIVED / INCONCLUSIVE;
- IMPLEMENTATION_DEPENDENT has an engine-side witness already:
  CONFIG_DIVERGENCE and NO_EXECUTION_ATTESTATION on the completion, and
  NO_EFFECTIVE_INTERVENTION / INTERVENTION_NOT_APPLIED on a fork;
- UNMEASURABLE has a witness in a registered MEASUREMENT's declared range
  (v7 `value_path`, `direction`, `unit`, range): a value pinned at the
  range edge is a ceiling, not a result;
- the engine never interprets any of this. The surface is a READ over
  sealed records, assembled by Kairos, and it lives beside the ledger
  (committed JSON under roles/Kairos/science/surfaces/), never inside it.

So no schema change, no new route, no new status word. The one thing
that must be DECLARED by the experimenter, because the engine cannot
infer it, is the axis list: which knobs the perturbation moved. That is
the manifest convention in section 3.

## 3. Manifest convention (inside the family manifest; freeform to the engine)

    "kairos_surface": {
      "version": "v0",
      "hypothesis": "<one sentence, the estimand the family attacks>",
      "base_exp_id": "<the E whose outcome started the map>",
      "axes": [
        {"name": "density",        "kind": "parameter",
         "values": [0.3, 0.4, 0.5], "units": "fraction"},
        {"name": "null_family",    "kind": "null",
         "values": ["permutation", "generator", "row_shuffle"]},
        {"name": "representation", "kind": "representation",
         "values": ["direct", "seeded_balanced", "seeded_scrambled"]},
        {"name": "seed_root",      "kind": "stochastic",
         "values": ["s1", "s2", "s3", "s4", "s5"]},
        {"name": "executor_build", "kind": "implementation",
         "values": ["<player_identity_hash A>", "<B>"]},
        {"name": "gate",           "kind": "gate",
         "values": [{"threshold": 0.05, "attainable_range": [0, 0.14],
                     "eligible_count": 96}]}
      ],
      "statistic": {"name": "<preregistered statistic>",
                    "relevance_floor": {"smd": 0.2},
                    "direction": "higher_is_better"}
    }

Axis kinds are a closed set: parameter | null | representation |
stochastic | implementation | gate | world | measurement. An unknown kind
fails closed (DFX-4), in Kairos's reader, not in the engine.

Every member experiment's `spec` carries `"kairos_point": {"<axis>":
<value>, ...}` naming its coordinates. The reader joins members to axes
by that key. A member with no point is UNASSIGNED and is reported, never
guessed (mirrors "a member with no arm is unassigned").

## 4. The surface record (roles/Kairos/science/surfaces/<family_id>.json, committed)

    {
      "family_id": "...", "hypothesis": "...", "base_exp_id": "...",
      "built_from": {"base_sha": "...", "branch": "...", "worktree_path": "..."},
      "axes": [...as declared...],
      "points": [
        {"exp_id": "...", "point": {"density": 0.3, "null_family": "permutation"},
         "outcome": "FALSIFIED", "statistic_value": 0.02, "se": 0.011,
         "engine_findings": ["CONFIG_DIVERGENCE"],
         "region": "IMPLEMENTATION_DEPENDENT",
         "why": "attested config diverged from sealed spec; outcome not attributable to the axis"}
      ],
      "regions": {
        "SURVIVES": [...point ids...], "WEAKENS": [...], "DISAPPEARS": [...],
        "REVERSES": [...], "UNMEASURABLE": [...], "IMPLEMENTATION_DEPENDENT": [...],
        "UNTRIED": [ {"point": {...}} ... ]
      },
      "boundaries": [
        {"axis": "density", "between": [0.3, 0.4],
         "from": "DISAPPEARS", "to": "SURVIVES",
         "evidence": ["exp_a", "exp_b"]}
      ],
      "neighbours_proposed": [
        {"point": {"density": 0.35}, "reason": "bisect the density boundary",
         "would_change": "whether the boundary is sharp or graded"}
      ],
      "eligibility": {"points_declared": 30, "points_run": 12, "points_untried": 18},
      "controls": {"positive": "<exp id or fixture>", "cheat": "<...>", "negative": "<...>"},
      "kairos_receipt": "roles/Kairos/journal/<date>.md#<anchor>"
    }

Region assignment rules (deterministic; the reader is a predicate, not a
model):

    engine finding CONFIG_DIVERGENCE | NO_EXECUTION_ATTESTATION
      -> IMPLEMENTATION_DEPENDENT (takes precedence over outcome)
    two points with identical coordinates and different outcomes
      -> IMPLEMENTATION_DEPENDENT for both (with the executor hashes)
    statistic pinned at the measurement's declared range edge
      -> UNMEASURABLE
    outcome SURVIVED and |value| >= floor            -> SURVIVES
    outcome SURVIVED and |value| <  floor            -> WEAKENS
    outcome FALSIFIED and sign(value) != sign(base)  -> REVERSES
    outcome FALSIFIED and |value| < se               -> DISAPPEARS
    outcome FALSIFIED otherwise                      -> WEAKENS
    outcome INCONCLUSIVE                             -> UNTRIED-equivalent,
                                                        listed separately
    declared point with no member                    -> UNTRIED

A boundary is emitted between two adjacent points on one axis whose
regions differ, with the other coordinates held equal. A proposed
neighbour is the midpoint (numeric axis) or the untried value (categorical
axis) at every boundary. That is the whole automation: the map names the
next experiments; a human or a deterministic queue policy issues them.

## 5. Controls the reader must ship with (base rule 3)

    negative  a family whose points all SURVIVE at equal statistic:
              zero boundaries, zero neighbours proposed
    positive  a family with one planted boundary on one axis: exactly one
              boundary, exactly one neighbour, at the planted place
    cheat     a family whose manifest declares axes but whose members
              carry no kairos_point: the reader must report every member
              UNASSIGNED and propose NOTHING (presence of the axis list is
              a label; the property is the join)

## 6. What this is not

Not a verdict. A surface has no status word. It is a map that a claim's
owner, Harmonia (sizing, representation), Charon (a ruling, if one is
asked for) or the operator reads. Kairos proposes neighbours; it does
not enqueue them into another seat's world (lane discipline).
