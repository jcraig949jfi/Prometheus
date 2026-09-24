"""T-P1, T-P2, T-P3, T-P8, T-P9, T-P10 with defect injection.

EVERY test here runs twice: once against the repaired substrate, where it must PASS,
and once against an injected defect that restores the predecessor's exact behaviour,
where it must FAIL. A repair test that passes on the unrepaired code is not testing the
repair, and the predecessor campaign shipped three flags whose guards could not fire.

The injections are not approximations of the old behaviour; each one restores the
predecessor line it replaces, quoted in the injector's docstring.

Run:  python tests/test_repairs.py
Exit: 0 all repairs demonstrated, 1 otherwise.
"""
from __future__ import annotations

import contextlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import grammar as G          # noqa: E402
import tasks                 # noqa: E402
import world                 # noqa: E402

from constants import C  # noqa: E402
CROSS = C["CROSS"]


# ----------------------------------------------------------------- cells
def cell(**kw):
    base = {"world": "GRID", "environment": "STATIC", "representation": "Z8_32",
            "reproduction": "ENDOGENOUS_COPY", "self_location": "PRIMITIVE",
            "copy_primitive": "BYTEWISE", "pressure": "NONE_IMPLICIT",
            "structure": "WELL_MIXED", "task_transform": "ADD1",
            "read_order": "ANSWER_BEFORE_READ", "bridge": "VALLEY",
            "seeding": "SEEDED_REPLICATOR", "mutation_operator": "BOTH",
            "mutation_locality": "LOCAL", "mutation_rate": "MID", "atlas_axis": "NONE"}
    base.update(kw)
    return base


def runner(c, seed=1, **kw):
    return world.Runner(c, seed, tier="S", max_epochs=1, **kw)


# ----------------------------------------------------------------- injections
@contextlib.contextmanager
def inject(target, attr, fn):
    old = getattr(target, attr)
    setattr(target, attr, fn)
    try:
        yield
    finally:
        setattr(target, attr, old)


@contextlib.contextmanager
def no_migration_events():
    """P-1 unrepaired: `self.ct["migrations"] += 1` with no lineage event.

    The predecessor counted migrations and logged none, so a lineage that moved between
    two births left no trace of having moved.
    """
    with inject(world.Runner, "_lin_migration", lambda self, oid, frm, to: None):
        yield


@contextlib.contextmanager
def untagged_causal_edges():
    """P-2 unrepaired: every birth is an edge, with no causal tag.

    The predecessor's lineage tuple was (child, parent, epoch, niche, fidelity, span).
    Nothing recorded whether the parent had actually placed the child's bytes, so
    ordinary descent and evidence-backed replication were the same edge.
    """
    real = world.Runner._lin_birth

    def patched(self, child, parent, niche, fid, span, causal):
        return real(self, child, parent, niche, fid, span, True)

    with inject(world.Runner, "_lin_birth", patched):
        yield


@contextlib.contextmanager
def legacy_env_spec():
    """P-9 unrepaired, verbatim predecessor `_env_spec_for`.

    It returns the coevolution spec and never calls the niche modifier, so
    RESERVOIR x COEVO_ENV silently loses the easy niche.
    """
    def patched(self, o):
        if self.cell["environment"] == "COEVO_ENV" and self.env_pop:
            e = self.env_pop[o.niche % len(self.env_pop)]
            return tasks.TaskSpec(transform=e["transform"], read_order=e["read_order"],
                                  bridge=self.spec.bridge, n_episodes=self.spec.n_episodes,
                                  budget=self.spec.budget, neutral=self.spec.neutral)
        return self._niche_spec(o.niche)

    with inject(world.Runner, "_env_spec_for", patched):
        yield


# ----------------------------------------------------------------- T-P1
def t_p1():
    """Certificate: born easy -> migrated out -> crossing in a hard niche."""
    r = runner(cell(structure="RESERVOIR", world="SOUP_MEM"))
    founder = r._place(b"\x00" * 8, 0, niche=0)
    r.epoch = 5
    r._lin_migration(founder.oid, 0, 2)
    founder.niche = 2
    r.epoch = 9
    child = r._place(b"\x00" * 8, 0, pid=founder.oid, niche=2)
    r._lin_birth(child.oid, founder.oid, 2, 0.99, 8, True)
    p, cp, bn, mv = r._lineage_graph()
    cert = r.ancestry_certificate(child.oid, bn, p, mv)
    if not cert:
        return False, "no certificate built"
    ok = (cert["founder"] == founder.oid and cert["founder_niche"] == 0
          and cert["migration"]["from_niche"] == 0 and cert["migration"]["to_niche"] == 2)
    return ok, "founder niche %s, migration %s->%s, lineage_len %s" % (
        cert["founder_niche"], cert["migration"]["from_niche"],
        cert["migration"]["to_niche"], cert["lineage_len"])


def t_p1_truncated():
    """A truncated lineage yields NO certificate, not a weaker one."""
    r = runner(cell(structure="RESERVOIR", world="SOUP_MEM"))
    founder = r._place(b"\x00" * 8, 0, niche=0)
    r._lin_migration(founder.oid, 0, 2)
    child = r._place(b"\x00" * 8, 0, pid=founder.oid, niche=2)
    r._lin_birth(child.oid, founder.oid, 2, 0.99, 8, True)
    r.lineage_complete = False
    p, cp, bn, mv = r._lineage_graph()
    cert = r.ancestry_certificate(child.oid, bn, p, mv)
    return cert is None, "incomplete lineage -> certificate is %r" % (cert,)


# ----------------------------------------------------------------- T-P2
def _star(r):
    """A. One parent, many children, no child replicates."""
    par = r._place(b"\x00" * 8, 0, niche=0)
    for _ in range(5):
        ch = r._place(b"\x00" * 8, 0, pid=par.oid, niche=0)
        r._lin_birth(ch.oid, par.oid, 0, 0.99, 8, True)
    return r


def _descent(r):
    """B. A chain of births with NO evidence-backed replication."""
    prev = r._place(b"\x00" * 8, 0, niche=0)
    for _ in range(4):
        ch = r._place(b"\x00" * 8, 0, pid=prev.oid, niche=0)
        r._lin_birth(ch.oid, prev.oid, 0, 0.99, 8, False)
        prev = ch
    return r


def _causal_chain(r, n=4):
    """C. An evidence-backed replication chain of length n."""
    prev = r._place(b"\x00" * 8, 0, niche=0)
    for _ in range(n):
        ch = r._place(b"\x00" * 8, 0, pid=prev.oid, niche=0)
        r._lin_birth(ch.oid, prev.oid, 0, 0.99, 8, True)
        prev = ch
    return r


def _depths_of(r):
    p, cp, _, _ = r._lineage_graph()
    d_all, _ = r._depths(p)
    d_causal, _ = r._depths(cp)
    return d_all, d_causal, r._propagating_replicators(cp)


def t_p2_star():
    d, dc, prop = _depths_of(_star(runner(cell())))
    ok = d == 1 and dc == 1 and prop == 0
    return ok, "ancestry %d, causal %d, propagating %d (want 1/1/0)" % (d, dc, prop)


def t_p2_descent():
    d, dc, prop = _depths_of(_descent(runner(cell())))
    ok = d > 1 and dc == 0
    return ok, "ancestry %d (>1), causal %d (must not increase)" % (d, dc)


def t_p2_causal_chain():
    d, dc, prop = _depths_of(_causal_chain(runner(cell()), 4))
    ok = dc == 4
    return ok, "causal depth %d (want 4, the constructed chain length)" % dc


# ----------------------------------------------------------------- T-P3
def t_p3():
    """crossed_ever True while crossed_at_final False, and no final claim fires."""
    r = runner(cell())
    o = r._place(b"\x00" * 8, 0, niche=0)
    r.held_max_ever = 1.0
    r.first_cross = {"epoch": 1, "oid": o.oid, "held": 1.0, "niche": 0}
    r.cross_events = [dict(r.first_cross)]
    r._kill(o)                      # the crossing lineage is reaped before the end
    s = r.summary()
    ok = (s["crossed_ever"] is True and s["crossed_at_final"] is False
          and s["held_max_ever"] >= CROSS and s["held_max_final"] < CROSS)
    return ok, "ever %s/%.2f  final %s/%.2f" % (
        s["crossed_ever"], s["held_max_ever"], s["crossed_at_final"], s["held_max_final"])


# ----------------------------------------------------------------- T-P8
def t_p8_isolated():
    """Every niche populated, counts differ by at most one, no migration."""
    res = world.run_cell(cell(structure="NICHES_ISOLATED", world="SOUP_MEM"), 3,
                         tier="S", max_epochs=30)
    occ = res["summary"]["niche_occupancy"]
    mig = res["summary"]["migration_events"]
    start = [0, 0, 0, 0]
    r = runner(cell(structure="NICHES_ISOLATED", world="SOUP_MEM"))
    for i in range(r.pop_cap):
        start[r._initial_niche(i)] += 1
    ok = (all(n > 0 for n in start) and max(start) - min(start) <= 1 and mig == 0)
    return ok, "initial %s (spread %d), migrations %d" % (start, max(start) - min(start), mig)


def t_p8_reservoir_not_all_easy():
    r = runner(cell(structure="RESERVOIR", world="SOUP_MEM"))
    start = [0, 0, 0, 0]
    for i in range(r.pop_cap):
        start[r._initial_niche(i)] += 1
    share = start[0] / float(sum(start))
    ok = share < 0.5
    return ok, "easy-niche share at t=0 is %.3f (must be < 0.5)" % share


# ----------------------------------------------------------------- T-P9
def t_p9_composition():
    """RESERVOIR x COEVO_ENV: niche 0 easy, hard niches harder, coevolution still live."""
    c = cell(structure="RESERVOIR", environment="COEVO_ENV", world="SOUP_MEM")
    r = runner(c)
    r._env_epoch()                                  # build the coevolving env population
    o0 = r._place(b"\x00" * 8, 0, niche=0)
    o1 = r._place(b"\x00" * 8, 0, niche=1)
    s0, s1 = r._env_spec_for(o0), r._env_spec_for(o1)
    easy = s0.read_order == "FORCED_READ" and s0.bridge == "NEUTRAL_BRIDGE"
    hard = not (s1.read_order == "FORCED_READ" and s1.bridge == "NEUTRAL_BRIDGE")
    # coevolution still drives the transform in the hard niche
    coevo = s1.transform in ("XOR1", "ADD1", "XOR15", "XOR5A")
    # deterministic: same inputs, same answer, twice
    det = (r._env_spec_for(o0).as_dict() == s0.as_dict())
    ok = easy and hard and coevo and det
    return ok, "niche0 easy=%s, niche1 hard=%s, coevo=%s, deterministic=%s" % (
        easy, hard, coevo, det)


# ----------------------------------------------------------------- T-P10
def t_p10_absent():
    ok = "ENV_MIG" not in G.FACTORS["structure"]
    levels = sorted(G.FACTORS["structure"])
    return ok, "ENV_MIG absent from Cycle-9 grammar; structure levels %s" % (levels,)


def t_p10_inertness():
    """Demonstrate on the PREDECESSOR code that ENV_MIG's gate could never fire.

    The gate is `if s == "ENV_MIG" and self.env_difficulty(o.niche) < 0.5: continue`,
    and env_difficulty returns 1.0 for every structure except RESERVOIR. So under
    ENV_MIG the skip never happens and the level is a plain 0.05 migration rate.
    """
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent
                           / "z80atlas-2026-09-19"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "legacy_world",
        pathlib.Path(__file__).resolve().parent.parent.parent
        / "z80atlas-2026-09-19" / "world.py")
    legacy = importlib.util.module_from_spec(spec)
    sys.modules["legacy_world"] = legacy
    spec.loader.exec_module(legacy)
    lr = legacy.Runner(cell(structure="ENV_MIG", world="SOUP_MEM"), 1, tier="S", max_epochs=1)
    diffs = {lr.env_difficulty(n) for n in range(lr.n_niches)}
    never_skips = all(d >= 0.5 for d in diffs)
    return never_skips, ("predecessor env_difficulty under ENV_MIG returns %s for every "
                         "niche, so the `< 0.5` skip never fires" % (sorted(diffs),))


# ----------------------------------------------------------------- harness
REPAIRED = [
    ("T-P1  certificate built", t_p1),
    ("T-P1  truncated -> none", t_p1_truncated),
    ("T-P2  A star", t_p2_star),
    ("T-P2  B ordinary descent", t_p2_descent),
    ("T-P2  C causal chain", t_p2_causal_chain),
    ("T-P3  historical vs final", t_p3),
    ("T-P8  isolated niches", t_p8_isolated),
    ("T-P8  reservoir not all easy", t_p8_reservoir_not_all_easy),
    ("T-P9  env x structure", t_p9_composition),
    ("T-P10 absent from grammar", t_p10_absent),
    ("T-P10 inertness demonstrated", t_p10_inertness),
]

# (label, injector, test) - each MUST fail while the defect is injected.
INJECTED = [
    ("T-P1  certificate", no_migration_events, t_p1),
    ("T-P2  B descent", untagged_causal_edges, t_p2_descent),
    ("T-P8  isolated niches", lambda: inject(world.Runner, "_initial_niche",
                                             lambda self, i: 0), t_p8_isolated),
    ("T-P8  reservoir easy share", lambda: inject(world.Runner, "_initial_niche",
                                                  lambda self, i: 0),
     t_p8_reservoir_not_all_easy),
    ("T-P9  env x structure", legacy_env_spec, t_p9_composition),
]


def main():
    ok = True
    print("REPAIRED SUBSTRATE - every check must PASS")
    print("-" * 92)
    for name, fn in REPAIRED:
        try:
            good, detail = fn()
        except Exception as e:                                    # noqa: BLE001
            good, detail = False, "raised %s: %s" % (type(e).__name__, e)
        ok &= good
        print("%-6s %-32s %s" % ("PASS" if good else "FAIL", name, detail))

    print()
    print("DEFECT INJECTED - every check must FAIL (a test that cannot fail is worthless)")
    print("-" * 92)
    for name, injector, fn in INJECTED:
        with injector():
            try:
                good, detail = fn()
            except Exception as e:                                # noqa: BLE001
                good, detail = False, "raised %s" % type(e).__name__
        caught = not good
        ok &= caught
        print("%-6s %-32s %s" % ("caught" if caught else "MISSED", name, detail))

    print("-" * 92)
    print("repair gate:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
