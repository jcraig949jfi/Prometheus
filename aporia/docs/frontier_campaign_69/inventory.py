"""
Extract the software inventory from the campaign dossiers.

69 dossiers of 20 to 45KB each is a corpus nobody will read twice. The one
part that must be machine-readable is PART 3, because that is the part that
says what can actually be installed and run, and it is the part that decays
fastest.

WHAT THIS DOES NOT DO. It does not guess. PART 3 has no enforced grammar --
the prompt asks for name, URL, language, licence, year and verdict on
separate lines, and different reports oblige to different degrees. A regex
that pairs the nth URL with the nth verdict will silently mis-attribute
MAINTAINED to an abandoned project the moment one entry omits a field, and
a wrong liveness verdict is worse than no verdict, because it sends someone
to install a dead repository.

So the extractor pairs a URL with a verdict ONLY when they are close enough
in the text to be unambiguous, and reports everything else as UNPAIRED for a
human to resolve. Coverage is measured and printed rather than assumed. A
dossier whose PART 3 cannot be parsed is named, not dropped.

    python aporia/docs/frontier_campaign_69/inventory.py
    python aporia/docs/frontier_campaign_69/inventory.py --unpaired
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOSSIERS = HERE / "dossiers"
OUT = HERE / "software_inventory.jsonl"

PART3_RE = re.compile(r"^#*\s*PART 3\.", re.M)
PART4_RE = re.compile(r"^#*\s*PART 4\.", re.M)
URL_RE = re.compile(r"https?://[^\s)>\]]+")
VERDICT_RE = re.compile(r"\b(MAINTAINED|DORMANT|ABANDONED)\b")
FIELD_RE = re.compile(r"^# Prompt \d+:\s*(.+?)\s*$", re.M)
# a verdict this far from its URL is not safely attributable to it
MAX_GAP = 400


def part3(text: str) -> str | None:
    a = PART3_RE.search(text)
    if not a:
        return None
    b = PART4_RE.search(text, a.end())
    return text[a.end() : b.start() if b else len(text)]


def extract(path: Path) -> dict:
    t = path.read_text(encoding="utf-8")
    fm = FIELD_RE.search(t)
    field = fm.group(1) if fm else path.stem

    seg = part3(t)
    if seg is None:
        return {"file": path.name, "field": field, "status": "NO_PART_3",
                "entries": [], "unpaired_urls": [], "unpaired_verdicts": 0}

    urls = list(URL_RE.finditer(seg))
    verdicts = list(VERDICT_RE.finditer(seg))
    used_v: set[int] = set()
    entries, unpaired = [], []

    for u in urls:
        # the verdict that belongs to a URL follows it and is the nearest one
        best, best_gap = None, MAX_GAP + 1
        for i, v in enumerate(verdicts):
            if i in used_v or v.start() < u.end():
                continue
            gap = v.start() - u.end()
            if gap < best_gap:
                best, best_gap, best_i = v, gap, i
        if best is None:
            unpaired.append(seg[max(0, u.start() - 60) : u.end()].strip()[-140:])
            continue
        used_v.add(best_i)
        window = seg[max(0, u.start() - 260) : u.end()]
        name = ""
        for line in reversed(window.split("\n")[:-1]):
            s = line.strip().strip("*#`- ").strip()
            if s and not s.lower().startswith(("http", "part ")) and len(s) < 80:
                name = s
                break
        entries.append({
            "name": name,
            "url": u.group(0).rstrip(".,;"),
            "verdict": best.group(1),
            "gap_chars": best_gap,
        })

    return {
        "file": path.name,
        "field": field,
        "status": "ok" if entries else "NO_ENTRIES",
        "entries": entries,
        "unpaired_urls": unpaired,
        "unpaired_verdicts": len(verdicts) - len(used_v),
    }


def main(argv: list[str]) -> int:
    show_unpaired = "--unpaired" in argv
    rows = [extract(p) for p in sorted(DOSSIERS.glob("*.md"))]

    with OUT.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    n_entries = sum(len(r["entries"]) for r in rows)
    n_unpaired_u = sum(len(r["unpaired_urls"]) for r in rows)
    n_unpaired_v = sum(r["unpaired_verdicts"] for r in rows)
    counts: dict[str, int] = {}
    for r in rows:
        for e in r["entries"]:
            counts[e["verdict"]] = counts.get(e["verdict"], 0) + 1

    for r in rows:
        if r["status"] != "ok":
            print(f"  !! {r['file']}: {r['status']}")

    print(f"\n{len(rows)} dossiers -> {n_entries} paired software entries")
    for v in ("MAINTAINED", "DORMANT", "ABANDONED"):
        print(f"    {v:<11} {counts.get(v, 0)}")
    print(f"  unpaired: {n_unpaired_u} urls with no verdict in range, "
          f"{n_unpaired_v} verdicts with no url")
    print(f"  written: {OUT}")
    print("\nPairing is proximity-based and therefore FALLIBLE. Before acting on")
    print("a verdict -- especially before skipping a tool marked ABANDONED --")
    print("open the dossier and read the entry. gap_chars is how far the verdict")
    print("sat from its URL; a large gap is a weaker pairing.")

    if show_unpaired:
        print("\nUNPAIRED URLS")
        for r in rows:
            for u in r["unpaired_urls"]:
                print(f"  {r['file']}: ...{u}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
