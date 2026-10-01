"""Task 2: W2-L refresh plant at row physics with dials neutralised.
usage: python t2_dials.py <tag> <M> <spec> [cells,comma|@file]
spec: '+'-joined dial letters (D,L,C,U,J; X = extended: noise0,dup0,economy off), 'ALL' = all active of DLCUJ,
'SINGLES' = each active dial separately, 'PAIRS' = each pair of active dials, 'NONE' = row physics."""
from w2s_common import *
import itertools
tag, M, spec = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sel = sys.argv[4] if len(sys.argv) > 4 else "@undecided"
PLANT = os.environ.get("W2S_PLANT", "refresh")
if sel.startswith("@"):
    ids = [l.strip() for l in (HERE / "out" / (sel[1:] + ".txt")).read_text().split(",") if l.strip()]
else:
    ids = sel.split(",")
NEUTRAL = {"D": dict(decay_shift=0), "L": dict(loss=0.0), "C": dict(cap=0, collision="none"),
           "U": dict(update_mode="sync", update_period=1), "J": dict(lat_jitter=0),
           "E": dict(e_income=0, c_emit=0, c_op=0, c_mem=0), "N": dict(noise=0, dup=0.0)}
def active(ph):
    a = []
    if ph.decay_shift > 0: a.append("D")
    if ph.loss > 0: a.append("L")
    if ph.cap > 0: a.append("C")
    if ph.update_mode != "sync" or ph.update_period != 1: a.append("U")
    if ph.lat_jitter > 0: a.append("J")
    return a
def active_x(ph):
    a = active(ph)
    if ph.economy_on: a.append("E")
    if ph.noise > 0 or ph.dup > 0: a.append("N")
    return a
def apply(ph, dials):
    kw = {}
    for d in dials: kw.update(NEUTRAL[d])
    return ph.replace(**kw).validate() if kw else ph
ck = Clock(); out = []
for cid in ids:
    r = hc.row(cid); ph0, env = cell(r)
    p = ph0.replace(state_dim=max(2, ph0.state_dim), prog_len=max(hv.NEED_L[PLANT], ph0.prog_len)).validate()
    act = active(ph0)
    if spec == "ALL": cfgs = [act]
    elif spec == "SINGLES": cfgs = [[d] for d in act]
    elif spec == "PAIRS": cfgs = [list(c) for c in itertools.combinations(act, 2)]
    elif spec == "NONE": cfgs = [[]]
    elif spec == "LOO": cfgs = [[d for d in act if d != x] for x in act]
    elif spec == "LOOX": cfgs = [[d for d in active_x(ph0) if d != x] for x in active_x(ph0)]
    elif spec == "ALLX": cfgs = [active_x(ph0)]
    elif spec == "SINGLESX": cfgs = [[d] for d in active_x(ph0)]
    elif spec == "PAIRSX": cfgs = [list(c) for c in itertools.combinations(active_x(ph0), 2)]
    else: cfgs = [spec.split("+")]
    seeds = held_seeds(r, 64)[:M]
    for dials in cfgs:
        pp = apply(p, dials)
        g = hv.plant(PLANT, pp)
        o = flip_eval(pp, g, env, seeds); o.pop("pairs"); o.pop("tab", None)
        o.update(plant=PLANT, cell=cid, dials="+".join(dials) or "none", active=act, active_x=active_x(ph0), M=M)
        out.append(o)
        print(cid[:8], "act", "".join(act), "->", o["dials"], "M%d acc %.3f [%.3f,%.3f] chg %.3f [%.3f]" % (M, o["acc"], o["lo99"], o["hi99"], o["chg"], o["chg_lo99"]), flush=True)
save(f"t2_{tag}.json", {"rows": out, "compute": ck.done()}); print(ck.done())
