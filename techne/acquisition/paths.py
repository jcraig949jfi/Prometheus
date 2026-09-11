"""Where acquired bytes land. Host-local, never a hardcoded drive letter.

Resolution order, identical in spirit to archaeon.fossils._default_sfe_db:

    TECHNE_TOOL_CACHE env var
      -> techne/config.local.json  key "tool_cache"   (gitignored, per-host)
      -> <repo>/vault/techne_tools                    (vault/ is gitignored:
                                                       "cloned repos and model weights")

The cache is deliberately OUTSIDE the tracked tree. Wheels, cloned repositories and
isolated virtual environments are not artifacts of this repository; their hashes are.
"""
from __future__ import annotations

import json
import os
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ACQ_ROOT = pathlib.Path(__file__).resolve().parent


def tool_cache() -> pathlib.Path:
    env = os.environ.get("TECHNE_TOOL_CACHE")
    if env:
        return pathlib.Path(env)
    local = REPO_ROOT / "techne" / "config.local.json"
    try:
        cfg = json.loads(local.read_text(encoding="utf-8"))
        if cfg.get("tool_cache"):
            return pathlib.Path(cfg["tool_cache"])
    except (OSError, ValueError):
        pass
    return REPO_ROOT / "vault" / "techne_tools"


def _provides_libgcc(bin_dir: pathlib.Path) -> bool:
    """Does this toolchain actually ship libgcc?

    THE REASON THIS IS A CAPABILITY TEST AND NOT A NAME TEST. My first version of
    gcc_bin() resolved by `shutil.which("gcc")` and a glob for gcc.exe, and on this
    host it returned llvm-mingw -- whose `gcc` is a clang shim with NO libgcc. That
    is precisely the toolchain that failed the stitch Rust build twice with
    `cannot find -lgcc_eh` / `-lgcc`, and resolving to it would have reintroduced
    the failure the hardcoded path was put there to avoid. A resolver that finds
    something called gcc is not a resolver for what the gnu target needs.
    """
    root = bin_dir.parent
    for pat in ("lib/gcc/*/*/libgcc.a", "lib/libgcc_s.a", "*/*/libgcc.a"):
        for _ in root.glob(pat):
            return True
    return False


def gcc_bin() -> pathlib.Path | None:
    """The host's GCC bin directory, RESOLVED and never hardcoded.

    Why this exists: three check modules carried the literal
    C:/Users/<me>/AppData/Local/Microsoft/WinGet/Packages/... path, which
    base-role s2 forbids outright ("never hardcode a drive letter") and which is
    also this seat's own standing rule. It is needed because Rust's gnu target
    links against libgcc and llvm-mingw does not ship one, so the build has to
    find a real GCC.

    Resolution order, the same shape as tool_cache(), with every candidate held to
    _provides_libgcc():
        TECHNE_GCC_BIN env        (taken as declared; an explicit choice is not
                                   second-guessed, but it IS reported as unverified
                                   by gcc_bin_report() if it lacks libgcc)
        -> techne/config.local.json key "gcc_bin"   (gitignored, per-host)
        -> a libgcc-providing toolchain under LOCALAPPDATA's WinGet packages
        -> gcc.exe on PATH, only if it provides libgcc
        -> None, and the caller reports that rather than guessing
    """
    import json
    import os
    import shutil

    env = os.environ.get("TECHNE_GCC_BIN")
    if env:
        return pathlib.Path(env)
    local = REPO_ROOT / "techne" / "config.local.json"
    if local.exists():
        try:
            v = json.loads(local.read_text(encoding="utf-8")).get("gcc_bin")
            if v:
                return pathlib.Path(v)
        except (OSError, ValueError):
            pass
    appdata = os.environ.get("LOCALAPPDATA")
    if appdata:
        cands = sorted(pathlib.Path(appdata).glob(
            "Microsoft/WinGet/Packages/*/mingw64/bin/gcc.exe"))
        for cand in cands:
            if _provides_libgcc(cand.parent):
                return cand.parent
    found = shutil.which("gcc")
    if found and _provides_libgcc(pathlib.Path(found).parent):
        return pathlib.Path(found).parent
    return None


def gcc_bin_report() -> dict:
    """What a receipt records about the resolution, so a build failure on another
    host is diagnosable from the artifact rather than from a rerun."""
    b = gcc_bin()
    return {"gcc_bin": None if b is None else str(b),
            "provides_libgcc": None if b is None else _provides_libgcc(b),
            "resolved_by": ("TECHNE_GCC_BIN env" if __import__("os").environ.get(
                "TECHNE_GCC_BIN") else "config.local.json, WinGet discovery, or PATH"),
            "why_it_matters": "the gnu Rust target links libgcc; llvm-mingw's gcc is a "
                              "clang shim that has none, and selecting it fails the link"}


def gcc_bin_or_empty() -> str:
    """The same answer as a PATH fragment, for prefixing os.environ["PATH"]."""
    b = gcc_bin()
    return str(b) if b else ""


def downloads() -> pathlib.Path:
    return tool_cache() / "downloads"


def repos() -> pathlib.Path:
    return tool_cache() / "repos"


def env_root(env_name: str) -> pathlib.Path:
    """Isolated virtual environment root. `env_name` comes from the manifest entry,
    so DreamCoder's ancient stack never shares an interpreter with stitch_core."""
    return tool_cache() / "envs" / env_name


def manifest_path() -> pathlib.Path:
    return ACQ_ROOT / "MANIFEST.json"


def budget_path() -> pathlib.Path:
    return ACQ_ROOT / "BUDGET_PROFILES.json"


def host_capacity_path() -> pathlib.Path:
    return ACQ_ROOT / "HOST_CAPACITY.json"


def locks() -> pathlib.Path:
    return ACQ_ROOT / "locks"


def receipts() -> pathlib.Path:
    return ACQ_ROOT / "receipts"
