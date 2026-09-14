"""P3: does the Kalman-divergence claim survive when its world stops floating? (batch 11)

The ESTIMATION_DIVERGENCE dataset (batch 07) was produced with `pip install -q numpy scipy` -- no
versions. Searching every artifact for the world that produced it finds bare package NAMES and no
version anywhere: the record, the recipe, the receipts and the dataset all omit it.

    ORIGINAL WORLD: UNRECOVERABLE FROM EVIDENCE.

That half of P3 cannot be answered and is reported as such rather than guessed. What CAN be
answered is the question the charter actually cares about: pin the world and see whether the claim
reproduces. The DRIVER IS IMPORTED FROM THE ORIGINAL EXPERIMENT, so the fossil body, the inputs,
the oracle, the scoring and the divergence threshold are literally the same code -- only the world
changes.

PREREGISTERED WORLDS (fixed before running; not chosen after seeing results):
    W_2024      numpy==1.26.4  scipy==1.11.4    a plausible world of the numpy 1.x era
    W_CURRENT   numpy==2.1.3   scipy==1.14.1    a plausible current world (numpy 2.x)
    W_FLOATING  numpy scipy                     exactly what the recipe does today: unpinned

PREREGISTERED PREDICTION: the experiment is float64 linear algebra plus PCG64 noise, and NumPy
guarantees Generator stream stability for a given bit generator across versions. I therefore expect
CLASSIFICATION_PRESERVED in every world, and probably bit-exact agreement. A changed classification
would be a major finding; a bit-level difference with preserved classification would be the
ordinary outcome for floating-point under a different BLAS.

OUTCOME LADDER (strongest first):
    BIT_EXACT                 every recorded float identical
    NUMERICALLY_EQUIVALENT    all floats agree to 1e-9 relative
    CLASSIFICATION_PRESERVED  floats differ but every `diverged` flag matches
    CLASSIFICATION_CHANGED    at least one `diverged` flag differs
Unlike the original, this dataset RECORDS THE WORLD IT RAN IN (pip freeze of the two packages).

    python -m techne.fossils.pressure.run_filterpy_replication
"""
import json, pathlib, subprocess, time

from .run_estimation_divergence import DRIVER, VAULT, FP_TREE   # the SAME experiment code

HERE = pathlib.Path(__file__).resolve().parent
DATE = "2026-09-13"
ORIGINAL = HERE / "ESTIMATION_DIVERGENCE_2026-09-13.json"

WORLDS = [
    ("W_2024", "numpy==1.26.4 scipy==1.11.4"),
    ("W_CURRENT", "numpy==2.1.3 scipy==1.14.1"),
    ("W_FLOATING", "numpy scipy"),
]

SCRIPT = (
    "pip install -q %(spec)s >/dev/null 2>&1 || { echo WORLD_UNAVAILABLE; exit 0; }\n"
    "python -c \"import numpy,scipy;print('WORLD numpy=%%s scipy=%%s'%%(numpy.__version__,scipy.__version__))\"\n"
    "cat > /tmp/drv.py <<'PYEOF'\n" + DRIVER + "\nPYEOF\n"
    "PYTHONPATH=%(tree)s python /tmp/drv.py\n"
)


def _q(s):
    return "'" + s.replace("'", "'\\''") + "'"


def run_world(spec):
    script = SCRIPT % {"spec": spec, "tree": FP_TREE}
    out = subprocess.run(["wsl.exe", "-e", "bash", "-lc",
        "docker run --rm -v %s:/vault:ro python:3.11-slim bash -lc %s" % (VAULT, _q(script))],
        capture_output=True, text=True, timeout=2400).stdout
    rows, world = None, ""
    for line in out.splitlines():
        if line.startswith("WORLD "):
            world = line[6:].strip()
        elif line.startswith("RESULT "):
            rows = json.loads(line[len("RESULT "):])
    if "WORLD_UNAVAILABLE" in out:
        return None, "UNAVAILABLE"
    return rows, world


FLOAT_KEYS = ("final_gain", "reported_sigma_final", "actual_abs_error_final",
              "actual_rmse_after_manoeuvre", "reported_sigma_after_manoeuvre",
              "overconfidence_ratio_error_over_reported")


def compare(orig, new):
    if new is None:
        return "WORLD_UNAVAILABLE", {}
    if len(orig) != len(new):
        return "CLASSIFICATION_CHANGED", {"reason": "row count differs"}
    if any(o["diverged"] != n["diverged"] for o, n in zip(orig, new)):
        return "CLASSIFICATION_CHANGED", {
            "flags_original": [o["diverged"] for o in orig], "flags_new": [n["diverged"] for n in new]}
    worst, worst_key = 0.0, ""
    exact = True
    for o, n in zip(orig, new):
        for k in FLOAT_KEYS:
            a, b = o.get(k), n.get(k)
            if a is None or b is None:
                continue
            if a != b:
                exact = False
            rel = abs(a - b) / max(abs(a), 1e-300)
            if rel > worst:
                worst, worst_key = rel, k
    if exact:
        return "BIT_EXACT", {"worst_rel_diff": 0.0}
    if worst <= 1e-9:
        return "NUMERICALLY_EQUIVALENT", {"worst_rel_diff": worst, "worst_key": worst_key}
    return "CLASSIFICATION_PRESERVED", {"worst_rel_diff": worst, "worst_key": worst_key}


def main():
    orig = json.loads(ORIGINAL.read_text(encoding="utf-8"))["rows"]
    results = []
    for name, spec in WORLDS:
        rows, world = run_world(spec)
        verdict, detail = compare(orig, rows)
        results.append({"world": name, "requested": spec, "resolved": world,
                        "verdict": verdict, "detail": detail, "rows": rows})
        print("%-12s %-28s %-26s %s" % (name, spec, world or "-", verdict))
    doc = {"schema": "techne.fossil.filterpy_replication/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "fossil": "filterpy-labbe",
           "original_dataset": ORIGINAL.name,
           "original_world": "UNRECOVERABLE_FROM_EVIDENCE",
           "original_world_search": "record.json, recipe.json, all receipts and the dataset itself "
                                    "were searched; every one names the packages and none names a version.",
           "driver_provenance": "imported from run_estimation_divergence (same body, inputs, oracle, "
                                "scoring and threshold; only the world differs)",
           "preregistered_worlds": [w[0] for w in WORLDS],
           "preregistered_prediction": "CLASSIFICATION_PRESERVED in every world; bit-exactness plausible "
                                       "because PCG64 streams are version-stable and the arithmetic is float64",
           "outcome_ladder": ["BIT_EXACT", "NUMERICALLY_EQUIVALENT", "CLASSIFICATION_PRESERVED",
                              "CLASSIFICATION_CHANGED", "WORLD_UNAVAILABLE"],
           "results": results}
    op = HERE / ("FILTERPY_REPLICATION_%s.json" % DATE)
    op.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("wrote", op)


if __name__ == "__main__":
    main()
