"""Fire tests for requirements_to_jsonl.py: show that each check can fail.

A checker that has only ever printed PASS is not a checker. Each case below
damages a copy of REQUIREMENTS.md in memory in one specific way and expects
the corresponding defect. Run:

    python process/test_requirements_checker.py
"""
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("r2j", HERE / "requirements_to_jsonl.py")
r2j = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r2j)

TEXT = r2j.SRC.read_text(encoding="utf-8")


def defects_for(text):
    reqs, d = r2j.parse(text)
    return d + r2j.check(reqs, text)


def expect(name, text, needle):
    d = defects_for(text)
    ok = any(needle in x for x in d)
    print("%-34s %s" % (name, "fires" if ok else "DID NOT FIRE"))
    return ok


def main():
    results = []
    # 0. the undamaged file must be clean (negative control)
    clean = defects_for(TEXT)
    print("%-34s %s" % ("clean file", "no defects" if not clean else "DEFECTS: %r" % clean[:3]))
    results.append(not clean)

    # 1. duplicate id
    t = TEXT.replace("### SCI-02 [REQUIRED]", "### SCI-01 [REQUIRED]", 1)
    results.append(expect("duplicate id", t, "duplicate id SCI-01"))

    # 2. bad status word
    t = TEXT.replace("### ORG-01 [REQUIRED]", "### ORG-01 [MANDATORY]", 1)
    results.append(expect("bad status", t, "status 'MANDATORY' not allowed"))

    # 3. missing Check line
    head = "### WLD-02 [REQUIRED]"
    i = TEXT.index(head)
    j = TEXT.index("- Check:", i)
    k = TEXT.index("\n", j)
    t = TEXT[:j] + TEXT[k + 1:]
    results.append(expect("missing Check line", t, "WLD-02: missing or empty Check"))

    # 4. traceability names a requirement that does not exist
    t = TEXT.replace("| T08 | baseline omitted | WLD-03, MEAS-04 |", "| T08 | baseline omitted | WLD-03, MEAS-99 |", 1)
    results.append(expect("dangling traceability id", t, "MEAS-99 does not exist"))

    # 5. a taxonomy class with no row
    row = [l for l in TEXT.splitlines() if l.startswith("| T21 |")][0]
    t = TEXT.replace(row + "\n", "", 1)
    results.append(expect("taxonomy class without a row", t, "class T21 has no row"))

    # 6. malformed requirement heading
    t = TEXT.replace("### DEV-01 [REQUIRED] A lifetime has structure", "### DEV-01 REQUIRED A lifetime has structure", 1)
    results.append(expect("malformed heading", t, "requirement heading does not parse"))

    # 7. a requirement that points at a missing requirement
    t = TEXT.replace("- Check: Covered by SCI-01 and SCI-11.", "- Check: Covered by SCI-01 and SCI-77.", 1)
    results.append(expect("dangling cross-reference", t, "refers to SCI-77"))

    print("RESULT:", "PASS" if all(results) else "FAIL", "(%d of %d)" % (sum(results), len(results)))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
