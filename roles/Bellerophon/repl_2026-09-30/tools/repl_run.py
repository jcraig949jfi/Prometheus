"""E-BEL-REPL-01 production runner (frozen with PREREG.md; nothing here may change after the freeze commit).

One run = one (pair s, arm) with arm in {ZERO, P90, P75}:
  cell  grounding G1 ENDOGENOUS_PARTIAL/Z80_64 (pilot_worlds.CELL), ticks 2000;
  world ZERO -> reg_world ZERO; P90 -> CARRIED reg_zero_p 0.9; P75 -> CARRIED reg_zero_p 0.75;
  seed  32_000_000 + s (same seed in every arm of a pair); founder F[s % len(F)] (FOUNDERS.json), transplanted as a quarter of
        the population into a random majority (World init_tapes).
Instrument, every 100 ticks (and at extinction): for each DISTINCT live genome, its state_free profile under the frozen
battery (Z, R1, R2) and under the K4 alternative battery (R3, R4), cached per genome; and which lineage sets carry it:
  L = causal lineage (Org.lineage) of the founder copies at tick 0 -- NPE's "accepted replication whose parent is in L; a member
      overwritten by a non-L source leaves L";
  G = genetic lineage (Org.glineage) of the founder copies at tick 0 -- BEE's native descent label (PRIMARY; the smoke run
      showed causal L transfers on 1-byte ENDOGENOUS_PARTIAL writes, PREREG s3);
  FM = founder material by CONTENT: the genome equals the founder at >= 16 of its 64 positions (chance ~0.25 positions) (K3).
Per checkpoint it records: alive, L_share, G_share, free (distinct STATE_FREE genomes), free_in_L, free_in_G, free_alt,
free_alt_in_L, free_alt_in_G, FM_share, free_in_FM. Scoring is repl_analysis.py; this file only measures.
    python -I repl_run.py --arm P90 --s0 0 --n 10 --out <jsonl>        (appends; a pair already present is skipped)
"""
import argparse, json, pathlib, random, sys, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
from prometheus.z80atlas.world import Config, World  # noqa: E402
import state_free as SF  # noqa: E402
from pilot_worlds import CELL  # noqa: E402

ARMS = {"ZERO": {"reg_world": "ZERO"}, "P90": {"reg_world": "CARRIED", "reg_zero_p": 0.9},
        "P75": {"reg_world": "CARRIED", "reg_zero_p": 0.75}}
SEED0 = 32_000_000
TICKS = 2000
EVERY = 100
FM_MIN = 16
_ra = random.Random("E-BEL-REPL-01|R-alt")
R3 = tuple(_ra.randrange(256) for _ in range(6)) + (bool(_ra.getrandbits(1)), bool(_ra.getrandbits(1)))
R4 = tuple(_ra.randrange(256) for _ in range(6)) + (bool(_ra.getrandbits(1)), bool(_ra.getrandbits(1)))
SF.ENTRY.update({"R3": R3, "R4": R4})


def founders():
    return json.loads((HERE.parent / "FOUNDERS.json").read_text(encoding="utf-8"))["tapes"]


def one(arm, s):
    F = founders(); fhex = F[s % len(F)]
    ftape = bytes.fromhex(fhex)
    cfg = Config(**CELL, ticks=TICKS, init_tapes=(fhex,), **ARMS[arm])
    w = World(cfg, SEED0 + s)
    fl = {o.lineage for o in w.cells if o is not None and o.mechanism == "transplant"}
    fg = {o.glineage for o in w.cells if o is not None and o.mechanism == "transplant"}
    cache = {}

    def prof(t):
        if t not in cache:
            c = {e: SF.competent(t, cfg, e)[0] for e in ("Z", "R1", "R2", "R3", "R4")}
            cache[t] = (c["R1"] and c["R2"], c["R3"] and c["R4"])
        return cache[t]

    cps = []; t0 = time.perf_counter()

    def checkpoint():
        alive = [o for o in w.cells if o is not None]
        n = len(alive)
        by = {}
        for o in alive:
            by.setdefault(bytes(o.tape), []).append(o)
        free = free_L = free_G = alt = alt_L = alt_G = free_FM = 0; fm_orgs = 0
        for t, os_ in by.items():
            sf, sa = prof(t)
            inL = any(o.lineage in fl for o in os_); inG = any(o.glineage in fg for o in os_)
            fm = sum(1 for i in range(min(len(t), len(ftape))) if t[i] == ftape[i]) >= FM_MIN
            fm_orgs += len(os_) if fm else 0
            if sf:
                free += 1; free_L += inL; free_G += inG; free_FM += fm
            if sa:
                alt += 1; alt_L += inL; alt_G += inG
        cps.append({"tick": w.tick, "alive": n, "distinct": len(by),
                    "L_share": (sum(o.lineage in fl for o in alive) / n) if n else 0.0,
                    "G_share": (sum(o.glineage in fg for o in alive) / n) if n else 0.0,
                    "free": free, "free_in_L": free_L, "free_in_G": free_G, "free_alt": alt, "free_alt_in_L": alt_L,
                    "free_alt_in_G": alt_G, "FM_share": (fm_orgs / n) if n else 0.0, "free_in_FM": free_FM})

    founder_free = prof(bytes.fromhex(fhex)[:cfg.L].ljust(cfg.L, b"\0"))
    checkpoint()
    for _ in range(TICKS):
        w.step()
        extinct = not any(o is not None for o in w.cells)
        if w.tick % EVERY == 0 or extinct:
            checkpoint()
        if extinct:
            break
    return {"pair": s, "arm": arm, "seed": SEED0 + s, "founder": fhex, "founder_state_free": founder_free[0],
            "founder_alt_free": founder_free[1], "checkpoints": cps, "genomes_profiled": len(cache),
            "wall_s": round(time.perf_counter() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=tuple(ARMS)); ap.add_argument("--s0", type=int, required=True)
    ap.add_argument("--n", type=int, required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            r = json.loads(line); done.add((r["arm"], r["pair"]))
    for s in range(a.s0, a.s0 + a.n):
        if (a.arm, s) in done:
            continue
        rec = one(a.arm, s)
        with out.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
