"""POST-HOC (labelled; written AFTER the frozen verdict DISAPPEARS (K3); feeds no gate or verdict): is the K3 kill real, or
the blind spot of a POSITIONAL content test that cannot see shifted copies?

For every run that scored an event under G (primary), in any arm, this replays the run deterministically with the frozen
runner's code path (repl_run.one's world, seed and founder). It asserts that the replayed checkpoint records equal the
sealed ones (the replay gate). At the event checkpoint (the last checkpoint with >= 1 STATE_FREE genome) it records, for
each STATE_FREE genome carried by G:
  pos_id     positions equal to the founder (the frozen FM test counts >= 16 of 64);
  shift_id   the best positional identity over the 64 cyclic shifts of the genome against the founder;
  kmer4      the share of the genome's 61 4-grams that occur anywhere in the founder (a random tape: ~61/2^32 each, so ~0);
  lcs        the longest common substring with the founder, in bytes.
It also records the same measures for a random-tape null (the tick-0 random majority of the same run).
    python -I posthoc_k3_shift.py <sealed runs_*.jsonl ...> --out <jsonl> [--arm ARM] [--part k --parts n]
"""
import argparse, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3])); sys.path.insert(0, str(HERE))
import repl_run as RR  # noqa: E402
import repl_analysis as RA  # noqa: E402
import state_free as SF  # noqa: E402
from prometheus.z80atlas.world import Config, World  # noqa: E402
from pilot_worlds import CELL  # noqa: E402


def lcs(a, b):
    best = 0; prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1; best = max(best, cur[j])
        prev = cur
    return best


def measures(g, f):
    fk = {f[i:i + 4] for i in range(len(f) - 3)}
    return {"pos_id": sum(x == y for x, y in zip(g, f)),
            "shift_id": max(sum(g[(i + k) % len(g)] == f[i] for i in range(len(f))) for k in range(len(g))),
            "kmer4": sum(g[i:i + 4] in fk for i in range(len(g) - 3)) / (len(g) - 3),
            "lcs": lcs(g, f)}


def replay(rec):
    arm, s = rec["arm"], rec["pair"]
    fhex = rec["founder"]; f = bytes.fromhex(fhex)
    cfg = Config(**CELL, ticks=RR.TICKS, init_tapes=(fhex,), **RR.ARMS[arm])
    w = World(cfg, RR.SEED0 + s)
    fg = {o.glineage for o in w.cells if o is not None and o.mechanism == "transplant"}
    rand0 = [bytes(o.tape) for o in w.cells if o is not None and o.mechanism == "init"][:20]
    target = next(c["tick"] for c in reversed(rec["checkpoints"]) if c["free"] > 0)
    cache = {}

    def sf(t):
        if t not in cache:
            cache[t] = SF.competent(t, cfg, "R1")[0] and SF.competent(t, cfg, "R2")[0]
        return cache[t]

    got = None; checked = 0
    for _ in range(RR.TICKS):
        if w.tick == target:
            break
        w.step()
        if not any(o is not None for o in w.cells):
            break
    alive = [o for o in w.cells if o is not None]
    by = {}
    for o in alive:
        by.setdefault(bytes(o.tape), []).append(o)
    sealed = next(c for c in rec["checkpoints"] if c["tick"] == target)
    G_share = (sum(o.glineage in fg for o in alive) / len(alive)) if alive else 0.0
    free = [t for t in by if sf(t)]
    free_G = [t for t in free if any(o.glineage in fg for o in by[t])]
    gate = (len(alive) == sealed["alive"] and len(by) == sealed["distinct"] and abs(G_share - sealed["G_share"]) < 1e-12
            and len(free) == sealed["free"] and len(free_G) == sealed["free_in_G"])
    return {"arm": arm, "pair": s, "tick": target, "replay_gate": gate, "n_free_G": len(free_G),
            "free_G": [dict(measures(t, f), carriers=len(by[t])) for t in free_G],
            "null_random": [measures(t, f) for t in rand0]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("runs", nargs="+"); ap.add_argument("--out", required=True)
    ap.add_argument("--part", type=int, default=0); ap.add_argument("--parts", type=int, default=1)
    a = ap.parse_args()
    recs = [json.loads(l) for p in a.runs for l in open(p, encoding="utf-8")]
    ev = sorted([r for r in recs if RA.score(r)["event"]], key=lambda r: (r["arm"], r["pair"]))[a.part::a.parts]
    out = pathlib.Path(a.out)
    done = {(json.loads(l)["arm"], json.loads(l)["pair"]) for l in out.read_text().splitlines()} if out.exists() else set()
    for r in ev:
        if (r["arm"], r["pair"]) in done:
            continue
        res = replay(r)
        with out.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(res, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
