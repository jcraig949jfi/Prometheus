"""The ONLY entry point for benchmark executors (operator amendment of 2026-09-18).

1. Verifies every bundle file on disk against BENCHMARK_MANIFEST.json and
   recomputes the canonical manifest hash; refuses to run on any mismatch.
2. Verifies the derived task fixtures still match what the harness generates
   (so the fixtures and the harness cannot drift apart).
3. Runs the UNCHANGED bench.py with the executor's arguments.
4. Stamps the receipt with bundle_manifest_sha256, bundle_git_commit,
   bundle_verified and the served-variant identity.

  python run_frozen.py --host-label M1 --base-url ... --model ... --checkpoint ... --quant ... \
      --runtime ... [--extra-body ...] --out <receipt.json>
"""
from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def lf_sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def verify_bundle():
    m = json.loads((HERE / "BENCHMARK_MANIFEST.json").read_text(encoding="utf-8"))
    bad = [f for f, h in m["files"].items() if lf_sha256(HERE / f) != h]
    canon = hashlib.sha256(json.dumps({"bundle_version": m["bundle_version"], "files": m["files"]},
                                      sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if canon != m["canonical_sha256"]:
        bad.append("canonical hash does not match the listed file hashes")
    import bench  # noqa: E402
    fx = json.loads((HERE / "bundle" / "task_fixture_manifest.json").read_text(encoding="utf-8"))
    for t in fx["starting_accuracy_tasks"]:
        p, g = bench.make_task(t["family"], random.Random(t["seed"]))
        if (p, g) != (t["prompt"], t["gold"]):
            bad.append(f"fixture drift at {t['family']}#{t['index']}")
            break
    if bad:
        raise SystemExit("REFUSING TO RUN -- bundle does not match BENCHMARK_MANIFEST: " + "; ".join(bad))
    return m


def main():
    m = verify_bundle()
    args = sys.argv[1:]
    out = Path(args[args.index("--out") + 1])
    subprocess.run([sys.executable, str(HERE / "bench.py")] + args, check=True)
    r = json.loads(out.read_text(encoding="utf-8"))
    mod = r["model"]
    r["bundle_manifest_sha256"] = m["canonical_sha256"]
    r["bundle_git_commit"] = m["git_commit_of_files"]
    r["bundle_verified"] = True
    r["served_variant"] = {"checkpoint": mod.get("checkpoint"), "quant": mod.get("quant"),
                           "runtime_family": (mod.get("runtime") or "").split(" ")[0].lower(),
                           "extra_body": mod.get("extra_body"), "requested": mod.get("requested")}
    out.write_text(json.dumps(r, indent=1), encoding="utf-8")
    print("bundle", m["canonical_sha256"], "verified; receipt", out)


if __name__ == "__main__":
    main()
