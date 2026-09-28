"""Review 6, step 1: replay r025144 on the FROZEN harness (git 16fc6c2a, extracted to ./scratch) using the
Bellerophon traced_replay tracer, compare the 20-column birth rows with the preserved r025144.births.jsonl.gz,
and capture each birth interaction's PRE-EXECUTION state (writer tape, occupant tape or None, inputs) to
r6_births_pre.json for step 2. Nothing in the world is changed; the capture is observation-only."""
import gzip, json, os, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.expanduser("~/Prometheus-worktrees/rev6")
ARC = os.path.join(REPO, "ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28")
sys.path.insert(0, os.path.join(REPO, "roles/Bellerophon/forensics_2026-09-23/tools"))
import traced_replay as T  # noqa
T.HARNESS = os.path.join(HERE, "scratch")
vm, W = T._install()
assert os.path.dirname(vm.__file__) == os.path.join(HERE, "scratch/prometheus/z80atlas"), vm.__file__
for f, h in (("world", "5b985241"), ("vm", "2536b1ac"), ("grammar", "3767d73d"), ("tasks", "e2c37f76")):
    assert hashlib.sha256(open(os.path.join(HERE, "scratch/prometheus/z80atlas/%s.py" % f), "rb").read()).hexdigest().startswith(h), f
from prometheus.z80atlas import grammar as G
TW = T._traced_world_class(W)
PRE = []


class CW(TW):
    def _execute(self, o, partner_tape, inputs):
        self._pre = (bytes(o.tape).hex(), None if partner_tape is None else bytes(partner_tape).hex(), list(inputs), self.tick, o.id)
        return super()._execute(o, partner_tape, inputs)

    def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
        wt, pt, inp, tick, oid = self._pre
        assert oid == parent.id and tick == self.tick
        PRE.append({"tick": tick, "writer": oid, "writer_tape": wt, "occ_tape": pt, "inputs": inp, "child": bytes(child).hex(),
                    "occ_id": None if replaced is None else replaced.id})
        return super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)


cj = json.load(open(os.path.join(ARC, "r025144.config.json")))
c = cj["config"]
cfg = G.to_config({a: c[a] for a in G.AXES}, c["ticks"], c["cells"], c["budget"], tuple(c["init_tapes"] or ()))
w = CW(cfg, cj["seed"])
summ = w.run()
got = [json.loads(json.dumps(b)) for b in w.births]
want = [json.loads(l) for l in gzip.open(os.path.join(ARC, "r025144.births.jsonl.gz"), "rt")]
print("births replayed", len(got), "preserved", len(want), "identical rows", sum(a == b for a, b in zip(got, want)),
      "ALL EQUAL" if got == want else "DIFFER")
for k, (a, b) in enumerate(zip(got, want)):
    if a != b:
        print("first diff", k, a, b); break
print("endogenous_births", summ.get("endogenous_births"), "captures", summ.get("captures"), "null_rewrites", summ.get("null_rewrites"))
for p, b in zip(PRE, got):
    p["row"] = b
json.dump(PRE, open(os.path.join(HERE, "r6_births_pre.json"), "w"))
print("wrote", len(PRE), "pre-states")
