"""Report integrity audit. READ-ONLY over the frozen campaign record.

WHY THIS EXISTS. The first REPORT.html carried four defects that the campaign record
itself would have refuted:

  R-01  Sign inversion. packet.py defines d_held_max = experiment - control, and the
        axis key reads "<axis>:<experiment level>-><control level>". A positive mean_d
        therefore means the EXPERIMENT (left) level won. The report read it backwards
        for pressure and read_order and wrote the opposite conclusion in prose.
  R-02  Wrong run identity. The report named an "admissible instance" that it took from
        the PACKET.md specials display list - the PREREGISTERED flag stream, which is a
        preservation trigger and carries no verdict. That run adjudicates WEAK. The one
        ADMISSIBLE instance was never named.
  R-03  Unsupported categorical language. "Answerable from per-run lineage records" was
        asserted for the reservoir question without checking what the lineage record
        retains. "Spontaneous replicators" was used for what the record shows to be
        mostly single replication events.
  R-04  Stale / partial counts. The effect table carried the rows PACKET.md happened to
        print rather than every axis in the record.

Each defect shares one root cause: a human-readable summary was sourced from another
human-readable summary instead of from the machine-readable record. So this file does
two things:

  1. recompute()  rebuilds every load-bearing number from INDEX.jsonl, the per-run
                  RESULT.json files, ADJUDICATION.json and PACKET.json.
  2. audit()      reads the claims REPORT.html declares about itself (a JSON block in
                  the page) and fails on sign inversion, wrong run identity, stale
                  counts, wrong sourcing, or unsupported categorical language.

A claim that names an admissible instance MUST cite ADJUDICATION.json. Citing the
SPECIALS stream is a hard failure, because that is exactly how R-02 happened.

Usage:  python report_audit.py [observatory_root] [report.html]
Writes: AUDIT_RECEIPT.json next to this file. Writes nothing under observatory/.
Exit:   0 all checks pass, 1 any check fails.
"""
from __future__ import annotations

import collections
import gzip
import json
import pathlib
import re
import sys

# Levels of the crossing threshold and control margin, copied from adjudicate.py so this
# file can be read alone. If they ever diverge, CHK-RULES fails.
CROSS = 0.90
MARGIN = 0.25

# Phrases that assert more than a preservation record or a single-run measurement can
# carry. Each maps to what the record would have to show to license it.
BANNED = {
    r"\bsustained (?:autonomous )?(?:multi-generation )?self-replicat":
        "requires ancestry depth >= 2 in most cases; the record is depth-1 dominated",
    r"\breplicat\w+ the (?:cycle[- ]8|forced[- ]read)":
        "this campaign's read_order effect runs opposite to cycle 8; say so",
    r"\banswerable from (?:the )?per-run lineage record":
        "lineage keeps a truncated tail and logs no migration events",
    r"\bproves\b|\bproven\b":
        "the campaign preserves and measures; it does not prove",
    r"\bno sharp accessibility cliff\b":
        "first-replication epochs pool tiers and cells; they do not identify topology",
}


# ----------------------------------------------------------------- loading
def _jsonl(p):
    out = []
    with open(p, encoding="ascii") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load(root):
    root = pathlib.Path(root)
    return {
        "root": root,
        "index": {r["run_id"]: r for r in _jsonl(root / "INDEX.jsonl")},
        "packet": json.loads((root / "PACKET.json").read_text(encoding="ascii")),
        "adjudication": json.loads((root / "ADJUDICATION.json").read_text(encoding="ascii")),
        "specials": _jsonl(root / "SPECIALS.jsonl"),
    }


# ----------------------------------------------------------------- recompute
def pair_audit(index):
    """Every matched pair, its Hamming distance, and the effect table rebuilt from it.

    grammar.control_partner() may repair additional fields after flipping one factor, so
    a pair is only honest if the realised experiment and control differ in exactly one
    factor AND that factor is the declared control axis. Both are checked here rather
    than assumed.
    """
    hamming = collections.Counter()
    impure = []
    agg = collections.defaultdict(list)
    for r in index.values():
        if r.get("role") != "CONTROL" or not r.get("control_of"):
            continue
        exp = index.get(r["control_of"])
        if exp is None:
            hamming["missing_experiment"] += 1
            continue
        diff = [f for f in sorted(exp["cell"]) if exp["cell"][f] != r["cell"][f]]
        hamming[len(diff)] += 1
        axis = r["control_axis"]
        if len(diff) != 1 or diff[0] != axis:
            impure.append({"axis": axis, "differing_factors": diff,
                           "experiment": exp["run_id"], "control": r["run_id"]})
        key = "%s:%s->%s" % (axis, exp["cell"][axis], r["cell"][axis])
        agg[key].append((
            (exp["summary"].get("held_max") or 0) - (r["summary"].get("held_max") or 0),
            int(bool(exp["summary"].get("crossed"))) - int(bool(r["summary"].get("crossed"))),
        ))

    table = {}
    for key, vals in agg.items():
        axis, _, levels = key.partition(":")
        frm, _, to = levels.partition("->")
        mean_d = round(sum(d for d, _ in vals) / len(vals), 4)
        table[key] = {
            "axis": axis, "experiment_level": frm, "control_level": to,
            "n_pairs": len(vals), "mean_d_held": mean_d,
            "crossed_only_experiment": sum(1 for _, c in vals if c > 0),
            "crossed_only_control": sum(1 for _, c in vals if c < 0),
            # d = experiment - control, so a positive mean means the EXPERIMENT level won.
            "better_level": frm if mean_d > 0 else (to if mean_d < 0 else None),
        }
    return {"hamming_histogram": dict(sorted(hamming.items(), key=str)),
            "impure_pairs": impure, "n_pairs": sum(len(v) for v in agg.values()),
            "n_axes": len(table), "table": table}


def spontaneity_audit(root, adjudication):
    """What the 1031 admissible spontaneity flags actually show.

    A replication EVENT is a birth backed by evidence the organism placed the child's
    bytes. That is not the same as a lineage that goes on replicating. Ancestry depth
    separates the two: depth 1 is a star (one parent, N children, no grandchildren),
    depth >= 2 means a child reproduced in turn.
    """
    adm = [v for v in adjudication["verdicts"]
           if v["flag"] == "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES" and v["verdict"] == "ADMISSIBLE"]
    events = collections.Counter()
    depth = collections.Counter()
    epochs = []
    epochs_by_tier = collections.defaultdict(list)
    cells = collections.Counter()
    truncated = 0
    for v in adm:
        d = pathlib.Path(root) / "runs" / v["family"] / v["run_id"]
        res = json.loads((d / "RESULT.json").read_text(encoding="ascii"))
        s = res["summary"]
        events[s["replication_events"]] += 1
        # The stored lineage is a tail (run_cell keeps the last 400 events); a run with
        # more events than that would give a depth that is only a lower bound.
        if s.get("lineage_events", 0) > 400:
            truncated += 1
        parent = {}
        lf = d / "lineage.jsonl.gz"
        if lf.exists():
            with gzip.open(lf, "rt") as fh:
                for line in fh:
                    e = json.loads(line)
                    parent[e["child"]] = e["parent"]
        best = 0
        for child in parent:
            n, cur, seen = 0, child, set()
            while cur in parent and cur not in seen:
                seen.add(cur)
                cur = parent[cur]
                n += 1
            best = max(best, n)
        depth[best] += 1
        fr = s.get("first_replicator") or {}
        if fr.get("epoch") is not None:
            epochs.append(fr["epoch"])
            m = re.search(r"-t([SML])-", v["run_id"])
            epochs_by_tier[m.group(1) if m else "?"].append(fr["epoch"])
        c = v.get("cell") or {}
        cells[(c.get("reproduction"), c.get("structure"), c.get("representation"))] += 1

    n = len(adm)
    return {
        "n_admissible": n,
        "replication_events_distribution": dict(sorted(events.items())),
        "at_least_2_events": sum(k for e, k in events.items() if e >= 2),
        "at_least_3_events": sum(k for e, k in events.items() if e >= 3),
        "at_least_10_events": sum(k for e, k in events.items() if e >= 10),
        "ancestry_depth_distribution": dict(sorted(depth.items())),
        "depth_1_only": depth.get(1, 0),
        "depth_ge_2": sum(k for d_, k in depth.items() if d_ >= 2),
        "runs_with_truncated_lineage": truncated,
        "first_replication_epoch": {
            "min": min(epochs) if epochs else None, "max": max(epochs) if epochs else None,
            "by_tier": {t: {"n": len(v), "min": min(v), "max": max(v)}
                        for t, v in sorted(epochs_by_tier.items())},
        },
        "distinct_repro_structure_representation": len(cells),
        "top_cells": [{"cell": list(k), "n": v} for k, v in cells.most_common(5)],
    }


def verdict_audit(adjudication):
    by_flag = collections.defaultdict(lambda: collections.Counter())
    reasons = collections.Counter()
    admissible = collections.defaultdict(list)
    for v in adjudication["verdicts"]:
        by_flag[v["flag"]][v["verdict"]] += 1
        reasons[(v["flag"], v["verdict"], v["why"])] += 1
        if v["verdict"] == "ADMISSIBLE":
            admissible[v["flag"]].append({"run_id": v["run_id"], "numbers": v["numbers"]})
    return {
        "counts": {f: dict(c) for f, c in by_flag.items()},
        "reasons": [{"flag": f, "verdict": v, "why": w, "n": n}
                    for (f, v, w), n in sorted(reasons.items())],
        "admissible_instances": dict(admissible),
        "rules": adjudication.get("rules", {}),
    }


def lineage_capability(campaign_dir):
    """What an ancestry question can and cannot be answered with, read off the source.

    Checked by reading world.py rather than asserted, because R-03 was exactly an
    assertion about this that nobody checked.
    """
    src = (pathlib.Path(campaign_dir) / "world.py").read_text(encoding="ascii", errors="replace")
    tail = re.search(r"lineage\[-(\d+):\]", src)
    rec = re.search(r"self\.lineage\.append\(\(([^)]*)\)", src)
    return {
        "retained_tail": int(tail.group(1)) if tail else None,
        "record_fields": [f.strip() for f in rec.group(1).split(",")] if rec else None,
        "migration_events_logged": bool(re.search(r"lineage\.append.*migrat", src, re.I)),
        "migrations_counted_only": 'self.ct["migrations"] += 1' in src,
        "niche_field_is_parent_niche_at_birth": "o.niche" in (rec.group(1) if rec else ""),
    }


def recompute(root, campaign_dir):
    d = load(root)
    return {
        "source_root": str(pathlib.Path(root).resolve()),
        "grammar_hash": d["packet"].get("grammar_hash"),
        "totals": d["packet"].get("totals", {}),
        "pairs": pair_audit(d["index"]),
        "verdicts": verdict_audit(d["adjudication"]),
        "spontaneity": spontaneity_audit(root, d["adjudication"]),
        "lineage_capability": lineage_capability(campaign_dir),
        "packet_table_axes": len(d["packet"]["map_paired"]["by_axis"]),
        "specials_stream_n": len(d["specials"]),
    }


# ----------------------------------------------------------------- audit
def _claims(html):
    m = re.search(r'<script[^>]+id="report-claims"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def _visible_text(html):
    """Prose the report ASSERTS, which is not all the prose it contains.

    A corrections section has to be able to quote the claim it is retracting, so any
    element marked class="corr-was" is dropped before linting. Without this the lint
    fires on the report's own admission of the defect, which would push a corrected
    report toward describing its errors vaguely - the opposite of what is wanted.
    Only the retracted half is exempt; the replacement text is linted normally.
    """
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r'<(\w+)[^>]*class="[^"]*\bcorr-was\b[^"]*"[^>]*>.*?</\1>', " ", t, flags=re.S)
    return re.sub(r"<[^>]+>", " ", t)


def audit(root, report_path, campaign_dir):
    R = recompute(root, campaign_dir)
    html = pathlib.Path(report_path).read_text(encoding="utf-8", errors="replace")
    claims = _claims(html)
    checks = []

    def chk(cid, ok, detail):
        checks.append({"check": cid, "pass": bool(ok), "detail": detail})

    chk("CHK-CLAIMS-PRESENT", claims is not None,
        "REPORT declares a machine-readable claims block" if claims else
        "no <script id='report-claims'> block: nothing can be verified")
    if claims is None:
        return R, checks

    chk("CHK-RULES", R["verdicts"]["rules"].get("CROSS") == CROSS
        and R["verdicts"]["rules"].get("MARGIN") == MARGIN,
        "adjudication rules match this auditor's copy (CROSS=%s MARGIN=%s)"
        % (CROSS, MARGIN))

    # --- pair purity, the precondition for every effect claim -------------
    ph = R["pairs"]["hamming_histogram"]
    chk("CHK-PAIRS-HAMMING", set(ph) == {1},
        "every matched pair differs in exactly one factor: histogram %s" % ph)
    chk("CHK-PAIRS-AXIS", not R["pairs"]["impure_pairs"],
        "in every pair the single differing factor is the declared control axis "
        "(%d exceptions)" % len(R["pairs"]["impure_pairs"]))

    # --- effect claims: value, and the DIRECTION spelled out in prose -----
    for c in claims.get("effects", []):
        key = c["axis_key"]
        row = R["pairs"]["table"].get(key)
        if row is None:
            chk("CHK-EFFECT:%s" % key, False, "axis not present in recomputed table")
            continue
        same = (row["n_pairs"] == c["n_pairs"]
                and abs(row["mean_d_held"] - c["mean_d_held"]) < 1e-4
                and row["crossed_only_experiment"] == c["crossed_only_experiment"]
                and row["crossed_only_control"] == c["crossed_only_control"])
        chk("CHK-EFFECT:%s" % key, same,
            "n=%s d=%s oE=%s oC=%s" % (row["n_pairs"], row["mean_d_held"],
                                       row["crossed_only_experiment"], row["crossed_only_control"]))
        if "better_level" in c:
            # THE SIGN TEST. d = experiment - control and the key reads exp->ctl, so a
            # positive mean_d means the LEFT level won. This is the check that would
            # have caught R-01.
            chk("CHK-SIGN:%s" % key, row["better_level"] == c["better_level"],
                "d=%+.4f so %s scored higher; report says %s"
                % (row["mean_d_held"], row["better_level"], c["better_level"]))

    chk("CHK-EFFECT-TABLE-COMPLETE",
        claims.get("n_axes_shown") == R["pairs"]["n_axes"],
        "report shows %s of %s axes in the record"
        % (claims.get("n_axes_shown"), R["pairs"]["n_axes"]))
    chk("CHK-PAIR-TOTAL", claims.get("n_pairs_total") == R["pairs"]["n_pairs"],
        "total matched pairs %s" % R["pairs"]["n_pairs"])

    # --- named instances must come from the adjudicated record ------------
    special_ids = {s["run_id"] for s in load(root)["specials"]}
    for c in claims.get("admissible_instances", []):
        flag, rid = c["flag"], c["run_id"]
        real = {i["run_id"] for i in R["verdicts"]["admissible_instances"].get(flag, [])}
        chk("CHK-ADMISSIBLE-ID:%s" % flag, rid in real,
            "%s is ADMISSIBLE for %s (adjudicated set: %s)"
            % (rid, flag, sorted(real) if len(real) < 6 else "%d runs" % len(real)))
        # R-02 was sourcing a verdict claim from the preregistered flag stream, which
        # carries no verdict at all. Citing it is the defect, even if the id is right.
        chk("CHK-ADMISSIBLE-SOURCE:%s" % flag,
            c.get("source", "").startswith("ADJUDICATION"),
            "cites %r (must be ADJUDICATION.json; SPECIALS.jsonl carries no verdict)"
            % c.get("source"))
        if rid in special_ids and not c.get("source", "").startswith("ADJUDICATION"):
            chk("CHK-ADMISSIBLE-NOT-FROM-SPECIALS:%s" % flag, False,
                "%s appears in the SPECIALS stream and the claim cites it" % rid)

    # --- verdict counts ---------------------------------------------------
    for c in claims.get("verdict_counts", []):
        got = R["verdicts"]["counts"].get(c["flag"], {})
        want = {k: v for k, v in c.items() if k in ("ADMISSIBLE", "WEAK", "INADMISSIBLE")}
        norm = {k: got.get(k, 0) for k in want}
        chk("CHK-VERDICTS:%s" % c["flag"], norm == want,
            "record says %s; report says %s" % (norm, want))

    # --- reason breakdown -------------------------------------------------
    for c in claims.get("verdict_reasons", []):
        hit = [r for r in R["verdicts"]["reasons"]
               if r["flag"] == c["flag"] and r["verdict"] == c["verdict"]
               and c["why_contains"].lower() in r["why"].lower()]
        n = sum(r["n"] for r in hit)
        chk("CHK-REASON:%s/%s" % (c["flag"], c["why_contains"][:24]), n == c["n"],
            "record %d vs report %d" % (n, c["n"]))

    # --- distribution claims ---------------------------------------------
    sp = R["spontaneity"]
    for c in claims.get("distributions", []):
        got = sp.get(c["key"])
        chk("CHK-DIST:%s" % c["key"], got == c["value"],
            "record %r vs report %r" % (got, c["value"]))

    # --- lineage capability, asserted only from source --------------------
    for c in claims.get("lineage_capability", []):
        got = R["lineage_capability"].get(c["key"])
        chk("CHK-LINEAGE:%s" % c["key"], got == c["value"],
            "world.py says %r; report says %r" % (got, c["value"]))

    # --- prose lint -------------------------------------------------------
    text = _visible_text(html)
    for pat, why in BANNED.items():
        m = re.search(pat, text, re.I)
        chk("CHK-LANGUAGE:%s" % pat[:28], m is None,
            ("unsupported phrase %r: %s" % (m.group(0), why)) if m else "absent")

    return R, checks


def main(argv):
    here = pathlib.Path(__file__).resolve().parent
    root = pathlib.Path(argv[1]) if len(argv) > 1 else here / "observatory"
    report = pathlib.Path(argv[2]) if len(argv) > 2 else here / "REPORT.html"
    R, checks = audit(root, report, here)
    failed = [c for c in checks if not c["pass"]]
    receipt = {
        "audited": str(report),
        "source_root": R["source_root"],
        "grammar_hash": R["grammar_hash"],
        "n_checks": len(checks), "n_failed": len(failed),
        "verdict": "PASS" if not failed else "FAIL",
        "checks": checks,
        "recomputed": R,
    }
    (here / "AUDIT_RECEIPT.json").write_text(
        json.dumps(receipt, indent=1, ensure_ascii=True, default=str), encoding="ascii")
    for c in checks:
        print("%-4s %s  %s" % ("PASS" if c["pass"] else "FAIL", c["check"], c["detail"]))
    print("\n%d checks, %d failed -> %s" % (len(checks), len(failed), receipt["verdict"]))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
