"""Tier-A exit review #3 — machine attack on the single chartered invariant.

    TREATMENT IDENTITY MUST BE COMPUTATIONALLY UNAVAILABLE AFTER SEMANTIC CONTENT IS REMOVED.

Charon (kill authority, M1), 2026-08-23. Charter R2-1. $0 — local compute only, no API calls.

METHOD NOTE (why this file exists rather than reuse):
The review prompt requires a stripper *I* write: reusing `ergon.probe`'s own redaction would
test the pipeline with the pipeline. Everything below is independent of the pipeline except
for calling it to RENDER the packets under attack.

TWO STRIPPERS, deliberately, because "semantic content removed" has a defensible range:
  STRICT  — every alphanumeric run collapses to a single class token (W / N). Preserves token
            counts, punctuation, line and blank-line structure, whitespace, field ordering,
            position. Destroys word lengths. This is the VERDICT-BEARING stripper.
  SHAPE   — every alphanumeric CHARACTER maps to its class (a / 9), preserving run lengths.
            Strictly more information than STRICT. Reported as a supplementary finding: a leak
            visible only here means fixed boilerplate is recoverable from its silhouette.

TWO PIPELINE STATES, because the pipeline that will run is not the pipeline as committed:
  AS-IS    — exactly as committed. ATK-013 is live, so the residue pool is empty.
  REPAIRED — a READ-ONLY shim maps the campaign ledger's `key: [rep, uid]` into the flat
             `rep`/`uid` schema `assemble.load_prepass` expects. Nothing in ergon/ is modified.
             This is the packet set Tier B would actually ship once the seam is closed, and it
             is the state the invariant must be certified against.

Run:  PYTHONPATH=. python charon/probe/exit_review_3_attack.py
Out:  charon/probe/exit_review_3_evidence.json
"""
import json
import os
import pathlib
import re
import sys
import tempfile

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

ARMS = ("F0", "F-null", "F-generic", "F-prom-retrieved", "F-oracle", "F-answer")
SEED = 20260823
N_SUB = 240          # tasks subsampled for the classifier (grouped CV)
N_REFIT_NULL = 10    # permutation refits, run only where the observed accuracy is not perfect
OUT = ROOT / "charon/probe/exit_review_3_evidence.json"
STATES = tuple(os.environ.get("ER3_STATES", "as-is,repaired").split(","))


# --------------------------------------------------------------- packet rendering

def render(state):
    """Return {arm: {uid: prompt}} for `state` in {'as-is', 'repaired'}."""
    import ergon.probe.campaign as C
    rows = C.manifest()
    gold = {r["uid"]: r["gold_int"] for r in rows}

    if state in ("as-is", "live"):
        # "live" = the pipeline exactly as it stands on disk. After Techne's ATK-013 repair
        # (c6736671, landed 2026-08-23 mid-review) this is the state Tier B would ship.
        arms = C.Arms(rows, gold)
    else:
        # READ-ONLY shim: rewrite the ledger into the loader's schema in a temp file, point
        # the Arms constructor at it, restore immediately. ergon/ is never modified.
        led = C.DIR / "p1_prepass.jsonl"
        tmp = pathlib.Path(tempfile.mkdtemp()) / "p1_prepass.jsonl"
        with tmp.open("w", encoding="utf-8") as fh:
            for line in led.read_text(encoding="utf-8").splitlines():
                d = json.loads(line)
                rep, uid = d["key"]
                d["rep"], d["uid"] = int(rep), uid
                d["ledger_id"] = "p1_prepass"
                fh.write(json.dumps(d, ensure_ascii=False) + "\n")
        real_dir = C.DIR
        C.DIR = tmp.parent
        try:
            arms = C.Arms(rows, gold)
        finally:
            C.DIR = real_dir

    out = {a: {} for a in ARMS}
    for r in rows:
        for a in ARMS:
            out[a][r["uid"]] = arms.prompt(a, r["uid"])
    return out, len(arms.pool)


# --------------------------------------------------------------- my strippers

_RUN = re.compile(r"[A-Za-z]+|[0-9]+")


def strip_strict(text):
    """Collapse every alphanumeric run to one class token. Word LENGTHS destroyed."""
    return _RUN.sub(lambda m: "W" if m.group(0)[0].isalpha() else "N", text)


def strip_shape(text):
    """Map every alphanumeric CHARACTER to its class. Word lengths PRESERVED."""
    return re.sub(r"[A-Za-z]", "a", re.sub(r"[0-9]", "9", text))


# --------------------------------------------------------------- non-content features

def features(text):
    """Numeric non-content features. No lexical content enters this vector."""
    lines = text.split("\n")
    ws = re.findall(r"\s+", text)
    return [
        len(text),
        len(_RUN.findall(text)),                      # token count
        len(lines),
        sum(1 for l in lines if not l.strip()),       # blank lines
        max((len(l) for l in lines), default=0),
        float(np.mean([len(l) for l in lines])) if lines else 0.0,
        text.count("\n\n"),
        text.count(":"),
        text.count("("),
        text.count("["),
        text.count("{"),
        text.count("-"),
        text.count("."),
        text.count(","),
        len(re.findall(r"[0-9]+", text)),
        len(re.findall(r"[A-Z]", text)),
        sum(len(w) for w in ws),                      # total whitespace
        text.find("\n\n") if "\n\n" in text else -1,  # position of first block break
        len(text) - len(text.lstrip()),
        1 if text.lstrip().startswith("{") else 0,    # JSON framing (ATK-001)
        1 if text.rstrip().endswith("}") else 0,
    ]


# --------------------------------------------------------------- the attack

def pair_attack(texts_a, texts_b, uids, rng, want_null=True):
    """Binary arm-pair classifier on stripped text + non-content features.

    Grouped by task uid so no task straddles the train/test split.

    Two readings are reported, and the STRONGER one is `separable_exactly`:
    the invariant says treatment identity must be UNAVAILABLE, so a perfect separator is a
    defect whatever a permutation null says. The permutation null is computed only where the
    observed accuracy is imperfect — where a null is what decides the question. Refitting a
    null against a 1.000 separator would spend compute to confirm that 1.000 > 0.5.
    """
    from scipy.sparse import hstack, csr_matrix
    X_text = list(texts_a) + list(texts_b)
    X_num = np.array([features(t) for t in X_text], dtype=float)
    y = np.array([0] * len(texts_a) + [1] * len(texts_b))
    groups = np.array(list(uids) + list(uids))

    def cv_acc(labels):
        accs = []
        for tr, te in GroupKFold(n_splits=3).split(X_text, labels, groups):
            vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 4), min_df=2,
                                  max_features=5000, lowercase=False)
            A = vec.fit_transform([X_text[i] for i in tr])
            B = vec.transform([X_text[i] for i in te])
            sc = StandardScaler().fit(X_num[tr])
            A = hstack([A, csr_matrix(sc.transform(X_num[tr]))])
            B = hstack([B, csr_matrix(sc.transform(X_num[te]))])
            clf = LogisticRegression(max_iter=1000, C=1.0)
            clf.fit(A, labels[tr])
            accs.append(float(np.mean(clf.predict(B) == labels[te])))
        return float(np.mean(accs))

    obs = cv_acc(y)
    # exact separability of the stripped strings themselves — the strongest statement
    sep = len(set(texts_a) & set(texts_b)) == 0
    out = {"observed": round(obs, 4), "separable_exactly": bool(sep)}
    if want_null and obs < 0.999:
        nulls = []
        for _ in range(N_REFIT_NULL):
            yp = y.copy()
            rng.shuffle(yp)
            nulls.append(cv_acc(yp))
        nm, ns = float(np.mean(nulls)), float(np.std(nulls) or 1e-9)
        out.update({"perm_null_mean": round(nm, 4),
                    "perm_null_95_hi": round(nm + 1.959964 * ns, 4),
                    "z": round((obs - nm) / ns, 2),
                    "beats_null": bool(obs > nm + 1.959964 * ns)})
    else:
        out.update({"perm_null_mean": 0.5, "perm_null_95_hi": None,
                    "z": None, "beats_null": bool(obs >= 0.999)})
    return out


def main():
    rng = np.random.default_rng(SEED)
    report = {"invariant": "treatment identity computationally unavailable after semantic "
                           "content is removed",
              "reviewer": "Charon (kill authority, M1)", "seed": SEED,
              "n_permutations_refit": N_REFIT_NULL,
              "n_tasks_subsampled": N_SUB, "states": {}}

    for state in (STATES):
        packets, pool = render(state)
        uids_all = sorted(packets["F0"])
        uids = list(rng.choice(uids_all, size=min(N_SUB, len(uids_all)),
                               replace=False))
        st = {"residue_pool_records": pool, "arm_token_means": {}, "pairs": {}}
        for a in ARMS:
            toks = [len(_RUN.findall(packets[a][u])) for u in uids_all]
            st["arm_token_means"][a] = {"mean_tokens": round(float(np.mean(toks)), 1),
                                        "sd": round(float(np.std(toks)), 1)}
        # identity check first — a degenerate pair makes the classifier meaningless
        st["byte_identical_pairs"] = []
        for i, a in enumerate(ARMS):
            for b in ARMS[i + 1:]:
                same = sum(1 for u in uids_all if packets[a][u] == packets[b][u])
                if same == len(uids_all):
                    st["byte_identical_pairs"].append(f"{a} == {b}")

        for stripper, fn in (("STRICT", strip_strict), ("SHAPE", strip_shape)):
            st["pairs"][stripper] = {}
            for i, a in enumerate(ARMS):
                for b in ARMS[i + 1:]:
                    if f"{a} == {b}" in st["byte_identical_pairs"]:
                        st["pairs"][stripper][f"{a}|{b}"] = {"degenerate": True}
                        continue
                    ta = [fn(packets[a][u]) for u in uids]
                    tb = [fn(packets[b][u]) for u in uids]
                    st["pairs"][stripper][f"{a}|{b}"] = pair_attack(ta, tb, uids, rng)
                    print(f"  [{state}/{stripper}] {a} vs {b}: "
                          f"{st['pairs'][stripper][f'{a}|{b}']}")

        # ---- POSITIVE CONTROL (mandatory): plant a leak into a COPY and re-attack.
        # One trailing space on F-null only — invisible to a reader, trivial for a meter.
        ta = [strip_strict(packets["F0"][u]) for u in uids]
        tb = [strip_strict(packets["F-answer"][u]) + " " for u in uids]
        st["positive_control"] = pair_attack(ta, tb, uids, rng)
        st["positive_control"]["leak_planted"] = "one trailing space on arm B only"
        print(f"  [{state}] POSITIVE CONTROL: {st['positive_control']}")

        report["states"][state] = st

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
