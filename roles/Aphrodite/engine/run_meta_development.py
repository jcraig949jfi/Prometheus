"""TIER 3A meta-development: the donor improves its own proposal library.

AMENDMENT 9 section 3. The donor sees ONLY the meta-development problems and
its own successful artifacts. It never sees the tribunal, the meta-tribunal
families, or any evaluation outside its own development instances.

Output: the frozen Tier-3 artifact (a proposal library), canonicalised and
hashed at a fixed positional boundary. No adaptation after freeze.
"""
import json
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as E        # noqa: E402
import improver as I      # noqa: E402

DEV_PER_PROBLEM = 4
WORKER_ESCROW = 400_000        # per meta-dev problem, per library evaluation
META_ESCROW = 20_000_000       # total meta-level budget
SEED_TAG = "T3A-meta"


def dev_instances(family, rep):
    return I.tasks(family, DEV_PER_PROBLEM,
                   E.dev_entropy("%s-%s-%d" % (SEED_TAG, family, rep), 0))


def evaluate_library(lib, reps, meta_escrow, record_successes=None,
                     record_failures=None):
    """META-FITNESS (immutable): censored mean charges to a development-exact
    solution over the meta-dev problems. The tribunal plays no part."""
    costs = []
    for fam in I.META_DEV:
        for rep in range(reps):
            esc = E.Escrow(WORKER_ESCROW)
            rng = random.Random(E.search_entropy("%s-%s-%d" % (SEED_TAG, fam, rep)))
            got = I.search(lib, dev_instances(fam, rep), esc, WORKER_ESCROW, rng)
            meta_escrow.charge(min(esc.spent, meta_escrow.remaining()))
            if got:
                prog, coord, charges = got
                costs.append(charges)
                if record_successes is not None:
                    record_successes.append(prog)
            else:
                costs.append(WORKER_ESCROW)
                if record_failures is not None:
                    record_failures.append(fam)
    return statistics.mean(costs), costs


def main():
    t0 = time.perf_counter()
    meta = E.Escrow(META_ESCROW)
    base = I.pristine_library()

    # 1-2. the donor searches its own development problems and observes its
    # own successful artifacts. Nothing else is observed.
    observed, failed = [], []
    base_fitness, base_costs = evaluate_library(base, 2, meta, observed, failed)

    # bodies the donor tried early and that did not succeed -- used ONLY to
    # construct the declared SHAM, never to build the evolved library
    failed_bodies = [b for b in __import__("basis_v4").BODY_SPACE[:8]
                     if b not in {p[2] for p in observed}]

    # 3-5. generate candidate libraries with the immutable operators, evaluate
    # them on the meta-dev problems only, and select under the meta escrow.
    rows = []
    for name, lib in I.candidate_libraries(observed, failed_bodies, base):
        ok, bad = lib.desugars_into_g4()
        if not ok:
            rows.append({"operator": name, "rejected": "does not desugar into G4",
                         "offending": bad[:5]})
            continue
        fit, costs = evaluate_library(lib, 2, meta)
        rows.append({"operator": name, "fitness_censored_mean_charges": round(fit, 1),
                     "entries": [e["name"] for e in lib.entries],
                     "library_size": lib.size(), "sha256": lib.sha256(),
                     "costs": costs})
    scored = [r for r in rows if "fitness_censored_mean_charges" in r]
    scored.sort(key=lambda r: (r["fitness_censored_mean_charges"], len(r["entries"]),
                               r["library_size"]))
    best = scored[0]

    chosen = None
    for name, lib in I.candidate_libraries(observed, failed_bodies, base):
        if name == best["operator"]:
            chosen = lib
            break

    sham = I.sham_library(failed_bodies, base)
    artifact = {
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "meta_generation": 1,
        "selected_operator": best["operator"],
        "evolved_library": chosen.entries,
        "evolved_library_sha256": chosen.sha256(),
        "evolved_library_size": chosen.size(),
        "pristine_library_sha256": base.sha256(),
        "pristine_library_size": base.size(),
        "sham_library": sham.entries,
        "sham_library_sha256": sham.sha256(),
        "sham_library_size": sham.size(),
        "observed_successful_programs": [list(p) for p in observed],
        "meta_dev_families": I.META_DEV,
        "candidate_evaluations": rows,
        "meta_charges_spent": meta.spent,
        "meta_escrow": META_ESCROW,
        "seconds": round(time.perf_counter() - t0, 1),
        "note": ("the donor observed only its own development problems and its own "
                 "successful artifacts; the tribunal and the meta-tribunal families "
                 "were not readable at any point"),
    }
    (HERE / "TIER3A_ARTIFACT_2026-09-22.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in artifact.items()
                      if k not in ("candidate_evaluations", "evolved_library",
                                   "sham_library")}, indent=2, sort_keys=True))
    for r in rows:
        print(json.dumps({k: v for k, v in r.items() if k != "costs"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
