"""Batch 10 P5: test environment-dependent correctness by an explicit world change.

The census (env_assumption_census) found 14 specimens carrying the SAME pattern that broke
md5-rfc1321 -- a fixed width asserted onto `long`. Presence of a pattern is not a defect, so each
runnable, oracle-backed candidate is RUN AGAIN, unchanged, in a different world (32-bit userland),
and its oracle outcome is compared with its native world.

Nothing is manufactured and nothing is patched: same preserved body, same recipe, different image.
harvest.run(image=...) never persists, so a foreign-world probe cannot overwrite a real classification.

Outcomes are kept distinct, because they mean different things:
  AGREES              same oracle verdict in both worlds -> correctness does not depend on this axis
  INCONCLUSIVE_NATIVE_FAILS  the fossil fails in its OWN world, so nothing can be concluded
  DIVERGES            passes in one world, fails its oracle in the other -> NATURAL SPECIMEN
  INCONCLUSIVE_BUILD  did not build in the other world -> says nothing about correctness

    python run_world_change.py -> WORLD_CHANGE_<date>.json
"""
import json, pathlib, time

from .. import harvest, record

HERE = pathlib.Path(__file__).resolve().parent
DATE = "2026-09-13"
WORLD_32 = "prometheus-fossil-i386:bookworm"
WORLD_64 = "prometheus-fossil-c:bookworm"


def other_world(native_image):
    """The other world must actually DIFFER from the native one. md5-rfc1321 is native to the
    32-bit image, so probing it 'in i386' compared a world against itself and the positive
    control silently passed as AGREES -- which is how this bug was caught."""
    return WORLD_64 if (native_image or "").startswith("prometheus-fossil-i386") else WORLD_32

# md5-rfc1321 is the POSITIVE CONTROL: it is already known to diverge, so if the method reports
# AGREES for it, the method is broken and no other row can be trusted.
CANDIDATES = ["md5-rfc1321", "cjson-1.7.18", "femtolisp", "espresso-logic", "zchaff-2007", "tinycc"]
# Bounded on purpose. NOT tested this round (heavier builds), named rather than silently dropped:
NOT_TESTED = ["bdwgc-8.2.6", "dmtcp-3.1.2", "glpk-5.0", "gnu-prolog-1.5.0", "pari-gp-2.17",
              "valgrind-helgrind-fixtures-3.19", "openssl-1.0.1f-heartbleed (SOURCE_ONLY)",
              "xv6-riscv (NOT_ATTEMPTED)"]


def _probe(sid, image):
    try:
        r = harvest.run(sid, timeout=1800, image=image)
        builds = all(b.get("ok") for b in r.get("build", [])) if r.get("build") else True
        return {"classification": r.get("classification"), "ok": bool(r.get("ok")),
                "builds": bool(builds),
                "failed_runs": [x.get("why_not") for x in r.get("runs", []) if not x.get("ok")]}
    except Exception as e:
        return {"classification": "PROBE_ERROR", "ok": False, "builds": False, "error": str(e)[:200]}


def main(argv=None):
    import sys
    sel = (argv if argv is not None else sys.argv[1:]) or CANDIDATES
    rows = []
    for sid in sel:
        rec = record.load(sid)
        native_image = json.loads((harvest.vault.specimen_dir(sid) / "recipe.json")
                                  .read_text(encoding="utf-8")).get("image")
        native = _probe(sid, native_image)
        ow = other_world(native_image)
        other = _probe(sid, ow)
        if not other["builds"]:
            verdict = "INCONCLUSIVE_BUILD"
        elif not native["ok"]:
            # It fails in its OWN world, so this run cannot speak to world-dependence at all.
            # Without this, two failures for unrelated (e.g. host) reasons read as "AGREES".
            verdict = "INCONCLUSIVE_NATIVE_FAILS"
        elif native["ok"] == other["ok"]:
            verdict = "AGREES"
        else:
            verdict = "DIVERGES"
        rows.append({"specimen_id": sid, "native_image": native_image, "other_image": ow,
                     "native": native, "other": other, "verdict": verdict,
                     "recorded_classification": rec.get("run_classification")})
        print("%-34s native_ok=%-5s other_ok=%-5s builds_other=%-5s %s" % (
            sid, native["ok"], other["ok"], other["builds"], verdict))

    control = next((r for r in rows if r["specimen_id"] == "md5-rfc1321"), None)
    # Distinguish "the control ran and failed" from "the control was not in this selection".
    # Reporting a missing control as False would look like a broken method.
    control_ok = "NOT_RUN" if control is None else bool(control["verdict"] == "DIVERGES")
    doc = {"schema": "techne.fossil.world_change/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "census": "techne/fossils/ENV_ASSUMPTION_CENSUS_2026-09-13.json",
           "other_world_rule": "the world that differs from the fossil's native image (64-bit <-> 32-bit)",
           "positive_control": "md5-rfc1321 must report DIVERGES; if it does not, the method is broken",
           "positive_control_held": control_ok,
           "tested": sel, "full_candidate_set": CANDIDATES, "not_tested_this_round": NOT_TESTED,
           "rows_trustworthy": control_ok is True,
           "natural_specimens_found": [r["specimen_id"] for r in rows
                                       if r["verdict"] == "DIVERGES" and r["specimen_id"] != "md5-rfc1321"],
           "note": "A world probe never persists; recorded classifications are untouched. "
                   "INCONCLUSIVE_BUILD is not evidence of environment-dependent correctness.",
           "rows": rows}
    op = HERE / ("WORLD_CHANGE_%s.json" % DATE)
    op.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("\npositive control held:", control_ok)
    print("natural specimens (besides the control):", doc["natural_specimens_found"] or "NONE")
    print("wrote", op)


if __name__ == "__main__":
    main()
