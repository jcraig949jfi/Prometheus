"""Deep fill of remaining 69 non-INVERT empty cells."""
import duckdb, sys
sys.stdout.reconfigure(encoding='utf-8')
db = duckdb.connect('noesis/v2/noesis_v2.duckdb')

fills = [
    ("ABBE_DIFFRACTION_LIMIT", "HIERARCHIZE", "Super-resolution microscopy", "STED/PALM/STORM push resolution to meta-level via fluorescence switching above diffraction limit."),
    ("ALGEBRIZATION_BARRIER", "TRUNCATE", "Geometric Complexity Theory", "Restrict to orbit closures where algebrization does not apply."),
    ("BANACH_TARSKI", "HIERARCHIZE", "Amenability Hierarchy", "Push to meta-level: paradox fails for amenable groups. Classify groups by amenability."),
    ("BEKENSTEIN_BOUND", "PARTITION", "Holographic Screens", "Partition spacetime using holographic screens; each has its own Bekenstein bound."),
    ("BEKENSTEIN_BOUND", "TRUNCATE", "Sub-Planck Truncation", "Truncate below Planck scale where bound becomes trivial."),
    ("BGS_ORACLE_SEPARATION", "PARTITION", "Barrier Decomposition", "Partition proof techniques into relativizing and non-relativizing."),
    ("BROCAS_BINDING", "RANDOMIZE", "Neural Noise Binding", "Stochastic resonance in neural oscillations aids feature binding."),
    ("CARNOT_LIMIT", "TRUNCATE", "Finite-Time Thermodynamics", "Truncate to finite-time: Curzon-Ahlborn efficiency is practical bound."),
    ("CHRONOLOGY_PROTECTION", "HIERARCHIZE", "Quantum Gravity Meta-Level", "Push to quantum gravity where chronology protection emerges from deeper principles."),
    ("EULER_CHARACTERISTIC_OBSTRUCTION", "RANDOMIZE", "Random Vector Fields", "Random fields have expected singularity structure matching Euler characteristic."),
    ("GIBBARD_SATTERTHWAITE", "CONCENTRATE", "Single-Issue Concentration", "Concentrate on single-issue votes where strategy-proofness achievable."),
    ("GIBBARD_SATTERTHWAITE", "HIERARCHIZE", "Tiered Voting", "Hierarchical: primaries then general election pushes manipulation to meta-level."),
    ("GOODSTEIN_INDEPENDENCE", "RANDOMIZE", "Probabilistic Independence", "Random models satisfy Goodstein with high probability."),
    ("HAIRY_BALL_THEOREM", "HIERARCHIZE", "Frame Bundle", "Push to frame bundle where obstruction lives in characteristic classes."),
    ("HUMES_GUILLOTINE", "RANDOMIZE", "Evolutionary Ethics", "Evolved moral intuitions provide stochastic ought-from-is via fitness landscapes."),
    ("IMPOSSIBILITY_BELLS_THEOREM", "HIERARCHIZE", "Decoherence Theory", "Push to meta-level where measurement problem dissolves."),
    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "TRUNCATE", "Finite Bandwidth Truncation", "Truncate to finite bandwidth where integral is bounded."),
    ("IMPOSSIBILITY_BORSUK_ULAM", "RANDOMIZE", "Probabilistic Antipodal Avoidance", "Guarantee collision probability below epsilon via randomized maps."),
    ("IMPOSSIBILITY_CALENDAR", "CONCENTRATE", "Fixed Calendar Epoch", "Concentrate all damage at epoch reset (Julian Day Number)."),
    ("IMPOSSIBILITY_CRAMER_RAO_BOUND", "PARTITION", "Stratified Estimation", "Partition parameter space; achieve bound per stratum."),
    ("IMPOSSIBILITY_EASTIN_KNILL_THEOREM", "CONCENTRATE", "Magic State Distillation", "Concentrate non-transversality in magic state preparation."),
    ("IMPOSSIBILITY_HOLEVO_BOUND", "HIERARCHIZE", "Superdense Coding Hierarchy", "Push beyond Holevo using entanglement as meta-resource."),
    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "CONCENTRATE", "Optimal Single-Copy Cloning", "Concentrate fidelity on one optimal copy (Buzek-Hillery cloner)."),
    ("LANDAUER_LIMIT", "TRUNCATE", "Reversible Computing", "Fully reversible computation avoids Landauer cost entirely."),
    ("NYQUIST_LIMIT", "HIERARCHIZE", "Multi-Rate Sampling", "Hierarchical sampling at multiple rates; combine via filter bank."),
    ("NYQUIST_LIMIT", "PARTITION", "Subband Decomposition", "Partition frequency into subbands; sample each at own Nyquist rate."),
    ("REVENUE_EQUIVALENCE", "CONCENTRATE", "All-Pay Auction", "Concentrate revenue extraction on entry fee; everyone pays."),
    ("RUNGE_PHENOMENON", "HIERARCHIZE", "Adaptive Mesh Refinement", "Hierarchical: refine only where oscillations emerge."),
    ("RUNGE_PHENOMENON", "PARTITION", "Piecewise Polynomial (Splines)", "Partition domain; low-degree polynomial per interval."),
    ("RUNGE_PHENOMENON", "RANDOMIZE", "Random Node Placement", "Random nodes avoid systematic equispaced pathology."),
    ("SEN_LIBERAL_PARADOX", "TRUNCATE", "Rights Restriction", "Truncate scope of rights to non-Pareto-conflicting domains."),
    ("SOCIAL_CHOICE_IMPOSSIBILITY", "CONCENTRATE", "Dictator with Checks", "Concentrate decision power with veto/override mechanisms."),
    ("VITALI_NONMEASURABLE", "CONCENTRATE", "Point Mass (Dirac Delta)", "Concentrate measure at single point where non-measurability irrelevant."),
    ("IMPOSSIBILITY_MODULARITY_EVOLVABILITY_TRADEOFF", "TRUNCATE", "Frozen Module", "Freeze some modules entirely to allow others to evolve."),
    ("IMPOSSIBILITY_TSIRELSON_BOUND", "TRUNCATE", "Finite-Dimensional Truncation", "Restrict to finite-dimensional Hilbert spaces."),
    ("IMPOSSIBILITY_TSIRELSON_BOUND", "PARTITION", "Bell Scenario Partition", "Partition measurement settings; analyze bound per partition."),
    ("IMPOSSIBILITY_FIVE_COLOR", "EXTEND", "Surface Genus Extension", "Extend to higher-genus surfaces (Heawood bound)."),
    ("IMPOSSIBILITY_NO_BROADCASTING_THEOREM", "EXTEND", "Classical Side Channel", "Add classical communication channel alongside quantum."),
    ("IMPOSSIBILITY_NO_COMMUNICATION_THEOREM", "EXTEND", "Classical Superchannel", "Extend with classical signaling; hybrid protocol."),
    ("IMPOSSIBILITY_NO_DELETING_THEOREM", "EXTEND", "Ancilla Absorption", "Ancilla absorbs deleted information (unitary dilation)."),
    ("IMPOSSIBILITY_NO_HIDING_THEOREM", "EXTEND", "Environment Purification", "Information is in the joint system, not hidden."),
    ("KAKUTANI_FIXED_POINT", "EXTEND", "Continuous Selection", "Michael selection theorem: extend set-valued map to single-valued."),
    ("NO_RETRACTION_THEOREM", "EXTEND", "ANR Extension", "Extend to absolute neighborhood retract."),
    ("NO_RETRACTION_THEOREM", "RANDOMIZE", "Random Retraction", "Probabilistic retraction proportional to boundary distance."),
    ("WEIERSTRASS_NOWHERE_DIFFERENTIABLE", "EXTEND", "Distributional Derivative", "Extend derivative concept to Schwartz distributions."),
    ("IMPOSSIBILITY_WELLORDER_WITHOUT_CHOICE", "EXTEND", "Axiom of Determinacy", "Extend axioms with AD instead of AC."),
    ("BURNSIDE_IMPOSSIBILITY", "PARTITION", "Orbit Partition", "Partition by orbit type; Burnside lemma counts per conjugacy class."),
    ("IMPOSSIBILITY_SQUARING_CIRCLE", "PARTITION", "Approximate Quadrature", "Partition circle into polygonal regions; sum areas."),
    ("PARIS_HARRINGTON", "RANDOMIZE", "Probabilistic Ramsey", "Random colorings satisfy PH with high probability for large instances."),
    ("MUNTZ_SZASZ", "RANDOMIZE", "Random Lacunary Approximation", "Random exponent sampling gives probabilistic density."),
]

added = 0
for hub, op, name, desc in fills:
    iid = f"{hub}__DEEP_{op}"
    notes = f"{name}: {desc} | DAMAGE_OP: {op} | SOURCE: aletheia_deep_fill"
    try:
        db.execute("""INSERT INTO composition_instances
            (instance_id, comp_id, system_id, tradition, domain, notes)
            VALUES (?, ?, NULL, ?, ?, ?)""",
            [iid, hub, "Deep Fill", "cross-domain", notes[:1000]])
        added += 1
    except:
        pass

db.commit()

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
print(f"Added: {added}")
print(f"Empty: {empty}/{total_cells} ({100*(1-empty/total_cells):.1f}% fill)")
print(f"Total spokes: {total_spokes}")
db.close()
