"""G0 and every draft B B9 bundle edit (E01-E05) as in-memory fixtures (C-004-T014).

G0 is the S2 reference bundle of B9: receipts for every B7.1 prerequisite of CL-CAL(STANDARD), CL-RET(REG),
CL-RET(PKTD) and CL-RET(LAGD) (REG and PKTD with observers NULL and BOOKKEEP, LAGD with NULL), one
TWIN_EQ(REG) receipt, complete nodes, a manifest and a terminal inventory. Outcomes are draft A's expected
outcomes taken as given (B9 notation): every gate PASS and RETENTION POSITIVE, except ERASE(LAGD) FAIL.

Every receipt, trace, anchor, stage record and keeper row here is a synthetic software fixture. A custody
QUALIFIED computed from these exercises the logic only and is never custody evidence (B5.3, CONTRACT.md s4,
amendment V8). Nothing here was produced by running a runtime.
"""
import copy
import hashlib
import json

from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R

COMMIT = "c004" + "0" * 36
CONTRACT_REV = hashlib.sha256(b"fixture: rso/slice001/contract/contract.json v1.0.1").hexdigest()
REGISTERED_AT = "2026-10-04T00:00:00Z"
FIRST_CHECK = "2026-10-04T01:00:00Z"
LATE = "2026-10-04T02:00:00Z"
SUBJECTS = ("REG", "PKTD", "LAGD")
OBSERVERS = {"REG": ("BOOKKEEP", "NULL"), "PKTD": ("BOOKKEEP", "NULL"), "LAGD": ("NULL",)}
CODE_PATH = {"BOUNDS": "rso/slice001/world.py", "CALIBRATION": "rso/slice001/rulers.py",
             "RETENTION": "rso/slice001/rulers.py", "ERASE": "rso/slice001/reset.py",
             "PRESERVE": "rso/slice001/reset.py", "CHANNEL": "rso/slice001/reset.py",
             "RESTART": "rso/slice001/reset.py", "OBSERVER": "rso/slice001/observer.py",
             "TWIN_EQ": "rso/slice001/encoding.py"}
ROLES = {"BOUNDS": ("trace:sends",), "CALIBRATION": ("trace:probe_a", "trace:probe_d"),
         "RETENTION": ("trace:probe_a", "trace:probe_d"), "ERASE": ("trace:probe_a", "trace:probe_d"),
         "PRESERVE": ("trace:probe_a", "trace:probe_d"), "CHANNEL": ("trace:clamp",),
         "RESTART": ("trace:capture",), "OBSERVER": ("trace:observer",), "TWIN_EQ": ("trace:probe_a",)}
GATE_CODE = {"G-BIND": "rso/slice001/evidence.py", "G-INV": "rso/slice001/evidence.py",
             "G-RECOMP": "rso/slice001/checker.py"}
_ID = {n: p for p, n in R.PREDICATE_NAMES}


def _h(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def code_ref(path):
    return {"role": "code:" + path, "sha256": _h("blob " + path), "length": 1000, "commit": COMMIT}


def predicate_code(name):
    return [code_ref(CODE_PATH[name])]


def gate_code(gate):
    return [code_ref(GATE_CODE[gate])]


def _repo_ref(path):
    return {"path": path, "blob_sha256": _h("blob " + path), "commit": COMMIT}


def cell(subject, name):
    physics = subject if subject == EV.WORLD_SUBJECT else subject
    return {"cell_id": "W-S1", "revision": CONTRACT_REV, "physics": "%s %s" % (physics, _h("code " + physics)),
            "world": "STANDARD " + _h("world STANDARD"), "boundary": "EPISODE_CONTENT_RESET j=1..3",
            "search": "NONE", "development": "NONE", "resources": _h("OP-1 caps"),
            "measurement": EV.predicate_version(predicate_code(name)), "exposure": "EXPOSURE " + _h("exp")}


def claim_cell(subject):
    c = cell(subject, "BOUNDS")
    del c["measurement"]
    return c


def trace_bytes(node_id, role, tag=""):
    return ("%s|%s|%s|" % (node_id, role, tag) * 8).encode("utf-8")


def _outcome(subject, name):
    pid = _ID[name]
    if name == "RETENTION":
        return {"kind": "RULER", "ruler": pid, "value": "POSITIVE", "statistic": "1/1", "successes": 12288,
                "trials": 12288, "per_boundary": [{"j": j, "statistic": "1/1"} for j in (1, 2, 3)],
                "reason": "RETENTION above exact bound 1/2 (draft A T01 expected)"}
    if subject == "LAGD" and name == "ERASE":
        return {"kind": "GATE", "predicate": pid, "value": "FAIL",
                "reason": "ERASE FAIL at j = 1 (draft A T04 expected)", "witness": {"j": 1, "history": 0},
                "eligible_count": 9600, "applicable_count": 9600, "vacuous": False}
    return {"kind": "GATE", "predicate": pid, "value": "PASS", "reason": "%s held (draft A expected)" % name,
            "witness": None, "eligible_count": 4096, "applicable_count": 4096, "vacuous": False}


def make_receipt_dict(subject, name, run_id, observer=None, world="STANDARD", tag=""):
    nid = R.make_node_id(subject, name, world, observer=observer)
    outputs = [{"role": role, "sha256": hashlib.sha256(trace_bytes(nid, role, tag)).hexdigest(),
                "length": len(trace_bytes(nid, role, tag))} for role in ROLES[name]]
    return {
        "schema": R.SCHEMA, "node_id": nid,
        "registration_ref": _repo_ref("rso/slice001/contract/contract.json"),
        "contract_ref": _repo_ref("rso/slice001/contract/contract.json"),
        "cell": cell(subject, name),
        "subject": {"id": subject, "code": [code_ref("rso/slice001/fixtures/%s.py" % subject.lower())]},
        "observer": ({"id": observer, "code": [code_ref("rso/slice001/observer.py")]}
                     if observer is not None else None),
        "world": {"variant": world, "code": [code_ref("rso/slice001/world.py")]},
        "predicate": {"id": _ID[name], "kind": R.PREDICATE_KINDS[_ID[name]], "code": predicate_code(name)},
        "code": {"producer": [code_ref("rso/slice001/adapter.py")], "base_sha": COMMIT,
                 "branch": "fixture", "worktree_path": "fixture", "dirty": False},
        "inputs": {"domain": {"role": "domain", "sha256": _h("4096 histories"), "length": 4096},
                   "reset_model_sha256": _h("reset model H=3 R=1")},
        "outputs": outputs,
        "oracle": {"role": "oracle", "sha256": _h("truth table"), "length": 4096},
        "expected_answer": {"table": _repo_ref("rso/slice001/expected/EXPECTED_ANSWERS.json"),
                            "row_id": "G0:" + nid},
        "dependencies": sorted(EV.required_deps(nid)),
        "execution": {"status": "RAN", "missing": [], "run_id": run_id},
        "outcome": _outcome(subject, name),
        "resources": {"cpu_seconds": 1, "wall_seconds": 1, "launches": 1, "artifact_bytes": 64},
        "limitations": ["draft A A7: not in the model"],
        "created_at_utc": "2026-10-03T23:00:00Z",
    }


def stage_record(instrument, version):
    path = "ops/campaigns/C-004/fixtures/fire_tests/%s.json" % instrument
    return {"instrument": instrument, "version": version, "stage": "AUTHOR_TESTED",
            "fire_test": {"must_accept": ["T01.REG"],
                          "must_reject": [{"case_id": "T05.WIPE", "expected_reason": "FAIL"}],
                          "receipt": {"path": path, "blob_sha256": hashlib.sha256(
                              fire_blob(instrument)).hexdigest(), "commit": COMMIT}},
            "first_sight": None, "closure": None,
            "recorded_by": "fixture", "recorded_at_utc": "2026-10-03T23:30:00Z"}


def fire_blob(instrument):
    return ("fixture fire-test receipt for %s" % instrument).encode("utf-8")


class Case(object):
    """One bundle with the anchors and store the consumer holds for it."""

    def __init__(self, name, bundle, anchors, store, claims, first_check=FIRST_CHECK, keeper_anchors=None):
        self.name = name
        self.bundle = bundle
        self.anchors = anchors
        self.store = store
        self.claims = claims
        self.first_check = first_check
        self.keeper_anchors = keeper_anchors
        self.config = EV.Config(CONTRACT_REV)


def g0_dicts():
    """The G0 receipt dicts, keyed by node id, with sequential run ids."""
    out, n = {}, 0

    def add(subject, name, observer=None):
        nonlocal n
        n += 1
        d = make_receipt_dict(subject, name, "run-%03d" % n, observer=observer)
        out[d["node_id"]] = d

    add(EV.WORLD_SUBJECT, "CALIBRATION")
    for m in SUBJECTS:
        for name in ("BOUNDS", "RETENTION", "ERASE", "PRESERVE", "CHANNEL", "RESTART"):
            add(m, name)
        for o in OBSERVERS[m]:
            add(m, "OBSERVER", observer=o)
    add("REG", "TWIN_EQ")
    return out


def claims():
    c = {"CL-CAL(STANDARD)": EV.make_claim("CL-CAL", cell=claim_cell(EV.WORLD_SUBJECT))}
    for m in SUBJECTS:
        c["CL-RET(%s)" % m] = EV.make_claim("CL-RET", m, observers=OBSERVERS[m], cell=claim_cell(m))
    c["TWIN(REG)"] = EV.make_claim("TWIN", "REG", cell=claim_cell("REG"))
    c["CL-CUST(G0)"] = EV.make_claim("CL-CUST", bundle_id="G0")
    return c


def _bytes(d):
    return R.Receipt.from_dict(d).canonical_bytes()


def _traces(dicts, tag=""):
    return {nid: {role: trace_bytes(nid, role, tag) for role in ROLES[EV.parse_node_id(nid)[1]]}
            for nid in dicts}


def _inventory(dicts):
    rows = [{"kind": "RUN", "run_id": d["execution"]["run_id"], "node_id": nid, "status": "COMPLETED"}
            for nid, d in sorted(dicts.items(), key=lambda kv: kv[1]["execution"]["run_id"])]
    return rows + [{"kind": "TERMINAL", "row_count": len(rows)}]


def stage_records():
    recs = [stage_record(_ID[name], predicate_code(name)) for name in sorted(CODE_PATH)]
    recs += [stage_record(g, gate_code(g)) for g in sorted(GATE_CODE)]
    return recs


def blobs():
    b = {"ops/campaigns/C-004/fixtures/fire_tests/%s.json" % s["instrument"]: fire_blob(s["instrument"])
         for s in stage_records()}
    return b


EXPECTED_TABLE = {"path": "rso/slice001/expected/EXPECTED_ANSWERS.json",
                  "blob_sha256": _h("fixture expected table"), "commit": COMMIT}


def row(kind, blob, at=REGISTERED_AT, path="fixture"):
    return {"registered_at_utc": at, "registrar": "Aporia (fixture)", "record_kind": kind, "repo_path": path,
            "blob_sha256": blob, "commit_sha": COMMIT, "row_id": "%s:%s" % (kind, blob[:12])}


def stage_rows(at=REGISTERED_AT):
    return [row("STAGE_RECORD", EV.record_blob(s), at) for s in stage_records()]


def make_bundle(dicts, traces=None, inventory=None, withdrawals=()):
    return EV.Bundle({nid: _bytes(d) for nid, d in dicts.items()},
                     traces if traces is not None else _traces(dicts),
                     inventory if inventory is not None else _inventory(dicts),
                     stage_records=stage_records(), withdrawals=withdrawals, blobs=blobs(),
                     expected_table=EXPECTED_TABLE)


def manifest_of(dicts):
    return EV.build_manifest(R.Receipt.from_dict(d) for d in dicts.values())


def retained(dicts):
    """Consumer-retained in-memory anchors taken at registration time (not producer-supplied)."""
    return EV.Anchors(manifest_of(dicts), "keeper")


def keeper_rows(dicts, bundle, at=REGISTERED_AT):
    m = manifest_of(dicts)
    inv = EV.record_blob({"schema": EV.INVENTORY_SCHEMA, "rows": bundle.inventory})
    return ([row("EVIDENCE_MANIFEST", hashlib.sha256(m).hexdigest(), at, "fixtures/G0/MANIFEST.json"),
             row("RUN_INVENTORY", inv, at), row("EXPECTED_ANSWER_TABLE", EXPECTED_TABLE["blob_sha256"], at)]
            + stage_rows(at))


# --------------------------------------------------------------------------------------------------------
# The cases. Each returns a Case; edits are applied to a fresh deep copy of G0.

def g0():
    d = g0_dicts()
    return Case("G0", make_bundle(d), retained(d), EV.FixtureStore(stage_rows()), claims())


def g0_without_lagd():
    d = {k: v for k, v in g0_dicts().items() if EV.parse_node_id(k)[0] != "LAGD"}
    full = g0_dicts()
    return Case("G0-LAGD", make_bundle(d), retained(full), EV.FixtureStore(stage_rows()), claims())


def outcome_edit():
    """E01: LAGD's ERASE rewritten FAIL -> PASS after the run, witness nulled, node and manifest re-hashed
    by the producer; traces intact. Anchors: the producer's re-made manifest."""
    d = g0_dicts()
    orig = copy.deepcopy(d)
    e = d["rcpt:LAGD:ERASE:STANDARD"]
    e["outcome"].update({"value": "PASS", "witness": None, "reason": "ERASE held"})
    c = Case("OUTCOME_EDIT", make_bundle(d), EV.anchors_from_producer(manifest_of(d)),
             EV.FixtureStore(stage_rows()), claims())
    c.keeper_anchors = retained(orig)
    return c


def _fabricate_reg(d):
    """Replace REG's output traces by fabricated ones and make the receipts agree (before registration)."""
    for nid, rd in d.items():
        if EV.parse_node_id(nid)[0] == "REG":
            for out in rd["outputs"]:
                b = trace_bytes(nid, out["role"], "FABRICATED")
                out["sha256"], out["length"] = hashlib.sha256(b).hexdigest(), len(b)
    tr = _traces(d)
    for nid in d:
        if EV.parse_node_id(nid)[0] == "REG":
            tr[nid] = {role: trace_bytes(nid, role, "FABRICATED") for role in ROLES[EV.parse_node_id(nid)[1]]}
    return tr


def fab_consistent():
    """E01 coupling: fabricated, internally consistent REG traces, anchored as presented."""
    d = g0_dicts()
    tr = _fabricate_reg(d)
    return Case("FAB_CONSISTENT", make_bundle(d, traces=tr), retained(d), EV.FixtureStore(stage_rows()),
                claims())


def missing():
    """E02: REG's PRESERVE receipt removed; the inventory still lists its run COMPLETED."""
    d = g0_dicts()
    full = copy.deepcopy(d)
    b = make_bundle(d)
    del b.receipts["rcpt:REG:PRESERVE:STANDARD"]
    del b.traces["rcpt:REG:PRESERVE:STANDARD"]
    return Case("MISSING", b, retained(full), EV.FixtureStore(stage_rows()), claims())


def malformed():
    """E02: REG's ERASE receipt with an unregistered boundary value."""
    d = g0_dicts()
    full = copy.deepcopy(d)
    d["rcpt:REG:ERASE:STANDARD"]["cell"]["boundary"] = "EPISODE_RESET j=1"
    return Case("MALFORMED", make_bundle(d), retained(full), EV.FixtureStore(stage_rows()), claims())


def relabel(rename_ids=False):
    """E02: every REG node's physics and subject renamed REG -> REG2; old anchors. node ids are kept unless
    rename_ids (the two readings of X02; neither is chosen here)."""
    d = g0_dicts()
    full = copy.deepcopy(d)
    out = {}
    for nid, rd in d.items():
        if EV.parse_node_id(nid)[0] == "REG":
            rd["subject"]["id"] = "REG2"
            rd["cell"]["physics"] = "REG2 " + _h("code REG")
            if rename_ids:
                rd["node_id"] = nid.replace("rcpt:REG:", "rcpt:REG2:")
                rd["dependencies"] = sorted(x.replace("rcpt:REG:", "rcpt:REG2:") for x in rd["dependencies"])
        out[rd["node_id"]] = rd
    tr = {}
    for nid, rd in out.items():
        old = nid.replace("rcpt:REG2:", "rcpt:REG:")
        tr[nid] = {role: trace_bytes(old, role) for role in ROLES[EV.parse_node_id(nid)[1]]}
    inv = _inventory(full)
    if rename_ids:
        for r in inv[:-1]:
            r["node_id"] = r["node_id"].replace("rcpt:REG:", "rcpt:REG2:")
    cl = claims()
    if rename_ids:
        c2 = claim_cell("REG")
        c2["physics"] = "REG2 " + _h("code REG")
        cl["CL-RET(REG2)"] = EV.make_claim("CL-RET", "REG2", observers=OBSERVERS["REG"], cell=c2)
    return Case("RELABEL_IDS" if rename_ids else "RELABEL", make_bundle(out, traces=tr, inventory=inv),
                retained(full), EV.FixtureStore(stage_rows()), cl)


def wrong_subject():
    """E02: the RESTART prerequisite slot of CL-RET(REG) holds PKTD's RESTART receipt."""
    d = g0_dicts()
    b = make_bundle(d)
    b.receipts["rcpt:REG:RESTART:STANDARD"] = b.receipts["rcpt:PKTD:RESTART:STANDARD"]
    b.traces["rcpt:REG:RESTART:STANDARD"] = b.traces["rcpt:PKTD:RESTART:STANDARD"]
    return Case("WRONG_SUBJECT", b, retained(d), EV.FixtureStore(stage_rows()), claims())


def strip(manifest_from_stripped=False):
    """E03: CALIBRATION removed from REG's RETENTION deps; node re-hashed; manifest unchanged (or, the
    harder variant, rebuilt from the stripped node)."""
    d = g0_dicts()
    full = copy.deepcopy(d)
    r = d["rcpt:REG:RETENTION:STANDARD"]
    r["dependencies"] = [x for x in r["dependencies"] if "CALIBRATION" not in x]
    anchors = retained(d) if manifest_from_stripped else retained(full)
    return Case("STRIP", make_bundle(d), anchors, EV.FixtureStore(stage_rows()), claims())


def _flip(b):
    x = bytearray(b)
    x[0] ^= 0x01
    return bytes(x)


def byteflip():
    """E03: one byte of REG's RETENTION PROBE_A trace changed, length kept."""
    d = g0_dicts()
    b = make_bundle(d)
    nid = "rcpt:REG:RETENTION:STANDARD"
    b.traces[nid]["trace:probe_a"] = _flip(b.traces[nid]["trace:probe_a"])
    return Case("BYTEFLIP", b, retained(d), EV.FixtureStore(stage_rows()), claims())


def reanchor():
    """E03 coupling: BYTEFLIP plus a receipt and manifest re-made by the producer to match the flipped trace."""
    d = g0_dicts()
    full = copy.deepcopy(d)
    nid = "rcpt:REG:RETENTION:STANDARD"
    tr = _traces(d)
    tr[nid]["trace:probe_a"] = _flip(tr[nid]["trace:probe_a"])
    for out in d[nid]["outputs"]:
        if out["role"] == "trace:probe_a":
            out["sha256"] = hashlib.sha256(tr[nid]["trace:probe_a"]).hexdigest()
    c = Case("REANCHOR", make_bundle(d, traces=tr), EV.anchors_from_producer(manifest_of(d)),
             EV.FixtureStore(stage_rows()), claims())
    c.keeper_anchors = retained(full)
    return c


def withdrawal(wid, target):
    return {"withdrawal_id": wid, "target": target, "reason": "fixture withdrawal", "authority": "Palamedes",
            "at_utc": "2026-10-04T00:30:00Z"}


def restart_stage_node():
    return EV.stage_node_id("P6", EV.predicate_version(predicate_code("RESTART")))


def _withdrawn(name, w, registered=True):
    d = g0_dicts()
    rows = stage_rows() + ([row("WITHDRAWAL", EV.record_blob(w))] if registered else [])
    return Case(name, make_bundle(d, withdrawals=[w]), retained(d), EV.FixtureStore(rows), claims())


def w_restart():
    """E04: anchored withdrawal of the RESTART stage record."""
    return _withdrawn("W_RESTART", withdrawal("W-RESTART", restart_stage_node()))


def w_obs():
    """E04: anchored withdrawal of the OBSERVER(REG, BOOKKEEP) receipt."""
    return _withdrawn("W_OBS", withdrawal("W-OBS", "rcpt:REG:OBSERVER:BOOKKEEP:STANDARD"))


def w_unrelated():
    """E04: anchored withdrawal of the TWIN_EQ receipt (no CL claim depends on it)."""
    return _withdrawn("W_UNRELATED", withdrawal("W-TWIN", "rcpt:REG:TWIN_EQ:STANDARD"))


def w_unanchored():
    """E04: W_RESTART not registered with the keeper."""
    return _withdrawn("W_UNANCHORED", withdrawal("W-RESTART", restart_stage_node()), registered=False)


def fab_anchors():
    """E05: fabricated data with matching fabricated anchors supplied by the producer; no keeper rows."""
    d = g0_dicts()
    tr = _fabricate_reg(d)
    return Case("FAB_ANCHORS", make_bundle(d, traces=tr), EV.anchors_from_producer(manifest_of(d)),
                EV.FixtureStore(stage_rows()), claims())


def late_reg():
    """E05: keeper rows written after the consumer's first check."""
    d = g0_dicts()
    b = make_bundle(d)
    store = EV.FixtureStore(keeper_rows(d, b, at=LATE))
    return Case("LATE_REG", b, retained(d), store, claims())


def _keeper_case(name, d, traces=None):
    b = make_bundle(d, traces=traces)
    store = EV.FixtureStore(keeper_rows(d, b))
    blob_map = {"fixtures/G0/MANIFEST.json": manifest_of(d)}
    return Case(name, b, EV.anchors_from_keeper(store, blob_map), store, claims())


def keeper():
    """E05: G0 with keeper rows for manifest, inventory, stages and expected table, registered before."""
    return _keeper_case("KEEPER", g0_dicts())


def fab_registered():
    """E05 stated limit: FAB_CONSISTENT data registered with the keeper."""
    d = g0_dicts()
    tr = _fabricate_reg(d)
    return _keeper_case("FAB_REGISTERED", d, traces=tr)


CASES = {
    "E01.G0": g0, "E01.OUTCOME_EDIT": outcome_edit, "E01.FAB_CONSISTENT": fab_consistent,
    "E02.MISSING": missing, "E02.MALFORMED": malformed, "E02.RELABEL": relabel,
    "E02.WRONG_SUBJECT": wrong_subject, "E02.G0": g0,
    "E03.STRIP": strip, "E03.BYTEFLIP": byteflip, "E03.REANCHOR": reanchor, "E03.G0": g0,
    "E04.W_RESTART": w_restart, "E04.W_OBS": w_obs, "E04.W_UNRELATED": w_unrelated,
    "E04.W_UNANCHORED": w_unanchored,
    "E05.FAB_ANCHORS": fab_anchors, "E05.LATE_REG": late_reg, "E05.KEEPER": keeper,
    "E05.FAB_REGISTERED": fab_registered,
}


def describe():
    return json.dumps(sorted(CASES))
