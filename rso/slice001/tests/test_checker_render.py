"""Tests for the consumer/checker and the claim renderer (C-004-T015).

Fixture traces are constructed here from the contract (draft A A2-A3 world and channel semantics, A6 runtimes
REG, PKTD, LAGD, WIPE, QCARRY, AMNESIAC, FLIP, HCOUNT; roles per amendment V2; byte layout per checker
TRACE_LAYOUT). They are software fixtures, not world traces: Cadmus's world (T010) does not exist yet, so
end-to-end recomputation on real world traces is exercised only at T020. Expected values are stated from the
contract text (A4-A6, B8.2, B9) and hand-derived witnesses, never from checker output.

The B9 bundles are draft B's E01-E05 fixtures (rso/slice001/fixtures/evidence_cases.py, T014) with the
synthetic trace bytes of recompute-set receipts replaced by these fixture traces and their outcomes by the
contract's expected outcomes (patched in place for the test; that module is T014's and is not edited).
Every custody QUALIFIED here exercises logic only and is never custody evidence (B5.3, V8). Stdlib only.
"""
import copy
import hashlib
import unittest
from unittest import mock

from rso.slice001 import checker as C
from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R
from rso.slice001 import render as RD
from rso.slice001.fixtures import evidence_cases as F

# --------------------------------------------------------------------------------------------------------
# A minimal composite runtime simulator, from draft A A2-A3 and the A6 fixture descriptions.


class Reg(object):
    """REG: a := u and d := f at CUE; PROBE_A returns (a, d); PROBE_D returns d; reset d := 0, flush."""

    def __init__(self):
        self.a, self.d, self.chan, self.n = 0, 0, [], 0

    def deliver(self, bits):
        pass

    def probe_a(self):
        return self.a, self.d

    def cue(self, u, f):
        self.a, self.d = u, f
        return []

    def probe_d(self):
        return self.d

    def reset(self):
        self.d, self.chan, self.n = 0, [], self.n + 1


class Pktd(Reg):
    """PKTD: display realised through the channel: sends (f, 0); d := first delivered bit."""

    def cue(self, u, f):
        self.a = u
        return [(f, 0)]

    def deliver(self, bits):
        self.d = bits[0]


class Lagd(Reg):
    """LAGD: d := f and sends (f, 1); on delivery d := bit; reset sets d := 0 only (channel kept)."""

    def cue(self, u, f):
        self.a, self.d = u, f
        return [(f, 1)]

    def deliver(self, bits):
        self.d = bits[0]

    def reset(self):
        self.d, self.n = 0, self.n + 1


class Wipe(Reg):
    """WIPE: reset sets a := 0 as well."""

    def reset(self):
        Reg.reset(self)
        self.a = 0


class Qcarry(Reg):
    """QCARRY: sends (u, 1), sets a := delivered bit; reset does not flush."""

    def cue(self, u, f):
        self.d = f
        return [(u, 1)]

    def deliver(self, bits):
        self.a = bits[0]

    def reset(self):
        self.d, self.n = 0, self.n + 1


class Amnesiac(Reg):
    """AMNESIAC: a is never written."""

    def cue(self, u, f):
        self.d = f
        return []


class Flip(Reg):
    """FLIP: answers 1 - a."""

    def probe_a(self):
        return 1 - self.a, self.d


class Hcount(Reg):
    """HCOUNT: hidden reset counter; answer inverted once 2 or more resets have happened."""

    def probe_a(self):
        return (self.a if self.n < 2 else 1 - self.a), self.d


def _life(cls, h, skip=None, clamp=None):
    """One life of history h. skip: the boundary whose reset is replaced by no reset. clamp (j, v): right
    after the reset at boundary j capture, set a := v, restore into a fresh instance, and return y_A at PROBE_A
    of episode j+1 (A5 P5). Otherwise return (probe_a, sends, probe_d) per episode."""
    rt = cls()
    pa, sd, pd = [], [], []
    for e in range(1, C.EPISODES + 1):
        due = [b for (ep, t, b) in rt.chan if ep == e and t == "D"]
        rt.chan = [x for x in rt.chan if not (x[0] == e and x[1] == "D")]
        if due:
            rt.deliver(due)
        y = rt.probe_a()
        if clamp is not None and e == clamp[0] + 1:
            return y[0]
        pa.append(y)
        sends = rt.cue(C.u_of(h, e), C.f_of(h, e))
        for b, k in sends:
            rt.chan.append((e, "P", b) if k == 0 else (e + k, "D", b))
        sd.append(sends)
        due = [b for (ep, t, b) in rt.chan if ep == e and t == "P"]
        rt.chan = [x for x in rt.chan if not (x[0] == e and x[1] == "P")]
        if due:
            rt.deliver(due)
        pd.append(rt.probe_d())
        if e < C.EPISODES and skip != e:
            rt.reset()
        if clamp is not None and e == clamp[0]:
            state = copy.deepcopy(rt.__dict__)          # capture
            state["a"] = clamp[1]                       # set a := v
            rt = cls()
            rt.__dict__.update(state)                   # restore into a fresh instance
    return pa, sd, pd


_CACHE = {}


def traces(cls, role):
    """Canonical trace bytes of one runtime for one role (cached)."""
    key = (cls.__name__, role)
    if key in _CACHE:
        return _CACHE[key]
    hs = range(C.HISTORIES)
    if role == "trace:clamp":
        runs = {"CLAMP": "".join(str(_life(cls, h, clamp=(j, v))) for h in hs for j in C.BOUNDARIES
                                 for v in (0, 1))}
    else:
        lives = {None: [_life(cls, h) for h in hs]}
        if role == "trace:probe_a":
            for j in C.BOUNDARIES:
                lives[j] = [_life(cls, h, skip=j) for h in hs]
            runs = {("RESET" if s is None else "SKIP%d" % s): "".join("%d%d" % y for life in ls for y in life[0])
                    for s, ls in lives.items()}
        elif role == "trace:probe_d":
            runs = {"RESET": "".join(str(y) for life in lives[None] for y in life[2])}
        else:
            runs = {"RESET": "".join("".join("%d%d" % s for s in sends) + "--" * (2 - len(sends))
                                     for life in lives[None] for sends in life[1])}
    _CACHE[key] = C.make_trace(role, runs)
    return _CACHE[key]


def parsed(cls, *roles):
    return {role: C.parse_trace(role, traces(cls, role)) for role in roles}


# --------------------------------------------------------------------------------------------------------
# Expected outcomes, from the contract text (A4, A5 eligible counts, A6) and hand-derived first witnesses.
#   LAGD ERASE: canonical order is history, then boundary (V5). Every h < 64 is its own representative at
#   j = 1..3 (bits 0-5 are inputs after episode 3); h = 64 (f_3 = 1) has representative 0 at j = 3, and the
#   packet (f_3, 1) delivered at DELIVER of episode 4 shows in the PROBE_A display of episode 4.
#   WIPE PRESERVE: the smallest history with some u_j = 1 (bits 11, 9, 7) is h = 128 (u_3), partner 0.
#   QCARRY CHANNEL: h = 0, j = 1, v = 1: the delivered u_1 = 0 overrides the clamp.

def gate(pid, value, eligible, witness=None, applicable=None):
    return {"kind": "GATE", "predicate": pid, "value": value, "reason": "expected (contract A6)",
            "witness": witness, "eligible_count": eligible, "applicable_count": applicable,
            "vacuous": applicable == 0}


def ruler(value, succ, per):
    trials = 12288
    return {"kind": "RULER", "ruler": "P2", "value": value, "statistic": C._frac(succ, trials),
            "successes": succ, "trials": trials, "per_boundary": [{"j": j, "statistic": s}
                                                                   for j, s in zip((1, 2, 3), per)],
            "reason": "expected (contract A6)"}


CAL_PASS = gate("P1", "PASS", 98304)
RET_POS = ruler("POSITIVE", 12288, ("1/1", "1/1", "1/1"))
ERASE_PASS = gate("P3", "PASS", 9600)
LAGD_ERASE = gate("P3", "FAIL", 9600, {"history": 64, "partner": 0, "j": 3, "episode": 4, "tick": "PROBE_A"})
PRESERVE_PASS = gate("P4", "PASS", 6144, applicable=6144)
CHANNEL_PASS = gate("P5", "PASS", 24576)
EXPECTED = {("WORLD", "CALIBRATION"): CAL_PASS}
for _m in ("REG", "PKTD", "LAGD"):
    EXPECTED.update({(_m, "RETENTION"): RET_POS, (_m, "ERASE"): ERASE_PASS, (_m, "PRESERVE"): PRESERVE_PASS,
                     (_m, "CHANNEL"): CHANNEL_PASS})
EXPECTED[("LAGD", "ERASE")] = LAGD_ERASE
RUNTIMES = {"REG": Reg, "PKTD": Pktd, "LAGD": Lagd}


def check(test, got, want):
    for f in ("value", "eligible_count", "applicable_count", "witness", "successes", "trials", "statistic",
              "per_boundary", "vacuous"):
        if f in want:
            test.assertEqual(got[f], want[f], f)


# --------------------------------------------------------------------------------------------------------
# B9 bundles with fixture traces: T014's builders, with recompute-set traces and outcomes patched in.

_orig_trace_bytes, _orig_outcome = F.trace_bytes, F._outcome
REAL_ROLES = dict(F.ROLES, ERASE=C.RECOMPUTE_ROLES["ERASE"])


def _trace_bytes(node_id, role, tag=""):
    subject, name, _o, _w = EV.parse_node_id(node_id)
    if name in C.RECOMPUTE_SET and role in C.RECOMPUTE_ROLES[name] and subject in RUNTIMES:
        # FABRICATED: PKTD's traces under REG's receipts; every REG outcome recomputes identically (E01).
        return traces(Pktd if tag == "FABRICATED" else RUNTIMES[subject], role)
    return _orig_trace_bytes(node_id, role, tag)


def _outcome(subject, name):
    if (subject, name) in EXPECTED:
        return copy.deepcopy(EXPECTED[(subject, name)])
    return _orig_outcome(subject, name)


def real(case_name):
    """Build B9 case `case_name` with fixture traces."""
    with mock.patch.object(F, "trace_bytes", _trace_bytes), mock.patch.object(F, "_outcome", _outcome), \
            mock.patch.dict(F.ROLES, REAL_ROLES):
        return F.CASES[case_name]() if case_name in F.CASES else getattr(F, case_name)()


GATE_VERSIONS = {g: F.gate_code(g) for g in C.GATES}


def consumer(case, anchors=None):
    return C.Consumer(case.bundle, anchors or case.anchors, case.store, case.config, GATE_VERSIONS,
                      case.first_check, keeper="operator (James) -- authority, C-004-OP2",
                      registrar="Aporia (fixture)")


_DECISIONS = {}


def decisions(case_name):
    if case_name not in _DECISIONS:
        case = real(case_name)
        _DECISIONS[case_name] = consumer(case).decide_all(case.claims)
    return _DECISIONS[case_name]


def line(dec, predicate, scope=None):
    for ln in dec["prerequisites"]:
        if ln["predicate"] == predicate and (scope is None or ln["scope"] == scope):
            return ln
    raise KeyError(predicate)


def outcome_of(dec, predicate):
    v = line(dec, predicate)["verdict"]
    if v["execution"]["status"] == "BLOCKED":
        return ("BLOCKED", v["execution"]["missing"][0])
    o = v["outcome"]
    return (o["value"], o["reason"] if o["value"] == "FAIL" else None)


def same(test, a, b, ids, bundle_custody_differs=False):
    """Byte-identical decision records. Custody is a property of the whole bundle (B5.3), printed on every
    claim; where the consumer holds the producer's anchors for the whole bundle it differs on every claim
    alike and is compared separately (FD-T015-6)."""
    for cid in ids:
        x, y = a[cid], b[cid]
        if bundle_custody_differs:
            x, y = dict(x, custody=None), dict(y, custody=None)
        test.assertEqual(C.decision_bytes(x), C.decision_bytes(y), cid)


# --------------------------------------------------------------------------------------------------------

class TestRecomputeKnownAnswers(unittest.TestCase):
    """Each recomputation reproduces the contract's stated outcome on fixture traces (A4, A6)."""

    def test_calibration_standard_and_clocked(self):
        check(self, C.recompute_calibration("STANDARD"), CAL_PASS)
        got = C.recompute_calibration("CLOCKED")                         # T02 false: max over N = 1
        check(self, got, gate("P1", "FAIL", 98304, {"j": 1, "policy": [1, 0, 1]}))
        self.assertEqual(got["reason"], "no-carry class reaches 1/1 > 1/2 at boundary 1")

    def test_reg_pktd_lagd(self):
        for m, cls in RUNTIMES.items():
            runs = parsed(cls, "trace:probe_a", "trace:probe_d", "trace:sends", "trace:clamp")
            for name in ("RETENTION", "ERASE", "PRESERVE", "CHANNEL"):
                with self.subTest(m=m, name=name):
                    check(self, C.recompute(name, "STANDARD", runs), EXPECTED[(m, name)])

    def test_wipe(self):                                                 # T05
        runs = parsed(Wipe, "trace:probe_a", "trace:probe_d", "trace:sends")
        check(self, C.recompute_preserve(runs),
              gate("P4", "FAIL", 6144, {"history": 128, "partner": 0, "j": 3}, applicable=6144))
        check(self, C.recompute_erase(runs), ERASE_PASS)
        check(self, C.recompute_retention(runs), ruler("NEGATIVE", 6144, ("1/2", "1/2", "1/2")))

    def test_qcarry(self):                                               # T01 false
        runs = parsed(Qcarry, "trace:probe_a", "trace:probe_d", "trace:sends", "trace:clamp")
        check(self, C.recompute_channel(runs), gate("P5", "FAIL", 24576, {"history": 0, "j": 1, "v": 1}))
        check(self, C.recompute_erase(runs), ERASE_PASS)
        check(self, C.recompute_retention(runs), RET_POS)

    def test_amnesiac_flip_hcount(self):                                 # T02 true, T02 ruler false, T06
        am = parsed(Amnesiac, "trace:probe_a")
        check(self, C.recompute_retention(am), ruler("NEGATIVE", 6144, ("1/2", "1/2", "1/2")))
        check(self, C.recompute_preserve(am), gate("P4", "PASS", 6144, applicable=0))   # vacuous, reported
        self.assertTrue(C.recompute_preserve(am)["vacuous"])
        check(self, C.recompute_retention(parsed(Flip, "trace:probe_a")), ruler("NOT_SHOWN", 0, ("0/1",) * 3))
        check(self, C.recompute_retention(parsed(Hcount, "trace:probe_a")),
              ruler("NOT_SHOWN", 4096, ("1/1", "0/1", "0/1")))


class TestTraceFormat(unittest.TestCase):

    def test_refusals(self):
        good = C.parse_trace("trace:clamp", traces(Reg, "trace:clamp"))["CLAMP"]
        bad = [b'{"histories":4096,"role":"trace:clamp","runs":{"CLAMP":"0"},"schema":"rso.slice001.trace.v1"}',
               R.canonical_bytes({"schema": C.TRACE_SCHEMA, "role": "trace:clamp", "histories": 4096,
                                  "runs": {"CLAMP": good, "EXTRA": good}}),
               R.canonical_bytes({"schema": C.TRACE_SCHEMA, "role": "trace:probe_d", "histories": 4096,
                                  "runs": {"CLAMP": good}}),
               R.canonical_bytes({"schema": C.TRACE_SCHEMA, "role": "trace:clamp", "histories": 4096,
                                  "runs": {"CLAMP": "2" + good[1:]}}),
               b'{"histories":4096.0}']
        for b in bad:
            with self.assertRaises(C.TraceError) as cm:
                C.parse_trace("trace:clamp", b)
            self.assertEqual(cm.exception.code, "TRACE_SCHEMA:trace:clamp")


class TestE01(unittest.TestCase):

    def test_g0(self):
        d = decisions("E01.G0")
        for cid in ("CL-RET(REG)", "CL-RET(PKTD)", "CL-RET(LAGD)"):
            self.assertEqual(outcome_of(d[cid], "G-RECOMP"), ("PASS", None), cid)
            self.assertEqual(outcome_of(d[cid], "G-BIND"), ("PASS", None), cid)
            self.assertEqual(outcome_of(d[cid], "G-INV"), ("PASS", None), cid)
        for cid in ("CL-CAL(STANDARD)", "CL-RET(REG)", "CL-RET(PKTD)"):
            self.assertEqual((d[cid]["eligibility"], d[cid]["standing"]), ("ELIGIBLE", "SATISFIED"), cid)
        lagd = d["CL-RET(LAGD)"]
        self.assertEqual((lagd["eligibility"], lagd["standing"]), ("NOT_ELIGIBLE", "UNMET"))
        self.assertEqual(lagd["not_satisfied"], ["rcpt:LAGD:ERASE:STANDARD"])
        self.assertNotIn("G-RECOMP", [ln["predicate"] for ln in d["CL-CAL(STANDARD)"]["prerequisites"]])

    def test_independent_branch_unaffected(self):
        """REG/PKTD decisions byte-identical with and without the LAGD branch present."""
        same(self, decisions("E01.G0"), decisions("g0_without_lagd"),
             ("CL-CAL(STANDARD)", "CL-RET(REG)", "CL-RET(PKTD)"))

    def test_outcome_edit(self):
        """G-RECOMP line closed at fixture level: the edited LAGD ERASE receipt recomputes FAIL from intact
        traces (OUTCOME_MISMATCH:value); LAGD stays NOT_ELIGIBLE UNMET; REG and PKTD unchanged."""
        d = decisions("E01.OUTCOME_EDIT")
        lagd = d["CL-RET(LAGD)"]
        self.assertEqual(outcome_of(lagd, "G-BIND"), ("PASS", None))     # self-consistent re-hashed manifest
        self.assertEqual(outcome_of(lagd, "G-RECOMP"), ("FAIL", "OUTCOME_MISMATCH:value"))
        self.assertEqual(outcome_of(lagd, "ERASE"), ("PASS", None))      # the edited receipt, as presented
        self.assertEqual((lagd["eligibility"], lagd["standing"]), ("NOT_ELIGIBLE", "UNMET"))
        self.assertEqual(lagd["not_satisfied"], ["gate:G-RECOMP:CL-RET(LAGD)"])
        same(self, d, decisions("E01.G0"), ("CL-CAL(STANDARD)", "CL-RET(REG)", "CL-RET(PKTD)"),
             bundle_custody_differs=True)
        self.assertEqual(len({C.decision_bytes(x["custody"]) for x in d.values()}), 1)
        self.assertIn("ANCHORS_FROM_PRODUCER", d["CL-RET(REG)"]["custody"]["why"])

    def test_fab_consistent(self):
        """Coupling with E05: fabricated, internally consistent traces pass every check (B5.4)."""
        d = decisions("E01.FAB_CONSISTENT")
        reg = d["CL-RET(REG)"]
        for g in ("G-BIND", "G-INV", "G-RECOMP"):
            self.assertEqual(outcome_of(reg, g), ("PASS", None), g)
        self.assertEqual(reg["eligibility"], "ELIGIBLE")


class TestE02E03(unittest.TestCase):

    def test_missing(self):
        d = decisions("E02.MISSING")
        reg = d["CL-RET(REG)"]
        self.assertEqual((reg["eligibility"], reg["standing"]), ("NOT_ELIGIBLE", "BLOCKED"))
        self.assertEqual(outcome_of(reg, "PRESERVE"), ("BLOCKED", "EVIDENCE_MISSING:rcpt:REG:PRESERVE:STANDARD"))
        self.assertEqual(outcome_of(reg, "G-RECOMP"), ("BLOCKED", "EVIDENCE_MISSING:rcpt:REG:PRESERVE:STANDARD"))
        same(self, d, decisions("E01.G0"), ("CL-CAL(STANDARD)", "CL-RET(PKTD)"))

    def test_malformed_relabel_wrong_subject_strip(self):
        g0 = decisions("E01.G0")
        for case, reason in (("E02.MALFORMED", "SCOPE_MALFORMED:boundary"),
                             ("E02.RELABEL", "SCOPE_MISMATCH:physics"),
                             ("E02.WRONG_SUBJECT", "SCOPE_MISMATCH:physics"),
                             ("E03.STRIP", "DEPENDENCY_MISMATCH:rcpt:REG:RETENTION:STANDARD->"
                                           "rcpt:WORLD:CALIBRATION:STANDARD")):
            with self.subTest(case=case):
                d = decisions(case)
                reg = d["CL-RET(REG)"]
                self.assertEqual(outcome_of(reg, "G-BIND"), ("FAIL", reason))
                self.assertEqual((reg["eligibility"], reg["standing"]), ("NOT_ELIGIBLE", "UNMET"))
                same(self, d, g0, ("CL-CAL(STANDARD)", "CL-RET(PKTD)"))

    def test_byteflip(self):
        """X03 (code falls): nothing is recomputed from bytes that do not bind; G-RECOMP FAIL BYTES_MISMATCH."""
        d = decisions("E03.BYTEFLIP")
        reg = d["CL-RET(REG)"]
        self.assertEqual(outcome_of(reg, "G-BIND"), ("FAIL", "BYTES_MISMATCH:trace:probe_a"))
        self.assertEqual(outcome_of(reg, "G-RECOMP"), ("FAIL", "BYTES_MISMATCH:trace:probe_a"))
        self.assertEqual((reg["eligibility"], reg["standing"]), ("NOT_ELIGIBLE", "UNMET"))
        same(self, d, decisions("E01.G0"), ("CL-CAL(STANDARD)", "CL-RET(PKTD)"))

    def test_reanchor(self):
        """X03: re-made producer anchors bind; recomputation from the flipped trace FAILs. T014's fixture flips
        byte 0 (the trace no longer parses: TRACE_SCHEMA); flipping a y_A digit changes RETENTION's value."""
        case = real("E03.REANCHOR")
        reg = consumer(case).decide(case.claims["CL-RET(REG)"])
        self.assertEqual(outcome_of(reg, "G-BIND"), ("PASS", None))
        self.assertEqual(outcome_of(reg, "G-RECOMP"), ("FAIL", "TRACE_SCHEMA:trace:probe_a"))
        self.assertIn("ANCHORS_FROM_PRODUCER", consumer(case).custody["why"])

        # digit flip: h = 0, episode 2, y_A: '0' -> '1' (one byte, length kept); receipt and anchors re-made
        case = real("E01.G0")
        nid = "rcpt:REG:RETENTION:STANDARD"
        with mock.patch.object(F, "trace_bytes", _trace_bytes), mock.patch.object(F, "_outcome", _outcome), \
                mock.patch.dict(F.ROLES, REAL_ROLES):
            d = F.g0_dicts()
            tr = {n: {role: _trace_bytes(n, role) for role in REAL_ROLES[EV.parse_node_id(n)[1]]} for n in d}
        b = bytearray(tr[nid]["trace:probe_a"])
        off = b.index(b'"RESET":"') + len(b'"RESET":"') + 2
        self.assertEqual(b[off:off + 1], b"0")
        b[off] ^= 0x01
        tr[nid]["trace:probe_a"] = bytes(b)
        for out in d[nid]["outputs"]:
            if out["role"] == "trace:probe_a":
                out["sha256"] = hashlib.sha256(bytes(b)).hexdigest()
        bundle = F.make_bundle(d, traces=tr)
        flipped = F.Case("REANCHOR_DIGIT", bundle, EV.anchors_from_producer(F.manifest_of(d)), case.store,
                         F.claims())
        reg = consumer(flipped).decide(flipped.claims["CL-RET(REG)"])
        self.assertEqual(outcome_of(reg, "G-BIND"), ("PASS", None))
        self.assertEqual(outcome_of(reg, "G-RECOMP"), ("FAIL", "OUTCOME_MISMATCH:value"))
        self.assertEqual((reg["eligibility"], reg["standing"]), ("NOT_ELIGIBLE", "UNMET"))


class TestE04(unittest.TestCase):

    def test_w_restart(self):
        d, g0 = decisions("E04.W_RESTART"), decisions("E01.G0")
        for cid in ("CL-RET(REG)", "CL-RET(PKTD)", "CL-RET(LAGD)"):              # X07: LAGD shares the record
            self.assertEqual((d[cid]["eligibility"], d[cid]["standing"]), ("NOT_ELIGIBLE", "UNQUALIFIED"), cid)
            for p in ("RESTART", "CHANNEL"):
                self.assertIn("WITHDRAWN:W-RESTART", line(d[cid], p)["verdict"]["authority"]["why"])
        same(self, d, g0, ("CL-CAL(STANDARD)",))

    def test_w_obs(self):
        d = decisions("E04.W_OBS")
        reg = d["CL-RET(REG)"]
        self.assertEqual((reg["eligibility"], reg["standing"]), ("NOT_ELIGIBLE", "UNQUALIFIED"))
        self.assertEqual(line(reg, "OBSERVER", "REG/BOOKKEEP/STANDARD")["verdict"]["authority"]["why"],
                         ["WITHDRAWN:W-OBS"])
        same(self, d, decisions("E01.G0"), ("CL-CAL(STANDARD)", "CL-RET(PKTD)", "CL-RET(LAGD)"))

    def test_w_unrelated(self):
        """No B7.1 CL claim changes; the registered TWIN(REG) claim does (X08: its node is the target)."""
        d, g0 = decisions("E04.W_UNRELATED"), decisions("E01.G0")
        same(self, d, g0, ("CL-CAL(STANDARD)", "CL-RET(REG)", "CL-RET(PKTD)", "CL-RET(LAGD)", "CL-CUST(G0)"))
        self.assertEqual(d["TWIN(REG)"]["standing"], "UNQUALIFIED")

    def test_w_unanchored(self):
        d, g0 = decisions("E04.W_UNANCHORED"), decisions("E01.G0")
        for cid in d:
            self.assertEqual((d[cid]["eligibility"], d[cid]["standing"]),
                             (g0[cid]["eligibility"], g0[cid]["standing"]), cid)
        for cid in ("CL-RET(REG)", "CL-RET(PKTD)", "CL-RET(LAGD)"):
            self.assertEqual(d[cid]["unverified"], ["unverified record W-RESTART: not registered"], cid)
        same(self, d, g0, ("CL-CAL(STANDARD)",))


class TestE05(unittest.TestCase):

    def test_custody_claims(self):
        for case, elig, standing, why in (("E05.KEEPER", "ELIGIBLE", "SATISFIED", None),
                                          ("E05.FAB_REGISTERED", "ELIGIBLE", "SATISFIED", None),
                                          ("E05.FAB_ANCHORS", "NOT_ELIGIBLE", "UNQUALIFIED", "ANCHORS_FROM_PRODUCER"),
                                          ("E05.LATE_REG", "NOT_ELIGIBLE", "UNQUALIFIED", "REGISTERED_AFTER_CHECK")):
            with self.subTest(case=case):
                cust = decisions(case)["CL-CUST(G0)"]
                self.assertEqual((cust["eligibility"], cust["standing"]), (elig, standing))
                if why:
                    self.assertIn(why, cust["custody"]["why"])

    def test_fab_registered_stated_limit(self):
        """B5.4: custody QUALIFIED says bytes since registration and nothing more; the render says so."""
        d = decisions("E05.FAB_REGISTERED")
        text = RD.render_claim(d["CL-RET(REG)"])
        self.assertIn("; execution not authenticated.", text.splitlines()[2])
        self.assertEqual(d["CL-RET(REG)"]["eligibility"], "ELIGIBLE")


# --------------------------------------------------------------------------------------------------------
# Fire tests: stubs that must fail the properties above (RED controls kept permanently).

def naive_decide_all(case):
    """RED stub: one global verdict -- any non-SATISFIED prerequisite anywhere revokes every claim."""
    real_ = consumer(case).decide_all(case.claims)
    bad = any(d["standing"] != "SATISFIED" for d in real_.values())
    out = {}
    for cid, d in real_.items():
        d = dict(d)
        if bad:
            d["eligibility"], d["standing"] = "NOT_ELIGIBLE", "UNMET"
        out[cid] = d
    return out


def naive_render(decision_or_text):
    """RED stub: prints what it is given."""
    return decision_or_text if isinstance(decision_or_text, str) else "[%s] %s" % (
        decision_or_text["eligibility"], decision_or_text["claim_id"])


class TestFireStubs(unittest.TestCase):

    def test_unrelated_failure_revokes_under_stub_only(self):
        """LAGD's ERASE FAIL (G0) and its edited receipt (OUTCOME_EDIT) are unrelated to REG and PKTD."""
        for name in ("E01.G0", "E01.OUTCOME_EDIT"):
            stub, ok = naive_decide_all(real(name)), decisions(name)
            for cid in ("CL-CAL(STANDARD)", "CL-RET(REG)", "CL-RET(PKTD)"):
                self.assertEqual(stub[cid]["eligibility"], "NOT_ELIGIBLE", (name, cid))
                self.assertEqual(ok[cid]["eligibility"], "ELIGIBLE", (name, cid))

    def test_unbounded_no_organism_passes_stub_only(self):
        text = "[ELIGIBLE] REG retains the bit better than no organism without memory."
        self.assertEqual(naive_render(text), text)
        with self.assertRaises(RD.RenderRefused) as cm:
            RD.render_statement("ELIGIBLE", "REG retains the bit better than no organism without memory",
                                F_CLASS, CELL, SETTING)
        self.assertEqual(cm.exception.codes, ["RENDER_QUANTIFIER_UNBOUND:no"])


# --------------------------------------------------------------------------------------------------------
# Render (B8)

F_CLASS = dict(C.CLASS_N)
CELL = {"cell_id": "W-S1", "revision": F.CONTRACT_REV}
SETTING = {"id": "reset_model", "sha256": F.CONTRACT_REV}


class TestRender(unittest.TestCase):

    def test_b82_accepted(self):
        text = RD.render_claim(decisions("E01.G0")["CL-RET(REG)"]).splitlines()
        sha12 = F.CONTRACT_REV[:12]
        self.assertEqual(text[0], "[ELIGIBLE] Runtime REG answers u_j at the first probe after boundary j, "
                         "j = 1..3, in 12288 of 12288 trials, carried by the declared allowed component a; "
                         "relative to class N (policies whose answer is a function of j alone; exact bound 1/2 "
                         "by enumeration of 8 policies over 12288 trials); cell W-S1 rev %s, setting "
                         "reset_model %s." % (sha12, sha12))
        self.assertEqual(text[1], "Authority: author-tested (lowest of 11 instruments)")
        self.assertTrue(text[2].startswith("Custody: UNQUALIFIED (KEEPER_ROW_MISSING:EVIDENCE_MANIFEST"))
        self.assertIn("  RETENTION on REG/STANDARD: execution RAN | authority QUALIFIED at author-tested | "
                      "outcome POSITIVE 12288/12288 (1/1)", text)
        self.assertIn("  RESTART on REG/STANDARD: execution RAN | authority QUALIFIED at author-tested | "
                      "outcome PASS (not recomputed)", text)
        self.assertIn("  OBSERVER on REG/BOOKKEEP/STANDARD: execution RAN | authority QUALIFIED at "
                      "author-tested | outcome PASS (not recomputed)", text)
        self.assertEqual(len(text), 3 + 12)                                     # 12 prerequisite lines

    def test_b82_refused(self):
        with self.assertRaises(RD.RenderRefused) as cm:
            RD.render_statement("ELIGIBLE", "REG retains information across resets better than any organism "
                                "without memory")
        self.assertEqual(cm.exception.codes, ["RENDER_QUANTIFIER_UNBOUND:any", "RENDER_RELATIVE_MISSING",
                                              "RENDER_CELL_MISSING", "RENDER_SETTING_MISSING"])
        self.assertEqual(RD.lint("REG retains information across resets better than any organism without "
                                 "memory."),
                         ["RENDER_QUANTIFIER_UNBOUND:any", "RENDER_RELATIVE_MISSING", "RENDER_CELL_MISSING",
                          "RENDER_SETTING_MISSING"])
        codes = RD.lint("REG-FLAT independently confirms REG's retention on a second physics.")
        self.assertEqual(codes[0], "RENDER_TWIN_PROMOTION")

    def test_every_rendered_claim_carries_its_stage(self):
        for case in ("E01.G0", "E01.OUTCOME_EDIT", "E02.MISSING", "E03.BYTEFLIP", "E04.W_RESTART",
                     "E04.W_UNANCHORED", "E05.KEEPER", "E05.FAB_ANCHORS"):
            for cid, d in decisions(case).items():
                with self.subTest(case=case, claim=cid):
                    text = RD.render_claim(d).splitlines()
                    self.assertTrue(text[1].startswith("Authority: "))
                    self.assertTrue(text[2].startswith("Custody: "))
                    self.assertEqual(RD.lint("\n".join(text)), [])

    def test_not_eligible_never_weaker_positive(self):
        d = decisions("E01.OUTCOME_EDIT")["CL-RET(LAGD)"]
        text = RD.render_claim(d).splitlines()
        self.assertTrue(text[0].startswith("[NOT_ELIGIBLE] Runtime LAGD answers u_j"))
        self.assertNotIn(" trials, carried", text[0])                            # no counts on the claim
        self.assertTrue(text[3].startswith("  G-RECOMP on CL-RET(LAGD): execution RAN | authority QUALIFIED at "
                                           "author-tested | outcome FAIL OUTCOME_MISMATCH:value"))
        d = decisions("E02.MISSING")["CL-RET(REG)"]
        text = RD.render_claim(d).splitlines()
        self.assertTrue(text[3].startswith("  PRESERVE on REG/STANDARD: execution BLOCKED (missing "
                                           "EVIDENCE_MISSING:rcpt:REG:PRESERVE:STANDARD)"))
        self.assertIn("Authority: UNQUALIFIED (rcpt:REG:PRESERVE:STANDARD: EVIDENCE_MISSING:", text[1])

    def test_quantifier_only_beside_exact_bound(self):
        ok = RD.render_statement("ELIGIBLE", "Runtime REG answers u_j", F_CLASS, CELL, SETTING)
        self.assertIn("class N (", ok)
        unbounded = dict(F_CLASS, bound="about half")
        with self.assertRaises(RD.RenderRefused) as cm:
            RD.render_statement("ELIGIBLE", "Runtime REG answers u_j", unbounded, CELL, SETTING)
        self.assertEqual(cm.exception.codes, ["RENDER_RELATIVE_MISSING"])
        for word in ("All", "every", "None", "never", "Always", "class"):
            with self.assertRaises(RD.RenderRefused) as cm:
                RD.render_statement("ELIGIBLE", "Runtime REG answers u_j %s time" % word, F_CLASS, CELL, SETTING)
            self.assertEqual(cm.exception.codes, ["RENDER_QUANTIFIER_UNBOUND:%s" % word.lower()])
        for missing, code in (("cell", "RENDER_CELL_MISSING"), ("setting", "RENDER_SETTING_MISSING")):
            kw = {"relative": F_CLASS, "cell": CELL, "setting": SETTING}
            kw[missing] = None
            with self.assertRaises(RD.RenderRefused) as cm:
                RD.render_statement("ELIGIBLE", "Runtime REG answers u_j", **kw)
            self.assertEqual(cm.exception.codes, [code])

    def test_prose_is_not_rendered(self):
        """Producer reason prose never reaches a rendering (FAIL lines print typed codes only)."""
        d = copy.deepcopy(decisions("E01.G0")["CL-RET(LAGD)"])
        v = line(d, "ERASE")["verdict"]
        v["outcome"]["reason"] = "the runtime always leaks; no organism could do better"
        text = RD.render_claim(d)
        self.assertNotIn("always", text)
        self.assertIn("  ERASE on LAGD/STANDARD: execution RAN | authority QUALIFIED at author-tested | outcome "
                      "FAIL", text)

    def test_twin_rule(self):
        d = copy.deepcopy(decisions("E01.G0")["TWIN(REG)"])
        d["twin"], d["encoding"] = "REG-ONEHOT", "onehot(a, d)"
        text = RD.render_claim(d).splitlines()
        self.assertTrue(text[0].startswith("[ELIGIBLE] REG-ONEHOT has the outcome vector of REG under "
                                           "onehot(a, d); one physics; relative to comparator set {REG}"))
        d["twin"] = "REG-FLAT, a second physics,"
        with self.assertRaises(RD.RenderRefused) as cm:
            RD.render_claim(d)
        self.assertEqual(cm.exception.codes, ["RENDER_TWIN_PROMOTION"])

    def test_vacuous_and_custody_lines(self):
        ln = {"predicate": "PRESERVE", "scope": "AMNESIAC/STANDARD", "recomputed": True,
              "verdict": R.make_verdict("rcpt:AMNESIAC:PRESERVE:STANDARD",
                                        {"status": "RAN", "missing": [], "run_id": "r"},
                                        {"status": "QUALIFIED", "stage": "AUTHOR_TESTED"},
                                        dict(gate("P4", "PASS", 6144, applicable=0), reason="held"), "PASS")}
        self.assertTrue(RD.verdict_line(ln).endswith("outcome PASS (vacuous: 0 applicable)"))
        k = decisions("E05.KEEPER")["CL-CUST(G0)"]
        text = RD.render_claim(k).splitlines()
        self.assertTrue(text[2].startswith("Custody: QUALIFIED -- bytes registered with operator (James) -- "
                                           "authority, C-004-OP2 at "))
        self.assertIn("  custody on CL-CUST(G0): QUALIFIED", text)


if __name__ == "__main__":
    unittest.main()
