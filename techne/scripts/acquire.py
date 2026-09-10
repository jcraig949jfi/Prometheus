"""The acquisition command. H0-H5 design v0.1 section 7, 'Downloads and executable commands'.

    python -m techne.scripts.acquire --list
    python -m techne.scripts.acquire --entry z3        --profile light_probe
    python -m techne.scripts.acquire --entry stitch    --profile light_probe
    python -m techne.scripts.acquire --entry dreamcoder --profile isolated_heavy_build
    python -m techne.scripts.acquire --entry z3 --profile light_probe --dry-run

Inputs are a MANIFEST ENTRY and a BUDGET PROFILE, exactly as the design specifies. It
resolves the recorded commit/tag, checks license and notices and submodules, obtains
dependencies into an isolated cache/environment, writes hashes and prints a receipt.

Network is allowed ONLY here. Nothing this command installs enters the live interpreter,
and nothing it installs is thereby qualified for a scientific run: an INSTALLATION
receipt says so in its own `does_not_establish` field.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from techne.acquisition import budget as _budget
from techne.acquisition import fixtures as _fixtures
from techne.acquisition import manifest_io, paths, pypi, receipt, repo


def _print_entries(man: dict) -> None:
    print(f"manifest: {paths.manifest_path()}")
    print(f"{'id':<18} {'kind':<16} {'version':<10} {'env':<20} consumer")
    for e in man["entries"]:
        print(f"{e['id']:<18} {e['kind']:<16} {str(e.get('pinned_version') or '-'):<10} "
              f"{str(e.get('env') or '-'):<20} {(e.get('named_consumer') or '')[:70]}")


def acquire_python_package(entry: dict, prof: dict, dry_run: bool) -> dict:
    rec = receipt.new("INSTALLATION", entry["id"], tool=entry["distribution"])
    rec["manifest_entry"] = {k: entry.get(k) for k in
                             ("id", "kind", "distribution", "pinned_version", "env",
                              "named_consumer", "integration_path", "official_source")}
    rec["budget_profile"] = prof
    with _budget.Budget(profile=prof) as b:
        try:
            meta = pypi.release_metadata(entry["distribution"], entry["pinned_version"], b)
            sel = pypi.select_artifact(meta)
            rec["observations"]["artifact_selection"] = {
                "reason": sel["reason"], "host_tag_count": sel["host_tag_count"],
                "selected": sel["selected"],
                "n_candidates": len(sel["candidates"]),
                "rejected_for_platform": [c["filename"] for c in sel["candidates"]
                                          if c["packagetype"] == "bdist_wheel"
                                          and not c["host_compatible"]][:40],
            }
            if sel["selected"] is None:
                rec["status"] = "BLOCKED_NO_COMPATIBLE_ARTIFACT"
                rec["unrun_or_blocked"].append(sel["reason"])
                return _finish(rec, b)

            if dry_run:
                rec["status"] = "DRY_RUN"
                rec["unrun_or_blocked"].append("--dry-run: no bytes transferred, no env touched")
                return _finish(rec, b)

            dl = pypi.download(sel["selected"], b)
            rec["observations"]["download"] = dl
            if not dl["digest_matches_pypi"]:
                rec["status"] = "FAILED_DIGEST_MISMATCH"
                rec["unrun_or_blocked"].append(
                    "locally computed sha256 disagrees with PyPI's declared digest; "
                    "nothing was installed")
                return _finish(rec, b)

            lic = pypi.license_from_wheel(dl["path"])
            rec["observations"]["license"] = lic
            rec["observations"]["license_rule_applied"] = entry.get("license_resolution_rule")
            rec["observations"]["requires_dist"] = pypi.requires_dist_from_wheel(dl["path"])

            envinfo = pypi.ensure_env(entry["env"], b)
            rec["observations"]["isolated_env"] = envinfo
            if envinfo["is_live_interpreter"]:
                rec["status"] = "REFUSED_WOULD_TOUCH_LIVE_INTERPRETER"
                return _finish(rec, b)

            spec = f"{entry['distribution']}=={entry['pinned_version']}"
            res = pypi.resolve_lock(entry["env"], spec, b)
            rec["observations"]["resolution"] = {
                "ok": res["ok"],
                "n_resolved": len(res.get("resolved", [])),
                "resolved": res.get("resolved", []),
                "unhashed": res.get("unhashed", []),
            }
            if not res["ok"]:
                receipt.record_command(rec, res["command"])
                rec["status"] = "FAILED_RESOLUTION"
                return _finish(rec, b)
            if res["unhashed"]:
                rec["deviations"].append(
                    f"DEV-T3[{entry['id']}]: pip reported no sha256 for "
                    f"{res['unhashed']} -- those lines are REFUSED in the lock, so the "
                    f"closure is incomplete and the install will fail rather than "
                    f"silently install an unhashed artifact")

            lock = pypi.write_lock(
                entry["id"], entry["env"], res["resolved"],
                extra_header=f"named consumer: {entry.get('named_consumer')}\n"
                             f"license status: {lic['status']}")
            rec["observations"]["lock"] = {
                "path": str(lock.relative_to(paths.REPO_ROOT)).replace("\\", "/"),
                "sha256_of_lock": __import__("hashlib").sha256(lock.read_bytes()).hexdigest(),
            }

            inst = pypi.install_locked(entry["env"], lock, b)
            rec["observations"]["install"] = inst
            if inst["returncode"] != 0:
                rec["status"] = "FAILED_INSTALL"
                return _finish(rec, b)

            if entry.get("fixtures"):
                rec["observations"]["fixtures"] = _fixtures.acquire(entry, b)

            ver = pypi.verify_import(entry["env"], entry["import_name"],
                                     entry["distribution"], b)
            rec["observations"]["import_verification"] = ver
            rec["status"] = "INSTALLED_PINNED_AND_HASHED" if ver.get("imported") else \
                "INSTALLED_BUT_IMPORT_FAILED"
            rec["observations"]["version_match"] = (
                ver.get("dist_version") == entry["pinned_version"])
        except (_budget.BudgetExceeded, _budget.NetworkForbidden) as exc:
            rec["status"] = f"ABORTED_{type(exc).__name__}"
            rec["unrun_or_blocked"].append(str(exc))
        except Exception as exc:  # recorded, never swallowed
            rec["status"] = "ERROR"
            rec["unrun_or_blocked"].append(f"{type(exc).__name__}: {exc}")
        return _finish(rec, b)


def acquire_repository(entry: dict, prof: dict, dry_run: bool) -> dict:
    rec = receipt.new("INSTALLATION", entry["id"])
    rec["manifest_entry"] = {k: entry.get(k) for k in
                             ("id", "kind", "env", "named_consumer", "integration_path",
                              "official_source", "absent_recipe_warning")}
    rec["manifest_entry"]["upstream_revision"] = entry["upstream_revision"]
    rec["budget_profile"] = prof
    with _budget.Budget(profile=prof) as b:
        try:
            if dry_run:
                rec["status"] = "DRY_RUN"
                rec["unrun_or_blocked"].append("--dry-run: nothing fetched")
                return _finish(rec, b)
            out = repo.clone_at_revision(entry, b)
            rec["observations"]["clone"] = out
            if not out.get("ok"):
                rec["status"] = "FAILED_CLONE"
                rec["unrun_or_blocked"].append(out.get("reason", "clone failed"))
                return _finish(rec, b)
            rec["status"] = "SOURCE_AT_PINNED_REVISION"
            sub = out.get("submodules", {})
            if sub.get("moving_branch_pins"):
                rec["deviations"].append(
                    f"DEV-T4[{entry['id']}]: {len(sub['moving_branch_pins'])} submodule(s) "
                    f"declare a `branch` in .gitmodules. A branch is not a pin; `pins` "
                    f"records the commit actually checked out after forcing.")
            for d in sub.get("deviations", []):
                rec["deviations"].append(f"DEV-T6[{entry['id']}]: {d}")
            if sub.get("declared") and not sub.get("all_at_recorded_commit"):
                rec["status"] = "SOURCE_AT_PINNED_REVISION_SUBMODULES_INCOMPLETE"
                rec["unrun_or_blocked"].append(
                    f"{sub.get('n_not_initialized')} submodule(s) not initialised and "
                    f"{sub.get('n_off_pin')} off their recorded commit; any build or smoke "
                    f"run depending on them is BLOCKED, not merely degraded")
            if out["licenses"]["status"] == "NO_NOTICE_FILES_FOUND":
                rec["deviations"].append(
                    f"DEV-T5[{entry['id']}]: no LICENSE/COPYING/NOTICE file found in the "
                    f"acquired copy; licensing stays UNRESOLVED")
        except (_budget.BudgetExceeded, _budget.NetworkForbidden) as exc:
            rec["status"] = f"ABORTED_{type(exc).__name__}"
            rec["unrun_or_blocked"].append(str(exc))
        except Exception as exc:
            rec["status"] = "ERROR"
            rec["unrun_or_blocked"].append(f"{type(exc).__name__}: {exc}")
        return _finish(rec, b)


def _finish(rec: dict, b: "_budget.Budget") -> dict:
    rec["resource_receipt"] = b.resource_receipt()
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Acquire one manifest entry under one budget profile.")
    ap.add_argument("--entry", help="manifest entry id")
    ap.add_argument("--profile", default="light_probe", help="budget profile name")
    ap.add_argument("--list", action="store_true", help="list manifest entries and exit")
    ap.add_argument("--dry-run", action="store_true",
                    help="resolve and select, transfer nothing, touch no environment")
    ap.add_argument("--receipt-dir", default=None)
    a = ap.parse_args(argv)

    man = manifest_io.load()
    if a.list or not a.entry:
        _print_entries(man)
        return 0 if a.list else 2

    entry = manifest_io.entry(man, a.entry)
    prof = _budget.get_profile(a.profile)

    if entry.get("acquisition_status") in ("NOT_ATTEMPTED_NO_CONSUMER",
                                           "NOT_APPLICABLE_IN_REPO"):
        print(f"REFUSED: entry {entry['id']!r} is marked {entry['acquisition_status']}.")
        print(f"  {entry.get('named_consumer')}")
        print("  The design requires a named consumer for every integration. Acquiring "
              "this now would be the 'download every historical framework' failure the "
              "design forbids.")
        return 3

    if entry["kind"] == "python_package":
        rec = acquire_python_package(entry, prof, a.dry_run)
    elif entry["kind"] == "repository":
        rec = acquire_repository(entry, prof, a.dry_run)
    else:
        print(f"no acquisition defined for kind {entry['kind']!r}")
        return 3

    out = receipt.write(rec, pathlib.Path(a.receipt_dir) if a.receipt_dir else None)

    print(f"\n=== {rec['stage']} receipt: {rec['entry_id']} ===")
    print(f"status          {rec['status']}")
    obs = rec["observations"]
    if "artifact_selection" in obs:
        s = obs["artifact_selection"]
        sel = s["selected"]
        print(f"selection       {sel['filename'] if sel else 'NONE'}")
        print(f"  reason        {s['reason']}")
        print(f"  candidates    {s['n_candidates']} total, "
              f"{len(s['rejected_for_platform'])} wheels rejected for this platform")
    if "download" in obs:
        d = obs["download"]
        print(f"artifact        {pathlib.Path(d['path']).name}")
        print(f"sha256 (local)  {d['sha256_local']}")
        print(f"digest vs PyPI  {'MATCH' if d['digest_matches_pypi'] else 'MISMATCH'}")
    if "license" in obs:
        lc = obs["license"]
        print(f"license         {lc['status']}  expression={lc['license_expression']!r} "
              f"classifiers={lc['classifiers']}")
        print(f"notice files    {[f.get('name') for f in lc['license_files']]}")
    if "lock" in obs:
        print(f"lock            {obs['lock']['path']}")
        print(f"closure         {obs['resolution']['n_resolved']} distributions, "
              f"{len(obs['resolution']['unhashed'])} unhashed")
    if "fixtures" in obs:
        for fx in obs["fixtures"]:
            print(f"fixture         {fx['id']} {fx['bytes']}B sha256={fx['sha256_observed']}")
            print(f"  blob id       computed={fx['git_blob_sha1_computed'][:12]} "
                  f"upstream={fx.get('repo_blob_sha')} "
                  f"match={fx.get('blob_id_matches_upstream')}")
            print(f"  status        {fx['status']}")
    if "import_verification" in obs:
        print(f"import          {obs['import_verification']}")
    if "clone" in obs:
        c = obs["clone"]
        print(f"path            {c['path']}")
        print(f"pin verified    {c['pin_verified']}  ({c['checked_out_commit']})")
        sm = c["submodules"]
        print(f"submodules      {sm['status']} n_declared={sm.get('n_declared')} "
              f"at_pin={sm.get('n_at_pin')} uninit={sm.get('n_not_initialized')} "
              f"off_pin={sm.get('n_off_pin')}")
        for f in sm.get("forced_to_recorded_commit", []):
            print(f"  forced        {f['path']} -> {f['wanted'][:12]} ok={f['ok']}")
        print(f"notices         {c['licenses']['status']} "
              f"{[f['path'] for f in c['licenses']['files']]}")
    rr = rec["resource_receipt"]
    print(f"resources       {rr['wall_seconds']}s / {rr['wall_ceiling']}s ceiling, "
          f"{rr['downloaded_bytes']}B downloaded, peak RSS "
          f"{rr['peak_rss_bytes_os_counter']}B (OS counter, this process only, NOT capped)")
    for d in rec["deviations"]:
        print(f"DEVIATION       {d}")
    for u in rec["unrun_or_blocked"]:
        print(f"BLOCKED         {u}")
    print(f"does not establish: {', '.join(rec['does_not_establish'])}")
    print(f"receipt         {out}")
    return 0 if rec["status"] in ("INSTALLED_PINNED_AND_HASHED", "SOURCE_AT_PINNED_REVISION",
                                 "DRY_RUN") else 1


if __name__ == "__main__":
    sys.exit(main())
