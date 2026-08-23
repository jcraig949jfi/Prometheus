"""Free-tier decisive campaign — quota-gated drip orchestrator (James, 2026-08-21).

Every 30 minutes (schtasks): probe the channel with one tiny call; if open, push work until
the first 429/402 or the batch cap; if closed, sleep the cycle. All state on disk, all
finalization atomic, every phase transport-gated. The campaign measures its own daily quota
(ok-calls per firing land in the log), so the timeline estimate updates itself.

HOST PINNING, stated up front: this campaign is pinned to nvidia:deepseek-v4-flash — the
FREE host. The paid-host leveling (M30 @ 0.500) does NOT transfer across the measured +14pp
host delta; the free host's own measured centre is M20 (0.500, n=40, clean run, 2026-08-18).
Per the C2 precedent and HB's band-is-(manifest x host) ruling, phase P1's pre-pass IS the
cold-band check for this (manifest x host) pair. No row from this campaign may ever be
pooled with a paid-host row.

PHASES (dependencies enforced by file existence):
  P1  prepass    manifest 620 @ M20-free, 2 cold reps (1,240 calls) -> band read (full rule:
                 point in [0.35,0.60] AND movable >= 0.30) + screen + rep-1 residue ledger.
                 NOT-LEVELED here ends the campaign (that itself is a result for this host).
  P2  controls   R3 live on this host: F0/F-answer paired (A, D), cheat at N=400 pairs (B),
                 leakage with diagnostics + guess-instruction (C). ~1,300 calls.
  P3  pilot      corrected pilot, 5 arms x 150 sampled post-screen tasks (~750 calls) — the
                 exit-review C3 evidence, with oracle v2 and .body/.body symmetric arms.
  --  HOLD       P4 does not start until ergon/probe/ledgers/campaign/RE_REVIEW_SIGNOFF
                 exists (Charon + Harmonia B re-review of the cures; the drip's calendar
                 time is the review window).
  P4  arms       Tier B decisive: 6 arms x full post-screen N (~450) ~= 2,700 calls.
  P5  drift      end-of-campaign band re-read (200 calls); >7pp vs P1 => HOST-DRIFTED and
                 the campaign is declared void rather than analysed (HB ruling). A mid-
                 campaign read fires automatically between P3 and P4.

Schedule:  schtasks /create /tn PrometheusCampaign /tr F:\\Prometheus\\ergon\\run_campaign.cmd /sc MINUTE /mo 30
Remove:    schtasks /delete /tn PrometheusCampaign /f
"""
import json
import math
import os
import pathlib
import random
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ergon.probe.solver import call
from ergon.probe.extract import extract_numeric
from ergon.probe.assemble import assemble_retrieved, load_prepass, select_residue
from ergon.probe.f_null import build_f_null
from ergon.probe.task_gen_v3 import generate, is_prime, manifest_sha256, generator_sha256
from ergon.probe.chain_run import TRUNCATION_GATE

SOLVER = "nvidia:deepseek-v4-flash"     # FREE host pin — never pooled with paid rows
RUNG, MANIFEST_N, SEED = "M20", 620, 20260821
BAND, MOVABLE_FLOOR = (0.35, 0.60), 0.30
# MAX_TOK raised 8192 -> 16384 on 2026-08-21 after the confounded first P1: at 8192 the
# free host truncated 3.13% of rep-1 calls (>2% gate) and — worse — truncated rows scored
# accuracy 0.000 while parse-fail read 0.000, because the frozen extractor lifts arithmetic
# scratch numbers (24, 756, 950) out of mid-reasoning trial division and scores them as
# answers. Silent corruption, not visible missing data. Observed acc 0.604 = 0.624 x (1-.031):
# the truncation was dragging the point INTO the band. Lane accepts 16384 and 32768 (tested).
MAX_TOK, TIMEOUT = 16384, 420
BATCH_CAP = 400                          # per firing; the 429 stop is the real limiter
CALL_SPACING_S = 2.0
DIR = ROOT / "ergon/probe/ledgers/campaign"
HOLD_FILE = DIR / "RE_REVIEW_SIGNOFF"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(**kw):
    kw["ts_utc"] = now()
    with (DIR / "campaign_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(kw) + "\n")


# Charon exit-review C6: the §4.1 scope caveat travels ON the artifact, not in a doc a
# later reader may never open. Every result object this campaign writes carries it.
D0_SCOPE_CAVEAT = (
    "SCOPE (prereg §4.1, C6): this is a D0 result on self-generated first-cycle residue "
    "(the pre-pass of §4.2). It is NOT a corpus result — it says nothing about the native "
    "residue Prometheus accumulated (D2/D3). A D0 win with a D3 null is not a success for "
    "the accumulated corpus. D0 levels are never compared across strata. Pinned to "
    "(manifest × host); does not transfer across hosts."
)


def atomic(path, obj):
    if isinstance(obj, dict):
        obj = {**obj, "scope_caveat": D0_SCOPE_CAVEAT, "solver_pin": SOLVER,
               "prereg_version": "v1+amendments-2026-08-21"}
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    os.replace(tmp, path)


# ------------------------------------------------------------------ manifest (deterministic)

def manifest():
    mpath = DIR / f"campaign_manifest_{RUNG}_n{MANIFEST_N}.jsonl"
    if not mpath.exists():
        rows = generate(RUNG, MANIFEST_N, SEED)
        for i, r in enumerate(rows):
            r["uid"] = f"camp-{RUNG}-{i:05d}"
        with mpath.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        atomic(DIR / "manifest_meta.json",
               {"n": len(rows), "rung": RUNG, "seed": SEED, "solver_pin": SOLVER,
                "manifest_sha256": manifest_sha256(rows),
                "generator_sha256": generator_sha256(), "ts_utc": now()})
    return [json.loads(l) for l in mpath.read_text(encoding="utf-8").splitlines()]


# ------------------------------------------------------------------ generic drip machinery

def done_keys(led):
    if not led.exists():
        return set()
    return {tuple(r["key"]) for r in (json.loads(l) for l in led.read_text(encoding="utf-8").splitlines())
            if r["status"] == "ok"}


def push_jobs(led_path, jobs, budget):
    """Send jobs until 429/402, exhaustion, or budget. Returns (sent, ok, walled)."""
    sent = ok = 0
    walled = False
    with led_path.open("a", encoding="utf-8") as fh:
        for key, prompt in jobs:
            if sent >= budget:
                break
            res = call(SOLVER, prompt, max_tokens=MAX_TOK, timeout=TIMEOUT, retries=0)
            sent += 1
            rec = {"key": list(key), "status": res.status, "error_type": res.error_type,
                   "latency_s": res.latency_s, "prompt_tokens": res.prompt_tokens,
                   "completion_tokens": res.completion_tokens,
                   "extracted_int": extract_numeric(res.text if res.status == "ok" else None).value,
                   "attempt_text": (res.text or "").strip()[:4000],
                   "solver": SOLVER, "derives_from_gold": False,
                   "ts_utc": res.ts_utc, "host": res.host, "executor": res.executor}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())   # a killed firing must not lose rows that each cost
            #                          ~60s of free-lane latency; Python's 8KB buffer
            #                          silently drops ~10 of them on taskkill.
            if res.status == "ok":
                ok += 1
            elif res.error_type in ("HTTP429", "HTTP402"):
                walled = True
                break
            time.sleep(CALL_SPACING_S)
    return sent, ok, walled


def best(led_path):
    """Latest ok row per key."""
    out = {}
    if led_path.exists():
        for r in (json.loads(l) for l in led_path.read_text(encoding="utf-8").splitlines()):
            if r["status"] == "ok":
                out[tuple(r["key"])] = r
    return out


# ------------------------------------------------------------------ P1: prepass + band read

def p1(rows, gold, budget):
    led = DIR / "p1_prepass.jsonl"
    out = DIR / "p1_bandread.json"
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8")), 0
    have = done_keys(led)
    jobs = [((rep, r["uid"]), r["prompt"]) for rep in (1, 2) for r in rows
            if (rep, r["uid"]) not in have]
    if jobs:
        sent, ok, walled = push_jobs(led, jobs, budget)
        log(phase="P1", sent=sent, ok=ok, walled=walled,
            coverage=f"{len(done_keys(led))}/{2 * len(rows)}")
        if done_keys(led) != {(rep, r["uid"]) for rep in (1, 2) for r in rows}:
            return None, sent
    b = best(led)
    n = len(rows)
    # pre-committed truncation gate (chain_run TRUNCATION_GATE = 0.02). A truncated row is
    # NOT missing data here: it parses to a scratch number and scores wrong, so truncation
    # biases the point estimate downward — toward the band. Refuse rather than repair: any
    # row-level fix (drop / score-wrong) selects on task difficulty, which is the axis the
    # probe measures.
    rep1 = [b[(1, r["uid"])] for r in rows if b.get((1, r["uid"]))]
    trunc_rate = (sum(1 for x in rep1 if (x.get("completion_tokens") or 0) >= MAX_TOK)
                  / max(1, len(rep1)))
    if trunc_rate > TRUNCATION_GATE:
        atomic(DIR / "p1_bandread.TRUNCATION-CONFOUNDED.json",
               {"verdict": "TRUNCATION-CONFOUNDED", "truncation_rate": round(trunc_rate, 4),
                "gate": TRUNCATION_GATE, "max_tokens": MAX_TOK, "n_rep1": len(rep1),
                "note": "no leveling may be chosen from this read (chain_run rule); "
                        "raise MAX_TOK or re-rung, then re-collect from scratch (R11)",
                "ts_utc": now()})
        log(phase="P1", verdict="TRUNCATION-CONFOUNDED", trunc_rate=round(trunc_rate, 4))
        return None, 0
    succ = [b.get((1, r["uid"])) is not None
            and b[(1, r["uid"])]["extracted_int"] == gold[r["uid"]] for r in rows]
    acc = sum(succ) / n
    disc = sum(1 for r in rows
               if (b[(1, r["uid"])]["extracted_int"] == gold[r["uid"]])
               != (b[(2, r["uid"])]["extracted_int"] == gold[r["uid"]]))
    movable = disc / n
    lenient = [r["uid"] for r in rows
               if b[(1, r["uid"])]["extracted_int"] == gold[r["uid"]]
               and b[(2, r["uid"])]["extracted_int"] == gold[r["uid"]]]
    z = 1.959964
    se = math.sqrt(max(acc * (1 - acc), 1e-12) / n)
    mlo, mhi = max(0.0, acc - z * se), min(1.0, acc + z * se)
    # Wilson reported beside the manifest interval as the conservative bound (§3.1 ruling 3)
    den = 1 + z * z / n
    wc = (acc + z * z / (2 * n)) / den
    wh = z * math.sqrt(acc * (1 - acc) / n + z * z / (4 * n * n)) / den
    # HB-R1: at ONE family the lenient screen is a diagnostic, not a contamination screen, so the
    # band is read on the raw manifest here; both numbers are reported always. At Tier B (>=2
    # families) the band is read post-screen.
    post = [r for r in rows if r["uid"] not in set(lenient)]
    acc_post = (sum(1 for r in post
                    if b[(1, r["uid"])]["extracted_int"] == gold[r["uid"]]) / len(post)
                if post else float("nan"))
    # §3.1 ruling 1 — THREE-VALUED. Point rule is standing; when the manifest-level interval
    # straddles a band edge the level is UNDECIDED and re-measured at the decision-n rather than
    # failed outright; UNDECIDED resolves CONSERVATIVELY INTO FAILURE if it survives
    # re-measurement (Charon's terminal rule). n_decidable = the n at which this point estimate
    # would stop straddling — reported so the verdict is honest about whether this n could ever
    # have decided it.
    straddles = (mlo < BAND[0] < mhi) or (mlo < BAND[1] < mhi)
    edge = BAND[0] if abs(acc - BAND[0]) < abs(acc - BAND[1]) else BAND[1]
    margin = abs(acc - edge)
    n_decidable = (math.ceil((z / margin) ** 2 * acc * (1 - acc))
                   if margin > 1e-9 else None)
    point_in = BAND[0] <= acc <= BAND[1]
    if not point_in:
        verdict = "NOT-LEVELED"
    elif movable < MOVABLE_FLOOR:
        verdict = "NOT-LEVELED-DISPERSION"          # HB-R2 dispersion term
    elif straddles:
        # this n IS the decision-n only if it could resolve the straddle; say which.
        # Charon's terminal rule fires only once the straddle has SURVIVED a re-measurement
        # that was capable of resolving it. A straddle at an n too small to decide is not a
        # surviving straddle — it is an underpowered read, and calling it failure would let
        # manifest size masquerade as a result about the host.
        verdict = ("UNDECIDED-RESOLVES-TO-FAILURE"
                   if (n_decidable is not None and n >= n_decidable)
                   else "UNDECIDED-UNDERPOWERED")
    else:
        verdict = "LEVELED"
    read = {"phase": "P1", "solver_pin": SOLVER, "rung": RUNG, "n": n,
            "point_estimate": round(acc, 4),
            "point_estimate_post_screen": (round(acc_post, 4) if post else None),
            "band_read_on": "raw manifest (HB-R1: one family, screen is diagnostic only)",
            "manifest_interval_95": [round(mlo, 4), round(mhi, 4)],
            "wilson_interval_95": [round(max(0, wc - wh), 4), round(min(1, wc + wh), 4)],
            "interval_straddles_band_edge": straddles,
            "nearest_edge": edge, "margin_to_edge": round(margin, 4),
            "n_required_for_decidability": n_decidable,
            "movable_share": round(movable, 4),
            "full_band_passes": point_in and movable >= MOVABLE_FLOOR and not straddles,
            "leveling_verdict": verdict,
            "next_step_if_not_leveled":
                ("Two distinct routes, and they are NOT interchangeable. (a) UNDECIDED-"
                 "UNDERPOWERED means this read could not decide the straddle at this n: under "
                 "the manifest-level estimand the live noise is SOLVER STOCHASTICITY, so the "
                 "resolving move is MORE REPS on the frozen manifest, not more items -- adding "
                 "items changes the estimand and breaks the (manifest x host) pin. (b) A point "
                 "genuinely outside the band routes to the next pre-declared rung "
                 "(M20 -> M30 -> M40 -> M60 -> M80), each with its own cold-band read then its "
                 "own decision-n re-measurement. This campaign STOPS at any non-LEVELED read "
                 "and escalates rather than auto-advancing: sweep-until-in-band inflates "
                 "false-accept 3.9x (HB-R2 measurement), so the advance is the kill authority's "
                 "call, not the runner's."),
            "screen_excluded": sorted(lenient),
            "n_post_screen": n - len(lenient), "ts_utc": now()}
    atomic(out, read)
    log(phase="P1", finalized=read["leveling_verdict"])
    return read, 0


# ------------------------------------------------------------------ arm builders (shared)

def oracle_text(row, rep1_ok):
    comps = [x for x in row["items"] if not is_prime(x)]
    hard = [c for c in comps if all(c % k for k in range(2, 1000))]
    elem = hard[0] if hard else (comps[0] if comps else None)
    if elem is None:
        return "Ground-truth diagnosis: no deceptive composite in this set. Ordinary care suffices."
    why = ("it is a product of two large primes, so no small-divisor test finds a factor"
           if hard else "it has a small factor findable by trial division")
    if rep1_ok:
        return ("Ground-truth diagnosis of the prior attempt: it judged this set correctly, "
                f"including the hardest element, {elem} — composite although {why}. "
                "The same care suffices. The count of primes is withheld.")
    return ("Ground-truth diagnosis of the prior attempt: it misjudged this set. The hardest "
            f"element is {elem}, which is COMPOSITE although a weak test may pass it — {why}. "
            "A deterministic Miller-Rabin test over the first twelve prime bases is decisive. "
            "The count of primes is withheld.")


_ALNUM = re.compile(r"[A-Za-z0-9]")


class Arms:
    def __init__(self, rows, gold):
        self.rows_by_uid = {r["uid"]: r for r in rows}
        self.gold = gold
        # ledger_id must match the cutoff vector this campaign registers, and the M-rung
        # task family is COUNT — its prose channel is a measured answer oracle, so the
        # policy is stated here rather than inferred from a filename prefix.
        self.pool = load_prepass(DIR / "p1_prepass.jsonl",
                                 ledger_id="p1_prepass", withhold_prose=True)
        self.tau = {"p1_prepass": 10 ** 9}
        b = best(DIR / "p1_prepass.jsonl")
        self.rep1_ok = {u: (b.get((1, u)) or {}).get("extracted_int") == gold[u] for u in gold}

    def prom_body(self, uid):
        recs = select_residue(self.pool, stratum="D0", target_uid=uid)
        return assemble_retrieved(task_uid=uid, stratum="D0", records=recs, tau=self.tau).body

    def null_body(self, uid):
        fn = build_f_null(task_uid=uid, stratum="D0",
                          prom_records=select_residue(self.pool, stratum="D0", target_uid=uid),
                          prom_packet_text=self.prom_body(uid), pool=self.pool,
                          tau=self.tau, seed=SEED)
        body = fn.packet.body if hasattr(fn, "packet") else fn.body
        assert not body.lstrip().startswith("{"), "header asymmetry (Charon C1)"
        return body

    def prompt(self, arm, uid):
        base = self.rows_by_uid[uid]["prompt"]
        if arm == "F0":
            return base
        if arm == "F-prom-retrieved":
            return "A prior attempt record:\n" + self.prom_body(uid) + "\n\n" + base
        if arm == "F-null":
            return "A prior attempt record:\n" + self.null_body(uid) + "\n\n" + base
        if arm == "F-generic":
            # Charon's clean-room generic-advice pool. Projected prom packets are tiny
            # (15-60 tokens) -- below the pool's preamble floor -- so exact matching returns
            # UNDER-FLOOR. Ruling (R12, recorded): F-generic ships the pool's SMALLEST unit
            # (~30 tokens, same order as the projection); per-arm token means are logged per
            # BC-7 so the size relationship is a number, not an assumption.
            from ergon.probe.f_generic import render_f_generic, units
            from ergon.probe.assemble import count_tokens
            target = max(40, count_tokens(self.prom_body(uid)))
            pkt = render_f_generic(target)
            text = getattr(pkt, "text", "") or ""
            if not text:
                text = min((u.text for u in units()), key=len)
            return text + "\n\n" + base
        if arm == "F-oracle":
            return oracle_text(self.rows_by_uid[uid], self.rep1_ok[uid]) + "\n\n" + base
        if arm == "F-answer":
            return f"Prior context: the correct count is {self.gold[uid]}.\n\n" + base
        if arm == "F-cheat":
            return base + "\n\nPrior attempt record:\n" + _ALNUM.sub("x", self.prom_body(uid))
        raise ValueError(arm)


def run_arm_phase(name, arm_task_pairs, arms, budget, led_name):
    """Ledger keys are (arm, uid) and are UNIQUE by construction: one row per arm per task.
    A caller that hands the same pair twice would burn a free-lane call to overwrite a row it
    already has, and would plant duplicate task-arm rows that R10 refuses outright. So the
    work set is de-duplicated here (order-preserving) and completion is judged against the
    unique set — the raw list length is not a coverage denominator."""
    led = DIR / f"{led_name}.jsonl"
    want, seen = [], set()
    for arm, uid in arm_task_pairs:
        if (arm, uid) not in seen:
            seen.add((arm, uid))
            want.append((arm, uid))
    dropped = len(arm_task_pairs) - len(want)
    if dropped:
        log(phase=name, deduplicated=dropped,
            note="duplicate (arm,uid) pairs removed before dispatch — each would have been a "
                 "wasted call and a duplicate ledger row")
    have = done_keys(led)
    jobs = [((arm, uid), arms.prompt(arm, uid)) for arm, uid in want if (arm, uid) not in have]
    if not jobs:
        return len(have & seen) >= len(want), 0
    sent, ok, walled = push_jobs(led, jobs, budget)
    have = done_keys(led)
    log(phase=name, sent=sent, ok=ok, walled=walled,
        coverage=f"{len(have & seen)}/{len(want)}")
    return len(have & seen) >= len(want), sent


# ------------------------------------------------------------------ orchestrator

def _pid_alive(pid):
    """Windows PID liveness. NEVER use os.kill(pid, 0) here -- on Windows that
    TERMINATES the target. The 6h age cap in the caller guards against PID reuse."""
    import ctypes
    h = ctypes.windll.kernel32.OpenProcess(0x1000, 0, pid)  # QUERY_LIMITED_INFORMATION
    if not h:
        return False
    code = ctypes.c_ulong()
    ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
    ctypes.windll.kernel32.CloseHandle(h)
    return bool(ok) and code.value == 259  # STILL_ACTIVE


def main():
    DIR.mkdir(parents=True, exist_ok=True)
    # single-instance lock: long-output batches routinely outlive the 30-min firing
    # interval; an overlapping firing would double-spend quota. Stale (>6h) locks are
    # assumed dead (crash without cleanup) and taken over.
    lock = DIR / "campaign.lock"
    if lock.exists():
        age_h = (time.time() - lock.stat().st_mtime) / 3600
        pid = lock.read_text(encoding="utf-8").strip()
        holder_alive = pid.isdigit() and _pid_alive(int(pid)) and age_h < 6
        if holder_alive:
            log(event="skipped_locked", holder_pid=int(pid), lock_age_h=round(age_h, 2))
            print("another firing is still running -- skipped")
            return
        log(event="stale_lock_removed", holder_pid=pid, lock_age_h=round(age_h, 2))
    lock.write_text(str(os.getpid()), encoding="utf-8")
    try:
        _campaign()
    finally:
        lock.unlink(missing_ok=True)


def _campaign():
    # Nothing to do? Then do not spend a call finding that out. Once P1 has finalized
    # non-LEVELED the campaign is halted pending a ruling, and once P1-P3 are complete
    # without a sign-off it is halted pending the re-review — in both states every further
    # firing can only re-probe a channel it will not use. At a 30-min schedule that is ~48
    # free-lane calls a day burned to re-learn a fact already on disk.
    br = DIR / "p1_bandread.json"
    if br.exists():
        v = json.loads(br.read_text(encoding="utf-8")).get("leveling_verdict")
        if v != "LEVELED":
            print(f"halted: P1 {v} — awaiting a ruling on next_step_if_not_leveled; no calls made")
            return
        if (DIR / "p3_pilot.jsonl").exists() and not HOLD_FILE.exists():
            done3 = done_keys(DIR / "p3_pilot.jsonl")
            if done3 and len(done3) >= 5 * 150:
                print("halted: P1-P3 complete, awaiting RE_REVIEW_SIGNOFF; no calls made")
                return

    # channel probe — one tiny call, no retries
    probe = call(SOLVER, "Say OK.", max_tokens=64, timeout=120, retries=0)
    if probe.status != "ok":
        log(event="channel_closed", error=probe.error_type)
        print("channel closed:", probe.error_type)
        return
    log(event="channel_open", latency_s=probe.latency_s)

    rows = manifest()
    gold = {r["uid"]: r["gold_int"] for r in rows}
    budget = BATCH_CAP

    # P1 — prepass + band read (also the C2 cold-band check for this host)
    read, spent = p1(rows, gold, budget)
    budget -= spent
    if read is None or budget <= 0:
        return
    if read["leveling_verdict"] != "LEVELED":
        v = read["leveling_verdict"]
        log(event="campaign_end", verdict=v,
            n_required_for_decidability=read.get("n_required_for_decidability"),
            reason=("P1 did not level on this (manifest x host) pin. This is a RESULT, not an "
                    "error. UNDECIDED-UNDERPOWERED means the manifest could not decide the "
                    "straddle and the resolving move is more reps, not more items; a point "
                    "outside the band routes to the next pre-declared rung. Either advance is "
                    "the kill authority's call — see next_step_if_not_leveled."))
        print(f"P1 {v} — campaign stops and escalates (result, not error); "
              f"n_required_for_decidability={read.get('n_required_for_decidability')}")
        return

    post = [r for r in rows if r["uid"] not in set(read["screen_excluded"])]
    arms = Arms(rows, gold)
    rng = random.Random(SEED)

    # P2 — controls: A/D pairs (200), B cheat pairs (400), C leakage (100)
    # Controls A/D (F0 vs F-answer) and B (F0 vs F-cheat) share their F0 leg: one row per
    # (arm, task) serves both comparisons, so F0 is requested ONCE over the union. The earlier
    # construction doubled the task list and asked for F0 twice, which cost ~470 free-lane calls
    # to produce rows it already had.
    ctl = rng.sample(post, min(200, len(post)))
    b_tasks = post[:400]
    f0_union = {r["uid"] for r in ctl} | {r["uid"] for r in b_tasks}
    p2_pairs = ([("F0", u) for u in sorted(f0_union)]
                + [("F-answer", r["uid"]) for r in ctl]
                + [("F-cheat", r["uid"]) for r in b_tasks])
    done2, spent = run_arm_phase("P2", p2_pairs, arms, budget, "p2_controls")
    budget -= spent
    if not done2 or budget <= 0:
        return

    # P3 — corrected pilot: 5 arms x 150
    pilot_tasks = rng.sample(post, min(150, len(post)))
    p3_pairs = [(a, r["uid"]) for a in ("F0", "F-null", "F-prom-retrieved", "F-oracle", "F-answer")
                for r in pilot_tasks]
    done3, spent = run_arm_phase("P3", p3_pairs, arms, budget, "p3_pilot")
    budget -= spent
    if not done3 or budget <= 0:
        return

    # HOLD — the decisive arms wait for the exit re-review sign-off
    if not HOLD_FILE.exists():
        log(event="holding", reason="P4 gated on re-review sign-off "
            f"(create {HOLD_FILE.name} to release)")
        print("HOLDING before P4 — awaiting re-review sign-off")
        return

    # P4 — decisive arms: 6 arms x full post-screen N
    p4_pairs = [(a, r["uid"]) for a in ("F0", "F-null", "F-generic", "F-prom-retrieved",
                                        "F-oracle", "F-answer") for r in post]
    done4, spent = run_arm_phase("P4", p4_pairs, arms, budget, "p4_arms")
    budget -= spent
    if not done4 or budget <= 0:
        return

    # P5 — end-of-campaign drift re-read
    drift_tasks = rng.sample(rows, 200)
    p5_pairs = [("F0", r["uid"]) for r in drift_tasks]
    done5, spent = run_arm_phase("P5", p5_pairs, arms, budget, "p5_drift")
    if done5:
        log(event="campaign_complete",
            note="run r10_recompute + drift check; verdict belongs to Charon (spec 4.1)")
        print("CAMPAIGN COMPLETE — hand off to R10 + adjudication")


if __name__ == "__main__":
    main()
