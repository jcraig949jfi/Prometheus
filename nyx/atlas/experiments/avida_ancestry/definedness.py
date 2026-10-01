"""Harmonia rule A5, applied to the Avida ancestry packet BEFORE its hash: every observable is checked DEFINED (a
non-zero eligible count) on a small synthetic fixture for every arm it is claimed on, and refused at plan time where
it is not. The same fixtures carry the packet's controls, so the harness is shown able to see each violation it
reports zero of. No .spop from the body is opened here; the fixtures come from model.py (30 cells).

    python -m nyx.atlas.experiments.avida_ancestry.definedness      -> DEFINEDNESS.json, exit 1 on any failed expectation

Arms
    BASE            asexual, pruning on, save_historic=1, saves at begin and every 10 updates to 40
    HIST0           BASE saved with save_historic=0
    UNPRUNED        BASE with pruning switched off            (POSITIVE control: the history Avida does not keep)
    SEVER           BASE with every organism re-injected parentless at update 19 (stamped 20)
    PASSIVE_HOLDER  BASE plus one passive reference held outside the arbiter (cDeme.cc:958,985), owner then killed
    ACTIVE_HOLDER   BASE plus one active reference held outside the arbiter (cBirthChamber.cc:160), owner then killed
    SEXUAL          half the births record a second parent
    PARASITE        one unit whose source is horz:ext
"""
from __future__ import annotations

import json
from pathlib import Path

from nyx.atlas.experiments.avida_ancestry import spop
from nyx.atlas.experiments.avida_ancestry.model import World

OUT = Path(__file__).resolve().parent / "DEFINEDNESS.json"
END = 40


def _saver(save_historic=True, extra=None):
    def events(w):
        if extra:
            extra(w)
        if w.update == -1 or w.update % 10 == 0:
            w.save(save_historic=save_historic)
    return events


def _arm(name: str) -> World:
    if name == "BASE":
        return World().run(END, _saver())
    if name == "HIST0":
        return World().run(END, _saver(save_historic=False))
    if name == "UNPRUNED":
        return World(prune=False).run(END, _saver())
    if name == "SEVER":
        return World().run(END, _saver(extra=lambda w: w.sever() if w.update == 19 else None))
    if name == "SEXUAL":
        return World(sexual=0.5).run(END, _saver())
    if name == "PARASITE":
        def ev(w):
            if w.update == -1:
                g = w.arb.classify("zzzz", [], "horz:ext", "ABB")
                w.extra_units.append((0, g))
        return World().run(END, _saver(extra=ev))
    if name in ("PASSIVE_HOLDER", "ACTIVE_HOLDER"):
        def ev(w):
            if w.update != 5:
                return
            if name == "PASSIVE_HOLDER":
                # a LEAF: a living genotype no other genotype descends from; hold it, then kill its organisms
                named = {p.id for g in w.arb.ever if not g.gone for p in g.parents}
                g = next(g for g in w.cells if g is not None and g.id not in named)
                g.p_refs += 1
            else:
                # an ANCESTOR: a living genotype with a living child genotype; hold it, then kill its organisms
                g = next(p for c in w.cells if c is not None for p in c.parents if p.num > 0)
                g.a_refs += 1
            for i, c in enumerate(w.cells):
                if c is g:
                    w.kill(i)
        return World().run(END, _saver(extra=ev))
    raise KeyError(name)


def _files(w: World):
    return [spop.read_text(t, n) for n, t in w.files.items()]


def _verdict(count: int, eligible: int) -> str:
    return "NOT_ELIGIBLE" if eligible == 0 else ("HOLDS" if count == 0 else "VIOLATED")


def _agg(files, key: str, elig: str):
    ms = [spop.measure(f) for f in files]
    c, e = sum(m[key] for m in ms), sum(m[elig] for m in ms)
    return {"count": c, "eligible": e, "verdict": _verdict(c, e)}


def _edit(text: str, fn) -> str:
    head, body = text.split("\n\n", 1)
    return head + "\n\n" + "\n".join(fn([l for l in body.splitlines() if l.strip()])) + "\n"


def run() -> dict:
    worlds = {a: _arm(a) for a in ("BASE", "HIST0", "UNPRUNED", "SEVER", "PASSIVE_HOLDER", "ACTIVE_HOLDER", "SEXUAL", "PARASITE")}
    files = {a: _files(w) for a, w in worlds.items()}
    table, checks = {}, []

    def expect(label: str, ok: bool, detail=""):
        checks.append({"check": label, "ok": bool(ok), "detail": detail})

    obs = [("I1", "I1_dangling_parent_refs", "I1_eligible_parent_refs"), ("I2", "I2_dead_leaves", "I2_eligible_dead_rows"),
           ("I3", "I3_depth_violations", "I3_eligible_rows"), ("I4", "I4_live_duplicate_keys", "I4_eligible_live_rows"),
           ("I5", "I5_dead_rows", "I5_eligible_rows"), ("I6a", "I6_born_at_zero", "I6_eligible_rows"),
           ("I6b", "I6_born_after_T_plus_1", "I6_eligible_rows")]
    for arm, fs in files.items():
        table[arm] = {o: _agg(fs, k, e) for o, k, e in obs}
        table[arm]["I7"] = (lambda s: {"count": s["I7_missing_at_earlier_save"] + s["I7_changed_immutable_fields"], "eligible": s["I7_eligible_rows"],
                                       "verdict": _verdict(s["I7_missing_at_earlier_save"] + s["I7_changed_immutable_fields"], s["I7_eligible_rows"])})(spop.measure_series(fs))
        ms = [spop.measure(f) for f in fs]
        table[arm]["content"] = {"multi_parent": any(m["multi_parent"] for m in ms), "parasite": any(m["parasite"] for m in ms),
                                 "in_scope": all(f["in_scope"] for f in fs), "unparsed": sum(m["n_unparsed"] for m in ms),
                                 "shifted_rows": sum(m["n_shifted_rows"] for m in ms), "files": len(fs)}
    sev = spop.measure_series(files["SEVER"], sever_at=20)
    table["SEVER"]["I8"] = {"count": sev["I8_rows_stamped_before_severance"] + sev["I8_roots_not_stamped_at_severance"],
                            "eligible": sev["I8_eligible_rows"], "roots": sev["I8_roots"],
                            "max_rows_before": sev["I8_max_rows_in_a_save_before_severance"],
                            "verdict": _verdict(sev["I8_rows_stamped_before_severance"] + sev["I8_roots_not_stamped_at_severance"], sev["I8_eligible_rows"])}

    # ---- A5: defined and holding where claimed --------------------------------------------------------------
    for o in ("I1", "I2", "I3", "I4", "I6a", "I6b", "I7"):
        expect(f"A5 {o} defined and HOLDS on BASE", table["BASE"][o]["verdict"] == "HOLDS", table["BASE"][o])
        expect(f"A5 {o} defined and HOLDS on SEVER", table["SEVER"][o]["verdict"] == "HOLDS", table["SEVER"][o])
    expect("A5 I5 defined and HOLDS on HIST0", table["HIST0"]["I5"]["verdict"] == "HOLDS", table["HIST0"]["I5"])
    expect("A5 I8 defined and HOLDS on SEVER", table["SEVER"]["I8"]["verdict"] == "HOLDS" and table["SEVER"]["I8"]["max_rows_before"] > 1
           and table["SEVER"]["I8"]["roots"] > 0, table["SEVER"]["I8"])
    expect("reader survives src_args containing spaces (SEVER rows are shifted, none unparsed)",
           table["SEVER"]["content"]["shifted_rows"] > 0 and table["SEVER"]["content"]["unparsed"] == 0, table["SEVER"]["content"])
    for arm in ("UNPRUNED", "HIST0", "SEXUAL", "PARASITE"):
        expect(f"I7 HOLDS on {arm} (ids are stable identities under every arm without an outside holder)",
               table[arm]["I7"]["verdict"] == "HOLDS", table[arm]["I7"])
    fence = {arm: spop.measure_series(fs)["R_rows_stamped_minus_one_founded_after_the_begin_save"] for arm, fs in files.items()}
    expect("the fixtures exercise the update-0 fencepost (rows stamped -1 that the begin save cannot hold); I7 excludes that pair",
           sum(fence.values()) >= 1, fence)
    # ---- A5: refused at plan time ---------------------------------------------------------------------------
    refused = [
        {"measure": "I2 (dead leaves)", "arm": "HIST0", "why": "save_historic=0 writes no dead rows: eligible is 0 by construction",
         "observed": table["HIST0"]["I2"]},
        {"measure": "organism-level parent-edge recall", "arm": "every .spop",
         "why": "the record is genotype-level: a birth that breeds true, or converges on a living genotype, writes no edge; no organism pedigree exists to score against"},
        {"measure": "genotype-level edge recall against truth", "arm": "every .spop from the body",
         "why": "the truth (every genotype ever founded) is exactly what the save does not contain; defined on the model only"},
        {"measure": "I8 (severance)", "arm": "any run without a parentless re-injection event", "why": "no severing event: nothing to sever"},
        {"measure": "I7 (persistence)", "arm": "a pair of saves whose earlier save is the begin save (T = -1)",
         "why": "the stamp -1 means both 'before the run' and 'during update 0'; a row stamped -1 may postdate that save. "
                "FOUND BY THIS FIXTURE: the first draft of I7 counted such rows as violations (3 in the SEXUAL arm)"},
    ]
    expect("REFUSED I2 on HIST0 really is NOT_ELIGIBLE", table["HIST0"]["I2"]["verdict"] == "NOT_ELIGIBLE", table["HIST0"]["I2"])
    # ---- exclusions are real: the holder arms break exactly the claim they are excluded from ---------------
    expect("PASSIVE_HOLDER (deme-like) produces a dead leaf -> justifies excluding deme runs from I2",
           table["PASSIVE_HOLDER"]["I2"]["count"] >= 1, table["PASSIVE_HOLDER"]["I2"])
    expect("ACTIVE_HOLDER (birth-chamber-like) produces a dangling parent -> justifies excluding sexual runs from I1",
           table["ACTIVE_HOLDER"]["I1"]["count"] >= 1, table["ACTIVE_HOLDER"]["I1"])
    expect("content rule sees a sexual file", table["SEXUAL"]["content"]["multi_parent"] and not table["BASE"]["content"]["multi_parent"])
    expect("content rule sees a parasite file", table["PARASITE"]["content"]["parasite"] and not table["BASE"]["content"]["parasite"])
    expect("HIST0 leaves dangling parents (what LoadPopulation then drops)", table["HIST0"]["I1"]["count"] >= 1, table["HIST0"]["I1"])
    # ---- POSITIVE control -----------------------------------------------------------------------------------
    expect("C-POS: with pruning off the same harness reports dead leaves", table["UNPRUNED"]["I2"]["count"] >= 1, table["UNPRUNED"]["I2"])
    # ---- NEGATIVE control: a save holding only the injected ancestor ---------------------------------------
    first = [f for f in files["BASE"] if f["T"] == -1]
    m0 = spop.measure(first[0])
    neg = {o: _verdict(m0[k], m0[e]) for o, k, e in obs[:3]}
    expect("C-NEG: the begin save (ancestor only) is NOT_ELIGIBLE for I1, I2, I3 -- never a pass",
           m0["n_rows"] == 1 and set(neg.values()) == {"NOT_ELIGIBLE"}, neg)
    # ---- CHEAT controls: inject each violation into the last BASE save and require the count to move -------
    base_last = worlds["BASE"].files[f"detail-{END}.spop"]
    f0 = spop.read_text(base_last, f"detail-{END}.spop")
    m_clean = spop.measure(f0)
    named = {p for r in f0["rows"] for p in r["parents"]}
    dead_parent = next(r["id"] for r in f0["rows"] if r["num_units"] == 0 and r["id"] in named)
    child = next(r["id"] for r in f0["rows"] if r["parents"])
    live = next(r for r in f0["rows"] if r["num_units"] > 0)

    def cheat(fn, key):
        return spop.measure(spop.read_text(_edit(base_last, fn), f"detail-{END}.spop"))[key] - m_clean[key]

    def bump_depth(ls):
        out = []
        for l in ls:
            t = l.split()
            if int(t[0]) == child:
                t[13] = str(int(t[13]) + 1)
            out.append(" ".join(t) + " ")
        return out

    def born_zero(ls):
        t = ls[0].split(); t[11] = "0"
        return [" ".join(t) + " "] + ls[1:]

    cheats = {
        "I1 delete a dead row that is named as a parent": cheat(lambda ls: [l for l in ls if int(l.split()[0]) != dead_parent], "I1_dangling_parent_refs"),
        "I2 append a dead row nobody names": cheat(lambda ls: ls + ["99999 div:int (none) (none) 0 1 12 0 0 0 -1 3 4 0 0 heads_default qqqqqqqqqqqq "], "I2_dead_leaves"),
        "I3 add one to a child's depth": cheat(bump_depth, "I3_depth_violations"),
        "I4 copy a living row under a new id": cheat(lambda ls: ls + [" ".join(["99998"] + [l for l in ls if int(l.split()[0]) == live["id"]][0].split()[1:]) + " "], "I4_live_duplicate_keys"),
        "I6 stamp a row update_born 0": cheat(born_zero, "I6_born_at_zero"),
    }
    for k, d in cheats.items():
        expect(f"C-CHEAT: {k} -> count moves", d >= 1, {"delta": d})
    fs = sorted(files["BASE"], key=lambda f: f["T"])
    keep = {r["id"] for r in fs[-1]["rows"] if r["update_born"] <= fs[-2]["T"]}
    victim = next(iter(keep))
    cut = dict(fs[-2]); cut["rows"] = [r for r in fs[-2]["rows"] if r["id"] != victim]
    d7 = spop.measure_series(fs[:-2] + [cut, fs[-1]])["I7_missing_at_earlier_save"]
    expect("C-CHEAT: I7 drop a persisting row from the earlier save -> count moves", d7 >= 1, {"missing": d7})

    # ---- synthetic calibration, labelled: how much the retention rule keeps (model truth; nothing about Avida) ----
    w = worlds["BASE"]
    kept = sum(1 for g in w.arb.ever if not g.gone)
    calib = {"label": "SYNTHETIC MODEL ONLY -- not a measurement of the fossil",
             "genotypes_ever_founded": len(w.arb.ever), "genotypes_retained_at_end": kept,
             "fraction_of_founded_genotypes_retained": round(kept / len(w.arb.ever), 4),
             "births": w.n_births, "births_that_wrote_a_parent_edge": w.n_edge_births,
             "fraction_of_births_with_a_recorded_edge": round(w.n_edge_births / w.n_births, 4),
             "unpruned_rows_at_end": spop.measure(spop.read_text(worlds["UNPRUNED"].files[f"detail-{END}.spop"]))["n_rows"],
             "pruned_rows_at_end": m_clean["n_rows"]}
    return {"schema": "nyx.avida_ancestry_definedness/1", "fixture": "model.World(seed=20260930, n_cells=30, births_per_update=6, mu=0.35), 40 updates",
            "table": table, "refused_at_plan_time": refused, "controls_and_expectations": checks,
            "all_expectations_met": all(c["ok"] for c in checks), "synthetic_calibration": calib}


def main() -> int:
    r = run()
    OUT.write_text(json.dumps(r, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    for arm, row in r["table"].items():
        cells = "  ".join(f"{o}={v['count']}/{v['eligible']}" for o, v in row.items() if o != "content")
        print(f"{arm:15s} {cells}")
    for c in r["controls_and_expectations"]:
        print(("ok   " if c["ok"] else "FAIL ") + c["check"])
    print("synthetic calibration:", json.dumps(r["synthetic_calibration"]))
    print("ALL EXPECTATIONS MET" if r["all_expectations_met"] else "EXPECTATION FAILED")
    return 0 if r["all_expectations_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
