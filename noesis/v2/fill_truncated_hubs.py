"""Fill the 8 hubs truncated by Gemini's token limit in batch 12."""
import duckdb, json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb')

# Each hub gets 9 operator entries: (operator, status, resolution_name, description, analog)
# For IMPOSSIBLE/EMPTY_PLAUSIBLE: (operator, status, description)
hubs = {
    "SYBIL_IMPOSSIBILITY": [
        ("DISTRIBUTE", "FILLED", "Proof-of-Work", "Distribute identity cost across computational effort so creating many identities is expensive.", "equal_temperament"),
        ("CONCENTRATE", "FILLED", "Trusted Authority", "Concentrate identity verification in a single trusted certifier.", "wolf_interval"),
        ("TRUNCATE", "FILLED", "Closed Membership", "Remove ability to create new identities — fixed participant set.", "bandlimiting"),
        ("EXPAND", "FILLED", "Social Graph Verification", "Add social network structure so fake identities lack real connections.", "error_correction"),
        ("RANDOMIZE", "FILLED", "Proof-of-Stake Slashing", "Randomize validator selection weighted by stake; cheating risks loss.", "monte_carlo"),
        ("HIERARCHIZE", "FILLED", "Reputation Systems", "Push identity trust to meta-level of accumulated reputation.", "combined_cycle"),
        ("PARTITION", "FILLED", "Sharding with Local Trust", "Partition network into zones with separate identity management.", "gain_scheduling"),
        ("QUANTIZE", "FILLED", "Biometric One-Person-One-Vote", "Force identity onto biological grid — one body, one vote.", "twelve_tet"),
        ("INVERT", "IMPOSSIBLE", None, "Sybil attacks are directional; reversal has no structural meaning.", ""),
    ],
    "SZEMEREDI_REGULARITY_LIMIT": [
        ("DISTRIBUTE", "FILLED", "Regular Partition", "Distribute edges uniformly across partition cells to approximate structure.", "equal_temperament"),
        ("CONCENTRATE", "FILLED", "Sparse Regularity", "Concentrate analysis on dense subgraph where structure lives.", "wolf_interval"),
        ("TRUNCATE", "FILLED", "Tower Function Bounds", "Accept tower-function blow-up in partition count; truncate precision.", "bandlimiting"),
        ("EXPAND", "FILLED", "Hypergraph Regularity", "Expand to higher-order regularity lemmas at cost of worse bounds.", "error_correction"),
        ("RANDOMIZE", "FILLED", "Algorithmic Regularity", "Randomized algorithms find approximately regular partitions efficiently.", "monte_carlo"),
        ("HIERARCHIZE", "FILLED", "Energy Increment Method", "Hierarchical partition refinement guided by energy functional (Tao).", "combined_cycle"),
        ("PARTITION", "FILLED", "Equitable Partition", "Force all classes to equal size, simplifying regularity condition.", "gain_scheduling"),
        ("QUANTIZE", "EMPTY_PLAUSIBLE", None, "Discretizing the regularity parameter epsilon onto a finite grid.", ""),
        ("INVERT", "IMPOSSIBLE", None, "Regularity is a structural decomposition; reversing reconstructs original without new info.", ""),
    ],
    "TARSKI_UNDEFINABILITY": [
        ("DISTRIBUTE", "EMPTY_PLAUSIBLE", None, "Distributing truth predicates across a family of partial truth definitions.", ""),
        ("CONCENTRATE", "FILLED", "Object/Meta Split", "Concentrate truth predicate in meta-language, denying it to object language.", "wolf_interval"),
        ("TRUNCATE", "FILLED", "Kripke Partial Truth", "Truncate domain to sentences where truth is grounded, leaving paradoxical ones undefined.", "bandlimiting"),
        ("EXPAND", "FILLED", "Tarskian Hierarchy", "Infinite hierarchy of languages, each defining truth for the one below.", "meta_system"),
        ("RANDOMIZE", "EMPTY_PLAUSIBLE", None, "Probabilistic truth values for self-referential sentences.", ""),
        ("HIERARCHIZE", "FILLED", "Type Theory", "Stratified type hierarchy preventing self-reference.", "combined_cycle"),
        ("PARTITION", "FILLED", "Revision Theory", "Partition sentences into stable/unstable; iterate truth on unstable.", "gain_scheduling"),
        ("QUANTIZE", "FILLED", "Many-Valued Logic", "Force truth onto discrete grid (3-valued, 4-valued) to handle liar.", "twelve_tet"),
        ("INVERT", "FILLED", "Dialetheism", "Accept some sentences are both true and false — invert exclusivity.", "heat_pumps"),
    ],
    "THIRD_LAW_UNATTAINABILITY": [
        ("DISTRIBUTE", "FILLED", "Distributed Cooling Stages", "Multiple stages each approaching but never reaching 0K.", "equal_temperament"),
        ("CONCENTRATE", "FILLED", "Adiabatic Demagnetization", "Concentrate cooling on magnetic entropy of paramagnetic salts.", "wolf_interval"),
        ("TRUNCATE", "FILLED", "Finite-Step Protocols", "Accept finite steps reach a floor; truncate asymptotic tail.", "bandlimiting"),
        ("EXPAND", "FILLED", "Laser Cooling", "Add photon momentum as new cooling degree of freedom.", "error_correction"),
        ("RANDOMIZE", "FILLED", "Evaporative Cooling", "Probabilistically eject hottest atoms to reduce mean temperature.", "monte_carlo"),
        ("HIERARCHIZE", "FILLED", "Cascaded Refrigeration", "Chain cooling cycles, each using output of previous as heat sink.", "combined_cycle"),
        ("PARTITION", "FILLED", "Differential Cooling Zones", "Partition system into zones at different temperatures.", "gain_scheduling"),
        ("QUANTIZE", "FILLED", "Discrete Energy Levels", "Quantum systems have discrete ground states; temperature quantizes near 0K.", "twelve_tet"),
        ("INVERT", "FILLED", "Heat Pump Operation", "Reverse cooling direction to pump heat out; Carnot dual.", "heat_pumps"),
    ],
    "VITALI_NONMEASURABLE": [
        ("DISTRIBUTE", "IMPOSSIBLE", None, "Non-measurable sets have no measure to distribute.", ""),
        ("CONCENTRATE", "IMPOSSIBLE", None, "Cannot localize what has no measure.", ""),
        ("TRUNCATE", "FILLED", "Restrict to Lebesgue Measurable", "Truncate domain to sigma-algebra where measure works.", "bandlimiting"),
        ("EXPAND", "FILLED", "Hausdorff Measure", "Expand to fractional-dimensional measures for exotic sets.", "error_correction"),
        ("RANDOMIZE", "FILLED", "Random Set Sampling", "Assign probabilistic measure via random point processes avoiding AC.", "monte_carlo"),
        ("HIERARCHIZE", "FILLED", "Solovay Model", "Model of set theory (without full AC) where all sets measurable.", "meta_system"),
        ("PARTITION", "FILLED", "Caratheodory Criterion", "Partition using splitting condition to identify measurable subsets.", "gain_scheduling"),
        ("QUANTIZE", "FILLED", "Discrete Measure", "Force onto counting measure where non-measurability vanishes.", "twelve_tet"),
        ("INVERT", "IMPOSSIBLE", None, "Non-measurability is a set property, not directional.", ""),
    ],
    "WEDDERBURN_LITTLE": [
        ("DISTRIBUTE", "EMPTY_PLAUSIBLE", None, "Distributing commutativity across a family of near-fields.", ""),
        ("CONCENTRATE", "FILLED", "Center of Division Ring", "Concentrate commutative structure in center subfield.", "wolf_interval"),
        ("TRUNCATE", "FILLED", "Finite Field Restriction", "In finite case, Wedderburn proves all division rings are commutative.", "bandlimiting"),
        ("EXPAND", "FILLED", "Quaternion Extension", "Accept non-commutativity by expanding to quaternions/octonions.", "error_correction"),
        ("RANDOMIZE", "EMPTY_PLAUSIBLE", None, "Random non-commutative algebra sampling for near-commutative structures.", ""),
        ("HIERARCHIZE", "FILLED", "Brauer Group", "Classify division algebras via cohomological invariants.", "combined_cycle"),
        ("PARTITION", "FILLED", "Wedderburn-Artin Decomposition", "Decompose semisimple rings into matrix rings over division algebras.", "gain_scheduling"),
        ("QUANTIZE", "IMPOSSIBLE", None, "Division algebras are algebraic, not continuous-to-discrete.", ""),
        ("INVERT", "FILLED", "Opposite Ring", "Construct R^op with reversed multiplication; tests commutativity.", "heat_pumps"),
    ],
    "WEINBERG_MASSLESS_CONSTRAINT": [
        ("DISTRIBUTE", "FILLED", "Soft Graviton Theorems", "Distribute masslessness constraint across soft radiation carrying zero energy.", "equal_temperament"),
        ("CONCENTRATE", "FILLED", "Spin-Statistics Concentration", "Only spin-1 and spin-2 are consistent massless; concentrate constraint there.", "wolf_interval"),
        ("TRUNCATE", "FILLED", "Massive Approximation", "Give particles small mass (Proca, massive gravity) accepting inconsistencies.", "bandlimiting"),
        ("EXPAND", "FILLED", "String Theory Extension", "Infinite tower of massive states makes massless limits consistent.", "error_correction"),
        ("RANDOMIZE", "EMPTY_PLAUSIBLE", None, "Stochastic mass generation through vacuum fluctuations.", ""),
        ("HIERARCHIZE", "FILLED", "Higgs Mechanism", "Push mass generation to meta-level via spontaneous symmetry breaking.", "combined_cycle"),
        ("PARTITION", "FILLED", "Helicity Partition", "Partition massless particles by helicity; each is independent representation.", "gain_scheduling"),
        ("QUANTIZE", "IMPOSSIBLE", None, "Mass is continuous in QFT; forcing discrete has no known consistent formulation.", ""),
        ("INVERT", "FILLED", "Dual Graviton", "Dual formulation where constraint appears in dual tensor sector.", "heat_pumps"),
    ],
    "WHEELER_FEYNMAN_ABSORBER": [
        ("DISTRIBUTE", "FILLED", "Cosmological Absorption", "Distribute absorber condition across all future matter in expanding universe.", "equal_temperament"),
        ("CONCENTRATE", "FILLED", "Perfect Absorber Boundary", "Concentrate absorption at cosmological boundary.", "wolf_interval"),
        ("TRUNCATE", "FILLED", "Retarded-Only Convention", "Discard advanced solutions entirely (standard QED).", "bandlimiting"),
        ("EXPAND", "FILLED", "Transactional Interpretation", "Include both offer (retarded) and confirmation (advanced) waves (Cramer 1986).", "error_correction"),
        ("RANDOMIZE", "FILLED", "Stochastic Electrodynamics", "Replace absorber with background random zero-point field.", "monte_carlo"),
        ("HIERARCHIZE", "FILLED", "QED Renormalization", "Push radiation reaction to meta-level via field quantization.", "combined_cycle"),
        ("PARTITION", "FILLED", "Near/Far Field Split", "Partition EM field into near-field (bound) and far-field (radiated).", "gain_scheduling"),
        ("QUANTIZE", "FILLED", "Photon Quantization", "Discrete photon exchange eliminates the absorber issue.", "twelve_tet"),
        ("INVERT", "FILLED", "Advanced-Wave Formulation", "Use advanced Green functions as primary propagator.", "heat_pumps"),
    ],
}

filled = impossible = plausible = 0
for hub_id, grid in hubs.items():
    for entry in grid:
        operator = entry[0]
        status = entry[1]
        res_name = entry[2]
        desc = entry[3]
        analog = entry[4] if len(entry) > 4 else ""

        if status == "FILLED":
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(res_name)[:30])
            instance_id = f"{hub_id}__B12F_{operator}_{safe_name}"
            notes = f"{res_name}: {desc} | DAMAGE_OP: {operator} | ANALOG: {analog} | SOURCE: aletheia_truncation_fill"
            try:
                db.execute("""INSERT INTO composition_instances
                    (instance_id, comp_id, system_id, tradition, domain, notes)
                    VALUES (?, ?, NULL, ?, ?, ?)""",
                    [instance_id, hub_id, "Aletheia Fill", "cross-domain", notes[:1000]])
                filled += 1
            except:
                pass
        elif status == "IMPOSSIBLE":
            impossible += 1
        elif status == "EMPTY_PLAUSIBLE":
            plausible += 1

db.commit()
total = db.execute("SELECT COUNT(*) FROM composition_instances").fetchone()[0]
print(f"8 truncated hubs filled")
print(f"FILLED: {filled}, IMPOSSIBLE: {impossible}, PLAUSIBLE: {plausible}")
print(f"Total spokes: {total}")
db.close()
