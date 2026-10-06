"""Consumer / checker: G-RECOMP, typed prerequisite verdicts, eligibility and the decision record (C-004-T015).

Normative text: rso/slice001/contract/CONTRACT.md v1.0.0 (draft A A2, A4, A5; draft B B1, B3.5, B4.3, B6.4,
B7) and AMENDMENT_v1.0.1.md (V2 trace roles, V3 spellings, V5 canonical order and pair partner, V7).

The consumer evaluates each registered claim on its own subgraph (B6.4): every prerequisite named by policy
(B7.1, never by the producer) becomes a three-field verdict (receipt.make_verdict), the consumer gates G-BIND,
G-INV and G-RECOMP are evaluated per claim over the nodes reachable from that claim, and eligibility is the
worst standing (B7.2). An unrelated failure therefore never touches another claim's decision record, which is
canonical JSON so independence is checked byte for byte.

G-RECOMP recomputes CALIBRATION, RETENTION, ERASE, PRESERVE and CHANNEL from the bound output traces and
compares value, counts, statistic and first witness with the receipt (B6.4). The trace FORMAT below is this
packet's reading of V2 (roles fixed by the contract; byte layout not): the producer adapter (T016) must emit
it, and until a real world (T010) exists every recomputation here runs on fixture traces built from the
contract. End-to-end recomputation on real world traces is exercised only at T020.

What this module does not establish (B5.4): a recomputation equal to the receipt shows the receipt is
consistent with the presented traces, never that the traces came from an execution. An internally consistent
fabrication made before registration passes G-RECOMP (E01 FAB_CONSISTENT).

Python >= 3.8, standard library only.
"""
from fractions import Fraction

from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R

# --------------------------------------------------------------------------------------------------------
# World W-S1 (draft A A2, A4): 6 episodes, 4096 histories, evaluated boundaries j = 1..3, horizon H = 3.

EPISODES = 6
HISTORIES = 4096
BOUNDARIES = (1, 2, 3)
HORIZON = 3
TICKS = ("DELIVER", "PROBE_A", "CUE", "PROBE_D")
RECOMPUTE_SET = ("CALIBRATION", "RETENTION", "ERASE", "PRESERVE", "CHANNEL")   # FD-B4, contract.json gates
NO_CARRY_BOUND = Fraction(1, 2)


def _u_bit(e):
    return 11 - 2 * (e - 1)          # history h, MSB first: (u_1, f_1, ..., u_6, f_6) (A5 canonical order)


def _f_bit(e):
    return 10 - 2 * (e - 1)


def u_of(h, e, variant="STANDARD"):
    """u_e of history h. CLOCKED (A4): u_j = j mod 2 at the evaluated boundaries, the enumeration otherwise."""
    if variant == "CLOCKED" and e in BOUNDARIES:
        return e % 2
    return (h >> _u_bit(e)) & 1


def f_of(h, e):
    return (h >> _f_bit(e)) & 1


def _forbidden_mask(j):
    """Bits forbidden at boundary j: every input of episodes 1..j except u_j (A5 P3)."""
    m = 0
    for e in range(1, j + 1):
        if e < j:
            m |= 1 << _u_bit(e)
        m |= 1 << _f_bit(e)
    return m


def _frac(n, d):
    f = Fraction(n, d)
    return "%d/%d" % (f.numerator, f.denominator)


# --------------------------------------------------------------------------------------------------------
# Trace format (this packet's reading of V2; FD-T015-1). One canonical JSON document per role:
#   {"schema": TRACE_SCHEMA, "role": <V2 role>, "histories": 4096, "runs": {<run key>: <string>}}
# Histories in canonical order 0..4095; each run is one fixed-width digit string:
#   trace:probe_a   12 chars per history: per episode e = 1..6, y_A then the PROBE_A display ('0'/'1').
#                   Runs RESET (every reset made) and SKIP1, SKIP2, SKIP3 (the reset at boundary j replaced by
#                   no reset, the others unchanged; A5 P4).
#   trace:probe_d    6 chars per history: y_D per episode. Run RESET.
#   trace:sends     24 chars per history: per episode two send slots, each "<bit><k>" or "--". Run RESET.
#   trace:clamp      6 chars per history: y_A at PROBE_A of episode j+1 after the P5 clamp, for j = 1..3 and
#                   v = 0, 1 in that order. Run CLAMP.

TRACE_SCHEMA = "rso.slice001.trace.v1"
TRACE_LAYOUT = {
    "trace:probe_a": (12, ("RESET", "SKIP1", "SKIP2", "SKIP3"), "01"),
    "trace:probe_d": (6, ("RESET",), "01"),
    "trace:sends": (24, ("RESET",), "0123-"),
    "trace:clamp": (6, ("CLAMP",), "01"),
}
RECOMPUTE_ROLES = {"CALIBRATION": (), "RETENTION": ("trace:probe_a",),
                   "ERASE": ("trace:probe_a", "trace:probe_d", "trace:sends"),
                   "PRESERVE": ("trace:probe_a",), "CHANNEL": ("trace:clamp",)}


class TraceError(ValueError):
    def __init__(self, role, detail=""):
        self.code = "TRACE_SCHEMA:%s" % role
        ValueError.__init__(self, self.code + (": " + detail if detail else ""))


def make_trace(role, runs):
    """Canonical bytes of one trace document (for producers and fixtures). Validates what it writes."""
    doc = {"schema": TRACE_SCHEMA, "role": role, "histories": HISTORIES, "runs": dict(runs)}
    b = R.canonical_bytes(doc)
    parse_trace(role, b)
    return b


def parse_trace(role, data):
    """The run strings of a trace document, or TraceError(TRACE_SCHEMA:<role>)."""
    if role not in TRACE_LAYOUT:
        raise TraceError(role, "no recomputation layout for this role")
    width, runs, alphabet = TRACE_LAYOUT[role]
    try:
        doc = R.loads_canonical(data)
    except R.ReceiptError as e:
        raise TraceError(role, str(e))
    if not isinstance(doc, dict) or sorted(doc) != ["histories", "role", "runs", "schema"]:
        raise TraceError(role, "closed object {schema, role, histories, runs}")
    if doc["schema"] != TRACE_SCHEMA or doc["role"] != role or doc["histories"] != HISTORIES:
        raise TraceError(role, "schema, role or history count")
    if not isinstance(doc["runs"], dict) or sorted(doc["runs"]) != sorted(runs):
        raise TraceError(role, "runs must be exactly %s" % (list(runs),))
    for k, s in doc["runs"].items():
        if not isinstance(s, str) or len(s) != width * HISTORIES or set(s) - set(alphabet):
            raise TraceError(role, "run %s: %d chars from %r required" % (k, width * HISTORIES, alphabet))
    return doc["runs"]


# --------------------------------------------------------------------------------------------------------
# Recomputation of the five predicates (draft A A5) from parsed traces. Outcomes are B3.4 shapes. Witness
# shapes (FD-T015-2): ERASE {history, partner, j, episode, tick}; PRESERVE {history, partner, j};
# CHANNEL {history, j, v}; CALIBRATION {j, policy}. First witness in canonical order: history, then boundary,
# then clamp value (V5); the pair partner is the comparison-class representative (V5).

def _gate(pid, value, reason, witness, eligible, applicable=None):
    return {"kind": "GATE", "predicate": pid, "value": value, "reason": reason,
            "witness": witness if value == "FAIL" else None, "eligible_count": eligible,
            "applicable_count": applicable, "vacuous": applicable == 0}


def recompute_calibration(variant):
    """P1 from the registered domain itself (A4): no producer bytes are read (FD-T015-3)."""
    trials = HISTORIES * len(BOUNDARIES)
    ones = {j: sum(u_of(h, j, variant) for h in range(HISTORIES)) for j in BOUNDARIES}
    best, best_policy = -1, None
    for p in range(8):                                        # policies g: j -> bit, lexicographic (g1, g2, g3)
        g = [(p >> (2 - i)) & 1 for i in range(3)]
        score = sum(ones[j] if g[j - 1] else HISTORIES - ones[j] for j in BOUNDARIES)
        if score > best:
            best, best_policy = score, g
    eligible = 8 * trials
    # A balanced u_j at every j forces every policy in N to exactly 1/2, so max over N = 1/2 covers both clauses.
    if Fraction(best, trials) != NO_CARRY_BOUND:
        g = best_policy
        j = next(j for j in BOUNDARIES
                 if Fraction(ones[j] if g[j - 1] else HISTORIES - ones[j], HISTORIES) > NO_CARRY_BOUND)
        return _gate("P1", "FAIL", "no-carry class reaches %s > 1/2 at boundary %d" % (_frac(best, trials), j),
                     {"j": j, "policy": g}, eligible)
    return _gate("P1", "PASS", "no-carry maximum equals the registered bound 1/2; u_j balanced", None, eligible)


def _y_a(pa, h, e):
    return pa[h * 12 + (e - 1) * 2]


def recompute_retention(runs, variant="STANDARD"):
    pa = runs["trace:probe_a"]["RESET"]
    per, succ = [], 0
    for j in BOUNDARIES:
        s = sum(1 for h in range(HISTORIES) if int(_y_a(pa, h, j + 1)) == u_of(h, j, variant))
        per.append({"j": j, "statistic": _frac(s, HISTORIES)})
        succ += s
    trials = HISTORIES * len(BOUNDARIES)
    if succ == trials:
        value = "POSITIVE"
    elif all(_y_a(pa, h, j + 1) == _y_a(pa, h ^ (1 << _u_bit(j)), j + 1)
             for j in BOUNDARIES for h in range(HISTORIES)):
        value = "NEGATIVE"                                    # FD-A2: the answer never depends on u_j
    else:
        value = "NOT_SHOWN"
    return {"kind": "RULER", "ruler": "P2", "value": value, "statistic": _frac(succ, trials),
            "successes": succ, "trials": trials, "per_boundary": per,
            "reason": "RETENTION %s: s = %s over %d trials" % (value, _frac(succ, trials), trials)}


def _outputs(runs, h, e):
    """Outputs of episode e in tick order (DELIVER returns nothing): PROBE_A, CUE, PROBE_D."""
    pa = runs["trace:probe_a"]["RESET"]
    return (("PROBE_A", pa[h * 12 + (e - 1) * 2:h * 12 + (e - 1) * 2 + 2]),
            ("CUE", runs["trace:sends"]["RESET"][h * 24 + (e - 1) * 4:h * 24 + (e - 1) * 4 + 4]),
            ("PROBE_D", runs["trace:probe_d"]["RESET"][h * 6 + e - 1]))


def recompute_erase(runs):
    masks = {j: _forbidden_mask(j) for j in BOUNDARIES}
    pairs, witness = 0, None
    for h in range(HISTORIES):
        for j in BOUNDARIES:
            r = h & ~masks[j]
            if r == h:
                continue
            pairs += 1
            if witness is not None:
                continue
            for e in range(j + 1, j + HORIZON + 1):
                diff = [t for (t, x), (_t, y) in zip(_outputs(runs, h, e), _outputs(runs, r, e)) if x != y]
                if diff:
                    witness = {"history": h, "partner": r, "j": j, "episode": e, "tick": diff[0]}
                    break
    if witness is not None:
        return _gate("P3", "FAIL", "forbidden influence across boundary %d, first visible at (%d, %s)"
                     % (witness["j"], witness["episode"], witness["tick"]), witness, pairs)
    return _gate("P3", "PASS", "no forbidden influence across boundaries 1-3 within the horizon", None, pairs)


def recompute_preserve(runs):
    pa = runs["trace:probe_a"]
    pairs, applicable, witness = 0, 0, None
    for h in range(HISTORIES):
        for j in BOUNDARIES:
            if not u_of(h, j):
                continue
            r = h & ~(1 << _u_bit(j))
            pairs += 1
            skip = pa["SKIP%d" % j]
            if _y_a(skip, h, j + 1) == _y_a(skip, r, j + 1):
                continue
            applicable += 1
            if witness is None and _y_a(pa["RESET"], h, j + 1) == _y_a(pa["RESET"], r, j + 1):
                witness = {"history": h, "partner": r, "j": j}
    if witness is not None:
        return _gate("P4", "FAIL", "reset at %d destroys allowed content carried without it" % witness["j"],
                     witness, pairs, applicable)
    return _gate("P4", "PASS", "every difference carried without a reset survives it", None, pairs, applicable)


def recompute_channel(runs):
    cl = runs["trace:clamp"]["CLAMP"]
    witness, n = None, 0
    for h in range(HISTORIES):
        for j in BOUNDARIES:
            for v in (0, 1):
                n += 1
                if witness is None and int(cl[h * 6 + (j - 1) * 2 + v]) != v:
                    witness = {"history": h, "j": j, "v": v}
    if witness is not None:
        return _gate("P5", "FAIL", "retained answer does not follow the declared allowed channel at %d"
                     % witness["j"], witness, n)
    return _gate("P5", "PASS", "retained answer follows the declared allowed channel", None, n)


def recompute(name, variant, runs):
    """The outcome of predicate NAME recomputed from parsed traces ({role: {run: string}})."""
    if name == "CALIBRATION":
        return recompute_calibration(variant)
    if name == "RETENTION":
        return recompute_retention(runs, variant)
    if name == "ERASE":
        return recompute_erase(runs)
    if name == "PRESERVE":
        return recompute_preserve(runs)
    if name == "CHANNEL":
        return recompute_channel(runs)
    raise ValueError("not in the recompute set: %r" % (name,))


# Compared fields, in the order the first mismatch is reported (B6.4: value, counts, statistic, first witness;
# V3 field spellings). applicable_count is compared only where P4 defines it (FD-T015-4).
GATE_FIELDS = ("value", "eligible_count", "witness")
PRESERVE_FIELDS = ("value", "eligible_count", "applicable_count", "witness")
RULER_FIELDS = ("value", "successes", "trials", "statistic", "per_boundary")


def first_mismatch(name, presented, recomputed):
    fields = RULER_FIELDS if recomputed["kind"] == "RULER" else (
        PRESERVE_FIELDS if name == "PRESERVE" else GATE_FIELDS)
    for f in fields:
        if R.canonical_bytes(presented.get(f)) != R.canonical_bytes(recomputed[f]):
            return f
    return None


# --------------------------------------------------------------------------------------------------------
# G-RECOMP (B6.4), per claim over the claim's required nodes in the recompute set.

def _ran():
    return {"status": "RAN", "missing": [], "run_id": "consumer"}


def _fail(reason, witness, eligible, applicable):
    return {"execution": _ran(), "outcome": _gate("G-RECOMP", "FAIL", reason, witness, eligible, applicable)}


def g_recomp(claim, bundle, anchors):
    """PASS iff every presented receipt of the recompute set that RAN recomputes equal from its bound traces.

    Typed results (FD-T015-5): an absent receipt -> execution BLOCKED EVIDENCE_MISSING:<node_id> (as G-BIND);
    an unparseable receipt -> FAIL RECEIPT_SCHEMA:<field>; a required role whose bytes do not bind to the
    receipt's own ref -> FAIL BYTES_MISMATCH:<role> (nothing is recomputed from unbound bytes); bound bytes
    outside the trace format -> FAIL TRACE_SCHEMA:<role>; a difference -> FAIL OUTCOME_MISMATCH:<field>.
    A receipt whose execution is BLOCKED has no outcome to recompute; it is not applicable.
    """
    anchors = EV.resolve_anchors(anchors, bundle)
    nodes = [n for n in EV.required_nodes(claim, anchors) if EV.parse_node_id(n)[1] in RECOMPUTE_SET]
    eligible, applicable, done = len(nodes), 0, []
    for n in nodes:
        rc, err = bundle.parsed(n)
        if rc is None and err is None:
            return EV._blocked(["EVIDENCE_MISSING:%s" % n])
    for n in nodes:
        rc, err = bundle.parsed(n)
        if err is not None:
            return _fail(err, n, eligible, applicable)
        d = rc.to_dict()
        if d["execution"]["status"] != "RAN":
            continue
        name = EV.NAME[d["predicate"]["id"]]
        if name not in RECOMPUTE_SET:
            return _fail("IDENTITY_MISMATCH:predicate", n, eligible, applicable)
        runs = {}
        for role in RECOMPUTE_ROLES[name]:
            refs = [a for a in d["outputs"] if a["role"] == role]
            data = bundle.traces.get(n, {}).get(role)
            if len(refs) != 1 or data is None or len(data) != refs[0]["length"] \
                    or EV._sha(data) != refs[0]["sha256"]:
                return _fail("BYTES_MISMATCH:%s" % role, n, eligible, applicable)
            try:
                runs[role] = parse_trace(role, data)
            except TraceError as e:
                return _fail(e.code, n, eligible, applicable)
        applicable += 1
        field = first_mismatch(name, d["outcome"], recompute(name, d["world"]["variant"], runs))
        if field is not None:
            return _fail("OUTCOME_MISMATCH:%s" % field, n, eligible, applicable)
        done.append(name)
    return {"execution": _ran(),
            "outcome": _gate("G-RECOMP", "PASS", "recomputed equal: %s" % (", ".join(done) or "-"), None,
                             eligible, applicable)}


# --------------------------------------------------------------------------------------------------------
# Prerequisites (policy, B7.1) and the decision record (B1 DECISION RECORD, B3.5, B4.3, B7.2)

REQUIRED = {"BOUNDS": "PASS", "CALIBRATION": "PASS", "RETENTION": "POSITIVE", "ERASE": "PASS",
            "PRESERVE": "PASS", "CHANNEL": "PASS", "RESTART": "PASS", "OBSERVER": "PASS", "TWIN_EQ": "PASS"}
GATES = ("G-BIND", "G-INV", "G-RECOMP")
CLASS_N = {"form": "class", "class_id": "N", "def": "policies whose answer is a function of j alone",
           "bound": "1/2", "method": "enumeration of 8 policies over 12288 trials"}
SETTING_ID = "reset_model"


def prerequisites(claim, anchors):
    """[(kind, node or gate, required)] in B7.1 order; kind is "receipt", "gate" or "custody"."""
    t, m, w = claim["type"], claim["subject"], claim["world"]
    rcpt = lambda name, subj=m, world=w, obs=None: ("receipt", R.make_node_id(subj, name, world, obs),
                                                    REQUIRED[name])
    gate = lambda g: ("gate", g, "PASS")
    if t == "CL-CAL":
        return [rcpt("CALIBRATION", EV.WORLD_SUBJECT), gate("G-BIND"), gate("G-INV")]
    if t == "CL-CUST":
        return [("custody", "custody", "QUALIFIED"), gate("G-BIND"), gate("G-INV")]
    if t == "TWIN":
        return [rcpt("TWIN_EQ")]
    out = [rcpt("BOUNDS"), rcpt("CALIBRATION", EV.WORLD_SUBJECT, "STANDARD"), rcpt("RETENTION"), rcpt("ERASE"),
           rcpt("PRESERVE"), rcpt("CHANNEL"), rcpt("RESTART")]
    out += [rcpt("OBSERVER", obs=o) for o in claim["observers"]]
    return out + [gate("G-BIND"), gate("G-INV"), gate("G-RECOMP")]


def _scope_label(node_id):
    subject, _name, obs, world = EV.parse_node_id(node_id)
    return "/".join([subject] + ([obs] if obs else []) + [world])


class Consumer(object):
    """Evaluates registered claims against one presented bundle with the anchors and store the consumer holds.

    gate_versions: {gate: [CodeRef]} -- the consumer gates' own instrument versions (their stage records are
    looked up by these, B6.4). first_check_utc: the consumer's first check of the bundle (custody, B5.3).
    """

    def __init__(self, bundle, anchors, store, config, gate_versions, first_check_utc, keeper=None,
                 registrar=None):
        anchors = EV.resolve_anchors(anchors, bundle)          # C-004-T042 F2
        self.bundle, self.anchors, self.store, self.config = bundle, anchors, store, config
        self.gate_versions = dict(gate_versions)
        self.first_check_utc = first_check_utc
        self.keeper, self.registrar = keeper, registrar
        self.registry = EV.Registry(bundle, store)
        self.custody = EV.custody(bundle, anchors, store, first_check_utc, keeper, registrar)

    def _receipt_line(self, node_id, required):
        rc, err = self.bundle.parsed(node_id)
        auth = EV.authority(node_id, self.bundle, self.anchors, self.registry)
        instrument = (EV.parse_node_id(node_id)[1], None)
        if rc is None:
            ex = {"status": "BLOCKED", "missing": [err or "EVIDENCE_MISSING:%s" % node_id], "run_id": "absent"}
            v = R.make_verdict(node_id, ex, auth, None, required)
        else:
            d = rc.to_dict()
            instrument = (d["predicate"]["id"], EV.predicate_version(d["predicate"]["code"]))
            try:
                v = R.make_verdict(node_id, d["execution"], auth, d["outcome"], required)
            except R.VerdictError as e:          # a receipt of another predicate kind in this slot
                ex = {"status": "BLOCKED", "missing": ["VERDICT_REFUSED:%s" % e.code], "run_id": "absent"}
                v = R.make_verdict(node_id, ex, auth, None, required)
        return v, instrument

    def _gate_result(self, gate, claim):
        if gate == "G-BIND":
            return EV.g_bind(claim, self.bundle, self.anchors, self.config)
        if gate == "G-INV":
            return EV.g_inv(claim, self.bundle, self.anchors)
        return g_recomp(claim, self.bundle, self.anchors)

    def decide(self, claim):
        """The decision record of one claim (canonical JSON; see decision_bytes)."""
        lines, verdicts, instruments = [], [], set()
        recomputed = claim["type"] == "CL-RET"           # G-RECOMP is a prerequisite of CL-RET only (B7.1)
        custody_standing = None
        for kind, ref, required in prerequisites(claim, self.anchors):
            if kind == "custody":
                custody_standing = "SATISFIED" if self.custody["status"] == "QUALIFIED" else "UNQUALIFIED"
                lines.append({"predicate": "custody", "scope": claim["claim_id"], "required": required,
                              "custody": self.custody, "standing": custody_standing, "recomputed": False})
                continue
            if kind == "gate":
                res = self._gate_result(ref, claim)
                auth = EV.gate_authority(ref, self.gate_versions[ref], self.registry)
                v = R.make_verdict("gate:%s:%s" % (ref, claim["claim_id"]), res["execution"], auth,
                                   res["outcome"], required)
                instruments.add((ref, EV.predicate_version(self.gate_versions[ref])))
                lines.append({"predicate": ref, "scope": claim["claim_id"], "required": required,
                              "verdict": v, "recomputed": False})
            else:
                v, inst = self._receipt_line(ref, required)
                instruments.add(inst)
                name = EV.parse_node_id(ref)[1]
                lines.append({"predicate": name, "scope": _scope_label(ref), "required": required,
                              "verdict": v, "recomputed": recomputed and name in RECOMPUTE_SET})
            verdicts.append(v)
        el = R.eligibility(verdicts)
        if custody_standing is not None and custody_standing != "SATISFIED":
            el["eligibility"] = "NOT_ELIGIBLE"
            el["standing"] = min((el["standing"], custody_standing), key=R.STANDING_ORDER.index)
            el["not_satisfied"] = ["custody"] + el["not_satisfied"]
        cell = claim.get("cell") or {"cell_id": EV.REGISTERED_AXES["cell_id"],
                                     "revision": self.config.contract_revision}
        retention = None
        if claim["type"] == "CL-RET":
            rc, _ = self.bundle.parsed(R.make_node_id(claim["subject"], "RETENTION", claim["world"]))
            o = rc.to_dict()["outcome"] if rc is not None else None
            if o is not None:
                retention = {"successes": o["successes"], "trials": o["trials"], "statistic": o["statistic"]}
        return {"schema": "rso.slice001.decision.v1", "claim_id": claim["claim_id"], "type": claim["type"],
                "subject": claim["subject"], "world": claim["world"],
                "twin": claim.get("twin"), "encoding": claim.get("encoding"),
                "relative": self._relative(claim),
                "cell": {"cell_id": cell["cell_id"], "revision": cell["revision"]},
                "setting": {"id": SETTING_ID, "sha256": self.config.contract_revision},
                "prerequisites": lines, "eligibility": el["eligibility"], "standing": el["standing"],
                "not_satisfied": el["not_satisfied"], "authority": R.inherited_authority(verdicts),
                "instruments": len(instruments), "custody": self.custody,
                "unverified": EV.unverified_records(claim, self.bundle, self.anchors, self.registry),
                "retention": retention}

    def _relative(self, claim):
        if claim["type"] in ("CL-CAL", "CL-RET"):
            return dict(CLASS_N)
        if claim["type"] == "CL-CUST":
            rows = self.custody.get("rows", []) if self.custody["status"] == "QUALIFIED" else []
            return {"form": "comparator", "ids": ["keeper:C-004-OP2"] + list(rows)}
        return {"form": "comparator", "ids": [claim["subject"]]}

    def decide_all(self, claims):
        return {cid: self.decide(c) for cid, c in sorted(claims.items())}


def decision_bytes(decision):
    return R.canonical_bytes(decision)
