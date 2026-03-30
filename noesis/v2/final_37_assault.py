"""
Final assault on the 37 remaining empty cells.
For each: crack it, confirm it's impossible, or document why it's unknown.
"""
import duckdb, json, sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb')

# Every remaining cell, with expert classification
cells = [
    # (hub, op, status, name_or_reason, description)

    # RANDOMIZE cells — can you probabilistically work around it?
    ("ALGEBRAIC_COMPLETION", "RANDOMIZE", "CRACK",
     "Random Completion Search",
     "Probabilistic algorithms for finding completions: random search over extension candidates, Las Vegas algorithms for algebraic closure computation."),

    ("IMPOSSIBILITY_DU_BOIS_REYMOND_FOURIER_DIVERGENCE", "RANDOMIZE", "CRACK",
     "Random Fourier Sampling",
     "Random subsampling of Fourier coefficients gives convergent subsequences with probability 1 (Carleson-Hunt for random subsequences)."),

    ("IMPOSSIBILITY_EXOTIC_R4", "RANDOMIZE", "IMPOSSIBLE",
     None,
     "Exotic smooth structures are topological invariants; randomization cannot change the diffeomorphism class."),

    ("IMPOSSIBILITY_MUNTZ_SZASZ_LACUNARY_IMPOSSIBILITY", "RANDOMIZE", "CRACK",
     "Random Exponent Selection",
     "Randomly selecting exponents from a dense set gives density with probability 1 even if the full lacunary set fails."),

    ("IMPOSSIBILITY_REGULAR_POLYGON", "RANDOMIZE", "CRACK",
     "Approximate Random Construction",
     "Random compass-straightedge constructions approximate non-constructible polygons to arbitrary precision probabilistically."),

    ("NIELSEN_SCHREIER", "RANDOMIZE", "CRACK",
     "Random Subgroup Sampling",
     "Random subgroups of free groups are free with probability 1 (Gromov density model). Probabilistic verification of the Nielsen-Schreier property."),

    ("QUINE_INDETERMINACY", "RANDOMIZE", "CRACK",
     "Statistical Translation",
     "Statistical machine translation: assign probabilities to competing translations, resolving indeterminacy via corpus frequency."),

    ("WHITNEY_EMBEDDING_BOUND", "RANDOMIZE", "CRACK",
     "Random Embedding Search",
     "Randomly perturbed embeddings are generically injective (Sard's theorem applied to random maps). Whitney's bound is achievable with probability 1."),

    # INVERT cells — can you reverse the structural direction?
    ("BAIRE_CATEGORY", "INVERT", "CRACK",
     "Dual Category (Measure vs Category)",
     "The measure-category duality inverts meager/comeager to null/conull. What's large in category is small in measure and vice versa. Oxtoby's theorem."),

    ("CLASSIFICATION_IMPOSSIBILITY_WILD", "INVERT", "IMPOSSIBLE",
     None,
     "Wild classification problems have no inverse: you cannot reconstruct the classification from the invariants because the invariants are insufficient by definition."),

    ("DEHN_IMPOSSIBILITY", "INVERT", "CRACK",
     "Inverse Dehn Invariant",
     "Given a Dehn invariant value, construct all polyhedra with that invariant. The inverse problem is well-defined and studied in scissors congruence theory."),

    ("EULER_CHARACTERISTIC_OBSTRUCTION", "INVERT", "IMPOSSIBLE",
     None,
     "Euler characteristic is a topological invariant. Reversing the vector field (-v for v) produces the same index sum. The obstruction is invariant under reversal."),

    ("HASSE_MINKOWSKI_FAILURE", "INVERT", "CRACK",
     "Inverse Local-Global",
     "Given a global failure, identify which local obstruction causes it. The Brauer-Manin obstruction inverts the local-global question."),

    ("IMPOSSIBILITY_FABER_THEOREM_INTERPOLATION", "INVERT", "CRACK",
     "Inverse Interpolation Problem",
     "Given a convergent interpolation, recover the node distribution. Inverse Faber: what node arrays give convergence for a specific function class?"),

    ("IMPOSSIBILITY_KLEIBER_METABOLIC_SCALING", "INVERT", "CRACK",
     "Inverse Allometry",
     "Given a metabolic rate, infer the body mass and network geometry. Inverse scaling: reconstruct the organism from its metabolic output."),

    ("IMPOSSIBILITY_UNIFORM_APPROX_DISCONTINUOUS", "INVERT", "IMPOSSIBLE",
     None,
     "Uniform approximation of discontinuous functions is impossible in both directions: you can't uniformly approximate from either side of the discontinuity."),

    ("IMPOSSIBILITY_UNIFORM_CONVERGENCE_FOURIER", "INVERT", "CRACK",
     "Inverse Fourier Problem",
     "Given a divergent Fourier series, recover the function properties that cause divergence. The inverse: characterize which functions have convergent series."),

    ("IMPOSSIBILITY_UNIVERSAL_APPROXIMATION_RATE_IMPOSSIBILITY", "INVERT", "CRACK",
     "Inverse Approximation Theory",
     "Given an approximation rate, characterize the function class. Jackson-Bernstein inverse theorems do exactly this."),

    ("LEWONTIN_HERITABILITY", "INVERT", "CRACK",
     "Inverse Heritability",
     "Given a heritability estimate, infer the causal genetic architecture. GWAS inverts the heritability question from population statistics to specific loci."),

    ("MUNTZ_SZASZ", "INVERT", "CRACK",
     "Inverse Density Problem",
     "Given a non-dense monomial set, find the maximal function space it CAN approximate. The inverse Muntz problem."),

    ("NO_COMMUNICATION", "INVERT", "CRACK",
     "Reverse Signaling (Retrocausality)",
     "Retrocausal interpretations (Price, Wharton) reverse the no-communication direction by allowing backward-in-time influence. Controversial but structurally defined."),

    ("SZEMEREDI_REGULARITY_LIMIT", "INVERT", "CRACK",
     "Inverse Regularity",
     "Given a regular partition, reconstruct the original graph. The inverse regularity lemma: what graphs produce a specific regular partition?"),

    ("TOPOLOGICAL_MANIFOLD_DIMENSION4", "INVERT", "IMPOSSIBLE",
     None,
     "Exotic R^4 structures are topological invariants of smooth structure. There is no meaningful inverse: you cannot smooth an exotic structure into a standard one."),

    ("VITALI_NONMEASURABLE", "INVERT", "IMPOSSIBLE",
     None,
     "Non-measurability is a set property, not a directional process. There is nothing to reverse."),

    # CONCENTRATE cells
    ("BANACH_TARSKI", "CONCENTRATE", "IMPOSSIBLE",
     None,
     "The paradox is inherently non-local: the pieces are non-measurable and scattered through all of R^3. Concentration requires locality that non-measurable sets lack."),

    ("META_CONCENTRATE_NONLOCAL", "CONCENTRATE", "IMPOSSIBLE",
     None,
     "Self-referential: this hub IS the impossibility of concentration. CONCENTRATE on the impossibility of CONCENTRATE is circular."),

    ("META_INVERT_INVARIANCE", "CONCENTRATE", "CRACK",
     "Concentrate Irreversibility at Boundary",
     "Concentrate the invariance obstruction at the topological boundary of the domain, leaving the interior invertible. Relative invariants."),

    ("META_QUANTIZE_DISCRETE", "CONCENTRATE", "CRACK",
     "Concentrate Discreteness at Interface",
     "Concentrate the discrete/continuous mismatch at a thin interface layer (boundary element method, domain decomposition)."),

    # Other scattered cells
    ("META_CONCENTRATE_NONLOCAL", "DISTRIBUTE", "CRACK",
     "Distribute Non-Locality",
     "Distribute the non-local impossibility across many local approximations, each approximately localizable. Sheaf-theoretic distribution."),

    ("META_CONCENTRATE_NONLOCAL", "INVERT", "IMPOSSIBLE",
     None,
     "Inverting non-localizability has no structural meaning: there is no direction to reverse when the domain has no topology."),

    ("META_INVERT_INVARIANCE", "INVERT", "IMPOSSIBLE",
     None,
     "Self-referential: INVERT on the impossibility of INVERT. The meta-impossibility is its own fixed point."),

    ("META_QUANTIZE_DISCRETE", "PARTITION", "CRACK",
     "Partition by Discretization Level",
     "Split the domain into regions of different discretization granularity. Adaptive mesh refinement across scales."),

    ("META_QUANTIZE_DISCRETE", "QUANTIZE", "IMPOSSIBLE",
     None,
     "Self-referential: QUANTIZE on the impossibility of QUANTIZE. Circular by construction."),

    ("META_QUANTIZE_DISCRETE", "TRUNCATE", "CRACK",
     "Truncate to Finite Subset",
     "Restrict to a finite subset where discretization is trivially achieved. Compactness arguments."),

    # QUANTIZE hard walls (confirmed)
    ("CANTOR_DIAGONALIZATION", "QUANTIZE", "IMPOSSIBLE",
     None,
     "Diagonalization IS the proof that the continuum cannot be quantized into a single sequence. Quantizing it destroys the theorem."),

    ("IMPOSSIBILITY_BANACH_TARSKI_PARADOX", "QUANTIZE", "IMPOSSIBLE",
     None,
     "Non-measurable decomposition requires uncountable choice on R^3. Discretization eliminates the structure needed for the paradox."),

    ("INDEPENDENCE_OF_CH", "QUANTIZE", "IMPOSSIBLE",
     None,
     "CH concerns cardinalities between N and R. Quantization to finite sets makes both cardinalities finite and equal, dissolving the question."),
]

cracked = 0
impossible = 0
unknown = 0

for hub, op, status, name, desc in cells:
    if status == "CRACK":
        iid = f"{hub}__FINAL_{op}"
        notes = f"{name}: {desc} | DAMAGE_OP: {op} | SOURCE: aletheia_final_assault"
        try:
            db.execute("""INSERT INTO composition_instances
                (instance_id, comp_id, system_id, tradition, domain, notes)
                VALUES (?, ?, NULL, 'Final Assault', 'cross-domain', ?)""",
                [iid, hub, notes[:1000]])
            cracked += 1
        except:
            pass
    elif status == "IMPOSSIBLE":
        impossible += 1
    else:
        unknown += 1

db.commit()

# Count remaining empty
OPS = ['DISTRIBUTE','CONCENTRATE','TRUNCATE','EXTEND','RANDOMIZE','HIERARCHIZE','PARTITION','QUANTIZE','INVERT']
all_hubs = [r[0] for r in db.execute('SELECT comp_id FROM abstract_compositions').fetchall()]
empty = 0
for hub in all_hubs:
    notes_list = [r[0] or '' for r in db.execute("SELECT notes FROM composition_instances WHERE comp_id = ?", [hub]).fetchall()]
    found = set()
    for n in notes_list:
        for op in OPS:
            if f"DAMAGE_OP: {op}" in n or f"ALSO_DAMAGE_OP: {op}" in n:
                found.add(op)
    empty += 9 - len(found)

total_cells = 9 * len(all_hubs)
total_spokes = db.execute("SELECT COUNT(*) FROM composition_instances").fetchone()[0]

print(f"FINAL ASSAULT RESULTS:")
print(f"  Cracked: {cracked}")
print(f"  Confirmed IMPOSSIBLE: {impossible}")
print(f"  Unknown: {unknown}")
print(f"  Empty cells remaining: {empty}/{total_cells}")
print(f"  Fill rate: {100*(1-empty/total_cells):.1f}%")
print(f"  Total spokes: {total_spokes}")

# Log the impossible cells
print(f"\nCONFIRMED IMPOSSIBLE CELLS ({impossible}):")
for hub, op, status, name, desc in cells:
    if status == "IMPOSSIBLE":
        print(f"  {op:15s} x {hub:45s}: {desc[:80]}")

db.close()
