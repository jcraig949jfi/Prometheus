"""
Cross-category transfer tests: does the Megethos-Arithmos coordinate system
extend beyond pure mathematics into physics, chemistry, and chaos?

Tests 8 specific domain pairs spanning the new physical/chemical domains
and established math domains.
"""
import sys, json, time
from pathlib import Path
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from harmonia.src.tensor_falsify import falsify_bond, FalsificationReport

PAIRS = [
    {
        "d1": "chemistry", "d2": "materials",
        "inference": "Both have band gap / molecular properties — should couple via shared material science phonemes"
    },
    {
        "d1": "rmt", "d2": "ec_zeros",
        "inference": "GUE statistics vs EC zeros — should be the SAME objects from different angles (Montgomery-Odlyzko)"
    },
    {
        "d1": "dynamics", "d2": "oeis",
        "inference": "Both are OEIS sequences — dynamics has Lyapunov exponents, oeis has growth stats"
    },
    {
        "d1": "spectral_sigs", "d2": "modular_forms",
        "inference": "Formula spectra vs modular form invariants — spectral decomposition connection"
    },
    {
        "d1": "codata", "d2": "materials",
        "inference": "Physical constants vs material properties — fundamental physics constraining materials"
    },
    {
        "d1": "pdg_particles", "d2": "chemistry",
        "inference": "Particle properties vs molecular properties — subatomic to molecular scale"
    },
    {
        "d1": "chemistry", "d2": "elliptic_curves",
        "inference": "The big cross-category test: molecular chemistry vs pure number theory"
    },
    {
        "d1": "rmt", "d2": "modular_forms",
        "inference": "Quantum chaos <-> number theory — the deep connection (Bohigas-Giannoni-Schmit)"
    },
]


def main():
    results = []
    print("=" * 80)
    print("CROSS-CATEGORY TRANSFER TESTS")
    print("Does Megethos-Arithmos extend beyond pure mathematics?")
    print("=" * 80)

    for i, pair in enumerate(PAIRS):
        d1, d2 = pair["d1"], pair["d2"]
        print(f"\n[{i+1}/8] {d1} <-> {d2}")
        print(f"  Hypothesis: {pair['inference']}")
        print(f"  Running falsification battery...")

        try:
            report = falsify_bond(d1, d2, subsample=2000, inference=pair["inference"])
            print(report.summary())

            # Convert to serializable dict
            rd = asdict(report)
            rd["overall_verdict"] = "PASS" if report.surviving_rank > 0 else "FAIL"
            results.append(rd)

            verdict = "PASS" if report.surviving_rank > 0 else "FAIL"
            print(f"\n  >>> VERDICT: {verdict} (rank {report.original_rank} -> {report.surviving_rank}, {report.wall_time:.1f}s)")
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback; traceback.print_exc()
            results.append({
                "domain_a": d1, "domain_b": d2,
                "overall_verdict": "ERROR",
                "error": str(e),
                "inference": pair["inference"],
            })

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    passes = [r for r in results if r.get("overall_verdict") == "PASS"]
    fails = [r for r in results if r.get("overall_verdict") == "FAIL"]
    errors = [r for r in results if r.get("overall_verdict") == "ERROR"]

    print(f"\nPASS: {len(passes)}  FAIL: {len(fails)}  ERROR: {len(errors)}")

    if passes:
        print("\nPASSING transfers (genuine cross-domain connections):")
        for r in passes:
            print(f"  + {r['domain_a']} <-> {r['domain_b']}: rank {r.get('original_rank','?')} -> {r.get('surviving_rank','?')}")
            for t in r.get("tests", []):
                icon = "+" if t["verdict"] == "SURVIVES" else "X"
                print(f"    [{icon}] {t['test']}: {t['verdict']} (val={t['value']:.3f}, thresh={t['threshold']:.3f})")

    if fails:
        print("\nFAILING transfers:")
        for r in fails:
            print(f"  X {r['domain_a']} <-> {r['domain_b']}: rank {r.get('original_rank','?')} -> {r.get('surviving_rank','?')}")
            for t in r.get("tests", []):
                icon = "+" if t["verdict"] == "SURVIVES" else "X"
                print(f"    [{icon}] {t['test']}: {t['verdict']} (val={t['value']:.3f}, thresh={t['threshold']:.3f})")

    # Save
    out_path = Path(__file__).resolve().parents[1] / "results" / "cross_category_transfer.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "description": "Cross-category transfer tests: math vs physics/chemistry/chaos",
            "subsample": 2000,
            "n_pairs": len(PAIRS),
            "n_pass": len(passes),
            "n_fail": len(fails),
            "n_error": len(errors),
            "results": results,
        }, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
