"""ATTACK on ergon/probe/adversarial_leakage.py -- construct the leak it must report, and see.

THREE WORLDS, all fixed in the pre-registration before this file was run:

  W1  ROTATING  a marker whose arm->token map rotates by task index. Given the task the marker
                determines the arm EXACTLY; across tasks the mapping is a different permutation.
                A perfect leak that a task-blind classifier cannot generalise.
  W2  INVERTED  the same rotation, read by a TASK-AWARE adversary, to prove W1's leak is real
                and not merely undetected noise.
  W3  LIVE      Ergon's own live packets, with features normalised WITHIN task, asking the
                question the gate never asks: is arm recoverable GIVEN the task?

EVERY ADVERSARY AND THE NULL ARE IMPORTED FROM ERGON'S MODULE. Reimplementing them would fork
the estimator, which is the ATK-014 shape this attack exists to test for. The only thing written
here is the injection and the within-task normalisation.

    PYTHONPATH=. python techne/attacks/probe_ergon_leakage_gate_2026-08-25.py

Exit 1 = at least one defect present.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# IMPORTED, NOT REIMPLEMENTED -- the whole point.
from ergon.probe.adversarial_leakage import (ARMS, build, cv_balanced_accuracy,  # noqa: E402
                                             distributional_features, permute_within_task,
                                             run_gate, structural_features, _dictvec,
                                             _proxy_tokenizer, SEED)

OUT = ROOT / "techne" / "attacks" / "ledgers"
ARM_ORDER = sorted(ARMS)

#: Kept small deliberately: the defect is structural, so it must show at a size that runs in
#: minutes. If it needed 200 tasks to appear it would be a power problem, not a design problem.
N_TASKS = 60
N_PERM = 60


# --------------------------------------------------------------------------- the injection

def make_rotating_injection(uids):
    """Arm -> marker, ROTATED by task. Perfect leak given the task; none without it.

    `LEAK_k` with k = (arm_index + task_index) mod 6. Within any task the six arms carry six
    distinct markers, so arm is a deterministic function of (marker, task). Across tasks the
    map is a different cyclic permutation, so no task-blind rule transfers.
    """
    order = {u: i for i, u in enumerate(sorted(uids))}

    def inject(arm, uid, payload):
        k = (ARM_ORDER.index(arm) + order[uid]) % len(ARM_ORDER)
        return f"LEAK_{k}\n" + payload

    return inject


def task_aware_recovery(texts, labels, groups):
    """W2 -- decode the arm from (marker, task) with the rotation as the only unknown.

    Deliberately NOT a learned classifier: the point is that the information is PRESENT, and a
    decoder that reads it is the cleanest possible demonstration. For each task, recover the
    rotation from a single anchor packet, then read every other arm off the marker.
    """
    import re
    marker = re.compile(r"^LEAK_(\d+)")
    by_task: dict = {}
    for t, lab, g in zip(texts, labels, groups):
        m = marker.match(t)
        if m:
            by_task.setdefault(g, []).append((int(m.group(1)), lab))
    correct = total = 0
    for g, items in by_task.items():
        if not items:
            continue
        k0, lab0 = items[0]                       # ONE labelled anchor per task
        rot = (k0 - ARM_ORDER.index(lab0)) % len(ARM_ORDER)
        for k, lab in items:
            pred = ARM_ORDER[(k - rot) % len(ARM_ORDER)]
            correct += (pred == lab)
            total += 1
    return correct / max(1, total), total


# --------------------------------------------------------------------------- W3, live probe

def within_task_normalised(texts, groups, tok):
    """Numeric features z-scored WITHIN each task, so task-conditional structure survives and
    task-level structure is removed. This is the representation the gate never builds."""
    Xs, _ = _dictvec([structural_features(t) for t in texts])
    Xd, _ = _dictvec([distributional_features(t, tok) for t in texts])
    X = np.hstack([Xs, Xd])
    out = np.zeros_like(X)
    for g in np.unique(groups):
        idx = np.where(groups == g)[0]
        block = X[idx]
        mu = block.mean(axis=0)
        sd = block.std(axis=0)
        sd[sd == 0] = 1.0
        out[idx] = (block - mu) / sd
    return out


def probe(X, y, groups, n_perm, seed=SEED):
    """Ergon's own estimator and Ergon's own null, on a different representation."""
    from sklearn.model_selection import GroupKFold
    folds = list(GroupKFold(n_splits=5).split(np.zeros(len(y)), y, groups))
    obs = cv_balanced_accuracy(X, y, groups, "trees", folds)
    rng = np.random.default_rng(seed)
    null = np.array([cv_balanced_accuracy(X, permute_within_task(y, groups, rng), groups,
                                          "trees", folds) for _ in range(n_perm)])
    return {"observed": round(float(obs), 4), "null_mean": round(float(null.mean()), 4),
            "null_p95": round(float(np.percentile(null, 95)), 4),
            "null_p05": round(float(np.percentile(null, 5)), 4),
            "delta": round(float(obs - null.mean()), 4),
            "abs_delta": round(abs(float(obs - null.mean())), 4),
            "n_perm": int(n_perm), "n_rows": int(len(y))}


def main() -> int:
    import ergon.probe.campaign as C
    OUT.mkdir(parents=True, exist_ok=True)
    rows = C.manifest()[:N_TASKS]
    gold = {r["uid"]: r["gold_int"] for r in rows}
    arms_obj = C.Arms(rows, gold)
    tok, tokname = _proxy_tokenizer()
    uids = [r["uid"] for r in rows]
    findings = {}

    # ---- W1: does the UNMODIFIED gate report a perfect task-conditional leak? --------------
    inj = make_rotating_injection(uids)
    texts, labels, groups, nc = build(rows, arms_obj, inject=inj)
    gate = run_gate(texts, labels, groups, "ATTACK_rotating", tokname, tok, N_PERM)
    w1_pass = not gate["any_fail"]
    findings["W1_gate_verdict_on_perfect_task_conditional_leak"] = {
        "any_fail": gate["any_fail"], "any_undecided": gate["any_undecided"],
        "gate_reports_PASS": w1_pass,
        "pairs_below_null": sum(1 for v in gate["pairs"].values()
                                if v["observed_balanced_accuracy"] < v["null_mean"]),
        "of_pairs": len(gate["pairs"]),
        "DEFECT": w1_pass,
    }

    # ---- W2: is that leak real? --------------------------------------------------------------
    acc, n = task_aware_recovery(texts, labels, groups)
    findings["W2_task_aware_recovery_of_the_same_leak"] = {
        "balanced_accuracy": round(acc, 4), "n_decoded": n,
        "note": "one labelled anchor per task; every other arm read off the marker",
        "leak_is_real": acc >= 0.95,
    }

    # ---- W3: is there anything in the blind spot on LIVE packets? ---------------------------
    ltexts, llabels, lgroups, lnc = build(rows, arms_obj)
    Xw = within_task_normalised(ltexts, lgroups, tok)
    live_arm6 = probe(Xw, llabels, lgroups, N_PERM)
    R = np.array([ARMS[a][0] for a in llabels])
    live_R = probe(Xw, R, lgroups, N_PERM)
    findings["W3_live_within_task_normalised"] = {
        "arm6": live_arm6, "R": live_R,
        "n_tasks": len(rows), "nonconforming": lnc,
        "exceeds_null_p95": bool(live_arm6["observed"] > live_arm6["null_p95"]
                                 or live_R["observed"] > live_R["null_p95"]),
    }

    # ---- one-sidedness as a code fact -------------------------------------------------------
    src = (ROOT / "ergon/probe/adversarial_leakage.py").read_text(encoding="utf-8")
    findings["W4_verdict_is_one_sided"] = {
        "tests_upper_tail": "obs > p95" in src,
        "tests_lower_tail": ("obs < " in src) or ("p05" in src) or ("percentile(null, 5)" in src),
        "DEFECT": ("obs > p95" in src) and not (("obs < " in src) or ("p05" in src)),
    }

    out = {
        "attack": "techne/attacks/ATTACK_ergon_measurements_2026-08-25.md",
        "target": "ergon/probe/adversarial_leakage.py",
        "command": "PYTHONPATH=. python techne/attacks/probe_ergon_leakage_gate_2026-08-25.py",
        "n_tasks": len(rows), "n_perm": N_PERM, "seed": SEED,
        "adversaries_imported_not_reimplemented": True,
        "findings": findings,
    }
    (OUT / "ergon_leakage_gate_attack.json").write_text(json.dumps(out, indent=2),
                                                        encoding="utf-8")
    print("\n" + json.dumps(findings, indent=2))
    defects = [k for k, v in findings.items() if isinstance(v, dict) and v.get("DEFECT")]
    print(f"\nDEFECTS PRESENT: {defects or 'none'}")
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
