"""Producer receipt, three-field verdict and authority-stage record (C-004-T013).

Normative text: rso/slice001/contract/CONTRACT.md v1.0.0 (draft B B2-B4, B7.2 incorporated) and
AMENDMENT_v1.0.1.md (V1 node_id spelling, V2 trace roles, V3 parameter spellings, V8 fixture stores).

Five objects are kept apart (draft B B1). This module owns three of them:

  PRODUCER RECEIPT   one evaluation of one predicate: execution + outcome, closed schema, canonical bytes,
                     immutable. It has NO authority key (FD-B1): a producer cannot qualify its instrument.
  STAGE RECORD       the C4 authority stage of one instrument VERSION (B4.1).
  VERDICT            the consumer's three-field record per prerequisite (B3.5): execution, authority and
                     outcome are all present; standing is derived from them (B7.2) and never replaces them.

Not here: evidence-graph binding and invalidation (T014), the A1-A5 authority computation and rendering
(T014/T015). verdict_for_receipt() checks only that an asserted QUALIFIED stage does not exceed what a
supplied stage record for the receipt's exact instrument version says; deciding which records count as
registered is the caller's (B4.3, B6.5; V8: in S2 tests the in-memory fixture store counts for the logic and
is never custody evidence).

Python >= 3.8, standard library only.
"""
import copy
import hashlib
import json
import re
from fractions import Fraction

SCHEMA = "rso.slice001.receipt.v1"

PREDICATE_NAMES = (("P0", "BOUNDS"), ("P1", "CALIBRATION"), ("P2", "RETENTION"), ("P3", "ERASE"),
                   ("P4", "PRESERVE"), ("P5", "CHANNEL"), ("P6", "RESTART"), ("P7", "OBSERVER"),
                   ("P8", "TWIN_EQ"))
_ID_BY_NAME = {n: p for p, n in PREDICATE_NAMES}
_NAME_BY_ID = dict(PREDICATE_NAMES)
PREDICATE_KINDS = {p: ("RULER" if p == "P2" else "GATE") for p, _ in PREDICATE_NAMES}
CONSUMER_GATES = ("G-BIND", "G-INV", "G-RECOMP")      # no producer receipt (B3.1); stage records yes
WORLD_VARIANTS = ("STANDARD", "CLOCKED")
OBSERVER_PREDICATE = "P7"

EXECUTION_STATUS = ("RAN", "BLOCKED")
GATE_VALUES = ("PASS", "FAIL")
RULER_VALUES = ("POSITIVE", "NEGATIVE", "NOT_SHOWN")
TRACE_ROLES = ("trace:probe_a", "trace:probe_d", "trace:sends", "trace:deliveries", "trace:capture",
               "trace:clamp", "trace:observer")
STANDING_ORDER = ("BLOCKED", "UNQUALIFIED", "UNMET", "SATISFIED")       # worst first (B7.2, FD-B2)
STAGE_ORDER = ("AUTHOR_TESTED", "FIRST_SIGHT_CHALLENGED", "CLOSED_AFTER_REPAIR")   # lowest first (B4.1)

# B3.1 field table, in table order. Missing or malformed fields are reported in this order.
RECEIPT_FIELDS = ("schema", "node_id", "registration_ref", "contract_ref", "cell", "subject", "observer",
                  "world", "predicate", "code", "inputs", "outputs", "oracle", "expected_answer",
                  "dependencies", "execution", "outcome", "resources", "limitations", "created_at_utc")
CELL_AXES = ("cell_id", "revision", "physics", "world", "boundary", "search", "development", "resources",
             "measurement", "exposure")
EDIT_COUNTS = ("proposed", "applicable", "duplicate", "executed", "killed", "survived", "equivalent",
               "error", "timeout")

_HEX64 = re.compile(r"\A[0-9a-f]{64}\Z")
_HEX40 = re.compile(r"\A[0-9a-f]{40}\Z")
_UTC = re.compile(r"\A\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z\Z")
_DATE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")
_RATIONAL = re.compile(r"\A(0|[1-9]\d*)/([1-9]\d*)\Z")
_NODE_ID = re.compile(r"\Arcpt:([^:\s]+):([A-Z_]+)(?::([^:\s]+))?:([A-Z]+)\Z")


class _CodedError(ValueError):
    def __init__(self, code, detail=""):
        self.code = code
        ValueError.__init__(self, code + (": " + detail if detail else ""))


class ReceiptError(_CodedError):
    """A producer receipt or canonical bytes refused. code = RECEIPT_SCHEMA:<dotted field path>."""


class VerdictError(_CodedError):
    """A three-field verdict refused (e.g. VERDICT_FIELD_MISSING:<field>)."""


class StageError(_CodedError):
    """A stage record or stage list refused. code = STAGE_SCHEMA:<field> or STAGE_UNKNOWN:<value>."""


class AuthorityRefused(_CodedError):
    """An asserted QUALIFIED authority not backed by a stage record for the exact instrument version."""


# --------------------------------------------------------------------------------------------------------
# Canonical bytes (B2)

def _check_canonical_value(obj, path="$"):
    if obj is None or isinstance(obj, (bool, str)):
        return
    if isinstance(obj, int):
        return
    if isinstance(obj, float):
        raise ReceiptError("RECEIPT_SCHEMA:float", "floats are not allowed at %s" % path)
    if isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _check_canonical_value(v, "%s[%d]" % (path, i))
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise ReceiptError("RECEIPT_SCHEMA:key", "non-string key at %s" % path)
            _check_canonical_value(v, path + "." + k)
        return
    raise ReceiptError("RECEIPT_SCHEMA:type", "%s at %s" % (type(obj).__name__, path))


def canonical_bytes(obj):
    """JSON, UTF-8, keys sorted, separators , and :, no whitespace, no floats (B2)."""
    _check_canonical_value(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def sha256_hex(obj):
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def _no_duplicates(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ReceiptError("RECEIPT_SCHEMA:duplicate_key", k)
        out[k] = v
    return out


def _refuse_float(s):
    raise ReceiptError("RECEIPT_SCHEMA:float", s)


def _refuse_constant(s):
    raise ReceiptError("RECEIPT_SCHEMA:float", s)


def loads_canonical(data):
    """Parse JSON bytes, refusing duplicate keys, floats and NaN/Infinity (B2)."""
    if isinstance(data, bytes):
        try:
            data = data.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ReceiptError("RECEIPT_SCHEMA:encoding", str(e))
    try:
        return json.loads(data, object_pairs_hook=_no_duplicates, parse_float=_refuse_float,
                          parse_constant=_refuse_constant)
    except ReceiptError:
        raise
    except ValueError as e:
        raise ReceiptError("RECEIPT_SCHEMA:json", str(e))


# --------------------------------------------------------------------------------------------------------
# Field checkers. Each raises ReceiptError("RECEIPT_SCHEMA:<path>") on the first problem.

def _fail(path, detail=""):
    raise ReceiptError("RECEIPT_SCHEMA:" + path, detail)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _nat(v, path):
    if not _is_int(v) or v < 0:
        _fail(path, "non-negative integer required")


def _str(v, path):
    if not isinstance(v, str) or not v:
        _fail(path, "non-empty string required")


def _obj(v, path, keys):
    """A closed object: exactly `keys`. Missing keys are reported before unknown ones, in key order."""
    if not isinstance(v, dict):
        _fail(path, "object required")
    for k in keys:
        if k not in v:
            _fail(path + "." + k, "missing")
    for k in sorted(v):
        if k not in keys:
            _fail(path + "." + k, "unknown field")


def _hex64(v, path):
    if not isinstance(v, str) or not _HEX64.match(v):
        _fail(path, "64 lowercase hex required")


def _hex40(v, path):
    if not isinstance(v, str) or not _HEX40.match(v):
        _fail(path, "40 lowercase hex required")


def _repo_ref(v, path):
    _obj(v, path, ("path", "blob_sha256", "commit"))
    _str(v["path"], path + ".path")
    _hex64(v["blob_sha256"], path + ".blob_sha256")
    _hex40(v["commit"], path + ".commit")


def _artifact_ref(v, path):
    _obj(v, path, ("role", "sha256", "length"))
    _str(v["role"], path + ".role")
    _hex64(v["sha256"], path + ".sha256")
    _nat(v["length"], path + ".length")


def _code_ref(v, path):
    _obj(v, path, ("role", "sha256", "length", "commit"))
    if not isinstance(v["role"], str) or not v["role"].startswith("code:") or len(v["role"]) <= 5:
        _fail(path + ".role", "code:<repo path> required")
    _hex64(v["sha256"], path + ".sha256")
    _nat(v["length"], path + ".length")
    _hex40(v["commit"], path + ".commit")


def _code_refs(v, path):
    if not isinstance(v, list) or not v:
        _fail(path, "non-empty list of CodeRef required")
    for i, c in enumerate(v):
        _code_ref(c, "%s[%d]" % (path, i))


def _str_list(v, path, nonempty=False):
    if not isinstance(v, list) or (nonempty and not v):
        _fail(path, ("non-empty " if nonempty else "") + "list of strings required")
    for i, s in enumerate(v):
        _str(s, "%s[%d]" % (path, i))


def _rational(v, path):
    if not isinstance(v, str):
        _fail(path, "exact rational string n/d required")
    m = _RATIONAL.match(v)
    if not m:
        _fail(path, "exact rational string n/d required")
    n, d = int(m.group(1)), int(m.group(2))
    f = Fraction(n, d)
    if (f.numerator, f.denominator) != (n, d):
        _fail(path, "not in lowest terms")
    return f


def _utc(v, path):
    if not isinstance(v, str) or not _UTC.match(v):
        _fail(path, "ISO-8601 UTC with Z required")


def make_node_id(subject, predicate_name, world, observer=None):
    """rcpt:<subject>:<predicate NAME>[:<observer>]:<world> (draft B B3.1, amendment V1)."""
    if predicate_name not in _ID_BY_NAME:
        raise ReceiptError("RECEIPT_SCHEMA:node_id", "unknown predicate name %r" % predicate_name)
    parts = ["rcpt", subject, predicate_name] + ([observer] if observer is not None else []) + [world]
    return ":".join(parts)


def _check_node_id_form(v, path):
    if not isinstance(v, str):
        _fail(path, "string required")
    m = _NODE_ID.match(v)
    if not m or m.group(2) not in _ID_BY_NAME or m.group(4) not in WORLD_VARIANTS:
        _fail(path, "rcpt:<subject>:<predicate NAME>[:<observer>]:<world> required")
    return m


def _cell(v, path):
    _obj(v, path, CELL_AXES)
    _str(v["cell_id"], path + ".cell_id")
    _hex64(v["revision"], path + ".revision")
    for a in CELL_AXES[2:]:
        _str(v[a], path + "." + a)


def _gate_outcome(v, path, pid):
    _obj(v, path, ("kind", "predicate", "value", "reason", "witness", "eligible_count",
                   "applicable_count", "vacuous"))
    if v["predicate"] != pid:
        _fail(path + ".predicate", "must equal predicate.id")
    if v["value"] not in GATE_VALUES:
        _fail(path + ".value", "gate value must be PASS or FAIL")
    _str(v["reason"], path + ".reason")
    if (v["witness"] is None) != (v["value"] == "PASS"):
        _fail(path + ".witness", "witness is null iff PASS")
    _nat(v["eligible_count"], path + ".eligible_count")
    if v["applicable_count"] is not None:
        _nat(v["applicable_count"], path + ".applicable_count")
    if not isinstance(v["vacuous"], bool) or v["vacuous"] != (v["applicable_count"] == 0):
        _fail(path + ".vacuous", "vacuous is true iff applicable_count = 0")


def _ruler_outcome(v, path, pid):
    _obj(v, path, ("kind", "ruler", "value", "statistic", "successes", "trials", "per_boundary",
                   "reason"))
    if v["ruler"] != pid:
        _fail(path + ".ruler", "must equal predicate.id")
    if v["value"] not in RULER_VALUES:
        _fail(path + ".value", "ruler value must be POSITIVE, NEGATIVE or NOT_SHOWN")
    _nat(v["successes"], path + ".successes")
    _nat(v["trials"], path + ".trials")
    if v["trials"] == 0 or v["successes"] > v["trials"]:
        _fail(path + ".trials", "0 < trials and successes <= trials required")
    if _rational(v["statistic"], path + ".statistic") != Fraction(v["successes"], v["trials"]):
        _fail(path + ".statistic", "must equal successes/trials")
    pb = v["per_boundary"]
    if not isinstance(pb, list):
        _fail(path + ".per_boundary", "list required")
    for i, b in enumerate(pb):
        p = "%s.per_boundary[%d]" % (path, i)
        _obj(b, p, ("j", "statistic"))
        _nat(b["j"], p + ".j")
        _rational(b["statistic"], p + ".statistic")
    _str(v["reason"], path + ".reason")


def _outcome(v, path, pid):
    if not isinstance(v, dict):
        _fail(path, "object required")
    kind = PREDICATE_KINDS[pid]
    if v.get("kind") != kind:
        _fail(path + ".kind", "predicate %s is a %s" % (pid, kind))
    if kind == "GATE":
        _gate_outcome(v, path, pid)
    else:
        _ruler_outcome(v, path, pid)


def _execution(v, path):
    _obj(v, path, ("status", "missing", "run_id"))
    if v["status"] not in EXECUTION_STATUS:
        _fail(path + ".status", "RAN or BLOCKED")
    _str_list(v["missing"], path + ".missing", nonempty=(v["status"] == "BLOCKED"))
    if v["status"] == "RAN" and v["missing"]:
        _fail(path + ".missing", "RAN has missing = []")
    _str(v["run_id"], path + ".run_id")


def validate_receipt(d):
    """Validate a producer receipt dict against draft B B3 (closed schema). Raise ReceiptError."""
    if not isinstance(d, dict):
        _fail("$", "object required")
    if "authority" in d:                                   # FD-B1, before anything else
        _fail("authority", "a producer receipt carries no authority (FD-B1)")
    for f in RECEIPT_FIELDS:
        if f not in d:
            _fail(f, "missing")
    for f in sorted(d):
        if f not in RECEIPT_FIELDS:
            _fail(f, "unknown field")

    if d["schema"] != SCHEMA:
        _fail("schema", "must be %s" % SCHEMA)
    m = _check_node_id_form(d["node_id"], "node_id")
    _repo_ref(d["registration_ref"], "registration_ref")
    _repo_ref(d["contract_ref"], "contract_ref")
    _cell(d["cell"], "cell")
    _obj(d["subject"], "subject", ("id", "code"))
    _str(d["subject"]["id"], "subject.id")
    _code_refs(d["subject"]["code"], "subject.code")

    pred = d["predicate"]
    _obj(pred, "predicate", ("id", "kind", "code"))
    if pred["id"] not in _NAME_BY_ID:
        _fail("predicate.id", "P0..P8 required")
    pid = pred["id"]
    if pred["kind"] != PREDICATE_KINDS[pid]:
        _fail("predicate.kind", "predicate %s is a %s" % (pid, PREDICATE_KINDS[pid]))
    _code_refs(pred["code"], "predicate.code")
    # V1: the node_id carries this predicate's NAME; the observer segment is present iff P7.
    if m.group(2) != _NAME_BY_ID[pid] or (m.group(3) is None) != (pid != OBSERVER_PREDICATE):
        _fail("node_id", "must name predicate %s and carry an observer segment iff P7"
              % _NAME_BY_ID[pid])

    obs = d["observer"]
    if pid == OBSERVER_PREDICATE:
        _obj(obs, "observer", ("id", "code"))
        _str(obs["id"], "observer.id")
        _code_refs(obs["code"], "observer.code")
    elif obs is not None:
        _fail("observer", "null except for P7")

    _obj(d["world"], "world", ("variant", "code"))
    if d["world"]["variant"] not in WORLD_VARIANTS:
        _fail("world.variant", "STANDARD or CLOCKED")
    _code_refs(d["world"]["code"], "world.code")

    code = d["code"]
    _obj(code, "code", ("producer", "base_sha", "branch", "worktree_path", "dirty"))
    _code_refs(code["producer"], "code.producer")
    _hex40(code["base_sha"], "code.base_sha")
    _str(code["branch"], "code.branch")
    _str(code["worktree_path"], "code.worktree_path")
    if not isinstance(code["dirty"], bool):
        _fail("code.dirty", "boolean required")       # dirty=true is G-BIND's (T014), not a schema error

    _obj(d["inputs"], "inputs", ("domain", "reset_model_sha256"))
    _artifact_ref(d["inputs"]["domain"], "inputs.domain")
    _hex64(d["inputs"]["reset_model_sha256"], "inputs.reset_model_sha256")

    outs = d["outputs"]
    if not isinstance(outs, list):
        _fail("outputs", "list required")
    for i, a in enumerate(outs):
        _artifact_ref(a, "outputs[%d]" % i)
        if a["role"] not in TRACE_ROLES:
            _fail("outputs", "role %r is not a V2 trace role" % a["role"])

    _artifact_ref(d["oracle"], "oracle")
    _obj(d["expected_answer"], "expected_answer", ("table", "row_id"))
    _repo_ref(d["expected_answer"]["table"], "expected_answer.table")
    _str(d["expected_answer"]["row_id"], "expected_answer.row_id")

    deps = d["dependencies"]
    if not isinstance(deps, list):
        _fail("dependencies", "list required")
    for i, n in enumerate(deps):
        _check_node_id_form(n, "dependencies[%d]" % i)
    if deps != sorted(set(deps)):
        _fail("dependencies", "sorted and unique required")

    _execution(d["execution"], "execution")
    if d["execution"]["status"] == "RAN":
        if d["outcome"] is None:
            _fail("outcome", "RAN requires an outcome")
        _outcome(d["outcome"], "outcome", pid)
    elif d["outcome"] is not None:
        _fail("outcome", "BLOCKED carries no outcome")

    res = d["resources"]
    _obj(res, "resources", ("cpu_seconds", "wall_seconds", "launches", "artifact_bytes"))
    for k in ("cpu_seconds", "wall_seconds", "launches", "artifact_bytes"):
        _nat(res[k], "resources." + k)
    _str_list(d["limitations"], "limitations", nonempty=True)
    _utc(d["created_at_utc"], "created_at_utc")
    _check_canonical_value(d)                              # free-form parts (witness): no floats


class Receipt(object):
    """An immutable, validated producer receipt. Holds only its canonical bytes."""

    __slots__ = ("_bytes", "_sha256", "_node_id")

    def __init__(self, *a, **k):
        raise TypeError("use Receipt.from_dict or Receipt.from_bytes")

    @classmethod
    def _make(cls, d):
        validate_receipt(d)
        self = object.__new__(cls)
        b = canonical_bytes(d)
        object.__setattr__(self, "_bytes", b)
        object.__setattr__(self, "_sha256", hashlib.sha256(b).hexdigest())
        object.__setattr__(self, "_node_id", d["node_id"])
        return self

    @classmethod
    def from_dict(cls, d):
        return cls._make(copy.deepcopy(d))

    @classmethod
    def from_bytes(cls, data):
        return cls._make(loads_canonical(data))

    def __setattr__(self, name, value):
        raise AttributeError("Receipt is immutable")

    def __delattr__(self, name):
        raise AttributeError("Receipt is immutable")

    @property
    def node_id(self):
        return self._node_id

    @property
    def sha256(self):
        return self._sha256

    def canonical_bytes(self):
        return self._bytes

    def to_dict(self):
        """A fresh copy; mutating it never changes the receipt."""
        return json.loads(self._bytes.decode("utf-8"))

    def __eq__(self, other):
        return isinstance(other, Receipt) and other._bytes == self._bytes

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._bytes)

    def __repr__(self):
        return "Receipt(%s, sha256=%s)" % (self._node_id, self._sha256[:12])


# --------------------------------------------------------------------------------------------------------
# Authority stage (C4, B4)

def stage_rank(stage):
    if stage not in STAGE_ORDER:
        raise StageError("STAGE_UNKNOWN:%s" % (stage,))
    return STAGE_ORDER.index(stage)


def lowest_stage(stages):
    """The lowest stage in a non-empty list (B4.3: a claim inherits the lowest among its instruments)."""
    stages = list(stages)
    if not stages:
        raise StageError("STAGE_SCHEMA:stages", "no instruments")
    return min(stages, key=stage_rank)


def _sfail(path, detail=""):
    raise StageError("STAGE_SCHEMA:" + path, detail)


def _as_stage(fn, *args):
    try:
        return fn(*args)
    except ReceiptError as e:
        raise StageError(e.code.replace("RECEIPT_SCHEMA:", "STAGE_SCHEMA:", 1), str(e))


def _count_pair(v, path):
    _as_stage(_obj, v, path, ("correct", "total"))
    _as_stage(_nat, v["correct"], path + ".correct")
    _as_stage(_nat, v["total"], path + ".total")
    if v["correct"] > v["total"]:
        _sfail(path, "correct > total")


def _challenge(v, path, keys):
    _as_stage(_obj, v, path, keys)
    if not isinstance(v["date"], str) or not _DATE.match(v["date"]):
        _sfail(path + ".date", "YYYY-MM-DD required")
    _as_stage(_obj, v["challenger"], path + ".challenger", ("seat", "model"))
    _as_stage(_str, v["challenger"]["seat"], path + ".challenger.seat")
    _as_stage(_str, v["challenger"]["model"], path + ".challenger.model")
    _as_stage(_repo_ref, v["set_ref"], path + ".set_ref")
    _count_pair(v["sound_cases"], path + ".sound_cases")
    _count_pair(v["broken_cases"], path + ".broken_cases")
    _as_stage(_obj, v["edits"], path + ".edits", EDIT_COUNTS)
    for k in EDIT_COUNTS:
        _as_stage(_nat, v["edits"][k], path + ".edits." + k)
    _as_stage(_nat, v["unresolved"], path + ".unresolved")


_FIRST_SIGHT_KEYS = ("date", "challenger", "set_ref", "sound_cases", "broken_cases", "edits", "unresolved")
_CLOSURE_KEYS = _FIRST_SIGHT_KEYS + ("first_sight_preserved",)
_STAGE_KEYS = ("instrument", "version", "stage", "fire_test", "first_sight", "closure", "recorded_by",
               "recorded_at_utc")


def validate_stage_record(rec):
    """Validate a StageRecord (draft B B4.1). Raise StageError; return rec unchanged."""
    _as_stage(_check_canonical_value, rec)
    _as_stage(_obj, rec, "$", _STAGE_KEYS)
    if rec["instrument"] not in _NAME_BY_ID and rec["instrument"] not in CONSUMER_GATES:
        _sfail("instrument", "P0..P8 or a consumer gate required")
    _as_stage(_code_refs, rec["version"], "version")
    stage_rank(rec["stage"])
    ft = rec["fire_test"]
    _as_stage(_obj, ft, "fire_test", ("must_accept", "must_reject", "receipt"))
    # rso-builder 2.4: at least one case it must accept and one it must reject with the expected reason.
    _as_stage(_str_list, ft["must_accept"], "fire_test.must_accept", True)
    if not isinstance(ft["must_reject"], list) or not ft["must_reject"]:
        _sfail("fire_test.must_reject", "at least one case the instrument must reject")
    for i, c in enumerate(ft["must_reject"]):
        p = "fire_test.must_reject[%d]" % i
        _as_stage(_obj, c, p, ("case_id", "expected_reason"))
        _as_stage(_str, c["case_id"], p + ".case_id")
        _as_stage(_str, c["expected_reason"], p + ".expected_reason")
    _as_stage(_repo_ref, ft["receipt"], "fire_test.receipt")

    rank = stage_rank(rec["stage"])
    if rank >= 1:
        if rec["first_sight"] is None:
            _sfail("first_sight", "required at FIRST_SIGHT_CHALLENGED and above")
        _challenge(rec["first_sight"], "first_sight", _FIRST_SIGHT_KEYS)
    elif rec["first_sight"] is not None:
        _sfail("first_sight", "AUTHOR_TESTED carries no challenge record")
    if rank == 2:
        if rec["closure"] is None:
            _sfail("closure", "required at CLOSED_AFTER_REPAIR")
        _challenge(rec["closure"], "closure", _CLOSURE_KEYS)
        # Scores are never merged: the closure record carries the first-sight object unchanged.
        if canonical_bytes(rec["closure"]["first_sight_preserved"]) != canonical_bytes(rec["first_sight"]):
            _sfail("closure.first_sight_preserved", "must equal first_sight unchanged")
    elif rec["closure"] is not None:
        _sfail("closure", "only at CLOSED_AFTER_REPAIR")
    _as_stage(_str, rec["recorded_by"], "recorded_by")
    _as_stage(_utc, rec["recorded_at_utc"], "recorded_at_utc")
    return rec


def _version_key(code_refs):
    return canonical_bytes(sorted(code_refs, key=lambda c: canonical_bytes(c)))


def recorded_stage(stage_records, instrument, version):
    """Highest stage among the supplied records for (instrument, exact version); None if there are none.

    The caller supplies only records it treats as registered (B4.3, B6.5; V8 for S2 fixtures). A record for
    another version of the same instrument does not count (B4.1: a stage belongs to a VERSION).
    """
    key = _version_key(version)
    best = None
    for rec in stage_records:
        validate_stage_record(rec)
        if rec["instrument"] == instrument and _version_key(rec["version"]) == key:
            if best is None or stage_rank(rec["stage"]) > stage_rank(best):
                best = rec["stage"]
    return best


# --------------------------------------------------------------------------------------------------------
# Three-field verdict (B3.5) and eligibility (B7.2)

VERDICT_FIELDS = ("execution", "authority", "outcome")


def _authority(v):
    if not isinstance(v, dict) or v.get("status") not in ("QUALIFIED", "UNQUALIFIED"):
        raise VerdictError("VERDICT_SCHEMA:authority", "QUALIFIED or UNQUALIFIED")
    if v["status"] == "QUALIFIED":
        if sorted(v) != ["stage", "status"]:
            raise VerdictError("VERDICT_SCHEMA:authority", "{status, stage}")
        try:
            stage_rank(v["stage"])
        except StageError as e:
            raise VerdictError("VERDICT_SCHEMA:authority.stage", str(e))
    else:
        if sorted(v) != ["status", "why"] or not isinstance(v["why"], list) or not v["why"] \
                or not all(isinstance(w, str) and w for w in v["why"]):
            raise VerdictError("VERDICT_SCHEMA:authority", "UNQUALIFIED needs a non-empty why list")


def _verdict_outcome(execution, outcome, required):
    if execution["status"] == "BLOCKED":
        if outcome is not None:
            raise VerdictError("VERDICT_SCHEMA:outcome", "BLOCKED carries no outcome")
        return
    if not isinstance(outcome, dict) or outcome.get("kind") not in ("GATE", "RULER"):
        raise VerdictError("VERDICT_SCHEMA:outcome", "RAN requires a GATE or RULER outcome")
    pid = outcome.get("predicate") if outcome["kind"] == "GATE" else outcome.get("ruler")
    if PREDICATE_KINDS.get(pid) != outcome["kind"]:
        raise VerdictError("VERDICT_SCHEMA:outcome", "outcome predicate/kind mismatch")
    try:
        _outcome(outcome, "outcome", pid)
    except ReceiptError as e:
        raise VerdictError(e.code.replace("RECEIPT_SCHEMA:", "VERDICT_SCHEMA:", 1), str(e))
    allowed = GATE_VALUES if outcome["kind"] == "GATE" else RULER_VALUES
    if required not in allowed:
        raise VerdictError("VERDICT_SCHEMA:required",
                           "required value %r is not a %s value" % (required, outcome["kind"]))


def make_verdict(node_id, execution, authority, outcome, required):
    """Assemble the B3.5 record; derive standing by B7.2. `required` is the policy's required value."""
    if not isinstance(node_id, str) or not node_id:
        raise VerdictError("VERDICT_SCHEMA:node_id")
    try:
        _execution(execution, "execution")
    except ReceiptError as e:
        raise VerdictError(e.code.replace("RECEIPT_SCHEMA:", "VERDICT_SCHEMA:", 1), str(e))
    _authority(authority)
    allowed = set(GATE_VALUES) | set(RULER_VALUES)
    if required not in allowed:
        raise VerdictError("VERDICT_SCHEMA:required", repr(required))
    _verdict_outcome(execution, outcome, required)

    if execution["status"] == "BLOCKED":
        standing, reasons = "BLOCKED", list(execution["missing"])
    elif authority["status"] == "UNQUALIFIED":
        standing, reasons = "UNQUALIFIED", list(authority["why"])
    elif outcome["value"] != required:
        standing, reasons = "UNMET", [outcome["reason"]]
    else:
        standing, reasons = "SATISFIED", [outcome["reason"]]
    return {"node_id": node_id, "execution": copy.deepcopy(execution),
            "authority": copy.deepcopy(authority), "outcome": copy.deepcopy(outcome),
            "standing": standing, "reasons": reasons}


def verdict_from_fields(fields, required):
    """make_verdict from a dict that must carry node_id and all three C1 fields (outcome may be null)."""
    if not isinstance(fields, dict):
        raise VerdictError("VERDICT_SCHEMA:$")
    for f in ("node_id",) + VERDICT_FIELDS:
        if f not in fields:
            raise VerdictError("VERDICT_FIELD_MISSING:" + f)
    return make_verdict(fields["node_id"], fields["execution"], fields["authority"], fields["outcome"],
                        required)


def verdict_for_receipt(receipt, authority, required, stage_records):
    """The verdict for one bound producer receipt, refusing an unbacked QUALIFIED authority.

    Cheat control (packet T013): QUALIFIED at stage X is accepted only if a supplied stage record for the
    receipt's exact instrument version is at X or higher; a claimed stage above the record is refused with
    STAGE_EXCEEDS_RECORD:<claimed>><recorded>, no record at all with NO_STAGE_RECORD. Computing authority
    (A1-A5) and choosing which records are registered is the consumer's (T014/T015).
    """
    if not isinstance(receipt, Receipt):
        raise VerdictError("VERDICT_SCHEMA:receipt", "a validated Receipt is required")
    d = receipt.to_dict()
    _authority(authority)
    if authority["status"] == "QUALIFIED":
        rec = recorded_stage(stage_records, d["predicate"]["id"], d["predicate"]["code"])
        if rec is None:
            raise AuthorityRefused("NO_STAGE_RECORD")
        if stage_rank(authority["stage"]) > stage_rank(rec):
            raise AuthorityRefused("STAGE_EXCEEDS_RECORD:%s>%s" % (authority["stage"], rec))
    return make_verdict(d["node_id"], d["execution"], authority, d["outcome"], required)


def _check_verdict(v):
    if not isinstance(v, dict):
        raise VerdictError("VERDICT_SCHEMA:$")
    for f in ("node_id",) + VERDICT_FIELDS + ("standing", "reasons"):
        if f not in v:
            raise VerdictError("VERDICT_FIELD_MISSING:" + f)
    if v["standing"] not in STANDING_ORDER:
        raise VerdictError("VERDICT_SCHEMA:standing")


def eligibility(verdicts):
    """Claim eligibility (B7.2): ELIGIBLE iff every prerequisite SATISFIED; else the worst standing.

    not_satisfied lists EVERY non-SATISFIED prerequisite (sorted node ids), so a headline BLOCKED never
    hides an UNMET line.
    """
    verdicts = list(verdicts)
    if not verdicts:
        raise VerdictError("VERDICT_SCHEMA:prerequisites", "a claim has at least one prerequisite")
    for v in verdicts:
        _check_verdict(v)
    worst = min((v["standing"] for v in verdicts), key=STANDING_ORDER.index)
    bad = sorted(v["node_id"] for v in verdicts if v["standing"] != "SATISFIED")
    return {"eligibility": "ELIGIBLE" if not bad else "NOT_ELIGIBLE", "standing": worst,
            "not_satisfied": bad}


def inherited_authority(verdicts):
    """A claim's authority (B4.3): the lowest stage among its prerequisites' instruments, gates and rulers
    alike (FD-B6); if any prerequisite is UNQUALIFIED the claim has no stage and is UNQUALIFIED with every
    reason, each prefixed by its node id.
    """
    verdicts = list(verdicts)
    if not verdicts:
        raise StageError("STAGE_SCHEMA:stages", "no instruments")
    why = []
    for v in sorted(verdicts, key=lambda x: x["node_id"]):
        _check_verdict(v)
        _authority(v["authority"])
        if v["authority"]["status"] == "UNQUALIFIED":
            why.extend("%s: %s" % (v["node_id"], w) for w in v["authority"]["why"])
    if why:
        return {"status": "UNQUALIFIED", "why": why}
    return {"status": "QUALIFIED", "stage": lowest_stage(v["authority"]["stage"] for v in verdicts)}
