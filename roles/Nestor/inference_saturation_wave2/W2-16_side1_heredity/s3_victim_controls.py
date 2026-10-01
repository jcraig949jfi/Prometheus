"""Step 3: is the side-1 CVT-R failure intrinsic to the copier, or caused by the side-0 partner running first?
CVT (certs.cvt / certs.score unchanged) re-run with the step function's victim bytes replaced:
  RAND    sha256("VICTIM", sid, g, k)            -- Artemis's own victims (reproduces the record)
  HALT    all 0x76: the partner halts on its first instruction, executes nothing  -> pure self-copy
  RAND_HALT0  Artemis's random bytes but byte 0 forced to 0x76 (partner still present as bytes, never runs)
  RESEED  Artemis's procedure with 4 other victim seeds (is acceptance a per-genome coin flip?)
Both sides are scored, for side-1-certified genomes and the side-0 comparison genomes."""
import json, random, pathlib, time
from _env import A, ROWS, certs, FRESH, shabytes
import p11


def make_step(z, P, side, vfun):
    n = P["n"]

    def step(G, g, k):
        vb = vfun(g, k)
        ga, gb = (G, vb) if side == 0 else (vb, G)
        tape, _, _, _ = p11.interact(z, n=n, tape_len=P["tape_len"], ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                     budget=P["budget"], ops_mask=P["mask"], cmr=0.0, rng=random.Random(0))
        v0 = n if side == 0 else 0
        return bytes(tape[v0:v0 + n])
    return step


def run(G, r, side, mode, sid):
    P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"]); n = P["n"]
    if mode == "RAND":
        vf = lambda g, k: shabytes("VICTIM", sid, g, k, n=n)
    elif mode == "HALT":
        vf = lambda g, k: bytes([0x76]) * n
    elif mode == "RAND_HALT0":
        vf = lambda g, k: bytes([0x76]) + shabytes("VICTIM", sid, g, k, n=n)[1:]
    rows, base = certs.cvt(make_step(z, P, side, vf), G, r["hex"], False)
    return rows, base, certs.score(rows, n)


if __name__ == "__main__":
    t0 = time.time()
    side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
    s0 = [r for r in ROWS if r["P11"]["certified_sides"] == [0] and r["vm"] == "DENSE"]
    s0 = [r for r in s0 if not r["CVTR_accept"]] + [r for r in s0 if r["CVTR_accept"]][:12]
    out = []
    for r in side1 + s0:
        G = bytes.fromhex(r["hex"]); s = r["P11"]["certified_sides"][0]
        rec = {"key": r["key"], "cell": r["cell"], "p11_side": s, "record_cvtr": r["CVTR_accept"]}
        for mode in ("RAND", "HALT", "RAND_HALT0"):
            rows, base, sc = run(G, r, s, mode, r["hex"])
            rec[mode] = [sc[c]["n"] for c in ("CVT1", "CVT2", "CVTR")] + [sc["CVTR"]["accept"]]
            if mode == "HALT":
                rec["HALT_base_child_eq_parent"] = [base[0][0] == G, base[0][1] == base[0][0]]
                rec["HALT_child_diff_pos"] = [i for i in range(len(G)) if base[0][0][i] != G[i]]
        acc = []
        for j in range(4):
            sid = r["hex"] + ":reseed%d" % j
            acc.append(run(G, r, s, "RAND", sid)[2]["CVTR"]["accept"])
        rec["RESEED_accept"] = acc
        out.append(rec)
        print(rec, round(time.time() - t0))
    pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
