"""E-003 step 1 (C-001 attribution arc, BEE leg): reproduce a preserved BEE run's birth rows bit-for-bit on the PINNED
frozen harness, before any ancestry tracing.

- Harness: a `git archive 16fc6c2a prometheus` copy (default C:/Users/James/e003_harness_16fc6c2a). It is never imported
  from the working tree. Module sha256 prefixes (LF-normalised, prereg v5 R8) are logged at import and must equal the
  prereg pins: world 5b985241, vm 2536b1ac, grammar 3767d73d, tasks e2c37f76.
- Row generator: roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py (the generator of the preserved rows),
  with its HARNESS path repointed to the pin (v4 s3: "traced_replay's HARNESS path repointed").
- Checks: every birth row equals the preserved row, in order. Self-consistency records (v5 R8): the sha256 of every
  child tape and of the world RNG state after every tick.
    python replay_births.py --config r022153.config.json --births r022153.births.jsonl.gz --out <receipt.json>
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "forensics_2026-09-23" / "tools"
PINS = {"world": "5b985241", "vm": "2536b1ac", "grammar": "3767d73d", "tasks": "e2c37f76"}


def pin_hashes(harness: pathlib.Path) -> dict:
    out = {}
    for m in PINS:
        b = (harness / "prometheus" / "z80atlas" / (m + ".py")).read_bytes().replace(b"\r\n", b"\n")
        out[m] = hashlib.sha256(b).hexdigest()[:8]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True); ap.add_argument("--births", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--harness", default="C:/Users/James/e003_harness_16fc6c2a")
    a = ap.parse_args()
    harness = pathlib.Path(a.harness)
    got = pin_hashes(harness)
    if got != PINS:
        raise SystemExit("harness pin mismatch: %s != %s" % (got, PINS))
    sys.path.insert(0, str(TOOLS))
    import traced_replay as TR                                      # noqa: E402
    TR.HARNESS = str(harness)                                       # repoint (never the working tree)
    vm, W = TR._install()
    import prometheus.z80atlas.world as world_mod                   # noqa: E402
    loaded_from = pathlib.Path(world_mod.__file__).resolve()
    if harness.resolve() not in loaded_from.parents:
        raise SystemExit("world imported from %s, not the pinned harness" % loaded_from)
    from prometheus.z80atlas import grammar as G
    cj = json.loads(pathlib.Path(a.config).read_text(encoding="utf-8"))
    cfg = G.to_config(cj["vec"], cj["ticks"], cj["cells"], cj["budget"], tuple(cj["init_tapes"] or ()))
    TW = TR._traced_world_class(W)

    child_h = []; rng_h = []
    class TW2(TW):                                                   # observation only: hashes after the fact
        def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
            super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
            child_h.append(hashlib.sha256(bytes(child)).hexdigest()[:16])

        def step(self):
            r = super().step()
            rng_h.append(hashlib.sha256(repr(self.rng.getstate()).encode()).hexdigest()[:16])
            return r

    w = TW2(cfg, cj["seed"])
    w.run()
    got_rows = [json.loads(json.dumps(b)) for b in w.births]
    want = [json.loads(l) for l in gzip.open(a.births, "rt", encoding="utf-8")]
    first_diff = next((i for i, (x, y) in enumerate(zip(got_rows, want)) if x != y), None)
    ok = len(got_rows) == len(want) and first_diff is None
    rec = {"run": cj["id"], "config_sha256": cj.get("config_sha256"), "harness": str(harness), "harness_pins": got,
           "world_loaded_from": str(loaded_from), "births_replayed": len(got_rows), "births_preserved": len(want),
           "bit_for_bit": ok, "first_diff_index": first_diff,
           "preserved_births_sha256": hashlib.sha256(pathlib.Path(a.births).read_bytes()).hexdigest(),
           "child_tape_sha256_chain": hashlib.sha256("".join(child_h).encode()).hexdigest(),
           "rng_state_sha256_chain": hashlib.sha256("".join(rng_h).encode()).hexdigest(), "ticks_recorded": len(rng_h)}
    pathlib.Path(a.out).write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
