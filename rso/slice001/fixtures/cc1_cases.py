"""C-009 CC1 fire cases: every C-004 survivor shape on G-INV run attribution, end to end (C-009-T011).

rso/binding/CONTRACT.md s3 CC1: S3.BROKEN.RUN_BORROW, S4.BROKEN.OBS_RUN_BORROW (+ edit X3), S4.PROBE.STALE_RUN,
R2 edit Y1 (world), R2.BROKEN.LATER_WINDOW_RUN, R2 OVERLAP_RUN, R2 FAILED_ROW_CITED, ARTIFACT_SWAP and
LAUNCH_SUBSTITUTION. Each case is RED on the FREEZE_R2 code (ad6b3fa96) where that code admits it and GREEN on
the C-009 code. The reviewers' committed builders are reused as they are (challenge/S4/closure_set/cases.py,
challenge/R2/closure_set/cases.py); the rest follow the reviewers' shapes. "_STRICT" variants leave exactly ONE
binding dimension wrong, so each BX2 check is pinned alone (an edit that weakens one check is killed by its
strict case even where a broader case still fails on another dimension).

Bases: "synthetic" (the fixture G0) and "s4" (the committed S4 G0, rso/slice001/s4/G0: real executions, 232-row
cumulative inventory) in the bound form of fixtures.evidence_cases.bind_legacy -- a FIXTURE until T020's fresh
produce, never custody evidence (V8). Everything here calls only APIs the FREEZE_R2 code also has, so the
same cases run on both codes:

    python -B -m rso.slice001.fixtures.cc1_cases --label C009 --out <rows.jsonl>

writes one JSONL row per (base, case): the target claim's G-INV value, reason and witness, the claim's
eligibility and standing, and whether every OTHER claim's decision is byte-identical to the base's G0.

Python >= 3.8, standard library only.
"""
import argparse
import base64
import copy
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time

from rso.slice001 import checker as C
from rso.slice001 import evidence as EV
from rso.slice001.fixtures import evidence_cases as F

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SUBSTITUTE = "fixture-launch-SUBSTITUTE"     # LAUNCH_SUBSTITUTION: the launch the bundle's run.json names
LATER = "fixture-launch-LATER"               # a later launch of the same node (LATER_WINDOW_STRICT)
PRESERVE = "rcpt:REG:PRESERVE:STANDARD"
ERASE = "rcpt:REG:ERASE:STANDARD"
BOOKKEEP = "rcpt:REG:OBSERVER:BOOKKEEP:STANDARD"
NULL = "rcpt:REG:OBSERVER:NULL:STANDARD"


def _s4():
    return importlib.import_module("rso.slice001.challenge.S4.closure_set.cases")


def _r2():
    return importlib.import_module("rso.slice001.challenge.R2.closure_set.cases")


def _terminal(rows):
    return rows + [{"kind": "TERMINAL", "row_count": len(rows)}]


def _runs(inv):
    return [dict(r) for r in inv[:-1]]


def _case(name, d, inv, base, run_id=None, traces=None):
    b = F._base(base)
    return F._case(name, F.make_bundle(d, traces=traces, inventory=inv, base=b, run_id=run_id), F.retained(d),
                   b.stage_rows(), b)


# --------------------------------------------------------------------------------------------------------
# C-004 survivor shapes

def run_borrow(base=None):
    """S3.BROKEN.RUN_BORROW (C-004-T042 F3): REG's PRESERVE receipt cites ERASE's run; its own row is absent."""
    b = F._base(base)
    d = b.dicts()
    old = d[PRESERVE]["execution"]["run_id"]
    d[PRESERVE]["execution"]["run_id"] = d[ERASE]["execution"]["run_id"]
    rows = [r for r in _runs(b.inventory(d)) if r["run_id"] != old]
    return _case("RUN_BORROW", d, _terminal(rows), base)


def obs_run_borrow(base=None):
    """S4.BROKEN.OBS_RUN_BORROW (C-004-T046 C2), the S4 reviewer's builder as committed."""
    return _s4().broken_obs_run_borrow(F._base(base))


def _rename_cited(base, victim, node_id):
    """The receipt cites its OWN row, whose node_id is rewritten (nothing else: digest, parent, status bound)."""
    b = F._base(base)
    d = b.dicts()
    rid = d[victim]["execution"]["run_id"]
    rows = [dict(r, node_id=node_id) if r["run_id"] == rid else r for r in _runs(b.inventory(d))]
    return d, _terminal(rows)


def x3_observer_strict(base=None):
    """Edit X3's shape alone: BOOKKEEP's receipt cites its own row, which names OBSERVER(REG, NULL)."""
    d, inv = _rename_cited(base, BOOKKEEP, NULL)
    return _case("X3_OBSERVER_STRICT", d, inv, base)


def y1_world(base=None):
    """R2 edit Y1's witness (world): PRESERVE(REG, STANDARD)'s receipt cites its own row, which names the same
    subject, predicate and observer in world TWINWORLD."""
    d, inv = _rename_cited(base, PRESERVE, "rcpt:REG:PRESERVE:TWINWORLD")
    return _case("Y1_WORLD", d, inv, base)


def stale_run(base=None):
    """S4.PROBE.STALE_RUN (C-004-T046): REG's PRESERVE receipt cites an EARLIER launch's run of its own node. On
    the s4 base this is the S4 reviewer's builder (the S2 row, still in the cumulative inventory); on the
    synthetic base the earlier launch's rows are prepended, as T046's fixture did."""
    b = F._base(base)
    if base is not None and getattr(b, "s2_dicts", None) is not None:
        return _s4().probe_stale_run(b, b.s2_dicts)
    d = b.dicts()
    early = [{"kind": "RUN", "run_id": "early/%s" % n, "node_id": n, "status": "COMPLETED",
              "launch_kind": "RECEIPT", "parent_run_id": "early"} for n in sorted(d)]
    rows = [F.launch_row("early")] + early + _runs(b.inventory(d))
    d[PRESERVE]["execution"]["run_id"] = "early/%s" % PRESERVE
    return _case("STALE_RUN", d, _terminal(rows), base)


def later_window_run(base=None):
    """R2.BROKEN.LATER_WINDOW_RUN, the R2 reviewer's builder as committed."""
    return _r2().broken_later_window_run(F._base(base))


def overlap_run(base=None):
    """R2.PROBE.OVERLAP_RUN, the R2 reviewer's builder as committed."""
    return _r2().probe_overlap_run(F._base(base))


def failed_row_cited(base=None):
    """R2.PROBE.FAILED_ROW_CITED, the R2 reviewer's builder as committed."""
    return _r2().probe_failed_row_cited(F._base(base))


def failed_row_strict(base=None):
    """FAILED_ROW_CITED with every other dimension bound: the receipt cites its own row, whose status is FAILED."""
    b = F._base(base)
    d = b.dicts()
    rid = d[PRESERVE]["execution"]["run_id"]
    rows = [dict(r, status="FAILED") if r["run_id"] == rid else r for r in _runs(b.inventory(d))]
    return _case("FAILED_ROW_STRICT", d, _terminal(rows), base)


def later_window_strict(base=None):
    """LATER_WINDOW_RUN with every other dimension bound: the cited row is COMPLETED, of the receipt's exact node,
    records the digest of the receipt as presented, and its launch (a TOP_LEVEL row, COMPLETED) is present --
    but it is a LATER launch, not the one the anchored manifest names (BX2 parent)."""
    b = F._base(base)
    d = b.dicts()
    rid = "%s/%s" % (LATER, PRESERVE)
    d[PRESERVE]["execution"]["run_id"] = rid
    rows = _runs(b.inventory(d)) + [
        F.launch_row(LATER),
        {"kind": "RUN", "run_id": rid, "node_id": PRESERVE, "status": "COMPLETED", "launch_kind": "RECEIPT",
         "parent_run_id": LATER, "receipt_sha256": F.receipt_digest(d[PRESERVE]),
         "start_utc": "2026-10-07T12:00:00Z", "end_utc": "2026-10-07T12:00:01Z"}]
    return _case("LATER_WINDOW_STRICT", d, _terminal(rows), base)


# --------------------------------------------------------------------------------------------------------
# New shapes (CONTRACT.md CC1)

def artifact_swap(base=None):
    """ARTIFACT_SWAP: after its run, REG's PRESERVE receipt is edited to name other output bytes (the trace
    swapped for another runtime's, receipt and manifest re-made to match). The inventory is the one written at
    the run, recording the digest of the receipt the run produced."""
    b = F._base(base)
    d = b.dicts()
    inv = b.inventory(d)                                  # written at the run, before the edit
    tr = b.traces(d)
    for out in d[PRESERVE]["outputs"]:
        x = b.fabricate(PRESERVE, out["role"])
        if x == tr[PRESERVE][out["role"]]:            # another runtime's identical bytes would swap nothing
            x = x[::-1] + b"\n"
        out["sha256"], out["length"] = hashlib.sha256(x).hexdigest(), len(x)
        tr[PRESERVE][out["role"]] = x
    return _case("ARTIFACT_SWAP", d, inv, base, traces=tr)


def launch_substitution(base=None):
    """LAUNCH_SUBSTITUTION: the bundle's run.json names another launch (present in the inventory, COMPLETED)
    than its anchored manifest; every receipt row is otherwise bound to the anchored launch."""
    b = F._base(base)
    d = b.dicts()
    rows = _runs(b.inventory(d)) + [F.launch_row(SUBSTITUTE)]
    return _case("LAUNCH_SUBSTITUTION", d, _terminal(rows), base, run_id=SUBSTITUTE)


# --------------------------------------------------------------------------------------------------------
# Sound controls (must stay PASS on both codes unless stated)

def g0(base=None):
    return F.g0(base)


def cumulative(base=None):
    """An earlier launch of every node (its own TOP_LEVEL row, bound rows) precedes this launch's rows; every
    receipt cites its own row. BX5: the earlier rows are provenance, never errors."""
    b = F._base(base)
    d = b.dicts()
    early = [{"kind": "RUN", "run_id": "early/%s" % n, "node_id": n, "status": "COMPLETED",
              "launch_kind": "RECEIPT", "parent_run_id": "early", "receipt_sha256": "0" * 64} for n in sorted(d)]
    rows = [F.launch_row("early")] + early + _runs(b.inventory(d))
    return _case("CUMULATIVE", d, _terminal(rows), base)


def foreign_unreported(base=None):
    """BX5: REG's PRESERVE receipt is absent and the only COMPLETED row of that node belongs to ANOTHER launch
    (this launch's row removed). RUN_UNREPORTED reads the anchored launch's rows only, so G-INV raises nothing
    (G-BIND blocks on the missing receipt). FREEZE_R2 reads every row: RUN_UNREPORTED on a historical row."""
    b = F._base(base)
    d = b.dicts()
    full = copy.deepcopy(d)
    own = d[PRESERVE]["execution"]["run_id"]
    rows = [F.launch_row("early"),
            {"kind": "RUN", "run_id": "early/%s" % PRESERVE, "node_id": PRESERVE, "status": "COMPLETED",
             "launch_kind": "RECEIPT", "parent_run_id": "early", "receipt_sha256": "0" * 64}]
    rows += [r for r in _runs(b.inventory(d)) if r["run_id"] != own]
    del d[PRESERVE]
    c = _case("FOREIGN_UNREPORTED", d, _terminal(rows), base)
    c.anchors = F.retained(full)
    return c


# (case id, builder, target claim, expected G-INV on the C-009 code: (value, reason, binding reasons))
RWR = "RECEIPT_WITHOUT_RUN:%s"
CASES = [
    ("SOUND.G0", g0, "CL-RET(REG)", ("PASS", None, None)),
    ("SOUND.CUMULATIVE", cumulative, "CL-RET(REG)", ("PASS", None, None)),
    ("SOUND.BX5.FOREIGN_UNREPORTED", foreign_unreported, "CL-RET(REG)", ("PASS", None, None)),
    ("S3.BROKEN.RUN_BORROW", run_borrow, "CL-RET(REG)",
     ("FAIL", RWR % PRESERVE, ["BIND_NODE_MISMATCH", "BIND_DIGEST_MISMATCH"])),
    ("S4.BROKEN.OBS_RUN_BORROW", obs_run_borrow, "CL-RET(REG)",
     ("FAIL", RWR % BOOKKEEP, ["BIND_NODE_MISMATCH", "BIND_DIGEST_MISMATCH"])),
    ("S4.EDIT.X3.OBSERVER_STRICT", x3_observer_strict, "CL-RET(REG)",
     ("FAIL", RWR % BOOKKEEP, ["BIND_NODE_MISMATCH"])),
    ("S4.PROBE.STALE_RUN", stale_run, "CL-RET(REG)",
     ("FAIL", RWR % PRESERVE, ["BIND_FOREIGN_LAUNCH", "BIND_DIGEST_MISSING"])),
    ("R2.EDIT.Y1.WORLD", y1_world, "CL-RET(REG)", ("FAIL", RWR % PRESERVE, ["BIND_NODE_MISMATCH"])),
    ("R2.BROKEN.LATER_WINDOW_RUN", later_window_run, "CL-RET(REG)",
     ("FAIL", RWR % PRESERVE, ["BIND_FOREIGN_LAUNCH", "BIND_DIGEST_MISSING"])),
    ("R2.BROKEN.LATER_WINDOW_STRICT", later_window_strict, "CL-RET(REG)",
     ("FAIL", RWR % PRESERVE, ["BIND_FOREIGN_LAUNCH"])),
    ("R2.PROBE.OVERLAP_RUN", overlap_run, "CL-RET(REG)",
     ("FAIL", RWR % PRESERVE, ["BIND_FOREIGN_LAUNCH", "BIND_DIGEST_MISSING"])),
    ("R2.PROBE.FAILED_ROW_CITED", failed_row_cited, "CL-RET(REG)",
     ("FAIL", RWR % PRESERVE, ["BIND_FOREIGN_LAUNCH", "BIND_STATUS:FAILED", "BIND_DIGEST_MISSING"])),
    ("R2.PROBE.FAILED_ROW_STRICT", failed_row_strict, "CL-RET(REG)",
     ("FAIL", RWR % PRESERVE, ["BIND_STATUS:FAILED"])),
    ("NEW.ARTIFACT_SWAP", artifact_swap, "CL-RET(REG)", ("FAIL", RWR % PRESERVE, ["BIND_DIGEST_MISMATCH"])),
    ("NEW.LAUNCH_SUBSTITUTION", launch_substitution, "CL-RET(REG)", ("FAIL", "LAUNCH_UNBOUND", [])),
]
BY_ID = {c[0]: c for c in CASES}


def expected(case_id):
    return BY_ID[case_id][3]


def g_inv_of(case, claim_id):
    """(value, reason, binding reasons or None) of G-INV for one claim; BLOCKED reads (BLOCKED, first missing)."""
    g = EV.g_inv(case.claims[claim_id], case.bundle, case.anchors)
    if g["execution"]["status"] == "BLOCKED":
        return "BLOCKED", g["execution"]["missing"][0], None
    o = g["outcome"]
    w = o.get("witness")
    bind = w.get("binding") if isinstance(w, dict) else None
    return o["value"], (o["reason"] if o["value"] == "FAIL" else None), bind


# --------------------------------------------------------------------------------------------------------
# Bases and the end-to-end driver

def load_g0(window, name="G0", root=ROOT):
    """A committed bundle (rso/slice001/<window>/<name>) as an s2_bundle.G0."""
    from rso.slice001 import s2_bundle as SB
    d = os.path.join(root, "rso", "slice001", window, name)

    def j(f):
        with open(os.path.join(d, f), "rb") as fh:
            return json.loads(fh.read())
    tr = {nid: {role: base64.b64decode(s) for role, s in t.items()} for nid, t in j("traces.json")["traces"].items()}
    with open(os.path.join(d, "MANIFEST.json"), "rb") as fh:
        manifest = fh.read()
    return SB.G0(j("receipts.json")["receipts"], tr, j("inventory.json")["rows"], manifest, j("run.json")["run_id"])


def s4_base(recs=(), blobs=None):
    """The committed S4 G0 in the bound form (bind_legacy), with the S2 G0's receipts for STALE_RUN."""
    base = F.real_base(F.bind_legacy(load_g0("s4")), stage_records=recs, blobs=blobs)
    base.s2_dicts = load_g0("s2").dicts
    return base


def decide(case, recs):
    gate_versions = {r["instrument"]: r["version"] for r in recs if r["instrument"] in C.GATES}
    cons = C.Consumer(case.bundle, case.anchors, case.store, case.config, gate_versions, case.first_check)
    return cons.decide_all(case.claims), cons.custody


def _line(decision, pred):
    for ln in decision["prerequisites"]:
        if ln["predicate"] == pred:
            v = ln["verdict"]
            o = v["outcome"] or {}
            return {"execution": v["execution"]["status"], "authority": v["authority"]["status"],
                    "value": o.get("value"), "reason": o.get("reason"), "witness": o.get("witness"),
                    "standing": v["standing"]}
    return None


def run(label, out_path, bases=("synthetic", "s4")):
    from rso.slice001 import s2_run as SR
    recs, blobs = SR.stage_records()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, stdout=subprocess.PIPE,
                            universal_newlines=True, timeout=120).stdout.strip()
    code = {p: hashlib.sha256(open(os.path.join(ROOT, *p.split("/")), "rb").read().replace(b"\r\n", b"\n"))
            .hexdigest() for p in ("rso/slice001/evidence.py", "rso/slice001/checker.py", "rso/slice001/receipt.py")}
    rows = [{"row": "header", "label": label, "root": ROOT, "head": commit, "code_lf_sha256": code,
             "python": sys.version.split()[0], "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}]
    c0 = time.process_time()
    for bname in bases:
        base = None if bname == "synthetic" else s4_base(recs, blobs)
        ref, _ = decide(F.g0(base), recs)
        for cid, build, claim, want in CASES:
            row = {"row": "case", "base": bname, "id": cid, "claim": claim, "expected_c009": list(want)}
            try:
                case = build(base)
                dec, cust = decide(case, recs)
                got = g_inv_of(case, claim)
                row.update({"g_inv": list(got), "g_inv_line": _line(dec[claim], "G-INV"),
                            "claim": claim, "eligibility": dec[claim]["eligibility"],
                            "standing": dec[claim]["standing"], "custody": cust["status"],
                            "others_identical_to_g0": sorted(
                                k for k in dec if k != claim and k in ref
                                and C.decision_bytes(dec[k]) == C.decision_bytes(ref[k])),
                            "others_differing_from_g0": sorted(
                                k for k in dec if k != claim and k in ref
                                and C.decision_bytes(dec[k]) != C.decision_bytes(ref[k])),
                            "admitted": got[0] == "PASS", "matches_c009": got == want})
            except Exception as e:                            # recorded, never hidden
                row["error"] = "%s: %s" % (type(e).__name__, e)
            rows.append(row)
    rows.append({"row": "terminal", "cases": sum(1 for r in rows if r["row"] == "case"),
                 "cpu_s": round(time.process_time() - c0, 3),
                 "ended_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    with open(out_path, "x", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bases", default="synthetic,s4")
    a = ap.parse_args(argv)
    rows = run(a.label, a.out, tuple(a.bases.split(",")))
    for r in rows:
        if r["row"] == "case":
            print("%-10s %-32s %-14s %s" % (r["base"], r["id"], "ERROR" if "error" in r else
                                            ("ADMITTED" if r["admitted"] else "REJECTED"),
                                            r.get("error") or r["g_inv"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
