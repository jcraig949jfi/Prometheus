"""Holdout D2 protocol gates, v2 (operator directive "COSMOS C3 SUCCESSOR-SEAL", 2026-09-28, s3; repaired after
Odysseus's firewall audit FAIL, roles/Odysseus/fabric_pilot/d2_audit/VERDICT.md, findings F1-F4 and S1-S5).

The order below is ENFORCED, not advised. The runner (runner.py), key release and reveal (custody.py) and the
Harmonia evidence bundle (evidence.py) all call `check_gates` and refuse on any failure. Those three are started only
through entry.py, which verifies the audited code BEFORE any prometheus module is imported (F1).

  1. SEAL         the commit that added hidden_D2.enc + MANIFEST_D2.json is PINNED here (SEAL_COMMIT, SPEC_ID; S5)
                  and must be on the reference branch, with both files still hashing to the sealed values.
  2. AUDIT        versioned records protocol/FIREWALL_AUDIT_<n>.json, n = 1, 2, ... (S2). The record with the highest
                  n is the governing one; it must say PASS, be bound to SPEC_ID and to the sha256 of EVERY file in
                  AUDITED_FILES, and those files must still hash to that (committed tree AND working tree). A later
                  FAIL supersedes an earlier PASS; a later PASS re-audits changed code.
  3. COMMITMENT   protocol/PREDICTION_COMMITMENT.json (Cosmos's frozen package sha256), committed strictly after the
                  governing audit.
  4. DESIGNATION  protocol/RUNNER_DESIGNATION.json: runner id, host (never M2), the runner's OS account (which must
                  not be the custodian's), the EXACT run parameters and a run nonce (S4: one run per designation).
  5. RESULT_SEAL  protocol/RESULT_SEAL.json: chain head + sha256(RESULT.json) + the run nonce; public hashes only.

Record integrity:
  - every record is read from the COMMITTED tree of a FULLY QUALIFIED ref (default refs/remotes/origin/main); a short
    name is refused, and a tag or branch that could shadow origin/main is refused (F3);
  - "added once, never modified" is checked with --full-history, so a record replaced through a merge is seen (F4),
    and any merge commit that touches a record path is refused;
  - the records directory may hold ONLY the record files named above (F1 variant: a protocol/__init__.py would shadow
    this module);
  - every governing record (audit, commitment, designation) must also appear in the custodian's out-of-band allow-list
    on M1 (S1): its sha256, role and the comms message by which its author (Odysseus / Cosmos / the custodian)
    confirmed it. allowlist.py writes that list after checking the comms message's sender and body.

Loaded-code closure (F1): check_gates(..., verify_loaded=True) refuses unless EVERY loaded prometheus.* module file is
in AUDITED_FILES and hashes to the governing audit's binding.

Nothing in this module reads secrets.
"""
from __future__ import annotations

import json
import re
import socket
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

from prometheus.cosmos.c3_holdout_D2 import sealbox

HERE = Path(__file__).resolve().parent
PKG_REL = "prometheus/cosmos/c3_holdout_D2"
PROTO_REL = PKG_REL + "/protocol"
FORBIDDEN_HOSTS = {"SPECTREX5"}               # M2, Cosmos's machine: never holds the key, never runs D
DEFAULT_REF = "refs/remotes/origin/main"
SHORT_REF = "origin/main"
SEAL_COMMIT = "95b31a30d06daa973a27ca0cacd4b768ec7d5fff"                             # pinned (S5)
SPEC_ID = "e2d3213b02aae58b0b20bbd6b5a296545b6335078ae6a0a382ceaf346dc0d9fe"         # pinned (S5)
DEFAULT_ALLOWLIST = Path("C:/Users/jcrai/nestor_receipts/holdout_D2/ALLOWLIST.json")
CUSTODIAN_ACCOUNT = "jcrai"

AUDIT_RE = re.compile(r"^FIREWALL_AUDIT_([1-9][0-9]*)\.json$")
COMMITMENT_FILE = "PREDICTION_COMMITMENT.json"
DESIGNATION_FILE = "RUNNER_DESIGNATION.json"
RESULT_SEAL_FILE = "RESULT_SEAL.json"
FIXED_RECORDS = {COMMITMENT_FILE, DESIGNATION_FILE, RESULT_SEAL_FILE}
RESULT_SEAL_FORMAT = "c3-D2-result-seal/2"
AUDIT_FORMAT = "c3-D2-firewall-audit/2"
COMMITMENT_FORMAT = "c3-D2-prediction-commitment/1"
DESIGNATION_FORMAT = "c3-D2-runner-designation/2"

# Every file whose code runs in a key-holding process (runner, custody, evidence) or decides a gate. F1 added
# c3/probe.py and the package __init__ files; entry.py and allowlist.py are new in v2.
AUDITED_FILES = (
    "prometheus/__init__.py", "prometheus/cosmos/__init__.py", "prometheus/cosmos/c3/__init__.py",
    "prometheus/cosmos/c3_holdout_D/__init__.py",
    PKG_REL + "/__init__.py", PKG_REL + "/sealbox.py", PKG_REL + "/draw.py", PKG_REL + "/runner.py",
    PKG_REL + "/protocol.py", PKG_REL + "/custody.py", PKG_REL + "/evidence.py", PKG_REL + "/entry.py",
    PKG_REL + "/allowlist.py", PKG_REL + "/verify_reveal.py", PKG_REL + "/firewall_check.py",
    "prometheus/cosmos/c3/certify.py", "prometheus/cosmos/c3/probe.py", "prometheus/cosmos/c3/system.py",
    "prometheus/cosmos/c3/task.py", "prometheus/cosmos/c3_holdout_D/medium.py",
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


class UnboundCodeLoaded(GateRefusal):
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


class RecordDirPolluted(GateRefusal):
    pass


class AmbiguousRef(GateRefusal):
    pass


class NotAllowListed(GateRefusal):
    pass


class RunParamsMismatch(GateRefusal):
    pass


# ---------------------------------------------------------------- git access (committed trees only)
def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _show(repo: Path, ref: str, rel: str) -> Optional[bytes]:
    p = subprocess.run(["git", "-C", str(repo), "show", "%s:%s" % (ref, rel)], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def resolve_ref(repo: Path, ref: str) -> str:
    """F3: only a fully qualified ref is accepted, and nothing may shadow the short name origin/main."""
    if not ref.startswith("refs/"):
        raise AmbiguousRef("refusing a short ref name %r: use a fully qualified refs/... name" % ref)
    for shadow in ("refs/tags/" + SHORT_REF, "refs/heads/" + SHORT_REF, "refs/tags/main"):
        if _git(repo, "show-ref", "--verify", "--quiet", shadow).returncode == 0:
            raise AmbiguousRef("%s exists and could shadow the reference branch" % shadow)
    p = _git(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    if p.returncode != 0:
        raise AmbiguousRef("reference %s does not resolve" % ref)
    return p.stdout.strip()


def _commits_touching(repo: Path, ref: str, rel: str) -> list:
    """F4: --full-history, so a record replaced through a merge shows up."""
    p = _git(repo, "log", "--full-history", "--format=%H %P", ref, "--", rel)
    out = []
    for line in p.stdout.splitlines() if p.returncode == 0 else []:
        parts = line.split()
        if parts:
            out.append((parts[0], len(parts) - 1))
    return out


def _strict_ancestor(repo: Path, a: str, b: str) -> bool:
    return a != b and _git(repo, "merge-base", "--is-ancestor", a, b).returncode == 0


def _added_once(repo: Path, ref: str, rel: str, err_missing) -> str:
    cs = _commits_touching(repo, ref, rel)
    if not cs:
        raise err_missing("%s is not committed on %s" % (rel, ref))
    if any(npar > 1 for _c, npar in cs):
        raise RecordRewritten("%s is touched by a merge commit; records may not arrive or change through merges" % rel)
    if len(cs) != 1:
        raise RecordRewritten("%s was changed after it was recorded (%d commits touch it, full history)" % (rel, len(cs)))
    return cs[0][0]


def _proto_tree(repo: Path, ref: str) -> list:
    p = _git(repo, "ls-tree", "--name-only", ref, PROTO_REL + "/")
    return [Path(x).name for x in p.stdout.split()] if p.returncode == 0 else []


def check_records_dir(repo: Path, ref: str) -> list:
    """Only the named record files may exist in protocol/, committed or in the working tree (F1 variant)."""
    names = set(_proto_tree(repo, ref))
    wt = Path(repo) / PROTO_REL
    if wt.exists():
        names |= {p.name for p in wt.iterdir()}
    bad = sorted(n for n in names if not (n in FIXED_RECORDS or AUDIT_RE.match(n)))
    if bad:
        raise RecordDirPolluted("unexpected files in %s: %s" % (PROTO_REL, ", ".join(bad)))
    return sorted(names)


def code_hashes(repo: Path, ref: str) -> Dict[str, Optional[str]]:
    out = {}
    for rel in AUDITED_FILES:
        b = _show(repo, ref, rel)
        out[rel] = sealbox.sha256_hex(b.replace(b"\r\n", b"\n")) if b is not None else None
    return out


def worktree_code_hashes(repo: Path) -> Dict[str, Optional[str]]:
    out = {}
    for rel in AUDITED_FILES:
        p = Path(repo) / rel
        out[rel] = sealbox.src_sha_lf(p) if p.exists() else None
    return out


def loaded_closure(repo: Path) -> Dict[str, str]:
    """{repo-relative path: sha256 LF} of every loaded prometheus.* module; a module whose file is outside the repo, or
    has no file, is reported as such (and is refused by check_gates)."""
    root = Path(repo).resolve()
    out = {}
    for name, mod in list(sys.modules.items()):
        if not (name == "prometheus" or name.startswith("prometheus.")):
            continue
        f = getattr(mod, "__file__", None)
        if not f:
            out["<nofile>:" + name] = "?"
            continue
        p = Path(f).resolve()
        if p.suffix != ".py":
            out["<not-source>:" + name] = str(p)
            continue
        try:
            rel = str(p.relative_to(root)).replace("\\", "/")
        except ValueError:
            out["<outside-repo>:" + name] = str(p)
            continue
        out[rel] = sealbox.src_sha_lf(p)
    return out


def _load_bytes(repo, ref, name, err_missing):
    b = _show(repo, ref, PROTO_REL + "/" + name)
    if b is None:
        raise err_missing("%s/%s not on %s" % (PROTO_REL, name, ref))
    try:
        return b, json.loads(b.decode("utf-8"))
    except Exception as e:                                        # noqa: BLE001
        raise err_missing("%s unreadable: %s" % (name, type(e).__name__))


def record_sha(b: bytes) -> str:
    return sealbox.sha256_hex(b.replace(b"\r\n", b"\n"))


def _allowlisted(allowlist, role: str, name: str, b: bytes):
    if allowlist is False:                                        # explicitly disabled (tests of other gates only)
        return
    path = Path(allowlist)
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))["entries"]
    except Exception as e:                                        # noqa: BLE001
        raise NotAllowListed("custodian allow-list unreadable (%s): %s" % (path, type(e).__name__))
    h = record_sha(b)
    if not any(e.get("role") == role and e.get("record") == name and e.get("sha256") == h for e in entries):
        raise NotAllowListed("%s (%s, sha256 %s...) is not in the custodian's allow-list" % (name, role, h[:12]))


# ---------------------------------------------------------------- the gates
def check_gates(repo, through: str = "DESIGNATION", ref: str = DEFAULT_REF, package_sha256: Optional[str] = None,
                runner_id: Optional[str] = None, host: Optional[str] = None, check_worktree_code: bool = True,
                allowlist=DEFAULT_ALLOWLIST, verify_loaded: bool = False, account: Optional[str] = None,
                run_params: Optional[dict] = None, pins: Optional[dict] = None) -> dict:
    order = ("SEAL", "AUDIT", "COMMITMENT", "DESIGNATION", "RESULT_SEAL")
    if through not in order:
        raise ValueError(through)
    need = order[: order.index(through) + 1]
    repo = Path(repo)
    pins = pins or {"seal_commit": SEAL_COMMIT, "spec_id": SPEC_ID}
    st: dict = {"ref": ref, "ref_commit": resolve_ref(repo, ref)}
    check_records_dir(repo, ref)

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
    if seal_c != pins["seal_commit"] or man["spec_id"] != pins["spec_id"]:
        raise SealMissing("seal commit / spec_id differ from the values pinned in code")
    spec_id = man["spec_id"]
    st.update(seal_commit=seal_c, spec_id=spec_id, commitment=man["commitment"],
              ciphertext_sha256=man["ciphertext_sha256"])
    if "AUDIT" not in need:
        return st

    # 2. AUDIT (versioned; the highest n governs)
    audits = sorted((int(AUDIT_RE.match(n).group(1)), n) for n in _proto_tree(repo, ref) if AUDIT_RE.match(n))
    if not audits:
        raise AuditMissing("no protocol/FIREWALL_AUDIT_<n>.json on %s" % ref)
    prev_c = seal_c
    for _n, name in audits:                                       # each added once, in increasing commit order
        c = _added_once(repo, ref, PROTO_REL + "/" + name, AuditMissing)
        if not _strict_ancestor(repo, prev_c, c):
            raise RecordOrderViolation("%s was not recorded after the seal and the previous audit" % name)
        prev_c = c
    gov_n, gov = audits[-1]
    au_b, au = _load_bytes(repo, ref, gov, AuditMissing)
    au_c = prev_c
    if au.get("format") != AUDIT_FORMAT or au.get("spec_id") != spec_id or au.get("n") != gov_n:
        raise AuditMissing("governing audit %s has the wrong format, spec_id or n" % gov)
    if au.get("verdict") != "PASS":
        raise AuditNotPass("governing audit %s verdict is %r, not PASS" % (gov, au.get("verdict")))
    _allowlisted(allowlist, "AUDIT", gov, au_b)
    bound = au.get("code_sha256") or {}
    if set(bound) != set(AUDITED_FILES):
        raise AuditStale("the audit does not bind exactly AUDITED_FILES")
    now_ref = code_hashes(repo, ref)
    stale = sorted(rel for rel in AUDITED_FILES if bound.get(rel) is None or bound.get(rel) != now_ref[rel])
    if check_worktree_code:
        now_wt = worktree_code_hashes(repo)
        stale += sorted(rel for rel in AUDITED_FILES if bound.get(rel) != now_wt[rel] and rel not in stale)
    if stale:
        raise AuditStale("audited code changed after the audit: %s" % ", ".join(stale))
    if verify_loaded:
        loaded = loaded_closure(repo)
        bad = sorted(k for k, h in loaded.items() if k not in bound or bound[k] != h)
        if bad:
            raise UnboundCodeLoaded("loaded prometheus code not bound by the audit: %s" % ", ".join(bad))
    st.update(audit_commit=au_c, audit_record=gov, auditor=au.get("auditor"))
    if "COMMITMENT" not in need:
        return st

    # 3. COMMITMENT
    cm_b, cm = _load_bytes(repo, ref, COMMITMENT_FILE, CommitmentMissing)
    cm_c = _added_once(repo, ref, PROTO_REL + "/" + COMMITMENT_FILE, CommitmentMissing)
    if cm.get("format") != COMMITMENT_FORMAT or cm.get("spec_id") != spec_id or \
            not isinstance(cm.get("package_sha256"), str) or len(cm["package_sha256"]) != 64:
        raise CommitmentMissing("prediction commitment has the wrong format, spec_id or package hash")
    if not _strict_ancestor(repo, au_c, cm_c):
        raise RecordOrderViolation("predictions were committed before the governing firewall audit")
    _allowlisted(allowlist, "COMMITMENT", COMMITMENT_FILE, cm_b)
    if package_sha256 is not None and package_sha256.lower() != cm["package_sha256"].lower():
        raise PackageNotCommitted("package sha256 differs from the committed prediction package")
    st.update(commitment_commit=cm_c, package_sha256=cm["package_sha256"])
    if "DESIGNATION" not in need:
        return st

    # 4. DESIGNATION
    ds_b, ds = _load_bytes(repo, ref, DESIGNATION_FILE, DesignationMissing)
    ds_c = _added_once(repo, ref, PROTO_REL + "/" + DESIGNATION_FILE, DesignationMissing)
    if ds.get("format") != DESIGNATION_FORMAT or ds.get("spec_id") != spec_id or not ds.get("runner_id") \
            or not ds.get("host") or not ds.get("account") or not isinstance(ds.get("run_params"), dict) \
            or not ds.get("run_nonce"):
        raise DesignationMissing("runner designation has the wrong format, spec_id, account, run_params or nonce")
    if str(ds["host"]).upper() in FORBIDDEN_HOSTS:
        raise ForbiddenHost("designated host %s is Cosmos's machine" % ds["host"])
    if str(ds["account"]).lower() == CUSTODIAN_ACCOUNT:
        raise RunnerNotDesignated("the designated runner account must not be the custodian's account")
    if not _strict_ancestor(repo, cm_c, ds_c):
        raise RecordOrderViolation("runner designated before the prediction commitment")
    _allowlisted(allowlist, "DESIGNATION", DESIGNATION_FILE, ds_b)
    h = (host or socket.gethostname()).upper()
    if h in FORBIDDEN_HOSTS:
        raise ForbiddenHost("this host (%s) is Cosmos's machine" % h)
    if h != str(ds["host"]).upper():
        raise RunnerNotDesignated("this host %s is not the designated host %s" % (h, ds["host"]))
    if runner_id is not None and runner_id != ds["runner_id"]:
        raise RunnerNotDesignated("runner %r is not the designated runner" % runner_id)
    if account is not None and account.lower() != str(ds["account"]).lower():
        raise RunnerNotDesignated("this OS account %r is not the designated runner account" % account)
    if run_params is not None and run_params != ds["run_params"]:
        raise RunParamsMismatch("run parameters differ from the designation (S4)")
    st.update(designation_commit=ds_c, runner_id=ds["runner_id"], host=ds["host"], account=ds["account"],
              run_params=ds["run_params"], run_nonce=ds["run_nonce"])
    if "RESULT_SEAL" not in need:
        return st

    # 5. RESULT_SEAL
    rs = _load_bytes(repo, ref, RESULT_SEAL_FILE, ResultNotSealed)[1]
    rs_c = _added_once(repo, ref, PROTO_REL + "/" + RESULT_SEAL_FILE, ResultNotSealed)
    if rs.get("format") != RESULT_SEAL_FORMAT or rs.get("spec_id") != spec_id or \
            rs.get("package_sha256") != cm["package_sha256"] or not rs.get("chain_head") or \
            not rs.get("result_sha256") or rs.get("run_nonce") != ds["run_nonce"]:
        raise ResultNotSealed("result seal has the wrong format, spec_id, package, hashes or run nonce")
    if not _strict_ancestor(repo, ds_c, rs_c):
        raise RecordOrderViolation("result sealed before the designation")
    st.update(result_seal_commit=rs_c, chain_head=rs["chain_head"], result_sha256=rs["result_sha256"])
    return st


def status(repo, ref: str = DEFAULT_REF, allowlist=DEFAULT_ALLOWLIST) -> dict:
    out = {}
    for stage in ("SEAL", "AUDIT", "COMMITMENT", "DESIGNATION", "RESULT_SEAL"):
        try:
            check_gates(repo, stage, ref=ref, host=socket.gethostname(), allowlist=allowlist)
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
