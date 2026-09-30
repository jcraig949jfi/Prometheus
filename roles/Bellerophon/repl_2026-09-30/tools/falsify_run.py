"""E-BEL-REPL-02 runner (frozen with PREREG_02.md): the E-BEL-REPL-01 residue under adversarial transformations.

Residue under test: in BEE (grounding G1 ENDOGENOUS_PARTIAL/Z80_64 cell), a PARTIAL register scaffold (CARRIED with zero reset
at p = 0.9) makes STATE_FREE genomes come to DOMINATE the population far more often than an always-present scaffold (ZERO).
The readout is LABEL-FREE: no lineage label is used anywhere.

Each ARM = (transformation, register world). Every transformation is run in both P90 and ZERO on the same seeds:
  BASE   the REPL-01 world (founders transplanted, ENDOGENOUS_PARTIAL, mutation MED), fresh seeds
  NOFND  no founders: random populations only (init RANDOM, no init_tapes)
  COPY   reproduction ENDOGENOUS_COPY (a birth needs a full-window copy) instead of ENDOGENOUS_PARTIAL
  MUTLO  mutation_rate LOW
plus RANDOM: BASE with reg_world RANDOM (every execution from uniform random registers; the strongest payoff, positive control).
Per checkpoint (every 250 ticks, and at extinction): alive; distinct; free_orgs / free_orgs_strict = organisms whose genome
is STATE_FREE under the frozen ruler (state_free.py) / under a STRICT ruler (rate >= 0.8 AND window match 100%, R1 and R2);
fm_orgs = organisms carrying founder CONTENT (>= 16/64 positions; BASE/COPY/MUTLO only). Nothing else.
    python -I falsify_run.py --arm BASE:P90 --s0 0 --n 10 --out <jsonl>
"""
import argparse, json, pathlib, random, sys, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3])); sys.path.insert(0, str(HERE))
from prometheus.z80atlas import vm  # noqa: E402
from prometheus.z80atlas.world import Config, World  # noqa: E402
import state_free as SF  # noqa: E402
from pilot_worlds import CELL  # noqa: E402

SEED0 = 33_000_000
TICKS = 2000
EVERY = 250
FM_MIN = 16
REG = {"P90": {"reg_world": "CARRIED", "reg_zero_p": 0.9}, "ZERO": {"reg_world": "ZERO"}, "RANDOM": {"reg_world": "RANDOM"}}
TRANS = {"BASE": {}, "NOFND": {}, "COPY": {"reproduction": "ENDOGENOUS_COPY"}, "MUTLO": {"mutation_rate": "LOW"}}
ARMS = [t + ":" + r for t in TRANS for r in ("P90", "ZERO")] + ["BASE:RANDOM"]


def founders():
    return json.loads((HERE.parent / "FOUNDERS.json").read_text(encoding="utf-8"))["tapes"]


def strict_trial(tape, cfg, e, k):
    L = cfg.L
    rng = random.Random("strict|%s|%s|%d" % (tape.hex(), e, k))
    mem = bytearray(256); mem[:L] = tape
    for i in range(L, 2 * L):
        mem[i] = rng.randrange(256)
    ins = [rng.randrange(256) for _ in range(16)]
    for i, v in enumerate(ins):
        mem[vm.IN_BASE + i] = v
    vm.execute(mem, L, 0, cfg.budget, ins, allow_copyall=cfg.allow_copyall, strict_budget=cfg.physics != "v1", regs=SF.ENTRY[e], **cfg.chem)
    return bytes(mem[L:2 * L]) == tape


def strict_free(tape, cfg):
    for e in ("R1", "R2"):
        if not any(strict_trial(tape, cfg, e, k) for k in range(2)):
            return False
        if sum(strict_trial(tape, cfg, e, k) for k in range(20)) < 16:
            return False
    return True


def one(arm, s):
    t, r = arm.split(":")
    F = founders(); fhex = F[s % len(F)]; ftape = bytes.fromhex(fhex)
    tapes = () if t == "NOFND" else (fhex,)
    cfg = Config(**dict(CELL, **TRANS[t]), ticks=TICKS, init_tapes=tapes, **REG[r])
    w = World(cfg, SEED0 + s)
    cache = {}; cps = []; t0 = time.perf_counter()

    def prof(g):
        if g not in cache:
            sf = SF.competent(g, cfg, "R1")[0] and SF.competent(g, cfg, "R2")[0]
            cache[g] = (sf, sf and strict_free(g, cfg))
        return cache[g]

    def checkpoint():
        alive = [o for o in w.cells if o is not None]
        by = {}
        for o in alive:
            by.setdefault(bytes(o.tape), []).append(o)
        fo = so = fm = 0
        for g, os_ in by.items():
            a, b = prof(g)
            fo += len(os_) * a; so += len(os_) * b
            if tapes:
                fm += len(os_) * (sum(1 for i in range(len(ftape)) if g[i] == ftape[i]) >= FM_MIN)
        cps.append({"tick": w.tick, "alive": len(alive), "distinct": len(by), "free_orgs": fo, "free_orgs_strict": so, "fm_orgs": fm})

    checkpoint()
    for _ in range(TICKS):
        w.step()
        ext = not any(o is not None for o in w.cells)
        if w.tick % EVERY == 0 or ext:
            checkpoint()
        if ext:
            break
    return {"arm": arm, "pair": s, "seed": SEED0 + s, "founder": fhex if tapes else None, "checkpoints": cps,
            "genomes_profiled": len(cache), "wall_s": round(time.perf_counter() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=ARMS); ap.add_argument("--s0", type=int, required=True)
    ap.add_argument("--n", type=int, required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    done = {(json.loads(l)["arm"], json.loads(l)["pair"]) for l in out.read_text(encoding="utf-8").splitlines()} if out.exists() else set()
    for s in range(a.s0, a.s0 + a.n):
        if (a.arm, s) not in done:
            rec = one(a.arm, s)
            with out.open("a", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
