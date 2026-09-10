"""Generate deploy/DEPLOYED_BUILD.json -- the pin that makes the running M1
build recoverable without depending on the deployment checkout's branch state.
"""
import hashlib
import io
import json
import os
import subprocess

WT = ("C:/Users/jcrai/AppData/Local/Temp/claude/F--SerendipityD/"
      "1abf2828-fed8-4e30-a8e2-7e51465690a5/scratchpad/daedwt2")
LIVE = "F:/Prometheus"
REL = "SerendipityFoundry/SerendipityFoundryEngine"

FILES = [
    REL + "/sfe/__init__.py", REL + "/sfe/api.py", REL + "/sfe/canary.py",
    REL + "/sfe/errors.py", REL + "/sfe/events.py", REL + "/sfe/executors.py",
    REL + "/sfe/ids.py", REL + "/sfe/release.py", REL + "/sfe/runtime.py",
    REL + "/sfe/store.py",
    REL + "/serve.py",
    "SerendipityFoundry/SerendipityFoundryClient/sfclient/client.py",
]


def norm(b):
    return b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def git(a):
    r = subprocess.run(["git"] + a, cwd=WT, capture_output=True)
    return r.stdout.decode("utf-8", "replace").strip() if r.returncode == 0 else None


commit = git(["rev-parse", "HEAD"])


def _schema_version():
    """Read it from the SOURCE, never hardcode it. The first cut of this
    generator pinned 6 as a literal and kept pinning 6 after v7 shipped, so
    verify_deploy reported a drift that did not exist -- the verifier was
    right and the pin was wrong."""
    import re
    src = io.open(os.path.join(WT, REL, "sfe", "store.py"),
                  encoding="utf-8").read()
    return int(re.search(r"^SCHEMA_VERSION = (\d+)", src, re.M).group(1))


def _release_note():
    return "schema v%d" % _schema_version()

# engine_source_hash exactly as sfe/release.py computes it
h = hashlib.sha256()
sfe_dir = os.path.join(WT, REL, "sfe")
for n in sorted(p for p in os.listdir(sfe_dir) if p.endswith(".py")):
    d = norm(io.open(os.path.join(sfe_dir, n), "rb").read())
    h.update(n.encode("utf-8"))
    h.update(b"\x00")
    h.update(d)
    h.update(b"\x00")
engine_hash = "sha256:" + h.hexdigest()

files = {}
for f in FILES:
    d = norm(io.open(os.path.join(WT, f), "rb").read())
    files[f] = {"sha256_lf": hashlib.sha256(d).hexdigest(), "bytes_lf": len(d)}

pin = {
    "_what_this_is": (
        "The exact source constituting the SFE build deployed on M1. It exists "
        "because the deployment tree (F:/Prometheus) is a SHARED checkout that "
        "other roles switch branches in, so the deployed source's presence "
        "there is not guaranteed by that tree's git state. This pin is the "
        "recovery record and does not depend on it."),
    "engine": "M1 / SKULLPORT",
    "endpoint": "https://192.168.1.202:8811",
    "pinned_at": "2026-09-10",
    "pinned_by": "Daedalus",
    "schema_version": _schema_version(),
    "release": _release_note(),
    "source_commit_containing_build": commit,
    "release_commits": ["ef05397f2", "07b5b05a7", "877d478c6", "b91880a2d"],
    "engine_source_hash": engine_hash,
    "_engine_source_hash_definition": (
        "sha256 over sorted sfe/*.py, each contributing name + NUL + "
        "LF-normalized bytes + NUL. Computed at import by sfe/release.py; "
        "LF-normalized so a checkout's line-ending convention cannot change "
        "build identity. This is the AUTHORITATIVE build id. source_commit on "
        "/v2/version is best-effort git metadata from the deployment tree and "
        "may name a commit that cannot reproduce the build."),
    "expected_runtime_config": {
        "session_enforcement": "advisory",
        "science_profile": "warn",
        "engine_instance_id": "eng_8a37a5d305969034d488c43e",
    },
    "_engine_instance_id_note": (
        "identity of the LEDGER, minted once per database and stored in meta. "
        "It travels with the substrate, not the path, so it must survive any "
        "restore that preserves var/engine.db."),
    "rollback_behaviour": (
        "An older engine opened against a NEWER ledger REFUSES to start: "
        "RuntimeError 'db schema version N is NEWER than this engine's M; "
        "refusing to run (would misread state)' (sfe/store.py). Measured for "
        "6-over-5 on 2026-09-06 by running the 35758f9d0 source against a "
        "VACUUM INTO copy of the live ledger. So a source revert produces a "
        "LOUD OUTAGE, not a silent downgrade -- the service dies rather than "
        "quietly serving older semantics over newer data. That is the correct "
        "failure direction, and it is why this pin is a recovery aid rather "
        "than a safety interlock. It is ALSO why a rollback across 8 -> 7 is "
        "code AND data: the schema-7 snapshot taken before the deploy is the "
        "rollback, and everything written under 8 after it is not in that "
        "snapshot. See deploy/DEPLOY_SCHEMA8_2026-09-10.md section 4."),
    "deployed_2026-09-10": {
        "from": {"schema_version": 7,
                 "engine_source_hash":
                     "sha256:084f951f866cc50aec73c6403528abc234fd514742b25"
                     "ffd1aff5515a271feff"},
        "engine_instance_id_before_and_after":
            "eng_8a37a5d305969034d488c43e (UNCHANGED -- the ledger is the "
            "same substrate; a change here would have meant the service was "
            "pointed at a different database)",
        "pre_deploy_backup":
            "var/backup/engine-schema7-20260910-182335.db (109,989,888 bytes; "
            "VACUUM INTO with the service stopped; verified readable as "
            "schema 7 with the same instance id and 63101 events)",
        "migration_was_additive":
            "events 63101 before and after; experiments 27525 before and "
            "after; budget_reservations and cost_events created empty",
        "runtime_flag_required":
            "--max-artifact-bytes 33554432. v8 adds a per-artifact ceiling "
            "that applies on READ; one stored artifact is 32 MiB and the "
            "16 MiB default would have made it unreadable.",
    },
    "restore": {
        "verify": "python deploy/verify_deploy.py",
        "restore_source": (
            "git -C <a checkout you own> fetch origin && git checkout %s -- "
            "SerendipityFoundry/  # then copy into the deployment tree"
        ) % (commit or "<commit>"),
        "do_not": (
            "Do NOT 'git checkout -- .' or 'git clean' in F:/Prometheus to fix "
            "this: that tree carries uncommitted work belonging to ergon, "
            "evidence_wiki/PEW and other roles."),
    },
    "files": files,
}

out = os.path.join(WT, REL, "deploy", "DEPLOYED_BUILD.json")
io.open(out, "w", encoding="utf-8", newline="\n").write(
    json.dumps(pin, indent=2, sort_keys=False) + "\n")
print("wrote", out)
print("  commit      :", commit[:9])
print("  engine hash :", engine_hash)
print("  files pinned:", len(files))
