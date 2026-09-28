"""Trace every pair interaction of the 11 T-003 runs (observation only) and export (v4 s3 + v5 R8).

Per run:
  _scratch/rows/<run>.jsonl.gz   one compact row per interaction (never committed: ~256k rows per run):
      iid (epoch, pair index, serial), oids, accepted sides (child oid), per half: n loci whose post-write-back label is
      ENTITY-other MOVE (copy-descent donor loci), ENTITY-self MOVE, written in this interaction, mutated
  exports/<run>.births.jsonl     one FULL record per birth (s3): pre-state (genomes, persisted registers/flags), per
      child locus data label + ctrl/addr/exec (at store and whole interaction) + performer + value + written, the victim
      window write log, mutation events with decode-dependence labels, birth-existence dependence, mechanism flags, the
      native lineage entry verbatim
  exports/<run>.summary.json     counts, P4 tallies, lineage_sha256 (must equal the pin's), shadow_checked

    python run_trace.py <job index 0..10> [--epochs N]
"""
from __future__ import annotations

import gzip
import hashlib
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "pin"))
import observe as O                                           # noqa: E402
import pin_reproduce as P                                     # noqa: E402
import z8shadow as S                                          # noqa: E402

OUT = HERE.parent / "exports"
ROWS = HERE.parent / "_scratch" / "rows"
SAMPLE_SEED = 20260928                      # the 1% agreement sample (Amendment C7.7): stated before any production run
SAMPLE_PERMILLE = 10


def in_sample(run_name: str, serial: int) -> bool:
    h = hashlib.sha256(("%d|%s|%d" % (SAMPLE_SEED, run_name, serial)).encode()).digest()
    return int.from_bytes(h[:4], "big") % 1000 < SAMPLE_PERMILLE


def diversity(final_labels, last_store, voff, n, donor_ent):
    """Painting / source-diversity guard (operator directive s6; C4.6). Written loci vs distinct causal sources,
    performers and instructions. Diagnostic only; never a decision rule."""
    import math
    from collections import Counter
    written = [j for j in range(n) if (voff + j) in last_store]
    src = Counter()
    perf, pcs, vals = set(), set(), set()
    for j in written:
        dl = final_labels[j][0]
        if dl[0] == "E":
            src[(dl[1], dl[2])] += 1
        st = last_store[voff + j]
        p_ = st.performer
        perf.add((p_[0], p_[1], p_[2]) if p_[0] == "E" else (p_[0],))
        pcs.add(st.pc)
        vals.add(st.val)
    tot = sum(src.values())
    hill = math.exp(-sum((c / tot) * math.log(c / tot) for c in src.values())) if tot else 0.0
    donor_src = Counter({k: v for k, v in src.items() if k[0] == donor_ent})
    return {"n_written": len(written), "n_entity_move": tot, "n_donor_move": sum(donor_src.values()),
            "n_distinct_sources": len(src), "n_distinct_donor_sources": len(donor_src),
            "top_source_share": round(max(src.values()) / tot, 4) if tot else None,
            "effective_sources_hill1": round(hill, 3), "n_distinct_performers": len(perf),
            "n_distinct_store_pcs": len(pcs), "n_distinct_values": len(vals),
            "source_multiplicity": sorted(src.values(), reverse=True)}


def lab_json(cell):
    return O.enc_label(cell[0])


def export_birth(runner, iid, pre_oid, orgs, gs, regs, flags, sh, last_store, post, e, n):
    a, b = orgs
    child = e["child"]
    vside = 0 if a.oid == child else 1
    dside = 1 - vside
    ent = {0: "a", 1: "b"}
    voff = 0 if vside == 0 else n
    final, new, events = post[vside]
    loci = []
    for j in range(n):
        st = last_store.get(voff + j)
        cell = final[j]
        rec = {"j": j, "value": new[j] if j < len(new) else 0, "label": O.enc_label(cell[0]),
               "written": st is not None}
        if st is not None:
            rec.update({"store_side": ent[st.side], "store_step": st.step, "store_pc": st.pc,
                        "performer": O.enc_label(st.performer),
                        "ctrl_at_store": O.enc_set(st.ctrl), "ctrl_slice_at_store": O.enc_set(st.ctrl_slice),
                        "exec_at_store": O.enc_set(st.exec_),
                        "addr": O.enc_set(st.cell[1])})
        loci.append(rec)
    wlog = [{"addr": s_.addr - voff, "value": s_.val, "side": ent[s_.side], "step": s_.step, "pc": s_.pc,
             "performer": O.enc_label(s_.performer), "label": O.enc_label(s_.cell[0])}
            for s_ in sh.stores if voff <= s_.addr < voff + n]
    pre_mut = runner._muts[vside][0]
    dec = []
    for ev in events:
        dec.append({"pos": ev["pos"], "call": ev["call"], "old": ev["old"], "new": ev["new"],
                    "decode_dep_labels": [O.enc_label(sh.lab[voff + p][0]) for p in ev["decode_dep_positions"]]})
    exist = set()
    for j in range(n):
        exist |= S.deps(sh.lab[voff + j])
    doff = 0 if dside == 0 else n
    for s_ in sh.stores:                                   # the harness counts the donor's writes OUTSIDE its own half
        if s_.side == dside and not (doff <= s_.addr < doff + n):
            exist |= s_.ctrl
    for side in (0, 1):
        off = 0 if side == 0 else n
        exist |= {("E", ent[side], i) for i in range(len(gs[side]))}
    return {
        "run": runner._run_name, "seed": runner.seed, "arm": runner._run_name.split("__")[-1],
        "iid": list(iid), "child": child, "victim_old_oid": pre_oid[vside],
        "diversity": diversity(final, last_store, voff, n, ent[dside]),
        "layers": {"L1_written": sum(1 for x in loci if x["written"]),
                   "L2_causally_by_donor": "interventions.py (R1 identified, donor-labelled loci)",
                   "L3_viable_offspring": "summary.children (child later a parent in the native lineage)",
                   "L4_survives_generations": "summary.children (descendant births, native lineage)",
                   "L5_inherited_machinery": "Q4 recert (Odysseus); construction is NOT heredity"},
        "donor_oid": pre_oid[dside], "victim_side": ent[vside], "donor_side": ent[dside], "n": n,
        "pre": {"ga": gs[0].hex(), "gb": gs[1].hex(), "regs_a": regs[0], "regs_b": regs[1],
                "flags_a": list(flags[0]), "flags_b": list(flags[1]), "budget": runner.t["slice"],
                "ops_mask": runner._ops_mask(), "tape_len": len(sh.mem)},
        "victim_pre": (gs[vside]).hex(), "victim_final_pre_mutation": pre_mut.hex(), "child_tape": bytes(new).hex(),
        "loci": loci, "window_write_log": wlog, "mutations": dec,
        "birth_existence_deps": O.enc_set(exist),
        "exec_whole_interaction": O.enc_set(sh.exec_all), "ctrl_whole_interaction": O.enc_set(sh.ctrl),
        "flags": {"budget_ended_a": sh.budget_ended.get(0), "budget_ended_b": sh.budget_ended.get(1),
                  "ldir_wrap": False, "in_window_source": any(
                      s_.cell[0][0] == "E" and s_.cell[0][1] == ent[vside] for s_ in sh.stores
                      if voff <= s_.addr < voff + n)},
        "native": e,
    }


def main():
    idx = int(sys.argv[1])
    ep = int(sys.argv[sys.argv.index("--epochs") + 1]) if "--epochs" in sys.argv else None
    jobs = P.job_list(O.Z, P.REPO / P.PATHS[2])
    job = jobs[idx]
    kw = dict(job["kwargs"]); kw.pop("implant_source", None); hx = kw.pop("implant_hex", None)
    if hx:
        kw["implant_bytes"] = bytes.fromhex(hx)
    if ep:
        kw["max_epochs"] = ep
    global OUT
    if ep is not None:                                        # smoke / validation runs never write into exports/
        OUT = HERE.parent / "_scratch" / "smoke"
    OUT.mkdir(parents=True, exist_ok=True)
    ROWS.mkdir(parents=True, exist_ok=True)
    tag = job["name"] + ("" if ep is None else "__ep%d" % ep)
    rows_f = gzip.open(ROWS / (tag + ".jsonl.gz"), "wt", encoding="utf-8")
    births_f = open(OUT / (tag + ".births.jsonl"), "w", encoding="utf-8", newline="\n")
    tally = {"interactions": 0, "births": 0, "p4_eligible_halves": 0, "p4_eligible_not_accepted": 0,
             "p4_eligible_accepted": 0, "accepted_halves": 0, "sampled": 0}
    sample_f = gzip.open(OUT / (tag + ".sample1pct.jsonl.gz"), "wt", encoding="utf-8")
    child_genomes = []

    def locus_rec(sh_last, post, side, j, n):
        a = (0 if side == 0 else n) + j
        cell = post[side][0][j]
        out = {"j": j, "label": O.enc_label(cell[0]), "addr": O.enc_set(cell[1])}
        st = sh_last.get(a)
        if st is None:
            out["written"] = False
        else:
            out.update({"written": True, "store_by": "ab"[st.side], "performer": O.enc_label(st.performer),
                        "ctrl": O.enc_set(st.ctrl), "ctrl_slice": O.enc_set(st.ctrl_slice),
                        "exec": O.enc_set(st.exec_)})
        return out

    def sink(runner, iid, pre_oid, orgs, gs, regs, flags, sh, last_store, post, births, n):
        a, b = orgs
        acc = {}
        for e in births:
            acc[0 if a.oid == e["child"] else 1] = e
        halves = []
        for side in (0, 1):
            other = "b" if side == 0 else "a"
            me = "a" if side == 0 else "b"
            off = 0 if side == 0 else n
            final = post[side][0]
            n_other = sum(1 for j in range(n) if final[j][0][0] == "E" and final[j][0][1] == other)
            n_self = sum(1 for j in range(n) if final[j][0][0] == "E" and final[j][0][1] == me)
            n_wr = sum(1 for j in range(n) if (off + j) in last_store)
            elig = n_other >= n / 2
            tally["p4_eligible_halves"] += elig
            if elig:
                tally["p4_eligible_accepted" if side in acc else "p4_eligible_not_accepted"] += 1
            halves.append([n_other, n_self, n_wr, len(post[side][2]), side in acc])
        tally["interactions"] += 1
        tally["accepted_halves"] += len(acc)
        if in_sample(runner._run_name, iid[2]):
            tally["sampled"] += 1
            st = runner._wb_state
            sample_f.write(json.dumps({
                "run": runner._run_name, "iid": list(iid), "oids": list(pre_oid),
                "pre": {"ga": gs[0].hex(), "gb": gs[1].hex(), "regs_a": regs[0], "regs_b": regs[1],
                        "flags_a": list(flags[0]), "flags_b": list(flags[1]), "budget": runner.t["slice"],
                        "ops_mask": runner._ops_mask(), "tape_len": len(sh.mem)},
                "rng_state_at_writeback": [st[0], list(st[1]), st[2]],
                "accepted_sides": sorted("ab"[k] for k in acc),
                "loci": {"ab"[side]: [locus_rec(last_store, post, side, j, n) for j in range(n)] for side in (0, 1)},
            }) + "\n")
        rows_f.write(json.dumps([list(iid), list(pre_oid), halves]) + "\n")
        for side, e in acc.items():
            tally["births"] += 1
            rec = export_birth(runner, iid, pre_oid, orgs, gs, regs, flags, sh, last_store, post, e, n)
            child_genomes.append({"child": rec["child"], "hex": rec["child_tape"]})
            births_f.write(json.dumps(rec, sort_keys=True) + "\n")

    t0 = time.time()
    r = O.Observed(job["cell"], job["seed"], tier=job["tier"], sink=sink, **kw)
    r._run_name = job["name"]
    r.run()
    rows_f.close()
    births_f.close()
    sample_f.close()
    # heredity layers L3/L4 from the native lineage (P-11 construction is NOT heredity; these are separate readings)
    kids = {}
    for e in r.lineage:
        if e.get("kind") == "birth":
            kids.setdefault(e["parent"], []).append(e["child"])
    children = {}
    for cg in child_genomes:
        c = cg["child"]
        direct = kids.get(c, [])
        seen, stack = set(), list(direct)
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(kids.get(x, []))
        children[str(c)] = {"L3_child_later_a_parent": bool(direct), "direct_offspring": len(direct),
                            "L4_descendant_births": len(seen)}
    lin = hashlib.sha256(json.dumps(r.lineage, sort_keys=True, default=str).encode()).hexdigest()
    summ = {"run": job["name"], "seed": job["seed"], "sim_id": lin[:16], "epochs": ep, "lineage_sha256": lin,
            "shadow_checked": r.shadow_checked, "sample_seed": SAMPLE_SEED, "sample_permille": SAMPLE_PERMILLE,
            "child_genomes_for_Q4": child_genomes, "children": children,
            "tally": tally, "wall_s": round(time.time() - t0, 1),
            "births_sha256": hashlib.sha256((OUT / (tag + ".births.jsonl")).read_bytes()).hexdigest()}
    (OUT / (tag + ".summary.json")).write_text(json.dumps(summ, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summ))


if __name__ == "__main__":
    main()
