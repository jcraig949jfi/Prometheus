"""Verification smoke: real bundles, same-seed controls, reordered completions, restart.

Two jobs.

1. TIMING. Measure one arm of every hypothesis at its declared tier, project the fixed
   manifest onto the 24-hour envelope, and apply SCALE_RULE if it does not fit with drain
   margin. Sizing happens HERE, before freeze, from measurement - not from a guess written
   into the preregistration and never checked.

2. INTEGRITY. Run a real bundle through the store twice, once with the arms completing in
   one order and once in the other, with a simulated process kill and resume in between,
   and require byte-equivalent scientific content and identical verdicts. T-P7 proves this
   on synthetic arms; this proves it on arms produced by the actual engine.

Writes only to a temp directory. Creates no production observatory.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import bundles                                   # noqa: E402
import manifest as M                             # noqa: E402
import specimens                                 # noqa: E402
import world                                     # noqa: E402

HOURS = 24.0
WORKERS = 6
DRAIN_MARGIN = 0.85          # never plan to use more than this share of the envelope
SMOKE_EPOCHS = 120           # short runs for timing; scaled up by the tier ratio


def _specimen_bytes(run_id):
    pred = pathlib.Path(__file__).resolve().parent.parent / "z80atlas-2026-09-19" / "observatory"
    for p in pred.glob("runs/*/%s/RESULT.json" % run_id):
        s = json.loads(p.read_text(encoding="ascii"))["summary"]
        g = (s.get("first_replicator") or {}).get("genome")
        return bytes.fromhex(g) if g else None
    return None


def _run_arm(arm, epochs=SMOKE_EPOCHS):
    kw = dict(arm.get("kwargs") or {})
    src = kw.pop("implant_source", None)
    if src:
        kw["implant_bytes"] = _specimen_bytes(src)
    t0 = time.time()
    res = world.run_cell(arm["cell"], arm["seed"], tier=arm["tier"], max_epochs=epochs, **kw)
    return res, time.time() - t0


def timings():
    m = M.build()
    per_h = {}
    for h in ("H1", "H2", "H3", "H4"):
        b = next(x for x in m["bundles"] if x["hypothesis_id"] == h)
        rows = []
        for arm in b["arms"]:
            _, dt = _run_arm(arm)
            rows.append((arm["arm"], dt))
        full = world.G.TIERS[b["arms"][0]["tier"]]["epochs"] if hasattr(world, "G") else None
        per_h[h] = {"tier": b["arms"][0]["tier"], "arms": rows,
                    "mean_s_at_%d_epochs" % SMOKE_EPOCHS: round(sum(d for _, d in rows) / len(rows), 3)}
    return m, per_h


def project(m, per_h):
    import grammar as G
    total = 0.0
    detail = {}
    for h, info in per_h.items():
        tier = info["tier"]
        full_epochs = G.TIERS[tier]["epochs"]
        scale = full_epochs / float(SMOKE_EPOCHS)
        per_run = info["mean_s_at_%d_epochs" % SMOKE_EPOCHS] * scale
        n = sum(b["expected_cardinality"] for b in m["bundles"] if b["hypothesis_id"] == h)
        cpu_h = per_run * n / 3600.0
        detail[h] = {"tier": tier, "runs": n, "est_s_per_run": round(per_run, 1),
                     "est_cpu_hours": round(cpu_h, 2)}
        total += cpu_h
    wall = total / WORKERS
    return {"per_hypothesis": detail, "total_cpu_hours": round(total, 2),
            "workers": WORKERS, "projected_wall_hours": round(wall, 2),
            "envelope_hours": HOURS, "usable_hours": round(HOURS * DRAIN_MARGIN, 2),
            "fits": wall <= HOURS * DRAIN_MARGIN}


def rescale(m, proj):
    """SCALE_RULE, applied only if the projection does not fit."""
    if proj["fits"]:
        return m, proj, None
    size = dict(M.SIZE)
    notes = []
    for _ in range(40):
        biggest = max(("H1", "H2", "H3", "H4"),
                      key=lambda h: proj["per_hypothesis"][h]["est_cpu_hours"])
        key = "%s_seeds" % biggest
        if size[key] <= M.MIN_SEEDS:
            notes.append("%s already at MIN_SEEDS" % biggest)
            break
        size[key] = max(M.MIN_SEEDS, int(size[key] * 0.75))
        notes.append("reduced %s to %d seeds" % (biggest, size[key]))
        m = M.build(size)
        per_h = {h: proj["per_hypothesis"][h] for h in proj["per_hypothesis"]}
        # recompute counts only; per-run cost is unchanged by seed count
        total = 0.0
        for h in per_h:
            n = sum(b["expected_cardinality"] for b in m["bundles"] if b["hypothesis_id"] == h)
            per_h[h] = dict(per_h[h], runs=n,
                            est_cpu_hours=round(per_h[h]["est_s_per_run"] * n / 3600.0, 2))
            total += per_h[h]["est_cpu_hours"]
        proj = {"per_hypothesis": per_h, "total_cpu_hours": round(total, 2),
                "workers": WORKERS, "projected_wall_hours": round(total / WORKERS, 2),
                "envelope_hours": HOURS, "usable_hours": round(HOURS * DRAIN_MARGIN, 2),
                "fits": total / WORKERS <= HOURS * DRAIN_MARGIN}
        if proj["fits"]:
            break
    return m, proj, notes


def bundle_integrity():
    """One REAL bundle, two completion orders, with a kill and resume between arms."""
    m = M.build()
    b = next(x for x in m["bundles"] if x["hypothesis_id"] == "H4")
    spec = bundles.BundleSpec(
        hypothesis_id=b["hypothesis_id"], pair_seed=b["pair_seed"],
        arms=[bundles.ArmSpec(a["arm"],
                              "TREATMENT" if a["arm"] == "endogenous" else "CONTROL",
                              a["cell"], a["seed"], a["tier"]) for a in b["arms"]],
        factor_deltas=b["factor_deltas"], expected_cardinality=b["expected_cardinality"],
        protocol_version=M.PROTOCOL_VERSION)

    results = {}
    for a in b["arms"]:
        res, dt = _run_arm(a, epochs=60)
        results[a["arm"]] = {k: res["summary"][k] for k in
                             ("held_max_final", "held_max_ever", "crossed_at_final",
                              "crossed_ever", "max_causal_replication_depth")}

    blobs, verdicts = [], []
    for order in (["endogenous", "external"], ["external", "endogenous"]):
        d = pathlib.Path(tempfile.mkdtemp(prefix="smoke_bundle_"))
        try:
            store = bundles.BundleStore(d)
            st = store.open(spec)
            st.add_result(order[0], dict(results[order[0]]))
            store.put(st)
            del store, st                                # simulated kill: nothing retained
            store2 = bundles.BundleStore(d)              # fresh process, same directory
            st2 = store2.open(spec)                      # resumed from disk alone
            st2.add_result(order[1], dict(results[order[1]]))
            store2.put(st2)
            final = store2.get(spec.bundle_id)
            blobs.append(bundles.content_bytes(final))
            verdicts.append(final.adjudicate())
        finally:
            shutil.rmtree(d, ignore_errors=True)

    same_blob = blobs[0] == blobs[1]
    same_verdict = json.dumps(verdicts[0], sort_keys=True, default=str) == \
        json.dumps(verdicts[1], sort_keys=True, default=str)
    return same_blob, same_verdict, verdicts[0]


def main():
    print("TIMING SMOKE (short runs, projected to full tier budgets)")
    print("-" * 92)
    m, per_h = timings()
    for h, info in sorted(per_h.items()):
        arms = ", ".join("%s %.2fs" % (n, d) for n, d in info["arms"])
        print("  %-3s tier %-2s  %s" % (h, info["tier"], arms))
    proj = project(m, per_h)
    print()
    print("PROJECTION onto the %.0f h envelope at %d workers" % (HOURS, WORKERS))
    print("-" * 92)
    for h, d in sorted(proj["per_hypothesis"].items()):
        print("  %-3s tier %-2s runs %-4d  %.1f s/run  %.2f cpu-h"
              % (h, d["tier"], d["runs"], d["est_s_per_run"], d["est_cpu_hours"]))
    print("  total %.2f cpu-h -> %.2f wall-h (usable %.2f h) fits=%s"
          % (proj["total_cpu_hours"], proj["projected_wall_hours"],
             proj["usable_hours"], proj["fits"]))

    m2, proj2, notes = rescale(m, proj)
    if notes:
        print()
        print("SCALE_RULE applied before freeze:")
        for n in notes:
            print("   ", n)
        print("  rescaled -> %.2f wall-h, fits=%s, runs=%d"
              % (proj2["projected_wall_hours"], proj2["fits"], m2["n_runs"]))

    print()
    print("BUNDLE INTEGRITY on real engine output (2 orders, kill + resume between arms)")
    print("-" * 92)
    sb, sv, verdict = bundle_integrity()
    print("  byte-equivalent scientific content: %s" % sb)
    print("  identical verdicts:                 %s  (%s)"
          % (sv, verdict.get("verdict") if isinstance(verdict, dict) else verdict))

    ok = proj2["fits"] and sb and sv
    out = {"timings": per_h, "projection": proj, "rescaled": proj2, "scale_notes": notes,
           "manifest_hash_after_sizing": m2["manifest_hash"], "n_runs": m2["n_runs"],
           "n_bundles": m2["n_bundles"], "by_hypothesis": m2["by_hypothesis"],
           "bundle_integrity": {"byte_equivalent": sb, "identical_verdicts": sv},
           "gate": "PASS" if ok else "FAIL"}
    pathlib.Path(__file__).resolve().parent.joinpath("SMOKE.json").write_text(
        json.dumps(out, indent=1, default=str), encoding="ascii")
    print()
    print("smoke gate:", out["gate"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
