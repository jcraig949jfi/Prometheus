"""G0 and every draft B B9 bundle edit (E01-E05) as in-memory fixtures (C-004-T014).

G0 is the S2 reference bundle of B9: receipts for every B7.1 prerequisite of CL-CAL(STANDARD), CL-RET(REG),
CL-RET(PKTD) and CL-RET(LAGD) (REG and PKTD with observers NULL and BOOKKEEP, LAGD with NULL), one
TWIN_EQ(REG) receipt, complete nodes, a manifest and a terminal inventory. Outcomes are draft A's expected
outcomes taken as given (B9 notation): every gate PASS and RETENTION POSITIVE, except ERASE(LAGD) FAIL.

Every receipt, trace, anchor, stage record and keeper row here is a synthetic software fixture. A custody
QUALIFIED computed from these exercises the logic only and is never custody evidence (B5.3, CONTRACT.md s4,
amendment V8). Nothing here was produced by running a runtime.

C-004-T024: every case is a function of a BASE bundle (class Base): `case(base=None)` applies the B9 edit to
`base`, and base=None is the synthetic G0 above, unchanged byte for byte. `real_base(g0, ...)` wraps a G0
built from real executions (s2_bundle.build_g0) so T020 can apply the same edits to it.

C-009-T011 (rso/binding/CONTRACT.md BX1-BX3): inventories and manifests carry the binding fields the producer
writes (C-009-T010; rso/binding/contract.json row_fields). An inventory opens with the TOP_LEVEL row of the
launch that produced the bundle; every receipt row names it as parent_run_id and records receipt_sha256, the
sha256 of the receipt's canonical bytes; the manifest names the launch as launch_run_id; the bundle's run.json
(Bundle.run_id) names it too. An inventory derived for edited dicts records the digests of the receipts as
presented: a B9 edit is the producer's own, made before it wrote its inventory, so E01-E05 keep their expected
answers. A receipt edited AFTER its run, against the inventory written at the run, is ARTIFACT_SWAP
(fixtures/cc1_cases.py). Fixture code calls no C-009 consumer API, so the same cases run unchanged on the
FREEZE_R2 code (CC1 RED).
"""
import collections
import copy
import hashlib
import json

from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R

COMMIT = "c004" + "0" * 36
LAUNCH = "fixture-launch-G0"        # the TOP_LEVEL launch of the synthetic G0 (its run ids carry no <launch>/)
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

    def __init__(self, name, bundle, anchors, store, claims, first_check=FIRST_CHECK, keeper_anchors=None,
                 revision=CONTRACT_REV):
        self.name = name
        self.bundle = bundle
        self.anchors = anchors
        self.store = store
        self.claims = claims
        self.first_check = first_check
        self.keeper_anchors = keeper_anchors
        self.config = EV.Config(revision)


class Base(object):
    """What every B9 edit starts from: receipt dicts by node id, their trace bytes, the run inventory (None:
    derived from the dicts' run ids), the stage records and blobs the bundle cites, the expected-table ref,
    the contract revision, and fabricate(node_id, role) -> other bytes for the FAB cases. Never mutated."""

    def __init__(self, dicts, traces, inventory, stage_records, blobs, expected_table, revision, fabricate,
                 launch=None):
        self._dicts, self._traces = dicts, traces
        self._inventory = inventory
        self.launch = launch or launch_of(dicts)
        self.stage_records, self.blobs = stage_records, blobs
        self.expected_table, self.revision, self.fabricate = expected_table, revision, fabricate

    def dicts(self):
        return copy.deepcopy(self._dicts)

    def traces(self, dicts=None):
        keys = self._dicts if dicts is None else dicts
        return {nid: dict(self._traces[nid]) for nid in keys}

    def inventory(self, dicts=None):
        """The base's rows (a real base's as produced; the synthetic base's derived from its own dicts), the
        receipt rows of its launch recording the digests of `dicts` -- the receipts as presented, where a
        presented receipt still cites its row (see the module note)."""
        rows = copy.deepcopy(self._inventory) if self._inventory is not None else _inventory(self._dicts)
        return _redigest(rows, self._dicts if dicts is None else dicts, self.launch)

    def stage_rows(self, at=REGISTERED_AT):
        return [row("STAGE_RECORD", EV.record_blob(s), at) for s in self.stage_records]


def synthetic_base():
    d = g0_dicts()
    return Base(d, _traces(d), None, stage_records(), blobs(), EXPECTED_TABLE, CONTRACT_REV,
                lambda nid, role: trace_bytes(nid, role, "FABRICATED"))


def real_base(g0, stage_records=(), blobs=None, expected_table=None, fabricate=None):
    """A Base over a real G0 (s2_bundle.G0). fabricate defaults to: the trace of PKTD's receipt of the same
    predicate and role -- another runtime's real, internally consistent bytes, as T015's tests fabricate the
    synthetic G0 (FD-T024-3); where PKTD has no such trace, the node's own bytes reversed."""
    dicts = {nid: copy.deepcopy(d) for nid, d in g0.dicts.items()}
    any_d = next(iter(dicts.values()))

    def other(nid, role):
        subject, name, obs, world = EV.parse_node_id(nid)
        alt = R.make_node_id("PKTD", name, world, observer=obs) if subject != "PKTD" else None
        if alt in g0.traces and role in g0.traces[alt]:
            return g0.traces[alt][role]
        return g0.traces[nid][role][::-1]

    return Base(dicts, g0.traces, g0.inventory, list(stage_records), dict(blobs or {}),
                expected_table or any_d["expected_answer"]["table"], any_d["cell"]["revision"],
                fabricate or other, launch=g0.run_id)


def bind_legacy(g0):
    """A G0 produced before C-009 (s2/G0, s4/G0: rows without binding fields, manifest without launch_run_id) in
    the bound form. FIXTURE, not a production: every RECEIPT row named <launch>/<node> whose <launch> is a
    TOP_LEVEL row of the inventory gets parent_run_id = <launch> (s2_bundle's naming rule); the receipt digests
    of the bundle's own launch come from Base.inventory; the manifest gains launch_run_id = run.json's run_id.
    A stand-in for CC1 until T020's fresh produce writes these fields itself."""
    tops = {r["run_id"] for r in g0.inventory if r.get("kind") == "RUN" and r.get("launch_kind") == "TOP_LEVEL"}
    rows = []
    for r in g0.inventory:
        r = dict(r)
        if r.get("kind") == "RUN" and r.get("launch_kind") == "RECEIPT" and "parent_run_id" not in r:
            parent = r["run_id"].split("/", 1)[0]
            if parent in tops:
                r["parent_run_id"] = parent
        rows.append(r)
    doc = R.loads_canonical(g0.manifest)
    doc.setdefault("launch_run_id", g0.run_id)
    return type(g0)(g0.dicts, g0.traces, rows, R.canonical_bytes(doc), g0.run_id)


def _base(base):
    return synthetic_base() if base is None else base


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


def claims(base=None):
    """The B9 claims. Each claim's cell is its subject's receipt cell without measurement (for CL-CAL, the
    CALIBRATION node's), read from the base, so a real G0 gets claims in its own registered cell."""
    if base is None:
        c = {"CL-CAL(STANDARD)": EV.make_claim("CL-CAL", cell=claim_cell(EV.WORLD_SUBJECT))}
        cells = {m: claim_cell(m) for m in SUBJECTS}
    else:
        d = base._dicts

        def strip_m(nid):
            x = dict(d[nid]["cell"])
            del x["measurement"]
            return x
        c = {"CL-CAL(STANDARD)": EV.make_claim("CL-CAL", cell=strip_m("rcpt:WORLD:CALIBRATION:STANDARD"))}
        cells = {m: strip_m(R.make_node_id(m, "BOUNDS", "STANDARD")) for m in SUBJECTS}
    for m in SUBJECTS:
        c["CL-RET(%s)" % m] = EV.make_claim("CL-RET", m, observers=OBSERVERS[m], cell=cells[m])
    c["TWIN(REG)"] = EV.make_claim("TWIN", "REG", cell=cells["REG"])
    c["CL-CUST(G0)"] = EV.make_claim("CL-CUST", bundle_id="G0")
    return c


def _bytes(d):
    return R.Receipt.from_dict(d).canonical_bytes()


def _traces(dicts, tag=""):
    return {nid: {role: trace_bytes(nid, role, tag) for role in ROLES[EV.parse_node_id(nid)[1]]}
            for nid in dicts}


def receipt_digest(d):
    """receipt_sha256 of a receipt dict: sha256 of its canonical bytes (rso.binding.binding.receipt_sha256)."""
    return hashlib.sha256(_bytes(d)).hexdigest()


def launch_of(dicts):
    """The launch a bundle's receipts ran under: the <launch> of their run ids <launch>/<node> (s2_bundle's
    spelling), by majority, so one edited receipt citing a foreign row does not move it (ties: the smallest);
    a run id without one counts for LAUNCH (the synthetic G0)."""
    n = collections.Counter(d["execution"]["run_id"].split("/", 1)[0] if "/" in d["execution"]["run_id"]
                            else LAUNCH for d in dicts.values())
    if not n:
        return LAUNCH
    top = max(n.values())
    return sorted(k for k, v in n.items() if v == top)[0]


def launch_row(launch, node_id="G0"):
    return {"kind": "RUN", "run_id": launch, "node_id": node_id, "launch_kind": "TOP_LEVEL", "status": "COMPLETED"}


def _inventory(dicts, launch=None):
    """The launch's TOP_LEVEL row, then one bound RECEIPT row per receipt (sorted by run id); terminal."""
    launch = launch or launch_of(dicts)
    rows = [launch_row(launch)]
    rows += [{"kind": "RUN", "run_id": d["execution"]["run_id"], "node_id": nid, "status": "COMPLETED",
              "launch_kind": "RECEIPT", "parent_run_id": launch, "receipt_sha256": receipt_digest(d)}
             for nid, d in sorted(dicts.items(), key=lambda kv: kv[1]["execution"]["run_id"])]
    return rows + [{"kind": "TERMINAL", "row_count": len(rows)}]


def _redigest(rows, dicts, launch):
    """Each RECEIPT row of `launch` whose run id the presented receipt of its node cites records that receipt's
    digest; every other row is left as it is."""
    for r in rows:
        if r.get("kind") == "RUN" and r.get("launch_kind") == "RECEIPT" and r.get("parent_run_id") == launch:
            d = dicts.get(r.get("node_id"))
            if d is not None and d["execution"]["run_id"] == r["run_id"]:
                r["receipt_sha256"] = receipt_digest(d)
    return rows


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


def make_bundle(dicts, traces=None, inventory=None, withdrawals=(), base=None, run_id=None):
    """The bundle; run_id is its run.json (default: the launch of its receipts), set as an attribute so the
    FREEZE_R2 Bundle, which reads no run.json, takes the same call."""
    if base is None:
        b = EV.Bundle({nid: _bytes(d) for nid, d in dicts.items()},
                      traces if traces is not None else _traces(dicts),
                      inventory if inventory is not None else _inventory(dicts),
                      stage_records=stage_records(), withdrawals=withdrawals, blobs=blobs(),
                      expected_table=EXPECTED_TABLE)
    else:
        b = EV.Bundle({nid: _bytes(d) for nid, d in dicts.items()},
                      traces if traces is not None else base.traces(dicts),
                      inventory if inventory is not None else base.inventory(dicts),
                      stage_records=list(base.stage_records), withdrawals=withdrawals, blobs=dict(base.blobs),
                      expected_table=base.expected_table)
    b.run_id = run_id or (launch_of(dicts) if base is None else base.launch)
    return b


def manifest_of(dicts, launch=None):
    """Manifest bytes (evidence.build_manifest) naming the launch (BX1): `launch`, else the receipts' launch."""
    doc = R.loads_canonical(EV.build_manifest(R.Receipt.from_dict(d) for d in dicts.values()))
    doc["launch_run_id"] = launch or launch_of(dicts)
    return R.canonical_bytes(doc)


def retained(dicts):
    """Consumer-retained in-memory anchors taken at registration time (not producer-supplied)."""
    return EV.Anchors(manifest_of(dicts), "keeper")


def keeper_rows(dicts, bundle, at=REGISTERED_AT, base=None):
    m = manifest_of(dicts)
    inv = EV.record_blob({"schema": EV.INVENTORY_SCHEMA, "rows": bundle.inventory})
    table = EXPECTED_TABLE if base is None else base.expected_table
    stages = stage_rows(at) if base is None else base.stage_rows(at)
    return ([row("EVIDENCE_MANIFEST", hashlib.sha256(m).hexdigest(), at, "fixtures/G0/MANIFEST.json"),
             row("RUN_INVENTORY", inv, at), row("EXPECTED_ANSWER_TABLE", table["blob_sha256"], at)]
            + stages)


# --------------------------------------------------------------------------------------------------------
# The cases. Each returns a Case; edits are applied to a fresh deep copy of the base (synthetic G0 when
# base is None). B = the base, D = its dicts, S = a fixture store with the base's stage rows.

def _ctx(base):
    b = _base(base)
    return b, b.dicts(), (None if base is None else b)


def _case(name, bundle, anchors, rows, base, **kw):
    b = _base(base)
    return Case(name, bundle, anchors, EV.FixtureStore(rows), claims(None if base is None else b),
                revision=b.revision, **kw)


def g0(base=None):
    b, d, mb = _ctx(base)
    return _case("G0", make_bundle(d, base=mb), retained(d), b.stage_rows(), base)


def g0_without_lagd(base=None):
    b, full, mb = _ctx(base)
    d = {k: v for k, v in b.dicts().items() if EV.parse_node_id(k)[0] != "LAGD"}
    return _case("G0-LAGD", make_bundle(d, base=mb), retained(full), b.stage_rows(), base)


def outcome_edit(base=None):
    """E01: LAGD's ERASE rewritten FAIL -> PASS after the run, witness nulled, node and manifest re-hashed
    by the producer; traces intact. Anchors: the producer's re-made manifest."""
    b, d, mb = _ctx(base)
    orig = copy.deepcopy(d)
    e = d["rcpt:LAGD:ERASE:STANDARD"]
    e["outcome"].update({"value": "PASS", "witness": None, "reason": "ERASE held"})
    return _case("OUTCOME_EDIT", make_bundle(d, base=mb), EV.anchors_from_producer(manifest_of(d)),
                 b.stage_rows(), base, keeper_anchors=retained(orig))


def _fabricate_reg(d, base=None):
    """Replace REG's output traces by fabricated ones and make the receipts agree (before registration)."""
    b = _base(base)
    tr = b.traces(d) if base is not None else _traces(d)
    for nid, rd in d.items():
        if EV.parse_node_id(nid)[0] == "REG":
            for out in rd["outputs"]:
                x = b.fabricate(nid, out["role"])
                out["sha256"], out["length"] = hashlib.sha256(x).hexdigest(), len(x)
                tr[nid][out["role"]] = x
    return tr


def fab_consistent(base=None):
    """E01 coupling: fabricated, internally consistent REG traces, anchored as presented."""
    b, d, mb = _ctx(base)
    tr = _fabricate_reg(d, base)
    return _case("FAB_CONSISTENT", make_bundle(d, traces=tr, base=mb), retained(d), b.stage_rows(), base)


def missing(base=None):
    """E02: REG's PRESERVE receipt removed; the inventory still lists its run COMPLETED."""
    b, d, mb = _ctx(base)
    full = copy.deepcopy(d)
    bd = make_bundle(d, base=mb)
    del bd.receipts["rcpt:REG:PRESERVE:STANDARD"]
    del bd.traces["rcpt:REG:PRESERVE:STANDARD"]
    return _case("MISSING", bd, retained(full), b.stage_rows(), base)


def malformed(base=None):
    """E02: REG's ERASE receipt with an unregistered boundary value."""
    b, d, mb = _ctx(base)
    full = copy.deepcopy(d)
    d["rcpt:REG:ERASE:STANDARD"]["cell"]["boundary"] = "EPISODE_RESET j=1"
    return _case("MALFORMED", make_bundle(d, base=mb), retained(full), b.stage_rows(), base)


def relabel(rename_ids=False, base=None):
    """E02: every REG node's physics and subject renamed REG -> REG2; old anchors. node ids are kept unless
    rename_ids (the two readings of X02; neither is chosen here)."""
    b, d, mb = _ctx(base)
    full = copy.deepcopy(d)
    out = {}
    for nid, rd in d.items():
        if EV.parse_node_id(nid)[0] == "REG":
            rd["subject"]["id"] = "REG2"
            rd["cell"]["physics"] = "REG2" + rd["cell"]["physics"][len("REG"):]
            if rename_ids:
                rd["node_id"] = nid.replace("rcpt:REG:", "rcpt:REG2:")
                rd["dependencies"] = sorted(x.replace("rcpt:REG:", "rcpt:REG2:") for x in rd["dependencies"])
        out[rd["node_id"]] = rd
    old_traces = b.traces(full) if base is not None else _traces(full)
    tr = {nid: dict(old_traces[nid.replace("rcpt:REG2:", "rcpt:REG:")]) for nid in out}
    inv = b.inventory(full)
    if rename_ids:
        for r in inv[:-1]:
            if isinstance(r.get("node_id"), str):
                r["node_id"] = r["node_id"].replace("rcpt:REG:", "rcpt:REG2:")
    _redigest(inv, out, b.launch)               # the producer's inventory records the receipts it presents
    cl = claims(None if base is None else b)
    if rename_ids:
        c2 = dict(cl["CL-RET(REG)"]["cell"])
        c2["physics"] = "REG2" + c2["physics"][len("REG"):]
        cl["CL-RET(REG2)"] = EV.make_claim("CL-RET", "REG2", observers=OBSERVERS["REG"], cell=c2)
    c = _case("RELABEL_IDS" if rename_ids else "RELABEL", make_bundle(out, traces=tr, inventory=inv, base=mb),
              retained(full), b.stage_rows(), base)
    c.claims = cl
    return c


def wrong_subject(base=None):
    """E02: the RESTART prerequisite slot of CL-RET(REG) holds PKTD's RESTART receipt."""
    b, d, mb = _ctx(base)
    bd = make_bundle(d, base=mb)
    bd.receipts["rcpt:REG:RESTART:STANDARD"] = bd.receipts["rcpt:PKTD:RESTART:STANDARD"]
    bd.traces["rcpt:REG:RESTART:STANDARD"] = bd.traces["rcpt:PKTD:RESTART:STANDARD"]
    return _case("WRONG_SUBJECT", bd, retained(d), b.stage_rows(), base)


def strip(manifest_from_stripped=False, base=None):
    """E03: CALIBRATION removed from REG's RETENTION deps; node re-hashed; manifest unchanged (or, the
    harder variant, rebuilt from the stripped node)."""
    b, d, mb = _ctx(base)
    full = copy.deepcopy(d)
    r = d["rcpt:REG:RETENTION:STANDARD"]
    r["dependencies"] = [x for x in r["dependencies"] if "CALIBRATION" not in x]
    anchors = retained(d) if manifest_from_stripped else retained(full)
    return _case("STRIP", make_bundle(d, base=mb), anchors, b.stage_rows(), base)


def _flip(b):
    x = bytearray(b)
    x[0] ^= 0x01
    return bytes(x)


def byteflip(base=None):
    """E03: one byte of REG's RETENTION PROBE_A trace changed, length kept."""
    b, d, mb = _ctx(base)
    bd = make_bundle(d, base=mb)
    nid = "rcpt:REG:RETENTION:STANDARD"
    bd.traces[nid]["trace:probe_a"] = _flip(bd.traces[nid]["trace:probe_a"])
    return _case("BYTEFLIP", bd, retained(d), b.stage_rows(), base)


def reanchor(base=None):
    """E03 coupling: BYTEFLIP plus a receipt and manifest re-made by the producer to match the flipped trace."""
    b, d, mb = _ctx(base)
    full = copy.deepcopy(d)
    nid = "rcpt:REG:RETENTION:STANDARD"
    tr = b.traces(d) if base is not None else _traces(d)
    tr[nid]["trace:probe_a"] = _flip(tr[nid]["trace:probe_a"])
    for out in d[nid]["outputs"]:
        if out["role"] == "trace:probe_a":
            out["sha256"] = hashlib.sha256(tr[nid]["trace:probe_a"]).hexdigest()
    return _case("REANCHOR", make_bundle(d, traces=tr, base=mb), EV.anchors_from_producer(manifest_of(d)),
                 b.stage_rows(), base, keeper_anchors=retained(full))


def withdrawal(wid, target):
    return {"withdrawal_id": wid, "target": target, "reason": "fixture withdrawal", "authority": "Palamedes",
            "at_utc": "2026-10-04T00:30:00Z"}


def restart_stage_node(base=None):
    if base is None:
        return EV.stage_node_id("P6", EV.predicate_version(predicate_code("RESTART")))
    code = base._dicts["rcpt:REG:RESTART:STANDARD"]["predicate"]["code"]
    return EV.stage_node_id("P6", EV.predicate_version(code))


def _withdrawn(name, w, registered=True, base=None):
    b, d, mb = _ctx(base)
    rows = b.stage_rows() + ([row("WITHDRAWAL", EV.record_blob(w))] if registered else [])
    return _case(name, make_bundle(d, withdrawals=[w], base=mb), retained(d), rows, base)


def w_restart(base=None):
    """E04: anchored withdrawal of the RESTART stage record."""
    return _withdrawn("W_RESTART", withdrawal("W-RESTART", restart_stage_node(base)), base=base)


def w_obs(base=None):
    """E04: anchored withdrawal of the OBSERVER(REG, BOOKKEEP) receipt."""
    return _withdrawn("W_OBS", withdrawal("W-OBS", "rcpt:REG:OBSERVER:BOOKKEEP:STANDARD"), base=base)


def w_unrelated(base=None):
    """E04: anchored withdrawal of the TWIN_EQ receipt (no CL claim depends on it)."""
    return _withdrawn("W_UNRELATED", withdrawal("W-TWIN", "rcpt:REG:TWIN_EQ:STANDARD"), base=base)


def w_unanchored(base=None):
    """E04: W_RESTART not registered with the keeper."""
    return _withdrawn("W_UNANCHORED", withdrawal("W-RESTART", restart_stage_node(base)), registered=False,
                      base=base)


def fab_anchors(base=None):
    """E05: fabricated data with matching fabricated anchors supplied by the producer; no keeper rows."""
    b, d, mb = _ctx(base)
    tr = _fabricate_reg(d, base)
    return _case("FAB_ANCHORS", make_bundle(d, traces=tr, base=mb), EV.anchors_from_producer(manifest_of(d)),
                 b.stage_rows(), base)


def late_reg(base=None):
    """E05: keeper rows written after the consumer's first check."""
    b, d, mb = _ctx(base)
    bd = make_bundle(d, base=mb)
    return _case("LATE_REG", bd, retained(d), keeper_rows(d, bd, at=LATE, base=mb), base)


def _keeper_case(name, d, traces=None, base=None):
    mb = base
    bd = make_bundle(d, traces=traces, base=mb)
    store = EV.FixtureStore(keeper_rows(d, bd, base=mb))
    blob_map = {"fixtures/G0/MANIFEST.json": manifest_of(d)}
    c = _case(name, bd, EV.anchors_from_keeper(store, blob_map), [], base)
    c.store = store
    return c


def keeper(base=None):
    """E05: G0 with keeper rows for manifest, inventory, stages and expected table, registered before."""
    return _keeper_case("KEEPER", _base(base).dicts(), base=base)


def fab_registered(base=None):
    """E05 stated limit: FAB_CONSISTENT data registered with the keeper."""
    d = _base(base).dicts()
    tr = _fabricate_reg(d, base)
    return _keeper_case("FAB_REGISTERED", d, traces=tr, base=base)


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


def case_for(case_id, base=None):
    """The registered case `case_id` (E01-E05) built on `base` (None: the synthetic G0)."""
    return CASES[case_id](base=base)


def describe():
    return json.dumps(sorted(CASES))
