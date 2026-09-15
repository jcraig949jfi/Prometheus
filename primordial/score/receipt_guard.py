"""H-R5-1 (round 5 P-BUILD, builder H): the AUTOMATIC RECEIPT GUARD (operator message 19 s4.4, SWARM_R5 s3).

On experiment completion a receipt is refused automatically, with a machine-readable reason per failed
check, unless ALL of these hold (every check runs; every failure is reported, not just the first):

  check                    reason codes
  rows_exist               ROWS_MISSING                 rows names >= 1 primordial/... path and each is on disk
  rows_committed           ROWS_UNCOMMITTED             each rows path is in the commit rec['git'] and clean
  sha_on_integration       SHA_INVALID, SHA_NOT_ON_INTEGRATION
  identity_tag             IDENTITY_TAG_MISSING         rec['tag'] is an instance tag <machine>-<8 hex>
  campaign_stage           CAMPAIGN_STAGE_INVALID       one of SMOKE|PILOT|PRODUCTION|REPLICATION (A 1789467242979-0)
                           CAMPAIGN_STAGE_NO_ENVELOPE   no job envelope campaign_stage to match
                           CAMPAIGN_STAGE_MISMATCH      receipt stage != job envelope stage (F-R5-1)
  predicate_predates_run   PREDICATE_MISSING            no bus post 'PREDICATE <predicate_id>' (exact id)
                           RUN_START_UNKNOWN            the committed rows carry no ts
                           PREDICATE_AFTER_RUN          predicate ts >= the earliest committed row ts
  required_controls        CONTROLS_MISSING             every envelope required_controls has a non-empty result
  oracle_result            ORACLE_MISSING               every envelope required_oracles (or, if none, >= 1
                                                        oracle) has a non-empty result in rec['oracles']
  sample_rule              SAMPLE_INVARIANT             runs_total != rng_family_count * runs_per_family
                           SAMPLE_FIELDS_MISSING        a scientific verdict with no runs_total /
                                                        rng_family_count / runs_per_family
                           CANDIDATE_N | BASELINE_N     a scientific verdict below the judge's minimum

Names are SWARM_R5 s3's (F envelope, G seed schema), top-level on the receipt by default (H 1789467218102-0).
Thresholds are imported from the judge (qd_ledger), never copied. A PILOT receipt that claims no scientific
verdict is NOT refused for its sample size: labelling a deliberate under-sample is H-R5-4's job, and campaign
stage never changes a scientific threshold (19 s3).

    python -m primordial.score.receipt_guard RECEIPT.json [--envelope ENV.json]      rc 0 accepted, 1 refused
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess

from primordial.score.round2 import ROOT

INTEGRATION_REF = "origin/nestor/sidequest-graphworld-2026-09-14"
STAGES = ("SMOKE", "PILOT", "PRODUCTION", "REPLICATION")
CHECKS = ("rows_exist", "rows_committed", "sha_on_integration", "identity_tag", "campaign_stage",
          "predicate_predates_run", "required_controls", "oracle_result", "sample_rule")
TAG_RE = re.compile(r"[a-z0-9]+-[0-9a-f]{8}")
ROWS_RE = re.compile(r"primordial/[\w./-]+\.jsonl?")
SAMPLE_FIELDS = ("runs_total", "rng_family_count", "runs_per_family")
SCIENTIFIC_VERDICTS = ("PASS", "FAIL", "BELOW_FLOOR", "KILL")


def _minimum() -> tuple[int, int, int]:
    from primordial.ops import qd_ledger as Q
    return Q.BASELINE_MIN_RUNS, Q.BASELINE_MIN_FAMILIES, Q.BASELINE_MIN_PER_FAMILY


def rows_paths(rec: dict) -> list[str]:
    return sorted(set(ROWS_RE.findall(str(rec.get("rows", "")))))


def _sha(rec: dict) -> str:
    g = rec.get("git")
    return str((g.get("sha") or g.get("rows") or "") if isinstance(g, dict) else (g or "")).strip()


def git_runner(repo=ROOT):
    def git(*a):
        return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=120)
    return git


def on_integration_default(git, ref: str = INTEGRATION_REF, fetch: bool = True):
    if fetch and ref.startswith("origin/"):
        git("fetch", "-q", "origin", ref.split("/", 1)[1])
    return lambda sha: git("merge-base", "--is-ancestor", sha, ref).returncode == 0


def predicate_ts_default(predicate_id: str, r=None) -> float | None:
    """Earliest ts of a bus claim whose subject is 'PREDICATE <predicate_id>' (the id must end there)."""
    from primordial.bus import bus
    r = r or bus.conn()
    pat = re.compile(rf"PREDICATE {re.escape(predicate_id)}(?![\w.-])")
    ts = [float(f.get("ts") or 0) for _, f in r.xrange(bus.SWARM)
          if f.get("kind") == "claim" and pat.match(f.get("subject") or "")]
    return min(ts) if ts else None


def envelope_of_job(lane: str, job_id: str | None, r=None) -> dict | None:
    """F-R5-1's job envelope: the JSON `envelope` field of job_id's spec on pm:jobs:<lane> (F 1789467306628-0)."""
    if not job_id:
        return None
    if r is None:
        from primordial.bus import bus
        r = bus.conn()
    for _, f in r.xrange(f"pm:jobs:{lane}"):
        if f.get("job_id") == job_id and f.get("envelope"):
            try:
                return json.loads(f["envelope"])
            except ValueError:
                return None
    return None


ROUND_CURRENT = "pm:round:current"   # F-R5-2 clock: pm:round:current = r5; hash pm:round:r5 {start_ts, end_ts, ...}
CLOSE_OUT_GRACE_S = 1800.0           # A 1789467821844-0: close-out receipts are still guarded


def active_round(r, now: float | None = None, grace_s: float = CLOSE_OUT_GRACE_S) -> str | None:
    """The round whose clock window [start_ts, end_ts + grace] holds now; None if the clock key is absent."""
    import time
    now = time.time() if now is None else now
    cur = r.get(ROUND_CURRENT)
    if not cur:
        return None
    h = r.hgetall(f"pm:round:{cur}") or {}
    try:
        start, end = float(h["start_ts"]), float(h["end_ts"])
    except (KeyError, TypeError, ValueError):
        return None
    return cur if start <= now <= end + grace_s else None


def should_guard(rec: dict, r, now: float | None = None) -> bool:
    """Guard a receipt that carries campaign_stage OR is filed inside an active round: omitting the field is
    not a way around the checks (A 1789467821844-0); the guard then refuses CAMPAIGN_STAGE_MISSING."""
    return rec.get("campaign_stage") is not None or active_round(r, now) is not None


def run_start_ts(paths: list[str], root=ROOT) -> float | None:
    ts = []
    for p in paths:
        f = pathlib.Path(root) / p
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                t = json.loads(line).get("ts")
            except (ValueError, AttributeError):
                continue
            if isinstance(t, (int, float)) and not isinstance(t, bool):
                ts.append(float(t))
    return min(ts) if ts else None


def guard(rec: dict, envelope: dict | None = None, *, root=ROOT, git=None, on_integration=None,
          predicate_ts=None) -> dict:
    """-> {accepted, refusals: [{check, reason, detail}], checks: {check: OK|REFUSED}}."""
    env = envelope or {}
    refusals: list[dict] = []

    def refuse(check, reason, detail):
        refusals.append({"check": check, "reason": reason, "detail": detail})

    paths = rows_paths(rec)
    if not paths:
        refuse("rows_exist", "ROWS_MISSING", "rows names no primordial/... path")
    absent = [p for p in paths if not (pathlib.Path(root) / p).exists()]
    if absent:
        refuse("rows_exist", "ROWS_MISSING", f"not on disk: {absent}")

    git = git or git_runner(root)
    sha = _sha(rec)
    if not re.fullmatch(r"[0-9a-f]{7,40}", sha) or git("cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
        refuse("sha_on_integration", "SHA_INVALID", f"git field {sha!r} is not a commit in this repo")
        refuse("rows_committed", "ROWS_UNCOMMITTED", "no commit to hold the rows")
    else:
        if not (on_integration or on_integration_default(git))(sha):
            refuse("sha_on_integration", "SHA_NOT_ON_INTEGRATION", f"{sha} is not on {INTEGRATION_REF}")
        for p in paths:
            if git("cat-file", "-e", f"{sha}:{p}").returncode != 0:
                refuse("rows_committed", "ROWS_UNCOMMITTED", f"{p} absent at {sha}")
            elif git("status", "--porcelain", "--", p).stdout.strip():
                refuse("rows_committed", "ROWS_UNCOMMITTED", f"{p} has uncommitted changes")

    tag = str(rec.get("tag") or "")
    if not TAG_RE.fullmatch(tag):
        refuse("identity_tag", "IDENTITY_TAG_MISSING", f"tag {tag!r} is not <machine>-<8 hex>")

    stage, env_stage = rec.get("campaign_stage"), env.get("campaign_stage")
    if stage is None:
        refuse("campaign_stage", "CAMPAIGN_STAGE_MISSING", "a round 5 receipt must carry campaign_stage (19 s1)")
    elif stage not in STAGES:
        refuse("campaign_stage", "CAMPAIGN_STAGE_INVALID", f"{stage!r} not in {STAGES}")
    elif env_stage is None:
        refuse("campaign_stage", "CAMPAIGN_STAGE_NO_ENVELOPE", "the job envelope carries no campaign_stage")
    elif stage != env_stage:
        refuse("campaign_stage", "CAMPAIGN_STAGE_MISMATCH", f"receipt {stage} != envelope {env_stage}")

    pid = rec.get("predicate_id") or env.get("predicate_id")
    if not pid:
        refuse("predicate_predates_run", "PREDICATE_MISSING", "no predicate_id on the receipt or envelope")
    else:
        pts = (predicate_ts or predicate_ts_default)(pid)
        start = run_start_ts(paths, root)
        if pts is None:
            refuse("predicate_predates_run", "PREDICATE_MISSING", f"no 'PREDICATE {pid}' post")
        elif start is None:
            refuse("predicate_predates_run", "RUN_START_UNKNOWN", "committed rows carry no ts")
        elif not pts < start:
            refuse("predicate_predates_run", "PREDICATE_AFTER_RUN", f"predicate ts {pts} >= run start {start}")

    controls = rec.get("controls") or {}
    missing = [c for c in env.get("required_controls") or () if not str(controls.get(c) or "").strip()]
    if missing:
        refuse("required_controls", "CONTROLS_MISSING", missing)

    oracles = rec.get("oracles") or {}
    required = list(env.get("required_oracles") or ())
    if required:
        missing = [o for o in required if not str(oracles.get(o) or "").strip()]
        if missing:
            refuse("oracle_result", "ORACLE_MISSING", missing)
    elif not any(str(v or "").strip() for v in oracles.values()):
        refuse("oracle_result", "ORACLE_MISSING", "no oracle result recorded")

    science = rec.get("science") or {}
    sample = {k: rec.get(k, science.get(k)) for k in SAMPLE_FIELDS}
    fams, per = rec.get("families", science.get("families")), rec.get("n_per_family", science.get("n_per_family"))
    have = all(isinstance(v, int) and not isinstance(v, bool) for v in sample.values())
    broken = []
    if have and sample["runs_total"] != sample["rng_family_count"] * sample["runs_per_family"]:
        broken.append("runs_total != rng_family_count * runs_per_family")
    if have and fams is not None and sample["rng_family_count"] != len(set(fams)):     # A 1789467299042-0
        broken.append("rng_family_count != len(families)")
    if have and isinstance(per, dict) and sample["runs_total"] != sum(int(v) for v in per.values()):
        broken.append("runs_total != sum(n_per_family)")
    if broken:
        refuse("sample_rule", "SAMPLE_INVARIANT", {**sample, "families": fams, "n_per_family": per, "broken": broken})
    if science.get("verdict") in SCIENTIFIC_VERDICTS:
        n_runs, n_fam, n_per = _minimum()
        rule = rec.get("sample_rule") if rec.get("sample_rule") in ("CANDIDATE_N", "BASELINE_N") else "CANDIDATE_N"
        thin = isinstance(per, dict) and any(int(v) < n_per for v in per.values())       # G: any n_per_family < 8
        if not have:
            refuse("sample_rule", "SAMPLE_FIELDS_MISSING", sample)
        elif (sample["runs_total"] < n_runs or sample["rng_family_count"] < n_fam
              or sample["runs_per_family"] < n_per or thin):
            refuse("sample_rule", rule, {**sample, "n_per_family": per,
                                         "need": {"runs_total": n_runs, "rng_family_count": n_fam,
                                                  "runs_per_family": n_per}})

    failed = {x["check"] for x in refusals}
    return {"accepted": not refusals, "refusals": refusals,
            "checks": {c: ("REFUSED" if c in failed else "OK") for c in CHECKS}}


def file(rec: dict, envelope: dict | None = None, *, post=None, file_receipt=None, **kw) -> str:
    """Guard, then file through bus.receipt. A refusal posts RECEIPT_REFUSED to the lane and A and raises."""
    from primordial.core.contract import ReceiptError
    out = guard(rec, envelope, **kw)
    if not out["accepted"]:
        if post is None:
            from primordial.bus.bus import post
        post("note", f"RECEIPT_REFUSED {rec.get('exp_id')}: {sorted({x['reason'] for x in out['refusals']})}",
             json.dumps(out, default=str), to=f"{rec.get('lane')},A")
        raise ReceiptError("receipt guard: " + json.dumps(out["refusals"], default=str))
    if file_receipt is None:
        from primordial.bus.bus import receipt as file_receipt
    return file_receipt(rec)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("receipt")
    ap.add_argument("--envelope")
    a = ap.parse_args(argv)
    rec = json.loads(pathlib.Path(a.receipt).read_text(encoding="utf-8"))
    env = json.loads(pathlib.Path(a.envelope).read_text(encoding="utf-8")) if a.envelope else rec.get("envelope")
    out = guard(rec, env)
    print(json.dumps(out, indent=1, default=str))
    return 0 if out["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
