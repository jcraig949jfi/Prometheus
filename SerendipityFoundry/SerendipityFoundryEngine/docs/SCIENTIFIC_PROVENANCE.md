# Scientific provenance — SFE schema v6

**Status:** v6 shipped 2026-09-05; **schema v7 added 2026-09-06** (measurement
identity and meaning, the cross-seat read contract, and family structure
surviving fossilization — §12). API `v2` throughout; every migration is purely
additive and back-fills nothing.
**Nothing in this release changes an existing contract.** Every field is
optional, every route is new, and an unmodified v5 client keeps working with
byte-identical results.

---

## 1. The one rule

Everything here obeys a single boundary:

> The engine compares **hashes**, **counts** distinct things, and checks
> **containment** of declared sets. It never computes a variance, fits a model,
> chooses an estimator, or judges whether a design was adequate.

Where an answer would need statistical interpretation, the engine records the
**declaration** and the **provenance**, and stops. The scientist keeps the
science. Concretely, the engine will tell you that your source set contains 8
distinct worlds when you declared n=128; it will never tell you which number is
correct for your question.

That boundary is not decoration. Four checks in this release were deliberately
built weaker than they could have been, because the stronger version would have
required the engine to interpret a result — see §8.

---

## 2. Why any of this exists

Five things were true of v5 and are no longer:

| | v5 | v6 |
|---|---|---|
| A campaign, comparison or analysis family | **inexpressible** — every scientific table declares `world_id NOT NULL`, and these span worlds by definition | `families` / `family_members` |
| "The survivor of twelve" vs "the only one I ran" | **the same record** | `selection_visible`, and the losers are recorded |
| What the executor actually ran | **never held** — the engine had `spec_hash` (requested) and nothing else | `executed_config_hash` and three sibling attestations |
| "Bounded below a declared relevance floor" | storable only as `SURVIVED` (ambiguous) or `INCONCLUSIVE` (destroys the information) | `SUCCESSFUL_NEGATIVE` |
| A perturbation that changed nothing | **indistinguishable** from one that worked — interventions were recorded verbatim and nowhere else | `NO_EFFECTIVE_INTERVENTION` |

And one thing about the engine itself: two engines could report an **identical**
`engine_source_hash` and still behave differently, because the enforcement modes
were launch arguments that appeared in no response. Build identity answers
*what code*; it never answered *under what rules*. Both are now on
`GET /v2/version` — along with `engine_instance_id`, the identity of the
**ledger** (minted once per database, so it travels with the substrate rather
than the filesystem path) as distinct from the identity of the **build**. If you
hold an anchor, that is the field that says which engine minted it; previously
you could only get it from `verify-anchor` or by parsing a session key.

---

## 3. `--science-profile off | warn | strict`

One graded flag for the whole bundle, reported on `/v2/version`.

| profile | behaviour |
|---|---|
| `off` | The checks are **not computed**, not recorded, not reported. The engine behaves exactly as v5 did. |
| `warn` | **Default.** Computed, returned in a `science.profile_findings` list, and **sealed into the event chain**. Never blocking. |
| `strict` | The same findings, but one that **contradicts a declaration the caller itself sealed** fails the call. |

`off` is a genuine control arm rather than a mute button. That matters: an
`off` / `warn` comparison measures the feature, not two different engines. And
`warn` and `strict` must agree on every **fact** and differ only in
**consequence** — there is a test asserting exactly that, because if they ever
disagreed on the facts the flag would be two engines wearing one name.

**M1 runs `warn`.** Nothing you send can be refused by a v6 check on M1 today.

Two rules are enforced in **every** profile, `off` included, because they are
structural coherence rather than science:

* `SUCCESSFUL_NEGATIVE` without a `relevance_floor` — the claim *is* about the
  bound, so without the bound there is no claim.
* Closed vocabularies (family kinds, member kinds, roles, claim statuses,
  replication dimensions, units of analysis, attestation fields) fail closed on
  an unknown value, as all scientific control configuration does (DFX-4).

---

## 4. Families — the first cross-world container

`POST /v2/families` `{kind, manifest, name?}`
`GET /v2/families` · `GET /v2/families/{fid}`
`POST /v2/families/{fid}/members` `{member_kind, member_id, role?}`
`POST /v2/families/{fid}/close`

* `kind`: `campaign` | `analysis` | `comparison` | `selection`
* `member_kind`: `experiment` | `analysis` | `world` | `claim`
* `role`: `planned` | `executed` | `abandoned` | `selected` | `alternative`

`family_members.world_id` is **nullable on purpose** — an analysis or a claim
belongs to no single world, and that is the whole reason the table is not
world-scoped. Every other scientific table keeps `world_id NOT NULL`; families
is the exception, and there is a test asserting it stays the only one.

`manifest` is freeform and **sealed by hash at creation**, never rewritten. The
engine reads exactly one convention inside it: an integer `planned_members` (or
`planned_experiments`) is compared against the members actually recorded.

**Membership roles are append-only.** Re-adding a member with the same role is
an idempotent no-op; re-adding it with a *different* role is a `409`. A member
quietly moving from `alternative` to `selected` after the results are in is
precisely the rewrite this table exists to prevent.

`GET /v2/families/{fid}` returns a census: `member_count`, `by_role`,
`by_kind`, `worlds_spanned`, and

```
"selection_visible": true    // iff >=1 selected AND >=1 alternative
```

Findings: `FAMILY_EXTENT_DIVERGENCE` (declared extent ≠ recorded),
`MULTIPLE_SELECTED`, `SELECTION_WITHOUT_ALTERNATIVES`.

The last one deserves a sentence. A family with one survivor and no recorded
alternatives is not a lie — but it is not a selection family either, and the
engine says so rather than letting a reader supply the missing assumption. The
provenance that makes best-of-N legible is *the losers*.

**Isolation.** A member owned by another client resolves to **not found**, never
to *access denied*. A denial would turn family membership into an existence
oracle for another client's substrate (I5). Same reasoning as §6's unresolved
sources.

---

## 5. Analysis = an experiment with a declared source set

There is **no parallel analysis object**. An analysis has a specification, is
sealed by `spec_hash`, crosses the same irreversible commit boundary, is
order-proved by `committed_seq`, and must not be edited once its result is
known. The experiment lifecycle already provides every one of those; a second
stack would have had to reimplement them all and then be kept in step forever.

```
POST /v2/worlds/{wid}/experiments
{
  "spec": {"procedure": "hedges_g", "tested_domain": ["landscapeA"]},
  "unit_of_analysis": "world",        // observation | experiment | world
                                      // | seed_root | topology_group
  "declared_n": 8,
  "source_set": ["obs_…", "obs_…", …] // all three, or none
}
```

The engine:

1. hashes the source set — **order-independent and world-independent**, so the
   same evidentiary base hashes identically no matter who assembled it, in what
   order, or in which world the analysis was registered. That is what makes
   "these two analyses used the same sources" a comparison rather than a claim;
2. **counts distinct units** under your declared key;
3. seals `ANALYSIS_REGISTERED` into the world's chain with declared vs verified;
4. returns an `analysis` block, and reports `unit_mismatch`.

```
"analysis": {"unit_of_analysis": "world", "declared_n": 8, "verified_n": 8,
             "sources_submitted": 128, "sources_unresolved": 0,
             "unit_mismatch": false, "source_set_hash": "sha256:…"}
```

128 observations drawn from 8 worlds are **n=8** under `world` and **n=128**
under `observation`. Counting distinct units under a declared key is counting,
not statistics — and it is the whole difference.

**Only the hash is stored, not the set.** Put the set itself in `spec` if you
want it recoverable; there `spec_hash` seals it at commit. Consequently
`GET /v2/worlds/{wid}/experiments/{eid}/analysis` reads the **sealed** event
back rather than recomputing — the verification is a fact recorded at
registration inside the hash chain, not a number regenerated later from state
that may have moved underneath it.

**The durable marker of an analysis is `source_set_hash`, not the work item's
`kind`.** `kind` only exists once an experiment is committed with `enqueue`, so
a registered-but-uncommitted analysis would otherwise have no identity.
`is_analysis` on the experiment read is derived from it.

**Sources owned by another client count as `unresolved`, not as a denial** —
same existence-oracle reasoning as §4. That has a useful side effect: a
cross-client analysis silently *undercounts*, and the declared-vs-verified check
then makes the undercount visible.

Under `strict`, a `unit_mismatch` fails the registration, and the whole
registration rolls back — a strict engine never holds a half-declared analysis.

---

## 6. Executed-config attestation

The largest provenance hole in v5. The engine held the **requested**
configuration — `spec_hash`, sealed at commit and order-proved by
`committed_seq` — and never held the **executed** side, so a run that quietly
used different parameters returned a result the ledger could not distinguish
from a faithful one.

```
POST /v2/work/{work_id}/complete
{
  "worker_id": …, "claim_id": …, "result": {…},
  "attestation": {
    "executed_config": {"noise": 0.0, "steps": 100},   // OR executed_config_hash
    "entry_state_hash":          "sha256:…",   // what the player ENTERED holding
    "player_identity_hash":      "sha256:…",   // which build of the agent
    "measurement_identity_hash": "sha256:…"    // which scorer / regime
  }
}
```

Send `executed_config` and the engine hashes it with the **same
canonicalization that produced `spec_hash`** — so a faithful executor matches by
construction and has to do nothing special. Send `executed_config_hash` instead
if you will not disclose the config. **Never both**: two sources for one fact is
exactly the ambiguity this closes (`422`).

Findings: `CONFIG_DIVERGENCE` (attested ≠ sealed) and
`NO_EXECUTION_ATTESTATION` (nothing to compare). Under `strict`, both are `409`
and the result is **not recorded** — a strict engine never holds a completion it
could not vouch for.

`GET /v2/work/{work_id}/attestation` returns the executed side beside
`requested_config_hash` and a `config_match` boolean (`null` when the work item
is not an experiment — the engine reports nothing it cannot compare).

A replay carrying a **different** attestation is a `409`, matching the existing
rule for a replay carrying a different result.

**`entry_state_hash` — read the limit before you trust it.** The engine never
sees player state and can never know whether a reset actually happened. It
checks a *declared* discipline against an *attested* hash: a claim against a
claim, both sealed. That is worth much more than nothing and much less than
verification. In particular, **a converged leaker enters every world from the
same fixed point**, so its entry hashes become indistinguishable from an honest
reset. An engine reporting "independence verified" there would manufacture
exactly the looks-good failure this release exists to prevent, so it does not
report that.

---

## 7. Claims

```
POST /v2/claims
{"estimand": "…", "status": "SUPPORTED",
 "family_id": …, "analysis_exp_id": …,
 "relevance_floor": {"smd": 0.2},
 "replication": {"new_world_draws": true, "reimplemented": false},
 "transport_domain": ["landscapeA"]}
```

`GET /v2/claims` · `GET /v2/claims/{clm}` · `POST /v2/claims/{clm}/retract`

A claim is deliberately **not** a world record: it cites an analysis, which
cites observations, which live in worlds. Binding it to one world would force
every multi-world conclusion to pick a world to lie in.

**`SUCCESSFUL_NEGATIVE`** is a new epistemic state, not a statistical one. The
engine stores the conclusion the experimenter reached, exactly as it already
does for `FALSIFIED` / `SURVIVED` / `INCONCLUSIVE`; it judges no equivalence
test. It enforces one thing: the floor must be declared.

**`replication` is compositional and never an ordinal.** Two replication
ladders were proposed two loops apart on *different axes* — L0–L4
(sequence / terminal / distribution / ranking / phenotype) and L1–L6
(resampling / world-distribution / landscape / implementation / player-build /
full). Encoding either as a rank would hard-code a taxonomy that has already
moved once. Independent booleans survive the taxonomy changing, and any ladder
anyone prefers is derivable from them. The dimensions are
`resampled_noise`, `new_world_draws`, `new_landscape`, `reimplemented`,
`rebuilt_player`, `independent_team`.

**An undeclared dimension is not a `false`.** It was not asserted either way,
and recording it as `false` would manufacture a negative claim nobody made.

**`transport_domain`** is checked for containment against the cited analysis's
`spec.tested_domain`. `TRANSPORT_OVERREACH` lists the excess;
`TRANSPORT_UNCHECKABLE` fires when no `tested_domain` was declared, because
silence would read as approval. The engine asserts nothing about whether a
result transports — it reports that you claimed it holds somewhere you never
tested. Under `strict`, both `TRANSPORT_OVERREACH` and
`CLAIM_CITES_NON_ANALYSIS` are `422`.

**Retraction preserves the original `content_hash`.** A claim made and withdrawn
is a different fact from a claim that never existed. `RETRACTED` is a
transition, never an origin state (`422` if you try to create one).

`NO_REPLICATION_DECLARED` is reported and **never enforced, in any profile** —
strict does not turn a missing declaration into a mandate.

---

## 8. `NO_EFFECTIVE_INTERVENTION`, and where the engine stays silent

Interventions were recorded verbatim in `WORLD_FORKED` and nowhere else, so a
perturbation that changed nothing was indistinguishable from one that worked.
Two deterministic tests, no statistics, and **both always run**:

1. **Declared before/after.** Send `intervention_effect: {"before": …,
   "after": …}` on a fork child. If the two content-hash identically, the
   intervention changed nothing.
2. **Engine-visible fields.** For `seed_root`, `sharing_policy` and
   `topology_group`, the engine compares the child's resulting value against
   both the parent's value and the intervention's declared value —
   `NO_EFFECTIVE_INTERVENTION` when the child simply inherited, and
   `INTERVENTION_NOT_APPLIED` when the fork does not actually carry what the
   intervention declared.

**They are independent evidence, so a fork can return more than one finding —
read `profile_findings` as a list.** Test 1 is the claimant's own account of two
states; test 2 is the engine's own observation. A *differing* before/after pair
is not evidence that the intervention reached the fields the engine can see, and
until 2026-09-06 it was treated as though it were: declaring
`intervention_effect` returned early and made `INTERVENTION_NOT_APPLIED`
unreachable. The incentive that created was exactly backwards — disclosing more
bought *less* checking, so the careless caller was caught and the conscientious
one was not. A check that punishes disclosure is worse than no check.

**Where an intervention names something the engine cannot see — a noise
parameter inside a player, a changed reward shaping — the engine returns
nothing at all.** Not "verified", not "unknown-but-probably-fine": nothing.
Silence is the honest answer; a reassurance it has not earned would manufacture
the very failure mode this release targets. There is a test asserting the
engine stays quiet on an opaque intervention.

Warning by default. It becomes **fatal** when the fork's own manifest declares
`intervention_effective: true` and the arithmetic disagrees — the engine is not
overruling a scientist, it is refusing to record a fork whose declaration
contradicts itself. Under `strict`, an inert intervention is refused even
undeclared, and so is one the engine can see was never applied. A fork with no interventions at all is never flagged: a plain
replicate is not a failed intervention.

---

## 9. Wire and schema summary

**`GET /v2/version` now carries the rules, not just the build:**

```json
{"api":"v2","schema_version":6,"runtime":"serendipity-foundry-sfe",
 "registration_open":true,
 "session_enforcement":"advisory",     // the rules, not just the build
 "science_profile":"warn",
 "engine_instance_id":"eng_…",         // identity of the LEDGER
 "engine_source_hash":"sha256:…",      // identity of the BUILD
 "source_commit":"…"}
```

`source_commit` is best-effort git metadata naming the working tree's HEAD and
**may name a tree that cannot reproduce the build**. `engine_source_hash` is
computed from the loaded source at import and is the authoritative build
identity — compare that one.

**Eleven new routes**, all inside the session-affinity perimeter (a container
that spans worlds must not span *engines*): five families, four claims,
`GET /v2/work/{id}/attestation`,
`GET /v2/worlds/{wid}/experiments/{eid}/analysis`.

**New tables:** `families`, `family_members` (`world_id` nullable), `claims`.
**New columns:** `work_items.{executed_config_hash, entry_state_hash,
player_identity_hash, measurement_identity_hash}`,
`experiments.{unit_of_analysis, declared_n, source_set_hash}`.

**New events:** `ANALYSIS_REGISTERED` (world chain), `FAMILY_CREATED`,
`FAMILY_MEMBER_ADDED`, `FAMILY_CLOSED`, `CLAIM_RECORDED`, `CLAIM_RETRACTED`
(the global `foundry_events` ledger, `scope_kind` = `family` / `claim`).
`WORK_COMPLETED` and `WORLD_FORKED` now carry a `finding` in their payload when
one fired — findings are **sealed**, not merely returned.

**Migration back-fills nothing.** A pre-v6 work item has `NULL` attestation
hashes because no executor ever attested anything; inventing a value would
manufacture a provenance claim that was never made. Same reasoning that left the
v5 `LEGACY` sessions unbound rather than guessing at bindings.

---

## 12. v7 — measurement meaning, cross-seat reads, family in the fossil

**Measurement.** `observations.content` is freeform, so nothing said which
field was the outcome — the gap behind §1's loudest decline. A registered
measurement now declares `value_path` (a dotted **address**, never a query: a
query language would let a measurement select its own value, and choosing which
of several values counts is interpretation), plus `direction`, `unit` and range.
`identity_hash` is derived from the definition, so
`work_items.measurement_identity_hash` resolves to a registered oracle instead
of being comparable only with itself. `(name, version)` is UNIQUE and never
silently replaced.

**Cross-seat reads.** Every read route is owner-scoped, which made an
archaeologist impossible: its only recourse was to open the SQLite file, a read
with no tenancy filter, no evidence-class filter and no schema guard. A read
grant is scoped to a **topology group** — already an unguessable server-issued
capability — grantable only by that group's creator, **read only**, revocable
with the revocation recorded. It lives on a separate `/v2/read/*` surface and
does **not** widen the owner-scoped routes, so an ordinary read can never
quietly begin returning another tenant's rows. An ungranted group returns empty
rather than 403, for the same anti-oracle reason a foreign family member is 404.
`/v2/read/observations` returns the corpus census — tenancy, evidence classes,
truncation — beside the rows, because an archaeologist's first obligation is to
say what population it drew from.

**Family and arm survive fossilization.** The audit envelope is the only thing
that leaves the engine as one verifiable object, and family membership stayed
behind in a table the fossil's reader has no credential for — so best-of-N went
invisible exactly when the record left the building. The envelope now carries a
`families` block **by value**: role, arm, member count, selected/alternatives,
and `selection_visible`. It is inside `envelope_hash`, so a fossil cannot be
re-attributed to a different family after export without breaking its own seal.

The **arm label is read from the sealed spec**, at a key the family's manifest
declares (`arm_key`, default `arm`). Two consequences, both deliberate: the
engine never guesses which key means arm, and a world member resolves to
`unresolved` rather than a count — worlds have no spec, and a label that can be
reassigned after the results are in is the thing this prevents.

---

## 10. What the engine still refuses to do

Unchanged, and reaffirmed by this release. Multiplicity correction, null
calibration, stopping rules, estimator choice, power thresholds, whether a sweep
was sufficient, whether an equivalence test is valid, and whether a claim's
`replication` declaration is adequate. Fields exist for `relevance_floor`,
`transport_domain`, `replication` and the estimator (inside your `spec`); **none
of them is enforced.**

One item is deliberately *not* built, and the reason is recorded rather than
hidden: a degenerate-replication detector that fires on identical content hashes
catches a **converging** state leak and misses a leaker that does not converge —
correlated-but-not-identical outcomes are visible only to variance or
correlation, which is on the far side of the boundary. The honest response is to
state the detector's domain, not to reach for variance. That case remains
Harmonia's.

---

## 11. Verifying

```bash
cd SerendipityFoundry/SerendipityFoundryEngine
python -m pytest tests/ -q          # 236 tests
python -m pytest tests/test_sfe_v6_science.py -q   # 65, this release
```

Every v6 test is **paired**: each detector is exercised once on input that
should trip it and once on input that should not, differing in the one thing
under test. A finding that only ever fires is evidence that the detector fires,
not that it works. The suite was mutation-checked — blinding the intervention
detector, the unit counter, the config comparison and the relevance-floor rule
turns 17 tests red.

| | |
|---|---|
| Client guide, all routes | `integration/SFE_CLIENT_GUIDE.md` |
| Session affinity (v5) | `SerendipityFoundryEngine/docs/SESSION_AFFINITY.md` |
| Reconstructing the record later | `integration/SFE_ARCHAEOLOGY_SCHEMA.md` |

The Engine's own `/v2/openapi.json` is authoritative over all of the above.
