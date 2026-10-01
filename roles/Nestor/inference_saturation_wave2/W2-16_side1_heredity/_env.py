"""W2-16 shared environment: Artemis's CVT-R adapter driven from the worktree copies of the foreign code
(file hashes verified equal to cvtr_nestor/results/ADAPTER_CHECK.json after CRLF->LF normalisation; see
s1_reproduce.py). Read-only on everything outside this folder. Adds a TRACED dense VM (pc + LDIR log) built by
the same source-injection method as run_dc.dense_z8, with the dense patch applied unchanged."""
from __future__ import annotations
import json, pathlib, sys, types, random

HERE = pathlib.Path(__file__).resolve().parent
WT = HERE.parents[3]                       # worktree root
NES = WT / "roles" / "Nestor" / "campaigns"
ART = WT / "roles" / "Artemis" / "challenge" / "cvtr_nestor"
W1 = NES / "npe-w1-donor-discovery-2026-09-26"
for p in [W1 / "x_dd_establish", W1 / "x_donor_discovery", W1 / "x_dd_dense_copy",
          NES / "c9x-explore-2026-09-24" / "x_donor_swap", NES / "z80atlas-verify-2026-09-22",
          ART / "artemis_p11", ART]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import adapter as A          # noqa: E402
import certs                 # noqa: E402
import p11                   # noqa: E402
from common import shabytes  # noqa: E402

ROWS = [json.loads(l) for l in (ART / "results" / "ROWS.jsonl").read_text().splitlines() if l.strip()]
FRESH = (None, 0, 0)


def traced_dense():
    """run_dc.dense_z8() source transform + two log lines: every fetched pc (who, pc) and every LDIR
    (who, src, dst, n). Semantics are unchanged (log appends only)."""
    import run_dc
    src = (NES / "z80atlas-verify-2026-09-22" / "z8.py").read_text()
    old = ("        if op == 0xED:\n"
           "            op2 = rd(pc + 1)\n"
           "            pc += 2\n")
    assert src.count(old) == 1
    new = ("        if op == 0xED or op in _DENSE:\n"
           "            if op == 0xED:\n"
           "                op2 = rd(pc + 1)\n"
           "                pc += 2\n"
           "            else:\n"
           "                op2 = _DENSE[op]\n"
           "                pc += 1\n")
    src = src.replace(old, new)
    f_old = "        op = mem[pc]\n"
    assert src.count(f_old) == 1
    src = src.replace(f_old, f_old + "        if _TR is not None: _TR.append((ctx.who, pc, op))\n")
    l_old = "                for _ in range(n):\n                    v = rd(src)\n"
    assert src.count(l_old) == 1
    src = src.replace(l_old, "                if _LD is not None: _LD.append((ctx.who, src, dst, n, step, pc))\n" + l_old)
    mod = types.ModuleType("z8_dense_traced")
    mod.__dict__["_DENSE"] = dict(run_dc.DENSE)
    mod.__dict__["_TR"] = None
    mod.__dict__["_LD"] = None
    exec(compile(src, "z8_dense_traced", "exec"), mod.__dict__)
    return mod


def row(key):
    return next(r for r in ROWS if r["key"] == key)
