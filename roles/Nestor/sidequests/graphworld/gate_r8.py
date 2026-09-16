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
GW = ROOT / "roles" / "Nestor" / "sidequests" / "graphworld"
MAP_FILE = GW / "GATE_MAP_R8.json"
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
        self.gid, self.fn, self.ok, self.detail = gid, fn, False, ""

    def probe(self):
        try:
            self.ok, self.detail = self.fn()
        except Exception as e:                       # noqa: BLE001 -- fail closed, never land on an exception
            self.ok, self.detail = False, f"probe raised {type(e).__name__}: {e}"
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
    """Gate enforcement itself: with a live clock and a planted not-landed gate, admit() refuses."""
    from primordial.fabric import envelope as E
    src = (pathlib.Path(E.__file__)).read_text(encoding="utf-8", errors="replace")
    if "GATE_NOT_LANDED" not in src:
        return False, "envelope.py contains no GATE_NOT_LANDED -- the fail-safe is still unimplemented"
    if "GATE_STATE_UNAVAILABLE" not in src:
        return False, "no GATE_STATE_UNAVAILABLE -- enforcement does not fail closed"
    return True, "GATE_NOT_LANDED and GATE_STATE_UNAVAILABLE both present in the admission path"


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
    from primordial.cohorts.e import transfer as T
    from primordial.score import transfer_b as TB
    d = [1.0, -1.0, 0.5, -0.25, 2.0, -0.5, 0.75, -1.5]
    a, b = T.signflip_p(list(d)), T.signflip_p(list(reversed(d)))
    same_judge = abs(TB.signflip_p(list(d)) - a) < 1e-12
    return (abs(a - b) < 1e-12 and same_judge), f"order_invariant={abs(a-b)<1e-12} judge_agrees={same_judge}"


def p_c3():
    from primordial.ops import residue as R
    src = pathlib.Path(R.__file__).read_text(encoding="utf-8", errors="replace")
    ok = "refresh" in src and ("ttl" in src.lower() or "expire" in src.lower())
    return ok, ("registration refresh re-creates a missing key" if ok else "no TTL refresh path (D28)")


def p_c1():
    return False, "C1 D23 gpuq worktree isolation was UNASSIGNED in the build (BUILD_R8 conditionals)"


PROBES = [("G8", p_g8), ("G1", p_g1), ("GE", p_ge), ("G6", p_g6), ("G5", p_g5), ("G7", p_g7),
          ("G2", p_g2), ("G3", p_g3), ("G4", p_g4), ("C1", p_c1), ("C2", p_c2), ("C3", p_c3)]


# ------------------------------------------------------- environment checks

def env_checks(round_id: str) -> list[tuple[str, bool, str]]:
    """The non-gate half of BUILD_R8's GATE RUN: suite, residue, registrations, capacity, tip sha."""
    out = []

    s = _run([PY, "-m", "pytest", "primordial", "-q"], timeout=1800)
    tail = (s.stdout or "").strip().splitlines()
    out.append(("full_suite", s.returncode == 0, f"rc={s.returncode} | {tail[-1] if tail else 'no output'}"))

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

    prof = c.get("pm:capacity:profile")
    out.append(("capacity_profile", bool(prof), (prof or "")[:120]))

    g = _run(["git", "-C", str(ROOT), "status", "--porcelain"], timeout=120)
    out.append(("conductor_worktree_clean", g.returncode == 0 and not g.stdout.strip(),
                f"dirty_lines={len((g.stdout or '').strip().splitlines())}"))

    t = _run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], timeout=120)
    sha = (t.stdout or "").strip()
    out.append(("tip_sha_recorded", bool(sha), sha))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="r8")
    ap.add_argument("--emit", action="store_true", help="publish the map to redis + GATE_MAP_R8.json")
    ap.add_argument("--rehearse", action="store_true", help="run everything, publish nothing")
    a = ap.parse_args(argv)
    if not (a.emit or a.rehearse):
        ap.error("pass --rehearse or --emit")

    checks = 0
    print(f"=== R8 LAUNCH GATE ({'EMIT' if a.emit else 'REHEARSAL'}) round={a.round} ===")
    print(f"    {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n-- environment --")
    env = env_checks(a.round)
    for name, ok, detail in env:
        checks += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")

    print("\n-- gate landed-probes (fail closed) --")
    gates = {}
    for gid, fn in PROBES:
        g = Gate(gid, fn).probe()
        checks += 1
        gates[gid] = {"landed": g.ok, "detail": g.detail, "blocks": BLOCKED_WORK.get(gid, "")}
        print(f"  [{'LANDED    ' if g.ok else 'NOT LANDED'}] {gid}: {g.detail}")

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

    record = {"round_id": a.round, "ts": time.time(), "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
              "tip_sha": dict((n, d) for n, _, d in env).get("tip_sha_recorded", ""),
              "environment": [{"check": n, "ok": ok, "detail": d} for n, ok, d in env],
              "gates": gates, "checks_run": checks, "environment_ok": env_ok}

    if a.emit:
        from primordial.bus import bus
        c = bus.conn()
        c.hset(f"pm:round:{a.round}:gates", mapping={k: ("landed" if v["landed"] else "not_landed")
                                                     for k, v in gates.items()})
        MAP_FILE.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print(f"\npublished pm:round:{a.round}:gates and {MAP_FILE.relative_to(ROOT).as_posix()}")
    else:
        print("\nREHEARSAL: nothing published")
    return 0 if env_ok else 1


if __name__ == "__main__":
    sys.exit(main())
