"""W2-23 self-tests ST1-ST3 (see PREREG). Output SELFTEST.json."""
import json, random, pathlib, sys, time
sys.dont_write_bytecode = True
import _harv as H
import alien_pair as AP          # W2-7, puts campaign z80atlas-verify on sys.path
import p11, z8 as Z8PLAIN

t0 = time.time()
out = {}


def run_pair(vm, tape, regs, ops=0x2A, budget=300, n=64):
    tape = bytearray(tape)
    st = []
    H_ = getattr(vm, '_HITS', [0]); H_[0] = 0
    for who, start in ((0, 0), (1, n)):
        ctx = vm.Ctx(tape, start, n, policy=vm.ARENA, rng=random.Random(5), copy_mut_rate=0.0, sense=who)
        ctx.regs = None if regs[who] is None else list(regs[who])
        ctx.fz, ctx.fc = 0, 0
        vm.run(ctx, start, budget, ops_enabled=ops)
        st.append((ctx.regs, ctx.fz, ctx.fc, ctx.ops, ctx.writes, ctx.copy_bytes))
    return bytes(tape), st, H_[0]


# ST1: plain HARV vs stock plain z8 (identical where no hit; live where hits)
rng = random.Random("W2-23-ST1")
st1 = {}
for name in ("HARV_HALT", "HARV_WRAP"):
    vm = H.plain(name)
    c = dict(nohit=0, nohit_identical=0, hit=0, hit_changed=0)
    for i in range(1500):
        tape = bytes(rng.randrange(256) for _ in range(128))
        regs = (None, None) if i % 2 == 0 else tuple([rng.randrange(256) for _ in range(8)] for _ in range(2))
        ops = (0x2A, 0x2C, 0xFF)[i % 3]
        a = run_pair(Z8PLAIN, tape, regs, ops)
        b = run_pair(vm, tape, regs, ops)
        if b[2] == 0:
            c["nohit"] += 1; c["nohit_identical"] += (a[0] == b[0] and a[1] == b[1])
        else:
            c["hit"] += 1; c["hit_changed"] += (a[0] != b[0] or a[1] != b[1])
    c["pass"] = c["nohit"] > 0 and c["nohit"] == c["nohit_identical"] and c["hit_changed"] > 0
    st1[name] = c
# plain STOCK rebuild == campaign z8
vm = H.plain("STOCK"); same = 0
for i in range(300):
    tape = bytes(rng.randrange(256) for _ in range(128))
    same += run_pair(Z8PLAIN, tape, (None, None))[:2] == run_pair(vm, tape, (None, None))[:2]
st1["plain_stock_rebuild_identical"] = [same, 300]
out["ST1"] = st1

# ST2: my injection on the dense source == alien_vm.build('HARV_*')
rng = random.Random("W2-23-ST2")
st2 = {}
for name in ("HARV_HALT", "HARV_WRAP"):
    a_vm, b_vm = H.dense(name), H.dense_mine(name)
    ok = 0; hits = 0
    for i in range(1000):
        tape = bytes(rng.randrange(256) for _ in range(128))
        regs = (None, None) if i % 2 == 0 else tuple([rng.randrange(256) for _ in range(8)] for _ in range(2))
        a = run_pair(a_vm, tape, regs); b = run_pair(b_vm, tape, regs)
        ok += a == b; hits += a[2] > 0
    st2[name] = {"identical": ok, "n": 1000, "runs_with_hits": hits, "pass": ok == 1000 and hits > 0}
out["ST2"] = st2

# ST3: P-11 ruler re-executes under the passed VM: p11.assay(HARV) == alien_pair.assay(HARV, early=False)
R = [json.loads(l) for l in (H.HERE.parents[2] / "Artemis/challenge/cvtr_nestor/results/ROWS.jsonl").read_text().splitlines() if l.strip()]
s1 = [r for r in R if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
st3 = {}
for name in ("HARV_HALT", "HARV_WRAP", "STOCK"):
    vm = H.dense(name); same = tot = 0; differs_from_stock = 0
    for r in s1[:6]:
        g = bytes.fromhex(r["hex"])
        for side in (0, 1):
            ga, gb = (g, bytes(64)) if side == 0 else (bytes(64), g)
            kw = dict(n=64, tape_len=128, ga=ga, gb=gb, st_a=(None, 0, 0), st_b=(None, 0, 0), budget=300,
                      ops_mask=0x2A, cmr=0.002, victim_side=1 - side, seed=("W2-23-ST3", r["key"], side))
            a = p11.assay(vm, **kw); b = AP.assay(vm, early=False, **kw)
            tot += 1; same += (a["pass"] == b["pass"] and a["draws"] == b["draws"])
            if name != "STOCK":
                c = p11.assay(H.dense("STOCK"), **kw)
                differs_from_stock += c["draws"] != a["draws"]
    st3[name] = {"identical": same, "n": tot, "draw_records_differ_from_stock": differs_from_stock,
                 "pass": same == tot}
out["ST3"] = st3
out["all_pass"] = all(v["pass"] for k in ("ST2", "ST3") for v in out[k].values()) and \
    all(st1[k]["pass"] for k in ("HARV_HALT", "HARV_WRAP")) and same == same
out["all_pass"] = out["all_pass"] and st1["plain_stock_rebuild_identical"][0] == 300
out["seconds"] = round(time.time() - t0, 1)
pathlib.Path(__file__).with_name("SELFTEST.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
