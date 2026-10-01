import json, gzip, pathlib, collections
H = pathlib.Path(__file__).resolve().parent
R = {}
for t in "ABC":
    d = json.load(open(H / "out" / f"maj_m{t}.json")); d.pop("_clock", None); R.update(d)
rows = {json.loads(l)["cell_id"]: json.loads(l) for l in gzip.open(H.parents[3] / "pte/c1_rows/cells.jsonl.gz", "rt")}
lc = {o["cell"]: o for o in json.load(open(H.parent / "W2-M/out/lc_maj.json"))["rows"]}
cl = {o["cell"]: o for o in json.load(open(H.parent / "W2-M/out/classification.json"))}
cap = open(H / "out/maj_capped.txt").read().split(",")
cnt = collections.Counter(); lines = []
for c, o in R.items():
    r = rows[c]; p = r["physics"]
    if o["lo99"] > 0.55:
        cls = "PLANT-SOLVED+INT" if o["plant_minus_DICT"][0] > 0 else "PLANT-SOLVED"
    else:
        why = []
        if p["topology"] == "global": why.append("global")
        if p["cap"] > 0 and p["collision"] == "aloha": why.append("aloha")
        if lc[c]["placement"] != "one_hop": why.append(lc[c]["placement"])
        cls = "UNDECIDED(" + ",".join(why or ["plant-inadequate"]) + ")"
    cnt[cls.split("(")[0]] += 1
    lines.append(f"| {c[:8]} | {p['topology'][:5]} {p['update_mode']} {p['update_period'] if p['update_mode']=='sync' else p['update_p']} | {lc[c]['placement']} | {lc[c]['lc_bound']:.3f} | {o['member']} ({o['lines']}) | {o['acc']:.3f} [{o['lo99']:.3f}] | {o['DICT'] if o['DICT'] is None else round(o['DICT'],3)} | {o['plant_minus_DICT']} | {o['champ_held']:.3f} | {cl.get(c, {}).get('class', '-')} | {cls} |")
hdr = "| cell | topo/update | placement | lc_bound (W2-M) | member (lines) | acc [lo99] 32 pairs | DICT | plant-DICT 99% | champion held | W2-M class | W2-Z class |\n|---|---|---|---|---|---|---|---|---|---|---|"
txt = hdr + "\n" + "\n".join(sorted(lines)) + "\n\nP-LC (W2-M light cone < .60, not scored): " + ", ".join(x[:8] for x in cap if x) + f"\n\ncounts: {dict(cnt)}  + P-LC {len([x for x in cap if x])}\n"
(H / "out/maj_table.md").write_text(txt); print(txt[-600:]); print(cnt)
