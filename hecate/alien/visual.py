"""Phase 2 preparation (directive SECOND PHASE): unlabeled, matched K / ALIEN /
NOISE sets for rendering in a Prometheus Visual Cortex, with an explicit
map from every visual channel to a source variable, and a separate key so a
human observer's calls can be scored against hidden ground truth.

Nothing here is rendered and no human is involved yet.

    python -m hecate.alien.visual     # -> hecate/alien/visual/{sets.json, key.json, README.md}
"""

from __future__ import annotations

import json
import os
import random

from hecate.alien.dataset import OUT
from hecate.alien.systems import dims_of, header, trajectory

HERE = os.path.dirname(os.path.abspath(__file__))
VIS = os.path.join(HERE, "visual")
SEED = 20260930


def build(per_family=1):
    with open(os.path.join(OUT, "answer_key.json"), encoding="utf-8") as fh:
        key = json.load(fh)
    rng = random.Random(SEED)
    fams = ["tab", "graph", "rewrite", "vm", "map"]
    chosen = []
    for f in fams:
        aliens = sorted(s for s, e in key.items() if e["family"] == f and e["class"] == "ALIEN_LAWFUL"
                        and not e.get("adversarial") and key[e["matched_to"]]["null_type"] != "DESTROY")
        knowns = sorted(s for s, e in key.items() if e["family"] == f and e["class"] == "KNOWN_LAWFUL")
        for a in rng.sample(aliens, per_family):
            chosen += [a, key[a]["matched_to"]]
        chosen += rng.sample(knowns, per_family)
    ids = rng.sample(range(1000, 9999), len(chosen))
    sets, vkey = [], {}
    for sid, vid in zip(chosen, ids):
        e = key[sid]
        p = e["params"]
        dims = dims_of(p)
        r = random.Random(f"{SEED}-{sid}")
        runs = [trajectory(p, tuple(r.randrange(d) for d in dims), 40) for _ in range(12)]
        name = f"VC-{vid}"
        sets.append({
            "id": name, "family_shape": e["family"], "header": header(p),
            "channels": [{"channel": i, "source_variable": f"position {i}", "range": [0, d - 1]}
                         for i, d in enumerate(dims)],
            "graph_links": (p.get("base") or p).get("edges"),
            "runs": [[list(s) for s in t] for t in runs]})
        vkey[name] = {"sys_id": sid, "class": e["class"], "null_type": e["null_type"],
                      "planted": e["planted"], "matched_to": e["matched_to"]}
    rng.shuffle(sets)                   # construction order would leak class
    return sets, vkey


README = """# Visual Cortex phase-2 set (prepared, not run)

sets.json: 15 unlabeled systems (per family: one standard alien, its
incompressible matched null, one known), 12 runs x 40 steps each. Every
visual channel maps to exactly one source variable ("channel i" = state
position i, range given); graph systems carry their link list, so a node
layout can be drawn from source structure, not invented.

key.json: hidden answer key (class, null type, planted properties) -- do
not open during an observation session. A human observer's calls
(structured / unstructured / anomaly at channel c, run r, step t) are
scored against key.json by the same rules as the model tasks; an anomaly
that cannot be mapped back to a channel and step is not scored as a hit.

Suggested renderings (any must preserve the channel->variable map):
lattice (position x time raster per run), field (state as a point cloud
over time), graph (node colour = value on the listed links), glyph strip
(rewrite family). Interactions to try: freeze, step, perturb one channel
(requires the simulator: hecate.alien.systems.step with the key's params).
"""


if __name__ == "__main__":
    sets, vkey = build()
    os.makedirs(VIS, exist_ok=True)
    with open(os.path.join(VIS, "sets.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(sets, ensure_ascii=True) + "\n")
    with open(os.path.join(VIS, "key.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(vkey, indent=1, ensure_ascii=True, default=int) + "\n")
    with open(os.path.join(VIS, "README.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(README)
    print(len(sets), "systems exported")
