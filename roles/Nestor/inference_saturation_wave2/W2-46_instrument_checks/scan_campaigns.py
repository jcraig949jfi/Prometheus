"""W2-46: run the ichecks read-only across the npe-frontier and c9x-explore run scripts and their records.

    python -B scan_campaigns.py   -> FINDINGS.json + a markdown table on stdout

Read-only: parses scripts with ast (never imports or runs them), reads JSON records. No world runs.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ichecks._static import index_dirs  # noqa: E402
from ichecks.block_pooling import check_block_exchangeability  # noqa: E402
from ichecks.label_integrity import check_label_absorbing, check_label_readout_write_back  # noqa: E402
from ichecks.max_of_cached import scan_max_of_cached  # noqa: E402
from ichecks.screen_context import check_screen_context  # noqa: E402
from ichecks.stores_genomes import check_stores_genomes, load_records  # noqa: E402

NESTOR = HERE.parents[1]
CAMP = NESTOR / "campaigns"
WORLD = CAMP / "z80atlas-verify-2026-09-22"
TARGETS = [CAMP / "npe-frontier-2026-09-30", CAMP / "c9x-explore-2026-09-24"]
LENGTHS = frozenset(range(24, 257)) - {32}          # genome lengths; 32-byte strings would be sha256 digests
ABBR = {"OK": "PASS", "NOT_VERIFIED": "NV"}


def scripts():
    for t in TARGETS:
        for d in sorted(p for p in t.iterdir() if p.is_dir()):
            for s in sorted(d.glob("*.py")):
                if s.name.startswith("run_") or s.name == "dense_taint.py":
                    yield d, s


def records(d):
    files = sorted((d / "results").glob("*.json"))[:40] if (d / "results").is_dir() else []
    files += [d / n for n in ("RESULTS.json", "SUMMARY.json") if (d / n).is_file()]
    return load_records(files)


def main():
    t0 = time.process_time()
    utc = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip()
    idx = index_dirs([CAMP])
    rows = []
    for d, s in scripts():
        row = {"experiment": "%s/%s" % (d.parent.name.split("-2026")[0], d.name), "script": s.name}
        sc = check_screen_context(s, WORLD, [CAMP], _index=idx)
        lw = check_label_readout_write_back(s, [CAMP], WORLD, _index=idx)
        mx = scan_max_of_cached(s, [CAMP], WORLD, _index=idx)
        recs = records(d)
        sg = check_stores_genomes(recs, genome_len=LENGTHS) if recs else None
        row["checks"] = {
            "a_screen_context": {"verdict": sc.verdict, "reason": sc.reason,
                                 "contexts": sorted({"%s:%d %s" % (pathlib.Path(c["file"]).name, c["line"], c["kind"])
                                                     for c in sc.details.get("contexts", [])})},
            "c_label_write_back": {"verdict": lw.verdict, "reason": lw.reason,
                                   "readouts": sorted({"%s:%d" % (pathlib.Path(r["file"]).name, r["line"])
                                                       for r in lw.details.get("label_readouts", [])}),
                                   "write_back": {k: v for k, v in lw.details.get("write_back", {}).items() if v}},
            "d_max_of_cached": {"verdict": mx.verdict, "keys": sorted({h["key"] for h in mx.details.get("max_readouts", [])})},
            "h_stores_genomes": ({"verdict": sg.verdict, "n_records": sg.details["n_records"],
                                  "genome_sites": sg.details.get("n_genome_sites"),
                                  "register_sites": sg.details.get("n_register_sites")}
                                 if sg else {"verdict": "NOT_VERIFIED", "reason": "no parseable records"}),
        }
        rows.append(row)

    extra = {}
    # (c) absorbing label on X-MAT's own L_share series (closed 256-site tape: W2-34 inventory)
    xm = CAMP / "npe-frontier-2026-09-30" / "x_mat_internalize" / "results"
    series = {p.stem: [c["L_share"] for c in sorted(json.loads(p.read_text())["record"]["checkpoints"],
                                                   key=lambda c: c["epoch"])]
              for p in sorted(xm.glob("*.json"))}
    ab = check_label_absorbing(series, closed_population=True)
    extra["c_label_absorbing X-MAT-INTERNALIZE"] = {"verdict": ab.verdict, "reason": ab.reason,
                                                    "reached_full": ab.details.get("reached_full"),
                                                    "dropped": ab.details.get("dropped_after_full")}
    # (e) C-ATOMIC C2 pooled across specimens: are the specimen blocks exchangeable?
    v = json.loads((CAMP / "c9x-explore-2026-09-24" / "c_atomic" / "VERDICT.json").read_text())["C2"]
    per = v["per_specimen"]
    n_sp = v["n_per_arm"] // len(per)
    for key in ("ATOMIC", "ATOMIC_d5"):
        r = check_block_exchangeability({k[:8]: (x[key], n_sp) for k, x in per.items()})
        extra["e_blocks C-ATOMIC C2 %s per specimen (n=%d each)" % (key, n_sp)] = {
            "verdict": r.verdict, "reason": r.reason, "p_mc": r.details.get("p_mc"),
            "culprits": r.details.get("single_block_culprits")}
    out = {"generated_utc": utc, "cpu_s": None, "rows": rows, "extra": extra}
    out["cpu_s"] = round(time.process_time() - t0, 1)
    (HERE / "FINDINGS.json").write_text(json.dumps(out, indent=1))

    print("| experiment | a screen ctx | c label/BASE | d max-of-cached | h genomes |")
    print("|---|---|---|---|---|")
    for r in rows:
        c = r["checks"]
        f = lambda k: ABBR.get(c[k]["verdict"], c[k]["verdict"])  # noqa: E731
        print("| %s (%s) | %s | %s | %s | %s |" % (r["experiment"], r["script"], f("a_screen_context"),
                                                 f("c_label_write_back"), f("d_max_of_cached"), f("h_stores_genomes")))
    print()
    for k, v in extra.items():
        print(k, "->", v["verdict"], "|", v["reason"][:200])
    tally = {}
    for r in rows:
        for k, c in r["checks"].items():
            tally.setdefault(k, {}).setdefault(c["verdict"], 0)
            tally[k][c["verdict"]] += 1
    print(json.dumps(tally, indent=1))
    print("cpu_s", out["cpu_s"], "utc", utc)


if __name__ == "__main__":
    main()
