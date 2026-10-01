"""W2-AH: list the C1 economy-transect rows (B, B2) for RELAY and MAJ with physics/env and recorded plant acc."""
import gzip, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[6]
rows = [json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
keys = ("topology", "n_sites", "radius", "dest_mode", "fanout", "update_mode", "update_period", "update_p",
        "lat_base", "lat_hop", "lat_jitter", "loss", "dup", "cap", "collision", "decay_shift", "prog_len",
        "state_dim", "channels", "payload_width", "rules", "noise", "e_income", "e_max", "c_emit", "c_op", "c_mem")
for r in rows:
    if r["wave"] not in ("B", "B2") or r["extra"].get("transect") != "economy": continue
    if r["env"]["family"] not in ("RELAY", "MAJ"): continue
    ph = r["physics"]
    print(r["wave"], r["kind"], r["extra"].get("track"), r["env"]["family"], "b%s" % r["extra"]["base"], "li", r["extra"]["level_index"],
          "rep", r["extra"].get("rep", 0), r["levels"].get("economy"), "plant", r["result"]["plant"]["acc"],
          "held", r["result"].get("held", {}).get("acc"), r["cell_id"][:8])
seen = set()
for r in rows:
    if r["wave"] not in ("B",) or r["extra"].get("transect") != "economy": continue
    if r["env"]["family"] not in ("RELAY", "MAJ"): continue
    k = (r["env"]["family"], r["extra"]["base"])
    if k in seen: continue
    seen.add(k)
    print(k, {x: r["physics"][x] for x in keys}, r["env"])
