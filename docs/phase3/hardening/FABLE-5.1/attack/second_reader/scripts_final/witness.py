"""For each first-sight change the tests did not notice: one input whose verdict differs between the original
gate and the changed gate (run as: python -B witness.py <ID>, with cwd = a copy of the harness, changed or not)."""
import sys

sys.dont_write_bytecode = True
from rso_harness import audits, claims, meta, registration, retain1 as R, rulers, search, stats, torture  # noqa: E402
from rso_harness.verdict import BLOCKED, FAIL, PASS, Result  # noqa: E402

which = sys.argv[1]
P = meta.PAIRS


def out(x):
    print(which, "->", x if isinstance(x, str) else x.verdict)


if which == "S03":
    # brute force: does any input change the verdict of preflight?
    seen = set()
    for n in (8, 16, 18, 20, 24, 30, 40, 64, 81, 96, 128, 200, 256):
        for p0 in (0.02, 0.1, 0.25, 0.5, 0.75, 0.9):
            for alpha in (1e-9, 1e-6, 1e-3, 5e-3, 9.9e-3):
                for pp in (0.3, 0.6, 0.8, 0.9, 0.9375, 0.99, 1.0):
                    seen.add((n, p0, alpha, pp, stats.preflight(n, p0, alpha, pp).verdict))
    import hashlib
    print(which, "->", len(seen), "inputs; digest of all verdicts", hashlib.sha256(repr(sorted(seen)).encode()).hexdigest()[:16])
elif which == "G04":
    out(registration.check_cell(meta.cell(registered_seeds=[])))
elif which == "U03":
    # an 'impostor' whose interchange counts fall between the two registered answers (32 seeds, 64 pairs)
    seeds = list(range(2000, 2032))
    found = None
    for k in range(0, 200):
        if rulers.interchange_ruler(R.scripted(k), seeds) in ("UNDECIDED",):
            found = k
            break
    if found is None:
        # the changed ruler never says UNDECIDED: use the k found on the original (passed in argv[2])
        found = int(sys.argv[2]) if len(sys.argv) > 2 else None
    panel = dict(R.PANEL, REGISTER=(R.Register, R.scripted(found)))
    print(which, "-> scripted k =", found, "| interchange says", rulers.interchange_ruler(R.scripted(found), seeds),
          "| G5 with it as the REGISTER impostor:", rulers.neutrality_gate("INTERCHANGE", rulers.interchange_ruler,
                                                                            ["REGISTER"], panel, seeds).verdict)
elif which == "T01":
    class LateWriter(R.Register):
        """Writes on the environment at the probe step what it saw in the episode before (a hidden carry)."""
        def __init__(self):
            self.w, self.carry = None, 0
        def reset(self):
            self.w = None
        def step(self, obs):
            if obs.kind == "CUE":
                self.w = obs.value
            if obs.kind == "PROBE":
                old, self.carry = self.carry, (self.w or 0)
                return ("WRITE", old)
    out(torture.reset_closure(LateWriter, P, writable_mark=True))
elif which == "T02":
    class Echo(R.Register):
        """Keeps the last two values it was shown; capture leaves them out."""
        def __init__(self):
            self.w, self.last, self.prev = None, 0, 0
        def reset(self):
            self.w, self.last, self.prev = None, 0, 0
        def step(self, obs):
            if obs.kind == "CUE":
                self.w = obs.value
            if obs.kind in ("CUE", "DISTRACT"):
                self.prev, self.last = self.last, (obs.value or 0)
            if obs.kind == "PROBE":
                self.last = self.prev = 0
                return self.w or 0
        def capture(self):
            return (self.w,)
        def restore(self, state):
            self.w, self.last, self.prev = state[0], 0, 0
        def native(self):
            return (self.w, self.last, self.prev)
    out(torture.restart_equivalence(Echo, P))
elif which == "T03":
    class LatticeEarlyBadCapture(R.Lattice):
        """Capture drops the step counter right after the first step only."""
        def capture(self):
            return (tuple(self.cells), self.t if self.t != 1 else 0)
    out(torture.restart_equivalence(LatticeEarlyBadCapture, P))
elif which == "T04":
    def from_the_seventh(log):
        def observe(world, seed, t, org):
            if world.episodes >= 6:
                world.draw(seed)
        return observe
    out(meta.all_positives(lambda m: torture.observer_equivalence(m, P, from_the_seventh)))
elif which == "R01":
    r = meta.report()
    r["policies"]["NEUTRAL"]["seeds"] = list(reversed(meta.REPORTED)) + [meta.REPORTED[0]]
    out(meta.checked(r))
elif which == "R02":
    r = meta.report()
    r["policies"]["NEUTRAL"]["hits"] -= 5
    out(meta.checked(r))
elif which == "R06":
    out(meta.checked(meta.null("VALLEY", ("NEUTRAL",))))
elif which == "A01":
    out(audits.audit_arms([{"a": 7, "b": 7} for _ in range(12)], ("a", "b")))
elif which == "A02":
    out(audits.audit_arms([{"a": i, "b": i, "c": 100 + i} for i in range(24)], ("a", "b", "c")))
elif which == "A10":
    elim = [r for r in audits.RUNS if r[0] == "KEY_ELIMINATOR"][0]
    out(audits.ruler_status("BITS", "BITS@KEYS", meta.COUNTERFEIT,
                            audits.RUNS + [("KEY_ELIMINATOR", "BITS@ANOTHER_SETTING", elim[2], elim[3])]))
elif which == "C01":
    out(claims.check_custody(meta.custody(confirmation_opened_at=20.5)))
elif which == "C03":
    c = meta.claim()
    out(claims.render(dict(c, setting=dict(reversed(list(c["setting"].items()))))))
elif which == "C04":
    out(claims.check_custody(meta.custody(discovery_custodian="")))
elif which == "W02":
    def marks_at_the_end(log):
        def observe(world, seed, t, org):
            if t == world.gap + 1:
                world.mark = 1
        return observe
    out(meta.all_positives(lambda m: torture.observer_equivalence(m, P, marks_at_the_end)))
elif which == "M02":
    rows = meta.qualify({"X": ("refuses a sound case", [lambda: Result("X", BLOCKED, "refused")],
                               [("m", lambda: Result("X", FAIL), FAIL)])})
    out("GM status %s, false alarms %s" % (rows["X"]["status"], rows["X"]["false_alarms"]))
elif which == "M03":
    def forgets_the_adapter(c):
        return registration.check_cell(dict(c, adapter=c.get("adapter") or "anything"))
    out(meta.every_missing_field_blocks(forgets_the_adapter, meta.cell, meta.CELL_FIELDS))
elif which == "M04":
    claims.KIND["ORIGIN"] = ("cold_start",)          # a gate that forgot the class bound of an ORIGIN claim
    out(meta.every_kind_facet_blocks())
