"""Ingest 5 final Gemini hubs: Crystallographic, Bode, Bell's Theorem, Borsuk-Ulam, Goodhart's Law."""
import duckdb, json, sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb')

hubs = [
    {"hub_id": "IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2",
     "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
     "desc": "Discrete periodic lattice cannot have 5,7,8+ fold rotational symmetry. Rotating by 2pi/5 forces lattice points closer than minimum distance.",
     "pattern": "Resolutions: aperiodic quasicrystals (EXPAND via higher-dim projection), approximant crystals (TRUNCATE), amorphous boundaries (CONCENTRATE), hyperbolic tiling (HIERARCHIZE), stochastic Voronoi (RANDOMIZE). Islamic girih predates Penrose by centuries.",
     "resolutions": [
         ("APERIODIC_QUASICRYSTALS", "Islamic/Modern", "geometry/physics", "EXPAND", "Projects periodic 5D lattice to 3D. Sacrifices translation periodicity. Shechtman 1984, Nobel 2011. | CROSS: robinson_projection, meta_system, bring_radicals"),
         ("APPROXIMANT_CRYSTALS", "Materials Science", "physics", "TRUNCATE", "Fibonacci-ratio distortion forces repeating box. Sacrifices exact 5-fold. Internal strain. | CROSS: oversampling, gall_peters, newton_raphson"),
         ("AMORPHOUS_BOUNDARIES", "Solid State Physics", "physics", "CONCENTRATE", "Perfect icosahedral islands in glass-like chaos. Damage at grain boundaries. | CROSS: mercator, capital_controls"),
         ("HYPERBOLIC_TILING", "Non-Euclidean Geometry", "geometry", "HIERARCHIZE", "Negative curvature allows pentagon tiling. Sacrifices flat Euclidean space. Escher Circle Limit. | CROSS: khayyam, meta_system, elliptic_modular"),
         ("STOCHASTIC_VORONOI", "Statistical Mechanics", "physics", "RANDOMIZE", "Soap froth with statistically predominant pentagons. Sacrifices deterministic symmetry. | CROSS: probabilistic, probabilistic_trading"),
     ]},
    {"hub_id": "IMPOSSIBILITY_BODE_INTEGRAL_V2",
     "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
     "desc": "Integral of log sensitivity over all frequencies = constant. Cannot suppress disturbances at all frequencies. Cauchy integral theorem enforces conservation.",
     "pattern": "THE validation case for damage algebra. Damage conservation is a THEOREM here, not a metaphor. 5 of 7 damage operators instantiated in one engineering domain.",
     "resolutions": [
         ("BAND_LIMITED_PID", "Classical Engineering", "control", "CONCENTRATE", "Suppress low-freq, accept high-freq spike. Waterbed bulge. | CROSS: anti_aliasing, mercator, domain_prior_knowledge"),
         ("H_INFINITY_OPTIMAL", "Robust Control", "control", "DISTRIBUTE", "Minimize max peak by raising floor everywhere. Persistent sluggishness. | CROSS: equal_temperament, gall_peters, cesaro_fejer, ensemble_averaging"),
         ("FEEDFORWARD_2DOF", "Advanced Control", "control", "EXPAND", "Open-loop parallel path outside integral theorem boundary. Predict future. | CROSS: axiom_extension, power_increase, external_subsidy"),
         ("GAIN_SCHEDULING", "Aerospace", "control", "PARTITION", "Swap controllers by operating regime. Cheats linearity assumption. Switching instability. | CROSS: sortition, local_projection, chebyshev_nodes"),
         ("PLANT_REDESIGN", "Mechatronics", "control", "TRUNCATE", "Physically rebuild the machine. Export damage from math to supply chain. | CROSS: restrict_language, cp_system, model_regularization"),
     ]},
    {"hub_id": "IMPOSSIBILITY_BELLS_THEOREM",
     "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
     "desc": "No local hidden variable theory reproduces all quantum predictions. Bell inequality violated experimentally. Universe cannot be both local and classically real.",
     "pattern": "Each interpretation of QM is a damage allocation: which of locality, realism, or single reality do you sacrifice?",
     "resolutions": [
         ("COPENHAGEN_NONLOCALITY", "Orthodox Physics", "quantum", "TRUNCATE", "Accept spooky action at distance. Sacrifice locality. | CROSS: ap_system, accept_gaps, floating_exchange_rate"),
         ("MANY_WORLDS", "Everett", "quantum", "EXPAND", "Universe branches. Sacrifice single reality. Infinite ontological bloat. | CROSS: meta_system, external_subsidy, bring_radicals"),
         ("SUPERDETERMINISM", "Fringe Physics", "quantum", "CONCENTRATE", "Everything predetermined from Big Bang. Sacrifice free choice. Rigged movie. | CROSS: vickrey_auction, capital_controls"),
         ("QBISM", "Quantum Information", "quantum", "PARTITION", "Quantum states are subjective belief. Sacrifice objective realism. Epistemic solipsism. | CROSS: gall_peters, local_projection, galois_classification"),
         ("GRW_COLLAPSE", "Theoretical Physics", "quantum", "RANDOMIZE", "Spontaneous random localization. Sacrifice exact QM predictions. Built-in noise. | CROSS: probabilistic_halting, stochastic_roots"),
     ]},
    {"hub_id": "IMPOSSIBILITY_BORSUK_ULAM",
     "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
     "desc": "Any continuous map from S^n to R^n must map some antipodal pair to same value. Sphere wraps back on itself, forcing collision.",
     "pattern": "Governs weather stagnation points, magnetic poles, hairy ball theorem. Every resolution trades a different topological property.",
     "resolutions": [
         ("DISCONTINUOUS_TEARING", "Applied Topology", "topology", "TRUNCATE", "Allow jump discontinuity. Tear the manifold. | CROSS: gall_peters, accept_overshoot, accept_deadweight_loss"),
         ("STEREOGRAPHIC_PUNCTURE", "Cartography/Complex Analysis", "topology", "EXPAND", "Delete one point to unwrap sphere to plane. Infinite distortion near puncture. | CROSS: mercator, axiom_extension, external_subsidy"),
         ("PROJECTIVE_QUOTIENT", "Algebraic Topology", "topology", "HIERARCHIZE", "Decree antipodal points identical. Non-orientable space. No left/right. | CROSS: meta_system, robinson_projection, currency_union"),
         ("EQUATORIAL_CONCENTRATION", "Differential Topology", "topology", "CONCENTRATE", "Force zeros to poles. Hurricane eye singularity. Hairy ball variant. | CROSS: borda, mercator, vickrey_auction"),
         ("FUZZY_FUZZIFICATION", "Fuzzy Mathematics", "topology", "DISTRIBUTE", "Map regions to intervals. Hide collision in error margins. Omnipresent blur. | CROSS: eventual_consistency, equal_temperament, cesaro_fejer"),
     ]},
    {"hub_id": "IMPOSSIBILITY_GOODHARTS_LAW",
     "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
     "desc": "A metric cannot simultaneously be accurate measurement AND optimization target. Agents exploit proxy, destroying correlation with true goal.",
     "pattern": "Universal limiting theorem of bureaucracies, algorithms, and AI alignment. Every evaluation system is a damage allocation for where gaming concentrates.",
     "resolutions": [
         ("METRIC_ROTATION", "Algorithmic Management", "cybernetics", "RANDOMIZE", "Constantly change metrics. Outrun exploitation. Chaotic churn. | CROSS: probabilistic_halting, time_outs, sgd_noise"),
         ("BALANCED_SCORECARD", "Corporate Management", "cybernetics", "DISTRIBUTE", "Dozens of opposing metrics. Bureaucratic paralysis. | CROSS: ensemble, approval, ensemble_averaging"),
         ("HIDDEN_METRICS", "Education/Testing", "cybernetics", "PARTITION", "Hide the rubric. Systemic alienation and mistrust. | CROSS: sortition, restrict_language, chebyshev_nodes"),
         ("SKIN_IN_THE_GAME", "Risk Management", "cybernetics", "HIERARCHIZE", "Abolish proxy. Tie survival to outcomes. Architect lives under bridge. | CROSS: meta_system, market_maker"),
         ("ACCEPT_METRIC_DECAY", "Common Law", "cybernetics", "TRUNCATE", "Human override when gaming detected. Unscalable bottleneck. | CROSS: accept_gaps, time_outs, accept_deadweight_loss"),
     ]},
]

hub_count = 0
res_count = 0
link_count = 0

for hub in hubs:
    hid = hub["hub_id"]
    db.execute("""
        INSERT OR REPLACE INTO abstract_compositions
        (comp_id, primitive_sequence, description, structural_pattern, chain_count)
        VALUES (?, ?, ?, ?, ?)
    """, [hid, hub["primitives"], hub["desc"], hub["pattern"], len(hub["resolutions"])])
    hub_count += 1

    for res_id, tradition, domain, damage_op, notes in hub["resolutions"]:
        instance_id = f"{hid}__{res_id}"
        cross_links = []
        if "CROSS:" in notes:
            cross_part = notes.split("CROSS:")[1].strip()
            cross_links = [x.strip() for x in cross_part.split(",")]
            notes_clean = notes.split("|")[0].strip()
        else:
            notes_clean = notes

        db.execute("""
            INSERT OR REPLACE INTO composition_instances
            (instance_id, comp_id, system_id, tradition, domain, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [instance_id, hid, None, tradition, domain, f"{notes_clean} | DAMAGE_OP: {damage_op}"])
        res_count += 1

        for target in cross_links:
            lid = f"{instance_id}__TO__{target.upper().replace(' ','_')}"
            db.execute("""
                INSERT OR REPLACE INTO cross_domain_links
                (link_id, source_resolution, source_hub, target_hub, link_type, damage_operator)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [lid, instance_id, hid, target.upper().replace(' ','_'), 'existing_hub', damage_op])
            link_count += 1

db.commit()

print(f"[FINAL HUBS] {hub_count} ingested")
print(f"[RESOLUTIONS] {res_count} instances")
print(f"[CROSS-DOMAIN LINKS] {link_count} new typed edges")
print()

print("FULL DATABASE INVENTORY:")
for table in ["operations", "chains", "chain_steps", "transformations",
              "ethnomathematics", "abstract_compositions", "composition_instances",
              "damage_operators", "cross_domain_links"]:
    r = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    print(f"  {table:30s} {r[0]:6d} rows")

total_s = db.execute("SELECT COUNT(*) FROM composition_instances").fetchone()[0]
total_h = db.execute("SELECT COUNT(*) FROM abstract_compositions").fetchone()[0]
total_l = db.execute("SELECT COUNT(*) FROM cross_domain_links").fetchone()[0]
print(f"\nTotal: {total_h} hubs, {total_s} spokes, {total_l} cross-domain links, 7 damage operators")

db.close()
