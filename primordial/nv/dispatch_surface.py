"""E-R6-3 (SWARM_R6 s5 E (3)): the dispatch surface backend = f(world, batch, representation, residency, hardware), read
from COMMITTED rows only -- E-R5-3 GPU-1/GPU-2 and D-R5-2. No new timing; nothing is interpolated.

A cell is MEASURED only where a committed timing row (kind timing, status record, exactness PASS, speed_status VALID)
exists at exactly that (world, batch, representation, residency, threads). The winner is the smallest wall among the
backends measured in that cell; `ratio` = runner-up wall / winner wall. Every other region is UNMEASURED.

Estimator notes carried into the table (feedback: ratio of unlike estimators):
  GPU-1 warp wall = kernel median of 3 + ONE cold h2d draw (r5_harness.gpu1_cell). D-R5-2 re-measured h2d at 16384+ as
  a median of 11 (alloc / assign / pinned); where it exists the table adds the composite kernel median + warm h2d
  median and says so. At 1024 / 4096 there is no warm h2d median: those warp walls keep the single cold draw.
  GPU-2 torch paths step all T ticks; B6 numba stops an env at its done tick (same fitness, different work).

    python -m primordial.nv.dispatch_surface --out roles/Nestor/sidequests/graphworld/E_R6_3_DISPATCH_SURFACE.md
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
GPU1 = [f"primordial/ledger/rows/E/E-R5-3-gpu1-n{n}.jsonl" for n in (1024, 4096, 16384, 65536)]
GPU2 = [f"primordial/ledger/rows/E/E-R5-3-gpu2-{f}.jsonl" for f in ("linear", "tt_digits")]
D52 = "primordial/ledger/rows/D/D-R5-2-h2d-cold-warm.jsonl"
THREADS = (1, 2, 4, 8)
HARDWARE = "RTX 5060 Ti 16 GB (driver 576.88) + host CPU, numba threads 1-8"


def load(path) -> list[dict]:
    return [json.loads(l) for l in (ROOT / path).read_text(encoding="utf-8").splitlines() if l.strip()]


def valid(r: dict) -> bool:
    return (r.get("kind") == "timing" and r.get("status") == "record" and r.get("exactness") == "PASS"
            and r.get("speed_status") == "VALID")


def blob(path) -> str:
    q = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%h", "--", str(path)], capture_output=True, text=True)
    return q.stdout.strip() or "uncommitted"


def pick(walls: dict) -> dict:
    order = sorted(walls, key=walls.get)
    w = order[0]
    return {"winner": w, "wall_s": walls[w], "runner_up": order[1] if len(order) > 1 else None,
            "ratio": walls[order[1]] / walls[w] if len(order) > 1 and walls[w] > 0 else None, "walls": walls}


def gpu1_cells(rows_by_batch: dict, d52: list[dict]) -> list[dict]:
    warm_h2d = {r["batch_size"]: r["wall_s"] for r in d52 if valid(r) and r["backend"] == "h2d_alloc"}
    out = []
    for n, rows in sorted(rows_by_batch.items()):
        rs = [r for r in rows if valid(r)]
        numba = {r["threads"]: r["wall_s"] for r in rs if r["backend"].startswith("numba_t")}
        warp = next((r for r in rs if r["backend"] == "warp_cuda"), None)
        for k in THREADS:
            base = {"question": "GPU-1", "world": "lane B B1 world (world_seed 4)", "batch": n,
                    "representation": "world step only (open-loop actions, no brain)", "threads": k,
                    "hardware": HARDWARE}
            if k not in numba or warp is None:
                out.append(dict(base, residency="-", status="UNMEASURED"))
                continue
            out.append(dict(base, residency="warp: host state, h2d copy per call (ONE cold draw)", status="MEASURED",
                            **pick({f"numba_t{k}": numba[k], "warp_cuda": warp["wall_s"]})))
            if n in warm_h2d:
                comp = warp["kernel_s"] + warm_h2d[n]
                out.append(dict(base, residency="warp: host state, h2d = D-R5-2 warm alloc median of 11 (composite)",
                                status="MEASURED_COMPOSITE", **pick({f"numba_t{k}": numba[k], "warp_cuda_composite": comp})))
    return out


def gpu2_cells(rows_by_family: dict) -> list[dict]:
    out = []
    for fam, rows in sorted(rows_by_family.items()):
        rs = [r for r in rows if valid(r)]
        numba = {r["threads"]: r["wall_s"] for r in rs if r["backend"] == "b6_numba"}
        gpu = {r["backend"]: r["wall_s"] for r in rs if r["backend"] in ("torch_eager", "graph_k1", "graph_kT")}
        n = rs[0]["batch_size"] if rs else None
        for k in THREADS:
            base = {"question": "GPU-2", "world": "B6 fused closed loop (lane B B1 world)", "batch": n,
                    "representation": f"closed loop, {fam} brain", "threads": k, "hardware": HARDWARE,
                    "residency": "numba: host; torch: GPU-resident loop (initial state in, fitness out)"}
            if k not in numba or not gpu:
                out.append(dict(base, status="UNMEASURED"))
                continue
            out.append(dict(base, status="MEASURED", **pick({f"b6_numba_t{k}": numba[k], **gpu})))
    return out


UNMEASURED = [
    "GPU-1 batch < 1024, > 65536, and every batch between 1024 / 4096 / 16384 / 65536 (no interpolation)",
    "GPU-1 warm-h2d composite at 1024 and 4096 (D-R5-2 measured h2d at 16384..131072 only)",
    "GPU-1 with pinned or resident state end to end (D-R5-2 timed pinned h2d copies, not a pinned kernel run)",
    "GPU-1 with any brain in the loop",
    "GPU-2 any batch other than 8192; families other than linear / tt_digits (tt_feat, transformer, int4a4 codebook)",
    "GPU-2 with done-tick early exit on the GPU side (torch steps all T)",
    "any world other than lane B's B1 / B6 world: graphworld_b2, NK stub, R16 w-cells",
    "numba threads > 8; any host other than this machine; any GPU other than the RTX 5060 Ti",
    "GPU-3 precision (fp16 resident closed loop): PRODUCTION_CANDIDATE, not in this table",
]


def build() -> dict:
    by_batch = {load(p)[0]["batch_size"]: load(p) for p in GPU1}
    by_fam = {p.rsplit("-", 1)[1].split(".")[0]: load(p) for p in GPU2}
    cells = gpu1_cells(by_batch, load(D52)) + gpu2_cells(by_fam)
    return {"sources": {p: blob(p) for p in GPU1 + GPU2 + [D52]}, "cells": cells, "unmeasured": UNMEASURED}


def fmt(x) -> str:
    return "-" if x is None else (f"{x * 1e3:.3f}" if isinstance(x, float) else str(x))


def markdown(doc: dict) -> str:
    L = ["# E-R6-3 dispatch surface (committed rows only; no new timing)", "",
         "backend = f(world, batch, representation, residency, hardware). Walls in ms (median of the row's reps).",
         "Generated by `python -m primordial.nv.dispatch_surface`; winner = smallest measured wall in the cell.", "",
         "Sources (path @ last commit):"]
    L += [f"- {p} @ {s}" for p, s in doc["sources"].items()]
    L += ["", "| q | world | batch | representation | residency | threads | status | winner | wall ms | runner-up | ratio |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in doc["cells"]:
        ru = c.get("runner_up")
        L.append(f"| {c['question']} | {c['world']} | {c['batch']} | {c['representation']} | {c['residency']} | "
                 f"{c['threads']} | {c['status']} | {c.get('winner', '-')} | {fmt(c.get('wall_s'))} | "
                 f"{'-' if ru is None else ru + ' ' + fmt(c['walls'][ru])} | "
                 f"{'-' if c.get('ratio') is None else format(c['ratio'], '.2f')} |")
    L += ["", f"Hardware for every MEASURED cell: {HARDWARE}.", "", "## UNMEASURED regions (never interpolated)", ""]
    L += [f"- {u}" for u in doc["unmeasured"]]
    L += ["", "## Estimator caveats", "",
          "- GPU-1 warp wall = kernel median of 3 + ONE cold h2d draw. The E-R5-3 65536 reading (numba wins) was withdrawn:",
          "  D-R5-2 refuted it (warm h2d median + kernel = 8.43 ms < numba t8 10.36 ms). The composite rows use D's warm",
          "  alloc h2d median of 11 with E's kernel median of 3: two committed medians from two jobs, summed, not re-timed.",
          "- GPU-2: B6 numba stops an env at done; torch steps all T. Winners compare wall for the same fitness output.",
          "- A thread count here is the numba thread count in the timing call; the broker grants tokens per job (k* = 2)."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    doc = build()
    text = json.dumps(doc, indent=1) if a.json else markdown(doc)
    if a.out:
        (ROOT / a.out).write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
