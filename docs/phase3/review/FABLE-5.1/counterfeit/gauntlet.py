"""Counterfeit gauntlet for the recursive-sagacity criterion of RSO v0.1 (section 19).

Question. The criterion asks for three things: functional savings, V -> U -> S
causal nesting, and developmental provenance, tested by a 13-step protocol
(develop on A; reset task content; let V_A construct fresh U_B on B; freeze;
test on fresh C; lesion, sham, rescue, donors, irrelevant history; repeat).
Can something that is plainly NOT recursive pass it?

Four designed organisms, all a few dozen lines, all deterministic:

  STATIC         a fixed list of three inherited learning procedures; nothing
                 develops. Must FAIL (fire test for the savings check).
  MATURATION     the same, but after ANY experience its list is rewritten to a
                 fixed inherited order. Must FAIL (fire test for the
                 irrelevant-history control).
  GEARBOX        the counterfeit: the same three inherited procedures and a
                 move-to-front list. Experience only reorders the list.
  BUILDER        a library builder: no inherited procedures, six primitive
                 operations, a fixed constructor that tries its own library,
                 then compositions of library items, then primitives.

Preregistered expectation (PREREG.md): GEARBOX and BUILDER both pass the v0.1
protocol. Three added checks then separate them: gain on a family whose
efficient procedure is not inherited; knockout of the inherited part; count of
distinct procedures against what was inherited.

Everything is exact integer arithmetic. The world is prediction of a hidden
function on Z_17 with feedback; cost is the number of errors in a 12-trial
task.

    python gauntlet.py --design     # design seeds; prints rates; writes nothing
    python gauntlet.py              # registered seeds; writes RECEIPT_gauntlet.json
"""
import hashlib
import itertools
import json
import pathlib
import platform
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
P = 17                     # modulus
T = 12                     # trials per task
TAU = 4                    # a procedure is accepted on a task if errors <= TAU
N_REP = 24                 # independent replicates per arm
N_TEST = 50                # test tasks per replicate
GOOD_MAX = 3.5             # replicate is GOOD if mean errors per task <= this
BAD_MIN = 6.0              # replicate is BAD if mean errors per task >= this
REP_QUORUM = 22            # an arm is GOOD (or BAD) if at least this many of N_REP replicates are
DESIGN_BASE = 11
REGISTERED_BASE = 2026100121

TYPE = {"SHIFT": 1, "SCALE": 2, "TABLE": 3, "AFFINE": 4, "SQR": 5, "CUB": 6}
PRIMS = ("ADD", "MUL", "NEG", "SQR", "INV", "CUB")
FREE = {"ADD": range(0, P), "MUL": range(1, P)}


def khash(*ints):
    h = hashlib.blake2b(digest_size=8)
    for v in ints:
        h.update(int(v).to_bytes(8, "little"))
    return int.from_bytes(h.digest(), "little")


# ---------------------------------------------------------------- world

def task_fn(ftype, fseed, i):
    """The hidden function of task i of a family, as a list f[0..16]."""
    code = TYPE[ftype]
    if ftype == "SHIFT":
        c = 1 + khash(fseed, i, code, 1) % 16
        return [(x + c) % P for x in range(P)]
    if ftype == "SCALE":
        a = 2 + khash(fseed, i, code, 1) % 15
        return [(a * x) % P for x in range(P)]
    if ftype == "AFFINE":
        a = 2 + khash(fseed, i, code, 1) % 15
        c = 1 + khash(fseed, i, code, 2) % 16
        return [(a * x + c) % P for x in range(P)]
    if ftype == "TABLE":
        return [khash(fseed, i, code, 3, x) % P for x in range(P)]
    if ftype == "SQR":
        return [(x * x) % P for x in range(P)]
    if ftype == "CUB":
        return [(x * x * x) % P for x in range(P)]
    raise ValueError(ftype)


def stimuli(fseed, i):
    return [1 + khash(fseed, i, 7, t) % 16 for t in range(T)]


# ---------------------------------------------------------------- learners (the U level)

def apply_template(template, consts, x):
    k = 0
    for prim in template:
        if prim == "ADD":
            x = (x + consts[k]) % P
            k += 1
        elif prim == "MUL":
            x = (x * consts[k]) % P
            k += 1
        elif prim == "NEG":
            x = (-x) % P
        elif prim == "SQR":
            x = (x * x) % P
        elif prim == "INV":
            x = pow(x, P - 2, P)
        elif prim == "CUB":
            x = (x * x * x) % P
    return x


class TemplateLearner:
    """Fits the free constants of a template to this task's examples, exactly."""

    def __init__(self, template):
        self.template = tuple(template)
        self.ranges = [FREE[p] for p in self.template if p in FREE]
        self.examples = {}
        self.consts = None

    def _fit(self):
        if self.consts is not None and all(apply_template(self.template, self.consts, x) == y
                                           for x, y in self.examples.items()):
            return self.consts
        for consts in itertools.product(*self.ranges):
            if all(apply_template(self.template, consts, x) == y for x, y in self.examples.items()):
                self.consts = consts
                return consts
        self.consts = None
        return None

    def predict(self, x):
        consts = self._fit()
        return 0 if consts is None else apply_template(self.template, consts, x)

    def learn(self, x, y):
        self.examples[x] = y


class TableLearner:
    def __init__(self):
        self.memory = {}

    def predict(self, x):
        return self.memory.get(x, 0)

    def learn(self, x, y):
        self.memory[x] = y


def make_learner(spec):
    return TableLearner() if spec == "TABLE" else TemplateLearner(spec)


def run_task(spec, ftype, fseed, i):
    """Errors made by a fresh learner of this procedure on one task. S (the task state) starts empty."""
    f = task_fn(ftype, fseed, i)
    learner = make_learner(spec)
    errors = 0
    for x in stimuli(fseed, i):
        if learner.predict(x) != f[x]:
            errors += 1
        learner.learn(x, f[x])
    return errors


# ---------------------------------------------------------------- organisms (the V level)

class Gearbox:
    """Three inherited procedures and a move-to-front list. The list is the only thing that develops."""

    kind = "GEARBOX"
    tight_budget = 1

    def __init__(self, library=("TABLE", ("ADD",), ("MUL",)), move_to_front=True, maturation=False):
        self.library = list(library)                 # inherited; never written
        self.order = list(range(len(self.library)))  # V state; written by experience
        self.scratch = 0                             # unused cell, for the sham lesion
        self.move_to_front = move_to_front
        self.maturation = maturation
        self.v_writes = 0
        self.v_reads = 0
        self.accepted = set()

    def v_state(self):
        return list(self.order)

    def set_v_state(self, state):
        self.order = list(state)

    def lesion_v(self):
        self.order = list(range(len(self.library)))

    def sham_lesion(self):
        self.scratch = 0

    def construct(self, ftype, fseed, budget):
        """Build U for a new family from at most `budget` tasks. Returns the procedure chosen."""
        self.v_reads += 1
        tried = list(self.order)
        for j, idx in enumerate(tried[:budget]):
            spec = self.library[idx]
            if run_task(spec, ftype, fseed, j) <= TAU:
                self.accepted.add(str(spec))
                if self.move_to_front and self.order[0] != idx:
                    self.order.remove(idx)
                    self.order.insert(0, idx)
                    self.v_writes += 1
                return spec
        return self.library[self.order[0]]

    def develop(self, history, budget):
        for ftype, fseed in history:
            self.construct(ftype, fseed, budget)
        if self.maturation and history:
            want = [i for i, s in enumerate(self.library) if s == ("ADD",)] + \
                   [i for i, s in enumerate(self.library) if s == ("MUL",)] + \
                   [i for i, s in enumerate(self.library) if s == "TABLE"]
            if want != self.order:
                self.order = want
                self.v_writes += 1


class Builder:
    """No inherited procedures. A fixed constructor and a library that experience fills."""

    kind = "BUILDER"
    tight_budget = 4

    def __init__(self, compose=True):
        self.compose = compose      # inherited construction operator; never written
        self.library = []           # V state; written by experience; most recent first
        self.scratch = 0
        self.v_writes = 0
        self.v_reads = 0
        self.accepted = set()

    def v_state(self):
        return [tuple(t) for t in self.library]

    def set_v_state(self, state):
        self.library = [tuple(t) for t in state]

    def lesion_v(self):
        self.library = []

    def sham_lesion(self):
        self.scratch = 0

    def candidates(self):
        cands = list(self.library)
        if self.compose:
            for a in self.library:
                for b in self.library:
                    if len(a) + len(b) <= 2:
                        cands.append(a + b)
        cands += [(p,) for p in PRIMS]
        cands += [(p, q) for p in PRIMS for q in PRIMS]
        seen, out = set(), []
        for c in cands:
            if c not in seen:
                seen.add(c)
                out.append(c)
        return out

    def construct(self, ftype, fseed, budget):
        self.v_reads += 1
        cands = self.candidates()
        for j, tmpl in enumerate(cands[:budget]):
            if run_task(tmpl, ftype, fseed, j) <= TAU:
                self.accepted.add(str(tmpl))
                if not self.library or self.library[0] != tmpl:
                    if tmpl in self.library:
                        self.library.remove(tmpl)
                    self.library.insert(0, tmpl)
                    self.v_writes += 1
                return tmpl
        return cands[0]

    def develop(self, history, budget):
        for ftype, fseed in history:
            self.construct(ftype, fseed, budget)


# ---------------------------------------------------------------- the v0.1 protocol

def test_u(spec, ftype, fseed):
    """Mean errors per task of a frozen U on a fresh family, as an exact (total, n)."""
    total = sum(run_task(spec, ftype, fseed, 1000 + i) for i in range(N_TEST))
    return total


def classify(totals):
    good = sum(1 for t in totals if t <= GOOD_MAX * N_TEST)
    bad = sum(1 for t in totals if t >= BAD_MIN * N_TEST)
    if good >= REP_QUORUM:
        label = "GOOD"
    elif bad >= REP_QUORUM:
        label = "BAD"
    else:
        label = "INDETERMINATE"
    return {"label": label, "good_replicates": good, "bad_replicates": bad, "replicates": len(totals),
            "errors_total": sum(totals), "tasks_total": len(totals) * N_TEST}


def protocol(make, history_types, irrelevant_types, target, base, dev_budget):
    """Run the 13-step protocol of RSO v0.1 section 19 on one kind of organism. Step 13 (another substrate) is not run."""
    arms = {k: [] for k in ("naive", "intact", "lesion_V", "sham_lesion", "rescue", "V_donor",
                            "U_donor_into_lesioned", "lesioned_U_with_intact_V", "irrelevant_history",
                            "repeat_D_intact", "repeat_D_lesion", "repeat_E_intact", "repeat_E_lesion")}
    writes = reads = 0
    for r in range(N_REP):
        s = lambda tag, k=0: khash(base, r, tag, k)
        hist = [(ft, s(1, n)) for n, ft in enumerate(history_types)]
        irr = [(ft, s(2, n)) for n, ft in enumerate(irrelevant_types)]
        fam_b, fam_c, fam_d, fam_e = s(3), s(4), s(5), s(6)

        naive = make()
        u = naive.construct(target, fam_b, naive.tight_budget)
        arms["naive"].append(test_u(u, target, fam_c))

        org = make()                                   # steps 1 to 6
        org.develop(hist, dev_budget)
        writes += org.v_writes
        v_a = org.v_state()
        u_b = org.construct(target, fam_b, org.tight_budget)
        reads += org.v_reads
        arms["intact"].append(test_u(u_b, target, fam_c))

        les = make()                                   # step 7
        les.develop(hist, dev_budget)
        les.lesion_v()
        u_les = les.construct(target, fam_b, les.tight_budget)
        arms["lesion_V"].append(test_u(u_les, target, fam_c))

        sham = make()                                  # step 8
        sham.develop(hist, dev_budget)
        sham.sham_lesion()
        arms["sham_lesion"].append(test_u(sham.construct(target, fam_b, sham.tight_budget), target, fam_c))

        resc = make()                                  # step 9
        resc.develop(hist, dev_budget)
        resc.lesion_v()
        resc.set_v_state(v_a)
        arms["rescue"].append(test_u(resc.construct(target, fam_b, resc.tight_budget), target, fam_c))

        recip = make()                                 # step 10: V donor into a naive recipient
        recip.set_v_state(v_a)
        arms["V_donor"].append(test_u(recip.construct(target, fam_b, recip.tight_budget), target, fam_c))
        # U donors. Once U is frozen, V plays no part in the test, so these two arms repeat the intact and
        # lesioned lines on a second fresh family. They show that U is the proximate carrier.
        arms["U_donor_into_lesioned"].append(test_u(u_b, target, khash(fam_c, 5)))        # frozen U from the intact line
        arms["lesioned_U_with_intact_V"].append(test_u(u_les, target, khash(fam_c, 5)))   # frozen U from the lesioned line

        other = make()                                 # step 11
        other.develop(irr, dev_budget)
        arms["irrelevant_history"].append(test_u(other.construct(target, fam_b, other.tight_budget), target, fam_c))

        for name, fam in (("D", fam_d), ("E", fam_e)):  # step 12
            o1 = make()
            o1.develop(hist, dev_budget)
            arms["repeat_%s_intact" % name].append(test_u(o1.construct(target, fam, o1.tight_budget), target, khash(fam, 99)))
            o2 = make()
            o2.develop(hist, dev_budget)
            o2.lesion_v()
            arms["repeat_%s_lesion" % name].append(test_u(o2.construct(target, fam, o2.tight_budget), target, khash(fam, 99)))
    out = {k: classify(v) for k, v in arms.items()}
    out["_v_writes_during_development"] = writes
    out["_v_reads_during_construction"] = reads
    return out


V01_EXPECT = {"naive": "BAD", "intact": "GOOD", "lesion_V": "BAD", "sham_lesion": "GOOD", "rescue": "GOOD",
              "V_donor": "GOOD", "U_donor_into_lesioned": "GOOD", "lesioned_U_with_intact_V": "BAD",
              "irrelevant_history": "BAD", "repeat_D_intact": "GOOD", "repeat_D_lesion": "BAD",
              "repeat_E_intact": "GOOD", "repeat_E_lesion": "BAD"}


def v01_verdict(res):
    """The combined criterion of RSO v0.1: savings, nesting, provenance. PASS, FAIL or INDETERMINATE."""
    labels = {k: res[k]["label"] for k in V01_EXPECT}
    if any(v == "INDETERMINATE" for v in labels.values()):
        return "INDETERMINATE", labels
    savings = labels["naive"] == "BAD" and labels["intact"] == "GOOD"
    nesting = all(labels[k] == V01_EXPECT[k] for k in ("lesion_V", "sham_lesion", "rescue", "V_donor",
                                                      "U_donor_into_lesioned", "lesioned_U_with_intact_V"))
    provenance = (res["_v_writes_during_development"] > 0 and res["_v_reads_during_construction"] > 0
                  and labels["irrelevant_history"] == "BAD")
    repeat = all(labels[k] == V01_EXPECT[k] for k in ("repeat_D_intact", "repeat_D_lesion",
                                                     "repeat_E_intact", "repeat_E_lesion"))
    ok = savings and nesting and provenance and repeat
    return ("PASS" if ok else "FAIL"), {"savings": savings, "nesting": nesting, "provenance": provenance,
                                        "repeat": repeat, "labels": labels}


# ---------------------------------------------------------------- the three added checks

def gain_arm(make, history_types, target, base, budget, dev_budget):
    """Experienced against naive on one target at one construction budget."""
    exp, nai = [], []
    for r in range(N_REP):
        hist = [(ft, khash(base, r, 11, n)) for n, ft in enumerate(history_types)]
        fam_b, fam_c = khash(base, r, 13), khash(base, r, 14)
        o = make()
        o.develop(hist, dev_budget)
        exp.append(test_u(o.construct(target, fam_b, budget), target, fam_c))
        n = make()
        nai.append(test_u(n.construct(target, fam_b, budget), target, fam_c))
    return {"experienced": classify(exp), "naive": classify(nai)}


def capacity(make, base, dev_budget):
    """How many distinct procedures does a long, varied history ever get accepted?"""
    o = make()
    types = ["SHIFT", "SCALE", "AFFINE", "SQR", "CUB", "SHIFT", "SCALE", "AFFINE", "TABLE"]
    o.develop([(ft, khash(base, 21, n)) for n, ft in enumerate(types)], dev_budget)
    return sorted(o.accepted)


def run(base):
    out = {}
    gear = lambda: Gearbox()
    out["STATIC"] = {"SHIFT": protocol(lambda: Gearbox(move_to_front=False), ["SHIFT"] * 3, ["SCALE"] * 3, "SHIFT", base + 1, 3)}
    out["MATURATION"] = {"SHIFT": protocol(lambda: Gearbox(move_to_front=False, maturation=True), ["SHIFT"] * 3, ["SCALE"] * 3, "SHIFT", base + 2, 3)}
    out["GEARBOX"] = {"SHIFT": protocol(gear, ["SHIFT"] * 3, ["SCALE"] * 3, "SHIFT", base + 3, 3),
                      "SCALE": protocol(gear, ["SCALE"] * 3, ["SHIFT"] * 3, "SCALE", base + 4, 3)}
    out["BUILDER"] = {"AFFINE": protocol(lambda: Builder(), ["SHIFT", "SCALE"], ["SQR", "CUB"], "AFFINE", base + 5, 42)}
    verdicts = {k: {t: v01_verdict(r)[0] for t, r in d.items()} for k, d in out.items()}
    detail = {k: {t: v01_verdict(r)[1] for t, r in d.items()} for k, d in out.items()}

    added = {
        "GEARBOX": {
            "out_of_library_AFFINE_budget_1": gain_arm(gear, ["SHIFT", "SCALE"], "AFFINE", base + 6, 1, 3),
            "out_of_library_AFFINE_budget_3": gain_arm(gear, ["SHIFT", "SCALE"], "AFFINE", base + 7, 3, 3),
            "knockout_of_inherited_ADD_then_SHIFT": gain_arm(lambda: Gearbox(library=("TABLE", ("MUL",))),
                                                             ["SHIFT"] * 3, "SHIFT", base + 8, 1, 3),
            "procedures_ever_accepted": capacity(gear, base + 9, 3),
            "inherited_units": [str(s) for s in ("TABLE", ("ADD",), ("MUL",))],
        },
        "BUILDER": {
            "out_of_library_AFFINE_budget_4": gain_arm(lambda: Builder(), ["SHIFT", "SCALE"], "AFFINE", base + 10, 4, 42),
            "knockout_of_inherited_compose_operator": gain_arm(lambda: Builder(compose=False), ["SHIFT", "SCALE"],
                                                               "AFFINE", base + 11, 4, 42),
            "procedures_ever_accepted": capacity(lambda: Builder(), base + 12, 42),
            "inherited_units": [str((p,)) for p in PRIMS],
        },
    }
    for a in added.values():
        a["accepted_but_not_inherited_as_a_unit"] = [p for p in a["procedures_ever_accepted"]
                                                     if p not in a["inherited_units"]]

    def klass(a, inherited_part_key, gain_key):
        gain = a[gain_key]["experienced"]["label"] == "GOOD" and a[gain_key]["naive"]["label"] == "BAD"
        ko = a[inherited_part_key]
        ko_gain = ko["experienced"]["label"] == "GOOD" and ko["naive"]["label"] == "BAD"
        more = len(a["accepted_but_not_inherited_as_a_unit"]) > 0
        if not gain and not more:
            return "SELECTION_AMONG_INHERITED"
        if gain and more:
            return "CONSTRUCTION_AT_FIXED_DEPTH" if not ko_gain else "CONSTRUCTION_WITHOUT_THE_INHERITED_OPERATOR"
        return "UNCLASSIFIED"

    classes = {
        "GEARBOX": klass(added["GEARBOX"], "knockout_of_inherited_ADD_then_SHIFT", "out_of_library_AFFINE_budget_3"),
        "BUILDER": klass(added["BUILDER"], "knockout_of_inherited_compose_operator", "out_of_library_AFFINE_budget_4"),
    }
    return {"protocol": out, "v01_verdict": verdicts, "v01_detail": detail, "added_checks": added, "class": classes}


EXPECTED = {
    "v01_verdict": {"STATIC": {"SHIFT": "FAIL"}, "MATURATION": {"SHIFT": "FAIL"},
                    "GEARBOX": {"SHIFT": "PASS", "SCALE": "PASS"}, "BUILDER": {"AFFINE": "PASS"}},
    "class": {"GEARBOX": "SELECTION_AMONG_INHERITED", "BUILDER": "CONSTRUCTION_AT_FIXED_DEPTH"},
}


def main(argv):
    design = "--design" in argv
    res = run(DESIGN_BASE if design else REGISTERED_BASE)
    for org, d in res["protocol"].items():
        for target, arms in d.items():
            print("%-10s target %-6s v0.1 verdict %s" % (org, target, res["v01_verdict"][org][target]))
            for k in V01_EXPECT:
                a = arms[k]
                print("    %-26s %-13s good %2d bad %2d of %d   mean errors per task %.2f" % (
                    k, a["label"], a["good_replicates"], a["bad_replicates"], a["replicates"],
                    a["errors_total"] / a["tasks_total"]))
            print("    V writes in development %d, V reads in construction %d" % (
                arms["_v_writes_during_development"], arms["_v_reads_during_construction"]))
    for org, a in res["added_checks"].items():
        print("%s added checks -> class %s" % (org, res["class"][org]))
        for k, v in a.items():
            if isinstance(v, dict):
                print("    %-42s experienced %-13s naive %-13s" % (k, v["experienced"]["label"], v["naive"]["label"]))
            else:
                print("    %-42s %s" % (k, v))
    as_expected = (res["v01_verdict"] == EXPECTED["v01_verdict"] and res["class"] == EXPECTED["class"])
    print("MATCHES PREREGISTERED EXPECTATION: %s" % as_expected)
    if design:
        return 0
    receipt = {
        "what": "counterfeit gauntlet for the recursive-sagacity criterion of RSO v0.1 section 19",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": sys.version.split()[0],
        "params": {"P": P, "T": T, "TAU": TAU, "N_REP": N_REP, "N_TEST": N_TEST, "GOOD_MAX": GOOD_MAX,
                   "BAD_MIN": BAD_MIN, "REP_QUORUM": REP_QUORUM, "seed_base": REGISTERED_BASE},
        "source_sha256_lf": hashlib.sha256(pathlib.Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "expected": EXPECTED, "matches_expectation": as_expected, "gate": "PASS" if as_expected else "FAILED",
        "result": res,
    }
    (HERE / "RECEIPT_gauntlet.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                                                encoding="ascii", newline="\n")
    return 0 if as_expected else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
