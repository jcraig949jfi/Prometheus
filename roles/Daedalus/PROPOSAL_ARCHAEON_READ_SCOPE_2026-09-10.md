# Proposal: the smallest engine read grant for Archaeon

**Daedalus, 2026-09-10. Decision B1, open since 2026-09-08.**
**FOR THE OPERATOR. Nothing here has been issued** — no client registered, no
scope created, no grant made.

## The situation

Archaeon holds no engine credential. It reads results through Vivarium's queue
projection (`archaeon/vivqueue.py`), which is a *derived* view: it carries what
the queue chose to record, and it is one seat's rendering of another seat's
ledger. Two consequences that matter for a seat whose job is provenance:

- Archaeon cannot see the engine's **sealed** record — `entry_hash`, the event
  chain, the audit envelope — only the queue's copy of the outcome.
- Its own `fossils.py` guard checks `expected_schema_version`, so it already
  reasons about the engine's schema while having no way to *ask* the engine.

## What a read grant is, and what it deliberately is not

v7 added read scopes (`sfe/runtime.py`: `create_read_scope`, `add_scope_worlds`,
`grant_read`, `revoke_read`, `read_worlds`, `read_observations`).

**A scope is a curated set of the owner's OWN worlds, and nothing else.** It was
deliberately not keyed on `topology_group`, because `_may_cross` gates on that
field — so scoping a read grant to a topology group would have silently
conferred **artifact-import eligibility**, turning "you may look" into "you may
take a copy into your own world". That was the design's sharpest decision and it
should survive this proposal: a read grant confers reading, and confers it on an
enumerated set of worlds.

What a grant does **not** give: write access, work claiming, artifact import,
budget consumption, or visibility of worlds not explicitly added to the scope.

## Options, least privilege first

### Option 0 — do nothing. Keep the queue projection.
**Cost:** Archaeon's provenance claims stay one hop from the evidence, and it
cannot independently verify a seal it is asked to attest to. **Recommend
against**, but it is a real option and it is free.

### Option 1 — a read scope over the campaign worlds Archaeon already issued
The producer *created* these candidate sets; the worlds exist because it asked
for them. A scope containing exactly those worlds gives Archaeon the sealed
version of what it can already see derived.

```
POST /v2/read-scopes            name="archaeon-campaigns"      -> scope_id
POST /v2/read-scopes/{id}/worlds  world_ids=[... the campaign worlds ...]
POST /v2/read-scopes/{id}/grants  grantee_client_id=<archaeon>  -> grant_id
```

**Exposes:** observations and world metadata for the enumerated worlds.
**Does not expose:** anything not enumerated; no import; no writes.
**Maintenance:** the scope must be *extended* per campaign. That is the cost,
and it is also the safety property — a scope that never needs touching is a
scope nobody is checking.
**This is my recommendation.**

### Option 2 — a role-scoped standing grant over all producer-origin worlds
One grant, no per-campaign maintenance. Requires either a new selector ("worlds
whose creating client is X") or a scope someone keeps current. The engine has no
such selector today, so this is **new engine work**, and it re-introduces the
thing scopes were built to avoid: a membership rule evaluated at read time
rather than an enumerated list someone decided on.
**Recommend against** unless per-campaign maintenance actually proves unbearable.

### Option 3 — a read-only credential over the whole ledger
Simple and wrong. There is no "read everything" grant, it would have to be
built, and it would make every future isolation guarantee conditional on one
token's confidentiality.
**Recommend against.**

## Credential lifecycle — and the gap that should gate this

Today: `POST /v2/clients` issues a token, shows it once, and that is the whole
lifecycle. **There is no rotation, no expiry, and no revocation.** A read grant
can be revoked (`revoke_read`), but the *credential* cannot — so if Archaeon's
token leaks, the remedy is to revoke every grant that names it and issue a new
client, orphaning the old principal in every record that mentions it.

Proposed lifecycle, in the order I would build it:

1. **Issue** a client `archaeon-reader`, distinct from any writer principal, so
   the records say which capability was used.
2. **Scope** per Option 1, extended per campaign by the owner of those worlds.
3. **Revoke** — available today at the grant level. Use it as the routine
   control: expire a campaign's grant when the campaign closes rather than
   letting scopes accumulate.
4. **Rotate** — *does not exist* (backlog C6/D8). Until token revocation exists,
   the grant is the only revocable thing, which is an argument for Option 1's
   narrow enumerated scope rather than against the grant itself.

**My recommendation to the operator:** issue Option 1, with the grant reviewed
when each campaign closes, and treat token revocation (C6) as the follow-up that
makes this comfortable rather than merely acceptable.

## What I need before issuing

1. The operator's word — this proposal does not authorise itself.
2. Archaeon's client id, or authority to register `archaeon-reader`.
3. The world list, from whoever owns those worlds. I should not choose which
   worlds Archaeon may read; the owner should.
