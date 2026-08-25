#!/usr/bin/env python3
"""Simulated epochs: does the exploit -> defense -> bypass cycle machinery work?

Seats are SCRIPTED, not language models. That is the point. This exercises the
arena's machinery — graph merge, defense promotion against a sealed holdout,
bypass detection, Purple catching bogus kills — on inputs whose ground truth is
known, before any of it is trusted with live agents. Passing here is instrument
calibration, exactly as `generator/pilot.py` is; it says nothing about whether
real agents produce anything worth scoring.

## The falsification test

A simulated game will always look like it works if you only run the arm designed
to work. So two arms run on identical machinery:

  ADAPTIVE  Red inspects promoted defenses and attacks a family none of them
            covers. This is the loop the rulebook predicts.
  NULL      Red picks a family uniformly at random and never looks at the
            defenses. No adaptation exists to detect.

If the cycle metrics cannot separate ADAPTIVE from NULL, the metrics are
decorative and any "the loop closed" claim from a live game would be
unfalsifiable. That separation is tested with a permutation test, and reported
as UNPOWERED when the arms overlap.

  python simulate.py --epochs 60 --reps 12
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent
sys.path.insert(0, str(ARENA / "generator"))

import defenses as DEF  # noqa: E402
import generate as GEN  # noqa: E402
import mutations as MUT  # noqa: E402
import templates as T  # noqa: E402
from derivation import argument_oracle  # noqa: E402

PLAY_TEMPLATES = ["t1_integer_sum_identity", "t2_modular_power_cycle",
                  "t4_linear_recurrence", "t5_collatz_stopping_time"]


# --------------------------------------------------------------------------
# item pool
# --------------------------------------------------------------------------

def build_pool(families: list[str], per_family: int, rng: random.Random,
               budget: int) -> dict[str, list[dict]]:
    """Generated TRUE_BUT_INVALID items, grouped by planted family."""
    pool: dict[str, list[dict]] = {f: [] for f in families}
    for fam in families:
        tries = 0
        while len(pool[fam]) < per_family and tries < per_family * 25:
            tries += 1
            tid = rng.choice(PLAY_TEMPLATES)
            got = GEN.build_one(tid, T.TRUE_INVALID, [fam], rng, budget)
            if not got:
                continue
            item, mut = got
            pool[fam].append({
                "claim_id": f"SIM-{fam}-{len(pool[fam]):03d}",
                "template_id": tid,
                "steps": item.steps,
                "planted_family": fam,
                "target_step": mut["target"],
                "sealed_class": T.TRUE_INVALID,
            })
    return {f: v for f, v in pool.items() if v}


def build_clean(n: int, rng: random.Random, budget: int) -> list[dict]:
    """TRUE_VALID items: the negative regression examples."""
    out = []
    tries = 0
    while len(out) < n and tries < n * 25:
        tries += 1
        tid = rng.choice(PLAY_TEMPLATES)
        got = GEN.build_one(tid, T.TRUE_VALID, [], rng, budget)
        if not got:
            continue
        item, _ = got
        out.append({"claim_id": f"CLEAN-{len(out):03d}", "template_id": tid,
                    "steps": item.steps, "planted_family": None,
                    "target_step": None, "sealed_class": T.TRUE_VALID})
    return out


# --------------------------------------------------------------------------
# graph
# --------------------------------------------------------------------------

class Graph:
    def __init__(self) -> None:
        self.records: list[dict] = []

    def add(self, kind: str, **fields) -> str:
        payload = json.dumps(fields, sort_keys=True)
        nid = hashlib.sha256(f"{kind}:{payload}".encode()).hexdigest()[:12]
        self.records.append({"id": nid, "type": kind, **fields})
        return nid

    def edge(self, rel: str, src: str, dst: str) -> None:
        self.records.append({"type": "EDGE", "rel": rel, "src": src, "dst": dst})

    def write(self, path: Path) -> None:
        path.write_text("".join(json.dumps(r, sort_keys=True) + "\n"
                                for r in self.records),
                        encoding="utf-8", newline="\n")


# --------------------------------------------------------------------------
# one simulated run
# --------------------------------------------------------------------------

def run(arm: str, epochs: int, coverage, pool, holdout, clean, rng,
        p_blue_base: float, p_bogus: float, p_audit: float,
        p_propose: float, graph: Graph | None = None) -> dict:
    families = sorted(pool)
    promoted: dict[str, set[str]] = {}     # defense -> families it demonstrably catches
    events, bypasses, promotions = [], [], []
    first_promotion_epoch = None

    def covered() -> dict[str, float]:
        """Per-family detection probability supplied by promoted defenses."""
        cov: dict[str, float] = {}
        for d in promoted:
            for fam, c in coverage[d].items():
                if c > 0:
                    cov[fam] = max(cov.get(fam, 0.0), c)
        return cov

    for ep in range(epochs):
        cov = covered()
        if arm == "ADAPTIVE":
            uncovered = [f for f in families if cov.get(f, 0.0) < 0.5]
            fam = rng.choice(uncovered or families)
        else:
            fam = rng.choice(families)

        item = rng.choice(pool[fam])
        p_detect = max(p_blue_base, cov.get(fam, 0.0))

        kills, bogus_kills = [], []
        for seat in ("BLUE_A", "BLUE_B"):
            if rng.random() < p_detect:
                kills.append((seat, item["target_step"], True))
            elif rng.random() < p_bogus:
                wrong = rng.choice([s["id"] for s in item["steps"]
                                    if s["id"] != item["target_step"]])
                bogus_kills.append((seat, wrong, False))

        caught_bogus = [b for b in bogus_kills if rng.random() < p_audit]
        landed = not kills                      # both Blues missed the real defect
        is_bypass = landed and promoted and cov.get(fam, 0.0) < 0.5

        proposed = promo = None
        if kills and rng.random() < p_propose:
            best = max(DEF.STRUCTURAL,
                       key=lambda d: coverage[d].get(fam, 0.0))
            if coverage[best].get(fam, 0.0) > 0 and best not in promoted:
                proposed = best
                res = DEF.promotion_test(best, {fam}, holdout + clean)
                if res["promoted"]:
                    promoted[best] = {f for f, c in coverage[best].items() if c > 0}
                    promotions.append({"epoch": ep, "defense": best,
                                       "designed_against": fam,
                                       "independent_hits": res["independent_hits"]})
                    if first_promotion_epoch is None:
                        first_promotion_epoch = ep
                    promo = best

        if is_bypass:
            bypasses.append({"epoch": ep, "family": fam})

        events.append({"epoch": ep, "family": fam, "landed": landed,
                       "was_covered": cov.get(fam, 0.0) >= 0.5,
                       "after_promotion": bool(promoted),
                       "bypass": is_bypass, "kills": len(kills),
                       "bogus": len(bogus_kills), "bogus_caught": len(caught_bogus),
                       "proposed": proposed, "promoted": promo})

        if graph is not None:
            cid = graph.add("CLAIM", claim_id=item["claim_id"], epoch=ep,
                            family=fam, template=item["template_id"])
            for seat, step, valid in kills + bogus_kills:
                aid = graph.add("ATTACK", epoch=ep, seat=seat, target_step=step,
                                valid=valid)
                graph.edge("ATTACKS", aid, cid)
                if valid:
                    graph.edge("FALSIFIES", aid, cid)
            audit = graph.add("AUDIT", epoch=ep, bogus_seen=len(bogus_kills),
                              bogus_caught=len(caught_bogus))
            graph.edge("AUDITS", audit, cid)
            if promo:
                did = graph.add("DEFENSE", epoch=ep, defense=promo,
                                status="PROMOTED", designed_against=fam)
                graph.edge("DEFENDED_BY", cid, did)
            if is_bypass:
                graph.edge("BYPASSES_DEFENSE", cid, "promoted-set")

    # internal control: within this arm, did promoted defenses actually lower
    # the landing rate on the families they cover? If not, the between-arm
    # separation is about Red's choice and nothing about defenses working.
    post = [e for e in events if e["after_promotion"]]
    cov_ev = [e for e in post if e["was_covered"]]
    unc_ev = [e for e in post if not e["was_covered"]]
    bogus_total = sum(e["bogus"] for e in events)
    return {
        "arm": arm,
        "epochs": epochs,
        "promotions": len(promotions),
        "first_promotion_epoch": first_promotion_epoch,
        "bypasses": len(bypasses),
        "bypass_rate_after_promotion": (
            len(bypasses) / max(1, epochs - (first_promotion_epoch or epochs))
            if first_promotion_epoch is not None else 0.0),
        "landed_rate": sum(e["landed"] for e in events) / epochs,
        "bogus_kills": bogus_total,
        "bogus_caught": sum(e["bogus_caught"] for e in events),
        "landed_on_covered": (sum(e["landed"] for e in cov_ev) / len(cov_ev)
                              if cov_ev else None),
        "landed_on_uncovered": (sum(e["landed"] for e in unc_ev) / len(unc_ev)
                                if unc_ev else None),
        "n_covered_epochs": len(cov_ev),
        "n_uncovered_epochs": len(unc_ev),
        "promotion_detail": promotions,
        "events": events,
    }


def permutation_p(a, b, rng, draws=2000):
    obs = abs(statistics.mean(a) - statistics.mean(b))
    pool = list(a) + list(b)
    na, hits = len(a), 0
    for _ in range(draws):
        rng.shuffle(pool)
        if abs(statistics.mean(pool[:na]) - statistics.mean(pool[na:])) >= obs:
            hits += 1
    return (hits + 1) / (draws + 1)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--epochs", type=int, default=60)
    p.add_argument("--reps", type=int, default=12)
    p.add_argument("--seed", type=int, default=20260825)
    p.add_argument("--p-blue", type=float, default=0.35)
    p.add_argument("--p-bogus", type=float, default=0.20)
    p.add_argument("--p-audit", type=float, default=0.70)
    p.add_argument("--p-propose", type=float, default=0.60)
    args = p.parse_args()

    rng = random.Random(args.seed)
    budget = GEN.budget_search_size()
    split = json.loads((ARENA / "generator" / "MUTATION_SPLIT.json")
                       .read_text(encoding="utf-8"))

    L = []
    L.append("SIMULATED EPOCHS — cycle machinery calibration")
    L.append("=" * 70)
    L.append("Scripted seats. No language models. This is instrument")
    L.append("calibration, not a result about agents.")
    L.append("")

    L.append("building item pools ...")
    play_pool = build_pool(split["play"], 6, rng, budget)
    holdout_pool = build_pool(split["holdout"], 5, rng, budget)
    clean = build_clean(12, rng, budget)
    holdout_items = [i for v in holdout_pool.values() for i in v]
    L.append(f"  play families with items    : {len(play_pool)} "
             f"({sorted(f.split('_')[0] for f in play_pool)})")
    L.append(f"  holdout items (promotion)   : {len(holdout_items)} "
             f"from {sorted(f.split('_')[0] for f in holdout_pool)}")
    L.append(f"  clean negative examples     : {len(clean)}")
    L.append("")

    # measured, not declared
    all_items = [i for v in play_pool.values() for i in v] + holdout_items + clean
    coverage: dict[str, dict[str, float]] = {}
    L.append("DEFENSE COVERAGE — measured over items with known planted families")
    L.append("  (declared coverage is recorded and then ignored)")
    for d in DEF.STRUCTURAL:
        m = DEF.measure_coverage(d, all_items)
        cov = {f: m["caught_by_family"].get(f, 0) / n
               for f, n in m["seen_by_family"].items()
               if m["caught_by_family"].get(f, 0)}
        coverage[d] = cov
        L.append(f"  {d}")
        L.append(f"    declared : {m['declared']}")
        L.append(f"    measured : "
                 f"{ {f.split('_')[0]: round(c, 2) for f, c in cov.items()} or 'nothing'}")
        L.append(f"    false positives on clean reasoning: "
                 f"{m['false_positive_rate']:.0%}" if m["false_positive_rate"]
                 is not None else "    no clean items")
    L.append("")

    fp = sum(1 for i in all_items
             if i["planted_family"] and i["target_step"] in DEF.text_fingerprint(i["steps"]))
    planted = sum(1 for i in all_items if i["planted_family"])
    L.append("FINGERPRINT HAZARD (not a defense; the score a prose-matching cheat gets)")
    L.append(f"  a grep over mutation prose would flag {fp}/{planted} planted "
             f"defects = {fp/max(1,planted):.0%}")
    L.append("  structural defenses above never read `text`. If one of them ever")
    L.append("  approaches this number, check why before believing it.")
    L.append("")

    arms = {"ADAPTIVE": [], "NULL": []}
    graph = Graph()
    for rep in range(args.reps):
        for arm in arms:
            r = run(arm, args.epochs, coverage, play_pool, holdout_items, clean,
                    random.Random(args.seed + rep * 7919 + (0 if arm == "ADAPTIVE" else 1)),
                    args.p_blue, args.p_bogus, args.p_audit, args.p_propose,
                    graph if (rep == 0 and arm == "ADAPTIVE") else None)
            arms[arm].append(r)

    graph.write(HERE / "sim_graph.jsonl")

    L.append(f"TWO ARMS — {args.reps} independent runs of {args.epochs} epochs each")
    L.append(f"  Blue base detection {args.p_blue:.0%} · bogus-kill rate "
             f"{args.p_bogus:.0%} · Purple audit {args.p_audit:.0%} · "
             f"defense proposal {args.p_propose:.0%}")
    L.append("")
    metrics = ["promotions", "bypasses", "landed_rate", "bogus_caught"]
    L.append(f"  {'metric':<28s} {'ADAPTIVE':>12s} {'NULL':>12s} {'perm p':>9s}")
    prng = random.Random(7)
    verdicts = {}
    for m in metrics:
        a = [r[m] for r in arms["ADAPTIVE"]]
        b = [r[m] for r in arms["NULL"]]
        pv = permutation_p(a, b, prng)
        verdicts[m] = pv
        L.append(f"  {m:<28s} {statistics.mean(a):>12.2f} "
                 f"{statistics.mean(b):>12.2f} {pv:>9.3f}")
    L.append("")

    L.append("FALSIFICATION CHECK")
    sep = [m for m, pv in verdicts.items() if pv < 0.05]
    if "bypasses" in sep or "landed_rate" in sep:
        L.append("  The cycle metrics SEPARATE an adapting Red from a random one.")
        L.append(f"  Separating metrics: {sep}")
        L.append("  A live game's 'the loop closed' claim would therefore be")
        L.append("  falsifiable on this machinery.")
    else:
        L.append("  The cycle metrics DO NOT separate an adapting Red from a")
        L.append("  random one. Any 'the loop closed' claim measured this way")
        L.append("  would be unfalsifiable. Fix the metrics before playing live.")
        L.append(f"  p-values: { {m: round(v,3) for m, v in verdicts.items()} }")
    L.append("")

    L.append("INTERNAL CONTROL — are the defenses doing the work?")
    L.append("  Within each arm, after the first promotion, landing rate on")
    L.append("  families a promoted defense covers vs families it does not.")
    for arm in ("ADAPTIVE", "NULL"):
        c = [r["landed_on_covered"] for r in arms[arm]
             if r["landed_on_covered"] is not None]
        u = [r["landed_on_uncovered"] for r in arms[arm]
             if r["landed_on_uncovered"] is not None]
        if c and u:
            pv = permutation_p(c, u, prng)
            L.append(f"  {arm:<9s} covered {statistics.mean(c):.2f}  "
                     f"uncovered {statistics.mean(u):.2f}  perm p {pv:.3f}")
        else:
            L.append(f"  {arm:<9s} insufficient epochs in one cell")
    L.append("  If covered and uncovered do not differ, a promoted defense is")
    L.append("  not raising detection and the cycle is cosmetic.")
    L.append("")

    L.append("WHAT THIS SIMULATION CANNOT TEST")
    L.append("  The family set is CLOSED: Red chooses from eight known mutation")
    L.append("  families. A bypass here means picking a family no promoted")
    L.append("  defense covers — never inventing one that does not yet exist.")
    L.append("  The rulebook's most interesting outcome, Red producing an")
    L.append("  unforeseen attack, is outside this vocabulary by construction.")
    L.append("  Scripted seats cannot invent; that is what live agents are for.")
    L.append("")

    ex = arms["ADAPTIVE"][0]
    L.append("ONE ADAPTIVE RUN, in detail (graph written to sim_graph.jsonl)")
    L.append(f"  promotions {ex['promotions']}, first at epoch "
             f"{ex['first_promotion_epoch']}, bypasses {ex['bypasses']}")
    for pr in ex["promotion_detail"]:
        hits = ", ".join(f"{f.split('_')[0]}" for _, f in pr["independent_hits"][:4])
        L.append(f"    epoch {pr['epoch']:>3d}  {pr['defense']}")
        L.append(f"              designed against {pr['designed_against'].split('_')[0]}, "
                 f"promoted on independent hits: {hits}")
    if not ex["promotion_detail"]:
        L.append("    no defense reached promotion in this run")
    L.append(f"  bogus kills {ex['bogus_kills']}, caught by Purple "
             f"{ex['bogus_caught']} "
             f"({ex['bogus_caught']/max(1,ex['bogus_kills']):.0%})")

    text = "\n".join(L)
    print(text)
    (HERE / "SIMULATION.txt").write_text(text + "\n", encoding="utf-8", newline="\n")
    (HERE / "SIMULATION.json").write_text(json.dumps({
        "config": vars(args), "coverage": coverage,
        "arms": {k: [{kk: vv for kk, vv in r.items() if kk != "events"}
                     for r in v] for k, v in arms.items()},
        "permutation_p": verdicts,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
