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

AMENDMENT 2026-08-31 (Harmonia B, self-attack).  Two defects in THIS file, found by me
while preparing the block-B run that my own EXIT REVIEW 3 scope limit requires:

  D-1  ZERO-COVERAGE IS INDISTINGUISHABLE FROM A RESULT.  `load()` wrapped rendering in
       `try/except: continue`, so on a block whose residue pool is not wired EVERY task is
       silently dropped, `tasks` comes back empty, and all four plants report 0/0.

       I PREDICTED this failed OPEN ("it will print NO HOLES over zero tasks") and wrote
       that claim into this docstring before testing it.  IT IS WRONG, and the measurement
       is recorded here rather than quietly corrected.  `rate = caught / n if n else 0.0`
       makes an unmeasured plant score 0.0, which is `!= must_catch`, so the old code fails
       CLOSED: it prints FOUR FABRICATED HOLES IN INVARIANT 7 and exits 1, over zero
       rendered packets.  Measured by planting a total render failure against the committed
       version (`git show HEAD:` + the same plant): 4/4 phantom holes, exit 1.

       That is the more dangerous direction for THIS seat, not the safer one.  Run against
       an unwired block B, the committed gate-fire would have handed me a four-hole
       indictment of another agent's gate that no packet supports -- an instrument error
       filed as evidence, which is the one thing an independent seat may never do.
       Same family as everything exit review 3 section 3b filed: a check that cannot tell
       the condition it fears from a legitimate state.  Ergon closed this class in
       `packet_invariants._run` ("COUNTED, NOT SILENTLY SKIPPED"); mine was still open.
       CLOSED: skips are counted and printed, an unmeasured plant reads NOT MEASURED rather
       than MISSED, and a run under COVERAGE_FLOOR tasks is VACUOUS -- NO VERDICT in either
       direction, exit 1.  Gate-fired: the same plant now yields 0 exercised, VACUOUS, four
       NOT MEASURED, and no hole claimed.

  D-2  BLOCK-BLIND.  The file hardcoded `C.manifest()`, which returns block A
       unconditionally, so it could not be pointed at block B at all -- and "the gate-fire
       passes" would have silently meant "on block A".  Same defect Ergon had already fixed
       in packet_invariants under this same scope condition.
       CLOSED: `--block B` selects via `blocks.load` + `blocks.repointed`, reusing the
       driver's own scoping rather than a second implementation of it.

  D-3  A GREEN INV 7 LEDGER IS NOT A DURABLE CERTIFICATE, and nothing in it says so.
       Re-running `packet_invariants.py B` today reproduced 220/220 and 0 failures, but the
       payload lengths MOVED against the committed ledger: F-null 461.8 -> 475.2 mean chars,
       F-prom-retrieved 461.6 -> 474.9, F-null+hint 635.8 -> 649.2, F-prom+hint 635.6 ->
       648.9 -- exactly the four RESIDUE-DRAWING arms, all by ~+13.3 -- while the two
       non-residue arms moved -0.2.  Cause, from git: at the commit that produced that ledger
       (`986bf0058`) block B's prepass held **4 records**; it holds **534** now, collection
       having continued until 23:14 the same day.

       INV 7 was not wrong.  It decides byte-identity ACROSS ARMS WITHIN A TASK, which is
       independent of how large the residue pool is -- so it passed then and passes now.  But
       it certified DIFFERENT PACKETS, and `invariants_block*.json` carries no timestamp, no
       manifest sha, and no fingerprint of the pool it was computed against, so a reader six
       days later cannot decide whether the certificate is current.  My 08-25 scope condition
       caught this only because I wrote the condition; the artifact would never have told
       anyone.  Filed as HB3-4 against packet_invariants; closed HERE for my own instrument,
       which now fingerprints the pool it ran against and writes it beside the verdict.

Run:  PYTHONPATH=. python harmonia/probe/exit3_inv7_gatefire.py [--block A|B] [--tasks N]
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


#: A run exercising fewer than this many tasks is VACUOUS and may not be read as a pass.
#: 25 is the number the exit-review-3 signoff records for block A; block B must meet it too.
COVERAGE_FLOOR = 25


def load(n_tasks=25, block="A"):
    """Render every arm for up to `n_tasks` tasks of `block`.

    Returns (tasks, attempted, skips) -- skips are RETURNED, not swallowed (D-1).  Block
    selection reuses the driver's own scoping (D-2) rather than reimplementing it.
    """
    import contextlib
    from ergon.probe import blocks as B

    if block == "A":
        rows = C.manifest()
        ctx = contextlib.nullcontext()
    else:
        rows = B.load(block)
        ctx = B.repointed(block)      # so the prepass pool resolves to the block's own

    gold = {r["uid"]: r["gold_int"] for r in rows}
    out, skips, attempted = [], [], 0
    with ctx:
        arms = C.Arms(rows, gold)
        for r in rows:
            uid = r["uid"]
            attempted += 1
            try:
                out.append((uid, {a: arms.prompt(a, uid) for a in ALL}))
            except Exception as e:
                skips.append((uid, f"{type(e).__name__}: {e}"))
                continue
            if len(out) >= n_tasks:
                break
    return out, attempted, skips


def pool_fingerprint(block):
    """What this run actually certified, in a form a later reader can decide staleness against.

    D-3: `invariants_block*.json` reports `checked_tasks` and `failures` and nothing about the
    inputs, so a certificate computed over a 4-record residue pool is indistinguishable from
    one computed over 534.  A verdict that cannot be dated is a verdict that must be re-earned
    every time, which is fine for me and useless for everyone downstream.
    """
    import hashlib
    from ergon.probe import blocks as B
    if block == "A":
        pool = C.DIR / "p1_prepass.jsonl"
        man = ROOT / C.PINNED_MANIFEST
    else:
        pool = B.block_dir(block) / "p1_prepass.jsonl"
        man = ROOT / B.spec(block)["manifest"]
    fp = {"block": block, "pool_path": str(pool.relative_to(ROOT)).replace(chr(92), "/"),
          "manifest_path": str(man.relative_to(ROOT)).replace(chr(92), "/")}
    for label, path in (("pool", pool), ("manifest", man)):
        if path.exists():
            raw = path.read_bytes()
            fp[label + "_sha256_16"] = hashlib.sha256(raw).hexdigest()[:16]
            fp[label + "_records"] = sum(1 for l in raw.splitlines() if l.strip())
        else:
            fp[label + "_sha256_16"] = None
            fp[label + "_records"] = 0
    return fp


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


def main(block="A", n_tasks=25) -> int:
    tasks, attempted, skips = load(n_tasks, block)
    print("=" * 78)
    print(f"EXIT REVIEW 3 - independent gate-fire of INVARIANT 7   [block {block}]")
    print("=" * 78)
    print()
    print(f"tasks requested: {n_tasks}   attempted: {attempted}   "
          f"exercised: {len(tasks)}   skipped: {len(skips)}")
    print(f"arms: {len(CARRYING)} carrying + F0    coverage floor: {COVERAGE_FLOOR}")
    fp = pool_fingerprint(block)
    print()
    print("WHAT THIS RUN CERTIFIED (D-3 -- a verdict with no fingerprint cannot be dated):")
    print(f"  residue pool  {fp['pool_path']}")
    print(f"                {fp['pool_records']} records, sha256:{fp['pool_sha256_16']}")
    print(f"  manifest      {fp['manifest_path']}")
    print(f"                {fp['manifest_records']} rows, sha256:{fp['manifest_sha256_16']}")

    # D-1: skips are COUNTED and REPORTED, never swallowed. A gate-fire that renders no
    # packets has measured nothing, whatever the plant table says below.
    if skips:
        print()
        print(f"SKIPPED TASKS (render raised) - {len(skips)}; first 3:")
        for uid, err in skips[:3]:
            print(f"  {uid}: {err[:150]}")

    vacuous = len(tasks) < COVERAGE_FLOOR
    if vacuous:
        print()
        print(f"*** VACUOUS: {len(tasks)} tasks exercised < floor {COVERAGE_FLOOR}. ***")
        print("*** Nothing below may be read as a pass for this block. ***")

    # --- control: clean packets must PASS
    clean_fail = 0
    for uid, prompts in tasks:
        ok, _ = nontreatment_identical(prompts, CARRYING)
        if not ok:
            clean_fail += 1
    ctrl = ("NOT MEASURED" if not tasks
            else "OK" if clean_fail == 0 else "INV 7 IS BROKEN ON CLEAN INPUT")
    print()
    print("NEGATIVE CONTROL (clean packets must pass INV 7)")
    print(f"  tasks failing on clean input: {clean_fail}/{len(tasks)}   {ctrl}")

    print()
    print("PLANTED DEFECTS (each must be REJECTED by INV 7)")
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
        rate = (caught / n) if n else float("nan")
        if n == 0:
            verdict, flag, rate_txt = "NOT MEASURED", "   <<< NOT MEASURED", "  n/a "
        else:
            verdict = "CAUGHT" if rate == 1.0 else ("PARTIAL" if rate > 0 else "MISSED")
            flag = "" if (rate == 1.0) == must_catch else "   <<< HOLE"
            rate_txt = f"{rate:6.1%}"
        print(f"  {name:<34s} {caught:>3d}/{n:<3d} = {rate_txt}  {verdict}{flag}")
        if skipped:
            print(f"  {'':<34s} (skipped {skipped} tasks: plant not constructible)")
        results.append((name, rate, must_catch, n))

    print()
    print("-" * 78)
    unmeasured = [nm for nm, r, m, k in results if k == 0]
    holes = [nm for nm, r, m, k in results if k and (r == 1.0) != m]
    if vacuous or unmeasured:
        print("NO VERDICT: the gate-fire did not exercise enough packets to decide anything.")
        if unmeasured:
            print(f"  plants never constructed: {len(unmeasured)}")
    elif holes:
        print("HOLES FOUND in INVARIANT 7:")
        for h in holes:
            print(f"  - {h}")
    else:
        print(f"NO HOLES: every planted defect was rejected on every one of "
              f"{len(tasks)} tasks (block {block}).")
    print("-" * 78)

    # my own certificate, fingerprinted. Written even on a VACUOUS run -- a reader must be
    # able to see that a gate-fire ran and decided nothing, which is the D-1 lesson.
    import json as _json
    led_dir = ROOT / "harmonia/probe/ledgers"
    led_dir.mkdir(parents=True, exist_ok=True)
    (led_dir / f"gatefire_block{block}.json").write_text(_json.dumps({
        "seat": "Harmonia B", "gate": "exit3_inv7_gatefire", "block": block,
        "tasks_requested": n_tasks, "tasks_attempted": attempted,
        "tasks_exercised": len(tasks), "tasks_skipped": len(skips),
        "coverage_floor": COVERAGE_FLOOR, "vacuous": vacuous,
        "clean_control_failures": clean_fail,
        "plants": [{"plant": nm, "catch_rate": (None if k == 0 else round(r, 4)),
                    "n_tasks": k, "must_catch": m} for nm, r, m, k in results],
        "holes": holes, "not_measured": unmeasured,
        "verdict": ("NO VERDICT - vacuous" if (vacuous or unmeasured)
                    else "HOLES" if holes else "NO HOLES"),
        "certified_over": fp,
        "note": "This certificate is scoped to the fingerprinted pool and manifest. If either "
                "sha changes, this verdict is STALE and must be re-earned -- see D-3.",
    }, indent=2), encoding="utf-8")

    print()
    print("PREDICTIONS FILED BEFORE RUNNING (Harmonia B):")
    print("  P-B: constantize() ends in .strip(), so a pure trailing-whitespace arm label")
    print("       should survive blanking and NOT be caught.")
    pb = [(r, k) for nm, r, m, k in results if nm.startswith("3 trailing")]
    if pb and pb[0][1]:
        rate = pb[0][0]
        held = rate < 1.0
        print(f"       measured catch rate {rate:.1%} -> "
              f"{'P-B HELD (hole confirmed)' if held else 'P-B FAILED (INV 7 catches it)'}")
    else:
        print("       NOT MEASURED on this run.")
    return 1 if (vacuous or unmeasured or holes) else 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", default="A", choices=["A", "B"])
    ap.add_argument("--tasks", type=int, default=25)
    a = ap.parse_args()
    raise SystemExit(main(a.block, a.tasks))
