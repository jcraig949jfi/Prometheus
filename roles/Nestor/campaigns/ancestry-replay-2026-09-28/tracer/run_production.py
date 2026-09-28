"""PREPARED, NOT RUN. Production replay of the 11 T-003 run records (9 distinct simulations; Amendment C7.4).

Refuses unless GATES.json says every gate is CLEAR (it is written by hand, dated, by the Nestor seat after each ruling),
and unless the tracer files still hash to TRACER_FREEZE.json (a changed tracer = a new freeze = the agreement evidence is
stale). Runs run_trace.py for the 11 records (processes <= 10) under the M1 cpu8 host lease, then writes
PRODUCTION_INDEX.json: per record its sim_id (lineage hash prefix), duplicate_of (records with an identical lineage hash
are ONE simulation), births, and the export sha256s. No statistic is computed here.
"""
import hashlib, json, pathlib, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent


def freeze_ok():
    fz = json.loads((HERE / "TRACER_FREEZE.json").read_text(encoding="utf-8"))
    return all(hashlib.sha256((HERE / f).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == h
               for f, h in fz["files"].items())


def main():
    gates = json.loads((ROOT / "GATES.json").read_text(encoding="utf-8"))
    open_ = [g for g, v in gates["gates"].items() if v["status"] != "CLEAR"]
    if open_:
        sys.exit("REFUSED: gates not clear: %s" % ", ".join(open_))
    if not freeze_ok():
        sys.exit("REFUSED: tracer changed since TRACER_FREEZE.json (agreement evidence stale)")
    with ThreadPoolExecutor(10) as ex:
        list(ex.map(lambda i: subprocess.run([sys.executable, str(HERE / "run_trace.py"), str(i)], check=True), range(11)))
    idx = {}
    for p in sorted((ROOT / "exports").glob("*.summary.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        idx[d["run"]] = {"sim_id": d["sim_id"], "lineage_sha256": d["lineage_sha256"], "births": d["tally"]["births"],
                         "births_sha256": d["births_sha256"]}
    first = {}
    for run, v in idx.items():
        v["duplicate_of"] = first.setdefault(v["lineage_sha256"], run) if first.get(v["lineage_sha256"]) != run else None
    (ROOT / "exports" / "PRODUCTION_INDEX.json").write_text(json.dumps(idx, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("distinct simulations:", len(first))


if __name__ == "__main__":
    main()
