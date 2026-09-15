"""Families C3 (exact behavioural quotient) and C4 (consequence signatures), run first by the frozen order.

Both are EXACT table compressions: they group states whose consequence rows over the TRAIN targets are identical and
store one row per class plus a state -> class index.  Neither has an input encoding for unseen states or targets, so
per the frozen preregistration they are scored as compression of the exact table (CR at lookup accuracy) and, on
HELD_PAIRS, by row sharing: a held entry (s, t) is predicted from train states whose known row (all train targets
except t, held entries masked) is identical to s's and whose (s', t) entry is known.  Coverage is reported.
Post hoc (AC-01R interpretation only): adjusted mutual information between the classes and the kernel classes.
Nothing here reads a held-out D entry as an input: held entries are replaced by a sentinel before any grouping.
"""
from __future__ import annotations
import json, lzma, os, time
import numpy as np
from ..corpus import build
from ..evaluate import DENOM_LZMA, write_result
from ...universe.directed_rewriting import sha256_arrays

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SENT = -3


def ami(a: np.ndarray, b: np.ndarray) -> float:
    from sklearn.metrics import adjusted_mutual_info_score  # optional dependency
    return float(adjusted_mutual_info_score(a, b))


def nmi_plugin(a: np.ndarray, b: np.ndarray) -> float:
    """Normalised mutual information (plug-in, arithmetic mean normalisation) without external deps."""
    au, ai = np.unique(a, return_inverse=True); bu, bi = np.unique(b, return_inverse=True); ai = ai.ravel(); bi = bi.ravel()
    n = len(ai); pa = np.bincount(ai) / n; pb = np.bincount(bi) / n
    pair, cnt = np.unique(ai.astype(np.int64) * len(bu) + bi, return_counts=True); pj = cnt / n
    I = float((pj * np.log(pj / (pa[pair // len(bu)] * pb[pair % len(bu)]))).sum())
    Ha = float(-(pa[pa > 0] * np.log(pa[pa > 0])).sum()); Hb = float(-(pb[pb > 0] * np.log(pb[pb > 0])).sum())
    return I / (0.5 * (Ha + Hb)) if Ha + Hb > 0 else 0.0


def bytes_lzma(*arrays) -> int:
    return len(lzma.compress(b"".join(np.ascontiguousarray(a).tobytes() for a in arrays), preset=6))


def run():
    t0 = time.perf_counter()
    U, M, manifest = build(); D = U["D"]; NS = U["NS"]
    sr, trole, pr, live, corpus = M["state_role"], M["target_role"], M["pair_role"], M["live"], M["corpus"]
    train_t = np.nonzero(trole == 0)[0]; held_t = np.nonzero(trole == 1)[0]
    tr_s = np.nonzero((sr == 0) & corpus)[0]
    # ---- fitted table over train states x train targets with held pairs masked (FIT only)
    rows = D[np.ix_(tr_s, train_t)].astype(np.int16)
    masked = pr[np.ix_(tr_s, train_t)] == 1
    rows_fit = rows.copy(); rows_fit[masked] = SENT
    # C3: exact behavioural quotient on the fitted rows
    def quotient(sig_rows, label):
        keys, inv, counts = np.unique(sig_rows, axis=0, return_inverse=True, return_counts=True)
        inv = inv.ravel()
        table_bytes = bytes_lzma(keys.astype(np.int16)); index_bytes = bytes_lzma(inv.astype(np.int32))
        total = table_bytes + index_bytes
        return {"classes": int(len(keys)), "states": int(len(inv)), "mean_class_size": float(len(inv) / len(keys)),
                "class_size_quartiles": [int(np.percentile(counts, q)) for q in (0, 25, 50, 75, 100)],
                "bytes_table_lzma": table_bytes, "bytes_index_lzma": index_bytes, "bytes_total": total, "CR_vs_denominator": DENOM_LZMA / total,
                "sha256_classes": sha256_arrays(keys)}, inv
    c3, inv3 = quotient(rows_fit, "C3")
    # C3 on the complete exact table (all 63 targets, all corpus states): pure representation-compression figure
    full_rows = D[np.ix_(np.nonzero(corpus)[0], np.arange(D.shape[1]))].astype(np.int16)
    c3_full, inv_full = quotient(full_rows, "C3-full")
    # C4: consequence signature = (D over train targets, and per action the successor-D delta code over train targets)
    succ = M["succ"]; sig_parts = [rows_fit]
    for r in range(3):
        sd = D[np.ix_(succ[tr_s, r], train_t)].astype(np.int16)
        delta = np.where(rows >= 0, np.where(sd >= 0, sd - rows, 99), SENT).astype(np.int16)  # 99 = target lost, SENT = source not live
        delta[masked] = SENT
        sig_parts.append(delta)
    sig = np.concatenate(sig_parts, axis=1)
    c4, inv4 = quotient(sig, "C4")
    # ---- HELD_PAIRS completion by row sharing (C3 rows): coverage and accuracy
    held_idx = np.argwhere(masked & (rows >= 0))  # held entries with a true value (scored subset)
    rng = np.random.default_rng(0)
    if len(held_idx) > 200000: held_idx = held_idx[rng.choice(len(held_idx), 200000, replace=False)]
    # group train states by their fitted row with column j removed, for each column j touched (vectorised per column)
    covered = 0; exact = 0; within1 = 0; scored = 0
    for j in np.unique(held_idx[:, 1]):
        cols = np.delete(np.arange(rows.shape[1]), j)
        sub = rows_fit[:, cols]
        keys, inv = np.unique(sub, axis=0, return_inverse=True); inv = inv.ravel()
        known = ~masked[:, j] & (rows[:, j] >= 0)
        # per class: majority known value at column j (vectorised: count (class, value) pairs)
        kc = inv[known]; kv = rows[known, j].astype(np.int64) + 1  # values >= 0 -> shift by 1
        pair = kc.astype(np.int64) * 64 + kv
        pu, pc = np.unique(pair, return_counts=True)
        cls_of = pu // 64; val_of = pu % 64 - 1
        order = np.lexsort((-pc, cls_of)); cls_sorted = cls_of[order]; val_sorted = val_of[order]
        first = np.concatenate([[True], cls_sorted[1:] != cls_sorted[:-1]])
        maj_cls = cls_sorted[first]; maj_val = val_sorted[first]
        rows_j = held_idx[held_idx[:, 1] == j, 0]
        c_s = inv[rows_j]; pos = np.searchsorted(maj_cls, c_s); pos = np.clip(pos, 0, max(0, len(maj_cls) - 1))
        hit = (len(maj_cls) > 0) & (maj_cls[pos] == c_s) if len(maj_cls) else np.zeros(len(rows_j), bool)
        scored += int(len(rows_j)); covered += int(hit.sum())
        if hit.any():
            pred = maj_val[pos[hit]]; true = rows[rows_j[hit], j].astype(np.int64)
            exact += int((pred == true).sum()); within1 += int((np.abs(pred - true) <= 1).sum())
    held = {"scored": scored, "coverage": covered / max(1, scored), "exact_given_covered": exact / max(1, covered), "within1_given_covered": within1 / max(1, covered),
            "exact_overall": exact / max(1, scored)}
    # ---- post hoc: relation of classes to the kernel and to count-vector classes
    kern = U["kmask"][tr_s]; cvec = U["cvec_id"][tr_s]
    post = {"C3_vs_kernel_NMI": nmi_plugin(inv3, kern), "C3_vs_countvector_NMI": nmi_plugin(inv3, cvec), "C4_vs_kernel_NMI": nmi_plugin(inv4, kern),
            "C3full_vs_kernel_NMI": nmi_plugin(inv_full, U["kmask"][corpus]), "kernel_classes_in_train": int(len(np.unique(kern))),
            "C3_classes_per_kernel_class_mean": float(len(np.unique(inv3)) / len(np.unique(kern)))}
    res = {"family": "C3/C4 exact quotient and consequence signature", "eligible_sets": ["FIT compression", "HELD_PAIRS by row sharing"],
           "train_states": int(len(tr_s)), "train_targets": int(len(train_t)), "denominator_lzma": DENOM_LZMA,
           "C3_fit_rows": c3, "C3_full_exact_table": c3_full, "C4_fit_signatures": c4, "HELD_PAIRS_row_sharing": held, "post_hoc": post,
           "interpretation_rules": "exact families are scored as table compression (CR at lookup accuracy on FIT) and HELD_PAIRS row sharing; not eligible for cross-target verdicts",
           "seconds": round(time.perf_counter() - t0, 1)}
    path = write_result(res, "C3_C4_exact"); print(json.dumps(res, indent=1)); print(path)
    return res


if __name__ == "__main__":
    run()
