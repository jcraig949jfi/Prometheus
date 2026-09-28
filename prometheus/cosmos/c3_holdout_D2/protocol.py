"""Holdout D2 protocol gates (operator directive "COSMOS C3 SUCCESSOR-SEAL", 2026-09-28, s3).

The order below is ENFORCED, not advised. The runner (runner.py), key release (custody.py) and the Harmonia
evidence bundle (evidence.py) all call `check_gates` and refuse on any failure:

  1. SEAL         the commit that added hidden_D2.enc + MANIFEST_D2.json is on the reference branch, and the files
                  there still hash to the sealed values (ciphertext sha256, spec_id).
  2. AUDIT        protocol/FIREWALL_AUDIT.json, verdict PASS, written by the independent auditor, bound to the
                  spec_id AND to the sha256 of every file whose behaviour the audit covered (AUDITED_FILES). If any
                  of those files changed after the audit, the audit is STALE and nothing runs.
  3. COMMITMENT   protocol/PREDICTION_COMMITMENT.json: Cosmos's frozen prediction package, identified by its
                  sha256, bound to the spec_id. The package run later must hash to exactly this value.
  4. DESIGNATION  protocol/RUNNER_DESIGNATION.json: the one runner (id + host) allowed to execute D. The host must
                  not be M2 (SPECTREX5), Cosmos's machine.
  5. RESULT_SEAL  protocol/RESULT_SEAL.json: after the run closes, ONLY the receipt-chain head and sha256(RESULT.json)
                  are made public. Results stay on M1 outside git. Reveal of the hidden set (custody.py reveal) and
                  the Harmonia evidence bundle (evidence.py) require this record and a run that matches it.
  Ordering: every record is read from the COMMITTED TREE of a git ref (default origin/main), never from the
  working tree, and each record file must have been added in exactly one commit and never modified. The seal
  commit must be a strict ancestor of the audit commit, and the audit commit a strict ancestor of both the
  commitment commit and the designation commit, and both of those strict ancestors of the result-seal commit. So a prediction committed before the audit, an audit recorded
  before the seal, or a record rewritten after the fact is refused.

Cosmos's "predictions" in the D contract are an executable package that predicts each hidden world through the
public System interface. "Cosmos commits predictions" (directive s3.3) therefore means Cosmos publicly fixes
that package's sha256 (record 3). The per-world predictions the package produces are then sealed in the runner's
receipt chain BEFORE any world is certified (runner.py phases PREDICT -> SEAL -> CERTIFY).

Nothing in this module reads secrets.
"""
from __future__ import annotations

import json
import socket
import subprocess
from pathlib import Path
from typing import Dict, Optional

from prometheus.cosmos.c3_holdout_D2 import sealbox

HERE = Path(__file__).resolve().parent
PKG_REL = "prometheus/cosmos/c3_holdout_D2"
PROTO_REL = PKG_REL + "/protocol"
FORBIDDEN_HOSTS = {"SPECTREX5"}               # M2, Cosmos's machine: never holds the key, never runs D
DEFAULT_REF = "origin/main"

AUDIT_FILE = "FIREWALL_AUDIT.json"
COMMITMENT_FILE = "PREDICTION_COMMITMENT.json"
DESIGNATION_FILE = "RUNNER_DESIGNATION.json"
RESULT_SEAL_FILE = "RESULT_SEAL.json"
RESULT_SEAL_FORMAT = "c3-D2-result-seal/1"
AUDIT_FORMAT = "c3-D2-firewall-audit/1"
COMMITMENT_FORMAT = "c3-D2-prediction-commitment/1"
DESIGNATION_FORMAT = "c3-D2-runner-designation/1"

# Every file whose behaviour the firewall audit covers (repo-relative). Changing any of them after the audit
# makes the audit stale.
AUDITED_FILES = (
    PKG_REL + "/__init__.py", PKG_REL + "/sealbox.py", PKG_REL + "/draw.py", PKG_REL + "/runner.py",
    PKG_REL + "/protocol.py", PKG_REL + "/custody.py", PKG_REL + "/evidence.py",
    PKG_REL + "/verify_reveal.py", PKG_REL + "/firewall_check.py",
    "prometheus/cosmos/c3/certify.py", "prometheus/cosmos/c3/system.py", "prometheus/cosmos/c3/task.py",
    "prometheus/cosmos/c3_holdout_D/medium.py",
)


class GateRefusal(Exception):
    """Base: the protocol order is not satisfied; nothing may run or be released."""


class SealMissing(GateRefusal):
    pass


class AuditMissing(GateRefusal):
    pass


class AuditNotPass(GateRefusal):
    pass


class AuditStale(GateRefusal):
    pass


class CommitmentMissing(GateRefusal):
    pass


class PackageNotCommitted(GateRefusal):
    pass


class DesignationMissing(GateRefusal):
    pass


class RunnerNotDesignated(GateRefusal):
    pass


class ForbiddenHost(GateRefusal):
    pass


class ResultNotSealed(GateRefusal):
    pass


class RecordOrderViolation(GateRefusal):
    pass


class RecordRewritten(GateRefusal):
    pass


# ---------------------------------------------------------------- git access (committed trees only)
def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _show(repo: Path, ref: str, rel: str) -> Optional[bytes]:
    p = subprocess.run(["git", "-C", str(repo), "show", "%s:%s" % (ref, rel)], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def _commits_touching(repo: Path, ref: str, rel: str) -> list:
    p = _git(repo, "log", "--format=%H", ref, "--", rel)
    return [c for c in p.stdout.split() if c] if p.returncode == 0 else []


def _strict_ancestor(repo: Path, a: str, b: str) -> bool:
    return a != b and _git(repo, "merge-base", "--is-ancestor", a, b).returncode == 0


def _added_once(repo: Path, ref: str, rel: str, err_missing) -> str:
    cs = _commits_touching(repo, ref, rel)
    if not cs:
        raise err_missing("%s is not committed on %s" % (rel, ref))
    if len(cs) != 1:
        raise RecordRewritten("%s was changed after it was recorded (%d commits touch it); records are immutable"
                              % (rel, len(cs)))
    return cs[0]


def code_hashes(repo: Path, ref: str) -> Dict[str, Optional[str]]:
    """sha256 (LF-normalised) of every audited file in the committed tree of `ref`."""
    out = {}
    for rel in AUDITED_FILES:
        b = _show(repo, ref, rel)
        out[rel] = sealbox.sha256_hex(b.replace(b"\r\n", b"\n")) if b is not None else None
    return out


def worktree_code_hashes(repo: Path) -> Dict[str, Optional[str]]:
    """Same, from the files actually about to execute (the working tree)."""
    out = {}
    for rel in AUDITED_FILES:
        p = Path(repo) / rel
        out[rel] = sealbox.src_sha_lf(p) if p.exists() else None
    return out


def _load(repo: Path, ref: str, name: str, err_missing) -> dict:
    b = _show(repo, ref, PROTO_REL + "/" + name)
    if b is None:
        raise err_missing("%s/%s not on %s" % (PROTO_REL, name, ref))
    try:
        return json.loads(b.decode("utf-8"))
    except Exception as e:                                        # noqa: BLE001
        raise err_missing("%s unreadable: %s" % (name, type(e).__name__))


# ---------------------------------------------------------------- the gates
def check_gates(repo, through: str = "DESIGNATION", ref: str = DEFAULT_REF, package_sha256: Optional[str] = None,
                runner_id: Optional[str] = None, host: Optional[str] = None,
                check_worktree_code: bool = True) -> dict:
    """Verify protocol stages up to and including `through` (SEAL < AUDIT < COMMITMENT < DESIGNATION < RESULT_SEAL).

    Returns a public status dict; raises a GateRefusal subclass at the first failure.
    """
    order = ("SEAL", "AUDIT", "COMMITMENT", "DESIGNATION", "RESULT_SEAL")
    if through not in order:
        raise ValueError(through)
    need = order[: order.index(through) + 1]
    repo = Path(repo)
    st: dict = {"ref": ref, "ref_commit": _git(repo, "rev-parse", ref).stdout.strip()}

    # 1. SEAL
    man_b = _show(repo, ref, PKG_REL + "/MANIFEST_D2.json")
    ct_b = _show(repo, ref, PKG_REL + "/hidden_D2.enc")
    if man_b is None or ct_b is None:
        raise SealMissing("sealed manifest/ciphertext not on %s" % ref)
    man = json.loads(man_b.decode("utf-8"))
    if sealbox.manifest_spec_id(man) != man.get("spec_id") or sealbox.sha256_hex(ct_b) != man["ciphertext_sha256"]:
        raise SealMissing("sealed manifest/ciphertext on %s do not verify" % ref)
    seal_c = _added_once(repo, ref, PKG_REL + "/hidden_D2.enc", SealMissing)
    if _added_once(repo, ref, PKG_REL + "/MANIFEST_D2.json", SealMissing) != seal_c:
        raise SealMissing("manifest and ciphertext were not sealed in the same commit")
    spec_id = man["spec_id"]
    st.update(seal_commit=seal_c, spec_id=spec_id, commitment=man["commitment"],
              ciphertext_sha256=man["ciphertext_sha256"])
    if "AUDIT" not in need:
        return st

    # 2. AUDIT
    au = _load(repo, ref, AUDIT_FILE, AuditMissing)
    au_c = _added_once(repo, ref, PROTO_REL + "/" + AUDIT_FILE, AuditMissing)
    if au.get("format") != AUDIT_FORMAT or au.get("spec_id") != spec_id:
        raise AuditMissing("audit record has the wrong format or spec_id")
    if au.get("verdict") != "PASS":
        raise AuditNotPass("firewall audit verdict is %r, not PASS" % au.get("verdict"))
    if not _strict_ancestor(repo, seal_c, au_c):
        raise RecordOrderViolation("audit was not recorded after the seal")
    bound = au.get("code_sha256") or {}
    now_ref = code_hashes(repo, ref)
    stale = sorted(rel for rel in AUDITED_FILES if bound.get(rel) is None or bound.get(rel) != now_ref[rel])
    if check_worktree_code:
        now_wt = worktree_code_hashes(repo)
        stale += sorted(rel for rel in AUDITED_FILES if bound.get(rel) != now_wt[rel] and rel not in stale)
    if stale:
        raise AuditStale("audited code changed after the audit: %s" % ", ".join(stale))
    st.update(audit_commit=au_c, auditor=au.get("auditor"))
    if "COMMITMENT" not in need:
        return st

    # 3. COMMITMENT
    cm = _load(repo, ref, COMMITMENT_FILE, CommitmentMissing)
    cm_c = _added_once(repo, ref, PROTO_REL + "/" + COMMITMENT_FILE, CommitmentMissing)
    if cm.get("format") != COMMITMENT_FORMAT or cm.get("spec_id") != spec_id or \
            not isinstance(cm.get("package_sha256"), str) or len(cm["package_sha256"]) != 64:
        raise CommitmentMissing("prediction commitment has the wrong format, spec_id or package hash")
    if not _strict_ancestor(repo, au_c, cm_c):
        raise RecordOrderViolation("predictions were committed before the firewall audit passed")
    if package_sha256 is not None and package_sha256.lower() != cm["package_sha256"].lower():
        raise PackageNotCommitted("package sha256 differs from the committed prediction package")
    st.update(commitment_commit=cm_c, package_sha256=cm["package_sha256"])
    if "DESIGNATION" not in need:
        return st

    # 4. DESIGNATION
    ds = _load(repo, ref, DESIGNATION_FILE, DesignationMissing)
    ds_c = _added_once(repo, ref, PROTO_REL + "/" + DESIGNATION_FILE, DesignationMissing)
    if ds.get("format") != DESIGNATION_FORMAT or ds.get("spec_id") != spec_id or not ds.get("runner_id") \
            or not ds.get("host"):
        raise DesignationMissing("runner designation has the wrong format or spec_id")
    if str(ds["host"]).upper() in FORBIDDEN_HOSTS:
        raise ForbiddenHost("designated host %s is Cosmos's machine" % ds["host"])
    if not _strict_ancestor(repo, au_c, ds_c):
        raise RecordOrderViolation("runner designated before the firewall audit passed")
    h = (host or socket.gethostname()).upper()
    if h in FORBIDDEN_HOSTS:
        raise ForbiddenHost("this host (%s) is Cosmos's machine" % h)
    if h != str(ds["host"]).upper():
        raise RunnerNotDesignated("this host %s is not the designated host %s" % (h, ds["host"]))
    if runner_id is not None and runner_id != ds["runner_id"]:
        raise RunnerNotDesignated("runner %r is not the designated runner" % runner_id)
    st.update(designation_commit=ds_c, runner_id=ds["runner_id"], host=ds["host"])
    if "RESULT_SEAL" not in need:
        return st

    # 5. RESULT_SEAL
    rs = _load(repo, ref, RESULT_SEAL_FILE, ResultNotSealed)
    rs_c = _added_once(repo, ref, PROTO_REL + "/" + RESULT_SEAL_FILE, ResultNotSealed)
    if rs.get("format") != RESULT_SEAL_FORMAT or rs.get("spec_id") != spec_id or             rs.get("package_sha256") != cm["package_sha256"] or not rs.get("chain_head") or not rs.get("result_sha256"):
        raise ResultNotSealed("result seal has the wrong format, spec_id, package or hashes")
    if not (_strict_ancestor(repo, cm_c, rs_c) and _strict_ancestor(repo, ds_c, rs_c)):
        raise RecordOrderViolation("result sealed before the commitment/designation")
    st.update(result_seal_commit=rs_c, chain_head=rs["chain_head"], result_sha256=rs["result_sha256"])
    return st


def status(repo, ref: str = DEFAULT_REF) -> dict:
    """Which stages currently pass (public; for posting)."""
    out = {}
    for stage in ("SEAL", "AUDIT", "COMMITMENT", "DESIGNATION", "RESULT_SEAL"):
        try:
            check_gates(repo, stage, ref=ref, host=socket.gethostname())
            out[stage] = "PASS"
        except GateRefusal as e:
            out[stage] = "%s: %s" % (type(e).__name__, e)
            break
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="holdout D2 protocol gate status (public)")
    ap.add_argument("--repo", default=str(HERE.parents[2]))
    ap.add_argument("--ref", default=DEFAULT_REF)
    ap.add_argument("--code-hashes", action="store_true",
                    help="print the code_sha256 map of the committed tree of --ref (for the auditor's record)")
    a = ap.parse_args()
    print(json.dumps(code_hashes(Path(a.repo), a.ref) if a.code_hashes else status(a.repo, a.ref), indent=1))
