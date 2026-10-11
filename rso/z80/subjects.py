"""C-017-T030 subjects: planted starters, the ten ground-truth arms, and the seed partitions. Read-only against archaeon/z80atlas.

Every arm is a native engine spec built with grammar.make (archaeon/z80atlas/grammar.py:68) on the C-017-T020 carrier world
(well_mixed / unlimited / fixed, vmcopy, G = 32, ECHO_forced; rso/z80/SELECTION.md s1). Planted tapes enter through the engine's
own transplant path (engine.py:179-185); the seeded arm uses the engine's seeded-replicator path (engine.py:176-178, 186-188).
GROUND TRUTH IS BY CONSTRUCTION, per arm (PREREGISTRATION.md s3): who writes the bytes of the function-bearing organisms.
"""
from archaeon.z80atlas import grammar as GR, tasks as T, vm

G = 32
TASK = "ECHO_forced"
I = vm.I
WORLD = {"topology": "well_mixed", "migration": "none", "resources": "unlimited", "env_dynamics": "fixed", "reservoir": False, "niches": 1}
REP = {"substrate": "vmcopy", "genome": G, "layout": "shared"}


def H():
    """Heritable function: solve ECHO, then copy the whole tape into the neighbour window (tasks.py:90)."""
    return T.pad(T.task_then_replicate(TASK, True), G)


def NH():
    """Function only, no copier (tasks.py:68 WITNESS)."""
    return T.pad(T.WITNESS[TASK], G)


def RECON():
    """Reconstructor: IN A / OUT A / NOP at 0..2, then a copier of bytes 3..31 ONLY (29/32 = .906 >= copy_min_frac .9, engine.py:320).
    Its child's bytes 0..2 are never written by the parent: they are whatever the target cell held (kept, donor_contributes,
    engine.py:35). A child placed over a functional occupant is functional; over an empty cell it is a NOP-prefixed copier."""
    return T.pad([I(21, 0), I(22, 0), 0, I(1, 1), 3, I(1, 2), 131, I(1, 3), 29, I(20), I(6, 3), I(16), 0xFC, I(23)], G)


def HOST():
    """Carries ECHO's bytes at 1..3 behind a HALT: never expresses them itself (unit known answer only, not an arm)."""
    return T.pad([I(23), I(21, 0), I(22, 0), I(23)], G)


def PARASITE():
    """JP 129: runs the neighbour's bytes from window offset 1 (unit known answer only, not an arm)."""
    return T.pad([I(13), 129], G)


# name, ground-truth class, origin truth, starter, planted cells, reproduction, pressure, epochs, init path
ARMS = [
    dict(name="H_ENDO_GATED", gt="ENDO", origin="INSERTED", starter="H", n=13, phys="ENDOGENOUS_COPY", press="competence_gated", epochs=80),
    dict(name="SEEDED_ENDO_GATED", gt="ENDO", origin="INSERTED", starter=None, n=0, phys="ENDOGENOUS_COPY", press="competence_gated", epochs=80,
         init="seeded_replicator"),
    dict(name="H_ENDO_IMPL", gt="ENDO", origin="INSERTED", starter="H", n=13, phys="ENDOGENOUS_COPY", press="implicit_survival", epochs=80),
    dict(name="H_EXT_GATED", gt="EXT", origin="INSERTED", starter="H", n=13, phys="EXTERNAL", press="competence_gated", epochs=200),
    dict(name="H_EXT_SHORT", gt="EXT", origin="INSERTED", starter="H", n=13, phys="EXTERNAL", press="competence_gated", epochs=10),
    dict(name="NH_EXT_GATED", gt="EXT", origin="INSERTED", starter="NH", n=13, phys="EXTERNAL", press="competence_gated", epochs=200),
    dict(name="RANDOM_EXT_GATED", gt="EXT", origin="ARISEN", starter=None, n=0, phys="EXTERNAL", press="competence_gated", epochs=200),
    dict(name="RECON_ENDO_IMPL", gt="ENV", origin="INSERTED", starter="RECON", n=128, phys="ENDOGENOUS_COPY", press="implicit_survival", epochs=100),
    dict(name="NH_ENDO_SHORT", gt="INS", origin="INSERTED", starter="NH", n=13, phys="ENDOGENOUS_COPY", press="competence_gated", epochs=30),
    dict(name="RANDOM_ENDO_GATED", gt="NONE", origin="", starter=None, n=0, phys="ENDOGENOUS_COPY", press="competence_gated", epochs=200),
]
NAMES = [a["name"] for a in ARMS]
ARM = {a["name"]: a for a in ARMS}
STARTERS = {"H": H, "NH": NH, "RECON": RECON}


def spec(arm, epochs=None):
    init = arm.get("init", "random")
    s = GR.make(WORLD, REP, arm["phys"], [arm["press"]], TASK, "local_byte", init, stage="early", reason="z80attr:" + arm["name"])
    s["budget"] = dict(s["budget"], max_epochs=epochs or arm["epochs"])
    if arm["starter"]:
        s["transplant"] = {"from_run": None, "tapes": [STARTERS[arm["starter"]]().hex()] * arm["n"]}
        s["init"] = "transplanted_lineage"          # the scheduler's relabel (scheduler.py:246-262); physics ignores it under transplant
        s["spec_id"] = GR.spec_id(s) + "-t"
    return s


# ---- seeds: base + 1000 * arm index + k, k = 1.. (dev 17_030, Pallas challenge 17_040, confirmatory 17_050)
BASE = {"dev": 17_030_000, "challenge": 17_040_000, "confirm": 17_050_000}
# registered namespaces this partition must not touch (inclusive ranges): smoke 16_021_xxx, C-016 re-runs 16_020 / 16_030 / 16_3xx,
# C-017-T020 demand gate 17_020_001 + 100 * 17 + 23, Archaeon's small integers (scheduler.py:173, 217, 241-262: 1, 2, 100.., 2000..)
REGISTERED = [(16_020_000, 16_031_999), (16_300_000, 16_399_999), (17_020_000, 17_022_999), (0, 1_000_000)]


def seeds(name, part, n):
    return [BASE[part] + 1000 * NAMES.index(name) + k for k in range(1, n + 1)]


def partition_conflicts(n=999):
    allseeds = [(a, p, s) for a in NAMES for p in BASE for s in seeds(a, p, n)]
    bad = [(a, p, s) for a, p, s in allseeds if any(lo <= s <= hi for lo, hi in REGISTERED)]
    seen = {}
    for a, p, s in allseeds:
        if s in seen:
            bad.append((a, p, s))
        seen[s] = 1
    return bad
