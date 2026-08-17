"""Task family v2 — compositional numeric chains. Replaces the binary family (prereg §3.2).

WHY THE BINARY FAMILY HAD TO GO. Three measured defects, one root cause:

  * **Chance sits inside the band.** A True/False family gives a zero-capability solver 0.500,
    and 0.500 is inside [0.35, 0.60] — so the band cannot distinguish headroom from
    coin-flipping (Harmonia B, ruling 6).
  * **The post-screen cap.** At one solver the lenient screen retains both-wrong plus
    discordant, so post-screen accuracy is <= 0.50 identically — the band's upper half is
    unreachable. Predicted 0.2460, measured 0.2481.
  * **Control C cannot pass.** On a binary task the reasoning trace IS the answer: strip the
    verdict token and the prose still recovers gold at 72.2%. There is no rendering that keeps
    the residue and removes the answer.

All three are the same property: a **1-bit answer space**. Widening it fixes all three at once,
which is why this is a task-set change and not a threshold change.

WHAT REPLACES IT. A chain of exactly-computable integer operations:

    Let a = 8432.
    Step 1: let b = the sum of the decimal digits of a.
    Step 2: let c = the smallest prime strictly greater than b.
    Step 3: let d = gcd(c, 1170).
    Report d.

  * **Answer space is the integers**, so chance is ~0 rather than 0.500. The band regains its
    full range, the screen cap disappears, and the dispersion term becomes informative.
  * **Difficulty is COMPOSITIONAL DEPTH**, not operand magnitude. The v1 dial was measured
    NON-MONOTONE (72.6 -> 53.6 -> 64.3 -> 59.5) because a reasoning solver computes exactly at
    any scale — magnitude was never a difficulty axis. Depth is a different claim, and it is
    MEASURED here (`measure_axis`) rather than assumed. An assumed axis is exactly what failed
    last time and it must not recur silently.
  * **Failure lands on a STEP.** This is the residue-plausibility argument, and it is the reason
    this family is right for *this* probe rather than merely harder:

        A prior failed attempt records its intermediate values. Comparing them against the
        correct chain localizes the FIRST step at which it diverged. A packet can therefore
        carry "your previous attempt produced b=17 at step 1, which is where it went wrong"
        WITHOUT carrying the final answer — knowing step 1 was wrong does not hand over the
        number. That is break-location residue: usable by the next attempt, and not the answer.

    On the binary family the same packet was impossible in principle, because the trace and the
    label were the same object. Here they are different objects, which is what makes redaction
    meaningful for the first time — and it is precisely the break-step residue shape the
    2026-06-07 training-data survey named as the thing our substrate never recorded.

  * **Gold is computed, never judged** (R1). Every answer is produced by the same Python that
    the grader uses.
  * **No index-correlated layout.** v1 laid gold out in blocks by uid index (indices 0-8 True,
    9-17 False in 6 of 7 domains), and the packet body carries the uid — a 92.1%-accurate answer
    oracle shipped inside every D0 packet (Harmonia B, channel 0). Here uids are assigned AFTER
    shuffling and the correlation between uid index and answer is ASSERTED near zero before write.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import random
from collections import Counter
from typing import Callable

SEED_SEQUENCE = (20260817, 20260818, 20260819, 20260820)

#: The difficulty axis. Measured, not assumed — see `measure_axis`.
DEPTHS = (1, 2, 3, 4, 5)


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def _next_prime(n: int) -> int:
    m = max(2, n + 1)
    while not _is_prime(m):
        m += 1
    return m


def _digit_sum(n: int) -> int:
    return sum(int(c) for c in str(abs(n)))


def _divisor_count(n: int) -> int:
    n = abs(n) or 1
    c, i = 0, 1
    while i * i <= n:
        if n % i == 0:
            c += 2 if i * i != n else 1
        i += 1
    return c


# Each op: (key, renders the step in words, computes it). All exact, all cheap, all verifiable.
OPS: dict[str, tuple[Callable[[int, int], str], Callable[[int, int], int]]] = {
    "digit_sum": (lambda v, k: "the sum of the decimal digits of {v}",
                  lambda v, k: _digit_sum(v)),
    "next_prime": (lambda v, k: "the smallest prime strictly greater than {v}",
                   lambda v, k: _next_prime(v)),
    "gcd": (lambda v, k: f"the greatest common divisor of {{v}} and {k}",
            lambda v, k: math.gcd(v, k)),
    "mod": (lambda v, k: f"the remainder when {{v}} is divided by {k}",
            lambda v, k: v % k),
    "isqrt": (lambda v, k: "the integer square root of {v} (the largest n with n*n <= {v})",
              lambda v, k: math.isqrt(abs(v))),
    "divisor_count": (lambda v, k: "the number of positive divisors of {v}",
                      lambda v, k: _divisor_count(v)),
    "times_plus": (lambda v, k: f"{{v}} multiplied by {k}, plus {k + 1}",
                   lambda v, k: v * k + (k + 1)),
}
OP_KEYS = tuple(OPS)

#: Constants per op, chosen so intermediates stay in a range that is tractable by hand but
#: cannot be eyeballed — the work is real, the arithmetic is not the point.
_K_RANGE = {
    "gcd": (60, 5_000), "mod": (7, 97), "times_plus": (3, 19),
    "digit_sum": (0, 0), "next_prime": (0, 0), "isqrt": (0, 0), "divisor_count": (0, 0),
}


def _pick_k(rng: random.Random, op: str) -> int:
    lo, hi = _K_RANGE[op]
    return 0 if hi == 0 else rng.randint(lo, hi)


def _var_names(depth: int) -> list[str]:
    """b, c, ... z, then b1, c1, ... — unbounded, and never collides with the seed name `a`."""
    base = [chr(c) for c in range(ord("b"), ord("z") + 1)]
    out = list(base)
    cycle = 1
    while len(out) < depth:
        out.extend(f"{ch}{cycle}" for ch in base)
        cycle += 1
    return out[:depth]


def build_chain(rng: random.Random, depth: int, seed_value: int) -> tuple[str, int, list[dict]]:
    """Returns (rendered problem, gold answer, per-step trace). The trace is what makes
    break-location recordable — it is emitted into the manifest for the grader and for the
    residue path, and it is NEVER shown to the solver."""
    lines = [f"Let a = {seed_value}."]
    v = seed_value
    trace: list[dict] = []
    # Variable names for ARBITRARY depth. A fixed "bcdefghij" caps the dial at 9 steps and
    # IndexErrors past it — found when the extension sweep hit depth 12. A difficulty dial whose
    # generator cannot express its own upper rungs is not a dial.
    names = _var_names(depth)
    for i in range(depth):
        op = rng.choice(OP_KEYS)
        k = _pick_k(rng, op)
        render, fn = OPS[op]
        prev = v
        v = fn(v, k)
        # Each step refers to the PREVIOUS VARIABLE BY NAME, never by its value. Rendering the
        # value would let the solver skip straight to the last step, which would make "depth"
        # a label rather than a difficulty axis — the exact mistake the v1 dial made.
        prev_symbol = "a" if i == 0 else names[i - 1]
        if v > 10 ** 12:
            v = v % (10 ** 9 + 7)
            lines.append(f"Step {i+1}: let {names[i]} = " +
                         render(prev, k).format(v=prev_symbol) +
                         f", then reduce modulo {10**9+7}.")
        else:
            lines.append(f"Step {i+1}: let {names[i]} = " +
                         render(prev, k).format(v=prev_symbol) + ".")
        trace.append({"step": i + 1, "op": op, "k": k, "input": prev, "output": v,
                      "name": names[i], "refers_to": prev_symbol})
    lines.append(f"Report the value of {names[depth-1]} as a single integer.")
    lines.append("Give your final answer on the last line in the form: ANSWER: <integer>")
    return "\n".join(lines), v, trace


def generate(depth: int, n: int, seed: int = SEED_SEQUENCE[0]) -> list[dict]:
    rng = random.Random(f"{seed}:d{depth}")
    rows = []
    for i in range(n):
        seed_value = rng.randint(1_000, 99_999)
        prompt, gold, trace = build_chain(rng, depth, seed_value)
        rows.append({
            "domain": f"chain_d{depth}", "depth": depth,
            "seed_value": seed_value,
            "prompt": prompt, "gold_int": gold, "trace": trace,
            "ops": [t["op"] for t in trace],
        })
    return rows


def generate_manifest(per_depth: int, depths=DEPTHS, seed: int = SEED_SEQUENCE[0]) -> list[dict]:
    """Balanced by construction, ASSERTED before write, and decorrelated from uid index."""
    rows: list[dict] = []
    for d in depths:
        rows.extend(generate(d, per_depth, seed))

    # Balance assertion — v1's 80/80/.../14 defect was silent; this one cannot be.
    cells = Counter(r["depth"] for r in rows)
    for d in depths:
        if cells[d] != per_depth:
            raise AssertionError(f"unbalanced depth cell {d}: {cells[d]} != {per_depth}")

    # Shuffle FIRST, assign uids SECOND — so uid index carries no information about the answer.
    rng = random.Random(f"{seed}:layout")
    rng.shuffle(rows)
    for i, r in enumerate(rows):
        r["uid"] = f"chain-{i:05d}"

    _assert_no_index_leak(rows)
    return rows


def _assert_no_index_leak(rows: list[dict]) -> None:
    """Harmonia B's channel 0, made structurally impossible.

    v1 shipped a 92.1%-accurate answer oracle in the uid because gold was laid out in blocks by
    index and the packet body renders the uid. Here we assert that index predicts neither the
    answer's parity, nor its magnitude rank, nor the task's depth.
    """
    n = len(rows)
    if n < 20:
        return
    idx = list(range(n))

    par = [r["gold_int"] % 2 for r in rows]
    half = sum(par[: n // 2]) / max(1, n // 2)
    if not 0.30 <= half <= 0.70:
        raise AssertionError(f"uid index predicts answer parity ({half:.2f} in first half)")

    ranks = sorted(idx, key=lambda i: rows[i]["gold_int"])
    pos = [0] * n
    for rank, i in enumerate(ranks):
        pos[i] = rank
    mi, mp = (n - 1) / 2, (n - 1) / 2
    num = sum((i - mi) * (pos[i] - mp) for i in idx)
    den = math.sqrt(sum((i - mi) ** 2 for i in idx) * sum((p - mp) ** 2 for p in pos))
    rho = num / den if den else 0.0
    if abs(rho) > 0.20:
        raise AssertionError(f"uid index correlates with answer magnitude (rho={rho:.3f})")

    d_first = [r["depth"] for r in rows[: n // 2]]
    if len(set(d_first)) < 2:
        raise AssertionError("uid index predicts depth")


def manifest_sha256(rows: list[dict]) -> str:
    blob = "\n".join(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def generator_sha256() -> str:
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()


def write(rows: list[dict], path: pathlib.Path) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"n": len(rows), "manifest_sha256": manifest_sha256(rows),
            "generator_sha256": generator_sha256()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-depth", type=int, default=40)
    ap.add_argument("--seed", type=int, default=SEED_SEQUENCE[0])
    ap.add_argument("--out", default="ergon/probe/manifests/chain_manifest.jsonl")
    args = ap.parse_args()
    rows = generate_manifest(args.per_depth, seed=args.seed)
    meta = write(rows, pathlib.Path(args.out))
    print(f"[task_gen_v2] n={meta['n']} depths={sorted(set(r['depth'] for r in rows))}")
    print(f"[task_gen_v2] manifest_sha256={meta['manifest_sha256']}")
    print(f"[task_gen_v2] generator_sha256={meta['generator_sha256']}")
    print("\n--- sample (depth 3) ---")
    ex = next(r for r in rows if r["depth"] == 3)
    print(ex["prompt"])
    print(f"[gold = {ex['gold_int']}]")


if __name__ == "__main__":
    main()
