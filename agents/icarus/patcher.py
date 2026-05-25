"""
Icarus diff applier.

Applies a unified diff (typically produced by improve.propose_diff()) to a
cycle's code/ directory. Uses `git apply` since git is guaranteed available
in the Prometheus environment and is more robust than hand-rolled parsing.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def apply_diff(diff_text: str, target_dir: Path) -> dict:
    """Apply a unified diff to target_dir/.

    Returns:
        {
          "applied": bool,
          "method": "git_apply" | "noop",
          "stdout": str,
          "stderr": str,
          "files_changed": list[str],
          "reason": str,
        }
    """
    if not diff_text or not diff_text.strip():
        return {
            "applied": False, "method": "noop",
            "stdout": "", "stderr": "",
            "files_changed": [], "reason": "empty_diff",
        }

    if not target_dir.exists():
        return {
            "applied": False, "method": "noop",
            "stdout": "", "stderr": "",
            "files_changed": [], "reason": f"target_missing: {target_dir}",
        }

    # Write diff to temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".patch", delete=False, encoding="utf-8"
    ) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(diff_text)
        if not diff_text.endswith("\n"):
            tmp.write("\n")

    try:
        # git apply -p1 strips the leading a/ b/ prefixes; --unsafe-paths
        # lets us write outside the current repo's tree.
        # --whitespace=fix tolerates minor whitespace issues.
        result = subprocess.run(
            ["git", "apply", "-p1", "--unsafe-paths", "--whitespace=fix",
             "--ignore-space-change", str(tmp_path)],
            cwd=str(target_dir),
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            # Try without --ignore-space-change; sometimes that flag rejects
            # legit diffs
            result2 = subprocess.run(
                ["git", "apply", "-p1", "--unsafe-paths", "--whitespace=fix",
                 str(tmp_path)],
                cwd=str(target_dir),
                capture_output=True, text=True, timeout=30,
            )
            if result2.returncode == 0:
                result = result2
            else:
                return {
                    "applied": False, "method": "git_apply",
                    "stdout": result.stdout, "stderr": result.stderr,
                    "files_changed": [],
                    "reason": f"git_apply_failed: {result.stderr[:300]}",
                }

        # Get list of files changed (parse diff for ---/+++ lines)
        files_changed = _extract_files_from_diff(diff_text)

        return {
            "applied": True, "method": "git_apply",
            "stdout": result.stdout, "stderr": result.stderr,
            "files_changed": files_changed, "reason": "ok",
        }
    except subprocess.TimeoutExpired:
        return {
            "applied": False, "method": "git_apply",
            "stdout": "", "stderr": "timeout",
            "files_changed": [], "reason": "git_apply_timeout",
        }
    except Exception as e:
        return {
            "applied": False, "method": "git_apply",
            "stdout": "", "stderr": str(e),
            "files_changed": [], "reason": f"git_apply_exception: {e}",
        }
    finally:
        try:
            tmp_path.unlink()
        except Exception:
            pass


def _extract_files_from_diff(diff_text: str) -> list[str]:
    """Walk the diff and pull out file paths from +++ lines."""
    files = []
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            path = line[4:].strip()
            if path.startswith("b/"):
                path = path[2:]
            if path != "/dev/null":
                files.append(path)
    return files


def diff_lines_changed(diff_text: str) -> int:
    """Count + and - lines in the diff body (excluding hunk markers)."""
    count = 0
    for line in diff_text.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+") or line.startswith("-"):
            count += 1
    return count
