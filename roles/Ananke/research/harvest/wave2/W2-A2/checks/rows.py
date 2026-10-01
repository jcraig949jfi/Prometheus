import gzip, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[7]
ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
_R = None
def rows():
    global _R
    if _R is None:
        _R = [json.loads(l) for l in gzip.open(ROWS, "rt") if l.strip()]
    return _R
