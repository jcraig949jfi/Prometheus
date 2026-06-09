# Techne Substrate Fire Log — 2026-06-05

## v3c forward path closed — predicate_kind is now a self-describing schema field

**Context on entry.** The 2026-06-03 calibration v3c fix shipped a production
guard in `content_aware_promote.py` that excludes meta-relational generators
(g4/g5/a3) from the raw-value F2 null — but it resolved their class via a
`generator_id` denylist (`META_RELATIONAL_GENERATORS = {g4,g5,a3}`). The fire
log filed the forward path explicitly: "generators stamp `predicate_kind` on
emission + a record_schema field, so the filter never depends on a generator_id
denylist." Inbox is stale (newest 2026-05-22), so this was the live owed item.

**Change shipped.** Mirrored the existing `role: GeneratorRole` declarative
pattern rather than hand-editing 60+ payload dicts:

- `record_schema.py` — `TheseusRecord` gains first-class `predicate_kind:
  Optional[str] = None` (the "record_schema field"). It does NOT enter
  `record_id` (id = `hash(generator_id|canonical_text)`), so the addition is
  content-address-stable: zero churn on existing corpora.
- `generators/base.py` — `Generator.predicate_kind: str = "direct"` class
  attribute (default = the only predicate F2's raw-value null is valid for).
- `g4`/`g5` set `predicate_kind = "invariance"`, `a3` set `"transformed"`,
  and stamp `predicate_kind=self.predicate_kind` at record construction.
- `is_direct_relation_record()` resolution order is now payload override →
  **record schema field** → generator_id denylist. The denylist is demoted to
  a LEGACY FALLBACK for un-stamped pre-v3c records only.

**The point of the change (not just hygiene):** a *new* meta-relational
generator now only needs to set the `predicate_kind` class attribute — it does
NOT need to be added to the denylist, and it will still be excluded correctly.
The filter's primary path is self-describing. Test
`test_schema_field_independent_of_denylist` pins this: a generator id NOT in
`META_RELATIONAL_GENERATORS`, stamped `"invariance"` via the schema field, is
still excluded.

**Verification.**
- 5 new guard tests added (schema-field honored, denylist-independence,
  payload-beats-field precedence, legacy-fallback, and a live-generator
  integration test that g4/g5/a3 instances stamp the field). 20/20 green.
- Full theseus suite: 562 passed, 1 skipped, 0 regressions.
- Serialization round-trip verified: stamped record → `to_jsonl` →
  `TheseusRecord(**json.loads)` preserves `"invariance"`; a legacy line with
  the key removed loads to `predicate_kind=None` (denylist fallback path).

**Backwards-compat ledger.** All loaders share one schema module and use
`TheseusRecord(**data)`; an Optional field defaulting to None loads old records
unchanged. New records carry the key; cross-machine, the co-researcher machine
must pull before reading new corpora (standard append-only-schema caveat).

**Doctrine:** assume-wrong / kills-are-the-output (this hardens the artifact
that *refused* a false coupling) ✓; backwards-compat + behavior-preserving
tests mandatory for substrate primitives ✓; pivot stack green before commit ✓;
take-a-stand (chose declarative class-attribute pattern over 60 brittle payload
edits) ✓.

**Forward path (filed, not run).** The owed v3 per-generator audit named g4/g5/a3
as the only bias injectors among non-mutated records; with `predicate_kind` now
on the schema, the natural next step is to have the *other* relational families
(a1, f-family) stamp `"direct"` explicitly too, so the denylist fallback can
eventually be retired entirely once corpora are re-emitted. Low priority — the
fallback is correct and the default already classifies them right.
