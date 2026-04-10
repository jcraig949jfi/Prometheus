"""
Concept Index — Atomic concept extraction and bridge detection.
================================================================
Extracts normalized concepts from all datasets and finds cross-domain
bridges (Swanson's ABC model as a database join).

Concepts are atomic: "prime", "modular_form", "determinant_5", "conductor_11".
Links are many-to-many: each dataset object maps to multiple concepts.
Bridges are concept-sharing pairs across different datasets.

Storage:
  convergence/data/concepts.jsonl       — the atoms
  convergence/data/concept_links.jsonl  — many-to-many edges
  convergence/data/bridges.jsonl        — cross-domain bridges

Usage:
    from concept_index import build_index, find_bridges
    build_index()        # Extract concepts from all datasets
    find_bridges()       # Detect cross-domain connections

    python concept_index.py   # Full build + bridge detection
"""

import json
import math
import re
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

CONVERGENCE = Path(__file__).resolve().parents[2] / "convergence"
CONCEPTS_FILE = CONVERGENCE / "data" / "concepts.jsonl"
LINKS_FILE = CONVERGENCE / "data" / "concept_links.jsonl"
BRIDGES_FILE = CONVERGENCE / "data" / "bridges.jsonl"


def _is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True


def _number_concepts(n: int) -> list[str]:
    """Extract mathematical property concepts from an integer."""
    concepts = []
    if isinstance(n, int) and n > 0:
        concepts.append(f"integer_{n}")
        if _is_prime(n):
            concepts.append("prime")
        if n % 2 == 1:
            concepts.append("odd")
        else:
            concepts.append("even")
        if int(math.sqrt(n)) ** 2 == n:
            concepts.append("perfect_square")
        if n < 100:
            concepts.append("small_integer")
        elif n < 1000:
            concepts.append("medium_integer")
        else:
            concepts.append("large_integer")
    return concepts


# ---------------------------------------------------------------------------
# Extractors — one per dataset
# ---------------------------------------------------------------------------

def extract_knotinfo() -> tuple[list[dict], list[dict]]:
    """Extract concepts from KnotInfo knots."""
    from search_engine import _load_knots, _knots_cache, KNOTS_JSON
    if not KNOTS_JSON.exists(): return [], []
    _load_knots()

    concepts = set()
    links = []

    for knot in _knots_cache.get("knots", []):
        name = knot["name"]
        det = knot.get("determinant")
        crossing = knot.get("crossing_number", 0)

        knot_concepts = [f"crossing_{crossing}"]
        if det is not None:
            knot_concepts.extend(_number_concepts(det))
            knot_concepts.append(f"determinant_{det}")
        if knot.get("alex_coeffs"):
            knot_concepts.append("has_alexander_polynomial")
        if knot.get("jones_coeffs"):
            knot_concepts.append("has_jones_polynomial")

        for c in knot_concepts:
            concepts.add(c)
            links.append({
                "concept": c, "dataset": "KnotInfo", "object_id": name,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "KnotInfo"} for c in concepts], links


def extract_lmfdb() -> tuple[list[dict], list[dict]]:
    """Extract concepts from LMFDB objects."""
    from search_engine import _get_duck, CHARON_DB
    if not CHARON_DB.exists(): return [], []

    concepts = set()
    links = []

    con = _get_duck()
    rows = con.execute("""
        SELECT lmfdb_label, object_type, conductor,
               json_extract_string(properties, '$.rank') as rank
        FROM objects LIMIT 50000
    """).fetchall()
    con.close()

    for label, obj_type, conductor, rank in rows:
        obj_concepts = [f"object_type_{obj_type}"]

        if conductor:
            c = int(conductor)
            obj_concepts.extend(_number_concepts(c))
            obj_concepts.append(f"conductor_{c}")

        if rank is not None:
            obj_concepts.append(f"rank_{rank}")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "LMFDB", "object_id": label,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "LMFDB"} for c in concepts], links


def extract_fungrim() -> tuple[list[dict], list[dict]]:
    """Extract concepts from Fungrim formulas."""
    from search_engine import FUNGRIM_JSON
    if not FUNGRIM_JSON.exists(): return [], []
    data = json.loads(FUNGRIM_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    for formula in data.get("formulas", []):
        fid = formula["id"]
        module = formula["module"]
        concepts.add(f"topic_{module}")
        links.append({
            "concept": f"topic_{module}", "dataset": "Fungrim", "object_id": fid,
            "relationship": "in_module",
        })
        for symbol in formula.get("symbols", []):
            sym_concept = f"symbol_{symbol}"
            concepts.add(sym_concept)
            links.append({
                "concept": sym_concept, "dataset": "Fungrim", "object_id": fid,
                "relationship": "uses_symbol",
            })

    return [{"id": c, "type": "symbol" if c.startswith("symbol_") else "topic",
             "source": "Fungrim"} for c in concepts], links


def extract_antedb() -> tuple[list[dict], list[dict]]:
    """Extract concepts from ANTEDB theorems."""
    from search_engine import ANTEDB_JSON
    if not ANTEDB_JSON.exists(): return [], []
    data = json.loads(ANTEDB_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    for chapter in data.get("chapters", []):
        ch_name = chapter["chapter"]
        concepts.add(f"topic_{ch_name}")
        for thm in chapter.get("theorems", []):
            tid = f"{ch_name}/{thm['label']}"
            links.append({
                "concept": f"topic_{ch_name}", "dataset": "ANTEDB", "object_id": tid,
                "relationship": "in_chapter",
            })
            for val in thm.get("numerical_values", []):
                concepts.add(f"bound_{val}")
                links.append({
                    "concept": f"bound_{val}", "dataset": "ANTEDB", "object_id": tid,
                    "relationship": "has_bound",
                })

    return [{"id": c, "type": "topic" if "topic_" in c else "bound",
             "source": "ANTEDB"} for c in concepts], links


def extract_mathlib() -> tuple[list[dict], list[dict]]:
    """Extract concepts from mathlib namespace hierarchy."""
    from search_engine import MATHLIB_GRAPH, _load_mathlib, _mathlib_graph
    if not MATHLIB_GRAPH.exists(): return [], []
    _load_mathlib()

    concepts = set()
    links = []

    for node in _mathlib_graph.get("nodes", []):
        name = node if isinstance(node, str) else node.get("name", "")
        parts = name.split(".")
        # Extract namespace as concept
        if len(parts) >= 2:
            ns = parts[1] if parts[0] == "Mathlib" else parts[0]
            concept = f"namespace_{ns}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "mathlib", "object_id": name,
                "relationship": "in_namespace",
            })
        # Last part is often the specific topic
        if len(parts) >= 3:
            topic = parts[-1]
            if len(topic) > 3:
                concept = f"topic_{topic}"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "mathlib", "object_id": name,
                    "relationship": "about",
                })

    return [{"id": c, "type": "namespace" if "namespace_" in c else "topic",
             "source": "mathlib"} for c in concepts], links


def extract_number_fields() -> tuple[list[dict], list[dict]]:
    """Extract concepts from LMFDB Number Fields."""
    from search_engine import NUMBER_FIELDS_JSON
    if not NUMBER_FIELDS_JSON.exists(): return [], []
    data = json.loads(NUMBER_FIELDS_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    for field in data:
        label = field.get("label", "")
        degree = field.get("degree")
        class_num = field.get("class_number")
        galois = field.get("galois_label", "")
        disc_abs = field.get("disc_abs")

        obj_concepts = []
        if degree is not None:
            obj_concepts.append(f"degree_{degree}")
        if class_num is not None:
            cn = int(class_num) if class_num else 0
            obj_concepts.append(f"class_number_{cn}")
            obj_concepts.extend(_number_concepts(cn) if cn > 0 else [])
        if galois:
            obj_concepts.append(f"galois_{galois}")
        if disc_abs:
            d = abs(int(disc_abs))
            if d < 10000:
                obj_concepts.extend(_number_concepts(d))

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "NumberFields", "object_id": label,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "NumberFields"} for c in concepts], links


def extract_isogenies() -> tuple[list[dict], list[dict]]:
    """Extract concepts from supersingular isogeny graphs."""
    from search_engine import ISOGENY_GRAPHS
    import numpy as np
    if not ISOGENY_GRAPHS.exists(): return [], []

    concepts = set()
    links = []

    for pdir in sorted(ISOGENY_GRAPHS.iterdir()):
        if not pdir.is_dir(): continue
        prime = pdir.name
        try:
            p = int(prime)
        except ValueError:
            continue

        obj_id = f"isogeny_p{prime}"
        obj_concepts = _number_concepts(p)
        obj_concepts.append("supersingular_isogeny")

        # Count nodes from first available npz
        npz_files = list(pdir.glob("*.npz"))
        if npz_files:
            try:
                adj = np.load(str(npz_files[0]))
                for key in adj.files:
                    n = adj[key].shape[0]
                    obj_concepts.append(f"graph_nodes_{n}")
                    break
            except Exception:
                pass

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Isogenies", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "Isogenies"} for c in concepts], links


def extract_local_fields() -> tuple[list[dict], list[dict]]:
    """Extract concepts from wildly ramified local field extensions."""
    from search_engine import LOCAL_FIELDS_DIR
    if not LOCAL_FIELDS_DIR.exists(): return [], []

    concepts = set()
    links = []

    for fpath in LOCAL_FIELDS_DIR.iterdir():
        if not fpath.is_file(): continue
        name = fpath.name  # e.g. p2d10all
        # Extract prime and degree from filename
        import re as _re
        m = _re.match(r'p(\d+)d(\d+)', name)
        if not m: continue
        prime, degree = int(m.group(1)), int(m.group(2))

        obj_id = f"localfield_p{prime}_d{degree}"
        obj_concepts = [
            f"ramification_prime_{prime}",
            f"extension_degree_{degree}",
            "wildly_ramified",
        ]
        obj_concepts.extend(_number_concepts(prime))

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "LocalFields", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "LocalFields"} for c in concepts], links


def extract_spacegroups() -> tuple[list[dict], list[dict]]:
    """Extract concepts from Bilbao crystallographic space groups."""
    from search_engine import BILBAO_DIR
    if not BILBAO_DIR.exists(): return [], []

    concepts = set()
    links = []

    # Crystal system mapping by space group number ranges
    _sg_systems = {
        range(1, 3): "triclinic", range(3, 16): "monoclinic",
        range(16, 75): "orthorhombic", range(75, 143): "tetragonal",
        range(143, 168): "trigonal", range(168, 195): "hexagonal",
        range(195, 231): "cubic",
    }

    for sg_file in sorted(BILBAO_DIR.glob("sg_*.json")):
        try:
            data = json.loads(sg_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        sg_num = data.get("space_group_number", 0)
        obj_id = f"sg_{sg_num}"
        obj_concepts = [f"spacegroup_{sg_num}"]

        # Crystal system
        for rng, system in _sg_systems.items():
            if sg_num in rng:
                obj_concepts.append(f"crystal_system_{system}")
                break

        # Point group order
        pg_order = data.get("point_group_order")
        if pg_order:
            obj_concepts.append(f"point_group_order_{pg_order}")
            obj_concepts.extend(_number_concepts(int(pg_order)))

        # Number of Wyckoff positions
        n_wyckoff = data.get("num_wyckoff_positions")
        if n_wyckoff:
            obj_concepts.append(f"wyckoff_positions_{n_wyckoff}")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "SpaceGroups", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "SpaceGroups"} for c in concepts], links


def extract_polytopes() -> tuple[list[dict], list[dict]]:
    """Extract concepts from polyDB polytope collections."""
    from search_engine import POLYTOPES_DIR
    if not POLYTOPES_DIR.exists(): return [], []

    concepts = set()
    links = []

    for json_file in sorted(POLYTOPES_DIR.glob("*.json")):
        if json_file.name == "manifest.json": continue
        try:
            entries = json.loads(json_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(entries, list): continue

        collection_name = json_file.stem
        for i, entry in enumerate(entries[:200]):  # Cap per collection
            if not isinstance(entry, dict) or not entry: continue
            obj_id = f"{collection_name}_{i}"
            obj_concepts = [f"collection_{collection_name}"]

            dim = entry.get("DIM") or entry.get("AMBIENT_DIM")
            if dim is not None:
                obj_concepts.append(f"dimension_{dim}")

            fvec = entry.get("F_VECTOR")
            if fvec and isinstance(fvec, list):
                obj_concepts.append(f"fvector_len_{len(fvec)}")

            n_verts = entry.get("N_VERTICES")
            if n_verts:
                obj_concepts.append(f"vertices_{n_verts}")

            for concept in obj_concepts:
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "Polytopes", "object_id": obj_id,
                    "relationship": "has_property",
                })

    return [{"id": c, "type": "property", "source": "Polytopes"} for c in concepts], links


def extract_pibase() -> tuple[list[dict], list[dict]]:
    """Extract concepts from pi-Base topological spaces."""
    from search_engine import PIBASE_DIR
    if not PIBASE_DIR.exists(): return [], []

    concepts = set()
    links = []

    spaces_dir = PIBASE_DIR / "spaces"
    if not spaces_dir.exists(): return [], []

    for space_dir in sorted(spaces_dir.iterdir()):
        if not space_dir.is_dir(): continue
        readme = space_dir / "README.md"
        if not readme.exists(): continue

        # Parse YAML frontmatter
        text = readme.read_text(encoding="utf-8", errors="replace")
        uid = space_dir.name
        name = ""
        if text.startswith("---"):
            end = text.find("---", 3)
            if end > 0:
                fm = text[3:end]
                for line in fm.split("\n"):
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip().strip('"').strip("'")

        obj_id = uid
        obj_concepts = ["topological_space"]

        # Extract math keywords from name
        name_lower = name.lower()
        for kw in ["compact", "hausdorff", "metrizable", "connected", "discrete",
                    "countable", "separable", "regular", "normal", "paracompact",
                    "locally_compact", "complete", "totally_bounded"]:
            if kw.replace("_", " ") in name_lower or kw in name_lower:
                obj_concepts.append(f"topo_{kw}")

        # Read properties
        props_dir = space_dir / "properties"
        if props_dir.is_dir():
            for prop_file in props_dir.glob("*.md"):
                prop_text = prop_file.read_text(encoding="utf-8", errors="replace")
                if "value: true" in prop_text.lower():
                    prop_name = prop_file.stem
                    obj_concepts.append(f"topo_prop_{prop_name}")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "piBase", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "piBase"} for c in concepts], links


def extract_mmlkg() -> tuple[list[dict], list[dict]]:
    """Extract concepts from MMLKG theorem reference graph."""
    from search_engine import MMLKG_REFS
    import csv
    if not MMLKG_REFS.exists(): return [], []

    concepts = set()
    links = []
    article_topics = defaultdict(set)

    with open(MMLKG_REFS, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2: continue
            src_article = row[0]
            tgt_article = row[2] if len(row) > 2 else row[1]
            article_topics[src_article].add(tgt_article)

    # Extract concepts from article names (Mizar naming convention)
    for article, refs in article_topics.items():
        obj_id = f"mizar_{article}"
        obj_concepts = [f"mizar_article_{article}"]

        # Hub articles (many references) are interesting bridge points
        if len(refs) > 20:
            obj_concepts.append("mizar_hub")
        if len(refs) > 50:
            obj_concepts.append("mizar_superhub")

        # Extract topic from article name prefix
        prefix = article.rstrip("_0123456789")
        if prefix:
            obj_concepts.append(f"mizar_topic_{prefix}")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "MMLKG", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "MMLKG"} for c in concepts], links


def extract_genus2() -> tuple[list[dict], list[dict]]:
    """Extract concepts from genus-2 curves."""
    from search_engine import GENUS2_PG, GENUS2_JSON
    src = GENUS2_PG if GENUS2_PG.exists() else GENUS2_JSON
    if not src.exists(): return [], []
    raw = json.loads(src.read_text(encoding="utf-8"))
    data = raw.get("records", raw) if isinstance(raw, dict) else raw

    concepts = set()
    links = []

    for curve in data:
        label = curve.get("label", "")
        cond = curve.get("conductor") or curve.get("cond")
        st = curve.get("st_group", "")
        rn = curve.get("root_number")
        torsion = curve.get("torsion", [])

        obj_concepts = ["genus_2_curve"]
        if cond is not None and cond < 10000:
            obj_concepts.extend(_number_concepts(cond))
            obj_concepts.append("conductor")
        if st:
            obj_concepts.append(f"sato_tate_{st}")
        if rn == 1:
            obj_concepts.append("even_rank")
        elif rn == -1:
            obj_concepts.append("odd_rank")
        if isinstance(torsion, list):
            for t in torsion:
                if isinstance(t, int) and t > 0:
                    obj_concepts.extend(_number_concepts(t))

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Genus2", "object_id": label,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "Genus2"} for c in concepts], links


def extract_maass() -> tuple[list[dict], list[dict]]:
    """Extract concepts from Maass forms (35K rigorous)."""
    from search_engine import MAASS_PG, MAASS_JSON
    src = MAASS_PG if MAASS_PG.exists() else MAASS_JSON
    if not src.exists(): return [], []
    raw = json.loads(src.read_text(encoding="utf-8"))
    data = raw.get("records", raw) if isinstance(raw, dict) else raw

    concepts = set()
    links = []

    for form in data:
        label = form.get("maass_label", form.get("label", ""))
        level = form.get("level")
        fricke = form.get("fricke_eigenvalue", form.get("fricke"))
        sp = form.get("spectral_parameter")
        if isinstance(sp, str):
            try:
                sp = float(sp)
            except (ValueError, OverflowError):
                sp = None

        obj_concepts = ["maass_form"]
        if level is not None:
            obj_concepts.append(f"level_{level}")
        if fricke == 1:
            obj_concepts.append("fricke_plus")
        elif fricke == -1:
            obj_concepts.append("fricke_minus")
        if sp is not None:
            # Bin spectral parameters into ranges for bridge detection
            sp_bin = int(sp // 10) * 10
            obj_concepts.append(f"spectral_bin_{sp_bin}")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Maass", "object_id": label,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "Maass"} for c in concepts], links


def extract_lattices() -> tuple[list[dict], list[dict]]:
    """Extract concepts from lattices (39K integral)."""
    from search_engine import LATTICES_PG, LATTICES_JSON
    src = LATTICES_PG if LATTICES_PG.exists() else LATTICES_JSON
    if not src.exists(): return [], []
    raw = json.loads(src.read_text(encoding="utf-8"))
    data = raw.get("records", raw.get("lattices", raw)) if isinstance(raw, dict) else raw

    concepts = set()
    links = []

    for lat in data:
        name = lat.get("name", "")
        if not isinstance(name, str):
            name = str(name) if name else ""
        obj_id = name or lat.get("label", "")
        dim = lat.get("dim")
        det = lat.get("det")
        kissing = lat.get("kissing")

        obj_concepts = ["lattice"]
        if dim is not None:
            obj_concepts.append(f"dimension_{dim}")
        if det is not None:
            obj_concepts.extend(_number_concepts(int(det)) if isinstance(det, (int, float)) and det > 0 else [])
            obj_concepts.append("determinant")
        if kissing is not None:
            obj_concepts.append(f"kissing_{kissing}")
            obj_concepts.extend(_number_concepts(int(kissing)) if isinstance(kissing, int) and kissing > 0 else [])

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Lattices", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "Lattices"} for c in concepts], links


def extract_openalex() -> tuple[list[dict], list[dict]]:
    """Extract concepts from OpenAlex academic taxonomy."""
    from search_engine import OPENALEX_CONCEPTS
    if not OPENALEX_CONCEPTS.exists(): return [], []
    data = json.loads(OPENALEX_CONCEPTS.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    # Math/physics keywords that bridge to our other datasets
    bridge_keywords = {
        "prime", "number", "algebra", "topology", "geometry", "analysis",
        "group", "ring", "field", "modular", "elliptic", "lattice",
        "combinatorics", "graph", "polynomial", "matrix", "vector",
        "manifold", "knot", "crystal", "symmetry", "representation",
    }

    for c in data:
        name = c.get("display_name", "")
        level = c.get("level")
        desc = c.get("description", "")
        obj_id = c.get("id", "")

        obj_concepts = []
        name_lower = name.lower()
        # Extract bridge-relevant terms from name
        for kw in bridge_keywords:
            if kw in name_lower:
                obj_concepts.append(kw)
        if level is not None:
            obj_concepts.append(f"openalex_level_{level}")

        if obj_concepts:
            for concept in obj_concepts:
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "OpenAlex", "object_id": obj_id,
                    "relationship": "has_property",
                })

    return [{"id": c, "type": "property", "source": "OpenAlex"} for c in concepts], links


def extract_smallgroups() -> tuple[list[dict], list[dict]]:
    """Extract concepts from GAP small groups library."""
    from search_engine import SMALLGROUPS_JSON
    if not SMALLGROUPS_JSON.exists(): return [], []
    data = json.loads(SMALLGROUPS_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    for g in data.get("groups", []):
        order = g.get("order", 0)
        n_groups = g.get("n_groups", 0)
        obj_id = f"order_{order}"

        obj_concepts = ["group"]
        if order > 0:
            obj_concepts.extend(_number_concepts(order))
        if g.get("is_prime"):
            obj_concepts.append("prime_order")
        if g.get("all_abelian"):
            obj_concepts.append("abelian")
        if g.get("is_cyclic_only"):
            obj_concepts.append("cyclic")
        if g.get("is_squarefree"):
            obj_concepts.append("squarefree_order")
        if n_groups is not None and isinstance(n_groups, int):
            if n_groups == 1:
                obj_concepts.append("unique_group")
            obj_concepts.extend(_number_concepts(n_groups) if n_groups > 0 else [])

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "SmallGroups", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "SmallGroups"} for c in concepts], links


def extract_verb_smallgroups() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from small groups: group structure operations."""
    from search_engine import SMALLGROUPS_JSON
    if not SMALLGROUPS_JSON.exists(): return [], []
    data = json.loads(SMALLGROUPS_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    for g in data.get("groups", []):
        order = g.get("order", 0)
        obj_id = f"order_{order}"
        obj_concepts = ["verb_involves_group", "verb_involves_order"]

        if g.get("all_abelian"):
            obj_concepts.append("verb_abelian_group")
        if g.get("is_cyclic_only"):
            obj_concepts.append("verb_cyclic_group")
        if g.get("is_prime"):
            obj_concepts.append("verb_involves_prime")
        if g.get("is_squarefree"):
            obj_concepts.append("verb_squarefree")

        # Factorization bridges to number fields
        fac = g.get("factorization", {})
        if len(fac) >= 2:
            obj_concepts.append("verb_composite_order")
        for p in fac:
            obj_concepts.append("verb_involves_prime")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "SmallGroups", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "verb", "source": "SmallGroups"} for c in concepts], links


# ---------------------------------------------------------------------------
# Verb concept extractors — cross-domain bridges
# ---------------------------------------------------------------------------

# Canonical math tokens: map variations to a single normalized form so that
# the same mathematical idea from different datasets lands on the same concept.
_CANONICAL = {
    "Zeta": "zeta", "RiemannZeta": "zeta", "DirichletLFunction": "l_function",
    "LFunction": "l_function", "LSeries": "l_function",
    "BernoulliB": "bernoulli", "Bernoulli": "bernoulli",
    "EulerE": "euler", "Euler": "euler",
    "Integral": "integral", "integral": "integral",
    "Sum": "sum", "Product": "product",
    "Equal": "equal", "Inequality": "inequality",
    "Pi": "pi", "Gamma": "gamma", "GammaFunction": "gamma",
    "Exp": "exp", "Log": "log",
    "Sin": "sin", "Cos": "cos", "Theta": "theta",
    "Modular": "modular", "ModularForm": "modular_form",
    "Elliptic": "elliptic", "EllipticCurve": "elliptic_curve",
    "Prime": "prime", "Primes": "prime",
    "Polynomial": "polynomial", "Poly": "polynomial",
    "Matrix": "matrix", "Determinant": "determinant",
    "Conductor": "conductor", "Rank": "rank",
    "Bound": "bound", "Estimate": "estimate",
    "Convergence": "convergence", "Limit": "limit",
    "NumberTheory": "number_theory", "Analysis": "analysis",
    "Algebra": "algebra", "Topology": "topology",
    "CategoryTheory": "category_theory",
    "Combinatorics": "combinatorics",
    "Probability": "probability",
    "MeasureTheory": "measure_theory",
    "RingTheory": "ring_theory",
    "AlgebraicGeometry": "algebraic_geometry",
    "RepresentationTheory": "representation_theory",
    "LinearAlgebra": "linear_algebra",
    "Alexander": "alexander", "Jones": "jones",
    "Knot": "knot", "Crossing": "crossing",
    "Dirichlet": "dirichlet",
    "Isogeny": "isogeny", "Supersingular": "supersingular",
    "Galois": "galois", "GaloisGroup": "galois_group",
    "Discriminant": "discriminant", "ClassNumber": "class_number",
    "Regulator": "regulator", "Ramification": "ramification",
    "SpaceGroup": "space_group", "Wyckoff": "wyckoff",
    "Crystal": "crystal", "Lattice": "lattice",
    "Polytope": "polytope", "FVector": "f_vector",
    "Compact": "compact", "Hausdorff": "hausdorff",
    "Metrizable": "metrizable", "Connected": "connected",
    "Separable": "separable", "Paracompact": "paracompact",
    "Mizar": "mizar", "Theorem": "theorem",
    "Convex": "convex", "Simplicial": "simplicial",
    "Symmorphic": "symmorphic", "Centrosymmetric": "centrosymmetric",
    "Ramified": "ramified", "WildlyRamified": "wildly_ramified",
    "Triclinic": "triclinic", "Monoclinic": "monoclinic",
    "Orthorhombic": "orthorhombic", "Tetragonal": "tetragonal",
    "Trigonal": "trigonal", "Hexagonal": "hexagonal", "Cubic": "cubic",
}


def _canonicalize(token: str) -> str:
    """Map a token to its canonical form, or lowercase it."""
    return _CANONICAL.get(token, token.lower())


def _split_camel(name: str) -> list[str]:
    """Split CamelCase or dot-separated names into tokens."""
    # First split on dots and underscores
    parts = re.split(r'[._]', name)
    tokens = []
    for part in parts:
        # Split camelCase
        sub = re.sub(r'([a-z])([A-Z])', r'\1_\2', part)
        for t in sub.split('_'):
            if len(t) > 2:
                tokens.append(t)
    return tokens


def extract_verb_fungrim() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from Fungrim: symbol pairs, formula types, cross-module bridges."""
    from search_engine import FUNGRIM_JSON
    if not FUNGRIM_JSON.exists():
        return [], []
    data = json.loads(FUNGRIM_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    # Track which modules each symbol appears in (for cross-module bridges)
    symbol_modules = defaultdict(set)

    for formula in data.get("formulas", []):
        fid = formula["id"]
        module = formula.get("module", "")
        ftype = formula.get("type", "")
        symbols = formula.get("symbols", [])

        # 1) Formula type as verb concept
        if ftype:
            concept = f"verb_formula_{ftype}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Fungrim", "object_id": fid,
                "relationship": "has_type",
            })

        # 2) Symbol PAIRS as verb concepts (sorted to deduplicate)
        canon_syms = sorted(set(_canonicalize(s) for s in symbols if len(s) > 2))
        for s1, s2 in combinations(canon_syms[:8], 2):  # cap to avoid combinatorial explosion
            concept = f"verb_{s1}_{s2}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Fungrim", "object_id": fid,
                "relationship": "relates_symbols",
            })

        # 3) Track symbol-module mapping
        for sym in symbols:
            csym = _canonicalize(sym)
            symbol_modules[csym].add(module)

        # 4) Individual canonical symbols as verb concepts (for cross-dataset matching)
        for sym in symbols:
            csym = _canonicalize(sym)
            if len(csym) > 2:
                concept = f"verb_involves_{csym}"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "Fungrim", "object_id": fid,
                    "relationship": "involves",
                })

    # 5) Cross-module bridge concepts
    for sym, modules in symbol_modules.items():
        if len(modules) >= 2:
            for m1, m2 in combinations(sorted(modules), 2):
                concept = f"verb_bridges_{m1}_{m2}"
                concepts.add(concept)
                # Link to a synthetic object representing this bridge
                links.append({
                    "concept": concept, "dataset": "Fungrim",
                    "object_id": f"bridge_{sym}_{m1}_{m2}",
                    "relationship": "cross_module_bridge",
                })

    return [{"id": c, "type": "verb", "source": "Fungrim"} for c in concepts], links


def extract_verb_mathlib() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from mathlib: import relationships, cross-namespace bridges."""
    from search_engine import MATHLIB_GRAPH, _load_mathlib, _mathlib_graph
    if not MATHLIB_GRAPH.exists():
        return [], []
    _load_mathlib()

    concepts = set()
    links = []

    # Extract top-level namespaces from nodes
    def _top_ns(name: str) -> str:
        parts = name.split(".")
        if parts[0] == "Mathlib" and len(parts) >= 2:
            return parts[1]
        return parts[0]

    # 1) Import relationship verbs from edges
    edges = _mathlib_graph.get("edges", [])
    # Track cross-namespace imports
    ns_imports = defaultdict(set)  # (src_ns, tgt_ns) pairs

    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            continue
        src, tgt = edge
        src_ns = _top_ns(src)
        tgt_ns = _top_ns(tgt)

        # Import relationship as verb
        concept = f"verb_imports_{_canonicalize(tgt_ns)}"
        concepts.add(concept)
        links.append({
            "concept": concept, "dataset": "mathlib", "object_id": src,
            "relationship": "imports",
        })

        # Cross-namespace bridge
        if src_ns != tgt_ns:
            ns_pair = tuple(sorted([_canonicalize(src_ns), _canonicalize(tgt_ns)]))
            ns_imports[ns_pair].add(src)

    # 2) Cross-namespace connection concepts
    for (ns1, ns2), modules in ns_imports.items():
        concept = f"verb_connects_{ns1}_{ns2}"
        concepts.add(concept)
        # Link a sample of modules (avoid millions of links)
        for mod in list(modules)[:20]:
            links.append({
                "concept": concept, "dataset": "mathlib", "object_id": mod,
                "relationship": "cross_namespace_import",
            })

    # 3) Canonical topic verbs from node names (for cross-dataset matching)
    for node in _mathlib_graph.get("nodes", []):
        name = node if isinstance(node, str) else node.get("name", "")
        tokens = _split_camel(name)
        for tok in tokens:
            ctok = _canonicalize(tok)
            if len(ctok) > 3:
                concept = f"verb_involves_{ctok}"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "mathlib", "object_id": name,
                    "relationship": "involves",
                })

    return [{"id": c, "type": "verb", "source": "mathlib"} for c in concepts], links


def extract_verb_antedb() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from ANTEDB: theorem types, chapter connections."""
    from search_engine import ANTEDB_JSON
    if not ANTEDB_JSON.exists():
        return [], []
    data = json.loads(ANTEDB_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    # Keyword patterns that indicate theorem types
    _TYPE_PATTERNS = {
        "bound": re.compile(r'\b(bound|upper|lower|majoriz|minoriz)\b', re.I),
        "estimate": re.compile(r'\b(estimat|approximat|asymptot)\b', re.I),
        "inequality": re.compile(r'\b(inequalit|leq|geq|≤|≥)\b', re.I),
        "identity": re.compile(r'\b(identity|equals|=)\b', re.I),
        "formula": re.compile(r'\b(formula|explicit|closed.form)\b', re.I),
        "convergence": re.compile(r'\b(converg|limit|tend)\b', re.I),
        "zero": re.compile(r'\b(zero|root|vanish)\b', re.I),
        "prime": re.compile(r'\b(prime|primes|primality)\b', re.I),
        "density": re.compile(r'\b(densit|distribut|counting)\b', re.I),
        "zeta": re.compile(r'\b(zeta|riemann|L.function|l.function)\b', re.I),
        "modular": re.compile(r'\b(modular|automorphic|eisenstein)\b', re.I),
        "elliptic": re.compile(r'\b(elliptic|curve|abelian)\b', re.I),
        "analytic": re.compile(r'\b(analytic|meromorphic|holomorphic)\b', re.I),
    }

    chapter_names = [ch.get("chapter", "") for ch in data.get("chapters", [])]

    for chapter in data.get("chapters", []):
        ch_name = chapter.get("chapter", "")
        ch_canon = _canonicalize(ch_name.replace("_", " ").replace("-", " "))

        for thm in chapter.get("theorems", []):
            tid = f"{ch_name}/{thm['label']}"
            label_text = thm.get("label", "")

            # 1) Theorem type verbs based on label/chapter keywords
            search_text = f"{ch_name} {label_text}"
            for ttype, pattern in _TYPE_PATTERNS.items():
                if pattern.search(search_text):
                    concept = f"verb_proves_{ttype}"
                    concepts.add(concept)
                    links.append({
                        "concept": concept, "dataset": "ANTEDB", "object_id": tid,
                        "relationship": "proves",
                    })

            # 2) Canonical topic verbs (for cross-dataset matching)
            for token in _split_camel(search_text):
                ctok = _canonicalize(token)
                if len(ctok) > 3:
                    concept = f"verb_involves_{ctok}"
                    concepts.add(concept)
                    links.append({
                        "concept": concept, "dataset": "ANTEDB", "object_id": tid,
                        "relationship": "involves",
                    })

            # 3) Chapter connection concepts: link this theorem's chapter to related chapters
            for other_ch in chapter_names:
                if other_ch != ch_name:
                    # Check if the theorem label references concepts from another chapter
                    other_tokens = set(_split_camel(other_ch))
                    label_tokens = set(_split_camel(label_text))
                    shared = other_tokens & label_tokens
                    if shared and any(len(t) > 3 for t in shared):
                        ch1, ch2 = sorted([ch_name, other_ch])
                        concept = f"verb_connects_{_canonicalize(ch1)}_{_canonicalize(ch2)}"
                        concepts.add(concept)
                        links.append({
                            "concept": concept, "dataset": "ANTEDB", "object_id": tid,
                            "relationship": "chapter_connection",
                        })

    return [{"id": c, "type": "verb", "source": "ANTEDB"} for c in concepts], links


def extract_verb_lmfdb() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from LMFDB: object type relationships, property patterns."""
    from search_engine import _get_duck, CHARON_DB
    if not CHARON_DB.exists():
        return [], []

    concepts = set()
    links = []

    con = _get_duck()
    rows = con.execute("""
        SELECT lmfdb_label, object_type, conductor,
               json_extract_string(properties, '$.rank') as rank,
               json_extract_string(properties, '$.degree') as degree
        FROM objects LIMIT 50000
    """).fetchall()
    con.close()

    for label, obj_type, conductor, rank, degree in rows:
        # 1) Object type as verb: "has_elliptic_curve", "has_modular_form", etc.
        if obj_type:
            concept = f"verb_has_{_canonicalize(obj_type)}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "LMFDB", "object_id": label,
                "relationship": "has_type",
            })

            # Also add canonical involvement
            for token in _split_camel(obj_type):
                ctok = _canonicalize(token)
                if len(ctok) > 3:
                    concept = f"verb_involves_{ctok}"
                    concepts.add(concept)
                    links.append({
                        "concept": concept, "dataset": "LMFDB", "object_id": label,
                        "relationship": "involves",
                    })

        # 2) Property patterns
        if conductor is not None:
            c = int(conductor)
            if _is_prime(c):
                concept = "verb_conductor_is_prime"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "LMFDB", "object_id": label,
                    "relationship": "property_pattern",
                })

        if rank is not None:
            try:
                r = int(rank)
                concept = f"verb_has_rank_{r}"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "LMFDB", "object_id": label,
                    "relationship": "property_pattern",
                })
                # Generic rank involvement
                concepts.add("verb_involves_rank")
                links.append({
                    "concept": "verb_involves_rank", "dataset": "LMFDB", "object_id": label,
                    "relationship": "involves",
                })
            except (ValueError, TypeError):
                pass

        # 3) Canonical math topic verbs from object type
        if obj_type:
            ot_lower = obj_type.lower()
            if "elliptic" in ot_lower or "ec" == ot_lower:
                for c in ["verb_involves_elliptic", "verb_involves_elliptic_curve"]:
                    concepts.add(c)
                    links.append({
                        "concept": c, "dataset": "LMFDB", "object_id": label,
                        "relationship": "involves",
                    })
            if "modular" in ot_lower or "mf" in ot_lower:
                for c in ["verb_involves_modular", "verb_involves_modular_form"]:
                    concepts.add(c)
                    links.append({
                        "concept": c, "dataset": "LMFDB", "object_id": label,
                        "relationship": "involves",
                    })

    return [{"id": c, "type": "verb", "source": "LMFDB"} for c in concepts], links


def extract_verb_knotinfo() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from KnotInfo: polynomial relationships, crossing patterns."""
    from search_engine import _load_knots, _knots_cache, KNOTS_JSON
    if not KNOTS_JSON.exists():
        return [], []
    _load_knots()

    concepts = set()
    links = []

    for knot in _knots_cache.get("knots", []):
        name = knot["name"]
        crossing = knot.get("crossing_number", 0)

        # 1) Polynomial relationship verbs
        if knot.get("alex_coeffs"):
            concept = "verb_has_alexander_polynomial"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "KnotInfo", "object_id": name,
                "relationship": "has_polynomial",
            })
            # Alexander degree
            deg = len(knot["alex_coeffs"]) - 1
            concept = f"verb_alexander_degree_{deg}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "KnotInfo", "object_id": name,
                "relationship": "polynomial_degree",
            })
            # Generic polynomial involvement
            concepts.add("verb_involves_polynomial")
            links.append({
                "concept": "verb_involves_polynomial", "dataset": "KnotInfo", "object_id": name,
                "relationship": "involves",
            })

        if knot.get("jones_coeffs"):
            concept = "verb_has_jones_polynomial"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "KnotInfo", "object_id": name,
                "relationship": "has_polynomial",
            })
            concepts.add("verb_involves_polynomial")
            links.append({
                "concept": "verb_involves_polynomial", "dataset": "KnotInfo", "object_id": name,
                "relationship": "involves",
            })

        # 2) Crossing pattern verbs
        if crossing > 0:
            if crossing <= 6:
                concept = "verb_low_complexity"
            elif crossing <= 10:
                concept = "verb_medium_complexity"
            else:
                concept = "verb_high_complexity"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "KnotInfo", "object_id": name,
                "relationship": "complexity_class",
            })

        # 3) Determinant-related verbs
        det = knot.get("determinant")
        if det is not None:
            if _is_prime(det):
                concept = "verb_determinant_is_prime"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "KnotInfo", "object_id": name,
                    "relationship": "property_pattern",
                })
            # Generic determinant involvement
            concepts.add("verb_involves_determinant")
            links.append({
                "concept": "verb_involves_determinant", "dataset": "KnotInfo", "object_id": name,
                "relationship": "involves",
            })

        # 4) Canonical involvement verbs for cross-dataset matching
        concepts.add("verb_involves_knot")
        links.append({
            "concept": "verb_involves_knot", "dataset": "KnotInfo", "object_id": name,
            "relationship": "involves",
        })

    return [{"id": c, "type": "verb", "source": "KnotInfo"} for c in concepts], links


def extract_verb_number_fields() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from Number Fields: class group structure, Galois type, quadratic type."""
    from search_engine import NUMBER_FIELDS_JSON
    if not NUMBER_FIELDS_JSON.exists():
        return [], []
    data = json.loads(NUMBER_FIELDS_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    for field in data:
        label = field.get("label", "")
        degree = field.get("degree")
        class_num = field.get("class_number")
        galois = field.get("galois_label", "")
        disc = field.get("disc_sign", 0)
        reg = field.get("regulator")

        obj_concepts = []

        # Class number verbs
        if class_num is not None:
            cn = int(class_num) if class_num else 0
            if cn == 1:
                obj_concepts.append("verb_has_class_number_1")
            elif cn > 1:
                obj_concepts.append("verb_has_nontrivial_class_group")
            obj_concepts.append("verb_involves_class_number")

        # Degree verb
        if degree is not None:
            obj_concepts.append(f"verb_degree_{degree}")

        # Galois type: abelian if transitive group label is nTm with m=1
        if galois:
            m_gal = re.match(r'(\d+)T(\d+)', galois)
            if m_gal and m_gal.group(2) == "1":
                obj_concepts.append("verb_galois_abelian")
            obj_concepts.append("verb_involves_galois")

        # Quadratic type (degree 2)
        if degree == 2:
            if disc is not None:
                if int(disc) > 0:
                    obj_concepts.append("verb_real_quadratic")
                else:
                    obj_concepts.append("verb_imaginary_quadratic")

        # Regulator
        if reg is not None:
            obj_concepts.append("verb_has_regulator")
            obj_concepts.append("verb_involves_regulator")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "NumberFields", "object_id": label,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "verb", "source": "NumberFields"} for c in concepts], links


def extract_verb_isogenies() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from Isogenies: supersingularity, graph diameter, special primes."""
    from search_engine import ISOGENY_GRAPHS
    import numpy as np
    if not ISOGENY_GRAPHS.exists():
        return [], []

    concepts = set()
    links = []

    # Small primes with special isogeny structure
    _SPECIAL_PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47}

    for pdir in sorted(ISOGENY_GRAPHS.iterdir()):
        if not pdir.is_dir():
            continue
        prime = pdir.name
        try:
            p = int(prime)
        except ValueError:
            continue

        obj_id = f"isogeny_p{prime}"
        obj_concepts = ["verb_supersingular", "verb_involves_isogeny"]

        # Special prime structure
        if p in _SPECIAL_PRIMES:
            obj_concepts.append(f"verb_involves_prime_{p}")

        # Graph diameter from adjacency matrix
        npz_files = list(pdir.glob("*.npz"))
        if npz_files:
            try:
                adj = np.load(str(npz_files[0]))
                for key in adj.files:
                    mat = adj[key]
                    n = mat.shape[0]
                    if n > 0 and n < 500:
                        # BFS-based diameter estimate
                        from collections import deque
                        diameter = 0
                        binary = (mat > 0).astype(int)
                        for start in range(min(n, 10)):  # sample starts
                            dist = [-1] * n
                            dist[start] = 0
                            q = deque([start])
                            while q:
                                u = q.popleft()
                                for v in range(n):
                                    if binary[u, v] and dist[v] < 0:
                                        dist[v] = dist[u] + 1
                                        q.append(v)
                            max_d = max(d for d in dist if d >= 0)
                            diameter = max(diameter, max_d)
                        if diameter > 0:
                            obj_concepts.append(f"verb_graph_diameter_{diameter}")
                    break
            except Exception:
                pass

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Isogenies", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "verb", "source": "Isogenies"} for c in concepts], links


def extract_verb_spacegroups() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from Space Groups: crystal system, centrosymmetry, Wyckoff, symmorphic."""
    from search_engine import BILBAO_DIR
    if not BILBAO_DIR.exists():
        return [], []

    concepts = set()
    links = []

    _sg_systems = {
        range(1, 3): "triclinic", range(3, 16): "monoclinic",
        range(16, 75): "orthorhombic", range(75, 143): "tetragonal",
        range(143, 168): "trigonal", range(168, 195): "hexagonal",
        range(195, 231): "cubic",
    }

    # Expected number of generators for symmorphic groups by crystal system
    # (approximation: symmorphic groups have fewer generators than non-symmorphic)
    _SYMMORPHIC_SG = {
        1, 2, 3, 5, 6, 8, 10, 12, 16, 21, 22, 23, 25, 35, 38, 42, 44, 47,
        65, 69, 71, 75, 79, 81, 82, 83, 87, 89, 97, 99, 107, 111, 115, 119,
        121, 123, 131, 139, 143, 146, 147, 148, 149, 150, 155, 156, 157, 160,
        162, 164, 166, 168, 174, 175, 177, 183, 187, 189, 191, 195, 196, 197,
        200, 202, 204, 207, 209, 211, 215, 216, 217, 221, 225, 229,
    }

    for sg_file in sorted(BILBAO_DIR.glob("sg_*.json")):
        try:
            data = json.loads(sg_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        sg_num = data.get("space_group_number", 0)
        obj_id = f"sg_{sg_num}"
        obj_concepts = []

        # Crystal system verb
        for rng, system in _sg_systems.items():
            if sg_num in rng:
                obj_concepts.append(f"verb_crystal_system_{_canonicalize(system)}")
                break

        # Centrosymmetric: point group order is even
        pg_order = data.get("point_group_order")
        if pg_order and int(pg_order) % 2 == 0:
            obj_concepts.append("verb_centrosymmetric")

        # Wyckoff positions
        n_wyckoff = data.get("num_wyckoff_positions")
        if n_wyckoff:
            obj_concepts.append(f"verb_has_wyckoff_{n_wyckoff}")

        # Symmorphic
        if sg_num in _SYMMORPHIC_SG:
            obj_concepts.append("verb_symmorphic")

        # Cross-dataset bridge verbs
        obj_concepts.append("verb_involves_space_group")
        if pg_order:
            obj_concepts.append("verb_involves_lattice")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "SpaceGroups", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "verb", "source": "SpaceGroups"} for c in concepts], links


def extract_verb_polytopes() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from Polytopes: convexity, simpliciality, dimension, symmetry."""
    from search_engine import POLYTOPES_DIR
    if not POLYTOPES_DIR.exists():
        return [], []

    concepts = set()
    links = []

    for json_file in sorted(POLYTOPES_DIR.glob("*.json")):
        if json_file.name == "manifest.json":
            continue
        try:
            entries = json.loads(json_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(entries, list):
            continue

        collection_name = json_file.stem
        for i, entry in enumerate(entries[:200]):
            if not isinstance(entry, dict) or not entry:
                continue
            obj_id = f"{collection_name}_{i}"
            obj_concepts = []

            dim = entry.get("DIM") or entry.get("AMBIENT_DIM")
            n_verts = entry.get("N_VERTICES")
            fvec = entry.get("F_VECTOR")

            # Convex — polyDB polytopes are convex by construction
            obj_concepts.append("verb_convex")
            obj_concepts.append("verb_involves_polytope")

            # Simplicial: f_0 = dim + 1 (minimal vertices for dimension)
            if dim is not None and n_verts is not None:
                if int(n_verts) == int(dim) + 1:
                    obj_concepts.append("verb_simplicial")

            # Dimension verb
            if dim is not None:
                obj_concepts.append(f"verb_dimension_{dim}")

            # Symmetry: check for symmetry-related keys
            if (entry.get("GROUP") or entry.get("N_ORBITS_OF_VERTICES")
                    or entry.get("SYMMETRY") or entry.get("GROUP_ORDER")):
                obj_concepts.append("verb_has_symmetry")

            for concept in obj_concepts:
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "Polytopes", "object_id": obj_id,
                    "relationship": "has_property",
                })

    return [{"id": c, "type": "verb", "source": "Polytopes"} for c in concepts], links


def extract_verb_pibase() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from pi-Base: topological property verbs."""
    from search_engine import PIBASE_DIR
    if not PIBASE_DIR.exists():
        return [], []

    concepts = set()
    links = []

    # Map pi-Base property IDs/filenames to canonical verb concepts
    _PROP_VERB_MAP = {
        "compact": "verb_topo_compact",
        "hausdorff": "verb_topo_hausdorff",
        "metrizable": "verb_topo_metrizable",
        "connected": "verb_topo_connected",
        "separable": "verb_topo_separable",
        "t2": "verb_topo_hausdorff",       # T2 = Hausdorff
        "t1": "verb_topo_hausdorff",        # conservative — T1 is weaker but bridge-worthy
        "path_connected": "verb_topo_connected",
        "second_countable": "verb_topo_separable",
        "paracompact": "verb_topo_compact",
    }

    spaces_dir = PIBASE_DIR / "spaces"
    if not spaces_dir.exists():
        return [], []

    for space_dir in sorted(spaces_dir.iterdir()):
        if not space_dir.is_dir():
            continue

        obj_id = space_dir.name
        obj_concepts = []

        # Read properties from property files
        props_dir = space_dir / "properties"
        if props_dir.is_dir():
            for prop_file in props_dir.glob("*.md"):
                prop_text = prop_file.read_text(encoding="utf-8", errors="replace")
                if "value: true" not in prop_text.lower():
                    continue
                prop_name = prop_file.stem.lower()

                # Direct match to verb map
                for key, verb in _PROP_VERB_MAP.items():
                    if key in prop_name:
                        obj_concepts.append(verb)

                # Also check for the five core properties by name
                for core in ["compact", "hausdorff", "metrizable", "connected", "separable"]:
                    if core in prop_name:
                        obj_concepts.append(f"verb_topo_{core}")

        # Deduplicate per object
        obj_concepts = list(set(obj_concepts))

        # Always add topology involvement for cross-dataset bridging
        obj_concepts.append("verb_involves_topology")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "piBase", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "verb", "source": "piBase"} for c in concepts], links


def extract_verb_mmlkg() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from MMLKG: hub status, foundational references, topic prefixes."""
    from search_engine import MMLKG_REFS
    import csv
    if not MMLKG_REFS.exists():
        return [], []

    concepts = set()
    links = []
    article_refs = defaultdict(set)
    article_in_degree = defaultdict(int)

    with open(MMLKG_REFS, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            src_article = row[0]
            tgt_article = row[2] if len(row) > 2 else row[1]
            article_refs[src_article].add(tgt_article)
            article_in_degree[tgt_article] += 1

    # Prefix-based topic classification
    _ALGEBRAIC_PREFIXES = {
        "group", "ring", "vectsp", "algstr", "mod", "ideal", "field",
        "polynom", "matrix", "linalg", "matrlin", "grsolv", "rlvect",
    }
    _ANALYTIC_PREFIXES = {
        "sin", "integr", "mesfunc", "measure", "comseq", "rfunct",
        "seq", "series", "limfunc", "fcont", "fdiff",
    }
    _TOPOLOGICAL_PREFIXES = {
        "tops", "topsp", "topalg", "metric", "tmap", "pcomps",
        "connsp", "compts",
    }
    _FOUNDATIONAL = {"tarski", "xboole", "boole", "zfmisc", "subset", "ordinal"}

    for article, refs in article_refs.items():
        obj_id = f"mizar_{article}"
        obj_concepts = []

        # Hub status (high out-degree)
        if len(refs) > 20:
            obj_concepts.append("verb_mizar_hub")

        # Foundational: references tarski or xboole-family articles
        refs_lower = {r.lower() for r in refs}
        if refs_lower & _FOUNDATIONAL:
            obj_concepts.append("verb_mizar_foundational")

        # Topic classification from article name prefix
        art_lower = article.lower().rstrip("_0123456789")
        for pfx in _ALGEBRAIC_PREFIXES:
            if art_lower.startswith(pfx):
                obj_concepts.append("verb_mizar_algebraic")
                break
        for pfx in _ANALYTIC_PREFIXES:
            if art_lower.startswith(pfx):
                obj_concepts.append("verb_mizar_analytic")
                break
        for pfx in _TOPOLOGICAL_PREFIXES:
            if art_lower.startswith(pfx):
                obj_concepts.append("verb_mizar_topological")
                break

        # Cross-dataset bridge verbs from topic
        if "verb_mizar_algebraic" in obj_concepts:
            obj_concepts.append("verb_involves_algebra")
        if "verb_mizar_analytic" in obj_concepts:
            obj_concepts.append("verb_involves_analysis")
        if "verb_mizar_topological" in obj_concepts:
            obj_concepts.append("verb_involves_topology")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "MMLKG", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "verb", "source": "MMLKG"} for c in concepts], links


def extract_verb_local_fields() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from Local Fields: wild ramification, prime, extension degree."""
    from search_engine import LOCAL_FIELDS_DIR
    if not LOCAL_FIELDS_DIR.exists():
        return [], []

    concepts = set()
    links = []

    for fpath in LOCAL_FIELDS_DIR.iterdir():
        if not fpath.is_file():
            continue
        name = fpath.name
        m = re.match(r'p(\d+)d(\d+)', name)
        if not m:
            continue
        prime, degree = int(m.group(1)), int(m.group(2))

        obj_id = f"localfield_p{prime}_d{degree}"
        obj_concepts = [
            "verb_wildly_ramified",
            f"verb_ramification_prime_{prime}",
            f"verb_extension_degree_{degree}",
            "verb_involves_ramification",
        ]

        # Cross-dataset bridge: prime involvement
        if _is_prime(prime):
            obj_concepts.append("verb_involves_prime")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "LocalFields", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "verb", "source": "LocalFields"} for c in concepts], links


def extract_verb_genus2() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from genus-2 curves: conductor-discriminant relationships, Sato-Tate structure."""
    from search_engine import GENUS2_PG, GENUS2_JSON
    src = GENUS2_PG if GENUS2_PG.exists() else GENUS2_JSON
    if not src.exists(): return [], []
    raw = json.loads(src.read_text(encoding="utf-8"))
    data = raw.get("records", raw) if isinstance(raw, dict) else raw

    concepts = set()
    links = []

    for curve in data:
        label = curve.get("label", "")
        cond = curve.get("conductor") or curve.get("cond")
        disc = curve.get("discriminant")
        st = curve.get("st_group", "")
        rn = curve.get("root_number")
        torsion = curve.get("torsion", [])

        obj_concepts = []

        # Conductor-discriminant relationship (key bridge to EC and NF)
        obj_concepts.append("verb_involves_conductor")
        obj_concepts.append("verb_involves_discriminant")
        if cond is not None and disc is not None and cond != 0:
            ratio = abs(disc) / cond if cond != 0 else 0
            if ratio == 1:
                obj_concepts.append("verb_conductor_equals_discriminant")
            elif ratio < 10:
                obj_concepts.append("verb_small_disc_conductor_ratio")

        # Sato-Tate group (bridges to Galois representations, modular forms)
        if st:
            obj_concepts.append("verb_has_sato_tate")
            if "USp" in st:
                obj_concepts.append("verb_generic_sato_tate")
            else:
                obj_concepts.append("verb_exceptional_sato_tate")

        # Root number / rank parity (bridges to BSD, L-functions)
        if rn is not None:
            obj_concepts.append("verb_involves_root_number")
            obj_concepts.append("verb_involves_l_function")

        # Torsion structure
        if isinstance(torsion, list) and torsion:
            obj_concepts.append("verb_has_torsion")
            if any(t > 1 for t in torsion if isinstance(t, int)):
                obj_concepts.append("verb_nontrivial_torsion")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Genus2", "object_id": label,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "verb", "source": "Genus2"} for c in concepts], links


def extract_verb_maass() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from Maass forms: spectral theory, symmetry, Fricke."""
    from search_engine import MAASS_PG, MAASS_JSON
    src = MAASS_PG if MAASS_PG.exists() else MAASS_JSON
    if not src.exists(): return [], []
    raw = json.loads(src.read_text(encoding="utf-8"))
    data = raw.get("records", raw) if isinstance(raw, dict) else raw

    concepts = set()
    links = []

    for form in data:
        label = form.get("maass_label", form.get("label", ""))
        level = form.get("level")
        fricke = form.get("fricke_eigenvalue", form.get("fricke"))
        sp = form.get("spectral_parameter")

        obj_concepts = ["verb_involves_spectral_parameter", "verb_involves_laplacian"]

        # Fricke eigenvalue bridges to modular forms
        if fricke is not None:
            obj_concepts.append("verb_involves_fricke")
            if fricke == 1:
                obj_concepts.append("verb_fricke_plus")
            elif fricke == -1:
                obj_concepts.append("verb_fricke_minus")

        # Level bridges to modular forms and elliptic curves
        if level is not None:
            obj_concepts.append("verb_involves_level")

        # Spectral parameter is the key number-theoretic invariant
        if sp is not None:
            obj_concepts.append("verb_involves_eigenvalue")
            # Connection to zeros of zeta function
            obj_concepts.append("verb_involves_zeta")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Maass", "object_id": label,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "verb", "source": "Maass"} for c in concepts], links


def extract_verb_lattices() -> tuple[list[dict], list[dict]]:
    """Extract verb concepts from lattices: packing, coding theory, modular forms connection."""
    from search_engine import LATTICES_PG, LATTICES_JSON
    src = LATTICES_PG if LATTICES_PG.exists() else LATTICES_JSON
    if not src.exists(): return [], []
    raw = json.loads(src.read_text(encoding="utf-8"))
    data = raw.get("records", raw.get("lattices", raw)) if isinstance(raw, dict) else raw

    concepts = set()
    links = []

    for lat in data:
        name = lat.get("name", "")
        if not isinstance(name, str):
            name = str(name) if name else ""
        obj_id = name or lat.get("label", "")
        dim = lat.get("dim")
        det = lat.get("det")
        kissing = lat.get("kissing")
        min_norm = lat.get("min_norm")

        obj_concepts = ["verb_involves_packing", "verb_involves_lattice"]

        # Theta series connection (bridges to modular forms)
        obj_concepts.append("verb_involves_theta_series")
        obj_concepts.append("verb_involves_modular_form")

        # Root lattices bridge to Lie algebras
        if name and isinstance(name, str) and re.match(r'^[ADE]\d', name):
            obj_concepts.append("verb_root_lattice")
            obj_concepts.append("verb_involves_lie_algebra")

        # Kissing number bridges to sphere packing and coding theory
        if kissing is not None:
            obj_concepts.append("verb_involves_kissing_number")

        # Determinant bridges to discriminants
        if det is not None:
            obj_concepts.append("verb_involves_determinant")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "Lattices", "object_id": obj_id,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "verb", "source": "Lattices"} for c in concepts], links


def extract_verb_concepts() -> tuple[list[dict], list[dict]]:
    """
    Master verb extractor: runs all per-dataset verb extractors.
    Returns (concepts, links) aggregated across datasets.
    """
    all_concepts = []
    all_links = []

    verb_extractors = [
        ("Fungrim-verbs", extract_verb_fungrim),
        ("mathlib-verbs", extract_verb_mathlib),
        ("ANTEDB-verbs", extract_verb_antedb),
        ("LMFDB-verbs", extract_verb_lmfdb),
        ("KnotInfo-verbs", extract_verb_knotinfo),
        ("NumberFields-verbs", extract_verb_number_fields),
        ("Isogenies-verbs", extract_verb_isogenies),
        ("SpaceGroups-verbs", extract_verb_spacegroups),
        ("Polytopes-verbs", extract_verb_polytopes),
        ("piBase-verbs", extract_verb_pibase),
        ("MMLKG-verbs", extract_verb_mmlkg),
        ("LocalFields-verbs", extract_verb_local_fields),
        ("Genus2-verbs", extract_verb_genus2),
        ("Maass-verbs", extract_verb_maass),
        ("Lattices-verbs", extract_verb_lattices),
        ("SmallGroups-verbs", extract_verb_smallgroups),
    ]

    for name, fn in verb_extractors:
        print(f"  Extracting {name}...")
        try:
            concepts, links = fn()
            all_concepts.extend(concepts)
            all_links.extend(links)
            print(f"    {len(concepts)} verb concepts, {len(links)} verb links")
        except Exception as e:
            print(f"    ERROR: {e}")

    return all_concepts, all_links


# ---------------------------------------------------------------------------
# Build and query
# ---------------------------------------------------------------------------

def build_index() -> dict:
    """Extract concepts from all datasets. Returns stats."""
    print("Building concept index...")
    CONVERGENCE.joinpath("data").mkdir(parents=True, exist_ok=True)

    all_concepts = {}  # id → concept dict
    all_links = []

    extractors = [
        ("KnotInfo", extract_knotinfo),
        ("LMFDB", extract_lmfdb),
        ("Fungrim", extract_fungrim),
        ("ANTEDB", extract_antedb),
        ("mathlib", extract_mathlib),
        ("NumberFields", extract_number_fields),
        ("Isogenies", extract_isogenies),
        ("LocalFields", extract_local_fields),
        ("SpaceGroups", extract_spacegroups),
        ("Polytopes", extract_polytopes),
        ("piBase", extract_pibase),
        ("MMLKG", extract_mmlkg),
        ("Genus2", extract_genus2),
        ("Maass", extract_maass),
        ("Lattices", extract_lattices),
        ("OpenAlex", extract_openalex),
        ("SmallGroups", extract_smallgroups),
    ]

    for name, fn in extractors:
        print(f"  Extracting {name}...")
        try:
            concepts, links = fn()
            for c in concepts:
                cid = c["id"]
                if cid not in all_concepts:
                    all_concepts[cid] = c
                else:
                    # Merge sources
                    existing = all_concepts[cid]
                    if c["source"] not in existing.get("sources", [existing["source"]]):
                        existing.setdefault("sources", [existing["source"]]).append(c["source"])
            all_links.extend(links)
            print(f"    {len(concepts)} concepts, {len(links)} links")
        except Exception as e:
            print(f"    ERROR: {e}")

    # --- Verb concept extraction (cross-domain bridges) ---
    print("\n  Extracting verb concepts (cross-domain bridges)...")
    verb_concepts, verb_links = extract_verb_concepts()
    for c in verb_concepts:
        cid = c["id"]
        if cid not in all_concepts:
            all_concepts[cid] = c
        else:
            existing = all_concepts[cid]
            if c["source"] not in existing.get("sources", [existing["source"]]):
                existing.setdefault("sources", [existing["source"]]).append(c["source"])
    all_links.extend(verb_links)
    n_verb = len(verb_concepts)
    n_verb_links = len(verb_links)
    print(f"    Total: {n_verb} verb concepts, {n_verb_links} verb links")

    # Write concepts
    with open(CONCEPTS_FILE, "w", encoding="utf-8") as f:
        for c in sorted(all_concepts.values(), key=lambda x: x["id"]):
            f.write(json.dumps(c) + "\n")

    # Write links
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        for link in all_links:
            f.write(json.dumps(link) + "\n")

    stats = {
        "n_concepts": len(all_concepts),
        "n_links": len(all_links),
        "by_dataset": defaultdict(int),
    }
    for link in all_links:
        stats["by_dataset"][link["dataset"]] += 1
    stats["by_dataset"] = dict(stats["by_dataset"])

    print(f"\nIndex built: {stats['n_concepts']} concepts, {stats['n_links']} links")
    print(f"  By dataset: {stats['by_dataset']}")
    return stats


def find_bridges(min_datasets: int = 2, max_results: int = 5000) -> list[dict]:
    """Find concepts shared across multiple datasets — these are bridge points."""
    print("\nFinding bridges...")

    # Load links
    links_by_concept = defaultdict(lambda: defaultdict(list))
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            link = json.loads(line)
            links_by_concept[link["concept"]][link["dataset"]].append(link["object_id"])

    # Find concepts present in 2+ datasets
    bridges = []
    for concept, datasets in links_by_concept.items():
        if len(datasets) >= min_datasets:
            total_objects = sum(len(objs) for objs in datasets.values())
            # Verb bridges are always valuable regardless of object count.
            # Noun bridges with >50K objects are too generic (e.g. "even", "odd").
            is_verb = concept.startswith("verb_")
            if not is_verb and total_objects > 50000:
                continue

            bridge = {
                "concept": concept,
                "n_datasets": len(datasets),
                "datasets": {ds: len(objs) for ds, objs in datasets.items()},
                "total_objects": total_objects,
                "sample_objects": {ds: objs[:5] for ds, objs in datasets.items()},
                "specificity": 1.0 / max(total_objects, 1),
            }
            bridges.append(bridge)

    # Sort by: more datasets first, then more specific (fewer total objects)
    bridges.sort(key=lambda b: (-b["n_datasets"], b["total_objects"]))

    # Write bridges
    with open(BRIDGES_FILE, "w", encoding="utf-8") as f:
        for b in bridges[:max_results]:
            f.write(json.dumps(b) + "\n")

    # Stats
    by_n_datasets = defaultdict(int)
    for b in bridges:
        by_n_datasets[b["n_datasets"]] += 1

    print(f"Found {len(bridges)} bridge concepts")
    print(f"  By dataset count: {dict(by_n_datasets)}")

    # Show top bridges
    print(f"\nTop 20 bridges:")
    for b in bridges[:20]:
        ds_str = ", ".join(f"{ds}({n})" for ds, n in sorted(b["datasets"].items()))
        print(f"  {b['concept']:40s} | {b['n_datasets']} datasets | {ds_str}")

    return bridges[:max_results]


if __name__ == "__main__":
    stats = build_index()
    bridges = find_bridges()
    print(f"\nBridges saved to {BRIDGES_FILE}")
