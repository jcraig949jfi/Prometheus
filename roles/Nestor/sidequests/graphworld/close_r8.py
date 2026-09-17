"""R8 CLOSE RUNNER (lane A, logistics only). POST_ROUND_FINAL_STEPS as executable steps.

Written and rehearsed BEFORE the close so the close is EXECUTION, not assembly under a deadline
(POST_ROUND s2). Lives in the sidequest directory, not primordial/, so it collides with no lane's files.

    python roles/Nestor/sidequests/graphworld/close_r8.py --rehearse   # everything EXCEPT --emit
    python roles/Nestor/sidequests/graphworld/close_r8.py --emit       # the real close

--emit writes UNRECEIPTED_OBSERVATION events and MUST NOT run against a live round; the runner refuses
unless the round is closed by code.

Every counting trap below produced a WRONG NUMBER in a real packet, or in this session:
  ff first                 a stale checkout reported "zero cited" in r7 and it was broadcast to seven lanes
  dedup rows by FILE       committed rows propagate to every worktree; a per-worktree sum gave me 1590 for 714
  split lane-A posts       "A_bus_posts_by_kind {'note': 45}" counted 9 controller boundary notes as A's actions
  PC id window             xlen(pm:production_candidates) is ALL TIME (149 in r7), not this round
  receipts != rows files   different denominators; state both, never one as the other
  residue rc 1 is EXPECTED one DEAD_CONSUMER per lane group with pending 0 is the normal close state
  query the host           "4-core host" was recalled, not measured
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
GW = ROOT / "roles" / "Nestor" / "sidequests" / "graphworld"
PY = r"C:\Users\jcrai\lab\gw-venv\Scripts\python.exe"
INTEGRATION = "nestor/sidequest-graphworld-2026-09-14"
ROUND = "r8"
LANES = "BCDEGHR"
CLOCK_START = 1789591916          # pm:round:r8 start_ts, derived at launch
WORKTREES = {"B": "nestor-r8-b", "C": "nestor-r8-c", "D": "nestor-r8-d", "E": "nestor-r8-e",
             "R": "nestor-r8-r", "G": "nestor-bld-g", "H": "nestor-bld-h"}


def _run(args, timeout=900, cwd=None):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=str(cwd or ROOT))


def step_ff(out):
    """POST_ROUND s1: ff BEFORE every sweep. close_sweep reads receipt MIRRORS from the WORKING TREE."""
    _run(["git", "-C", str(ROOT), "fetch", "origin", "--quiet"], timeout=300)
    b = _run(["git", "-C", str(ROOT), "rev-list", "--count", f"HEAD..origin/{INTEGRATION}"])
    behind = (b.stdout or "").strip()
    if behind != "0":
        m = _run(["git", "-C", str(ROOT), "merge", "--ff-only", f"origin/{INTEGRATION}"])
        out.append(("ff_worktree", m.returncode == 0, f"was {behind} behind; ff rc={m.returncode}"))
    else:
        out.append(("ff_worktree", True, "already current"))
    d = _run(["git", "-C", str(ROOT), "status", "--porcelain"])
    out.append(("worktree_clean", not (d.stdout or "").strip(),
                f"dirty_lines={len((d.stdout or '').strip().splitlines())}"))


def step_round_closed(r, out, emit):
    """POST_ROUND s0. --emit is REFUSED while the round is live."""
    st = r.hgetall("pm:epoch:state") or {}
    cur = r.get("pm:round:current")
    regs = len(r.keys("pm:worker:reg:*"))
    stops = len(r.keys("pm:stop*"))
    h = r.hgetall(f"pm:round:{ROUND}") or {}
    past_end = bool(h.get("end_ts")) and time.time() > float(h["end_ts"])
    closed = st.get("phase") == "closed" and st.get("round_id") == ROUND and cur is None
    out.append(("round_closed_by_code", closed, f"phase={st.get('phase')} current={cur}"))
    out.append(("now_past_end_ts", past_end, f"end_ts={h.get('end_ts')}"))
    out.append(("zero_registrations", regs == 0, f"registrations={regs}"))
    out.append(("zero_stop_flags", stops == 0, f"stop_flags={stops}"))
    if emit and not (closed and past_end):
        raise SystemExit("REFUSING --emit: the round is not closed by code. Rehearse instead.")


def rows_deduplicated():
    """Committed rows propagate to EVERY worktree that ff-merges. Count each rows FILE once."""
    best = {}
    for wt in WORKTREES.values():
        root = pathlib.Path(f"F:/Prometheus-worktrees/{wt}/primordial/ledger/rows")
        if not root.is_dir():
            continue
        for p in root.rglob("*.jsonl"):
            try:
                if p.stat().st_mtime <= CLOCK_START:
                    continue
                n = sum(1 for _ in p.open(encoding="utf-8", errors="replace"))
            except Exception:                       # noqa: BLE001 -- an unreadable file is not a count
                continue
            k = f"{p.parent.name}/{p.name}"
            best[k] = max(best.get(k, 0), n)
    return best


def a_post_split(r):
    """POST_ROUND trap: the controller posts as lane A. Subtract '^EPOCH <n> boundary' notes."""
    ctrl = cond = 0
    for _mid, f in r.xrange("pm:swarm", min=str(int(CLOCK_START * 1000))):
        if f.get("lane") != "A":
            continue
        if re.match(r"^EPOCH \d+ (boundary|NO_NEW_WORK)|^ROUND ", f.get("subject", "")):
            ctrl += 1
        else:
            cond += 1
    return ctrl, cond


def pc_in_window(r):
    """PC stream length is ALL TIME. Count only ids inside the round's window."""
    lo = int(CLOCK_START * 1000)
    total = r.xlen("pm:production_candidates")
    inside = sum(1 for mid, _f in r.xrange("pm:production_candidates", min=str(lo)))
    return total, inside


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehearse", action="store_true")
    ap.add_argument("--emit", action="store_true")
    a = ap.parse_args(argv)
    if not (a.rehearse or a.emit):
        ap.error("pass --rehearse or --emit")

    from primordial.bus import bus
    r = bus.conn()
    checks, out = 0, []
    t0 = time.time()
    print(f"=== R8 CLOSE ({'EMIT' if a.emit else 'REHEARSAL'}) === {time.strftime('%Y-%m-%d %H:%M:%S')}")

    step_ff(out)
    step_round_closed(r, out, a.emit)

    # -- FINALs: A's packet is generated from these; prose may NOT be the source of counts
    finals = {}
    fdir = GW / "finals_r8"
    for L in LANES:
        p = fdir / f"{L}.json"
        finals[L] = p.exists()
    missing = [L for L, ok in finals.items() if not ok]
    out.append(("finals_present", not missing, f"have={sorted(L for L,ok in finals.items() if ok)} missing={missing}"))

    replays = sorted(p.name for p in (GW / "replay_r8").glob("*.json")) if (GW / "replay_r8").is_dir() else []
    out.append(("replays_present", bool(replays), f"{len(replays)}: {replays}"))

    for f in ("ROUND8_CLOCK.json", "GATE_MAP_R8.json", "R8_DISPUTES.json", "R8_PACKET_GUARDS.json"):
        out.append((f"record_{f}", (GW / f).exists(), str((GW / f).exists())))

    # -- close_sweep: THE receipt-integrity check. --emit only when the round is closed.
    # close_sweep prints ONE json doc whose tail is a brace -- reading the last line told me nothing but "}".
    # Parse it and report the fields POST_ROUND names: rows_files, cited, unreceipted, emitted, ok.
    # Mid-round rc=1 is EXPECTED: rows exist before their receipts while jobs are still in flight. At the real
    # close it is a hard failure, so the check is informational under --rehearse and binding under --emit.
    cmd = [PY, "-m", "primordial.score.close_sweep", "--round", ROUND] + (["--emit"] if a.emit else [])
    s = _run(cmd, timeout=900)
    raw = (s.stdout or "").strip()
    try:
        doc = json.loads(raw) if raw.startswith("{") else json.JSONDecoder().raw_decode(raw[raw.find("{"):])[0]
    except Exception:                               # noqa: BLE001 -- unparseable output is itself the finding
        doc = {}
    unrec = doc.get("unreceipted") or []
    detail = (f"rc={s.returncode} rows_files={doc.get('rows_files')} cited={doc.get('cited')} "
              f"unreceipted={len(unrec)}{' ' + str([e.get('path','').rsplit('/',1)[-1] for e in unrec][:4]) if unrec else ''} "
              f"emitted={len(doc.get('emitted') or [])} ok={doc.get('ok')}")
    if not doc:
        detail = f"rc={s.returncode} | UNPARSEABLE close_sweep output: {raw[:120]!r}"
    clean = s.returncode == 0 and not unrec
    out.append(("close_sweep", clean if a.emit else bool(doc),
                detail + ("" if a.emit else "   [rehearsal: unreceipted rows are EXPECTED while jobs run]")))

    # -- residue: rc 1 with pending-0 dead consumers is EXPECTED at close, not a failure
    rs = _run([PY, "-m", "primordial.ops.residue", "scan", "--round", ROUND], timeout=300)
    try:
        scan = json.loads((rs.stdout or "{}").strip().splitlines()[-1])
        kinds = sorted({x.get("kind") for x in scan.get("residue", [])})
        only_dead = kinds in ([], ["DEAD_CONSUMER"])
        out.append(("residue_expected_shape", only_dead,
                    f"rc={rs.returncode} kinds={kinds} n={len(scan.get('residue', []))} (rc 1 + DEAD_CONSUMER is EXPECTED)"))
    except Exception as e:                          # noqa: BLE001
        out.append(("residue_expected_shape", False, f"unparseable: {type(e).__name__}"))

    for name, ok, detail in out:
        checks += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")

    # ---------------------------------------------------------------- the numbers, derived
    print("\n-- ROWS (deduplicated by file; a per-worktree sum double-counts committed rows) --")
    rows = rows_deduplicated()
    for k in sorted(rows):
        print(f"   {k:56s} {rows[k]:5d}")
    print(f"   distinct rows files: {len(rows)} | TOTAL ROWS: {sum(rows.values())}")
    checks += 1

    print("\n-- JOBS per lane (r8 delta is measured against the recorded r7 baseline) --")
    base = json.loads((pathlib.Path(__file__).parent / "r8_job_baseline.json").read_text()) \
        if (pathlib.Path(__file__).parent / "r8_job_baseline.json").exists() else {}
    for L in LANES:
        sub = r.xlen(f"pm:jobs:{L}") - base.get(f"pm:jobs:{L}", 0)
        done = r.xlen(f"pm:jobs:{L}:done") - base.get(f"pm:jobs:{L}:done", 0)
        if sub or done:
            print(f"   {L}: submitted {sub}  done {done}")
    checks += 1

    ctrl, cond = a_post_split(r)
    print(f"\n-- LANE A POSTS: {ctrl + cond} total = {ctrl} controller boundary + {cond} CONDUCTOR actions --")
    total_pc, inside = pc_in_window(r)
    print(f"-- PRODUCTION CANDIDATES: {inside} in this round's id window ({total_pc} all-time on the stream) --")
    checks += 2

    print("\n-- HOST, QUERIED NOT RECALLED --")
    hw = _run([PY, "-c", "import platform,psutil;print(platform.platform(),'|',psutil.cpu_count(logical=False),"
                         "'physical /',psutil.cpu_count(),'logical |',round(psutil.virtual_memory().total/2**30,1),'GB')"])
    print(f"   {(hw.stdout or hw.stderr).strip()[:160]}")
    checks += 1

    ok_all = all(o for _n, o, _d in out)
    print(f"\nchecks run: {checks}")
    print(f"preconditions: {'PASS' if ok_all else 'FAIL'} | elapsed {round(time.time()-t0,2)}s")
    if a.rehearse:
        print("REHEARSAL: nothing emitted, no UNRECEIPTED_OBSERVATION written")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
