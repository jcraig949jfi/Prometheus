"""B16 -- memory by SENSORY SHUTDOWN? (Phase 2-B Beta)

Disassembly of jitter-robust W2_K2 shelf organisms (B03_BASE_302, _301) shows a latch: the input-reading block runs on
the first tick(s) only, and afterwards the organism loops emitting the first value without executing IN again. If that
is the general mechanism, "one stored value" is achieved by ceasing to perceive, which would explain the composition
wall directly: a second value can never be stored by an organism that has stopped reading input.

Readout per organism (B03 final elites, B11 classes): over 16 held-out W2_K2 episodes, the share of ticks AFTER the
first tick on which at least one IN (op 21) instruction executes ("perception after tick 0"). Latch = < .05.
PREDICTION (before running): >= 70% of B11-robust shelf organisms are latches; delay-line organisms read input on
~100% of ticks; the hand one-slot shelf program reads on 100%.
"""
import json
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, SHELF, TARGET, manifest
from archaeon.beta.disasm import _tracer
from archaeon.wse.worlds import episodes_for

OUT = Path(__file__).resolve().parent / "results"


def perception_after_first(m, eps):
    T = _tracer()
    p = T.Player(m)
    later, read = 0, 0
    for ei, ep in enumerate(eps):
        st = p.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", 7, ei))
        for ti, words in enumerate(ep.ticks):
            T._TRACE.clear()
            p.run_tick(st, [words], 1, rng)
            if ti == 0:
                continue
            later += 1
            tape = st["tape"]
            if any(tape[ip] % 25 == 21 for ip in T._TRACE if ip < len(tape)):
                read += 1
    return read / max(1, later)


def main():
    eps = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", 7, 16)
    b11 = {x["who"]: x for x in json.loads((OUT / "B11_result.json").read_text(encoding="utf-8"))["rows"]}
    b3 = json.loads((OUT / "B03_result.json").read_text(encoding="utf-8"))["rows"]
    rows = [{"who": "hand_one_slot_shelf", "class": "hand", "perception": perception_after_first(manifest(SHELF), eps)}]
    for r in b3:
        who = "B03_%s_%d" % (r["arm"], r["seed"])
        x = b11[who]
        d = x["plain"] - x["jitter"]
        cls = "robust" if d < .05 else ("delay" if d >= .15 else "partial")
        m = r.get("final_manifest") or r.get("summit_manifest")
        rows.append({"who": who, "class": cls, "perception": round(perception_after_first(m, eps), 4)})
    summ = {}
    for c in ("robust", "delay", "partial", "hand"):
        rr = [x for x in rows if x["class"] == c]
        if rr:
            summ[c] = {"n": len(rr), "latch_lt_.05": sum(x["perception"] < .05 for x in rr),
                       "median_perception": sorted(x["perception"] for x in rr)[len(rr) // 2]}
    print(json.dumps(summ))
    (OUT / "B16_result.json").write_text(json.dumps({"probe": "B16", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
