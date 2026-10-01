"""W2-38 cross-context: genomes from checkpoint A screened (run_de rule) in realized register states drawn from
checkpoint B (donor and partner states both drawn from B's population). Separates 'genomes lost competence'
from 'the carried register environment moved'. python -B cross_context.py"""
import gzip, hashlib, json, random, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import rescreen as rs

def load(f):
    r = json.load(gzip.open(f, "rt")); return r, {d["epoch"]: d["orgs"] for d in r["dumps"]}

out = {}
for f, pairs in (("replay_ffa6_27000052.json.gz", [(1600, 1700), (1700, 1600), (1600, 1600), (1700, 1700)]),
                 ("replay_7ae3_27000008.json.gz", [(900, 1000), (1000, 900), (900, 900), (1000, 1000), (800, 1000)])):
    r, D = load(f); R = r["runner"]
    for ga_ep, st_ep in pairs:
        states = [rs.st_of(o) for o in D[st_ep]]
        sel = sorted(D[ga_ep], key=lambda o: hashlib.sha256(repr(("X", ga_ep, o["oid"])).encode()).digest())[:32]
        k = 0
        for o in sel:
            key = int(hashlib.sha256(repr((r["seed"], ga_ep, st_ep, o["oid"])).encode()).hexdigest()[:12], 16)
            draw = lambda i, s, salt: states[random.Random(key + 7919 * i + 104729 * s + salt).randrange(len(states))]
            ok, _ = rs.competent_ctx(R, bytes.fromhex(o["genome"]), lambda i, s: draw(i, s, 2), lambda i, s: draw(i, s, 3))
            k += ok
        out["%s g@%d states@%d" % (r["cell"], ga_ep, st_ep)] = "%d/32" % k
        print(r["cell"], "genomes@", ga_ep, "states@", st_ep, k, "/32", flush=True)
(pathlib.Path(__file__).resolve().parent / "cross_context.json").write_text(json.dumps(out, indent=1))
