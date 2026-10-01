"""W2-39: M* (F* reference process) with an arbitrary implanted founder genome, WITHOUT editing ffield.py / w22.py.
M* = w22.run2("BASE", seed, "FREE", "BANK", "CARRY", True, T=300, bank=BANKS["BASE"], pool=BANKS["POOL"], stop="xk"),
exactly as W2-22 p1_run.py ran it. The only intervention: ffield.make_runner reads the module global G7 at call time
(implant_bytes=G7), so we rebind ffield.G7 to the genotype before each run. ACTUAL_GENOME implant consumes no rng.
Genotypes: founder F = run_ds.donor_genome() (asserted == ffield.G7); 44->AC (ec->ac), 37->81 (a5->81), 43->C3, C3+AC."""
import pathlib, pickle, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-22_second_regime"))
import w22  # noqa: E402
F = w22.F
G_STOCK = F.G7
DONOR = F.run_ds.donor_genome()
assert DONOR == G_STOCK, "donor_genome != ffield.G7"


def mk(g, edits, expect):
    b = bytearray(g)
    for pos, v in edits.items():
        assert b[pos] == expect[pos], (pos, hex(b[pos]))
        b[pos] = v
    return bytes(b)


GENOS = {"F": DONOR,
         "AC": mk(DONOR, {44: 0xAC}, {44: 0xEC}),
         "81": mk(DONOR, {37: 0x81}, {37: 0xA5}),
         "C3": mk(DONOR, {43: 0xC3}, {43: 0xC1}),
         "C3+AC": mk(DONOR, {43: 0xC3, 44: 0xAC}, {43: 0xC1, 44: 0xEC})}
BANKS = None


def run(geno, seed, traj=False):
    global BANKS
    if BANKS is None:
        BANKS = pickle.load(open(F.HERE / "banks.pkl", "rb"))
    F.G7 = GENOS[geno]
    try:
        return w22.run2("BASE", seed, "FREE", "BANK", "CARRY", True, T=300, bank=BANKS["BASE"], pool=BANKS["POOL"],
                        traj=traj, mech=None, stop="xk")
    finally:
        F.G7 = G_STOCK


def founder_bytes(geno, seed=1):
    F.G7 = GENOS[geno]
    try:
        r = F.make_runner("BASE", seed)
        o = next(o for o in r.orgs if o.anc == 0)
        return r._genome(o)
    finally:
        F.G7 = G_STOCK
