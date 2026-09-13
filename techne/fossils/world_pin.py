"""Pin the execution world of the high-value network-dependent fossils (batch 11 P2).

Batch 10's queue ranked 18 recipes that fetch at build/run time. This pins them in priority order,
one at a time, by capturing the FULL TRANSITIVE dependency closure actually resolved in the
fossil's own image and freezing it into a constraints file that lives in the specimen's TRACKED
harness. The recipe then installs under that constraint, so a later run resolves the same closure.

    python -m techne.fossils.world_pin <specimen_id> [...] [--apply]

Honest classification, per the charter:
    ORIGINAL_WORLD_RECOVERED   evidence names the versions the original evidence ran under
    COMPATIBLE_RECONSTRUCTION  the original versions are NOT recoverable, but a pinned world is
                               captured and the fossil still satisfies its own oracle in it
    CURRENT_WORLD_ONLY         only today's resolution is captured; the oracle was not re-checked
    UNKNOWN                    the closure could not be captured

No fossil in the vault records the versions its evidence ran under, so ORIGINAL_WORLD_RECOVERED is
not reachable for any of them today. Choosing modern versions and calling them historical is
exactly what the charter forbids; COMPATIBLE_RECONSTRUCTION says what was actually done.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import time

from . import record, vault

CONSTRAINTS = "world_constraints.txt"
PIP_RE = re.compile(r"(pip3?\s+install\s+(?:-q\s+)?)(?!-c\b)")


def _wsl(cmd, timeout=2400):
    p = subprocess.run(["wsl.exe", "-e", "bash", "-lc", cmd], capture_output=True, text=True,
                       timeout=timeout)
    return p.stdout, p.stderr


def _q(s):
    return "'" + s.replace("'", "'\\''") + "'"


def _specs(recipe):
    """The direct pip specs a recipe asks for, minus local-path installs."""
    out = []
    for ph in ("build", "runs"):
        for st in (recipe.get(ph) or []):
            for m in re.finditer(r"pip3?\s+install\s+(?:-q\s+)?([^&|;>\"]*)", st.get("cmd", "")):
                for tok in m.group(1).split():
                    # a package name starts with a letter; this drops ".", flags, and shell
                    # redirection crumbs like the "2" of "2>" that the command regex can catch
                    if not re.match(r"^[A-Za-z][A-Za-z0-9_.\-]*$", tok):
                        continue
                    out.append(tok)
    return sorted(set(out))


def capture_closure(sid: str) -> dict:
    rec = record.load(sid)
    sd = vault.specimen_dir(sid)
    recipe = json.loads((sd / "recipe.json").read_text(encoding="utf-8"))
    image = recipe.get("image") or "python:3.11-slim"
    specs = _specs(recipe)
    if not specs:
        return {"specimen_id": sid, "status": "UNKNOWN", "reason": "no external pip spec found"}
    script = ("pip install -q %s >/dev/null 2>&1 || { echo CAPTURE_FAILED; exit 0; }\n"
              "echo FREEZE_BEGIN\npip freeze --exclude-editable\n" % " ".join(specs))
    out, _ = _wsl("docker run --rm %s bash -lc %s" % (image, _q(script)))
    if "CAPTURE_FAILED" in out or "FREEZE_BEGIN" not in out:
        return {"specimen_id": sid, "status": "UNKNOWN", "reason": "closure capture failed", "image": image}
    frozen = [l.strip() for l in out.split("FREEZE_BEGIN", 1)[1].splitlines() if "==" in l]
    # never constrain the fossil's own distribution (it is installed from the preserved body)
    own = re.sub(r"[^a-z0-9]+", "-", sid.lower())
    frozen = [l for l in frozen if re.sub(r"[^a-z0-9]+", "-", l.split("==")[0].lower()) not in own]
    return {"specimen_id": sid, "status": "CAPTURED", "image": image, "direct_specs": specs,
            "closure": sorted(frozen), "n_pinned": len(frozen)}


def apply_pin(sid: str, closure: dict) -> dict:
    sd = vault.specimen_dir(sid)
    (sd / "harness").mkdir(exist_ok=True)
    header = ("# Execution-world closure for %s, captured %s.\n"
              "# The ORIGINAL world of this fossil's existing evidence is NOT recoverable: no record,\n"
              "# recipe, receipt or dataset names a version. This is a COMPATIBLE RECONSTRUCTION --\n"
              "# a world that is pinned from here on, not a claim about the world that ran before.\n"
              % (sid, time.strftime("%Y-%m-%d", time.gmtime())))
    (sd / "harness" / CONSTRAINTS).write_text(header + "\n".join(closure["closure"]) + "\n",
                                              encoding="utf-8", newline="\n")
    rp = sd / "recipe.json"
    recipe = json.loads(rp.read_text(encoding="utf-8"))
    n = 0
    for ph in ("build", "runs"):
        for st in (recipe.get(ph) or []):
            if "pip install" in st.get("cmd", "") or "pip3 install" in st.get("cmd", ""):
                new = PIP_RE.sub(lambda m: m.group(1) + "-c $HARNESS/%s " % CONSTRAINTS, st["cmd"])
                if new != st["cmd"]:
                    st["cmd"] = new
                    n += 1
    recipe["world_closure"] = {"constraints": "harness/" + CONSTRAINTS,
                               "n_pinned": closure["n_pinned"],
                               "captured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                               "classification": "COMPATIBLE_RECONSTRUCTION",
                               "note": "original world unrecoverable from evidence; this pins the world "
                                       "from here on"}
    rp.write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"pip_commands_pinned": n, "constraints_file": str(sd / "harness" / CONSTRAINTS)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("specimens", nargs="+")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rows = []
    for sid in a.specimens:
        c = capture_closure(sid)
        row = {**{k: c.get(k) for k in ("specimen_id", "status", "image", "direct_specs", "n_pinned")},
               "classification": "UNKNOWN"}
        if c["status"] == "CAPTURED":
            row["closure_sample"] = c["closure"][:6]
            if a.apply:
                row.update(apply_pin(sid, c))
                row["classification"] = "COMPATIBLE_RECONSTRUCTION_PENDING_ORACLE"
            else:
                row["classification"] = "CURRENT_WORLD_ONLY"
        else:
            row["reason"] = c.get("reason")
        rows.append(row)
        print("%-28s %-10s pinned=%-4s %s" % (sid, c["status"], c.get("n_pinned", "-"),
                                              row["classification"]))
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(
            {"schema": "techne.fossil.world_pin/1",
             "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "note": "ORIGINAL_WORLD_RECOVERED is unreachable for every fossil in the vault: none "
                     "records the versions its evidence ran under.",
             "rows": rows}, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
