"""W2-34 Q4: apply W2-27 reading (b) -- the condition must hold at the FINAL checkpoint -- to X-A3-SFLINEAGE and X-DD-ESTABLISH.
Read-only over committed results. python -B q4_reading_b.py -> q4_reading_b.json"""
import json, pathlib, collections
HERE = pathlib.Path(__file__).resolve().parent
C = HERE.parents[1] / "campaigns"
out = {}
# ---- X-A3-SFLINEAGE (run_sfl.py): per run, at the last checkpoint with free > 0, free_in_L/free >= 0.8; SIGNAL iff >= 3 such runs
sfl = []
for p in sorted((C / "npe-arc3-2026-09-28/x_a3_sflineage/results").glob("*.json")):
    r = json.loads(p.read_text())
    cps = r["checkpoints"]
    d0n = bool(r["d0_free"]) and not any(r["d0_free"])
    last = next((c for c in reversed(cps) if c["free"] > 0), None)
    fin = cps[-1]
    first = next((i for i, c in enumerate(cps) if c["free"] > 0 and c["free_in_L"] >= 0.8 * c["free"]), None)
    coded = d0n and last is not None and last["free_in_L"] >= 0.8 * last["free"]
    b = d0n and fin["free"] > 0 and fin["free_in_L"] >= 0.8 * fin["free"]
    cmaj = (d0n and first is not None and
            sum(c["free"] > 0 and c["free_in_L"] >= 0.8 * c["free"] for c in cps[first:]) > len(cps[first:]) / 2)
    every = d0n and first is not None and all(c["free"] > 0 and c["free_in_L"] >= 0.8 * c["free"] for c in cps[first:])
    sfl.append({"run": p.stem, "d0_all_not_free": d0n, "last_free_epoch": last["epoch"] if last else None, "final_epoch": fin["epoch"],
                "final": [fin["L_share"], fin["competent"], fin["free"], fin["free_in_L"]], "coded": coded, "b_final": b,
                "c_majority_from_first": cmaj, "every_cp_from_first": every})
cnt = lambda k: sum(x[k] for x in sfl)
out["SFLINEAGE"] = {"per_run": sfl, "within_counts": {k: cnt(k) for k in ("coded", "b_final", "c_majority_from_first", "every_cp_from_first")},
                    "verdict_coded": "SIGNAL" if cnt("coded") >= 3 else "not SIGNAL",
                    "verdict_b": "SIGNAL" if cnt("b_final") >= 3 else "not SIGNAL"}
# ---- X-DD-ESTABLISH (run_de.py): verdict = mode shares over STALLED runs; ESTABLISHED = world depth >= 20 (historical).
# 'last_competent_member' is the run's "last checkpoint with" field (reported, not verdict-bearing).
de = [json.loads(p.read_text()) for p in sorted((C / "npe-w1-donor-discovery-2026-09-26/x_dd_establish/results").glob("*.json"))]
FINAL = 2000
est = [r for r in de if r["status"] == "ESTABLISHED"]
stalled = [r for r in de if r["status"] not in ("ESTABLISHED", "NO_D0")]
coded = collections.Counter(r["status"] for r in stalled)


def mode(r):
    return ("NO_COPY" if r["lineage_births"] == 0 else "INCOMPETENT_COPIES" if r["competent_nonD0_first"] is None
            else "LOST_COMPETENT")


# reading (b): ESTABLISHED only if the D0 causal lineage still has a live competent member at the final check
est_b = [r for r in est if r["last_competent_member"] == FINAL]
moved = [r for r in est if r["last_competent_member"] != FINAL]
stalled_b = collections.Counter(coded)
for r in moved:
    stalled_b[mode(r)] += 1
nb = sum(stalled_b.values())
topb = max(stalled_b.values()) / nb
cls = lambda top: "SIGNAL" if top >= 0.7 else "CLEAN_NULL" if top < 0.4 else "WEAK_SIGNAL"
out["DD_ESTABLISH"] = {
    "n": len(de), "established_coded": len(est), "stalled_coded": dict(coded),
    "top_share_coded": round(max(coded.values()) / len(stalled), 4), "verdict_coded": cls(max(coded.values()) / len(stalled)),
    "established_lcm_values": sorted((r["last_competent_member"] or -1) for r in est),
    "established_with_lineage_births_0": sum(r["lineage_births"] == 0 for r in est),
    "established_with_competent_member_at_final": len(est_b),
    "stalled_competent_member_at_final": sum(r["last_competent_member"] == FINAL for r in stalled),
    "reading_b_relabel_established": {"moved_modes": dict(collections.Counter(mode(r) for r in moved)),
                                      "stalled_modes": dict(stalled_b), "top_share": round(topb, 4), "verdict": cls(topb)},
    "note": "ESTABLISHED is world causal depth >= 20 (any lineage, historical), not D0-lineage persistence; the verdict's "
            "modes are 'ever' events; only last_competent_member is a 'last checkpoint with' field and it is not verdict-bearing."}
(HERE / "q4_reading_b.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
