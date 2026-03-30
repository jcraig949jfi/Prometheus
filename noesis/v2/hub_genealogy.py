"""
Hub Genealogy — How impossibility theorems derive from each other.

Builds a directed graph where edge A→B means "A implies B" or "B is a
special case / direct consequence of A". Identifies root theorems (most
fundamental), leaf theorems (most specialized), longest derivation chains,
and the most generative hubs.

Author: Aletheia (Structural Mathematician, Project Prometheus)
Date: 2026-03-29
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import duckdb
import networkx as nx
from collections import defaultdict
from pathlib import Path

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"
OUT_GRAPHML = Path(__file__).parent / "hub_genealogy.graphml"
OUT_JSON = Path(__file__).parent / "hub_genealogy_results.json"

# ═══════════════════════════════════════════════════════════════════
# 1. Load all hubs from the database
# ═══════════════════════════════════════════════════════════════════

con = duckdb.connect(str(DB_PATH), read_only=True)
hubs = con.execute("""
    SELECT comp_id, description, structural_pattern
    FROM abstract_compositions
""").fetchall()
con.close()

hub_map = {}
for comp_id, desc, pattern in hubs:
    hub_map[comp_id] = {
        "description": desc or "",
        "structural_pattern": pattern or "",
    }

print(f"Loaded {len(hub_map)} hubs from database")

# ═══════════════════════════════════════════════════════════════════
# 2. Known derivation chains (mathematically established)
#    Edge: parent → child  means  parent implies child / child derives from parent
# ═══════════════════════════════════════════════════════════════════

KNOWN_DERIVATIONS = [
    # ── Logic / Computability ──
    # Gödel's incompleteness is the ur-theorem; multiple IDs exist in the DB
    ("GODEL_INCOMPLETENESS", "GOEDEL_INCOMPLETENESS_1"),
    ("GODEL_INCOMPLETENESS", "GOEDEL_INCOMPLETENESS_2"),
    ("GODEL_INCOMPLETENESS", "FOUNDATIONAL_IMPOSSIBILITY"),
    ("GOEDEL_INCOMPLETENESS_1", "GOEDEL_INCOMPLETENESS_2"),       # G1 → G2
    ("GODEL_INCOMPLETENESS", "HALTING_PROBLEM"),                   # Gödel → Halting
    ("HALTING_PROBLEM", "RICE_THEOREM"),                           # Halting → Rice
    ("HALTING_PROBLEM", "ENTSCHEIDUNGSPROBLEM"),                   # Halting → Entscheidungsproblem
    ("GODEL_INCOMPLETENESS", "TARSKI_UNDEFINABILITY"),             # Gödel → Tarski
    ("GODEL_INCOMPLETENESS", "CHURCH_UNDECIDABILITY"),             # Gödel → Church
    ("CHURCH_UNDECIDABILITY", "HALTING_PROBLEM"),                  # Church ↔ Halting (equivalent, but Church published first)
    ("HALTING_PROBLEM", "MATIYASEVICH_HILBERT10"),                 # Halting → Hilbert's 10th
    ("GOEDEL_INCOMPLETENESS_1", "GOODSTEIN_INDEPENDENCE"),         # G1 → Goodstein
    ("GOEDEL_INCOMPLETENESS_1", "PARIS_HARRINGTON"),               # G1 → Paris-Harrington
    ("CANTOR_DIAGONALIZATION", "GODEL_INCOMPLETENESS"),            # Cantor's method → Gödel
    ("CANTOR_DIAGONALIZATION", "HALTING_PROBLEM"),                 # Cantor's diag → Halting (technique)
    ("CANTOR_DIAGONALIZATION", "INDEPENDENCE_OF_CH"),              # Cantor → CH independence
    ("CANTOR_DIAGONALIZATION", "IMPOSSIBILITY_BANACH_TARSKI_PARADOX"),  # AC → Banach-Tarski
    ("IMPOSSIBILITY_NAIVE_SET_THEORY", "CANTOR_DIAGONALIZATION"),  # Russell's paradox context
    ("HALTING_PROBLEM", "IMPOSSIBILITY_COMPUTATIONAL_IRREDUCIBILITY_CA"),  # Halting → CA irreducibility
    ("RICE_THEOREM", "MINIMUM_CIRCUIT_SIZE_PROBLEM"),              # Rice → MCSP hardness connection
    ("HALTING_PROBLEM", "UNDECIDED_TILES"),                        # Halting → Wang tile undecidability

    # ── Complexity theory ──
    ("HALTING_PROBLEM", "COMPLEXITY_HIERARCHY"),                    # Undecidability → complexity separations
    ("PCP_THEOREM_HARDNESS", "UNIQUE_GAMES_CONJECTURE"),           # PCP → UGC
    ("IP_EQUALS_PSPACE", "PCP_THEOREM_HARDNESS"),                  # IP=PSPACE techniques → PCP
    ("CIRCUIT_LOWER_BOUNDS", "CIRCUIT_COMPLEXITY_LOWER_BOUND"),    # Same family
    ("BGS_ORACLE_SEPARATION", "NATURAL_PROOFS_BARRIER"),           # Oracle barriers → natural proofs
    ("BGS_ORACLE_SEPARATION", "ALGEBRIZATION_BARRIER"),            # Oracle barriers → algebrization

    # ── Social choice / Mechanism design ──
    ("ARROW_IMPOSSIBILITY", "GIBBARD_SATTERTHWAITE"),              # Arrow → GS
    ("ARROW_IMPOSSIBILITY", "IMPOSSIBILITY_ARROW"),                # Duplicate IDs
    ("IMPOSSIBILITY_ARROW", "GIBBARD_SATTERTHWAITE"),              # Arrow → GS (alt ID)
    ("GIBBARD_SATTERTHWAITE", "SEN_LIBERAL_PARADOX"),              # GS → Sen
    ("ARROW_IMPOSSIBILITY", "SOCIAL_CHOICE_IMPOSSIBILITY"),        # Arrow → social choice meta
    ("ARROW_IMPOSSIBILITY", "CONDORCET_PARADOX"),                  # Arrow generalizes Condorcet
    ("CONDORCET_PARADOX", "GIBBARD_SATTERTHWAITE"),                # Condorcet → GS
    ("ARROW_IMPOSSIBILITY", "IMPOSSIBILITY_DICTATORSHIP_WITHOUT_MONEY"),
    ("GIBBARD_SATTERTHWAITE", "IMPOSSIBILITY_IMPLEMENTATION_MASKIN"),  # GS → Maskin
    ("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "IMPOSSIBILITY_BILATERAL_TRADE_CHATTERJEE_SAMUELSON"),
    ("ARROW_IMPOSSIBILITY", "IMPOSSIBILITY_WELFARE_IMPOSSIBILITY_INTERPERSONAL"),
    ("IMPOSSIBILITY_WELFARE_IMPOSSIBILITY_INTERPERSONAL", "INTERPERSONAL_UTILITY"),
    ("ARROW_IMPOSSIBILITY", "GERRYMANDERING_IMPOSSIBILITY"),
    ("IMPOSSIBILITY_VCG_BUDGET_BALANCE", "VCG_BUDGET_IMPOSSIBILITY"),  # Same theorem, diff IDs
    ("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "IMPOSSIBILITY_VCG_BUDGET_BALANCE"),
    ("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "IMPOSSIBILITY_REVELATION_PRINCIPLE_LIMITS"),
    ("IMPOSSIBILITY_NASH_PPAD_HARDNESS", "IMPOSSIBILITY_COMPETITIVE_EQUILIBRIUM_INDIVISIBLE"),
    ("IMPOSSIBILITY_NO_FREE_LUNCH", "WOLPERT_NO_FREE_LUNCH"),      # Same theorem
    ("IMPOSSIBILITY_CONDORCET_JURY_LIMITATIONS", "CONDORCET_PARADOX"),
    ("IMPOSSIBILITY_MUNDELL_FLEMING", "IMPOSSIBILITY_IMPOSSIBLE_TRINITY_MACROECONOMICS"),  # Same theorem
    ("IMPOSSIBILITY_GROSSMAN_STIGLITZ_PARADOX", "EFFICIENT_MARKET_LIMITS"),
    ("IMPOSSIBILITY_GOODHARTS_LAW", "IMPOSSIBILITY_LUCAS_CRITIQUE_POLICY_INVARIANCE"),  # Goodhart → Lucas
    ("SONNENSCHEIN_MANTEL_DEBREU", "IMPOSSIBILITY_SECOND_WELFARE_IMPOSSIBILITY"),

    # ── Game theory ──
    ("BROUWER_FIXED_POINT", "KAKUTANI_FIXED_POINT"),               # Brouwer → Kakutani
    ("KAKUTANI_FIXED_POINT", "IMPOSSIBILITY_NASH_PPAD_HARDNESS"),  # Kakutani → Nash existence/hardness
    ("BROUWER_FIXED_POINT", "NO_RETRACTION_THEOREM"),              # Brouwer → No retraction
    ("IMPOSSIBILITY_FOLK_THEOREM_BOUNDARY", "IMPOSSIBILITY_CONGESTION_PRICE_OF_ANARCHY"),
    ("IMPOSSIBILITY_ENVY_FREE_DIVISION", "IMPOSSIBILITY_STABLE_MATCHING_THREE_SIDED"),
    ("IMPOSSIBILITY_REVENUE_EQUIVALENCE_BREAKDOWN", "REVENUE_EQUIVALENCE"),

    # ── Quantum mechanics ──
    ("HEISENBERG_UNCERTAINTY", "IMPOSSIBILITY_NO_CLONING_THEOREM"),  # Heisenberg → No-Cloning
    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "IMPOSSIBILITY_NO_BROADCASTING_THEOREM"),  # No-Cloning → No-Broadcasting
    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "IMPOSSIBILITY_NO_DELETING_THEOREM"),      # No-Cloning → No-Deleting
    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "NO_BROADCASTING"),        # Alt IDs
    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "NO_DELETION"),            # Alt IDs
    ("IMPOSSIBILITY_NO_DELETING_THEOREM", "NO_DELETION"),
    ("IMPOSSIBILITY_NO_BROADCASTING_THEOREM", "NO_BROADCASTING"),
    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "IMPOSSIBILITY_NO_HIDING_THEOREM"),
    ("IMPOSSIBILITY_NO_HIDING_THEOREM", "NO_HIDING"),
    ("HEISENBERG_UNCERTAINTY", "IMPOSSIBILITY_BELLS_THEOREM"),      # Uncertainty → Bell
    ("IMPOSSIBILITY_BELLS_THEOREM", "KOCHEN_SPECKER"),              # Bell → Kochen-Specker
    ("IMPOSSIBILITY_BELLS_THEOREM", "IMPOSSIBILITY_TSIRELSON_BOUND"),
    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "IMPOSSIBILITY_QUANTUM_KEY_DISTRIBUTION_RATE_LIMIT"),
    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "IMPOSSIBILITY_EASTIN_KNILL_THEOREM"),
    ("IMPOSSIBILITY_BELLS_THEOREM", "IMPOSSIBILITY_ENTANGLEMENT_MONOGAMY"),
    ("IMPOSSIBILITY_ENTANGLEMENT_MONOGAMY", "IMPOSSIBILITY_NO_COMMUNICATION_THEOREM"),
    ("IMPOSSIBILITY_NO_COMMUNICATION_THEOREM", "NO_COMMUNICATION"),
    ("HEISENBERG_UNCERTAINTY", "IMPOSSIBILITY_HOLEVO_BOUND"),
    ("SHANNON_CAPACITY", "IMPOSSIBILITY_HOLEVO_BOUND"),             # Shannon → Holevo
    ("IMPOSSIBILITY_HOLEVO_BOUND", "IMPOSSIBILITY_QUANTUM_CAPACITY_NO_ADDITIVITY"),
    ("HEISENBERG_UNCERTAINTY", "IMPOSSIBILITY_MARGOLUS_LEVITIN_SPEED_LIMIT"),
    ("IMPOSSIBILITY_QUANTUM_ERROR_CORRECTION_THRESHOLD", "IMPOSSIBILITY_EASTIN_KNILL_THEOREM"),
    ("HEISENBERG_UNCERTAINTY", "GABOR_LIMIT"),                      # Uncertainty → Gabor

    # ── Thermodynamics ──
    ("CARNOT_LIMIT", "KELVIN_PLANCK"),                              # Carnot → Kelvin-Planck
    ("CARNOT_LIMIT", "CLAUSIUS_INEQUALITY"),                        # Carnot → Clausius
    ("KELVIN_PLANCK", "LANDAUER_LIMIT"),                            # Kelvin-Planck → Landauer
    ("CLAUSIUS_INEQUALITY", "THIRD_LAW_UNATTAINABILITY"),           # Clausius → Third law
    ("LANDAUER_LIMIT", "IMPOSSIBILITY_MARGOLUS_LEVITIN_SPEED_LIMIT"),  # Landauer → speed limit
    ("CARNOT_LIMIT", "IMPOSSIBILITY_KLEIBER_METABOLIC_SCALING"),    # Thermo → metabolic scaling

    # ── Topology ──
    ("IMPOSSIBILITY_BORSUK_ULAM", "HAIRY_BALL_THEOREM"),            # Borsuk-Ulam → Hairy Ball
    ("IMPOSSIBILITY_BORSUK_ULAM", "HAIRY_BALL"),                    # Alt ID
    ("HAIRY_BALL_THEOREM", "EULER_CHARACTERISTIC_OBSTRUCTION"),     # Hairy Ball → Euler char
    ("HAIRY_BALL", "EULER_CHARACTERISTIC_OBSTRUCTION"),             # Alt
    ("BROUWER_FIXED_POINT", "IMPOSSIBILITY_BORSUK_ULAM"),          # Brouwer → Borsuk-Ulam
    ("EULER_CHARACTERISTIC_OBSTRUCTION", "EULER_POLYHEDRON_OBSTRUCTION"),
    ("GAUSS_BONNET_CURVATURE_TOPOLOGY", "EULER_CHARACTERISTIC_OBSTRUCTION"),  # GB → Euler
    ("BROUWER_FIXED_POINT", "TOPOLOGICAL_INVARIANCE_OF_DIMENSION"),
    ("WHITNEY_EMBEDDING_OBSTRUCTION", "WHITNEY_EMBEDDING_BOUND"),
    ("POINCARE_DUALITY_OBSTRUCTION", "DEHN_SURGERY_OBSTRUCTION"),
    ("NASH_ISOMETRIC_EMBEDDING", "IMPOSSIBILITY_MAP_PROJECTION"),   # Embedding → map projection
    ("GAUSS_BONNET_CURVATURE_TOPOLOGY", "IMPOSSIBILITY_MAP_PROJECTION"),  # Theorema Egregium
    ("COVERING_SPACE_OBSTRUCTION", "KNOT_INVARIANT_INCOMPLETENESS"),
    ("TOPOLOGICAL_MANIFOLD_DIMENSION4", "IMPOSSIBILITY_EXOTIC_R4"),
    ("DEHN_IMPOSSIBILITY", "DEHN_SURGERY_OBSTRUCTION"),             # Dehn → surgery
    ("HEAWOOD_CONJECTURE", "IMPOSSIBILITY_FIVE_COLOR"),             # Map coloring

    # ── Algebra ──
    ("GALOIS_UNSOLVABILITY", "IMPOSSIBILITY_QUINTIC_INSOLVABILITY"),  # Galois → Abel-Ruffini
    ("IMPOSSIBILITY_RATIONAL_SQRT2", "IMPOSSIBILITY_TRANSCENDENCE_E_PI"),  # Irrationality → transcendence
    ("CANTOR_DIAGONALIZATION", "IMPOSSIBILITY_RATIONAL_SQRT2"),     # Countability arguments
    ("NO_DIVISION_ALGEBRA_BEYOND_8", "IMPOSSIBILITY_COMMUTATIVE_CROSS_PRODUCT"),
    ("GALOIS_UNSOLVABILITY", "IMPOSSIBILITY_ANGLE_TRISECTION"),     # Galois → constructibility
    ("GALOIS_UNSOLVABILITY", "IMPOSSIBILITY_DOUBLING_CUBE"),
    ("GALOIS_UNSOLVABILITY", "IMPOSSIBILITY_SQUARING_CIRCLE"),
    ("GALOIS_UNSOLVABILITY", "IMPOSSIBILITY_REGULAR_POLYGON"),
    ("IMPOSSIBILITY_SQUARING_CIRCLE", "IMPOSSIBILITY_TRANSCENDENCE_E_PI"),  # π transcendence
    ("BURNSIDE_IMPOSSIBILITY", "CLASSIFICATION_IMPOSSIBILITY_WILD"),

    # ── Information / Signal processing ──
    ("SHANNON_CAPACITY", "NYQUIST_LIMIT"),                          # Shannon → Nyquist
    ("SHANNON_CAPACITY", "NYQUIST_SHANNON"),                        # Alt ID
    ("NYQUIST_LIMIT", "NYQUIST_SHANNON"),                           # Same theorem
    ("SHANNON_CAPACITY", "SHANNON_CHANNEL_CAPACITY"),               # Same
    ("SHANNON_CAPACITY", "SOURCE_CODING_BOUND"),                    # Shannon → source coding
    ("SHANNON_CAPACITY", "RATE_DISTORTION_BOUND"),                  # Shannon → rate distortion
    ("SHANNON_CAPACITY", "IMPOSSIBILITY_CHANNEL_CODING_CONVERSE"),
    ("RATE_DISTORTION_BOUND", "IMPOSSIBILITY_RATE_DISTORTION_NEURAL_CODING"),
    ("RATE_DISTORTION_BOUND", "IMPOSSIBILITY_INFORMATION_BOTTLENECK"),
    ("SHANNON_CAPACITY", "IMPOSSIBILITY_CRAMER_RAO_BOUND"),        # Information → estimation
    ("IMPOSSIBILITY_CRAMER_RAO_BOUND", "IMPOSSIBILITY_KALMAN_OPTIMALITY_BOUND"),
    ("NYQUIST_LIMIT", "ABBE_DIFFRACTION_LIMIT"),                   # Sampling → diffraction
    ("NYQUIST_LIMIT", "RUNGE_PHENOMENON"),                         # Sampling → interpolation pathology
    ("IMPOSSIBILITY_GIBBS_PHENOMENON", "IMPOSSIBILITY_DU_BOIS_REYMOND_FOURIER_DIVERGENCE"),
    ("IMPOSSIBILITY_GIBBS_PHENOMENON", "IMPOSSIBILITY_UNIFORM_CONVERGENCE_FOURIER"),
    ("IMPOSSIBILITY_WEIERSTRASS_APPROXIMATION_DISCONTINUITY", "IMPOSSIBILITY_UNIFORM_APPROX_DISCONTINUOUS"),
    ("IMPOSSIBILITY_GIBBS_PHENOMENON", "IMPOSSIBILITY_MUNTZ_SZASZ_LACUNARY_IMPOSSIBILITY"),
    ("MUNTZ_SZASZ", "IMPOSSIBILITY_MUNTZ_SZASZ_LACUNARY_IMPOSSIBILITY"),
    ("IMPOSSIBILITY_FABER_THEOREM_INTERPOLATION", "RUNGE_PHENOMENON"),
    ("IMPOSSIBILITY_BERNSTEIN_LETHARGY", "IMPOSSIBILITY_CURSE_OF_DIMENSIONALITY"),
    ("WEIERSTRASS_NOWHERE_DIFFERENTIABLE", "BAIRE_CATEGORY"),      # Pathological functions

    # ── Control theory ──
    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "IMPOSSIBILITY_BODE_INTEGRAL_V2"),  # Same theorem
    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "IMPOSSIBILITY_BODE_GAIN_PHASE"),
    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "IMPOSSIBILITY_WATERBED_GENERALIZED"),
    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "IMPOSSIBILITY_ZAMES_SENSITIVITY"),
    ("IMPOSSIBILITY_BODE_INTEGRAL_V2", "IMPOSSIBILITY_TRACKING_DISTURBANCE_LIMIT"),
    ("SHANNON_CAPACITY", "IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED"),  # Info theory → control
    ("IMPOSSIBILITY_SMALL_GAIN_THEOREM", "IMPOSSIBILITY_MIMO_FUNDAMENTAL_LIMITS"),
    ("IMPOSSIBILITY_PONTRYAGIN_MAXIMUM_PRINCIPLE", "IMPOSSIBILITY_KALMAN_OPTIMALITY_BOUND"),
    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "ANTENNA_GAIN_BANDWIDTH"),

    # ── Biology / Evolution ──
    ("IMPOSSIBILITY_FISHER_FUNDAMENTAL_THEOREM", "FISHERS_THEOREM_LIMITS"),
    ("IMPOSSIBILITY_FISHER_FUNDAMENTAL_THEOREM", "IMPOSSIBILITY_PRICE_EQUATION_CONSTRAINT"),
    ("IMPOSSIBILITY_NK_FITNESS_LANDSCAPE", "IMPOSSIBILITY_MODULARITY_EVOLVABILITY_TRADEOFF"),
    ("IMPOSSIBILITY_COMPETITIVE_EXCLUSION", "IMPOSSIBILITY_LOTKA_VOLTERRA_STRUCTURAL_STABILITY"),
    ("IMPOSSIBILITY_COMPETITIVE_EXCLUSION", "PARADOX_OF_ENRICHMENT"),
    ("IMPOSSIBILITY_POPULATION_GENETICS_DRIFT_SELECTION", "MULLERS_RATCHET"),
    ("IMPOSSIBILITY_VALIANT_EVOLVABILITY", "IMPOSSIBILITY_POPULATION_GENETICS_DRIFT_SELECTION"),

    # ── Distributed systems ──
    ("IMPOSSIBILITY_CAP", "FLP_IMPOSSIBILITY"),                     # CAP → FLP
    ("FLP_IMPOSSIBILITY", "BYZANTINE_GENERALS_BOUND"),              # FLP → Byzantine
    ("IMPOSSIBILITY_CAP", "SYBIL_IMPOSSIBILITY"),
    ("SHANNON_CAPACITY", "ONE_TIME_PAD_NECESSITY"),                 # Shannon → OTP
    ("ONE_TIME_PAD_NECESSITY", "KEY_DISTRIBUTION_CLASSICAL"),

    # ── Neuroscience / Cognitive ──
    ("IMPOSSIBILITY_FITTS_HICK_SPEED_ACCURACY", "DUAL_TASK_BOTTLENECK"),
    ("SHANNON_CAPACITY", "MILLERS_LAW"),                            # Information → 7±2
    ("IMPOSSIBILITY_RATE_DISTORTION_NEURAL_CODING", "NEURAL_CODING_LIMITS"),
    ("BINDING_PROBLEM", "BROCAS_BINDING"),
    ("IMPOSSIBILITY_INFORMATION_BOTTLENECK", "IMPOSSIBILITY_UNIVERSAL_APPROXIMATION_RATE_IMPOSSIBILITY"),

    # ── Approximation theory ──
    ("IMPOSSIBILITY_KOLMOGOROV_SUPERPOSITION_COMPUTATIONAL_BARRIER", "IMPOSSIBILITY_CURSE_OF_DIMENSIONALITY"),
    ("IMPOSSIBILITY_CURSE_OF_DIMENSIONALITY", "IMPOSSIBILITY_NO_FREE_LUNCH"),

    # ── Physics (GR / cosmology) ──
    ("LIGHT_SPEED_LIMIT", "PENROSE_SINGULARITY"),
    ("LIGHT_SPEED_LIMIT", "CHRONOLOGY_PROTECTION"),
    ("PENROSE_SINGULARITY", "COSMIC_CENSORSHIP"),
    ("BEKENSTEIN_BOUND", "IMPOSSIBILITY_HOLEVO_BOUND"),             # Holographic → quantum info
    ("LIGHT_SPEED_LIMIT", "IMPOSSIBILITY_NO_COMMUNICATION_THEOREM"),
    ("WEINBERG_MASSLESS_CONSTRAINT", "LIGHT_SPEED_LIMIT"),

    # ── Statistical mechanics ──
    ("CARNOT_LIMIT", "ERGODIC_BREAKING"),
    ("KAM_THEOREM", "ERGODIC_BREAKING"),
    ("MERMIN_WAGNER", "IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2"),

    # ── Miscellaneous cross-links ──
    ("IMPOSSIBILITY_BORSUK_ULAM", "IMPOSSIBILITY_PENTAGONAL_TILING"),
    ("IMPOSSIBILITY_PENTAGONAL_TILING", "PENROSE_APERIODICITY"),
    ("RAMSEY_INEVITABILITY", "SZEMEREDI_REGULARITY_LIMIT"),
    ("LOWENHEIM_SKOLEM", "IMPOSSIBILITY_WELLORDER_WITHOUT_CHOICE"),
    ("CANTOR_DIAGONALIZATION", "LOWENHEIM_SKOLEM"),
    ("VITALI_NONMEASURABLE", "IMPOSSIBILITY_BANACH_TARSKI_PARADOX"),
    ("HUMES_GUILLOTINE", "PROBLEM_OF_INDUCTION"),
    ("QUINE_INDETERMINACY", "UNIVERSAL_GRAMMAR_LIMITS"),
    ("IMPOSSIBILITY_PYTHAGOREAN_COMMA", "IMPOSSIBILITY_CALENDAR"),  # Same structure (incommensurability)
    ("ASHBY_LIMITS", "IMPOSSIBILITY_GOODHARTS_LAW"),                # Requisite variety → Goodhart
]

# ═══════════════════════════════════════════════════════════════════
# 3. Build the directed graph
# ═══════════════════════════════════════════════════════════════════

G = nx.DiGraph()

# Add all hubs as nodes
for comp_id, data in hub_map.items():
    G.add_node(comp_id,
               description=data["description"][:200],
               structural_pattern=data["structural_pattern"][:200])

# Add derivation edges (only if both nodes exist in DB)
edges_added = 0
edges_skipped = []
for parent, child in KNOWN_DERIVATIONS:
    if parent in hub_map and child in hub_map:
        G.add_edge(parent, child, relation="implies")
        edges_added += 1
    else:
        missing = []
        if parent not in hub_map:
            missing.append(f"parent={parent}")
        if child not in hub_map:
            missing.append(f"child={child}")
        edges_skipped.append((parent, child, missing))

print(f"Edges added: {edges_added}")
print(f"Edges skipped (missing nodes): {len(edges_skipped)}")
for p, c, m in edges_skipped[:10]:
    print(f"  {p} → {c}: missing {m}")

# ═══════════════════════════════════════════════════════════════════
# 4. Analysis
# ═══════════════════════════════════════════════════════════════════

# Only consider the connected subgraph for genealogy analysis
connected_nodes = set()
for u, v in G.edges():
    connected_nodes.add(u)
    connected_nodes.add(v)
G_connected = G.subgraph(connected_nodes).copy()

print(f"\nConnected genealogy subgraph: {G_connected.number_of_nodes()} nodes, {G_connected.number_of_edges()} edges")

# ROOT theorems: no incoming edges (in-degree 0 in connected subgraph)
roots = [n for n in G_connected.nodes() if G_connected.in_degree(n) == 0]
roots.sort(key=lambda n: G_connected.out_degree(n), reverse=True)

# LEAF theorems: no outgoing edges (out-degree 0 in connected subgraph)
leaves = [n for n in G_connected.nodes() if G_connected.out_degree(n) == 0]
leaves.sort()

# Most generative: highest out-degree
generativity = [(n, G_connected.out_degree(n)) for n in G_connected.nodes()]
generativity.sort(key=lambda x: x[1], reverse=True)

# Longest path (DAG longest path)
# First check for cycles
if nx.is_directed_acyclic_graph(G_connected):
    longest_path = nx.dag_longest_path(G_connected)
    longest_path_length = len(longest_path) - 1
    print(f"DAG verified. Longest derivation chain: {longest_path_length} steps")
else:
    # Find and report cycles, then break them for analysis
    cycles = list(nx.simple_cycles(G_connected))
    print(f"WARNING: {len(cycles)} cycles found. Breaking cycles for analysis.")
    for cyc in cycles[:5]:
        print(f"  Cycle: {' → '.join(cyc)}")
    # Remove back edges to make DAG
    G_dag = G_connected.copy()
    while not nx.is_directed_acyclic_graph(G_dag):
        cycle = list(nx.simple_cycles(G_dag))[0]
        G_dag.remove_edge(cycle[-1], cycle[0])
    longest_path = nx.dag_longest_path(G_dag)
    longest_path_length = len(longest_path) - 1

# Descendant counts (all reachable from each node)
descendant_counts = {}
for node in G_connected.nodes():
    descendant_counts[node] = len(nx.descendants(G_connected, node))
desc_sorted = sorted(descendant_counts.items(), key=lambda x: x[1], reverse=True)

# Ancestor counts (how many theorems lead to this one)
ancestor_counts = {}
for node in G_connected.nodes():
    ancestor_counts[node] = len(nx.ancestors(G_connected, node))
anc_sorted = sorted(ancestor_counts.items(), key=lambda x: x[1], reverse=True)

# Find all maximal chains (paths from root to leaf)
def find_all_root_to_leaf_paths(G, roots, leaves):
    """Find representative paths from roots to leaves."""
    paths = []
    for root in roots[:10]:  # top 10 roots by generativity
        for leaf in leaves:
            try:
                path = nx.shortest_path(G, root, leaf)
                if len(path) >= 3:
                    paths.append(path)
            except nx.NetworkXNoPath:
                continue
    return paths

notable_paths = find_all_root_to_leaf_paths(G_connected, roots, leaves)
notable_paths.sort(key=len, reverse=True)

# ═══════════════════════════════════════════════════════════════════
# 5. Print results
# ═══════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("ROOT THEOREMS (no parents — most fundamental)")
print("="*70)
for r in roots:
    desc = hub_map[r]["description"][:80]
    print(f"  {r} (→ {G_connected.out_degree(r)} children, {descendant_counts[r]} total descendants)")
    print(f"    {desc}")

print(f"\n  Total roots: {len(roots)}")

print("\n" + "="*70)
print("LEAF THEOREMS (no children — most specialized)")
print("="*70)
for l in leaves[:20]:
    desc = hub_map[l]["description"][:80]
    print(f"  {l} ({ancestor_counts[l]} ancestors)")
    print(f"    {desc}")
print(f"\n  Total leaves: {len(leaves)}")

print("\n" + "="*70)
print("MOST GENERATIVE HUBS (direct children)")
print("="*70)
for n, deg in generativity[:15]:
    desc = hub_map[n]["description"][:60]
    print(f"  {n}: {deg} direct children, {descendant_counts[n]} total descendants")
    print(f"    {desc}")

print("\n" + "="*70)
print("DEEPEST DERIVATION CHAIN")
print("="*70)
print(f"  Length: {longest_path_length} steps")
print(f"  Chain: {' → '.join(longest_path)}")

print("\n" + "="*70)
print("NOTABLE DERIVATION PATHS (longest root-to-leaf)")
print("="*70)
seen = set()
for path in notable_paths[:10]:
    key = (path[0], path[-1])
    if key not in seen:
        seen.add(key)
        print(f"  [{len(path)-1} steps] {' → '.join(path)}")

print("\n" + "="*70)
print("MOST DERIVED THEOREMS (most ancestors)")
print("="*70)
for n, count in anc_sorted[:10]:
    print(f"  {n}: {count} ancestors")

# ═══════════════════════════════════════════════════════════════════
# 6. Build results JSON
# ═══════════════════════════════════════════════════════════════════

# Domain classification for roots
DOMAIN_MAP = {
    "CANTOR_DIAGONALIZATION": "set_theory",
    "BROUWER_FIXED_POINT": "topology",
    "HEISENBERG_UNCERTAINTY": "quantum_mechanics",
    "CARNOT_LIMIT": "thermodynamics",
    "SHANNON_CAPACITY": "information_theory",
    "ARROW_IMPOSSIBILITY": "social_choice",
    "GALOIS_UNSOLVABILITY": "algebra",
    "LIGHT_SPEED_LIMIT": "relativity",
    "WEINBERG_MASSLESS_CONSTRAINT": "particle_physics",
    "IMPOSSIBILITY_BORSUK_ULAM": "topology",
    "IMPOSSIBILITY_CAP": "distributed_systems",
    "IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED": "control_theory",
    "IMPOSSIBILITY_COMPETITIVE_EXCLUSION": "ecology",
    "IMPOSSIBILITY_FISHER_FUNDAMENTAL_THEOREM": "population_genetics",
    "IMPOSSIBILITY_MYERSON_SATTERTHWAITE": "mechanism_design",
    "IMPOSSIBILITY_NK_FITNESS_LANDSCAPE": "evolutionary_biology",
    "IMPOSSIBILITY_PYTHAGOREAN_COMMA": "music_theory",
    "IMPOSSIBILITY_NAIVE_SET_THEORY": "foundations",
    "HUMES_GUILLOTINE": "philosophy",
    "GAUSS_BONNET_CURVATURE_TOPOLOGY": "differential_geometry",
    "KAM_THEOREM": "dynamical_systems",
    "MERMIN_WAGNER": "statistical_mechanics",
}

results = {
    "summary": {
        "total_hubs": len(hub_map),
        "connected_hubs": G_connected.number_of_nodes(),
        "isolated_hubs": len(hub_map) - G_connected.number_of_nodes(),
        "edges": G_connected.number_of_edges(),
        "root_count": len(roots),
        "leaf_count": len(leaves),
        "longest_chain_length": longest_path_length,
        "is_dag": nx.is_directed_acyclic_graph(G_connected),
    },
    "roots": [
        {
            "hub_id": r,
            "domain": DOMAIN_MAP.get(r, "unknown"),
            "direct_children": G_connected.out_degree(r),
            "total_descendants": descendant_counts[r],
            "description": hub_map[r]["description"][:200],
        }
        for r in roots
    ],
    "leaves": [
        {
            "hub_id": l,
            "ancestor_count": ancestor_counts[l],
            "description": hub_map[l]["description"][:200],
        }
        for l in leaves
    ],
    "most_generative": [
        {
            "hub_id": n,
            "direct_children": deg,
            "total_descendants": descendant_counts[n],
        }
        for n, deg in generativity[:20]
    ],
    "longest_chain": {
        "length": longest_path_length,
        "path": longest_path,
    },
    "notable_paths": [
        {"length": len(p)-1, "path": p}
        for p in notable_paths[:20]
        if len(p) >= 3
    ],
    "most_derived": [
        {"hub_id": n, "ancestor_count": count}
        for n, count in anc_sorted[:15]
    ],
    "edge_list": [
        {"parent": u, "child": v}
        for u, v in G_connected.edges()
    ],
}

# ═══════════════════════════════════════════════════════════════════
# 7. Save outputs
# ═══════════════════════════════════════════════════════════════════

# Save GraphML
nx.write_graphml(G_connected, str(OUT_GRAPHML))
print(f"\nSaved graph: {OUT_GRAPHML}")

# Save JSON results
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Saved results: {OUT_JSON}")

print(f"\n{'='*70}")
print("GENEALOGY COMPLETE")
print(f"{'='*70}")
print(f"  {G_connected.number_of_nodes()} theorems connected by {G_connected.number_of_edges()} derivation edges")
print(f"  {len(roots)} root theorems (the 'axioms of impossibility')")
print(f"  {len(leaves)} leaf theorems (the most specialized consequences)")
print(f"  Longest derivation chain: {longest_path_length} steps")
print(f"  Most generative: {generativity[0][0]} ({generativity[0][1]} direct children)")
