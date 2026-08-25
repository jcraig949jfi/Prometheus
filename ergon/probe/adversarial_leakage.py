"""Adversarial assignment-leakage gate: constantize the treatment, then attack what remains.

PREREGISTRATION: `ergon/probe/PREREG_adversarial_leakage_gate_2026-08-25.md`. Thresholds, nulls,
adversaries and targets were fixed there before this file produced a number.

WHY THIS REPLACES THE FEATURE CENSUS. The previous gate enumerated features by hand and asserted
"arm identity is computationally unavailable". That claim is malformed: THE TREATMENT IDENTIFIES
THE ARM, and a packet-shape check can pass in full while testing the wrong property. It is also
unachievable, and the conditional repair `I(A;N|R,H)=0` is degenerate here because A is a
deterministic function of (R,H).

What is measurable is the destructive form: replace the treatment slot with a constant and ask
whether assignment survives in what remains. That needs no guess about which feature class the
next label will hide in -- which matters, because every hand-enumerated census this campaign has
written was blind, by construction, to the label that was actually present.

    python ergon/probe/adversarial_leakage.py

No LLM. No network. Reads the pinned manifests; writes only its own ledger.
"""
import collections
import json
import pathlib
import re
import sys
import unicodedata
import zlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

OUT = ROOT / "ergon/probe/ledgers/adversarial_leakage"

#: The six arms as (R, H). The design is 3x2: R has THREE levels, not two. `null` is a real
#: prior-attempt record drawn from a DIFFERENT task, which is a distinct condition from
#: `generic` (advice with no task provenance) and from `prom` (this task's own record).
ARMS = {
    "F-generic":        ("generic", 0),
    "F-hint":           ("generic", 1),
    "F-null":           ("null",    0),
    "F-null+hint":      ("null",    1),
    "F-prom-retrieved": ("prom",    0),
    "F-prom+hint":      ("prom",    1),
}
#: The 2x2 the factorial reading actually uses (F-null is the residue control for `prom`).
FACTORIAL_CELLS = ("F-generic", "F-hint", "F-prom-retrieved", "F-prom+hint")

#: prereg §4 as amended 2026-08-25 (before any result was observed; the first run was stopped
#: with no ledger written). The LIVE world -- the only one whose null is load-bearing -- keeps
#: the full 200. The positive controls need only to DETECT a known, large, planted leak, so 50
#: permutations is ample there and the saving is spent where the answer matters.
N_PERM_LIVE = 200
N_PERM_CONTROL = 50
SEED = 20260825


# --------------------------------------------------------------------------- packets

def constantize(payload):
    """Replace the treatment slot with a single constant token.

    THE TREATMENT IS THE ITEMS SLOT and nothing else: the method census, the generic advice
    list, the hint tokens. Everything the template leaves around it -- frame, slug and its
    digits, sparsity block, whitespace, ordering, length -- is nuisance and stays, because
    nuisance is exactly what is on trial.

    Returns None if the payload does not match the template, which is itself a leak (a packet
    outside the frame is a packet whose shape is arm-conditional) and is counted, not dropped
    silently.

    DELEGATES to `packet_render.blank_treatment` and keeps no blanking logic of its own.

    It used to strip the payload before substituting, which erased whitespace differences
    between arms -- Harmonia B measured a planted trailing space at 0/25 caught (HB3-1). Two
    blankers with two behaviours is the seam this campaign keeps re-cutting, so there is now
    one, and this name survives only because the adversary's call sites read better with it.
    """
    from ergon.probe.packet_render import blank_treatment
    return blank_treatment(payload)


def build(rows, arms_obj, inject=None):
    """(texts, arm_labels, groups) over every (task, arm), treatment constantized.

    `inject` is a callable (arm, uid, payload) -> payload used ONLY by the positive controls to
    put a known leak back in. It is applied BEFORE constantizing, so an injected leak has to
    survive the same removal the real packets get.
    """
    from ergon.probe.packet_invariants import payload_of
    texts, labels, groups, nonconforming = [], [], [], 0
    for r in rows:
        uid = r["uid"]
        base = arms_obj.prompt("F0", uid)
        for arm in ARMS:
            payload = payload_of(arms_obj.prompt(arm, uid), base)
            if inject is not None:
                payload = inject(arm, uid, payload)
            c = constantize(payload)
            if c is None:
                nonconforming += 1
                c = payload            # keep it: dropping it would hide the leak
            texts.append(c)
            labels.append(arm)
            groups.append(uid)
    return texts, np.array(labels), np.array(groups), nonconforming


# --------------------------------------------------------------------------- adversaries

_WS_RUN = re.compile(r"[ \t]+")
_DIGIT_RUN = re.compile(r"\d+")


def structural_features(text):
    """Explicit structure, INCLUDING DIGITS AS VALUES. The historical band lived in digits, and
    every shape abstraction this campaign wrote mapped digit runs to a placeholder, so the
    evidence was erased before the check saw it. Here the integers are features."""
    cats = collections.Counter(unicodedata.category(ch) for ch in text)
    digits = _DIGIT_RUN.findall(text)
    ws = [len(m) for m in _WS_RUN.findall(text)]
    ints = [int(d) for d in digits] or [0]
    f = {
        "bytes": len(text.encode("utf-8")),
        "chars": len(text),
        "lines": text.count("\n"),
        "tokens_ws": len(text.split()),
        "digit_runs": len(digits),
        "digit_chars": sum(len(d) for d in digits),
        "int_max": max(ints), "int_min": min(ints), "int_sum": sum(ints),
        "int_mean": sum(ints) / len(ints),
        "n_distinct_ints": len(set(ints)),
        "commas": text.count(","), "colons": text.count(":"),
        "brackets": text.count("["), "parens": text.count("("),
        "hyphens": text.count("-"), "underscores": text.count("_"),
        "ws_runs": len(ws), "ws_run_max": max(ws) if ws else 0,
        "ends_newline": int(text.endswith("\n")),
        "first_char": ord(text[0]) if text else 0,
        "treatment_offset": text.find("<TREATMENT>"),
        "treatment_offset_frac": (text.find("<TREATMENT>") / max(1, len(text))),
        "longest_line": max((len(l) for l in text.split("\n")), default=0),
    }
    for c in ("Ll", "Lu", "Nd", "Po", "Zs", "Pd", "Ps", "Pe", "Cc", "Pc", "Sm"):
        f[f"cat_{c}"] = cats.get(c, 0)
    return f


def distributional_features(text, tok=None):
    b = text.encode("utf-8")
    comp = len(zlib.compress(b, 9))
    counts = np.array(list(collections.Counter(text).values()), dtype=float)
    p = counts / counts.sum()
    ent = float(-(p * np.log2(p)).sum())
    f = {
        "compress_ratio": comp / max(1, len(b)),
        "compressed_bytes": comp,
        "entropy": ent,
        "vocab": len(set(text)),
        "digit_freq": sum(ch.isdigit() for ch in text) / max(1, len(text)),
        "punct_freq": sum(unicodedata.category(ch).startswith("P") for ch in text) / max(1, len(text)),
    }
    n = len(tok(text)) if tok else len(text.split())
    f["tok_len"] = n
    for m in (8, 16, 64):
        f[f"tok_len_mod_{m}"] = n % m
    return f


def _proxy_tokenizer():
    """PROXY ONLY. The solver is nvidia:deepseek-v4-flash and its tokenizer is not available
    locally, so the parser/tokenizer attack class is NOT closed by this gate (prereg §3.1).
    Falls back to whitespace if no local tokenizer loads -- and says so in the ledger."""
    try:
        from transformers import AutoTokenizer
        t = AutoTokenizer.from_pretrained("gpt2", local_files_only=True)
        return (lambda s: t.encode(s)), "gpt2 (local, PROXY — not the solver's tokenizer)"
    except Exception:
        return (lambda s: s.split()), "whitespace FALLBACK — no local tokenizer available"


def _dictvec(dicts):
    keys = sorted(dicts[0])
    return np.array([[d[k] for k in keys] for d in dicts], dtype=float), keys


# --------------------------------------------------------------------------- evaluation

def _fit_predict(kind, Xtr, ytr, Xte, seed):
    if kind == "text":
        clf = LinearSVC(C=1.0, dual="auto", max_iter=5000)
    elif kind == "trees":
        clf = HistGradientBoostingClassifier(max_iter=150, random_state=seed)
    else:
        clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=4000, C=4.0))
    clf.fit(Xtr, ytr)
    return clf.predict(Xte)


def cv_balanced_accuracy(X, y, groups, kind, folds=None, seed=SEED):
    """Grouped 5-fold balanced accuracy on a PRE-VECTORIZED matrix.

    Grouped by TASK, so no fold can memorise task text and read the arm off it -- a row-level
    split is what let 14 memorised constants produce a positive that was later retracted.

    `X` is already numeric. Vectorization happens ONCE per world, outside the permutation loop,
    because permuting LABELS does not change the features -- re-vectorizing inside the loop was
    costing ~2 orders of magnitude and would have forced a weaker null to fit the time budget.
    The vectorizer is fit on all rows, which is safe here precisely because it is LABEL-BLIND:
    it cannot transmit label information it never saw, and it is applied identically to the
    observed and permuted runs, so the null absorbs any transductive advantage.
    """
    if folds is None:
        folds = list(GroupKFold(n_splits=5).split(np.zeros(len(y)), y, groups))
    preds = np.empty(len(y), dtype=object)
    for tr, te in folds:
        preds[te] = _fit_predict(kind, X[tr], y[tr], X[te], seed)
    return float(balanced_accuracy_score(y, preds.astype(str)))


def permute_within_task(y, groups, rng):
    """THE NULL. Each task contributes exactly one packet per arm, so permuting the six labels
    within a task destroys arm identity while preserving every task property. That is precisely
    the exchangeability the design asserts -- and it is why chance (1/6) is the wrong reference:
    at n=1200 with high-dimensional features an adversary beats 1/6 by overfitting alone."""
    out = np.array(y, copy=True)
    for g in np.unique(groups):
        idx = np.where(groups == g)[0]
        out[idx] = y[idx][rng.permutation(len(idx))]
    return out


def target_labels(arm_labels, target):
    if target == "arm6":
        return arm_labels
    if target == "cell4":
        return arm_labels
    if target == "R":
        return np.array([ARMS[a][0] for a in arm_labels])
    if target == "H":
        return np.array([str(ARMS[a][1]) for a in arm_labels])
    raise ValueError(target)


def input_vacuity(texts, groups):
    """Is the gate's INPUT constant within task? Then it can decide nothing.

    TECHNE 2026-08-25, ATK-016. INVARIANT 7 re-keyed the slug on the task, which makes every
    arm's blanked payload byte-identical -- and `packet_invariants.check_invariant_7`'s own
    docstring says so: *"the adversarial gate is now VACUOUS on these packets ... a vacuous
    reading reported as a passing one is its own defect class"*. That was written in prose and
    nothing enforced it: `main()` would still compute obs = 1/n_classes exactly, find it below
    p95, and write `verdict: PASS -- no tested adversary recovered assignment`.

    Measured on the current packets: 200 tasks, ONE distinct blanked payload per task across all
    six arms, and the permutation null has ZERO variance (p05 == p95 == mean). A PASS from that
    input is not evidence about the packets; it is arithmetic about a constant.

    This is the generalization already recorded in ATK-013: *a gate whose input field is absent
    must RAISE, never return a passing value.* Here the field is present and CONSTANT, which is
    the same defect with a different presentation.
    """
    per_task = {}
    for t, g in zip(texts, groups):
        per_task.setdefault(g, set()).add(t)
    constant = sum(1 for v in per_task.values() if len(v) <= 1)
    return {"tasks": len(per_task), "tasks_with_constant_input": constant,
            "fraction_constant": round(constant / max(1, len(per_task)), 4),
            "distinct_texts": len(set(texts)), "n_texts": len(texts),
            "VACUOUS": constant == len(per_task)}


def run_gate(texts, arm_labels, groups, label, tokname, tok, n_perm):
    """Every (adversary x target) pair against its OWN within-task permutation null."""
    rng = np.random.default_rng(SEED)

    # Vectorize once per world. Label-blind, so this cannot leak the target.
    tfidf = TfidfVectorizer(analyzer="char", ngram_range=(1, 5), min_df=2, lowercase=False)
    # KEPT SPARSE. Densifying char 1-5 grams over 1,200 packets is a ~50k-column float
    # matrix; LinearSVC consumes CSR natively and row-indexing works the same.
    Xtext = tfidf.fit_transform(texts)
    Xstruct, struct_keys = _dictvec([structural_features(t) for t in texts])
    Xdist, dist_keys = _dictvec([distributional_features(t, tok) for t in texts])
    Xs = {"lexical": (Xtext, "text"),
          "structural": (Xstruct, "trees"),
          "distributional": (Xdist, "dense")}

    results = {}
    for target in ("arm6", "cell4", "R", "H"):
        y_all = target_labels(arm_labels, target)
        keep = (np.isin(arm_labels, FACTORIAL_CELLS) if target == "cell4"
                else np.ones(len(arm_labels), dtype=bool))
        idx = np.where(keep)[0]
        g, y = groups[idx], y_all[idx]
        folds = list(GroupKFold(n_splits=5).split(np.zeros(len(y)), y, g))
        for adv, (X, kind) in Xs.items():
            Xk = X[idx]
            obs = cv_balanced_accuracy(Xk, y, g, kind, folds)
            null = np.array([cv_balanced_accuracy(Xk, permute_within_task(y, g, rng), g, kind,
                                                  folds) for _ in range(n_perm)])
            p95, p90 = float(np.percentile(null, 95)), float(np.percentile(null, 90))
            p05 = float(np.percentile(null, 5))
            # TECHNE 2026-08-25, ATK-016/ATK-017. The verdict was ONE-SIDED: only `obs > p95`
            # could fail. But balanced accuracy BELOW chance carries the same information as
            # above it -- an adversary inverts the prediction -- so for a gate asking whether
            # assignment is RECOVERABLE the quantity is |obs - null|, not obs - null.
            #
            # This is not hypothetical here. The committed LIVE world sat below its null on 9 of
            # 12 pairs, and its lexical|arm6 signature (obs 0.1275, null 0.1677, d = -0.0402) is
            # quantitatively indistinguishable from this file's OWN planted-leak control
            # SENSITIVITY_band_plus3 (obs 0.1292, null 0.1647, d = -0.0355) -- a leak the
            # sensitivity sweep documents the gate as unable to detect. Both were scored PASS.
            #
            # The new branch is ADDITIVE and carries its own name rather than reinterpreting the
            # preregistered upper-tail thresholds: a below-null excursion is reported as
            # FAIL-LEAK-INVERTED, and the semantics of the original verdicts are untouched.
            verdict = ("FAIL-LEAK" if obs > p95 else
                       "FAIL-LEAK-INVERTED" if obs < p05 else
                       "UNDECIDED" if obs > p90 else "PASS")
            results[f"{adv}|{target}"] = {
                "observed_balanced_accuracy": round(obs, 4),
                "null_mean": round(float(null.mean()), 4),
                "null_p05": round(p05, 4),
                "null_p90": round(p90, 4), "null_p95": round(p95, 4),
                "null_max": round(float(null.max()), 4),
                "signed_delta": round(float(obs - null.mean()), 4),
                "abs_delta": round(abs(float(obs - null.mean())), 4),
                "n_permutations": int(n_perm),
                "n_rows": int(len(y)), "n_classes": int(len(set(y))),
                "verdict": verdict,
            }
        print(f"    {label}/{target}: " + "  ".join(
            f"{a}={results[f'{a}|{target}']['observed_balanced_accuracy']:.3f}"
            f"/p95={results[f'{a}|{target}']['null_p95']:.3f}" for a in Xs))
    vac = input_vacuity(texts, groups)
    return {"world": label, "tokenizer": tokname, "pairs": results,
            "n_features": {"lexical": int(Xtext.shape[1]), "structural": len(struct_keys),
                           "distributional": len(dist_keys)},
            "input_vacuity": vac,
            "any_fail": any(v["verdict"].startswith("FAIL-LEAK") for v in results.values()),
            "any_inverted": any(v["verdict"] == "FAIL-LEAK-INVERTED" for v in results.values()),
            "any_undecided": any(v["verdict"] == "UNDECIDED" for v in results.values())}


# --------------------------------------------------------------------------- injections

def inject_lead_line(arm, uid, payload):
    """Killed defect 1, re-injected: a lead line on 2 of 6 arms."""
    return ("A prior attempt record:\n" + payload
            if arm in ("F-null", "F-prom-retrieved") else payload)


def _reslug(payload, offset):
    return re.sub(r"(probe_pool:[a-z_]+-[A-Z]\d+-)(\d{5})",
                  lambda m: f"{m.group(1)}{(int(m.group(2)) + offset) % 100000:05d}",
                  payload, count=1)


def inject_slug_band(arm, uid, payload):
    """Killed defect 2, re-injected: disjoint per-arm numeric bands."""
    off = {"F-generic": 40000, "F-hint": 50000, "F-null+hint": 60000, "F-prom+hint": 70000}
    return _reslug(payload, off[arm]) if arm in off else payload


def inject_subtle_band(arm, uid, payload):
    """REPORTED, NOT GATED. A per-arm offset of +3 -- three orders of magnitude smaller than the
    historical defect. This measures the smallest leak the gate can see, which is the honest
    content of a PASS: a gate whose sensitivity is unknown licenses nothing."""
    off = {"F-generic": 3, "F-hint": 6, "F-null+hint": 9, "F-prom+hint": 12}
    return _reslug(payload, off.get(arm, 0))


def main():
    import ergon.probe.campaign as C
    OUT.mkdir(parents=True, exist_ok=True)
    rows = C.manifest()
    gold = {r["uid"]: r["gold_int"] for r in rows}
    arms_obj = C.Arms(rows, gold)
    tok, tokname = _proxy_tokenizer()

    # TECHNE 2026-08-25, ATK-016. `manifest_sha16` covers the TASK MANIFEST and not the packet
    # RENDERER, so it is invariant to exactly the change that invalidated this ledger. Measured:
    # the committed leakage_gate.json carries manifest_sha16 e6b1e001bf79e3ef, the CURRENT
    # manifest hashes to the same value, and yet not one of its six LIVE observed figures
    # reproduces -- lexical|arm6 is committed at 0.1275 and recomputes to 0.1667. The slug was
    # re-keyed on the task between the two, and no provenance field could see it. A stamp that
    # covers the inputs but not the transform cannot detect a stale artifact.
    render_src = (ROOT / "ergon/probe/packet_render.py").read_bytes()
    import hashlib
    renderer_sha16 = hashlib.sha256(render_src).hexdigest()[:16]

    report = {"prereg": "ergon/probe/PREREG_adversarial_leakage_gate_2026-08-25.md",
              "manifest_sha16": C.manifest_sha256(rows)[:16],
              "renderer_sha16": renderer_sha16,
              "n_tasks": len(rows), "arms": sorted(ARMS),
              "retired_claim": "arm identity is computationally unavailable — MALFORMED, "
                               "retired 2026-08-25: the treatment identifies the arm",
              "worlds": {}}

    # POSITIVE CONTROLS FIRST (prereg §5). A null from an adversary that cannot detect a known
    # leak is uninterpretable, so this order is not cosmetic.
    for name, inj, gated in (("POSCTRL_lead_line", inject_lead_line, True),
                             ("POSCTRL_slug_band", inject_slug_band, True),
                             ("SENSITIVITY_band_plus3", inject_subtle_band, False)):
        texts, labels, groups, nc = build(rows, arms_obj, inject=inj)
        r = run_gate(texts, labels, groups, name, tokname, tok, N_PERM_CONTROL)
        r["gated"] = gated
        r["nonconforming_payloads"] = nc
        r["must_detect"] = gated
        r["detected"] = r["any_fail"]
        report["worlds"][name] = r
        print(f"{name:26s} detected={r['any_fail']}  (gated={gated})")

    live_texts, live_labels, live_groups, nc = build(rows, arms_obj)
    live = run_gate(live_texts, live_labels, live_groups, "LIVE", tokname, tok, N_PERM_LIVE)
    live["nonconforming_payloads"] = nc
    report["worlds"]["LIVE"] = live
    print(f"{'LIVE':26s} any_fail={live['any_fail']}  any_undecided={live['any_undecided']}")

    ctrl_ok = all(report["worlds"][n]["detected"]
                  for n in ("POSCTRL_lead_line", "POSCTRL_slug_band"))
    report["positive_controls_pass"] = ctrl_ok
    # TECHNE 2026-08-25, ATK-016. Vacuity is checked BEFORE the pass/fail ladder, because a
    # gate whose live input is constant across arms cannot produce evidence about those arms
    # and its PASS would otherwise be byte-indistinguishable from an earned one.
    live_vac = live["input_vacuity"]
    report["live_input_vacuity"] = live_vac
    if live_vac["VACUOUS"]:
        report["verdict"] = (
            "VACUOUS — the live packets' non-treatment content is BYTE-IDENTICAL across all "
            f"arms ({live_vac['tasks_with_constant_input']}/{live_vac['tasks']} tasks have a "
            "single distinct blanked payload), so this gate has no input to discriminate on and "
            "its permutation null has zero variance. This is NOT a PASS: it is the correct "
            "consequence of INVARIANT 7 having closed the channel by construction, and the gate "
            "is retained only as a REGRESSION detector that would fire if an arm-varying "
            "nuisance field were reintroduced. Reporting it as PASS would be a vacuous reading "
            "presented as a passing one.")
        (OUT / "leakage_gate.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print()
        print(report["verdict"])
        return 0
    if not ctrl_ok:
        report["verdict"] = ("UNINTERPRETABLE — an adversary that cannot detect a KNOWN leak "
                             "proves nothing when it reports a null. This is a terminal finding "
                             "about the gate, not a result about the packets.")
    elif live["any_fail"]:
        inv = " (INVERTED: recovery is BELOW the null, which is recovery all the same — an "
        inv += "adversary inverts the prediction)" if live.get("any_inverted") else ""
        report["verdict"] = ("FAIL — nuisance leakage detected on live packets; P2 does not run"
                             + inv)
    elif live["any_undecided"]:
        report["verdict"] = "UNDECIDED — re-run at 1,000 permutations before reading either way"
    else:
        report["verdict"] = ("PASS — no tested adversary recovered assignment above its "
                             "preregistered permutation null, from the non-treatment content of "
                             "held-out packets, at any of three representations. This does NOT "
                             "establish that no arm label exists; see prereg §3.1 for the "
                             "attack classes that remain uncovered.")
    (OUT / "leakage_gate.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\n" + report["verdict"])
    return 0 if (ctrl_ok and not live["any_fail"]) else 2


if __name__ == "__main__":
    sys.exit(main())
