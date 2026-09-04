"""G16 semantic-firewall test: PEW-NATIVE responses must contain no prose
from the human substrate — no claim text, no interpretation statements, no
canonical ontology labels, no world family names. Tested against the LIVE
substrate content (every >=5-char word appearing in claims/interpretations/
dim_terms is forbidden inside native responses, ids/hashes excluded)."""
import json
import re
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import db  # noqa: E402
from ew.client import CFG  # noqa: E402

BASE = f"http://localhost:{CFG['port']}"
HDRS = {"Authorization": f"Bearer {CFG['auth_token']}",
        "X-Prometheus-Machine": "M1", "X-Prometheus-Agent": "firewall-test"}


def forbidden_vocabulary(conn):
    words = set()
    with db.dict_cur(conn) as cur:
        cur.execute("SELECT text_canonical FROM ew.claims LIMIT 300")
        for r in cur.fetchall():
            words |= set(re.findall(r"[a-zA-Z]{5,}", r["text_canonical"].lower()))
        cur.execute("SELECT statement FROM ew.interpretations WHERE statement IS NOT NULL")
        for r in cur.fetchall():
            words |= set(re.findall(r"[a-zA-Z]{5,}", r["statement"].lower()))
        cur.execute("SELECT term_id, label FROM ew.dim_terms")
        for r in cur.fetchall():
            words |= set(re.findall(r"[a-zA-Z]{5,}",
                                    (r["term_id"] + " " + r["label"]).lower()))
        cur.execute("SELECT DISTINCT family FROM ew.fossil_worlds")
        for r in cur.fetchall():
            if r["family"]:
                words.add(r["family"].lower())
    # structural JSON/id tokens that are not semantics
    return words - {"sha256", "committed"}


def scan(obj, forbidden, path="$"):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            hits += scan(v, forbidden, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += scan(v, forbidden, f"{path}[{i}]")
    elif isinstance(obj, str):
        if re.match(r"^(sha256:)?[0-9a-f]{8,}$", obj) or \
           re.match(r"^(wld_|evt_|art_|fam:|out:|ENC-|I-|CB-)", obj):
            return hits
        for w in re.findall(r"[a-zA-Z]{5,}", obj.lower()):
            if w in forbidden:
                hits.append({"path": path, "word": w, "value": obj[:60]})
    return hits


def main():
    conn = db.connect()
    forbidden = forbidden_vocabulary(conn)
    conn.close()
    results = {}
    for ep in ("/api/v1/native/fossil/matrix",
               "/api/v1/native/fossil/anomalies?top=5"):
        r = requests.get(BASE + ep, headers=HDRS, timeout=30)
        r.raise_for_status()
        hits = scan(r.json(), forbidden)
        results[ep] = {"leaks": hits, "clean": not hits}
    # negative control: the HUMAN endpoint MUST trip the scanner
    r = requests.get(BASE + "/api/v1/search?q=retention&mode=lexical&k=2",
                     headers=HDRS, timeout=30)
    ctrl_hits = scan(r.json(), forbidden)
    results["_negative_control_human_endpoint"] = {
        "leaks_found_as_expected": len(ctrl_hits) > 0,
        "n": len(ctrl_hits)}
    ok = all(v.get("clean") for k, v in results.items()
             if k.startswith("/api")) and \
        results["_negative_control_human_endpoint"]["leaks_found_as_expected"]
    out = {"pass": ok, "forbidden_vocab_size": len(forbidden),
           "results": results}
    (HERE / "v3" / "firewall_audit.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({"pass": ok,
                      "native_clean": {k: v.get("clean") for k, v in
                                       results.items() if k.startswith("/api")},
                      "control_tripped": results["_negative_control_human_endpoint"]}))


if __name__ == "__main__":
    main()
