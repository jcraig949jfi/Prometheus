"""Migrate the 69 mined templates into the shape the real registry expects.

WHY THIS EXISTS. The templates were written against the ILLUSTRATIVE schema in
archaeon/docs/ROADMAP.md, which shows a FLAT param_space. The registry that
Archaeon has since built (archaeon/producer/templates.py, and the admitted
bitstring.uniform.v0) expects a NESTED one:

    "param_space": {"payload": {<exactly the kind's params>},
                    "world":   {"seed_root": {...}}}

templates.check() reads param_space["payload"] and compares it to the kind's
exact parameter set. Against a flat template it sees an EMPTY payload, so all
69 fail, including the seven that name implemented kinds. Measured before
writing this: 69 load, 0 runnable, 7 failing in the archaeon lane on shape and
62 in the vivarium lane on a missing kind.

WHAT THIS DOES, AND WHAT IT REFUSES TO DO.

It restructures. It adds `registry_version`. It adds a `world.seed_root` block
copied from the frozen baseline's declared range.

It does NOT invent destroyed science. Where the research tool destroyed a
parameter's value, that axis is either left null, or filled ONLY when a
defensible bench-native value exists, and every such fill is recorded by name
in `_design_choices` with its justification. Nothing introduced here is
presented as recovered.

Status stays PROPOSED for all 69. Admission is a human act.

    python migrate_to_registry_shape.py --out <dir> [--apply]
"""
import argparse
import io
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("PROMETHEUS_REPO") or HERE.parents[4])
INBOX = REPO / "archaeon" / "templates" / "inbox"

REGISTRY_VERSION = "archaeon.template.v0"

#: Copied from the ADMITTED frozen baseline bitstring.uniform.v0, so a mined
#: template varies the world on exactly the axis the bench already varies it on.
#: This is a NEW DESIGN CHOICE for every template that did not declare a world.
WORLD_DEFAULT = {"seed_root": {"int_range": [100000, 999999]}}
WORLD_JUSTIFY = ("world.seed_root added, range copied verbatim from the "
                 "ADMITTED frozen baseline bitstring.uniform.v0. The mined "
                 "template declared no world because the mining deck wrongly "
                 "told it to declare payload parameters only.")

#: Fills for axes whose values a source marker destroyed, used ONLY for kinds
#: the bench implements, and ONLY where the bench itself already declares the
#: value somewhere. Anything not listed here stays null.
NATIVE_FILLS = {
    ("evaluate_bitstring", "length"): (
        {"choices": [16, 24, 32]},
        "lengths copied from ALLOWED_LENGTHS in archaeon/producer/"
        "contract.py, which is the producer's own declared space"),
    ("evaluate_bitstring", "bits"): (
        {"uniform_bits": "length"},
        "the only bits spec the registry's draw vocabulary supports for a "
        "bitstring of declared length; matches the frozen baseline"),
}


def migrate(t):
    """Return (new_template, design_choices, notes)."""
    choices, notes = [], []
    t = json.loads(json.dumps(t))          # never mutate the caller's dict
    space = t.get("param_space") or {}

    # already nested? then only top up the missing pieces
    if "payload" in space or "world" in space:
        payload = dict(space.get("payload") or {})
        world = dict(space.get("world") or {})
        notes.append("template was already nested")
    else:
        payload = {k: v for k, v in space.items() if k != "seed_root"}
        world = {}
        if "seed_root" in space:
            world["seed_root"] = space["seed_root"]
            notes.append("seed_root moved from payload to world")

    if not world:
        world = json.loads(json.dumps(WORLD_DEFAULT))
        choices.append(WORLD_JUSTIFY)

    kind = t.get("kind")

    # COHERENCE FIRST, and this is a correction to an earlier version of this
    # script. When `bits` is a literal choice list, `length` is NOT free: it is
    # DETERMINED by the data that survived, and filling it from the producer's
    # generic ALLOWED_LENGTHS introduces exactly the F-1 silent-ceiling defect
    # documented in 02_FINDINGS. A 16-character candidate drawn against
    # length 32 is scored over the overlap and divided by 32, so it is capped
    # at 0.5 and `solved` becomes unreachable, with no error anywhere.
    # Recovering the implied length is a REPAIR, not a design choice: the value
    # is entailed by data the template still carries.
    if kind == "evaluate_bitstring":
        bspec = payload.get("bits") or {}
        lits = bspec.get("choices") if isinstance(bspec, dict) else None
        if isinstance(lits, list) and lits and all(isinstance(x, str) for x in lits):
            lens = sorted({len(x) for x in lits})
            if len(lens) == 1:
                payload["length"] = {"choices": [lens[0]]}
                choices.append(
                    "payload.length: REPAIR, not a design choice. Set to %d "
                    "because it is entailed by the surviving bits literals; "
                    "any other value silently caps the score at "
                    "len(bits)/length (see F-1)." % lens[0])
            else:
                notes.append(
                    "payload.bits carries literals of DIFFERING lengths %s, so "
                    "no single length is coherent with them. Left for an "
                    "operator; filling it would guarantee a capped score for "
                    "at least one draw." % lens)

    for axis, spec in list(payload.items()):
        if not isinstance(spec, dict):
            continue
        if any(v is None for v in spec.values()):
            fill = NATIVE_FILLS.get((kind, axis))
            if fill:
                payload[axis] = json.loads(json.dumps(fill[0]))
                choices.append("payload.%s: %s" % (axis, fill[1]))
            else:
                notes.append("payload.%s left NULL: its value was destroyed "
                             "in the source report and no bench-native value "
                             "exists to justify a fill" % axis)

    t["param_space"] = {"payload": payload, "world": world}
    t["registry_version"] = REGISTRY_VERSION
    t["status"] = "PROPOSED"
    t["admitted_by"] = None
    t["admitted_at"] = None

    ing = dict(t.get("_ingest") or {})
    if choices:
        ing["design_choices"] = choices
        ing["design_choices_note"] = (
            "Values introduced by Herakles on 2026-09-06 during the "
            "registry-shape migration. These are NEW DESIGN CHOICES, not "
            "recovered data, and each names its justification.")
    if notes:
        ing["migration_notes"] = notes
    ing["migrated_from"] = "flat param_space (ROADMAP illustrative schema)"
    t["_ingest"] = ing
    return t, choices, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "migrated"))
    ap.add_argument("--apply", action="store_true",
                    help="write back into the inbox instead of --out")
    args = ap.parse_args()
    out = INBOX if args.apply else Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(REPO / "vivarium"))
    sys.path.insert(0, str(REPO))
    from archaeon.producer import templates as T

    n = filled = still_null = 0
    runnable_before = runnable_after = 0
    for p in sorted(INBOX.glob("*.json")):
        t = json.loads(p.read_text(encoding="utf-8"))
        try:
            if T.check(t)["runnable"]:
                runnable_before += 1
        except Exception:
            pass
        new, choices, notes = migrate(t)
        n += 1
        if any("payload." in c for c in choices):
            filled += 1
        if any("left NULL" in x for x in notes):
            still_null += 1
        try:
            if T.check(new)["runnable"]:
                runnable_after += 1
        except Exception:
            pass
        io.open(out / p.name, "w", encoding="utf-8", newline="").write(
            json.dumps(new, indent=2, sort_keys=True) + "\n")

    print("templates migrated ................ %d" % n)
    print("runnable BEFORE (real registry) ... %d" % runnable_before)
    print("runnable AFTER  (real registry) ... %d" % runnable_after)
    print("had a destroyed axis filled ....... %d  (labelled design choices)"
          % filled)
    print("still carrying a NULL axis ........ %d  (left destroyed on purpose)"
          % still_null)
    print("written to ........................ %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
