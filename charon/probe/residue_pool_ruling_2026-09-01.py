"""Charon - the measurements behind RULINGS_2026-09-01 ruling 1.

Ruling request: ergon/probe/FINDING_pooled_population_single_block_residue_2026-08-30 section 4.
Ergon offers three forms for the D0 residue pool and declares himself the conflicted party.
The request assumes the pools are clean and asks only how to combine them. This probe tests
that assumption too, so the ruling stands on a measured pool rather than a described one.

Ergon's own loader and selector are IMPORTED, never re-derived - recomputing a selection in a
second place is the seam error this campaign keeps committing (ATK-013). Read-only: this probe
opens no ledger for writing and makes no network call.

INSTRUMENT ERROR FOUND IN THIS PROBE AND FIXED BEFORE ANYTHING WAS FILED
  The first build keyed residue records by `ledger_id#seq`, which is what build_f_null itself
  uses. Both blocks load under ledger_id "p1_prepass" and `seq` is the line index WITHIN each
  file, so that key collides on 200 of block A's 206 records against block B. Two consequences:
  the contamination counts were inflated (block A appeared to draw 35 distinct fabricating
  records from a pool holding 6), and the control-rewrite count was deflated (a block A pick
  and a block B pick sharing a seq compared equal, i.e. read as "unchanged"). Both are fixed
  here by keying on (block, ledger_id, seq). The collision itself is then reported as
  measurement M5, because it is not only my bug - see the ruling.

MEASUREMENTS
  M1 pool census, per block, ledger rows vs pool records
  M2 contamination: residue records manufactured from transport failures, and how often each
     pooling form draws one into the F-NULL control
  M3 control rewrite: does form (a) change an already-rendered block's F-NULL selection
  M4 stability: does F-NULL selection survive growth of its OWN block's pool
  M5 record identity: the collision above, in the campaign's own code path
  M6 the resolution of merge rule section 3.2's pooling criterion

PREDICATES, kept separate because they count different things:
  transport_failed  a rep-1 LEDGER ROW with status != "ok" or empty attempt_text
  fabricating       a POOL RECORD whose rendered body is method_projection("") - the token
                    "(prior attempt recorded no recognizable method vocabulary)", which asserts
                    to the solver that an attempt was made and used no recognisable method
"""
import collections
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ergon.probe.assemble import load_prepass, select_residue
from ergon.probe.f_null import select_mismatched

SEED = 20260821                     # campaign.SEED, as build_f_null is actually called
FAB = "(prior attempt recorded no recognizable method vocabulary)"
PATHS = {"A": ROOT / "ergon/probe/ledgers/campaign/p1_prepass.jsonl",
         "B": ROOT / "ergon/probe/ledgers/campaign_blockB/p1_prepass.jsonl"}
PREFIX = {"A": "nearmiss_mix-M30-", "B": "nearmiss_mixB-M30-"}
SNAPS = ["dbaa9404b", "32e38d970"]  # committed states of block A's prepass, for M4

#: The campaign's own key, which is what build_f_null uses to decide which records shipped.
def ergon_key(r):
    return f"{r.ledger_id}#{r.seq}"


def block_of(rec):
    u = str(rec.uid or "")
    if u.startswith(PREFIX["B"]):
        return "B"
    return "A" if u.startswith(PREFIX["A"]) else "?"


#: Charon's key. Block-qualified, so it is an identity rather than a line number.
def key(r):
    return f"{block_of(r)}:{r.ledger_id}#{r.seq}"


def load(path):
    return load_prepass(path, ledger_id="p1_prepass", withhold_prose=True)


def m1_census(path, pool, uids):
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    r1 = [d for d in rows if d["key"][0] == 1]
    by = collections.defaultdict(list)
    for d in r1:
        by[d["key"][1]].append(d)

    def bad(d):
        return d.get("status") != "ok" or not (d.get("attempt_text") or "").strip()

    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256_16": hashlib.sha256(path.read_bytes()).hexdigest()[:16],
        "raw_lines": len(rows), "rep1_rows": len(r1), "distinct_uids": len(by),
        "rep1_status_census": dict(collections.Counter(d.get("status") for d in r1)),
        "transport_failed_rep1_rows": sum(1 for d in r1 if bad(d)),
        "uids_whose_ONLY_rep1_row_is_transport_failed":
            len([u for u, v in by.items() if all(bad(d) for d in v)]),
        "uids_carrying_both_a_failed_row_and_a_real_one":
            len([u for u, v in by.items()
                 if any(bad(d) for d in v) and not all(bad(d) for d in v)]),
        "pool_rep1_records": len(pool),
        "pool_fabricating_records": sum(1 for r in pool if r.body.strip() == FAB),
        "tasks_whose_F_PROM_ships_more_than_one_record":
            sum(1 for u in uids if len(select_residue(pool, stratum="D0", target_uid=u)) > 1),
    }


def null_pick(uid, own_pool, draw_pool):
    prom = select_residue(own_pool, stratum="D0", target_uid=uid)
    if not prom:
        return None
    return select_mismatched(prom, draw_pool, seed=SEED, strategy="matched")


def m2_draws(uids, own_pool, draw_pool, fab_keys):
    hit, n, per = 0, 0, collections.Counter()
    for uid in uids:
        sel = null_pick(uid, own_pool, draw_pool)
        if sel is None:
            continue
        n += 1
        got = [key(r) for r in sel if key(r) in fab_keys]
        if got:
            hit += 1
            per.update(got)
    return {"tasks": n, "tasks_drawing_a_fabricating_record": hit,
            "share": round(hit / n, 4) if n else None,
            "distinct_fabricating_records_drawn": len(per),
            "max_times_one_record_served_as_the_null": max(per.values(), default=0)}


def m3_rewrite(uids, own_pool, union, own_label):
    changed = other = reorder = n = 0
    for uid in uids:
        own = null_pick(uid, own_pool, own_pool)
        uni = null_pick(uid, own_pool, union)
        if own is None:
            continue
        n += 1
        if [key(r) for r in own] != [key(r) for r in uni]:
            changed += 1
            if any(block_of(r) != own_label for r in uni):
                other += 1
            else:
                reorder += 1
    return {"tasks": n, "n_F_NULL_selection_changed": changed,
            "changed_share": round(changed / n, 4) if n else None,
            "composition_effect_drew_from_the_other_block": other,
            "reordering_artifact_same_block_different_record_no_new_record_involved": reorder}


def m4_stability(scratch):
    snaps = []
    for c in SNAPS:
        txt = subprocess.run(
            ["git", "show", f"{c}:ergon/probe/ledgers/campaign/p1_prepass.jsonl"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
        p = scratch / f"p1_prepass_{c}.jsonl"
        p.write_text(txt, encoding="utf-8")
        snaps.append((c, p))
    snaps.append(("live", PATHS["A"]))
    states = []
    for name, p in snaps:
        pool = load(p)
        picks = {}
        for uid in sorted({str(r.uid) for r in pool if r.uid}):
            sel = null_pick(uid, pool, pool)
            if sel is not None:
                picks[uid] = [key(r) for r in sel]
        states.append({"snapshot": name,
                       "sha256_16": hashlib.sha256(p.read_bytes()).hexdigest()[:16],
                       "raw_lines": sum(1 for _ in p.open(encoding="utf-8")),
                       "rep1_records": len(pool), "picks": picks})
    comps = []
    for a, b in zip(states, states[1:]):
        shared = sorted(set(a["picks"]) & set(b["picks"]))
        ch = [u for u in shared if a["picks"][u] != b["picks"][u]]
        a_all = set().union(*[set(v) for v in a["picks"].values()]) if a["picks"] else set()
        b_all = set().union(*[set(v) for v in b["picks"].values()]) if b["picks"] else set()
        newk = b_all - a_all
        to_new = [u for u in ch if set(b["picks"][u]) & newk]
        comps.append({"from": a["snapshot"], "to": b["snapshot"],
                      "rep1_records": f'{a["rep1_records"]} -> {b["rep1_records"]}',
                      "tasks_servable_in_both": len(shared),
                      "n_F_NULL_selection_changed": len(ch),
                      "changed_share": round(len(ch) / len(shared), 4) if shared else None,
                      "of_those_that_selected_a_NEWLY_ADDED_record": len(to_new),
                      "of_those_that_selected_a_PRE_EXISTING_record": len(ch) - len(to_new)})
    return {"snapshots": [{k: v for k, v in s.items() if k != "picks"} for s in states],
            "consecutive": comps}


def m5_identity(pools, union):
    ka = {ergon_key(r) for r in pools["A"]}
    kb = {ergon_key(r) for r in pools["B"]}
    return {
        "campaign_key_is": ("ledger_id#seq  (build_f_null: shipped = [r for r in records if "
                            "f'{r.ledger_id}#{r.seq}' in kept])"),
        "ledger_id_values": {k: sorted({r.ledger_id for r in v}) for k, v in pools.items()},
        "campaign_keys_A": len(ka), "campaign_keys_B": len(kb),
        "campaign_keys_COLLIDING_across_blocks": len(ka & kb),
        "record_id_distinct_A": len({r.record_id for r in pools["A"]}),
        "record_id_total_A": len(pools["A"]),
        "record_id_distinct_B": len({r.record_id for r in pools["B"]}),
        "record_id_total_B": len(pools["B"]),
        "record_id_colliding_across_blocks":
            len({r.record_id for r in pools["A"]} & {r.record_id for r in pools["B"]}),
        "charon_keys_colliding_across_blocks":
            len({key(r) for r in pools["A"]} & {key(r) for r in pools["B"]}),
        "union_records": len(union),
        "union_distinct_campaign_keys": len({ergon_key(r) for r in union}),
        "union_distinct_charon_keys": len({key(r) for r in union}),
    }


def m6_resolution():
    m = json.loads((ROOT / "ergon/probe/ledgers/campaign/block_merge.json").read_text("utf-8"))
    a, b = m["block_A"], m["block_B"]
    ha = (a["manifest_interval_95"][1] - a["manifest_interval_95"][0]) / 2
    hb = (b["manifest_interval_95"][1] - b["manifest_interval_95"][0]) / 2
    obs = abs(a["point_estimate"] - b["point_estimate"])
    scale = 0.5225 - 0.4900        # heuristic floor vs solver, the live effect scale
    return {"criterion": "merge rule 3.2 cond. 3 - the two blocks' 95% intervals overlap",
            "half_width_A": round(ha, 4), "half_width_B": round(hb, 4),
            "largest_block_difference_the_criterion_still_permits": round(ha + hb, 4),
            "observed_block_difference": round(obs, 4),
            "observed_as_share_of_what_is_permitted": round(obs / (ha + hb), 4),
            "live_effect_scale_heuristic_floor_minus_solver": round(scale, 4),
            "permitted_difference_in_units_of_that_effect": round((ha + hb) / scale, 2)}


def main():
    scratch = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "charon/probe/_scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    pools = {k: load(p) for k, p in PATHS.items()}
    union = list(pools["A"]) + list(pools["B"])
    uids = {k: sorted({str(r.uid) for r in v}) for k, v in pools.items()}
    fab_keys = {key(r) for r in union if r.body.strip() == FAB}

    out = {
        "probe": "charon/probe/residue_pool_ruling_2026-09-01.py",
        "ruling": "charon/probe/RULINGS_2026-09-01.md ruling 1",
        "question": "ergon/probe/FINDING_pooled_population_single_block_residue_2026-08-30 s4",
        "stratum": "D0", "null_strategy": "matched (STRATEGY_BY_STRATUM['D0'])", "seed": SEED,
        "M1_pool_census": {k: m1_census(PATHS[k], pools[k], uids[k]) for k in PATHS},
        "M2_contamination": {
            "fabricating_records_in_union_pool": len(fab_keys),
            "form_b_and_c_block_scoped_pools": {
                "block_A_tasks_draw_from_A":
                    m2_draws(uids["A"], pools["A"], pools["A"], fab_keys),
                "block_B_tasks_draw_from_B":
                    m2_draws(uids["B"], pools["B"], pools["B"], fab_keys)},
            "form_a_one_pooled_pool": {
                "block_A_tasks_draw_from_AuB":
                    m2_draws(uids["A"], pools["A"], union, fab_keys),
                "block_B_tasks_draw_from_AuB":
                    m2_draws(uids["B"], pools["B"], union, fab_keys)},
            "note": ("forms (b) and (c) draw from the same block-scoped pools and so carry the "
                     "same contamination; the three forms differ in how the STATISTIC is "
                     "combined, not in what the pool contains")},
        "M3_control_rewrite_under_form_a": {
            "block_A": m3_rewrite(uids["A"], pools["A"], union, "A"),
            "block_B": m3_rewrite(uids["B"], pools["B"], union, "B")},
        "M4_stability_under_own_block_growth": m4_stability(scratch),
        "M5_record_identity": m5_identity(pools, union),
        "M6_pooling_criterion_resolution": m6_resolution(),
    }
    dest = ROOT / "charon/probe/residue_pool_ruling_2026-09-01.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
