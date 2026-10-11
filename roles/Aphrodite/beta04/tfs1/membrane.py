"""TFS-1 minimal membrane: artifact hashing, entries-only library transplant into a FRESH process with a
no-donor-state receipt, paired common-random-number comparison, and the exact sign-flip test (ported verbatim from
roles/Aphrodite/engine/v2b/b02.py flip_dist / flip_test).

No-donor-state receipt. The recipient is a new Python process started with -I (isolated: no PYTHONPATH, no user site,
no script-dir injection). It is given exactly two paths -- the serialized library and the task supply -- and reads
nothing else (every read goes through ReadLog and is recorded with its sha256 and byte count). It re-serializes the
loaded library and reports that hash, its pid, the hashes of the tfs1 code files it imported, and its results. The
parent's verify_receipt() checks: fresh pid, reads == exactly {library, tasks} with the parent-side hashes, loaded
library re-serializes byte-identically, and the code hashes equal the parent's.

Run the recipient by hand:  python -I <path>/tfs1/membrane.py recipient LIB.json TASKS.json OUT.json
TASKS.json: {"budget": int, "max_size": int, "seed": int, "tasks": [contract task JSON objects]}.
"""
import hashlib
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

HERE = Path(__file__).resolve().parent
if __name__ == "__main__":                      # executed as a script inside the isolated recipient
    sys.path.insert(0, str(HERE.parent))

from tfs1 import core as C                      # noqa: E402
from tfs1.library import Library, canon, sha   # noqa: E402
from tfs1.enum import Enumerator, make_verifier  # noqa: E402

RECEIPT_VERSION = "tfs1-receipt-v0"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def artifact_sha256(obj) -> str:
    """Hash of any JSON-able artifact in canonical form (sorted keys, no whitespace)."""
    return sha(obj)


def code_hashes() -> Dict[str, str]:
    return {p.name: sha256_file(p) for p in sorted(HERE.glob("*.py"))}


def export_library(lib: Library, path) -> str:
    data = lib.dumps().encode()
    Path(path).write_bytes(data)
    return sha256_bytes(data)


class ReadLog:
    def __init__(self):
        self.reads: List[Dict] = []

    def read(self, path) -> bytes:
        b = Path(path).read_bytes()
        self.reads.append({"path": str(Path(path).resolve()), "sha256": sha256_bytes(b), "bytes": len(b)})
        return b


# ---------------------------------------------------------------- recipient side
def run_tasks(lib: Library, supply: Dict) -> List[Dict]:
    E = Enumerator(lib)
    out = []
    for task in supply["tasks"]:
        verify = make_verifier(task["test"], lib)
        r = E.search(task["dev"], task["output_type"], supply.get("seed", 0), task["family_id"], supply["budget"],
                     supply.get("max_size", 8), verify=verify)
        out.append({"family_id": task["family_id"], "hit": r["hit"], "hit_charge": r["hit_charge"],
                    "charges": r["charges"], "program": r["program"], "units_expanded": r["units_expanded"],
                    "units_promoted": r["units_promoted"]})
    return out


def recipient_main(lib_path, tasks_path, out_path):
    log = ReadLog()
    lib_bytes = log.read(lib_path)
    task_bytes = log.read(tasks_path)
    lib = Library.loads(lib_bytes.decode())
    supply = json.loads(task_bytes.decode())
    results = run_tasks(lib, supply)
    receipt = {"receipt_version": RECEIPT_VERSION, "pid": os.getpid(), "python": sys.version.split()[0],
               "isolated_flag": bool(sys.flags.isolated), "reads": log.reads,
               "library_loaded_sha256": lib.sha256(), "library_entries": lib.ids(),
               "library_max_depth": lib.max_depth(), "tasks_sha256": sha256_bytes(task_bytes),
               "code_sha256": code_hashes(), "results": results}
    receipt["receipt_sha256"] = artifact_sha256(receipt)
    Path(out_path).write_text(json.dumps(receipt, sort_keys=True, indent=1))
    return receipt


# ---------------------------------------------------------------- donor / parent side
def transplant(lib: Library, supply: Dict, workdir, tag: str = "t", timeout: int = 900) -> Dict:
    """Serialize lib (entries only) + supply, run a fresh isolated recipient, verify its receipt."""
    wd = Path(workdir)
    wd.mkdir(parents=True, exist_ok=True)
    lp, tp, op = wd / ("%s_library.json" % tag), wd / ("%s_tasks.json" % tag), wd / ("%s_receipt.json" % tag)
    lib_sha = export_library(lib, lp)
    tp.write_bytes(canon(supply))
    task_sha = sha256_file(tp)
    env = {k: v for k, v in os.environ.items() if k.upper() in ("SYSTEMROOT", "PATH", "TEMP", "TMP", "WINDIR")}
    env["OMP_NUM_THREADS"] = "1"
    proc = subprocess.run([sys.executable, "-I", str(HERE / "membrane.py"), "recipient", str(lp), str(tp), str(op)],
                          capture_output=True, text=True, timeout=timeout, env=env, cwd=str(wd))
    if proc.returncode != 0:
        raise RuntimeError("recipient failed: %s" % proc.stderr[-2000:])
    receipt = json.loads(op.read_text())
    check = verify_receipt(receipt, lp, lib_sha, tp, task_sha)
    return {"library_sha256": lib_sha, "tasks_sha256": task_sha, "receipt": receipt, "verification": check}


def verify_receipt(receipt: Dict, lib_path, lib_sha: str, tasks_path, task_sha: str) -> Dict:
    body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    reads = {(r["path"], r["sha256"]) for r in receipt["reads"]}
    want = {(str(Path(lib_path).resolve()), lib_sha), (str(Path(tasks_path).resolve()), task_sha)}
    checks = {
        "receipt_hash_ok": artifact_sha256(body) == receipt["receipt_sha256"],
        "fresh_process": receipt["pid"] != os.getpid(),
        "isolated_interpreter": receipt["isolated_flag"] is True,
        "reads_exactly_library_and_tasks": reads == want and len(receipt["reads"]) == 2,
        "library_reserializes_identically": receipt["library_loaded_sha256"] == lib_sha,
        "tasks_hash_ok": receipt["tasks_sha256"] == task_sha,
        "same_code": receipt["code_sha256"] == code_hashes(),
    }
    checks["NO_DONOR_STATE"] = all(checks.values())
    return checks


# ---------------------------------------------------------------- paired CRN comparison
def hitting_costs(lib: Optional[Library], tasks: Sequence[Dict], budget: int, seed, max_size: int = 8,
                  verify_test: bool = True) -> List[Dict]:
    """Per task: hitting cost under the keyed CRN walk (slot = family_id; censored at budget)."""
    E = Enumerator(lib)
    out = []
    for task in tasks:
        verify = make_verifier(task["test"], lib) if verify_test else None
        r = E.search(task["dev"], task["output_type"], seed, task["family_id"], budget, max_size, verify=verify)
        out.append({"family_id": task["family_id"], "cost": r["hit_charge"] if r["hit"] else budget,
                    "censored": not r["hit"], "program": r["program"], "units_expanded": r["units_expanded"],
                    "units_promoted": r["units_promoted"]})
    return out


def paired_crn(control: List[Dict], treatment: List[Dict]) -> Dict:
    """d_i = cost_control - cost_treatment (positive = treatment cheaper), same cells/seed/slot. Exact sign-flip."""
    assert [c["family_id"] for c in control] == [t["family_id"] for t in treatment]
    d = [c["cost"] - t["cost"] for c, t in zip(control, treatment)]
    res = flip_test(d)
    res["hits_control"] = sum(not c["censored"] for c in control)
    res["hits_treatment"] = sum(not t["censored"] for t in treatment)
    return res


# ---------------------------------------------------------------- exact sign-flip (verbatim port of b02.py)
def flip_dist(d):
    """Exact sign-flip null distribution of sum(+-|d_i|) over integer d (zeros drop out): {sum: count}."""
    dist = {0: 1}
    for x in (abs(int(v)) for v in d if v != 0):
        nd = {}
        for s, c in dist.items():
            nd[s + x] = nd.get(s + x, 0) + c
            nd[s - x] = nd.get(s - x, 0) + c
        dist = nd
    return dist


def flip_test(d):
    nz = [int(v) for v in d if v != 0]
    obs = sum(nz)
    dist = flip_dist(nz)
    tot = 2 ** len(nz)
    p1 = sum(c for s, c in dist.items() if s >= obs) / tot
    p2 = sum(c for s, c in dist.items() if abs(s) >= abs(obs)) / tot
    return {"n": len(d), "nonzero": len(nz), "sum": obs, "mean": round(sum(d) / len(d), 3) if d else None,
            "median": statistics.median(d) if d else None, "better": sum(v > 0 for v in d),
            "worse": sum(v < 0 for v in d), "tied": sum(v == 0 for v in d), "p_one_sided": round(p1, 6),
            "p_two_sided": round(p2, 6), "attainable_min_p": round(1 / tot, 8), "diffs": list(d)}


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "recipient":
        os.environ["OMP_NUM_THREADS"] = "1"
        recipient_main(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__)
        sys.exit(2)
