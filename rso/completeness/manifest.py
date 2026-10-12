"""C-018-T011 experiment MANIFEST: the frozen statement of what the complete experiment is (engine-agnostic).

A manifest is a plain JSON object, sealed by `manifest_sha256` over every other field:

    schema, experiment_id, arms[], row_key_fields[], seed_field,
    shards[]      {id, seeds[], arm_counts{key: n}, rows, rows_sha256, meta_sha256}
    sources{}     {path: sha256} of the code that produced / will read the evidence
    early_stop    null, or {rule_id, preregistered_in, skippable[shard ids], trigger{where{field: value}, at_least}}
    manifest_sha256

`key` of a row = "|".join(str(row[f]) for f in row_key_fields) (the arm, and for Z80 the forgery kind). Expected execution
count per arm is the sum of arm_counts over shards. A caller that must not be fooled by a re-sealed, smaller manifest passes
`pinned_manifest_sha256` to verify(): the seal only proves the manifest was not edited, the pin proves it is THE manifest.
"""
import hashlib
import json

SCHEMA = "prometheus.rso.completeness.manifest.v1"


def canonical(obj):
    """JSON, sorted keys, no whitespace, UTF-8 (same bytes as rso/slice001/receipt.py:116 canonical_bytes for float-free data)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def seal(m):
    body = {k: v for k, v in m.items() if k != "manifest_sha256"}
    return dict(body, manifest_sha256=digest(body))


def is_sealed(m):
    return m.get("manifest_sha256") == digest({k: v for k, v in m.items() if k != "manifest_sha256"})


def row_key(row, fields):
    return "|".join(str(row.get(f, "")) for f in fields)


def build(experiment_id, arms, shards, sources=None, early_stop=None, row_key_fields=("arm",), seed_field="seed"):
    ids = [s["id"] for s in shards]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate shard ids in a manifest: %s" % ids)
    for s in shards:
        for k in ("id", "seeds", "arm_counts", "rows", "rows_sha256", "meta_sha256"):
            if k not in s:
                raise ValueError("shard %s lacks %s" % (s.get("id"), k))
        if sum(s["arm_counts"].values()) != s["rows"]:
            raise ValueError("shard %s: arm_counts sum %d != rows %d" % (s["id"], sum(s["arm_counts"].values()), s["rows"]))
    if early_stop:
        unknown = set(early_stop["skippable"]) - set(ids)
        if unknown:
            raise ValueError("early_stop.skippable names shards not in the manifest: %s" % sorted(unknown))
    return seal(dict(schema=SCHEMA, experiment_id=experiment_id, arms=list(arms), row_key_fields=list(row_key_fields),
                     seed_field=seed_field, shards=[dict(s, seeds=sorted(s["seeds"])) for s in shards],
                     sources=dict(sources or {}), early_stop=early_stop))


def expected_counts(m):
    """{key: total expected executions over all shards}"""
    out = {}
    for s in m["shards"]:
        for k, n in s["arm_counts"].items():
            out[k] = out.get(k, 0) + n
    return out
