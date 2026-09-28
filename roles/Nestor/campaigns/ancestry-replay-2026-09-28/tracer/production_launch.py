"""Production launcher (GO_FINAL binding hygiene). It computes no statistic.

  1. START RECEIPT:
     - every tracer file vs TRACER_FREEZE.json, which must itself hash to 77a822ac...;
     - run_production.py vs c31cca76...;
     - s4_run.py and this launcher, hashed (committed before production);
     - GO_FINAL record sha256 fefef4b0...; git HEAD; host; python.
     Any mismatch: refuse.
  2. run_production.py, unchanged and bound: traces the 11 records and writes PRODUCTION_INDEX.json.
  3. s4_run.py: the instrument tests on every birth.
  4. The 1% agreement sample files (exports/*.sample1pct.jsonl.gz, git-ignored) are hashed into SAMPLE_MANIFEST.json. They
     go to M2 only by scp after the hash is posted.
  5. END RECEIPT.
The M1 compute lease (fabric lease skullport:cpu8 via nestor_lease.py) is taken and released by the one-shot task that
starts this script.
"""
import hashlib, json, pathlib, platform, socket, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
EXPORTS = ROOT / "exports"
BIND = {"TRACER_FREEZE.json": "77a822acb7203295c28187b16a93d368bb0a8cf1bc72a3630aed304015d4bc3e",
        "run_production.py": "c31cca76b7458dfb048c6b4d895935926353021919501185ef27ab0daf4c42c4"}
GO_FINAL_SHA = "fefef4b076577ef2e94627a4c0a43eeb1c5fb2fa90fec314872c3cf69446d12f"


def lf(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main():
    t0 = time.time()
    fz = json.loads((HERE / "TRACER_FREEZE.json").read_text(encoding="utf-8"))
    checks = {f: lf(HERE / f) == h for f, h in BIND.items()}
    checks.update({"freeze:" + f: lf(HERE / f) == h for f, h in fz["files"].items()})
    EXPORTS.mkdir(parents=True, exist_ok=True)
    start = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "host": socket.gethostname(),
             "python": platform.python_version(), "git_head": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                                                             capture_output=True, text=True).stdout.strip(),
             "go_final_sha256": GO_FINAL_SHA, "binding_checks": checks, "all_bindings_hold": all(checks.values()),
             "s4_run_sha256": lf(HERE / "s4_run.py"), "launcher_sha256": lf(__file__)}
    (EXPORTS / "START_RECEIPT.json").write_text(json.dumps(start, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if not start["all_bindings_hold"]:
        sys.exit("REFUSED: bindings do not hold: %s" % [k for k, v in checks.items() if not v])
    subprocess.run([sys.executable, str(HERE / "run_production.py")], check=True)
    subprocess.run([sys.executable, str(HERE / "s4_run.py")], check=True)
    sample = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(EXPORTS.glob("*.sample1pct.jsonl.gz"))}
    (EXPORTS / "SAMPLE_MANIFEST.json").write_text(json.dumps(sample, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    end = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "wall_s": round(time.time() - t0, 1),
           "production_index_sha256": lf(EXPORTS / "PRODUCTION_INDEX.json"),
           "s4_summary_sha256": lf(EXPORTS / "S4_SUMMARY.json"), "sample_files": len(sample)}
    (EXPORTS / "END_RECEIPT.json").write_text(json.dumps(end, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(end))


if __name__ == "__main__":
    main()
