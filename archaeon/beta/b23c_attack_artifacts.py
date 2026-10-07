"""B23c -- attack the strongest B23b signal: W-artifacts elites at 1.000 vs constant/blind .44-.49.

Echo twins: for each input channel c and word position j (0..7), a program that reads the j-th word of channel c and
writes it on every output channel. If an echo twin reaches the elite's score, the "competence" is input pass-through,
not a mechanism. Also reported: the world's features and the elite's executed code (archaeon/beta/disasm.py-style
listing is v0-only; graph elites are reported by node count).
"""
import gzip
import json
from pathlib import Path

from archaeon.campaign6.segment import resolve_world
from archaeon.campaign6.worlds.runtime import evaluate_world
from archaeon.beta.b23b_composed_world_audit import RUNS, score

OUT = Path(__file__).resolve().parent / "results"
TARGETS = ["W-artifacts_w50047_persist", "W-artifacts_w50135_persist", "W-artifacts_w50142_persist", "B-worldgen.T4",
           "P-boom_B_shuffle_s3", "P-boom_K_D_persist_s3"]


def echo_manifest(c, j, K):
    g = [3, 5, c, 0]                                     # LDC r5, c  (input channel)
    g += [21, 1, 5, 0] * (j + 1)                         # IN r1, ch r5  (j+1 times: keep the j-th word)
    for ch in range(K):
        g += [3, 2, ch, 0, 23, 1, 2, 0]                  # LDC r2, ch ; OUT r1 on ch r2
    g += [1, 0, 0, 0]
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": 6, "tape_words": max(16, len(g) + 16),
            "genome": g, "code_writable": False, "persist": "none", "tick_budget": 128, "out_cap": 1}


def find(name):
    for fam in RUNS.iterdir():
        p = fam / name
        if p.is_dir():
            return p
    return None


def main():
    rows = []
    for name in TARGETS:
        exp = find(name)
        c = json.load(gzip.open(sorted(exp.glob("chunk_*.json.gz"))[-1]))
        wd = c["spec"]["world"]; world = resolve_world(wd); seed = c["spec"].get("provenance", {}).get("seed", 0) or 0
        pop = c["out"]["checkpoint_out"]["population"]
        er, em = max(((score(o["manifest"], world, seed), o["manifest"]) for o in pop), key=lambda z: z[0])
        n_in = len(world.observe(world.reset(seed, 0, None)))
        echoes = {}
        for ch in range(n_in):
            for j in range(8):
                echoes["c%d_j%d" % (ch, j)] = round(score(echo_manifest(ch, j, world.K), world, seed), 4)
        best_echo = max(echoes.items(), key=lambda kv: kv[1])
        rows.append({"exp": name, "features": world.features, "K": world.K, "n_in_channels": n_in, "elite": round(er, 4),
                     "best_echo": best_echo, "echo_reaches_elite": best_echo[1] >= er - .02,
                     "elite_substrate": "graph" if "nodes" in em else "v0",
                     "elite_size": len(em["nodes"]) if "nodes" in em else len(em["genome"]) // 4})
        print(json.dumps(rows[-1]), flush=True)
    (OUT / "B23c_result.json").write_text(json.dumps({"probe": "B23c", "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
