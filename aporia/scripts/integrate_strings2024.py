"""Integrate Strings 2024: 100 Open Questions into physics catalog."""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "data"))
from strings2024_extracted import QUESTIONS

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHYS_JSONL = ROOT / "physics" / "questions.jsonl"

TOPIC_MAP = {
    "holography": "holography", "duality": "duality",
    "string_compactification": "string_compactification",
    "cosmology": "cosmology", "black_holes": "black_holes",
    "quantum_gravity": "quantum_gravity",
    "scattering_amplitudes": "scattering_amplitudes",
    "quantum_information": "quantum_information",
    "string_phenomenology": "string_phenomenology",
    "swampland": "swampland", "mathematical_physics": "mathematical_physics",
}

def load_jsonl(path):
    qs = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line: qs.append(json.loads(line))
    return qs

def normalize(t):
    t = t.lower().strip()
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return re.sub(r"\s+", " ", t)

def main():
    existing = load_jsonl(PHYS_JSONL)
    titles = {normalize(e["title"]) for e in existing}
    stmts = {normalize(e.get("statement", "")) for e in existing}
    max_num = 0
    for e in existing:
        m = re.match(r"PHYS-(\d+)", e["id"])
        if m: max_num = max(max_num, int(m.group(1)))

    added = 0
    for num, author, topic, stmt in QUESTIONS:
        title = f"Strings2024 Q{num}: {stmt[:60]}{'...' if len(stmt) > 60 else ''}"
        if normalize(title) in titles or normalize(stmt) in stmts:
            continue
        max_num += 1
        entry = {
            "id": f"PHYS-{max_num:04d}", "title": title,
            "domain": "physics",
            "subdomain": TOPIC_MAP.get(topic, "string_theory"),
            "statement": stmt, "status": "open", "importance": "",
            "year_posed": 2024, "posed_by": author,
            "sources": ["https://indico.cern.ch/event/1284995/"],
            "tags": ["strings2024"], "related_ids": [], "papers": [],
            "notes": f"Strings 2024 conference, question #{num}",
        }
        existing.append(entry)
        titles.add(normalize(title))
        added += 1

    with open(PHYS_JSONL, "w", encoding="utf-8") as f:
        for e in existing:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"  Added {added} Strings 2024 questions")
    print(f"  Total physics: {len(existing)}")

if __name__ == "__main__":
    main()
