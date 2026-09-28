"""AMENDMENT 20 -- ABSTRACTION COMPOUNDING ASSAY C3: RECURRENCE-CONTROLLED WORLD.

Mechanistic assay (recurrence is GUARANTEED by construction; a positive shows
the mechanism works WHEN reusable structure recurs, not that natural worlds
supply recurrence). Re-uses the frozen instruments and drivers (a18.py,
a18_c1.py, tribunal_t4.py, ruler_v2.py; all imported unmodified).

WORLD: W5. PANEL: G1 + 3 CLEAN shams + OFF. A sham is clean iff NEW_FINAL vs
G1 and it neither COMPOSES nor REFINES G1 OR ANY RE-EXPRESSION of G1
(ruler_v2.reexpressions: (acc + {H}), (acc - {H}), ({H} + acc)) -- this closes
the C2 SHAM_0 hole -- with an admissible composed-family rate in
[0.5x, 1.5x] of G1's.

PER REPLICATE r and per ON-path abstraction A (seeded, blind to donors):
  motif m_A     one composition wrap(A, op, atom) with >= 8 T4-admissible
                accumulating instances (seed ".../MOTIF/<r>/<A>");
  other o_A     a different such composition of A;
  VALIDATE      1 family = an instance of m_A;
  T_SAME        2 families = OTHER instances of m_A (different filler, and a
                freshly drawn init/final): recurrence of the motif;
  T_OTHER       2 families = instances of o_A: no motif recurrence (same A);
  OBSERVE       4 families with p_PRISTINE > 0 (any source, including 2 NAT).
  Every family: Q2 + T4 + pilots (a18_c1.qualify_family); VALIDATE/TRANSFER
  window p_PRISTINE <= 0.75. A family that fails is replaced by the next
  seeded instance of the same motif (at most 40 tries; else the replicate is
  NOT run and counted).
ARMS: G1, G1_NC (no composition), SHAM_0..2, OFF_0, P. n = 8.
Transfer uses a18_c1._transfer_job (SELECTED / START / PRISTINE, 4 cells, T4-
qualified; ladder to 40 x escrow). Verdicts: see AMENDMENT_20 and stage_report.
Usage: python a20_c3.py <panel|foundry|donors|transfer|report> [workers]
"""
import json
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("A18_TAG", "A20")
import a18                       # noqa: E402
import a18_c1 as C               # noqa: E402
import a19_c2 as C2              # noqa: E402  (imported FIRST: its module-level path settings are overridden below)
from a18 import G, T3D, I, a17, FR, log   # noqa: E402

C.DATE = "2026-09-28"
C.HERE = HERE / "A20_C3"
C.HERE.mkdir(exist_ok=True)
G1_RATE = 0.362
ON = ["G1", "SHAM_0", "SHAM_1", "SHAM_2"]
C.ARMS = ["G1", "G1_NC", "SHAM_0", "SHAM_1", "SHAM_2", "OFF_0", "P"]
C.COMPOSE = {a: (a != "G1_NC") for a in C.ARMS}
C.HELD = {"G1": "G1", "G1_NC": "G1", "SHAM_0": "SHAM_0", "SHAM_1": "SHAM_1", "SHAM_2": "SHAM_2",
          "OFF_0": "OFF_0", "P": "P"}
NREP = 8
LET = "abcdefghijklmnopqrstuvwxyz"


def _nm(prefix, i):
    return prefix + "".join(LET[(i // 26 ** k) % 26] for k in range(3))


def clean(s, sp, tsp):
    import ruler_v2 as R
    v = R.verdict_full(s, a18.G1, sp, tsp)
    if not v["NEW_FINAL"] or v["accumulating"] < 20:
        return False
    for ref in R.reexpressions(a18.G1):
        rel = R.relations(s, ref)
        if rel["COMPOSES"] or rel["REFINES"] or rel["EQUAL"]:
            return False
    return True


def stage_panel(_w=0):
    import ruler_v2 as R
    a18.use_world("W5")
    sp, tsp = R.span_of_schema(a18.G1), R.traj_span(R.reexpression_bodies(a18.G1))
    rng = random.Random(I._seed("APHRODITE/A20/PANEL/v1"))
    panel, rates, seen, tries = {"G1": a18.G1}, {"G1": G1_RATE}, {a18.G1}, 0
    need = ["SHAM_0", "SHAM_1", "SHAM_2", "OFF_0"]
    while need and tries < 600:
        s = a18._random_schema(rng)
        if not s or s in seen:
            continue
        seen.add(s)
        tries += 1
        if not clean(s, sp, tsp):
            continue
        rate, good, _n = C2.comp_rate(s, random.Random(s))
        if need[0].startswith("SHAM") and not (0.5 * G1_RATE <= rate <= 1.5 * G1_RATE and good >= 20):
            continue
        panel[need[0]], rates[need[0]] = s, rate
        need.pop(0)
    C.wr("A20_PANEL_%s.json" % C.DATE, {"panel": panel, "rates": rates, "tries": tries, "unmet": need})
    log("panel %s rates %s unmet %s" % (panel, rates, need))


def motif_pool(schema, rng_seed, k_min=8):
    """compositions of schema with >= k_min T4-admissible accumulating instance
    families (init/final drawn per instance); returns {motif: [triples]}."""
    import ruler_v2 as R
    import tribunal_t4 as T4
    rng = random.Random(rng_seed)
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    out = {}
    for w in a18.compositions(schema):
        trip = []
        for b in T3D.instantiate(w):
            if not R.accumulating(b):
                continue
            p = ("fold", rng.choice(G.H1_SPACE), b, rng.choice(finals))
            if T4.family_profile(p)["admissible"]:
                trip.append(p)
        if len(trip) >= k_min:
            out[w] = trip
    return out


def stage_foundry(workers=5):
    import ruler_v2 as R
    import tribunal_t4 as T4
    a18.use_world("W5")
    sel = C.rd("A20_PANEL_%s.json" % C.DATE)
    if sel["unmet"]:
        C.wr("A20_C3_RESULT_%s.json" % C.DATE, {"C3": "UNTESTABLE", "reason": "PANEL unmet %s" % sel["unmet"]})
        return
    panel = sel["panel"]
    pools = {a: motif_pool(panel[a], "APHRODITE/A20/POOL/" + a) for a in ON}
    log("motif pools %s" % {a: len(p) for a, p in pools.items()})
    plan, i = {}, 0
    nat_rng = random.Random(I._seed("APHRODITE/A20/NAT/v1"))
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    draws = []
    for r in range(NREP):
        plan[r] = {}
        for a in ON:
            rng = random.Random(I._seed("APHRODITE/A20/MOTIF/%d/%s" % (r, a)))
            motifs = sorted(pools[a])
            m, o = rng.sample(motifs, 2)
            same = list(pools[a][m])
            rng.shuffle(same)
            other = list(pools[a][o])
            rng.shuffle(other)
            plan[r][a] = {"motif": m, "other": o}
            for role, lst, k in (("VALIDATE", same, 1 + 2), ("OTHER", other, 2)):
                for p in lst[: 6 if role == "VALIDATE" else 4]:        # spares for failures
                    draws.append((_nm("c", i), p[2], p[1], p[3], "%d|%s|%s" % (r, a, "MOTIF" if role == "VALIDATE"
                                                                              else "OTHER")))
                    i += 1
        for _ in range(6):                                            # NAT spares for OBSERVE
            while True:
                b = nat_rng.choice(G.BODY_SPACE)
                p = ("fold", nat_rng.choice(G.H1_SPACE), b, nat_rng.choice(finals))
                if R.accumulating(b) and T4.family_profile(p)["admissible"]:
                    break
            draws.append((_nm("c", i), b, p[1], p[3], "%d|NAT|NAT" % r))
            i += 1
    C.wr("A20_PLAN_%s.json" % C.DATE, {"panel": panel, "plan": plan, "draws": draws, "draws_sha256": C.sha(draws),
                                       "motif_pool_sizes": {a: len(p) for a, p in pools.items()}})
    done = {x["name"] for x in C.rd_jsonl("A20_FOUNDRY_ROWS_%s.jsonl" % C.DATE)}
    todo = [d for d in draws if d[0] not in done]
    log("foundry draws %d todo %d" % (len(draws), len(todo)))
    with open(C.HERE / ("A20_FOUNDRY_ROWS_%s.jsonl" % C.DATE), "a", encoding="utf-8") as fh:
        for row in C.pool(C.qualify_family, todo, workers):
            fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
            fh.flush()


def assign(rows, r):
    """Deterministic role fill for replicate r (identical for all arms)."""
    q = [x for x in rows if x.get("T4_qualified") and x["source"].startswith("%d|" % r)]
    q.sort(key=lambda x: x["name"])
    head = [x for x in q if x.get("p_PRISTINE", 0) <= 0.75]
    fams, used, ok = [], set(), True

    def take(pool, k, role, tag):
        nonlocal ok
        c = [x for x in pool if x["name"] not in used][:k]
        if len(c) < k:
            ok = False
        for x in c:
            used.add(x["name"])
            fams.append(dict(x, role=role, tclass=tag, qualified_dev_size=x["Q2_size"]))

    floor = [x for x in q if 0 < x.get("p_PRISTINE", 0) <= 0.75]
    take(floor, 4, "OBSERVE", "OBS")
    for a in ON:
        take([x for x in head if x["source"] == "%d|%s|MOTIF" % (r, a)], 1, "VALIDATE", a + ":MOTIF")
        take([x for x in head if x["source"] == "%d|%s|MOTIF" % (r, a)], 2, "TRANSFER", a + ":SAME")
        take([x for x in head if x["source"] == "%d|%s|OTHER" % (r, a)], 2, "TRANSFER", a + ":OTHER")
    return fams, ok


def stage_donors(workers=5):
    a18.use_world("W5")
    plan = C.rd("A20_PLAN_%s.json" % C.DATE)
    panel = plan["panel"]
    rows = C.rd_jsonl("A20_FOUNDRY_ROWS_%s.jsonl" % C.DATE)
    roles, jobs = {}, []
    for r in range(NREP):
        fams, ok = assign(rows, r)
        roles["CON/%d" % r] = {"ok": ok, "families": [{k: f[k] for k in (
            "name", "role", "tclass", "source", "body", "init", "final", "Q2_size")} for f in fams]}
        if not ok:
            continue
        specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fams}
        for arm in C.ARMS:
            jobs.append(("CON%d" % r, C.HELD[arm], r, fams, specs, panel, C.COMPOSE[arm], arm))
    C.wr("A18_ROLES_%s.json" % C.DATE, roles)
    done = {(x["catalog"], x["arm"]) for x in C.rd_jsonl("A18_DONORS_%s.jsonl" % C.DATE)}
    jobs = [j for j in jobs if (j[0], j[7]) not in done]
    log("replicates ok %s; donor jobs %d" % ({k: v["ok"] for k, v in roles.items()}, len(jobs)))
    with open(C.HERE / ("A18_DONORS_%s.jsonl" % C.DATE), "a", encoding="utf-8") as fh:
        for d in C.pool(C._donor_job, jobs, workers):
            fh.write(json.dumps(d, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("donor %s %-6s sel=%s origin=%s COMP=%s" % (d["catalog"], d["arm"], d["selected_schema"],
                                                           d["selected_origin"], d["COMPOSES_held"]))


def stage_transfer(workers=5):
    """a18_c1.stage_transfer reads A18_ROLES / A18_DONORS in C.HERE and the
    PANEL file; provide the panel under the name it expects."""
    plan = C.rd("A20_PLAN_%s.json" % C.DATE)
    C.wr("A18_PANEL_%s.json" % C.DATE, {"panel": plan["panel"]})
    C.stage_transfer(workers)


def stage_report(_w=0):
    """Frozen verdict rules (AMENDMENT 20 s5)."""
    plan = C.rd("A20_PLAN_%s.json" % C.DATE)
    panel = plan["panel"]
    roles = C.rd("A18_ROLES_%s.json" % C.DATE)
    donors = C.rd_jsonl("A18_DONORS_%s.jsonl" % C.DATE)
    trans = C.rd_jsonl("A18_TRANSFER_%s.jsonl" % C.DATE)
    tcls = {f["name"]: f["tclass"] for v in roles.values() for f in v["families"]}
    lad = defaultdict(dict)
    for d in donors:
        held = C.HELD[d["arm"]]
        rows = [t for t in trans if t["catalog"] == d["catalog"] and t["arm"] == d["arm"]]
        per = {}
        for cls in ("SAME", "OTHER"):
            key = "%s:%s" % (held, cls) if held != "P" else None
            own = [t for t in rows if key and tcls.get(t["family"]) == key]
            fam_solved = {t["family"] for t in own for c in t["cells"]
                          if c["SELECTED"]["qualified"] and not c["START"]["qualified"]}
            fam_cap = {t["family"] for t in own for c in t["cells"]
                       if c["SELECTED"]["qualified"] and not c["START"]["qualified"]
                       and "ladder_charge" in c["START"] and "ladder_charge" in c["PRISTINE"]
                       and not c["START"].get("ladder_qualified") and not c["PRISTINE"].get("ladder_qualified")}
            per[cls] = {"solved_families": sorted(fam_solved), "capability_families": sorted(fam_cap)}
        # off-path: other abstractions' motif families -- composition should NOT help
        off = [t for t in rows if tcls.get(t["family"], "").endswith(":SAME") and not tcls[t["family"]].startswith(held + ":")]
        off_gain = sum(1 for t in off for c in t["cells"] if c["SELECTED"]["qualified"] and not c["START"]["qualified"])
        losses = sum(1 for t in rows for c in t["cells"]
                     if c["START"]["qualified"] and not c["SELECTED"]["qualified"])
        lad[d["arm"]][d["catalog"]] = {
            "SELECTED_ANY": d["selected_schema"] is not None,
            "LOSS_CELLS": losses,
            "SELECTED": bool(d["COMPOSES_held"]),
            "SOLVED_SAME": len(per["SAME"]["solved_families"]) >= 1,
            "REUSED_SAME": len(per["SAME"]["solved_families"]) >= 2,
            "CAPABILITY_SAME": len(per["SAME"]["capability_families"]) >= 2,
            "REUSED_OTHER": len(per["OTHER"]["solved_families"]) >= 2,
            "OFFPATH_GAIN_CELLS": off_gain, "detail": per}
    counts = {a: {k: sum(1 for v in lad[a].values() if v[k]) for k in
                  ("SELECTED", "SOLVED_SAME", "REUSED_SAME", "CAPABILITY_SAME", "REUSED_OTHER")}
              for a in C.ARMS}
    for a in C.ARMS:
        counts[a]["OFFPATH_GAIN_CELLS"] = sum(v["OFFPATH_GAIN_CELLS"] for v in lad[a].values())
        counts[a]["LOSS_CELLS"] = sum(v["LOSS_CELLS"] for v in lad[a].values())
        counts[a]["SELECTED_ANY"] = sum(1 for v in lad[a].values() if v["SELECTED_ANY"])
        counts[a]["n"] = len(lad[a])

    def sign(arm, ctrl, key):
        a = sum(1 for r in lad[arm] if lad[arm][r][key] and not lad[ctrl].get(r, {}).get(key))
        b = sum(1 for r in lad[ctrl] if lad[ctrl][r][key] and not lad[arm].get(r, {}).get(key))
        return C._sign_p(a, b)

    def verdict(arm, controls):
        ps = {c: sign(arm, c, "REUSED_SAME") for c in controls}
        yes = (counts[arm]["n"] >= 8 and counts[arm]["REUSED_SAME"] >= 5 and counts[arm]["CAPABILITY_SAME"] >= 5
               and all(p < 0.05 for p in ps.values()))
        return {"YES": yes, "sign_p_REUSED_SAME": ps}
    out = {"panel": panel, "counts": counts, "ladders": lad,
           "H1_G1": verdict("G1", ["G1_NC", "P", "OFF_0"]),
           "H2_SHAMS": {s: verdict(s, ["P", "OFF_0"]) for s in ("SHAM_0", "SHAM_1", "SHAM_2")}}
    out["G1_RECURRENT_STEPPING_STONE"] = ("UNTESTABLE" if counts["G1"]["n"] < 8
                                          else ("YES" if out["H1_G1"]["YES"] else "NO"))
    out["GENERIC_RECURRENT_STEPPING_STONE"] = sum(v["YES"] for v in out["H2_SHAMS"].values())
    C.wr("A20_C3_RESULT_%s.json" % C.DATE, out)
    log("counts %s" % json.dumps(counts))
    log("G1_RECURRENT_STEPPING_STONE=%s GENERIC=%d/3 H1=%s" % (out["G1_RECURRENT_STEPPING_STONE"],
                                                             out["GENERIC_RECURRENT_STEPPING_STONE"], out["H1_G1"]))


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    log("A20 stage %s workers %d" % (st, w))
    {"panel": stage_panel, "foundry": stage_foundry, "donors": stage_donors,
     "transfer": stage_transfer, "report": stage_report}[st](w)
    log("A20 stage %s done" % st)
