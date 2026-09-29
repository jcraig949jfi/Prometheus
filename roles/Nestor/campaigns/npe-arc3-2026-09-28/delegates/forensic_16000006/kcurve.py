"""Robustness beyond k=1: copy rate from the state left by k own blank-partner executions, k = 0..KMAX
(20 seeds x 2 sides, tag 'F16-K'), plus CONST and RANDOM. Panel: D0 genomes, path genomes, the localization
variants, and the 8 most common live competent genomes at epochs 400, 500, 700 of the replay.
Writes kcurve.json."""
import collections
import json
import pathlib

import measure as M

HERE = pathlib.Path(__file__).resolve().parent
KMAX = 6


def kcurve(g, k=20, tag="F16-K"):
    import run_nc
    world, r = M.env()
    n = r.L
    rates = []
    for kk in range(KMAX + 1):
        hits = tot = 0
        for sd in range(k):
            for side in (0, 1):
                st = M.FRESH
                for j in range(kk):
                    st = M.exec_once(g, st, side, (tag, "pre", sd, side, j))
                hits += bool(run_nc.copies(world, r, g, st, bytes(n), M.FRESH, side, (tag, kk, sd, side)))
                tot += 1
        rates.append(round(hits / tot, 4))
    return rates


def main():
    G = json.loads((HERE / "genealogy.json").read_text())
    L = json.loads((HERE / "localize.json").read_text())
    D = json.loads((HERE / "replay_events.json").read_text())
    panel = []
    for i, g in enumerate(G["d0_genomes"]):
        panel.append(("D0_%d" % i, g))
    for p in G["path"]:
        panel.append(("path_vid%d" % p["vid"], p["g"]))
    for row in L["rows"]:
        panel.append(("loc270+%s" % "_".join(map(str, row["applied"])), row["hex"]))
    for e in (400, 500, 700):
        c = collections.Counter(g for _, g in D["snaps"][str(e)]["live"])
        n = 0
        for g, cnt in c.most_common():
            if M.competent(bytes.fromhex(g)):
                panel.append(("e%d_top%d_x%d" % (e, n, cnt), g))
                n += 1
            if n == 8:
                break
    out = []
    for name, h in panel:
        g = bytes.fromhex(h)
        kc = kcurve(g)
        oth = M.state_rates(g, 20, ("CONST", "RANDOM"), tag="F16-K")
        rec = {"name": name, "hex": h, "rates_k": kc, **oth,
               "robust_k1_rule": kc[0] > 0 and kc[1] >= 0.25 * kc[0],
               "robust_all_k": kc[0] > 0 and all(x >= 0.25 * kc[0] for x in kc[1:])}
        out.append(rec)
        print(name, kc, oth, rec["robust_k1_rule"], rec["robust_all_k"], flush=True)
    (HERE / "kcurve.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
