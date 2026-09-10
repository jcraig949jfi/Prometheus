#!/usr/bin/env python3
"""
Necropolis validator — dependency-free (stdlib only; jsonschema not required).

Checks (Necropolis founding invariants):
  1. Every machine-readable file parses (SCHEMA.json, ROSTER.jsonl, QUEUE.jsonl, dossiers/*.json).
  2. Every dossier validates against SCHEMA.json (a minimal JSON-Schema 2020-12 subset walker).
  3. The generic 'FAILED' classification is REJECTED (self-test included).
  4. ROSTER.jsonl has no duplicate canonical agent_ids.
  5. Every QUEUE.jsonl target resolves to a ROSTER agent_id.
  6. Every dossier identity.agent_id resolves to a ROSTER agent_id (PLACEHOLDER* exempt).
  7. If a dossier proposes a descendant_candidate, LAW N6/N8/N9 fields are present and
     descendant_candidate.parent == identity.agent_id.

Run:  python engine/necropolis/validate.py     (exit 0 = all green)
"""
import json, os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
def here(*a): return os.path.join(HERE, *a)

errors = []
def err(where, msg): errors.append(f"[{where}] {msg}")

# ---------------------------------------------------------------- mini schema walker
def type_ok(val, t):
    if t == "string":  return isinstance(val, str)
    if t == "number":  return isinstance(val, (int, float)) and not isinstance(val, bool)
    if t == "integer": return isinstance(val, int) and not isinstance(val, bool)
    if t == "boolean": return isinstance(val, bool)
    if t == "object":  return isinstance(val, dict)
    if t == "array":   return isinstance(val, list)
    if t == "null":    return val is None
    return True

def validate(inst, schema, path, out):
    if "const" in schema and inst != schema["const"]:
        out.append(f"{path}: expected const {schema['const']!r}, got {inst!r}")
    if "enum" in schema and inst not in schema["enum"]:
        out.append(f"{path}: {inst!r} not in enum {schema['enum']}")
    if "type" in schema:
        t = schema["type"]
        ts = t if isinstance(t, list) else [t]
        if not any(type_ok(inst, x) for x in ts):
            out.append(f"{path}: type {type(inst).__name__} not in {ts}")
            return  # further checks assume the type matched
    if isinstance(inst, str) and "minLength" in schema and len(inst) < schema["minLength"]:
        out.append(f"{path}: string shorter than minLength {schema['minLength']} ({inst!r})")
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            out.append(f"{path}: array shorter than minItems {schema['minItems']}")
        if "items" in schema:
            for i, el in enumerate(inst):
                validate(el, schema["items"], f"{path}[{i}]", out)
    if isinstance(inst, dict):
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in inst:
                out.append(f"{path}: missing required '{req}'")
        if schema.get("additionalProperties") is False:
            for k in inst:
                if k not in props and not k.startswith("_"):  # _README/_comment allowed
                    out.append(f"{path}: additional property '{k}' not permitted")
        for k, v in inst.items():
            if k in props:
                validate(v, props[k], f"{path}.{k}", out)

# ---------------------------------------------------------------- load schema
try:
    SCHEMA = json.load(open(here("SCHEMA.json"), encoding="utf-8"))
except Exception as e:
    print(f"FATAL: SCHEMA.json failed to parse: {e}"); sys.exit(2)

FORBIDDEN_CLASSIFICATIONS = {"FAILED", "DEAD", "", "FAIL", "BROKEN"}

def semantic_checks(d, where):
    ident = d.get("identity", {})
    aid = ident.get("agent_id", "")
    disp = d.get("disposition", {})
    cls = disp.get("classification")
    if cls in FORBIDDEN_CLASSIFICATIONS:
        err(where, f"forbidden generic classification {cls!r} (Necropolis rejects undifferentiated FAILED)")
    dc = d.get("descendant_candidate")
    if dc is not None:
        for f in ("id","parent","changed_design","consumer","consumption_proof",
                  "expected_if_alive","expected_if_dead","kill_condition"):
            if not dc.get(f):
                err(where, f"descendant_candidate present but missing/empty '{f}' (LAW N6/N8/N9)")
        if dc.get("parent") and dc.get("parent") != aid:
            err(where, f"descendant_candidate.parent {dc.get('parent')!r} != identity.agent_id {aid!r}")
    return aid

# ---------------------------------------------------------------- roster
roster_ids = []
try:
    for i, line in enumerate(open(here("ROSTER.jsonl"), encoding="utf-8")):
        line = line.strip()
        if not line: continue
        r = json.loads(line)
        roster_ids.append(r["agent_id"])
except Exception as e:
    err("ROSTER.jsonl", f"parse error: {e}")

dupes = {x for x in roster_ids if roster_ids.count(x) > 1}
if dupes: err("ROSTER.jsonl", f"duplicate agent_ids: {sorted(dupes)}")
roster_set = set(roster_ids)

# ---------------------------------------------------------------- queue
try:
    for i, line in enumerate(open(here("QUEUE.jsonl"), encoding="utf-8")):
        line = line.strip()
        if not line: continue
        q = json.loads(line)
        tgt = q.get("target")
        if tgt not in roster_set:
            err("QUEUE.jsonl", f"target {tgt!r} does not resolve to a ROSTER agent_id")
        if q.get("status") != "READY":
            err("QUEUE.jsonl", f"target {tgt!r} status {q.get('status')!r} != READY (founding pass dispatches nothing)")
except Exception as e:
    err("QUEUE.jsonl", f"parse error: {e}")

# ---------------------------------------------------------------- dossiers
dossier_files = sorted(glob.glob(here("dossiers", "*.json")))
for f in dossier_files:
    name = os.path.basename(f)
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        err(name, f"parse error: {e}"); continue
    out = []
    validate(d, SCHEMA, name, out)
    for o in out: err(name, o)
    aid = semantic_checks(d, name)
    if aid and not aid.startswith("PLACEHOLDER") and aid not in roster_set:
        err(name, f"identity.agent_id {aid!r} does not resolve to a ROSTER agent_id")

# ---------------------------------------------------------------- self-test: FAILED rejected
_bad = {"schema_version":"1.0.0","identity":{"agent_id":"PLACEHOLDER_X","source_paths":["x"],"evidence_baseline":"0000000"},
        "autopsy":{"kill_boundary":"synthetic self-test","surviving_claims":[],"failure_classes":["X"]},
        "disposition":{"classification":"FAILED","rationale":"synthetic self-test row"},
        "provenance":{"investigator":"selftest","branch":"b","baseline_sha":"0000000","commands_run":["x"]}}
_probe = []
semantic_checks(_bad, "SELFTEST")
_selftest_caught = any("SELFTEST" in e for e in errors)
if not _selftest_caught:
    err("SELFTEST", "FAILED-classification rejection self-test did NOT fire — validator is broken")
else:
    errors[:] = [e for e in errors if not e.startswith("[SELFTEST]")]  # remove the intended self-test hit

# ---------------------------------------------------------------- report
print("=== Necropolis validate.py ===")
print(f"schema:   SCHEMA.json OK")
print(f"roster:   {len(roster_ids)} agents, {len(dupes)} duplicate ids")
print(f"dossiers: {len(dossier_files)} files checked")
print(f"selftest: FAILED-classification rejection {'FIRED (ok)' if _selftest_caught else 'MISSING'}")
if errors:
    print(f"\nFAIL — {len(errors)} problem(s):")
    for e in errors: print("  -", e)
    sys.exit(1)
print("\nALL GREEN")
sys.exit(0)
