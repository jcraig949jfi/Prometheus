"""Census: how many of the R1-R5 ladder steps in Hypatia's Type-D deep-research
reports could a corpus ingester actually parse?

Hypatia's whole product was step-tagged worked solutions, emitted as strict
JSONL (one object per proof step) inside deep-research reports. The
2026-06-24 dossier asserted the output was "unparseable" because citation
markers leaked into the JSON (depends_on: [cite: 1]). That was a qualitative
claim about one report. This measures it over every report the seat ever
produced.

Run from anywhere:  python roles/Hypatia/science/ladder_parse_census.py
Writes rows next to itself so the verdict ships with its evidence.
"""
import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
REPORT_GLOB = "aporia/docs/deep_research_reports/*/*hypatia*.md"
ROWS_OUT = pathlib.Path(__file__).resolve().parent / "ladder_parse_census.json"


def is_step_line(s):
    """A ladder step line is a JSON object carrying both "step" and "ladder"."""
    return s.startswith("{") and '"step"' in s and '"ladder"' in s


def census(repo_root=REPO_ROOT):
    rows = []
    for path in sorted(repo_root.glob(REPORT_GLOB)):
        ok = bad = 0
        bad_examples = []
        for line in path.read_text(encoding="utf-8").splitlines():
            s = line.strip().strip("`")
            if not is_step_line(s):
                continue
            try:
                json.loads(s)
                ok += 1
            except Exception:
                bad += 1
                if len(bad_examples) < 2:
                    bad_examples.append(s[:160])
        rows.append({
            "report": path.name,
            "steps_emitted": ok + bad,
            "steps_parseable": ok,
            "steps_unparseable": bad,
            "unparseable_examples": bad_examples,
        })
    return rows


def controls():
    """The instrument must be able to fail, to detect real success, and to
    detect a cheat. Base role section 2 makes the cheat control mandatory."""
    out = {}
    # NEGATIVE: prose that is not a step line must not be counted at all.
    out["negative_no_false_positives"] = not is_step_line(
        "The load-bearing move is the Palfy-Pudlak reduction.")
    # POSITIVE: a well-formed step line must parse.
    good = '{"step": 1, "claim": "c", "justification": "j", "ladder": "R2", "depends_on": [1]}'
    try:
        json.loads(good)
        out["positive_detects_valid_step"] = is_step_line(good)
    except Exception:
        out["positive_detects_valid_step"] = False
    # CHEAT: success deliberately injected -- the exact malformation this
    # census exists to catch must be scored unparseable, not waved through.
    cheat = '{"step": 1, "claim": "c", "justification": "j", "ladder": "R2", "depends_on": [cite: 1]}'
    try:
        json.loads(cheat)
        out["cheat_rejects_cite_leak"] = False
    except Exception:
        out["cheat_rejects_cite_leak"] = is_step_line(cheat)
    return out


def main():
    rows = census()
    ctl = controls()
    tot_e = sum(r["steps_emitted"] for r in rows)
    tot_ok = sum(r["steps_parseable"] for r in rows)
    print("%-46s %6s %6s %6s" % ("report", "steps", "parse", "fail"))
    print("-" * 68)
    for r in rows:
        print("%-46s %6d %6d %6d" % (r["report"][:46], r["steps_emitted"],
                                     r["steps_parseable"], r["steps_unparseable"]))
    print("-" * 68)
    print("%-46s %6d %6d %6d" % ("TOTAL", tot_e, tot_ok, tot_e - tot_ok))
    print()
    print("reports found:      %d" % len(rows))
    if tot_e:
        print("parseable fraction: %d/%d = %.1f%%" % (tot_ok, tot_e, 100.0 * tot_ok / tot_e))
    else:
        print("parseable fraction: INDETERMINATE (0 eligible step lines found)")
    print()
    print("controls: " + ", ".join("%s=%s" % (k, v) for k, v in ctl.items()))
    if not all(ctl.values()):
        print("CONTROL FAILURE -- the census is not trustworthy; do not quote it.")
    ROWS_OUT.write_text(json.dumps(
        {"reports": rows,
         "totals": {"steps_emitted": tot_e, "steps_parseable": tot_ok,
                    "steps_unparseable": tot_e - tot_ok},
         "controls": ctl},
        indent=2) + "\n", encoding="utf-8")
    print("rows written: %s" % ROWS_OUT.relative_to(REPO_ROOT).as_posix())


if __name__ == "__main__":
    main()
