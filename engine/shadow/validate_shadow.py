#!/usr/bin/env python3
"""validate_shadow.py — schema validator for the shadow channel (ELEN-P16b axis d fix).

Validates engine/shadow/WORKLOG.jsonl and REVIEWS.jsonl. Run from anywhere in the repo:
    python engine/shadow/validate_shadow.py
Exit 0 = both valid. Nonzero = violations printed. Both Aporia and Elenchus run this
before committing their respective files (each validates BOTH — cross-checking is free).

Mechanical citation rule (ELEN-P16 axis c): any worklog citation whose link starts with
http must either appear in that pass's external_links_fetched or carry "unverified": true.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKLOG = ROOT / "WORKLOG.jsonl"
REVIEWS = ROOT / "REVIEWS.jsonl"

WL_REQUIRED = ["pass_id", "prev_commit", "threads", "intent", "pre_stated_readings",
               "actions", "evidence", "claims", "citations",
               "self_identified_weaknesses", "falsifier", "files_touched",
               "review_responses"]
RV_REQUIRED = ["review_id", "pass_id", "verdict", "severity", "findings"]
VERDICTS = {"SOUND", "OVERCLAIMED", "UNDERCLAIMED", "METHOD-FLAW", "CITATION-FAIL",
            "INSUFFICIENT-LOG", "MIXED", "MISSED",
            # split taxonomy (DESIGN_RESPONSE rec 1, enforced from cycle 3 — ELEN cycle-2
            # flagged doctrine/enforcement divergence; doctrine wins, enum follows):
            "LOG-SOUND", "REPLAY-SOUND", "GROUND-SOUND"}
SEVERITIES = {"note", "correction-needed", "invalidates-claim"}
STRENGTHS = {"certain", "supported", "ambiguous", "withheld"}


def load(path):
    if not path.exists():
        return [], []
    recs, errs = [], []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            recs.append((i, json.loads(line)))
        except json.JSONDecodeError as e:
            errs.append(f"{path.name}:{i}: unparseable JSON ({e})")
    return recs, errs


def validate_worklog(recs):
    errs = []
    warns = []
    seen = set()
    for i, r in recs:
        pid = r.get("pass_id", f"<line {i}>")
        for k in WL_REQUIRED:
            if k not in r:
                errs.append(f"WORKLOG {pid}: missing field '{k}'")
        if pid in seen:
            errs.append(f"WORKLOG line {i}: duplicate pass_id {pid}")
        seen.add(pid)
        if not r.get("self_identified_weaknesses"):
            errs.append(f"WORKLOG {pid}: self_identified_weaknesses empty (rule 3)")
        for c in r.get("claims", []):
            if c.get("strength") not in STRENGTHS:
                errs.append(f"WORKLOG {pid}: claim strength '{c.get('strength')}' invalid")
        fetched = set(str(u) for u in r.get("external_links_fetched", []))
        fetched_blob = " ".join(fetched)
        # Mechanical rule adopted at P18 (2026-08-20, ELEN-P16 axis c). Entries written
        # before adoption are LEGACY: reported as warnings, not failures — the worklog is
        # append-only under review, and rewriting reviewed history would be the worse sin.
        legacy = pid <= "2026-08-20T09"  # SEED/P16/P16b/P17 predate adoption
        for c in r.get("citations", []):
            link = str(c.get("link", ""))
            if link.startswith("http") and not c.get("unverified") and not c.get("verified_via"):
                if link not in fetched and link not in fetched_blob:
                    msg = (f"WORKLOG {pid}: citation link {link} neither fetched this "
                           f"pass, nor flagged unverified, nor carrying verified_via")
                    (warns if legacy else errs).append(msg)
        for resp in r.get("review_responses", []):
            if resp.get("disposition") not in ("fixed", "acknowledged", "rebutted"):
                errs.append(f"WORKLOG {pid}: review_response disposition invalid")
    return errs, warns


def validate_reviews(recs, worklog_pass_ids):
    errs = []
    seen = set()
    for i, r in recs:
        rid = r.get("review_id", f"<line {i}>")
        for k in RV_REQUIRED:
            if k not in r:
                errs.append(f"REVIEWS {rid}: missing field '{k}'")
        if r.get("verdict") not in VERDICTS:
            errs.append(f"REVIEWS {rid}: verdict '{r.get('verdict')}' invalid")
        if r.get("severity") not in SEVERITIES:
            errs.append(f"REVIEWS {rid}: severity '{r.get('severity')}' invalid")
        if rid in seen:
            errs.append(f"REVIEWS line {i}: duplicate review_id {rid}")
        seen.add(rid)
        pid = r.get("pass_id")
        if pid and worklog_pass_ids and pid not in worklog_pass_ids \
                and not str(rid).startswith("ELEN-SELF"):
            errs.append(f"REVIEWS {rid}: pass_id {pid} not present in WORKLOG")
    return errs


def check_dispositions(rv, wl):
    """P66 rule mechanized (filed that pass as 'a cheap next item'): dispositions
    are a FIELD, read on every record regardless of verdict. A review carrying a
    non-empty spec_dispositions block must have its review_id echoed by at least
    one worklog review_responses entry — the ELEN-P50 block sat unapplied for two
    sweeps precisely because ingestion keyed on the record verdict. Warn-level so
    legacy records don't hard-fail; a warn here means: apply the block THIS pass.
    """
    echoed = set()
    for _, w in wl:
        for resp in w.get("review_responses") or []:
            if isinstance(resp, dict) and resp.get("review_id"):
                echoed.add(resp["review_id"])
    warns = []
    for _, r in rv:
        sd = r.get("spec_dispositions")
        if not isinstance(sd, dict):
            continue
        spec_ids = [k for k in sd if k != "_note"]
        if spec_ids and r.get("review_id") not in echoed:
            warns.append(
                f"REVIEWS {r.get('review_id')}: spec_dispositions for "
                f"{spec_ids} never echoed in any worklog review_responses "
                f"— apply the block this pass (dispositions are a FIELD)")
    return warns


def main():
    wl, errs = load(WORKLOG)
    rv, e2 = load(REVIEWS)
    errs += e2
    wl_errs, wl_warns = validate_worklog(wl)
    errs += wl_errs
    for w in wl_warns:
        print("WARN (legacy):", w)
    for w in check_dispositions(rv, wl):
        print("WARN (disposition):", w)
    errs += validate_reviews(rv, {r.get("pass_id") for _, r in wl})
    if errs:
        for e in errs:
            print("FAIL:", e)
        print(f"{len(errs)} violation(s)")
        return 1
    print(f"OK: {len(wl)} worklog entries, {len(rv)} reviews — both valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
