"""Fresh scoring (namespace W2JS = 0x57324A53, disjoint from DEV W2JD and from C1/C1b/H-PLANT/W2-B namespaces).
For each (cell8, fam, opts, tier): normal on 64 worlds (32 mirror pairs), must-fail (sensor-2 cue zeroed) on
the first 32 of those worlds, and the NOR one-flag cheat (same flood, readout '+ iff no + flag') on 64.
CPU, eager (hc.evaluate). usage: python score.py 'json list' tag [nomf] [nocheat]"""
import sys, time
from wj_common import *
import plants_wj as pw
from screen2 import build
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics


def zero_s2(ep):
    ep.schedule.sense_val[:, :, 1] = 0


def main():
    t0 = time.process_time()
    todo = json.loads(sys.argv[1]); tag = sys.argv[2]
    flags = set(sys.argv[3:])
    seeds = assays.world_seeds(WJ_NS, 64)
    rows = {r["cell_id"][:8]: r for r in xor_evolve()}
    out = []
    for c8, fam, o, tier in todo:
        r = rows[c8]
        ph0 = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
        lines, ev, f2 = build(ph0, env, fam, o)
        ph, ov = pw.fit(ph0, lines, ev, f2, strict=False)
        g = pw.genome(ph, lines)
        rec = {"cell": r["cell_id"], "fam": fam, "opts": o, "tier": tier, "len": len(lines), "override": ov,
               "program": hc.decompile(ph, g[0])}
        e = hc.evaluate(ph, g, env, seeds); rec["normal"] = e
        if "nomf" not in flags:
            e2 = hc.evaluate(ph, g, env, seeds[:32], sched_fn=zero_s2); rec["mf_s2_zeroed"] = e2
        if "nocheat" not in flags:
            lc_, ev_, f2_ = build(ph0, env, fam, o, readout="nor")
            phc, _ = pw.fit(ph0, lc_, ev_, f2_, strict=False)
            phc = phc.replace(prog_len=ph.prog_len) if phc.prog_len < ph.prog_len else phc
            e3 = hc.evaluate(phc, pw.genome(phc, lc_), env, seeds); rec["nor_cheat"] = e3
        out.append(rec)
        msg = f"{c8} {fam} {o} {tier} len={len(lines)} ov={ov} normal {e['acc']:.3f} [{e['lo99']:.3f},{e['hi99']:.3f}]"
        if "mf_s2_zeroed" in rec:
            msg += f" mf {rec['mf_s2_zeroed']['acc']:.3f}"
        if "nor_cheat" in rec:
            msg += f" nor {rec['nor_cheat']['acc']:.3f} [{rec['nor_cheat']['lo99']:.3f}]"
        print(msg, f"cpu {time.process_time() - t0:.0f}", flush=True)
    save(f"score_{tag}.json", {"rows": out, "cpu_s": time.process_time() - t0, "ns": WJ_NS, "M": 64})
    print("cpu_s", time.process_time() - t0)


if __name__ == "__main__":
    main()
