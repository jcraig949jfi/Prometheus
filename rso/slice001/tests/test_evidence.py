"""Tests for the evidence graph, G-BIND, G-INV, invalidation, authority and custody (C-004-T014).

Cases are draft B B9 E01-E05 on the in-memory G0 (rso/slice001/fixtures/evidence_cases.py). Assertions are
on the evidence plane: G-BIND / G-INV results, per-node authority, invalidation closure, custody, and the
eligibility that follows from them through receipt.make_verdict / receipt.eligibility. G-RECOMP and the
consumer's full decision record are T015's; where a B9 row's expectation rests on G-RECOMP that is stated.
Every custody QUALIFIED here exercises logic only and is never custody evidence (B5.3, V8). Stdlib only.
"""
import hashlib
import unittest

from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R
from rso.slice001.fixtures import evidence_cases as F

REQUIRED = {"BOUNDS": "PASS", "CALIBRATION": "PASS", "RETENTION": "POSITIVE", "ERASE": "PASS",
            "PRESERVE": "PASS", "CHANNEL": "PASS", "RESTART": "PASS", "OBSERVER": "PASS", "TWIN_EQ": "PASS"}


def hash_only_bind(claim, bundle, byte_anchors):
    """The RED stub: checks that each presented receipt's bytes match a byte-only anchor. Nothing else."""
    for n in EV.required_nodes(claim):
        if n in bundle.receipts and hashlib.sha256(bundle.receipts[n]).hexdigest() != byte_anchors.get(n):
            return "FAIL"
    return "PASS"


def producer_byte_anchors(bundle):
    return {n: hashlib.sha256(b).hexdigest() for n, b in bundle.receipts.items()}


def bind(case, claim_id, anchors=None):
    return EV.g_bind(case.claims[claim_id], case.bundle, anchors or case.anchors, case.config)


def value(gate):
    if gate["execution"]["status"] == "BLOCKED":
        return ("BLOCKED", gate["execution"]["missing"][0])
    return (gate["outcome"]["value"], gate["outcome"]["reason"] if gate["outcome"]["value"] == "FAIL" else None)


def registry(case):
    return EV.Registry(case.bundle, case.store)


def decision(case, claim_id):
    """Evidence-plane decision for one claim: gates, every prerequisite verdict, eligibility, inherited
    authority, unverified records. Canonical bytes are compared for independence."""
    claim = case.claims[claim_id]
    reg = registry(case)
    gb = bind(case, claim_id)
    gi = EV.g_inv(claim, case.bundle, case.anchors)
    verdicts = []
    for n in EV.required_nodes(claim, case.anchors):
        rc, _ = case.bundle.parsed(n)
        name = EV.parse_node_id(n)[1]
        auth = EV.authority(n, case.bundle, case.anchors, reg)
        if rc is None:
            ex = {"status": "BLOCKED", "missing": ["EVIDENCE_MISSING:%s" % n], "run_id": "absent"}
            verdicts.append(R.make_verdict(n, ex, auth, None, REQUIRED[name]))
        else:
            d = rc.to_dict()
            verdicts.append(R.make_verdict(n, d["execution"], auth, d["outcome"], REQUIRED[name]))
    gates_ok = [value(gb)[0], value(gi)[0]]
    elig = R.eligibility(verdicts)
    if elig["eligibility"] == "ELIGIBLE" and gates_ok != ["PASS", "PASS"]:
        elig = {"eligibility": "NOT_ELIGIBLE", "standing": "BLOCKED" if "BLOCKED" in gates_ok else "UNMET",
                "not_satisfied": ["G-BIND/G-INV"]}
    return {"g_bind": gb, "g_inv": gi, "verdicts": verdicts, "eligibility": elig,
            "authority": R.inherited_authority(verdicts),
            "unverified": EV.unverified_records(claim, case.bundle, case.anchors, reg)}


def dbytes(case, claim_id):
    return R.canonical_bytes(decision(case, claim_id))


class TestNodesAndManifest(unittest.TestCase):
    def test_complete_node_fields(self):
        d = F.g0_dicts()["rcpt:REG:RETENTION:STANDARD"]
        n = EV.node_from_receipt(R.Receipt.from_dict(d))
        self.assertEqual(sorted(n), ["artifact", "deps", "kind", "node_id", "predicate", "scope"])
        self.assertEqual(n["deps"], ["rcpt:REG:BOUNDS:STANDARD", "rcpt:WORLD:CALIBRATION:STANDARD"])
        self.assertEqual(len(EV.node_hash(n)), 64)

    def test_required_edges_b62(self):
        self.assertEqual(EV.required_deps("rcpt:WORLD:CALIBRATION:STANDARD"), set())
        self.assertEqual(EV.required_deps("rcpt:REG:BOUNDS:STANDARD"), set())
        self.assertEqual(EV.required_deps("rcpt:REG:CHANNEL:STANDARD"),
                         {"rcpt:REG:BOUNDS:STANDARD", "rcpt:REG:RESTART:STANDARD"})
        self.assertEqual(EV.required_deps("rcpt:PKTD:OBSERVER:NULL:STANDARD"),
                         {"rcpt:PKTD:BOUNDS:STANDARD", "rcpt:PKTD:RESTART:STANDARD"})

    def test_claim_prerequisites_from_policy(self):
        c = F.claims()["CL-RET(REG)"]
        self.assertEqual(len(EV.required_nodes(c)), 9)     # 7 predicates + 2 observers (R1: CHANNEL kept)
        with self.assertRaises(EV.EvidenceError):
            EV.make_claim("CL-NEW", "REG")

    def test_manifest_canonical_and_sorted(self):
        d = F.g0_dicts()
        m = F.manifest_of(d)
        nodes = R.loads_canonical(m)["nodes"]
        self.assertEqual([n["node_id"] for n in nodes], sorted(d))


class TestFireStub(unittest.TestCase):
    """RED fire test: every E02/E03 broken fixture is admitted by a stub that checks artifact hashes only,
    and rejected by G-BIND with the contract's typed reason (or BLOCKED for MISSING)."""

    EXPECT = {
        "E02.MISSING": ("BLOCKED", "EVIDENCE_MISSING:rcpt:REG:PRESERVE:STANDARD"),
        "E02.MALFORMED": ("FAIL", "SCOPE_MALFORMED:boundary"),
        "E02.RELABEL": ("FAIL", "SCOPE_MISMATCH:physics"),
        "E02.WRONG_SUBJECT": ("FAIL", "SCOPE_MISMATCH:physics"),
        "E03.STRIP": ("FAIL", "DEPENDENCY_MISMATCH:rcpt:REG:RETENTION:STANDARD->rcpt:WORLD:CALIBRATION:STANDARD"),
        "E03.BYTEFLIP": ("FAIL", "BYTES_MISMATCH:trace:probe_a"),
    }

    def test_stub_admits_g_bind_rejects(self):
        for cid, expected in sorted(self.EXPECT.items()):
            case = F.CASES[cid]()
            claim = case.claims["CL-RET(REG)"]
            self.assertEqual(hash_only_bind(claim, case.bundle, producer_byte_anchors(case.bundle)), "PASS", cid)
            self.assertEqual(value(bind(case, "CL-RET(REG)")), expected, cid)


class TestE01(unittest.TestCase):
    def test_g0_sound(self):
        case = F.g0()
        for cid in ("CL-CAL(STANDARD)", "CL-RET(REG)", "CL-RET(PKTD)", "CL-RET(LAGD)", "TWIN(REG)",
                    "CL-CUST(G0)"):
            self.assertEqual(value(bind(case, cid)), ("PASS", None), cid)
            self.assertEqual(value(EV.g_inv(case.claims[cid], case.bundle, case.anchors)), ("PASS", None), cid)
        el = {c: decision(case, c)["eligibility"] for c in ("CL-CAL(STANDARD)", "CL-RET(REG)", "CL-RET(PKTD)",
                                                           "CL-RET(LAGD)")}
        self.assertEqual(el["CL-CAL(STANDARD)"]["eligibility"], "ELIGIBLE")
        self.assertEqual(el["CL-RET(REG)"]["eligibility"], "ELIGIBLE")
        self.assertEqual(el["CL-RET(PKTD)"]["eligibility"], "ELIGIBLE")
        self.assertEqual((el["CL-RET(LAGD)"]["eligibility"], el["CL-RET(LAGD)"]["standing"]),
                         ("NOT_ELIGIBLE", "UNMET"))                      # ERASE FAIL: a bound negative
        self.assertEqual(el["CL-RET(LAGD)"]["not_satisfied"], ["rcpt:LAGD:ERASE:STANDARD"])
        self.assertEqual(decision(case, "CL-RET(REG)")["authority"], {"status": "QUALIFIED",
                                                                      "stage": "AUTHOR_TESTED"})

    def test_g0_custody_unqualified_without_keeper_rows(self):
        case = F.g0()
        c = EV.custody(case.bundle, case.anchors, case.store, case.first_check)
        self.assertEqual(c, {"status": "UNQUALIFIED", "why": ["KEEPER_ROW_MISSING:EVIDENCE_MANIFEST",
                                                              "KEEPER_ROW_MISSING:EXPECTED_ANSWER_TABLE",
                                                              "KEEPER_ROW_MISSING:RUN_INVENTORY"]})

    def test_independent_branch_unaffected(self):
        full, part = F.g0(), F.g0_without_lagd()
        for cid in ("CL-CAL(STANDARD)", "CL-RET(REG)", "CL-RET(PKTD)"):
            self.assertEqual(dbytes(full, cid), dbytes(part, cid), cid)
        self.assertEqual(value(bind(part, "CL-RET(LAGD)"))[0], "BLOCKED")

    def test_outcome_edit(self):
        # Evidence plane: the producer's re-hashed manifest binds (G-BIND PASS); against the consumer's
        # retained anchors the edited receipt is BYTES_MISMATCH:receipt. B9 expects G-RECOMP FAIL
        # OUTCOME_MISMATCH:value -- that recomputation is T015's (checker.py), not asserted here.
        case = F.outcome_edit()
        self.assertEqual(value(bind(case, "CL-RET(LAGD)")), ("PASS", None))
        self.assertEqual(value(bind(case, "CL-RET(LAGD)", case.keeper_anchors)),
                         ("FAIL", "BYTES_MISMATCH:receipt"))
        for cid in ("CL-RET(REG)", "CL-RET(PKTD)"):
            self.assertEqual(value(bind(case, cid)), ("PASS", None), cid)
        self.assertIn("ANCHORS_FROM_PRODUCER",
                      EV.custody(case.bundle, case.anchors, case.store, case.first_check)["why"])

    def test_fab_consistent_passes_and_asserts_nothing_true(self):
        case = F.fab_consistent()
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("PASS", None))
        self.assertEqual(value(EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)), ("PASS", None))
        self.assertEqual(decision(case, "CL-RET(REG)")["eligibility"]["eligibility"], "ELIGIBLE")
        c = EV.custody(case.bundle, case.anchors, case.store, case.first_check)
        self.assertEqual(c["status"], "UNQUALIFIED")          # no keeper rows: execution not authenticated


class TestE02(unittest.TestCase):
    def test_missing(self):
        case = F.missing()
        d = decision(case, "CL-RET(REG)")
        self.assertEqual(value(d["g_bind"]), ("BLOCKED", "EVIDENCE_MISSING:rcpt:REG:PRESERVE:STANDARD"))
        # X06: V7 attributes the omitted run to CL-RET(REG): G-INV FAIL RUN_UNREPORTED as well.
        run = F.g0_dicts()["rcpt:REG:PRESERVE:STANDARD"]["execution"]["run_id"]
        self.assertEqual(value(d["g_inv"]), ("FAIL", "RUN_UNREPORTED:%s" % run))
        pres = [v for v in d["verdicts"] if v["node_id"] == "rcpt:REG:PRESERVE:STANDARD"][0]
        self.assertEqual(pres["execution"]["status"], "BLOCKED")
        self.assertEqual((d["eligibility"]["eligibility"], d["eligibility"]["standing"]),
                         ("NOT_ELIGIBLE", "BLOCKED"))
        for cid in ("CL-RET(PKTD)", "CL-CAL(STANDARD)"):
            self.assertEqual(dbytes(case, cid), dbytes(F.g0(), cid), cid)

    def test_malformed(self):
        case = F.malformed()
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("FAIL", "SCOPE_MALFORMED:boundary"))
        for cid in ("CL-RET(PKTD)", "CL-CAL(STANDARD)"):
            self.assertEqual(dbytes(case, cid), dbytes(F.g0(), cid), cid)

    def test_relabel_both_readings(self):
        # X02 is not resolved here: with node ids kept the first failure is SCOPE_MISMATCH:physics; with
        # node ids renamed it is IDENTITY_UNKNOWN. Both are FAIL against the old complete-node anchors.
        case = F.relabel()
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("FAIL", "SCOPE_MISMATCH:physics"))
        self.assertEqual(bind(case, "CL-RET(REG)")["outcome"]["witness"], "rcpt:REG:BOUNDS:STANDARD")
        case2 = F.relabel(rename_ids=True)
        self.assertEqual(value(bind(case2, "CL-RET(REG2)")),
                         ("FAIL", "IDENTITY_UNKNOWN:rcpt:REG2:BOUNDS:STANDARD"))
        self.assertEqual(value(bind(case2, "CL-RET(REG)"))[0], "BLOCKED")
        self.assertEqual(value(bind(case, "CL-CAL(STANDARD)")), ("PASS", None))

    def test_wrong_subject(self):
        case = F.wrong_subject()
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("FAIL", "SCOPE_MISMATCH:physics"))
        self.assertEqual(value(bind(case, "CL-RET(PKTD)")), ("PASS", None))

    def test_g0_true(self):
        self.assertEqual(value(bind(F.g0(), "CL-RET(REG)")), ("PASS", None))


class TestE03(unittest.TestCase):
    def test_strip_detected_even_when_manifest_built_from_stripped_node(self):
        edge = "DEPENDENCY_MISMATCH:rcpt:REG:RETENTION:STANDARD->rcpt:WORLD:CALIBRATION:STANDARD"
        self.assertEqual(value(bind(F.strip(), "CL-RET(REG)")), ("FAIL", edge))
        self.assertEqual(value(bind(F.strip(manifest_from_stripped=True), "CL-RET(REG)")), ("FAIL", edge))

    def test_byteflip(self):
        case = F.byteflip()
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("FAIL", "BYTES_MISMATCH:trace:probe_a"))
        for cid in ("CL-RET(PKTD)", "CL-CAL(STANDARD)"):
            self.assertEqual(dbytes(case, cid), dbytes(F.g0(), cid), cid)

    def test_reanchor_coupling(self):
        case = F.reanchor()
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("PASS", None))              # producer anchors
        self.assertEqual(value(bind(case, "CL-RET(REG)", case.keeper_anchors)),
                         ("FAIL", "BYTES_MISMATCH:receipt"))                              # retained anchors
        c = EV.custody(case.bundle, case.anchors, case.store, case.first_check)
        self.assertIn("ANCHORS_FROM_PRODUCER", c["why"])

    def test_g0_true(self):
        self.assertEqual(value(bind(F.g0(), "CL-RET(REG)")), ("PASS", None))


class TestE04(unittest.TestCase):
    def auth(self, case, n):
        return EV.authority(n, case.bundle, case.anchors, registry(case))

    def test_w_restart(self):
        case, base = F.w_restart(), F.g0()
        for m in F.SUBJECTS:
            nodes = ["rcpt:%s:RESTART:STANDARD" % m, "rcpt:%s:CHANNEL:STANDARD" % m] + [
                "rcpt:%s:OBSERVER:%s:STANDARD" % (m, o) for o in F.OBSERVERS[m]]
            for n in nodes:
                self.assertEqual(self.auth(case, n), {"status": "UNQUALIFIED", "why": ["WITHDRAWN:W-RESTART"]}, n)
            for n in ("rcpt:%s:ERASE:STANDARD" % m, "rcpt:%s:BOUNDS:STANDARD" % m):
                self.assertEqual(self.auth(case, n)["status"], "QUALIFIED", n)
        for cid in ("CL-RET(REG)", "CL-RET(PKTD)"):
            e = decision(case, cid)["eligibility"]
            self.assertEqual((e["eligibility"], e["standing"]), ("NOT_ELIGIBLE", "UNQUALIFIED"), cid)
        # X07: LAGD shares the withdrawn stage record; by B6.5 its RESTART loses authority too.
        self.assertEqual(decision(case, "CL-RET(LAGD)")["eligibility"]["standing"], "UNQUALIFIED")
        self.assertEqual(dbytes(case, "CL-CAL(STANDARD)"), dbytes(base, "CL-CAL(STANDARD)"))

    def test_w_obs(self):
        case, base = F.w_obs(), F.g0()
        e = decision(case, "CL-RET(REG)")["eligibility"]
        self.assertEqual((e["eligibility"], e["standing"]), ("NOT_ELIGIBLE", "UNQUALIFIED"))
        self.assertEqual(e["not_satisfied"], ["rcpt:REG:OBSERVER:BOOKKEEP:STANDARD"])
        for cid in ("CL-RET(PKTD)", "CL-CAL(STANDARD)"):
            self.assertEqual(dbytes(case, cid), dbytes(base, cid), cid)

    def test_w_unrelated(self):
        case, base = F.w_unrelated(), F.g0()
        for cid in ("CL-CAL(STANDARD)", "CL-RET(REG)", "CL-RET(PKTD)", "CL-RET(LAGD)"):
            self.assertEqual(dbytes(case, cid), dbytes(base, cid), cid)
        self.assertEqual(decision(case, "CL-RET(REG)")["eligibility"]["eligibility"], "ELIGIBLE")
        # X08/X13: TWIN(REG) depends on the withdrawn receipt itself, so its line is WITHDRAWN.
        self.assertEqual(self.auth(case, "rcpt:REG:TWIN_EQ:STANDARD"),
                         {"status": "UNQUALIFIED", "why": ["WITHDRAWN:W-TWIN"]})

    def test_w_unanchored(self):
        case, base = F.w_unanchored(), F.g0()
        for cid in ("CL-RET(REG)", "CL-RET(PKTD)", "CL-RET(LAGD)"):
            d, b = decision(case, cid), decision(base, cid)
            self.assertEqual(d["eligibility"], b["eligibility"], cid)
            self.assertEqual(d["verdicts"], b["verdicts"], cid)
            self.assertEqual(d["unverified"], ["unverified record W-RESTART: not registered"], cid)
        self.assertEqual(decision(case, "CL-CAL(STANDARD)")["unverified"], [])


class TestE05(unittest.TestCase):
    def test_fab_anchors(self):
        case = F.fab_anchors()
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("PASS", None))
        c = EV.custody(case.bundle, case.anchors, case.store, case.first_check)
        self.assertEqual(c["status"], "UNQUALIFIED")
        self.assertEqual(c["why"][0], "ANCHORS_FROM_PRODUCER")
        self.assertIn("KEEPER_ROW_MISSING:EVIDENCE_MANIFEST", c["why"])   # V6: exhaustive (G11)

    def test_late_registration(self):
        case = F.late_reg()
        c = EV.custody(case.bundle, case.anchors, case.store, case.first_check)
        self.assertEqual(c, {"status": "UNQUALIFIED", "why": ["REGISTERED_AFTER_CHECK"]})

    def test_keeper_qualified_logic_only(self):
        case = F.keeper()
        self.assertEqual(case.anchors.source, "keeper")
        c = EV.custody(case.bundle, case.anchors, case.store, case.first_check, keeper="operator",
                       registrar="Aporia")
        self.assertEqual(c["status"], "QUALIFIED")
        self.assertEqual(c["registered_at_utc"], F.REGISTERED_AT)
        self.assertEqual(value(bind(case, "CL-CUST(G0)")), ("PASS", None))
        self.assertEqual(value(EV.g_inv(case.claims["CL-CUST(G0)"], case.bundle, case.anchors)), ("PASS", None))

    def test_fab_registered_is_a_stated_limit(self):
        # B5.4: custody covers bytes since registration only; a fabrication registered first is NOT detected.
        case = F.fab_registered()
        c = EV.custody(case.bundle, case.anchors, case.store, case.first_check)
        self.assertEqual(c["status"], "QUALIFIED")
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("PASS", None))

    def test_unset_store_is_keeper_row_missing(self):
        # A fixture custody dict, not the live contract (T021): the contract's custody.store is set at v1.0.2.
        store = EV.store_from_contract({"store": "UNSET: fixture"})
        case = F.keeper()
        c = EV.custody(case.bundle, case.anchors, store, case.first_check)
        self.assertEqual(c["why"], sorted("KEEPER_ROW_MISSING:%s" % k for k in
                                          ("EVIDENCE_MANIFEST", "EXPECTED_ANSWER_TABLE", "RUN_INVENTORY",
                                           "STAGE_RECORD")))


LOCATOR = "postgresql://192.168.1.202:5432/prometheus_fire#custody.registry"


def live_form(rows, at=None):
    """Fixture rows in the form ops.custody.registry.rows() returns: integer row_id, timezone-aware ISO time
    (or a datetime), char padding, prev_hash / row_hash chain fields."""
    out, prev = [], "0" * 64
    for i, r in enumerate(rows, 1):
        x = dict(r)
        x["row_id"] = i
        x["registered_at_utc"] = at if at is not None else r["registered_at_utc"].replace("Z", "+00:00")
        x["blob_sha256"] = r["blob_sha256"] + "  "
        x["prev_hash"] = prev
        x["row_hash"] = hashlib.sha256(("%d|%s" % (i, prev)).encode()).hexdigest()
        prev = x["row_hash"]
        out.append(x)
    return out


def _vkey(v):
    return tuple(int(x) for x in v.split("."))


def assert_contract_at_least(test, doc, version):
    """Amendment-robust contract version pin (C-004-T046): the contract's version is its LATEST amendment entry,
    every entry names its AMENDMENT file, versions strictly increase, and the version is at least `version`.
    A later amendment that appends its entry and bumps the version passes; a rollback or an unlisted bump fails."""
    import os
    listed = [a["version"] for a in doc["amendments"]]
    test.assertEqual(doc["version"], listed[-1])
    test.assertEqual(listed, sorted(listed, key=_vkey))
    test.assertEqual(len(set(listed)), len(listed))
    test.assertGreaterEqual(_vkey(doc["version"]), _vkey(version))
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    for a in doc["amendments"]:
        test.assertEqual(a["path"], "rso/slice001/contract/AMENDMENT_v%s.md" % a["version"])
        test.assertTrue(os.path.isfile(os.path.join(root, *a["path"].split("/"))), a["path"])


class StubReader(object):
    """The ops.custody.registry API surface the consumer uses: rows() and verify(). No network."""

    def __init__(self, rows=(), ok=True, unreachable=False):
        self._rows, self.ok, self.unreachable, self.calls = list(rows), ok, unreachable, []

    def rows(self, kind=None):
        self.calls.append("rows")
        if self.unreachable:
            raise OSError("connection refused (stub)")
        return [dict(r) for r in self._rows]

    def verify(self):
        self.calls.append("verify")
        if self.unreachable:
            raise OSError("connection refused (stub)")
        head = self._rows[-1]["row_hash"] if self._rows else "0" * 64
        return self.ok, ([] if self.ok else ["row 1: row_hash does not match its fields"]), head, len(self._rows)


def keeper_store(reader):
    return EV.store_from_contract({"store": LOCATOR}, reader=reader)


class TestCustodyStoreReader(unittest.TestCase):
    """T021: the read-only reader for the live custody registry (AMENDMENT_v1.0.2 W1), exercised on stubs.
    Every QUALIFIED here is logic only, never custody evidence (B5.3)."""

    def test_set_locator_with_registered_rows_qualifies(self):
        case = F.keeper()
        reader = StubReader(live_form(case.store.rows()))
        store = keeper_store(reader)
        c = EV.custody(case.bundle, case.anchors, store, case.first_check, keeper="operator", registrar="Aporia")
        self.assertEqual(c["status"], "QUALIFIED", c)
        self.assertTrue(all(isinstance(r, int) for r in c["rows"]), c["rows"])
        self.assertIn("verify", reader.calls)

    def test_keeper_anchors_from_live_store(self):
        case = F.keeper()
        store = keeper_store(StubReader(live_form(case.store.rows())))
        a = EV.anchors_from_keeper(store, {"fixtures/G0/MANIFEST.json": case.anchors.manifest_bytes})
        self.assertEqual((a.source, a.blob_sha256), ("keeper", case.anchors.blob_sha256))

    def test_chain_broken_is_never_a_pass(self):
        case = F.keeper()
        store = keeper_store(StubReader(live_form(case.store.rows()), ok=False))
        c = EV.custody(case.bundle, case.anchors, store, case.first_check)
        self.assertEqual(c, {"status": "UNQUALIFIED", "why": ["ROW_CHAIN_BROKEN"]})
        with self.assertRaises(EV.EvidenceError) as e:
            EV.anchors_from_keeper(store, {"fixtures/G0/MANIFEST.json": case.anchors.manifest_bytes})
        self.assertIn("ROW_CHAIN_BROKEN", str(e.exception))

    def test_unreachable_is_never_a_pass(self):
        case = F.keeper()
        store = keeper_store(StubReader(unreachable=True))
        c = EV.custody(case.bundle, case.anchors, store, case.first_check)
        self.assertEqual(c, {"status": "UNQUALIFIED", "why": ["STORE_UNREACHABLE"]})
        with self.assertRaises(EV.EvidenceError) as e:
            EV.anchors_from_keeper(store, {})
        self.assertIn("STORE_UNREACHABLE", str(e.exception))

    def test_store_failure_keeps_producer_anchor_why(self):
        case = F.fab_anchors()
        c = EV.custody(case.bundle, case.anchors, keeper_store(StubReader(unreachable=True)), case.first_check)
        self.assertEqual(c["why"], ["ANCHORS_FROM_PRODUCER", "STORE_UNREACHABLE"])

    def test_unreachable_store_registers_no_stage_record(self):
        # Registry (authority A1) must not raise and must not count a stage record it could not read.
        case = F.keeper()
        reg = EV.Registry(case.bundle, keeper_store(StubReader(unreachable=True)))
        self.assertEqual(reg.stages, [])
        self.assertTrue(reg.unverified)
        reg = EV.Registry(case.bundle, keeper_store(StubReader(live_form(case.store.rows()), ok=False)))
        self.assertEqual(reg.stages, [])

    def test_unknown_locator_is_unreachable(self):
        case = F.keeper()
        store = EV.store_from_contract({"store": "s3://elsewhere/registry"})
        c = EV.custody(case.bundle, case.anchors, store, case.first_check)
        self.assertEqual(c, {"status": "UNQUALIFIED", "why": ["STORE_UNREACHABLE"]})

    def test_registration_time_compared_as_time_not_text(self):
        # The live registrar writes microseconds and +00:00; the first check is a Z time. Text order is wrong
        # at the same second ("...00.5Z" sorts before "...00Z"); time order is what B5.3 means.
        import datetime
        case = F.keeper()
        just_after = live_form(case.store.rows(), at="2026-10-04T01:00:00.500000+00:00")
        c = EV.custody(case.bundle, case.anchors, keeper_store(StubReader(just_after)), case.first_check)
        self.assertEqual(c, {"status": "UNQUALIFIED", "why": ["REGISTERED_AFTER_CHECK"]})
        just_before = live_form(case.store.rows(), at=datetime.datetime(2026, 10, 4, 0, 59, 59, 500000,
                                                                         tzinfo=datetime.timezone.utc))
        c = EV.custody(case.bundle, case.anchors, keeper_store(StubReader(just_before)), case.first_check)
        self.assertEqual(c["status"], "QUALIFIED", c)
        self.assertEqual(c["registered_at_utc"], "2026-10-04T00:59:59.500000Z")

    def test_rows_beyond_the_verified_chain_are_not_used(self):
        # Rows appended after verify() are outside the verified prefix and do not count.
        case = F.keeper()
        rows = live_form(case.store.rows())

        class Appended(StubReader):
            def verify(self):
                ok, p, _h, _n = StubReader.verify(self)
                return ok, p, self._rows[0]["row_hash"], 1

        c = EV.custody(case.bundle, case.anchors, keeper_store(Appended(rows)), case.first_check)
        self.assertEqual(c["status"], "UNQUALIFIED")
        self.assertNotIn("ROW_CHAIN_BROKEN", c["why"])

    def test_rows_read_once_per_store(self):
        # One consumer check reads the registry once: custody and the registry agree on the same rows.
        case = F.keeper()
        reader = StubReader(live_form(case.store.rows()))
        store = keeper_store(reader)
        EV.Registry(case.bundle, store)
        EV.custody(case.bundle, case.anchors, store, case.first_check)
        self.assertEqual(reader.calls.count("rows"), 1)

    def test_contract_carries_v102_custody(self):
        import json
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "contract",
                            "contract.json")
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        assert_contract_at_least(self, doc, "1.0.2")               # every later amendment keeps the v1.0.2 custody
        self.assertEqual(doc["custody"]["store"], LOCATOR)
        self.assertIn("superuser", doc["custody"]["independence_caveat"])

    @unittest.skipUnless(__import__("os").environ.get("RSO_CUSTODY_LIVE") == "1",
                         "live custody smoke test: set RSO_CUSTODY_LIVE=1 (and EW_DB_HOST off M1)")
    def test_live_store_smoke(self):
        store = EV.store_from_contract({"store": LOCATOR})
        rows = store.rows()
        self.assertTrue(rows)
        self.assertIn("EXPECTED_ANSWER_TABLE", [r["record_kind"] for r in rows])


class TestAuthorityConditions(unittest.TestCase):
    def test_a1_no_stage_record_and_a2_no_fire_test(self):
        case = F.g0()
        reg = registry(case)
        reg.stages = [s for s in reg.stages if s["instrument"] != "P3"]
        self.assertEqual(EV.authority("rcpt:REG:ERASE:STANDARD", case.bundle, case.anchors, reg),
                         {"status": "UNQUALIFIED", "why": ["NO_STAGE_RECORD"]})
        reg = registry(case)
        reg.blobs = {}
        self.assertEqual(EV.authority("rcpt:REG:ERASE:STANDARD", case.bundle, case.anchors, reg)["why"],
                         ["NO_FIRE_TEST"])

    def test_unregistered_stage_record_promotes_nothing(self):
        case = F.g0()
        case.store = EV.FixtureStore([])
        a = EV.authority("rcpt:REG:ERASE:STANDARD", case.bundle, case.anchors, registry(case))
        self.assertEqual(a, {"status": "UNQUALIFIED", "why": ["NO_STAGE_RECORD"]})

    def test_a5_preconditions(self):
        d = F.g0_dicts()
        d["rcpt:REG:RESTART:STANDARD"]["outcome"].update({"value": "FAIL", "witness": {"h": 1},
                                                          "reason": "RESTART FAIL"})
        d["rcpt:WORLD:CALIBRATION:STANDARD"]["execution"] = {"status": "BLOCKED", "missing": ["x"],
                                                            "run_id": "run-001"}
        d["rcpt:WORLD:CALIBRATION:STANDARD"]["outcome"] = None
        case = F.Case("A5", F.make_bundle(d), F.retained(d), EV.FixtureStore(F.stage_rows()), F.claims())
        reg = registry(case)
        self.assertEqual(EV.authority("rcpt:REG:CHANNEL:STANDARD", case.bundle, case.anchors, reg)["why"],
                         ["PRECONDITION:RESTART"])
        self.assertEqual(EV.authority("rcpt:REG:OBSERVER:NULL:STANDARD", case.bundle, case.anchors, reg)["why"],
                         ["PRECONDITION:RESTART"])
        # X12 by the letter of B4.2 A5: a BLOCKED precondition is not PASS.
        self.assertEqual(EV.authority("rcpt:REG:RETENTION:STANDARD", case.bundle, case.anchors, reg)["why"],
                         ["PRECONDITION:CALIBRATION"])
        self.assertEqual(EV.authority("rcpt:REG:ERASE:STANDARD", case.bundle, case.anchors, reg)["status"],
                         "QUALIFIED")

    def test_gate_authority(self):
        case = F.g0()
        reg = registry(case)
        self.assertEqual(EV.gate_authority("G-BIND", F.gate_code("G-BIND"), reg),
                         {"status": "QUALIFIED", "stage": "AUTHOR_TESTED"})
        self.assertEqual(EV.gate_authority("G-BIND", [F.code_ref("rso/slice001/other.py")], reg)["why"],
                         ["NO_STAGE_RECORD"])


class TestBindingDetails(unittest.TestCase):
    def test_dirty_code_and_cycle_and_schema(self):
        d = F.g0_dicts()
        d["rcpt:REG:ERASE:STANDARD"]["code"]["dirty"] = True
        case = F.Case("DIRTY", F.make_bundle(d), F.retained(d), EV.FixtureStore(F.stage_rows()), F.claims())
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("FAIL", "CODE_NOT_COMMITTED"))
        case = F.g0()
        case.bundle.receipts["rcpt:REG:ERASE:STANDARD"] = b'{"schema":"x"}'
        self.assertEqual(value(bind(case, "CL-RET(REG)"))[1].split(":")[0], "RECEIPT_SCHEMA")

    def test_receipt_in_wrong_slot_same_subject(self):
        case = F.g0()
        b = case.bundle
        b.receipts["rcpt:REG:OBSERVER:BOOKKEEP:STANDARD"] = b.receipts["rcpt:REG:OBSERVER:NULL:STANDARD"]
        b.traces["rcpt:REG:OBSERVER:BOOKKEEP:STANDARD"] = b.traces["rcpt:REG:OBSERVER:NULL:STANDARD"]
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("FAIL", "IDENTITY_MISMATCH:node_id"))
        case = F.g0()
        case.bundle.receipts["rcpt:REG:PRESERVE:STANDARD"] = case.bundle.receipts["rcpt:REG:ERASE:STANDARD"]
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("FAIL", "IDENTITY_MISMATCH:predicate"))

    def test_inventory_not_terminal_blocks(self):
        case = F.g0()
        case.bundle.inventory = case.bundle.inventory[:-1]
        self.assertEqual(value(EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)),
                         ("BLOCKED", "terminal attempted-run inventory"))

    def test_receipt_without_run(self):
        case = F.g0()
        case.bundle.inventory = [r for r in case.bundle.inventory
                                 if r.get("node_id") != "rcpt:REG:ERASE:STANDARD"]
        case.bundle.inventory[-1] = {"kind": "TERMINAL", "row_count": len(case.bundle.inventory) - 1}
        self.assertEqual(value(EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)),
                         ("FAIL", "RECEIPT_WITHOUT_RUN:rcpt:REG:ERASE:STANDARD"))
        # V7: another claim's G-INV is untouched
        self.assertEqual(value(EV.g_inv(case.claims["CL-RET(PKTD)"], case.bundle, case.anchors)), ("PASS", None))


# --------------------------------------------------------------------------------------------------------
# C-004-T042: S4 repairs of the S3 findings (ops/campaigns/C-004/TRIAGE_S3.md). Each class names its row.

def _two_manifest_store(d, b, other_subject="PKTD", other_at="2026-10-04T00:30:00Z"):
    """Keeper rows for G0 plus a SECOND bundle's manifest registered later (before the first check)."""
    rows = F.keeper_rows(d, b)
    other = F.manifest_of({k: v for k, v in d.items() if EV.parse_node_id(k)[0] == other_subject})
    rows.append(F.row("EVIDENCE_MANIFEST", hashlib.sha256(other).hexdigest(), at=other_at,
                      path="fixtures/OTHER/MANIFEST.json"))
    blobs = {"fixtures/G0/MANIFEST.json": F.manifest_of(d), "fixtures/OTHER/MANIFEST.json": other}
    return EV.FixtureStore(rows), blobs, other


class TestF2KeeperManifestOfThisBundle(unittest.TestCase):
    """F2 (S3.SOUND.TWO_MANIFESTS): the keeper's LAST manifest row was taken as this bundle's anchors."""

    def setUp(self):
        self.d = F.g0_dicts()
        self.b = F.make_bundle(self.d)
        self.store, self.blobs, self.other = _two_manifest_store(self.d, self.b)

    def test_anchors_resolve_to_the_manifest_covering_the_bundle(self):
        anchors = EV.resolve_anchors(EV.anchors_from_keeper(self.store, self.blobs), self.b)
        self.assertEqual(anchors.blob_sha256, hashlib.sha256(F.manifest_of(self.d)).hexdigest())
        self.assertEqual(anchors.source, "keeper")

    def test_two_manifests_custody_and_binding_as_with_one(self):
        anchors = EV.anchors_from_keeper(self.store, self.blobs)
        c = EV.custody(self.b, anchors, self.store, F.FIRST_CHECK)
        self.assertEqual(c["status"], "QUALIFIED", c)
        claim = F.claims()["CL-RET(REG)"]
        self.assertEqual(value(EV.g_bind(claim, self.b, anchors, EV.Config(F.CONTRACT_REV))), ("PASS", None))

    def test_custody_refuses_anchors_omitting_the_bundles_nodes(self):
        # Anchors that are a registered manifest, but not one holding this bundle's nodes: never QUALIFIED.
        only_other = EV.Anchors(self.other, "keeper")
        c = EV.custody(self.b, only_other, self.store, F.FIRST_CHECK)
        self.assertEqual(c["status"], "UNQUALIFIED")
        self.assertIn("ROW_BLOB_MISMATCH", c["why"])

    def test_single_manifest_unchanged(self):
        case = F.keeper()
        self.assertEqual(EV.custody(case.bundle, case.anchors, case.store, case.first_check)["status"], "QUALIFIED")


class TestF3RunAttribution(unittest.TestCase):
    """F3 (S3.BROKEN.RUN_BORROW): a receipt citing ANOTHER node's run (its own run row absent) must fail G-INV
    (B3.3: run_id is the inventory row that launched it; V7: that row records the node_id it launched)."""

    def _borrow(self):
        case = F.g0()
        d = F.g0_dicts()
        victim, donor = "rcpt:REG:PRESERVE:STANDARD", "rcpt:REG:ERASE:STANDARD"
        old = d[victim]["execution"]["run_id"]
        d[victim]["execution"]["run_id"] = d[donor]["execution"]["run_id"]
        inv = [r for r in F._inventory(F.g0_dicts())[:-1] if r["run_id"] != old]
        inv.append({"kind": "TERMINAL", "row_count": len(inv)})
        return F.Case("RUN_BORROW", F.make_bundle(d, inventory=inv), F.retained(d), case.store, F.claims())

    def test_borrowed_run_is_receipt_without_run(self):
        case = self._borrow()
        self.assertEqual(value(EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)),
                         ("FAIL", "RECEIPT_WITHOUT_RUN:rcpt:REG:PRESERVE:STANDARD"))

    def test_other_claims_untouched(self):
        case = self._borrow()
        for cid in ("CL-RET(PKTD)", "CL-RET(LAGD)", "CL-CAL(STANDARD)"):
            self.assertEqual(value(EV.g_inv(case.claims[cid], case.bundle, case.anchors)), ("PASS", None), cid)

    def test_g0_still_passes(self):
        case = F.g0()
        self.assertEqual(value(EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)), ("PASS", None))


class TestMeasurementBinding(unittest.TestCase):
    """Probe MEASUREMENT_LIE: cell.measurement must be the predicate version of predicate.code (B3.2)."""

    def test_measurement_naming_another_version_fails_g_bind(self):
        d = F.g0_dicts()
        d["rcpt:REG:ERASE:STANDARD"]["cell"]["measurement"] = "f" * 64
        case = F.Case("MEASUREMENT_LIE", F.make_bundle(d), F.retained(d), EV.FixtureStore(F.stage_rows()),
                      F.claims())
        self.assertEqual(value(bind(case, "CL-RET(REG)")), ("FAIL", "SCOPE_MALFORMED:measurement"))

    def test_true_measurement_binds(self):
        self.assertEqual(value(bind(F.g0(), "CL-RET(REG)")), ("PASS", None))


# --------------------------------------------------------------------------------------------------------
# C-004-T046: second and final repair (operator OP6; S4 closure, challenge/S4/REPORT.md s3-s5).

S2_AT = "2026-10-03T22:00:00Z"          # the earlier production's manifest row (before F.REGISTERED_AT)


def _earlier_production():
    """The same 25 node ids produced again: an earlier window's receipts (other created_at, other bytes)."""
    d = F.g0_dicts()
    for x in d.values():
        x["created_at_utc"] = "2026-10-03T21:00:00Z"
    return d


def _reproduced():
    """S4.SOUND.REPRODUCED in fixture form: the keeper holds the earlier production's manifest (registered first)
    AND this bundle's; both manifests carry one node set; the consumer presents this bundle."""
    d1, d2 = _earlier_production(), F.g0_dicts()
    b2 = F.make_bundle(d2)
    m1, m2 = F.manifest_of(d1), F.manifest_of(d2)
    rows = [F.row("EVIDENCE_MANIFEST", hashlib.sha256(m1).hexdigest(), at=S2_AT, path="fixtures/G0_S2/MANIFEST.json")]
    rows += F.keeper_rows(d2, b2)
    store = EV.FixtureStore(rows)
    blobs = {"fixtures/G0_S2/MANIFEST.json": m1, "fixtures/G0/MANIFEST.json": m2}
    return d1, d2, b2, store, blobs


class TestC1ReproducedBundle(unittest.TestCase):
    """C1 (S4.SOUND.REPRODUCED): with two registered manifests of one node set, the earliest exact node-set match
    anchored a reproduced bundle -- G-BIND BYTES_MISMATCH:receipt while custody read QUALIFIED on the other row.
    The bundle's manifest is the one whose node artifacts match the presented receipts."""

    def setUp(self):
        self.d1, self.d2, self.b2, self.store, self.blobs = _reproduced()
        self.choice = EV.anchors_from_keeper(self.store, self.blobs)

    def test_two_candidates_with_one_node_set(self):
        self.assertIsInstance(self.choice, EV.AnchorChoice)
        self.assertEqual([set(a.nodes) for a in self.choice.candidates][0], set(self.d2))
        self.assertEqual(len({frozenset(a.nodes) for a in self.choice.candidates}), 1)

    def test_resolves_to_the_manifest_whose_artifacts_match(self):
        a = EV.resolve_anchors(self.choice, self.b2)
        self.assertEqual(a.blob_sha256, hashlib.sha256(F.manifest_of(self.d2)).hexdigest())
        # the earlier production, presented, resolves to its own manifest
        a1 = EV.resolve_anchors(self.choice, F.make_bundle(self.d1))
        self.assertEqual(a1.blob_sha256, hashlib.sha256(F.manifest_of(self.d1)).hexdigest())

    def test_reproduced_bundle_binds(self):
        cfg = EV.Config(F.CONTRACT_REV)
        for cid, claim in sorted(F.claims().items()):
            self.assertEqual(value(EV.g_bind(claim, self.b2, self.choice, cfg)), ("PASS", None), cid)

    def test_custody_qualified_on_the_matching_row(self):
        c = EV.custody(self.b2, self.choice, self.store, F.FIRST_CHECK)
        self.assertEqual(c["status"], "QUALIFIED", c)
        m2 = hashlib.sha256(F.manifest_of(self.d2)).hexdigest()
        self.assertIn("EVIDENCE_MANIFEST:%s" % m2[:12], c["rows"])
        m1 = hashlib.sha256(F.manifest_of(self.d1)).hexdigest()
        self.assertNotIn("EVIDENCE_MANIFEST:%s" % m1[:12], c["rows"])

    def test_decisions_identical_to_the_single_manifest_keeper(self):
        ref = F.keeper()
        case = F.Case("REPRODUCED", self.b2, self.choice, self.store, F.claims())
        for cid in ("CL-CAL(STANDARD)", "CL-RET(REG)", "CL-RET(PKTD)", "CL-RET(LAGD)", "TWIN(REG)"):
            self.assertEqual(dbytes(case, cid), dbytes(ref, cid), cid)

    def test_one_edited_receipt_still_anchors_to_its_own_manifest(self):
        # A presented receipt that matches no candidate does not move the choice to the other production: the
        # manifest with the most matching artifacts anchors, and G-BIND reports the edited node itself.
        d = F.g0_dicts()
        d["rcpt:REG:ERASE:STANDARD"]["outcome"]["reason"] = "edited after anchoring"
        b = F.make_bundle(d)
        a = EV.resolve_anchors(self.choice, b)
        self.assertEqual(a.blob_sha256, hashlib.sha256(F.manifest_of(self.d2)).hexdigest())
        self.assertEqual(value(EV.g_bind(F.claims()["CL-RET(REG)"], b, self.choice, EV.Config(F.CONTRACT_REV))),
                         ("FAIL", "BYTES_MISMATCH:receipt"))


def _obs_run_borrow():
    """S4.BROKEN.OBS_RUN_BORROW in fixture form: OBSERVER(REG, BOOKKEEP)'s receipt cites the run of
    OBSERVER(REG, NULL) -- same subject and predicate, another observer; its own run row is absent."""
    case = F.g0()
    d = F.g0_dicts()
    victim, donor = "rcpt:REG:OBSERVER:BOOKKEEP:STANDARD", "rcpt:REG:OBSERVER:NULL:STANDARD"
    old = d[victim]["execution"]["run_id"]
    d[victim]["execution"]["run_id"] = d[donor]["execution"]["run_id"]
    inv = [r for r in F._inventory(F.g0_dicts())[:-1] if r["run_id"] != old]
    inv.append({"kind": "TERMINAL", "row_count": len(inv)})
    return F.Case("OBS_RUN_BORROW", F.make_bundle(d, inventory=inv), F.retained(d), case.store, F.claims())


class TestC2ObserverRunBinding(unittest.TestCase):
    """C2 (S4 edit X3 survived): G-INV run evidence is bound to the receipt's SPECIFIC observer. A receipt for
    OBSERVER(M, o1) citing the run of OBSERVER(M, o2) is RECEIPT_WITHOUT_RUN, never a pass."""

    def test_observer_run_borrow_is_receipt_without_run(self):
        case = _obs_run_borrow()
        self.assertEqual(value(EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)),
                         ("FAIL", "RECEIPT_WITHOUT_RUN:rcpt:REG:OBSERVER:BOOKKEEP:STANDARD"))

    def test_the_donor_and_other_claims_untouched(self):
        case = _obs_run_borrow()
        for cid in ("CL-RET(PKTD)", "CL-RET(LAGD)", "CL-CAL(STANDARD)", "TWIN(REG)"):
            self.assertEqual(value(EV.g_inv(case.claims[cid], case.bundle, case.anchors)), ("PASS", None), cid)

    def test_cited_row_of_another_subject_same_observer_fails(self):
        # the observer segment matches but the subject does not: also not this receipt's run
        d = F.g0_dicts()
        victim, donor = "rcpt:REG:OBSERVER:NULL:STANDARD", "rcpt:PKTD:OBSERVER:NULL:STANDARD"
        old = d[victim]["execution"]["run_id"]
        d[victim]["execution"]["run_id"] = d[donor]["execution"]["run_id"]
        inv = [r for r in F._inventory(F.g0_dicts())[:-1] if r["run_id"] != old]
        inv.append({"kind": "TERMINAL", "row_count": len(inv)})
        self.assertEqual(value(EV.g_inv(F.claims()["CL-RET(REG)"], F.make_bundle(d, inventory=inv), F.retained(d))),
                         ("FAIL", "RECEIPT_WITHOUT_RUN:rcpt:REG:OBSERVER:NULL:STANDARD"))


# AMENDMENT_v1.0.5 (B3.3 governs; operator OP6 part 2). Timed inventory rows, as the T019 ledger writes them.
WINDOW = ("2026-10-03T23:00:00Z", "2026-10-03T23:00:30Z")     # the launch that produced F.g0_dicts()
EARLIER = ("2026-10-03T20:00:00Z", "2026-10-03T20:00:30Z")    # an earlier launch of the same nodes
STALE = "rcpt:REG:PRESERVE:STANDARD"


def _timed(rows, window):
    return [dict(r, start_utc=window[0], end_utc=window[1]) for r in rows]


def _cumulative(d):
    """Earlier window's rows of every node (run ids early/<node>), then this window's rows; terminal."""
    this = _timed(F._inventory(d)[:-1], WINDOW)
    early = _timed([{"kind": "RUN", "run_id": "early/%s" % nid, "node_id": nid, "status": "COMPLETED"}
                    for nid in sorted(d)], EARLIER)
    rows = early + this
    return rows + [{"kind": "TERMINAL", "row_count": len(rows)}]


def _stale_run():
    """S4.PROBE.STALE_RUN in fixture form: REG's PRESERVE receipt cites the EARLIER window's run of its own node;
    the cumulative inventory is intact (this window's row of that node is present, uncited)."""
    d = F.g0_dicts()
    inv = _cumulative(d)
    d[STALE]["execution"]["run_id"] = "early/%s" % STALE
    return F.Case("STALE_RUN", F.make_bundle(d, inventory=inv), F.retained(d), EV.FixtureStore(F.stage_rows()),
                  F.claims())


class TestB33RunAttribution(unittest.TestCase):
    """AMENDMENT_v1.0.5 Y1-Y3: a receipt's run_id must name the row that launched and produced THAT receipt; an
    earlier window's run of the same node does not satisfy it -> RECEIPT_WITHOUT_RUN:<node_id> (Y1). Earlier rows
    remain valid provenance: never RUN_UNREPORTED for being older (Y2)."""

    def test_earlier_window_run_is_receipt_without_run(self):
        case = _stale_run()
        self.assertEqual(value(EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)),
                         ("FAIL", "RECEIPT_WITHOUT_RUN:%s" % STALE))

    def test_other_claims_untouched(self):
        case = _stale_run()
        for cid in ("CL-RET(PKTD)", "CL-RET(LAGD)", "CL-CAL(STANDARD)", "TWIN(REG)"):
            self.assertEqual(value(EV.g_inv(case.claims[cid], case.bundle, case.anchors)), ("PASS", None), cid)

    def test_cumulative_inventory_with_earlier_rows_passes(self):
        # Y2: every receipt cites its own window's row; the earlier rows are provenance, not RUN_UNREPORTED.
        d = F.g0_dicts()
        b = F.make_bundle(d, inventory=_cumulative(d))
        for cid, claim in sorted(F.claims().items()):
            if cid.startswith("CL-CUST"):
                continue
            self.assertEqual(value(EV.g_inv(claim, b, F.retained(d))), ("PASS", None), cid)

    def test_receipt_created_within_its_run_passes(self):
        # A producer that stamps created_at at completion: created_at == the row's end is its own run.
        d = F.g0_dicts()
        for x in d.values():
            x["created_at_utc"] = WINDOW[1]
        b = F.make_bundle(d, inventory=_cumulative(d))
        self.assertEqual(value(EV.g_inv(F.claims()["CL-RET(REG)"], b, F.retained(d))), ("PASS", None))

    def test_bx4_no_timestamp_decides_attribution(self):
        # C-009 BX4 retires v1.0.5's end_utc >= created_at operationalisation (it admitted a LATER window's run,
        # R2.BROKEN.LATER_WINDOW_RUN). A receipt created after its own bound row ended still binds; the row's
        # launch, status, node and digest decide (TestCC1Binding), never a time.
        d = F.g0_dicts()
        d[STALE]["created_at_utc"] = "2026-10-03T23:00:31Z"          # one second after the cited row ended
        inv = F._inventory(d)
        b = F.make_bundle(d, inventory=_timed(inv[:-1], WINDOW) + [inv[-1]])
        self.assertEqual(value(EV.g_inv(F.claims()["CL-RET(REG)"], b, F.retained(d))), ("PASS", None))
        self.assertFalse(hasattr(EV, "_ended_before"))

    def test_contract_carries_v105(self):
        # AMENDMENT_v1.0.5 applied by this packet: version and amendments entry only (Y3).
        import json
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "contract",
                            "contract.json")
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        assert_contract_at_least(self, doc, "1.0.5")
        entry = [a for a in doc["amendments"] if a["version"] == "1.0.5"]
        self.assertEqual(len(entry), 1)
        self.assertIn("C-004-OP6", entry[0]["answers"])
        self.assertIn("run attribution only", entry[0]["scope"])


# --------------------------------------------------------------------------------------------------------
# C-009-T011: G-INV on rso.binding (rso/binding/CONTRACT.md BX1, BX2, BX4, BX5, BX7; closure CC1).

class TestCC1Binding(unittest.TestCase):
    """CC1: every C-004 survivor shape and the two new shapes, end to end on G-INV (fixtures/cc1_cases.py). The
    expected answers are the C-009 ones; FREEZE_R2 admitted every R2 shape, ARTIFACT_SWAP and
    LAUNCH_SUBSTITUTION (attempts/A-001/cc1_red_freeze_r2.jsonl). The slice spelling is kept as the reason and the
    BIND_* reasons are recorded beside it, in the witness."""

    def _check(self, base):
        from rso.slice001.fixtures import cc1_cases as CC
        for cid, build, claim, want in CC.CASES:
            case = build(base)
            self.assertEqual(CC.g_inv_of(case, claim), want, cid)
            # A node-level shape touches no other claim (V7); an unbound launch is the whole bundle's (BX1).
            other_want = ("FAIL", "LAUNCH_UNBOUND") if want[1] == "LAUNCH_UNBOUND" else ("PASS", None)
            for other in ("CL-RET(PKTD)", "CL-RET(LAGD)", "CL-CAL(STANDARD)"):
                self.assertEqual(value(EV.g_inv(case.claims[other], case.bundle, case.anchors)), other_want,
                                 (cid, other))

    def test_synthetic_base(self):
        self._check(None)

    def test_committed_s4_bundle_in_the_bound_form(self):
        from rso.slice001.fixtures import cc1_cases as CC
        self._check(CC.s4_base())

    def test_witness_names_node_run_and_binding(self):
        from rso.slice001.fixtures import cc1_cases as CC
        case = CC.artifact_swap()
        o = EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)["outcome"]
        run = case.bundle.parsed(CC.PRESERVE)[0].to_dict()["execution"]["run_id"]
        self.assertEqual(o["witness"], {"node_id": CC.PRESERVE, "run_id": run, "binding": ["BIND_DIGEST_MISMATCH"]})

    def test_strict_cases_leave_one_dimension_wrong(self):
        # Each BX2 check alone: killing an edit that weakens one check needs a case failing on that check only.
        from rso.slice001.fixtures import cc1_cases as CC
        singles = {cid: want[2] for cid, _b, _c, want in CC.CASES if want[2] is not None and len(want[2]) == 1}
        self.assertEqual(sorted(sum(singles.values(), [])),
                         ["BIND_DIGEST_MISMATCH", "BIND_FOREIGN_LAUNCH", "BIND_NODE_MISMATCH", "BIND_NODE_MISMATCH",
                          "BIND_STATUS:FAILED"])


class TestBX1Launch(unittest.TestCase):
    """BX1: the launch comes from the ANCHORED manifest; the inventory holds it as one TOP_LEVEL row, COMPLETED;
    a bundle whose run.json names another launch is LAUNCH_UNBOUND."""

    def _g_inv(self, case):
        from rso.slice001.fixtures import cc1_cases as CC
        return CC.g_inv_of(case, "CL-RET(REG)")

    def test_anchors_carry_the_launch(self):
        self.assertEqual(F.g0().anchors.launch_run_id, F.LAUNCH)
        self.assertEqual(EV.Anchors(EV.build_manifest([]), "keeper").launch_run_id, None)
        m = EV.build_manifest([R.Receipt.from_dict(d) for d in F.g0_dicts().values()], launch_run_id=F.LAUNCH)
        self.assertEqual(m, F.manifest_of(F.g0_dicts()))

    def test_manifest_without_launch_is_unbound(self):
        case = F.g0()
        case.anchors = EV.Anchors(EV.build_manifest(R.Receipt.from_dict(d) for d in F.g0_dicts().values()), "keeper")
        self.assertEqual(self._g_inv(case), ("FAIL", "LAUNCH_UNBOUND", ["BIND_LAUNCH_UNANCHORED"]))

    def test_launch_row_missing_or_not_completed(self):
        case = F.g0()
        runs = [r for r in case.bundle.inventory[:-1] if r.get("launch_kind") != "TOP_LEVEL"]
        case.bundle.inventory = runs + [{"kind": "TERMINAL", "row_count": len(runs)}]
        self.assertEqual(self._g_inv(case), ("FAIL", "LAUNCH_UNBOUND", ["BIND_LAUNCH_MISSING"]))
        case = F.g0()
        case.bundle.inventory[0] = dict(case.bundle.inventory[0], status="INTERRUPTED")
        self.assertEqual(self._g_inv(case), ("FAIL", "LAUNCH_UNBOUND", ["BIND_LAUNCH_NOT_COMPLETED:INTERRUPTED"]))

    def test_run_json_naming_another_launch(self):
        case = F.g0()
        case.bundle.run_id = "another-launch"
        g = EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)["outcome"]
        self.assertEqual((g["value"], g["reason"]), ("FAIL", "LAUNCH_UNBOUND"))
        self.assertEqual(g["witness"], {"anchored": F.LAUNCH, "presented": "another-launch", "binding": []})

    def test_bundle_without_run_json_reads_the_anchored_launch(self):
        # A bundle that presents no run.json claims no launch; the anchored one is read (s2_run passes none yet).
        case = F.g0()
        case.bundle.run_id = None
        self.assertEqual(self._g_inv(case), ("PASS", None, None))
        self.assertIsNone(EV.Bundle({}, {}, []).run_id)

    def test_producer_anchors_name_their_launch_too(self):
        # E05.FAB_ANCHORS: producer anchors bind (G-INV PASS); custody refuses them separately.
        case = F.fab_anchors()
        self.assertEqual(self._g_inv(case), ("PASS", None, None))


class TestBX5OwnLaunch(unittest.TestCase):
    """BX5: rows of other launches are provenance, never evidence and never errors."""

    def test_run_unreported_reads_the_anchored_launch_only(self):
        from rso.slice001.fixtures import cc1_cases as CC
        case = CC.foreign_unreported()
        self.assertEqual(value(EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)), ("PASS", None))
        run = F.g0_dicts()["rcpt:REG:PRESERVE:STANDARD"]["execution"]["run_id"]
        self.assertEqual(value(EV.g_inv(F.missing().claims["CL-RET(REG)"], F.missing().bundle, F.missing().anchors)),
                         ("FAIL", "RUN_UNREPORTED:%s" % run))

    def test_failed_own_row_of_an_absent_receipt_is_not_unreported(self):
        case = F.missing()
        run = F.g0_dicts()["rcpt:REG:PRESERVE:STANDARD"]["execution"]["run_id"]
        case.bundle.inventory = [dict(r, status="FAILED") if r.get("run_id") == run else r
                                 for r in case.bundle.inventory]
        self.assertEqual(value(EV.g_inv(case.claims["CL-RET(REG)"], case.bundle, case.anchors)), ("PASS", None))


class TestBX7InventoryCustody(unittest.TestCase):
    """BX7: custody (the qualification CL-CUST relies on with G-INV) holds only if the registered inventory is
    the inventory of the anchored manifest's launch, and the bundle's run.json does not name another."""

    def test_keeper_case_qualified(self):
        case = F.keeper()
        self.assertEqual(EV.custody(case.bundle, case.anchors, case.store, case.first_check)["status"], "QUALIFIED")

    def test_registered_inventory_of_another_launch(self):
        d = F.g0_dicts()
        bd = F.make_bundle(d)
        runs = [dict(r, run_id="other-launch") if r.get("launch_kind") == "TOP_LEVEL" else r
                for r in bd.inventory[:-1]]
        bd.inventory = runs + [bd.inventory[-1]]
        store = EV.FixtureStore(F.keeper_rows(d, bd))          # the inventory IS registered, as presented
        c = EV.custody(bd, F.retained(d), store, F.FIRST_CHECK)
        self.assertEqual(c, {"status": "UNQUALIFIED", "why": ["INVENTORY_UNBOUND:BIND_LAUNCH_MISSING"]})

    def test_run_json_naming_another_launch(self):
        case = F.keeper()
        case.bundle.run_id = "another-launch"
        c = EV.custody(case.bundle, case.anchors, case.store, case.first_check)
        self.assertEqual(c, {"status": "UNQUALIFIED", "why": ["LAUNCH_UNBOUND"]})

    def test_manifest_without_launch(self):
        case = F.keeper()
        case.anchors = EV.Anchors(EV.build_manifest(R.Receipt.from_dict(d) for d in F.g0_dicts().values()), "keeper")
        self.assertIn("INVENTORY_UNBOUND:BIND_LAUNCH_UNANCHORED",
                      EV.custody(case.bundle, case.anchors, case.store, case.first_check)["why"])


def _challenge(unresolved):
    return {"date": "2026-10-05", "challenger": {"seat": "Pallas", "model": "claude-fable-5-1"},
            "set_ref": {"path": "rso/slice001/challenge/S3/REPORT.md", "blob_sha256": "a" * 64, "commit": F.COMMIT},
            "sound_cases": {"correct": 4, "total": 5}, "broken_cases": {"correct": 3, "total": 5},
            "edits": {k: 0 for k in R.EDIT_COUNTS}, "unresolved": unresolved}


class TestE09GateWithdrawal(unittest.TestCase):
    """E09 survived S3: no test withdrew a consumer gate's OWN stage record (B4.2 A3, B6.4)."""

    def test_withdrawing_g_bind_stage_unqualifies_g_bind(self):
        case = F.g0()
        node = EV.stage_node_id("G-BIND", EV.predicate_version(F.gate_code("G-BIND")))
        w = F.withdrawal("W-GBIND", node)
        store = EV.FixtureStore(F.stage_rows() + [F.row("WITHDRAWAL", EV.record_blob(w))])
        bundle = F.make_bundle(F.g0_dicts(), withdrawals=[w])
        reg = EV.Registry(bundle, store)
        self.assertEqual(EV.gate_authority("G-BIND", F.gate_code("G-BIND"), reg),
                         {"status": "UNQUALIFIED", "why": ["WITHDRAWN:W-GBIND"]})
        self.assertEqual(EV.gate_authority("G-INV", F.gate_code("G-INV"), reg)["status"], "QUALIFIED")
        self.assertEqual(EV.gate_authority("G-BIND", F.gate_code("G-BIND"), registry(case))["status"], "QUALIFIED")


class TestE10Suspension(unittest.TestCase):
    """E10 survived S3: nothing separated unresolved = 0 from unresolved = 1 on the latest challenge (B4.2 A4)."""

    def _authority(self, unresolved):
        d = F.g0_dicts()
        recs = []
        for s in F.stage_records():
            if s["instrument"] == "P3":
                s = dict(s, stage="FIRST_SIGHT_CHALLENGED", first_sight=_challenge(unresolved))
            recs.append(R.validate_stage_record(s))
        bundle = F.make_bundle(d)
        bundle.stage_records = recs
        store = EV.FixtureStore([F.row("STAGE_RECORD", EV.record_blob(s)) for s in recs])
        return EV.authority("rcpt:REG:ERASE:STANDARD", bundle, F.retained(d), EV.Registry(bundle, store))

    def test_one_unresolved_suspends(self):
        self.assertEqual(self._authority(1), {"status": "UNQUALIFIED", "why": ["SUSPENDED"]})

    def test_zero_unresolved_qualifies_at_the_challenged_stage(self):
        self.assertEqual(self._authority(0), {"status": "QUALIFIED", "stage": "FIRST_SIGHT_CHALLENGED"})


class TestCaseCoverage(unittest.TestCase):
    def test_every_registered_e_case_has_a_fixture(self):
        import json
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "contract",
                            "contract.json")
        with open(path, encoding="utf-8") as f:
            ids = sorted(c["id"] for c in json.load(f)["cases"] if c["id"][:3] in ("E01", "E02", "E03", "E04",
                                                                                   "E05"))
        self.assertEqual(ids, sorted(F.CASES))
        for cid in ids:
            F.CASES[cid]()


if __name__ == "__main__":
    unittest.main()
