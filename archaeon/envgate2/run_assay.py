"""ENVGATE-02 runner: --freeze (write-once PREREG; requires PREFLIGHT PASS), --run (hash-verified; all blocks at once; no early look).
    python -m archaeon.envgate2.run_assay --freeze UTC ; python -m archaeon.envgate2.run_assay --run --workers 24 ; python -m archaeon.envgate2.analyze
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.envgate2 import mechanism as M

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREREG = HERE / "PREREG.json"; PREFLIGHT = HERE / "PREFLIGHT.json"; RUNS = HERE / "runs"
SCHEDULE = {"K_chambers": 2048, "dwell": 64, "refills": 512}
BLOCKS = list(range(24))
HASHED = ["archaeon/envgate2/mechanism.py", "archaeon/envgate2/analyze.py", "archaeon/envgate2/run_assay.py", "archaeon/envgate2/preflight.py",
          "archaeon/lineage/core.py", "archaeon/lineage/taint_vm.py", "archaeon/lineage/assay_block.py", "archaeon/envgate/mechanism.py",
          "archaeon/envgate/engine.py", "archaeon/envgate/ruler.py", "archaeon/envgate/OFFSPRING_VIABILITY.json",
          "archaeon/z80atlas/vm.py", "archaeon/z80atlas/engine.py", "archaeon/z80atlas/tasks.py", "archaeon/z80atlas/grammar.py",
          "archaeon/z80atlas/census/copier_census.py", "archaeon/z80atlas/census/HITS.json", "archaeon/z80atlas/census/RESULTS.json",
          "archaeon/tests/test_lineage_attribution.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def hashes() -> dict:
    return {h: sha(REPO / h) for h in HASHED}


POWER = ("Planning from ENVGATE-01 copier-founded establishment per block at full exposure (U 2.9; k~3 arm ~1.1) scaled to half exposure: "
         "expected per block U ~1.5, RRIGHT ~0.55, RWEAK ~0.2, R128 ~0.03, BAND0 ~0.03. With 24 blocks: P2 (RRIGHT>R128) ~10 positive vs <1 negative "
         "block -> power high; P3 (RRIGHT>RWEAK) ~40% power; Page's L high. Gate needs P2 OR P3. Half of ENVGATE-01's per-block exposure, 24 blocks "
         "(more independent units at ~0.75 of ENVGATE-01's total tape exposure).")


def freeze(stamp: str, slow_test_record: str) -> int:
    if PREREG.exists(): print("REFUSED: PREREG exists"); return 2
    pf = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    if pf["verdict"] != "PASS": print("REFUSED: preflight not PASS"); return 3
    slow = json.loads(Path(slow_test_record).read_text(encoding="utf-8"))
    pr = {"schema": "archaeon.envgate2.prereg.v1", "assay": M.ASSAY_ID, "frozen_at_utc": stamp, "mechanism_digest": M.digest(SCHEDULE, BLOCKS),
          "directive": "roles/Archaeon/prompts/2026-09-24_envgate_adjudication_rie/00_OPERATOR_DIRECTIVE.md", "claim": M.__doc__.split("Claim under test")[1].split("Arm construction")[0].strip(),
          "spec": M.spec(SCHEDULE, BLOCKS), "predictions_from_frozen_viability_map": M.predictions(), "power": POWER,
          "arrivals_per_arm_per_block": SCHEDULE["K_chambers"] * SCHEDULE["refills"], "analysis": __import__("archaeon.envgate2.analyze", fromlist=["x"]).__doc__,
          "attribution_tests": {"passed": pf["attribution_tests"]["PASS"] and slow["passed"], "fast": pf["attribution_tests"]["summary"], "slow_block13": slow},
          "preflight_sha256": sha(PREFLIGHT), "code_sha256_lf_normalised": hashes(),
          "stop_conditions": ["hash mismatch", "preflight not PASS", "a block errors (rerun from its own seeds)", "any change after results -> ENVGATE-03"]}
    PREREG.write_text(json.dumps(pr, indent=1, default=str) + "\n", encoding="utf-8", newline="\n"); print(json.dumps({"digest": pr["mechanism_digest"]})); return 0


def _block(b):
    from archaeon.lineage.assay_block import run_block
    r = run_block("envgate2", b, SCHEDULE, M.ARMS); p = RUNS / ("block_%02d.json" % b)
    p.write_text(json.dumps(r, default=str) + "\n", encoding="utf-8", newline="\n"); return str(p)


def run(workers: int) -> int:
    pr = json.loads(PREREG.read_text(encoding="utf-8"))
    if hashes() != pr["code_sha256_lf_normalised"]: print("STOP: code changed after preregistration", [k for k, v in hashes().items() if pr["code_sha256_lf_normalised"].get(k) != v]); return 3
    RUNS.mkdir(exist_ok=True); t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        for fu in as_completed([ex.submit(_block, b) for b in pr["spec"]["blocks"]]):
            print(json.dumps({"done": fu.result(), "elapsed_s": round(time.time() - t0)}), flush=True)
    (HERE / "RUNS_MANIFEST.json").write_text(json.dumps({p.name: {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(RUNS.glob("block_*.json"))}, indent=1) + "\n",
                                             encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--freeze"); ap.add_argument("--slow-test-record"); ap.add_argument("--run", action="store_true"); ap.add_argument("--workers", type=int, default=24)
    a = ap.parse_args()
    sys.exit(freeze(a.freeze, a.slow_test_record) if a.freeze else (run(a.workers) if a.run else 1))
