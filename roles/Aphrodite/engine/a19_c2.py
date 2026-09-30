"""AMENDMENT 19 -- ABSTRACTION COMPOUNDING ASSAY C2 (driver). Re-uses the
frozen A18 drivers (a18.py, a18_c1.py; unmodified, imported) and changes ONLY:
  (1) SUPPLY SCREEN: composed and natural bodies are sampled only from families
      that pass tribunal_t4.family_profile (task-side admissibility, no recipient)
      under ONE rule for every panel schema -- treatment-blind;
  (2) PANEL MATCHING: shams must (a) be NEW_FINAL vs G1, (b) neither COMPOSE nor
      REFINE G1 (a sham that contains G1 is not a control), (c) have an admissible
      composed-family rate within [0.5x, 1.5x] of G1's (K11: G1 = 0.362), and
      (d) >= 20 compositions with rate >= 0.25. OFF_0: the same (a)-(b), and its
      compositions are never supplied.
  (3) Identity: tag A19, date 2026-09-28; all artifacts under engine/A19_C2/
      (file names keep a18_c1's A18_ prefix, dated 2026-09-28).
All other rules (arms, roles, windows, ladder, verdicts) are a18_c1's.
Usage: python a19_c2.py <panel|foundry|donors|transfer|report> [workers]
"""
import json
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("A18_TAG", "A19")
import a18                       # noqa: E402
import a18_c1 as C               # noqa: E402
from a18 import G, T3D, I, log   # noqa: E402

C.DATE = "2026-09-28"
C.HERE = HERE / "A19_C2"            # every C2 artifact lives here (file names keep a18_c1's A18_ prefix)
C.HERE.mkdir(exist_ok=True)
SCREEN_FINALS = None             # task finals: uniform among acc-finals (as A18)
G1_RATE = 0.362                  # K11 (science/compounding/rb4/K11_ADMISSIBLE_COMPOSITIONS.json)
_TAG = "A19"


def comp_rate(schema, rng, per_comp=6):
    """Admissible composed-family rate of a schema (task-side, T4 profile)."""
    import ruler_v2 as R
    import tribunal_t4 as T4
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    n = ok = good = 0
    comps = a18.compositions(schema)
    for w in comps:
        inst = [b for b in T3D.instantiate(w) if R.accumulating(b)]
        rng.shuffle(inst)
        cn = cok = 0
        for b in inst[:per_comp]:
            p = ("fold", rng.choice(G.H1_SPACE), b, rng.choice(finals))
            cn += 1
            cok += T4.family_profile(p)["admissible"]
        n, ok = n + cn, ok + cok
        good += cn > 0 and cok / cn >= 0.25
    return (ok / n if n else 0.0), good, len(comps)


def build_panel_c2(seed="APHRODITE/A19/PANEL/v1", max_tries=400):
    import ruler_v2 as R
    a18.use_world("W5")
    sp, tsp = R.span_of_schema(a18.G1), R.traj_span(R.reexpression_bodies(a18.G1))
    rng = random.Random(I._seed(seed))
    panel, rates, seen, tries = {"G1": a18.G1}, {"G1": G1_RATE}, {a18.G1}, 0
    need = ["SHAM_0", "SHAM_1", "OFF_0"]
    while need and tries < max_tries:
        s = a18._random_schema(rng)
        if not s or s in seen:
            continue
        seen.add(s)
        tries += 1
        v = R.verdict_full(s, a18.G1, sp, tsp)
        rel = R.relations(s, a18.G1)
        if not v["NEW_FINAL"] or rel["COMPOSES"] or rel["REFINES"] or v["accumulating"] < 20:
            continue
        rate, good, ncomp = comp_rate(s, random.Random(s))
        if need[0].startswith("SHAM") and not (0.5 * G1_RATE <= rate <= 1.5 * G1_RATE and good >= 20):
            continue
        panel[need[0]], rates[need[0]] = s, rate
        need.pop(0)
    return panel, rates, tries, need


def supply_bodies_c2(panel, on_path_keys):
    """Screened supply: (init, body, final) triples of composed instances that
    pass T4.family_profile, equal share per ON-path schema."""
    import ruler_v2 as R
    import tribunal_t4 as T4
    rng = random.Random(I._seed("APHRODITE/A19/SUPPLY-SCREEN/v1"))
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    out = {}
    for k in on_path_keys:
        trip = []
        for w in a18.compositions(panel[k]):
            for b in T3D.instantiate(w):
                if not R.accumulating(b):
                    continue
                p = ("fold", rng.choice(G.H1_SPACE), b, rng.choice(finals))
                if T4.family_profile(p)["admissible"]:
                    trip.append(p)
        out[k] = sorted(set(trip))
    return out


def stage_panel(_w=0):
    panel, rates, tries, need = build_panel_c2()
    log("panel %s rates %s tries %d unmet %s" % (panel, rates, tries, need))
    C.wr("A18_PANELSEL_%s.json" % C.DATE, {"panel": panel, "rates": rates, "tries": tries, "unmet": need})


def stage_foundry(workers=8, draws_per_source=48):
    import ruler_v2 as R
    import tribunal_t4 as T4
    a18.use_world("W5")
    sel = C.rd("A18_PANELSEL_%s.json" % C.DATE)
    panel = sel["panel"]
    if sel["unmet"]:
        C.wr("A18_C2_RESULT_%s.json" % C.DATE, {"C2": "UNTESTABLE", "reason": "PANEL: unmet %s" % sel["unmet"]})
        log("UNTESTABLE: panel unmet %s" % sel["unmet"])
        return
    sb = supply_bodies_c2(panel, C.ON_PATH)
    rng = random.Random(I._seed("APHRODITE/A19/SUPPLY/v1"))
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    draws, i = [], 0
    for k in C.ON_PATH:
        pool = sb[k]
        for p in rng.sample(pool, min(draws_per_source, len(pool))):
            draws.append((C._pname(i), p[2], p[1], p[3], "CON:" + k))
            i += 1
    nat = 0
    while nat < draws_per_source * 3:
        b = rng.choice(G.BODY_SPACE)
        if not R.accumulating(b):
            continue
        p = ("fold", rng.choice(G.H1_SPACE), b, rng.choice(finals))
        if not T4.family_profile(p)["admissible"]:
            continue
        draws.append((C._pname(i), b, p[1], p[3], "NAT"))
        i, nat = i + 1, nat + 1
    C.wr("A18_PANEL_%s.json" % C.DATE, {"panel": panel, "panel_sha256": C.sha(panel), "rates": sel["rates"],
                                        "supply_sizes": {k: len(v) for k, v in sb.items()},
                                        "draws_sha256": C.sha(draws), "draws": draws})
    log("supply sizes %s draws %d sha %s" % ({k: len(v) for k, v in sb.items()}, len(draws), C.sha(draws)[:12]))
    done = {r["name"] for r in C.rd_jsonl("A18_FOUNDRY_ROWS_%s.jsonl" % C.DATE)}
    todo = [d for d in draws if d[0] not in done]
    with open(C.HERE / ("A18_FOUNDRY_ROWS_%s.jsonl" % C.DATE), "a", encoding="utf-8") as fh:
        for r in C.pool(C.qualify_family, todo, workers):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
    rows = C.rd_jsonl("A18_FOUNDRY_ROWS_%s.jsonl" % C.DATE)
    by = {}
    for r in rows:
        s = by.setdefault(r["source"], {"n": 0, "Q2": 0, "T4": 0, "p_P>0": 0, "p_P<=0.75": 0})
        s["n"] += 1
        s["Q2"] += r["Q2_size"] is not None
        s["T4"] += bool(r.get("T4_qualified"))
        s["p_P>0"] += r.get("p_PRISTINE", 0) > 0
        s["p_P<=0.75"] += bool(r.get("T4_qualified")) and r.get("p_PRISTINE", 0) <= 0.75
    C.wr("A18_FOUNDRY_SUMMARY_%s.json" % C.DATE, by)
    log("foundry summary %s" % by)


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    log("A19 stage %s workers %d" % (st, w))
    {"panel": stage_panel, "foundry": stage_foundry, "donors": C.stage_donors,
     "transfer": C.stage_transfer, "report": C.stage_report}[st](w)
    log("A19 stage %s done" % st)
