"""H2 alpha run: one real CA pass through the whole path, with controls.

NO DISCOVERED-COMPONENT CLAIM. This run exists to show the contract, the
fixtures, the controls and one actual CA execution. There is no rule search,
no matched intervention and no export, so nothing here may be read as evidence
that a CA computed anything. The baselines are present so that any CA number
can be compared with what the readout alone achieves.

    python -m herakles.ca_stream.run_alpha
"""
from __future__ import annotations

import io
import json
import os
import time

import numpy as np

from herakles.ca_stream import core as cs
from herakles.evca import genomes as G

HERE = os.path.dirname(os.path.abspath(__file__))
HORIZON = cs.HORIZON
N_CELLS = cs.N_CELLS
CASES = [("delayed_recall", 0), ("delayed_recall", 1), ("delayed_recall", 2),
         ("delayed_recall", 3), ("temporal_xor", 0), ("temporal_xor", 1)]


def substrates():
    out = [("ca_" + n, lambda n=n: cs.CaSubstrate(G.rule_hex(n), N_CELLS, (0,)))
           for n in G.NAMES]
    out += [
        ("control_shift_register", lambda: cs.ShiftRegister(N_CELLS)),
        ("control_shift_xor_d0", lambda: cs.ShiftXorRegister(N_CELLS, 0)),
        ("control_shift_xor_d1", lambda: cs.ShiftXorRegister(N_CELLS, 1)),
        ("baseline_direct_input", lambda: cs.DirectInput(N_CELLS)),
        ("baseline_frozen_random", lambda: cs.FrozenRandom(N_CELLS, seed=7)),
    ]
    return out


def main():
    t0 = time.perf_counter()
    streams = cs.all_streams(HORIZON)
    parts = cs.partitions(len(streams), 64, 64)
    rows, costs = [], []

    for sub_name, make in substrates():
        sub = make()
        t1 = time.perf_counter()
        feats, ca_steps = cs.run_streams(sub, streams)
        extract_s = time.perf_counter() - t1
        for task, delay in CASES:
            y = cs.build_targets(streams, task, delay)
            mask = cs.warmup_mask(HORIZON, task, delay)
            t2 = time.perf_counter()
            w = cs.fit_readout(feats[parts["train"]], y[parts["train"]], mask)
            train_s = time.perf_counter() - t2
            dev = cs.score_readout(feats[parts["dev"]], y[parts["dev"]],
                                   mask, w)
            conf = cs.score_readout(feats[parts["confirmation"]],
                                    y[parts["confirmation"]], mask, w)
            rows.append({
                "substrate": sub_name, "task": task, "delay": delay,
                "dev_accuracy": dev["accuracy"],
                "confirmation_accuracy": conf["accuracy"],
                "base_rate": conf["base_rate"],
                "above_base": conf["accuracy"] - conf["base_rate"],
                "n_scored_confirmation": conf["n_scored"],
                "readout_parameters": int(w.size),
                "train_seconds": round(train_s, 4),
            })
        costs.append({"substrate": sub_name, "descriptor": sub.descriptor(),
                      "ca_or_substrate_steps": ca_steps,
                      "extraction_seconds": round(extract_s, 3),
                      "feature_width": sub.width})

    out = {
        "kind": "ca_stream_v1", "stage": "alpha",
        "claim_boundary": ("contract, fixtures, controls and one real CA run. "
                           "NO discovered-component claim: no rule search, no "
                           "matched intervention, no export."),
        "update_order": "inject at ports -> exactly one CA step -> read lattice",
        "reset": "before every independent stream, to all zeros",
        "readout_class": ("capacity-limited linear over the CURRENT lattice; "
                          "no undeclared input history"),
        "readout_parameters": N_CELLS + 1,
        "fitting_budget": ("one closed-form ridge solve per (substrate, task); "
                           "lambda %.3f fixed; no restarts; no hyperparameter "
                           "search" % cs.RIDGE_LAMBDA),
        "scope": {"n_cells": N_CELLS, "horizon": HORIZON,
                  "n_streams": len(streams), "ports": [0],
                  "partition": {"train": 64, "dev": 64, "confirmation": 128}},
        "catalogue_digest": cs.catalogue_digest(streams),
        "partition_indices_digest": cs.catalogue_digest(
            np.concatenate([parts["train"], parts["dev"],
                            parts["confirmation"]]).astype(np.uint8)),
        "results": rows, "costs": costs,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    path = os.path.join(HERE, "alpha_results.json")
    io.open(path, "w", encoding="utf-8", newline="").write(
        json.dumps(out, indent=1, sort_keys=True) + "\n")

    print("%-24s %-16s %5s %7s %7s %8s" % ("substrate", "task", "delay",
                                           "dev", "confirm", "vs base"))
    for r in rows:
        print("%-24s %-16s %5d %7.4f %7.4f %+8.4f"
              % (r["substrate"], r["task"], r["delay"], r["dev_accuracy"],
                 r["confirmation_accuracy"], r["above_base"]))
    print()
    print("wrote %s in %.1fs" % (path, out["elapsed_s"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
