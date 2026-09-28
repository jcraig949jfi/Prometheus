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
                        "ctrl_at_store": O.enc_set(st.ctrl), "exec_at_store": O.enc_set(st.exec_),
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
        "run": runner._run_name, "iid": list(iid), "child": child, "victim_old_oid": pre_oid[vside],
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
    OUT.mkdir(parents=True, exist_ok=True)
    ROWS.mkdir(parents=True, exist_ok=True)
    tag = job["name"] + ("" if ep is None else "__ep%d" % ep)
    rows_f = gzip.open(ROWS / (tag + ".jsonl.gz"), "wt", encoding="utf-8")
    births_f = open(OUT / (tag + ".births.jsonl"), "w", encoding="utf-8", newline="\n")
    tally = {"interactions": 0, "births": 0, "p4_eligible_halves": 0, "p4_eligible_not_accepted": 0,
             "p4_eligible_accepted": 0, "accepted_halves": 0}

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
        rows_f.write(json.dumps([list(iid), list(pre_oid), halves]) + "\n")
        for side, e in acc.items():
            tally["births"] += 1
            births_f.write(json.dumps(export_birth(runner, iid, pre_oid, orgs, gs, regs, flags, sh, last_store,
                                                   post, e, n), sort_keys=True) + "\n")

    t0 = time.time()
    r = O.Observed(job["cell"], job["seed"], tier=job["tier"], sink=sink, **kw)
    r._run_name = job["name"]
    r.run()
    rows_f.close()
    births_f.close()
    lin = hashlib.sha256(json.dumps(r.lineage, sort_keys=True, default=str).encode()).hexdigest()
    summ = {"run": job["name"], "epochs": ep, "lineage_sha256": lin, "shadow_checked": r.shadow_checked,
            "tally": tally, "wall_s": round(time.time() - t0, 1),
            "births_sha256": hashlib.sha256((OUT / (tag + ".births.jsonl")).read_bytes()).hexdigest()}
    (OUT / (tag + ".summary.json")).write_text(json.dumps(summ, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summ))


if __name__ == "__main__":
    main()
