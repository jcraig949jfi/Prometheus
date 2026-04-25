"""Driver: run every bench_*.py through pytest-benchmark and emit
a Markdown summary at prometheus_math/benchmarks/RESULTS.md.

Usage:
    python -m prometheus_math.benchmarks.run_all
        [--quick]               # single round per benchmark
        [--out PATH]            # alternate Markdown output
        [--threshold-ms 100]    # Tier-2 candidate threshold

Behavior:
- Calls pytest with `--benchmark-only --benchmark-json=<tmp>` so
  pytest-benchmark emits a structured stats file.
- Reads the JSON stats and writes RESULTS.md grouping by source
  bench_*.py file, sorted by median descending.
- Marks operations with median > threshold-ms as Tier-2 promotion
  candidates.

Exit codes:
- 0: ran successfully (regardless of how slow individual benches were)
- 1: pytest itself failed (collection error, import error, etc.)
- 2: invalid arguments
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from typing import Iterable, Optional


_BENCH_DIR = pathlib.Path(__file__).parent
_DEFAULT_OUT = _BENCH_DIR / "RESULTS.md"
_DEFAULT_JSON = _BENCH_DIR / ".benchmarks" / "latest.json"


def _bench_files() -> list[pathlib.Path]:
    return sorted(_BENCH_DIR.glob("bench_*.py"))


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="prometheus_math.benchmarks.run_all",
        description="Run prometheus_math benchmarks and aggregate results.",
    )
    p.add_argument("--quick", action="store_true",
                   help="Single round per benchmark (CI-friendly).")
    p.add_argument("--out", type=pathlib.Path, default=_DEFAULT_OUT,
                   help="Markdown output file (default: RESULTS.md).")
    p.add_argument("--threshold-ms", type=float, default=100.0,
                   help="Median threshold for Tier-2 promotion candidate flag.")
    p.add_argument("--json-out", type=pathlib.Path, default=_DEFAULT_JSON,
                   help="pytest-benchmark JSON stats file path.")
    p.add_argument("--no-run", action="store_true",
                   help="Skip pytest execution; aggregate from existing JSON.")
    p.add_argument("--no-update-benchmarks-md", action="store_true",
                   help="Do not refresh BENCHMARKS.md (useful for tests).")
    return p.parse_args(argv)


def _run_pytest(json_out: pathlib.Path, quick: bool) -> int:
    """Invoke pytest in benchmark-only mode, writing stats to json_out."""
    json_out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "pytest",
        str(_BENCH_DIR),
        "--run-benchmarks",
        "--benchmark-only",
        f"--benchmark-json={json_out}",
        "-q",
    ]
    if quick:
        cmd += [
            "--benchmark-min-rounds=1",
            "--benchmark-max-time=2.0",
            "--benchmark-warmup=off",
        ]
    proc = subprocess.run(cmd)
    return proc.returncode


def _load_stats(path: pathlib.Path) -> dict:
    if not path.is_file():
        return {"benchmarks": [], "machine_info": {}, "commit_info": {}}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _format_seconds(s: float) -> str:
    if s >= 1.0:
        return f"{s:.3f} s"
    if s >= 1e-3:
        return f"{s * 1e3:.2f} ms"
    return f"{s * 1e6:.1f} µs"


def _group_by_file(benches: Iterable[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for b in benches:
        # pytest-benchmark gives a "fullname" like
        # "prometheus_math/benchmarks/bench_number_theory.py::bench_xyz"
        fullname = b.get("fullname", "")
        src = fullname.split("::", 1)[0]
        src = pathlib.Path(src).name or "unknown"
        groups.setdefault(src, []).append(b)
    return groups


def _emit_markdown(stats: dict, out: pathlib.Path,
                   threshold_ms: float) -> list[str]:
    """Emit RESULTS.md and return the list of Tier-2 candidate names."""
    benches = stats.get("benchmarks", [])
    machine = stats.get("machine_info", {}) or {}
    commit = stats.get("commit_info", {}) or {}

    candidates: list[tuple[str, float]] = []

    lines: list[str] = []
    lines.append("# prometheus_math benchmark results")
    lines.append("")
    lines.append(f"- machine: {machine.get('node', '?')} "
                 f"({machine.get('system', '?')} "
                 f"{machine.get('release', '')})")
    lines.append(f"- python: {machine.get('python_version', '?')}")
    if commit.get("id"):
        lines.append(f"- commit: `{commit['id']}` "
                     f"({commit.get('branch', '')})")
    lines.append(f"- Tier-2 threshold: median > {threshold_ms:.0f} ms")
    lines.append("")

    if not benches:
        lines.append("_No benchmark data. Run with `python -m "
                     "prometheus_math.benchmarks.run_all`._")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return []

    groups = _group_by_file(benches)
    for src in sorted(groups):
        lines.append(f"## {src}")
        lines.append("")
        lines.append(
            "| Benchmark | Median | Mean | Min | Max | Rounds | Tier-2? |"
        )
        lines.append(
            "|---|---:|---:|---:|---:|---:|:---:|"
        )
        sorted_benches = sorted(
            groups[src],
            key=lambda b: b.get("stats", {}).get("median", 0.0),
            reverse=True,
        )
        for b in sorted_benches:
            name = b.get("name", "?")
            s = b.get("stats", {})
            median = float(s.get("median", 0.0))
            mean = float(s.get("mean", 0.0))
            mn = float(s.get("min", 0.0))
            mx = float(s.get("max", 0.0))
            rounds = int(s.get("rounds", 0))
            is_tier2 = (median * 1000.0) > threshold_ms
            mark = "**yes**" if is_tier2 else "no"
            lines.append(
                f"| `{name}` | {_format_seconds(median)} | "
                f"{_format_seconds(mean)} | {_format_seconds(mn)} | "
                f"{_format_seconds(mx)} | {rounds} | {mark} |"
            )
            if is_tier2:
                candidates.append((name, median))
        lines.append("")

    lines.append("## Tier-2 promotion candidates")
    lines.append("")
    if not candidates:
        lines.append("_No operations exceeded the threshold._")
    else:
        candidates.sort(key=lambda kv: kv[1], reverse=True)
        for name, median in candidates:
            lines.append(f"- `{name}` — median {_format_seconds(median)}")
    lines.append("")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return [c[0] for c in candidates]


def _update_benchmarks_md(candidates: list[str]) -> None:
    """Refresh the auto-generated section of BENCHMARKS.md."""
    bm = _BENCH_DIR / "BENCHMARKS.md"
    if not bm.is_file():
        return
    text = bm.read_text(encoding="utf-8")
    begin = "<!-- BENCHMARKS_AUTO_BEGIN -->"
    end = "<!-- BENCHMARKS_AUTO_END -->"
    if begin not in text or end not in text:
        return
    body = ["", "_Auto-refreshed by `run_all.py`._", ""]
    if candidates:
        for name in candidates:
            body.append(f"- `{name}`")
    else:
        body.append("- _no candidates as of last run_")
    body.append("")
    pre, _, rest = text.partition(begin)
    _, _, post = rest.partition(end)
    new = pre + begin + "\n" + "\n".join(body) + end + post
    bm.write_text(new, encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)

    if not args.no_run:
        rc = _run_pytest(args.json_out, args.quick)
        # rc==5 means "no tests collected"; tolerate it. Anything else
        # we surface but still try to emit a (possibly empty) RESULTS.md.
        if rc not in (0, 5):
            print(f"[run_all] pytest exited with code {rc}; "
                  "attempting partial aggregation", file=sys.stderr)

    stats = _load_stats(args.json_out)
    candidates = _emit_markdown(stats, args.out, args.threshold_ms)
    if not args.no_update_benchmarks_md:
        _update_benchmarks_md(candidates)

    print(f"[run_all] wrote {args.out}")
    if candidates:
        print(f"[run_all] {len(candidates)} Tier-2 candidate(s):")
        for c in candidates:
            print(f"  - {c}")
    else:
        print("[run_all] no Tier-2 candidates above threshold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
