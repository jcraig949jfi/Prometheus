"""
Download the full OpenAlex concept taxonomy (~65K concepts) using cursor pagination.
Saves:
  - openalex_concepts.json           (all concepts)
  - openalex_concept_edges.json      (parent->child edges)
  - openalex_math_physics_concepts.json (math/physics subset)
  - openalex_download_summary.json   (summary stats)
"""

import json
import ssl
import time
import urllib.request
import urllib.parse
import sys
import os

sys.stdout.reconfigure(line_buffering=True)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# SSL workaround
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Prometheus/1.0 (mailto:prometheus-cartography@proton.me)",
    "Accept": "application/json",
}

PER_PAGE = 200
BASE_URL = "https://api.openalex.org/concepts?per_page={}&cursor={}"


def fetch_cursor(cursor):
    url = BASE_URL.format(PER_PAGE, urllib.parse.quote(cursor, safe=""))
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_concept(raw):
    """Extract the fields we care about from a raw OpenAlex concept."""
    return {
        "id": raw.get("id", ""),
        "display_name": raw.get("display_name", ""),
        "level": raw.get("level"),
        "description": raw.get("description", ""),
        "wikidata": raw.get("wikidata", ""),
        "works_count": raw.get("works_count", 0),
        "cited_by_count": raw.get("cited_by_count", 0),
        "ancestors": [
            {"id": a["id"], "display_name": a["display_name"], "level": a["level"]}
            for a in (raw.get("ancestors") or [])
        ],
        "related_concepts": [
            {"id": r["id"], "display_name": r["display_name"], "level": r.get("level"), "score": r.get("score")}
            for r in (raw.get("related_concepts") or [])
        ],
    }


def main():
    # --- Phase 1: Fetch all concepts using cursor pagination ---
    print("Phase 1: Fetching OpenAlex concept taxonomy (cursor pagination)...")
    all_concepts = []
    cursor = "*"
    batch = 0

    while cursor:
        time.sleep(1.05)  # respect rate limit
        try:
            data = fetch_cursor(cursor)
        except Exception as e:
            print(f"  Error at batch {batch}: {e}. Retrying in 10s...")
            time.sleep(10)
            try:
                data = fetch_cursor(cursor)
            except Exception as e2:
                print(f"  Retry failed at batch {batch}: {e2}. Aborting.")
                break

        results = data.get("results", [])
        if not results:
            break

        for item in results:
            all_concepts.append(extract_concept(item))

        cursor = data["meta"].get("next_cursor")
        batch += 1
        total_expected = data["meta"]["count"]

        if batch % 25 == 0 or not cursor:
            print(f"  Batch {batch} — {len(all_concepts)}/{total_expected} concepts")

    print(f"  Done fetching. Total concepts downloaded: {len(all_concepts)}")

    # --- Phase 2: Save all concepts ---
    path_all = os.path.join(OUT_DIR, "openalex_concepts.json")
    with open(path_all, "w", encoding="utf-8") as f:
        json.dump(all_concepts, f, ensure_ascii=False)
    print(f"  Saved {path_all} ({len(all_concepts)} concepts)")

    # --- Phase 3: Build parent-child edges ---
    print("Phase 2: Building hierarchy edges...")
    edges = []
    for c in all_concepts:
        c_level = c["level"]
        if c_level is None or c_level == 0:
            continue
        for anc in c["ancestors"]:
            if anc["level"] == c_level - 1:
                edges.append({
                    "parent_id": anc["id"],
                    "parent_name": anc["display_name"],
                    "child_id": c["id"],
                    "child_name": c["display_name"],
                    "child_level": c_level,
                })

    path_edges = os.path.join(OUT_DIR, "openalex_concept_edges.json")
    with open(path_edges, "w", encoding="utf-8") as f:
        json.dump(edges, f, ensure_ascii=False)
    print(f"  Saved {path_edges} ({len(edges)} edges)")

    # --- Phase 4: Filter math/physics subset ---
    print("Phase 3: Filtering math/physics concepts...")
    MATH_PHYSICS_ROOTS = {"Mathematics", "Physics"}

    def is_math_physics(concept):
        if concept["level"] is None or concept["level"] < 1:
            return False
        ancestor_names = {a["display_name"] for a in concept["ancestors"]}
        return bool(ancestor_names & MATH_PHYSICS_ROOTS)

    mp_concepts = [c for c in all_concepts if is_math_physics(c)]

    path_mp = os.path.join(OUT_DIR, "openalex_math_physics_concepts.json")
    with open(path_mp, "w", encoding="utf-8") as f:
        json.dump(mp_concepts, f, ensure_ascii=False)
    print(f"  Saved {path_mp} ({len(mp_concepts)} math/physics concepts)")

    # --- Phase 5: Summary ---
    levels = {}
    for c in all_concepts:
        lv = c["level"]
        levels[lv] = levels.get(lv, 0) + 1

    mp_levels = {}
    for c in mp_concepts:
        lv = c["level"]
        mp_levels[lv] = mp_levels.get(lv, 0) + 1

    summary = {
        "source": "OpenAlex Concept Taxonomy",
        "url": "https://api.openalex.org/concepts",
        "download_date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_concepts": len(all_concepts),
        "total_edges": len(edges),
        "math_physics_concepts": len(mp_concepts),
        "concepts_by_level": dict(sorted(levels.items(), key=lambda x: (x[0] is None, str(x[0])))),
        "math_physics_by_level": dict(sorted(mp_levels.items(), key=lambda x: (x[0] is None, str(x[0])))),
        "files": [
            "openalex_concepts.json",
            "openalex_concept_edges.json",
            "openalex_math_physics_concepts.json",
        ],
    }

    path_summary = os.path.join(OUT_DIR, "openalex_download_summary.json")
    with open(path_summary, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"  Saved summary to {path_summary}")

    print("\n=== SUMMARY ===")
    print(f"  Total concepts:        {len(all_concepts)}")
    print(f"  Hierarchy edges:       {len(edges)}")
    print(f"  Math/Physics subset:   {len(mp_concepts)}")
    print(f"  Concepts by level:     {levels}")
    print(f"  Math/Physics by level: {mp_levels}")
    print("Done.")


if __name__ == "__main__":
    main()
