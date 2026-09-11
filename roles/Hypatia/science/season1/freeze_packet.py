"""Freeze an admissible evidence packet from a closed Prometheus case.

Preregistration: roles/Hypatia/science/season1/PREREGISTRATION.md section 3.

The splitting is DELIBERATELY DETERMINISTIC and not hand-curated. If this
seat hand-split the evidence into units it would hold a degree of freedom
that lets it shape a packet until the ladder becomes easy -- a quiet form of
the exact cheat this season exists to detect. The splitter is a fixed rule,
versioned, and the same rule runs on every case including the controls.

Two properties are measured at freeze time and stored in the packet, because
a gate that cannot see its own chance floor is decorative:

  terminal_leak   does any single evidence unit already contain every
                  required token of the terminal ruling? If yes, terminal
                  reconstruction is obtainable by copying and G6 proves
                  nothing for that case.
  load_bearing    the unit whose removal should break reconstruction. Named
                  at freeze time, BEFORE the stripped CHEAT packet is built,
                  so the cheat cannot be tuned afterwards.

Usage:
    python roles/Hypatia/science/season1/freeze_packet.py
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import unicodedata

SPLITTER_VERSION = "hypatia-freeze-1.0"
REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
AUTOPSIES = REPO_ROOT / "engine" / "ledger" / "AGENT_AUTOPSIES.jsonl"
OUT_DIR = pathlib.Path(__file__).resolve().parent / "packets"

# Fields admitted as evidence. failure_class is EXCLUDED: it is the terminal
# ruling, and a packet that carries its own conclusion makes the experiment
# circular (preregistration s3.4).
EVIDENCE_FIELDS = ("design_choice", "boundary_localization",
                   "representation_hint", "evidence")

MIN_UNIT_CHARS = 40      # below this a "unit" is a fragment, not an assertion
MIN_UNITS = 4            # admissibility floor, preregistration s3

STOPWORDS = {"a", "an", "the", "with", "in", "of", "and", "or", "to",
             "for", "on", "by", "is", "as", "at", "its", "it"}


def to_ascii(s: str):
    """Normalize to ASCII, reporting whether anything changed.

    The source ledger carries mangled em-dashes. Provenance stays honest only
    if the hash is over what was actually frozen AND the edit is recorded.
    """
    original_len = len(s.encode("utf-8"))
    out = unicodedata.normalize("NFKD", s)
    out = (out.replace("—", "--").replace("–", "-")
              .replace("‘", "'").replace("’", "'")
              .replace("“", '"').replace("”", '"')
              .replace("�", "--"))
    out = out.encode("ascii", "ignore").decode("ascii")
    out = re.sub(r"\s+", " ", out).strip()
    return out, (out.encode("utf-8") != s.encode("utf-8")), original_len


def split_units(text: str):
    """Fixed rule: split on sentence enders and semicolons at a space boundary.

    Not clever. Not tuned. The same rule for every case.
    """
    parts = re.split(r"(?<=[.;])\s+", text)
    merged, buf = [], ""
    for p in parts:
        buf = (buf + " " + p).strip() if buf else p.strip()
        if len(buf) >= MIN_UNIT_CHARS:
            merged.append(buf)
            buf = ""
    if buf:
        if merged:
            merged[-1] = (merged[-1] + " " + buf).strip()
        else:
            merged.append(buf)
    return [m for m in merged if m]


def required_tokens(failure_class: str):
    """Tokens the terminal step must contain. Taken from the class NAME only,
    i.e. the text before any parenthetical gloss."""
    head = failure_class.split("(")[0]
    head = head.split(" - ")[0]
    ascii_head, _, _ = to_ascii(head)
    toks = re.split(r"[^A-Za-z]+", ascii_head.lower())
    return sorted({t for t in toks if t and t not in STOPWORDS and len(t) > 1})


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build_packet(row: dict) -> dict:
    units, idx = [], 1
    for field in EVIDENCE_FIELDS:
        raw = row.get(field)
        if not raw:
            continue
        ascii_text, changed, orig_len = to_ascii(str(raw))
        for unit in split_units(ascii_text):
            units.append({
                "id": "EV%d" % idx,
                "text": unit,
                "source_path": "engine/ledger/AGENT_AUTOPSIES.jsonl",
                "locator": "agent_id=%s field=%s" % (row["agent_id"], field),
                "sha256": sha256_text(unit),
                "ascii_normalized": changed,
                "source_field_utf8_bytes": orig_len,
            })
            idx += 1

    ruling_ascii, _, _ = to_ascii(str(row["failure_class"]))
    req = required_tokens(row["failure_class"])

    # Chance floor: can any single unit hand over the whole ruling?
    leaks = [u["id"] for u in units
             if all(t in u["text"].lower() for t in req)]

    # Load-bearing unit: the one carrying the most required tokens, ties
    # broken by length. Named NOW, before the stripped packet exists.
    def score(u):
        return (sum(1 for t in req if t in u["text"].lower()), len(u["text"]))
    load_bearing = max(units, key=score)["id"] if units else None

    return {
        "packet_id": "PKT-%s" % row["agent_id"].upper(),
        "case_id": row["agent_id"],
        "splitter_version": SPLITTER_VERSION,
        "frozen_from": "engine/ledger/AGENT_AUTOPSIES.jsonl",
        "source_row": {"agent_id": row["agent_id"],
                       "autopsied": row.get("autopsied"),
                       "by": row.get("by")},
        "terminal_ruling": {"text": ruling_ascii, "required_tokens": req},
        "admissible": len(units) >= MIN_UNITS,
        "unit_count": len(units),
        "terminal_leak": bool(leaks),
        "terminal_leak_units": leaks,
        "load_bearing_unit": load_bearing,
        "evidence": units,
    }


def main():
    rows = {}
    for line in AUTOPSIES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            r = json.loads(line)
            rows[r["agent_id"]] = r

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = ["Atalanta", "Hypatia", "Nephele", "Iris"]
    print("%-10s %6s %6s %6s %-14s %s" %
          ("case", "units", "adm", "leak", "load_bearing", "required_tokens"))
    print("-" * 88)
    index = []
    for c in cases:
        if c not in rows:
            print("%-10s MISSING FROM LEDGER -- INDETERMINATE" % c)
            continue
        p = build_packet(rows[c])
        path = OUT_DIR / ("%s.json" % p["packet_id"])
        body = json.dumps(p, indent=2, sort_keys=True) + "\n"
        path.write_text(body, encoding="utf-8")
        print("%-10s %6d %6s %6s %-14s %s" %
              (c, p["unit_count"], p["admissible"], p["terminal_leak"],
               p["load_bearing_unit"],
               ",".join(p["terminal_ruling"]["required_tokens"])))
        index.append({"packet_id": p["packet_id"], "case_id": c,
                      "path": path.relative_to(REPO_ROOT).as_posix(),
                      "sha256": sha256_text(body),
                      "unit_count": p["unit_count"],
                      "admissible": p["admissible"],
                      "terminal_leak": p["terminal_leak"],
                      "load_bearing_unit": p["load_bearing_unit"]})

    (OUT_DIR / "INDEX.json").write_text(
        json.dumps({"splitter_version": SPLITTER_VERSION,
                    "min_unit_chars": MIN_UNIT_CHARS,
                    "min_units": MIN_UNITS,
                    "packets": index}, indent=2) + "\n", encoding="utf-8")
    print()
    n_adm = sum(1 for i in index if i["admissible"])
    n_leak = sum(1 for i in index if i["terminal_leak"])
    print("admissible packets: %d of %d (floor %d units)" %
          (n_adm, len(index), MIN_UNITS))
    print("packets whose ruling leaks into a single unit: %d" % n_leak)
    if n_leak:
        print("  -> G6 proves nothing for those cases; reported, not hidden.")
    print("index: %s" % (OUT_DIR / "INDEX.json").relative_to(REPO_ROOT).as_posix())


if __name__ == "__main__":
    main()
