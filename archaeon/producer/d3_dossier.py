"""D3 live-fire dossier (Harmonia item 5, 2026-09-10).

Rebuilds the corpus exactly as the tick does (recent fossils through the
default chart, repeats aggregated to one row per independent unit), runs D3
under BOTH denominators, and for every UPPER fire under v0 writes what
Harmonia asked for, per firing region:

  * neighbourhood_kind (k_nearest vs the family fallback)
  * the region's rows: one metric per independent unit, with unit ids
  * the neighbour ids actually used, with their rows
  * the recorded v_reg / v_nb / ratio, and the centroids
  * whether any region still carries repeats after aggregation
  * whether the same region fires under v1 (pooled-within), and its ratio

That enables her four checks (survives v1; family fallback; one outlier
row driving v_reg; the region spans sub-units with different means).
Numbers only; the adjudication is Harmonia's.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime
import json
from collections import defaultdict
from typing import Any, Dict, List

from .. import config as cfg
from .. import fossils
from ..detectors import d3_variance_anomaly as D3
from ..detectors.base import variance
from . import readers


def _rows_by_region(corpus) -> Dict[str, List[Any]]:
    by = defaultdict(list)
    for r in corpus.rows:
        by[r.region].append(r)
    return by


def _row_view(r) -> Dict[str, Any]:
    return {"unit": fossils.unit_key(r), "row_id": r.row_id, "metric": r.metric,
            "player": r.player, "family": r.family, "coords": dict(r.coords),
            "anchors": {k: str(v)[:40] for k, v in (r.anchors or {}).items()}}


def build(lookback_rows: int = 2000, chart: str = None) -> Dict[str, Any]:
    raw = readers.recent_fossils(chart or cfg.DEFAULT.chart, lookback_rows)
    agg = fossils.aggregate_repeats(raw)
    raw_by = _rows_by_region(raw); agg_by = _rows_by_region(agg)
    repeats_remaining = {}
    for reg, rs in agg_by.items():
        units = [fossils.unit_key(r) for r in rs]
        if len(units) != len(set(units)):
            repeats_remaining[reg] = len(units) - len(set(units))
    dc = cfg.DEFAULT.detectors
    v0 = dataclasses.replace(dc, d3_denominator="concatenated")
    v1 = dataclasses.replace(dc, d3_denominator="pooled_within")
    r0 = D3.detect(agg, v0); r1 = D3.detect(agg, v1)
    fires1 = {s.regions[0]: s for s in r1.signals}
    scales = agg.coord_scales()
    centroid = {}
    for reg, rs in agg_by.items():
        acc = defaultdict(list)
        for r in rs:
            for k, v in agg.normalized_coords(r, scales).items():
                acc[k].append(v)
        centroid[reg] = {k: sum(v) / len(v) for k, v in acc.items()}
    dossier = []
    for s in r0.signals:
        reg = s.regions[0]
        rows = [_row_view(r) for r in agg_by[reg]]
        metrics = [x["metric"] for x in rows]
        # one-outlier check: variance of the region with each row removed
        loo = []
        for i in range(len(metrics)):
            rest = metrics[:i] + metrics[i + 1:]
            loo.append(variance(rest) if len(rest) >= 2 else None)
        # sub-unit means: by player, and by the first differing coordinate value
        by_player = defaultdict(list)
        for x in rows:
            by_player[str(x["player"])].append(x["metric"])
        entry = {"region": reg, "direction": s.values["direction"], "v0": {"v_reg": s.values["region_variance"],
                 "v_nb": s.values["neighbourhood_variance"], "ratio": s.values["variance_ratio"],
                 "neighbourhood_kind": s.values["neighbourhood_kind"], "neighbourhood_n": s.values["neighbourhood_n"],
                 "neighbourhood_df": s.values.get("neighbourhood_df")},
                 "v1": (None if reg not in fires1 else {"fires": True, "direction": fires1[reg].values["direction"],
                                                          "v_nb": fires1[reg].values["neighbourhood_variance"],
                                                          "ratio": fires1[reg].values["variance_ratio"]}),
                 "v1_fires": reg in fires1,
                 "family": s.values["family"], "centroid": centroid.get(reg),
                 "region_rows": rows, "region_n_units": len({x["unit"] for x in rows}),
                 "region_rows_raw_before_aggregation": len(raw_by.get(reg, [])),
                 "leave_one_out_variance": loo,
                 "min_loo_variance": min((v for v in loo if v is not None), default=None),
                 "sub_unit_means_by_player": {k: (sum(v) / len(v), len(v)) for k, v in by_player.items()},
                 "neighbours": [{"region": o, "centroid": centroid.get(o), "n": len(agg_by[o]),
                                 "variance": variance([r.metric for r in agg_by[o]]),
                                 "mean": sum(r.metric for r in agg_by[o]) / len(agg_by[o]),
                                 "rows": [_row_view(r) for r in agg_by[o]]} for o in s.values["neighbours"]]}
        dossier.append(entry)
    return {"schema": "archaeon.d3.dossier.v0",
            "written": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "chart": chart or cfg.DEFAULT.chart, "lookback_rows": lookback_rows,
            "corpus": {"rows_raw": len(raw.rows), "rows_aggregated": len(agg.rows), "regions": len(agg_by)},
            "repeats_remaining_after_aggregation": repeats_remaining,
            "v0": {"eligible": r0.eligibility.eligible_units if hasattr(r0.eligibility, "eligible_units") else None,
                   "fires": len(r0.signals), "upper": sum(1 for s in r0.signals if s.values["direction"] == "HIGHER_DISPERSION"),
                   "lower": sum(1 for s in r0.signals if s.values["direction"] == "LOWER_DISPERSION"),
                   "detail": dict(r0.eligibility.detail or {})},
            "v1": {"fires": len(r1.signals), "upper": sum(1 for s in r1.signals if s.values["direction"] == "HIGHER_DISPERSION"),
                   "lower": sum(1 for s in r1.signals if s.values["direction"] == "LOWER_DISPERSION"),
                   "detail": dict(r1.eligibility.detail or {})},
            "fires_v0": dossier,
            "upper_fires_v0": [d for d in dossier if d["direction"] == "HIGHER_DISPERSION"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.producer.d3_dossier")
    ap.add_argument("--lookback", type=int, default=2000)
    ap.add_argument("--out", default="archaeon/docs/h0h5/D3_LIVE_DOSSIER_2026-09-10.json")
    a = ap.parse_args(argv)
    d = build(a.lookback)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, sort_keys=True, default=str)
    print(json.dumps({"corpus": d["corpus"], "v0": {k: d["v0"][k] for k in ("fires", "upper", "lower")},
                      "v1": {k: d["v1"][k] for k in ("fires", "upper", "lower")},
                      "repeats_remaining": d["repeats_remaining_after_aggregation"],
                      "upper": [{"region": u["region"], "kind": u["v0"]["neighbourhood_kind"], "ratio": round(u["v0"]["ratio"], 3),
                                 "v1_fires": u["v1_fires"], "n_units": u["region_n_units"],
                                 "min_loo_var_over_v_reg": (None if u["min_loo_variance"] is None or not u["v0"]["v_reg"] else round(u["min_loo_variance"] / u["v0"]["v_reg"], 3)),
                                 "sub_unit_means": u["sub_unit_means_by_player"]} for u in d["upper_fires_v0"]]}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
