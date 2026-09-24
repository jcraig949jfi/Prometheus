"""Z80 x Atlas post-campaign audit + re-adjudication (directive 2026-09-23, Phases 1 and 3). READ-ONLY over the campaign.

Reads the preserved 72-hour campaign records (RUNS.jsonl, PACKET.json, per-run SPEC/RECEIPT) from wherever they live, writes
nothing there, and emits NEW artifacts beside this file:

    AUDIT_RECEIPT_<date>.json                          Phase 1: defect code paths + the complete affected-run list
    Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_<date>.json     Phase 3: machine-readable companion
    (the .md is written by hand from the .json; numbers are never retyped -- see render_md)

Every input is fingerprinted (sha256) in the outputs. Before anything is corrected, the campaign's OWN family scorer
(scheduler.Campaign.family_table, unchanged since launch commit c7610ea19) is re-run over the preserved runs and must reproduce
the historical PACKET top table exactly; if it does not, the tool stops (INSTRUMENT_FAILURE: the reconstruction, not the
campaign, would be wrong).

    python -m archaeon.z80atlas.postcampaign.adjudicate --hist <campaign dir> --date 2026-09-23
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from archaeon.z80atlas import grammar as GR, scheduler as S

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
F = GR.FROZEN
CAMPAIGN_COMMIT = "c7610ea19"
NAMED = ["2ace470e5c47", "5b237a475b69", "e8394eee206d"]
DEFAULT_HIST = r"D:\Prometheus-worktrees\archaeon-wse-2026-09-16\archaeon\z80atlas\campaign"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git_line(path: str, needle: str) -> dict:
    src = subprocess.run(["git", "show", "%s:%s" % (CAMPAIGN_COMMIT, path)], cwd=REPO, capture_output=True, check=True, text=True, encoding="utf-8").stdout
    hits = [(i + 1, l.strip()) for i, l in enumerate(src.splitlines()) if needle in l]
    assert len(hits) == 1, (path, needle, hits)
    return {"commit": CAMPAIGN_COMMIT, "file": path, "line": hits[0][0], "code": hits[0][1][:300]}


def load_runs(hist: Path):
    runs, rows, dup = {}, 0, Counter()
    for line in (hist / "RUNS.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line); rows += 1; dup[r["run_id"]] += 1; runs[r["run_id"]] = r      # last wins, exactly as Campaign.__init__
    return runs, rows, {k: v for k, v in dup.items() if v > 1}


def family_table(runs: dict) -> dict:
    return S.Campaign.family_table(SimpleNamespace(runs=runs))            # the campaign's own scorer, unmodified


def top(fams: dict, n=30):
    return [{"family": fam, "score": f["best"], "flags": sorted(f["flags"]), "runs": len(f["runs"]), "best_run": f.get("best_run")}
            for fam, f in sorted(fams.items(), key=lambda x: -x[1]["best"])[:n]]


def spec_of(hist: Path, r: dict) -> dict:
    return json.loads((hist / "runs" / r["run_dir"] / "SPEC.json").read_text(encoding="utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--hist", default=DEFAULT_HIST); ap.add_argument("--date", required=True); ap.add_argument("--no-hash-big", action="store_true")
    a = ap.parse_args(argv); hist = Path(a.hist)
    for need in ("RUNS.jsonl", "PACKET.json", "CAMPAIGN_STATE.json", "GRAMMAR_FROZEN.json", "runs"):
        if not (hist / need).exists():
            print("STOP: required campaign artifact missing: %s" % (hist / need)); return 2
    inputs = {n: sha(hist / n) for n in ("PACKET.json", "CAMPAIGN_PACKET.md", "CAMPAIGN_STATE.json", "CAMPAIGN_DONE.json", "GRAMMAR_FROZEN.json")}
    if not a.no_hash_big:
        inputs.update({n: sha(hist / n) for n in ("RUNS.jsonl", "ATLAS_INDEX.jsonl")})
    grammar_frozen = json.loads((hist / "GRAMMAR_FROZEN.json").read_text(encoding="utf-8"))
    pk = json.loads((hist / "PACKET.json").read_text(encoding="utf-8"))
    runs, n_rows, dups = load_runs(hist)
    done = {k: r for k, r in runs.items() if r["status"] == "DONE"}

    # ---- 0. reconstruction check: the campaign's scorer over the preserved runs must give back the historical table
    fams0 = family_table(copy.deepcopy(runs))
    top0 = top(fams0)
    hist_top = [{"family": t["family"], "score": t["score"], "flags": sorted(t["flags"]), "runs": t["runs"], "best_run": t["best_run"]} for t in pk["top_families"]]
    recon_ok = top0 == hist_top
    if not recon_ok:
        print("STOP: INSTRUMENT_FAILURE -- family_table over RUNS.jsonl does not reproduce PACKET.top_families"); return 3

    # ---- 1. audit: the flagged runs, their construction, their founders' origin
    flagged = sorted((r for r in done.values() if r["signals"].get("spontaneous_replication")), key=lambda r: r["run_id"])
    assert len(flagged) == len(pk["spontaneous_runs"]) and {r["run_id"] for r in flagged} == set(pk["spontaneous_runs"])
    rows_by_id = defaultdict(list)
    for line in (hist / "RUNS.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if r["run_id"] in dups or (r.get("signals") or {}).get("spontaneous_replication"):
                rows_by_id[r["run_id"]].append(r)
    affected = []
    for r in flagged:
        sp = spec_of(hist, r); tr = sp.get("transplant")
        src = None
        if tr:
            srow = runs.get(tr["from_run"]); src_spec = spec_of(hist, srow) if srow else None
            src = {"run_id": tr["from_run"], "init": src_spec and src_spec["init"], "task": src_spec and src_spec["task"]["name"],
                   "topology": src_spec and src_spec["world"]["topology"], "reproduction": src_spec and src_spec["reproduction"]}
        reasons = [x["scheduler_reason"] for x in rows_by_id[r["run_id"]]]
        kinds = sorted({x.split(":", 2)[2] for x in reasons})
        vacuous_env = None
        if tr and src and any(k == "transplant:environment_swap" for k in kinds):
            vacuous_env = sp["task"]["name"] == src["task"]
        affected.append({"run_id": r["run_id"], "run_dir": "runs/" + r["run_dir"], "family": r["family"], "kind": r["kind"], "seed": r["seed"],
                         "scheduler_reasons": reasons, "verification_kinds": kinds, "spec_init_label": sp["init"], "transplant": bool(tr),
                         "transplanted_tapes": len(tr["tapes"]) if tr else 0, "random_founders": 0 if tr else None, "source": src,
                         "task": sp["task"]["name"], "topology": sp["world"]["topology"], "reproduction": sp["reproduction"],
                         "environment_swap_was_vacuous": vacuous_env,
                         "rows_in_runs_jsonl": len(rows_by_id[r["run_id"]]),
                         "duplicate_rows_identical_signals": len({json.dumps(x["signals"], sort_keys=True) for x in rows_by_id[r["run_id"]]}) == 1,
                         "legacy_signals": {k: r["signals"][k] for k in ("final_pop_frac", "births_endo", "fidelity_late", "best_ever", "task_max_final", "moat_crossed", "migrations", "extinct_epoch", "epochs")},
                         "corrected_spontaneous_replication": False if tr else "UNRESOLVED_REQUIRES_REPLAY",
                         "correction_basis": ("all %d founders were transplanted tapes (source %s, itself init=%s); a world with zero random founders cannot contain "
                                              "a random-only lineage, so the repaired predicate is false by construction" % (len(tr["tapes"]), tr["from_run"], src and src["init"])) if tr else None,
                         "reclassified_as": "transplanted_lineage_replication" if tr else None})
    kind_counts = Counter(k for x in affected for k in x["verification_kinds"])
    label_counts = Counter(x["scheduler_reasons"][-1].split(":", 2)[2] for x in affected)             # label the packet saw (last row wins)
    receipt = {
        "schema": "archaeon.z80atlas.postcampaign.audit_receipt.v1", "date": a.date, "campaign_grammar": grammar_frozen.get("digest", pk["grammar"]),
        "campaign_code_commit": CAMPAIGN_COMMIT, "inputs_sha256": inputs, "historical_dir": str(hist), "historical_records_modified": False,
        "code_paths": {
            "1_transplant_spec_constructor": git_line("archaeon/z80atlas/scheduler.py", 't["init"] = "random"'),
            "2a_transplant_branch_in_init": git_line("archaeon/z80atlas/engine.py", 'transplant = spec.get("transplant")'),
            "2b_transplanted_tape_injection": git_line("archaeon/z80atlas/engine.py", "genomes[i] = bytes.fromhex(tapes[i])"),
            "3_spontaneous_predicate": git_line("archaeon/z80atlas/engine.py", '"spontaneous_replication": bool(spec["init"] == "random"'),
            "4_flag_and_weight": git_line("archaeon/z80atlas/scheduler.py", 'if sig.get("spontaneous_replication")'),
        },
        "why_false": ("verify() builds each transplant spec from the source run's final population, puts those tapes in spec['transplant'] and sets "
                      "init='random' (1). run() fills cells from spec['transplant']['tapes'] and never draws a random tape in that branch (2a/2b), so every "
                      "founder is inserted material. The predicate tests only the nominal label spec['init']=='random' plus endogenous births, population "
                      "and fidelity (3); it has no access to founder origin, so a transplanted lineage that keeps replicating satisfies it. The flag then "
                      "scored +5 in the family table (4)."),
        "sources_all_seeded": all(x["source"] and x["source"]["init"] == "seeded_replicator" for x in affected),
        "affected_runs_n": len(affected), "runs_jsonl_rows_for_affected": sum(x["rows_in_runs_jsonl"] for x in affected),
        "verification_kind_counts_as_packet_labelled": dict(label_counts), "verification_kind_counts_all_rows": dict(kind_counts),
        "vacuous_environment_swaps": [x["run_id"] for x in affected if x["environment_swap_was_vacuous"]],
        "affected_runs": affected,
        "reconstruction": {"runs_jsonl_rows": n_rows, "unique_run_ids": len(runs), "done": len(done), "duplicate_run_ids": len(dups),
                           "family_table_reproduces_packet_top30": recon_ok},
    }

    # ---- 3B. corrected family scores
    runs1 = copy.deepcopy(runs)
    for x in affected:
        if x["corrected_spontaneous_replication"] is False:
            runs1[x["run_id"]]["signals"]["spontaneous_replication"] = False
    fams1 = family_table(runs1)
    orig_rank = {t["family"]: i + 1 for i, t in enumerate(top(fams0, n=len(fams0)))}
    corr_list = top(fams1, n=len(fams1)); corr_rank = {t["family"]: i + 1 for i, t in enumerate(corr_list)}

    def fam_row(fam):
        f0, f1 = fams0[fam], fams1[fam]
        return {"family": fam, "original_score": f0["best"], "corrected_score": f1["best"], "original_rank": orig_rank[fam], "corrected_rank": corr_rank[fam],
                "original_flags": sorted(f0["flags"]), "corrected_flags": sorted(f1["flags"]), "original_best_run": f0.get("best_run"), "corrected_best_run": f1.get("best_run"),
                "flags_removed": sorted(set(f0["flags"]) - set(f1["flags"])), "flags_added": sorted(set(f1["flags"]) - set(f0["flags"]))}
    changed = sorted({x["family"] for x in affected})
    rescoring = {"original_top30": [fam_row(t["family"]) for t in top(fams0)], "corrected_top30": [fam_row(t["family"]) for t in corr_list[:30]],
                 "named": {fam: fam_row(fam) for fam in NAMED}, "families_touched": {fam: fam_row(fam) for fam in changed},
                 "flag_totals_corrected": {"spontaneous_replication": sum(1 for r in runs1.values() if r["status"] == "DONE" and r["signals"].get("spontaneous_replication"))}}

    # ---- 3C. what the transplant runs genuinely establish (all transplant runs of every verified family, flagged or not)
    th = {"persist_pop_frac": F["spont_pop_frac"], "reproduce_births": F["spont_births"], "fidelity": F["spont_fid"], "competence": F["cross_score"]}
    transplant = defaultdict(dict)
    for r in sorted(done.values(), key=lambda r: r["run_id"]):
        if not r["scheduler_reason"].startswith("verify:") or ":transplant:" not in r["scheduler_reason"]:
            continue
        fam = r["scheduler_reason"].split(":")[1]; kind = r["scheduler_reason"].split(":", 2)[2]; s = r["signals"]; sp = spec_of(hist, r)
        src = runs.get(sp["transplant"]["from_run"]); ss = src["signals"] if src else {}
        endo = sp["reproduction"] in ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE", "PAIR_EXECUTION")
        transplant[fam][kind] = {
            "run_id": r["run_id"], "task": sp["task"]["name"], "source_task": src and src["factor_vector"]["task"], "topology": sp["world"]["topology"], "reproduction": sp["reproduction"],
            "vacuous": (kind == "transplant:environment_swap" and src is not None and sp["task"]["name"] == src["factor_vector"]["task"]),
            "persisted": s["extinct_epoch"] is None and s["final_pop_frac"] >= th["persist_pop_frac"], "final_pop_frac": s["final_pop_frac"], "extinct_epoch": s["extinct_epoch"],
            "reproduced_endogenously": endo and s["births_endo"] >= th["reproduce_births"], "births_endo": s["births_endo"], "fidelity_late": s["fidelity_late"],
            "task_competence_final": s["task_max_final"], "task_best_ever": s["best_ever"], "competence_retained": (s["task_max_final"] or 0) >= th["competence"],
            "source_best_ever": ss.get("best_ever"), "source_task_max_final": ss.get("task_max_final"), "moat_crossed": s["moat_crossed"],
            "legacy_spontaneous_label": bool(s.get("spontaneous_replication"))}

    # ---- 3D/E. regime tables over DONE runs, flags as the campaign's own scorer assigned them (corrected)
    def rate_table(rows, key):
        t = defaultdict(lambda: Counter())
        for r in rows:
            k = key(r)
            if k is None: continue
            fl = r.get("flags") or {}
            t[k]["runs"] += 1; t[k]["moat_crossed"] += bool(r["signals"].get("moat_crossed")); t[k]["moat_advantage"] += "moat_advantage" in fl
            t[k]["has_repro_control"] += r.get("_has_ctrl", False)
        return {k: dict(v, moat_crossed_rate=round(v["moat_crossed"] / v["runs"], 4), moat_advantage_rate=round(v["moat_advantage"] / v["runs"], 4)) for k, v in sorted(t.items())}
    for fam, f in fams1.items():                                           # mark which runs had a reproduction control to be compared with
        ctrl_tasks = {r2["factor_vector"]["task"] for r2 in f["specs"].values() if r2["scheduler_reason"].startswith("matched_control:reproduction")}
        for rid in f["runs"]:
            runs1[rid]["_has_ctrl"] = runs1[rid]["factor_vector"]["task"] in ctrl_tasks and not runs1[rid]["scheduler_reason"].startswith("matched_control:reproduction")
    d1 = [r for r in runs1.values() if r["status"] == "DONE"]
    expl = [r for r in d1 if r["kind"] == "exploration"]
    fv = lambda r: r["factor_vector"]
    niches_coupled = lambda r: fv(r)["world.migration"] != "none" or fv(r)["world.reservoir"] or fv(r)["world.env_dynamics"] in ("local_shift", "env_coevolve")
    topo = {
        "all_runs_by_topology": rate_table(d1, lambda r: fv(r)["world.topology"]),
        "exploration_runs_by_topology": rate_table(expl, lambda r: fv(r)["world.topology"]),
        "allocation_by_topology_and_kind": {t: dict(Counter(r["kind"] for r in d1 if fv(r)["world.topology"] == t)) for t in sorted({fv(r)["world.topology"] for r in d1})},
        "niches_split_by_coupled_features": rate_table([r for r in d1 if fv(r)["world.topology"] == "niches"], lambda r: "niches+coupled(migration|reservoir|local_shift|env_coevolve)" if niches_coupled(r) else "niches_bare(no migration, no reservoir, env fixed/nonstationary/env_mutate)"),
        "bare_comparison_all_topologies": rate_table([r for r in d1 if not niches_coupled(r)], lambda r: fv(r)["world.topology"]),
        "bare_comparison_exploration_only": rate_table([r for r in expl if not niches_coupled(r)], lambda r: fv(r)["world.topology"]),
        "moat_advantage_families_by_best_run_topology": dict(Counter(fv(runs1[f["best_run"]])["world.topology"] for f in fams1.values() if "moat_advantage" in f["flags"])),
        "niches_exploration_levels": {ax: dict(Counter(str(fv(r)[ax]) for r in expl if fv(r)["world.topology"] == "niches")) for ax in ("world.migration", "world.reservoir", "world.env_dynamics")},
        "sampler_note": ("grammar.random_spec weights each level by 1/(1+coverage); migration=none and reservoir=False are forced (and counted) in every "
                         "non-niches run, so a niches draw almost never selects them: the exploration sampler itself coupled topology to migration/reservoir"),
    }
    has_rec = lambda r: "recombination" in fv(r)["pressure"].split("+")
    # exact pairing: a treatment's reproduction control is a pure function of its spec (grammar.matched_controls), so it is
    # recomputed from the preserved SPEC rather than guessed from family membership
    ctrl_pairs = Counter(); spec_ids = {r["spec_id"] for r in d1}
    for r in d1:
        if not has_rec(r) or r["scheduler_reason"].startswith("matched_control"):
            continue
        sp = spec_of(hist, r); cs = [c for c in GR.matched_controls(sp, sp["stage"]) if c["scheduler_reason"] == "matched_control:reproduction"]
        ctrl_pairs["recombination_treatments"] += 1
        if not cs:
            ctrl_pairs["no_control_constructible"] += 1; continue
        c = cs[0]; cf = GR.factor_vector(c)
        ctrl_pairs["control_ran"] += c["spec_id"] in spec_ids
        ctrl_pairs["control_has_recombination"] += "recombination" in c["pressure"]
        ctrl_pairs["control_keeps_explicit_fitness"] += "explicit_fitness" in c["pressure"]
        ctrl_pairs["treatment_had_explicit_fitness"] += "explicit_fitness" in sp["pressure"]
        ctrl_pairs["control_reproduction_" + cf["reproduction"]] += 1
        ctrl_pairs["control_pressure_" + cf["pressure"]] += 1
    ext = [r for r in d1 if fv(r)["reproduction"] == "EXTERNAL"]
    recomb = {
        "grammar_constraint": [c[0] for c in GR.CONSTRAINTS if "recombination" in c[0]],
        "matched_control_rule": "grammar.matched_controls: flip_r = ENDOGENOUS_COPY for an EXTERNAL treatment; pressures explicit_fitness and recombination are dropped (-> implicit_survival if empty)",
        "treatment_control_pairs": dict(ctrl_pairs),
        "by_recombination_all": rate_table(d1, lambda r: "recombination" if has_rec(r) else "no_recombination"),
        "within_EXTERNAL_all": rate_table(ext, lambda r: "recombination" if has_rec(r) else "no_recombination"),
        "within_EXTERNAL_exploration_only": rate_table([r for r in ext if r["kind"] == "exploration"], lambda r: "recombination" if has_rec(r) else "no_recombination"),
        "by_reproduction_all": rate_table(d1, lambda r: fv(r)["reproduction"]),
    }

    # ---- F. same defect class, second signal: moat crossing is not provenance-qualified either. With init=seeded_replicator and
    # init_hybrid (grammar.make default True), the seeded tape is tasks.task_then_replicate = the hand-written task WITNESS + a
    # replicator, so a crossing can be the inserted witness scoring, not an evolved solution.
    def first_epoch(r):
        return min(v["epoch"] for v in r["signals"]["first_crossing"].values())
    wit = defaultdict(Counter)
    for r in d1:
        k = "%s|%s" % (fv(r)["init"], "task" if fv(r)["task"] != "none" else "task=none")
        wit[k]["runs"] += 1
        if r["signals"].get("moat_crossed"):
            e = first_epoch(r); wit[k]["crossed"] += 1; wit[k]["crossed_at_epoch0"] += e == 0; wit[k]["crossed_by_epoch5"] += e <= 5
    adv = Counter()
    for r in d1:
        if "moat_advantage" in (r.get("flags") or {}):
            e = first_epoch(r); adv["%s|%s" % (fv(r)["init"], "epoch0" if e == 0 else ("epoch1-5" if e <= 5 else "epoch>5"))] += 1
    hi = [f for f in fams1.values() if f["best"] >= 14]
    witness = {"moat_crossed_by_init": {k: dict(v) for k, v in sorted(wit.items())}, "moat_advantage_runs_by_init_and_first_crossing_epoch": dict(sorted(adv.items())),
               "families_scoring_14_by_best_run_init": dict(Counter(fv(runs1[f["best_run"]])["init"] for f in hi)), "families_scoring_14": len(hi),
               "moat_scoring_weight": {"moat_advantage": F["promotion_weights"]["moat_advantage"], "moat_crossed": F["promotion_weights"]["moat_crossed"]},
               "status": "CONFOUND_MEASURED_FROM_RECORDS; causal attribution per run requires instrumented replay (replays/REPLAY_*.json first_crossing provenance)"}

    # ---- G. the campaign's own de-novo denominator: random-init endogenous worlds that received no inserted material
    endo_phys = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE", "PAIR_EXECUTION")
    rnd = [r for r in d1 if fv(r)["init"] == "random" and fv(r)["reproduction"] in endo_phys and ":transplant:" not in r["scheduler_reason"]]
    ext_ep = sorted(r["signals"]["extinct_epoch"] for r in rnd if r["signals"]["extinct_epoch"] is not None)
    denovo = {"random_init_endogenous_runs_without_inserted_material": len(rnd), "by_reproduction": dict(Counter(fv(r)["reproduction"] for r in rnd)),
              "extinct": len(ext_ep), "median_extinct_epoch": ext_ep[len(ext_ep) // 2] if ext_ep else None, "max_extinct_epoch": ext_ep[-1] if ext_ep else None,
              "not_extinct": [{"run_id": r["run_id"], "run_dir": "runs/" + r["run_dir"], "factors": fv(r), **{k: r["signals"][k] for k in ("final_pop_frac", "births_endo", "fidelity_late", "epochs", "vm_steps", "lineages_final", "best_ever")}}
                              for r in rnd if r["signals"]["extinct_epoch"] is None],
              "legacy_label_fired_on_any": sum(1 for r in rnd if r["signals"].get("spontaneous_replication")),
              "max_births_endo_among_extinct": max((r["signals"]["births_endo"] for r in rnd if r["signals"]["extinct_epoch"] is not None), default=0)}

    adj = {"schema": "archaeon.z80atlas.postcampaign.adjudication.v1", "date": a.date, "inputs_sha256": inputs, "campaign_code_commit": CAMPAIGN_COMMIT,
           "historical_records_modified": False, "reconstruction_verified": recon_ok,
           "A_reclassification": {"verified_de_novo_spontaneous_replication": 0, "denominator_runs_done": len(done), "flagged_by_legacy_label": len(affected),
                                  "reclassified_transplanted_lineage_replication": sum(1 for x in affected if x["reclassified_as"]),
                                  "unresolved": [x["run_id"] for x in affected if x["corrected_spontaneous_replication"] != False],
                                  "runs": [{k: x[k] for k in ("run_id", "family", "verification_kinds", "task", "topology", "reproduction", "transplanted_tapes", "source", "environment_swap_was_vacuous", "reclassified_as")} for x in affected]},
           "B_rescoring": rescoring, "C_transplant": {"thresholds_frozen_grammar": th, "families": transplant},
           "D_topology": topo, "E_recombination": recomb, "F_seeded_witness_confound": witness, "G_denovo_denominator": denovo}
    out_r = HERE / ("AUDIT_RECEIPT_%s.json" % a.date); out_a = HERE / ("Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_%s.json" % a.date)
    out_r.write_text(json.dumps(receipt, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    out_a.write_text(json.dumps(adj, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"receipt": str(out_r), "adjudication": str(out_a), "reconstruction_verified": recon_ok, "affected": len(affected),
                      "named": {k: (v["original_score"], v["corrected_score"]) for k, v in rescoring["named"].items()}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
