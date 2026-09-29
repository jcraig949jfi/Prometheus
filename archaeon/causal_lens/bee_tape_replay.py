"""Bounded FULL replay of ONE BEE run on Bellerophon's FROZEN harness (read-only), observing tapes only.

Standalone on purpose: the harness package is also named `prometheus`, so this script must not import the repo's packages.
Observation = the same stashes traced_replay.py makes (writer tape at execution start), plus the child, the writer's post-execution
tape and the replaced occupant's tape per registered offspring. Nothing the world computes is changed.
    python bee_tape_replay.py <rid> <out.json>
"""
import json
import sys
import time

HARNESS = "C:/Users/James/z80atlas_campaign_2026-09-19/code"
RUNS = "C:/Users/James/z80atlas_campaign_2026-09-19/runs"


def main(rid, out):
    sys.path.insert(0, HARNESS)
    from prometheus.z80atlas import grammar as G
    from prometheus.z80atlas import world as W
    spec = json.load(open("%s/%s/config.json" % (RUNS, rid), encoding="utf-8"))
    cfg = G.to_config(spec["vec"], spec["ticks"], spec["cells"], spec.get("budget", 256), tuple(spec.get("init_tapes") or ()))
    stash = {}; rows = []

    class Obs(W.World):
        def _execute(self, o, partner_tape, inputs):
            stash["w"] = bytes(o.tape); return super()._execute(o, partner_tape, inputs)

        def _pair_execute(self, a, b, inputs):
            stash["w"] = bytes(a.tape); return super()._pair_execute(a, b, inputs)

        def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
            rows.append([self.tick, parent.id, bytes(child).hex(), (stash.get("w") or bytes(parent.tape)).hex(), bytes(parent.tape).hex(),
                         bytes(replaced.tape).hex() if replaced is not None else None, mechanism])
            return super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)

    t0 = time.time(); w = Obs(cfg, spec["seed"]); summary = w.run()
    json.dump({"rid": rid, "births_observed": len(rows), "wall_s": round(time.time() - t0, 1), "cols": ["tick", "writer", "child", "writer_pre", "writer_post", "replaced", "mechanism"],
               "rows": rows}, open(out, "w", encoding="utf-8"))
    print(json.dumps({"rid": rid, "births_observed": len(rows), "wall_s": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
