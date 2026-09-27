"""B6 probe (read-only): replay ONE BEE run with Bellerophon's OWN traced VM (traced_replay._install / _traced_world_class, unmodified)
and, per birth, classify the CODE that performed each own-sourced copy write (src < L) by the MATERIAL at the code's location:
  own_region   pc < L                                         (the writer's own tape region)
  self_copied  pc >= L and that code byte was itself copied from the writer's own tape during this execution (last-writer map)
  foreign      pc in the window, never written by an own-sourced copy this execution (original occupant/partner bytes)
  elsewhere    any other pc
Does NOT call traced_replay._one (which writes into the preserved births directory). Output: JSON to argv[2]."""
import json, sys, time, os
sys.path.insert(0, os.path.dirname(__file__))
import traced_replay as TR

def main(rid, out):
    vm, W = TR._install(); TW = TR._traced_world_class(W)
    from prometheus.z80atlas import grammar as G
    cfg_j = json.load(open("C:/Users/James/z80atlas_campaign_2026-09-19/runs/%s/config.json" % rid, encoding="utf-8"))
    cfg = G.to_config(cfg_j["vec"], cfg_j["ticks"], cfg_j["cells"], cfg_j["budget"], tuple(cfg_j["init_tapes"] or ()))
    extra = []
    class P(TW):
        def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
            L = TR._ACC["L"]; ws = TR._ACC["writes"]; c = {"own_region": 0, "self_copied": 0, "foreign": 0, "elsewhere": 0}
            for a, (src, pc, op) in ws.items():
                if op not in TR.COPY_OPS or src is None or src >= L: continue
                if pc < L: c["own_region"] += 1
                elif L <= pc < 2 * L:
                    w = ws.get(pc - L)          # write-map keys are window OFFSETS (addr - WL, WL = L)
                    if w is not None and w[2] in TR.COPY_OPS and w[0] is not None and w[0] < L: c["self_copied"] += 1
                    else: c["foreign"] += 1
                else: c["elsewhere"] += 1
            extra.append(c)
            return super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
    t0 = time.time(); w = P(cfg, cfg_j["seed"]); w.run()
    json.dump({"rid": rid, "births": len(w.births), "wall_s": round(time.time() - t0, 1), "births_rows": w.births, "codeprov": extra}, open(out, "w", encoding="utf-8"))
    print(json.dumps({"rid": rid, "births": len(w.births), "wall_s": round(time.time() - t0, 1)}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
