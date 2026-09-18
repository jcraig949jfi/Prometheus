"""HARM-13 (Harmonia #413): per-detector exchangeability class table on the live corpus.

    ARCHAEON_SFE_DB=<ledger> python -m archaeon.producer.exchangeability_table [--lookback 2000] [--out-dir archaeon/docs/h0h5]

For D1, D2, D4, D5 and D6: the detector's own eligibility (its detect() is CALLED, never
re-derived), and for every eligible grain the record Harmonia's diagnostic returns on the
grain's rows in committed_seq order (roles/Harmonia/qualification/h0h5/exchangeability.py,
imported; its cut is never re-derived here). D3 is what the D3 dossier already covers.

Grain membership is the one thing detect() does not export, so it is MIRRORED here from each
detector's own cell construction, with the source line cited on every grain kind. A mirror is a
claim about another function; the eligible_units count from detect() is printed beside the
number of grains this mirror produced, and a mismatch is reported, not hidden.

The corpus identity is printed FIRST (ledger path, engine_instance_id from meta, schema,
corpus_hash, tenancy window): the 2026-09-10 identity (M1 ledger eng_8a37a5d3) is not reachable
from M2, so this table is on whatever ledger the environment names.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import itertools
import json
import os
import sqlite3
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
HARMONIA = REPO / "roles" / "Harmonia" / "qualification" / "h0h5"
if str(HARMONIA) not in sys.path:
    sys.path.insert(0, str(HARMONIA))

from archaeon import config as cfg, fossils, stats, workspace                       # noqa: E402
from archaeon.detectors import (d1_repeated_deviation as D1, d2_sign_instability as D2,  # noqa: E402
                                d4_order_reversal as D4, d5_outlier_region as D5, d6_boundary_hint as D6)
from archaeon.detectors.base import mad, mean                                        # noqa: E402
import exchangeability as EX                                                         # noqa: E402

DETECTORS = {"D1": D1, "D2": D2, "D4": D4, "D5": D5, "D6": D6}


def _blob_hash(path: Path) -> str:
    r = subprocess.run(["git", "-C", str(REPO), "hash-object", str(path)], capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def _ledger_identity(path: str) -> dict:
    cx = sqlite3.connect("file:%s?mode=ro" % path.replace("?", "%3f"), uri=True)
    try:
        meta = dict(cx.execute("SELECT key, value FROM meta").fetchall())
        n = {t: cx.execute("SELECT count(*) FROM %s" % t).fetchone()[0] for t in ("observations", "experiments", "worlds", "clients")}
        # what the chart WOULD have read, by client and evidence class: the metric field
        # (content.score / content.result.score) and the coordinate (spec.candidate) presence
        census = [{"client": r[0], "evidence_class": r[1], "n": r[2], "with_score_metric": r[3], "with_spec_candidate": r[4]}
                  for r in cx.execute(
                      "SELECT cl.name, o.evidence_class, count(*), "
                      " sum(CASE WHEN json_extract(o.content,'$.score') IS NOT NULL OR json_extract(o.content,'$.result.score') IS NOT NULL THEN 1 ELSE 0 END), "
                      " sum(CASE WHEN json_extract(e.spec,'$.candidate') IS NOT NULL THEN 1 ELSE 0 END) "
                      "FROM observations o JOIN experiments e ON e.exp_id=o.exp_id JOIN worlds w ON w.world_id=o.world_id "
                      "JOIN clients cl ON cl.client_id=w.client_id GROUP BY 1,2 ORDER BY 3 DESC")]
    finally:
        cx.close()
    return {"path": path, "engine_instance_id": meta.get("engine_instance_id"), "schema_version": meta.get("schema_version"),
            "table_counts": n, "census_by_client_and_evidence_class": census,
            "census_note": "rows the chart could admit need evidence_class ENGINE_WORK_RESULT, an admitted client name, a score metric and a spec.candidate coordinate"}


def _rec(rows) -> dict:
    """Harmonia's record on the grain's rows in committed_seq order (the dossier row shape)."""
    seq = sorted(rows, key=lambda r: (int(r.anchors["committed_seq"]), r.row_id))
    return EX.diagnose_rows([{"anchors": {"committed_seq": r.anchors["committed_seq"]}, "metric": r.metric} for r in seq]).as_dict()


def _ids(rows) -> List[str]:
    return [r.row_id for r in sorted(rows, key=lambda r: (int(r.anchors["committed_seq"]), r.row_id))]


# ---------------------------------------------------------------- grain mirrors
def grains_d1(corpus, dcfg) -> List[dict]:
    """Mirror of d1_repeated_deviation.detect: cells (family, player, region) with
    n >= d1_min_runs whose attainable effect floor <= d1_max_effect_sd."""
    if corpus.chart.player_field is None:
        return []
    cells: Dict[Tuple[str, str, str], List] = defaultdict(list)
    for r in corpus.rows:
        cells[(r.family or "<nofamily>", r.player, r.region)].append(r)
    out = []
    for k, v in sorted(cells.items(), key=lambda kv: str(kv[0])):
        if len(v) < dcfg.d1_min_runs:
            continue
        if stats.attainable_effect_floor(dcfg.d1_min_t, len(v)) > dcfg.d1_max_effect_sd:
            continue
        out.append({"grain": "%s|%s|%s" % k, "kind": "cell(family,player,region)", "n": len(v), "row_ids": _ids(v), "record": _rec(v)})
    return out


def _pr_cells(corpus, min_runs: int):
    pr: Dict[Tuple[str, str], List] = defaultdict(list)
    for r in corpus.rows:
        pr[(r.player, r.region)].append(r)
    return {k: v for k, v in pr.items() if len(v) >= min_runs}


def grains_d2(corpus, dcfg) -> List[dict]:
    """Mirror of d2_sign_instability.detect: neighbour region pairs (normalized centroid
    distance <= d2_neighbor_radius) sharing two players each supported by d2_min_runs; the
    record for EACH side (player, region) of each pair."""
    if corpus.chart.player_field is None or not corpus.chart.coord_fields or not corpus.rows:
        return []
    scales = corpus.coord_scales()
    reg_coords: Dict[str, List[Dict[str, float]]] = defaultdict(list)
    for r in corpus.rows:
        reg_coords[r.region].append(corpus.normalized_coords(r, scales))
    centroid = {}
    for reg, cs in reg_coords.items():
        acc: Dict[str, List[float]] = {}
        for c in cs:
            for k, v in c.items():
                acc.setdefault(k, []).append(v)
        centroid[reg] = {k: mean(v) for k, v in acc.items()}
    supported = _pr_cells(corpus, dcfg.d2_min_runs)
    players_of: Dict[str, set] = defaultdict(set)
    for (p, reg) in supported:
        players_of[reg].add(p)
    out = []
    for r1, r2 in itertools.combinations(sorted(centroid), 2):
        d = D2._dist(centroid[r1], centroid[r2])
        if d is None or d > dcfg.d2_neighbor_radius:
            continue
        shared = sorted(players_of[r1] & players_of[r2])
        for a, b in itertools.combinations(shared, 2):
            for side in ((a, r1), (a, r2), (b, r1), (b, r2)):
                rows = supported[side]
                out.append({"grain": "pair(%s,%s)x(%s,%s)|side %s@%s" % (r1, r2, a, b, side[0], side[1]), "kind": "pair-side(player,region)",
                            "n": len(rows), "row_ids": _ids(rows), "record": _rec(rows)})
    return out


def grains_d4(corpus, dcfg) -> List[dict]:
    """Mirror of d4_order_reversal.detect: same-family region pairs sharing two players each
    supported by d4_min_runs; the record for EACH side."""
    if corpus.chart.player_field is None or not corpus.rows:
        return []
    supported = _pr_cells(corpus, dcfg.d4_min_runs)
    fam_of = {r.region: (r.family or "<nofamily>") for r in corpus.rows}
    players_of: Dict[str, set] = defaultdict(set)
    for (p, reg) in supported:
        players_of[reg].add(p)
    by_family: Dict[str, set] = defaultdict(set)
    for reg, fam in fam_of.items():
        by_family[fam].add(reg)
    out = []
    for fam, regs in sorted(by_family.items()):
        for r1, r2 in itertools.combinations(sorted(regs), 2):
            shared = sorted(players_of[r1] & players_of[r2])
            for a, b in itertools.combinations(shared, 2):
                for side in ((a, r1), (a, r2), (b, r1), (b, r2)):
                    rows = supported[side]
                    out.append({"grain": "%s:pair(%s,%s)x(%s,%s)|side %s@%s" % (fam, r1, r2, a, b, side[0], side[1]), "kind": "pair-side(player,region)",
                                "n": len(rows), "row_ids": _ids(rows), "record": _rec(rows)})
    return out


def grains_d5(corpus, dcfg) -> List[dict]:
    """Mirror of d5_outlier_region.detect: cells (family, region, coords binned at
    d5_coord_bin) with n >= d5_min_repeats inside families with n >= d5_min_family_n and MAD > 0."""
    scales = corpus.coord_scales()
    fam_rows: Dict[str, List] = defaultdict(list)
    for r in corpus.rows:
        fam_rows[r.family or "<nofamily>"].append(r)

    def cell_key(r):
        nc = corpus.normalized_coords(r, scales)
        binned = tuple(sorted((k, round(v / dcfg.d5_coord_bin) * dcfg.d5_coord_bin) for k, v in nc.items()))
        return (r.family or "<nofamily>", r.region, binned)

    cells: Dict[Any, List] = defaultdict(list)
    for r in corpus.rows:
        cells[cell_key(r)].append(r)
    big = {f for f, rs in fam_rows.items() if len(rs) >= dcfg.d5_min_family_n}
    usable = {f for f in big if mad([r.metric for r in fam_rows[f]]) > 0}
    out = []
    for k, v in sorted(cells.items(), key=lambda kv: str(kv[0])):
        if k[0] in usable and len(v) >= dcfg.d5_min_repeats:
            out.append({"grain": "%s|%s|%s" % (k[0], k[1], json.dumps(k[2])), "kind": "cell(family,region,coord-bin)", "n": len(v),
                        "row_ids": _ids(v), "record": _rec(v)})
    return out


def grains_d6(corpus, dcfg) -> List[dict]:
    """Mirror of d6_boundary_hint.detect: per live axis, bins of width BIN_WIDTH over normalized
    coordinates with n >= d6_min_n_side; the record for each BIN."""
    if not corpus.chart.coord_fields or not corpus.rows:
        return []
    scales = corpus.coord_scales()
    live = [a for a in corpus.chart.coord_fields if (scales.get(a, {}).get("span") or 0) > 0]
    out = []
    for axis in live:
        bins: Dict[float, List] = defaultdict(list)
        for r in corpus.rows:
            nc = corpus.normalized_coords(r, scales)
            if axis in nc:
                bins[round(nc[axis] / D6.BIN_WIDTH) * D6.BIN_WIDTH].append(r)
        for b in sorted(bins):
            if len(bins[b]) >= dcfg.d6_min_n_side:
                out.append({"grain": "%s@%.2f" % (axis, b), "kind": "axis-bin", "n": len(bins[b]), "row_ids": _ids(bins[b]), "record": _rec(bins[b])})
    return out


MIRRORS = {"D1": grains_d1, "D2": grains_d2, "D4": grains_d4, "D5": grains_d5, "D6": grains_d6}
CONFIG_KEYS = {"D1": ("d1_min_runs", "d1_min_t", "d1_max_effect_sd", "d1_consistency_blocks"),
               "D2": ("d2_min_runs", "d2_neighbor_radius"), "D4": ("d4_min_runs", "d4_min_margin_sd"),
               "D5": ("d5_min_repeats", "d5_min_family_n", "d5_coord_bin"), "D6": ("d6_min_n_side", "d6_min_steps_for_trend")}


def build(lookback: int, chart_name: str) -> dict:
    ws = workspace.assert_not_canonical("HARM-13 exchangeability table")
    corpus = fossils.read(chart_name, lookback_rows=lookback)
    path = str(corpus.source_ref)
    ident = {"ledger": _ledger_identity(path) if os.path.exists(path) else {"path": path, "error": "absent"},
             "chart": corpus.chart.name, "lookback_rows": lookback, "corpus_hash": corpus.corpus_hash if isinstance(corpus.corpus_hash, str) else corpus.corpus_hash(),
             "rows": len(corpus.rows), "window": corpus.window,
             "note_2026_09_10_identity": "the 2026-09-10 corpus (M1 ledger eng_8a37a5d3, archive on SKULLPORT) is not reachable from M2; "
                                         "this table is on the ledger named above (printed first, per #413)"}
    dcfg = cfg.DEFAULT.detectors if hasattr(cfg.DEFAULT, "detectors") else cfg.DEFAULT
    out = {"schema": "archaeon.exchangeability_table.v1", "written": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "for": "Harmonia HARM-13 (#413)", "diagnostic": {"module": "roles/Harmonia/qualification/h0h5/exchangeability.py", "version": EX.EX_VERSION,
                                                           "blob": _blob_hash(HARMONIA / "exchangeability.py")},
           "identity": ident, "workspace": ws, "detectors": {}}
    for name, mod in DETECTORS.items():
        res = mod.detect(corpus, dcfg)
        el = res.eligibility.to_json()
        grains = MIRRORS[name](corpus, dcfg)
        counts = {EX.EXCHANGEABLE: 0, EX.SUSPECT: 0, EX.VIOLATED: 0, EX.INDETERMINATE: 0}
        for g in grains:
            counts[g["record"]["label"]] += 1
        out["detectors"][name] = {
            "config": {k: getattr(dcfg, k) for k in CONFIG_KEYS[name]},
            "detector_blob": _blob_hash(Path(mod.__file__)),
            "detector_version": getattr(mod, "VERSION", None) or getattr(mod, "DETECTOR_VERSION", None),
            "eligibility": el, "signals": len(res.signals),
            "grain_mirror": {"source": "%s.detect (cell construction mirrored; see this module's docstring)" % mod.__name__,
                             "grains_from_mirror": len(grains),
                             "eligible_units_from_detect": el.get("eligible_units"),
                             "agree": (len(grains) == el.get("eligible_units")) if name in ("D1", "D5", "D6") else "n/a (pairs report one record per side)"},
            "class_counts": counts, "eligible_grains": len(grains), "grains": grains}
    out["rows"] = [{"row_id": r.row_id, "region": r.region, "family": r.family, "player": r.player, "metric": r.metric,
                    "committed_seq": r.anchors.get("committed_seq"), "obs_seq": r.seq, "coords": r.coords} for r in corpus.rows]
    return out


def render(out: dict) -> str:
    L = ["HARM-13 -- exchangeability class table per detector (EX %s)" % out["diagnostic"]["version"], "",
         "IDENTITY (printed first)",
         "  ledger      %s" % out["identity"]["ledger"].get("path"),
         "  instance    %s   schema %s" % (out["identity"]["ledger"].get("engine_instance_id"), out["identity"]["ledger"].get("schema_version")),
         "  chart       %s   lookback %d   rows %d   corpus_hash %s" % (out["identity"]["chart"], out["identity"]["lookback_rows"], out["identity"]["rows"], str(out["identity"]["corpus_hash"])[:16]),
         "  tenancy     %s" % json.dumps((out["identity"]["window"] or {}).get("tenancy"))[:300],
         "  2026-09-10  NOT REACHABLE from M2 (M1 ledger eng_8a37a5d3 is an archive on SKULLPORT)", "",
         "  det  eligible  mirror  EXCH  SUSP  VIOL  INDET  blocked_reason",
         "  ---  --------  ------  ----  ----  ----  -----  --------------"]
    for name, d in out["detectors"].items():
        c = d["class_counts"]
        L.append("  %-3s  %8s  %6d  %4d  %4d  %4d  %5d  %s" % (name, d["eligibility"].get("eligible_units"), d["eligible_grains"],
                 c[EX.EXCHANGEABLE], c[EX.SUSPECT], c[EX.VIOLATED], c[EX.INDETERMINATE], (d["eligibility"].get("blocked_reason") or "-")[:70]))
    L += ["", "eligible = the detector's own detect() count; mirror = grains this module produced (pairs: one record per side).",
          "Every grain's row_ids and record are in the JSON beside this file; rows carry committed_seq for reproduction.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lookback", type=int, default=2000)
    ap.add_argument("--chart", default=cfg.DEFAULT_CHART)
    ap.add_argument("--out-dir", default="archaeon/docs/h0h5")
    ap.add_argument("--date", default=_dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d"))
    a = ap.parse_args(argv)
    out = build(a.lookback, a.chart)
    d = REPO / a.out_dir
    d.mkdir(parents=True, exist_ok=True)
    jp = d / ("EXCHANGEABILITY_D1_D6_%s.json" % a.date)
    mp = d / ("EXCHANGEABILITY_D1_D6_%s.md" % a.date)
    jp.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    mp.write_text(render(out), encoding="utf-8", newline="\n")
    print(render(out))
    print("written:", jp, mp, "sha256:", hashlib.sha256(jp.read_bytes()).hexdigest()[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
