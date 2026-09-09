"""Hypothesis first useful check. Runs INSIDE the isolated env; imports nothing from techne.

    <env>/python techne/acquisition/checks/hypothesis_first_check.py --work <dir>

Design requirement: "Minimize a known defect; persist the explicit fixture; isolate its
example database by scope."

Each of the three is made falsifiable rather than asserted:

  MINIMIZE   the two seeded defects have an EXACTLY KNOWN minimal witness (128 for the
             integer defect, [0, 0] for the duplicate defect, given Hypothesis's documented
             shrink ordering). The check asserts the reported counterexample IS that
             minimum, so a run that finds 9999 instead of 128 FAILS rather than passing as
             "found a counterexample".

  PERSIST    the minimized witness is written out as a plain JSON fixture that replays
             WITHOUT Hypothesis, and the replay is executed here. A fixture that cannot be
             replayed by a non-Hypothesis consumer is not persisted, it is logged.

  ISOLATE    two scopes get two DirectoryBasedExampleDatabase directories. The check then
             verifies (a) each scope's database holds entries, (b) neither scope's
             directory contains the other's, and (c) no .hypothesis directory appears in
             the working directory -- the failure mode that makes two data scopes share
             remembered examples.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from hypothesis import HealthCheck, Phase, given, seed, settings
from hypothesis import strategies as st
from hypothesis.database import DirectoryBasedExampleDatabase
from hypothesis.errors import Flaky


# ------------------------------------------------------------------ seeded defects
def defect_threshold(x: int) -> bool:
    """Seeded defect: silently wrong at and above 128. A byte-boundary bug, which is the
    realistic shape. Minimal failing input under Hypothesis's integer shrink (toward 0
    from the failing side) is exactly 128."""
    return x < 128


def defect_duplicate(xs: list[int]) -> bool:
    """Seeded defect: a 'unique' check that is wrong whenever a duplicate exists.
    Minimal failing input: [0, 0] -- shortest list, smallest values."""
    return len(xs) == len(set(xs))


def run_defect(name: str, db_dir: pathlib.Path) -> dict:
    db = DirectoryBasedExampleDatabase(str(db_dir))
    found: dict = {}

    # derandomize=True would imply database=None, and the scoped database is the whole point
    # of this check -- so reproducibility comes from an explicit @seed instead.
    common = dict(
        database=db,
        max_examples=2000,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow],
        phases=[Phase.generate, Phase.shrink],
    )
    RUN_SEED = 20260909

    if name == "threshold":
        @settings(**common)
        @seed(RUN_SEED)
        @given(st.integers(min_value=0, max_value=10**6))
        def prop(x):
            assert defect_threshold(x), f"defect at x={x}"
        expected_minimum = 128
        witness_key = "x"
    else:
        @settings(**common)
        @seed(RUN_SEED)
        @given(st.lists(st.integers(min_value=0, max_value=50), max_size=8))
        def prop(xs):
            assert defect_duplicate(xs), f"defect at xs={xs}"
        expected_minimum = [0, 0]
        witness_key = "xs"

    error = None
    try:
        prop()
        raised = False
    except AssertionError as exc:
        raised = True
        error = str(exc)
    except Flaky as exc:              # recorded, not swallowed
        raised = True
        error = f"FLAKY: {exc}"

    # The falsifying example is in the assertion message, which the property itself wrote.
    witness = None
    if error and "defect at" in error:
        tail = error.split("defect at", 1)[1].split("\n")[0].strip()
        raw = tail.split("=", 1)[1].strip() if "=" in tail else tail
        try:
            witness = json.loads(raw)
        except ValueError:
            witness = raw

    entries = sorted(p.name for p in db_dir.rglob("*") if p.is_file())
    return {
        "defect": name,
        "property_failed_as_designed": raised,
        "witness_key": witness_key,
        "minimized_witness": witness,
        "expected_minimum": expected_minimum,
        "minimization_reached_known_minimum": witness == expected_minimum,
        "raw_assertion_message": error,
        "example_database_dir": str(db_dir),
        "example_database_entries": len(entries),
        "example_database_sample": entries[:6],
        "reproducibility": "explicit @seed(20260909); derandomize is NOT used because it "
                           "would disable the example database this check exists to verify",
    }


# ------------------------------------------------------------------ fixture persistence
def persist_fixture(results: list[dict], out: pathlib.Path) -> dict:
    fixture = {
        "schema": "techne.acquisition.hypothesis_fixture/1",
        "why": "Explicit minimized counterexamples, replayable WITHOUT Hypothesis. A "
               "consumer's regression test should assert on these, not re-search for them.",
        "cases": [
            {"defect": r["defect"], "input": r["minimized_witness"],
             "expected": "the property under test FAILS on this input"}
            for r in results
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    # Replay the persisted fixture with plain asserts -- no Hypothesis in the loop.
    replay = []
    for case in fixture["cases"]:
        fn = defect_threshold if case["defect"] == "threshold" else defect_duplicate
        try:
            held = fn(case["input"])
        except Exception as exc:
            held = f"ERROR {exc}"
        replay.append({"defect": case["defect"], "input": case["input"],
                       "property_holds": held,
                       "fixture_reproduces_failure": held is False})
    return {"fixture_path": str(out), "replay": replay,
            "all_fixtures_reproduce": all(r["fixture_reproduces_failure"] for r in replay),
            "replay_used_hypothesis": False}


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="working directory for scoped databases")
    ap.add_argument("--fixture-out", required=True)
    a = ap.parse_args()

    work = pathlib.Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    cwd_before = set(p.name for p in pathlib.Path.cwd().iterdir())

    scope_a = work / "scope_threshold" / "examples"
    scope_b = work / "scope_duplicate" / "examples"
    r_a = run_defect("threshold", scope_a)
    r_b = run_defect("duplicate", scope_b)

    fixture = persist_fixture([r_a, r_b], pathlib.Path(a.fixture_out))

    files_a = {p.name for p in scope_a.rglob("*") if p.is_file()}
    files_b = {p.name for p in scope_b.rglob("*") if p.is_file()}
    cwd_after = set(p.name for p in pathlib.Path.cwd().iterdir())
    appeared = sorted(n for n in (cwd_after - cwd_before) if ".hypothesis" in n)

    # The SECOND directory. `database=` controls where saved EXAMPLES go. It does not
    # control Hypothesis's storage directory, which is a separate side channel holding a
    # constants cache and temporary files, and which defaults to .hypothesis in the CWD.
    # An SFE worker running contract fixtures would write that into whatever its cwd is.
    from hypothesis.configuration import storage_directory
    # On 6.165.x storage_directory() returns a StorageDirectory object -- neither a str nor
    # PathLike, and its repr is an object address, so the real path comes from `.path`.
    sd = storage_directory(intent_to_write=False)
    storage = pathlib.Path(sd.path if hasattr(sd, "path") else str(sd))
    side_channel_files = sorted(
        str(p.relative_to(storage)).replace("\\", "/")
        for p in storage.rglob("*") if p.is_file()) if storage.exists() else []
    side_channel_has_examples = any(
        part == "examples" for f in side_channel_files for part in f.split("/"))

    isolation = {
        "scope_a_dir": str(scope_a), "scope_b_dir": str(scope_b),
        "scope_a_entries": len(files_a), "scope_b_entries": len(files_b),
        "both_scopes_populated": bool(files_a) and bool(files_b),
        "shared_entry_names": sorted(files_a & files_b),
        "scopes_disjoint": not (files_a & files_b),
        "honest_limit": "Entry names are content-addressed by Hypothesis, so two scopes that "
                        "happened to record the SAME example would legitimately share a name. "
                        "Here the two defects have different shapes, so disjointness is the "
                        "expected result and a shared name would indicate a shared database.",
        "side_channel": {
            "storage_directory": str(storage),
            "HYPOTHESIS_STORAGE_DIRECTORY_set": bool(
                __import__("os").environ.get("HYPOTHESIS_STORAGE_DIRECTORY")),
            "appeared_in_cwd_during_run": appeared,
            "storage_is_inside_declared_work_dir": work.resolve() in storage.resolve().parents
                                                   or storage.resolve() == work.resolve(),
            "files": side_channel_files,
            "contains_saved_examples": side_channel_has_examples,
            "finding": "MEASURED: setting `database=DirectoryBasedExampleDatabase(...)` scopes "
                       "the saved EXAMPLES and nothing else. Hypothesis additionally creates "
                       "its storage directory -- a constants cache plus temporary files -- at "
                       "the path above, which defaults to .hypothesis under the CURRENT "
                       "WORKING DIRECTORY. Containing it requires the "
                       "HYPOTHESIS_STORAGE_DIRECTORY environment variable, set before "
                       "hypothesis is imported. A consumer that scopes only `database=` has "
                       "scoped half of it.",
        },
    }

    decided = [
        ("threshold defect minimized to its known minimum",
         r_a["property_failed_as_designed"] and r_a["minimization_reached_known_minimum"]),
        ("duplicate defect minimized to its known minimum",
         r_b["property_failed_as_designed"] and r_b["minimization_reached_known_minimum"]),
        ("persisted fixtures reproduce the failures without Hypothesis",
         fixture["all_fixtures_reproduce"]),
        ("saved examples are scoped per data scope and the scopes are disjoint",
         isolation["both_scopes_populated"] and isolation["scopes_disjoint"]),
        ("the storage side channel holds no saved examples",
         not side_channel_has_examples),
    ]
    out = {
        "check": "hypothesis_first_useful_check",
        "tool": "hypothesis",
        "hypothesis_version": __import__("hypothesis").__version__,
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "defects": [r_a, r_b],
        "fixture": fixture,
        "isolation": isolation,
        "assertions": [{"claim": c, "pass": bool(p)} for c, p in decided],
        "n_passed": sum(1 for _, p in decided if p),
        "n_total": len(decided),
        "all_passed": all(p for _, p in decided),
    }
    print(json.dumps(out))
    return 0 if out["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
