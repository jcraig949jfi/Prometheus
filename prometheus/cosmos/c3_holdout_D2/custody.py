"""Holdout D2 key custody and controlled reveal (M1 only; the custodian is Nestor; nothing here ever runs on M2).

  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.custody release-key --runner-id ID --dest DIR
  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.custody result-seal --run RUN_DIR --record-out FILE
  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.custody reveal --run RUN_DIR --dest DIR
  (all accept --ref, default origin/main)

release-key  protocol.check_gates(..., "DESIGNATION", runner_id): the sealed set exists, a firewall audit of this
             exact code PASSED, Cosmos committed its package hash after the audit, and ID on this host is the
             designated runner. Only then is a copy of the key written to DIR (outside every git repository,
             outside the secrets directory). At most once per spec_id.
result-seal  after the run CLOSED with a verifying receipt chain for the COMMITTED package: writes the PUBLIC
             record protocol/RESULT_SEAL.json (spec_id, package sha256, chain head, sha256(RESULT.json)) for the
             custodian to commit. Results themselves stay on M1, outside git, and are not sent to Cosmos.
reveal       protocol.check_gates(..., "RESULT_SEAL") and the run on disk must match the sealed chain head and
             result hash. Only then are plaintext, salt and key copied to DIR for publication, and verify_reveal
             is run on the copies. At most once per spec_id.

Every action (and every refusal) is appended to CUSTODY_LOG (M1, outside git; public fields only). Printed
output carries booleans, hashes of public records and paths; never key, salt, nonce or world content.
"""
from __future__ import annotations

import os

if os.environ.get("COSMOS_BROKER") != "1":
    raise ImportError("holdout D2 custody: set COSMOS_BROKER=1 (broker only)")

import argparse
import datetime as _dt
import json
import socket
import sys
from pathlib import Path

from prometheus.cosmos.c3_holdout_D2 import protocol, sealbox

HERE = Path(__file__).resolve().parent
SECRETS_DIR = Path("C:/Users/jcrai/nestor_secrets/holdout_D2")
PLAIN_NAME, SALT_NAME, KEY_NAME = "hidden_D2.plain.json", "hidden_D2.salt.hex", "hidden_D2.key.hex"
CUSTODY_LOG = Path("C:/Users/jcrai/nestor_receipts/holdout_D2/custody.jsonl")
DEFAULT_REPO = HERE.parents[2]


class CustodyRefusal(Exception):
    pass


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _inside_git(p: Path) -> bool:
    p = Path(p).resolve()
    return any((q / ".git").exists() for q in [p] + list(p.parents))


def _inside(p: Path, root: Path) -> bool:
    try:
        Path(p).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


class Custody:
    def __init__(self, repo=DEFAULT_REPO, ref=protocol.DEFAULT_REF, secrets_dir=SECRETS_DIR, log=CUSTODY_LOG,
                 host=None, allowlist=None, pins=None, verify_loaded=True):
        self.repo, self.ref = Path(repo), ref
        self.secrets_dir, self.log = Path(secrets_dir), Path(log)
        self.host = host or socket.gethostname()
        self.allowlist = protocol.DEFAULT_ALLOWLIST if allowlist is None else allowlist
        self.pins, self.verify_loaded = pins, verify_loaded

    def _gates(self, through, **kw):
        return protocol.check_gates(self.repo, through, ref=self.ref, host=self.host, allowlist=self.allowlist,
                                    pins=self.pins, verify_loaded=self.verify_loaded, **kw)

    # ------------------------------------------------------------ log
    def _events(self) -> list:
        if not self.log.exists():
            return []
        return [json.loads(x) for x in self.log.read_text(encoding="utf-8").splitlines() if x.strip()]

    def _append(self, rec: dict) -> None:
        self.log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(dict(rec, utc=_utc(), host=self.host), sort_keys=True) + "\n")

    def _refuse(self, action: str, e: Exception):
        self._append({"event": "REFUSED", "action": action, "reason": "%s: %s" % (type(e).__name__, e)})
        raise e

    def _dest_ok(self, dest: Path) -> None:
        if _inside_git(dest):
            raise CustodyRefusal("destination is inside a git repository")
        if _inside(dest, self.secrets_dir):
            raise CustodyRefusal("destination is inside the secrets directory")
        if self.host.upper() in protocol.FORBIDDEN_HOSTS:
            raise protocol.ForbiddenHost("custody never acts on Cosmos's machine")

    def _write_excl(self, path: Path, data: bytes) -> None:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0))
        with os.fdopen(fd, "wb") as f:
            f.write(data)

    # ------------------------------------------------------------ release the key to the designated runner
    def release_key(self, runner_id: str, dest) -> dict:
        dest = Path(dest)
        try:
            self._dest_ok(dest)
            g = self._gates("DESIGNATION", runner_id=runner_id)
            if any(e.get("event") == "KEY_RELEASED" and e.get("spec_id") == g["spec_id"] for e in self._events()):
                raise CustodyRefusal("the key for this spec_id was already released once")
            if protocol.once_record_present(self.repo, self.ref, protocol.KEY_RELEASED_FILE):
                raise CustodyRefusal("a KEY_RELEASED record is committed: the key was already released (v3: git, not the log)")
            key = sealbox.read_hex_file(self.secrets_dir / KEY_NAME, sealbox.KEY_BYTES)
            dest.mkdir(parents=True, exist_ok=True)
            self._write_excl(dest / KEY_NAME, key.hex().encode("ascii") + b"\n")
            del key
        except (protocol.GateRefusal, CustodyRefusal, OSError) as e:
            self._refuse("release-key", e)
        rec = {"event": "KEY_RELEASED", "spec_id": g["spec_id"], "runner_id": runner_id, "dest": str(dest),
               "gates": {k: v for k, v in g.items() if k.endswith("_commit")}}
        self._append(rec)
        self._write_once_record(protocol.KEY_RELEASED_FILE, {k: rec[k] for k in ("event", "spec_id", "runner_id", "gates")})
        return rec

    def _write_once_record(self, name, body):
        """v3: write protocol/<name> in the working tree for the custodian to COMMIT immediately; once committed, a second
        release/reveal is refused from git regardless of the custody log."""
        p = self.repo / protocol.PROTO_REL / name
        if not p.exists():
            p.write_text(json.dumps(dict(body, utc=_utc()), indent=1, sort_keys=True) + "\n", encoding="utf-8",
                         newline="\n")
        return p

    # ------------------------------------------------------------ public result-seal record
    def result_seal_record(self, run_dir, record_out) -> dict:
        from prometheus.cosmos.c3_holdout_D2 import runner       # broker-only import
        run_dir = Path(run_dir)
        try:
            g = self._gates("DESIGNATION")
            ok, recs, why = runner.verify_receipts(run_dir / "receipts.jsonl")
            if not ok:
                raise CustodyRefusal("receipt chain does not verify: %s" % why)
            if not recs or recs[-1]["kind"] != "close":
                raise CustodyRefusal("run is not closed")
            if recs[0]["body"]["package"]["sha256"] != g["package_sha256"]:
                raise CustodyRefusal("run used a package other than the committed one")
            if recs[0]["body"]["spec_id"] != g["spec_id"]:
                raise CustodyRefusal("run is not on the sealed hidden set")
            if recs[0]["body"].get("run_nonce") != g["run_nonce"]:
                raise CustodyRefusal("run was not made under this designation (run nonce)")
            res_b = (run_dir / "RESULT.json").read_bytes()
            if json.loads(res_b.decode("utf-8")).get("chain_head") != recs[-1]["hash"]:
                raise CustodyRefusal("RESULT.json does not match the receipt chain head")
        except (protocol.GateRefusal, CustodyRefusal, OSError, ValueError, KeyError) as e:
            self._refuse("result-seal", e)
        rec = {"format": protocol.RESULT_SEAL_FORMAT, "spec_id": g["spec_id"], "package_sha256": g["package_sha256"],
               "run_nonce": g["run_nonce"],
               "chain_head": recs[-1]["hash"], "result_sha256": sealbox.sha256_hex(res_b),
               "n_receipts": len(recs), "sealed_by": "Nestor (custodian)", "utc": _utc()}
        Path(record_out).write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        self._append({"event": "RESULT_SEAL_WRITTEN", **{k: rec[k] for k in ("spec_id", "chain_head", "result_sha256")}})
        return rec

    # ------------------------------------------------------------ controlled reveal
    def reveal(self, run_dir, dest) -> dict:
        from prometheus.cosmos.c3_holdout_D2 import runner, verify_reveal
        run_dir, dest = Path(run_dir), Path(dest)
        try:
            self._dest_ok(dest)
            g = self._gates("RESULT_SEAL")
            # v2 (Odysseus S3): re-verify the whole run, not only the result seal
            ok, recs, why = runner.verify_receipts(run_dir / "receipts.jsonl")
            if not ok:
                raise CustodyRefusal("receipt chain does not verify: %s" % why)
            if not recs or recs[-1]["kind"] != "close" or recs[-1]["hash"] != g["chain_head"]:
                raise CustodyRefusal("run on disk is not closed at the sealed chain head")
            if recs[0]["body"]["package"]["sha256"] != g["package_sha256"] or recs[0]["body"]["spec_id"] != g["spec_id"] \
                    or recs[0]["body"].get("run_nonce") != g["run_nonce"]:
                raise CustodyRefusal("run package / hidden set / designation nonce does not match the protocol")
            if sealbox.sha256_file(run_dir / "RESULT.json") != g["result_sha256"]:
                raise CustodyRefusal("RESULT.json does not match the sealed result hash")
            if any(e.get("event") == "REVEALED" and e.get("spec_id") == g["spec_id"] for e in self._events()):
                raise CustodyRefusal("already revealed")
            if protocol.once_record_present(self.repo, self.ref, protocol.REVEALED_FILE):
                raise CustodyRefusal("a REVEALED record is committed: already revealed (v3: git, not the log)")
            dest.mkdir(parents=True, exist_ok=True)
            for name in (PLAIN_NAME, SALT_NAME, KEY_NAME):
                self._write_excl(dest / name, (self.secrets_dir / name).read_bytes())
        except (protocol.GateRefusal, CustodyRefusal, OSError, ValueError, KeyError) as e:
            self._refuse("reveal", e)
        man_b = protocol._show(self.repo, self.ref, protocol.PKG_REL + "/MANIFEST_D2.json")
        ct_b = protocol._show(self.repo, self.ref, protocol.PKG_REL + "/hidden_D2.enc")
        chk = verify_reveal.verify((dest / PLAIN_NAME).read_bytes(),
                                   sealbox.read_hex_file(dest / SALT_NAME, 32),
                                   sealbox.read_hex_file(dest / KEY_NAME, sealbox.KEY_BYTES),
                                   json.loads(man_b.decode("utf-8")), ct_b)
        rec = {"event": "REVEALED", "spec_id": g["spec_id"], "dest": str(dest), "verify_reveal": chk,
               "result_seal_commit": g["result_seal_commit"]}
        self._append(rec)
        self._write_once_record(protocol.REVEALED_FILE, {"event": "REVEALED", "spec_id": g["spec_id"],
                                                         "result_seal_commit": g["result_seal_commit"]})
        return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="holdout D2 custody (M1)")
    ap.add_argument("cmd", choices=("release-key", "result-seal", "reveal"))
    ap.add_argument("--runner-id")
    ap.add_argument("--dest")
    ap.add_argument("--run")
    ap.add_argument("--record-out")
    ap.add_argument("--ref", default=protocol.DEFAULT_REF)
    a = ap.parse_args(argv)
    if a.cmd in ("release-key", "reveal") and os.environ.get("C3D2_ENTRY") != "verified":
        print(json.dumps({"refused": True, "reason": "start custody through entry.py (pre-import code verification)"}))
        return 3
    c = Custody(ref=a.ref)
    try:
        if a.cmd == "release-key":
            r = c.release_key(a.runner_id, a.dest)
        elif a.cmd == "result-seal":
            r = c.result_seal_record(a.run, a.record_out)
        else:
            r = c.reveal(a.run, a.dest)
    except (protocol.GateRefusal, CustodyRefusal) as e:
        print(json.dumps({"refused": True, "reason": "%s: %s" % (type(e).__name__, e)}))
        return 3
    print(json.dumps(r, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
