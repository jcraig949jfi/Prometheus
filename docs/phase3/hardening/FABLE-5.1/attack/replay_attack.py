"""Replay the adversarial reader's attack on the FIRST version of the harness.

    python -B replay_attack.py         about four minutes; writes RECEIPT_attack_on_first_version.json

first_version/ is the harness as its author first wrote it (34 sound cases, 62 mutants, all the
author's, every gate PASS). reader/ holds the scripts an adversarial reader wrote against it, as it
left them. This script runs those scripts on a temporary copy and counts:

  - broken cases the reader built that the first version PASSED (the reader marks them "E");
  - sound cases the reader built that the first version REJECTED (marked "S");
  - one-line changes to gate logic that the first version's tests did not notice;
  - the reader's simulation of the key world with a second nested boundary.

Nothing here is a test of the current harness. It is the record of why the current one differs.
"""
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
FIRST, READER = HERE / "first_version", HERE / "reader"
COUNTERFEIT = HERE.parents[1].parent / "review" / "FABLE-5.1" / "counterfeit"
PROBES = ("p04_escapes_a.py", "p05_escapes_b.py", "p06_escapes_c.py", "p07_audits.py")
DRV = '''import sys, pathlib, json
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "harness"))
from rso_harness import meta
meta.COUNTERFEIT = pathlib.Path(r"%s")
'''


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def run(script, cwd):
    r = subprocess.run([sys.executable, "-B", script], cwd=str(cwd), capture_output=True, text=True)
    return r.stdout + r.stderr


def main():
    original = json.loads((FIRST / "RECEIPT_harness_v0.json").read_text(encoding="ascii"))
    same = all(sha(FIRST / name) == h for name, h in original["source_sha256_lf"].items())
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="rso_attack_"))
    try:
        ignore = shutil.ignore_patterns("__pycache__")
        shutil.copytree(FIRST, tmp / "harness", ignore=ignore)
        shutil.copytree(FIRST, tmp / "harness_run", ignore=ignore)
        meta = tmp / "harness_run" / "rso_harness" / "meta.py"
        text = meta.read_text(encoding="ascii")
        line = 'COUNTERFEIT = HERE.parents[2].parent / "review" / "FABLE-5.1" / "counterfeit"'
        assert text.count(line) == 1
        meta.write_text(text.replace(line, 'COUNTERFEIT = pathlib.Path(r"%s")' % COUNTERFEIT), encoding="ascii",
                        newline="\n")
        (tmp / "drv.py").write_text(DRV % COUNTERFEIT, encoding="ascii", newline="\n")
        for name in PROBES + ("p09_mutate.py", "p11_order4.py"):
            shutil.copy(READER / name, tmp / name)
        base = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover"], cwd=str(tmp / "harness_run"),
                              capture_output=True, text=True)
        section, broken, sound = None, {}, {}
        for name in PROBES:
            for row in run(name, tmp).splitlines():
                head = re.match(r"#+ (.*)", row)
                if head:
                    section = head.group(1).strip()
                    continue
                case = re.match(r"\s*(E|S) (.*?)\s+-> (\w+)", row)
                if case and section:
                    (broken if case.group(1) == "E" else sound).setdefault(section, []).append(
                        {"case": case.group(2).strip(), "verdict": case.group(3)})
        probe9 = run("p09_mutate.py", tmp)
        logic = re.search(r"(\d+) of (\d+) changes to gate logic are not noticed", probe9)
        probe11 = run("p11_order4.py", tmp)
        order4 = {}
        block = probe11.split("epoch-level hidden object: rotation")[1].split("epoch-level hidden object")[0]
        for row in block.splitlines():
            m = re.match(r"\s+(\S.*?)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$", row)
            if m:
                order4[m.group(1)] = {"first_family": float(m.group(2)), "across_families": float(m.group(3)),
                                      "across_epochs": float(m.group(4))}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    escaped = {s: sum(1 for c in rows if c["verdict"] == "PASS") for s, rows in broken.items()}
    rejected = {s: sum(1 for c in rows if c["verdict"] != "PASS") for s, rows in sound.items()}
    out = {
        "what": "replay of the adversarial reader's attack on the first version of the reference harness",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "python": sys.version.split()[0],
        "first_version": {"is_the_code_that_wrote_its_receipt": same, "summary": original["summary"],
                          "its_own_tests_pass": base.returncode == 0},
        "broken_cases_written_by_the_reader": sum(len(v) for v in broken.values()),
        "of_which_passed": sum(escaped.values()),
        "sections_probed": len(broken), "sections_with_an_escape": sum(1 for v in escaped.values() if v),
        "sound_cases_written_by_the_reader": sum(len(v) for v in sound.values()),
        "of_which_rejected": sum(rejected.values()),
        "logic_changes": int(logic.group(2)) if logic else None,
        "logic_changes_not_noticed": int(logic.group(1)) if logic else None,
        "by_section": {s: {"broken": len(rows), "passed": escaped[s]} for s, rows in sorted(broken.items())},
        "sound_by_section": {s: {"sound": len(rows), "rejected": rejected[s]} for s, rows in sorted(sound.items())},
        "cases": {"broken": broken, "sound": sound},
        "readers_key_world_with_a_second_boundary": {"lives": 3000, "mean_correct_of_16": order4},
        "source_sha256_lf": {p.relative_to(HERE).as_posix(): sha(p) for p in sorted(
            list(FIRST.rglob("*.py")) + list(READER.glob("*.py")) + [HERE / "replay_attack.py"])},
    }
    (HERE / "RECEIPT_attack_on_first_version.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n",
                                                               encoding="ascii", newline="\n")
    print("first version is the code that wrote its receipt: %s; its own tests pass: %s" % (same, base.returncode == 0))
    print("broken cases by the reader: %d, passed: %d, in %d of %d sections"
          % (out["broken_cases_written_by_the_reader"], out["of_which_passed"], out["sections_with_an_escape"],
             out["sections_probed"]))
    print("sound cases by the reader: %d, rejected: %d" % (out["sound_cases_written_by_the_reader"],
                                                           out["of_which_rejected"]))
    print("logic changes: %s, not noticed: %s" % (out["logic_changes"], out["logic_changes_not_noticed"]))
    for name, row in order4.items():
        print("  %-64s %s" % (name[:64], row))
    return 0 if same and logic else 1


if __name__ == "__main__":
    sys.exit(main())
