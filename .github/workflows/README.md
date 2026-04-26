# GitHub Actions — `prometheus_math` arsenal

This directory holds CI/CD for the `prometheus_math` unified API package and the
underlying tool arsenal in `techne/lib/`.

## Workflows

### `arsenal.yml`

Three jobs, one workflow:

| Job | Trigger | Purpose |
|---|---|---|
| `arsenal-smoke` | push, PR, every 6h cron, manual | Tolerant install of all pip-based tools, print capability matrix, run `techne/tests/` and `prometheus_math/tests/`, upload JUnit XML + capability JSON as artifact, post the matrix to the workflow summary. Matrix: Python 3.11 and 3.12 on `ubuntu-latest`. |
| `capability-tracking` | daily cron (07:17 UTC), manual | Re-detect installed backends, diff against `prometheus_math/.capability_snapshot.json`. On change: commit the new snapshot with message `arsenal: capability matrix updated` AND open a GitHub issue summarizing the delta. |
| `docs-regen` | push to `prometheus_math/**` | Run `python -c "import prometheus_math; prometheus_math.doc.arsenal()"` to regenerate `prometheus_math/ARSENAL.md`. Commits if changed. |

The two `schedule:` crons in the workflow are gated per-job by
`github.event.schedule == '<cron expression>'` so each cron only fires the right job.

## What's NOT in CI scope

The arsenal includes some heavy native tools that are **not** installed in CI:

- **GAP** (groups & representations) — needs separate Linux package; install locally if you need it.
- **Macaulay2** (commutative algebra) — same.
- **Singular** (polynomial rings) — same.
- **Lean 4** — toolchain install is large; use `lean4-action` if/when we need it.
- **Julia** (gateway to OSCAR / Hecke / Nemo) — local only for now.
- **R** — local only.

The `registry.py` capability matrix probes for these binaries and just records them as
unavailable in CI; that's expected. If you need them in CI for a specific test, add a
dedicated job rather than expanding `arsenal-smoke`.

`snappy`, `knot_floer_homology`, `gudhi`, `gmpy2`, and `cvxpy` may also fail to install
on a vanilla `ubuntu-latest` runner depending on wheel availability. The install step is
**tolerant** (each `pip install` is wrapped in `|| echo WARN`), so a missing wheel does
not fail the job — it just shows up as unavailable in the capability matrix.

## Adding a new tool to the capability matrix

1. Edit [`prometheus_math/registry.py`](../../prometheus_math/registry.py) and append a
   new `Backend(...)` entry to `_BACKENDS`. Pick the right `kind` (`"python"` or
   `"binary"`), set `import_name` or `binary_name`, and assign a `category` short code.
2. Add the pip package name to the `pkgs=( ... )` arrays in **both** `arsenal-smoke`
   and `capability-tracking` in [`arsenal.yml`](./arsenal.yml). Two arrays, both must
   be updated.
3. Push. The next `capability-tracking` run will detect the new backend, commit an
   updated `.capability_snapshot.json`, and open an issue announcing it.
4. If the package needs system libraries (e.g. `libfoo-dev`), add them to the
   `apt-get install` step in both jobs. Stay tolerant — append `|| true` so a transient
   apt failure doesn't kill the job.

## Who to ping when CI breaks

- **`arsenal-smoke` red on main**: ping Techne (toolsmith). Most common cause is a new
  upstream release of a fragile package (`snappy`, `cvxpy`, `gmpy2`); the right fix is
  usually a version pin in `arsenal.yml`, not a code change.
- **`capability-tracking` opened a surprising issue**: ping Mnemosyne/Techne to confirm
  whether the gain/loss is intentional. If a backend disappeared because of an upstream
  change, decide whether to pin the old version or accept the regression.
- **`docs-regen` looping**: probably `prometheus_math.doc.arsenal()` is non-deterministic
  (e.g. embedding a timestamp). Make the generated `ARSENAL.md` fully reproducible.

## Local validation

Before pushing changes to `arsenal.yml`:

```bash
# Lint the YAML
yamllint .github/workflows/arsenal.yml

# Or, with actionlint:
actionlint .github/workflows/arsenal.yml
```

Neither is currently run in CI; they're just for sanity.
