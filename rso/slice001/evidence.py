"""Evidence graph: complete nodes, G-BIND, G-INV, invalidation, authority A1-A5, custody (C-004-T014).

Normative text: rso/slice001/contract/CONTRACT.md v1.0.0 (draft B B4.2, B5, B6, B7.1 incorporated) and
AMENDMENT_v1.0.1.md (V1 node_id, V3 edge spelling, V6 custody why list, V7 G-INV attribution, V8 fixture
stores).

What this module establishes and what it does not (B5.4, closure D10): binding checks that presented bytes and
complete nodes equal the anchors the consumer holds. It never establishes that execution happened or that an
observation is true; an internally consistent fabrication made before anchoring passes every check here.

Not here: G-RECOMP, standing, eligibility and rendering (T015, checker.py / render.py). Gate results are
returned as {execution, outcome} pairs in the B3.3 / B3.4 shapes; their authority comes from
gate_authority().

Python >= 3.8, standard library only.
"""
import hashlib

from rso.slice001 import receipt as R

MANIFEST_SCHEMA = "rso.slice001.manifest.v1"
INVENTORY_SCHEMA = "rso.slice001.inventory.v1"
RECORD_KINDS = ("EVIDENCE_MANIFEST", "RUN_INVENTORY", "STAGE_RECORD", "WITHDRAWAL", "EXPECTED_ANSWER_TABLE")
# Registered values of the fixed cell axes (draft B B3.2). revision is the frozen contract.json blob and is
# passed in by the caller (Config); physics, world, resources, measurement and exposure are free strings.
REGISTERED_AXES = {"cell_id": "W-S1", "boundary": "EPISODE_CONTENT_RESET j=1..3", "search": "NONE",
                   "development": "NONE"}
# A claim's cell is compared on every axis except measurement (which names each predicate's own code) and,
# for the world-side CALIBRATION node, physics (its subject is WORLD).
CLAIM_AXES = tuple(a for a in R.CELL_AXES if a != "measurement")
WORLD_SUBJECT = "WORLD"
CLAIM_TYPES = ("CL-CAL", "CL-RET", "CL-CUST", "TWIN")
WITHDRAWAL_AUTHORITIES = ("operator", "Palamedes", "reviewer")
NAME = dict(R.PREDICATE_NAMES)


class EvidenceError(ValueError):
    pass


def _sha(b):
    return hashlib.sha256(b).hexdigest()


# --------------------------------------------------------------------------------------------------------
# Identities

def parse_node_id(node_id):
    """(subject, predicate NAME, observer or None, world) of a receipt node id (V1)."""
    m = R._NODE_ID.match(node_id) if isinstance(node_id, str) else None
    if not m:
        raise EvidenceError("not a receipt node id: %r" % (node_id,))
    return m.group(1), m.group(2), m.group(3), m.group(4)


def predicate_version(code_refs):
    """The instrument VERSION hash: sha256 of the canonical sorted CodeRef list (B4.1)."""
    return R.sha256_hex(sorted(code_refs, key=R.canonical_bytes))


def stage_node_id(instrument, version_hash):
    return "stage:%s:%s" % (instrument, version_hash)


def node_from_receipt(rc):
    """The complete node (B6.1) of a validated producer receipt."""
    d = rc.to_dict()
    b = rc.canonical_bytes()
    return {"node_id": d["node_id"], "kind": "RECEIPT", "scope": d["cell"],
            "predicate": {"id": d["predicate"]["id"], "version": predicate_version(d["predicate"]["code"])},
            "deps": list(d["dependencies"]),
            "artifact": {"role": "receipt", "sha256": _sha(b), "length": len(b)}}


def node_hash(node):
    return R.sha256_hex(node)


def build_manifest(receipts):
    """Manifest bytes over the complete nodes of the given Receipts, sorted by node_id (B5.2)."""
    nodes = sorted((node_from_receipt(rc) for rc in receipts), key=lambda n: n["node_id"])
    ids = [n["node_id"] for n in nodes]
    if len(set(ids)) != len(ids):
        raise EvidenceError("duplicate node ids in manifest")
    return R.canonical_bytes({"schema": MANIFEST_SCHEMA, "nodes": nodes})


class Anchors(object):
    """Complete-node anchors the consumer holds, and where they came from ("keeper" or "producer")."""

    def __init__(self, manifest_bytes, source):
        if source not in ("keeper", "producer"):
            raise EvidenceError("anchor source must be keeper or producer")
        doc = R.loads_canonical(manifest_bytes)
        if not isinstance(doc, dict) or doc.get("schema") != MANIFEST_SCHEMA:
            raise EvidenceError("not a manifest")
        self.source = source
        self.manifest_bytes = manifest_bytes
        self.blob_sha256 = _sha(manifest_bytes)
        self.nodes = {n["node_id"]: n for n in doc["nodes"]}


def anchors_from_producer(manifest_bytes):
    """Anchors handed over inside the producer bundle. They bind; they never qualify custody (B5.3)."""
    return Anchors(manifest_bytes, "producer")


def anchors_from_keeper(store, blobs):
    """Anchors the consumer fetched itself: the keeper's EVIDENCE_MANIFEST row, then the blob it names.

    `blobs` maps repo_path -> bytes (in T020: `git show <commit>:<path>`). Returns Anchors or raises
    EvidenceError when the store has no manifest row or the blob does not match the row.
    """
    rows = [r for r in store.rows() if r["record_kind"] == "EVIDENCE_MANIFEST"]
    if not rows:
        raise EvidenceError("KEEPER_ROW_MISSING:EVIDENCE_MANIFEST")
    row = rows[-1]
    data = blobs.get(row["repo_path"])
    if data is None or _sha(data) != row["blob_sha256"]:
        raise EvidenceError("ROW_BLOB_MISMATCH:EVIDENCE_MANIFEST")
    return Anchors(data, "keeper")


# --------------------------------------------------------------------------------------------------------
# Policy: required edges (B6.2) and claim prerequisite node sets (B7.1)

def required_deps(node_id):
    """RECEIPT-to-RECEIPT edges B6.2 requires of a receipt node, derived from its identity (not the producer)."""
    subject, name, _obs, world = parse_node_id(node_id)
    req = set()
    if subject != WORLD_SUBJECT and name != "BOUNDS":
        req.add(R.make_node_id(subject, "BOUNDS", world))
    if name == "RETENTION":
        req.add(R.make_node_id(WORLD_SUBJECT, "CALIBRATION", world))
    if name in ("CHANNEL", "OBSERVER"):
        req.add(R.make_node_id(subject, "RESTART", world))
    return req


def edge(a, b):
    return "%s->%s" % (a, b)                                    # V3


def make_claim(claim_type, subject=None, world="STANDARD", observers=(), cell=None, bundle_id=None):
    """A registered claim (policy, B7.1). `cell` is the claim's registered cell (all axes but measurement)."""
    if claim_type not in CLAIM_TYPES:
        raise EvidenceError("BLOCKED: registered claim type (%r)" % (claim_type,))
    if claim_type == "CL-CAL":
        cid = "CL-CAL(%s)" % world
    elif claim_type == "CL-CUST":
        cid = "CL-CUST(%s)" % (bundle_id or "bundle")
    elif claim_type == "TWIN":
        cid = "TWIN(%s)" % subject
    else:
        cid = "CL-RET(%s)" % subject
    return {"claim_id": cid, "type": claim_type, "subject": subject, "world": world,
            "observers": sorted(observers), "cell": dict(cell) if cell is not None else None}


def required_nodes(claim, anchors=None):
    """The claim's required receipt node set (B7.1 prerequisites; V7). Prerequisites come from policy only."""
    t, m, w = claim["type"], claim["subject"], claim["world"]
    if t == "CL-CAL":
        return [R.make_node_id(WORLD_SUBJECT, "CALIBRATION", w)]
    if t == "TWIN":
        return [R.make_node_id(m, "TWIN_EQ", w)]
    if t == "CL-CUST":
        if anchors is None:
            raise EvidenceError("CL-CUST needs the anchored manifest")
        return sorted(anchors.nodes)
    ids = [R.make_node_id(m, n, w) for n in ("BOUNDS", "RETENTION", "ERASE", "PRESERVE", "CHANNEL", "RESTART")]
    ids.append(R.make_node_id(WORLD_SUBJECT, "CALIBRATION", "STANDARD"))
    ids.extend(R.make_node_id(m, "OBSERVER", w, observer=o) for o in claim["observers"])
    return sorted(ids)


# --------------------------------------------------------------------------------------------------------
# Bundle

class Bundle(object):
    """What a producer presents: receipt bytes per node id, trace bytes per (node id, role), the run
    inventory, and the stage/withdrawal records and blobs it cites. Nothing here is trusted."""

    def __init__(self, receipts, traces, inventory, stage_records=(), withdrawals=(), blobs=None,
                 expected_table=None):
        self.receipts = dict(receipts)              # node_id -> bytes
        self.traces = {k: dict(v) for k, v in traces.items()}   # node_id -> {role: bytes}
        self.inventory = list(inventory)            # rows (see g_inv)
        self.stage_records = list(stage_records)
        self.withdrawals = list(withdrawals)
        self.blobs = dict(blobs or {})              # repo_path -> bytes
        self.expected_table = expected_table        # {repo_path, blob_sha256, commit} or None

    def parsed(self, node_id):
        """(Receipt, None) or (None, RECEIPT_SCHEMA:<field>) or (None, None) when absent."""
        if node_id not in self.receipts:
            return None, None
        try:
            return R.Receipt.from_bytes(self.receipts[node_id]), None
        except R.ReceiptError as e:
            return None, e.code


def _ran(n, applicable=None):
    return {"status": "RAN", "missing": [], "run_id": "consumer"}


def _gate(pid, value, reason, witness, eligible):
    return {"kind": "GATE", "predicate": pid, "value": value, "reason": reason,
            "witness": witness if value == "FAIL" else None, "eligible_count": eligible,
            "applicable_count": eligible, "vacuous": eligible == 0}


def _blocked(missing):
    return {"execution": {"status": "BLOCKED", "missing": list(missing), "run_id": "consumer"},
            "outcome": None}


# --------------------------------------------------------------------------------------------------------
# G-BIND (B6.3)

class Config(object):
    """Consumer-side registered values: the frozen contract revision and the trace roles B3.1 allows."""

    def __init__(self, contract_revision):
        self.contract_revision = contract_revision


def reachable(claim, bundle, anchors):
    """Node ids reachable from the claim: its required nodes and, transitively, every dependency named by a
    presented receipt, an anchored node or B6.2. Sorted (canonical order)."""
    todo = list(required_nodes(claim, anchors))
    seen = set()
    while todo:
        n = todo.pop()
        if n in seen:
            continue
        seen.add(n)
        nxt = set()
        try:
            nxt |= required_deps(n)
        except EvidenceError:
            pass
        rc, _ = bundle.parsed(n)
        if rc is not None:
            nxt |= set(rc.to_dict()["dependencies"])
        if n in anchors.nodes:
            nxt |= set(anchors.nodes[n]["deps"])
        todo.extend(sorted(nxt - seen))
    return sorted(seen)


def _first_cycle(nodes, deps_of):
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}

    def visit(n):
        color[n] = GREY
        for d in sorted(deps_of.get(n, ())):
            if d not in color:
                continue
            if color[d] == GREY:
                return d
            if color[d] == WHITE:
                c = visit(d)
                if c:
                    return c
        color[n] = BLACK
        return None

    for n in nodes:
        if color[n] == WHITE:
            c = visit(n)
            if c:
                return c
    return None


def _check_node(slot, rc, err, claim, bundle, anchors, config):
    """The B6.3 checks for one node, in table order. Return None or (kind, reason) with kind BLOCKED|FAIL."""
    if rc is None and err is None:
        return ("BLOCKED", "EVIDENCE_MISSING:%s" % slot)
    if err is not None:
        return ("FAIL", err)
    d = rc.to_dict()
    cell = d["cell"]
    for axis, value in sorted(REGISTERED_AXES.items(), key=lambda kv: R.CELL_AXES.index(kv[0])):
        if cell[axis] != value:
            return ("FAIL", "SCOPE_MALFORMED:%s" % axis)
    if cell["revision"] != config.contract_revision:
        return ("FAIL", "SCOPE_MALFORMED:revision")
    nid = d["node_id"]
    anchor = anchors.nodes.get(nid)
    if anchor is None:
        return ("FAIL", "IDENTITY_UNKNOWN:%s" % nid)
    for axis in R.CELL_AXES:
        if anchor["scope"] is None or anchor["scope"].get(axis) != cell[axis]:
            return ("FAIL", "SCOPE_MISMATCH:%s" % axis)
    if claim.get("cell") is not None and claim["type"] != "CL-CUST":
        world_side = parse_node_id(nid)[0] == WORLD_SUBJECT
        for axis in CLAIM_AXES:
            if axis == "physics" and world_side:
                continue
            if claim["cell"].get(axis) != cell[axis]:
                return ("FAIL", "SCOPE_MISMATCH:%s" % axis)
    node = node_from_receipt(rc)
    if node["predicate"] != anchor["predicate"] or parse_node_id(slot)[1] != parse_node_id(nid)[1]:
        return ("FAIL", "IDENTITY_MISMATCH:predicate")
    if nid != slot:
        return ("FAIL", "IDENTITY_MISMATCH:node_id")
    presented, anchored = set(d["dependencies"]), set(anchor["deps"])
    bad = sorted((presented ^ anchored) | (required_deps(nid) - presented))
    if bad:
        return ("FAIL", "DEPENDENCY_MISMATCH:%s" % edge(nid, bad[0]))
    if node["artifact"] != anchor["artifact"]:
        return ("FAIL", "BYTES_MISMATCH:receipt")
    traces = bundle.traces.get(slot, {})
    for ref in sorted(d["outputs"], key=lambda a: a["role"]):
        data = traces.get(ref["role"])
        if data is None or len(data) != ref["length"] or _sha(data) != ref["sha256"]:
            return ("FAIL", "BYTES_MISMATCH:%s" % ref["role"])
    if d["code"]["dirty"]:
        return ("FAIL", "CODE_NOT_COMMITTED")
    return None


def g_bind(claim, bundle, anchors, config):
    """G-BIND over every node reachable from the claim, canonical order, first failure reported."""
    nodes = reachable(claim, bundle, anchors)
    deps_of = {}
    for n in nodes:
        rc, _ = bundle.parsed(n)
        deps_of[n] = set(rc.to_dict()["dependencies"]) if rc is not None else set(
            anchors.nodes.get(n, {}).get("deps", ()))
    for n in nodes:
        rc, err = bundle.parsed(n)
        bad = _check_node(n, rc, err, claim, bundle, anchors, config)
        if bad is not None:
            kind, reason = bad
            if kind == "BLOCKED":
                return _blocked([reason])
            return {"execution": _ran(len(nodes)), "outcome": _gate("G-BIND", "FAIL", reason, n, len(nodes))}
    c = _first_cycle(nodes, deps_of)
    if c is not None:
        return {"execution": _ran(len(nodes)),
                "outcome": _gate("G-BIND", "FAIL", "CYCLE:%s" % c, c, len(nodes))}
    return {"execution": _ran(len(nodes)),
            "outcome": _gate("G-BIND", "PASS", "every reachable node binds to the anchors held", None,
                             len(nodes))}


# --------------------------------------------------------------------------------------------------------
# G-INV (B6.4, V7). Inventory rows consumed from C-004-T019 (interface fixed here until T019 lands):
#   {"kind": "RUN", "run_id": str, "node_id": str, "status": "COMPLETED" | <any other terminal status>}
#   last row {"kind": "TERMINAL", "row_count": <number of RUN rows>}

def inventory_terminal(rows):
    if not rows or rows[-1].get("kind") != "TERMINAL":
        return False
    runs = [r for r in rows[:-1] if r.get("kind") == "RUN"]
    return rows[-1].get("row_count") == len(runs) == len(rows) - 1


def g_inv(claim, bundle, anchors):
    """G-INV over the claim's required node set (V7)."""
    rows = bundle.inventory
    if not inventory_terminal(rows):
        return _blocked(["terminal attempted-run inventory"])
    runs = rows[:-1]
    req = required_nodes(claim, anchors)
    count = {}
    for r in runs:
        count[r["run_id"]] = count.get(r["run_id"], 0) + 1
    for n in req:
        rc, _ = bundle.parsed(n)
        if rc is not None:
            run_id = rc.to_dict()["execution"]["run_id"]
            if count.get(run_id, 0) != 1:
                return {"execution": _ran(len(req)),
                        "outcome": _gate("G-INV", "FAIL", "RECEIPT_WITHOUT_RUN:%s" % n, n, len(req))}
        else:
            for r in runs:
                if r["node_id"] == n and r["status"] == "COMPLETED":
                    return {"execution": _ran(len(req)),
                            "outcome": _gate("G-INV", "FAIL", "RUN_UNREPORTED:%s" % r["run_id"], n, len(req))}
    return {"execution": _ran(len(req)),
            "outcome": _gate("G-INV", "PASS", "inventory terminal; every run reported", None, len(req))}


# --------------------------------------------------------------------------------------------------------
# Registry: which stage records and withdrawals count (registered with the keeper; V8 fixture store in S2)

class FixtureStore(object):
    """In-memory keeper store (V8): rows in the MWO-0004 D2-1 form. Logic only; never custody evidence."""

    def __init__(self, rows=()):
        self._rows = [dict(r) for r in rows]

    def rows(self):
        return [dict(r) for r in self._rows]


class UnsetStore(object):
    """contract.json custody.store is UNSET (R3): no rows can be read."""

    unset = True

    def rows(self):
        return []


def store_from_contract(custody):
    """The store the consumer reads, from contract.json `custody`. UNSET -> UnsetStore (R3)."""
    if not isinstance(custody.get("store"), str) or custody["store"].startswith("UNSET"):
        return UnsetStore()
    raise EvidenceError("STORE_UNREACHABLE: no reader for locator %r in S2" % custody["store"])


def record_blob(obj):
    return R.sha256_hex(obj)


def _registered(store, kind, blob):
    return any(r["record_kind"] == kind and r["blob_sha256"] == blob for r in store.rows())


def _validate_withdrawal(w):
    keys = ("withdrawal_id", "target", "reason", "authority", "at_utc")
    if not isinstance(w, dict) or sorted(w) != sorted(keys) or w["authority"] not in WITHDRAWAL_AUTHORITIES:
        raise EvidenceError("malformed withdrawal %r" % (w,))


class Registry(object):
    """Stage records and withdrawals split into registered (count) and unverified (listed, never act)."""

    def __init__(self, bundle, store):
        self.stages, self.withdrawals, self.unverified = [], [], []
        for s in bundle.stage_records:
            R.validate_stage_record(s)
            if _registered(store, "STAGE_RECORD", record_blob(s)):
                self.stages.append(s)
            else:
                self.unverified.append(("stage:%s:%s" % (s["instrument"], s["stage"]),
                                        stage_node_id(s["instrument"], predicate_version(s["version"]))))
        for w in bundle.withdrawals:
            _validate_withdrawal(w)
            if _registered(store, "WITHDRAWAL", record_blob(w)):
                self.withdrawals.append(w)
            else:
                self.unverified.append((w["withdrawal_id"], w["target"]))
        self.blobs = dict(bundle.blobs)


# --------------------------------------------------------------------------------------------------------
# Graph closure and invalidation (B6.5)

def upstream(node_id, bundle, anchors):
    """Every node the given node depends on, transitively: receipt dependencies (presented and anchored),
    B6.2 edges and the STAGE node of each receipt's predicate version. Includes node_id itself."""
    seen, todo = set(), [node_id]
    while todo:
        n = todo.pop()
        if n in seen:
            continue
        seen.add(n)
        if n.startswith("stage:"):
            continue
        rc, _ = bundle.parsed(n)
        nxt = set()
        if rc is not None:
            d = rc.to_dict()
            nxt |= set(d["dependencies"])
            nxt.add(stage_node_id(d["predicate"]["id"], predicate_version(d["predicate"]["code"])))
        if n in anchors.nodes:
            a = anchors.nodes[n]
            nxt |= set(a["deps"])
            nxt.add(stage_node_id(a["predicate"]["id"], a["predicate"]["version"]))
        try:
            nxt |= required_deps(n)
        except EvidenceError:
            pass
        todo.extend(sorted(nxt - seen))
    return seen


def withdrawals_applying(node_id, bundle, anchors, registry):
    up = upstream(node_id, bundle, anchors)
    return sorted(w["withdrawal_id"] for w in registry.withdrawals if w["target"] in up)


def unverified_records(claim, bundle, anchors, registry):
    """FD-B8: unregistered records whose target lies in the claim's upstream; listed, never acted on."""
    up = set()
    for n in required_nodes(claim, anchors):
        up |= upstream(n, bundle, anchors)
    return sorted("unverified record %s: not registered" % rid for rid, target in registry.unverified
                  if target in up)


# --------------------------------------------------------------------------------------------------------
# Authority of one evaluation (B4.2 A1-A5)

_PRECONDITIONS = {"RETENTION": ("CALIBRATION", "world"), "CHANNEL": ("RESTART", "subject"),
                  "OBSERVER": ("RESTART", "subject")}


def _stage_for(instrument, version_refs, registry):
    best, rec = None, None
    key = predicate_version(version_refs)
    for s in registry.stages:
        if s["instrument"] == instrument and predicate_version(s["version"]) == key:
            if best is None or R.stage_rank(s["stage"]) > R.stage_rank(best):
                best, rec = s["stage"], s
    return rec


def _a1_a2_a4(instrument, version_refs, registry):
    why = []
    rec = _stage_for(instrument, version_refs, registry)
    if rec is None:
        return None, ["NO_STAGE_RECORD"]
    ref = rec["fire_test"]["receipt"]
    data = registry.blobs.get(ref["path"])
    if data is None or _sha(data) != ref["blob_sha256"]:
        why.append("NO_FIRE_TEST")
    latest = rec["closure"] or rec["first_sight"]
    if latest is not None and latest["unresolved"] > 0:
        why.append("SUSPENDED")
    return rec, why


def authority(node_id, bundle, anchors, registry):
    """QUALIFIED at the recorded stage iff A1-A5 hold for the presented receipt; else UNQUALIFIED with every
    failing reason (A1, A2, A3, A4, A5 order). A BLOCKED or absent precondition is not PASS (B4.2 A5)."""
    rc, _ = bundle.parsed(node_id)
    if rc is None:
        return {"status": "UNQUALIFIED", "why": ["EVIDENCE_MISSING:%s" % node_id]}
    d = rc.to_dict()
    rec, why = _a1_a2_a4(d["predicate"]["id"], d["predicate"]["code"], registry)
    for wid in withdrawals_applying(node_id, bundle, anchors, registry):
        why.append("WITHDRAWN:%s" % wid)
    if rec is not None and "SUSPENDED" in why:
        why.remove("SUSPENDED")
        why.append("SUSPENDED")                                       # keep A1..A5 order
    subject, name, _obs, world = parse_node_id(node_id)
    if name in _PRECONDITIONS:
        pre, by = _PRECONDITIONS[name]
        pid = R.make_node_id(WORLD_SUBJECT, pre, world) if by == "world" else R.make_node_id(subject, pre, world)
        prc, _ = bundle.parsed(pid)
        po = prc.to_dict()["outcome"] if prc is not None else None
        if po is None or po["value"] != "PASS":
            why.append("PRECONDITION:%s" % pre)
    if why:
        return {"status": "UNQUALIFIED", "why": why}
    return {"status": "QUALIFIED", "stage": rec["stage"]}


def gate_authority(instrument, version_refs, registry, withdrawn_targets=()):
    """Authority of a consumer gate (G-BIND, G-INV, G-RECOMP) from its own stage record (B6.4)."""
    rec, why = _a1_a2_a4(instrument, version_refs, registry)
    node = stage_node_id(instrument, predicate_version(version_refs))
    for w in registry.withdrawals:
        if w["target"] == node:
            why.append("WITHDRAWN:%s" % w["withdrawal_id"])
    if why:
        return {"status": "UNQUALIFIED", "why": why}
    return {"status": "QUALIFIED", "stage": rec["stage"]}


# --------------------------------------------------------------------------------------------------------
# Custody (B5.3, V6)

def required_records(bundle, anchors):
    """(record_kind, blob_sha256) pairs a bundle's custody needs: its manifest, terminal inventory, expected
    table and every stage record it cites (B5.2). Withdrawals are needed only to revoke, not for custody."""
    req = [("EVIDENCE_MANIFEST", anchors.blob_sha256),
           ("RUN_INVENTORY", record_blob({"schema": INVENTORY_SCHEMA, "rows": bundle.inventory}))]
    if bundle.expected_table is not None:
        req.append(("EXPECTED_ANSWER_TABLE", bundle.expected_table["blob_sha256"]))
    else:
        req.append(("EXPECTED_ANSWER_TABLE", None))
    for s in bundle.stage_records:
        req.append(("STAGE_RECORD", record_blob(s)))
    return req


def custody(bundle, anchors, store, first_check_utc, keeper=None, registrar=None):
    """Custody of a bundle. QUALIFIED iff the anchors came from the keeper, every required record has a row
    whose blob matches, and every row was registered before the consumer's first check. `why` is exhaustive
    and sorted (V6). Establishes bytes since registration only (B5.4)."""
    why = set()
    if anchors.source != "keeper":
        why.add("ANCHORS_FROM_PRODUCER")
    rows = store.rows()
    used = []
    for kind, blob in required_records(bundle, anchors):
        of_kind = [r for r in rows if r["record_kind"] == kind]
        match = [r for r in of_kind if blob is not None and r["blob_sha256"] == blob]
        if not of_kind:
            why.add("KEEPER_ROW_MISSING:%s" % kind)
        elif not match:
            why.add("ROW_BLOB_MISMATCH" if kind != "STAGE_RECORD" else "KEEPER_ROW_MISSING:%s" % kind)
        else:
            r = match[0]
            used.append(r)
            if not r["registered_at_utc"] < first_check_utc:
                why.add("REGISTERED_AFTER_CHECK")
    if why:
        return {"status": "UNQUALIFIED", "why": sorted(why)}
    return {"status": "QUALIFIED", "keeper": keeper, "registrar": registrar,
            "rows": sorted(r.get("row_id", "%s:%s" % (r["record_kind"], r["blob_sha256"][:12])) for r in used),
            "registered_at_utc": max(r["registered_at_utc"] for r in used)}
