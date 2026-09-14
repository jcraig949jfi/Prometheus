"""File a lane-C receipt from a JSON file: {"receipt": {...}, "board": {...}}.

usage: PM_LANE=C PM_TAG=<tag> python -m primordial.brain.file_receipt <path.json>
"""
from __future__ import annotations

import json
import sys

from primordial.bus import bus
from primordial.core.contract import board_eligible, validate_receipt


def main(argv: list[str]) -> int:
    doc = json.load(open(argv[0], encoding="utf-8"))
    rec = validate_receipt(doc["receipt"])
    print("board eligible:", board_eligible(rec))
    print(bus.receipt(rec, board=doc.get("board")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
