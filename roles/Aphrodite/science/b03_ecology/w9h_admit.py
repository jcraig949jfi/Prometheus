"""W9-H admission + depth-two certification (Beta-03 E4). OUTCOME-FREE: no treatment library is ever walked here.

Admission (per family; `foundry`):
  A1 valid executable witness           generator: accumulating + T4 task-side profile (w9h_grammar.supply)
  A2 Q2 qualification                   a18_c1.qualify_family (exact-fast Q2, unchanged)
  A3 tribunal coverage                  T4 v1 on the witness artifact (qualify_family), i.e. as in T51/b02
  A4 pristine reachability, measured    p_PRISTINE: 4 dev cells at escrow 30k (qualify_family);
                                        R_PRISTINE_1M: 2 transfer cells at cap 1,000,000 (walk to first T4-v1a-
                                        qualified program, as the v2b D endpoint)
  A5 entropy independence               dev-cell and transfer-cell example sets come from distinct seed labels and
                                        share no prompt (checked, not assumed)
  A6 learning opportunity (post-hoc, from generator truth only):
        L1  its mechanism has >= 3 T4-qualified level-1 families in the seed
        L2  inner and outer mechanisms each have >= 2 T4-qualified level-1 families, and the composition has >= 2
            T4-qualified level-2 families in the seed
        all p_PRISTINE <= 0.75 (the A19 window ceiling)
        L0  background: A2-A5 + window only
Certification (`certify`; the KNOWN-POSITIVE SENSITIVITY CONTROL; by EXPANSION, see W9H_DESIGN.md s5):
  For a level-2 family with witness body S_b[H := S_a[H := e]], walk these libraries on the same cells (common
  random numbers):
    PRISTINE         FR.pristine()
    FLAT             every seed mechanism as an ordinary (unpromoted) W5 schema entry, then PRISTINE
    PROMOTED_A       P_a := S_a promoted: entries S_x o P_a (expanded over LEVEL1 fillers, not limited to W5) for
                     EVERY seed mechanism x, then FLAT, then PRISTINE -- the library knows the right primitive but
                     not which outer mechanism uses it
    PROMOTED_ORACLE  the single entry S_b o P_a, then FLAT, then PRISTINE (attainability given the right depth-2
                     schema)
    SHAM_C           as PROMOTED_A with a WRONG inner primitive P_c (c != a, seeded) -- specificity control
  Budgets: 4 cells at 30k (dev label) and 2 cells at 1,000,000 (transfer label). Endpoint: first program the T4 v1a
  qualifier (DIRECT, positives confirmed by ARTIFACT) accepts. Every qualified program is also checked for
  behavioural equality with the witness (identity.behavior_id on B1 + audit_id on B2): a qualified program that is
  not equal is a tribunal FALSE POSITIVE; a dev-consistent program the tribunal rejects but that IS equal is a
  FALSE NEGATIVE.
  CERTIFIED_DEPTH2 iff admitted and PROMOTED_A reaches at 1M in >= 1 of 2 cells and PRISTINE reaches in 0 of 2.
  For level-1 families the same machinery runs PRISTINE vs FLAT_A (the correct mechanism as a flat schema).

Usage: python w9h_admit.py foundry|certify|report <pilot_dir> [workers]
"""
import hashlib
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w9h_grammar as W  # noqa: E402  (sets sys.path + fast-path flags)
import a17  # noqa: E402
import fair  # noqa: E402

ESC = 30_000
CAP = 1_000_000
a17.ESCROW = ESC
fair.ESCROW = ESC
import a18  # noqa: E402
import a18_c1 as C  # noqa: E402
from a18 import FR, G, T3D, I  # noqa: E402

DEV_CELLS, TX_CELLS = 4, 2
DEV_LABEL, TX_LABEL = "W9H-cert-dev", "W9H-tx"
MAX_SPURIOUS = 300
WINDOW = 0.75


def init_worker():
    a17.ESCROW = ESC
    fair.ESCROW = ESC
    W.init()


def log(m):
    print("[W9H-ADM %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def rdl(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


# ------------------------------------------------------------------ libraries (entries are DATA)
def expand(schema):
    """Instantiations of a one-hole schema over every LEVEL1 filler, W5-canonical where in W5, raw otherwise (the
    expansion of a promoted-primitive body into the base DSL)."""
    return list(dict.fromkeys(W.canon(W.fill(schema, f))[0] for f in FR.LEVEL1))


def _hkey(s):
    return hashlib.sha256(("APHRODITE/W9H/ENTRY-ORDER/v1/" + s).encode()).hexdigest()


def promoted_entry(schema, tag):
    return {"name": tag, "inits": list(G.H1_SPACE), "bodies": expand(schema), "finals": list(G.FINAL_SPACE),
            "schema_expanded": schema}


def flat_entries(mechs):
    return [a17.schema_entry("flat_%s" % m["id"], m["schema"]) for m in sorted(mechs, key=lambda m: _hkey(m["schema"]))]


def promoted_entries(mechs, inner):
    """Entries S_x o P_inner for every seed mechanism x (entry order: hash of the composite schema, arm-blind)."""
    comps = sorted({W.compose(m["schema"], inner["schema"]) for m in mechs}, key=_hkey)
    return [promoted_entry(s, "promoted_%d" % i) for i, s in enumerate(comps)]


def libraries_l2(truth, comp, sham_inner):
    mechs = {m["id"]: m for m in truth["mechanisms"]}
    ml = truth["mechanisms"]
    pr = FR.pristine().entries
    flat = flat_entries(ml)
    return {
        "PRISTINE": pr,
        "FLAT": flat + pr,
        "PROMOTED_A": promoted_entries(ml, mechs[comp["inner"]]) + flat + pr,
        "PROMOTED_ORACLE": [promoted_entry(comp["schema"], "promoted_oracle")] + flat + pr,
        "SHAM_C": promoted_entries(ml, mechs[sham_inner]) + flat + pr,
    }


def libraries_l1(truth, mech_id):
    m = {x["id"]: x for x in truth["mechanisms"]}[mech_id]
    pr = FR.pristine().entries
    return {"PRISTINE": pr, "FLAT_A": [a17.schema_entry("flat_" + mech_id, m["schema"])] + pr}


# ------------------------------------------------------------------ walking with FP/FN accounting
_BID, _AID = {}, {}


def _bid(prog):
    k = tuple(prog)
    if k not in _BID:
        _BID[k] = I.behavior_id(k, True)
    return _BID[k]


def _aid(prog):
    k = tuple(prog)
    if k not in _AID:
        _AID[k] = I.audit_id(k, True)
    return _AID[k]


def walk_cell(lib, cell, cap, prov, name):
    """As walk.first_qualified (same traversal + charges) but also classifies every dev-consistent program the
    tribunal REJECTS (true negative vs false negative) and the qualified one (true vs false positive)."""
    import walk
    import instruments as INS
    q = INS.qualifier(prov, name, "v1a", "BOTH")
    wit = prov.witness(name)
    out = {"charge": cap, "censored": True, "spurious": 0, "fn": 0, "program": None}
    for ch, prog in walk.iter_hits(lib, cell, cap):
        if q(prog):
            out.update({"charge": ch, "censored": False, "program": list(prog),
                        "equal_B1": _bid(prog) == _bid(wit), "equal_B2": _aid(prog) == _aid(wit)})
            return out
        out["spurious"] += 1
        if _bid(prog) == _bid(wit):
            out["fn"] += 1
        if out["spurious"] >= MAX_SPURIOUS:
            out.update({"charge": ch, "stopped": "max_spurious"})
            return out
    return out


def cells_for(prov, name, size):
    dev = [FR.Cell(prov, name, i, size, label=DEV_LABEL) for i in range(DEV_CELLS)]
    tx = [FR.Cell(prov, name, i, size, label=TX_LABEL) for i in range(TX_CELLS)]
    return dev, tx


def run_libs(libs, prov, name, size):
    dev, tx = cells_for(prov, name, size)
    res = {}
    for k, ents in libs.items():
        lib = FR.KLib(ents)
        res[k] = {"dev": [walk_cell(lib, c, ESC, prov, name) for c in dev],
                  "tx": [walk_cell(lib, c, CAP, prov, name) for c in tx]}
    return res


# ------------------------------------------------------------------ foundry
def _foundry_job(d):
    init_worker()
    name, body, init, final, src = d
    t0 = time.time()
    row = C.qualify_family((name, body, init, final, src))
    if row.get("T4_qualified"):
        prov = a17.Prov({name: (body, final, init)})
        a17.M.use_provider(prov)
        dev, tx = cells_for(prov, name, row["Q2_size"])
        # A5: entropy independence of the dev and transfer example sets (and of the qualify_family pilot cells)
        pilot = FR.Cell(prov, name, 0, row["Q2_size"], label="%s-pilot-PRISTINE" % a18.TAG)
        sets = [set(t["prompt"] for t in c.examples) for c in [pilot] + dev + tx]
        row["entropy_independent"] = all(not (sets[i] & sets[j]) for i in range(len(sets))
                                         for j in range(i + 1, len(sets)))
        row["tx_seeds_distinct"] = len({c.seed for c in dev + tx + [pilot]}) == len(dev + tx) + 1
        lib = FR.KLib(FR.pristine().entries)
        row["PRISTINE_TX"] = [walk_cell(lib, c, CAP, prov, name) for c in tx]
    row["seconds"] = round(time.time() - t0, 1)
    return row


def stage_foundry(pdir, workers=2):
    sups = json.loads((pdir / "W9H_SUPPLIES.json").read_text())
    draws = [(n, b, i, f, k) for k in sorted(sups) for n, i, b, f in sups[k]["families"]]
    fp = pdir / "W9H_FOUNDRY.jsonl"
    done = {r["name"] for r in rdl(fp)}
    todo = [d for d in draws if d[0] not in done]
    log("foundry todo %d of %d" % (len(todo), len(draws)))
    with open(fp, "a", encoding="utf-8") as fh, ProcessPoolExecutor(workers, initializer=init_worker) as ex:
        for i, row in enumerate(ex.map(_foundry_job, todo, chunksize=2)):
            fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
            fh.flush()
            if i % 10 == 0:
                log("foundry %d/%d (%ss)" % (i + 1, len(todo), row["seconds"]))


# ------------------------------------------------------------------ admission (post-foundry, truth-only)
def admit(rows, truths):
    """Returns {name: record} with level, source, admitted flag and the failing criterion. Uses generator truth and
    foundry rows only (never a treatment outcome)."""
    by = {r["name"]: r for r in rows}
    out = {}
    for key, tr in truths.items():
        fam = tr["families"]
        q = {n: by[n] for n in fam if n in by and by[n].get("T4_qualified")}
        nq = Counter(fam[n].get("src") for n in q)
        comp = {c["id"]: c for c in tr["compositions"]}
        for n, meta in fam.items():
            r = by.get(n)
            rec = {"seed": key, "level": meta["level"], "src": meta.get("src"), "in_W5": meta.get("in_W5", True)}
            why = None
            if r is None:
                why = "NOT_RUN"
            elif r.get("Q2_size") is None:
                why = "Q2"
            elif not r.get("T4_qualified"):
                why = "T4"
            elif not r.get("entropy_independent", False):
                why = "ENTROPY"
            elif r.get("p_PRISTINE", 0) > WINDOW:
                why = "WINDOW"
            elif meta["level"] == "L1" and nq[meta["src"]] < 3:
                why = "L1_RECURRENCE"
            elif meta["level"] == "L2":
                c = comp[meta["src"]]
                if nq[c["inner"]] < 2 or nq[c["outer"]] < 2 or nq[meta["src"]] < 2:
                    why = "L2_RECURRENCE"
            rec.update({"admitted": why is None, "why_not": why})
            out[n] = rec
    return out


# ------------------------------------------------------------------ certification
def certify_family(args):
    """The coordinator-callable certification of ONE level-2 (or level-1) family. args = (row, truth_for_seed,
    sham_inner_id or None). Returns the per-library walk results + the CERTIFIED verdict."""
    init_worker()
    row, truth, sham = args
    t0 = time.time()
    name = row["name"]
    meta = truth["families"][name]
    prov = a17.Prov({name: (row["body"], row["final"], row["init"])})
    a17.M.use_provider(prov)
    if meta["level"] == "L2":
        comp = {c["id"]: c for c in truth["compositions"]}[meta["src"]]
        libs = libraries_l2(truth, comp, sham)
    else:
        libs = libraries_l1(truth, meta["src"])
    res = run_libs(libs, prov, name, row["Q2_size"])
    summ = {k: {"dev_reached": sum(not x["censored"] for x in v["dev"]),
                "tx_reached": sum(not x["censored"] for x in v["tx"]),
                "tx_charges": [x["charge"] for x in v["tx"]],
                "dev_charges": [x["charge"] for x in v["dev"]]} for k, v in res.items()}
    if meta["level"] == "L2":
        cert = summ["PROMOTED_A"]["tx_reached"] >= 1 and summ["PRISTINE"]["tx_reached"] == 0
        oracle = summ["PROMOTED_ORACLE"]["tx_reached"] >= 1 and summ["PRISTINE"]["tx_reached"] == 0
    else:
        cert = summ["FLAT_A"]["tx_reached"] >= 1 and summ["PRISTINE"]["tx_reached"] == 0
        oracle = None
    return {"name": name, "seed": row["source"], "level": meta["level"], "src": meta["src"], "sham_inner": sham,
            "summary": summ, "walks": res, "CERTIFIED": cert, "CERTIFIED_ORACLE": oracle,
            "seconds": round(time.time() - t0, 1)}


def sham_for(truth, comp_id, key):
    comp = {c["id"]: c for c in truth["compositions"]}[comp_id]
    others = sorted(m["id"] for m in truth["mechanisms"] if m["id"] != comp["inner"])
    return random.Random(I._seed("APHRODITE/W9H/SHAM/%s/%s" % (key, comp_id))).choice(others)


def stage_certify(pdir, workers=2, levels=("L2", "L1")):
    truths = json.loads((pdir / "W9H_TRUTH.json").read_text())
    rows = rdl(pdir / "W9H_FOUNDRY.jsonl")
    adm = admit(rows, truths)
    by = {r["name"]: r for r in rows}
    cp = pdir / "W9H_CERTIFY.jsonl"
    done = {r["name"] for r in rdl(cp)}
    jobs = []
    for lv in levels:                 # every T4-qualified family of the level (admitted or not: yield is measured)
        for n, a in sorted(adm.items()):
            r = by.get(n)
            if a["level"] == lv and r and r.get("T4_qualified") and n not in done:
                tr = truths[a["seed"]]
                jobs.append((r, tr, sham_for(tr, a["src"], a["seed"]) if lv == "L2" else None))
    log("certify jobs %d" % len(jobs))
    with open(cp, "a", encoding="utf-8") as fh, ProcessPoolExecutor(workers, initializer=init_worker) as ex:
        for i, res in enumerate(ex.map(certify_family, jobs)):
            fh.write(json.dumps(res, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("certify %d/%d %s %s cert=%s %s (%ss)" % (i + 1, len(jobs), res["name"], res["level"],
                                                         res["CERTIFIED"],
                                                         {k: v["tx_reached"] for k, v in res["summary"].items()},
                                                         res["seconds"]))


if __name__ == "__main__":
    cmd, pdir = sys.argv[1], Path(sys.argv[2])
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    if cmd == "foundry":
        stage_foundry(pdir, w)
    elif cmd == "certify":
        stage_certify(pdir, w)
    elif cmd == "report":
        import w9h_report
        w9h_report.report(pdir)
