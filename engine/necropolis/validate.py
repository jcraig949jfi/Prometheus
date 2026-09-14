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
  9. LAW N17 (NECROPOLIS DOES NOT INHERIT DEATH CERTIFICATES): every dossier carries death_certificates (reviewed),
     a 9-layer cause_of_death_stack (each layer VALID/INVALID/NOT_EXAMINED with evidence), fair_test and primary_cause.
     Cause classes must sit on admissible layers; HYPOTHESIS_FAILURE/PREMISE_FAILURE need fair_test FAIR and no
     NOT_EXAMINED or load-bearing INVALID layer in DESIGN..MEASUREMENT; PREMISE_FAILURE needs premise_exclusion;
     TRUE_CORPSE needs a strong primary cause; every repo path cited is resolved (the Cleric's hallucination scan);
     repairs target a recorded INVALID layer of their one ancestor, carry a record check and a feasible ancestral
     comparison; unexecuted organs need an organ_execution_plan. COUNTERFACTUAL_HISTORY.jsonl is byte-checked
     against build_counterfactuals.py.
 10. monsters/FRANK-*.monster.json validate against MONSTER_SCHEMA.json; every non-novel organ_id resolves
     to ORGANS.jsonl; at least one organ is non-novel (F5); F2 sentence verbatim (const in schema);
     lightning fields present; a self-test proves a monster without kill_condition is rejected.

Run:  python engine/necropolis/validate.py     (exit 0 = all green)
"""
import json, os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
def here(*a): return os.path.join(HERE, *a)

errors = []
notes = []
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

# ---------------------------------------------------------------- path resolution (LAW N17 hallucination scan)
import re as _re
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
_PATH_RX = _re.compile(r"(?<![\w./-])((?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.(?:py|jsonl|json|md|txt|csv))(?![\w.])")
def path_scan(obj, where):
    """Every repo-relative path cited in a record must resolve (repo root or engine/necropolis) or be flagged.
    Printed as a note, not an error: archived/lost artifacts are legitimate citations, but the Cleric must see them."""
    text = json.dumps(obj, ensure_ascii=False)
    cited = sorted(set(_PATH_RX.findall(text)))
    bases = (REPO, HERE, here("dossiers"), os.path.join(REPO, "agents", "coeus"))
    missing = [p for p in cited if not any(os.path.exists(os.path.join(b, p)) for b in bases)]
    if cited:
        notes.append(f"{where}: {len(cited) - len(missing)}/{len(cited)} cited paths resolve" + (f"; unresolved: {missing}" if missing else ""))
    return cited, missing


# ---------------------------------------------------------------- cause-of-death stack (LAW N17)
LAYERS = ["HYPOTHESIS","DESIGN","IMPLEMENTATION","CONFIGURATION","EXECUTION","INSTRUMENTATION","MEASUREMENT","INTERPRETATION","ECOSYSTEM"]
FAIRNESS_LAYERS = LAYERS[1:7]   # DESIGN..MEASUREMENT: the layers that decide whether the test was fair
LAYER_CAUSES = {                # which cause classes a layer may carry
    "HYPOTHESIS":      {"HYPOTHESIS_FAILURE", "PREMISE_FAILURE"},
    "DESIGN":          {"DESIGN_ERROR", "CAPABILITY_CEILING"},
    "IMPLEMENTATION":  {"IMPLEMENTATION_ERROR", "CAPABILITY_CEILING"},
    "CONFIGURATION":   {"CONFIGURATION_ERROR", "CAPABILITY_CEILING"},
    "EXECUTION":       {"EXECUTION_ERROR", "CAPABILITY_CEILING"},
    "INSTRUMENTATION": {"INSTRUMENT_ERROR"},
    "MEASUREMENT":     {"MEASUREMENT_ERROR"},
    "INTERPRETATION":  {"INTERPRETATION_ERROR", "IDENTITY_PROVENANCE_ERROR"},
    "ECOSYSTEM":       {"ECOSYSTEM_FAILURE"},
}
STRONG = {"HYPOTHESIS_FAILURE", "PREMISE_FAILURE"}
dossier_stacks = {}   # agent_id -> stack (read by the monster checks: a repair must target a recorded error)

def stack_checks(d, where):
    au = d.get("autopsy", {}) or {}
    stack = au.get("cause_of_death_stack", {}) or {}
    cls = (d.get("disposition", {}) or {}).get("classification")
    supported = set()
    for L in LAYERS:
        lay = stack.get(L) or {}
        v = lay.get("verdict"); cc = set(lay.get("cause_classes") or [])
        bad = cc - LAYER_CAUSES[L]
        if bad: err(where, f"stack.{L} carries cause classes {sorted(bad)} not admissible on that layer")
        if v in ("VALID", "INVALID") and not lay.get("evidence"):
            err(where, f"stack.{L} is {v} with no evidence (LAW N17: write NOT_EXAMINED)")
        if v == "INVALID" and not cc:
            err(where, f"stack.{L} is INVALID but names no cause class")
        if v == "NOT_EXAMINED" and cc:
            err(where, f"stack.{L} is NOT_EXAMINED but carries cause classes {sorted(cc)}")
        if v == "VALID" and cc and L != "HYPOTHESIS":
            err(where, f"stack.{L} is VALID but carries cause classes {sorted(cc)} (only HYPOTHESIS may be VALID and falsified)")
        if v == "INVALID" and lay.get("load_bearing") is False and len(lay.get("evidence") or []) < 1:
            err(where, f"stack.{L} claims non-load-bearing without evidence")
        supported |= cc
    # fair test
    ft = au.get("fair_test", {}) or {}
    fv = ft.get("verdict")
    unexamined = [L for L in FAIRNESS_LAYERS if (stack.get(L) or {}).get("verdict") == "NOT_EXAMINED"]
    lb_invalid = [L for L in FAIRNESS_LAYERS if (stack.get(L) or {}).get("verdict") == "INVALID"
                  and (stack.get(L) or {}).get("load_bearing") is not False]
    if fv == "FAIR" and (unexamined or lb_invalid):
        err(where, f"fair_test FAIR but DESIGN..MEASUREMENT has NOT_EXAMINED {unexamined} / load-bearing INVALID {lb_invalid}")
    if fv == "UNFAIR" and not lb_invalid:
        err(where, "fair_test UNFAIR but no load-bearing INVALID layer in DESIGN..MEASUREMENT names why")
    # primary / contributing
    pc = au.get("primary_cause"); contrib = au.get("contributing_causes") or []
    if pc == "UNDETERMINED":
        if cls != "NEEDS_MORE_EVIDENCE" and not any((stack.get(L) or {}).get("verdict") == "NOT_EXAMINED" for L in LAYERS):
            err(where, "primary_cause UNDETERMINED with every layer examined and classification != NEEDS_MORE_EVIDENCE")
    elif pc not in supported:
        err(where, f"primary_cause {pc} is not carried by any layer of the stack")
    for c in contrib:
        if c not in supported: err(where, f"contributing cause {c} is not carried by any layer of the stack")
        if c == pc: err(where, f"contributing cause {c} duplicates primary_cause")
    if pc in STRONG:
        if fv != "FAIR": err(where, f"primary_cause {pc} requires fair_test FAIR (was {fv}): a strong claim needs a fair test")
        if unexamined or lb_invalid: err(where, f"primary_cause {pc} with NOT_EXAMINED {unexamined} / load-bearing INVALID {lb_invalid} in DESIGN..MEASUREMENT")
        if (stack.get("ECOSYSTEM") or {}).get("verdict") == "NOT_EXAMINED": err(where, f"primary_cause {pc} with ECOSYSTEM NOT_EXAMINED")
    if pc == "PREMISE_FAILURE" and not au.get("premise_exclusion"):
        err(where, "PREMISE_FAILURE without premise_exclusion: the strongest claim is admitted only after the alternatives are excluded")
    # classification coherence
    if cls == "TRUE_CORPSE" and pc not in STRONG:
        err(where, f"TRUE_CORPSE requires primary_cause HYPOTHESIS_FAILURE/PREMISE_FAILURE (was {pc}); pick the neighbour the stack supports")
    if cls == "CAPABILITY_BOUND" and pc != "CAPABILITY_CEILING":
        err(where, f"CAPABILITY_BOUND requires primary_cause CAPABILITY_CEILING (was {pc})")
    if cls == "NO_FAIR_TEST_ON_RECORD" and fv != "UNFAIR":
        err(where, f"NO_FAIR_TEST_ON_RECORD requires fair_test UNFAIR (was {fv})")
    if fv == "UNFAIR" and cls == "TRUE_CORPSE":
        err(where, "fair_test UNFAIR is incompatible with TRUE_CORPSE")
    # death certificates
    for i, dc in enumerate(au.get("death_certificates") or []):
        if dc.get("review") in ("PARTIALLY_UPHELD", "OVERTURNED") and not dc.get("errors"):
            err(where, f"death_certificates[{i}] is {dc.get('review')} but lists no errors")
        if dc.get("review") == "UPHELD" and dc.get("errors"):
            err(where, f"death_certificates[{i}] is UPHELD but lists errors")
    n_inv = sum(1 for L in LAYERS if (stack.get(L) or {}).get("verdict") == "INVALID")
    n_ne = sum(1 for L in LAYERS if (stack.get(L) or {}).get("verdict") == "NOT_EXAMINED")
    notes.append(f"{where}: stack {n_inv} INVALID / {n_ne} NOT_EXAMINED; fair_test={fv}; primary={pc}; certificates "
                 + ",".join((dc.get('review') or '?') for dc in (au.get('death_certificates') or [])))
    return stack

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
    if aid and not aid.startswith("PLACEHOLDER"):
        path_scan(d, name)
        dossier_stacks[aid] = stack_checks(d, name)
    if aid and not aid.startswith("PLACEHOLDER") and aid not in roster_set:
        err(name, f"identity.agent_id {aid!r} does not resolve to a ROSTER agent_id")

# ---------------------------------------------------------------- organs (F5)
organ_ids = set()
organ_exec = {}
organs_fp = None
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
            organ_exec[o["organ_id"]] = o.get("executed_by_necromancer")
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

# ---------------------------------------------------------------- counterfactual history (derived, like ORGANS)
cf_path = here("COUNTERFACTUAL_HISTORY.jsonl")
try:
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("build_counterfactuals", here("build_counterfactuals.py"))
    _bc = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_bc)
    _expected = _bc.render(_bc.build_rows())
    _have = open(cf_path, "rb").read().replace(b"\r\n", b"\n") if os.path.exists(cf_path) else b""
    if _have != _expected.encode("utf-8"):
        open(cf_path, "w", encoding="utf-8", newline="\n").write(_expected)
        err("COUNTERFACTUAL_HISTORY.jsonl", "was STALE relative to dossiers/monsters; regenerated by validate.py -- re-run validate and commit the new file")
    n_cf = _expected.count("\n")
    n_cf_repaired = sum(1 for line in _expected.splitlines() if line and json.loads(line).get("repair"))
except Exception as e:
    err("COUNTERFACTUAL_HISTORY.jsonl", f"build_counterfactuals failed: {e}"); n_cf = n_cf_repaired = -1

# ---------------------------------------------------------------- monsters (F1-F7)
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
    # LAW N17 / F7: organs the Necromancer only read need an execution plan before a monster reads from them
    unexecuted = [o.get("organ_id") for o in organs
                  if not o.get("novel") and organ_exec.get(o.get("organ_id")) is not True]
    if unexecuted and not (m.get("organ_execution_plan") or "").strip():
        err(where, f"organs not executed by the Necromancer {unexecuted} but no organ_execution_plan (F7)")
    # F7: a repair is one ancestor, one change, feasible ancestral comparison, record checked
    if m.get("kind") == "repair":
        cr = m.get("counterfactual_repair")
        if not cr:
            err(where, "kind=repair without counterfactual_repair (F7)")
        else:
            if cr.get("ancestor") not in roster_set:
                err(where, f"counterfactual_repair.ancestor {cr.get('ancestor')!r} not in ROSTER")
            harvested = {o.get("source_agent") for o in organs if not o.get("novel")}
            if harvested - {cr.get("ancestor")}:
                err(where, f"repair harvests organs from {sorted(harvested - {cr.get('ancestor')})} but a repair has exactly one ancestor (F7); file as kind=chimera")
            if not cr.get("record_check"):
                err(where, "repair without record_check (F7: check the record first)")
            anc_stack = dossier_stacks.get(cr.get("ancestor")) or {}
            fl, fc = cr.get("failure_layer"), cr.get("cause_class")
            lay = anc_stack.get(fl) or {}
            if anc_stack and lay.get("verdict") != "INVALID":
                err(where, f"repair targets layer {fl} but the ancestor's stack has it {lay.get('verdict')!r}, not INVALID (F7: repair a recorded error)")
            if anc_stack and fc not in (lay.get("cause_classes") or []):
                err(where, f"repair names cause {fc} on layer {fl} but the ancestor's stack records {lay.get('cause_classes')} there (F7)")
        ac = (m.get("lightning_experiment", {}) or {}).get("ancestral_comparison", {}) or {}
        if ac.get("feasible") is not True:
            err(where, "repair with ancestral_comparison.feasible != true (F7: the ancestor with and without the change IS the experiment)")
    elif m.get("counterfactual_repair"):
        err(where, "counterfactual_repair present but kind != repair")
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
    path_scan(m, name)

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
# self-test: a repair without counterfactual_repair must be rejected
_repairs = [f for f in monster_files if json.load(open(f, encoding="utf-8")).get("kind") == "repair"]
_repair_selftest_caught = None
if _repairs:
    _bad_r = json.load(open(_repairs[0], encoding="utf-8")); _bad_r.pop("counterfactual_repair", None)
    monster_checks(_bad_r, "REPAIR_SELFTEST")
    _repair_selftest_caught = any("REPAIR_SELFTEST" in e and "counterfactual_repair" in e for e in errors)
    errors[:] = [e for e in errors if not e.startswith("[REPAIR_SELFTEST]")]
    notes[:] = [n for n in notes if not n.startswith("REPAIR_SELFTEST")]
    if not _repair_selftest_caught:
        err("REPAIR_SELFTEST", "a repair without counterfactual_repair was NOT rejected -- validator is broken")

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
print(f"organs:   {n_organs} organs in ORGANS.jsonl; executed_by_necromancer=true for {sum(1 for v in organ_exec.values() if v is True)}")
print(f"history:  {n_cf} counterfactual rows (mistake -> symptom -> verdict -> corrected cause -> repair -> post-repair); {n_cf_repaired} with a repair filed")
print(f"monsters: {len(monster_files)} files checked; kill_condition-rejection self-test "
      f"{'FIRED (ok)' if _monster_selftest_caught else ('n/a (no monsters)' if _monster_selftest_caught is None else 'MISSING')}; "
      f"repair-without-counterfactual self-test {'FIRED (ok)' if _repair_selftest_caught else ('n/a (no repairs)' if _repair_selftest_caught is None else 'MISSING')}")
for n in notes: print("note:    ", n)
if errors:
    print(f"\nFAIL — {len(errors)} problem(s):")
    for e in errors: print("  -", e)
    sys.exit(1)
print("\nALL GREEN")
sys.exit(0)
