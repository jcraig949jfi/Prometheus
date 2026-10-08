"""Reducer for fh.py runs.  python -B analyze.py <EXP> [--json]

Per arm, over ESTABLISHED runs (causal depth >= 20) unless noted:
  persistence  CS_peak, last epoch with CS > 0 (median, max), CS AUC (mean CS over snapshots), final CS > 0 count
  ledger       loss / gain classes summed; outcome shares of a competent half per interaction
  hazards      competence loss per competent-half interaction and per competent-half epoch;
               exposure = interactions per half-epoch, competent vs non-competent
  transmission P(child competent | competent donor) for P-11 / LABEL births, and P(tape copy competent | competent donor)
  positions    loss-causing byte changes by CT_UA region (copier 0-6, routine 7-38, padding 39-63), and the per-region
               destructiveness = loss-causing changes / all mutation changes on competent genomes (in-place only)
"""
from __future__ import annotations

import gzip
import json
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
REG = {"copier": range(0, 7), "routine": range(7, 39), "padding": range(39, 64)}


def load(exp):
    d = HERE / "runs" / exp
    rows = [json.loads(p.read_text()) for p in sorted(d.glob("*.json")) if not p.name.startswith("RECEIPT")]
    for r in rows:
        p = d / ("%s_%d.detail.json.gz" % (r["arm"], r["seed"]))
        r["_detail_path"] = str(p)
    return rows


def detail(r):
    with gzip.open(r["_detail_path"], "rt") as f:
        return json.load(f)


def med(x):
    return statistics.median(x) if x else None


def reduce_arm(rows, with_positions=True):
    est = [r for r in rows if r["depth"] >= 20]
    out = {"n": len(rows), "established": len(est)}
    if not est:
        return out
    out["CS_peak_median"] = med([r["CS_peak"] for r in est])
    out["last_CS_gt0_median"] = med([r["last_epoch_CS_gt_0"] for r in est])
    out["last_CS_gt0_all"] = sorted(r["last_epoch_CS_gt_0"] for r in est)
    out["auc_median"] = med([r["comp_auc"] for r in est])
    out["final_CS_gt0"] = sum(r["CS"] > 0 for r in est)
    out["max_tx_p11_ever_median"] = med([r["max_tx_p11_ever"] for r in est])
    out["interaction_rate_median"] = med([r["interaction_rate"] for r in est])
    led = {}
    for r in est:
        for k, v in r["ledger"].items():
            led[k] = led.get(k, 0) + v
    out["ledger"] = led
    comp_out = {k: led.get(k, 0) for k in ("KEPT", "REPL_COMP", "REPL_CREATED", "LOST_INPLACE", "LOST_OVERWRITE",
                                          "LOST_COPY_ERR", "LOST_COPY_MUT")}
    tot = sum(comp_out.values()) or 1
    out["competent_half_outcome_share"] = {k: round(v / tot, 4) for k, v in comp_out.items()}
    losses = sum(v for k, v in led.items() if k.startswith("LOST_"))
    gains = sum(v for k, v in led.items() if k.startswith("GAIN_"))
    out["losses"], out["gains"] = losses, gains
    out["loss_share"] = {k: round(led.get(k, 0) / max(1, losses), 4)
                         for k in ("LOST_INPLACE", "LOST_OVERWRITE", "LOST_COPY_ERR", "LOST_COPY_MUT")}
    ex = {k: sum(r["exposure"][k] for r in est) for k in est[0]["exposure"]}
    out["exposure"] = ex
    out["inter_per_epoch_comp"] = round(ex["comp_half_interactions"] / max(1, ex["comp_half_epochs"]), 4)
    out["inter_per_epoch_noncomp"] = round(ex["noncomp_half_interactions"] / max(1, ex["noncomp_half_epochs"]), 4)
    out["hazard_per_comp_interaction"] = round(losses / max(1, ex["comp_half_interactions"]), 4)
    out["hazard_per_comp_epoch"] = round(losses / max(1, ex["comp_half_epochs"]), 4)
    out["gain_per_comp_interaction"] = round(gains / max(1, ex["comp_half_interactions"]), 4)
    # replacement exchange (selection-neutral component): competent overwrites non-competent vs the reverse
    out["exchange_GAIN_COPY_vs_LOST_OVERWRITE"] = (led.get("GAIN_COPY", 0), led.get("LOST_OVERWRITE", 0))
    tx = {}
    for kind in ("P11", "LABEL"):
        n = sum(r["tx"][kind][0] for r in est)
        tx[kind] = {"n": n, "P_child_comp": round(sum(r["tx"][kind][1] for r in est) / max(1, n), 4),
                    "P_tape_comp": round(sum(r["tx"][kind][2] for r in est) / max(1, n), 4)}
    out["transmission"] = tx
    side = {k: sum(r["side"][k] for r in est) for k in est[0]["side"]}
    out["side"] = side
    if with_positions:
        pl = {k: [0] * 64 for k in ("LOST_INPLACE", "LOST_COPY_MUT", "LOST_COPY_ERR")}
        den = [0] * 64
        for r in est:
            d = detail(r)
            for k in pl:
                for j, v in enumerate(d["pos_loss"][k]):
                    pl[k][j] += v
            for j, v in enumerate(d["pos_mut_on_comp"]):
                den[j] += v
        out["loss_positions_by_region"] = {k: {g: sum(pl[k][j] for j in rg) for g, rg in REG.items()} for k in pl}
        out["inplace_destructiveness_by_region"] = {
            g: round(sum(pl["LOST_INPLACE"][j] for j in rg) / max(1, sum(den[j] for j in rg)), 4) for g, rg in REG.items()}
        out["top_loss_positions_inplace"] = sorted(range(64), key=lambda j: -pl["LOST_INPLACE"][j])[:10]
        out["inplace_destructiveness_by_pos"] = [round(pl["LOST_INPLACE"][j] / den[j], 3) if den[j] else None
                                                 for j in range(64)]
    return out


def reduce(exp, with_positions=True):
    rows = load(exp)
    arms = sorted({r["arm"] for r in rows})
    return {a: reduce_arm([r for r in rows if r["arm"] == a], with_positions) for a in arms}


if __name__ == "__main__":
    res = reduce(sys.argv[1])
    out = HERE / "runs" / sys.argv[1] / "REDUCED.json"
    out.write_text(json.dumps(res, indent=1))
    for a, v in res.items():
        print("==", a, json.dumps({k: v.get(k) for k in ("n", "established", "CS_peak_median", "last_CS_gt0_all",
                                                         "auc_median", "final_CS_gt0", "interaction_rate_median",
                                                         "inter_per_epoch_comp", "inter_per_epoch_noncomp",
                                                         "hazard_per_comp_interaction", "hazard_per_comp_epoch",
                                                         "gain_per_comp_interaction", "loss_share",
                                                         "exchange_GAIN_COPY_vs_LOST_OVERWRITE", "transmission",
                                                         "inplace_destructiveness_by_region",
                                                         "competent_half_outcome_share")}))
