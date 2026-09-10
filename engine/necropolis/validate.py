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
  8. ORGANS.jsonl (if present): parses, organ_ids unique, source_agent in ROSTER, source_dossier exists,
     and the file is byte-identical to what build_organs.py would regenerate (organs come only from residue, F5).
  9. monsters/FRANK-*.monster.json validate against MONSTER_SCHEMA.json; every non-novel organ_id resolves
     to ORGANS.jsonl; at least one organ is non-novel (F5); F2 sentence verbatim (const in schema);
     lightning fields present; a self-test proves a monster without kill_condition is rejected.

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

# ---------------------------------------------------------------- organs (F5)
organ_ids = set()
organs_fp = None
notes = []
organs_path = here("ORGANS.jsonl")
n_organs = 0
if os.path.exists(organs_path):
    seen = []
    try:
        for line in open(organs_path, encoding="utf-8"):
            line = line.strip()
            if not line: continue
            o = json.loads(line); n_organs += 1
            seen.append(o["organ_id"])
            if o.get("source_agent") not in roster_set:
                err("ORGANS.jsonl", f"{o['organ_id']}: source_agent {o.get('source_agent')!r} not in ROSTER")
            if not os.path.exists(here(o.get("source_dossier", ""))):
                err("ORGANS.jsonl", f"{o['organ_id']}: source_dossier {o.get('source_dossier')!r} missing")
            if o.get("status") != "certified_by_dossier" and not o.get("failures_recorded_against"):
                pass  # other statuses are Keeper annotations via ORGAN_NOTES.json; allowed
    except Exception as e:
        err("ORGANS.jsonl", f"parse error: {e}")
    od = {x for x in seen if seen.count(x) > 1}
    if od: err("ORGANS.jsonl", f"duplicate organ_ids: {sorted(od)}")
    organ_ids = set(seen)
    import hashlib
    organs_fp = hashlib.sha256(open(organs_path, "rb").read().replace(b"\r\n", b"\n")).hexdigest()
    # regeneration check: the inventory must equal what the dossiers certify (only writer is build_organs.py)
    try:
        import io, contextlib, importlib.util
        spec = importlib.util.spec_from_file_location("build_organs", here("build_organs.py"))
        bo = importlib.util.module_from_spec(spec); spec.loader.exec_module(bo)
        before = open(organs_path, "rb").read()
        with contextlib.redirect_stdout(io.StringIO()):
            bo.main()
        after = open(organs_path, "rb").read()
        if before != after:
            err("ORGANS.jsonl", "was STALE relative to dossier residue; regenerated by validate.py -- re-run validate and commit the new file")
    except Exception as e:
        err("ORGANS.jsonl", f"regeneration check failed: {e}")

# ---------------------------------------------------------------- monsters (F1-F6)
try:
    MSCHEMA = json.load(open(here("MONSTER_SCHEMA.json"), encoding="utf-8"))
except Exception as e:
    MSCHEMA = None; err("MONSTER_SCHEMA.json", f"failed to parse: {e}")

F2_SENTENCE = (MSCHEMA or {}).get("properties", {}).get("vindication_disclaimer", {}).get("const")
LIGHTNING_REQUIRED = ("design", "expected_if_alive", "expected_if_dead", "kill_condition", "chance_floor",
                      "positive_control", "ancestral_comparison")

def monster_checks(m, where):
    out = []
    if MSCHEMA: validate(m, MSCHEMA, where, out)
    for o in out: err(where, o)
    if m.get("vindication_disclaimer") != F2_SENTENCE:
        err(where, "F2 vindication_disclaimer is not verbatim")
    le = m.get("lightning_experiment", {}) or {}
    for f in LIGHTNING_REQUIRED:
        if not le.get(f):
            err(where, f"lightning_experiment missing/empty '{f}' (F3)")
    organs = m.get("organs", []) or []
    if organs and not any(not o.get("novel", False) for o in organs):
        err(where, "every organ is novel -- that is a new project, not a monster (F5)")
    for o in organs:
        oid = o.get("organ_id", "")
        if o.get("novel"):
            if not oid.startswith("novel."):
                err(where, f"novel organ {oid!r} must use the 'novel.' prefix")
        elif oid not in organ_ids:
            err(where, f"organ {oid!r} does not resolve to ORGANS.jsonl (F5: uncertified organ)")
    gate = m.get("cleric_gate", {}) or {}
    if gate.get("status") == "DEAD" and not gate.get("dossier_if_dead"):
        err(where, "status DEAD but no dossier_if_dead (F6: the monster gets no special burial)")
    if gate.get("status") in ("RUNNING", "ALIVE", "DEAD") and not gate.get("james_signoff"):
        err(where, f"status {gate.get('status')} without james_signoff")
    want = (m.get("provenance", {}) or {}).get("organs_inventory_sha")
    if want and organs_fp and want != organs_fp and gate.get("status") == "PROPOSED":
        notes.append(f"{where}: organs_inventory_sha is stale (inventory changed since proposal); Frankenstein should re-read ORGANS.jsonl and amend")
    elif want and organs_fp and want != organs_fp:
        err(where, f"organs_inventory_sha does not match the current inventory and status is {gate.get('status')} (gated monsters are pinned to the inventory they were gated against)")
    mid = m.get("monster_id")
    if mid and not os.path.basename(where).startswith(mid):
        err(where, f"filename does not start with monster_id {mid!r}")

monster_files = sorted(glob.glob(here("monsters", "FRANK-*.monster.json")))
for f in monster_files:
    name = "monsters/" + os.path.basename(f)
    try:
        m = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        err(name, f"parse error: {e}"); continue
    monster_checks(m, name)

# self-test: a monster without a kill_condition must be rejected
_bad_monster = None
if monster_files:
    _bad_monster = json.load(open(monster_files[0], encoding="utf-8"))
    _bad_monster["lightning_experiment"] = dict(_bad_monster["lightning_experiment"])
    _bad_monster["lightning_experiment"].pop("kill_condition", None)
    _n_before = len(errors)
    monster_checks(_bad_monster, "MONSTER_SELFTEST")
    _monster_selftest_caught = any("MONSTER_SELFTEST" in e and "kill_condition" in e for e in errors)
    errors[:] = [e for e in errors if not e.startswith("[MONSTER_SELFTEST]")]
    if not _monster_selftest_caught:
        err("MONSTER_SELFTEST", "a monster without kill_condition was NOT rejected -- validator is broken")
else:
    _monster_selftest_caught = None

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
print(f"organs:   {n_organs} organs in ORGANS.jsonl")
print(f"monsters: {len(monster_files)} files checked; kill_condition-rejection self-test "
      f"{'FIRED (ok)' if _monster_selftest_caught else ('n/a (no monsters)' if _monster_selftest_caught is None else 'MISSING')}")
for n in notes: print("note:    ", n)
if errors:
    print(f"\nFAIL — {len(errors)} problem(s):")
    for e in errors: print("  -", e)
    sys.exit(1)
print("\nALL GREEN")
sys.exit(0)
