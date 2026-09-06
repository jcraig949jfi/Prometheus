"""Turn returned mining reports into PROPOSED templates and expansion requests.

Reads the NN_*.md reports in this directory, extracts the delimited blocks the
deck asked for, validates each template against Vivarium's live kind registry,
and writes:

    archaeon/templates/inbox/<template_id>.json      one PROPOSED template each
    EXPANSION_REQUESTS.md                            the consolidated register
    INGEST_REPORT.md                                 what was accepted, what was
                                                     rejected, and why

NOTHING here admits a template. Admission is a human act, per
archaeon/docs/ROADMAP.md. Everything written to the inbox is PROPOSED and
nothing in the inbox is drawn from.

VALIDATION IS DELIBERATELY STRICT. Vivarium's registry declares the EXACT
parameter set of each kind, and rejects both a missing and an extra parameter.
A template whose param_space does not match its kind exactly would be admitted
into a registry and then fail at execution, so it is rejected here instead,
with the reason recorded. A template naming a kind that does not exist is NOT
rejected -- that is the expansion case the roadmap asks for, and it is kept and
flagged.

    python ingest.py [--dry-run]
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Repo root is four levels up from this file. PROMETHEUS_REPO overrides it,
# which is what lets this script be exercised against a fixture directory
# outside the tree instead of only against live report output.
REPO = os.environ.get("PROMETHEUS_REPO") or os.path.abspath(
    os.path.join(HERE, "..", "..", "..", ".."))
INBOX = os.path.join(REPO, "archaeon", "templates", "inbox")

TEMPLATE_RE = re.compile(r"BEGIN_TEMPLATE\s*(.*?)\s*END_TEMPLATE", re.S)
EXPANSION_RE = re.compile(r"BEGIN_EXPANSION\s*(.*?)\s*END_EXPANSION", re.S)
REQUIRED = ("template_id", "kind", "param_space", "origin", "status",
            "rationale")
#: Axes a template may declare that are NOT payload parameters. `world.seed_root`
#: is part of the spec but outside `work.payload`, and it is a real axis of the
#: declared space, so a template that varies it is correct, not malformed.
WORLD_AXES = frozenset({"seed_root"})


def load_registry():
    """Vivarium's live kind registry. Ground truth, never transcribed."""
    sys.path.insert(0, os.path.join(REPO, "vivarium"))
    from viv import kinds as K  # noqa: E402
    return K.REGISTRY


def strip_fences(raw):
    """A model may wrap the JSON in a code fence despite being asked not to."""
    s = raw.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    return s.strip()


#: A run's template blocks are destroyed if the research agent's grounding layer
#: overwrites square-bracketed content with source markers. The deck therefore
#: asks for ranges and choice lists as QUOTED STRINGS. These decode them back
#: into real JSON, so the stored template is normal data and the bracket-free
#: encoding never leaves this script.
RANGE_RE = re.compile(r"^\s*(-?[\d.]+)\s*(?:to|\.\.|-)\s*(-?[\d.]+)\s*$", re.I)
CITE_RE = re.compile(r"\[\s*cite[^\]]*\]", re.I)


def _num(tok):
    tok = tok.strip()
    try:
        return int(tok)
    except ValueError:
        pass
    try:
        return float(tok)
    except ValueError:
        return tok


#: Source markers sitting in a JSON VALUE position (right after a colon) make
#: the block unparseable. Replacing them with null recovers the template's
#: structure -- its kind, its axis names, its rationale -- while recording that
#: the value itself is gone. Markers inside a string are prose noise and are
#: simply removed. Nothing is ever reconstructed: a destroyed number stays null
#: and the template is flagged INCOMPLETE.
CITE_VALUE_RE = re.compile(r"(:\s*)\[\s*cite[^\]]*\]", re.I)
#: The renderer sometimes deletes the value outright rather than replacing it,
#: leaving a key with an empty slot: a colon followed straight by a comma or a
#: closing brace. That is the same loss, and it gets the same null.
EMPTY_VALUE_RE = re.compile(r"(:\s*)(?=[,}])")


def repair_citations(body):
    """Return (repaired_text, was_repaired)."""
    # a lambda, not a backreference string: the replacement must contain
    # no backslash escape for the surrounding tooling to mangle
    fixed, n = CITE_VALUE_RE.subn(lambda m: m.group(1) + "null", body)
    fixed2, n2 = CITE_RE.subn("", fixed)
    fixed3, n3 = EMPTY_VALUE_RE.subn(lambda m: m.group(1) + "null", fixed2)
    return fixed3, bool(n or n2 or n3)


def decode_axis(spec):
    """Decode one param_space axis. Returns (decoded, note_or_None).

    Leaves anything it does not recognise untouched: a silent reinterpretation
    would be worse than an undecoded string an operator can read.
    """
    if not isinstance(spec, dict):
        return spec, None
    out, note = {}, None
    for k, v in spec.items():
        if not isinstance(v, str):
            out[k] = v
            continue
        if CITE_RE.search(v):
            out[k] = None
            note = ("value destroyed by a source marker in the returned "
                    "report; NOT reconstructed, and must be supplied by the "
                    "operator before admission")
            continue
        m = RANGE_RE.match(v)
        if m and k.endswith("range"):
            out[k] = [_num(m.group(1)), _num(m.group(2))]
        elif k == "choices":
            parts = [t for t in (x.strip() for x in v.split(",")) if t]
            out[k] = [_num(t) for t in parts] if parts else v
        else:
            out[k] = v
    return out, note


def decode_param_space(space):
    """Decode every axis. Returns (decoded_space, list_of_incomplete_axes)."""
    if not isinstance(space, dict):
        return space, []
    out, incomplete = {}, []
    for axis, spec in space.items():
        dec, note = decode_axis(spec)
        out[axis] = dec
        if note:
            incomplete.append(axis)
    return out, incomplete


def validate(tpl, registry):
    """Reasons this template cannot go to the inbox as-is. Empty list = ok.

    Returns (reasons, flags). A flag is a note that travels WITH an accepted
    template rather than blocking it.
    """
    reasons, flags = [], []
    for f in REQUIRED:
        if f not in tpl:
            reasons.append("missing required field %r" % f)
    if reasons:
        return reasons, flags

    tid = tpl["template_id"]
    # Underscores are normal in the first segment: kinds themselves are named
    # random_walk_v0, and ids like version_space_search.v0 are correct. An
    # earlier version of this rule allowed them only after the first dot.
    if not re.match(r"^[a-z0-9_]+(\.[a-z0-9_]+)*\.v\d+$", tid or ""):
        reasons.append("template_id %r is not a lowercase dotted id ending "
                       ".vN" % tid)
    if tpl.get("status") != "PROPOSED":
        reasons.append("status is %r; anything arriving here is PROPOSED"
                       % tpl.get("status"))
    if tpl.get("admitted_by") or tpl.get("admitted_at"):
        reasons.append("carries admission fields; admission is a human act")

    space = tpl.get("param_space")
    if not isinstance(space, dict):
        reasons.append("param_space is not an object")
        return reasons, flags

    kind = tpl.get("kind")
    entry = registry.get(kind)
    if entry is None:
        flags.append("EXPANSION: kind %r is not implemented by Vivarium; this "
                     "template is an expansion request by definition" % kind)
    else:
        if getattr(entry, "retired", False):
            reasons.append("kind %r is RETIRED and cannot be admitted again"
                           % kind)
        # A template's param_space spans MORE than the payload. `seed_root` is
        # a world field, not a payload parameter, and the live generator draws
        # it as a first-class axis alongside length and bits
        # (archaeon/producer/randomgen.py draw()). The roadmap's own canonical
        # example, bitstring.uniform.v0, declares exactly {length, seed_root,
        # bits}. An earlier version of this check compared param_space against
        # the payload set alone and would have rejected the registry's founding
        # example, which is the signature of a rule that cannot pass.
        declared = set(entry.params)
        got = set(space)
        missing = sorted(declared - got)
        extra = sorted(got - declared - WORLD_AXES)
        if missing:
            reasons.append("param_space is missing %s, which kind %r consumes "
                           "and for which no executor default exists"
                           % (missing, kind))
        if extra:
            reasons.append("param_space has extra %s, which is neither a "
                           "payload parameter of kind %r nor a world axis %s"
                           % (extra, kind, sorted(WORLD_AXES)))
        if not entry.implemented:
            flags.append("EXPANSION: kind %r has a known contract but no "
                         "executor here" % kind)

    origin = tpl.get("origin") or {}
    if origin.get("source") != "LITERATURE":
        reasons.append("origin.source is %r; this miner writes LITERATURE"
                       % origin.get("source"))
    for f in ("field", "reference", "proposed_by"):
        if not origin.get(f):
            reasons.append("origin.%s is empty" % f)
    if not (tpl.get("rationale") or "").strip():
        reasons.append("rationale is empty")
    return reasons, flags


def parse_expansion(block):
    """The expansion block is line-oriented with continuation lines."""
    out, key = {}, None
    for line in block.split("\n"):
        m = re.match(r"^\s*([A-Z_]+):\s*(.*)$", line)
        if m and m.group(1) in ("FIELD", "LACKS", "WHY", "SMALLEST_FORM",
                                "BLOCKS", "EVIDENCE"):
            key = m.group(1)
            out[key] = m.group(2).strip()
        elif key and line.strip():
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reports", default=HERE,
                    help="directory holding the NN_*.md reports; defaults to "
                         "this directory. The v1 run's reports live in a "
                         "subdirectory because their template blocks were "
                         "corrupted, but their expansion blocks are intact and "
                         "worth reading.")
    args = ap.parse_args()
    reports_dir = os.path.abspath(args.reports)

    registry = load_registry()
    reports = sorted(f for f in os.listdir(reports_dir)
                     if re.match(r"^\d\d_.*\.md$", f))
    if not reports:
        print("no NN_*.md reports in %s" % reports_dir)
        return 1

    accepted, rejected, expansions = [], [], []
    for r in reports:
        text = io.open(os.path.join(reports_dir, r),
                       encoding="utf-8").read()
        for raw in TEMPLATE_RE.findall(text):
            body = strip_fences(raw)
            repaired = False
            try:
                tpl = json.loads(body)
            except Exception:
                body2, repaired = repair_citations(body)
                try:
                    tpl = json.loads(body2)
                except Exception as e:
                    rejected.append(dict(
                        report=r, template_id="<unparseable>",
                        reasons=["not valid JSON even after removing source "
                                 "markers: %s" % e], body=body[:400]))
                    continue
            space, incomplete = decode_param_space(tpl.get("param_space"))
            if isinstance(space, dict):
                tpl["param_space"] = space
            reasons, flags = validate(tpl, registry)
            if repaired:
                flags.append(
                    "REPAIRED: source markers were removed from this block to "
                    "make it parse. Structure is the report's; any value that "
                    "a marker had overwritten is null, never guessed.")
            if incomplete:
                flags.append(
                    "INCOMPLETE: axes %s lost their values to source markers "
                    "in the returned report. The axis names are real; the "
                    "numbers are NOT reconstructed and must be set by the "
                    "operator before admission." % sorted(incomplete))
            rec = dict(report=r, template_id=tpl.get("template_id"),
                       kind=tpl.get("kind"), flags=flags, tpl=tpl)
            if reasons:
                rec["reasons"] = reasons
                rejected.append(rec)
            else:
                accepted.append(rec)
        for raw in EXPANSION_RE.findall(text):
            e = parse_expansion(raw)
            if e.get("FIELD") and e.get("LACKS"):
                e["report"] = r
                expansions.append(e)

    # ---- collisions: two reports proposing the same id are a real event
    seen = {}
    for rec in accepted:
        seen.setdefault(rec["template_id"], []).append(rec["report"])
    collisions = {k: v for k, v in seen.items() if len(v) > 1}

    print("reports read      : %d" % len(reports))
    print("templates accepted: %d" % len(accepted))
    print("templates rejected: %d" % len(rejected))
    print("expansion requests: %d" % len(expansions))
    print("id collisions     : %d" % len(collisions))
    runnable = [a for a in accepted if not a["flags"]]
    print("runnable on the bench as it stands: %d of %d"
          % (len(runnable), len(accepted)))

    if args.dry_run:
        for rec in rejected:
            print("  REJECT %-40s %s" % (rec.get("template_id"),
                                         "; ".join(rec["reasons"])[:120]))
        return 0

    os.makedirs(INBOX, exist_ok=True)
    written = []
    for rec in accepted:
        tid = rec["template_id"]
        path = os.path.join(INBOX, tid + ".json")
        if tid in collisions and os.path.exists(path):
            tid = "%s__%s" % (tid, rec["report"][:2])
            path = os.path.join(INBOX, tid + ".json")
        tpl = dict(rec["tpl"])
        tpl["_ingest"] = dict(
            source_report=rec["report"],
            deck="roles/Herakles/deep_research/2026-09-06_archaeon_template_"
                 "mining/deck.md",
            flags=rec["flags"],
            note="PROPOSED by a literature miner. Nothing in the inbox is "
                 "drawn from. Admission is a human act.")
        io.open(path, "w", encoding="utf-8", newline="").write(
            json.dumps(tpl, indent=2) + "\n")
        written.append(path)
    print("wrote %d templates to %s" % (len(written), INBOX))

    # ---- expansion register
    lines = ["# Expansion requests from literature mining",
             "",
             "Generated by `ingest.py` from the 2026-09-06 mining deck.",
             "Each entry is the SMALLEST capability a field says the bench",
             "lacks. These are measurements of a gap, not verdicts, and none",
             "of them is a commitment to build anything.",
             ""]
    by_lack = {}
    for e in expansions:
        by_lack.setdefault(e["LACKS"], []).append(e)
    for i, (lack, group) in enumerate(sorted(by_lack.items()), start=1):
        fields = sorted({g.get("FIELD", "") for g in group})
        lines += ["## %d. %s" % (i, lack), "",
                  "**Raised by:** " + ", ".join(fields), ""]
        g = group[0]
        for k, label in (("WHY", "Why"), ("SMALLEST_FORM", "Smallest form"),
                         ("BLOCKS", "Also blocks"), ("EVIDENCE", "Evidence")):
            if g.get(k):
                lines += ["**%s:** %s" % (label, g[k]), ""]
    io.open(os.path.join(HERE, "EXPANSION_REQUESTS.md"), "w",
            encoding="utf-8", newline="").write("\n".join(lines))

    # ---- ingest report: rejections are the interesting part
    rep = ["# Ingest report", "",
           "reports read: %d | accepted: %d | rejected: %d | expansions: %d"
           % (len(reports), len(accepted), len(rejected), len(expansions)),
           "", "Runnable on the bench as it stands: %d of %d accepted."
           % (len(runnable), len(accepted)), ""]
    if collisions:
        rep += ["## Template id collisions", ""]
        for k, v in sorted(collisions.items()):
            rep.append("- `%s` proposed by %s" % (k, ", ".join(v)))
        rep.append("")
    if rejected:
        rep += ["## Rejected", "",
                "A rejection is a defect in the proposal, not in the field.",
                ""]
        for rec in rejected:
            rep.append("- **%s** (%s): %s"
                       % (rec.get("template_id"), rec["report"],
                          "; ".join(rec["reasons"])))
        rep.append("")
    if any(a["flags"] for a in accepted):
        rep += ["## Accepted, but not runnable today", "",
                "These name a kind the bench does not implement. Per the",
                "roadmap that makes each one an expansion request.", ""]
        for a in accepted:
            if a["flags"]:
                rep.append("- **%s** -> kind `%s`" % (a["template_id"],
                                                      a["kind"]))
        rep.append("")
    io.open(os.path.join(HERE, "INGEST_REPORT.md"), "w", encoding="utf-8",
            newline="").write("\n".join(rep))
    print("wrote EXPANSION_REQUESTS.md and INGEST_REPORT.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
