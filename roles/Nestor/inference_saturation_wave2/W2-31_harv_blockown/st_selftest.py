"""W2-31 self-tests ST1-ST4 (see PREREG). Output SELFTEST.json. No scoring quantity is computed here."""
import json, random, pathlib, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
from _env import A, ROWS, FRESH, shabytes  # noqa: E402
import _arms as W  # noqa: E402
import alien_vm, alien_pair as AP, p11  # noqa: E402

t0 = time.time()
out = {}
REF_HALT = alien_vm.build("HARV_HALT")
REF_BO = alien_vm.build("BLOCK_OWN")


def run_pair(vm, tape, regs, ops=0x2A, budget=300, n=64, order=(0, 1)):
    tape = bytearray(tape)
    st = []
    for who in order:
        start = n * who
        ctx = vm.Ctx(tape, start, n, policy=vm.ARENA, rng=random.Random(5), copy_mut_rate=0.0, sense=who)
        ctx.regs = None if regs[who] is None else list(regs[who])
        ctx.fz, ctx.fc = 0, 0
        vm.run(ctx, start, budget, ops_enabled=ops)
        st.append((ctx.regs, ctx.fz, ctx.fc, ctx.ops, ctx.writes, ctx.copy_bytes))
    return bytes(tape), st


# ST0: the HALT arm source is W2-7's HARV_HALT source, text-identical
out["ST0_halt_source_identical_to_W2-7"] = W.source("HALT") == REF_HALT.SOURCE

# ST1: each arm vs W2-7 HARV_HALT, identical where confinement counters stay 0, changed somewhere they fire
rng = random.Random("W2-31-ST1")
tapes = []
for i in range(1500):
    t = bytes(rng.randrange(256) for _ in range(128))
    regs = (None, None) if i % 2 == 0 else tuple([rng.randrange(256) for _ in range(8)] for _ in range(2))
    tapes.append((t, regs, (0x2A, 0x2C, 0xFF)[i % 3]))
st1 = {}
for arm in ("HALT", "BO_OP", "SO_OP", "BO_BL", "SO_BL"):
    z = W.vm(arm)
    c = dict(nohit=0, nohit_identical=0, hit=0, hit_changed=0)
    for t, regs, ops in tapes:
        a = run_pair(REF_HALT, t, regs, ops)
        W.reset(z)
        b = run_pair(z, t, regs, ops)
        k = W.counts(z); fired = k["_HB"] + k["_HS"]
        if fired == 0:
            c["nohit"] += 1; c["nohit_identical"] += a == b
        else:
            c["hit"] += 1; c["hit_changed"] += a != b
    c["pass"] = c["nohit"] > 0 and c["nohit"] == c["nohit_identical"] and (arm == "HALT" or c["hit_changed"] > 0)
    st1[arm] = c
out["ST1"] = st1

# ST2: BO_BL == W2-7 BLOCK_OWN wherever HARV did not fire
z = W.vm("BO_BL"); c = dict(noharv=0, identical=0, blocks_fired_in_identical=0)
for t, regs, ops in tapes:
    W.reset(z)
    b = run_pair(z, t, regs, ops)
    k = W.counts(z)
    if k["_HITS"] == 0:
        a = run_pair(REF_BO, t, regs, ops)
        c["noharv"] += 1; c["identical"] += a == b; c["blocks_fired_in_identical"] += (a == b and k["_HB"] > 0)
c["pass"] = c["noharv"] > 0 and c["noharv"] == c["identical"] and c["blocks_fired_in_identical"] > 0
out["ST2"] = c


# ST3: mechanism on hand-assembled programs
def prog(b):
    return bytes(b) + bytes(64 - len(b))


STORE0 = prog([0x21, 0x40, 0x00, 0x3E, 0x99, 0x77, 0x76])                     # side 0: (64) <- 0x99
LDIR0 = prog([0x21, 0x00, 0x00, 0x11, 0x40, 0x00, 0x01, 0x08, 0x00, 0xED, 0xB0, 0x76])  # side 0: [0,8)->[64,72)
LDIR1 = prog([0x21, 0x40, 0x00, 0x11, 0x00, 0x00, 0x01, 0x08, 0x00, 0xED, 0xB0, 0x76])  # side 1: [64,72)->[0,8)
HALT64 = prog([0x76])
expect = {  # arm: (store0 lands, ldir0 lands, ldir1 lands)
    "HALT": (True, True, True), "BO_OP": (True, False, True), "SO_OP": (False, False, True),
    "BO_BL": (True, False, False), "SO_BL": (False, False, False)}
st3 = {}
for arm, (e_s0, e_l0, e_l1) in expect.items():
    z = W.vm(arm)
    t, _ = run_pair(z, STORE0 + HALT64, (None, None))
    s0 = t[64] == 0x99
    t, _ = run_pair(z, LDIR0 + HALT64, (None, None))
    l0 = t[64:72] == LDIR0[0:8]
    t, _ = run_pair(z, HALT64 + LDIR1, (None, None))
    l1 = t[0:8] == LDIR1[0:8]
    # reset: a FRESH tape where side 1 runs alone (side 0 never started) -> its write into side 0 is protected in OP
    t, _ = run_pair(z, HALT64 + LDIR1, (None, None), order=(1,))
    l1_alone = t[0:8] == LDIR1[0:8]
    e_alone = arm == "HALT"   # OP arms: side 0 never started -> protected; BL arms: outside own half
    got = (s0, l0, l1)
    st3[arm] = {"store0_lands": s0, "ldir0_lands": l0, "ldir1_lands_after_side0_ran": l1,
                "ldir1_lands_on_fresh_tape_side0_never_ran": l1_alone,
                "pass": got == (e_s0, e_l0, e_l1) and l1_alone == e_alone}
out["ST3"] = st3

# ST4: same-physics ruler + CVT-R step receives the arm module
s1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
st4 = {}
for arm in ("HALT", "BO_OP", "SO_OP", "BO_BL", "SO_BL"):
    z = W.vm(arm); same = tot = 0
    for r in s1[:6]:
        g = bytes.fromhex(r["hex"])
        for side in (0, 1):
            ga, gb = (g, bytes(64)) if side == 0 else (bytes(64), g)
            kw = dict(n=64, tape_len=128, ga=ga, gb=gb, st_a=(None, 0, 0), st_b=(None, 0, 0), budget=300,
                      ops_mask=0x2A, cmr=0.002, victim_side=1 - side, seed=("W2-31-ST4", r["key"], side))
            a = p11.assay(z, **kw); b = AP.assay(z, early=False, **kw)
            tot += 1; same += (a["pass"] == b["pass"] and a["draws"] == b["draws"])
    # counter fires inside the CVT-R step for a side-1 copier (adapter.make_step -> p11.interact(z))
    fired = 0
    for r in s1:
        G = bytes.fromhex(r["hex"])
        step = A.make_step(z, 64, 128, 300, 0x2A, 1, r["hex"])
        W.reset(z)
        for g in range(3):
            step(G, g, 0)
        k = W.counts(z)
        fired += (k["_HB"] + k["_HS"] + k["_HITS"]) > 0
    st4[arm] = {"assay_identical": same, "n": tot, "cvtr_step_copiers_with_counter_firing": fired,
                "pass": same == tot and fired > 0}
out["ST4"] = st4

out["all_pass"] = (out["ST0_halt_source_identical_to_W2-7"] and all(v["pass"] for v in st1.values())
                   and out["ST2"]["pass"] and all(v["pass"] for v in st3.values())
                   and all(v["pass"] for v in st4.values()))
out["seconds"] = round(time.time() - t0, 1)
HERE.joinpath("SELFTEST.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
