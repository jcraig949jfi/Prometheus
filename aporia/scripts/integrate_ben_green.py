"""
Aporia — Integrate Ben Green's 87 open problems into the math catalog.
"""

import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "data"))

from ben_green_extracted import OPEN_PROBLEMS

ROOT = pathlib.Path(__file__).resolve().parent.parent
MATH_JSONL = ROOT / "mathematics" / "questions.jsonl"

# Map Ben Green categories to subdomains
CAT_MAP = {
    "sum_free_sets": "additive_combinatorics",
    "arithmetic_progressions": "additive_combinatorics",
    "sumsets_bases": "additive_combinatorics",
    "sidon_sets": "additive_combinatorics",
    "covering_packing": "combinatorics",
    "sieving": "analytic_number_theory",
    "additive_combinatorics": "additive_combinatorics",
    "additive_combinatorial_number_theory": "additive_number_theory",
    "discrete_combinatorial_geometry": "discrete_geometry",
    "nonabelian_group_theory": "group_theory",
    "harmonic_analysis": "harmonic_analysis",
    "miscellany": "combinatorics",
}

def load_existing():
    existing = []
    if MATH_JSONL.exists():
        with open(MATH_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    existing.append(json.loads(line))
    return existing

def normalize(t):
    t = t.lower().strip()
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return re.sub(r"\s+", " ", t)

def next_id(existing):
    max_num = 0
    for q in existing:
        m = re.match(r"MATH-(\d+)", q["id"])
        if m: max_num = max(max_num, int(m.group(1)))
    return max_num


def main():
    existing = load_existing()
    # We can't dedup by title (Ben Green problems don't have named titles),
    # but we can check if "Ben Green" problems are already present
    existing_notes = {q.get("notes", "") for q in existing}

    start_num = next_id(existing)
    counter = start_num

    added = 0
    for num, status, category, statement in OPEN_PROBLEMS:
        note = f"Ben Green Problem {num}"
        if note in existing_notes:
            continue

        counter += 1
        subdomain = CAT_MAP.get(category, "combinatorics")
        # Truncate statement to reasonable length
        stmt = statement.strip().replace("\n", " ")
        if len(stmt) > 300:
            stmt = stmt[:297] + "..."

        entry = {
            "id": f"MATH-{counter:04d}",
            "title": f"Ben Green Problem {num}",
            "domain": "mathematics",
            "subdomain": subdomain,
            "statement": stmt,
            "status": "open",
            "importance": "",
            "year_posed": 2018,
            "posed_by": "Ben Green",
            "sources": ["https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf"],
            "tags": ["ben_green"],
            "related_ids": [],
            "papers": [],
            "notes": note,
        }
        existing.append(entry)
        added += 1

    with open(MATH_JSONL, "w", encoding="utf-8") as f:
        for entry in existing:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"  Added {added} Ben Green open problems")
    print(f"  Total math questions: {len(existing)}")


if __name__ == "__main__":
    main()
