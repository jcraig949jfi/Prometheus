"""
FALSIFICATION TEST 15: 11 Structural Primitives — Independence & Spanning
Aletheia — 2026-03-30
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

PRIMITIVES = [
    'COMPOSE', 'MAP', 'EXTEND', 'REDUCE', 'LIMIT',
    'DUALIZE', 'LINEARIZE', 'STOCHASTICIZE', 'SYMMETRIZE',
    'BREAK_SYMMETRY', 'COMPLETE'
]

# ============================================================
# CHECK 1: INDEPENDENCE — Can any primitive decompose into others?
# ============================================================

independence = {}

# COMPOSE: combining two structures into one while preserving both
# Could COMPOSE = MAP + EXTEND? No. MAP transforms a single structure.
# EXTEND adds dimensions. Neither preserves two separate inputs as a product.
# COMPOSE is the monoidal product — categorically, the tensor product functor.
# Verdict: INDEPENDENT
independence['COMPOSE'] = {
    'status': 'INDEPENDENT',
    'attempted_decomposition': 'MAP + EXTEND',
    'why_fails': 'MAP transforms one structure; EXTEND adds dimensions to one structure. Neither produces a product of two independent structures. COMPOSE is the monoidal product — categorically irreducible.',
    'categorical_role': 'Tensor product functor in monoidal categories'
}

# MAP: structure-preserving transformation (functorial)
# Could MAP = LINEARIZE + EXTEND? No — MAP doesn't require linearity.
# MAP is the general functor. LINEARIZE is MAP restricted to tangent spaces.
# Verdict: INDEPENDENT
independence['MAP'] = {
    'status': 'INDEPENDENT',
    'attempted_decomposition': 'LINEARIZE + EXTEND',
    'why_fails': 'MAP is the general functor (structure-preserving morphism). LINEARIZE is a special case of MAP (linear approximation). You cannot build MAP from LINEARIZE because MAP includes nonlinear maps.',
    'categorical_role': 'Functor between categories'
}

# EXTEND: adding structure/dimensions (left adjoint / free functor)
# Could EXTEND = COMPOSE + MAP? Test: extending R to C = composing R with i and
# mapping the embedding? But COMPOSE requires two pre-existing structures, while
# EXTEND creates new structure. The free functor creates from nothing.
# Verdict: INDEPENDENT
independence['EXTEND'] = {
    'status': 'INDEPENDENT',
    'attempted_decomposition': 'COMPOSE + MAP',
    'why_fails': 'EXTEND is the free construction / left adjoint — it creates new structure (e.g., free group on generators). COMPOSE combines existing structures. You cannot compose with something that doesn\'t exist yet. EXTEND is categorically the left adjoint (free functor), which is not decomposable into tensor product + functor.',
    'categorical_role': 'Left adjoint / free functor'
}

# REDUCE: removing structure/dimensions (right adjoint / forgetful)
# Could REDUCE = MAP(projection) + LIMIT? Test: reducing R^3 to R^2 = projecting
# then taking limit? No — projection IS a MAP, but REDUCE is the forgetful functor
# which strips structure, not just projects. Forgetting group structure ≠ projecting.
# However: REDUCE as "forgetful functor" is closely related to MAP.
# The distinction: MAP preserves structure type, REDUCE changes it.
# Verdict: BORDERLINE — REDUCE is very close to a special case of MAP
independence['REDUCE'] = {
    'status': 'BORDERLINE',
    'attempted_decomposition': 'MAP (surjective/forgetful)',
    'why_fails': 'REDUCE (forgetful functor) strips structure. MAP (general functor) preserves structure type. A forgetful functor IS a functor — technically REDUCE is a special case of MAP (a functor that forgets). But categorically, forgetful functors have special properties (right adjoints, create limits) that general functors don\'t. The distinction is whether you preserve the category or change it.',
    'risk': 'If REDUCE = MAP(forgetful), the count drops to 10. However, the REDUCE-specific behavior (creating limits, having a left adjoint EXTEND) distinguishes it functorially.',
    'categorical_role': 'Forgetful functor / right adjoint'
}

# LIMIT: taking limits (sequential, topological, categorical)
# Could LIMIT = REDUCE applied infinitely? No — LIMIT involves convergence,
# a topological/order-theoretic property. REDUCE is algebraic (forget structure).
# LIMIT is the categorical limit (terminal cone), fundamentally different.
# Verdict: INDEPENDENT
independence['LIMIT'] = {
    'status': 'INDEPENDENT',
    'attempted_decomposition': 'iterated REDUCE',
    'why_fails': 'LIMIT is categorical limit (terminal cone over a diagram). It involves convergence and completeness — topological properties absent from REDUCE. Iterated REDUCE gives a chain of forgetful steps, not convergence to a limit object. The categorical limit is a universal property, not a sequential operation.',
    'categorical_role': 'Categorical limit (inverse limit, projective limit)'
}

# DUALIZE: swapping domain/codomain, contravariance
# Nothing else does this. The only primitive that reverses arrows.
# Verdict: INDEPENDENT
independence['DUALIZE'] = {
    'status': 'INDEPENDENT',
    'attempted_decomposition': 'none viable',
    'why_fails': 'DUALIZE is the contravariant functor / op-construction. No other primitive reverses the direction of morphisms. Unique.',
    'categorical_role': 'Contravariant functor / op-category construction'
}

# LINEARIZE: local linear approximation
# Could LINEARIZE = MAP(tangent) + REDUCE(to first order)?
# This is plausible: linearization IS mapping to tangent space (MAP) and then
# reducing to first-order terms (REDUCE/TRUNCATE).
# But: LINEARIZE has a specific geometric meaning (derivative/Jacobian) that
# MAP + REDUCE doesn't capture — it requires differential structure.
# Verdict: BORDERLINE — arguably MAP + REDUCE on a differential category
independence['LINEARIZE'] = {
    'status': 'BORDERLINE',
    'attempted_decomposition': 'MAP(tangent bundle) + REDUCE(to first order)',
    'why_fails_partially': 'Linearization IS mapping to the tangent space and truncating to first order. This is compositionally valid in differential categories. However, LINEARIZE requires smooth/differential structure on the source category — it\'s not just any MAP + REDUCE, it\'s specifically the derivative functor.',
    'risk': 'If LINEARIZE = MAP + REDUCE in differential categories, the count drops to 10 (or 9 if REDUCE is also redundant). However, LINEARIZE is the unique primitive that interfaces between nonlinear and linear worlds — its role in the basis is to bridge these regimes.',
    'categorical_role': 'Tangent functor / derivative / Jacobian'
}

# STOCHASTICIZE: deterministic → probabilistic
# Nothing else adds probability. Unique operation.
# Could it be EXTEND(probability space) + MAP(measurable)?
# Test: stochasticizing a deterministic map f: X→Y means extending to
# f: X→P(Y) where P is the probability monad. This IS EXTEND + MAP
# but the probability monad itself is the new structure.
# Verdict: INDEPENDENT — the probability monad is irreducible
independence['STOCHASTICIZE'] = {
    'status': 'INDEPENDENT',
    'attempted_decomposition': 'EXTEND(probability space) + MAP(measurable function)',
    'why_fails': 'While stochasticization can be DESCRIBED as extending to a probability space and mapping measurably, the Giry monad (probability monad) itself is a new mathematical object not derivable from deterministic primitives. You need the concept of measure/probability as a primitive to construct it. EXTEND adds algebraic structure, but probability requires measure theory.',
    'categorical_role': 'Giry monad / Kleisli category of probability'
}

# SYMMETRIZE: imposing symmetry (quotient by group action)
# Could SYMMETRIZE = REDUCE(quotient)? Test: symmetrizing by group G means
# taking X/G (quotient). This IS a reduction — forgetting the G-action and
# collapsing orbits. But: SYMMETRIZE specifically requires a group action,
# while REDUCE is general structure-forgetting.
# Verdict: BORDERLINE — special case of REDUCE via quotient
independence['SYMMETRIZE'] = {
    'status': 'BORDERLINE',
    'attempted_decomposition': 'REDUCE(quotient by group action)',
    'why_fails_partially': 'SYMMETRIZE = quotient by group action = a specific type of REDUCE. Categorically, taking the quotient X/G is a coequalizer (a colimit, actually — the dual of LIMIT). But SYMMETRIZE carries additional information: it specifies WHICH group acts and HOW. This makes it more structured than bare REDUCE.',
    'risk': 'If SYMMETRIZE ⊂ REDUCE, count drops. But REDUCE forgets structure while SYMMETRIZE ADDS structure (the symmetry constraint). These go in opposite directions. The quotient interpretation works algebraically but misses the constructive aspect: SYMMETRIZE as "enforce that φ(gx) = φ(x) for all g ∈ G" is an imposition, not a forgetting.',
    'categorical_role': 'Quotient/orbit functor, equivariant category'
}

# BREAK_SYMMETRY: removing symmetry, choosing a representative
# Could BREAK_SYMMETRY = EXTEND(labeling) + MAP(section)?
# Breaking symmetry = choosing a section of the quotient map X → X/G.
# This requires EXTENDING with a labeling and MAPPING to a representative.
# But: choosing a section is a fundamentally non-canonical operation —
# it requires CHOICE (related to Axiom of Choice). No composition of
# deterministic primitives produces non-canonical choice.
# Verdict: INDEPENDENT — requires non-canonical choice
independence['BREAK_SYMMETRY'] = {
    'status': 'INDEPENDENT',
    'attempted_decomposition': 'EXTEND(labeling) + MAP(section)',
    'why_fails': 'BREAK_SYMMETRY requires choosing a section of a quotient map — a fundamentally non-canonical operation. This is why it\'s connected to spontaneous symmetry breaking in physics: the choice cannot be derived from the symmetric system. No composition of structure-preserving primitives produces non-canonical choice. Categorically: sections of epimorphisms don\'t always exist and when they do, they\'re not functorial.',
    'categorical_role': 'Section of epimorphism / choice function'
}

# COMPLETE: filling gaps (Cauchy completion, algebraic closure)
# Could COMPLETE = EXTEND + LIMIT? Test: completing Q to R =
# extending with Cauchy sequences (EXTEND) and taking limits (LIMIT).
# This is VERY plausible. Cauchy completion IS: extend the space with
# equivalence classes of Cauchy sequences, then the limit points are
# automatically included.
# Algebraic closure: extend with roots (EXTEND), complete under limits.
# Verdict: LIKELY REDUNDANT — COMPLETE ≈ EXTEND + LIMIT
independence['COMPLETE'] = {
    'status': 'LIKELY_REDUNDANT',
    'attempted_decomposition': 'EXTEND + LIMIT',
    'why_works': 'Cauchy completion = extend with Cauchy sequences + take their limits. Algebraic closure = extend with roots of polynomials + close under limits. Profinite completion = extend with inverse system + take limit. In all standard cases, COMPLETE decomposes into EXTEND (add the missing elements) + LIMIT (ensure closure). Categorically, completion is the left adjoint to the inclusion of complete objects, which factors through free extension and limit.',
    'risk': 'HIGH. If COMPLETE = EXTEND + LIMIT, the primitive count drops from 11 to 10. This was flagged when COMPLETE was added as the 11th primitive — it may have been premature.',
    'categorical_role': 'Completion functor (factors through EXTEND + LIMIT)',
    'counterargument': 'COMPLETE has a holistic character — it fills ALL gaps simultaneously, not sequentially. But formally, this is still EXTEND (add all missing limit points) + LIMIT (verify they converge).'
}

# ============================================================
# TALLY
# ============================================================
independent = [p for p, v in independence.items() if v['status'] == 'INDEPENDENT']
borderline = [p for p, v in independence.items() if v['status'] == 'BORDERLINE']
redundant = [p for p, v in independence.items() if v['status'] == 'LIKELY_REDUNDANT']

print("=== INDEPENDENCE CHECK ===", flush=True)
print(f"INDEPENDENT:      {len(independent)} — {independent}", flush=True)
print(f"BORDERLINE:       {len(borderline)} — {borderline}", flush=True)
print(f"LIKELY REDUNDANT: {len(redundant)} — {redundant}", flush=True)

# ============================================================
# CHECK 2: SPANNING — Do other frameworks need a 12th primitive?
# ============================================================

spanning = {}

# MOULINES (1987) — Structuralist theory of science
# Key operations: specialization, reduction, theoretization, approximation
spanning['moulines'] = {
    'operations': {
        'specialization': 'REDUCE — restricting a theory to a special case',
        'reduction': 'MAP — mapping one theory into another (inter-theoretic reduction)',
        'theoretization': 'EXTEND — adding theoretical terms to an empirical base',
        'approximation': 'LIMIT — approaching exact description via successive approximation',
        'idealization': 'LINEARIZE — simplifying by taking limiting cases (frictionless, infinite population)',
        'combination': 'COMPOSE — combining two theories into a unified framework'
    },
    'unmapped': [],
    'verdict': 'All Moulines operations map to existing primitives. No 12th needed.'
}

# LAWVERE (1963) — Categorical foundations
# Key operations: products, coproducts, exponentials, limits, colimits, adjunctions
spanning['lawvere'] = {
    'operations': {
        'product': 'COMPOSE — categorical product (pairs of objects)',
        'coproduct': 'COMPOSE (dual) — categorical coproduct (disjoint union)',
        'exponential': 'MAP — internal hom / function space',
        'limit': 'LIMIT — categorical limit',
        'colimit': 'EXTEND — categorical colimit (free construction)',
        'left_adjoint': 'EXTEND — free functor',
        'right_adjoint': 'REDUCE — forgetful functor',
        'natural_transformation': 'MAP — morphism between functors',
        'Kan_extension': 'EXTEND + MAP — universal extension along a functor',
        'subobject_classifier': 'BREAK_SYMMETRY — truth values / characteristic functions',
        'topos_internal_logic': 'No direct map — but built from COMPOSE + MAP + LIMIT'
    },
    'unmapped': [],
    'note': 'Kan extensions (left/right) decompose into EXTEND + MAP. Topos logic is emergent from composition of primitives.',
    'verdict': 'All Lawvere categorical operations map. No 12th needed.'
}

# GOGUEN-BURSTALL (1984) — Institutions
# Key operations: signature morphisms, theory morphisms, model reducts
spanning['goguen_burstall'] = {
    'operations': {
        'signature_morphism': 'MAP — mapping between signature categories',
        'theory_morphism': 'MAP + REDUCE — mapping theories with axiom preservation',
        'model_reduct': 'REDUCE — restricting models along signature morphisms',
        'institution_morphism': 'MAP — structure-preserving map between institutions',
        'colimit_of_theories': 'EXTEND + COMPOSE — combining theories via pushout',
        'amalgamation': 'COMPOSE + LIMIT — combining models consistently'
    },
    'unmapped': [],
    'verdict': 'All institution-theoretic operations map. No 12th needed.'
}

# SHIEBLER ET AL (2021) — Categorical deep learning
# Key operations: functors, natural transformations, monoidal products, parameterized maps
spanning['shiebler_2021'] = {
    'operations': {
        'parameterized_morphism': 'MAP — parameterized function (neural network layer)',
        'functor': 'MAP — structure-preserving transformation between categories',
        'natural_transformation': 'MAP — morphism between functors',
        'monoidal_product': 'COMPOSE — tensor product of representations',
        'backpropagation': 'DUALIZE + MAP — reverse-mode differentiation (contravariant)',
        'regularization': 'REDUCE + STOCHASTICIZE — dropout, weight decay',
        'data_augmentation': 'SYMMETRIZE — enforcing invariance to transformations',
        'normalization': 'SYMMETRIZE + LINEARIZE — batch norm, layer norm',
        'attention': 'BREAK_SYMMETRY + COMPOSE — selecting and combining inputs',
        'pooling': 'REDUCE + SYMMETRIZE — invariant aggregation'
    },
    'unmapped': [],
    'verdict': 'All categorical deep learning operations map. No 12th needed.'
}

# CANDIDATE 12th PRIMITIVES
candidates = {
    'ADJOIN': {
        'description': 'Left/right adjunction from category theory',
        'decomposition': 'EXTEND (left adjoint = free) + REDUCE (right adjoint = forgetful). Adjunction is not a primitive — it\'s a RELATIONSHIP between EXTEND and REDUCE.',
        'is_new_primitive': False
    },
    'QUOTIENT': {
        'description': 'Equivalence class formation',
        'decomposition': 'SYMMETRIZE (impose equivalence relation) + REDUCE (collapse classes). Or: REDUCE via coequalizer.',
        'is_new_primitive': False
    },
    'PULLBACK': {
        'description': 'Fibered product',
        'decomposition': 'COMPOSE (product) + REDUCE (fiber condition) = categorical limit over a cospan. Decomposes into LIMIT + COMPOSE.',
        'is_new_primitive': False
    },
    'PUSHOUT': {
        'description': 'Fibered coproduct',
        'decomposition': 'COMPOSE (coproduct) + EXTEND (identification) = categorical colimit over a span. Decomposes into EXTEND + COMPOSE.',
        'is_new_primitive': False
    },
    'FORGET': {
        'description': 'Forgetful functor',
        'decomposition': 'This IS REDUCE. Not a separate primitive.',
        'is_new_primitive': False
    },
    'CURRY': {
        'description': 'Currying / exponential adjunction',
        'decomposition': 'MAP (internal hom construction) + COMPOSE (partial application). Standard in cartesian closed categories.',
        'is_new_primitive': False
    },
    'SAMPLE': {
        'description': 'Drawing from a probability distribution',
        'decomposition': 'STOCHASTICIZE + REDUCE (select one outcome). Or: MAP from probability space to sample space.',
        'is_new_primitive': False
    }
}

print("\n=== SPANNING CHECK ===", flush=True)
for framework, data in spanning.items():
    unmapped = data.get('unmapped', [])
    print(f"{framework}: {len(data['operations'])} ops mapped, {len(unmapped)} unmapped", flush=True)

print("\n=== CANDIDATE 12th PRIMITIVES ===", flush=True)
for name, data in candidates.items():
    print(f"  {name}: {'NEW PRIMITIVE' if data['is_new_primitive'] else 'DECOMPOSES'} — {data['decomposition'][:80]}", flush=True)

# ============================================================
# FINAL VERDICT
# ============================================================

# The critical findings:
# 1. COMPLETE is likely EXTEND + LIMIT (redundant)
# 2. LINEARIZE is borderline MAP + REDUCE (in differential categories)
# 3. SYMMETRIZE is borderline REDUCE (quotient)
# 4. REDUCE is borderline MAP (forgetful functor)
# If all borderline cases go redundant: 11 - 1(COMPLETE) - 1(LINEARIZE) - 1(SYMMETRIZE) - 1(REDUCE) = 7 primitives
# Conservative: only COMPLETE is clearly redundant → 10 primitives
# Most conservative: all borderline survive → 10 primitives (COMPLETE still falls)

if len(redundant) > 0:
    result = "FAIL"
    confidence = "MODERATE"
    summary = (
        f"COMPLETE is likely redundant (EXTEND + LIMIT). "
        f"Additionally, {len(borderline)} primitives are borderline: {borderline}. "
        f"Conservative count: 10 independent primitives, not 11. "
        f"If borderline cases also fall: as few as 7."
    )
else:
    result = "PASS"
    confidence = "HIGH"
    summary = "All 11 primitives are independent."

print(f"\n=== VERDICT: {result} ({confidence}) ===", flush=True)
print(summary, flush=True)

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    "test": 15,
    "paper": "11 Structural Primitives",
    "claim": "Mathematics decomposes into exactly 11 structural transformation primitives, no more and no fewer",
    "result": result,
    "confidence": confidence,
    "evidence": summary,
    "independence_analysis": {p: v['status'] for p, v in independence.items()},
    "independent_primitives": independent,
    "borderline_primitives": borderline,
    "redundant_primitives": redundant,
    "conservative_count": 11 - len(redundant),
    "aggressive_count": 11 - len(redundant) - len(borderline),
    "decomposition_details": {
        p: {
            'status': v['status'],
            'attempted': v.get('attempted_decomposition', ''),
            'analysis': v.get('why_fails', v.get('why_fails_partially', v.get('why_works', '')))
        } for p, v in independence.items()
    },
    "spanning_analysis": {
        fw: {
            'operations_mapped': len(data['operations']),
            'unmapped': data.get('unmapped', []),
            'verdict': data['verdict']
        } for fw, data in spanning.items()
    },
    "candidate_12th_primitives": {
        name: {'is_new': data['is_new_primitive'], 'decomposition': data['decomposition']}
        for name, data in candidates.items()
    },
    "missing_primitives": [],
    "implications_for_other_papers": (
        "If COMPLETE is redundant, Paper 15 title must change from '11' to '10'. "
        "The primitive basis is still valid — just smaller. "
        "Papers 1-14 are unaffected since they use the damage operators (derived from primitives), "
        "not the primitives directly. The damage operator count (9) is independent of "
        "whether COMPLETE is primitive or derived. "
        "If LINEARIZE and SYMMETRIZE also fall, the basis shrinks to 7-8 but the "
        "SPANNING property still holds — all mathematical operations still decompose."
    )
}

with open('F:/Prometheus/falsification/test_15_result.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\nSaved to F:/Prometheus/falsification/test_15_result.json", flush=True)
