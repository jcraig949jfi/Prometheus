"""G2 fresh-set run (Amendment C9 s5(d); seed record d33421a07; pre-states FRESH_SET_PRE.jsonl sha256 e37bdd48...).

Driver only: every label comes from the FROZEN v2 tracer (z8shadow / observe / interventions at fb1c322cb, TRACER_FREEZE
sha256 af5ec3da...). This file adds no tracer semantics.

Set A: the interaction, loci BEFORE write-back (as FUZZ_AGREEMENT_nestor.jsonl).
Set M: the same, then the write-back exactly as the frozen world does it for the T-003 cell:
  - rng = random.Random(wb_seed), in that state at the start of write-back; half a is mutated, then half b;
  - rate = the record's mut_rate;
  - VALUES come from the FROZEN world.Runner._mutate (called on a minimal stand-in carrying the cell, rate, rng, slot size);
  - LABELS come from the frozen observe.Observed._my_mutate on an identical RNG copy; bytes and the final RNG state are
    asserted equal to the frozen routine.
  - MUTATION encoding (v3, Amendment C10 s3(a)): label ["M", [side, k, pos], old_label]; k = RNG calls since the
    start of THIS interaction's write-back (a's half first), counted at the position's random() draw.
    Also exported explicitly: "mutation": {"side", "call", "pos", "old_label"}.

    python fresh_run.py <FRESH_SET_PRE.jsonl> <out.jsonl>
"""
import json, pathlib, random, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "pin"))
import interventions as I, observe as O, z8shadow as S          # noqa: E402
import world as W                                                # noqa: E402  (frozen)
import pin_reproduce as P                                        # noqa: E402

CELL = P.job_list(O.Z, P.REPO / P.PATHS[2])[0]["cell"]


class Stand:
    """Minimal stand-in exposing exactly what world.Runner._mutate and observe.Observed._my_mutate read."""

    def __init__(self, rate, rng):
        self.cell, self.mut_rate, self.rng, self.slot_size = CELL, rate, rng, 32

    def _boundaries(self, g):
        return W.Runner._boundaries(self, g)


def locus_rows(r, side, labels_override=None, mutated=None):
    off = 0 if side == 0 else 32
    rows = []
    for j in range(32):
        cell = labels_override[j] if labels_override else r.sh.lab[off + j]
        st = r.last.get(off + j)
        row = {"j": j, "label": O.enc_label(cell[0]), "addr": O.enc_set(cell[1]), "written": st is not None}
        if st is not None:
            row.update({"store_by": "ab"[st.side], "performer": O.enc_label(st.performer),
                        "ctrl": O.enc_set(st.ctrl), "ctrl_slice": O.enc_set(st.ctrl_slice), "exec": O.enc_set(st.exec_)})
        if mutated is not None:
            row["mutated"] = j in mutated
            if j in mutated:
                ev = mutated[j]
                row["mutation"] = {"side": "ab"[side], "k": ev["k"], "pos": j,
                                   "old_label": O.enc_label(r.sh.lab[off + j][0])}
        rows.append(row)
    return rows


def main():
    src, dst = sys.argv[1], sys.argv[2]
    out = open(dst, "w", encoding="utf-8", newline="\n")
    for line in open(src, encoding="utf-8"):
        d = json.loads(line)
        pre = d["pre"]
        p = I.Pre()
        p.n, p.size, p.budget, p.mask, p.vside = 32, pre["tape_len"], pre["budget"], pre["ops_mask"], 0
        p.g = {0: bytearray.fromhex(pre["ga"]), 1: bytearray.fromhex(pre["gb"])}
        p.regs = {0: pre["regs_a"], 1: pre["regs_b"]}
        p.flags = {0: tuple(pre["flags_a"]), 1: tuple(pre["flags_b"])}
        r = I.Run(p)
        rec = {"k": d["k"], "set": d["set"], "loci": {}}
        if d["set"] == "A":
            for side in (0, 1):
                rec["loci"]["ab"[side]] = locus_rows(r, side)
        else:
            rng_frozen = random.Random(d["wb_seed"])
            rng_mine = random.Random(d["wb_seed"])
            offset = 0
            for side in (0, 1):
                off = 0 if side == 0 else 32
                half = bytes(r.sh.mem[off:off + 32])
                new_frozen = W.Runner._mutate(Stand(d["mut_rate"], rng_frozen), half)
                stand = Stand(d["mut_rate"], rng_mine)
                new_mine, events = O.Observed._my_mutate(stand, half)
                if new_frozen != new_mine or rng_frozen.getstate() != rng_mine.getstate():
                    raise AssertionError("write-back replication differs from the frozen _mutate at k=%d" % d["k"])
                labels = [r.sh.lab[off + j] for j in range(32)]
                mutated = {}
                for ev in events:
                    labels[ev["pos"]] = (("M", ("ab"[side], offset + ev["rnd"], ev["pos"]), labels[ev["pos"]][0]),
                                         S.EMPTY)
                    mutated[ev["pos"]] = dict(ev, k=offset + ev["rnd"])
                rec["loci"]["ab"[side]] = locus_rows(r, side, labels, mutated)
                offset += stand._mutate_calls
                rec.setdefault("child_tape", {})["ab"[side]] = new_frozen.hex()
        out.write(json.dumps(rec, sort_keys=True) + "\n")
    out.close()
    print("ok")


if __name__ == "__main__":
    main()
