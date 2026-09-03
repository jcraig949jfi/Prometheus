"""Adjudicate two replay artifacts against the frozen two-layer numerical contract.

    python proteus/v0_6/run_replay_compare.py A.json B.json [...]

EXACT layer must be byte-identical (compared by digest AND field by field, so a digest
collision or a missing field cannot pass silently). NUMERICAL layer is compared against the
tolerances frozen in PREREG_V0_6.json, which were set by conditioning and not by observed
differences. Byte-identity of the numerical layer is REPORTED but is not the criterion.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = {"pi": (1e-9, 1e-6), "residual_l1": (1e-10, 0.0), "max_abs_current": (1e-12, 0.0),
       "total_abs_current": (1e-12, 0.0), "sigma": (1e-9, 0.0), "one_way_edges": (0.0, 0.0)}


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def cmp_num(a, b, absol, rel):
    d = abs(a - b)
    return d, (d <= absol or (rel > 0 and abs(b) > 0 and d / abs(b) <= rel))


def main():
    paths = sys.argv[1:]
    if len(paths) < 2:
        print("need >= 2 replay artifacts")
        return 2
    arts = [(p, load(p)) for p in paths]
    ref_p, ref = arts[0]
    rows, exact_ok, num_ok = [], True, True
    for p, a in arts[1:]:
        e_digest = a["exact_layer_digest"] == ref["exact_layer_digest"]
        # field-by-field, so digest equality is corroborated rather than trusted
        e_fields = {k: (a["exact_layer"].get(k) == ref["exact_layer"].get(k))
                    for k in sorted(set(ref["exact_layer"]) | set(a["exact_layer"]))}
        e_all = e_digest and all(e_fields.values())
        exact_ok = exact_ok and e_all
        devs = {}
        for k, (absol, rel) in TOL.items():
            if k == "pi":
                worst, ok = 0.0, True
                for s, v in ref["numerical_layer"]["pi"].items():
                    d, o = cmp_num(a["numerical_layer"]["pi"][s], v, absol, rel)
                    worst = max(worst, d)
                    ok = ok and o
                devs["pi_max_abs_dev"] = worst
                devs["pi_within_tolerance"] = ok
            else:
                d, o = cmp_num(a["numerical_layer"][k], ref["numerical_layer"][k], absol, rel)
                devs[k + "_abs_dev"] = d
                devs[k + "_within_tolerance"] = o
        n_all = all(v for k, v in devs.items() if k.endswith("_within_tolerance"))
        num_ok = num_ok and n_all
        rows.append({
            "reference_host": ref["host"], "host": a["host"],
            "exact_layer_digest_equal": e_digest,
            "exact_layer_fields_equal": e_fields,
            "exact_layer_identical": e_all,
            "numerical_layer_digest_equal": (a["numerical_layer_digest"]
                                             == ref["numerical_layer_digest"]),
            "numerical_layer_within_tolerance": n_all,
            "numerical_deviations": devs,
        })
    out = {"schema_version": "proteus.v0_6_replay_comparison.v1",
           "artifacts": [p for p, _ in arts],
           "tolerances_abs_rel": {k: list(v) for k, v in TOL.items()},
           "comparisons": rows,
           "exact_layer_passed": exact_ok, "numerical_layer_passed": num_ok,
           "contract_passed": exact_ok and num_ok,
           "numerical_layer_byte_identical_on_all_tested_hosts":
               all(r["numerical_layer_digest_equal"] for r in rows),
           "claim_bounded_to_hosts": [a["host"] for _p, a in arts]}
    with open(os.path.join(HERE, "REPLAY_COMPARISON.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    for r in rows:
        print(f"{r['host']['python']:<8} vs {r['reference_host']['python']:<8} "
              f"exact {'IDENTICAL' if r['exact_layer_identical'] else 'DIFFERS'} | "
              f"numerical digest "
              f"{'IDENTICAL' if r['numerical_layer_digest_equal'] else 'differs'} | "
              f"pi max dev {r['numerical_deviations']['pi_max_abs_dev']:.3e} | "
              f"tolerance {'PASS' if r['numerical_layer_within_tolerance'] else 'FAIL'}")
    print(f"CONTRACT {'PASSED' if out['contract_passed'] else 'FAILED'}")
    return 0 if out["contract_passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
