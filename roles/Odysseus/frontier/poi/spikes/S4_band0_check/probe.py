"""S4 BAND0 check: independent recomputation from archaeon/envgate2/RESULTS.json (stdlib only).
Run from repo root:  python3 roles/Odysseus/frontier/poi/spikes/S4_band0_check/probe.py
Writes band0_check.json next to this file."""
import hashlib, json, statistics, subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
E2 = ROOT / "archaeon" / "envgate2"
OUT = Path(__file__).resolve().parent / "band0_check.json"
BAND = set(range(120, 136))                                   # mechanism.py:26
ARMS = ["U", "RRIGHT", "RWEAK", "R128", "BAND0"]
OPEN = {"U": BAND, "RRIGHT": {128, 129, 130, 131}, "RWEAK": {125, 126, 127, 128}, "R128": {128}, "BAND0": set()}  # PREREG spec.arms
FILES = ["archaeon/envgate2/RESULTS.json", "archaeon/envgate2/analyze.py", "archaeon/envgate2/mechanism.py", "archaeon/envgate2/PREREG.json",
         "archaeon/envgate2/OPS_LOG.jsonl", "archaeon/lineage/core.py", "archaeon/lineage/assay_block.py",
         "archaeon/envgate2/VERDICT_2026-09-26.md", "archaeon/envgate2/ENVGATE_CLOSURE_2026-09-26.md", "ops/threads/TH-001.md",
         "roles/Odysseus/frontier/poi/raw/I1_z80_lineage_worlds.md"]


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


R = json.loads((E2 / "RESULTS.json").read_text(encoding="utf-8"))
rows = R["established_glins"]
# --- consistency with frozen per_block
cnt = defaultdict(int)
for x in rows: cnt[(x["block"], x["arm"])] += 1
per_block_ok = all(cnt[(int(b), a)] == n for b, d in R["per_block"].items() for a, n in d.items())

# --- arrival -> arms in which it established (same block); arrivals are paired across arms (pairing_sha256)
est_arms = defaultdict(set); tapes = defaultdict(set)
for x in rows: est_arms[(x["block"], x["arrival"])].add(x["arm"]); tapes[(x["block"], x["arrival"])].add(x["tape"])


def gate_rel(ex):
    if not ex: return "NO_EXACT_GATE"
    s = set(ex)
    if len(s) == 256: return "UNGATED_ALL_256"
    if s <= BAND: return "GATE_IN_BAND"
    if not (s & BAND): return "GATE_OUTSIDE_BAND"
    return "GATE_MIXED"


def row(x):
    k = (x["block"], x["arrival"]); arms = sorted(est_arms[k], key=ARMS.index)
    ex = x["ruler_exact_inputs"] or []
    return {"block": x["block"], "arm": x["arm"], "glin": x["glin"], "arrival": x["arrival"], "tape12": x["tape"][:12], "ruler_class": x["ruler_class"],
            "gate": gate_rel(ex), "exact_inputs": ex if len(ex) < 256 else "all 256", "first_birth_input": x["first_birth_input"],
            "fbi_in_band": x["first_birth_input"] in BAND, "fbi_in_arm_open_set": x["first_birth_input"] in OPEN[x["arm"]],
            "peak": x["peak"], "births": x["births"], "max_ggen": x["max_ggen"], "last_alive": x["last_alive"],
            "established_in_arms": arms, "n_arms": len(arms), "tapes_identical_across_arms": len(tapes[k]) == 1}


band0 = [row(x) for x in rows if x["arm"] == "BAND0"]
allrows = [row(x) for x in rows]

# --- window-dependence counts under several explicit definitions
defs = {}
for a in ARMS:
    A = [r for r in allrows if r["arm"] == a]
    d1 = [r for r in A if r["n_arms"] == 1]                                     # D1 arm-unique (delegate's operationalisation)
    d2 = [r for r in A if "BAND0" not in r["established_in_arms"]]              # D2 not also established in BAND0 same block
    # D3: not in BAND0 AND (first-birth input in the arm's open set OR exact gate lies in the arm's open set)
    d3 = [r for r in d2 if r["fbi_in_arm_open_set"] or (r["gate"] == "GATE_IN_BAND" and set(r["exact_inputs"]) & OPEN[a])]
    d4 = [r for r in d2 if r["fbi_in_arm_open_set"]]                            # D4: not in BAND0 AND first-birth input in open set
    defs[a] = {"total": len(A), "D1_arm_unique": len(d1), "D2_not_in_BAND0": len(d2), "D3_notBAND0_and_(input_or_gate_in_open_set)": len(d3),
               "D4_notBAND0_and_input_in_open_set": len(d4),
               "D2_minus_D3_rows": [(r["block"], r["arrival"], r["ruler_class"], r["gate"], r["first_birth_input"]) for r in d2 if r not in d3]}

# --- block wall times from OPS_LOG (submit -> block_done)
s = {}; d = {}
for l in (E2 / "OPS_LOG.jsonl").read_text(encoding="utf-8").splitlines():
    e = json.loads(l); t = datetime.fromisoformat(e["t"].replace("Z", "+00:00")) if "t" in e else None
    if e["event"] == "submit": s[e["block"]] = t
    if e["event"] == "block_done": d[e["block"]] = t
wall = {b: round((d[b] - s[b]).total_seconds() / 3600, 2) for b in s}
slow = sorted(wall, key=lambda b: -wall[b])[:3]

# --- blocks where non-U establishments fall
nonU_blocks = defaultdict(int)
for r in allrows:
    if r["arm"] != "U": nonU_blocks[r["block"]] += 1
inv = sorted({(r["block"], r["arrival"]) for r in allrows if r["n_arms"] >= 4})

out = {"inputs": {f: {"last_commit": git("log", "-1", "--format=%H", "--", f), "sha256": hashlib.sha256((ROOT / f).read_bytes()).hexdigest()} for f in FILES},
       "head": git("rev-parse", "HEAD"), "per_block_consistent_with_established_glins": per_block_ok, "n_rows": len(rows),
       "totals": {a: sum(1 for r in allrows if r["arm"] == a) for a in ARMS},
       "band0_establishments": band0, "arm_invariant_arrivals_(>=4_arms)": inv,
       "window_dependence_by_definition": defs, "block_wall_h": wall, "median_wall_h": round(statistics.median(wall.values()), 2),
       "slowest3": slow, "nonU_establishments_by_block": dict(sorted(nonU_blocks.items())),
       "frozen_takeover_worlds": R["takeover_worlds"], "frozen_establishments_in_takeover_worlds": R["establishments_in_takeover_worlds"]}
OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
print(json.dumps({k: out[k] for k in ("per_block_consistent_with_established_glins", "totals", "arm_invariant_arrivals_(>=4_arms)", "slowest3", "median_wall_h", "nonU_establishments_by_block")}))
for r in band0: print({k: r[k] for k in ("block", "arrival", "tape12", "ruler_class", "gate", "first_birth_input", "peak", "births", "established_in_arms")})
for a in ARMS: print(a, {k: v for k, v in defs[a].items()})
