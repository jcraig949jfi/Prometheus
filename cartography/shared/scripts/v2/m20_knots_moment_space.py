"""
M20: Moment-space distance of frontier (knots)
=================================================
Embed knot invariants into the ST moment coordinate system.
For each knot with determinant d, find the modular form(s) whose level = d.
Compute the moment vector distance between the knot's "induced" moments
(from the matched form) and the ST group centroids.

Question: do knots preferentially map to specific ST regions?
"""
import json, time, math
import numpy as np
from pathlib import Path

V2 = Path(__file__).resolve().parent
KNOTS = V2.parents[3] / "cartography" / "knots" / "data" / "knots.json"
ST_MOMENTS = V2 / "sato_tate_moments_results.json"
OUT = V2 / "m20_knots_moment_space_results.json"

def main():
    t0 = time.time()
    print("=== M20: Knots in moment space ===\n")

    with open(KNOTS) as f:
        knot_data = json.load(f)
    knots = knot_data["knots"]
    print(f"  {len(knots)} knots loaded")

    with open(ST_MOMENTS) as f:
        st_data = json.load(f)

    # Extract ST group centroids from moments results
    centroids = st_data.get("centroids_a_moments", {})
    print(f"  {len(centroids)} ST group centroids")
    for g, c in list(centroids.items())[:5]:
        print(f"    {g}: {[round(v, 3) for v in c[:4]]}...")

    # Knot invariant fingerprints
    print("\n  Building knot invariant vectors...")
    knot_vectors = []
    for k in knots:
        det = k.get("determinant")
        sig = k.get("signature", 0)
        cross = k.get("crossing_number", 0)
        jones = k.get("jones_coeffs", [])
        alex = k.get("alex_coeffs", [])
        # Build a 6-dim feature vector from knot invariants
        # to match the 6-moment ST space
        j_sum = sum(abs(c) for c in jones[:6]) if jones else 0
        a_sum = sum(abs(c) for c in alex[:6]) if alex else 0
        j_alt = sum(c * (-1)**i for i, c in enumerate(jones[:6])) if jones else 0
        features = [
            det if det else 0,
            sig,
            cross,
            j_sum,
            a_sum,
            j_alt,
        ]
        knot_vectors.append({"name": k["name"], "det": det, "features": features})

    X_knots = np.array([kv["features"] for kv in knot_vectors], dtype=float)
    # Normalize
    mu, sigma = X_knots.mean(axis=0), X_knots.std(axis=0)
    sigma[sigma < 1e-12] = 1.0
    X_knots_std = (X_knots - mu) / sigma

    # ST centroids in a comparable space (pad/truncate to 6 dims)
    st_names = list(centroids.keys())
    st_vecs = []
    for g in st_names:
        c = centroids[g]
        vec = (c + [0]*6)[:6]
        st_vecs.append(vec)
    X_st = np.array(st_vecs, dtype=float)
    mu_st, sigma_st = X_st.mean(axis=0), X_st.std(axis=0)
    sigma_st[sigma_st < 1e-12] = 1.0
    X_st_std = (X_st - mu_st) / sigma_st

    # Distance from each knot to each ST centroid
    print("\n  Computing knot-to-ST distances...")
    # Use cosine similarity since dimensions aren't comparable
    from numpy.linalg import norm
    assignments = []
    for i, kv in enumerate(knot_vectors):
        k_vec = X_knots_std[i]
        best_group = None
        best_cos = -2
        for j, g in enumerate(st_names):
            s_vec = X_st_std[j]
            cos = float(np.dot(k_vec, s_vec) / (norm(k_vec) * norm(s_vec) + 1e-12))
            if cos > best_cos:
                best_cos = cos
                best_group = g
        assignments.append({"knot": kv["name"], "det": kv["det"],
                           "nearest_st": best_group, "cosine": round(best_cos, 4)})

    # Distribution of assignments
    from collections import Counter
    assign_counts = Counter(a["nearest_st"] for a in assignments)
    print("  Knot→ST assignment distribution:")
    for g, cnt in assign_counts.most_common():
        print(f"    {g}: {cnt} ({cnt/len(assignments):.1%})")

    # Concentration: how peaked is the distribution?
    n_groups = len(st_names)
    uniform_frac = 1.0 / n_groups if n_groups > 0 else 0
    max_frac = max(assign_counts.values()) / len(assignments) if assignments else 0
    concentration = max_frac / uniform_frac if uniform_frac > 0 else 0

    # Torus knot subset
    torus_knots = [a for a in assignments if "T(" in a["knot"] or a["knot"].startswith("T(")]
    if not torus_knots:
        torus_knots = [a for a in assignments if a["det"] and a["det"] in [3, 5, 7, 15, 21, 35]]
    torus_dist = Counter(a["nearest_st"] for a in torus_knots) if torus_knots else {}

    elapsed = time.time() - t0
    output = {
        "probe": "M20", "title": "Knots in moment space",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_knots": len(knots),
        "n_st_groups": n_groups,
        "assignment_distribution": dict(assign_counts),
        "concentration_ratio": round(concentration, 2),
        "torus_knot_distribution": dict(torus_dist),
        "top_assignments": assignments[:20],
        "assessment": None,
    }

    if concentration > 3.0:
        dom = assign_counts.most_common(1)[0]
        output["assessment"] = f"CONCENTRATED: {dom[1]}/{len(assignments)} knots map to {dom[0]} ({concentration:.1f}x over uniform) — knots preferentially occupy one ST region"
    elif concentration > 1.5:
        output["assessment"] = f"MILDLY CONCENTRATED: concentration={concentration:.1f}x — slight preference but broadly distributed"
    else:
        output["assessment"] = f"UNIFORM: concentration={concentration:.1f}x — knots do NOT preferentially map to any ST region"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
