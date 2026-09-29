"""Protocol-order selftest for holdout D2, v2 (after Odysseus's firewall audit FAIL: F1-F4, S1-S5).

  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_protocol [--write]

NEVER touches the hidden set, its key, the real allow-list or the real custody log.
- Everything runs in a temp directory outside every repository, on a THROWAWAY hidden set (public nonce, throwaway
  keys).
- The protocol records live in THROWAWAY git repositories that carry byte-exact copies of the audited code files.
- Real code runs throughout: protocol.check_gates, runner.FirewallRun (its isolation probe included), custody,
  evidence, allowlist, and entry.py (by path, in a subprocess).

POSITIVE: seal -> audit 1 PASS (allow-listed) -> Cosmos commitment (allow-listed) -> designation (account, run
parameters, nonce; allow-listed) -> key released -> ONE run in run_<nonce> (key deleted before the child starts; the
child's isolation probe finds nothing readable) -> close -> result seal -> reveal (re-verifies the chain) -> evidence
bundle.

NEGATIVE: every v1 refusal, plus v2 (each must be REFUSED):
- F1: a protocol/__init__.py (committed, or only in the working tree); loaded prometheus code not bound by the audit;
  AUDITED_FILES must be the COMPLETE import closure of runner + custody + evidence (checked in a fresh process);
- F2: a package with a .pyc member; np.fromfile / [open][0] flagged; a child that CAN open a secret path;
- F3: a short ref name; a tag named origin/main;
- F4: a record replaced through a merge;
- S1: a record missing from the allow-list; allowlist.add refusing a wrong sender or a message without the sha256;
- S2: a later FAIL audit supersedes an earlier PASS; a commitment made before the GOVERNING audit; the positive re-audit
  path (audit 2 PASS on changed code);
- S3: reveal of a run whose receipt chain was truncated;
- S4: a designated account equal to the custodian's; run parameters differing from the designation; a run directory
  that is not run_<nonce>;
- entry: entry.py refuses on the real repo (no governing audit yet); runner.main refuses without entry.py.

DEFECT CONTROLS (must make the matching test FAIL): ordering check removed; stale-code check removed; M2 block
removed; --full-history removed (F4).

--write saves SELFTEST_PROTOCOL.json (booleans only) beside this file.
"""
from __future__ import annotations

import os

if os.environ.get("COSMOS_BROKER") != "1":
    raise ImportError("holdout D2 protocol selftest: set COSMOS_BROKER=1 (broker only)")

import json
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

from prometheus.cosmos.c3_holdout_D2 import allowlist, custody, draw, evidence, protocol, runner, sealbox
from prometheus.cosmos.c3_holdout_D2.selftest_D2 import DUMMY_PREDICTOR, SMALL, make_package

HERE = Path(__file__).resolve().parent
REAL_REPO = HERE.parents[2]
RID = "selftest-runner"
ACCT = "c3runner"
HOST = socket.gethostname()
REF = "refs/heads/main"
NONCE = "c0ffee00" * 8
RUN_NONCE = "n0001"
PARAMS = {"predict_timeout": 300, "max_episode_steps": None, "certify_kwargs": SMALL}


def throwaway_set(tmp: Path, tag: str, n: int = 4) -> dict:
    fam = sealbox.src_sha_lf(draw.D_DIR / "medium.py")
    nonce = NONCE if tag == "main" else ("%02x" % len(tag)) * 32
    w, s, rej = draw.draw_hidden(nonce, n, draw.exposed_d_worlds())
    plain = draw.build_plaintext(w, s, nonce, "selftest", rej, fam)
    sd, pd = tmp / ("secrets_" + tag), tmp / ("public_" + tag)
    pd.mkdir(parents=True)
    m = draw.seal(plain, sd, pd, "selftest", n, fam)
    return {"manifest": pd / draw.MANIFEST_NAME, "enc": pd / draw.ENC_NAME, "secrets": sd, "m": m}


def _git(repo: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, text=True).stdout.strip()


class GateRepo:
    def __init__(self, path: Path, ts: dict):
        self.p, self.ts = path, ts
        self.al = path.parent / (path.name + "_ALLOWLIST.json")
        path.mkdir(parents=True)
        _git(path, "init", "-q", "-b", "main")
        _git(path, "config", "user.name", "selftest")
        _git(path, "config", "user.email", "selftest@invalid")
        _git(path, "config", "core.autocrlf", "false")
        for rel in protocol.AUDITED_FILES:
            dst = path / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REAL_REPO / rel, dst)
        self.commit("code")
        self.seal_commit = None

    def commit(self, msg):
        _git(self.p, "add", "-A")
        _git(self.p, "commit", "-q", "--allow-empty", "-m", msg)
        return _git(self.p, "rev-parse", "HEAD")

    def pins(self):
        return {"seal_commit": self.seal_commit, "spec_id": self.ts["m"]["spec_id"]}

    def seal(self):
        d = self.p / protocol.PKG_REL
        shutil.copyfile(self.ts["manifest"], d / "MANIFEST_D2.json")
        shutil.copyfile(self.ts["enc"], d / "hidden_D2.enc")
        self.seal_commit = self.commit("seal")

    def put(self, name, obj, commit=True):
        d = self.p / protocol.PROTO_REL
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        if commit:
            self.commit(name)

    def allow(self, role, name):
        b = subprocess.run(["git", "-C", str(self.p), "show", "%s:%s/%s" % (REF, protocol.PROTO_REL, name)],
                           capture_output=True, check=True).stdout
        data = json.loads(self.al.read_text()) if self.al.exists() else {"entries": []}
        data["entries"].append({"role": role, "record": name, "sha256": protocol.record_sha(b)})
        self.al.write_text(json.dumps(data))

    def audit(self, n=1, verdict="PASS", commit=True, allow=True):
        name = "FIREWALL_AUDIT_%d.json" % n
        self.put(name, {"format": protocol.AUDIT_FORMAT, "n": n, "verdict": verdict, "auditor": "selftest",
                        "spec_id": self.ts["m"]["spec_id"], "code_sha256": protocol.worktree_code_hashes(self.p)},
                 commit)
        if commit and allow:
            self.allow("AUDIT", name)

    def commitment(self, sha, commit=True, allow=True):
        self.put(protocol.COMMITMENT_FILE, {"format": protocol.COMMITMENT_FORMAT, "committer": "selftest",
                                            "spec_id": self.ts["m"]["spec_id"], "package_sha256": sha}, commit)
        if commit and allow:
            self.allow("COMMITMENT", protocol.COMMITMENT_FILE)

    def designate(self, runner_id=RID, host=HOST, account=ACCT, params=None, nonce=RUN_NONCE, allow=True):
        self.put(protocol.DESIGNATION_FILE, {"format": protocol.DESIGNATION_FORMAT, "runner_id": runner_id,
                                             "host": host, "account": account, "run_params": params or PARAMS,
                                             "run_nonce": nonce, "designated_by": "selftest",
                                             "spec_id": self.ts["m"]["spec_id"]})
        if allow:
            self.allow("DESIGNATION", protocol.DESIGNATION_FILE)

    def full(self, sha):
        self.seal()
        self.audit()
        self.commitment(sha)
        self.designate()
        return self


def gates(r, through="DESIGNATION", **kw):
    kw.setdefault("ref", REF)
    kw.setdefault("allowlist", r.al)
    kw.setdefault("pins", r.pins())
    kw.setdefault("host", HOST)
    try:
        protocol.check_gates(r.p, through, **kw)
        return "PASSED"
    except protocol.GateRefusal as e:
        return type(e).__name__


def try_open(tmp, r, pkg, sha, tag, runner_id=RID, account=ACCT, manifest=None, run_dir=None, timeout=None):
    """runner.open() with a key path that does not exist: a GateRefusal proves the gate ran before the key."""
    out = (tmp / "runs" / tag / (run_dir or ("run_" + RUN_NONCE)))
    out.parent.mkdir(parents=True, exist_ok=True)
    rr = runner.FirewallRun(manifest or r.ts["manifest"], r.ts["enc"], tmp / "no_such_key.hex", pkg, sha, out,
                            runner_id=runner_id, gate_repo=r.p, gate_ref=REF, certify_kwargs=SMALL,
                            predict_timeout=timeout or PARAMS["predict_timeout"], account=account,
                            allowlist=r.al, gate_pins=r.pins(), verify_loaded=False, secret_paths=(), write_probe_paths=())
    try:
        rr.open()
        return "OPENED"
    except Exception as e:                                                   # noqa: BLE001
        return type(e).__name__ + ("" if not (out / "receipts.jsonl").exists() else "+RECEIPTS_WRITTEN")


def runner_gate_cases(tmp, ts, pkg, sha):
    k = [0]

    def R():
        k[0] += 1
        return GateRepo(tmp / "repos" / ("r%02d" % k[0]), ts)

    c = {}
    r = R().full(sha)
    c["control_all_gates_pass"] = (try_open(tmp, r, pkg, sha, "ctl"), ("FileNotFoundError", "OSError"))
    r = R(); r.seal(); r.commitment(sha); r.designate()
    c["no_audit"] = (try_open(tmp, r, pkg, sha, "noaudit"), ("AuditMissing",))
    r = R(); r.seal(); r.audit(verdict="FAIL"); r.commitment(sha); r.designate()
    c["audit_fail"] = (try_open(tmp, r, pkg, sha, "afail"), ("AuditNotPass",))
    r = R().full(sha)
    with open(r.p / protocol.PKG_REL / "runner.py", "a", encoding="utf-8") as f:
        f.write("\n# edited after the audit\n")
    c["code_changed_after_audit_worktree"] = (try_open(tmp, r, pkg, sha, "stale_wt"), ("AuditStale",))
    r.commit("edit runner after audit")
    c["code_changed_after_audit_committed"] = (try_open(tmp, r, pkg, sha, "stale_c"), ("AuditStale",))
    r = R().full(sha)
    with open(r.p / "prometheus/cosmos/c3/probe.py", "a", encoding="utf-8") as f:     # F1: probe.py now bound
        f.write("\n# edited after the audit\n")
    c["F1_probe_py_changed_after_audit"] = (try_open(tmp, r, pkg, sha, "stale_probe"), ("AuditStale",))
    r = R(); r.seal(); r.commitment(sha); r.audit(); r.designate()
    c["commitment_before_audit"] = (try_open(tmp, r, pkg, sha, "cm_first"), ("RecordOrderViolation",))
    r = R(); r.seal(); r.audit(commit=False); r.commitment(sha, commit=False); r.commit("both")
    r.allow("AUDIT", "FIREWALL_AUDIT_1.json"); r.allow("COMMITMENT", protocol.COMMITMENT_FILE); r.designate()
    c["commitment_same_commit_as_audit"] = (try_open(tmp, r, pkg, sha, "cm_same"), ("RecordOrderViolation",))
    r = R(); r.audit(); r.seal(); r.commitment(sha); r.designate()
    c["audit_before_seal"] = (try_open(tmp, r, pkg, sha, "au_first"), ("RecordOrderViolation",))
    r = R(); r.seal(); r.audit(); r.designate()
    c["no_commitment"] = (try_open(tmp, r, pkg, sha, "nocm"), ("CommitmentMissing",))
    r = R(); r.seal(); r.audit(); r.commitment(sha, commit=False)
    c["commitment_only_in_worktree"] = (try_open(tmp, r, pkg, sha, "cm_wt"), ("CommitmentMissing",))
    r = R().full(sha); r.commitment("0" * 64, allow=False)
    c["commitment_rewritten"] = (try_open(tmp, r, pkg, sha, "cm_rw"), ("RecordRewritten",))
    other = ("0" if sha[0] != "0" else "1") + sha[1:]
    r = R(); r.seal(); r.audit(); r.commitment(other); r.designate()
    c["package_not_the_committed_one"] = (try_open(tmp, r, pkg, sha, "wrongpkg"), ("PackageNotCommitted",))
    r = R(); r.seal(); r.audit(); r.commitment(sha)
    c["no_designation"] = (try_open(tmp, r, pkg, sha, "nods"), ("DesignationMissing",))
    r = R().full(sha)
    c["wrong_runner_id"] = (try_open(tmp, r, pkg, sha, "wrid", runner_id="x"), ("RunnerNotDesignated",))
    r = R(); r.seal(); r.audit(); r.commitment(sha); r.designate(host="OTHERHOST")
    c["wrong_host"] = (try_open(tmp, r, pkg, sha, "whost"), ("RunnerNotDesignated",))
    r = R(); r.seal(); r.audit(); r.commitment(sha); r.designate(host="SPECTREX5")
    c["m2_designated"] = (try_open(tmp, r, pkg, sha, "m2"), ("ForbiddenHost",))
    r = R().full(sha)
    c["running_on_m2"] = (gates(r, host="SPECTREX5"), ("ForbiddenHost",))
    other_ts = throwaway_set(tmp, "other", 2)
    r = R().full(sha)
    c["manifest_not_the_sealed_one"] = (try_open(tmp, r, pkg, sha, "swap", manifest=other_ts["manifest"]),
                                        ("HiddenSetMismatch",))
    # ---- v2
    r = R().full(sha)
    (r.p / protocol.PROTO_REL / "__init__.py").write_text("# shadow\n")
    c["F1_protocol_init_py_worktree"] = (gates(r), ("RecordDirPolluted",))
    r.commit("shadow")
    c["F1_protocol_init_py_committed"] = (gates(r), ("RecordDirPolluted",))
    r = R().full(sha)
    c["F1_unbound_loaded_code"] = (gates(r, verify_loaded=True), ("UnboundCodeLoaded",))
    r = R().full(sha)
    c["F3_short_ref"] = (gates(r, ref="main"), ("AmbiguousRef",))
    _git(r.p, "tag", "origin/main")
    c["F3_tag_shadows_origin_main"] = (gates(r), ("AmbiguousRef",))
    r = R(); r.seal(); r.audit()
    _git(r.p, "branch", "side")
    r.commitment(sha)
    _git(r.p, "checkout", "-q", "side")
    r.put(protocol.COMMITMENT_FILE, {"format": protocol.COMMITMENT_FORMAT, "committer": "forger",
                                     "spec_id": ts["m"]["spec_id"], "package_sha256": other})
    _git(r.p, "checkout", "-q", "main")
    subprocess.run(["git", "-C", str(r.p), "merge", "-q", "-X", "theirs", "--no-edit", "side"], capture_output=True)
    r.allow("COMMITMENT", protocol.COMMITMENT_FILE); r.designate()
    c["F4_record_replaced_through_merge"] = (gates(r), ("RecordRewritten",))
    f4_repo = r
    r = R(); r.seal(); r.audit(); r.commitment(sha, allow=False); r.designate()
    c["S1_commitment_not_allowlisted"] = (gates(r), ("NotAllowListed",))
    r = R(); r.seal(); r.audit(allow=False); r.commitment(sha); r.designate()
    c["S1_audit_not_allowlisted"] = (gates(r), ("AuditMissing",))    # v3: a non-allow-listed audit is IGNORED
    r = R(); r.seal(); r.audit(1)
    with open(r.p / protocol.PKG_REL / "runner.py", "a", encoding="utf-8") as f:
        f.write("\n# a later, re-audited change\n")
    r.commit("change")
    r.audit(2)
    r.commitment(sha); r.designate()
    c["S2_reaudit_path_positive"] = (gates(r), ("PASSED",))
    r = R(); r.seal(); r.audit(1); r.audit(2, verdict="FAIL"); r.commitment(sha); r.designate()
    c["S2_later_FAIL_supersedes_PASS"] = (gates(r), ("AuditNotPass",))
    r = R(); r.seal(); r.audit(1); r.commitment(sha); r.audit(2); r.designate()
    c["S2_commitment_before_governing_audit"] = (gates(r), ("RecordOrderViolation",))
    r = R(); r.seal(); r.audit(); r.commitment(sha); r.designate(account=protocol.CUSTODIAN_ACCOUNT)
    c["S4_account_is_custodian"] = (gates(r), ("RunnerNotDesignated",))
    r = R().full(sha)
    c["S4_run_params_differ"] = (try_open(tmp, r, pkg, sha, "params", timeout=299), ("RunParamsMismatch",))
    c["S4_run_dir_not_nonce"] = (try_open(tmp, r, pkg, sha, "rundir", run_dir="run_other"), ("RunParamsMismatch",))
    c["S4_wrong_account"] = (try_open(tmp, r, pkg, sha, "acct", account="someone"), ("RunnerNotDesignated",))
    return {name: {"got": got, "ok": got in want} for name, (got, want) in c.items()}, f4_repo


def closure_checks():
    """F1: AUDITED_FILES must be the complete prometheus import closure of runner + custody + evidence, measured in a
    FRESH process; a negative control imports one extra (unaudited) module and must be detected."""
    code = ("import os,sys,json;os.environ['COSMOS_BROKER']='1';sys.path.insert(0,%r);"
            "import prometheus.cosmos.c3_holdout_D2.runner, prometheus.cosmos.c3_holdout_D2.custody, "
            "prometheus.cosmos.c3_holdout_D2.evidence%s;"
            "from prometheus.cosmos.c3_holdout_D2 import protocol as P;"
            "print(json.dumps(sorted(set(P.loaded_closure(%r))-set(P.AUDITED_FILES))))")
    res = {}
    for tag, extra in (("complete", ""), ("neg_extra_module", ", prometheus.cosmos.c3_holdout_D2.selftest_D2")):
        p = subprocess.run([sys.executable, "-c", code % (str(REAL_REPO), extra, str(REAL_REPO))],
                           capture_output=True, text=True)
        res[tag] = json.loads(p.stdout.strip().splitlines()[-1]) if p.returncode == 0 else ["<error>"]
    return {"F1_audited_files_cover_import_closure": res["complete"] == [],
            "F1_closure_detects_extra_module": len(res["neg_extra_module"]) > 0}, res


def package_checks(tmp):
    import io
    import zipfile
    res = {}
    buf = io.BytesIO()
    meta = {"format": runner.PACKAGE_FORMAT, "entry": "predictor.py", "adjudication": {},
            "intervention": {"knob": "p_decay", "to": 1.0}}
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("package.json", json.dumps(meta))
        z.writestr("predictor.py", DUMMY_PREDICTOR)
        z.writestr("helper.pyc", b"\x00" * 16)
    pkg = tmp / "pyc.zip"
    pkg.write_bytes(buf.getvalue())
    try:
        runner.load_package(pkg, sealbox.sha256_file(pkg), tmp / "pyc_out")
        res["F2_pyc_member_refused"] = False
    except runner.PackageInvalid:
        res["F2_pyc_member_refused"] = True
    for tag, src in (("fromfile", "import numpy as np\ndef predict(s,t,seed):\n    return np.fromfile('x')\n"),
                     ("open_alias", "def predict(s,t,seed):\n    f=[open][0]\n    return f('x')\n")):
        res["F2_audit_flags_" + tag] = bool(runner.audit_source(src, tag + ".py"))
    return res


def entry_checks():
    env = dict(os.environ, C3D2_NO_FETCH="1")
    env.pop("C3D2_ENTRY", None)
    p = subprocess.run([sys.executable, str(HERE / "entry.py"), "runner", "--help"], capture_output=True, text=True,
                       env=env)
    refused_real = p.returncode != 0 and "REFUSED" in (p.stdout + p.stderr)
    saved = os.environ.pop("C3D2_ENTRY", None)
    try:
        runner.main(["--package", "x", "--package-sha256", "0" * 64, "--key", "x", "--runner-id", RID])
        main_guard = False
    except runner.RunnerRefusal:
        main_guard = True
    finally:
        if saved is not None:
            os.environ["C3D2_ENTRY"] = saved
    return {"entry_refuses_real_repo_without_audit": refused_real, "runner_main_refuses_without_entry": main_guard}


def end_to_end(tmp, ts, pkg, sha):
    out = {}
    repo = GateRepo(tmp / "repos" / "e2e", ts).full(sha)
    log = tmp / "custody.jsonl"
    cu = custody.Custody(repo=repo.p, ref=REF, secrets_dir=ts["secrets"], log=log, host=HOST, allowlist=repo.al,
                         pins=repo.pins(), verify_loaded=False)

    def refused(fn, *a):
        try:
            fn(*a)
            return "NOT_REFUSED"
        except (protocol.GateRefusal, custody.CustodyRefusal, evidence.EvidenceRefusal) as e:
            return type(e).__name__

    pre = GateRepo(tmp / "repos" / "pre", ts)
    pre.seal()
    cu_pre = custody.Custody(repo=pre.p, ref=REF, secrets_dir=ts["secrets"], log=tmp / "cpre.jsonl", host=HOST,
                             allowlist=pre.al, pins=pre.pins(), verify_loaded=False)
    out["release_before_audit_refused"] = refused(cu_pre.release_key, RID, tmp / "rel_pre") == "AuditMissing"
    out["release_into_git_refused"] = refused(cu.release_key, RID, repo.p / "k") == "CustodyRefusal"
    rel = tmp / "released"
    out["release_key_ok"] = cu.release_key(RID, rel)["event"] == "KEY_RELEASED"
    out["release_twice_refused"] = refused(cu.release_key, RID, tmp / "rel2") == "CustodyRefusal"
    # v3: once-only rests on git. Commit the KEY_RELEASED record custody wrote, then clear the custody log:
    # a second release must STILL be refused.
    out["v3_key_released_record_written"] = (repo.p / protocol.PROTO_REL / protocol.KEY_RELEASED_FILE).exists()
    repo.commit("key released record")
    log.write_text("", encoding="utf-8")
    out["v3_release_refused_from_git_after_log_cleared"] = refused(cu.release_key, RID, tmp / "rel3") == "CustodyRefusal"
    # F2: a child that CAN open a secret path is refused before any world is served
    fake = tmp / "fake_secret.hex"
    fake.write_text("00")
    keyc = tmp / "keyc"
    keyc.mkdir()
    shutil.copyfile(rel / custody.KEY_NAME, keyc / custody.KEY_NAME)
    iso = tmp / "runs" / "iso" / ("run_" + RUN_NONCE)
    iso.parent.mkdir(parents=True)
    r0 = runner.FirewallRun(ts["manifest"], ts["enc"], keyc / custody.KEY_NAME, pkg, sha, iso, runner_id=RID,
                            gate_repo=repo.p, gate_ref=REF, certify_kwargs=SMALL, predict_timeout=300, account=ACCT,
                            allowlist=repo.al, gate_pins=repo.pins(), verify_loaded=False, delete_key=True,
                            secret_paths=(fake,), write_probe_paths=())
    r0.open()
    try:
        r0.predict_all()
        out["F2_child_that_can_read_a_secret_refused"] = False
    except runner.ChildNotIsolated:
        out["F2_child_that_can_read_a_secret_refused"] = True
    fake.unlink()
    # the real, single run
    run_dir = tmp / "runs" / "e2e" / ("run_" + RUN_NONCE)
    run_dir.parent.mkdir(parents=True)
    r = runner.FirewallRun(ts["manifest"], ts["enc"], rel / custody.KEY_NAME, pkg, sha, run_dir, runner_id=RID,
                           gate_repo=repo.p, gate_ref=REF, certify_kwargs=SMALL, predict_timeout=300, account=ACCT,
                           allowlist=repo.al, gate_pins=repo.pins(), verify_loaded=False, delete_key=True,
                           secret_paths=(fake,), write_probe_paths=(), extra_probe_paths=[str(ts["secrets"] / "nonexistent")])
    r.open()
    out["key_deleted_after_read"] = not (rel / custody.KEY_NAME).exists()
    r.predict_all(); r.seal_predictions(); r.certify_all(); res = r.close()
    out["run_closed"] = res["chain_head"] == r.receipts.head and r.receipts.records[0]["body"]["run_nonce"] == RUN_NONCE
    rev0 = tmp / "revealed_early"
    out["reveal_before_result_seal_refused"] = refused(cu.reveal, run_dir, rev0) == "ResultNotSealed" and not rev0.exists()
    rec_path = repo.p / protocol.PROTO_REL / protocol.RESULT_SEAL_FILE
    cu.result_seal_record(run_dir, rec_path)
    repo.commit("result seal")
    out["v3_reveal_refused_result_seal_not_allowlisted"] = refused(cu.reveal, run_dir, tmp / "rev_nal") == "NotAllowListed"
    repo.allow("RESULT_SEAL", protocol.RESULT_SEAL_FILE)
    out["result_seal_carries_nonce"] = json.loads(rec_path.read_text())["run_nonce"] == RUN_NONCE
    tam = tmp / "runs" / "tam" / ("run_" + RUN_NONCE)
    shutil.copytree(run_dir, tam)
    lines = (tam / "receipts.jsonl").read_text(encoding="utf-8").splitlines()
    (tam / "receipts.jsonl").write_text("\n".join(lines[:-2] + lines[-1:]) + "\n", encoding="utf-8", newline="\n")
    out["S3_reveal_truncated_chain_refused"] = refused(cu.reveal, tam, tmp / "rev_tam") == "CustodyRefusal"
    revd = tmp / "revealed"
    out["reveal_ok"] = cu.reveal(run_dir, revd)["verify_reveal"]["all_ok"]
    b = evidence.build(run_dir, tmp / "bundle", revd, repo.p, REF, HOST, allowlist=repo.al, pins=repo.pins(),
                       verify_loaded=False)
    rv = json.loads((tmp / "bundle" / "REVEAL_VERIFY.json").read_text())
    out["evidence_bundle_ok"] = bool(rv["all_ok"] and rv.get("redraw_from_nonce_ok") and b["chain_head"] == res["chain_head"])
    return out


def allowlist_checks(tmp, ts, sha):
    r = GateRepo(tmp / "repos" / "al", ts)
    r.seal(); r.audit(allow=False)
    name = "FIREWALL_AUDIT_1.json"
    b = subprocess.run(["git", "-C", str(r.p), "show", "%s:%s/%s" % (REF, protocol.PROTO_REL, name)],
                       capture_output=True, check=True).stdout
    h = protocol.record_sha(b)
    al = tmp / "al.json"
    allowlist.REPO = r.p
    res = {}
    for tag, msg, want_ok in (("good", {"sender": "Odysseus", "subject": "PASS " + h, "body": ""}, True),
                              ("wrong_sender", {"sender": "Cosmos", "subject": h, "body": ""}, False),
                              ("no_sha", {"sender": "Odysseus", "subject": "PASS", "body": "looks fine"}, False)):
        try:
            allowlist.add("AUDIT", name, 1, REF, path=al, message=msg)
            ok = True
        except SystemExit:
            ok = False
        res["S1_allowlist_" + tag] = ok == want_ok
    allowlist.REPO = REAL_REPO
    return res


def defect_controls(tmp, ts, pkg, sha, f4_repo):
    res = {}
    saved = (protocol._strict_ancestor, protocol.worktree_code_hashes, protocol.code_hashes,
             set(protocol.FORBIDDEN_HOSTS), protocol._record_history)
    try:
        protocol._strict_ancestor = lambda repo, a, b: True
        r = GateRepo(tmp / "repos" / "dc1", ts); r.seal(); r.commitment(sha); r.audit(); r.designate()
        res["DefectNoOrderCheck[commitment_before_audit]"] = gates(r) != "RecordOrderViolation"
        protocol._strict_ancestor = saved[0]
        r = GateRepo(tmp / "repos" / "dc2", ts).full(sha)
        bound = json.loads((r.p / protocol.PROTO_REL / "FIREWALL_AUDIT_1.json").read_text())["code_sha256"]
        with open(r.p / protocol.PKG_REL / "runner.py", "a", encoding="utf-8") as f:
            f.write("\n# edited\n")
        r.commit("edit")
        protocol.worktree_code_hashes = lambda repo: dict(bound)
        protocol.code_hashes = lambda repo, ref: dict(bound)
        res["DefectNoStaleCheck[code_changed_after_audit]"] = gates(r) != "AuditStale"
        protocol.worktree_code_hashes, protocol.code_hashes = saved[1], saved[2]
        protocol.FORBIDDEN_HOSTS.clear()
        r = GateRepo(tmp / "repos" / "dc3", ts); r.seal(); r.audit(); r.commitment(sha); r.designate(host="SPECTREX5")
        res["DefectNoM2Block[m2_designated_and_running_on_m2]"] = gates(r, host="SPECTREX5") == "PASSED"
        protocol.FORBIDDEN_HOSTS.update(saved[3])

        def plain_log(repo, ref, rel):                                    # the v1 behaviour Odysseus broke
            p = protocol._git(repo, "log", "--raw", "--no-abbrev", "--format=C %H %P", ref, "--", rel)
            out, cur, npar = [], None, 0
            for line in p.stdout.splitlines():
                if line.startswith("C "):
                    parts = line.split(); cur, npar = parts[1], len(parts) - 2
                elif line.startswith(":") and cur:
                    f = line.split("\t", 1)[0].split()
                    out.append((cur, npar, f[4], f[3]))
            return out
        protocol._record_history = plain_log
        res["DefectNoFullHistory[F4_record_replaced_through_merge]"] = gates(f4_repo) != "RecordRewritten"
    finally:
        protocol._strict_ancestor, protocol.worktree_code_hashes, protocol.code_hashes = saved[0], saved[1], saved[2]
        protocol.FORBIDDEN_HOSTS.clear()
        protocol.FORBIDDEN_HOSTS.update(saved[3])
        protocol._record_history = saved[4]
    return res


def v3_checks(tmp, ts, pkg, sha):
    """v3: DEF-HARM-D2-001 (real history), merge carrying the sealed blob, unauthenticated later FAIL ignored,
    write probe, import guard / verified source loader."""
    res = {}
    try:
        protocol.check_gates(REAL_REPO, "SEAL")
        res["v3_real_history_seal_passes"] = True
    except protocol.GateRefusal as e:
        res["v3_real_history_seal_passes"] = False
        res["v3_real_history_seal_reason"] = str(e)[:120]
    r = GateRepo(tmp / "repos" / "v3merge", ts)
    _git(r.p, "branch", "side")
    _git(r.p, "checkout", "-q", "side")
    r.seal()                                               # seal on a side branch ...
    _git(r.p, "checkout", "-q", "main")
    (r.p / "unrelated.txt").write_text("x")
    r.commit("unrelated")
    subprocess.run(["git", "-C", str(r.p), "merge", "-q", "--no-ff", "--no-edit", "side"], capture_output=True)
    res["v3_integration_merge_carrying_sealed_blob_passes"] = gates(r, "SEAL") == "PASSED"
    r = GateRepo(tmp / "repos" / "v3fail", ts); r.seal(); r.audit(1); r.audit(2, verdict="FAIL", allow=False)
    r.commitment(sha); r.designate()
    res["v3_unauthenticated_later_FAIL_ignored"] = gates(r) == "PASSED"
    r = GateRepo(tmp / "repos" / "v3pass", ts); r.seal(); r.audit(1, verdict="FAIL"); r.audit(2, allow=False)
    r.commitment(sha); r.designate()
    res["v3_unauthenticated_later_PASS_ignored"] = gates(r) == "AuditNotPass"
    # write probe: a child that can APPEND to a protected path is refused
    r = GateRepo(tmp / "repos" / "v3wp", ts).full(sha)
    kd = tmp / "v3wp_key"
    kd.mkdir()
    shutil.copyfile(ts["secrets"] / "hidden_D2.key.hex", kd / "k.hex")
    wf = tmp / "writable_receipt.jsonl"
    wf.write_text("")
    out = tmp / "runs" / "v3wp" / ("run_" + RUN_NONCE)
    out.parent.mkdir(parents=True)
    rr = runner.FirewallRun(ts["manifest"], ts["enc"], kd / "k.hex", pkg, sha, out, runner_id=RID, gate_repo=r.p,
                            gate_ref=REF, certify_kwargs=SMALL, predict_timeout=300, account=ACCT, allowlist=r.al,
                            gate_pins=r.pins(), verify_loaded=False, delete_key=True, secret_paths=(),
                            write_probe_paths=(wf,))
    rr.open()
    try:
        rr.predict_all()
        res["v3_child_that_can_append_receipts_refused"] = False
    except runner.ChildNotIsolated:
        res["v3_child_that_can_append_receipts_refused"] = True
    # import guard + verified source loader
    from prometheus.cosmos.c3_holdout_D2 import entry
    try:
        entry.AuditedImportGuard({}).find_spec("prometheus.cosmos.c3.task")
        res["v3_import_guard_refuses_unbound"] = False
    except ImportError:
        res["v3_import_guard_refuses_unbound"] = True
    mod = tmp / "v3mod.py"
    mod.write_bytes(b"X = 1\n")
    good = entry._VerifiedSourceLoader("v3mod", str(mod), entry.lf_sha(b"X = 1\n"))
    res["v3_loader_compiles_verified_source"] = good.get_code("v3mod") is not None
    bad = entry._VerifiedSourceLoader("v3mod", str(mod), "0" * 64)
    try:
        bad.get_code("v3mod")
        res["v3_loader_refuses_changed_source"] = False
    except ImportError:
        res["v3_loader_refuses_changed_source"] = True
    return res


def run() -> dict:
    with tempfile.TemporaryDirectory(prefix="c3D2_protocol_") as t:
        tmp = Path(t)
        assert not runner.inside_git_repo(tmp)
        (tmp / "runs").mkdir()
        ts = throwaway_set(tmp, "main")
        pkg = tmp / "dummy.zip"
        sha = make_package(pkg, DUMMY_PREDICTOR)
        gate_cases, f4_repo = runner_gate_cases(tmp, ts, pkg, sha)
        closure, closure_raw = closure_checks()
        pk = package_checks(tmp)
        en = entry_checks()
        al = allowlist_checks(tmp, ts, sha)
        e2e = end_to_end(tmp, ts, pkg, sha)
        v3 = v3_checks(tmp, ts, pkg, sha)
        dcs = defect_controls(tmp, ts, pkg, sha, f4_repo)
    checks = {"gate[%s]" % k: v["ok"] for k, v in gate_cases.items()}
    for grp in (closure, pk, en, al, {k: v for k, v in v3.items() if not k.endswith("_reason")}):
        checks.update(grp)
    checks.update({"e2e[%s]" % k: bool(v) for k, v in e2e.items()})
    res = {"checks": checks, "gate_outcomes": {k: v["got"] for k, v in gate_cases.items()},
           "closure_extras": closure_raw, "defect_controls_must_be_true": dcs,
           "hidden_set_or_key_touched": False, "all_checks_true": all(checks.values()),
           "all_defect_controls_true": all(dcs.values())}
    res["selftest_pass"] = bool(res["all_checks_true"] and res["all_defect_controls_true"])
    return res


if __name__ == "__main__":
    out = run()
    txt = json.dumps(out, indent=1, sort_keys=True)
    if "--write" in sys.argv:
        (HERE / "SELFTEST_PROTOCOL.json").write_text(txt + "\n", encoding="utf-8", newline="\n")
    print(txt)
    sys.exit(0 if out["selftest_pass"] else 1)
