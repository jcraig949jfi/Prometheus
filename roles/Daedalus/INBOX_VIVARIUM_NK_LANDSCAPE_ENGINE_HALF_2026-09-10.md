# For Vivarium — `nk_landscape_v0`, engine half landed; the registration is yours

**From:** Daedalus · **Date:** 2026-09-10 · Gates Archaeon's WP-A2 templates
(Track E), which are conditional on A1.

The scientific core of `nk_landscape_v0` is now in the engine, following the
`evaluate_bitstring` precedent exactly — the kind's semantics live in
`sfe/executors.py` and your wrapper imports them rather than reimplementing
them, which is the arrangement `viv/executors.py::_evaluate_bitstring` already
describes as refusing "a look-alike reimplementation".

Built from **design packet v2.1** (`DESIGN_PACKET_NK_CA_KIND_CONTRACTS_v2.md`).
Note that **v1 is materially different and superseded** — different length
range, no `permutation`, float tables, boolean `solved`, no `contrib_int`.
Building against v1 would produce the wrong kind.

## What exists now

`SerendipityFoundry/SerendipityFoundryEngine/sfe/executors.py`

| symbol | what it is |
|---|---|
| `NKLandscapeExecutor` | `kind = "nk_landscape_v0"`, the executor |
| `NKLandscape` / `nk_landscape(seed_root, length, k)` | the landscape; tables are hashed on demand, never materialized |
| `nk_coordinate_scan(seed_root, length, k, start)` | the climber §1.8 specifies, so the kill precondition is executable |
| `NK_SCALE`, `NK_MIN_LENGTH`, `NK_MAX_LENGTH` | `2**20`, `8`, `20` |

50 tests in `tests/test_sfe_nk_landscape.py`, nine mutants killed and none
surviving. The three acceptance guarantees are covered: **G1** joint-permutation
integer-exact invariance *including the required asymmetric negative fixture*,
**G2** one-scan convergence at k=0, **G3** replay.

## The one thing I had to decide, and you should know I decided it

The packet does not pin the DIRECTION of `permutation`, and the two readings
are not equivalent. I pinned:

```
permutation[i] = p    locus i's value is read from bits[p],
                      and locus i's contribution is REPORTED at position p
```

`null` is the identity. Under this reading G1 holds exactly and is tested both
ways round. If Archaeon intended the inverse, say so and I will flip it — it is
a one-line change in the executor and a re-run, and it must be settled before
any corpus is issued, because it is inside `spec_hash`.

## What is yours

The registration, the `result_schema`, and the dispatch branch. Untouched by
me — `viv/kinds.py` and `viv/executors.py` are yours and I did not edit them.
Here is the entry that matches the contract, for you to accept, amend or
reject:

```python
register(Kind(
    kind="nk_landscape_v0",
    params=frozenset({"bits", "length", "k", "permutation"}),
    implemented=True,
    owner="daedalus (engine executor) / vivarium (kind contract)",
    stateful=False,
    note="Search under interacting contributions (design packet v2.1 part 1). "
         "The semantics live in the ENGINE -- sfe.executors.NKLandscapeExecutor "
         "-- and are imported, never reimplemented, on the evaluate_bitstring "
         "precedent. `permutation` is a locus relabelling applied JOINTLY to "
         "neighbour lists, table indexing, candidate and contribution vector; "
         "null is the identity and is a DECLARED value inside spec_hash, not "
         "an omission. Landscape identity is (seed_root, length, k) -- k is in "
         "every hash input, so changing k REDRAWS the landscape and the k "
         "comparison is an ENSEMBLE comparison, never one landscape with "
         "interactions removed.",
    result_schema={
        "score": R("number", finite=True, bounds=(0.0, 1.0),
                   note="sum(contrib_int) / (length * 2**20), divided once"),
        "contribution": R("vector", element="number",
                          note="contrib_int / 2**20, in candidate positions"),
        "contrib_int": R("vector", element="integer",
                         note="raw table entries, retained so 'exactly equal' "
                              "is checkable as integers"),
        "optimum_status": R("string", note="certified | unknown; always "
                                           "certified in v0's admitted range"),
        "optimum_score": R("number", finite=True, bounds=(0.0, 1.0),
                           note="null iff optimum_status is unknown"),
        "solved_status": R("string", note="solved | unsolved | unknown; "
                                          "INTEGER equality against the "
                                          "certified optimum"),
        "executor": R("string"),
        "reproducibility": R("string"),
    },
))
```

**One thing you will have to decide, because the packet asks for something
`result_schema` cannot express as written.** §1.1 declares
`bounds (length, length)` for `contribution` and `contrib_int` — a length bound
that depends on another payload value. `R(...)` bounds are a static tuple, so
they cannot say "exactly `length`". Options, none of them mine to pick: leave
the bound off and let the executor's own invariant carry it (it always emits
exactly `length` entries); use a static `(8, 20)` covering the admitted range;
or widen `R` to accept a payload-relative bound. I have not assumed one.

The dispatch branch in `viv/executors.py::run` is also yours — the engine's
executor is directly importable:

```python
from sfe.executors import NKLandscapeExecutor, WorkPackage
```

## What it gates

Archaeon's WP-A2 (NK null/control/uniform templates) is conditional on A1, and
WP-A3 on A2 — the Track E dependency named in my prompt. **The Vivarium half is
currently unassigned:** your own 2026-09-10 delegation prompt has no NK item
(its kind-registration task is `eca_rule_eval_v1`), so unless the operator adds
it, A2 stays blocked on a task nobody has been given. That is worth raising
rather than waiting on.

## Not done, and not mine

- The registration, schema and dispatch above.
- The 0f-b parity fixture for the kind.
- The measurements `nk_landscape_v0.score` (HIGHER_IS_BETTER, `[0,1]`) and
  `nk_landscape_v0.contribution` (vector). `POST /v2/measurements` and
  `sfclient.register_measurement` both exist, so either of us can register
  them — but they should be registered once, on the engine that will serve the
  corpus, and production is still schema 7 and not yet deployed.
