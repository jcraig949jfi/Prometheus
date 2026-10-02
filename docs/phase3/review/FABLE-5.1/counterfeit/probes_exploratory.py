"""Exploratory probes of runs 2 and 3. NOT preregistered. Design seeds only.

A third reviewer probed gauntlet2.py and gauntlet3.py on design seeds and showed that several
statements in a draft of the review rested on things the two runs do not vary: what family A is, what
family C is, the savings factor, the acceptance rule, the number of inherited orders, and how the
worlds are chosen. This file reproduces the probes the review now cites, so that every number quoted
from them has a receipt. It was written after the registered runs and after seeing the reviewer's
results. Nothing here is a registered result.

It imports the two preregistered scripts unchanged, changes module attributes in memory only, and
never uses a registered seed base. Entries under "registered_arithmetic" are arithmetic on the two
registered receipts, which are read and not rewritten.

Counts are "of 24 replicates", one number per design base, in this order:
    gauntlet2: 37, 41, 53, 67, 71, 83        gauntlet3: 43, 47, 59, 61, 73, 79

    python probes_exploratory.py             writes RECEIPT_probes_exploratory.json (about 4 minutes)
"""
import sys

sys.dont_write_bytecode = True

import collections
import hashlib
import json
import pathlib
import platform
import statistics
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone

import gauntlet2 as g2
import gauntlet3 as g3

HERE = pathlib.Path(__file__).resolve().parent
G2_BASES = (37, 41, 53, 67, 71, 83)
G3_BASES = (43, 47, 59, 61, 73, 79)
N = 24
ORIG_SETUP2 = g2.setup
ORIG_SETUP3 = g3.setup
ORIG_SHUFFLED = g2.shuffled
assert max(G2_BASES + G3_BASES) + 900 < 100000 < g2.REGISTERED_BASE, "design bases only"


def rel2(o, factor=4):
    """gauntlet2's six relations with the savings factor as a parameter (4 as registered)."""
    slack = 2 * o["dev_B"] + 4
    return {
        "SAVINGS": factor * o["dev_B"] <= o["naive_B"],
        "LIFECYCLE": o["lifecycle_developed"] < o["lifecycle_naive"],
        "U_TRANSFER": (o["q_C_same_kind"] <= g2.GOOD_MAX and o["q_C_narrower"] <= g2.GOOD_MAX
                       and o["q_C_lesioned_line"] >= g2.BAD_MIN),
        "NESTING": (2 * o["lesion_B"] >= o["naive_B"] and o["sham_B"] <= slack and o["rescue_B"] <= slack
                    and factor * o["v_donor_B"] <= o["naive_B"]),
        "PROVENANCE": 2 * o["wrong_history_B"] >= o["naive_B"] and 2 * o["random_library_B"] >= o["naive_B"],
        "REPEAT": factor * o["dev_D"] <= o["naive_D"] and factor * o["dev_E"] <= o["naive_E"],
    }


def rel3(o, factor=2):
    """gauntlet3's six relations with the savings factor as a parameter (2 as registered)."""
    slack = 2 * o["dev_B"] + 4
    return {
        "SAVINGS": factor * o["dev_B"] <= o["naive_B"],
        "LIFECYCLE": o["lifecycle_developed"] < o["lifecycle_naive"],
        "U_TRANSFER": (o["q_C_same_kind"] <= g2.GOOD_MAX and o["q_C_narrower"] <= g2.GOOD_MAX
                       and o["q_C_lesioned_line"] >= g2.BAD_MIN),
        "NESTING": (2 * o["lesion_B"] >= o["naive_B"] and o["sham_B"] <= slack and o["rescue_B"] <= slack
                    and factor * o["v_donor_B"] <= o["naive_B"]),
        "PROVENANCE": 2 * o["irrelevant_history_B"] >= o["naive_B"] and 2 * o["random_V_B"] >= o["naive_B"],
        "REPEAT": factor * o["dev_D"] <= o["naive_D"] and factor * o["dev_E"] <= o["naive_E"],
    }


def verdict(counts):
    states = ["HOLDS" if v >= g2.HOLDS_AT else "FAILS" if v <= g2.FAILS_AT else "INDETERMINATE"
              for v in counts.values()]
    if all(s == "HOLDS" for s in states):
        return "PASS"
    return "FAIL" if "FAILS" in states else "INDETERMINATE"


def tally(reps, rel, factor):
    rels = [rel(o, factor) for o in reps]
    counts = {c: sum(1 for x in rels if x[c]) for c in g2.CONJUNCTS}
    return {"counts": counts, "verdict": verdict(counts)}


def by_base(cells):
    """A list of per-base tallies -> per-conjunct lists in base order, plus the verdicts."""
    out = {c: [x["counts"][c] for x in cells] for c in g2.CONJUNCTS}
    out["verdicts"] = [x["verdict"] for x in cells]
    return out


def med(reps, key):
    return statistics.median(o[key] for o in reps)


BUILDER2 = lambda o: g2.Builder(o)
STRATEGIST = lambda o: g3.Strategist(o)
BUILDER3 = lambda o: g3.LibraryBuilder(o)


# ---------------------------------------------------------------- sections

def clauses2(o, factor=4):
    """gauntlet2's six relations split into their thirteen clauses."""
    slack = 2 * o["dev_B"] + 4
    return {
        "SAVINGS": factor * o["dev_B"] <= o["naive_B"],
        "LIFECYCLE": o["lifecycle_developed"] < o["lifecycle_naive"],
        "U_TRANSFER.frozen_U_good_on_C": o["q_C_same_kind"] <= g2.GOOD_MAX,
        "U_TRANSFER.frozen_U_good_on_narrower_C": o["q_C_narrower"] <= g2.GOOD_MAX,
        "U_TRANSFER.lesioned_line_bad_on_C": o["q_C_lesioned_line"] >= g2.BAD_MIN,
        "NESTING.lesion_hurts": 2 * o["lesion_B"] >= o["naive_B"],
        "NESTING.sham_harmless": o["sham_B"] <= slack,
        "NESTING.rescue_restores": o["rescue_B"] <= slack,
        "NESTING.donor_V_helps": factor * o["v_donor_B"] <= o["naive_B"],
        "PROVENANCE.wrong_history_no_help": 2 * o["wrong_history_B"] >= o["naive_B"],
        "PROVENANCE.random_library_no_help": 2 * o["random_library_B"] >= o["naive_B"],
        "REPEAT.D": factor * o["dev_D"] <= o["naive_D"],
        "REPEAT.E": factor * o["dev_E"] <= o["naive_E"],
    }


def sec_baseline():
    """Three registered cells (run 2's BUILDER; run 3's STRATEGIST and BUILDER) on the design bases, as a reference."""
    out = {}
    cells = [tally([g2.replicate(BUILDER2, b + 100, r) for r in range(N)], rel2, 4) for b in G2_BASES]
    out["run2_BUILDER_factor4"] = by_base(cells)
    for name, make, ofs in (("STRATEGIST", STRATEGIST, 100), ("BUILDER", BUILDER3, 200)):
        reps_by_base = [[g3.replicate(make, b + ofs, r) for r in range(N)] for b in G3_BASES]
        for f in (2, 4):
            out["run3_%s_factor%d" % (name, f)] = by_base([tally(reps, rel3, f) for reps in reps_by_base])
    return out


def _world3(base, r):
    s = dict(ORIG_SETUP3(base, r))
    parts = g2.shuffled(g2.PARTS, base, r, 2, s["salt"])
    return s, parts[:4], parts[4:8]


def _composites(parts4, avoid, base, r, salt, tag):
    out = []
    for a, b in g2.shuffled([(a, b) for a in parts4 for b in parts4 if a != b], base, r, tag, salt):
        if g2.good_target(a + b, avoid + out):
            out.append(a + b)
    return out


def _setup3(mode, n_fam=1):
    """gauntlet3's world with the development curriculum replaced. Targets are never changed."""
    def f(base, r):
        s, tparts, hparts = _world3(base, r)
        if mode == "four_parts_of_the_targets":             # run 2's curriculum: the targets' own parts
            s["history"], s["history2"] = list(tparts), list(tparts)
        elif mode == "four_parts_disjoint":                 # four part families; targets use other parts
            s["history"], s["history2"] = list(hparts), list(hparts)
        elif mode == "one_composite_of_the_targets_parts":  # one composite family built from the targets' parts
            comp = _composites(tparts, list(s["targets"]), base, r, s["salt"], 41)
            if len(comp) < 2:
                raise RuntimeError("not enough composites")
            s["history"], s["history2"] = comp[:1], comp[1:2]
        elif mode == "four_parts_disjoint_plus_one_composite":
            comp = _composites(hparts, list(s["targets"]), base, r, s["salt"], 4)
            s["history"], s["history2"] = list(hparts) + comp[:1], list(hparts) + comp[1:2]
        elif mode == "n_composites_disjoint":
            comp = _composites(hparts, list(s["targets"]), base, r, s["salt"], 4)
            if len(comp) < n_fam + 1:
                raise RuntimeError("not enough composites")
            s["history"] = comp[:n_fam]
            s["history2"] = comp[n_fam:2 * n_fam] if len(comp) >= 2 * n_fam else comp[::-1][:n_fam]
        else:
            assert mode == "one_composite_disjoint"         # run 3 as registered
        return s
    return f


def sec_curriculum():
    """What family A is, crossed with whether its parts are the targets' parts. gauntlet3 harness, factor 2."""
    out = {}
    for mode in ("four_parts_of_the_targets", "four_parts_disjoint", "one_composite_of_the_targets_parts",
                 "one_composite_disjoint", "four_parts_disjoint_plus_one_composite"):
        g3.setup = _setup3(mode)
        for name, make, ofs in (("STRATEGIST", STRATEGIST, 100), ("BUILDER", BUILDER3, 200)):
            cells, same, ratio = [], [], []
            for b in G3_BASES:
                reps = [g3.replicate(make, b + ofs, r) for r in range(N)]
                cells.append(tally(reps, rel3, 2))
                same.append(sum(1 for o in reps if o["dev_B"] == o["naive_B"]))
                ratio.append([med(reps, "naive_B"), med(reps, "dev_B")])
            row = by_base(cells)
            row["developed_cost_equals_naive"] = same
            row["median_naive_B_and_developed_B"] = ratio
            out["%s__%s" % (mode, name)] = row
    g3.setup = ORIG_SETUP3
    return out


def sec_strict_c():
    """Step 6 with C a kind never met: the frozen U_B scored on D's and E's kinds by the same quality()."""
    out = {"BUILDER_run2_world": {}, "STRATEGIST_run3_world": {}}
    rows = collections.defaultdict(list)
    for b in G2_BASES:
        base = b + 100
        q = collections.defaultdict(list)
        for r in range(N):
            s = g2.setup(base, r)
            kb, kd, ke = s["targets"]
            seed = lambda tag, n=0: g2.khash(base, r, tag, n)
            org = g2.Builder(s["order"])
            org.develop(g2.shuffled([(k, seed(20, n)) for n, k in enumerate(s["hist"])], base, r, 5))
            u_b = org.construct(kb, seed(10, 0))[0]
            q["same_kind"].append(g2.quality(u_b, kb, seed(30)))
            q["kind_of_D"].append(g2.quality(u_b, kd, seed(30)))
            q["kind_of_E"].append(g2.quality(u_b, ke, seed(30)))
        for k, v in q.items():
            rows[k + "_good_of_24"].append(sum(1 for x in v if x <= g2.GOOD_MAX))
            rows[k + "_median_errors"].append(round(statistics.median(v), 2))
    out["BUILDER_run2_world"] = dict(rows)
    rows = collections.defaultdict(list)
    for b in G3_BASES:
        base = b + 100
        q = collections.defaultdict(list)
        for r in range(N):
            s = g3.setup(base, r)
            kb, kd, ke = s["targets"]
            seed = lambda tag, n=0: g2.khash(base, r, tag, n)
            org = g3.Strategist(s["order"])
            org.develop([(k, seed(20, n)) for n, k in enumerate(s["history"])])
            u_b = org.construct(kb, seed(10, 0))[0]
            q["same_kind"].append(g2.quality(u_b, kb, seed(30)))
            q["kind_of_D"].append(g2.quality(u_b, kd, seed(30)))
            q["kind_of_E"].append(g2.quality(u_b, ke, seed(30)))
        for k, v in q.items():
            rows[k + "_good_of_24"].append(sum(1 for x in v if x <= g2.GOOD_MAX))
            rows[k + "_median_errors"].append(round(statistics.median(v), 2))
    out["STRATEGIST_run3_world"] = dict(rows)
    return out


def sec_k():
    """STRATEGIST with K inherited orders (32 as registered). Factor 2."""
    orig_sham = g3.Strategist.sham

    def safe_sham(self):
        if len([i for i in range(1, g3.K) if i not in (self.front, self.useful)]) >= 2:
            orig_sham(self)             # with fewer than two idle orders the sham is a no-op

    g3.Strategist.sham = safe_sham
    out = {}
    for k in (2, 3, 4, 8, 16, 32, 64):
        g3.K = k
        out["K=%d" % k] = by_base([tally([g3.replicate(STRATEGIST, b + 100, r) for r in range(N)], rel3, 2)
                                   for b in G3_BASES])
    g3.K = 32
    g3.Strategist.sham = orig_sham
    return out


def sec_factor():
    """Run 2's BUILDER on design bases at other savings factors (4 as registered)."""
    reps_by_base = [[g2.replicate(BUILDER2, b + 100, r) for r in range(N)] for b in G2_BASES]
    return {"factor=%d" % f: by_base([tally(reps, rel2, f) for reps in reps_by_base]) for f in (2, 4, 6, 8, 16)}


def _setup2_variant(base, r, off_history=False, condition=True, stats=None):
    """gauntlet2.setup with its three label conditions switchable, and counters for what they reject."""
    order = g2.shuffled(g2.PRIMS, base, r, 1)
    for salt in range(200):
        parts = g2.shuffled(g2.PARTS, base, r, 2, salt)
        hist, rest = parts[:4], parts[4:]
        targets, first_seen = [], False
        for a, b in g2.shuffled([(a, b) for a in hist for b in hist if a != b], base, r, 3, salt):
            t = a + b
            if not targets:
                unique = g2.covering_pairs(t, hist) == [(a, b)]
                if g2.good_target(t, targets) and not first_seen:
                    first_seen = True
                    if stats is not None and not unique:
                        stats["first_candidate_B_rejected_second_decomposition"] += 1
                if condition and not unique:
                    continue
            if g2.good_target(t, targets):
                targets.append(t)
            if len(targets) == 3:
                break
        if len(targets) < 3:
            continue
        wrong = None
        for drop in range(len(rest)):
            cand = rest[:drop] + rest[drop + 1:]
            covers = g2.covering_pairs(targets[0], cand)
            if drop == 0 and stats is not None and covers:
                stats["first_four_other_parts_compose_B"] += 1
            if not condition or not covers:
                wrong = cand
                break
        if wrong is None:
            continue
        junk = []
        for t in g2.shuffled(g2.DEPTH2, base, r, 8, salt):
            unrelated = not any(g2.klass(t) <= g2.klass(h) or g2.klass(h) <= g2.klass(t) for h in hist)
            if unrelated and (not condition or not g2.covering_pairs(targets[0], junk + [t])):
                junk.append(t)
            if len(junk) == len(hist):
                break
        if len(junk) < len(hist):
            continue
        assert not off_history
        if stats is not None:
            stats["worlds"] += 1
            stats["salt_above_zero"] += 1 if salt else 0
        return {"order": order, "hist": hist, "wrong": wrong, "junk": junk, "targets": targets, "salt": salt}
    raise RuntimeError("no world")


def sec_selection():
    """How gauntlet2.setup makes its labels true: by choosing inside the first draw, not by redrawing."""
    same = all(_setup2_variant(b + 100, r) == ORIG_SETUP2(b + 100, r) for b in G2_BASES for r in range(N))
    stats = collections.Counter({"worlds": 0, "salt_above_zero": 0,
                                 "first_candidate_B_rejected_second_decomposition": 0,
                                 "first_four_other_parts_compose_B": 0})
    for r in range(2000):
        _setup2_variant(137, r, stats=stats)
    g2.setup = lambda base, r, off_history=False: _setup2_variant(base, r, off_history, condition=False)
    cells = [tally([g2.replicate(BUILDER2, b + 100, r) for r in range(N)], rel2, 4) for b in G2_BASES]
    g2.setup = ORIG_SETUP2
    return {"variant_with_conditions_equals_gauntlet2_setup_on_144_worlds": same,
            "over_2000_design_worlds_base_137": dict(stats),
            "BUILDER_with_the_conditions_off": by_base(cells)}


def sec_confirm():
    """Run 2's BUILDER when a candidate is accepted after CONFIRM passed tasks (8 as registered)."""
    out = {}
    for c in (1, 2, 3, 8):
        g2.CONFIRM = c
        out["CONFIRM=%d" % c] = by_base([tally([g2.replicate(BUILDER2, b + 100, r) for r in range(N)], rel2, 4)
                                         for b in G2_BASES])
    g2.CONFIRM = 8
    return out


def sec_memoriser():
    """Run 2's MEMORISER in the leak world, with the content resets applied and with both skipped."""
    orig = g2.Builder.reset_content
    make = lambda o: g2.Builder(o, write=False, memoriser=True)
    out = {}
    for label, fn in (("resets_applied", orig), ("resets_skipped", lambda self: None)):
        g2.Builder.reset_content = fn
        out[label] = by_base([tally([g2.replicate(make, b + 800, r, leak=True) for r in range(N)], rel2, 4)
                              for b in G2_BASES])
    g2.Builder.reset_content = orig
    return out


class AcceptedOnly(g3.Strategist):
    """STRATEGIST whose switch ranks only the accepted template, not every template of its function class."""

    def construct(self, kind, seed, limit=None):
        cost = 0
        for j, tmpl in enumerate(self.orders[self.front]):
            if limit is not None and cost >= limit:
                return None, cost
            ok, used = g2.passes(tmpl, kind, seed, j)
            cost += used
            if ok:
                best = min(range(g3.K), key=lambda s: (self.rank[s][tmpl], s != self.front, s))
                if self.rank[best][tmpl] < self.rank[self.front][tmpl]:
                    self.front = best
                return tmpl, cost
        return None, cost + 1

    def clone(self):
        c = AcceptedOnly.__new__(AcceptedOnly)
        c.__dict__.update(self.__dict__)
        return c


def sec_strategist_variants():
    """STRATEGIST with three composite families (the registered list of 81 pairs and the superseded list of 144),
    and with a switch that ranks only the accepted template. Factor 2."""
    out = {}
    g3.setup = _setup3("n_composites_disjoint", 3)
    out["three_composite_families__registered_organism"] = by_base(
        [tally([g3.replicate(STRATEGIST, b + 100, r) for r in range(N)], rel3, 2) for b in G3_BASES])
    orig_pairs = g3.RAW_PAIRS
    g3.RAW_PAIRS = set(a + b for a in g2.ALL_PARTS for b in g2.ALL_PARTS)
    out["three_composite_families__superseded_list_of_144_pairs"] = by_base(
        [tally([g3.replicate(STRATEGIST, b + 100, r) for r in range(N)], rel3, 2) for b in G3_BASES])
    out["superseded_list_length"] = len(g3.RAW_PAIRS)
    g3.RAW_PAIRS = orig_pairs
    g3.setup = ORIG_SETUP3
    out["switch_ranks_only_the_accepted_template"] = by_base(
        [tally([g3.replicate(lambda o: AcceptedOnly(o), b + 100, r) for r in range(N)], rel3, 2) for b in G3_BASES])
    return out


def sec_power():
    """240 design replicates of run 3's STRATEGIST cell (base 43), in ten blocks of 24."""
    reps = [g3.replicate(STRATEGIST, 143, r) for r in range(240)]
    out = {}
    for f in (2, 4):
        t = tally(reps, rel3, f)
        out["factor=%d" % f] = {"holds_of_240": t["counts"],
                                "block_verdicts": [tally(reps[i:i + N], rel3, f)["verdict"] for i in range(0, 240, N)]}
    out["development_plus_B_cheaper_than_naive_B_of_240"] = sum(
        1 for o in reps if o["development"] + o["dev_B"] < o["naive_B"])
    return out


def sec_reading1():
    """Run 1's reading (the target is a new seed of a kind already met) under run 2's cost, library learner."""
    out = collections.defaultdict(list)
    for b in G2_BASES:
        base = b + 100
        rows = []
        for r in range(N):
            s = g2.setup(base, r)
            seed = lambda tag, n=0: g2.khash(base, r, tag, n)
            org = g2.Builder(s["order"])
            dev = org.develop(g2.shuffled([(k, seed(20, n)) for n, k in enumerate(s["hist"])], base, r, 5))
            res = []
            for n, k in enumerate(s["hist"][:3]):
                fam = seed(60, n)
                res.append((g2.Builder(s["order"]).construct(k, fam)[1], org.clone().construct(k, fam)[1]))
            rows.append((dev, res))
        out["SAVINGS_factor4"].append(sum(1 for dev, res in rows if 4 * res[0][1] <= res[0][0]))
        out["SAVINGS_factor2"].append(sum(1 for dev, res in rows if 2 * res[0][1] <= res[0][0]))
        out["LIFECYCLE"].append(sum(1 for dev, res in rows if dev + sum(d for n, d in res) < sum(n for n, d in res)))
        out["median_naive_and_developed"].append([statistics.median(res[0][0] for dev, res in rows),
                                                  statistics.median(res[0][1] for dev, res in rows)])
    return dict(out)


def sec_families():
    """Run 2's BUILDER when development is the first 1, 2 or 3 of its four part families (4 as registered)."""
    out = {}
    for n_dev in (1, 2, 3, 4):
        def patched(items, *key):
            got = ORIG_SHUFFLED(items, *key)
            if len(key) == 3 and key[2] in (5, 6):          # the two history lists of gauntlet2.replicate
                return got[:n_dev]
            return got
        g2.shuffled = patched
        out["development_families=%d" % n_dev] = by_base(
            [tally([g2.replicate(BUILDER2, b + 100, r) for r in range(N)], rel2, 4) for b in G2_BASES])
        g2.shuffled = ORIG_SHUFFLED
    return out


def sec_facts():
    """Facts about run 3's world and organisms on the 144 design replicates."""
    index = collections.Counter()
    after_irrelevant = collections.Counter()
    lib = collections.Counter()
    targets = in_list = covered = history_in_list = history_n = 0
    for b in G3_BASES:
        for r in range(N):
            base = b + 100
            s = g3.setup(base, r)
            seed = lambda tag, n=0: g2.khash(base, r, tag, n)
            org = g3.Strategist(s["order"])
            org.develop([(k, seed(20, n)) for n, k in enumerate(s["history"])])
            index["useful" if org.front == org.useful else "plain" if org.front == 0 else "decoy"] += 1
            oth = g3.Strategist(s["order"])
            oth.develop([(k, seed(22, n)) for n, k in enumerate(s["shallow"])])
            after_irrelevant["useful" if oth.front == oth.useful else "plain" if oth.front == 0 else "decoy"] += 1
            parts = g2.shuffled(g2.PARTS, base, r, 2, s["salt"])
            for t in s["targets"]:
                targets += 1
                in_list += 1 if t in g3.RAW_PAIRS else 0
                covered += 1 if g2.covering_pairs(t, parts[4:8]) else 0
            for t in s["history"] + s["history2"]:
                history_n += 1
                history_in_list += 1 if t in g3.RAW_PAIRS else 0
            base = b + 200
            s = g3.setup(base, r)
            seed = lambda tag, n=0: g2.khash(base, r, tag, n)
            lb = g3.LibraryBuilder(s["order"])
            lb.develop([(k, seed(20, n)) for n, k in enumerate(s["history"])])
            entries = lb.b.library
            pairs = [x + y for x in entries for y in entries if len(x) + len(y) <= g2.MAX_DEPTH]
            lib["entries=%d depth=%s pairs=%d" % (len(entries), sorted(set(len(x) for x in entries)), len(pairs))] += 1
    naive_floor = len([t for t in g2.enumeration(g2.PRIMS) if len(t) <= 3])
    return {"STRATEGIST_index_after_development_of_144": dict(index),
            "STRATEGIST_index_after_irrelevant_history_of_144": dict(after_irrelevant),
            "BUILDER_library_after_development_of_144": dict(lib),
            "targets": targets, "targets_in_the_inherited_pairs_first_list": in_list,
            "targets_covered_by_a_pair_of_history_parts": covered,
            "history_families": history_n, "history_families_in_the_inherited_pairs_first_list": history_in_list,
            "templates_of_depth_3_or_less": naive_floor}


def sec_registered_arithmetic():
    """Arithmetic on the registered receipts of runs 2 and 3. Nothing is re-run."""
    d2 = json.loads((HERE / "RECEIPT_gauntlet2.json").read_text(encoding="ascii"))
    d3 = json.loads((HERE / "RECEIPT_gauntlet3.json").read_text(encoding="ascii"))
    b2 = d2["cells"]["BUILDER"]["replicates"]
    s3 = d3["cells"]["STRATEGIST"]["replicates"]
    b3 = d3["cells"]["BUILDER"]["replicates"]
    n = lambda reps, f: sum(1 for o in reps if f(o))
    names = list(clauses2(b2[0]))
    by_clause = {c: {cell: sum(1 for o in v["replicates"] if clauses2(o)[c]) for cell, v in d2["cells"].items()}
                 for c in names}
    out = {
        "run2_clause_true_of_24_by_cell": by_clause,
        "run2_clauses_never_false_in_any_cell": sorted(c for c in names if min(by_clause[c].values()) == N),
        "run2_clauses_that_fail_in_no_cell": sorted(c for c in names if min(by_clause[c].values()) > g2.FAILS_AT),
        "run2_BUILDER_by_factor": {"factor=%d" % f: tally(b2, rel2, f) for f in (2, 4, 6, 8, 10, 16)},
        "run3_STRATEGIST_by_factor": {"factor=%d" % f: tally(s3, rel3, f) for f in (2, 3, 4, 6, 8)},
        "run2_BUILDER": {
            "sham_cheaper_than_intact": n(b2, lambda o: o["sham_B"] < o["dev_B"]),
            "lesioned_line_scores_12.0_the_default_for_nothing_built": n(b2, lambda o: o["q_C_lesioned_line"] == 12.0),
            "max_developed_cost_B_D_E": max(max(o["dev_B"], o["dev_D"], o["dev_E"]) for o in b2),
            "min_naive_cost_B_D_E": min(min(o["naive_B"], o["naive_D"], o["naive_E"]) for o in b2),
        },
        "run3_STRATEGIST": {
            "lesion_equals_naive": n(s3, lambda o: o["lesion_B"] == o["naive_B"]),
            "sham_equals_intact": n(s3, lambda o: o["sham_B"] == o["dev_B"]),
            "rescue_equals_intact": n(s3, lambda o: o["rescue_B"] == o["dev_B"]),
            "v_donor_equals_intact": n(s3, lambda o: o["v_donor_B"] == o["dev_B"]),
            "irrelevant_history_equals_naive": n(s3, lambda o: o["irrelevant_history_B"] == o["naive_B"]),
            "development_plus_B_cheaper_than_naive_B": n(s3, lambda o: o["development"] + o["dev_B"] < o["naive_B"]),
            "median_development": med(s3, "development"),
        },
        "run3_BUILDER": {
            "PROVENANCE_false_replicates": [
                {"replicate": i, "naive_B": o["naive_B"], "random_V_B": o["random_V_B"]}
                for i, o in enumerate(b3) if not rel3(o, 2)["PROVENANCE"]],
            "lesion_equals_naive": n(b3, lambda o: o["lesion_B"] == o["naive_B"]),
        },
        "run2_failing_conjuncts_by_cell": {k: v["failing"] for k, v in d2["cells"].items()},
        "run3_failing_conjuncts_by_cell": {k: v["failing"] for k, v in d3["cells"].items()},
        "run2_MEMORISER_counts": d2["cells"]["MEMORISER"]["counts"],
        "world_salt_above_zero_in_registered_replicates": {
            "run2": sum(1 for c in d2["cells"].values() for o in c["replicates"] if o["world_salt"]),
            "run3": sum(1 for c in d3["cells"].values() for o in c["replicates"] if o["world_salt"]),
            "replicates": sum(len(c["replicates"]) for d in (d2, d3) for c in d["cells"].values())},
    }
    return out


SECTIONS = [sec_baseline, sec_curriculum, sec_strict_c, sec_k, sec_factor, sec_selection, sec_confirm,
            sec_memoriser, sec_strategist_variants, sec_power, sec_reading1, sec_families, sec_facts,
            sec_registered_arithmetic]


def sha(name):
    return hashlib.sha256((HERE / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main(argv):
    with ProcessPoolExecutor(max_workers=7) as pool:
        futures = [(f.__name__[4:], pool.submit(f)) for f in SECTIONS]
        results = {name: fut.result() for name, fut in futures}
    receipt = {
        "what": "exploratory probes of gauntlet2.py and gauntlet3.py on design seeds; not preregistered; "
                "written after the registered runs and after a reviewer's probes",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": sys.version.split()[0],
        "design_bases_gauntlet2": list(G2_BASES), "design_bases_gauntlet3": list(G3_BASES),
        "registered_seed_bases_never_used": [g2.REGISTERED_BASE, g3.REGISTERED_BASE],
        "source_sha256_lf": sha("probes_exploratory.py"),
        "gauntlet2_sha256_lf": sha("gauntlet2.py"), "gauntlet3_sha256_lf": sha("gauntlet3.py"),
        "probes": results,
    }
    (HERE / "RECEIPT_probes_exploratory.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                                                          encoding="ascii", newline="\n")
    for name, res in results.items():
        print(name, json.dumps(res, sort_keys=True)[:400])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
