"""E-003 production replay: run a preserved BEE run on the PINNED frozen harness with (a) traced_replay's native birth
rows (the generator of the preserved rows) and (b) this seat's shadow tracer on EVERY interaction. Observation only.

Per-organism persisted label vectors (v4 s1.2 "Persistence"): each locus carries an ORIGIN label that survives across
interactions, background mutation and migration:
- ("ORIG", org_id, i): an initial organism's random byte;
- ("NEW", tick, org_id, addr, kind): material created in an interaction (CONST / COMPUTED / COMPUTED_FROM / INPUT data
  label), with the creating interaction's writer;
- ("MUT", tick, seq): a background mutation at its RNG draw (never by diff). Each event records the old origin label and
  its decode-dependence set: the origin labels of the linear-decode opcode boundaries before the mutated position,
  which decide that the position is an opcode position under OPCODE mutation.
Within an interaction the tracer works on single-interaction ENTITY labels (E, W|P, locus). orig_id is the persisted
origin of that locus (v4 s1.2 "orig_id").

Checks:
- the native rows must equal the preserved births bit-for-bit;
- the tracer's post-interaction memory must equal the world's ACTUAL post-execution memory, on every interaction.

Output (gzip JSON lines, one per birth): the s3 fields computable from one pass, plus the pre-state needed to re-run
the interaction for the s4 tests (memory image hex, inputs, budget, orig vectors of writer and occupant).
    python traced_world.py --config <cfg.json> --births <preserved.jsonl.gz> --out <births_export.jsonl.gz> --receipt <r.json>
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import pathlib
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TOOLS = HERE.parents[1] / "forensics_2026-09-23" / "tools"
import bee_tracer as BT  # noqa: E402
import replay_births as RB  # noqa: E402

# ---- B-P1 performer-kind probe (Archaeon ruling #956): observation of the FROZEN tracer, no semantics added ------------
# The frozen tracer records performer = the ENTITY bases of the store opcode byte's label. Reading (B) needs to know
# whether that label was itself ENTITY (MOVE). Inside bee_tracer.trace's store(), the path event ("S", addr) is appended
# and the FIRST bases() call that follows is bases(perf_lab) (store(): ev append -> M[addr] = V(...) -> recs dict whose
# "performer" value calls bases(perf_lab); nothing in between calls bases). A list that arms on window stores plus a
# pass-through wrapper of bases() therefore captures perf_lab exactly. Every capture is ASSERTED to reproduce the
# performer set the tracer itself recorded; a mismatch stops the run.
_PROBE = {"armed": None, "last": {}, "L": 64}
_orig_bases = BT.bases


def _probed_bases(lab):
    a = _PROBE["armed"]
    if a is not None:
        _PROBE["last"][a] = lab; _PROBE["armed"] = None
    return _orig_bases(lab)


BT.bases = _probed_bases


class _ProbeEv(list):
    def append(self, e):
        super().append(e)
        if e[0] == "S" and _PROBE["L"] <= e[1] < 2 * _PROBE["L"]:
            _PROBE["armed"] = e[1]


def enc(lab):
    """compact JSON label encoding"""
    k = lab[0]
    if k == "E":
        return lab[1] + str(lab[2])
    if k == "INPUT":
        return "I%d" % lab[1]
    if k == "CONST":
        return "C:" + lab[1]
    if k == "COMPUTED":
        return {"COMPUTED": sorted(enc(b) for b in lab[1])}
    if k == "COMPUTED_FROM":
        return {"COMPUTED_FROM": enc(lab[1])}
    return list(lab)


def encset(s):
    return sorted(enc(b) for b in s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True); ap.add_argument("--births", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--receipt", required=True)
    ap.add_argument("--harness", default="C:/Users/James/e003_harness_16fc6c2a")
    a = ap.parse_args()
    harness = pathlib.Path(a.harness)
    if RB.pin_hashes(harness) != RB.PINS:
        raise SystemExit("harness pin mismatch")
    sys.path.insert(0, str(harness))
    from prometheus.z80atlas import vm as VM
    orig_execute = VM.execute                                      # the FROZEN execute, before traced_replay patches it
    vmshim = types.SimpleNamespace(**{k: getattr(VM, k) for k in dir(VM) if not k.startswith("_")})
    vmshim.execute = orig_execute
    sys.path.insert(0, str(TOOLS))
    import traced_replay as TR                                      # noqa: E402
    TR.HARNESS = str(harness)
    vm, W = TR._install()
    from prometheus.z80atlas import grammar as G
    cj = json.loads(pathlib.Path(a.config).read_text(encoding="utf-8"))
    cfg = G.to_config(cj["vec"], cj["ticks"], cj["cells"], cj["budget"], tuple(cj["init_tapes"] or ()))
    if cfg.layout != "SHARED" or cfg.reproduction != "ENDOGENOUS_COPY":
        raise SystemExit("this tracer handles the SHARED / ENDOGENOUS_COPY cell only")
    TW = TR._traced_world_class(W)
    out_fh = gzip.open(a.out, "wt", encoding="utf-8", newline="\n")
    stats = {"interactions": 0, "births": 0, "value_mismatch": 0, "mutations": 0, "pollinations": 0, "probe_checked": 0}

    class SW(TW):
        def __init__(self, cfg_, seed):
            self.vec = {}                                            # org id -> list of L origin labels
            self._last = None; self._mut_seq = 0; self.mut_events = []
            super().__init__(cfg_, seed)

        def _spawn(self, i, tape, parent, mechanism, lineage=None, glineage=None):
            o = super()._spawn(i, tape, parent, mechanism, lineage=lineage, glineage=glineage)
            if mechanism == "pollination":
                self.vec[o.id] = list(self.vec[parent]); stats["pollinations"] += 1   # world copy: labels carried positionally
            elif mechanism in ("init", "seed", "transplant"):
                self.vec[o.id] = [("ORIG", o.id, k) for k in range(self.L)]
            else:
                self.vec[o.id] = None                               # a birth: set in _register_offspring
            return o

        def _origin(self, lab, w_id, p_id, tick, addr):
            if lab[0] == "E":
                v = self.vec.get(w_id if lab[1] == "W" else p_id)
                return v[lab[2]] if v is not None else ("NEW", tick, w_id, addr, "EMPTY_PARTNER")
            return ("NEW", tick, w_id, addr, lab[0])

        def _execute(self, o, partner_tape, inputs):
            L = self.L
            # the partner by OBJECT identity of the tape step() passed (never call _partner(): it draws from the world rng)
            p = next((c for c in self.cells if c is not None and c.tape is partner_tape), None) if partner_tape is not None else None
            if partner_tape is not None and p is None:
                raise AssertionError("partner tape not found by identity at tick %d" % self.tick)
            pre = bytearray(256); pre[:L] = o.tape
            if partner_tape is not None:
                pre[L:2 * L] = partner_tape
            for k, v in enumerate(inputs[:16]):
                pre[vm.IN_BASE + k] = v
            labels = BT.initial_labels(L, len(inputs[:16]), vm.IN_BASE)
            if partner_tape is None:                                  # v4 s1.2: EMPTY is FOREIGN-STRUCTURAL (CONSTANT, kind)
                for a_ in range(L, 2 * L):
                    labels[a_] = ("CONST", "empty")
            _PROBE["L"] = L; _PROBE["last"] = {}; _PROBE["armed"] = None
            after, recs, info = BT.trace(vmshim, pre, L, self.cfg.budget, list(inputs), allow_copyall=self.cfg.allow_copyall,
                                         labels=labels, check=False, ev=_ProbeEv())
            perf_kind = {}
            for k_ in range(L):
                if recs[k_]["written"]:
                    pl = _PROBE["last"].get(L + k_)
                    if pl is None or frozenset(b for b in _orig_bases(pl) if b[0] == "E") != recs[k_]["performer"]:
                        raise AssertionError("B-P1 probe does not reproduce the tracer's performer at tick %d locus %d" % (self.tick, k_))
                    perf_kind[k_] = pl[0]
                    stats["probe_checked"] += 1
            mem, tr = super()._execute(o, partner_tape, inputs)
            stats["interactions"] += 1
            if bytes(mem) != bytes(after):
                stats["value_mismatch"] += 1
                raise AssertionError("tracer != world execution at tick %d org %d" % (self.tick, o.id))
            labs = info["labels_after"]; pid = p.id if p is not None else None
            prev_w = list(self.vec[o.id])
            self._last = {"pre": bytes(pre).hex(), "inputs": list(inputs), "writer": o.id, "occupant": pid, "recs": recs, "info": info,
                          "perf_kind": perf_kind,
                          "vec_w": prev_w, "vec_p": list(self.vec[pid]) if pid is not None else None, "labs": labs}
            self.vec[o.id] = [self._origin(labs[k], o.id, pid, self.tick, k) for k in range(L)]
            return mem, tr

        def _mutate(self, tape, rate):
            """frozen OPCODE-path _mutate, line for line, plus recording (identical rng consumption)"""
            cfg = self.cfg
            if cfg.mutation != "OPCODE":
                raise SystemExit("recording _mutate implemented for OPCODE only")
            org = next(o for o in self.cells if o is not None and o.tape is tape)
            L = len(tape); changes = 0
            positions = list(range(L))
            ops_list = self._opcode_positions(tape); ops = set(ops_list)
            positions = [p for p in range(L) if (p in ops) == (cfg.mutation == "OPCODE")] or positions
            for p in positions:
                if self.rng.random() < rate:
                    old = self.vec[org.id][p]
                    tape[p] = self.rng.randrange(256)
                    self._mut_seq += 1; changes += 1; stats["mutations"] += 1
                    dd = [self.vec[org.id][q] for q in ops_list if q < p]
                    self.mut_events.append({"tick": self.tick, "seq": self._mut_seq, "org": org.id, "pos": p, "old": old, "decode_dep": dd})
                    self.vec[org.id][p] = ("MUT", self.tick, self._mut_seq)
            return changes

        def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
            last = self._last; L = self.L
            n_before = len(self.births)
            super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
            cid = self.next_id - 1
            labs = last["labs"]
            self.vec[cid] = [self._origin(labs[L + k], last["writer"], last["occupant"], self.tick, L + k) for k in range(L)]
            recs = last["recs"]; info = last["info"]
            loci = []
            for k in range(L):
                r = recs[k]
                loci.append({"data": enc(r["data"]), "written": r["written"], "ctrl": encset(r["ctrl"]), "addr": encset(r["addr"]),
                             "exec": encset(r["exec"]), "performer": encset(r["performer"]),
                             "perf_kind": last["perf_kind"].get(k),
                             "orig": list(self.vec[cid][k])})
            rec = {"birth_index": n_before, "tick": self.tick, "writer": parent.id, "child": cid, "occupant": last["occupant"],
                   "native_row": self.births[n_before], "pre_state": {"mem": last["pre"], "inputs": last["inputs"], "entry": 0,
                   "budget": self.cfg.budget, "allow_copyall": self.cfg.allow_copyall, "window_empty": last["occupant"] is None},
                   "writer_pre": last["pre"][:2 * L], "writer_post": bytes(parent.tape).hex(), "child_tape": bytes(child).hex(),
                   "occupant_tape": last["pre"][2 * L:4 * L] if last["occupant"] is not None else None,
                   "vec_writer_pre": [list(x) for x in last["vec_w"]], "vec_occupant_pre": [list(x) for x in last["vec_p"]] if last["vec_p"] else None,
                   "birth_existence_deps": ("occupant full tape (n_written >= L and child != occupant)" if last["occupant"] is not None
                                            else "n_written >= L (empty target)"),
                   "flags": {k: info[k] for k in ("ldir_c0_entered", "in_window_source", "budget_ended", "halted", "steps")},
                   "exec_whole": encset(info["exec_whole"]), "pc_label_end": encset(info["pc_label_end"]), "loci": loci}
            out_fh.write(json.dumps(rec, sort_keys=True) + "\n")
            stats["births"] += 1

    w = SW(cfg, cj["seed"])
    w.run()
    out_fh.close()
    got = [json.loads(json.dumps(b)) for b in w.births]
    want = [json.loads(l) for l in gzip.open(a.births, "rt", encoding="utf-8")]
    ok = got == want
    mut_p = pathlib.Path(a.out).with_name(pathlib.Path(a.out).name.replace("births", "mutations"))
    with gzip.open(mut_p, "wt", encoding="utf-8", newline="\n") as fh:
        for e in w.mut_events:
            fh.write(json.dumps(e, sort_keys=True) + "\n")
    rec = {"run": cj["id"], "harness_pins": RB.pin_hashes(harness), "native_rows_bit_for_bit": ok, **stats,
           "tracer_sha256": hashlib.sha256((HERE / "bee_tracer.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
           "export": str(a.out), "export_sha256": hashlib.sha256(pathlib.Path(a.out).read_bytes()).hexdigest(),
           "mutations_export": str(mut_p), "mutations_sha256": hashlib.sha256(mut_p.read_bytes()).hexdigest()}
    pathlib.Path(a.receipt).write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if ok and stats["value_mismatch"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
