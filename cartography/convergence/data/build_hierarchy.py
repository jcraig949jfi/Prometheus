"""
Build OpenAlex concept hierarchy edges using Wikidata SPARQL.

Strategy:
1. Load all concepts with their Wikidata QIDs
2. Query Wikidata for P279 (subclass of) and P361 (part of) relationships between concept QIDs
3. Build parent-child edges
4. Filter math/physics subset using the hierarchy
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
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def load_concepts():
    path = os.path.join(OUT_DIR, "openalex_concepts.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sparql_query(query):
    url = "https://query.wikidata.org/sparql"
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(
        f"{url}?{params}",
        headers={
            "User-Agent": "Prometheus/1.0 (mailto:prometheus-cartography@proton.me)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, context=ctx, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    concepts = load_concepts()
    print(f"Loaded {len(concepts)} concepts")

    # Build QID -> concept mapping
    qid_to_concept = {}
    for c in concepts:
        qid = c.get("wikidata", "")
        if qid:
            # Extract QID from URL like "https://www.wikidata.org/wiki/Q395"
            if "/" in qid:
                qid = qid.rsplit("/", 1)[-1]
            qid_to_concept[qid] = c

    print(f"Concepts with Wikidata QIDs: {len(qid_to_concept)}")

    # Query Wikidata for subclass-of relationships between our QIDs
    # We need to batch this since there are 65K QIDs
    all_qids = list(qid_to_concept.keys())
    print(f"Total QIDs to query: {len(all_qids)}")

    # Strategy: Query for P279 (subclass of) relationships where both parent and child
    # are in our QID set. We'll batch by 500 QIDs at a time as VALUES.
    # But 65K QIDs is too many for VALUES. Instead, use a different approach:
    # Query ALL P279 links from our QIDs and filter.

    edges = []
    batch_size = 300
    total_batches = (len(all_qids) + batch_size - 1) // batch_size

    print(f"Querying Wikidata SPARQL in {total_batches} batches...")

    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(all_qids))
        batch_qids = all_qids[start:end]
        values_str = " ".join(f"wd:{q}" for q in batch_qids)

        query = f"""
        SELECT ?child ?parent WHERE {{
          VALUES ?child {{ {values_str} }}
          ?child wdt:P279 ?parent .
        }}
        """

        try:
            result = sparql_query(query)
            bindings = result.get("results", {}).get("bindings", [])

            for b in bindings:
                child_uri = b["child"]["value"]
                parent_uri = b["parent"]["value"]
                child_qid = child_uri.rsplit("/", 1)[-1]
                parent_qid = parent_uri.rsplit("/", 1)[-1]

                # Only keep edges where both ends are in our concept set
                if child_qid in qid_to_concept and parent_qid in qid_to_concept:
                    child_c = qid_to_concept[child_qid]
                    parent_c = qid_to_concept[parent_qid]
                    edges.append({
                        "parent_id": parent_c["id"],
                        "parent_name": parent_c["display_name"],
                        "parent_qid": parent_qid,
                        "child_id": child_c["id"],
                        "child_name": child_c["display_name"],
                        "child_qid": child_qid,
                        "child_level": child_c["level"],
                        "relation": "P279_subclass_of",
                    })
        except Exception as e:
            print(f"  Error on batch {batch_idx+1}: {e}")
            time.sleep(10)
            # Retry once
            try:
                result = sparql_query(query)
                bindings = result.get("results", {}).get("bindings", [])
                for b in bindings:
                    child_uri = b["child"]["value"]
                    parent_uri = b["parent"]["value"]
                    child_qid = child_uri.rsplit("/", 1)[-1]
                    parent_qid = parent_uri.rsplit("/", 1)[-1]
                    if child_qid in qid_to_concept and parent_qid in qid_to_concept:
                        child_c = qid_to_concept[child_qid]
                        parent_c = qid_to_concept[parent_qid]
                        edges.append({
                            "parent_id": parent_c["id"],
                            "parent_name": parent_c["display_name"],
                            "parent_qid": parent_qid,
                            "child_id": child_c["id"],
                            "child_name": child_c["display_name"],
                            "child_qid": child_qid,
                            "child_level": child_c["level"],
                            "relation": "P279_subclass_of",
                        })
            except Exception as e2:
                print(f"  Retry failed on batch {batch_idx+1}: {e2}")

        if (batch_idx + 1) % 10 == 0 or batch_idx + 1 == total_batches:
            print(f"  Batch {batch_idx+1}/{total_batches} — {len(edges)} edges so far")

        time.sleep(2)  # Wikidata rate limit

    print(f"\nTotal Wikidata-based edges: {len(edges)}")

    # Deduplicate
    seen = set()
    unique_edges = []
    for e in edges:
        key = (e["parent_id"], e["child_id"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)
    edges = unique_edges
    print(f"Unique edges: {len(edges)}")

    # Save edges
    path_edges = os.path.join(OUT_DIR, "openalex_concept_edges.json")
    with open(path_edges, "w", encoding="utf-8") as f:
        json.dump(edges, f, ensure_ascii=False)
    print(f"Saved {path_edges}")

    # Build math/physics subset using hierarchy traversal
    print("\nBuilding math/physics subset via hierarchy...")
    MATH_ID = "https://openalex.org/C33923547"
    PHYSICS_ID = "https://openalex.org/C121332964"

    # Build adjacency: parent -> children
    children_of = {}
    for e in edges:
        pid = e["parent_id"]
        if pid not in children_of:
            children_of[pid] = []
        children_of[pid].append(e["child_id"])

    # BFS from Math and Physics roots
    math_physics_ids = set()
    queue = [MATH_ID, PHYSICS_ID]
    math_physics_ids.update(queue)
    while queue:
        node = queue.pop(0)
        for child_id in children_of.get(node, []):
            if child_id not in math_physics_ids:
                math_physics_ids.add(child_id)
                queue.append(child_id)

    print(f"  Concepts reachable from Math/Physics roots: {len(math_physics_ids)}")

    # Also include keyword-matched ones from previous run
    id_to_concept = {c["id"]: c for c in concepts}
    mp_concepts = [id_to_concept[cid] for cid in math_physics_ids if cid in id_to_concept and id_to_concept[cid]["level"] >= 1]

    # Supplement with keyword matching for concepts not reached via hierarchy
    MATH_KEYWORDS = {"mathematics", "algebra", "geometry", "topology", "calculus", "number theory",
        "combinatorics", "mathematical", "trigonometry", "differential equation",
        "manifold", "group theory", "category theory", "graph theory", "fourier",
        "functional analysis", "operator theory", "dynamical system", "polynomial",
        "eigenvalue", "vector space", "metric space", "topological", "theorem"}
    PHYSICS_KEYWORDS = {"physics", "quantum", "thermodynamics", "mechanics", "relativity",
        "electromagnetism", "optics", "photon", "electron", "particle", "nuclear",
        "astrophysics", "cosmology", "gravity", "electromagnetic", "condensed matter",
        "plasma", "semiconductor", "superconductor", "spectroscopy",
        "boson", "fermion", "quark", "standard model", "dark matter", "black hole"}

    mp_ids_set = {c["id"] for c in mp_concepts}
    for c in concepts:
        if c["id"] in mp_ids_set or c["level"] is None or c["level"] < 1:
            continue
        name_lower = c["display_name"].lower()
        if any(kw in name_lower for kw in MATH_KEYWORDS | PHYSICS_KEYWORDS):
            c["_match_source"] = "keyword_supplement"
            mp_concepts.append(c)

    print(f"  Math/Physics total (hierarchy + keyword): {len(mp_concepts)}")

    path_mp = os.path.join(OUT_DIR, "openalex_math_physics_concepts.json")
    with open(path_mp, "w", encoding="utf-8") as f:
        json.dump(mp_concepts, f, ensure_ascii=False)
    print(f"Saved {path_mp}")

    # Update summary
    levels = {}
    for c in concepts:
        lv = c["level"]
        levels[lv] = levels.get(lv, 0) + 1
    mp_levels = {}
    for c in mp_concepts:
        lv = c["level"]
        mp_levels[lv] = mp_levels.get(lv, 0) + 1

    summary = {
        "source": "OpenAlex Concept Taxonomy",
        "api_url": "https://api.openalex.org/concepts",
        "snapshot_url": "https://openalex.s3.amazonaws.com/data/concepts/manifest",
        "hierarchy_source": "Wikidata SPARQL (P279 subclass-of)",
        "download_date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_concepts": len(concepts),
        "total_edges": len(edges),
        "math_physics_concepts": len(mp_concepts),
        "concepts_by_level": {str(k): v for k, v in sorted(levels.items(), key=lambda x: (x[0] is None, x[0]))},
        "math_physics_by_level": {str(k): v for k, v in sorted(mp_levels.items(), key=lambda x: (x[0] is None, x[0]))},
        "notes": [
            "OpenAlex deprecated the ancestors field on both API and S3 snapshot as of 2026",
            "Hierarchy edges reconstructed from Wikidata P279 (subclass-of) relationships",
            "Math/physics subset built by BFS from root concepts + keyword supplementation",
        ],
        "files": [
            "openalex_concepts.json",
            "openalex_concept_edges.json",
            "openalex_math_physics_concepts.json",
        ],
    }

    path_summary = os.path.join(OUT_DIR, "openalex_download_summary.json")
    with open(path_summary, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n=== FINAL SUMMARY ===")
    print(f"  Total concepts:        {len(concepts)}")
    print(f"  Hierarchy edges:       {len(edges)}")
    print(f"  Math/Physics subset:   {len(mp_concepts)}")
    print(f"  Concepts by level:     {levels}")
    print(f"  Math/Physics by level: {mp_levels}")
    print("Done.")


if __name__ == "__main__":
    main()
