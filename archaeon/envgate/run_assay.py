"""ENVGATE-01 runner: --freeze writes PREREG.json once; --run verifies code hashes + PREFLIGHT PASS, then runs every block (fixed
allocation, all blocks launched together, no early look); --report runs the frozen analysis.

    python -m archaeon.envgate.run_assay --freeze
    python -m archaeon.envgate.run_assay --run --workers 16
    python -m archaeon.envgate.analyze
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.envgate import mechanism as M

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREREG = HERE / "PREREG.json"; PREFLIGHT = HERE / "PREFLIGHT.json"; RUNS = HERE / "runs"
SCHEDULE = {"K_chambers": 2048, "dwell": 64, "refills": 1024}
BLOCKS = list(range(16))
HASHED = ["archaeon/envgate/mechanism.py", "archaeon/envgate/engine.py", "archaeon/envgate/ruler.py", "archaeon/envgate/block.py",
          "archaeon/envgate/analyze.py", "archaeon/envgate/run_assay.py", "archaeon/envgate/preflight.py",
          "archaeon/z80atlas/vm.py", "archaeon/z80atlas/engine.py", "archaeon/z80atlas/tasks.py", "archaeon/z80atlas/grammar.py",
          "archaeon/z80atlas/census/copier_census.py", "archaeon/z80atlas/census/HITS.json", "archaeon/z80atlas/census/RESULTS.json"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def hashes() -> dict:
    return {h: sha(REPO / h) for h in HASHED}


def freeze(stamp: str) -> int:
    if PREREG.exists():
        print("REFUSED: PREREG.json exists (write-once; a changed design needs ENVGATE-02)"); return 2
    pf = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    if pf["verdict"] != "PASS" or pf["schedule"] != SCHEDULE:
        print("REFUSED: preflight must PASS for this exact schedule"); return 3
    sup = pf["design_support"]["support"]
    pr = {"schema": "archaeon.envgate.prereg.v1", "assay": M.ASSAY_ID, "frozen_at_utc": stamp, "mechanism_digest": M.digest(SCHEDULE),
          "not_a_continuation_of": "Z80 x Atlas 72-hour campaign (frozen input; code/records unchanged)",
          "directive": "roles/Archaeon/prompts/2026-09-24_environmental_gating/00_OPERATOR_DIRECTIVE.md",
          "question": "Does access to a small set of environmental input values causally control whether random vmcopy32 self-copiers establish persistent reproductive lineages?",
          "mechanism": M.mechanism_spec(SCHEDULE), "held_rationale": M.HELD_RATIONALE, "sham_rule": M.SHAM_RULE,
          "arms": {k: {"blocked": list(v["blocked"]), "replacement_pool_size": len(v["pool"])} for k, v in M.ARMS.items()},
          "transform": M.__doc__.split("Input transforms.")[1].strip(),
          "blocks": BLOCKS, "schedule": SCHEDULE, "arrivals_per_arm_per_block": SCHEDULE["K_chambers"] * SCHEDULE["refills"],
          "epochs_per_world": SCHEDULE["refills"] * SCHEDULE["dwell"] + M.DEFAULTS["persistence_multiple"] * 60 + 1,
          "exposure_planning": {"census_density": sup["census_exact_density"], "expected_exact_copier_arrivals_per_block": sup["expected_exact_copier_arrivals_per_block"],
                                "expected_total": sup["expected_exact_copier_arrivals_total_16_blocks"], "expected_gate_available_per_block": sup["expected_gate_available_exact_arrivals_per_block"],
                                "throughput_basis": "engineering pilot block -1 (excluded): 16,384 arrivals x 5 arms in 40.8 s; dwell 64 ~ one max_age lifetime per arrival",
                                "chance_single_gate_fires_during_dwell": round(1 - (255 / 256) ** SCHEDULE["dwell"], 4)},
          "endpoint": {"name": "ESTABLISHED_RANDOM_INFLOW_LINEAGE",
                       "definition": ["founder origin random_inflow; world holds no other founder class", "lineage has ecology members (left the chamber; chambers are write-protected)",
                                      ">= 1 endogenous birth", "founder removed from its chamber (refill or end of inflow) -- the only original member",
                                      "lineage alive in the ecology at removal + %d epochs (%d x max_age)" % (M.DEFAULTS["persistence_multiple"] * 60, M.DEFAULTS["persistence_multiple"]),
                                      "peak ecology population >= %.2f x 128 OR max generation depth >= %d" % (M.DEFAULTS["min_pop_frac"], M.DEFAULTS["min_generation"]),
                                      "lineage = descendants of ONE arrival (primary lineage id); independent arrivals are different lineages"],
                       "fidelity": "recorded as a phenotype, never a gate"},
          "analysis": __import__("archaeon.envgate.analyze", fromlist=["x"]).__doc__, "preflight_sha256": sha(PREFLIGHT), "preflight_verdict": pf["verdict"],
          "code_sha256_lf_normalised": hashes(),
          "stop_conditions": ["hash mismatch at --run", "preflight not PASS", "any block errors (rerun that block from its own seeds; never patched)",
                              "a threshold/endpoint change after results -> ENVGATE-02"],
          "specimen_policy": "84616cf8257b is one control reference among census copiers; never seeded into treatment, never a target, gate 121 not used in design"}
    PREREG.write_text(json.dumps(pr, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"prereg": str(PREREG), "digest": pr["mechanism_digest"], "arrivals_per_arm_per_block": pr["arrivals_per_arm_per_block"]})); return 0


def _block(b: int) -> str:
    from archaeon.envgate.block import run_block
    r = run_block(b, SCHEDULE); p = RUNS / ("block_%02d.json" % b)
    p.write_text(json.dumps(r, default=str) + "\n", encoding="utf-8", newline="\n"); return str(p)


def run(workers: int) -> int:
    pr = json.loads(PREREG.read_text(encoding="utf-8"))
    if hashes() != pr["code_sha256_lf_normalised"]:
        bad = [k for k, v in hashes().items() if pr["code_sha256_lf_normalised"].get(k) != v]; print("STOP: code changed after preregistration: %s" % bad); return 3
    if sha(PREFLIGHT) != pr["preflight_sha256"]:
        print("STOP: preflight record changed"); return 3
    RUNS.mkdir(exist_ok=True); t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        for fu in as_completed([ex.submit(_block, b) for b in pr["blocks"]]):
            print(json.dumps({"done": fu.result(), "elapsed_s": round(time.time() - t0)}), flush=True)
    man = {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(RUNS.glob("block_*.json"))}
    (HERE / "RUNS_MANIFEST.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--freeze", metavar="UTC"); ap.add_argument("--run", action="store_true"); ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args(argv)
    if a.freeze: return freeze(a.freeze)
    if a.run: return run(a.workers)
    ap.print_help(); return 1


if __name__ == "__main__":
    sys.exit(main())
