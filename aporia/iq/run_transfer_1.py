"""run_transfer_1.py — TRANSFER-1 measurement. Predicates only; nothing here is interpreted.

Preregistration: aporia/iq/PREREG_TRANSFER_1_2026-08-25.md (e7a9b314), written before the
generator existed. Predictions T1-T6 and the terminal-state table are fixed there.

    python aporia/iq/run_transfer_1.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "apollo" / "src", ROOT / "apollo" / "scripts",
          ROOT / "agents" / "hephaestus" / "src", Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import blackboard_evolve as be                                   # noqa: E402
from blackboard import BlackboardState, run_pipeline             # noqa: E402
import port_ops                                                  # noqa: E402
from port_ops import _mutant                                     # noqa: E402
from run_iq_port_1 import make_pool, PORTED_BODY, CEILING_TAIL    # noqa: E402
import transfer1_generator as G                                  # noqa: E402

OUT = Path(__file__).resolve().parent

EXTRA_MUTANTS = {
    "M5_return_n": _mutant("M5_return_n", lambda t, n: n),
    "M6_half_total": _mutant("M6_half_total", lambda t, n: t // 2),
}
ALL_MUTANTS = {**port_ops.MUTANTS, **EXTRA_MUTANTS}


def score(tasks, pool, pipeline):
    """Returns (n_correct, n_total, per_task_bool). Exceptions count as wrong, never dropped."""
    ops = [pool[n] for n in pipeline]
    hits, per = 0, []
    for t in tasks:
        st = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        try:
            ans = run_pipeline(ops, st).selected_answer
        except Exception:
            ans = ""
        ok = (ans == t["correct"])
        hits += ok
        per.append(ok)
    return hits, len(tasks), per


def by_key(tasks, per, key):
    out = {}
    for t, ok in zip(tasks, per):
        k = str(t.get(key))
        a, b = out.get(k, (0, 0))
        out[k] = (a + ok, b + 1)
    return {k: {"correct": v[0], "n": v[1], "acc": round(v[0] / v[1], 4)}
            for k, v in sorted(out.items())}


def parser_fires(tasks):
    """Does parse_all_but_n write `quantities` at all? Separates a surface failure from a
    capability failure -- the whole reason surface varies independently of structure here."""
    n = 0
    for t in tasks:
        st = BlackboardState(problem_text=t["prompt"], candidates=[])
        port_ops.parse_all_but_n(st)
        n += ("total" in st.quantities and "removed" in st.quantities)
    return n


def main():
    R = {"experiment": "TRANSFER-1", "date": "2026-08-25", "agent": "Aporia (M1)",
         "prereg": "aporia/iq/PREREG_TRANSFER_1_2026-08-25.md", "prereg_commit": "e7a9b314",
         "E_of_C_qualifier": ("E(C)=0.8333 is the exact ceiling under Apollo's CLEAN-ROUTING "
                              "regime (Lexis fcdc91af), not the unrestricted-pool maximum "
                              "0.8917. This rung does not measure dE at all.")}

    train, test, xsets = G.build()
    R["corpus_sha256"] = G.corpus_hash(train, test, xsets)
    R["seed"] = G.SEED
    R["n_train"], R["n_test"] = len(train), len(test)
    R["stratum_mix_declared"] = {k: v for k, v in G.STRATUM_MIX}
    R["train_strata"] = dict(Counter(t["stratum"] for t in train))
    R["test_strata"] = dict(Counter(t["stratum"] for t in test))
    R["train_surfaces"] = dict(Counter(t["surface"] for t in train))
    R["test_surfaces"] = dict(Counter(t["surface"] for t in test))
    R["test_unseen_combination_n"] = sum(t["unseen_combination"] for t in test)

    # LOUD accounting: rejection sampling can fall through and mislabel a draw.
    mismatch = [t for t in train + test if t["stratum"] != t["stratum_requested"]]
    R["stratum_request_mismatches"] = len(mismatch)
    R["dropped_records"] = 0
    R["dropped_records_note"] = ("Nothing is dropped. Every generated task is scored; pipeline "
                                 "exceptions count as WRONG. Draws whose realised stratum "
                                 "differs from the requested one are counted above and kept, "
                                 "labelled by their REALISED stratum.")

    # T1: the nondegenerate stratum must contain no draw whose target equals an operand.
    nd = [t for t in train + test if t["stratum"] == "NONDEGENERATE"]
    viol = [t for t in nd if t["target"] in (t["T"], t["N"])]
    R["T1_nondegenerate_clean"] = (len(viol) == 0 and len(nd) > 0)
    R["T1_nondegenerate_n"] = len(nd)
    R["T1_violations"] = len(viol)
    # the stratum labels must partition, asserted by enumeration
    labels = {G.stratum(t["T"], t["N"]) for t in train + test}
    assert labels <= {"NONDEGENERATE", "DEGENERATE", "NEAR_DEGENERATE"}, "stratum leak"
    assert all(sum([G.stratum(t["T"], t["N"]) == s for s in
                    ("NONDEGENERATE", "DEGENERATE", "NEAR_DEGENERATE")]) == 1
               for t in train + test), "stratum labels do not partition"
    R["stratum_labels_partition"] = True

    CP = make_pool(port_ops.PORT_OPS)
    PIPE = PORTED_BODY + CEILING_TAIL

    def block(tasks, label):
        k, n, per = score(tasks, CP, PIPE)
        return {"n": n, "correct": k, "acc": round(k / n, 4) if n else None,
                "by_stratum": by_key(tasks, per, "stratum"),
                "by_surface": by_key(tasks, per, "surface"),
                "parser_fires": parser_fires(tasks), "label": label}

    R["port_train"] = block(train, "G-heldout TRAIN")
    R["port_test"] = block(test, "G-heldout TEST (held-out parameter region)")
    nd_train = [t for t in train if t["stratum"] == "NONDEGENERATE"]
    nd_test = [t for t in test if t["stratum"] == "NONDEGENERATE"]
    R["T2_port_train_nondegenerate_acc"] = R["port_train"]["by_stratum"].get("NONDEGENERATE")
    R["T3_port_test_nondegenerate_acc"] = R["port_test"]["by_stratum"].get("NONDEGENERATE")

    # T4 (LOAD-BEARING): wrong mutants near zero on NONDEGENERATE; return_n near ceiling on
    # DEGENERATE. Failing input, stated: any mutant at or near the port's nondegenerate rate.
    deg = [t for t in train + test if t["stratum"] == "DEGENERATE"]
    mut = {}
    for name, op in ALL_MUTANTS.items():
        pool = make_pool({"parse_all_but_n": port_ops.parse_all_but_n, "op_all_but_n": op})
        k_nd, n_nd, _ = score(nd_train + nd_test, pool, PIPE)
        k_dg, n_dg, _ = score(deg, pool, PIPE)
        mut[name] = {"nondegenerate_acc": round(k_nd / n_nd, 4) if n_nd else None,
                     "degenerate_acc": round(k_dg / n_dg, 4) if n_dg else None}
    k_nd, n_nd, _ = score(nd_train + nd_test, CP, PIPE)
    k_dg, n_dg, _ = score(deg, CP, PIPE)
    port_nd = round(k_nd / n_nd, 4)
    port_dg = round(k_dg / n_dg, 4) if n_dg else None
    R["mutants"] = mut
    R["port_nondegenerate_acc"] = port_nd
    R["port_degenerate_acc"] = port_dg
    R["degenerate_n"] = n_dg
    worst = max(v["nondegenerate_acc"] for v in mut.values())
    R["worst_mutant_nondegenerate_acc"] = worst
    R["T4_mutants_separated"] = (worst < 0.10 and port_nd > 0.50 and worst < port_nd / 2)
    R["T4_return_n_wins_on_degenerate"] = (mut["M5_return_n"]["degenerate_acc"] is not None
                                           and mut["M5_return_n"]["degenerate_acc"] > 0.50)

    # T5: does the port's parser fire at all on structurally different construction routes?
    xr = {}
    for name, tasks in xsets.items():
        k, n, per = score(tasks, CP, PIPE)
        xr[name] = {"n": n, "acc": round(k / n, 4), "parser_fires": parser_fires(tasks),
                    "by_stratum": by_key(tasks, per, "stratum")}
    R["x_heldout"] = xr
    R["T5_parser_fails_on_all_X_routes"] = all(v["parser_fires"] == 0 for v in xr.values())

    # T6: mutants passing G but failing X. Reported either way.
    R["T6_mutants_passing_G_failing_X"] = [
        name for name, v in mut.items()
        if v["nondegenerate_acc"] is not None and v["nondegenerate_acc"] > 0.50]

    # ── terminal state ───────────────────────────────────────────────────────
    if not R["T1_nondegenerate_clean"]:
        verdict = "PARK_GENERATOR_CANNOT_PRODUCE_CLEAN_STRATUM"
    elif not R["T4_mutants_separated"]:
        verdict = "REDESIGN_UNSTRATIFIED_DEGENERACY"
    else:
        verdict = "ADVANCE"
    R["verdict"] = verdict
    R["verdict_rule_null_output"] = ("If the generator produced zero NONDEGENERATE draws, T1 is "
                                     "false and the run PARKs; a vacuous pass is impossible "
                                     "because T1 requires len(nondegenerate) > 0.")
    seen = set()
    for t1 in (True, False):
        for t4 in (True, False):
            seen.add("PARK_GENERATOR_CANNOT_PRODUCE_CLEAN_STRATUM" if not t1 else
                     ("REDESIGN_UNSTRATIFIED_DEGENERACY" if not t4 else "ADVANCE"))
    assert seen == {"PARK_GENERATOR_CANNOT_PRODUCE_CLEAN_STRATUM",
                    "REDESIGN_UNSTRATIFIED_DEGENERACY", "ADVANCE"}, "terminal table leaks"
    R["terminal_table_partitions"] = True

    json.dump(R, open(OUT / "RESULT_TRANSFER_1.json", "w", encoding="utf-8"), indent=2)
    for k, v in R.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
