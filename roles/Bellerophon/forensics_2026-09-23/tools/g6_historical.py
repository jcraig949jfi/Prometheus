"""G6 historical (exploratory): how did each historical origin's first self-replicating writer come to exist?
From the traced birth logs (LOCAL births/<run>.jsonl.gz; row fields per traced_replay.py). Classes:
  INIT_AT_TICK0      the writer is an initial organism and self-replicated at tick 0 (a cliff present at init)
  INIT_LATER         the writer is an initial organism that first self-replicated later (background mutation of an
                     init tape or context change; the historical logs hold no per-tick tapes to separate these)
  BUILT_BY_COPY      the writer was itself born by a registered non-SR COPY_EVENT (constructed by another's writes);
                     the class of that construction (material target = capture/chimera, writer = partial copy)
Ancestor TAPES were not recorded historically, so the RAMP test is left to the grounding round (G6).
Writes receipts/G6_HISTORICAL.json."""
import collections, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import load as Ld

def main():
    out = collections.Counter(); built = collections.Counter(); rows = []
    for tag in ("spontaneous", "baseline"):
        for r in json.loads((Ld.OUT / ("TRACED_%s.json" % tag)).read_text(encoding="utf-8"))["rows"]:
            if r["intervention"] or r["self_rep"] == 0 or r["vec"]["init"] != "RANDOM":
                continue
            fsr = r["first_self_rep"]; w = fsr["writer"]
            born = None
            with gzip.open(Ld.LOCAL / "births" / (r["run"] + ".jsonl.gz"), "rt", encoding="utf-8") as fh:
                for line in fh:
                    b = json.loads(line)
                    if b[2] == w:
                        born = b; break
            if born is None:
                cls = "INIT_AT_TICK0" if fsr["tick"] == 0 else "INIT_LATER"
            else:
                cls = "BUILT_BY_COPY"; built["material=%s,changed<=2=%s,into_empty=%s" % (born[6], born[10] <= 2, bool(born[19]))] += 1
            out[cls] += 1
            rows.append({"run": r["run"], "set": tag, "class": cls, "first_sr_tick": fsr["tick"], "writer_birth": born[0] if born else None})
    res = {"definition": __doc__, "classes": dict(out), "built_by_copy_detail": dict(built), "n": sum(out.values()), "rows": rows}
    print(Ld.write("G6_HISTORICAL.json", res)); print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "definition")}, indent=1))

main()
