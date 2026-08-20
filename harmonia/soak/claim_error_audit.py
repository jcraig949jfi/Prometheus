"""Audit of this worker's own claim-level error rate (Harmonia-A soak P17).

Tests SOAK-34, which asserted that my errors concentrate in claims that SPAN
cases while narrow measurements survive re-audit. SOAK-34 is itself a spanning
claim, so by its own logic it is the kind most likely to be wrong.

Result: the DIRECTION survives (21% vs 6%) but the ABSOLUTE clause is refuted --
four narrow claims were corrected -- and the ratio is NOT established at n=10.

THE LIMIT THAT MATTERS MOST, and which no care in the classification fixes:
this counts corrections I CHOSE TO MAKE. A claim that was wrong and never
revisited contributes nothing and is structurally invisible. The number is
therefore a measure of diligence, not accuracy, and 10.4% is a floor.

Read-only. Reads the worklog; writes nothing.
"""
import collections
import json
import re

WORKLOG = "engine/shadow/WORKLOG.jsonl"
AGENT = "Harmonia-A"

# Proxy classifier: keys on generalising vocabulary. Misclassifies a narrow claim
# phrased broadly, and vice versa. Stated as a proxy, not a measurement.
SPANNING = re.compile(
    r"\b(every|all |always|never|systematic|the root|pattern|families|generalis|"
    r"across|both |neither|any check|cannot be read|concentrat)\b", re.I)

# What each correction OVERTURNED. Hand-classified: this is the load-bearing
# judgement of the audit, so it is listed item by item to be disputed, not summarised.
OVERTURNED = [
    ("P9  -> P4 maxima",                "NARROW",   "specific sample-max values"),
    ("P10 -> P9 'verdicts survive'",    "SPANNING", "claim about ALL divergence verdicts"),
    ("P10 -> P4 adelic_genus verdict",  "NARROW",   "one column's verdict"),
    ("P11 -> P9 trap-2 triage",         "NARROW",   "one column's beyond-int32 verdict"),
    ("P11 -> P10 gate entry",           "SPANNING", "bias direction stated one-way"),
    ("P13 -> SOAK-27",                  "SPANNING", "cross-suite pattern"),
    ("P14 -> own probe polarity",       "NARROW",   "one probe's construction"),
    ("P15 -> P14 binary-guard framing", "SPANNING", "claim about the guard in general"),
    ("P16 -> P8 synthesis fit",         "SPANNING", "cross-trap synthesis"),
    ("P16 -> P8 scope",                 "SPANNING", "cross-trap synthesis"),
]


def load_claims():
    passes = [json.loads(l) for l in open(WORKLOG, encoding="utf-8") if l.strip()]
    mine = [p for p in passes if p.get("agent") == AGENT]
    claims = [(p["pass_id"], c) for p in mine for c in p.get("claims", [])]
    return mine, claims


def main():
    mine, claims = load_claims()
    span = [c for _, c in claims if SPANNING.search(c.get("text", ""))]
    narrow = [c for _, c in claims if not SPANNING.search(c.get("text", ""))]
    S = sum(1 for _, k, _ in OVERTURNED if k == "SPANNING")
    N = sum(1 for _, k, _ in OVERTURNED if k == "NARROW")
    total = len(claims)

    print(f"passes {len(mine)} | claims {total}")
    print("by type:", dict(collections.Counter(c.get("type") for _, c in claims)))
    print(f"classified: spanning {len(span)}  narrow {len(narrow)}")
    print(f"\ncorrections: spanning {S}, narrow {N}  (n={len(OVERTURNED)})")
    print(f"  spanning rate {S/len(span):.1%}   narrow rate {N/len(narrow):.1%}"
          f"   ratio {(S/len(span))/(N/len(narrow)):.1f}x")

    exp_s = len(OVERTURNED) * len(span) / total
    print(f"  proportional expectation: spanning {exp_s:.1f} vs observed {S}"
          f"  -> excess ~{S-exp_s:.0f} claims")
    print("\nVERDICT: direction holds; ratio NOT established at this n;"
          " 'every narrow survived' REFUTED by 4 counterexamples.")
    print("FLOOR, not estimate: undetected errors are invisible to this method.")


if __name__ == "__main__":
    main()
