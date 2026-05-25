"""
Icarus lineage utilities — clone, freeze, revert.

The immutable-cycle-lineage mechanism per spec v0.2 sect 3. Each cycle is a
frozen snapshot in cycles/cycle_<N>/. The loop starts each iteration by
cloning the last STABLE cycle's `code/` into a new cycle dir. After TDD +
adversarial + complexity checks:

  - All pass + at least one metric improved -> mark stable; pointer advances
  - Anything fails -> cycle parked (frozen for forensics); pointer unchanged

FIXED infrastructure -- Icarus does NOT modify this module. Only James does.
"""
from __future__ import annotations

import json
import shutil
import sys
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ICARUS_DIR = Path(r"D:\Prometheus\agents\icarus")
CYCLES_DIR = ICARUS_DIR / "cycles"
STATE_DIR = ICARUS_DIR / "state"

ITERATION_STATE = STATE_DIR / "iteration_n.json"
LAST_STABLE_STATE = STATE_DIR / "last_stable_cycle.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[lineage] read {path} failed: {e}", file=sys.stderr)
        return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _cycle_id(n: int) -> str:
    """Zero-padded 3-digit cycle id (000, 001, ...). 999 cap before
    transitioning to 4-digit; for Phase 0, 3 digits is sufficient."""
    if n < 1000:
        return f"{n:03d}"
    return str(n)


def cycle_path(cycle_n: int) -> Path:
    return CYCLES_DIR / f"cycle_{_cycle_id(cycle_n)}"


def current_iteration() -> int:
    data = _read_json(ITERATION_STATE, {"n": 0})
    return int(data.get("n", 0))


def increment_iteration() -> int:
    n = current_iteration() + 1
    _write_json(ITERATION_STATE, {"n": n, "updated_at": _now_iso()})
    return n


def last_stable_cycle_id() -> str:
    data = _read_json(LAST_STABLE_STATE, {"cycle_id": "000"})
    return str(data.get("cycle_id", "000"))


def last_stable_cycle_n() -> int:
    return int(last_stable_cycle_id())


def clone_from_stable(target_cycle_n: int) -> Path:
    """Copy cycles/cycle_<stable>/code/ -> cycles/cycle_<target>/code/.
    Write parent.json + meta.json. Returns the new cycle dir.

    Idempotent: if target dir already exists, returns it (caller handles
    daemon-restart recovery)."""
    stable_id = last_stable_cycle_id()
    stable_path = cycle_path(int(stable_id))
    target_path = cycle_path(target_cycle_n)

    if not stable_path.exists():
        raise RuntimeError(
            f"last_stable cycle {stable_id} not found at {stable_path}; "
            f"cannot clone. Bootstrap state may be corrupt."
        )

    if target_path.exists():
        return target_path  # daemon-restart recovery

    target_path.mkdir(parents=True, exist_ok=False)
    src_code = stable_path / "code"
    dst_code = target_path / "code"
    if src_code.exists():
        shutil.copytree(src_code, dst_code, dirs_exist_ok=False)
    else:
        dst_code.mkdir(exist_ok=False)

    _write_json(target_path / "parent.json", {
        "parent_cycle": stable_id,
        "parent_path": str(stable_path),
        "cloned_at": _now_iso(),
    })

    _write_json(target_path / "meta.json", {
        "cycle_id": f"icarus-cycle-{_cycle_id(target_cycle_n)}",
        "cycle_n": target_cycle_n,
        "tier_target": _read_json(STATE_DIR / "tier_target.json",
                                   {"tier": "R1"}).get("tier", "R1"),
        "tier_currently_passing": _read_json(
            STATE_DIR / "tier_currently_passing.json", {"tier": "R0"}
        ).get("tier", "R0"),
        "created_at": _now_iso(),
    })

    # Empty placeholder log file
    (target_path / "log.jsonl").touch()

    return target_path


def record_outcome(
    cycle_n: int,
    decision: str,
    reason: Optional[str] = None,
    details: Optional[dict] = None,
) -> None:
    """Write outcome.json. decision is one of: mark_stable, park, regress."""
    if decision not in ("mark_stable", "park", "regress"):
        raise ValueError(f"unknown decision: {decision}")
    out_path = cycle_path(cycle_n) / "outcome.json"
    _write_json(out_path, {
        "decision": decision,
        "reason": reason,
        "details": details or {},
        "recorded_at": _now_iso(),
    })


def freeze_cycle(cycle_n: int) -> None:
    """Mark cycle dir as immutable (best-effort on Windows -- the OS-level
    read-only flag is fragile; the convention is enforced by code that
    checks `frozen_at.json` before any write to a non-current-cycle dir)."""
    cp = cycle_path(cycle_n)
    if not cp.exists():
        return
    frozen_marker = cp / "frozen_at.json"
    _write_json(frozen_marker, {"frozen_at": _now_iso()})

    # Try to set OS-level read-only flag on files (best-effort).
    # Windows: SetFileAttributes via Path.chmod is partial. Skip if it
    # raises -- the convention-enforcement (checking frozen_at.json before
    # writes) is the real safeguard.
    try:
        for f in cp.rglob("*"):
            if f.is_file() and f.name != "frozen_at.json":
                try:
                    f.chmod(stat.S_IREAD)
                except Exception:
                    pass
    except Exception:
        pass


def is_frozen(cycle_n: int) -> bool:
    return (cycle_path(cycle_n) / "frozen_at.json").exists()


def mark_stable(cycle_n: int) -> None:
    """Advance the last_stable pointer to cycle_n."""
    _write_json(LAST_STABLE_STATE, {
        "cycle_id": _cycle_id(cycle_n),
        "marked_at": _now_iso(),
    })


def revert_to(cycle_n: int) -> None:
    """Manual revert path: repoint last_stable to an arbitrary older cycle.
    Caller is responsible for ensuring cycle_n exists and is sensible."""
    if not cycle_path(cycle_n).exists():
        raise RuntimeError(f"cannot revert to non-existent cycle {cycle_n}")
    mark_stable(cycle_n)


def list_parked_cycles(limit: int = 100) -> list[dict]:
    """Return parked cycles for wisdom-module consumption. Most-recent first."""
    out: list[dict] = []
    if not CYCLES_DIR.exists():
        return out
    for cp in sorted(CYCLES_DIR.iterdir(), reverse=True):
        if not cp.is_dir() or not cp.name.startswith("cycle_"):
            continue
        outcome_path = cp / "outcome.json"
        if not outcome_path.exists():
            continue
        try:
            o = json.loads(outcome_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if o.get("decision") == "park":
            out.append({
                "cycle_path": str(cp),
                "cycle_n": int(cp.name.replace("cycle_", "")),
                "outcome": o,
            })
        if len(out) >= limit:
            break
    return out


def list_stable_cycles(limit: int = 100) -> list[dict]:
    """Same as list_parked_cycles but for stable. Most-recent first."""
    out: list[dict] = []
    if not CYCLES_DIR.exists():
        return out
    for cp in sorted(CYCLES_DIR.iterdir(), reverse=True):
        if not cp.is_dir() or not cp.name.startswith("cycle_"):
            continue
        outcome_path = cp / "outcome.json"
        if not outcome_path.exists():
            continue
        try:
            o = json.loads(outcome_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if o.get("decision") == "mark_stable":
            out.append({
                "cycle_path": str(cp),
                "cycle_n": int(cp.name.replace("cycle_", "")),
                "outcome": o,
            })
        if len(out) >= limit:
            break
    return out


def cycle_n_from_path(p: Path) -> int:
    """Extract N from cycles/cycle_<N>/."""
    return int(p.name.replace("cycle_", ""))
