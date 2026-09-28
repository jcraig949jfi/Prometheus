"""Protocol-order selftest for holdout D2 (operator directive "COSMOS C3 SUCCESSOR-SEAL", 2026-09-28, s3).

  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.selftest_protocol [--write]

NEVER touches the hidden set, its key or the real custody log. Everything runs in a temp directory outside
every repository. The material is a THROWAWAY hidden set drawn from a public nonce, with throwaway keys. The
protocol records live in THROWAWAY git repositories that carry byte-exact copies of the audited code files.
Real code runs throughout: protocol.check_gates, runner.FirewallRun, custody.Custody, evidence.build.

POSITIVE: seal -> audit PASS -> Cosmos commitment -> designation -> key released to the designated runner ->
predict -> seal predictions -> certify -> close -> public result seal -> reveal -> evidence bundle with
verify_reveal all true (including the redraw from the nonce).

NEGATIVE (each must be REFUSED, and with no side effect):
- runner refusals (the key path given does not exist, so a refusal proves the gate ran BEFORE the key was touched):
  missing audit, failing audit, code changed after the audit (committed or in the working tree), commitment
  before the audit or in the same commit, audit before the seal, missing commitment, a record only in the
  working tree, a record rewritten after it was recorded, wrong package, missing designation, wrong runner id,
  wrong host, M2 designated, running on M2, a manifest other than the sealed one;
- custody: key release before the audit, twice, or into a git repository; result seal of an unclosed run;
  reveal before the result seal, or with a tampered RESULT.json;
- evidence: bundle before the result seal, or with tampered receipts.

DEFECT CONTROLS (must make the matching test FAIL, i.e. the refusal disappears): ordering check removed;
stale-code check removed; M2 host block removed.

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

from prometheus.cosmos.c3_holdout_D2 import custody, draw, evidence, protocol, runner, sealbox, verify_reveal
from prometheus.cosmos.c3_holdout_D2.selftest_D2 import DUMMY_PREDICTOR, SMALL, make_package

HERE = Path(__file__).resolve().parent
REAL_REPO = HERE.parents[2]
RID = "selftest-runner"
HOST = socket.gethostname()
NONCE = "c0ffee00" * 8                                                # throwaway, public


# ------------------------------------------------------------------ throwaway material
def throwaway_set(tmp: Path, tag: str, n: int = 4) -> dict:
    fam = sealbox.src_sha_lf(draw.D_DIR / "medium.py")
    w, s, rej = draw.draw_hidden(NONCE if tag == "main" else ("%02x" % len(tag)) * 32, n, draw.exposed_d_worlds())
    plain = draw.build_plaintext(w, s, NONCE if tag == "main" else ("%02x" % len(tag)) * 32, "selftest", rej, fam)
    sd, pd = tmp / ("secrets_" + tag), tmp / ("public_" + tag)
    pd.mkdir(parents=True)
    m = draw.seal(plain, sd, pd, "selftest", n, fam)
    return {"manifest": pd / draw.MANIFEST_NAME, "enc": pd / draw.ENC_NAME, "secrets": sd, "m": m}


def _git(repo: Path, *a: str) -> None:
    subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)


class GateRepo:
    """A throwaway git repository holding copies of the audited code, the seal and protocol records."""

    def __init__(self, path: Path, ts: dict):
        self.p, self.ts = path, ts
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

    def commit(self, msg: str) -> None:
        _git(self.p, "add", "-A")
        _git(self.p, "commit", "-q", "--allow-empty", "-m", msg)

    def seal(self, commit=True):
        d = self.p / protocol.PKG_REL
        shutil.copyfile(self.ts["manifest"], d / "MANIFEST_D2.json")
        shutil.copyfile(self.ts["enc"], d / "hidden_D2.enc")
        if commit:
            self.commit("seal")

    def put(self, name: str, obj: dict, commit=True):
        d = self.p / protocol.PROTO_REL
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        if commit:
            self.commit(name)

    def audit(self, verdict="PASS", commit=True):
        self.put(protocol.AUDIT_FILE, {"format": protocol.AUDIT_FORMAT, "verdict": verdict, "auditor": "selftest",
                                       "spec_id": self.ts["m"]["spec_id"],
                                       "code_sha256": protocol.worktree_code_hashes(self.p)}, commit)

    def commitment(self, sha: str, commit=True):
        self.put(protocol.COMMITMENT_FILE, {"format": protocol.COMMITMENT_FORMAT, "committer": "selftest",
                                            "spec_id": self.ts["m"]["spec_id"], "package_sha256": sha}, commit)

    def designate(self, runner_id=RID, host=HOST, commit=True):
        self.put(protocol.DESIGNATION_FILE, {"format": protocol.DESIGNATION_FORMAT, "runner_id": runner_id,
                                             "host": host, "designated_by": "selftest",
                                             "spec_id": self.ts["m"]["spec_id"]}, commit)

    def full(self, sha: str):
        self.seal()
        self.audit()
        self.commitment(sha)
        self.designate()
        return self


def try_open(tmp: Path, repo: GateRepo, pkg: Path, sha: str, tag: str, runner_id=RID, manifest=None) -> str:
    """Name of the exception runner.open raised. The key path does not exist: a GateRefusal proves the gate ran
    before the key was touched; FileNotFoundError/OSError means every gate passed."""
    out = tmp / "runs" / ("open_" + tag)
    r = runner.FirewallRun(manifest or repo.ts["manifest"], repo.ts["enc"], tmp / "no_such_key.hex", pkg, sha, out,
                           runner_id=runner_id, gate_repo=repo.p, gate_ref="main", certify_kwargs=SMALL)
    try:
        r.open()
        return "OPENED"
    except Exception as e:                                                   # noqa: BLE001
        return type(e).__name__ + ("" if not (out / "receipts.jsonl").exists() else "+RECEIPTS_WRITTEN")


# ------------------------------------------------------------------ runner-gate negatives
def runner_gate_cases(tmp: Path, ts: dict, pkg: Path, sha: str) -> dict:
    k = [0]

    def R() -> GateRepo:
        k[0] += 1
        return GateRepo(tmp / "repos" / ("r%02d" % k[0]), ts)

    cases = {}
    r = R().full(sha)
    cases["control_all_gates_pass"] = (try_open(tmp, r, pkg, sha, "ctl"), ("FileNotFoundError", "OSError"))
    r = R(); r.seal(); r.commitment(sha); r.designate()
    cases["no_audit"] = (try_open(tmp, r, pkg, sha, "noaudit"), ("AuditMissing",))
    r = R(); r.seal(); r.audit("FAIL"); r.commitment(sha); r.designate()
    cases["audit_fail"] = (try_open(tmp, r, pkg, sha, "afail"), ("AuditNotPass",))
    r = R().full(sha)
    with open(r.p / protocol.PKG_REL / "runner.py", "a", encoding="utf-8") as f:
        f.write("\n# edited after the audit\n")
    cases["code_changed_after_audit_worktree"] = (try_open(tmp, r, pkg, sha, "stale_wt"), ("AuditStale",))
    r.commit("edit runner after audit")
    cases["code_changed_after_audit_committed"] = (try_open(tmp, r, pkg, sha, "stale_c"), ("AuditStale",))
    r = R(); r.seal(); r.commitment(sha); r.audit(); r.designate()
    cases["commitment_before_audit"] = (try_open(tmp, r, pkg, sha, "cm_first"), ("RecordOrderViolation",))
    r = R(); r.seal(); r.audit(commit=False); r.commitment(sha, commit=False); r.commit("both"); r.designate()
    cases["commitment_same_commit_as_audit"] = (try_open(tmp, r, pkg, sha, "cm_same"), ("RecordOrderViolation",))
    r = R(); r.audit(); r.seal(); r.commitment(sha); r.designate()
    cases["audit_before_seal"] = (try_open(tmp, r, pkg, sha, "au_first"), ("RecordOrderViolation",))
    r = R(); r.seal(); r.audit(); r.designate()
    cases["no_commitment"] = (try_open(tmp, r, pkg, sha, "nocm"), ("CommitmentMissing",))
    r = R(); r.seal(); r.audit(); r.commitment(sha, commit=False)
    cases["commitment_only_in_worktree"] = (try_open(tmp, r, pkg, sha, "cm_wt"), ("CommitmentMissing",))
    r = R().full(sha); r.commitment("0" * 64)
    cases["commitment_rewritten"] = (try_open(tmp, r, pkg, sha, "cm_rw"), ("RecordRewritten",))
    other = ("0" if sha[0] != "0" else "1") + sha[1:]
    r = R(); r.seal(); r.audit(); r.commitment(other); r.designate()
    cases["package_not_the_committed_one"] = (try_open(tmp, r, pkg, sha, "wrongpkg"), ("PackageNotCommitted",))
    r = R(); r.seal(); r.audit(); r.commitment(sha)
    cases["no_designation"] = (try_open(tmp, r, pkg, sha, "nods"), ("DesignationMissing",))
    r = R().full(sha)
    cases["wrong_runner_id"] = (try_open(tmp, r, pkg, sha, "wrongrid", runner_id="someone-else"),
                                ("RunnerNotDesignated",))
    r = R(); r.seal(); r.audit(); r.commitment(sha); r.designate(host="OTHERHOST")
    cases["wrong_host"] = (try_open(tmp, r, pkg, sha, "wronghost"), ("RunnerNotDesignated",))
    r = R(); r.seal(); r.audit(); r.commitment(sha); r.designate(host="SPECTREX5")
    cases["m2_designated"] = (try_open(tmp, r, pkg, sha, "m2des"), ("ForbiddenHost",))
    r = R().full(sha)
    try:
        protocol.check_gates(r.p, "DESIGNATION", ref="main", package_sha256=sha, runner_id=RID, host="SPECTREX5")
        got = "PASSED"
    except protocol.GateRefusal as e:
        got = type(e).__name__
    cases["running_on_m2"] = (got, ("ForbiddenHost",))
    other_ts = throwaway_set(tmp, "other", 2)
    r = R().full(sha)
    cases["manifest_not_the_sealed_one"] = (try_open(tmp, r, pkg, sha, "swap", manifest=other_ts["manifest"]),
                                            ("HiddenSetMismatch",))
    return {name: {"got": got, "ok": got in want} for name, (got, want) in cases.items()}


# ------------------------------------------------------------------ positive end to end + custody/evidence negatives
def end_to_end(tmp: Path, ts: dict, pkg: Path, sha: str) -> dict:
    out = {}
    repo = GateRepo(tmp / "repos" / "e2e", ts).full(sha)
    log = tmp / "custody.jsonl"
    cu = custody.Custody(repo=repo.p, ref="main", secrets_dir=ts["secrets"], log=log, host=HOST)

    def refused(fn, *a) -> str:
        try:
            fn(*a)
            return "NOT_REFUSED"
        except (protocol.GateRefusal, custody.CustodyRefusal, evidence.EvidenceRefusal) as e:
            return type(e).__name__

    # custody negatives BEFORE the audit (separate repo, same secrets)
    pre = GateRepo(tmp / "repos" / "pre", ts)
    pre.seal()
    cu_pre = custody.Custody(repo=pre.p, ref="main", secrets_dir=ts["secrets"], log=tmp / "custody_pre.jsonl", host=HOST)
    d0 = tmp / "released_pre"
    out["release_before_audit_refused"] = (refused(cu_pre.release_key, RID, d0) == "AuditMissing"
                                           and not (d0 / custody.KEY_NAME).exists())
    out["release_into_git_refused"] = refused(cu.release_key, RID, repo.p / "k") == "CustodyRefusal"
    out["release_wrong_runner_refused"] = refused(cu.release_key, "someone-else", tmp / "rel_x") == "RunnerNotDesignated"
    rel = tmp / "released"
    ev = cu.release_key(RID, rel)
    out["release_key_ok"] = ev["event"] == "KEY_RELEASED" and (rel / custody.KEY_NAME).exists()
    out["release_twice_refused"] = refused(cu.release_key, RID, tmp / "released2") == "CustodyRefusal"

    # a predict-only run cannot be result-sealed
    po = tmp / "runs" / "predict_only"
    r0 = runner.FirewallRun(ts["manifest"], ts["enc"], rel / custody.KEY_NAME, pkg, sha, po, runner_id=RID,
                            gate_repo=repo.p, gate_ref="main", certify_kwargs=SMALL, predict_timeout=300)
    r0.open(); r0.predict_all(); r0.seal_predictions()
    out["result_seal_unclosed_refused"] = refused(cu.result_seal_record, po, tmp / "rs_x.json") == "CustodyRefusal"

    # the real path
    run_dir = tmp / "runs" / "e2e"
    r = runner.FirewallRun(ts["manifest"], ts["enc"], rel / custody.KEY_NAME, pkg, sha, run_dir, runner_id=RID,
                           gate_repo=repo.p, gate_ref="main", certify_kwargs=SMALL, predict_timeout=300)
    r.open(); r.predict_all(); r.seal_predictions(); r.certify_all(); res = r.close()
    opened = r.receipts.records[0]["body"]
    out["run_closed"] = res["chain_head"] == r.receipts.head and opened["runner_id"] == RID \
        and set(opened["protocol_gates"]) >= {"seal_commit", "audit_commit", "commitment_commit", "designation_commit"}

    rev0 = tmp / "revealed_early"
    out["reveal_before_result_seal_refused"] = (refused(cu.reveal, run_dir, rev0) == "ResultNotSealed"
                                                and not rev0.exists())
    out["evidence_before_result_seal_refused"] = refused(evidence.build, run_dir, tmp / "bundle_early", None,
                                                         repo.p, "main", HOST) == "ResultNotSealed"
    rec_path = repo.p / protocol.PROTO_REL / protocol.RESULT_SEAL_FILE
    cu.result_seal_record(run_dir, rec_path)
    repo.commit("result seal")
    out["result_seal_public_fields_only"] = set(json.loads(rec_path.read_text(encoding="utf-8"))) == {
        "format", "spec_id", "package_sha256", "chain_head", "result_sha256", "n_receipts", "sealed_by", "utc"}

    # tampered copies must be refused
    tam = tmp / "runs" / "tampered"
    shutil.copytree(run_dir, tam)
    (tam / "RESULT.json").write_text((tam / "RESULT.json").read_text(encoding="utf-8").replace('"NONE"', '"PASSIVE"', 1),
                                     encoding="utf-8", newline="\n")
    out["reveal_tampered_result_refused"] = refused(cu.reveal, tam, tmp / "revealed_tam") == "CustodyRefusal"
    tam2 = tmp / "runs" / "tampered_receipts"
    shutil.copytree(run_dir, tam2)
    lines = (tam2 / "receipts.jsonl").read_text(encoding="utf-8").splitlines()
    (tam2 / "receipts.jsonl").write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8", newline="\n")
    out["evidence_tampered_receipts_refused"] = refused(evidence.build, tam2, tmp / "bundle_tam", None,
                                                        repo.p, "main", HOST) == "EvidenceRefusal"

    revd = tmp / "revealed"
    rv = cu.reveal(run_dir, revd)
    out["reveal_ok"] = rv["verify_reveal"]["all_ok"]
    out["reveal_twice_refused"] = refused(cu.reveal, run_dir, tmp / "revealed2") == "CustodyRefusal"
    b = evidence.build(run_dir, tmp / "bundle", revd, repo.p, "main", HOST)
    rvj = json.loads((tmp / "bundle" / "REVEAL_VERIFY.json").read_text(encoding="utf-8"))
    idx = json.loads((tmp / "bundle" / "INDEX.json").read_text(encoding="utf-8"))
    out["evidence_bundle_ok"] = bool(rvj["all_ok"] and rvj.get("redraw_from_nonce_ok")
                                     and all(sealbox.sha256_file(tmp / "bundle" / k) == v for k, v in idx.items())
                                     and b["chain_head"] == res["chain_head"])
    events = [json.loads(x)["event"] for x in log.read_text(encoding="utf-8").splitlines()]
    out["custody_log_records_refusals"] = events.count("REFUSED") >= 4 and "KEY_RELEASED" in events \
        and "REVEALED" in events
    return out


# ------------------------------------------------------------------ defect controls
def defect_controls(tmp: Path, ts: dict, pkg: Path, sha: str) -> dict:
    """Each injected defect must make the matching negative test stop refusing (True = the test can fail)."""
    res = {}
    saved = (protocol._strict_ancestor, protocol.worktree_code_hashes, protocol.code_hashes, set(protocol.FORBIDDEN_HOSTS))
    try:
        protocol._strict_ancestor = lambda repo, a, b: True
        r = GateRepo(tmp / "repos" / "dc1", ts); r.seal(); r.commitment(sha); r.audit(); r.designate()
        res["DefectNoOrderCheck[commitment_before_audit]"] = try_open(tmp, r, pkg, sha, "dc1") \
            not in ("RecordOrderViolation",)
        protocol._strict_ancestor = saved[0]

        r = GateRepo(tmp / "repos" / "dc2", ts).full(sha)
        bound = json.loads((r.p / protocol.PROTO_REL / protocol.AUDIT_FILE).read_text(encoding="utf-8"))["code_sha256"]
        with open(r.p / protocol.PKG_REL / "runner.py", "a", encoding="utf-8") as f:
            f.write("\n# edited after the audit\n")
        r.commit("edit")
        protocol.worktree_code_hashes = lambda repo: dict(bound)
        protocol.code_hashes = lambda repo, ref: dict(bound)
        res["DefectNoStaleCheck[code_changed_after_audit]"] = try_open(tmp, r, pkg, sha, "dc2") != "AuditStale"
        protocol.worktree_code_hashes, protocol.code_hashes = saved[1], saved[2]

        protocol.FORBIDDEN_HOSTS.clear()
        r = GateRepo(tmp / "repos" / "dc3", ts); r.seal(); r.audit(); r.commitment(sha); r.designate(host="SPECTREX5")
        try:
            protocol.check_gates(r.p, "DESIGNATION", ref="main", package_sha256=sha, runner_id=RID, host="SPECTREX5")
            got = "PASSED"
        except protocol.GateRefusal as e:
            got = type(e).__name__
        res["DefectNoM2Block[m2_designated_and_running_on_m2]"] = got == "PASSED"
    finally:
        protocol._strict_ancestor, protocol.worktree_code_hashes, protocol.code_hashes = saved[0], saved[1], saved[2]
        protocol.FORBIDDEN_HOSTS.clear()
        protocol.FORBIDDEN_HOSTS.update(saved[3])
    return res


def run() -> dict:
    with tempfile.TemporaryDirectory(prefix="c3D2_protocol_") as t:
        tmp = Path(t)
        assert not runner.inside_git_repo(tmp)
        (tmp / "runs").mkdir()
        ts = throwaway_set(tmp, "main")
        pkg = tmp / "dummy.zip"
        sha = make_package(pkg, DUMMY_PREDICTOR)
        gates = runner_gate_cases(tmp, ts, pkg, sha)
        e2e = end_to_end(tmp, ts, pkg, sha)
        dcs = defect_controls(tmp, ts, pkg, sha)
    checks = {"runner_gate[%s]" % k: v["ok"] for k, v in gates.items()}
    checks.update({"e2e[%s]" % k: bool(v) for k, v in e2e.items()})
    res = {"checks": checks, "runner_gate_outcomes": {k: v["got"] for k, v in gates.items()},
           "defect_controls_must_be_true": dcs, "hidden_set_or_key_touched": False,
           "all_checks_true": all(checks.values()), "all_defect_controls_true": all(dcs.values())}
    res["selftest_pass"] = bool(res["all_checks_true"] and res["all_defect_controls_true"])
    return res


if __name__ == "__main__":
    out = run()
    txt = json.dumps(out, indent=1, sort_keys=True)
    if "--write" in sys.argv:
        (HERE / "SELFTEST_PROTOCOL.json").write_text(txt + "\n", encoding="utf-8", newline="\n")
    print(txt)
    sys.exit(0 if out["selftest_pass"] else 1)
