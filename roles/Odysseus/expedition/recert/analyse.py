"""Tables for RESULT.md from L1_rows.json / L2_rows.json (+ L2_oracle.json) / L3_rows.json. Pure read; prints ASCII.

    python3 analyse.py > TABLES.txt
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ABBR = {"LABEL_OK": "OK", "LABEL_CONTEXT_DEPENDENT": "CTX", "BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM": "BWEM",
        "STRUCTURE_WITHOUT_BEHAVIOUR": "SWB", "LABEL_PROVENANCE_ONLY": "PROV"}
COLS = ["OK", "CTX", "BWEM", "SWB", "PROV"]


def load(name):
    return json.load(open(os.path.join(HERE, name)))


def table(title, groups):
    print(title)
    print("  %-44s %5s " % ("group", "n") + " ".join("%5s" % c for c in COLS) + "  not-OK")
    tot = Counter()
    for g, rows in groups:
        c = Counter(ABBR[r["now"]] for r in rows)
        tot.update(c)
        n = len(rows)
        print("  %-44s %5d " % (g[:44], n) + " ".join("%5d" % c[k] for k in COLS) + "  %5.1f%%" % (100 * (n - c["OK"]) / max(1, n)))
    n = sum(tot.values())
    print("  %-44s %5d " % ("TOTAL", n) + " ".join("%5d" % tot[k] for k in COLS) + "  %5.1f%%" % (100 * (n - tot["OK"]) / max(1, n)))
    print()


def origin_class(r):
    cells = " ".join(r["then"].get("cells", []))
    lanes = r["then"].get("lanes", [])
    if "HIST" in lanes:
        return "HIST (historical origin transplanted)"
    if "SEEDED" in cells or "pos_" in cells or "G5" in lanes:
        return "seeded replicator populations"
    return "random-start (de novo candidates)"


def l1():
    d = load("L1_rows.json")
    rows = d["rows"]
    g = [r for r in rows if r["id"].startswith("G:")]
    c = [r for r in rows if r["id"].startswith("C:")]
    print("=== L1 BEE self-replicator ===  wall_s", d.get("wall_s"))
    by = defaultdict(list)
    for r in g:
        by[origin_class(r)].append(r)
    table("L1a grounding dominant_sr_tape (distinct tape x chemistry), by origin", sorted(by.items()))
    by = defaultdict(list)
    for r in g:
        by[",".join(r["then"]["lanes"])].append(r)
    table("L1b grounding, by lane", sorted(by.items()))
    by = defaultdict(list)
    for r in g:
        if origin_class(r).startswith("random"):
            by[r["then"]["cells"][0]].append(r)
    table("L1c random-start cells", sorted(by.items()))
    by = defaultdict(list)
    for r in c:
        by[r["then"]["arm"] + (" copyless" if not r["then"]["ledger_n_copy_ops"] else " copy-bearing")].append(r)
    table("L1d coupling origin ledger (S1's 68), by arm x ledger n_copy_ops", sorted(by.items()))
    # then-vs-now: the descriptor's self_copy at the time vs verdict now
    tv = Counter((",".join(r["then"]["descriptor_self_copy_then"]), ABBR[r["now"]]) for r in g)
    print("L1e grounding: descriptor self_copy THEN (repro_descriptor, input 42, zero window) x verdict NOW")
    for k, v in sorted(tv.items()):
        print("  then=%-12s now=%-5s %5d" % (k[0], k[1], v))
    print()
    ok = [r for r in g + c if r["now"] == "LABEL_OK"]
    bits = sorted(r["causal"]["bits_transmitted"] for r in ok)
    lowc = sum(1 for r in ok if r["structural"]["dominant_byte_share"] >= 0.8)
    ko = [r["causal"]["behaviour_after_copy_op_knockout"] for r in ok if r["causal"].get("behaviour_after_copy_op_knockout") is not None]
    print("L1f information and mechanism among LABEL_OK (n=%d):" % len(ok))
    if bits:
        print("  bits_transmitted min/median/max: %d / %d / %d  (homopolymer painter: 0)" % (bits[0], bits[len(bits) // 2], bits[-1]))
    print("  tape content near-homopolymer (dominant byte >= 0.8): %d" % lowc)
    print("  executed copy-op knockout: behaviour gone (rate 0) in %d of %d; retained >= 0.5 in %d" % (
        sum(1 for x in ko if x == 0), len(ko), sum(1 for x in ko if x >= 0.5)))
    wr = [r["causal"].get("world_rule_rate") for r in g + c if r["now"] == "LABEL_OK"]
    print("  world copy-op self_copy rule rate among OK: min %.2f" % min(wr) if wr else "")
    bw = [r for r in g + c if r["now"] == "BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM"]
    print("  BWEM rows: %d; their transmission: %s" % (len(bw), sorted(r["causal"]["transmission"] for r in bw)[:20]))
    ctx = [r for r in g + c if r["now"] == "LABEL_CONTEXT_DEPENDENT"]
    pe = Counter(tuple(sorted({e["w"] for e in r["behavioural"]["passing_envs"]})) for r in ctx)
    print("  CTX rows: %d; windows in which they pass (first 8 passing envs): %s" % (len(ctx), dict(pe.most_common(6))))
    print()


def l2():
    d = load("L2_rows.json")
    orc = {r["id"]: r for r in load("L2_oracle.json")["rows"]}
    rows = d["rows"]
    print("=== L2 NPE P-11 causal copy ===  wall_s", d.get("wall_s"))
    by = defaultdict(list)
    for r in rows:
        by[r["structural"]["copy_primitive"] + (" near-homopolymer" if r["structural"]["near_homopolymer"] else " high-entropy")].append(r)
    table("L2a the 57 P-11-certified donors, by copy primitive x genome content", sorted(by.items()))
    print("L2b per donor: THEN (P-11 record) | NOW (this harness)")
    print("  %-30s %-8s %-5s %-5s %-4s | %-5s %5s %5s %6s %5s %5s %-6s" % ("run", "prim", "depth", "draws", "dom", "now", "rate",
                                                                      "fresh", "T", "bits", "orac", "domb"))
    for r in sorted(rows, key=lambda r: (r["now"], r["id"])):
        t, s, c = r["then"], r["structural"], r["causal"]
        print("  %-30s %-8s %-5s %-5s %-4s | %-5s %5.2f %5.2f %6s %5s %5s %-6s" % (
            t["run_id"][:30], s["copy_primitive"], t["max_p11_depth_then"], t["draws_passed_then"],
            "%.2f" % s["dominant_byte_share"], ABBR[r["now"]], r["behavioural"]["pass_rate"], c.get("fresh_state_pass_rate", 0),
            "-" if c.get("transmission") is None else "%.3f" % c["transmission"],
            "-" if c.get("bits_transmitted") is None else c["bits_transmitted"],
            "Y" if orc[r["id"]]["passes_with_oracle_registers"] else "n", s["dominant_byte"]))
    print()
    swb = [r for r in rows if r["now"] == "STRUCTURE_WITHOUT_BEHAVIOUR"]
    print("L2c SWB donors that DO copy when handed the ideal register file (oracle): %d of %d" % (
        sum(orc[r["id"]]["passes_with_oracle_registers"] for r in swb), len(swb)))
    d2 = [r for r in rows if r["then"]["max_p11_depth_then"] >= 2]
    print("L2d depth-2 P-11 lineages: %s" % [(r["then"]["run_id"][:12], ABBR[r["now"]]) for r in d2])
    print()


def l3():
    d = load("L3_rows.json")
    rows = d["rows"]
    print("=== L3 BEE competent / verified exact solver ===  wall_s", d.get("wall_s"))
    by = defaultdict(list)
    for r in rows:
        src = "coupling ledger" if r["id"].startswith("C:") else "grounding " + ",".join(r["then"]["lanes"])
        by[src + " | " + r["then"]["task"]["kind"]].append(r)
    table("L3a by source x task", sorted(by.items()))
    acc = defaultdict(list)
    for r in rows:
        for w, a in (r["causal"].get("accuracy_by_window") or {}).items():
            acc[w].append(a)
    print("L3b accuracy by window (mean over objects): " + ", ".join("%s %.3f" % (w, sum(v) / len(v)) for w, v in sorted(acc.items())))
    po = sum(1 for r in rows if r["causal"].get("panel_inputs_only"))
    print("L3c right on the 16 panel inputs but not on all 256 (zero window): %d of %d" % (po, len(rows)))
    notok = [r for r in rows if r["now"] != "LABEL_OK"]
    for r in notok[:25]:
        c = r["causal"]
        print("  %-16s %-5s task=%-9s rate=%.3f acc=%s ko=%s mech=%s then=%s" % (
            r["id"], ABBR[r["now"]], r["then"]["task"]["kind"], r["behavioural"]["pass_rate"], c.get("accuracy_by_window"),
            c.get("accuracy_after_IN_knockout"), c.get("mechanism"), r["then"].get("ledger_task_accuracy_then", "-")))
    zero_then = [r for r in rows if r["then"].get("ledger_task_accuracy_then") == 0.0]
    print("L3d coupling rows with ledger task_accuracy 0.0 THEN: %s" % [(r["id"], ABBR[r["now"]]) for r in zero_then])
    print()


if __name__ == "__main__":
    for f, fn in (("L1_rows.json", l1), ("L2_rows.json", l2), ("L3_rows.json", l3)):
        if os.path.exists(os.path.join(HERE, f)):
            fn()
