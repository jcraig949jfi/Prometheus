"""erebos_seam_census.py -- ONE question:

    Does the compose->falsify seam between Erebos (composer) and Stygian
    (falsifier) exist in the tree, and for how many of the 25 generator
    archetypes does a Stygian composition loader actually resolve an
    Erebos queue row?

The P57 death certificate (engine/ledger/AGENT_AUTOPSIES.jsonl,
2026-08-21) says the seam "was never built". This script executes the
seam offline: it imports the Erebos generator REGISTRY, force-imports the
composition loader modules exactly as charon/agents/stygian/executor.py
does, and calls find_loader() on a synthetic queue row per plugin shaped
like daemon._enqueue_to_stygian() emits. No network, no Postgres, no LLM.

Writes erebos_seam_census_result.json next to this file. Pure ASCII.
Repo root is resolved from __file__ (no drive letters).
"""
from __future__ import annotations

import importlib
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]          # engine/necropolis/dossiers/<x>_evidence -> repo
sys.path.insert(0, str(REPO))

EXECUTOR = REPO / "charon" / "agents" / "stygian" / "executor.py"
DAEMON = REPO / "charon" / "agents" / "erebos" / "daemon.py"
LOADER_DIR = REPO / "charon" / "agents" / "stygian" / "loaders"
STYG_TESTS = REPO / "charon" / "agents" / "stygian" / "tests"


def main() -> int:
    t0 = time.time()
    out: dict = {"question": __doc__.strip().splitlines()[0],
                 "repo_root": str(REPO), "errors": []}

    # 1. Erebos generator registry (Layer 1 producers).
    from charon.agents.erebos.generators import REGISTRY
    from charon.agents.erebos import _quarantine as q
    plugins = {}
    for pid, p in REGISTRY.items():
        plugins[pid] = {
            "expected_kill_pattern": getattr(p, "expected_kill_pattern", None),
            "feasibility_tier": getattr(p, "feasibility_tier", None),
            "quarantined_in_tree": bool(q.is_quarantined(pid)),
        }
    out["erebos_registry_n"] = len(plugins)
    out["erebos_quarantined_n"] = sum(1 for v in plugins.values()
                                      if v["quarantined_in_tree"])
    out["erebos_quarantined_ids"] = sorted(q.all_quarantined_plugins())

    # 2. Static: the executor's EREBOS-* branch and its force-import list.
    src = EXECUTOR.read_text(encoding="utf-8", errors="replace")
    forced = re.findall(
        r"import charon\.agents\.stygian\.loaders\.(composition_[a-z0-9_]+)", src)
    out["executor_forced_import_modules_n"] = len(forced)
    out["executor_short_circuit_kill_patterns"] = sorted(set(re.findall(
        r'kill_pattern="(stygian_erebos_[a-z_]+)"', src)))
    out["executor_has_EREBOS_branch"] = "EREBOS-" in src
    out["executor_calls_execute_composition_attack"] = (
        "_execute_composition_attack" in src)
    on_disk = sorted(p.stem for p in LOADER_DIR.glob("composition_*.py"))
    out["loader_modules_on_disk_n"] = len(on_disk)
    out["loader_modules_on_disk_not_force_imported"] = sorted(
        set(on_disk) - set(forced))

    # 3. Dynamic: import the loaders the way the executor does.
    from charon.agents.stygian.loaders._composition import (
        all_registered, find_loader)
    import_fail = {}
    for mod in forced:
        try:
            importlib.import_module(f"charon.agents.stygian.loaders.{mod}")
        except Exception as e:                      # noqa: BLE001
            import_fail[mod] = f"{type(e).__name__}: {e}"[:200]
    out["loader_import_failures"] = import_fail
    regs = all_registered()
    out["loaders_registered_n"] = len(regs)
    by_plugin: dict[str, list[str]] = {}
    for ld in regs:
        by_plugin.setdefault(getattr(ld, "plugin_id", "?"), []).append(
            getattr(ld, "composition_id", "?"))
    out["loaders_by_plugin"] = {k: sorted(v) for k, v in sorted(by_plugin.items())}
    out["plugins_with_ge1_loader"] = sorted(
        p for p in plugins if p in by_plugin)
    out["plugins_with_0_loaders"] = sorted(
        p for p in plugins if p not in by_plugin)
    out["loader_plugin_ids_not_in_registry"] = sorted(
        p for p in by_plugin if p not in plugins)

    # 4. Contract: keys daemon emits vs keys loaders read.
    dsrc = DAEMON.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"queue\.append\(\{(.*?)\}\)", dsrc, re.S)
    emitted = sorted(set(re.findall(r'"([a-z_]+)":', m.group(1)))) if m else []
    read_keys: dict[str, int] = {}
    for f in LOADER_DIR.glob("composition_*.py"):
        for k in re.findall(r'payload\.get\("([a-z_]+)"',
                            f.read_text(encoding="utf-8", errors="replace")):
            read_keys[k] = read_keys.get(k, 0) + 1
    out["daemon_queue_row_keys"] = emitted
    out["loader_payload_keys_read"] = read_keys
    out["loader_keys_not_emitted_by_daemon"] = sorted(
        k for k in read_keys if k not in emitted)

    # 5. Exercise find_loader with a daemon-shaped row per plugin, using
    #    a few composed_id conventions seen in the generators.
    resolved = {}
    for pid in plugins:
        gnum = pid[:3].upper()          # g02_contrast -> G02
        cands = [f"EREBOS-{gnum}-BL-C-001-x-salem_vs_non_salem",
                 f"EREBOS-{gnum}-BL-C-001",
                 f"EREBOS-{gnum}-BL-C-001-x-probe"]
        hit = None
        for cid in cands:
            row = {"source": "erebos", "kill_pattern": f"erebos_{pid}_{cid}",
                   "erebos_plugin_id": pid, "erebos_composed_id": cid,
                   "erebos_expected_kill_pattern":
                       plugins[pid]["expected_kill_pattern"],
                   "erebos_falsification_route": "synthetic",
                   "erebos_ledger_row_id": "synthetic",
                   "parent_record_ids": ["BL-C-001"],
                   "rationale": "synthetic probe"}
            ld = find_loader(row)
            if ld is not None:
                hit = getattr(ld, "composition_id", "?")
                break
        resolved[pid] = hit
    out["find_loader_synthetic_hits"] = {k: v for k, v in resolved.items() if v}
    out["find_loader_synthetic_hits_n"] = sum(1 for v in resolved.values() if v)
    out["find_loader_note"] = ("A miss here means the synthetic composed_id "
                               "did not match the loader regex, NOT that no "
                               "loader exists; see loaders_by_plugin.")
    # negative control: a non-erebos row must not resolve
    out["control_non_erebos_row_resolves"] = find_loader(
        {"source": "hecate", "erebos_plugin_id": "g02_contrast",
         "erebos_composed_id": "EREBOS-G02-BL-C-001-x-salem_vs_non_salem"}
    ) is not None

    # 6. Stygian composition tests on disk (read, not run here).
    out["stygian_composition_test_files"] = sorted(
        p.name for p in STYG_TESTS.glob("test_composition_*.py"))
    out["elapsed_s"] = round(time.time() - t0, 2)
    (HERE / "erebos_seam_census_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({k: out[k] for k in (
        "erebos_registry_n", "erebos_quarantined_n",
        "executor_forced_import_modules_n", "loaders_registered_n",
        "loader_import_failures", "plugins_with_ge1_loader",
        "find_loader_synthetic_hits_n", "loader_keys_not_emitted_by_daemon",
        "control_non_erebos_row_resolves")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
