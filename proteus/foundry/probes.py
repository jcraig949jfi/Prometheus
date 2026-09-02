"""Probe ensemble: algorithmically generated inputs from a frozen EXTERNAL seed. Amendment A4.

The seed root is the sha256 of the external review addendum that imposed this rule -- a public
value Proteus did not choose. Every probe's channel count, tick count, value count and values
are uniform draws from a splitmix64 stream keyed by (root, probe index). There is no task here.
Nothing is a maze, a sequence, a copy, a parity, or a pattern; the inputs are noise with a
declared shape, and the only thing measured is whether two organisms produce the same
externally visible transcript on the same noise under the same budget.

The relation this induces is called probe_transcript_equivalence and nothing else.
"""
from __future__ import annotations

from .identity import hash_obj
from .prng import SplitMix64, seed_from
from .vm import Player, Meter

ADDENDUM_SHA256 = "4a9fe0cb33fb88acbb64e3bcff23c609f80429ffb46b21040de81527d6510fab"

DEFAULT_ENSEMBLE = {
    "schema_version": "proteus.probe_ensemble.v0",
    "seed_root": ADDENDUM_SHA256,
    "n_probes": 4,
    "n_in_range": [1, 3],
    "n_out_range": [1, 3],
    "ticks_range": [3, 6],
    "values_per_channel_range": [0, 3],
    "budget_cap": 256,
}


def build_probes(cfg: dict = DEFAULT_ENSEMBLE) -> list:
    probes = []
    for k in range(cfg["n_probes"]):
        r = SplitMix64(seed_from("proteus.probe.v0", cfg["seed_root"], k))
        n_in = r.randint(*cfg["n_in_range"])
        n_out = r.randint(*cfg["n_out_range"])
        ticks = r.randint(*cfg["ticks_range"])
        inputs = []
        for _ in range(ticks):
            tick_in = []
            for _ in range(n_in):
                L = r.randint(*cfg["values_per_channel_range"])
                tick_in.append([r.next_u32() for _ in range(L)])
            inputs.append(tick_in)
        probes.append({"index": k, "n_in": n_in, "n_out": n_out, "ticks": ticks,
                       "inputs": inputs, "rnd_seed": r.next_u64()})
    return probes


def ensemble_identity(cfg: dict = DEFAULT_ENSEMBLE) -> str:
    return hash_obj({"cfg": cfg, "probes": build_probes(cfg)})


def run_probe(manifest: dict, probe: dict, budget_cap: int, meter: Meter | None = None) -> list:
    """Transcript of one probe: per tick, the outputs (per channel) and the status. Nothing else."""
    p = Player(manifest)
    state = p.fresh_state()
    rng = SplitMix64(probe["rnd_seed"])
    transcript = []
    for t in range(probe["ticks"]):
        outs, status = p.run_tick(state, probe["inputs"][t], probe["n_out"], rng, meter, budget_cap)
        transcript.append([outs, status])
    return transcript


def run_ensemble(manifest: dict, probes: list, cfg: dict = DEFAULT_ENSEMBLE, meter: Meter | None = None):
    """Full transcript over the ensemble, and its hash (the probe_transcript_equivalence class id)."""
    ts = [run_probe(manifest, pr, cfg["budget_cap"], meter) for pr in probes]
    return ts, hash_obj(ts)
