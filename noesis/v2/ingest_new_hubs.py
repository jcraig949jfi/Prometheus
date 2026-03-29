"""Ingest 5 new Gemini hubs: Quintic, Gibbs, No Free Lunch, Myerson-Satterthwaite, Finance Trilemma."""
import duckdb, json, sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb')

hubs = [
    {
        "hub_id": "IMPOSSIBILITY_QUINTIC_INSOLVABILITY",
        "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
        "desc": "No general algebraic solution using radicals for polynomials of degree 5+. S_n not solvable for n>=5 (A_5 is simple non-abelian).",
        "pattern": "Abel-Ruffini/Galois. Damage strategies: PARTITION domain (Galois classification), EXTEND operations (Bring radicals), TRUNCATE to approximation (Newton-Raphson), HIERARCHIZE to transcendentals (elliptic functions), RANDOMIZE search (Monte Carlo).",
        "resolutions": [
            ("GALOIS_CLASSIFICATION", "French", "algebra", "PARTITION", "Splits domain into solvable/unsolvable sub-classes. Preserves exactness for solvable subset. | CROSS: restrict_language"),
            ("BRING_RADICALS", "Swedish/British", "algebra", "EXTEND", "Invents new radical operator to force closure. Preserves exactness + universality, sacrifices simplicity. | CROSS: axiom_extension, crdts"),
            ("NEWTON_RAPHSON", "English", "numerical", "TRUNCATE", "Iterative approximation. Universal + simple but never exact. Infinite asymptotic tail. | CROSS: timeouts, eventual_consistency"),
            ("ELLIPTIC_FUNCTIONS", "French/German", "analysis", "HIERARCHIZE", "Hermite solved quintic via elliptic functions. Exact + universal but requires transcendental geometry. Domain leap. | CROSS: meta_system, khayyam"),
            ("MONTE_CARLO_ROOTS", "Modern", "computation", "RANDOMIZE", "Random sampling of complex plane. Universal but sacrifices exactness + determinism. | CROSS: probabilistic_halting"),
        ]
    },
    {
        "hub_id": "IMPOSSIBILITY_GIBBS_PHENOMENON",
        "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
        "desc": "Fourier series cannot converge to discontinuous function without permanent ~9% overshoot at jumps. L2 converges but L-infinity does not.",
        "pattern": "Gibbs 1899. Damage strategies: CONCENTRATE ringing at discontinuity, DISTRIBUTE via Cesaro averaging, TRUNCATE via Lanczos windowing, HIERARCHIZE via wavelets, PARTITION via Chebyshev nodes.",
        "resolutions": [
            ("ACCEPT_OVERSHOOT", "Classical", "signal processing", "CONCENTRATE", "Accept 8.95% overshoot. Preserves pure basis functions. Damage localized at discontinuities. | CROSS: mercator"),
            ("CESARO_FEJER", "Hungarian", "analysis", "DISTRIBUTE", "Average partial sums. Eliminates overshoot but blurs signal. Low-pass filter effect. | CROSS: equal_temperament, anti_aliasing"),
            ("LANCZOS_SIGMA", "Hungarian/American", "applied math", "TRUNCATE", "Windowing function attenuates high frequencies. Sacrifices fidelity for smoothness. | CROSS: oversampling"),
            ("WAVELET_TRANSFORM", "French", "analysis", "HIERARCHIZE", "Localized basis functions. Eliminates Gibbs but requires 2D time-frequency grid. Massive complexity increase. | CROSS: meta_system, robinson_projection"),
            ("CHEBYSHEV_NODES", "Russian", "numerical analysis", "PARTITION", "Non-uniform sampling concentrated at boundaries. Zero ringing but warped spatial sampling. | CROSS: gall_peters, sortition"),
        ]
    },
    {
        "hub_id": "IMPOSSIBILITY_NO_FREE_LUNCH",
        "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
        "desc": "No single ML algorithm outperforms random guessing across ALL possible problems. Reducing bias increases variance.",
        "pattern": "Wolpert-Macready 1997. Every ML algorithm is a damage allocation strategy for where to concentrate predictive power.",
        "resolutions": [
            ("INDUCTIVE_BIAS", "Bayesian/AI", "ML", "CONCENTRATE", "Hardcode domain assumptions (CNNs for images). High accuracy in domain, fails outside. | CROSS: restrict_language"),
            ("ENSEMBLE_METHODS", "Statistical Learning", "ML", "DISTRIBUTE", "Average many weak learners. Preserves generalization, sacrifices interpretability. | CROSS: ensemble, approval, cesaro_fejer"),
            ("REGULARIZATION", "Applied Statistics", "ML", "TRUNCATE", "Penalize complexity. Forces generalization by blunting intelligence. | CROSS: time_outs, lanczos_sigma"),
            ("META_LEARNING", "Modern DL", "ML", "HIERARCHIZE", "Train model to output models. Kicks NFL one level up. Exponentiated compute. | CROSS: meta_system, market_maker"),
            ("SGD_NOISE", "Optimization", "ML", "RANDOMIZE", "Mini-batch noise prevents overfitting to sharp valleys. Drunkard down a hill. | CROSS: probabilistic"),
        ]
    },
    {
        "hub_id": "IMPOSSIBILITY_MYERSON_SATTERTHWAITE",
        "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
        "desc": "No bilateral trading mechanism can be simultaneously efficient, budget-balanced, and individually rational under private overlapping valuations.",
        "pattern": "Information asymmetry makes truth-telling require information rents that break budget balance.",
        "resolutions": [
            ("EXTERNAL_SUBSIDY", "Public Economics", "economics", "EXTEND", "Third party pays information rent. Perfect efficiency but system bleeds resources. | CROSS: axiom_extension, bring_radicals"),
            ("DEADWEIGHT_LOSS", "Free Markets", "economics", "TRUNCATE", "Accept failed trades. Budget balanced but beneficial pairings left unconnected. | CROSS: cp_system, newton_raphson"),
            ("VCG_MECHANISM", "Auction Theory", "economics", "CONCENTRATE", "Force truth via externality payments. Efficient but drains money from participants. | CROSS: mercator, accept_overshoot"),
            ("MARKET_MAKER", "Global Finance", "economics", "HIERARCHIZE", "Insert broker to absorb information risk. Bid-ask spread is the toll. | CROSS: meta_system, elliptic_functions"),
            ("PROBABILISTIC_TRADING", "Mechanism Design", "economics", "RANDOMIZE", "Execute trades probabilistically. Expected values balance but local uncertainty is terrifying. | CROSS: probabilistic_halting, stochastic_roots"),
        ]
    },
    {
        "hub_id": "IMPOSSIBILITY_MUNDELL_FLEMING",
        "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
        "desc": "Cannot simultaneously maintain fixed exchange rate, free capital flow, and independent monetary policy.",
        "pattern": "Arbitrage under free capital + fixed rates negates monetary policy. Every nation picks which pillar to sacrifice.",
        "resolutions": [
            ("FLOATING_RATE", "Modern Western", "macroeconomics", "TRUNCATE", "Abandon currency stability. Preserves policy + capital flow. Offloads risk to private sector. | CROSS: ap_system, deadweight_loss"),
            ("CAPITAL_CONTROLS", "Developing/China", "macroeconomics", "CONCENTRATE", "Firewall around borders. Creates black markets and distortion. | CROSS: restrict_language, inductive_bias"),
            ("CURRENCY_UNION", "European Union", "macroeconomics", "HIERARCHIZE", "Surrender to supranational authority (ECB). Individual nations lose all leverage. Greece trapped. | CROSS: meta_system, gregorian, market_maker"),
            ("MANAGED_FLOAT", "Emerging Markets", "macroeconomics", "DISTRIBUTE", "Continuous active compromise. Central bank fights attrition war against arbitrage. | CROSS: equal_temperament, borda, cesaro_fejer"),
            ("DOLLARIZATION", "Ecuador/El Salvador", "macroeconomics", "EXTEND", "Adopt foreign currency entirely. Unbreakable peg but total sovereign castration. | CROSS: cp_system, external_subsidy"),
        ]
    },
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

        # Extract cross-domain links from notes
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
        """, [instance_id, hid, None, tradition, domain,
              f"{notes_clean} | DAMAGE_OP: {damage_op}"])
        res_count += 1

        for target in cross_links:
            link_id = f"{instance_id}__TO__{target.upper().replace(' ','_')}"
            db.execute("""
                INSERT OR REPLACE INTO cross_domain_links
                (link_id, source_resolution, source_hub, target_hub, link_type, damage_operator)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [link_id, instance_id, hid, target.upper().replace(' ','_'), 'existing_hub', damage_op])
            link_count += 1

db.commit()

print(f"[NEW HUBS] {hub_count} ingested")
print(f"[RESOLUTIONS] {res_count} instances")
print(f"[CROSS-DOMAIN LINKS] {link_count} new typed edges")

# Final state
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
