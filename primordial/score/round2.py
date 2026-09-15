"""The round 2 prior-vs-reality ledger (F10 acceptance): every round 2 receipt that has a prior,
resolved by code against rows.

Inputs, all committed: the bus export (pm_swarm predicate posts, pm_results receipts), the QD
ledger, and the cohort rows files. Round 2 receipts are pm_results entries with
ts >= ROUND2_START.

Priors. The predicate post (on the bus before the run) is authoritative. A receipt's
science.prior is the fallback, and a disagreement between the two is flagged.

Linking uses identifiers, never judgements. C and E posts carry "exp" == the receipt exp_id.
B posts name the id B-R2-<n> in their subject; a B receipt names that id as the first token
of its claim, or else as the prefix of its exp_id. B priors keyed per cell (w3_128,
int2_w4_128, a2_w4_8, ...) are matched to the receipt's QD rows by parsing the key tokens
against each row's cell. Exactly one key must match.

Translation. Round 2 predicates were posted before the schema was code. B predicates all use
the clause A check, so each B unit is {"qd_check"} == PASS on its QD row. C_TRANSLATION and
E_TRANSLATION spell each C/E predicate as a row expression. A threshold posted as a number is
read from the post (POSTED). A threshold posted as a rule string ("median(clean) -
0.5*IQR(clean)") is written out as the same rule over row fields; review those against the
posts in the export.

    python -m primordial.score.round2            # print coverage + calibration
    python -m primordial.score.round2 --write    # also commit rows (RowWriter) to OUT
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

from primordial.score import predicates as P

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPORT = ROOT / "roles" / "Nestor" / "sidequests" / "graphworld" / "bus_export"
DATE = "2026-09-14"
ROUND2_START = 1789415000.0   # after the last round 1 receipt (E10, ts 1789402803), before the QD seed (1789415669)
COHORTS = ("B", "C", "D", "E")   # round 2 cohort lanes (SWARM_R2 s1)
OUT = ROOT / "primordial" / "ledger" / "rows" / "H" / "F10-prior-vs-reality-r2.jsonl"
POSTED = "POSTED"
ORACLE_GATE = [["oracle_clean", "==", True]]


def _rows(exp: str, lane: str, **where) -> dict:
    return {"source": "rows", "path": f"primordial/ledger/rows/{lane}/{exp}.jsonl", "where": where}


# C: one predicate per drawn cell, read on the cohort's summary row, gated on its oracle bar.
_HELD = {"metric": {"field": "held64_median"}, "comparator": ">=", "threshold": POSTED}
C_TRANSLATION = {
    "C-R2-01-tt-feat-w4-cpu-ttl": _HELD,
    "C-R2-02-nk-small-program-decoder-rent": {       # posted: "median best_raw_nk of bitset control"
        "metric": {"field": "median_best_net_program"}, "comparator": ">=",
        "threshold": {"field": "median_best_raw_bitset"}},
    "C-R2-03-tt-digits-w4-cpu-ttl-numpy": _HELD,
    "C-R2-04-tt-feat-w3-cpu-ttl-torch-gpu": _HELD,
    "C-R2-05-tt-digits-w5-corruption-torch-gpu": {   # posted: "median(clean) - 0.5*IQR(clean)"
        "metric": {"field": "held64_median_corrupt"}, "comparator": ">=",
        "threshold": {"sum": [[1, {"field": "held64_median_clean"}], [-0.5, {"field": "iqr_clean"}]]}},
    "C-R2-08-small-program-w4-decoder-rent-metered": {
        "metric": {"field": "held64_median_cell"}, "comparator": ">=", "threshold": POSTED},
    "C-R2-09-nk-linear-heldout-graphblas": {         # posted: "median(bitset held-out) + 0.5*IQR(bitset held-out)"
        "metric": {"field": "held_median_linear"}, "comparator": ">",
        "threshold": {"sum": [[1, {"field": "held_median_bitset"}], [0.5, {"field": "iqr_bitset"}]]}},
}

# E: instrument predicates, one per prior key, read on E's committed rows.
E_T1, E_T1B, E_T2 = "E-T1-transfer-harness", "E-T1b-transfer-harness-vs-cheats", "E-T2-transformer-baseline"
_P05 = 0.05
E_TRANSLATION = {
    (E_T1, "control_detected"): {       # CONTROL self_graft p<0.05 in >=2/3 worlds
        "cells": _rows(E_T1, "E", condition="summary"),
        "metric": {"count": ["self_graft.held_auc_p", "<", _P05]}, "comparator": ">=", "threshold": 2},
    (E_T1, "cheats_silent"): {          # CHEATS rand_graft and shuffle_graft p<0.05 in 0/3 worlds
        "cells": _rows(E_T1, "E", condition="summary"),
        "metric": {"sum": [[1, {"count": ["rand_graft.held_auc_p", "<", _P05]}],
                           [1, {"count": ["shuffle_graft.held_auc_p", "<", _P05]}]]},
        "comparator": "==", "threshold": 0},
    (E_T1B, "primary"): {               # self_graft vs_cheats p_max < 0.05 in 3/3 worlds
        "cells": _rows(E_T1B, "E", condition="summary"),
        "metric": {"count": ["self_graft.vs_cheats_held_auc_p_max", "<", _P05]}, "comparator": ">=", "threshold": 3},
    (E_T1B, "secondary"): {             # rand_graft vs scratch p<0.05 in <=1/3 worlds
        "cells": _rows(E_T1B, "E", condition="summary"),
        "metric": {"count": ["rand_graft.held_auc_p", "<", _P05]}, "comparator": "<=", "threshold": 1},
    (E_T1B, "rerun_identical"): {       # run seeds 0-7 re-run bit-identical to E-T1 (ts, exp_id excluded)
        "cells": _rows(E_T1B, "E", condition="summary"),
        "metric": {"rows_equal": {"a": _rows(E_T1, "E", condition=["!=", "summary"]),
                                  "b": _rows(E_T1B, "E", condition=["!=", "summary"], run_seed=["<", 8]),
                                  "key": ["recipient_world", "condition", "run_seed"], "ignore": ["ts", "exp_id"]}},
        "comparator": "==", "threshold": 1.0},
    (E_T2, "oracles_clean"): {          # run seed 0: world 0/16, skip_lin>=14/16; brain 0 mismatched, cheat>=14/16
        "cells": _rows(E_T2, "E", run_seed=0),
        "metric": {"all": [
            {"metric": {"field": "world_oracle_honest.elites_failing"}, "comparator": "==", "threshold": 0},
            {"metric": {"field": "world_oracle_skip_lin.elites_failing"}, "comparator": ">=", "threshold": 14},
            {"metric": {"field": "brain_oracle_honest.mismatched_rows"}, "comparator": "==", "threshold": 0},
            {"metric": {"field": "brain_oracle_cheat.elites_mismatching"}, "comparator": ">=", "threshold": 14}]},
        "comparator": "==", "threshold": True},
    (E_T2, "all_seeds_under_ttl"): {     # 8/8 run seeds finish under the 600 s task TTL
        "cells": _rows(E_T2, "E", status="record"),
        "metric": {"count": ["wall_s", "<", 600], "distinct": "run_seed"}, "comparator": ">=", "threshold": 8},
}


class LinkError(ValueError):
    pass


def jsonl(path) -> list[dict]:
    p = pathlib.Path(path)
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


class Loader:
    """load(source, path) over committed files, cached."""

    def __init__(self, root=ROOT):
        self.root = pathlib.Path(root)
        self.cache: dict = {}

    def __call__(self, source, path=None):
        key = (source, path)
        if key not in self.cache:
            p = self.root / "primordial" / "ledger" / "qd" / "cells.jsonl" if source == "qd" else self.root / path
            if not p.exists():
                raise P.Indeterminate(f"rows file {path or p} absent")
            self.cache[key] = jsonl(p)
        return self.cache[key]


def predicate_posts(swarm: list[dict]) -> dict[str, list[dict]]:
    """id -> predicate posts (JSON bodies carrying a prior), oldest first."""
    posts: dict[str, list[dict]] = {}
    for m in swarm:
        if float(m["ts"]) < ROUND2_START or m.get("kind") == "result":
            continue
        try:
            body = json.loads(m.get("body") or "")
        except ValueError:
            continue
        if not isinstance(body, dict):
            continue
        pred = body["predicate"] if isinstance(body.get("predicate"), dict) else body
        if "prior" not in pred:
            continue
        sm = re.match(r"(B-R2-\d+)\b", m.get("subject", ""))
        pid = body.get("exp") or (sm[1] if sm else None)
        if pid:
            posts.setdefault(pid, []).append({"post_id": m["id"], "lane": m["lane"], "ts": float(m["ts"]),
                                              "prior": pred["prior"], "predicate": pred})
    return posts


def predicate_id(rec: dict) -> str | None:
    if rec["lane"] == "B":
        m = re.match(r"(B-R2-\d+)\b", rec.get("claim", "")) or re.match(r"(B-R2-\d+)-", rec["exp_id"])
        return m[1] if m else None
    return rec["exp_id"]


def key_constraints(key: str) -> dict | None:
    """'int2_w4_128' -> {bits: 2, world: w4, pressure: train128_held64}; None if not a cell key."""
    c: dict = {}
    for t in key.split("_"):
        if m := re.fullmatch(r"w(\d+)", t):
            c["world"] = f"w{m[1]}"
        elif t in ("8", "128"):
            c["pressure"] = f"train{t}_held64"
        elif m := re.fullmatch(r"(?:bits|int)(\d)", t):
            c["bits"] = int(m[1])
        elif m := re.fullmatch(r"[aA](\d)", t):
            c["acts"] = int(m[1])
        else:
            return None
    return c


def cell_facts(qd_row: dict) -> dict:
    c = qd_row["cell"]
    m = re.fullmatch(r"linear_int(\d)_nibble(?:_a(\d))?", c["representation"])
    return {"world": c["world"], "pressure": c["pressure"],
            "bits": int(m[1]) if m else None, "acts": (int(m[2]) if m[2] else 8) if m else None}


def match_prior(prior, qd_row: dict) -> tuple[str | None, float]:
    if not isinstance(prior, dict):
        return None, float(prior)
    facts = cell_facts(qd_row)
    hits = []
    for k, v in prior.items():
        c = key_constraints(k)
        if c is None:
            raise LinkError(f"prior key {k!r} is not a cell key")
        if all(facts.get(a) == b for a, b in c.items()):
            hits.append((k, float(v)))
    if len(hits) != 1:
        raise LinkError(f"{len(hits)} prior keys of {sorted(prior)} match cell {facts}")
    return hits[0]


def _units(rec: dict, post: dict | None, prior, load):
    """-> (prior_key, prior, canonical predicate | None, domain, note)."""
    lane, exp = rec["lane"], rec["exp_id"]
    pred = (post or {}).get("predicate", {})
    common = {"seeds": pred.get("seeds"), "ttl_cpu_s": pred.get("ttl_cpu_s")}
    if lane == "B":
        rows = [r for r in load("qd") if r.get("exp_id") == exp and not r.get("baseline")]
        if not rows:
            yield None, None, None, None, "no QD ledger row for this receipt"
        for r in rows:
            c = r["cell"]
            try:
                key, pv = match_prior(prior, r)
            except LinkError as e:
                yield None, None, None, c["world"], str(e)
                continue
            where = {"exp_id": exp, "baseline": False, "cell.world": c["world"], "cell.pressure": c["pressure"],
                     "cell.representation": c["representation"]}
            yield key, pv, {"metric": {"qd_check": True}, "cells": {"source": "qd", "where": where},
                            "comparator": "==", "threshold": "PASS", "prior": pv, **common}, c["world"], ""
    elif lane == "C":
        t = C_TRANSLATION.get(exp)
        if t is None or isinstance(prior, dict):
            yield None, None, None, None, "no translation for this predicate"
            return
        thr = pred.get("threshold") if t["threshold"] == POSTED else t["threshold"]
        if isinstance(thr, bool) or not isinstance(thr, (int, float, dict)):
            yield None, float(prior), None, None, f"posted threshold {thr!r} is not a number"
            return
        cells = _rows(exp, "C", kind="summary")
        canon = {**t, "cells": cells, "threshold": thr, "gate": ORACLE_GATE, "prior": float(prior), **common}
        try:
            domain = P.select(cells, load)[0]["cell"]["world"]
        except (P.Indeterminate, IndexError, KeyError):
            domain = None
        yield None, float(prior), canon, domain, ""
    elif lane == "E":
        for k, pv in (prior.items() if isinstance(prior, dict) else [(None, prior)]):
            t = E_TRANSLATION.get((exp, k))
            if t is None:
                yield k, float(pv), None, "instrument", "no translation for this prior key"
                continue
            yield k, float(pv), {**t, "prior": float(pv), **common}, "instrument", ""
    else:
        yield None, None, None, None, f"no resolver for lane {lane}"


def resolve(export=EXPORT, root=ROOT) -> dict:
    export = pathlib.Path(export)
    swarm = jsonl(export / f"pm_swarm_{DATE}.jsonl")
    results = jsonl(export / f"pm_results_{DATE}.jsonl")
    load, posts = Loader(root), predicate_posts(swarm)
    # round 2 = the cohort lanes only: builder receipts (round 3 F-H, round 6 MVPs P Q W T U) land in the
    # same export after ROUND2_START and must not enter the round 2 ledger (the export grows every epoch)
    receipts = sorted((r for r in results if float(r["ts"]) >= ROUND2_START and r["lane"] in COHORTS),
                      key=lambda r: float(r["ts"]))
    resolutions, no_prior = [], []
    for rec in receipts:
        pid = predicate_id(rec)
        cands = [p for p in posts.get(pid or "", []) if p["lane"] == rec["lane"] and p["ts"] < float(rec["ts"])]
        post = cands[-1] if cands else None
        rp = (rec.get("science") or {}).get("prior")
        prior = post["prior"] if post else rp
        if prior is None:
            no_prior.append({"receipt_id": rec["id"], "exp_id": rec["exp_id"], "predicate_id": pid})
            continue
        base = {"kind": "resolution", "receipt_id": rec["id"], "exp_id": rec["exp_id"], "cohort": rec["lane"],
                "predicate_id": pid, "predicate_post": post["post_id"] if post else None,
                "receipt_status": rec["status"]}
        if post and rp is not None and rp != post["prior"]:
            base["prior_mismatch"] = {"posted": post["prior"], "receipt": rp}
        for key, pv, canon, domain, note in _units(rec, post, prior, load):
            res = P.evaluate(canon, load) if canon else {"outcome": None, "lhs": None, "rhs": None, "why": note}
            resolutions.append({**base, "prior_key": key, "prior": pv, "domain": domain, "predicate": canon, **res})
    linked = {r["receipt_id"] for r in resolutions}
    return {
        "coverage": {"receipts": len(receipts), "with_prior": len(receipts) - len(no_prior),
                     "resolved_by_code": len(linked), "units": len(resolutions),
                     "decided": sum(r["outcome"] is not None for r in resolutions),
                     "untranslated": sum(r["predicate"] is None for r in resolutions)},
        "no_prior": no_prior,
        "resolutions": resolutions,
        "calibration": {"cohort": P.calibration(resolutions, ("cohort",)),
                        "cohort_domain": P.calibration(resolutions, ("cohort", "domain")),
                        "all": P.calibration(resolutions, ())},
    }


BOARD = "pm:board:prior_vs_reality"
BOARD_METRICS = ("n_decided", "mean_prior", "hit_rate", "brier", "over_confidence")


def publish_board(out: dict, r=None) -> int:
    """S3: the prior-vs-reality view on the live board. One zset, members "<cohort>|<domain>|<metric>"
    (ALL|all for the whole round, <cohort>|all per cohort). Replaced atomically; display only:
    nothing scores, allocates or selects from it. -> members written."""
    from primordial.bus import bus
    r = r or bus.conn()
    members = {}
    for name, rows in out["calibration"].items():
        for row in rows:
            cohort = row.get("cohort") or "ALL"
            domain = (row.get("domain") or "none") if name == "cohort_domain" else "all"
            for m in BOARD_METRICS:
                if m in row:
                    members[f"{cohort}|{domain}|{m}"] = float(row[m])
    p = r.pipeline(transaction=True)
    p.delete(BOARD)
    if members:
        p.zadd(BOARD, members)
    p.execute()
    return len(members)


def _fmt(row: dict, keys) -> str:
    head = " ".join(f"{str(row.get(k)):10s}" for k in keys)
    if "mean_prior" not in row:
        return f"{head} n={row['n']} decided=0"
    return (f"{head} n={row['n']:2d} decided={row['n_decided']:2d} prior={row['mean_prior']:.3f} "
            f"hit={row['hit_rate']:.3f} brier={row['brier']:.3f} over={row['over_confidence']:+.3f}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", default=str(EXPORT))
    ap.add_argument("--write", action="store_true", help=f"commit rows to {OUT.relative_to(ROOT).as_posix()}")
    ap.add_argument("--units", action="store_true", help="print every resolved unit")
    ap.add_argument("--board", action="store_true", help=f"publish the calibration view to {BOARD} (S3)")
    a = ap.parse_args(argv)
    out = resolve(a.export)
    if a.board:
        print(f"board {BOARD}: {publish_board(out)} members")
    print("coverage", json.dumps(out["coverage"]))
    if a.units:
        for r in out["resolutions"]:
            print(f"{r['cohort']} {r['exp_id'][:44]:44s} {str(r['prior_key']):16s} prior={r['prior']} "
                  f"-> {r['outcome']} ({r['lhs']} {r['predicate']['comparator'] if r['predicate'] else ''} "
                  f"{r['rhs']}) {r['why']}")
    for name, keys in (("all", ()), ("cohort", ("cohort",)), ("cohort_domain", ("cohort", "domain"))):
        for row in out["calibration"][name]:
            print(f"{name:14s}", _fmt(row, keys))
    if a.write:
        if OUT.exists():
            print(f"{OUT.relative_to(ROOT).as_posix()} exists; rows are append-only, not rewritten")
            return 1
        from primordial.fabric.rows import RowWriter
        with RowWriter(OUT, "F10-prior-vs-reality-r2", commit_every_s=10**9) as w:
            w.write({"kind": "coverage", "status": "record", **out["coverage"], "no_prior": out["no_prior"]})
            for r in out["resolutions"]:
                w.write({**r, "status": "record"})
            for name, rows in out["calibration"].items():
                for row in rows:
                    w.write({"kind": "calibration", "by": name, "status": "record", **row})
        print(f"wrote {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
