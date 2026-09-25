"""T-INFRA: the Cycle-9 runner, adjudicator, report and report audit, under failure
injection. A miniature manifest (a few real bundles of each hypothesis, 12 epochs)
exercises the real code:

  1. end to end: run -> adjudicate -> report -> audit PASS;
  2. KILL: a run killed abruptly mid-drain (os._exit after 4 stored results), then resumed
     in a fresh process, yields bundle files whose scientific content is byte-identical to
     an uninterrupted run's;
  3. FREEZE REFUSAL: verify_freeze refuses with no FREEZE.json, and refuses a frozen
     protocol hash that does not match the source;
  4. ERROR PATH: a job that raises is retried exactly once (identical inputs), then
     recorded; its bundle stays incomplete and is reported, not dropped;
  5. AUDIT NEGATIVE CONTROLS: six injected report defects must each FAIL the audit.

Run:  python tests/test_infra_c9.py     Exit 0 iff every check holds.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import adjudicate_c9 as ADJ      # noqa: E402
import bundles as BD             # noqa: E402
import manifest as M             # noqa: E402
import report_audit_c9 as AUD    # noqa: E402
import report_c9 as REP          # noqa: E402
import run_campaign as RUN       # noqa: E402

EPOCHS = 12


def mini_manifest():
    h1 = M.h1_bundles(2)
    h2, _ = M.h2_bundles(1)
    h3 = M.h3_bundles(1)
    return {"manifest_hash": "MINI", "bundles": h1 + h2[:2] + h3[:1]}


DRIVER = r'''
import json, sys
sys.path.insert(0, %(root)r)
import run_campaign as RUN
m = json.load(open(%(man)r))
RUN.run(m, %(obs)r, workers=3, max_epochs=%(ep)d, stop_after=%(stop)s, log=lambda *a: None)
'''


def drive(man_path, obs, stop=None):
    code = DRIVER % {"root": str(ROOT), "man": str(man_path), "obs": str(obs), "ep": EPOCHS,
                     "stop": "None" if stop is None else str(stop)}
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                          cwd=str(ROOT)).returncode


def content(obs):
    store = BD.BundleStore(pathlib.Path(obs) / "bundles")
    return {bid: BD.content_bytes(store.get(bid)) for bid in store.all_ids()}


def main():
    ok = True
    rows = []

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        rows.append({"check": name, "pass": bool(cond), "detail": detail})
        print("%-6s %-58s %s" % ("PASS" if cond else "FAIL", name, detail))

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="c9infra_"))
    try:
        man = mini_manifest()
        mp_ = tmp / "man.json"
        mp_.write_text(json.dumps(man))
        n_jobs = sum(len(b["arms"]) for b in man["bundles"])

        # 1 + 2: uninterrupted vs killed-and-resumed
        full, kill = tmp / "full", tmp / "kill"
        rc_full = drive(mp_, full)
        rc_kill = drive(mp_, kill, stop=4)
        partial = len(content(kill))
        rc_res = drive(mp_, kill)
        cf, ck = content(full), content(kill)
        chk("uninterrupted run drains", rc_full == 0 and len(cf) == len(man["bundles"]),
            "rc=%s bundles=%d/%d jobs=%d" % (rc_full, len(cf), len(man["bundles"]), n_jobs))
        chk("kill injection actually killed mid-drain", rc_kill == 3 and 0 < partial,
            "rc=%s bundle files after kill=%d" % (rc_kill, partial))
        chk("resume completes and is byte-identical", rc_res == 0 and cf == ck,
            "identical=%s" % (cf == ck))
        # re-running a completed observatory schedules nothing
        before = content(full)
        drive(mp_, full)
        chk("re-run of a drained observatory is a no-op", content(full) == before)

        adj = ADJ.adjudicate(full, man)
        (full / "ADJUDICATION_C9.json").write_text(json.dumps(adj, default=str))
        prov = {"protocol_hash": "PROTO-TEST", "manifest_hash": "MINI"}
        (full / "REPORT_C9.md").write_text(REP.render(adj, prov), encoding="utf-8")
        base = AUD.audit(full, man, {"protocol_hash": "PROTO-TEST"})
        chk("audit PASS on the honest report", all(c["pass"] for c in base),
            "%d checks" % len(base))
        chk("H2/H3 incomplete bundles are reported, not dropped",
            adj["hypotheses"]["H2"]["n_bundles"] == 2 and adj["hypotheses"]["H3"]["n_bundles"] == 1)

        # 3 freeze refusal
        try:
            RUN.verify_freeze(tmp)
            chk("verify_freeze refuses without FREEZE.json", False)
        except RUN.FreezeError as e:
            chk("verify_freeze refuses without FREEZE.json", True, str(e)[:60])
        fz = tmp / "fz"
        fz.mkdir()
        (fz / "FREEZE.json").write_text(json.dumps({"protocol_hash": "0" * 64, "manifest_hash": "x"}))
        (fz / "CALIBRATION.json").write_text(json.dumps({"gate": "PASS"}))
        try:
            RUN.verify_freeze(fz)
            chk("verify_freeze refuses a drifted protocol hash", False)
        except RUN.FreezeError as e:
            chk("verify_freeze refuses a drifted protocol hash", "drifted" in str(e), str(e)[:60])

        # 4 error path: an ACTUAL_GENOME implant with no bytes raises inside world
        bad = json.loads(json.dumps(man))
        bad["bundles"] = [b for b in bad["bundles"] if b["hypothesis_id"] == "H2"][:1]
        for a in bad["bundles"][0]["arms"]:
            if a["arm"] == "B_reimplant_actual":
                a["kwargs"] = {"implant": "ACTUAL_GENOME"}
        bp = tmp / "bad.json"
        bp.write_text(json.dumps(bad))
        eo = tmp / "err"
        rc = drive(bp, eo)
        errs = [json.loads(l) for l in (eo / "ERRORS.jsonl").read_text().splitlines()] if (eo / "ERRORS.jsonl").exists() else []
        st = BD.BundleStore(eo / "bundles")
        ids = st.all_ids()
        incomplete = bool(ids) and not st.get(ids[0]).is_complete()
        chk("failing job: exactly one identical retry, then recorded",
            rc == 0 and len(errs) == 2 and errs[0]["retry_scheduled"] and not errs[1]["retry_scheduled"],
            "errors=%d" % len(errs))
        chk("failing job leaves its bundle INCOMPLETE (other arms stored)", incomplete)

        # 5 audit negative controls
        good = (full / "REPORT_C9.md").read_text(encoding="utf-8")
        blk = json.loads(good.split(AUD.BEGIN, 1)[1].split(AUD.END, 1)[0])

        def inject(name, text):
            (full / "REPORT_C9.md").write_text(text, encoding="utf-8")
            res = AUD.audit(full, man, {"protocol_hash": "PROTO-TEST"})
            caught = not all(c["pass"] for c in res)
            chk("audit catches: " + name, caught)
            (full / "REPORT_C9.md").write_text(good, encoding="utf-8")

        def with_block(mut):
            b = json.loads(json.dumps(blk))
            mut(b)
            return good.replace(json.dumps(blk, indent=1, sort_keys=True),
                                json.dumps(b, indent=1, sort_keys=True))
        inject("H1 M sign flipped", with_block(lambda b: b["H1"].__setitem__("M", -(b["H1"]["M"] or 0.0) - 0.5)))
        sp0 = sorted(blk["H2"]["per_specimen"])[0]
        inject("H2 per-specimen count altered",
               with_block(lambda b: b["H2"]["per_specimen"][sp0].__setitem__("B_reaching", 99)))
        inject("H3 verdict word changed in prose only",
               good.replace("Verdict **%s** over" % blk["H3"]["verdict"], "Verdict **RESERVOIR_SUPPORTED** over"))
        inject("prose-only number added", good.replace("## H1 -- cue gating", "## H1 -- cue gating\n\nEffect 0.8765."))
        inject("machine block removed", good.split(AUD.BEGIN)[0] + good.split(AUD.END)[1])
        row0 = next(l for l in good.splitlines() if l.startswith("| " + sp0 + " |"))
        inject("H2 table row altered in prose only", good.replace(row0, row0.rsplit("|", 2)[0] + "| 7 |"))
        # stale report: a raw bundle changes after the report was written
        store = BD.BundleStore(full / "bundles")
        h1ids = [RUN.spec_of(b).bundle_id for b in man["bundles"] if b["hypothesis_id"] == "H1"]
        p = store.path_for(h1ids[0])
        orig = p.read_text()
        d = json.loads(orig)
        d["results"]["gate_on_cost_vm"]["held_max_final"] = 0.99
        p.write_text(json.dumps(d))
        res = AUD.audit(full, man, {"protocol_hash": "PROTO-TEST"})
        chk("audit catches: stale report (raw bundle changed after report)",
            not all(c["pass"] for c in res))
        p.write_text(orig)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    (ROOT / "T_INFRA_RECEIPT.json").write_text(json.dumps({"gate": "T-INFRA", "ok": ok, "checks": rows}, indent=1))
    print("T-INFRA:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
