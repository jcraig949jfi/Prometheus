"""R8 LAUNCH GATE (lane A, logistics only). Implements BUILD_R8 "GATE RUN" items 1-8.

Lives in the sidequest directory, NOT in primordial/ops/, because ops/ is Q's exclusive
file ownership this round (R16) and the conductor does not edit a builder's files.

Two rules this script exists to obey:
  R17  gate output reports the NUMBER OF CHECKS EXECUTED, not merely PASS/FAIL.
  3a   every check is a quoted heredoc / real subprocess with its OWN rc captured --
       never a pipe's rc, never a shell-interpolated python -c.

A gate is LANDED only if its behavioural probe passes. Probes are BEHAVIOURAL, not
name-based, because builders name their own tests. Every probe is wrapped so that an
exception marks the gate NOT LANDED: nothing may be landed by accident (fail closed).

    python roles/Nestor/sidequests/graphworld/gate_r8.py --rehearse
    python roles/Nestor/sidequests/graphworld/gate_r8.py --emit

--rehearse  runs every check and prints the map; publishes NOTHING.
--emit      additionally publishes pm:round:<round>:gates and writes GATE_MAP_R8.json.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[4]
# REHEARSAL FINDING (09:02 local, pre-T0, and exactly why the rehearsal exists): run as a script, python
# puts THIS FILE's directory on sys.path -- not the repo root. So every subprocess check passed (they are
# given cwd=ROOT) and the 4-minute suite really ran, and then the first in-process `from primordial...`
# died with ModuleNotFoundError. At 10:15 the gate would have failed AFTER spending its whole budget.
# Fix the path before any primordial import, not after.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
GW = ROOT / "roles" / "Nestor" / "sidequests" / "graphworld"
def map_file(round_id: str) -> pathlib.Path:
    """Per-round path. A hardcoded GATE_MAP_R8.json meant a run with any other --round silently
    overwrote r8's map -- the same 'round id not honoured' family as G8, in my own runner. It also
    made it unsafe to rehearse --emit, which is the one path that would otherwise execute for the
    first time at the real gate."""
    return GW / f"GATE_MAP_{round_id.upper()}.json"
PY = r"C:\Users\jcrai\lab\gw-venv\Scripts\python.exe"
INTEGRATION = "nestor/sidequest-graphworld-2026-09-14"

# SWARM_R8 s3 / BOOT_R8 s3. "blocks" is what admission refuses when the gate is NOT landed.
BLOCKED_WORK = {
    "G8": "THE CLOCK ITSELF, therefore everything",
    "G1": "ALL row-emitting science (expected_output_rows > 0)",
    "GE": "nothing directly -- but without it NO gate refusal is enforced at all",
    "G2": "all new anti-prior draws (experiment_class ANTI_PRIOR) and the BETA sweep",
    "G3": "shared-CPU multi-lane science",
    "G4": "nothing in-round; blocks CLOSE correctness",
    "G5": "nothing; but a round without it fails its own mission",
    "G6": "nothing directly; WHY_NOT_RUN and residue records need hand-written stubs",
    "G7": "nothing directly; without it the round's telemetry does not survive the round",
    "C1": "cross-lane GPU work (kind == 'gpu')",
    "C2": "any verdict depending on the MC signflip branch",
    "C3": "long-lived registered services",
}


def _run(args, timeout=1800, cwd=None):
    """A subprocess whose OWN returncode is what we read. No pipes, no shell."""
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=str(cwd or ROOT))


class Gate:
    """One check. .ok is False unless the probe explicitly returns True."""

    def __init__(self, gid, fn):
        self.gid, self.fn, self.ok, self.detail, self.secs = gid, fn, False, "", 0.0

    def probe(self):
        t0 = time.time()
        try:
            self.ok, self.detail = self.fn()
        except Exception as e:                       # noqa: BLE001 -- fail closed, never land on an exception
            self.ok, self.detail = False, f"probe raised {type(e).__name__}: {e}"
        self.secs = round(time.time() - t0, 2)
        return self


# ---------------------------------------------------------------- gate probes

def p_g8():
    """r8 row exists, returns the ruled 12 epochs, and an unknown round id FAILS CLOSED (R18)."""
    from primordial.ops import round_clock as RC
    if "r8" not in getattr(RC, "ROUNDS", {}):
        return False, "ROUNDS['r8'] absent -- plan() would silently fall back to DEFAULT_ROUND"
    p = RC.plan(time.time(), round_id="r8")
    if p.get("epochs") != 12 or float(p.get("epoch_s")) != 3600.0:
        return False, f"plan(r8) epochs={p.get('epochs')} epoch_s={p.get('epoch_s')}, want 12 / 3600.0"
    try:
        RC.plan(time.time(), round_id="r9")
    except Exception:
        pass                                          # raising is the requirement
    else:
        return False, "plan(r9) did NOT raise -- unknown round ids must fail closed (R18)"
    repos = (RC.ROUNDS["r8"].get("lane_repos") or {})
    missing = [L for L in ("B", "C", "D", "E", "G", "R", "H", "F", "P", "Q", "A") if L not in repos]
    if missing:
        return False, f"lane_repos incomplete, missing {missing} (FOREIGN_REPO would fire on a legitimate lane)"
    return True, f"epochs 12, r9 raises, lane_repos declares {len(repos)} lanes"


def p_g1():
    """A row outside the frozen vocabulary must fail LOUDLY, not one row at a time under an ok job."""
    from primordial.fabric import envelope as E
    for name in ("vocabulary_reasons", "validate_rows", "row_vocabulary_reasons", "check_row_vocabulary"):
        if hasattr(E, name):
            return True, f"envelope.{name} present (vocabulary refusal path)"
    return False, "no row-vocabulary refusal entrypoint found in envelope"


def p_ge():
    """R8 GE, the fail-safe the whole gate map rests on -- probed BEHAVIOURALLY.

    The first version grepped envelope.py for the two token names. That is the identical weak pattern
    that false-greened C2 and C3 on top of live defects this morning, and a false green HERE is the worst
    of all: the gate map would look enforced while nothing enforced it.

    F's implementation takes an injectable `gates=` dict, so state is planted IN-PROCESS -- no redis
    write, no cleanup, no contamination. The fail-closed case uses round id r99, which has no committed
    map file, so it stays deterministic even after the real gate writes GATE_MAP_R8.json at 10:15.
    """
    from primordial.fabric import envelope as E
    now = time.time()

    def clk(rid):
        return {"round_id": rid, "stage": "PILOT", "start_ts": now - 10.0, "epoch_s": 3600.0, "epochs": 12,
                "no_new_work_ts": now + 10000.0, "drain_ts": now + 20000.0, "end_ts": now + 30000.0}

    env = E.example(expected_output_rows=1)                      # rows > 0 -> G1 blocks it
    ALL = {g: "landed" for g in E.GATE_BLOCKS}
    checks = []

    # 1. BUILD phase (no clock) must not refuse -- or the gate refuses the very work that lands it.
    checks.append(("no_clock_no_refusal", E.gate_reasons(env, "cpu", None) == []))

    # 2. A planted not-landed blocking gate refuses at admission, as GATE_REFUSAL, with NO candidate stub.
    v = E.admit(env, "cpu", clock=clk("r8"), now=now, gates={**ALL, "G1": "not_landed"})
    checks.append(("g1_refused_zero_cpu", v["ok"] is False and f"{E.GATE_NOT_LANDED}:G1" in v["reasons"]
                   and v.get("event") == E.GATE_REFUSAL and v.get("stub") is False))

    # 3. With every gate landed, nothing is refused on gate grounds.
    v2 = E.admit(env, "cpu", clock=clk("r8"), now=now, gates=ALL)
    checks.append(("all_landed_admits",
                   not [x for x in v2["reasons"] if str(x).startswith(E.GATE_NOT_LANDED)]))

    # 4. FAIL CLOSED: unreadable/absent state under a live campaign clock refuses, never admits.
    checks.append(("fail_closed_when_state_absent",
                   E.gate_reasons(env, "cpu", clk("r99")) == [E.GATE_STATE_UNAVAILABLE]))

    # 5. Kind-specific topology: C1 blocks gpu work only.
    genv = E.example(expected_output_rows=0, gpu_budget_s=60)
    checks.append(("c1_blocks_gpu", f"{E.GATE_NOT_LANDED}:C1"
                   in E.gate_reasons(genv, "gpu", clk("r8"), {**ALL, "C1": "not_landed"})))

    bad = [n for n, ok in checks if not ok]
    return (not bad), (f"{len(checks)}/{len(checks)} behavioural: no-clock, G1 refusal at zero CPU, "
                       f"all-landed admits, fail-closed, C1 gpu-only" if not bad
                       else f"BEHAVIOURAL FAILURES: {bad}")


def p_g6():
    from primordial.fabric import envelope as E
    return (hasattr(E, "open_candidate"),
            "envelope.open_candidate present" if hasattr(E, "open_candidate") else "open_candidate absent (D27)")


def p_g5():
    from primordial.fabric import worker as W
    src = pathlib.Path(W.__file__).read_text(encoding="utf-8", errors="replace")
    need = ("queue_enter_ts", "grant_ts", "wait_s", "queue_position", "continuation")
    missing = [f for f in need if f not in src]
    return (not missing), ("all five queue fields emitted" if not missing else f"missing queue fields {missing}")


def p_g7():
    from primordial.ops import bus_export as B
    src = pathlib.Path(B.__file__).read_text(encoding="utf-8", errors="replace")
    has_done = ":done" in src or "jobs_done" in src
    has_cursor = "cursor" in src.lower()
    if has_done and has_cursor:
        return True, "done-stream export plus per-stream cursor present"
    return False, f"done_stream={has_done} cursor={has_cursor} (ADAPT-15 / R14 incomplete)"


def p_g2():
    from primordial.score import anti_prior as A
    for name in ("binding_precheck", "cell_binding_precheck", "precheck", "eligible_cell"):
        if hasattr(A, name):
            return True, f"anti_prior.{name} present (cell-binding pre-check)"
    return False, "no cell-binding pre-check entrypoint in anti_prior"


def p_g3():
    from primordial.fabric import broker as B
    src = pathlib.Path(B.__file__).read_text(encoding="utf-8", errors="replace")
    has_cont = "continuation" in src
    has_wait = "queue_enter_ts" in src or "wait_s" in src
    return (has_cont and has_wait), f"continuation_priority={has_cont} queue_telemetry={has_wait}"


def p_g4():
    from primordial.ops import epoch as EP
    src = pathlib.Path(EP.__file__).read_text(encoding="utf-8", errors="replace")
    ok = "protocol" in src.lower() and ("watch" in src.lower() or "beacon" in src.lower())
    return ok, ("close/watch protocol lint present" if ok else "no close/watch protocol lint in epoch.py")


def p_c2():
    """D25 is canonical ordering in the MONTE CARLO branch, so the probe MUST reach that branch.

    The first version of this probe used an 8-element vector and reported LANDED. That was a false
    green: r7's own tests pin `signflip_method(20) == "exact"`, and the exact branch enumerates all
    2^n sign assignments, so it is order-invariant for free. The probe passed without ever executing
    the code D25 is about. Use n=32, where the r7 tests show the MC floor 1/(SIGNFLIP_DRAWS+1) is
    used, and require the SEEDED result to survive a permutation of its input -- which is what
    canonical ordering means. If the MC branch cannot be reached, REFUSE rather than pass.
    """
    import random
    from primordial.cohorts.e import transfer as T
    from primordial.score import transfer_b as TB
    if T.signflip_method(32) == "exact":
        return False, "probe cannot reach the MC branch at n=32 (signflip_method reports exact) -- D25 untested"
    d = [((-1) ** i) * (0.25 + 0.5 * i) for i in range(32)]
    s = list(d)
    random.Random(20260916).shuffle(s)
    a, b = T.signflip_p(list(d)), T.signflip_p(s)
    order_ok = abs(a - b) < 1e-12
    judge_ok = abs(TB.signflip_p(list(d)) - a) < 1e-12
    return (order_ok and judge_ok), f"MC n=32 order_invariant={order_ok} judge_agrees={judge_ok} p={a:.6g}"


def p_c3():
    """D28: a job outliving REG_TTL loses its registration, and refresh() must RE-CREATE the missing key.

    The previous probe grepped residue.py for "refresh" and "ttl" -- the same source-text pattern that
    false-greened C2 on a live defect. Measured on this tip instead: `refresh(r, key)` is exactly
    `r.expire(key, REG_TTL)` with REG_TTL = 90, and redis EXPIRE on a MISSING key returns 0 and creates
    nothing. So the only honest question is behavioural: after the key is gone, does refresh bring the
    registration back?

    Cleans up in a finally: a stray pm:worker:reg:* key would break the gate's own zero_registrations
    check and be reported as residue by the scanner.
    """
    from primordial.bus import bus
    from primordial.ops import residue as RS
    r = bus.conn()
    key = None
    try:
        key = RS.register(r, "H", "F:/Prometheus-worktrees/nestor-bld-h",
                          round_id="gate-probe", tag="gate-probe-c3")
        r.delete(key)                                   # simulate REG_TTL elapsing mid-job
        RS.refresh(r, key)
        revived = bool(r.exists(key))
        return revived, ("refresh re-created the expired registration" if revived else
                         "refresh did NOT re-create the expired key -- D28 present "
                         "(EXPIRE on a missing key is a no-op)")
    finally:
        if key:
            r.delete(key)


def p_c1():
    return False, "C1 D23 gpuq worktree isolation was UNASSIGNED in the build (BUILD_R8 conditionals)"


PROBES = [("G8", p_g8), ("G1", p_g1), ("GE", p_ge), ("G6", p_g6), ("G5", p_g5), ("G7", p_g7),
          ("G2", p_g2), ("G3", p_g3), ("G4", p_g4), ("C1", p_c1), ("C2", p_c2), ("C3", p_c3)]


# ------------------------------------------------------- environment checks

def env_checks(round_id: str, skip_suite: bool = False, since_sha: str = "") -> list[tuple[str, bool, str]]:
    """The non-gate half of BUILD_R8's GATE RUN: suite, residue, registrations, capacity, tip sha."""
    out = []

    if skip_suite:
        # Deliberately counted as a FAILED check, never a silent omission: a gate that quietly
        # drops a check is exactly the failure mode R17 and POST_ROUND s3a name.
        out.append(("full_suite", False, "SKIPPED via --skip-suite (not a pass; never use at the real gate)"))
    else:
        s = _run([PY, "-m", "pytest", "primordial", "-q"], timeout=1800)
        tail = (s.stdout or "").strip().splitlines()
        out.append(("full_suite", s.returncode == 0, f"rc={s.returncode} | {tail[-1] if tail else 'no output'}"))

    # BUILD_R8 GATE RUN item 2: every test file added or modified in the build window RUNS.
    # This is the answer to the remaining source-text probes (G1/G3/G4/G5/G7): a grep can be fooled by a
    # builder writing a field name in a comment -- two such probes already false-greened live defects
    # (D25, D28) during this prep. The builders' own regression tests are what actually exercise those gates.
    if since_sha:
        d = _run(["git", "-C", str(ROOT), "diff", "--name-only", f"{since_sha}..HEAD"], timeout=120)
        changed = sorted(x for x in (d.stdout or "").split()
                         if x.endswith(".py") and "test" in x.rsplit("/", 1)[-1].lower())
        if not changed:
            out.append(("discovered_build_tests", False,
                        f"NO test file changed since {since_sha[:9]} -- a build that shipped no regression "
                        f"test is itself a finding (every brief required one per item)"))
        else:
            t = _run([PY, "-m", "pytest", *changed, "-q"], timeout=1800)
            tl = (t.stdout or "").strip().splitlines()
            out.append(("discovered_build_tests", t.returncode == 0,
                        f"{len(changed)} file(s) rc={t.returncode} | {tl[-1] if tl else 'no output'} | {changed}"))
    else:
        out.append(("discovered_build_tests", False,
                    "no --since-sha given, so GATE RUN item 2 did NOT execute; counted as a failed check "
                    "rather than silently omitted"))

    # BUILD_R8 GATE RUN item 3: the planted EVIDENCE_N_v1 refusals -- 16/1/16, 32/4/(16,8,4,4),
    # 32/4/(29,1,1,1) -- refused at ADMISSION with ZERO rows.
    #
    # Deliberately NOT reimplemented here. primordial/tests/test_r7_h1_evidence_admission.py already
    # drives the REAL worker and asserts zero rows AND no PRODUCTION_CANDIDATE stub (D16); an in-process
    # admit() call in this file could assert neither. A weaker duplicate that looked reassuring while
    # testing less is exactly the "verification not aimed at the claim" failure this gate exists to stop.
    #
    # The residual risk is a builder DELETING or SKIPPING those tests, which "full suite green" would
    # report as success -- the shrinking-check-set trap (POST_ROUND s3a). So: run them BY NAME, require
    # that tests actually passed (rc 5 means nothing was collected; an all-skipped run is a vacuous
    # green), and fail loudly if a required file has vanished.
    planted = ["primordial/tests/test_r7_h1_evidence_admission.py",
               "primordial/tests/test_score_evidence_n.py"]
    gone = [p for p in planted if not (ROOT / p).exists()]
    if gone:
        out.append(("planted_evidence_refusals", False,
                    f"REQUIRED TEST FILE(S) MISSING -- a hard gate check was deleted: {gone}"))
    else:
        t = _run([PY, "-m", "pytest", *planted, "-q"], timeout=900)
        tl = (t.stdout or "").strip().splitlines()
        last = tl[-1] if tl else "no output"
        out.append(("planted_evidence_refusals", t.returncode == 0 and " passed" in last,
                    f"rc={t.returncode} | {last}"))

    # BUILD_R8 GATE RUN item 4: G1's vocabulary lint and G4's protocol lint must RUN and PASS.
    # The argvs come from their OWNERS on the bus -- F 1789565285343-0 and Q 1789565200695-0 -- not from me.
    # Guessing an entrypoint is the score/signflip* error, and a lint retrofitted after the cap is not allowed.
    # A missing module or subcommand simply returns non-zero and is recorded as a FAILED check: that is the
    # correct fail-closed reading of "the lint did not land", and it needs no special case.
    for cid, argv in (("G1_vocabulary_lint", [PY, "-m", "primordial.fabric.envelope", "lint"]),
                      ("G4_protocol_lint", [PY, "-m", "primordial.ops.epoch", "lint", "--self-test"])):
        lt = _run(argv, timeout=600)
        ll = [x for x in ((lt.stdout or "") + (lt.stderr or "")).strip().splitlines() if x.strip()]
        out.append((cid, lt.returncode == 0, f"rc={lt.returncode} | {ll[-1][:120] if ll else 'no output'}"))

    r = _run([PY, "-m", "primordial.ops.residue", "scan", "--round", round_id], timeout=300)
    try:
        scan = json.loads((r.stdout or "{}").strip().splitlines()[-1])
        clean = bool(scan.get("ok"))
        detail = f"residue={len(scan.get('residue') or [])}"
    except Exception:
        clean, detail = False, f"unparseable residue scan rc={r.returncode}"
    out.append(("residue_scan_clean", clean, detail))

    from primordial.bus import bus
    c = bus.conn()
    regs = len(c.keys("pm:worker:reg:*"))
    stops = len(c.keys("pm:stop*")) + len(c.keys("pm:*:stop"))
    out.append(("zero_registrations", regs == 0, f"registrations={regs}"))
    out.append(("zero_stop_flags", stops == 0, f"stop_flags={stops}"))

    # GATE RUN item 6: present AND readable. Truthiness alone would pass a malformed profile. The broker
    # itself cannot be probed here -- broker.py is P's file and is being edited right now -- so validate the
    # DATA the broker depends on: it must parse, and carry k_star and threads_per_worker as numbers.
    prof = c.get("pm:capacity:profile")
    try:
        pj = json.loads(prof) if prof else {}
        need = ("k_star", "threads_per_worker")
        miss = [k for k in need if not isinstance(pj.get(k), (int, float)) or isinstance(pj.get(k), bool)]
        ok_prof, why = (not miss), (f"{pj.get('exp')} k*={pj.get('k_star')} threads={pj.get('threads_per_worker')}"
                                    if not miss else f"profile parsed but missing/non-numeric {miss}")
    except Exception as e:                              # noqa: BLE001 -- unparseable is a failed check, not a crash
        ok_prof, why = False, f"profile does not parse as JSON ({type(e).__name__}): {(prof or '')[:80]}"
    out.append(("capacity_profile", ok_prof, why))

    g = _run(["git", "-C", str(ROOT), "status", "--porcelain"], timeout=120)
    out.append(("conductor_worktree_clean", g.returncode == 0 and not g.stdout.strip(),
                f"dirty_lines={len((g.stdout or '').strip().splitlines())}"))

    # POST_ROUND s1: ff BEFORE every sweep. In r7 a stale checkout produced a false "zero cited" alarm,
    # broadcast to seven lanes before the conductor discovered its own checkout was 205 commits behind.
    # Here the cost is worse than a wrong count: gating a stale checkout reports gates NOT LANDED that DID
    # land, and under BOOT_R8 s3 a missed gate is PERMANENT for the round -- real science refused on a
    # bookkeeping error. Measured during the build window: builders push repeatedly, so A goes behind
    # within minutes.
    # The gate REFUSES rather than fast-forwarding itself. A verification step must not mutate the thing
    # it verifies, and silently moving the branch mid-gate would hide exactly this condition.
    _run(["git", "-C", str(ROOT), "fetch", "origin", "--quiet"], timeout=300)
    b = _run(["git", "-C", str(ROOT), "rev-list", "--count", f"HEAD..origin/{INTEGRATION}"], timeout=120)
    behind = (b.stdout or "").strip()
    out.append(("worktree_current_with_origin", behind == "0",
                f"behind_origin={behind or '?'}" + ("" if behind == "0" else
                " -- FAST-FORWARD BEFORE GATING; gates that landed would report NOT LANDED")))

    t = _run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], timeout=120)
    sha = (t.stdout or "").strip()
    out.append(("tip_sha_recorded", bool(sha), sha))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="r8")
    ap.add_argument("--emit", action="store_true", help="publish the map to redis + GATE_MAP_R8.json")
    ap.add_argument("--rehearse", action="store_true", help="run everything, publish nothing")
    ap.add_argument("--since-sha", default="",
                    help="pre-build tip; every test file changed since it is RUN (GATE RUN item 2). "
                         "R8 build started at 6c02b89a9.")
    ap.add_argument("--skip-suite", action="store_true",
                    help="skip the 4-minute full suite while builders hold the CPU; counted as a FAILED "
                         "check, so a run using it can never report a clean environment. NEVER at the real gate.")
    a = ap.parse_args(argv)
    if not (a.emit or a.rehearse):
        ap.error("pass --rehearse or --emit")

    checks = 0
    print(f"=== R8 LAUNCH GATE ({'EMIT' if a.emit else 'REHEARSAL'}) round={a.round} ===")
    print(f"    {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # The gate has a HARD 20 min budget and the clock is cap-anchored, so every second it overruns is
    # charged to SCIENCE. POST_ROUND s3: that number gets DERIVED, never recalled -- so time it here.
    t_start = time.time()

    print("\n-- environment --")
    t_env0 = time.time()
    env = env_checks(a.round, skip_suite=a.skip_suite, since_sha=a.since_sha)
    env_secs = round(time.time() - t_env0, 2)
    for name, ok, detail in env:
        checks += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    print(f"  (environment phase: {env_secs}s)")

    print("\n-- gate landed-probes (fail closed) --")
    t_probe0 = time.time()
    gates = {}
    for gid, fn in PROBES:
        g = Gate(gid, fn).probe()
        checks += 1
        gates[gid] = {"landed": g.ok, "detail": g.detail, "blocks": BLOCKED_WORK.get(gid, ""),
                      "secs": g.secs}
        print(f"  [{'LANDED    ' if g.ok else 'NOT LANDED'}] {gid}: {g.detail}  ({g.secs}s)")
    probe_secs = round(time.time() - t_probe0, 2)
    print(f"  (probe phase: {probe_secs}s)")

    print("\n-- gate -> blocked work map --")
    not_landed = [k for k, v in gates.items() if not v["landed"]]
    for gid in not_landed:
        print(f"  {gid} NOT LANDED -> REFUSED FOR THE ROUND: {gates[gid]['blocks']}")
    if not not_landed:
        print("  every gate landed; nothing is refused by the gate map")

    env_ok = all(ok for _, ok, _ in env)
    print(f"\nchecks run: {checks}")
    print(f"expected: {len(env)} environment + {len(PROBES)} gates = {len(env) + len(PROBES)}")
    print(f"environment: {'PASS' if env_ok else 'FAIL'} | gates landed: "
          f"{len(gates) - len(not_landed)}/{len(gates)} | not landed: {not_landed or 'none'}")

    total_secs = round(time.time() - t_start, 2)
    print(f"elapsed: {total_secs}s total ({env_secs}s environment + {probe_secs}s probes) "
          f"against the 20 min = 1200s gate budget")

    record = {"round_id": a.round, "ts": time.time(), "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
              "timings": {"total_secs": total_secs, "environment_secs": env_secs, "probe_secs": probe_secs,
                          "gate_budget_secs": 1200, "within_budget": total_secs <= 1200},
              "tip_sha": dict((n, d) for n, _, d in env).get("tip_sha_recorded", ""),
              "environment": [{"check": n, "ok": ok, "detail": d} for n, ok, d in env],
              "gates": gates, "checks_run": checks, "environment_ok": env_ok}

    if a.emit:
        from primordial.bus import bus
        c = bus.conn()
        c.hset(f"pm:round:{a.round}:gates", mapping={k: ("landed" if v["landed"] else "not_landed")
                                                     for k, v in gates.items()})
        mf = map_file(a.round)
        mf.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print(f"\npublished pm:round:{a.round}:gates and {mf.relative_to(ROOT).as_posix()}")
    else:
        print("\nREHEARSAL: nothing published")
    return 0 if env_ok else 1


if __name__ == "__main__":
    sys.exit(main())
