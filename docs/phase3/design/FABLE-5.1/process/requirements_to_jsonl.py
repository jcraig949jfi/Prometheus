"""Generate requirements.jsonl from REQUIREMENTS.md and check its shape.

Run from the package directory:

    python process/requirements_to_jsonl.py            # write + check
    python process/requirements_to_jsonl.py --check    # check only, exit 1 on defect

Checks (each can fail):
  - every requirement heading parses as "### <ID> [<STATUS>] <title>"
  - ids are unique
  - status is one of the four allowed words
  - every requirement has Statement, Why, Record and Check lines, none empty
  - every id named in the traceability table exists
  - every taxonomy class T01..T24 has a row in the traceability table
  - the generated file equals the committed file (--check)
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
SRC = HERE / "REQUIREMENTS.md"
OUT = HERE / "requirements.jsonl"
STATUSES = {"REQUIRED", "HIGH VALUE", "EXPERIMENTAL", "REJECTED"}
FIELDS = ("Statement", "Why", "Record", "Check")
HEAD = re.compile(r"^### ([A-Z]+-\d\d) \[([A-Z ]+)\] (.+)$")
AREA = {
    "SCI": "scientific", "ORG": "organism", "DEV": "developmental", "WLD": "world",
    "SRCH": "pressure_search", "MEAS": "measurement", "CAUS": "causal_analysis",
    "XFER": "transfer", "PROV": "provenance", "REPR": "reproducibility",
    "ANTI": "anti_prior", "COMP": "compute", "INF": "inference", "ENRG": "energy",
    "HUM": "human_attention", "PUB": "publication_output",
}


def parse(text):
    reqs, cur, defects = [], None, []
    for n, line in enumerate(text.splitlines(), 1):
        m = HEAD.match(line)
        if m:
            cur = {"id": m.group(1), "status": m.group(2), "title": m.group(3).strip(), "line": n}
            reqs.append(cur)
            continue
        if line.startswith("### ") and re.match(r"^### [A-Z]+-\d", line):
            defects.append("line %d: requirement heading does not parse: %r" % (n, line))
        if line.startswith("## ") or line.startswith("-----"):
            cur = None
            continue
        if cur is not None:
            for f in FIELDS:
                tag = "- %s: " % f
                if line.startswith(tag):
                    cur[f.lower()] = line[len(tag):].strip()
    return reqs, defects


def expand_range(a, b):
    pa, na = a.split("-")
    pb, nb = b.split("-")
    if pa != pb:
        return [a, b]
    return ["%s-%02d" % (pa, i) for i in range(int(na), int(nb) + 1)]


def check(reqs, text):
    defects = []
    seen = {}
    for r in reqs:
        if r["id"] in seen:
            defects.append("duplicate id %s (lines %d and %d)" % (r["id"], seen[r["id"]], r["line"]))
        seen[r["id"]] = r["line"]
        if r["status"] not in STATUSES:
            defects.append("%s: status %r not allowed" % (r["id"], r["status"]))
        prefix = r["id"].split("-")[0]
        if prefix not in AREA:
            defects.append("%s: unknown area prefix" % r["id"])
        for f in FIELDS:
            if not r.get(f.lower()):
                defects.append("%s: missing or empty %s" % (r["id"], f))
    # traceability table
    in_table, classes = False, set()
    for line in text.splitlines():
        if line.startswith("## 18. Traceability"):
            in_table = True
            continue
        if in_table and line.startswith("| T"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            classes.add(cells[0])
            body = cells[2]
            for a, b in re.findall(r"([A-Z]+-\d\d) to ([A-Z]+-\d\d)", body):
                for rid in expand_range(a, b):
                    if rid not in seen:
                        defects.append("traceability %s: %s does not exist" % (cells[0], rid))
            for rid in re.findall(r"[A-Z]+-\d\d", body):
                if rid not in seen:
                    defects.append("traceability %s: %s does not exist" % (cells[0], rid))
    for i in range(1, 25):
        if "T%02d" % i not in classes:
            defects.append("traceability: class T%02d has no row" % i)
    # ids referenced anywhere in Check lines must exist
    for r in reqs:
        for rid in re.findall(r"\b[A-Z]{3,4}-\d\d\b", r.get("check", "") + " " + r.get("why", "")):
            if rid.split("-")[0] in AREA and rid not in seen:
                defects.append("%s: refers to %s, which does not exist" % (r["id"], rid))
    return defects


def render(reqs):
    lines = []
    for r in reqs:
        lines.append(json.dumps({
            "id": r["id"],
            "area": AREA.get(r["id"].split("-")[0], "unknown"),
            "status": r["status"],
            "title": r["title"],
            "statement": r.get("statement", ""),
            "why": r.get("why", ""),
            "record": r.get("record", ""),
            "check": r.get("check", ""),
        }, ensure_ascii=True, sort_keys=False))
    return "\n".join(lines) + "\n"


def main():
    text = SRC.read_text(encoding="utf-8")
    reqs, defects = parse(text)
    defects += check(reqs, text)
    out = render(reqs)
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != out:
            defects.append("requirements.jsonl is missing or differs from REQUIREMENTS.md")
    else:
        OUT.write_text(out, encoding="utf-8", newline="\n")
    counts = {}
    for r in reqs:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("requirements: %d  %s" % (len(reqs), counts))
    for d in defects:
        print("DEFECT:", d)
    print("RESULT:", "FAIL" if defects else "PASS")
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
