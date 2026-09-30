"""AMENDMENT 23 -- C3R2-CONFIRM: the AMENDMENT 22 assay re-run as a confirmation.
Identical rules and panel (the A22 panel file is reused); changes: n = 12,
fresh seeds (A23), OTHER-motif spares 8 (was 4), directory A23_C3R2C, and the
verdict scaled to n (declared in AMENDMENT 23). Original A22 docstring follows.

AMENDMENT 22 -- C3R2: the recurrence-controlled assay, corrected.
Reuses a20_c3 (stage_donors / stage_transfer / stage_report logic) and changes:
  (1) PANEL is determined by the pre-freeze SUPPLY screen
      science/arc3/c3r2_feasibility/GENUINE_MOTIFS.json (supply-only, pre-donor):
        shams = the first 3 clean schemas, in pool order, with >= 6 usable GENUINE
                motifs (>= 8 T4-admissible instances), skipping any schema that is a
                re-expression of an already chosen one;
        OFF_0 = the first clean schema in pool order with 0 usable genuine motifs.
  (2) MOTIFS: m_A and o_A are drawn only from A's usable GENUINE motifs (not inert,
      not EQUAL/REFINES A or any re-expression of A, NEW_V2 and NEW_TRAJ vs A's span).
  (3) VALIDATE = 2 instances of m_A (so selection can see the recurrence; W6 R2);
      T_SAME = 2 other instances of m_A; T_OTHER = 2 instances of o_A;
      OBSERVE = 4 NAT, no floor (A21).
All other rules (instruments, window p_PRISTINE <= 0.75 on VALIDATE/TRANSFER, arms,
n = 8, ladder, verdict code, interpretation table) are AMENDMENT 20's.
Usage: python a22_c3r2.py <panel|foundry|donors|transfer|report> [workers]
"""
import json
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ["A18_TAG"] = "A23"
import a20_c3 as B               # noqa: E402
from a20_c3 import C, ON, NREP, log, a18, G, T3D, I   # noqa: E402

C.HERE = HERE / "A23_C3R2C"
NREP = 12
B.NREP = 12
C.HERE.mkdir(exist_ok=True)
FEAS = HERE.parent / "science" / "arc3" / "c3r2_feasibility" / "GENUINE_MOTIFS.json"
sys.path.insert(0, str(FEAS.parent))
import genuine_motifs as GM      # noqa: E402


def stage_panel(_w=0):
    """A23: reuse the A22 panel verbatim (identical deterministic rule and input)."""
    import shutil
    shutil.copyfile(HERE / "A22_C3R2" / ("A20_PANEL_%s.json" % C.DATE), C.HERE / ("A20_PANEL_%s.json" % C.DATE))
    log("panel reused from A22: %s" % C.rd("A20_PANEL_%s.json" % C.DATE)["panel"])
    return


def _unused_a22_panel(_w=0):
    import ruler_v2 as R
    rows = json.loads(FEAS.read_text())
    by_key = {r["key"]: r for r in rows}
    order = sorted(k for k in by_key if k != "G1")               # pool order S01, S02, ...
    panel, need = {"G1": a18.G1}, ["SHAM_0", "SHAM_1", "SHAM_2"]
    for k in order:
        r = by_key[k]
        if not need:
            break
        if r["genuine_usable"] < 6:
            continue
        s = r["schema"]
        if any(R.relations(s, x)["EQUAL"] or s in R.reexpressions(x) or x in R.reexpressions(s)
               or R._term(s) == R._term(x) for x in panel.values()):
            continue
        panel[need.pop(0)] = s
    off = next((by_key[k]["schema"] for k in order if by_key[k]["genuine_usable"] == 0), None)
    panel["OFF_0"] = off
    unmet = need + ([] if off else ["OFF_0"])
    C.wr("A20_PANEL_%s.json" % C.DATE, {"panel": panel, "unmet": unmet, "source": str(FEAS.name),
                                        "usable": {k: by_key[kk]["genuine_usable"] for k, kk in
                                                   ((k, next(x for x in by_key if by_key[x]["schema"] == v))
                                                    for k, v in panel.items() if v)}})
    log("panel %s unmet %s" % (panel, unmet))


def genuine_pool(schema, seed, k_min=8):
    import ruler_v2 as R
    import tribunal_t4 as T4
    rng = random.Random(seed)
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    out = {}
    for w in a18.compositions(schema):
        ok, inst = GM.genuine(w, schema)
        if not ok:
            continue
        trip = []
        for b in inst:
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
        C.wr("A23_C3R2C_RESULT_%s.json" % C.DATE, {"C3R2": "UNTESTABLE", "reason": "PANEL unmet %s" % sel["unmet"]})
        return
    panel = sel["panel"]
    pools = {a: genuine_pool(panel[a], "APHRODITE/A23/POOL/" + a) for a in ON}
    log("genuine motif pools %s" % {a: len(p) for a, p in pools.items()})
    nat_rng = random.Random(I._seed("APHRODITE/A23/NAT/v1"))
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    plan, draws, i = {}, [], 0
    for r in range(NREP):
        plan[r] = {}
        for a in ON:
            rng = random.Random(I._seed("APHRODITE/A23/MOTIF/%d/%s" % (r, a)))
            m, o = rng.sample(sorted(pools[a]), 2)
            same, other = list(pools[a][m]), list(pools[a][o])
            rng.shuffle(same)
            rng.shuffle(other)
            plan[r][a] = {"motif": m, "other": o}
            for p in same[:8]:
                draws.append((B._nm("d", i), p[2], p[1], p[3], "%d|%s|MOTIF" % (r, a)))
                i += 1
            for p in other[:8]:
                draws.append((B._nm("d", i), p[2], p[1], p[3], "%d|%s|OTHER" % (r, a)))
                i += 1
        for _ in range(6):
            while True:
                b = nat_rng.choice(G.BODY_SPACE)
                p = ("fold", nat_rng.choice(G.H1_SPACE), b, nat_rng.choice(finals))
                if R.accumulating(b) and T4.family_profile(p)["admissible"]:
                    break
            draws.append((B._nm("d", i), b, p[1], p[3], "%d|NAT|NAT" % r))
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
    q = sorted([x for x in rows if x.get("T4_qualified") and x["source"].startswith("%d|" % r)],
               key=lambda x: x["name"])
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
    for a in ON:
        take([x for x in head if x["source"] == "%d|%s|MOTIF" % (r, a)], 2, "VALIDATE", a + ":MOTIF")
        take([x for x in head if x["source"] == "%d|%s|MOTIF" % (r, a)], 2, "TRANSFER", a + ":SAME")
        take([x for x in head if x["source"] == "%d|%s|OTHER" % (r, a)], 2, "TRANSFER", a + ":OTHER")
    take([x for x in q if x["source"] == "%d|NAT|NAT" % r], 4, "OBSERVE", "OBS")
    return fams, ok


B.assign = assign


def stage_report(_w=0):
    """A20 report logic, then the A23 verdict: n = the fillable replicates (>= 10 of
    12 required, else UNTESTABLE); YES iff REUSED_SAME >= ceil(0.58 n) and
    CAPABILITY_SAME >= ceil(0.58 n), and sign tests p < 0.05 vs the frozen controls."""
    import math
    B.stage_report()
    res = C.rd("A20_C3_RESULT_%s.json" % C.DATE)
    cnt = res["counts"]
    n = cnt["G1"]["n"]
    k = math.ceil(0.58 * n)

    def yes(arm, v):
        return (cnt[arm]["n"] >= 10 and cnt[arm]["REUSED_SAME"] >= k and cnt[arm]["CAPABILITY_SAME"] >= k
                and all(p < 0.05 for p in v["sign_p_REUSED_SAME"].values()))
    res["A23_threshold"] = k
    res["A23_G1_RECURRENT_STEPPING_STONE"] = "UNTESTABLE" if n < 10 else ("YES" if yes("G1", res["H1_G1"]) else "NO")
    res["A23_GENERIC_RECURRENT_STEPPING_STONE"] = sum(yes(sname, v) for sname, v in res["H2_SHAMS"].items())
    res["note"] = "A20 verdict fields (n >= 8, >= 5) are superseded by the A23_* fields"
    C.wr("A23_C3R2C_RESULT_%s.json" % C.DATE, res)
    log("A23 G1_RECURRENT_STEPPING_STONE=%s GENERIC=%d/3 (n=%d, threshold %d)" % (
        res["A23_G1_RECURRENT_STEPPING_STONE"], res["A23_GENERIC_RECURRENT_STEPPING_STONE"], n, k))


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    log("A23 stage %s workers %d" % (st, w))
    {"panel": stage_panel, "foundry": stage_foundry, "donors": B.stage_donors,
     "transfer": B.stage_transfer, "report": stage_report}[st](w)
    log("A23 stage %s done" % st)
