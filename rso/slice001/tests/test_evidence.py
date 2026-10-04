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
        self.assertEqual(doc["version"], "1.0.3")                 # v1.0.3 (OP-4, C-004-T025) keeps the v1.0.2 custody
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
