"""W2-26 s4: per-birth genotype side-switch rates for the 7ae3 family (all 23 s1 replays).
Denominator: every accepted CAUSAL birth whose parent P (genome at the interaction, dg) is 7ae3-family
(>= 51/64 bytes equal to the implant at shift 0) and a static side-0 NON-converter (conv0 < 0.5).
Numerator routes:
  AT BIRTH  the child's birth genome is a static side-0 converter (conv0 >= 0.5); causal byte found by single-byte
            back-application onto P; source from s2.birth_sources (CE / DW / VW / RS / MB) or 'multi'.
  IN PLACE  the child's genome becomes a static side-0 converter later through a non-relabelling interaction
            (s1 hist: IM = _mutate, IX = execution write by self or partner ctx), before its next relabel.
Assay: common.outcome, BASE bank panel, N = 200 per genome per side (side 0; side 1 for converters only).
python -B s4_birth_rates.py -> s4_birth_rates.json"""
import json, pathlib, pickle, random, sys, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
sys.path.insert(0, str(HERE.parent / "W2-17_runaway_departure"))
import common as C  # noqa: E402
from r2_replay import RUNS  # noqa: E402
from s2_switch_diffs import birth_sources  # noqa: E402

N = 200
banks = pickle.load(open(HERE.parent / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]
r = C.runner_for_spec(C.run_ds.DONOR)
IMP = C.run_ds.donor_genome()
rng = random.Random("W2-26-s4")
PAN = []
for _ in range(N):
    ep = rng.randrange(10, 300)
    PAN.append(banks[ep][rng.randrange(len(banks[ep]))])
CACHE = {}


def conv(g, side):
    k = (g, side)
    if k not in CACHE:
        CACHE[k] = sum(C.outcome(r, g, y, side, C.ZERO, cy, 0.0, None)["conv"] for y, cy in PAN) / N
    return CACHE[k]


def f0(g):
    return sum(a == b for a, b in zip(g, IMP))


def cause(Pg, g, srcmap):
    for j in range(64):
        if g[j] != Pg[j]:
            h = bytearray(Pg); h[j] = g[j]
            if conv(bytes(h), 0) >= 0.5:
                return {"pos": j, "from": "%02x" % Pg[j], "to": "%02x" % g[j], "bits": bin(Pg[j] ^ g[j]).count("1"),
                        "src": srcmap.get(j, "?")}
    return "multi"


def main():
    res = {"per_run": {}, "events": []}
    for label, (_, dep) in RUNS.items():
        cls = "RUN" if dep >= 22 else "CTL"
        d = json.loads((HERE / "s1_out" / (label + ".json")).read_text())
        B = {int(k): v for k, v in d["births"].items()}
        H = {int(k): v for k, v in d["hist"].items()}
        relabel_e = collections.defaultdict(list)   # oid -> epochs it was relabelled away (as victim)
        for k, v in B.items():
            relabel_e[v["void"]].append(v["e"])
        den = {0: 0, 1: 0}
        num = collections.Counter()
        for k, v in sorted(B.items()):
            if not v["c"]:
                continue
            Pg = bytes.fromhex(v["dg"])
            if f0(Pg) < 51 or conv(Pg, 0) >= 0.5:
                continue
            ps = v["pside"]
            den[ps] += 1
            g = bytes.fromhex(v["g"])
            if g != Pg and conv(g, 0) >= 0.5:
                c = cause(Pg, g, birth_sources(v))
                route = "birth:" + (c if c == "multi" else c["src"] + ("1b" if c["bits"] == 1 else "mb"))
                num[(ps, route)] += 1
                res["events"].append({"run": label, "cls": cls, "k": k, "e": v["e"], "pside": ps, "route": route,
                                      "cause": c, "c1": conv(g, 1)})
                continue
            # in place: walk k's hist until it is relabelled away
            end = min([e for e in relabel_e.get(k, []) if e >= v["e"]] + [10 ** 9])
            cur = bytearray(g)
            for ev in H.get(k, []):
                if not (v["e"] <= ev["e"] <= end):
                    continue
                prev = bytes(cur)
                src = {}
                for j, old, new, pv in ev["ex"]:
                    cur[j] = new; src[j] = "IX"
                for j, old, new in ev["mu"]:
                    cur[j] = new; src[j] = "IM"
                if bytes(cur) != prev and conv(bytes(cur), 0) >= 0.5:
                    c = cause(prev, bytes(cur), src)
                    if c == "multi":
                        route = "inplace:multi"
                    else:
                        route = "inplace:" + c["src"] + ("1b" if c["bits"] == 1 else "mb")
                    num[(ps, route)] += 1
                    res["events"].append({"run": label, "cls": cls, "k": k, "e": ev["e"], "pside": ps, "route": route,
                                          "cause": c, "c1": conv(bytes(cur), 1), "ndiff_vs_P": sum(a != b for a, b in zip(cur, Pg))})
                    break
        res["per_run"][label] = {"cls": cls, "den": den, "num": {"%d|%s" % k: v for k, v in num.items()}}
        print(label, cls, den, dict(num), flush=True)
    (HERE / "s4_birth_rates.json").write_text(json.dumps(res, indent=1))
    print("cache", len(CACHE))


if __name__ == "__main__":
    main()
