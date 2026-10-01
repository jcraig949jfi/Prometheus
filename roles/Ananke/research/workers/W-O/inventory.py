"""W-O step 1: inventory of every recorded carrier-swap verdict CHANCE
(lens.swap_verdict output) in the Ananke records named in the brief.
Read-only over the records; writes out/inventory.csv and out/inventory_counts.json.

Sources scanned (swap arms only; perturbations such as delay+1 can never FLIP
and are excluded):
  WF   workers/W-F/out/census_s{0,1}.jsonl  (census_table.csv is derived from it)
  WI   workers/W-I/out/traj_<cell>.json     (table_<cell>.csv is derived from it)
  SCT  spikes/out/s_ct.json                 (upstream of W-E's class labels)
  W-E/W-G outputs, pte/c1b LABEL_TABLES.json, c1b_rows: scanned, 0 swap verdicts.
"""
import csv, glob, gzip, json, pathlib, sys, collections

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE.parents[1]            # roles/Ananke/research
ANK = RES.parent                 # roles/Ananke
REPO = ANK.parents[1]
sys.path.insert(0, str(REPO))
from prometheus.ananke import c1b, envs  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
FIELDS = ["vid", "source", "record", "record_line", "derived_record", "derived_line", "specimen", "family",
          "loader", "arm", "arrays", "timing", "offset", "swap_mode", "worlds", "seed_ns", "trial_set",
          "n_trials_scored_design", "normal_m", "normal_lo", "normal_hi", "swap_m", "swap_lo", "swap_hi",
          "readable_lo99_ge_60", "derived_reading"]

SITE = "S,E,r,Kp,Acc_sum,Acc_cnt,w"
FLIGHT = "Msum,Mcnt"
ARR = {"site_all": SITE, "channel_all": FLIGHT, "joint": SITE + "," + FLIGHT, "S": "S",
       "inbox": "Acc_sum,Acc_cnt", "Kp": "Kp", "E": "E", "r": "r", "w": "w",
       "channel_content": "Msum", "channel_count": "Mcnt",
       "inflight": FLIGHT, "sitestate": SITE, "payload": "Msum", "counts": "Mcnt"}


def offsets_wf(env):
    tk = c1b.ticks(env)
    t0 = tk["t0"][0]
    return {"mid": tk["mid"][0] - t0, "late": tk["late"][0] - t0, "pre": -1}


def wf_rows():
    out = []
    # census_table.csv line per cell (1-based incl header)
    ct = {}
    with open(RES / "workers/W-F/out/census_table.csv") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            ct[r["cell"]] = (i, r)
    for fn in sorted(glob.glob(str(RES / "workers/W-F/out/census_s*.jsonl"))):
        for ln, line in enumerate(open(fn), start=1):
            if not line.strip():
                continue
            r = json.loads(line)
            if "error" in r:
                continue
            env = envs.EnvSpec(**r["env"])
            offs = offsets_wf(env)
            cid8 = r["cell_id"][:8]
            ctl, ctr = ct.get(cid8, (None, None))
            secs = [("mid", r["mid"]), ("late", r["late"]), ("pre", r["pre"])]
            for tname, sec in secs:
                nrm = sec["normal"]
                for arm, v in sec.items():
                    if arm == "normal" or v.get("kind", "swap") != "swap" or v["verdict"] != "CHANCE":
                        continue
                    ar = ARR.get(arm) or ("Msum[%s]" % arm[3:] if arm.startswith("pay") else arm)
                    col = {("mid", "site_all"): "site_all", ("mid", "channel_all"): "channel_all",
                           ("late", "site_all"): "late_site", ("late", "channel_all"): "late_chan",
                           ("pre", "site_all"): "pre_site", ("pre", "channel_all"): "pre_chan"}.get((tname, arm), arm)
                    out.append(dict(source="WF", record=f"W-F/out/{pathlib.Path(fn).name}", record_line=ln,
                                    derived_record="W-F/out/census_table.csv", derived_line=f"{ctl}:{col}",
                                    specimen=r["cell_id"], family=r["family"], loader="c1_row", arm=arm, arrays=ar,
                                    timing=tname, offset=offs[tname], swap_mode="EVERY", worlds=64, seed_ns="0x5EA",
                                    trial_set="all", nrm=nrm, acc=v["acc"],
                                    derived=f"class={r['class']};class_late={r['class_late']};tags={ctr['tags'] if ctr else ''}"))
            if r.get("joint") and r["joint"]["verdict"] == "CHANCE":
                v = r["joint"]
                out.append(dict(source="WF", record=f"W-F/out/{pathlib.Path(fn).name}", record_line=ln,
                                derived_record="W-F/out/census_table.csv", derived_line=f"{ctl}:joint",
                                specimen=r["cell_id"], family=r["family"], loader="c1_row", arm="joint",
                                arrays=ARR["joint"], timing="mid", offset=offs["mid"], swap_mode="EVERY", worlds=64,
                                seed_ns="0x5EA", trial_set="all", nrm=r["mid"]["normal"], acc=v["acc"],
                                derived=f"class={r['class']};class_late={r['class_late']};tags={ctr['tags'] if ctr else ''}"))
    return out


def wi_rows():
    out = []
    for fn in sorted(glob.glob(str(RES / "workers/W-I/out/traj_*.json"))):
        r = json.loads(open(fn).read())
        c8 = r["cell"][:8]
        tab = RES / f"workers/W-I/out/table_{c8}.csv"
        tl = {}
        if tab.exists():
            with open(tab) as f:
                for i, row in enumerate(csv.DictReader(f), start=2):
                    tl[int(row["o"])] = (i, row)
        for o, d in sorted(r["offsets"].items(), key=lambda x: int(x[0])):
            for arm in r["arms"]:
                v = d[arm]
                if v["verdict"] != "CHANCE":
                    continue
                li, row = tl.get(int(o), (None, {}))
                col = {"site_all": "reader", "channel_all": "reader", "joint": "reader"}.get(arm, "sub_chance")
                out.append(dict(source="WI", record=f"W-I/out/traj_{c8}.json", record_line=f"offsets[{o}].{arm}",
                                derived_record=f"W-I/out/table_{c8}.csv", derived_line=f"{li}:{col}",
                                specimen=r["cell"], family=r["family"], loader="c1_row", arm=arm, arrays=ARR[arm],
                                timing=f"o{o}", offset=int(o), swap_mode="EVERY", worlds=64, seed_ns="0x5EE",
                                trial_set="1..", nrm=r["normal"], acc=v["acc"],
                                derived=f"reader={row.get('reader', '')};phase={row.get('phase', '')}"))
    return out


def sct_rows():
    out = []
    s = json.loads((RES / "spikes/out/s_ct.json").read_text())
    names = list(s)
    lines = (RES / "spikes/out/s_ct.json").read_text().splitlines()
    for name, row in s.items():
        env = None
        for arm in ("inflight", "sitestate", "payload", "counts", "w"):
            v = row.get(arm)
            if not v or v["verdict"] != "CHANCE":
                continue
            ln = next((i + 1 for i, l in enumerate(lines) if l.strip().startswith(f'"{name}"')), None)
            out.append(dict(source="SCT", record="spikes/out/s_ct.json", record_line=f"{ln}:{name}.{arm}",
                            derived_record="W-E/ret_census.py specimens() class; W-E/out/D_*.json",
                            derived_line=f"parent={name}",
                            specimen=name, family=row["family"], loader="d_wave", arm=arm, arrays=ARR[arm],
                            timing="mid_sct", offset=None, swap_mode="EVERY", worlds=64, seed_ns="0x5E3",
                            trial_set="all", nrm=row["normal"], acc=v["acc"], derived="W-E class input"))
    return out


def scan_null():
    """Confirm the other named sources hold no swap verdicts."""
    res = {}
    for p in ["pte/c1b/LABEL_TABLES.json", "pte/c1b/C1B_SUMMARY.json"]:
        t = (ANK / p).read_text()
        res[p] = {"CHANCE": t.count("CHANCE"), "swap": t.count("swap")}
    t = gzip.open(ANK / "pte/c1b/c1b_rows/rows.jsonl.gz", "rt").read()
    res["pte/c1b/c1b_rows/rows.jsonl.gz"] = {"CHANCE": t.count("CHANCE"), "swap": t.count("swap")}
    for w in ("W-E", "W-G"):
        n = 0
        for f in glob.glob(str(RES / f"workers/{w}/out/**/*.json"), recursive=True):
            n += open(f).read().count("CHANCE")
        res[f"workers/{w}/out"] = {"CHANCE": n}
    return res


if __name__ == "__main__":
    rows = wf_rows() + wi_rows() + sct_rows()
    with open(OUT / "inventory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for i, r in enumerate(rows):
            w.writerow({"vid": f"V{i:04d}", "source": r["source"], "record": r["record"], "record_line": r["record_line"],
                        "derived_record": r["derived_record"], "derived_line": r["derived_line"],
                        "specimen": r["specimen"], "family": r["family"], "loader": r["loader"], "arm": r["arm"],
                        "arrays": r["arrays"], "timing": r["timing"], "offset": r["offset"], "swap_mode": r["swap_mode"],
                        "worlds": r["worlds"], "seed_ns": r["seed_ns"], "trial_set": r["trial_set"],
                        "n_trials_scored_design": "", "normal_m": round(r["nrm"][0], 4), "normal_lo": round(r["nrm"][1], 4),
                        "normal_hi": round(r["nrm"][2], 4), "swap_m": round(r["acc"][0], 4), "swap_lo": round(r["acc"][1], 4),
                        "swap_hi": round(r["acc"][2], 4), "readable_lo99_ge_60": r["nrm"][1] >= 0.60,
                        "derived_reading": r["derived"]})
    cnt = collections.Counter(r["source"] for r in rows)
    by = collections.Counter((r["source"], r["arm"]) for r in rows)
    spec = {s: len({r["specimen"] for r in rows if r["source"] == s}) for s in cnt}
    readable = collections.Counter((r["source"], r["nrm"][1] >= 0.60) for r in rows)
    fam = collections.Counter((r["source"], r["family"]) for r in rows)
    summ = {"total": len(rows), "by_source": cnt, "specimens_by_source": spec,
            "by_source_arm": {f"{a}|{b}": n for (a, b), n in sorted(by.items())},
            "by_source_readable": {f"{a}|{b}": n for (a, b), n in readable.items()},
            "by_source_family": {f"{a}|{b}": n for (a, b), n in fam.items()},
            "null_sources": scan_null()}
    (OUT / "inventory_counts.json").write_text(json.dumps(summ, indent=1, default=int))
    print(json.dumps(summ, indent=1, default=int))
