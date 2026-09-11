"""Gate-fire of C1 and C2 (charon/probe/c1c2_checks.py) against the live metabolization-probe
ledgers, read-only, plus a COPY of block B with one planted HTTP-504 row. CHARON-01.

Reads:   ergon/probe/ledgers/campaign/{p1_prepass.jsonl,manifest_meta.json}
         ergon/probe/ledgers/campaign_blockB/p1_prepass.jsonl
Writes:  charon/probe/c1c2_gate_fire_2026-09-11.json (this repo)
         a planted copy under the OS temp dir (never under the repo; its sha is recorded)
Loader under test: ergon.probe.assemble.load_prepass, unchanged at the SHA in the receipt.

Run from the repository root of a linked worktree:
    python charon/probe/c1c2_gate_fire_2026-09-11.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from archaeon.workspace import assert_not_canonical, receipt as ws_receipt  # noqa: E402

_spec = importlib.util.spec_from_file_location("c1c2_checks", ROOT / "charon/probe/c1c2_checks.py")
c1c2 = importlib.util.module_from_spec(_spec)
sys.modules["c1c2_checks"] = c1c2  # dataclasses resolve annotations through sys.modules
_spec.loader.exec_module(c1c2)  # type: ignore[union-attr]

from ergon.probe.assemble import load_prepass  # noqa: E402  (the loader the ruling measured)

OUT = ROOT / "charon/probe/c1c2_gate_fire_2026-09-11.json"
POOL_A = ROOT / "ergon/probe/ledgers/campaign/p1_prepass.jsonl"
POOL_B = ROOT / "ergon/probe/ledgers/campaign_blockB/p1_prepass.jsonl"
META_A = ROOT / "ergon/probe/ledgers/campaign/manifest_meta.json"
PLANTED_UID = "charon-planted-504-2026-09-11"


def loader(path: pathlib.Path):
    # ledger_id names the count family so the loader renders the method projection, which is
    # the path the ruling quoted ("prior attempt recorded no recognizable method vocabulary").
    return load_prepass(pathlib.Path(path), ledger_id="nearmiss_mix")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=60).stdout.strip()


def main() -> int:
    guard = assert_not_canonical("charon c1c2 gate-fire", allow_override=False)
    out: dict = {
        "artifact": "charon/probe/c1c2_gate_fire_2026-09-11.json",
        "backlog": "CHARON-01",
        "ruling": c1c2.RULING,
        "checks_version": c1c2.CHECKS_VERSION,
        "ts_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "workspace": ws_receipt(),
        "guard": guard,
        "head": git("rev-parse", "HEAD"),
        "loader": "ergon.probe.assemble.load_prepass (ledger_id='nearmiss_mix')",
        "loader_last_commit": git("log", "-1", "--format=%h %ci", "--", "ergon/probe/assemble.py"),
        "pool_last_commit": {
            "A": git("log", "-1", "--format=%h %ci", "--", str(POOL_A.relative_to(ROOT))),
            "B": git("log", "-1", "--format=%h %ci", "--", str(POOL_B.relative_to(ROOT))),
        },
        "results": {},
    }

    # ---- C1: the receipts that exist. Block A has manifest_meta.json; block B has no receipt.
    meta_a = json.loads(META_A.read_text(encoding="utf-8"))
    out["results"]["C1_blockA_manifest_meta_as_receipt"] = c1c2.check_c1_pool_fingerprint(
        meta_a, {"blockA_p1_prepass": POOL_A}).as_dict()
    out["results"]["C1_blockB_no_receipt"] = c1c2.check_c1_pool_fingerprint(
        {}, {"blockB_p1_prepass": POOL_B}).as_dict()
    out["results"]["C1_current_fingerprints_for_a_successor"] = {
        "blockA_p1_prepass": c1c2.pool_fingerprint(POOL_A),
        "blockB_p1_prepass": c1c2.pool_fingerprint(POOL_B),
    }

    # ---- C2: the live pools, read-only.
    out["results"]["C2_blockA_live"] = c1c2.check_c2_transport_not_residue(POOL_A, loader).as_dict()
    out["results"]["C2_blockB_live"] = c1c2.check_c2_transport_not_residue(POOL_B, loader).as_dict()

    # ---- C2 gate-fire: a COPY of block B with exactly one planted 504 row, outside the repo.
    with tempfile.TemporaryDirectory(prefix="charon_c1c2_") as td:
        copy = pathlib.Path(td) / "p1_prepass.PLANTED.jsonl"
        src = POOL_B.read_bytes().replace(b"\r\n", b"\n")
        planted = {
            "key": [1, PLANTED_UID], "status": "http_error", "error_type": "HTTP504",
            "latency_s": 302.0, "prompt_tokens": None, "completion_tokens": None,
            "extracted_int": None, "attempt_text": "", "solver": "charon:planted",
            "derives_from_gold": False, "ts_utc": out["ts_utc"], "host": "charon", "executor": "charon",
        }
        copy.write_bytes(src + json.dumps(planted).encode() + b"\n")
        v = c1c2.check_c2_transport_not_residue(copy, loader)
        planted_row = next((r for r in v.rows if r["uid"] == PLANTED_UID), None)
        out["results"]["C2_blockB_COPY_planted_504"] = {
            "copy_sha256_lf": hashlib.sha256(copy.read_bytes()).hexdigest(),
            "copy_record_count": c1c2.pool_fingerprint(copy)["record_count"],
            "planted_row": planted,
            "planted_row_result": planted_row,
            "verdict": v.as_dict(),
        }
        # also: does C1 catch the copy against the live pool's fingerprint? (it must)
        out["results"]["C1_copy_vs_live_fingerprint"] = c1c2.check_c1_pool_fingerprint(
            {"prepass_fingerprints": {"blockB_p1_prepass": c1c2.pool_fingerprint(POOL_B)}},
            {"blockB_p1_prepass": copy}).as_dict()

    OUT.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    # one-screen summary
    def line(k: str) -> str:
        r = out["results"][k] if "verdict" not in out["results"][k] or isinstance(out["results"][k].get("verdict"), str) else out["results"][k]["verdict"]
        return f"{k:40s} {r['verdict']:14s} eligible={r.get('eligible_count')} fired={r.get('fired_count')} {'; '.join(r.get('reasons', []))[:90]}"
    for k in ("C1_blockA_manifest_meta_as_receipt", "C1_blockB_no_receipt", "C2_blockA_live",
              "C2_blockB_live", "C2_blockB_COPY_planted_504", "C1_copy_vs_live_fingerprint"):
        print(line(k))
    pr = out["results"]["C2_blockB_COPY_planted_504"]["planted_row_result"]
    print(f"planted row {PLANTED_UID}: rendered_by_loader={pr and pr['rendered_by_loader']}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
