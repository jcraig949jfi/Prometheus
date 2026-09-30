"""ARC3 Block A -- adversarial reconstruction of the C2 CON1 forensic case.
Forensic only; C2's frozen disposition (G1_STEPPING_STONE = NO) is untouched.

CON1: DONOR_G1 selected G2 = (v - (acc + {H})). On two SHAM_0-group transfer
families it solved 8/8 cells (4.5k-52k charges), where L1 and PRISTINE failed
at 10M. Attacks:
  T1 REPLAY      the 8 original cells, re-run with the same labels (determinism).
  T2 FRESH CELLS 16 new cells per original family (new label) -> not cell luck?
  T3 FRESH FAMS  12 new T4-admissible, Q2-qualified families drawn from W5
                 instances of G2 itself (disjoint from C2) -> does G2 generalise?
  T5 G1 ROLE     libraries: SELECTED (= g2 entry + L1 = g2 + G1 + PRISTINE);
                 G2_ONLY (g2 + PRISTINE, no G1); VMINUS ((v - {H}) + PRISTINE:
                 PRISTINE-derivable); SHAM0 (SHAM_0 + PRISTINE: confound control);
                 L1; PRISTINE. If G2_ONLY == SELECTED, the G1 entry is not
                 needed for the capability (G1 = route to the schema, not a
                 component of it).
  LADDER         L1 / PRISTINE re-run at 10M on cells SELECTED solves.
All hits are T4-qualified on the emitted artifact.
"""
import json
import os
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENG = HERE.parents[2] / "engine"
sys.path.insert(0, str(ENG))
os.environ["A17_FASTEVAL"] = "1"
os.environ["A18_FASTCOST"] = "1"
os.environ["A18_TAG"] = "ARC3-CON1"
import a18                      # noqa: E402
import a18_c1 as C              # noqa: E402
from a18 import a17, G, FR, I, T3D   # noqa: E402

G2 = "(v - (acc + {H}))"
LADDER = 40 * a17.ESCROW
C2DIR = ENG / "A19_C2"


def libs(panel):
    P = FR.pristine().entries
    return {"SELECTED": [a17.schema_entry("g2_new", G2)] + a17.L1_entries(),
            "G2_ONLY": [a17.schema_entry("g2_new", G2)] + P,
            "VMINUS": [a17.schema_entry("vminus", "(v - {H})")] + P,
            "SHAM0": [a17.schema_entry("sham0", panel["SHAM_0"])] + P,
            "L1": a17.L1_entries(), "PRISTINE": P}


def cell_job(args):
    a18.worker_init()
    tag, name, spec, size, i, label, panel = args
    prov = a17.Prov({name: spec})
    a17.M.use_provider(prov)
    out = {"tag": tag, "family": name, "spec": list(spec), "cell": i, "label": label}
    L = libs(panel)
    for k, ents in L.items():
        c = FR.Cell(prov, name, i, size, label=label)
        ch, prog = c.cost(FR.KLib(ents))
        q = bool(prog is not None and C.t4_qualified(prov, name, prog)[0])
        out[k] = {"charge": ch, "qualified": q, "program": list(prog) if prog else None}
    if out["SELECTED"]["qualified"]:
        for k in ("L1", "PRISTINE"):
            if not out[k]["qualified"]:
                c = FR.Cell(prov, name, i, size, label=label)
                ch, prog = c.cost(FR.KLib(L[k]), LADDER)
                out[k]["ladder_charge"] = ch
                out[k]["ladder_qualified"] = bool(prog is not None and C.t4_qualified(prov, name, prog)[0])
    return out


def fresh_families(n=12, seed="APHRODITE/ARC3/CON1/FRESH/v1"):
    import ruler_v2 as R
    import tribunal_t4 as T4
    a18.use_world("W5")
    rng = random.Random(I._seed(seed))
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    inst = [b for b in T3D.instantiate(G2) if R.accumulating(b)]
    used = set()
    roles = json.loads((C2DIR / "A18_ROLES_2026-09-28.json").read_text())
    for v in roles.values():
        for f in v["families"]:
            used.add(f["body"])
    out, tries = [], 0
    while len(out) < n and tries < 5000:
        tries += 1
        b = rng.choice(inst)
        if b in used:
            continue
        p = ("fold", rng.choice(G.H1_SPACE), b, rng.choice(finals))
        if not T4.family_profile(p)["admissible"]:
            continue
        name = "fr" + "".join("abcdefghijklmnopqrstuvwxyz"[(len(out) // 26 ** k) % 26] for k in range(3))
        prov = a17.Prov({name: (p[2], p[3], p[1])})
        size = a17.qualify(prov, name, "ARC3-CON1-Q2")
        if size is None:
            continue
        used.add(b)
        out.append((name, (p[2], p[3], p[1]), size))
    return out


if __name__ == "__main__":
    a18.use_world("W5")
    panel = json.loads((C2DIR / "A18_PANEL_2026-09-28.json").read_text())["panel"]
    roles = json.loads((C2DIR / "A18_ROLES_2026-09-28.json").read_text())
    fam = {f["name"]: f for f in roles["CON/1"]["families"]}
    tr = [json.loads(l) for l in (C2DIR / "A18_TRANSFER_2026-09-28.jsonl").read_text().splitlines()]
    orig = sorted({t["family"] for t in tr if t["catalog"] == "CON1" and t["arm"] == "G1"
                   and any(c["SELECTED"]["qualified"] and not c["START"]["qualified"] for c in t["cells"])})
    jobs = []
    for n in orig:
        f = fam[n]
        spec = (f["body"], f["final"], f["init"])
        for i in range(4):
            jobs.append(("T1_REPLAY", n, spec, f["Q2_size"], i, "A19-CON1-rx", panel))
        for i in range(16):
            jobs.append(("T2_FRESH_CELL", n, spec, f["Q2_size"], 100 + i, "ARC3-CON1-fresh", panel))
    ff = fresh_families()
    for n, spec, size in ff:
        for i in range(4):
            jobs.append(("T3_FRESH_FAMILY", n, spec, size, i, "ARC3-CON1-ff", panel))
    print("original families", orig, "fresh families", len(ff), "jobs", len(jobs), flush=True)
    with ProcessPoolExecutor(int(os.environ.get("CON1_WORKERS", "5")), initializer=a18.worker_init) as ex:
        rows = list(ex.map(cell_job, jobs, chunksize=1))
    (HERE / "CON1_FORENSICS.json").write_text(json.dumps({"G2": G2, "panel": panel, "original": orig,
                                                         "fresh_families": ff, "rows": rows}, indent=1))
    from collections import defaultdict, Counter
    s = defaultdict(Counter)
    for r in rows:
        for k in ("SELECTED", "G2_ONLY", "VMINUS", "SHAM0", "L1", "PRISTINE"):
            s[r["tag"]][k] += r[k]["qualified"]
        s[r["tag"]]["cells"] += 1
        for k in ("L1", "PRISTINE"):
            if "ladder_qualified" in r[k]:
                s[r["tag"]][k + "_ladder_q"] += r[k]["ladder_qualified"]
                s[r["tag"]][k + "_ladder_run"] += 1
    for t, v in s.items():
        print(t, dict(v))
