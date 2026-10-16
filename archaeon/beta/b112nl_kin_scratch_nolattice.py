"""B112-NL -- kin route FROM SCRATCH in the NO-LATTICE (jittered) world. Supersedes B112 (lattice), which would
replicate the copy-and-hash exploit (B113/B114) rather than test communication.

Design = B111 (random FOUNDRY_C2 gen 0, clonal 4-groups, c=0, E=8, G=300) with world = b114.jw() (pools jittered
[0,.3), order kept, residues mod 3 scrambled). Seeds 11211-11216.
Training-side value check (done before writing this): clonal COMPLETE .965 vs MUTE_OP .763 on training seed s, E=8.
Readout (fixed in advance): self-ablation drop > .05 on held-out jittered seeds s+1000..1003 x 16.
Instrument checks: COMPLETE and MUTE_OP drops re-scored in the same run.
SECOND READOUT (declared 17:40Z, after launch but BEFORE any cell result; see b115_info_readout.py): the self-ablation
drop measures dependence, not information (B111 11106). Every B112-NL best genome is ALSO scored with the B115
constant-twin info readout (info > .05); the prediction applies to both readouts.
PREDICTION (committed before running), no-from-scratch hypothesis (B104 0/12 under group reward; the only
from-scratch 'codes' so far were 1-instruction hash exploits): communicating <= 1/6.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b111_kin_scratch as B111
from archaeon.beta.b112_kin_scratch_rep import self_group
from archaeon.beta.b114_nolattice import jw

OUT = Path(__file__).resolve().parent / "results" / "B112NL_kin_scratch_nolattice"


def cell(job):
    B111.OUT = OUT; B111.sw = jw; r = B111.cell(job)
    w, s = jw(); m = json.loads((OUT / ("best_%d.json" % job["seed"])).read_text(encoding="utf-8"))
    a, b = self_group(m, w, s, False), self_group(m, w, s, True)
    r.update({"self_full": round(a, 4), "self_ablated": round(b, 4), "ablation_drop": round(a - b, 4), "communicating": a - b > .05})
    return r


def controls():
    import archaeon.beta.b92_signal_ladder as B92
    from archaeon.beta.b95_signal_restore import COMPLETE, MUTE_OP
    w, s = jw()
    return {k: round(self_group(B92.man(list(g)), w, s, False) - self_group(B92.man(list(g)), w, s, True), 4) for k, g in (("COMPLETE", COMPLETE), ("MUTE_OP", MUTE_OP))}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    ctl = controls(); print("controls", json.dumps(ctl), flush=True); rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 6) as ex:
        futs = {ex.submit(cell, {"seed": 11211 + i, "G": int(argv[0]) if argv else 300}): i for i in range(6)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 11211 + futs[fu], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B112NL_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    k = sum(r.get("communicating", False) for r in rows); summ = {"communicating": k, "n": len(rows), "pred": k <= 1, "controls": ctl}
    print(json.dumps(summ))
    (OUT / "B112NL_result.json").write_text(json.dumps({"probe": "B112NL", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
