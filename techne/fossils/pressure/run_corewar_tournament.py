"""Batch 08 depth (artificial life): a Core War (Redcode/MARS, 1984) survival tournament.

Round 08 digs the edges; this deepens the artificial-life area by driving the vault's own
corewar-redcode MARS. Classic warriors (Imp, Dwarf, Gemini, Mice, Core Clear) fight round-robin
in a shared memory core; each pair plays several rounds with randomised placement, and we record
who is still executing (non-empty task queue) at the end. Techne records the raw survival counts;
it does not rank strategies or say what "winning" means -- self-replication vs bombing vs scanning
are the warriors' own designs, and what the outcome spread MEANS is Nyx's question.

    python run_corewar_tournament.py -> COREWAR_TOURNAMENT_<date>.json
"""
import json, pathlib, subprocess, time

HERE = pathlib.Path(__file__).resolve().parent
VAULT = "/mnt/f/Prometheus/vault/fossils"
DATE = "2026-09-13"
TREE = "/vault/corewar-redcode/upstream/tree"

DRIVER = r'''
from __future__ import print_function, division
import sys, json
sys.path.insert(0, "%s")
from corewar import redcode, mars

ENV = {"CORESIZE": 8000, "MAXLENGTH": 100}
WARRIORS = ["imp", "dwarf", "gemini", "mice", "coreclear"]
MAX_STEPS = 4000
ROUNDS = 15

def load(name):
    with open("%s/warriors/" + name + ".red") as f:
        return redcode.parse(f, ENV)

def battle(a, b):
    aw = bw = tie = 0
    for r in range(ROUNDS):
        wa = load(a); wb = load(b)
        sim = mars.MARS(warriors=[wa, wb])  # __init__ loads + randomises placement
        for i in range(MAX_STEPS):
            try:
                sim.step()
            except Exception:
                break
            if sum(1 for w in (wa, wb) if w.task_queue) <= 1:
                break
        alive_a = bool(wa.task_queue); alive_b = bool(wb.task_queue)
        if alive_a and not alive_b: aw += 1
        elif alive_b and not alive_a: bw += 1
        else: tie += 1
    return aw, bw, tie

rows = []
for i in range(len(WARRIORS)):
    for j in range(i + 1, len(WARRIORS)):
        a, b = WARRIORS[i], WARRIORS[j]
        aw, bw, tie = battle(a, b)
        rows.append({"a": a, "b": b, "a_survives": aw, "b_survives": bw, "mutual_or_timeout": tie, "rounds": ROUNDS})
        print("ROW " + json.dumps(rows[-1]))
''' % (TREE, TREE)

SCRIPT = "cat > /tmp/drv.py <<'PYEOF'\n" + DRIVER + "\nPYEOF\npython /tmp/drv.py\n"


def main():
    out = subprocess.run(["wsl.exe", "-e", "bash", "-lc",
        "docker run --rm -v %s:/vault:ro python:2.7-slim bash -lc %s" % (VAULT, _q(SCRIPT))],
        capture_output=True, text=True, timeout=1800).stdout
    rows = []
    for line in out.splitlines():
        if line.startswith("ROW "):
            rows.append(json.loads(line[4:]))
    doc = {"schema": "techne.fossil.corewar_tournament/1", "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "fossil_driven": "corewar-redcode", "core_size": 8000, "max_steps": 4000, "rounds_per_pair": 15,
           "method": "round-robin among classic Redcode warriors (Imp, Dwarf, Gemini, Mice, Core Clear) in an 8000-cell MARS core; each pair plays 15 rounds with randomised placement; record how many rounds each warrior is still executing (non-empty task queue) at the end.",
           "note": "raw survival counts of preserved 1984 Core War warriors; NOT a strategy ranking. Imp is a one-instruction self-copier, Dwarf a bomber, Gemini a self-mover, Mice a replicator, Core Clear a sweeper -- different survival machinery. What the spread means is Nyx's question.",
           "warriors": ["imp", "dwarf", "gemini", "mice", "coreclear"], "rows": rows}
    op = HERE / ("COREWAR_TOURNAMENT_%s.json" % DATE)
    op.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    for r in rows:
        print("%-11s vs %-11s  a=%-3d b=%-3d tie=%-3d" % (r["a"], r["b"], r["a_survives"], r["b_survives"], r["mutual_or_timeout"]))
    print("wrote", op, len(rows), "rows")


def _q(s):
    return "'" + s.replace("'", "'\\''") + "'"


if __name__ == "__main__":
    main()
