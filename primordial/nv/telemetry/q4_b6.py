"""Q4: N2 telemetry row for the B6 fused rollout, and the Q1/Q2 refusals re-filed as status aborted.

(a) B6b FusedRollout (linear, world 4, P=128, E7.TRAIN) measured by unpriv.measure. The kernel is CPU
    numba, so every GPU feature must read exactly 0, and the metered rollout must equal E7.rollout.
    A host-sleep arm must move wall.
(b) refusal_rows(): one aborted row per tool/version, summarised by code from committed rows.

usage: python -m primordial.nv.telemetry.q4_b6 --out primordial/ledger/rows/Q/Q4-b6-telemetry.jsonl
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "Q"
REFUSAL_FILES = ("Q1-capture-smoke.jsonl", "Q2-ncu-2026-2-1.jsonl", "Q2b-ncu-2025-2-1.jsonl")


def refusal_rows(rows_by_file: dict) -> list[dict]:
    """rows_by_file: {file name: [row, ...]} -> aborted rows, re-classified by today's classify()."""
    from primordial.nv.telemetry.smoke import classify
    out = []
    for fname, rows in rows_by_file.items():
        for r in rows:
            if r.get("probe") == "control_torch":
                continue
            v = classify(r["probe"], r["rc"], r.get("stdout", ""), r.get("stderr", ""))
            if v == "ok":
                continue
            tool = "nsys" if r["probe"].startswith("nsys") else "ncu" if r["probe"].startswith("ncu") else "cupti"
            ver = r.get("host", {}).get(tool, "") if tool != "cupti" else "torch bundled cupti64_2025.1.1"
            text = r.get("stderr", "") + "\n" + r.get("stdout", "")        # ncu writes its errors to stdout
            first = next((ln.strip() for ln in text.splitlines()
                          if "ERR" in ln or "rror" in ln or "privileges" in ln), "")
            out.append({"status": "aborted", "kind": "capture_refusal", "tool": tool, "tool_version": ver,
                        "probe": r["probe"], "verdict_recorded": r.get("verdict"), "verdict": v,
                        "stderr_first": first[:300], "source_rows": f"primordial/ledger/rows/Q/{fname}",
                        "counter_features": "BLOCKED(ERR_NVGPUCTRPERM)"})
    return out


def b6_rows(P: int = 128, sleep_s: float = 0.05) -> list[dict]:
    import numpy as np

    from primordial.nv.telemetry.unpriv import measure
    from primordial.qd import e7_run as E7
    from primordial.soup.b6.fused import FusedRollout
    g7 = E7.G7(4, "linear")
    rng = np.random.default_rng([6262, 4, 1])
    g = g7.init(rng, P)
    for _ in range(50):
        g = g7.mutate(rng, g)
    ref_fit, ref_cells, _, _ = E7.rollout(g7, g, E7.TRAIN)
    fr = FusedRollout(g7.spec, P, E7.TRAIN, family="linear")
    fr.run(g)                                                      # compile outside the region
    out = []
    for arm, s in (("honest", 0.0), ("cheat_sleep", sleep_s)):
        res = {}

        def region():
            if s:
                time.sleep(s)
            res["r"] = fr.run(g)
        row = measure(region)
        fit, cells = res["r"][0], res["r"][1]
        row.update(arm=arm, workload="B6b_fused_linear_w4_P128_train8", P=P,
                   exact_fitness=bool(np.array_equal(fit, ref_fit)), exact_cells=bool(np.array_equal(cells, ref_cells)),
                   status="control" if arm == "honest" else "cheat")
        out.append(row)
    return out


def judge_b6(rows: list[dict]) -> str:
    h = next(r for r in rows if r["arm"] == "honest")
    c = next(r for r in rows if r["arm"] == "cheat_sleep")
    zero = all(h[k] == 0 for k in ("h2d_bytes", "d2h_bytes", "n_cuda_ops", "peak_mem_bytes"))
    exact = all(r["exact_fitness"] and r["exact_cells"] for r in rows)
    return "PASS" if zero and exact and c["wall_s"] - h["wall_s"] >= 0.045 else "FAIL"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    from primordial.fabric.rows import RowWriter
    by_file = {}
    for f in REFUSAL_FILES:
        with open(ROWS / f, encoding="utf-8") as fh:
            by_file[f] = [json.loads(x) for x in fh if x.strip()]
    with RowWriter(a.out, "Q4-b6-telemetry", commit_every_s=3600) as w:
        for r in refusal_rows(by_file):
            w.write(r)
            print("aborted", r["tool"], r["tool_version"], r["verdict"], "|", r["stderr_first"][:90])
        rows = b6_rows()
        for r in rows:
            w.write(r)
        verdict = judge_b6(rows)
        w.write({"status": "record", "kind": "judge", "verdict": verdict,
                 "features": {r["arm"]: {k: r[k] for k in ("wall_s", "h2d_bytes", "d2h_bytes", "n_cuda_ops",
                                                            "peak_mem_bytes", "kernel_share", "exact_fitness",
                                                            "exact_cells")} for r in rows}})
        print("B6", verdict, json.dumps([{k: r[k] for k in ("arm", "wall_s", "h2d_bytes", "n_cuda_ops",
                                                             "peak_mem_bytes", "exact_fitness")} for r in rows]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
