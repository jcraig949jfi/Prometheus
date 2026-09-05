"""Cross-engine session-affinity qualification (Harmonia, 2026-09-05).

Runs the charter's ten-step misrouting sequence and the A-H anchor cases
against TWO LIVE SFE ENGINES plus the local PEW, in both directions.

    charter: roles/Mnemosyne/prompts/CHARTER_SESSION_AFFINITY_PROVENANCE_2026-09-05.txt
    frozen bar: SESSION_AFFINITY_QUALIFICATION_SPEC_2026-09-05.md  (read it first)

This harness deliberately does NOT import `sfe`. It speaks HTTP to two engines
and asserts the wire contract written in the spec, so that a defect in the
engine cannot also be the thing defining what "correct" means.

    # plan only -- unauthenticated GETs, prints eligibility, writes nothing
    python roles/Harmonia/qualification/session_affinity_qualification.py

    # the real run
    python roles/Harmonia/qualification/session_affinity_qualification.py --go \
        --m1-url https://192.168.1.202:8811/v2 --m1-cacert .../m1.crt \
        --m2-url https://192.168.1.191:8811/v2 --m2-cacert .../m2.crt \
        --pew-url http://127.0.0.1:8377/api/v1 --pew-token $PEW_TOKEN \
        --expect-m1-engine eng_... --expect-m2-engine eng_...

Exit 0 iff the verdict is QUALIFIED. Every other verdict -- including
NOT_RUN -- exits non-zero, because "the battery could not fire" must never be
mistaken by a shell for "the battery passed".
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import random
import re
import string
import subprocess
import sys
import time

import requests

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
_DEPLOY = (REPO / "SerendipityFoundry" / "SerendipityFoundryEngine" / "deploy")

# --------------------------------------------------------------------------
# THE CONTRACT. Asserted from the frozen spec, not read out of the engine at
# run time. If the engine disagrees with these values the gate FAILS and the
# observed value is reported -- that is a finding about the engine (or about
# a contract change nobody told the qualifier about), and silently adopting
# whatever the engine returned would turn this battery into a mirror.
# --------------------------------------------------------------------------
SESSION_HEADER = "X-SFE-Session"
CODE_WRONG_SESSION = "WRONG_SESSION"
HTTP_WRONG_SESSION = 421
MIN_AFFINITY_SCHEMA = 5

# sfes_<24 hex engine body>_<url-safe tail>
SESSION_KEY_RE = re.compile(r"sfes_([0-9a-f]{24})_[A-Za-z0-9_\-]{16,}")

PASS, FAIL, INDET = "PASS", "FAIL", "INDETERMINATE"


# --------------------------------------------------------------------------
# Redaction. A session key is bearer material: one line in a ledger file is a
# credential leak, and this harness writes its ledger to a git repo. Every
# string that leaves the process passes through here first. The replacement is
# the same fingerprint the engine logs, so a redacted ledger is still
# correlatable against engine logs -- redaction that destroys the ability to
# investigate just moves the problem.
# --------------------------------------------------------------------------
def fingerprint(key: str) -> str:
    return "sfp_" + hashlib.sha256(key.encode()).hexdigest()[:16]


def redact(obj):
    if isinstance(obj, str):
        return SESSION_KEY_RE.sub(lambda m: fingerprint(m.group(0)), obj)
    if isinstance(obj, dict):
        return {k: redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    return obj


class Ledger:
    """Append-only JSONL of every exchange. Flushed per row: a battery that
    dies mid-run must still leave the rows it earned, because the rows are the
    evidence and the summary is only a claim about them."""

    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fh = self.path.open("w", encoding="utf-8")
        self.n = 0

    def write(self, kind, **row):
        self.n += 1
        rec = redact({"i": self.n, "ts": round(time.time(), 3), "kind": kind, **row})
        self.fh.write(json.dumps(rec, sort_keys=True) + "\n")
        self.fh.flush()

    def close(self):
        self.fh.close()


# --------------------------------------------------------------------------
# Clients
# --------------------------------------------------------------------------
class Sfe:
    """One live engine. `label` is what the OPERATOR called it; `identity` is
    what the engine ANSWERED. They are kept separate on purpose -- the entire
    defect under test is a client believing the first when only the second is
    true."""

    def __init__(self, label, url, cacert, ledger, token=None):
        self.label = label
        self.url = url.rstrip("/")
        self.verify = cacert if cacert else True
        self.led = ledger
        self.token = token
        self.session_key = None
        self.session_id = None
        self.identity = None          # filled by probe_identity(), live only

    def req(self, method, path, body=None, *, send_key=True, key=None,
            expect_json=True):
        h = {"content-type": "application/json"}
        if self.token:
            h["authorization"] = "Bearer " + self.token
        k = key if key is not None else (self.session_key if send_key else None)
        if k:
            h[SESSION_HEADER] = k
        u = self.url + path
        try:
            r = requests.request(method, u, headers=h,
                                 json=body if body is not None else None,
                                 verify=self.verify, timeout=30)
            status, payload = r.status_code, (r.json() if expect_json and r.content else {})
        except Exception as e:                                     # noqa: BLE001
            status, payload = None, {"transport_error": repr(e)}
        self.led.write("http", engine=self.label, method=method, path=path,
                       status=status, sent_key=bool(k),
                       key_fp=fingerprint(k) if k else None,
                       request=body, response=payload)
        return status, payload

    # -- identity ----------------------------------------------------------
    def version(self):
        return self.req("GET", "/version")

    def probe_identity(self):
        """Read engine_instance_id from the engine that ANSWERS.

        verify-anchor returns the engine's identity block even for an anchor
        that does not exist, and discloses nothing else, so it is the cheapest
        honest identity probe available. It needs a client credential, which is
        why identity is unknown in plan mode -- and an unknown identity is
        reported as unknown, never guessed from the URL."""
        st, p = self.req("POST", "/audit/verify-anchor", {
            "world_id": "wld_" + "0" * 24,
            "event_id": "evt_" + "0" * 16,
            "entry_hash": "sha256:" + "0" * 64}, send_key=False)
        eng = (p or {}).get("engine") or {}
        self.identity = eng.get("engine_instance_id")
        return self.identity

    def register(self, name):
        st, p = self.req("POST", "/clients", {"name": name}, send_key=False)
        if st == 200 and "token" in p:
            self.token = p["token"]
        return st, p

    # -- session -----------------------------------------------------------
    def create_session(self, name):
        st, p = self.req("POST", "/sessions", {"name": name}, send_key=False)
        if st == 200 and isinstance(p, dict) and p.get("session_key"):
            self.session_key = p["session_key"]
        return st, p


class Pew:
    def __init__(self, url, token, machine, agent, ledger):
        self.base = url.rstrip("/")
        self.h = {"Authorization": f"Bearer {token}",
                  "X-Prometheus-Machine": machine, "X-Prometheus-Agent": agent}
        self.led = ledger

    def _call(self, method, path, body=None):
        u = f"{self.base}/{path.lstrip('/')}"
        try:
            r = requests.request(method, u, headers=self.h, json=body, timeout=60)
            status, payload = r.status_code, (r.json() if r.content else {})
        except Exception as e:                                     # noqa: BLE001
            status, payload = None, {"transport_error": repr(e)}
        self.led.write("pew", method=method, path=path, status=status,
                       request=body, response=payload)
        return status, payload

    def get(self, path):
        return self._call("GET", path)

    def post(self, path, body):
        # Belt and braces: PEW refuses a raw session key with 422, but the
        # harness must not rely on the far side to protect the credential.
        return self._call("POST", path, redact(body))


# --------------------------------------------------------------------------
# Gates
# --------------------------------------------------------------------------
class Gates:
    def __init__(self):
        self.rows = []

    def record(self, name, state, detail, direction=None):
        assert state in (PASS, FAIL, INDET)
        self.rows.append({"gate": name, "state": state, "detail": detail,
                          "direction": direction})
        tag = {PASS: "PASS", FAIL: "FAIL", INDET: "INDT"}[state]
        d = f" [{direction}]" if direction else ""
        print(f"[{tag}] {name}{d}: {detail}")
        return state == PASS

    def gate(self, name, ok, detail, direction=None):
        return self.record(name, PASS if ok else FAIL, detail, direction)

    def indet(self, name, reason, direction=None):
        return self.record(name, INDET, reason, direction)

    def counts(self):
        c = {PASS: 0, FAIL: 0, INDET: 0}
        for r in self.rows:
            c[r["state"]] += 1
        return c

    def verdict(self, eligible):
        """The frozen rule from spec section 4. Note the order: a zero
        eligible count outranks everything, because a battery that could not
        fire has measured nothing and must not be reported as clean."""
        c = self.counts()
        if eligible == 0:
            return "NOT_RUN"
        if c[FAIL]:
            return "NOT_QUALIFIED"
        if c[INDET]:
            return "QUALIFIED_WITH_GAPS"
        return "QUALIFIED"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def err_code(payload):
    """The machine-readable code out of a FoundryError body, whatever nesting
    FastAPI wrapped it in."""
    if not isinstance(payload, dict):
        return None
    d = payload.get("detail", payload)
    if isinstance(d, dict):
        return d.get("error")
    return None


def err_field(payload, field):
    d = (payload or {}).get("detail", payload)
    return d.get(field) if isinstance(d, dict) else None


def key_claims_engine(key):
    """Parse the engine instance id out of a session key CLIENT-SIDE. This is
    the property that makes a wrong-engine answer possible without a lookup, so
    the qualifier checks it independently rather than taking the engine's word
    for its own design."""
    m = SESSION_KEY_RE.fullmatch(key or "")
    return ("eng_" + m.group(1)) if m else None


def tag():
    return "affq-%d-%s" % (int(time.time()),
                           "".join(random.choice(string.ascii_lowercase)
                                   for _ in range(4)))


def sealed_run(e: Sfe, name):
    """Produce one genuine evidence-bearing run on `e` and return its anchor.

    Mirrors closure_battery.sfe_sealed_run: hypothesis -> committed experiment
    -> observation, then resolve the anchoring ledger event by STRICT SINGLE
    MATCH on refs.obs_id. Ambiguity is an error and never a guess -- picking
    'some plausible event' is exactly the wrong-but-real anchor the C4b gate
    exists to reject."""
    st, w = e.req("POST", "/worlds", {
        "session_id": e.session_id, "name": name, "seed_root": 424242,
        "sharing_policy": "ISOLATED",
        "budget": {"ticks": {"limit": 9, "enforcement": "enforceable"}}})
    if st != 200:
        return None, ("world create -> %s %s" % (st, err_code(w)))
    wid = w["world_id"]
    e.req("POST", f"/worlds/{wid}/start")
    st, h = e.req("POST", f"/worlds/{wid}/hypotheses", {"statement": "H"})
    st, x = e.req("POST", f"/worlds/{wid}/experiments", {
        "spec": {"action": "encounter", "ticks": 32},
        "hyp_id": h.get("hyp_id"), "commit": True})
    eid = x.get("exp_id")
    st, o = e.req("POST", f"/worlds/{wid}/observations", {
        "exp_id": eid, "content": {"score": 0.5}, "outcome": "SURVIVED"})
    oid = o.get("obs_id")
    st, evs = e.req("GET", f"/worlds/{wid}/events?limit=500")
    events = evs.get("events", evs) if isinstance(evs, dict) else evs
    anchors = [ev for ev in (events or [])
               if (json.loads(ev["refs"]) if isinstance(ev.get("refs"), str)
                   else (ev.get("refs") or {})).get("obs_id") == oid]
    wc = next((ev for ev in (events or [])
               if ev.get("event_type") == "WORLD_CREATED"), None)
    if len(anchors) != 1:
        return None, ("anchor resolution ambiguous: %d candidates" % len(anchors))
    a = anchors[0]
    return {"world_id": wid, "exp_id": eid, "obs_id": oid,
            "event_id": a["event_id"], "entry_hash": a["entry_hash"],
            "wc_event_id": (wc or {}).get("event_id"),
            "wc_entry_hash": (wc or {}).get("entry_hash"),
            "engine_instance_id": e.identity,
            "session_id": e.session_id}, None


# --------------------------------------------------------------------------
# Preflight
# --------------------------------------------------------------------------
def preflight(g, m1, m2, args, led):
    """Read-only, fail-fast. Returns (eligible: bool, abort_reason: str|None)."""
    v = {}
    for e in (m1, m2):
        st, p = e.version()
        ok = st == 200 and isinstance(p, dict)
        g.gate(f"P0_{e.label}_reachable", ok, f"/version -> {st}")
        if not ok:
            return False, f"{e.label} unreachable"
        v[e.label] = p

    g.record("P1_versions_recorded", PASS, json.dumps(
        {k: {"schema": p.get("schema_version"),
             "source_commit": (p.get("source_commit") or "")[:9],
             "engine_source_hash": (p.get("engine_source_hash") or "")[:22]}
         for k, p in v.items()}, sort_keys=True))

    schemas = {k: p.get("schema_version") for k, p in v.items()}
    eligible = all(isinstance(s, int) and s >= MIN_AFFINITY_SCHEMA
                   for s in schemas.values())
    if eligible:
        g.gate("P2_affinity_eligible", True, f"schema {schemas} >= {MIN_AFFINITY_SCHEMA}")
    else:
        g.indet("P2_affinity_eligible",
                f"schema {schemas}; affinity requires >= {MIN_AFFINITY_SCHEMA} on BOTH "
                "engines. Eligible count 0 -> verdict NOT_RUN.")

    if not args.go:
        g.indet("P3_engine_identities_distinct",
                "plan mode: identity probe needs a client credential and would "
                "be a write; identity is reported unknown, never inferred from "
                "the URL")
        g.indet("P4_expected_identity_binding", "plan mode")
        return eligible, None

    # identity, live, from the engine that answers
    for e in (m1, m2):
        if not e.token:
            e.register(f"harmonia-affq-{e.label}")
        e.probe_identity()
    same = m1.identity is not None and m1.identity == m2.identity
    if m1.identity is None or m2.identity is None:
        g.indet("P3_engine_identities_distinct",
                f"identity unreadable (m1={m1.identity} m2={m2.identity})")
        return eligible, "engine identity unreadable; refusing to write"
    g.gate("P3_engine_identities_distinct", not same,
           f"m1={m1.identity} m2={m2.identity}")
    if same:
        # ABORT, before the first world is created. Precedent NB-7: a battery
        # that reports FAIL and keeps going contaminates the wrong machine.
        return eligible, ("both URLs answer with the SAME engine_instance_id "
                          f"{m1.identity}: split brain or misconfigured target")

    exp = {"M1": args.expect_m1_engine, "M2": args.expect_m2_engine}
    unsupplied = [k for k, x in exp.items() if not x]
    if unsupplied:
        g.indet("P4_expected_identity_binding",
                "no --expect-*-engine supplied for " + ",".join(unsupplied) +
                f"; observed m1={m1.identity} m2={m2.identity}. Recorded, not "
                "verified: without an independently supplied expectation this "
                "gate would only be comparing the engine to itself.")
    else:
        ok = (m1.identity == exp["M1"] and m2.identity == exp["M2"])
        g.gate("P4_expected_identity_binding", ok,
               f"expected {exp}, observed m1={m1.identity} m2={m2.identity}")
        if not ok:
            return eligible, "an engine is not the engine the operator expected"

    led.write("provenance", **harness_provenance())
    g.record("P5_harness_provenance", PASS, json.dumps(harness_provenance()))
    return eligible, None


def harness_provenance():
    def sh(*c):
        try:
            return subprocess.run(c, cwd=str(REPO), capture_output=True,
                                  text=True, timeout=30).stdout.strip()
        except Exception:                                          # noqa: BLE001
            return "?"
    return {"repo_head": sh("git", "rev-parse", "HEAD")[:12],
            "tree_dirty": bool(sh("git", "status", "--porcelain")),
            "harness_sha256": hashlib.sha256(
                pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}


# --------------------------------------------------------------------------
# The ten-step sequence, one direction
# --------------------------------------------------------------------------
def run_sequence(g, home: Sfe, foreign: Sfe, pew: Pew, t):
    d = f"{home.label}->{foreign.label}"

    # S1 -------------------------------------------------------------------
    st, s = home.create_session(f"{t}-{home.label}")
    key = s.get("session_key") if isinstance(s, dict) else None
    home.session_id = s.get("session_id") if isinstance(s, dict) else None
    g.gate("S1_session_issued_with_key", bool(key) and
           s.get("affinity_mode") == "STRICT" and
           s.get("engine_instance_id") == home.identity,
           f"status={st} has_key={bool(key)} mode={s.get('affinity_mode')} "
           f"engine={s.get('engine_instance_id')} (live identity {home.identity})", d)
    if not key:
        g.indet("S2_key_claims_home_engine", "no key issued", d)
        return None

    # S2 -------------------------------------------------------------------
    claimed = key_claims_engine(key)
    g.gate("S2_key_claims_home_engine", claimed == home.identity,
           f"key claims {claimed}, home is {home.identity}", d)

    # S3 -------------------------------------------------------------------
    run, why = sealed_run(home, f"{t}-home")
    if run is None:
        g.gate("S3_evidence_produced_on_home", False, why, d)
        return None
    g.gate("S3_evidence_produced_on_home", True,
           f"world={run['world_id']} exp={run['exp_id']} obs={run['obs_id']}", d)

    # S4 -------------------------------------------------------------------
    enc = f"AFFQ-{t}-{home.label}"
    st, w = pew.post("fossil/encounters", {
        "encounter_id": enc, "run_id": "r1", "namespace": "test",
        "sfe_world_id": run["world_id"], "sfe_event_id": run["event_id"],
        "sfe_entry_hash": run["entry_hash"],
        "sfe_engine_instance_id": home.identity,
        "sfe_session_id": home.session_id,
        "sfe_session_key_fp": fingerprint(key),
        "sfe_affinity_mode": "STRICT",
        "producer": {"exp_id": run["exp_id"], "obs_id": run["obs_id"]}})
    st2, rb = pew.get(f"fossil/encounters/{enc}")
    att = ((rb.get("runs") or [{}])[0].get("attestation") or {}) if isinstance(rb, dict) else {}
    g.gate("S4_home_anchor_binds_in_pew",
           st == 200 and att.get("sfe_anchor_verified") is True,
           f"write={st} verified={att.get('sfe_anchor_verified')} "
           f"checks={att.get('sfe_anchor_checks')}", d)

    # S5 -- the headline: same key, same world id, WRONG engine --------------
    before_st, before = foreign.req("GET", "/worlds")
    st, p = foreign.req("GET", f"/worlds/{run['world_id']}", key=key)
    code = err_code(p)
    g.gate("S5_foreign_rejects_wrong_session",
           st == HTTP_WRONG_SESSION and code == CODE_WRONG_SESSION,
           f"status={st} code={code} (contract: {HTTP_WRONG_SESSION}/{CODE_WRONG_SESSION})", d)
    g.gate("S5b_refusal_is_not_missing_or_broken",
           st not in (404, 500, None),
           f"status={st}: a 404 sends an operator hunting for missing data and "
           f"a 500 hides the diagnosis; neither says 'wrong machine'", d)
    claimed_e = err_field(p, "claimed_engine_instance_id")
    this_e = err_field(p, "this_engine_instance_id")
    g.gate("S5c_refusal_names_both_engines",
           claimed_e == home.identity and this_e == foreign.identity,
           f"claimed={claimed_e} (home {home.identity}) answering={this_e} "
           f"(foreign {foreign.identity})", d)

    after_st, after = foreign.req("GET", "/worlds")
    def ids(x):
        ws = x.get("worlds", x) if isinstance(x, dict) else x
        return sorted(w.get("world_id") for w in (ws or []))
    g.gate("S5d_foreign_left_no_trace",
           before_st == after_st == 200 and ids(before) == ids(after)
           and run["world_id"] not in ids(after),
           f"foreign world set unchanged={ids(before) == ids(after)}, "
           f"home world present on foreign={run['world_id'] in ids(after)}", d)

    # S6 -- PEW must not manufacture a success around the failed op ----------
    enc_bad = f"AFFQ-{t}-{home.label}-MISROUTE"
    st, w = pew.post("fossil/encounters", {
        "encounter_id": enc_bad, "run_id": "r1", "namespace": "test",
        "sfe_world_id": run["world_id"], "sfe_event_id": run["event_id"],
        "sfe_entry_hash": run["entry_hash"],
        "sfe_engine_instance_id": foreign.identity,   # the LIE under test
        "sfe_session_id": home.session_id,
        "sfe_affinity_mode": "STRICT",
        "producer": {"exp_id": run["exp_id"], "obs_id": run["obs_id"]}})
    st2, rb = pew.get(f"fossil/encounters/{enc_bad}")
    att = ((rb.get("runs") or [{}])[0].get("attestation") or {}) if isinstance(rb, dict) else {}
    refused = st in (409, 422)
    g.gate("S6_pew_no_misleading_artifact",
           refused or att.get("sfe_anchor_verified") is not True,
           f"write={st} verified={att.get('sfe_anchor_verified')} "
           f"(a fossil claiming the foreign engine for a home anchor must "
           f"never verify)", d)

    # S7 -- back home, work continues ---------------------------------------
    st, p = home.req("GET", f"/worlds/{run['world_id']}", key=key)
    g.gate("S7_home_continues_after_misroute", st == 200,
           f"home GET world -> {st}", d)

    # S8 -- one lineage ------------------------------------------------------
    st, rb = pew.get(f"fossil/encounters/{enc}")
    runs = rb.get("runs", []) if isinstance(rb, dict) else []
    engines = {r.get("sfe_engine_instance_id") for r in runs} - {None}
    sessions = {r.get("sfe_session_id") for r in runs} - {None}
    g.gate("S8_single_engine_and_session_lineage",
           engines <= {home.identity} and sessions <= {home.session_id}
           and len(engines) <= 1 and len(sessions) <= 1,
           f"engines={engines or 'none recorded'} sessions={sessions or 'none recorded'}", d)

    # S9 -- a genuine FOREIGN anchor must not close the HOME chain -----------
    fst, fs = foreign.create_session(f"{t}-{foreign.label}")
    foreign.session_id = fs.get("session_id") if isinstance(fs, dict) else None
    frun, why = sealed_run(foreign, f"{t}-foreign")
    if frun is None:
        g.indet("S9_foreign_anchor_cannot_close", f"could not seal on foreign: {why}", d)
    else:
        enc_sub = f"AFFQ-{t}-{home.label}-SUBST"
        st, w = pew.post("fossil/encounters", {
            "encounter_id": enc_sub, "run_id": "r1", "namespace": "test",
            "sfe_world_id": frun["world_id"], "sfe_event_id": frun["event_id"],
            "sfe_entry_hash": frun["entry_hash"],
            "sfe_engine_instance_id": home.identity,   # claims HOME, is FOREIGN
            "sfe_session_id": home.session_id,
            "sfe_affinity_mode": "STRICT",
            "producer": {"exp_id": run["exp_id"], "obs_id": run["obs_id"]}})
        st2, rb = pew.get(f"fossil/encounters/{enc_sub}")
        att = ((rb.get("runs") or [{}])[0].get("attestation") or {}) if isinstance(rb, dict) else {}
        g.gate("S9_foreign_anchor_cannot_close",
               st in (409, 422) or att.get("sfe_anchor_verified") is not True,
               f"write={st} verified={att.get('sfe_anchor_verified')} "
               f"(a real M-other anchor dressed as this chain)", d)
    return run


# --------------------------------------------------------------------------
# Anchor verification, charter cases A-H
# --------------------------------------------------------------------------
def run_anchor_cases(g, home: Sfe, foreign: Sfe, run, t):
    d = f"{home.label}->{foreign.label}"
    if run is None:
        for n in "ABCDEFGH":
            g.indet(f"V{n}", "no sealed home run to verify against", d)
        return

    def verify(**kw):
        body = {"world_id": run["world_id"], "event_id": run["event_id"],
                "entry_hash": run["entry_hash"]}
        body.update(kw)
        st, p = home.req("POST", "/audit/verify-anchor", body)
        return st, p

    st, p = verify(exp_id=run["exp_id"], obs_id=run["obs_id"])
    g.gate("VA_correct_binding_verifies", p.get("valid") is True,
           f"valid={p.get('valid')} checks={p.get('checks')}", d)

    # VB/VC: SFE does not yet assert binds_session (EXECUTION_LINEAGE s4, B1).
    # Passing these on binds_engine_instance alone would be the harness lying
    # to itself -- VB is a SAME-ENGINE test, so engine binding cannot possibly
    # discriminate it.
    checks = p.get("checks") or {}
    if "binds_session" not in checks:
        g.indet("VB_wrong_session_same_engine",
                "INDETERMINATE_BLOCKER_B1: verify-anchor returns no "
                f"binds_session; checks={sorted(checks)}", d)
        g.indet("VC_session_from_other_engine",
                "INDETERMINATE_BLOCKER_B1: no binds_session to discriminate on; "
                "engine binding alone cannot answer this", d)
    else:
        st2, s2 = home.create_session(f"{t}-vb")
        st, p2 = verify(exp_id=run["exp_id"], obs_id=run["obs_id"],
                        session_id=s2.get("session_id"))
        g.gate("VB_wrong_session_same_engine", p2.get("valid") is False,
               f"valid={p2.get('valid')} checks={p2.get('checks')}", d)
        st, p3 = verify(exp_id=run["exp_id"], obs_id=run["obs_id"],
                        session_id=getattr(foreign, "session_id", None))
        g.gate("VC_session_from_other_engine", p3.get("valid") is False,
               f"valid={p3.get('valid')} checks={p3.get('checks')}", d)

    st, p = verify(exp_id="exp_" + "0" * 16, obs_id=run["obs_id"])
    g.gate("VD_wrong_exp_rejected", p.get("valid") is False
           and (p.get("checks") or {}).get("binds_exp_id") is False,
           f"valid={p.get('valid')} binds_exp_id="
           f"{(p.get('checks') or {}).get('binds_exp_id')}", d)

    st, p = verify(exp_id=run["exp_id"], obs_id="obs_" + "0" * 16)
    g.gate("VE_wrong_obs_rejected", p.get("valid") is False
           and (p.get("checks") or {}).get("binds_obs_id") is False,
           f"valid={p.get('valid')} binds_obs_id="
           f"{(p.get('checks') or {}).get('binds_obs_id')}", d)

    # VF: a random fingerprint must not be able to buy verification. With B1
    # open the engine has nothing to check it against, so the honest report is
    # INDETERMINATE carrying the observed value -- not a PASS earned by a
    # check that was never performed.
    st, p = verify(exp_id=run["exp_id"], obs_id=run["obs_id"],
                   session_fp="sfp_" + "f" * 16)
    if "binds_session" in (p.get("checks") or {}):
        g.gate("VF_random_fingerprint_rejected",
               (p.get("checks") or {}).get("binds_session") is False,
               f"checks={p.get('checks')}", d)
    else:
        g.indet("VF_random_fingerprint_rejected",
                "INDETERMINATE_BLOCKER_B1: engine ignores an unknown session "
                f"fingerprint (valid={p.get('valid')}); nothing was checked, so "
                "nothing is proven", d)

    # VG: replayed pre-session evidence must stay LEGACY, never be dressed as
    # STRICT. This one IS testable today -- it is a PEW rule, not an SFE one.
    g.indet("VG_legacy_replay_not_fabricated",
            "exercised by PEW's own migration gates (EXECUTION_LINEAGE s3: "
            "STRICT without engine+session -> 422); not re-run here to avoid "
            "reporting Mnemosyne's gate as this battery's evidence", d)

    g.indet("VH_restore_continuity",
            "requires an operator-performed restore of an engine database; "
            "policy is documented in EXECUTION_LINEAGE s6 but the restore was "
            "not performed by this run, so nothing was measured", d)


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m1-url", default="https://192.168.1.202:8811/v2")
    ap.add_argument("--m2-url", default="https://192.168.1.191:8811/v2")
    ap.add_argument("--m1-cacert", default=str(_DEPLOY / "m1.crt"))
    ap.add_argument("--m2-cacert", default=str(_DEPLOY / "m2.crt"))
    ap.add_argument("--m1-token", default=os.environ.get("AFFQ_M1_TOKEN"))
    ap.add_argument("--m2-token", default=os.environ.get("AFFQ_M2_TOKEN"))
    ap.add_argument("--expect-m1-engine", default=None)
    ap.add_argument("--expect-m2-engine", default=None)
    ap.add_argument("--pew-url", default="http://127.0.0.1:8377/api/v1")
    ap.add_argument("--pew-token", default=os.environ.get("PEW_TOKEN", ""))
    ap.add_argument("--machine", default="M1")
    ap.add_argument("--agent", default="harmonia")
    ap.add_argument("--direction", choices=["both", "m1m2", "m2m1"], default="both")
    ap.add_argument("--out", default=str(HERE / "results"))
    ap.add_argument("--go", action="store_true",
                    help="actually write to the live engines and PEW; without "
                         "it the run is a plan and touches nothing")
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    led = Ledger(out / "affinity_qualification_ledger.jsonl")
    g = Gates()

    m1 = Sfe("M1", a.m1_url, a.m1_cacert, led, a.m1_token)
    m2 = Sfe("M2", a.m2_url, a.m2_cacert, led, a.m2_token)
    pew = Pew(a.pew_url, a.pew_token, a.machine, a.agent, led)

    print("=" * 72)
    print("SESSION AFFINITY QUALIFICATION -- %s" % ("LIVE RUN" if a.go else "PLAN ONLY"))
    print("bar: SESSION_AFFINITY_QUALIFICATION_SPEC_2026-09-05.md")
    print("=" * 72)

    eligible, abort = preflight(g, m1, m2, a, led)

    if abort:
        g.record("PREFLIGHT_ABORT", FAIL, abort)
        print("\nABORTED BEFORE ANY WRITE: " + abort)
        verdict = "NOT_RUN"
    elif not eligible:
        print("\nELIGIBLE COUNT 0 -- the affinity mechanism is not deployed on "
              "both engines. No gate below can fire.")
        verdict = "NOT_RUN"
    elif not a.go:
        print("\nPLAN. Eligible and ready; re-run with --go to execute:")
        for line in ("S1 session+key on HOME", "S2 key claims HOME engine",
                     "S3 sealed run on HOME", "S4 anchor binds in PEW",
                     "S5/S5b/S5c/S5d FOREIGN rejects, distinguishably, without trace",
                     "S6 PEW writes no misleading artifact",
                     "S7 HOME continues", "S8 one engine + one session lineage",
                     "S9 FOREIGN anchor cannot close the HOME chain",
                     "VA-VH anchor cases", "then the same, reversed"):
            print("   " + line)
        verdict = "NOT_RUN"
    else:
        t = tag()
        pairs = {"both": [(m1, m2), (m2, m1)], "m1m2": [(m1, m2)],
                 "m2m1": [(m2, m1)]}[a.direction]
        for home, foreign in pairs:
            print(f"\n--- direction {home.label} -> {foreign.label} ---")
            run = run_sequence(g, home, foreign, pew, t)
            run_anchor_cases(g, home, foreign, run, t)
        verdict = g.verdict(sum(1 for r in g.rows if r["state"] != INDET))

    c = g.counts()
    gaps = [r["gate"] for r in g.rows if r["state"] == INDET]
    report = {"verdict": verdict, "counts": c, "eligible_affinity": bool(eligible),
              "mode": "live" if a.go else "plan", "indeterminate": gaps,
              "ledger_rows": led.n, "gates": g.rows,
              "provenance": harness_provenance()}
    out.mkdir(parents=True, exist_ok=True)
    (out / "affinity_qualification_results.json").write_text(
        json.dumps(report, indent=1), encoding="utf-8")
    led.close()

    print("\n" + "=" * 72)
    print(f"VERDICT: {verdict}   pass={c[PASS]} fail={c[FAIL]} indeterminate={c[INDET]}")
    if gaps:
        print("NAMED GAPS (an unnamed gap is a false clean result):")
        for x in gaps:
            print("   - " + x)
    print(f"rows: {led.path}")
    print("=" * 72)
    return 0 if verdict == "QUALIFIED" else 1


if __name__ == "__main__":
    sys.exit(main())
