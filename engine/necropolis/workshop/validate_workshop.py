#!/usr/bin/env python3
"""
Necropolis workshop validator (TOOL MORGUE) -- stdlib only.

LAYER: NECROPOLIS VALIDATION (this file validates the registry; it is not an instrument).

Checks:
  1. TOOL_SCHEMA.json parses; TOOLS.jsonl parses; every row validates against the schema
     (same minimal JSON-Schema walker as ../validate.py, copied so this file stays standalone).
  2. tool_ids unique and ascending NT-001..; names unique.
  3. current_path resolves in the repo for every status except HISTORICAL_ONLY (path is
     relative to the repo root = three levels above this file); adapter paths resolve;
     self_test paths resolve unless they start with 'inline:'.
  4. Status rules (x-status-rules in the schema, enforced here because the walker has no
     if/then): READY / READY_WITH_CAVEAT need an ACCEPT-family AND a REJECT-family self test,
     all self tests PASS, a last_verified_execution, and (caveat) a non-empty caveat;
     DUPLICATE needs duplicate_of that resolves; BROKEN/UNTRUSTED/NEEDS_DEPENDENCY need
     status_reason; UNTRUSTED needs a REJECT-family self test with result FAIL
     (CHEAT, or SYNTHETIC_NULL / PERTURBATION -- a statistic that reads signal on
     independent samples is untrusted whether or not a cheat was scripted); HISTORICAL_ONLY
     needs historical_path.
  5. source_commit is an object in this repository (git cat-file -e), when git is available.
  6. frankenstein_refs resolve to ../monsters/FRANK-NNN.monster.json.
  7. battery_refs resolve to batteries/<name>.json and every battery step names a tool_id
     that exists and is not BROKEN.
  8. Self-tests (the validator distrusts itself): a READY row with no REJECT-family control is
     rejected; a row whose last_verified_execution is null but status READY is rejected; a
     DUPLICATE row without duplicate_of is rejected; a row with a fabricated source_commit
     is rejected when git is available.

Run:  python engine/necropolis/workshop/validate_workshop.py     (exit 0 = all green)
"""
import json, os, sys, glob, subprocess, copy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
def here(*a): return os.path.join(HERE, *a)
def repo(*a): return os.path.join(REPO, *a)

errors, notes = [], []
def err(where, msg): errors.append(f"[{where}] {msg}")

# ---------------------------------------------------------------- mini schema walker (copy of ../validate.py)
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
        out.append(f"{path}: {inst!r} not in enum")
    if "type" in schema:
        t = schema["type"]; ts = t if isinstance(t, list) else [t]
        if not any(type_ok(inst, x) for x in ts):
            out.append(f"{path}: type {type(inst).__name__} not in {ts}"); return
    if isinstance(inst, str):
        if "minLength" in schema and len(inst) < schema["minLength"]:
            out.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema:
            import re
            if not re.search(schema["pattern"], inst):
                out.append(f"{path}: {inst!r} does not match {schema['pattern']}")
    if isinstance(inst, (int, float)) and not isinstance(inst, bool):
        if "minimum" in schema and inst < schema["minimum"]:
            out.append(f"{path}: below minimum {schema['minimum']}")
    if isinstance(inst, dict):
        for r in schema.get("required", []):
            if r not in inst: out.append(f"{path}: missing required {r!r}")
        props = schema.get("properties", {})
        for k, v in inst.items():
            if k in props: validate(v, props[k], f"{path}.{k}", out)
            elif schema.get("additionalProperties", True) is False:
                out.append(f"{path}: additional property {k!r}")
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            out.append(f"{path}: fewer than minItems {schema['minItems']}")
        if "items" in schema:
            for i, v in enumerate(inst): validate(v, schema["items"], f"{path}[{i}]", out)

# ---------------------------------------------------------------- load
try:
    SCHEMA = json.load(open(here("TOOL_SCHEMA.json"), encoding="utf-8"))
except Exception as e:
    err("TOOL_SCHEMA.json", f"does not parse: {e}"); SCHEMA = None

ACCEPT_KINDS = {"ACCEPT", "SYNTHETIC_SIGNAL", "PARITY", "REPETITION"}
REJECT_KINDS = {"REJECT", "CHEAT", "SYNTHETIC_NULL", "CORRUPT_INPUT", "PERTURBATION", "LAUNDERING"}
RUNNER = "engine/necropolis/workshop/tests/run_controls.py"   # a self_test whose path starts here was RUN BY THE KEEPER

_git_ok = None
def git_has(sha):
    global _git_ok
    if _git_ok is False: return None
    try:
        r = subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"], cwd=REPO,
                           capture_output=True, timeout=20)
        _git_ok = True
        return r.returncode == 0
    except Exception:
        _git_ok = False
        return None

def load_jsonl(p):
    rows = []
    with open(p, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line: continue
            try: rows.append(json.loads(line))
            except Exception as e: err(os.path.basename(p), f"line {n} does not parse: {e}")
    return rows

def row_checks(t, where, ids, check_git=True):
    out = []
    if SCHEMA: validate(t, SCHEMA, "tool", out)
    for o in out: err(where, o)
    if out: return
    st = t["necropolis_status"]
    kinds = {s["kind"] for s in t["self_tests"]}
    results = {s["result"] for s in t["self_tests"]}
    if st in ("READY", "READY_WITH_CAVEAT"):
        if not (kinds & ACCEPT_KINDS): err(where, f"{st} without an ACCEPT-family self test")
        if not (kinds & REJECT_KINDS): err(where, f"{st} without a REJECT-family self test (VI: every tool must have a control)")
        if results - {"PASS"}: err(where, f"{st} with a self test not PASS: {sorted(results - {'PASS'})}")
        if t["last_verified_execution"] is None: err(where, f"{st} with last_verified_execution null")
        if t["current_path"] is None: err(where, f"{st} with current_path null")
        if not t.get("harvest", {}).get("inspected", False): err(where, f"{st} but harvest.inspected is not true")
    if st == "READY_WITH_CAVEAT" and not t.get("caveat"): err(where, "READY_WITH_CAVEAT without caveat")
    if st == "DUPLICATE":
        d = t.get("duplicate_of")
        if not d: err(where, "DUPLICATE without duplicate_of")
        elif d not in ids: err(where, f"duplicate_of {d} is not a registered tool_id")
        elif d == t["tool_id"]: err(where, "duplicate_of itself")
    if st in ("BROKEN", "UNTRUSTED", "NEEDS_DEPENDENCY") and not t.get("status_reason"):
        err(where, f"{st} without status_reason")
    if st == "UNTRUSTED":
        if not any(s["kind"] in REJECT_KINDS and s["result"] == "FAIL" for s in t["self_tests"]):
            err(where, "UNTRUSTED without a REJECT-family self test recorded as FAIL")
    if st == "HISTORICAL_ONLY" and not t.get("historical_path"): err(where, "HISTORICAL_ONLY without historical_path")
    if st == "NEEDS_DEPENDENCY" and t["dependency_status"] == "ALL_PRESENT":
        err(where, "NEEDS_DEPENDENCY but dependency_status ALL_PRESENT")
    # admissibility ladder (court charter 2026-09-14): each rung needs the one below it, and
    # admissible needs ALL of them plus a READY-family status.  The ladder is derived from
    # measurements; these checks catch a row where the status string and the measurements
    # disagree, in either direction.
    adm = t.get("admissibility") or {}
    if adm:
        keeper = any(s["path"].startswith(RUNNER) for s in t["self_tests"])
        if adm.get("admissible"):
            if st not in ("READY", "READY_WITH_CAVEAT"): err(where, f"admissible but status {st}")
            if adm.get("controlled") != "KEEPER": err(where, "admissible without Keeper controls (author tests are not controls)")
            if adm.get("executes") != "KEEPER_CONTROLS": err(where, f"admissible but executes={adm.get('executes')}")
            if adm.get("imports") != "IMPORT_OK" or not adm.get("path_exists"): err(where, "admissible but a lower rung is not measured OK")
            if adm.get("blocked_by") is not None: err(where, "admissible with blocked_by set")
            cs = adm.get("control_state", {})
            if cs.get("fail") or cs.get("error"): err(where, f"admissible with control_state fail={cs.get('fail')} error={cs.get('error')}")
            want = "EVIDENCE_WITH_CAVEAT" if st == "READY_WITH_CAVEAT" else "EVIDENCE"
            if adm.get("admissible_as") != want: err(where, f"admissible_as {adm.get('admissible_as')} but status {st} requires {want}")
        else:
            if adm.get("admissible_as") != "NOT_ADMISSIBLE": err(where, "not admissible but admissible_as is not NOT_ADMISSIBLE")
            if not adm.get("blocked_by"): err(where, "not admissible without blocked_by")
            if st in ("READY", "READY_WITH_CAVEAT"): err(where, f"status {st} but admissibility says NOT_ADMISSIBLE ({adm.get('blocked_by')})")
        if adm.get("controlled") == "KEEPER" and not keeper: err(where, "controlled=KEEPER but no self_test path is the Keeper runner")
        if keeper and adm.get("controlled") != "KEEPER": err(where, "Keeper controls on record but controlled != KEEPER")
        if st == "UNTRUSTED" and adm.get("admissible"): err(where, "UNTRUSTED can never be admissible")
        if st == "HISTORICAL_ONLY" and adm.get("path_exists"): err(where, "HISTORICAL_ONLY with path_exists true")
    # paths
    if st != "HISTORICAL_ONLY":
        cp = t["current_path"]
        if cp is None: err(where, "current_path null outside HISTORICAL_ONLY")
        else:
            base = cp.split("::")[0]
            if not os.path.exists(repo(base)): err(where, f"current_path does not resolve: {base}")
    ad = t.get("necropolis_adapter")
    if ad and not os.path.exists(repo(ad)): err(where, f"necropolis_adapter does not resolve: {ad}")
    for s in t["self_tests"]:
        p = s["path"]
        if p.startswith("inline:"): continue
        if not os.path.exists(repo(p.split("::")[0])): err(where, f"self_test path does not resolve: {p}")
    lve = t["last_verified_execution"]
    if lve and lve.get("artifact") and not os.path.exists(repo(lve["artifact"])):
        err(where, f"last_verified_execution.artifact does not resolve: {lve['artifact']}")
    for fr in t.get("frankenstein_refs", []):
        if not os.path.exists(here("..", "monsters", fr + ".monster.json")): err(where, f"frankenstein_ref {fr} has no monster file")
    for br in t.get("battery_refs", []):
        if not os.path.exists(here("batteries", br + ".json")): err(where, f"battery_ref {br} has no batteries/{br}.json")
    if check_git:
        g = git_has(t["source_commit"])
        if g is False: err(where, f"source_commit {t['source_commit']} is not a commit in this repository")

# ---------------------------------------------------------------- registry
tools = load_jsonl(here("TOOLS.jsonl")) if os.path.exists(here("TOOLS.jsonl")) else []
ids = [t.get("tool_id") for t in tools]
if len(ids) != len(set(ids)): err("TOOLS.jsonl", f"duplicate tool_ids: {sorted({i for i in ids if ids.count(i) > 1})}")
names = [t.get("name") for t in tools]
if len(names) != len(set(names)): err("TOOLS.jsonl", f"duplicate names: {sorted({n for n in names if names.count(n) > 1})}")
for i, t in enumerate(tools):
    row_checks(t, f"TOOLS.jsonl:{t.get('tool_id', i)}", set(ids))
notes.append(f"tools: {len(tools)}")
from collections import Counter
notes.append("status counts: " + ", ".join(f"{k}={v}" for k, v in sorted(Counter(t.get('necropolis_status') for t in tools).items())))

# ---------------------------------------------------------------- batteries
BROKEN_LIKE = {"BROKEN", "UNTRUSTED"}
by_id = {t["tool_id"]: t for t in tools if "tool_id" in t}
for bp in sorted(glob.glob(here("batteries", "*.json"))):
    where = "batteries/" + os.path.basename(bp)
    try: b = json.load(open(bp, encoding="utf-8"))
    except Exception as e: err(where, f"does not parse: {e}"); continue
    for k in ("battery_id", "name", "question", "steps", "coroner_run_required", "output_contract"):
        if k not in b: err(where, f"missing {k}")
    if b.get("battery_id") != os.path.basename(bp)[:-5]: err(where, "battery_id != file name")
    for j, s in enumerate(b.get("steps", [])):
        for k in ("step", "tool_id", "role", "does"):
            if k not in s: err(where, f"step {j} missing {k}")
        tid = s.get("tool_id")
        if tid and tid not in by_id: err(where, f"step {j} names unregistered tool {tid}")
        elif tid and by_id[tid]["necropolis_status"] in BROKEN_LIKE:
            err(where, f"step {j} names {tid} whose status is {by_id[tid]['necropolis_status']}")
    notes.append(f"battery {b.get('battery_id')}: {len(b.get('steps', []))} steps")

# ---------------------------------------------------------------- coroner plans (must NOT be marked executed here)
for cp in sorted(glob.glob(here("coroner_plans", "CR-*.json"))):
    where = "coroner_plans/" + os.path.basename(cp)
    try: c = json.load(open(cp, encoding="utf-8"))
    except Exception as e: err(where, f"does not parse: {e}"); continue
    for k in ("plan_id", "target_grave", "question", "invocation", "inputs", "controls", "kill_criteria",
              "expected_outputs", "non_resurrection_argument", "hitl_status", "tools"):
        if k not in c: err(where, f"missing {k}")
    if c.get("hitl_status") not in ("PROPOSED", "APPROVED", "REJECTED", "EXECUTED"):
        err(where, f"hitl_status {c.get('hitl_status')!r} invalid (DEAD_BEFORE_RUN is a disposition, never a plan status)")
    if c.get("hitl_status") == "EXECUTED" and not c.get("execution_receipt"):
        err(where, "EXECUTED without execution_receipt")
    for tid in c.get("tools", []):
        if tid not in by_id: err(where, f"names unregistered tool {tid}")
    par = c.get("parent_plan")
    if par is not None and (not isinstance(par, dict) or not par.get("plan_id") or not par.get("sha256_lf")):
        err(where, "parent_plan must be {plan_id, sha256_lf}")
    notes.append(f"coroner plan {c.get('plan_id')}: {c.get('hitl_status')}")

# ---------------------------------------------------------------- coroner dispositions (CORONER_RUN.md section 7)
# A disposition is written beside a plan, never into it.  D1: the plan bytes must still
# match the hash under which it was disposed -- a drift here is an ERROR, not a note,
# because "never silently repair the plan and retain its identity" (R-CR-2).
import hashlib
def _sha_lf(path):
    b = open(path, "rb").read()
    if b"\0" not in b[:4096]: b = b.replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest()

def disposition_checks(d, where):
    for k in ("disposition_id", "plan_id", "plan_file", "plan_sha256_lf", "disposition", "killed_by", "hypothesis_status",
              "ruled_by", "ruling_source", "recorded_by", "recorded", "plan_modified_in_place"):
        if k not in d: err(where, f"missing {k}")
    if d.get("disposition") not in ("DEAD_BEFORE_RUN", "SUPERSEDED", "WITHDRAWN"):
        err(where, f"disposition {d.get('disposition')!r} invalid")
    if d.get("plan_modified_in_place") is not False:
        err(where, "plan_modified_in_place must be false (R-CR-2)")
    pf = d.get("plan_file")
    if pf:
        fp = here(pf)
        if not os.path.exists(fp): err(where, f"plan_file {pf} does not exist")
        elif _sha_lf(fp) != d.get("plan_sha256_lf"):
            err(where, f"plan {pf} bytes no longer match the disposed hash {str(d.get('plan_sha256_lf'))[:12]} (D1: a plan repaired in place has lost its identity)")
    kb = d.get("killed_by") or {}
    if d.get("disposition") == "DEAD_BEFORE_RUN":
        for k in ("control_case", "control_result_file", "control_result_sha256_lf", "what_died"):
            if not kb.get(k): err(where, f"DEAD_BEFORE_RUN without killed_by.{k} (D2: name what fired)")
        if kb.get("grave_touched") is not False: err(where, "DEAD_BEFORE_RUN must assert killed_by.grave_touched == false")
        crf = kb.get("control_result_file")
        if crf and os.path.exists(here(crf)):
            got = _sha_lf(here(crf))
            notes.append(f"disposition {d.get('disposition_id')} control result {crf}: " + ("MATCH" if got == kb.get("control_result_sha256_lf") else f"DRIFT (disposed {str(kb.get('control_result_sha256_lf'))[:10]}, now {got[:10]})"))
        cc = kb.get("control_case")
        if cc and os.path.exists(here("tests", "controls_result.json")):
            cases = {x.get("case_id") for x in json.load(open(here("tests", "controls_result.json"), encoding="utf-8")).get("cases", [])}
            if cc not in cases: err(where, f"killed_by.control_case {cc} is not a case in tests/controls_result.json")
    for child in d.get("descendants") or []:
        if not glob.glob(here("coroner_plans", f"{child}_*.json")): err(where, f"descendant {child} has no plan file")

dispositions = []
dp = here("coroner_plans", "DISPOSITIONS.jsonl")
if os.path.exists(dp):
    for i, l in enumerate(open(dp, encoding="utf-8").read().splitlines(), 1):
        if not l.strip(): continue
        try: d = json.loads(l)
        except Exception as e: err("DISPOSITIONS", f"line {i} does not parse: {e}"); continue
        dispositions.append(d); disposition_checks(d, f"DISPOSITIONS:{d.get('disposition_id', i)}")
    ids = [d.get("disposition_id") for d in dispositions]
    if len(ids) != len(set(ids)): err("DISPOSITIONS", "duplicate disposition_id")
    for d in dispositions:
        notes.append(f"disposition {d.get('disposition_id')}: {d.get('plan_id')} {d.get('disposition')} (ruled_by {d.get('ruled_by')}; hypothesis: {str(d.get('hypothesis_status'))[:40]})")

def _expect_disposition_reject(label, mutate):
    if not dispositions: notes.append(f"selftest {label}: skipped (no dispositions)"); return
    before = len(errors)
    bad = copy.deepcopy(dispositions[0]); mutate(bad)
    disposition_checks(bad, f"SELFTEST:{label}")
    if len(errors) == before: errors.append(f"[SELFTEST] {label}: validator ACCEPTED a disposition it must reject")
    else: del errors[before:]; notes.append(f"selftest {label}: rejected as required")

# admissibility ladder negative self-tests
def _mut_admissible_untrusted(b):
    b["necropolis_status"] = "UNTRUSTED"; b["status_reason"] = "x"
    b["self_tests"] = [{"kind": "ACCEPT", "path": RUNNER + "::x", "result": "PASS"}, {"kind": "CHEAT", "path": RUNNER + "::y", "result": "FAIL"}]
    b["admissibility"]["admissible"] = True; b["admissibility"]["admissible_as"] = "EVIDENCE"; b["admissibility"]["blocked_by"] = None
def _mut_author_only_admissible(b):
    b["admissibility"]["controlled"] = "AUTHOR_ONLY"; b["admissibility"]["admissible"] = True
def _mut_caveat_as_plain_evidence(b):
    b["necropolis_status"] = "READY_WITH_CAVEAT"; b["caveat"] = "c"; b["admissibility"]["admissible"] = True
    b["admissibility"]["admissible_as"] = "EVIDENCE"; b["admissibility"]["blocked_by"] = None
def _mut_ready_but_not_admissible(b):
    b["admissibility"]["admissible"] = False; b["admissibility"]["admissible_as"] = "NOT_ADMISSIBLE"; b["admissibility"]["blocked_by"] = "IMPORTS"
_ready_rows = [t for t in tools if t.get("necropolis_status") == "READY" and t.get("admissibility", {}).get("admissible")]
if _ready_rows:
    for label, mut in (("admissible-untrusted", _mut_admissible_untrusted), ("author-tests-as-controls", _mut_author_only_admissible),
                       ("caveat-silently-evidence", _mut_caveat_as_plain_evidence), ("ready-but-ladder-blocked", _mut_ready_but_not_admissible)):
        before = len(errors); bad = copy.deepcopy(_ready_rows[0]); mut(bad)
        row_checks(bad, f"SELFTEST:{label}", set(ids), check_git=False)
        if len(errors) == before: errors.append(f"[SELFTEST] {label}: validator ACCEPTED a row it must reject")
        else: del errors[before:]; notes.append(f"selftest {label}: rejected as required")

_expect_disposition_reject("disposition-hash-drift", lambda d: d.update(plan_sha256_lf="0" * 64))
_expect_disposition_reject("disposition-modified-in-place", lambda d: d.update(plan_modified_in_place=True))
_expect_disposition_reject("disposition-grave-touched", lambda d: d["killed_by"].update(grave_touched=True))
_expect_disposition_reject("disposition-unnamed-control", lambda d: d["killed_by"].update(control_case="not.a.case"))
_expect_disposition_reject("disposition-orphan-descendant", lambda d: d.update(descendants=["CR-999"]))

# ---------------------------------------------------------------- self-tests of the validator
def _expect_reject(label, mutate):
    if not tools: notes.append(f"selftest {label}: skipped (empty registry)"); return
    before = len(errors)
    bad = copy.deepcopy(tools[0]); mutate(bad)
    row_checks(bad, f"SELFTEST:{label}", set(ids), check_git=False)
    if len(errors) == before:
        errors.append(f"[SELFTEST] {label}: validator ACCEPTED a row it must reject")
    else:
        del errors[before:]; notes.append(f"selftest {label}: rejected as required")

def _ready_no_reject(b):
    b["necropolis_status"] = "READY"; b["harvest"]["inspected"] = True
    b["last_verified_execution"] = {"date": "2026-09-13", "by": "x", "how": "python -c pass", "result": "ok"}
    b["self_tests"] = [{"kind": "ACCEPT", "path": "inline:x", "result": "PASS"}]
def _ready_no_exec(b):
    b["necropolis_status"] = "READY"; b["harvest"]["inspected"] = True; b["last_verified_execution"] = None
    b["self_tests"] = [{"kind": "ACCEPT", "path": "inline:x", "result": "PASS"}, {"kind": "REJECT", "path": "inline:x", "result": "PASS"}]
def _dup_no_ref(b):
    b["necropolis_status"] = "DUPLICATE"; b.pop("duplicate_of", None)
def _ready_failed_control(b):
    b["necropolis_status"] = "READY"; b["harvest"]["inspected"] = True
    b["last_verified_execution"] = {"date": "2026-09-13", "by": "x", "how": "python -c pass", "result": "ok"}
    b["self_tests"] = [{"kind": "ACCEPT", "path": "inline:x", "result": "PASS"}, {"kind": "CHEAT", "path": "inline:x", "result": "FAIL"}]
def _bad_status(b): b["necropolis_status"] = "WORKS"
def _ghost_path(b): b["necropolis_status"] = "NEEDS_VALIDATION"; b["current_path"] = "no/such/file.py"
_expect_reject("READY-without-reject-control", _ready_no_reject)
_expect_reject("READY-without-execution", _ready_no_exec)
_expect_reject("DUPLICATE-without-duplicate_of", _dup_no_ref)
_expect_reject("READY-with-failed-cheat", _ready_failed_control)
_expect_reject("status-outside-enum", _bad_status)
_expect_reject("current_path-ghost", _ghost_path)
if tools and _git_ok is not False:
    before = len(errors)
    bad = copy.deepcopy(tools[0]); bad["source_commit"] = "deadbeefdeadbeef"
    row_checks(bad, "SELFTEST:fabricated-commit", set(ids), check_git=True)
    if len(errors) == before: errors.append("[SELFTEST] fabricated-commit: validator ACCEPTED a fake source_commit")
    else: del errors[before:]; notes.append("selftest fabricated-commit: rejected as required")


# ---------------------------------------------------------------- freeze records (reader)
# A freeze record is the reported state at a named commit.  The reader recomputes
# every listed hash and reports MATCH / DRIFT per file.  Drift is a note (the
# registry is regenerated), a malformed or unreadable freeze record is an error.
import hashlib
for fz in sorted(glob.glob(here("FREEZE_*.json"))):
    try:
        rec = json.load(open(fz, encoding="utf-8"))
        files = rec["files"]; assert isinstance(files, dict) and files
    except Exception as e:  # noqa: BLE001
        err("FREEZE", f"{os.path.basename(fz)} unreadable or without files: {e}"); continue
    for rel, want in files.items():
        fp = here(rel)
        if not os.path.exists(fp):
            err("FREEZE", f"{os.path.basename(fz)} lists {rel} which no longer exists"); continue
        b = open(fp, "rb").read().replace(b"\r\n", b"\n")
        got = hashlib.sha256(b).hexdigest()
        notes.append(f"freeze {rec.get('frozen_at')} {rel}: " + ("MATCH" if got == want["sha256_lf"] else f"DRIFT (reported {want['sha256_lf'][:10]}, now {got[:10]})"))

# ---------------------------------------------------------------- forensic map (FORENSIC_QUESTIONS.json)
# The map may cite a row as an answerer only if the registry's ladder admits it; a
# candidate must be a row the ladder blocks; every id must exist; the verdict must
# follow the scope rule (GENERAL -> ANSWERABLE; named restriction -> at most
# ANSWERABLE_RESTRICTED; PARTIAL scope or no DIRECT row -> PARTIAL; none -> EMPTY).
FMAP = here("FORENSIC_QUESTIONS.json")
def forensic_map_checks(fm, where):
    by_id = {t["tool_id"]: t for t in tools}
    for q in fm.get("questions", []):
        w = f"{where}:{q.get('id')}"
        adm = q.get("admissible_instruments", []); cand = q.get("candidates_if_validated", [])
        for x in adm:
            r = by_id.get(x.get("tool_id"))
            if r is None: err(w, f"answerer {x.get('tool_id')} is not in the registry"); continue
            if not r["admissibility"]["admissible"]:
                err(w, f"answerer {x['tool_id']} is NOT admissible in the registry (blocked_by={r['admissibility']['blocked_by']}); the map cannot promote a tool")
            if x.get("admissible_as") != r["admissibility"]["admissible_as"]:
                err(w, f"answerer {x['tool_id']} admissible_as {x.get('admissible_as')} != registry {r['admissibility']['admissible_as']}")
            if r["admissibility"]["admissible_as"] == "EVIDENCE_WITH_CAVEAT" and not x.get("caveat"):
                err(w, f"answerer {x['tool_id']} is EVIDENCE_WITH_CAVEAT but the map drops the caveat")
        for x in cand:
            r = by_id.get(x.get("tool_id"))
            if r is None: err(w, f"candidate {x.get('tool_id')} is not in the registry"); continue
            if r["admissibility"]["admissible"]:
                err(w, f"candidate {x['tool_id']} is admissible in the registry; it belongs under answerers or the mapping is stale")
        direct = [x for x in adm if x.get("role") == "DIRECT"]
        sc = str(q.get("scope", ""))
        if not adm: want = "EMPTY"
        elif not direct or sc.startswith("PARTIAL"): want = "PARTIAL"
        elif sc == "GENERAL": want = "ANSWERABLE"
        else: want = "ANSWERABLE_RESTRICTED"
        if q.get("verdict") != want:
            err(w, f"verdict {q.get('verdict')} but scope/rows imply {want}")
        if sc.startswith("PARTIAL") and direct:
            err(w, "scope declared PARTIAL yet a DIRECT answerer is listed")
if os.path.exists(FMAP):
    try:
        fmap = json.load(open(FMAP, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        fmap = None; err("FORENSIC_MAP", f"unreadable: {e}")
    if fmap:
        forensic_map_checks(fmap, "FORENSIC_MAP")
        notes.append(f"forensic map: {len(fmap.get('questions', []))} questions, verdicts {fmap.get('summary', {}).get('verdicts')}")
        import copy as _copy
        def _expect_fmap_reject(label, mutate):
            bad = _copy.deepcopy(fmap); mutate(bad); before = len(errors)
            forensic_map_checks(bad, f"SELFTEST:{label}")
            if len(errors) == before: err("SELFTEST", f"{label}: forensic map check FAILED to reject")
            else: del errors[before:]; notes.append(f"selftest {label}: rejected as required")
        def _m_promote(b):  # cite an UNTRUSTED row as an answerer
            b["questions"][0]["admissible_instruments"].append({"tool_id": "NT-001", "role": "DIRECT", "admissible_as": "EVIDENCE"})
        def _m_verdict_up(b):  # PARTIAL question relabelled ANSWERABLE
            q = next(q for q in b["questions"] if q["verdict"] == "PARTIAL"); q["verdict"] = "ANSWERABLE"
        def _m_scope_up(b):  # restricted scope relabelled GENERAL keeps verdict -> mismatch
            q = next(q for q in b["questions"] if q["verdict"] == "ANSWERABLE_RESTRICTED"); q["scope"] = "GENERAL"
        def _m_drop_caveat(b):
            for q in b["questions"]:
                for x in q["admissible_instruments"]:
                    if x.get("admissible_as") == "EVIDENCE_WITH_CAVEAT": x.pop("caveat", None); return
        _expect_fmap_reject("fmap-untrusted-answerer", _m_promote)
        _expect_fmap_reject("fmap-verdict-inflated", _m_verdict_up)
        _expect_fmap_reject("fmap-scope-inflated", _m_scope_up)
        _expect_fmap_reject("fmap-caveat-dropped", _m_drop_caveat)
else:
    notes.append("forensic map: absent")

# ---------------------------------------------------------------- report
for n in notes: print("  note:", n)
if errors:
    print(f"\nWORKSHOP VALIDATION: {len(errors)} error(s)")
    for e in errors: print("  ERROR", e)
    sys.exit(1)
print("\nWORKSHOP VALIDATION: ALL GREEN")
