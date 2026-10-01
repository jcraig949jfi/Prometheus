"""W2-42 r1: bit-exact replay of W2-29 runs (FULL s1438, FULL s1469, BANK s1505) with W2-29's run3 copied verbatim
plus PASSIVE recorders (no rng use, no world-state writes):
  births: every causal-lineage birth (B): epoch, child, parent, donor side, donor pre-genome id, child genome id,
          victim pre-anc, victim pre-genome id, victim pre-in-lineage
  minter: every interaction with >=1 causal-lineage member alive before it: per member side, pre/post genome id,
          oid changed?, post anc, partner pre genome id, partner anc, partner in lineage, partner post gid,
          partner slot became a lineage child
  snaps:  per epoch, Counter of genome ids over live causal-lineage members
Bit-exact gate: B, Bxk, kin, Ball, epochs, maxA, depth_f, calls, stop, A_end, N_end == runs_*.jsonl row, and
G == genomes_*.jsonl.   python -B r1_replay.py  -> r1_<arm>_<s>.json, r1_gate.json"""
import json, pickle, random, sys, time, pathlib
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W29 = HERE.parent / "W2-29_residue"
sys.path.insert(0, str(W29))
import w29  # noqa
F = w29.F
from ffield import make_runner, set_org, Model, depth_from  # noqa


def run3x(rule, seed, partner, bank=None, pool=None, T=300):
    struct, ctx, mut = "FIELD", "CARRY", True
    r = make_runner(rule, seed, mut=mut)
    mrng = random.Random(repr(("W2-14", rule, seed, struct, partner, ctx, mut)))
    model = Model(partner, mrng, bank, pool, r.L)
    founder = next(o for o in r.orgs if o.anc == 0)
    f0 = founder.oid
    g_founder = r._genome(founder)
    causal_set = {f0}
    cnt = {"B": 0, "Ball": 0, "last_birth": 0, "calls": 0, "Bxk": 0, "kin": 0}
    G = {}
    GID = {}

    def gid(g):
        k = GID.get(g)
        if k is None:
            k = GID[g] = len(GID)
        return k
    births, minter, snaps = [], [], []
    orig_lb = r._lin_birth
    anc0_oids = set()
    cur = {}

    def record(child, vic):
        if vic is None:
            vic = next((o for o in r.orgs if o.alive and o.oid == child), None)
            if vic is None:
                return None
        g = r._genome(vic)
        e = G.get(g)
        if e is None:
            G[g] = [r.epoch, cnt["B"], 1]
        else:
            e[2] += 1
        return g

    def lb(child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None, victim_pre_anc=None, vic=None):
        if causal and parent in causal_set:
            causal_set.add(child)
            cnt["B"] += 1
            if victim_pre_anc is not None:
                if victim_pre_anc == 0:
                    cnt["kin"] += 1
                else:
                    cnt["Bxk"] += 1
            g = record(child, vic)
            births.append([r.epoch, child, parent, cur["side_of"].get(parent), cur["pre"].get(parent),
                           None if g is None else gid(g), victim_pre_anc, cur["pre_vic"].get(child),
                           cur["vic_in_lin"].get(child)])
        if parent in anc0_oids:
            cnt["Ball"] += 1
            cnt["last_birth"] = r.epoch
        orig_lb(child, parent, niche, fid, span, causal, causal_pred, None)

    def interact(a, b, i):
        for o in (a, b):
            if ctx == "ZERO" and o.anc == 0:
                o.regs, o.fz, o.fc = None, 0, 0
        cnt["calls"] += 1
        anc0_oids.clear()
        anc0_oids.update(o.oid for o in (a, b) if o.anc == 0)
        pre = {a.oid: gid(r._genome(a)), b.oid: gid(r._genome(b))}
        side_of = {a.oid: 0, b.oid: 1}
        inl = {a.oid: a.oid in causal_set, b.oid: b.oid in causal_set}
        pre_oid = (a.oid, b.oid)
        pre_anc = (a.anc, b.anc)
        buf = []

        def collect(child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            src = a if a.oid == parent else b
            vic = b if src is a else a
            buf.append(((child, parent, niche, fid, span, causal, causal_pred), vic, vic.anc))
        r._lin_birth = collect
        try:
            r._pair_interact(i, a, b)
        finally:
            r._lin_birth = lb
        pv, vl = {}, {}
        for args, vic, vanc in buf:
            vo = pre_oid[0] if vic is a else pre_oid[1]
            pv[args[0]] = pre[vo]
            vl[args[0]] = inl[vo]
        cur["pre"], cur["side_of"], cur["pre_vic"], cur["vic_in_lin"] = pre, side_of, pv, vl
        for args, vic, vanc in buf:
            lb(*args, victim_pre_anc=vanc, vic=vic)
        if inl[pre_oid[0]] or inl[pre_oid[1]]:
            post = (gid(r._genome(a)), gid(r._genome(b)))
            orgs = (a, b)
            for s in (0, 1):
                if inl[pre_oid[s]]:
                    p = 1 - s
                    o, po = orgs[s], orgs[p]
                    minter.append([r.epoch, s, pre_oid[s], pre[pre_oid[s]], post[s], o.oid != pre_oid[s], o.anc,
                                   pre[pre_oid[p]], pre_anc[p], inl[pre_oid[p]], post[p],
                                   po.oid != pre_oid[p] and po.oid in causal_set])

    r._lin_birth = lb
    maxA, stopr, A, N = 1, "horizon", 1, 1
    for ep in range(T):
        r.epoch = ep
        r._env_epoch()
        alive = [o for o in r.orgs if o.alive]
        r.rng.shuffle(alive)
        for i in range(0, len(alive) - 1, 2):
            a, b = alive[i], alive[i + 1]
            lin = a.anc == 0 or b.anc == 0
            if not lin:
                if partner == "FULL":
                    r._pair_interact(i, a, b)
                    cnt["calls"] += 1
                continue
            if partner != "FULL":
                for o in (a, b):
                    if o.anc != 0:
                        g, st = model.draw(ep)
                        set_org(r, o, g, st)
            interact(a, b, i)
        for o in r.orgs:
            if o.alive:
                o.age += 1
        live = [o for o in r.orgs if o.alive]
        A = sum(o.anc == 0 for o in live)
        N = sum(o.oid in causal_set for o in live)
        snap = {}
        for o in live:
            if o.oid in causal_set:
                k = gid(r._genome(o))
                snap[k] = snap.get(k, 0) + 1
        snaps.append([ep, A, N, snap])
        maxA = max(maxA, A)
        if A == 0:
            stopr = "extinct"
            break
        if ep >= 100 and ep - cnt["last_birth"] >= 100:
            stopr = "frozen"
            break
        if cnt["Bxk"] >= 163:
            stopr = "xk163"
            break
    out = {"rule": rule, "seed": seed, "struct": struct, "partner": partner, "ctx": ctx, "mut": mut,
           "epochs": ep + 1, "stop": stopr, "B": cnt["B"], "Ball": cnt["Ball"], "maxA": maxA,
           "A_end": A, "N_end": N, "depth_f": depth_from(r.lineage, [f0]),
           "depth_world": depth_from(r.lineage), "calls": cnt["calls"], "Bxk": cnt["Bxk"], "kin": cnt["kin"]}
    edges = [[e["child"], e["parent"], e["epoch"]] for e in r.lineage if e["kind"] == "birth" and e["causal"]]
    return out, G, g_founder, {"gid": [g.hex() for g in sorted(GID, key=GID.get)], "births": births,
                               "minter": minter, "snaps": snaps, "causal_edges": edges, "f0": f0}


def load_row(path, s):
    for l in open(path):
        d = json.loads(l)
        if d["s"] == s:
            return d


if __name__ == "__main__":
    BANKS = pickle.load(open(F.HERE / "banks.pkl", "rb"))
    gate = {}
    for arm, tag, s in (("FULL", "FULL", 1438), ("FULL", "FULL", 1469), ("BANK", "BANKREP", 1505)):
        t0 = time.process_time()
        kw = dict(bank=BANKS["BASE"], pool=BANKS["POOL"]) if arm == "BANK" else {}
        out, G, gf, X = run3x("BASE", 9_998_000 + s, arm, **kw)
        ref = load_row(W29 / ("runs_%s.jsonl" % tag), s)
        gref = load_row(W29 / ("genomes_%s.jsonl" % tag), s)
        keys = ["B", "Bxk", "kin", "Ball", "epochs", "maxA", "depth_f", "calls", "stop", "A_end", "N_end"]
        mism = {k: (out[k], ref[k]) for k in keys if out[k] != ref[k]}
        Gmine = sorted([g.hex(), e[0], e[1], e[2]] for g, e in G.items())
        g_ok = Gmine == sorted(gref["genomes"]) and gf.hex() == gref["founder"]
        cpu = round(time.process_time() - t0, 2)
        gate["%s_%d" % (arm, s)] = {"scalar_mismatch": mism, "genomes_equal": g_ok, "cpu_s": cpu, "out": out}
        X["out"] = out
        (HERE / ("r1_%s_%d.json" % (arm, s))).write_text(json.dumps(X))
        print(arm, s, "mism", mism, "G_equal", g_ok, "cpu", cpu, flush=True)
    (HERE / "r1_gate.json").write_text(json.dumps(gate, indent=1))
