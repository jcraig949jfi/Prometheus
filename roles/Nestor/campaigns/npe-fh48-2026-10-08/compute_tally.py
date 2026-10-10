"""Compute used per experiment (sum of per-run process CPU seconds) from run rows; excludes quarantined runs."""
import collections, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
tot, n = collections.Counter(), collections.Counter()
for d in sorted((HERE / "runs").iterdir()):
    if not d.is_dir():
        continue
    for p in d.glob("*.json"):
        try:
            r = json.loads(p.read_text())
        except Exception:
            continue
        if isinstance(r, dict) and "cpu_s" in r and "arm" in r:
            tot[d.name] += r["cpu_s"]
            n[d.name] += 1
for e in sorted(tot):
    print("%-38s runs %3d  cpu-h %6.1f" % (e, n[e], tot[e] / 3600))
valid = {e: v for e, v in tot.items() if "INVALID" not in e}
print("TOTAL valid runs %d  cpu-h %.1f   (quarantined: %s)" % (sum(n[e] for e in valid), sum(valid.values()) / 3600,
      {e: n[e] for e in tot if "INVALID" in e}))
