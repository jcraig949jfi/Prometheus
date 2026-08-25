"""EXIT REVIEW 3 - independent gate-fire of INVARIANT 7 (Harmonia B).

I am the only gate on the decisive arms, and the party who built INV 7 is the party a
clear review unblocks. So INV 7 is not accepted on its author's demonstration. This
plants defects MYSELF, through the same code path the real packets take, and asserts
INV 7 rejects each one.

Two of the four plants target blind spots I suspected from reading `constantize`
BEFORE running anything, and they are recorded here as predictions:

  P-A  `constantize` blanks the treatment with `m.group(0).replace(m.group("items"), ...)`
       - a STRING replace, not a positional splice, and with no count limit. If the items
       text also occurs elsewhere inside the matched region, the replace over-blanks and
       could erase a nuisance difference along with the treatment. PREDICTED: exploitable
       in principle; unclear whether reachable on this template.
  P-B  `constantize` ends with `payload.strip()`. Leading/trailing WHITESPACE differences
       between arms are therefore erased before comparison. That is the same failure class
       as the isomorphism test that stripped the lead line and then certified isomorphism.
       PREDICTED: INV 7 does NOT catch a pure trailing-whitespace arm label.

Plants:
  1. LEAD LINE          the historical 400/400 defect, re-injected on 2 of 6 arms
  2. SLUG ONE DIGIT     a single digit changed on one arm (the claim in prereg section 9)
  3. TRAILING SPACE     one arm gets a trailing space  <- tests P-B
  4. SPARSITY TWEAK     one arm's non-treatment frame text altered by one character

A plant that INV 7 does not reject is a hole in the only gate now standing between this
campaign and its decisive arms.

Run:  PYTHONPATH=. python harmonia/probe/exit3_inv7_gatefire.py
"""
from __future__ import annotations

import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ergon.probe.packet_invariants import payload_of, nontreatment_identical_across_arms as nontreatment_identical  # noqa: E402
from ergon.probe.adversarial_leakage import constantize                        # noqa: E402
import ergon.probe.campaign as C                                               # noqa: E402

CARRYING = ["F-null", "F-generic", "F-prom-retrieved",
            "F-hint", "F-null+hint", "F-prom+hint"]
ALL = ["F0"] + CARRYING


def load(n_tasks=25):
    rows = C.manifest()
    gold = {r["uid"]: r["gold_int"] for r in rows}
    arms = C.Arms(rows, gold)
    out = []
    for r in rows:
        uid = r["uid"]
        try:
            out.append((uid, {a: arms.prompt(a, uid) for a in ALL}))
        except Exception:
            continue
        if len(out) >= n_tasks:
            break
    return out


# ---------------------------------------------------------------- plants


def plant_lead_line(prompts, base):
    p = dict(prompts)
    for a in ("F-null", "F-prom-retrieved"):
        p[a] = "A prior attempt record:\n" + p[a]
    return p


def plant_slug_one_digit(prompts, base):
    """Change exactly one digit of one arm's slug - the finest slug perturbation possible."""
    import re
    p = dict(prompts)
    a = "F-hint"
    payload = payload_of(p[a], base)
    m = re.search(r"\d", payload)
    if not m:
        return None
    i = m.start()
    d = payload[i]
    newd = "7" if d != "7" else "3"
    p[a] = payload[:i] + newd + payload[i + 1:] + base
    return p


def plant_trailing_space(prompts, base):
    """A pure trailing-whitespace arm label - tests prediction P-B."""
    p = dict(prompts)
    a = "F-generic"
    payload = payload_of(p[a], base)
    p[a] = payload + " " + base
    return p


def plant_frame_char(prompts, base):
    """Alter one character of NON-treatment frame text on one arm."""
    p = dict(prompts)
    a = "F-null+hint"
    payload = payload_of(p[a], base)
    if "SPARSITY" in payload:
        payload = payload.replace("SPARSITY", "SPARSITX", 1)
    elif "not recorded" in payload:
        payload = payload.replace("not recorded", "not recordeX", 1)
    else:
        return None
    p[a] = payload + base
    return p


PLANTS = [
    ("1 lead line (historical 400/400)", plant_lead_line, True),
    ("2 slug, ONE digit changed", plant_slug_one_digit, True),
    ("3 trailing space on one arm", plant_trailing_space, True),
    ("4 one char of frame text", plant_frame_char, True),
]


def main() -> int:
    tasks = load()
    print("=" * 78)
    print("EXIT REVIEW 3 - independent gate-fire of INVARIANT 7")
    print("=" * 78)
    print(f"\ntasks exercised: {len(tasks)}   arms: {len(CARRYING)} carrying + F0")

    # --- control: clean packets must PASS
    clean_fail = 0
    for uid, prompts in tasks:
        ok, _ = nontreatment_identical(prompts, CARRYING)
        if not ok:
            clean_fail += 1
    print(f"\nNEGATIVE CONTROL (clean packets must pass INV 7)")
    print(f"  tasks failing on clean input: {clean_fail}/{len(tasks)}"
          f"   {'OK' if clean_fail == 0 else 'INV 7 IS BROKEN ON CLEAN INPUT'}")

    print(f"\nPLANTED DEFECTS (each must be REJECTED by INV 7)")
    results = []
    for name, fn, must_catch in PLANTS:
        caught = skipped = 0
        detail = None
        for uid, prompts in tasks:
            base = prompts.get("F0", "")
            planted = fn(prompts, base)
            if planted is None:
                skipped += 1
                continue
            ok, d = nontreatment_identical(planted, CARRYING)
            if not ok:
                caught += 1
                detail = detail or d
        n = len(tasks) - skipped
        rate = caught / n if n else 0.0
        verdict = "CAUGHT" if rate == 1.0 else ("PARTIAL" if rate > 0 else "MISSED")
        flag = "" if (rate == 1.0) == must_catch else "   <<< HOLE"
        print(f"  {name:<34s} {caught:>3d}/{n:<3d} = {rate:6.1%}  {verdict}{flag}")
        if skipped:
            print(f"  {'':<34s} (skipped {skipped} tasks: plant not constructible)")
        results.append((name, rate, must_catch))

    print("\n" + "-" * 78)
    holes = [n for n, r, m in results if (r == 1.0) != m]
    if holes:
        print("HOLES FOUND in INVARIANT 7:")
        for h in holes:
            print(f"  - {h}")
    else:
        print("NO HOLES: every planted defect was rejected on every task.")
    print("-" * 78)

    print("\nPREDICTIONS FILED BEFORE RUNNING (Harmonia B):")
    p_b = [r for n, r, m in results if n.startswith("3 trailing")]
    print("  P-B: constantize() ends in .strip(), so a pure trailing-whitespace arm label")
    print("       should survive blanking and NOT be caught.")
    if p_b:
        held = p_b[0] < 1.0
        print(f"       measured catch rate {p_b[0]:.1%} -> "
              f"{'P-B HELD (hole confirmed)' if held else 'P-B FAILED (INV 7 catches it)'}")
    return 1 if holes else 0


if __name__ == "__main__":
    raise SystemExit(main())
