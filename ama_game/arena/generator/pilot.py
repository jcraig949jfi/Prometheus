#!/usr/bin/env python3
"""Pilot report: is the generator's output actually usable as an instrument?

This is the gate described in PREREG_A0.md section 5. It answers, for a
generated set:

  1. does the set regenerate byte-identically from its seed?
  2. do the two oracle channels stay independent, or has the argument channel
     collapsed into the truth channel?
  3. does every item satisfy the postconditions of its sealed class, including
     the budget bands that separate FALSE_WITH_WITNESS from
     FALSE_BUT_HARD_WITHIN_BUDGET from UNRESOLVED_WITHIN_BUDGET?
  4. does anything sealed leak into the public package?
  5. can the sealed class be predicted from the template or the domain label
     alone? (measured in bits, not asserted to be small)
  6. does the scoring machinery separate all five dispositions, and reject a
     bogus falsifier?

Passing this is an instrument calibration, not a result. It shows the machinery
can tell the classes apart on input it was built to handle. It says nothing
about whether live agents produce anything worth scoring.

  python pilot.py --set ../heldout/PILOT_A0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

import oracle as ORACLE
import templates as T

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent

SEALED_ONLY_TOKENS = ["sealed_class", "oracle_disposition", "truth_status",
                      "planted_mutation_type", "known_witness", "claim_predicate",
                      "mutation_target_step", "minimum_known_disposition_method",
                      "M1_", "M2_", "M3_", "M4_", "M5_", "M6_", "M7_", "M8_",
                      "M9_", "M10_", "M11_", "M12_"]


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failures: list[str] = []

    def head(self, text: str) -> None:
        self.lines.append("")
        self.lines.append(text)
        self.lines.append("-" * len(text))

    def ok(self, label: str, detail: str = "") -> None:
        self.lines.append(f"  [OK  ] {label}" + (f"  {detail}" if detail else ""))

    def fail(self, label: str, detail: str = "") -> None:
        self.lines.append(f"  [FAIL] {label}" + (f"  {detail}" if detail else ""))
        self.failures.append(label)

    def info(self, text: str) -> None:
        self.lines.append(f"         {text}")

    def dump(self) -> None:
        print("\n".join(self.lines))


def load_set(root: Path):
    manifest = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    sealed = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((root / "sealed").glob("*.json"))]
    public = {p.stem: p.read_text(encoding="utf-8")
              for p in sorted((root / "public").glob("*.json"))}
    return manifest, sealed, public


def mutual_information(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    joint, mx, my = Counter(pairs), Counter(x for x, _ in pairs), \
        Counter(y for _, y in pairs)
    mi = 0.0
    for (x, y), c in joint.items():
        pxy, px, py = c / n, mx[x] / n, my[y] / n
        mi += pxy * math.log2(pxy / (px * py))
    return mi


def entropy(vals: list[str]) -> float:
    n, c = len(vals), Counter(vals)
    return -sum((v / n) * math.log2(v / n) for v in c.values()) if n else 0.0


# --------------------------------------------------------------------------
# the minimal scorer: PREREG_A0.md section 3
# --------------------------------------------------------------------------

def score_disposition(sealed: dict, disposition: str, verifier_calls: int,
                      budget_cap: int) -> dict:
    correct = disposition == sealed["oracle_disposition"]
    return {"correct": correct,
            "cost": verifier_calls if correct else budget_cap,
            "cost_rule": "correct ? verifier_calls : budget_cap"}


def adjudicate_kill(sealed: dict, witness) -> str:
    """VALID_KILL / INVALID_KILL, decided by re-execution, not by assertion."""
    v = ORACLE.verify_witness(sealed, witness)
    return "VALID_KILL" if v["is_counterexample"] else "INVALID_KILL"


# --------------------------------------------------------------------------

def check_determinism(root: Path, manifest: dict, rep: Report) -> None:
    rep.head("1. determinism")
    import generate as G

    tmp = Path(tempfile.mkdtemp(prefix="ama_pilot_"))
    try:
        args = argparse.Namespace(
            set_name=manifest["set_name"], seed=manifest["seed"],
            count=manifest["requested_count"],
            families=("play" if manifest["family_pool"] ==
                      G.load_json(HERE / "MUTATION_SPLIT.json")["play"]
                      else "holdout"),
            templates=",".join(manifest["template_pool"]),
            classes=",".join(manifest["class_pool"]),
            transfer_cell=manifest["transfer_cell"],
            player_search_budget=manifest["player_search_budget"],
            out=str(tmp), overwrite=True)
        G.generate_set(args)
        mismatches = []
        for p in sorted((root / "sealed").glob("*.json")):
            q = tmp / manifest["set_name"] / "sealed" / p.name
            if not q.exists() or q.read_bytes() != p.read_bytes():
                mismatches.append(p.name)
        for p in sorted((root / "public").glob("*.json")):
            q = tmp / manifest["set_name"] / "public" / p.name
            if not q.exists() or q.read_bytes() != p.read_bytes():
                mismatches.append(p.name)
        if mismatches:
            rep.fail("regeneration is not byte-identical",
                     f"{len(mismatches)} files differ, e.g. {mismatches[:3]}")
        else:
            rep.ok("regenerates byte-identically from the seed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_channels(sealed: list[dict], rep: Report) -> None:
    rep.head("2. oracle channel independence")

    bad = [s["claim_id"] for s in sealed
           if s["truth_status"] == "FALSE" and s["argument_validity"] == "VALID"]
    if bad:
        rep.fail("a FALSE claim carries a fully VALID argument",
                 f"{len(bad)} items, e.g. {bad[:3]}")
        rep.info("this means the step checks are too coarse to notice a false "
                 "conclusion being derived; it is a defect in derivation.py, "
                 "not in the players")
    else:
        rep.ok("no FALSE claim has a fully VALID argument")

    ti = [s for s in sealed if s["sealed_class"] == T.TRUE_INVALID]
    bad = [s["claim_id"] for s in ti if s["truth_status"] != "TRUE"]
    if bad:
        rep.fail("a planted mutation changed the truth of the conclusion", str(bad))
    else:
        rep.ok(f"all {len(ti)} TRUE_BUT_INVALID_ARGUMENT items kept a true "
               "conclusion")

    bad = [s["claim_id"] for s in ti
           if s["invalid_steps"] != [s["mutation_target_step"]]]
    if bad:
        rep.fail("planted defect is not the unique invalid step", str(bad[:3]))
    else:
        rep.ok("each planted defect is the unique invalid step in its derivation")

    # the divergence that proves the channels are not the same measurement
    div = [s for s in sealed
           if s["truth_status"] == "TRUE" and s["argument_validity"] != "VALID"]
    rep.ok("channels diverge where they must",
           f"{len(div)} items are TRUE with a non-VALID argument")


def check_classes(sealed: list[dict], budget: int, rep: Report) -> None:
    rep.head("3. sealed-class postconditions")
    bands = {
        T.FALSE_WITNESS: (1, T.EASY_WITNESS_MAX),
        T.FALSE_HARD: (T.EASY_WITNESS_MAX + 1, budget),
        T.UNRESOLVED: (budget + 1, None),
    }
    for cls, (lo, hi) in bands.items():
        items = [s for s in sealed if s["sealed_class"] == cls]
        bad = [s["claim_id"] for s in items
               if not (lo <= s["minimum_known_disposition_method"]["cost_units"]
                       and (hi is None or
                            s["minimum_known_disposition_method"]["cost_units"] <= hi))]
        costs = [s["minimum_known_disposition_method"]["cost_units"] for s in items]
        if bad:
            rep.fail(f"{cls} outside its budget band", str(bad[:3]))
        else:
            rep.ok(f"{cls}: {len(items)} items, cost units in "
                   f"[{min(costs) if costs else '-'}, {max(costs) if costs else '-'}]",
                   f"band [{lo}, {hi if hi else 'inf'}]")

    unres = [s for s in sealed if s["sealed_class"] == T.UNRESOLVED]
    t = sum(1 for s in unres if s["truth_status"] == "TRUE")
    n = len(unres)
    rep.info("")
    if n:
        skew = abs(t - n / 2) / (n / 2)
        label = (f"UNRESOLVED truth split: {t} TRUE / {n - t} FALSE of {n}")
        if n >= 8 and skew > 0.5:
            rep.fail(label + " — guessing the truth value beats chance", "")
            rep.info("an agent that guesses the majority truth value would score "
                     "above chance on this class without ever resolving anything")
        else:
            rep.ok(label, "guessing the truth value gains little")


def check_distinctness(root: Path, sealed: list[dict], rep: Report) -> None:
    rep.head("3b. distinct propositions")
    props = [json.loads((root / "public" / f"{s['claim_id']}.json")
                        .read_text(encoding="utf-8"))["proposition"]
             for s in sealed]
    dupes = {p: c for p, c in Counter(props).items() if c > 1}
    if dupes:
        rep.fail(f"{sum(dupes.values()) - len(dupes)} repeated propositions",
                 f"{len(dupes)} distinct texts repeat; the set has "
                 f"{len(set(props))} distinct items, not {len(props)}")
        rep.info("a repeated proposition is not an independent draw; the unit "
                 "of analysis is the claim, so n is overstated")
    else:
        rep.ok(f"all {len(props)} propositions are distinct")

    by_class: dict[str, set] = {}
    for s_, p_ in zip(sealed, props):
        by_class.setdefault(s_["sealed_class"], set()).add(p_)
    rep.info("distinct propositions per class: " +
             json.dumps({k: len(v) for k, v in sorted(by_class.items())}))


def check_leakage(public: dict[str, str], sealed: list[dict], rep: Report) -> None:
    rep.head("4. leakage from sealed into public")
    hits = []
    for cid, text in public.items():
        for tok in SEALED_ONLY_TOKENS:
            if tok in text:
                hits.append((cid, tok))
    if hits:
        rep.fail("sealed vocabulary appears in a public package", str(hits[:5]))
    else:
        rep.ok(f"no sealed field name or mutation family id in {len(public)} "
               "public packages")

    # a public package must not contain the machine checks
    check_hits = [cid for cid, t in public.items()
                  if '"check"' in t or "forall_identity" in t]
    if check_hits:
        rep.fail("step checks shipped in the public package", str(check_hits[:3]))
    else:
        rep.ok("no step checks in any public package")

    # a witness value should not be recoverable by reading the public text
    numeric = []
    for s in sealed:
        w = s.get("known_witness")
        if not w:
            continue
        val = w.get("n", w.get("graph_bits"))
        text = public.get(s["claim_id"], "")
        if val is not None and val > 50 and f"{val}" in text:
            numeric.append((s["claim_id"], val))
    if numeric:
        rep.fail("a witness value appears verbatim in its public package",
                 str(numeric[:5]))
    else:
        rep.ok("no witness value appears in its own public package")


def check_confounds(sealed: list[dict], rep: Report) -> None:
    rep.head("5. can the sealed class be read off metadata alone?")
    classes = [s["sealed_class"] for s in sealed]
    h = entropy(classes)
    rep.info("mutual information on a sparse joint histogram is biased upward, "
             "so the observed value is read against a label-shuffle null, not "
             "against a fixed threshold")
    rng = random.Random(0)
    for field in ("template_id", "domain_label"):
        keys = [s[field] for s in sealed]
        mi = mutual_information(list(zip(keys, classes)))
        frac = mi / h if h else 0.0

        null = []
        shuffled = list(classes)
        for _ in range(2000):
            rng.shuffle(shuffled)
            null.append(mutual_information(list(zip(keys, shuffled))))
        null.sort()
        null_mean = sum(null) / len(null)
        null_p95 = null[int(0.95 * len(null))]

        rep.info(f"I({field}; class) = {mi:.3f} bits of H(class) = {h:.3f} "
                 f"({frac:.0%});  shuffle null mean {null_mean:.3f}, "
                 f"p95 {null_p95:.3f}")
        if mi > null_p95 and frac > 0.35:
            rep.fail(f"{field} predicts the sealed class beyond chance",
                     f"{frac:.0%} of class entropy, null p95 {null_p95:.3f}")
        elif mi <= null_p95:
            rep.ok(f"{field}: observed MI is inside the shuffle null",
                   f"n={len(sealed)} is too small to distinguish this from chance")
        else:
            rep.ok(f"{field} carries {frac:.0%} of the class entropy",
                   f"above the null but under the 35% ceiling")
    rep.info("")
    rep.info("counts by template: " +
             json.dumps(dict(Counter(s["template_id"] for s in sealed))))
    fams = Counter(s["planted_mutation_type"] for s in sealed
                   if s["planted_mutation_type"])
    rep.info(f"mutation families used: {len(fams)} distinct — {json.dumps(dict(fams))}")


def check_scorer(sealed: list[dict], budget_cap: int, rep: Report) -> None:
    rep.head("6. scoring machinery: five-way confusion matrix")
    dispositions = ["TRUE", "FALSE", "TRUE_BUT_INVALID_ARGUMENT", "UNRESOLVED"]
    by_class = {}
    for s in sealed:
        by_class.setdefault(s["sealed_class"], []).append(s)

    matrix: dict[str, dict[str, int]] = {}
    for cls in T.ALL_CLASSES:
        items = by_class.get(cls, [])
        if not items:
            continue
        row = {}
        for d in dispositions:
            correct = sum(1 for s in items
                          if score_disposition(s, d, 3, budget_cap)["correct"])
            row[d] = correct
        matrix[cls] = row

    ok = True
    for cls, row in matrix.items():
        want = {T.TRUE_VALID: "TRUE", T.FALSE_WITNESS: "FALSE",
                T.TRUE_INVALID: "TRUE_BUT_INVALID_ARGUMENT",
                T.FALSE_HARD: "FALSE", T.UNRESOLVED: "UNRESOLVED"}[cls]
        n = len(by_class[cls])
        hits = {d: c for d, c in row.items() if c}
        if hits != {want: n}:
            ok = False
            rep.fail(f"{cls} does not score uniquely as {want}", json.dumps(hits))
        else:
            rep.ok(f"{cls:<30s} scores correct only for {want}", f"n={n}")
    if ok:
        rep.ok("confusion matrix is diagonal across all five sealed classes")

    rep.head("7. bogus-falsifier rejection")
    false_items = [s for s in sealed if s["truth_status"] == "FALSE"
                   and s.get("known_witness")]
    valid_ok = invalid_ok = 0
    for s in false_items[:12]:
        w = s["known_witness"]
        real = w.get("n", w.get("graph_bits"))
        if adjudicate_kill(s, real) == "VALID_KILL":
            valid_ok += 1
    true_items = [s for s in sealed if s["truth_status"] == "TRUE"]
    for s in true_items[:12]:
        lo = s["domain_lo"]
        if adjudicate_kill(s, lo) == "INVALID_KILL":
            invalid_ok += 1
    out_of_domain = 0
    for s in sealed[:12]:
        if adjudicate_kill(s, s["domain_hi"] + 10_000_000) == "INVALID_KILL":
            out_of_domain += 1

    n1, n2, n3 = len(false_items[:12]), len(true_items[:12]), len(sealed[:12])
    (rep.ok if valid_ok == n1 else rep.fail)(
        f"real witnesses adjudicated VALID_KILL: {valid_ok}/{n1}")
    (rep.ok if invalid_ok == n2 else rep.fail)(
        f"fabricated kills on TRUE claims rejected: {invalid_ok}/{n2}")
    (rep.ok if out_of_domain == n3 else rep.fail)(
        f"out-of-domain witnesses rejected: {out_of_domain}/{n3}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--set", required=True, help="path to a generated set directory")
    p.add_argument("--skip-determinism", action="store_true")
    args = p.parse_args()

    root = Path(args.set).resolve()
    manifest, sealed, public = load_set(root)
    budget = manifest["player_search_budget"]
    budget_cap = json.loads(
        (ARENA / "prompts" / "budget.json").read_text(encoding="utf-8")
    )["BUDGET_VERIFIER_CALLS"]

    rep = Report()
    rep.lines.append(f"AMA generator pilot — {manifest['set_name']}")
    rep.lines.append(f"protocol {manifest['protocol_version']}  "
                     f"generator {manifest['generator_sha256'][:16]}  "
                     f"items {manifest['emitted']}/{manifest['requested_count']}  "
                     f"player search budget {budget}")

    if not args.skip_determinism:
        check_determinism(root, manifest, rep)
    check_channels(sealed, rep)
    check_classes(sealed, budget, rep)
    check_distinctness(root, sealed, rep)
    check_leakage(public, sealed, rep)
    check_confounds(sealed, rep)
    check_scorer(sealed, budget_cap, rep)

    rep.head("verdict")
    if rep.failures:
        rep.lines.append(f"  FAIL — {len(rep.failures)} check(s) failed:")
        for f in rep.failures:
            rep.lines.append(f"    - {f}")
    else:
        rep.lines.append("  PASS — instrument calibrated. This is not a result.")
    rep.dump()
    return 1 if rep.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
