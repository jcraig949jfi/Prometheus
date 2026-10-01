"""Third reading: the strict protocol when the history shares NO component with the target.

gauntlet2.py showed a plain library learner passing section 19 with B a kind never met. A second
reviewer then gave the reply the criterion's authors would give: section 18 speaks of "genuinely new
causal families"; read step 3 as "family B shares no built component with history A" and the library
learner fails, on the wrong-history arm of that very run. So perhaps section 19 needs one clarifying
sentence and no more. The same reviewer, in an unregistered probe, found an organism with one
developed bit that passes under that reading.

This file tests that reading under the strict protocol of gauntlet2.py (same world, same task and
acceptance code, imported unchanged).

Development: ONE composite family A (depth 4) built from four HISTORY parts, as step 1 says
("Develop on family A"). Targets B, D, E: composite kinds built from four OTHER parts. No pair of
history parts covers a target's function class. So nothing the organism built in development is a
component of a target. What history and targets share is the shape of the construction problem:
both are pairs of parts. The second individual (rescue, V donor) develops on a different composite
family of the history parts. The irrelevant history is one shallow family (a single part).

Organisms (all designed):
  BUILDER      the library learner of gauntlet2.py, unchanged. Its library can only reorder
               candidates that contain what it built. Expected: FAIL (no savings).
  STRATEGIST   no library at all. It inherits 32 complete orders in which to enumerate the same 660
               templates: the plain order (in use at birth), one order that tries the 81 pairs of
               parts first, and 30 decoys that try them last. What develops is one index, 5 bits:
               after each success it switches to the inherited order that would have reached that
               success soonest. Expected: PASS.
and two fire tests:
  STATIC       STRATEGIST that never switches                                  (SAVINGS)
  EAGER        STRATEGIST that switches to the pairs-first order after any experience
                                                                               (PROVENANCE)

Relations are those of gauntlet2.py with one change, fixed before the registered run: the savings
factor is 2, not 4. A selector's saving is bounded by the length of its inherited list (81 pairs
against 660 templates) and it must also pass 8 confirmation tasks. On design seeds a factor of 4
held in 22 or 23 of 24 replicates, at the edge of the quorum of 22. Section 19 names no factor.

    python gauntlet3.py --design     design seeds; prints; writes nothing
    python gauntlet3.py              registered seeds; writes RECEIPT_gauntlet3.json
"""
import hashlib
import json
import pathlib
import platform
import statistics
import sys
from datetime import datetime, timezone

import gauntlet2 as g2

HERE = pathlib.Path(__file__).resolve().parent
N_REP = 24
HOLDS_AT = 22
FAILS_AT = 12
K = 32                      # inherited search orders
FACTOR = 2                  # savings factor in the relations
DESIGN_BASE = 43
REGISTERED_BASE = 2026100124
RAW_PAIRS = set(a + b for a in g2.PARTS for b in g2.PARTS)     # the 81 pairs of the nine distinct parts

khash, shuffled, klass = g2.khash, g2.shuffled, g2.klass


class Strategist:
    """Thirty-two inherited search orders and one developed index."""

    def __init__(self, order, switch=True, eager=False):
        plain = g2.enumeration(order)
        pairs = [t for t in plain if t in RAW_PAIRS]
        rest = [t for t in plain if t not in RAW_PAIRS]
        key = [g2.PRIMS.index(p) for p in order]
        self.useful = 1 + khash(91, *key) % (K - 1)
        self.orders = [plain]
        for i in range(1, K):
            self.orders.append(pairs + rest if i == self.useful else rest + shuffled(pairs, 92, i, *key))
        self.rank = [{t: n for n, t in enumerate(o)} for o in self.orders]
        self.front = 0              # V, declared: the order in use
        self.switch = switch
        self.eager = eager

    def clone(self):
        c = Strategist.__new__(Strategist)
        c.__dict__.update(self.__dict__)
        return c

    def construct(self, kind, seed, limit=None):
        cost = 0
        for j, tmpl in enumerate(self.orders[self.front]):
            if limit is not None and cost >= limit:
                return None, cost
            ok, used = g2.passes(tmpl, kind, seed, j)
            cost += used
            if ok:
                if self.switch:
                    c = klass(tmpl)
                    covers = [t for t in self.orders[0] if c <= klass(t)]
                    best = min(range(K), key=lambda s: (min(self.rank[s][t] for t in covers), s != self.front, s))
                    if min(self.rank[best][t] for t in covers) < min(self.rank[self.front][t] for t in covers):
                        self.front = best
                return tmpl, cost
        return None, cost + 1

    def develop(self, history):
        cost = sum(self.construct(k, s)[1] for k, s in history)
        if self.eager and history:
            self.front = self.useful
        return cost

    def lesion(self):
        self.front = 0

    def sham(self):                 # a change of the same size that should not matter: reorder two decoys
        idle = [i for i in range(1, K) if i not in (self.front, self.useful)][:2]
        a, b = idle
        self.orders[a], self.orders[b] = self.orders[b], self.orders[a]
        self.rank[a], self.rank[b] = self.rank[b], self.rank[a]
        self.orders, self.rank = list(self.orders), list(self.rank)

    def get_v(self):
        return self.front

    def set_v(self, v):
        self.front = v

    def randomize_v(self, *key):
        self.front = 1 + khash(93, *key) % (K - 1)


class LibraryBuilder:
    """gauntlet2's BUILDER behind the same interface."""

    def __init__(self, order):
        self.b = g2.Builder(order)
        self.order = order

    def clone(self):
        c = LibraryBuilder.__new__(LibraryBuilder)
        c.order = self.order
        c.b = self.b.clone()
        return c

    def construct(self, kind, seed, limit=None):
        return self.b.construct(kind, seed, limit=limit)

    def develop(self, history):
        return self.b.develop(history)

    def lesion(self):
        self.b.library = []

    def sham(self):
        pass

    def get_v(self):
        return list(self.b.library)

    def set_v(self, v):
        self.b.library = list(v)

    def randomize_v(self, *key):
        self.b.library = [t for t in shuffled(g2.DEPTH2, 94, *key) if t not in g2.PARTS][:3]


def setup(base, r):
    """Four history parts, four other parts for the targets, and nothing built in common."""
    order = shuffled(g2.PRIMS, base, r, 1)
    for salt in range(400):
        parts = shuffled(g2.PARTS, base, r, 2, salt)
        tparts, hparts = parts[:4], parts[4:8]
        targets = []
        for a, b in shuffled([(a, b) for a in tparts for b in tparts if a != b], base, r, 3, salt):
            t = a + b
            if g2.good_target(t, targets) and not g2.covering_pairs(t, hparts):
                targets.append(t)
            if len(targets) == 3:
                break
        if len(targets) < 3:
            continue
        history = []
        for a, b in shuffled([(a, b) for a in hparts for b in hparts if a != b], base, r, 4, salt):
            t = a + b
            if g2.good_target(t, targets + history):
                history.append(t)
            if len(history) == 2:
                break
        if len(history) < 2:
            continue
        return {"order": order, "targets": targets, "history": history[:1], "history2": history[1:],
                "shallow": hparts[:1], "salt": salt}
    raise RuntimeError("no world found for replicate %d" % r)


def replicate(make, base, r):
    s = setup(base, r)
    order = s["order"]
    kb, kd, ke = s["targets"]
    seed = lambda tag, n=0: khash(base, r, tag, n)
    fam = {k: seed(10, n) for n, k in enumerate((kb, kd, ke))}
    history = [(k, seed(20, n)) for n, k in enumerate(s["history"])]
    history2 = [(k, seed(21, n)) for n, k in enumerate(s["history2"])]
    shallow = [(k, seed(22, n)) for n, k in enumerate(s["shallow"])]
    out = {}

    for name, k in (("B", kb), ("D", kd), ("E", ke)):
        out["naive_" + name] = make(order).construct(k, fam[k])[1]

    org = make(order)
    out["development"] = org.develop(history)
    post_a = org.clone()
    u_b, out["dev_B"] = org.construct(kb, fam[kb])
    out["q_C_same_kind"] = g2.quality(u_b, kb, seed(30))
    out["q_C_narrower"] = g2.quality(u_b, kb, seed(31), pin=seed(32))
    for name, k in (("D", kd), ("E", ke)):
        out["dev_" + name] = post_a.clone().construct(k, fam[k])[1]

    les = post_a.clone()
    les.lesion()
    out["lesion_B"] = les.construct(kb, fam[kb])[1]
    les2 = post_a.clone()
    les2.lesion()
    out["q_C_lesioned_line"] = g2.quality(les2.construct(kb, fam[kb], limit=out["dev_B"])[0], kb, seed(30))

    sham = post_a.clone()
    sham.sham()
    out["sham_B"] = sham.construct(kb, fam[kb])[1]

    donor = make(order)                                 # a second individual with its own families
    donor.develop(history2)
    resc = post_a.clone()
    resc.lesion()
    resc.set_v(donor.get_v())
    out["rescue_B"] = resc.construct(kb, fam[kb])[1]
    recipient = make(order)
    recipient.set_v(donor.get_v())
    out["v_donor_B"] = recipient.construct(kb, fam[kb])[1]

    other = make(order)                                 # history that shares neither component nor shape
    other.develop(shallow)
    out["irrelevant_history_B"] = other.construct(kb, fam[kb])[1]
    rnd = make(order)
    rnd.randomize_v(base, r)
    out["random_V_B"] = rnd.construct(kb, fam[kb])[1]

    out["lifecycle_developed"] = out["development"] + out["dev_B"] + out["dev_D"] + out["dev_E"]
    out["lifecycle_naive"] = out["naive_B"] + out["naive_D"] + out["naive_E"]
    out["world_salt"] = s["salt"]
    return out


CONJUNCTS = ("SAVINGS", "LIFECYCLE", "U_TRANSFER", "NESTING", "PROVENANCE", "REPEAT")


def relations(o):
    slack = 2 * o["dev_B"] + 4
    return {
        "SAVINGS": FACTOR * o["dev_B"] <= o["naive_B"],
        "LIFECYCLE": o["lifecycle_developed"] < o["lifecycle_naive"],
        "U_TRANSFER": (o["q_C_same_kind"] <= g2.GOOD_MAX and o["q_C_narrower"] <= g2.GOOD_MAX
                       and o["q_C_lesioned_line"] >= g2.BAD_MIN),
        "NESTING": (2 * o["lesion_B"] >= o["naive_B"] and o["sham_B"] <= slack and o["rescue_B"] <= slack
                    and FACTOR * o["v_donor_B"] <= o["naive_B"]),
        "PROVENANCE": 2 * o["irrelevant_history_B"] >= o["naive_B"] and 2 * o["random_V_B"] >= o["naive_B"],
        "REPEAT": FACTOR * o["dev_D"] <= o["naive_D"] and FACTOR * o["dev_E"] <= o["naive_E"],
    }


def run_cell(make, base):
    reps = [replicate(make, base, r) for r in range(N_REP)]
    rels = [relations(o) for o in reps]
    counts = {c: sum(1 for x in rels if x[c]) for c in CONJUNCTS}
    states = {c: "HOLDS" if counts[c] >= HOLDS_AT else "FAILS" if counts[c] <= FAILS_AT else "INDETERMINATE"
              for c in CONJUNCTS}
    if all(v == "HOLDS" for v in states.values()):
        verdict = "PASS"
    elif any(v == "FAILS" for v in states.values()):
        verdict = "FAIL"
    else:
        verdict = "INDETERMINATE"
    return {"verdict": verdict, "conjuncts": states, "counts": counts,
            "medians": {k: statistics.median(o[k] for o in reps) for k in reps[0]},
            "failing": sorted(c for c in CONJUNCTS if states[c] == "FAILS"), "replicates": reps}


CELLS = [
    ("STRATEGIST", lambda o: Strategist(o), "PASS", []),
    ("BUILDER", lambda o: LibraryBuilder(o), "FAIL", ["SAVINGS"]),
    ("STATIC", lambda o: Strategist(o, switch=False), "FAIL", ["SAVINGS"]),
    ("EAGER", lambda o: Strategist(o, switch=False, eager=True), "FAIL", ["PROVENANCE"]),
]


def main(argv):
    design = "--design" in argv
    base = DESIGN_BASE if design else REGISTERED_BASE
    out, ok = {}, True
    for n, (name, make, want, must_fail) in enumerate(CELLS):
        cell = run_cell(make, base + 100 * (n + 1))
        m = cell["medians"]
        hit = cell["verdict"] == want and all(c in cell["failing"] for c in must_fail)
        ok = ok and hit
        out[name] = cell
        print("%-11s %-13s %s" % (name, cell["verdict"], "as expected" if hit else "NOT AS EXPECTED (wanted %s %s)" % (want, must_fail)))
        print("    " + "  ".join("%s %s %d" % (c, cell["conjuncts"][c], cell["counts"][c]) for c in CONJUNCTS))
        print("    median tasks: naive B %s, developed B %s, lesion %s, sham %s, rescue %s, V donor %s, "
              "irrelevant history %s, random V %s" % (m["naive_B"], m["dev_B"], m["lesion_B"], m["sham_B"],
                                                    m["rescue_B"], m["v_donor_B"], m["irrelevant_history_B"],
                                                    m["random_V_B"]))
        print("    median tasks: development %s; lifecycle developed %s against naive %s; D %s against %s; E %s against %s"
              % (m["development"], m["lifecycle_developed"], m["lifecycle_naive"], m["dev_D"], m["naive_D"],
                 m["dev_E"], m["naive_E"]))
        print("    median errors per task of frozen U: same kind %.2f, narrower %.2f, lesioned line %.2f"
              % (m["q_C_same_kind"], m["q_C_narrower"], m["q_C_lesioned_line"]))
    print("MATCHES PREREGISTERED EXPECTATION: %s" % ok)
    if design:
        return 0
    receipt = {
        "what": "third reading of 'fresh': strict section-19 protocol with a history that shares no component with the target",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": sys.version.split()[0],
        "params": {"N_REP": N_REP, "HOLDS_AT": HOLDS_AT, "FAILS_AT": FAILS_AT, "K": K, "FACTOR": FACTOR,
                   "seed_base": REGISTERED_BASE, "developed_state_bits_of_strategist": 5,
                   "pairs_of_raw_parts": len(RAW_PAIRS), "candidate_templates": len(g2.enumeration(g2.PRIMS))},
        "source_sha256_lf": hashlib.sha256(pathlib.Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "gauntlet2_sha256_lf": hashlib.sha256((HERE / "gauntlet2.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "expected": {name: {"verdict": want, "must_fail": must_fail} for name, _, want, must_fail in CELLS},
        "matches_expectation": ok, "gate": "PASS" if ok else "FAILED", "cells": out,
    }
    (HERE / "RECEIPT_gauntlet3.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                                                encoding="ascii", newline="\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
