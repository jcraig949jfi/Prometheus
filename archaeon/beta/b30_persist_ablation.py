"""B30 -- do evolved composed-world elites carry STATE across ticks? Persistence ablation (evaluation only).

For each B25 (P-boom) and B27 elite on its NOCLOCK world: reward as evolved vs with persist forced to "none" (tape
and registers reset at every tick boundary). Drop >= .05 = the policy uses memory of earlier ticks.
Classes from B26/B27: CONTENT (senses pool words; blind twin collapses) vs BLIND (open-loop; blind == elite).
PREDICTION (before running): BLIND elites drop >= .05 in >= 3/4 (an open-loop periodic pattern needs a counter);
CONTENT elites mostly reactive (drop < .05 in >= 4/7).
"""
import json
from pathlib import Path

from archaeon.beta.b23b_composed_world_audit import score
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b26_word_ablation import Ablate
from archaeon.beta.b27_noclock_generality import load_world

OUT = Path(__file__).resolve().parent / "results"


def main():
    rows = []
    b25 = json.loads((OUT / "B25_result.json").read_text(encoding="utf-8"))["rows"]
    b27 = json.loads((OUT / "B27_result.json").read_text(encoding="utf-8"))["rows"]
    items = [("P-boom_K_D_persist_s3", r) for r in b25 if r.get("arm") == "NOCLOCK" and "elite_manifest" in r]
    items += [(r["world"], r) for r in b27 if "elite_manifest" in r]
    cache = {}
    for wname, r in items:
        if wname not in cache:
            w, s = load_world(wname); cache[wname] = (NoClock(w), s)
        w, s = cache[wname]
        m = r["elite_manifest"]
        base = score(m, w, s); blind = score(m, Ablate(w, "all"), s)
        nop = score(dict(m, persist="none"), w, s)
        cls = "CONTENT" if base - blind >= .05 else "BLIND"
        rows.append({"world": wname, "seed": r["seed"], "class": cls, "persist": m["persist"], "elite": round(base, 4),
                     "blind": round(blind, 4), "persist_none": round(nop, 4), "uses_memory": base - nop >= .05})
        print(json.dumps(rows[-1]), flush=True)
    summ = {c: {"n": sum(x["class"] == c for x in rows), "uses_memory": sum(x["class"] == c and x["uses_memory"] for x in rows)}
            for c in ("CONTENT", "BLIND")}
    print(json.dumps(summ))
    (OUT / "B30_result.json").write_text(json.dumps({"probe": "B30", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
