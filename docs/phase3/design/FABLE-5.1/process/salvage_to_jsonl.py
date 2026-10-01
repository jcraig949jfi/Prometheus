"""Generate salvage.jsonl from SALVAGE_MATRIX.md and check the tallies quoted in it.

SALVAGE_MATRIX.md is the source of truth. Each component row is a block:

    ### O-03 [REBUILD] Title
    - Does: ...
    - Shown correct: ...
    - Fit: ...
    - Cost: ...
    - Coupling: ...
    - Take: ...
    - Lines: <integer> | not reported | counted in <ID>
    - Source: ...

Checks: ids unique and well formed; class in the vocabulary; every field
present exactly once and non-empty; "counted in" points at a real row. With
--check, also requires the three tally lines in the document (COUNTS all,
COUNTS scientific, LINES scientific) to equal the values computed here.

    python salvage_to_jsonl.py           # write ../salvage.jsonl, print tallies
    python salvage_to_jsonl.py --check   # verify only; exit 1 on any mismatch
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "SALVAGE_MATRIX.md"
OUT = HERE.parent / "salvage.jsonl"

CLASSES = ["KEEP", "HARDEN", "EXTRACT", "REBUILD", "RETIRE", "HISTORICAL CONTROL", "UNKNOWN"]
FIELDS = ["Does", "Shown correct", "Fit", "Cost", "Coupling", "Take", "Lines", "Source"]
LAYERS = {"O": "organism", "W": "world", "S": "search", "M": "measurement", "C": "causal", "I": "infrastructure"}
SCIENTIFIC = "OWSMC"
HEAD = re.compile(r"^### ([OWSMCI])-(\d\d) \[([A-Z ]+)\] (.+)$")


def parse(text):
    rows, errors = [], []
    cur = None
    for n, line in enumerate(text.split("\n"), 1):
        m = HEAD.match(line)
        if m:
            cur = {"id": "%s-%s" % (m.group(1), m.group(2)), "layer": LAYERS[m.group(1)],
                   "class": m.group(3), "title": m.group(4).strip(), "_line": n}
            rows.append(cur)
            continue
        if line.startswith("## ") or line.startswith("### ") or line.startswith("---"):
            cur = None
            continue
        if cur is not None and line.startswith("- "):
            key, sep, val = line[2:].partition(": ")
            if not sep:
                errors.append("line %d: field line without ': '" % n)
                continue
            if key not in FIELDS:
                errors.append("line %d: unknown field %r in %s" % (n, key, cur["id"]))
                continue
            if key in cur:
                errors.append("line %d: field %r repeated in %s" % (n, key, cur["id"]))
            cur[key] = val.strip()
    return rows, errors


def validate(rows):
    errors = []
    ids = [r["id"] for r in rows]
    for i in sorted(set(ids)):
        if ids.count(i) > 1:
            errors.append("duplicate id %s" % i)
    for r in rows:
        if r["class"] not in CLASSES:
            errors.append("%s: class %r not in the vocabulary" % (r["id"], r["class"]))
        for f in FIELDS:
            if not r.get(f):
                errors.append("%s: field %r missing or empty" % (r["id"], f))
        v = r.get("Lines", "")
        if v.isdigit():
            r["lines"] = int(v)
        elif v == "not reported":
            r["lines"] = None
        elif v.startswith("counted in "):
            r["lines"] = None
            if v[len("counted in "):] not in ids:
                errors.append("%s: Lines points at unknown row %r" % (r["id"], v))
        else:
            errors.append("%s: Lines must be an integer, 'not reported' or 'counted in <ID>', got %r" % (r["id"], v))
    for layer in LAYERS:
        nums = sorted(int(r["id"][2:]) for r in rows if r["id"][0] == layer)
        if nums != list(range(1, len(nums) + 1)):
            errors.append("layer %s: ids are not 01..%02d without gaps: %s" % (layer, len(nums), nums))
    return errors


def tallies(rows):
    def counts(sel):
        c = dict((k, 0) for k in CLASSES)
        for r in sel:
            c[r["class"]] += 1
        return c

    def fmt(prefix, c, total_word, total):
        return "%s: %s, %s %d" % (prefix, ", ".join("%s %d" % (k, c[k]) for k in CLASSES), total_word, total)

    sci = [r for r in rows if r["id"][0] in SCIENTIFIC]
    c_all, c_sci = counts(rows), counts(sci)
    lines = dict((k, 0) for k in CLASSES)
    for r in sci:
        if r.get("lines"):
            lines[r["class"]] += r["lines"]
    return [
        fmt("COUNTS all", c_all, "total", len(rows)),
        fmt("COUNTS scientific (O, W, S, M, C)", c_sci, "total", len(sci)),
        fmt("LINES scientific (O, W, S, M, C)", lines, "total reported", sum(lines.values())),
    ]


def main(argv):
    check = "--check" in argv
    text = SRC.read_text(encoding="ascii")
    rows, errors = parse(text)
    errors += validate(rows)
    want = tallies(rows)
    have = [ln.strip() for ln in text.split("\n") if ln.strip().startswith(("COUNTS ", "LINES "))]
    for w in want:
        print(w)
        if check and w not in have:
            errors.append("tally line not found in the document as computed: %s" % w)
    if check:
        for h in have:
            if h not in want:
                errors.append("document has a tally line that does not match: %s" % h)
    for e in errors:
        print("ERROR " + e)
    print("rows %d, errors %d" % (len(rows), len(errors)))
    if errors:
        return 1
    if not check:
        with open(OUT, "w", encoding="ascii", newline="\n") as f:
            for r in rows:
                rec = {"id": r["id"], "layer": r["layer"], "class": r["class"], "title": r["title"],
                       "does": r["Does"], "shown_correct": r["Shown correct"], "fit": r["Fit"],
                       "cost": r["Cost"], "coupling": r["Coupling"], "take": r["Take"],
                       "lines": r["lines"], "lines_note": r["Lines"], "source": r["Source"]}
                f.write(json.dumps(rec, sort_keys=True) + "\n")
        print("wrote %s" % OUT.name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
