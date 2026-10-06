"""C-004-T020: the S2 matrix run -- produce ledgered bundles, consume them with the real consumer, compare with the
independent expected-answer table (rso/slice001/expected/EXPECTED_ANSWERS.json, CONTRACT.md R4).

Two phases, because custody needs registration between them (AMENDMENT_v1.0.1 V8, v1.0.2 W1):

  produce   one ledger, five TOP_LEVEL launches (each bundle = 1 launch + 1 RECEIPT row per receipt, V7):
              G0      build_g0 (draft B B9: REG, PKTD, LAGD; observers NULL/BOOKKEEP; twin REG-ONEHOT)
              EXTRA   the non-G0 case subjects, observer NULL
              HEAL    REG with observers BOOKKEEP, NULL, HEAL (T07.HEAL: "CL-RET(REG) with HEAL registered as used")
              FLAT    REG with twin REG-FLAT    (a TWIN_EQ node id has no twin segment: one bundle per twin)
              LOSSY   REG with twin LOSSY
            Every bundle is written as exact canonical bytes under rso/slice001/s2/<NAME>/ so a committed file's
            blob sha256 IS the record identity the consumer looks up (the T027 lesson).
  consume   after Aporia registers EVIDENCE_MANIFEST + RUN_INVENTORY (G0) and the stage records: the real store
            (contract custody.store) for the five bundles; each E01-E05 edit keeps its own fixture store, because
            those cases construct withdrawals and late/fabricated keeper rows that must never be written to the
            real registry (V8: fixture stores are logic only).

The comparison itself is rso/slice001/matrix.py. This module never classifies a mismatch.
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time

from rso.slice001 import checker as C
from rso.slice001 import evidence as EV
from rso.slice001 import ledger as L
from rso.slice001 import matrix as M
from rso.slice001 import receipt as R
from rso.slice001 import rulers as RU
from rso.slice001 import s2_bundle as SB
from rso.slice001.fixtures import evidence_cases as F

REPO = SB.REPO_ROOT
OUT = os.environ.get("RSO_S2_OUT") or os.path.join(REPO, "rso", "slice001", "s2")   # S4 rerun: rso/slice001/s4
EXTRA_SUBJECTS = ("QCARRY", "AMNESIAC", "FLIP", "WIPE", "PKTD_NOQ", "HCOUNT", "EVERY3", "SLEEPER", "SPLIT1", "SPLIT2",
                  "OVERDELAY")
BUNDLES = ("G0", "EXTRA", "HEAL", "FLAT", "LOSSY")
G0_SUBJECTS = set(SB.SUBJECTS)
if not hasattr(R, "PREDICATE_NAMES_SET"):
    R.PREDICATE_NAMES_SET = {n for _p, n in R.PREDICATE_NAMES}


# ------------------------------------------------------------------------------------------------------------ produce

def _canon(obj):
    return R.canonical_bytes(obj)


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def record_versions():
    """{predicate NAME: version CodeRefs} from the committed stage records. Receipts MUST carry exactly these as
    predicate.code: the consumer matches a receipt to its stage record by the exact version list, and
    s2_bundle.predicate_version orders the same files differently (found in the T020 dry run: every
    authority NO_STAGE_RECORD)."""
    recs, _ = stage_records()
    names = dict(R.PREDICATE_NAMES)
    return {names[r["instrument"]]: r["version"] for r in recs if r["instrument"] in names}


def build(name, commit, ledger, created_at_utc, versions):
    kw = {"created_at_utc": created_at_utc, "versions": versions}
    if name == "G0":
        return SB.build_g0(commit, ledger, **kw)
    if name == "EXTRA":
        return SB.build_bundle(commit, ledger, EXTRA_SUBJECTS, node_id="EXTRA", **kw)
    if name == "HEAL":
        return SB.build_bundle(commit, ledger, ["REG"], observers={"REG": ("BOOKKEEP", "HEAL", "NULL")},
                               node_id="HEAL", **kw)
    if name == "FLAT":
        return SB.build_bundle(commit, ledger, ["REG"], twins=[("REG", "REG_FLAT")], node_id="FLAT", **kw)
    if name == "LOSSY":
        return SB.build_bundle(commit, ledger, ["REG"], twins=[("REG", "LOSSY")], node_id="LOSSY", **kw)
    raise ValueError(name)


def save(name, g):
    d = os.path.join(OUT, name)
    _write(os.path.join(d, "receipts.json"), _canon({"schema": "rso.slice001.s2.receipts.v1", "receipts": g.dicts}))
    _write(os.path.join(d, "traces.json"), _canon({"schema": "rso.slice001.s2.traces.v1", "traces": {
        nid: {role: base64.b64encode(b).decode("ascii") for role, b in sorted(t.items())}
        for nid, t in sorted(g.traces.items())}}))
    _write(os.path.join(d, "inventory.json"), _canon({"schema": EV.INVENTORY_SCHEMA, "rows": g.inventory}))
    _write(os.path.join(d, "MANIFEST.json"), g.manifest)
    _write(os.path.join(d, "run.json"), _canon({"run_id": g.run_id}))


def load(name):
    d = os.path.join(OUT, name)

    def j(f):
        with open(os.path.join(d, f), "rb") as fh:
            return json.loads(fh.read())
    tr = {nid: {role: base64.b64decode(s) for role, s in t.items()} for nid, t in j("traces.json")["traces"].items()}
    with open(os.path.join(d, "MANIFEST.json"), "rb") as fh:
        manifest = fh.read()
    return SB.G0(j("receipts.json")["receipts"], tr, j("inventory.json")["rows"], manifest, j("run.json")["run_id"])


def produce(commit, ledger_path, created_at_utc=None):
    """Five ledgered builds at `commit`. Refuses on a dirty named-code tree (build_bundle's own check)."""
    led = L.Ledger.from_contract(ledger_path)
    stamp = created_at_utc or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    usage = {}
    versions = record_versions()
    if len(versions) != 9:
        raise RuntimeError("expected stage-record versions for P0-P8, got %s" % sorted(versions))
    for name in BUNDLES:
        t0 = time.time()
        g = build(name, commit, led, stamp, versions)
        save(name, g)
        usage[name] = {"receipts": len(g.dicts), "wall_ms": int((time.time() - t0) * 1000), "run_id": g.run_id}
    u = led.usage()                                     # canonical bytes refuse floats (B2): integer microseconds
    usage["ledger"] = {"launches": u["launches"], "cpu_us": int(round(u["cpu_s"] * 1e6)),
                       "artifact_bytes": u["artifact_bytes"]}
    _write(os.path.join(OUT, "PRODUCE.json"), _canon({"commit": commit, "created_at_utc": stamp, "usage": usage}))
    return usage


# ------------------------------------------------------------------------------------------------------------ consume

def stage_records():
    recs, blobs = [], {}
    stages = os.path.join(REPO, "rso", "slice001", "stages")
    for fn in sorted(os.listdir(stages)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(stages, fn), "rb") as f:
            r = json.loads(f.read())
        if isinstance(r, dict) and "instrument" in r and "fire_test" in r:
            recs.append(r)
            p = r["fire_test"]["receipt"]["path"]
            with open(os.path.join(REPO, *p.split("/")), "rb") as f:
                blobs[p] = f.read().replace(b"\r\n", b"\n")
    return recs, blobs


def live_store():
    with open(os.path.join(REPO, "rso", "slice001", "contract", "contract.json"), encoding="utf-8") as f:
        return EV.store_from_contract(json.load(f)["custody"])


def _cell(g, subject):
    nid = (R.make_node_id(EV.WORLD_SUBJECT, "CALIBRATION", "STANDARD") if subject == EV.WORLD_SUBJECT
           else R.make_node_id(subject, "BOUNDS", "STANDARD"))
    cell = dict(g.dicts[nid]["cell"])
    cell.pop("measurement", None)
    return cell


def claims_of(name, g):
    subjects = sorted({EV.parse_node_id(n)[0] for n in g.dicts} - {EV.WORLD_SUBJECT})
    obs = {}
    for n in g.dicts:
        s, pred, o, _w = EV.parse_node_id(n)
        if pred == "OBSERVER":
            obs.setdefault(s, set()).add(o)
    out = {"CL-CAL(STANDARD)": EV.make_claim("CL-CAL", cell=_cell(g, EV.WORLD_SUBJECT))}
    for s in subjects:
        out["CL-RET(%s)" % s] = EV.make_claim("CL-RET", s, observers=sorted(obs.get(s, ())), cell=_cell(g, s))
        if R.make_node_id(s, "TWIN_EQ", "STANDARD") in g.dicts:
            out["TWIN(%s)" % s] = EV.make_claim("TWIN", s, cell=_cell(g, s))
    out["CL-CUST(%s)" % name] = EV.make_claim("CL-CUST", bundle_id=name)
    return out


def consumer_for(g, store, first_check_utc, recs, blobs, anchors=None, bundle=None):
    bundle = bundle or EV.Bundle({n: R.Receipt.from_dict(d).canonical_bytes() for n, d in g.dicts.items()},
                                 g.traces, g.inventory, stage_records=recs, blobs=blobs,
                                 expected_table=next(iter(g.dicts.values()))["expected_answer"]["table"])
    anchors = anchors or EV.Anchors(g.manifest, "keeper")
    some = next(iter(g.dicts.values()))
    gate_versions = {r["instrument"]: r["version"] for r in recs if r["instrument"] in C.GATES}
    return C.Consumer(bundle, anchors, store, EV.Config(some["cell"]["revision"]), gate_versions, first_check_utc)


def decisions_real(first_check_utc, store=None):
    """{bundle name: (G0 tuple, {claim_id: decision}, custody)} with the real store."""
    recs, blobs = stage_records()
    store = store or live_store()
    out = {}
    for name in BUNDLES:
        g = load(name)
        cons = consumer_for(g, store, first_check_utc, recs, blobs)
        out[name] = (g, cons.decide_all(claims_of(name, g)), cons.custody)
    return out


def decisions_case(case_id, g0):
    """An E01-E05 case built on the real G0 (fixture store of the case; V8)."""
    recs, blobs = stage_records()
    base = F.real_base(g0, stage_records=recs, blobs=blobs)
    case = F.case_for(case_id, base)
    gate_versions = {r["instrument"]: r["version"] for r in recs if r["instrument"] in C.GATES}
    cons = C.Consumer(case.bundle, case.anchors, case.store, case.config, gate_versions, case.first_check)
    return cons.decide_all(case.claims), cons.custody


# ------------------------------------------------------------------------------------------------------------ rows

def verdict_fields(v):
    """A consumer verdict (receipt.make_verdict) in the expected table's spelling."""
    ex = v["execution"]["status"]
    a = v["authority"]
    auth = ("QUALIFIED@%s" % a["stage"]) if a["status"] == "QUALIFIED" else ("UNQUALIFIED: " + "; ".join(a["why"]))
    o = v.get("outcome") or {}
    f = {"execution": ex, "authority": auth, "outcome": o.get("value"), "reason": o.get("reason")}
    for k in ("statistic", "successes", "trials", "eligible_count", "applicable_count", "per_boundary"):
        if k in o:
            f[k] = o[k]
    if ex == "BLOCKED":
        f["missing"] = v["execution"].get("missing")
    return f


def _agg(fields):
    """All lines a plural scope names must agree; a disagreement is reported, never averaged."""
    if not fields:
        return None
    out = {}
    for k in set().union(*fields):
        vals = [json.dumps(f.get(k), sort_keys=True) for f in fields]
        out[k] = fields[0].get(k) if len(set(vals)) == 1 else "MIXED[%s]" % ", ".join(sorted(set(vals)))
    out["lines"] = len(fields)
    return out


def lines_of(decisions):
    for cid, d in sorted(decisions.items()):
        for ln in d["prerequisites"]:
            yield cid, ln


def resolve(predicate, scope, decisions, custody, case_subjects):
    """The consumer lines an expected (predicate, scope) names. Returns a verdict-fields dict or None."""
    pred = predicate
    if pred == "custody":
        return {"execution": "n/a", "authority": "n/a", "outcome": custody["status"],
                "reason": "; ".join(custody.get("why", [])) or None}
    picked = []
    sc = scope or ""
    if pred.startswith("P1-independent predicates"):
        want = _scope_subjects(sc, case_subjects)
        for cid, ln in lines_of(decisions):
            if ln["predicate"] in R.PREDICATE_NAMES_SET - {"BOUNDS", "CALIBRATION"} and "verdict" in ln                     and ln["scope"].split("/")[0] in want:
                picked.append(verdict_fields(ln["verdict"]))
        uniq = {json.dumps(f, sort_keys=True): f for f in picked}
        return _agg(list(uniq.values()))
    for cid, ln in lines_of(decisions):
        if ln["predicate"] != pred or "verdict" not in ln:
            continue
        if pred in C.GATES:
            if (sc in ("per claim", "every claim of G0") or (sc == "per CL-RET claim" and cid.startswith("CL-RET("))
                    or sc == cid or (sc == "the relabelled CL-RET claim" and cid == "CL-RET(REG)")):
                picked.append(verdict_fields(ln["verdict"]))
            continue
        subj, obs, world = (ln["scope"].split("/") + [None, None])[:3] if ln["scope"].count("/") == 2 else \
            (ln["scope"].split("/")[0], None, ln["scope"].split("/")[-1])
        want = _scope_subjects(sc, case_subjects)
        if want and subj not in want:
            continue
        o = _scope_observer(sc)
        if o and obs != o:
            continue
        picked.append(verdict_fields(ln["verdict"]))
    uniq = {}
    for f in picked:                                   # the same receipt line appears in several claims
        uniq[json.dumps(f, sort_keys=True)] = f
    return _agg(list(uniq.values()))


def _scope_subjects(scope, case_subjects):
    names = set(G0_SUBJECTS) | set(EXTRA_SUBJECTS) | {"WORLD"}
    toks = set(scope.replace("(", " ").replace(")", " ").replace(",", " ").split())
    if "STANDARD" in toks and not (toks & (names - {"WORLD"})):
        return {"WORLD"}
    hit = toks & names
    if "every" in toks and "G0" in toks:
        return set(G0_SUBJECTS)
    return hit or set(case_subjects)


def _scope_observer(scope):
    for o in ("BOOKKEEP", "NULL", "HEAL"):
        if ("%s)" % o) in scope.replace(" ", "") or (", %s" % o) in scope:
            return o
    return None


def claim_row(name, decisions):
    key = {"CL-RET(REG) with HEAL registered as used": "CL-RET(REG)", "TWIN(REG, REG-ONEHOT)": "TWIN(REG)",
           "TWIN(REG, REG-FLAT)": "TWIN(REG)", "TWIN(REG, LOSSY)": "TWIN(REG)",
           "CL-CUST(bundle)": None}.get(name, name)
    if key is None:
        key = next((c for c in decisions if c.startswith("CL-CUST(")), None)
    d = decisions.get(key)
    if d is None:
        return {"claim": name, "eligibility": None, "standing": None}
    return {"claim": name, "eligibility": d["eligibility"], "standing": d["standing"]}


def clocked_row(exp):
    """T02.CLOCKED: the consumer has no CLOCKED bundle (build_bundle is STANDARD-only); direct evaluation of the
    two registered instruments, with the A5 precondition applied as the contract states (register X01)."""
    cal = RU.calibration("CLOCKED")
    prim = {"execution": "RAN", "authority": "QUALIFIED@AUTHOR_TESTED", "outcome": cal["value"],
            "reason": cal.get("reason")}
    ret = {"execution": "RAN", "authority": "UNQUALIFIED: PRECONDITION:CALIBRATION", "outcome": "NOT_COMPARED_PATH",
           "reason": "direct path; RETENTION on CLOCKED is not evidence (A5)"}
    return {"id": exp["id"], "primary": dict({"predicate": "CALIBRATION", "scope": "CLOCKED"}, **prim),
            "other_verdicts": [dict({"predicate": v["predicate"], "scope": v.get("scope")}, **ret)
                               for v in exp.get("other_verdicts", [])],
            "claims": [{"claim": "CL-CAL(CLOCKED)", "eligibility": "NOT_ELIGIBLE" if cal["value"] == "FAIL" else
                        "ELIGIBLE", "standing": "UNMET" if cal["value"] == "FAIL" else "SATISFIED"}],
            "path": "direct"}


def bundle_for_case(cid):
    sub = cid.split(".")[1]
    if cid == "T07.HEAL":
        return "HEAL", ["REG"]
    if cid == "E06.REG_FLAT":
        return "FLAT", ["REG"]
    if cid == "E06.LOSSY":
        return "LOSSY", ["REG"]
    if sub in EXTRA_SUBJECTS:
        return "EXTRA", [sub]
    subj = {"REG_ONEHOT": "REG", "BOOKKEEP": "REG", "NULL": "REG"}.get(sub, sub)
    return "G0", [subj]


def _actual(v, decisions, custody, subjects):
    got = resolve(v["predicate"], v.get("scope"), decisions, custody, subjects) or {}
    return dict({"predicate": v["predicate"], "scope": v.get("scope")}, **got)


def actual_rows(expected, real, g0):
    rows = {}
    for cid, exp in sorted(expected.items()):
        if cid == "T02.CLOCKED":
            rows[cid] = clocked_row(exp)
            continue
        if cid.startswith(("E01.", "E02.", "E03.", "E04.", "E05.")):
            decisions, custody = decisions_case(cid, g0)
            subjects = sorted(G0_SUBJECTS)
            path = "case"
        else:
            name, subjects = bundle_for_case(cid)
            _g, decisions, custody = real[name]
            path = "bundle:" + name
        # Actual rows are built from consumer output ONLY: seeding them from the expected row would compare the
        # table with itself wherever the consumer is silent (a silent false MATCH).
        row = {"id": cid, "path": path,
               "primary": _actual(exp["primary"], decisions, custody, subjects),
               "other_verdicts": [_actual(v, decisions, custody, subjects) for v in exp.get("other_verdicts", [])],
               "claims": [claim_row(c["claim"], decisions) for c in exp.get("claims", [])]}
        rows[cid] = row
    return rows


def run_matrix(first_check_utc=None, out=None):
    first = first_check_utc or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    expected = M.load_expected()
    real = decisions_real(first)
    g0 = real["G0"][0]
    act = actual_rows(expected, real, g0)
    rep = M.compare(expected, act, M.exit_flags())
    out = out or os.path.join(OUT, "MATRIX")
    _write(out + ".json", _canon({"first_check_utc": first, "report": rep,
                                  "custody": {n: real[n][2] for n in BUNDLES}}))
    _write(out + ".txt", M.render(rep).encode("ascii", "replace"))
    return rep, act


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m rso.slice001.s2_run")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("produce")
    p.add_argument("--commit", required=True)
    p.add_argument("--ledger", required=True)
    m = sub.add_parser("matrix")
    m.add_argument("--first-check")
    a = ap.parse_args(argv)
    if a.cmd == "produce":
        print(json.dumps(produce(a.commit, a.ledger), sort_keys=True))
    else:
        rep, _ = run_matrix(a.first_check)
        print(M.render(rep))
        return 0 if rep["exit_ok"] else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
