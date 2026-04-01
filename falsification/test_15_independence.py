"""
Aletheia — Falsification Test 15
CLAIM: Mathematics decomposes into exactly 11 structural transformation primitives.
Primitives: COMPOSE, MAP, EXTEND, REDUCE, LIMIT, DUALIZE, LINEARIZE,
            STOCHASTICIZE, SYMMETRIZE, BREAK_SYMMETRY, COMPLETE

CHECK 1: Independence — Can any primitive be expressed as a composition of others?
CHECK 2: Spanning — Do external frameworks require a 12th primitive?
"""

import json
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# PRIMITIVE DEFINITIONS — Semantic signatures
# ============================================================
# Each primitive is characterized by:
#   - Input type / Output type
#   - Essential property (what it MUST do)
#   - Distinguishing constraint (what makes it irreducible)

PRIMITIVES = {
    "COMPOSE": {
        "signature": "(F, G) -> F∘G",
        "essential": "Combines two structures/morphisms into one",
        "preserves": "Both input structures exist in the output",
    },
    "MAP": {
        "signature": "F(A) -> F(B) via f:A->B",
        "essential": "Applies transformation while preserving outer structure",
        "preserves": "Functoriality — structure of F is unchanged",
    },
    "EXTEND": {
        "signature": "A -> A⊕E (embedding into larger structure)",
        "essential": "Adds new dimensions, elements, or algebraic structure",
        "preserves": "Original structure is a substructure of the result",
    },
    "REDUCE": {
        "signature": "A -> π(A) (projection/quotient)",
        "essential": "Removes dimensions, collapses equivalence classes",
        "preserves": "Some structural aspect of A survives in π(A)",
    },
    "LIMIT": {
        "signature": "A_n -> lim(A_n) (convergence)",
        "essential": "Takes a limiting object of a directed/filtered system",
        "preserves": "Universal property — cone over the diagram",
    },
    "DUALIZE": {
        "signature": "A -> A* (swap domain/codomain)",
        "essential": "Reverses arrows, swaps perspectives",
        "preserves": "Structure up to reversal",
    },
    "LINEARIZE": {
        "signature": "A -> T_p(A) (tangent/first-order approximation)",
        "essential": "Local linear approximation at a point",
        "preserves": "First-order behavior",
    },
    "STOCHASTICIZE": {
        "signature": "A -> P(A) (probability measures on A)",
        "essential": "Converts deterministic structure to probabilistic",
        "preserves": "Underlying measurable structure",
    },
    "SYMMETRIZE": {
        "signature": "A -> A/G (impose group action invariance)",
        "essential": "Forces invariance under a symmetry group",
        "preserves": "G-invariant substructure",
    },
    "BREAK_SYMMETRY": {
        "signature": "A/G -> A (choose representative / lift)",
        "essential": "Selects among equivalent options, breaks degeneracy",
        "preserves": "Local structure, loses global symmetry",
    },
    "COMPLETE": {
        "signature": "A -> Â (add limit points / fill gaps)",
        "essential": "Fills in missing elements to make structure 'whole'",
        "preserves": "A is dense in Â",
    },
}

# ============================================================
# CHECK 1: Independence Analysis
# ============================================================

def analyze_independence():
    """For each primitive, attempt to decompose it as a composition of others."""

    results = {}

    # --- COMPOSE ---
    # Claim: COMPOSE = MAP + EXTEND?
    # MAP transforms *within* a structure. EXTEND adds structure.
    # COMPOSE combines two *independent* structures/morphisms.
    # MAP(f) applied to F gives F(f), but COMPOSE(F,G) gives F∘G —
    # these are categorically different: MAP is a functor action on morphisms,
    # COMPOSE is the composition operation of the category itself.
    # Verdict: MAP + EXTEND gives "transform then embed" not "combine two morphisms."
    results["COMPOSE"] = {
        "attempted_decomposition": "MAP + EXTEND",
        "analysis": (
            "MAP transforms within a fixed functor; EXTEND embeds into a larger space. "
            "Neither captures the essential operation of composing two morphisms f∘g. "
            "Composition is the fundamental operation of category theory — it is axiomatic, "
            "not derivable from functorial actions. MAP is *defined in terms of* COMPOSE "
            "(functors preserve composition), so COMPOSE is logically prior."
        ),
        "verdict": "independent",
        "confidence": "HIGH",
    }

    # --- MAP ---
    # Claim: MAP = LINEARIZE + EXTEND?
    # LINEARIZE approximates locally (first-order). MAP is exact and global.
    # A functor F: C -> D maps objects and morphisms preserving composition and identity.
    # LINEARIZE loses higher-order information. MAP does not.
    results["MAP"] = {
        "attempted_decomposition": "LINEARIZE + EXTEND",
        "analysis": (
            "MAP is exact structure-preservation (functoriality). LINEARIZE is approximate "
            "(first-order). MAP works on discrete structures (graphs, posets) where LINEARIZE "
            "is undefined. MAP is the *most general* structure-preserving operation — "
            "it IS the functor concept. Cannot be composed from approximation primitives."
        ),
        "verdict": "independent",
        "confidence": "HIGH",
    }

    # --- EXTEND --- *** INVESTIGATE ***
    # Claim: EXTEND = COMPOSE + MAP?
    # Example: Extend ℝ² to ℝ³. This is embedding via i: ℝ² ↪ ℝ³, (x,y) ↦ (x,y,0).
    # Could express as: MAP(i) where i is the inclusion, then COMPOSE with projection?
    # No — the inclusion i is itself the EXTENSION. MAP(i) presupposes i exists.
    # EXTEND *creates* the larger structure. MAP *uses* an existing morphism.
    # More precisely: EXTEND = "there exists a monomorphism A ↪ B where B is strictly larger."
    # This is an existential construction, not a transformation of existing data.
    # However: EXTEND(A, E) could be seen as COMPOSE(A, E) in the coproduct sense: A ⊕ E.
    # But COMPOSE is morphism composition (sequential), while EXTEND is coproduct (parallel).
    # These are fundamentally different categorical operations.
    results["EXTEND"] = {
        "attempted_decomposition": "COMPOSE + MAP",
        "analysis": (
            "EXTEND creates a strictly larger structure containing the original as substructure. "
            "Attempted decomposition: COMPOSE(A, E) + MAP(embedding). But this is circular — "
            "the embedding IS the extension. COMPOSE combines morphisms sequentially (f∘g); "
            "EXTEND combines structures in parallel (A⊕E, coproduct/product). "
            "Sequential composition cannot produce parallel enlargement. "
            "In category theory, coproducts are not derivable from composition alone — "
            "they require a universal property (colimit) that composition does not provide."
        ),
        "verdict": "independent",
        "confidence": "HIGH",
    }

    # --- REDUCE --- *** INVESTIGATE ***
    # Claim: REDUCE = MAP(projection) + LIMIT?
    # Example: ℝ³ → ℝ² via (x,y,z) ↦ (x,y). This is MAP applied to a projection morphism.
    # But is REDUCE just a special case of MAP?
    # Key distinction: MAP preserves structure (functorial). REDUCE *destroys* structure.
    # A projection π: ℝ³ → ℝ² is a morphism, and MAP(π) would apply it functorially.
    # But "applying a surjective morphism" IS reduction. Is MAP the more fundamental operation?
    #
    # CRITICAL ANALYSIS: In category theory, a functor F: C → D can be faithful, full, or
    # essentially surjective. A forgetful functor U: Grp → Set is a MAP that REDUCES
    # (forgets group structure). So yes, REDUCE can be expressed as MAP with a specific
    # class of morphisms (surjections/projections/forgetful functors).
    #
    # BUT: MAP is "apply a morphism functorially." REDUCE is "there exists a morphism that
    # loses information." The *existence* of such a morphism is the content of REDUCE.
    # MAP doesn't tell you *which* morphism to apply. REDUCE specifies a *direction*: less structure.
    #
    # Counter-argument: REDUCE = MAP(π) where π is a projection. This works for dimensional
    # reduction but not for quotient (ℤ → ℤ/nℤ). Quotients require identifying elements,
    # which is SYMMETRIZE + REDUCE... circular.
    #
    # Actually, REDUCE includes: projections, quotients, restrictions, truncations.
    # MAP is agnostic to information loss. REDUCE inherently loses information.
    # The information-theoretic directionality (entropy increase) distinguishes REDUCE from MAP.
    results["REDUCE"] = {
        "attempted_decomposition": "MAP(projection) or MAP + LIMIT",
        "analysis": (
            "REDUCE can be *implemented* as MAP applied to a surjective/projection morphism. "
            "However, REDUCE carries essential semantic content that MAP lacks: directionality "
            "of information loss. MAP is structure-preserving; REDUCE is structure-destroying. "
            "More critically: quotient constructions (Z -> Z/nZ) require equivalence class "
            "formation which is not just 'apply a morphism' — it requires choosing WHICH "
            "elements to identify. This is a separate creative act from MAP. "
            "The LIMIT decomposition fails because LIMIT is about convergence of sequences, "
            "not finite-dimensional projection. "
            "HOWEVER: the boundary between MAP-with-surjection and REDUCE is genuinely thin. "
            "If MAP is defined broadly enough to include non-injective morphisms, REDUCE is "
            "arguably a subclass of MAP rather than independent."
        ),
        "verdict": "WEAK_INDEPENDENT",
        "confidence": "MODERATE",
        "concern": (
            "REDUCE may be a special case of MAP (applying a non-injective morphism). "
            "Independence holds only if we restrict MAP to structure-preserving (injective) "
            "morphisms, which is non-standard in category theory where all morphisms are valid."
        ),
    }

    # --- LIMIT ---
    # Claim: LIMIT = special REDUCE?
    # REDUCE is finite/discrete. LIMIT involves convergence, continuity, topology.
    # LIMIT is a categorical universal property (terminal cone over a diagram).
    # REDUCE is a single morphism application. These are structurally different.
    # LIMIT produces *new* objects (the limit object), REDUCE projects onto existing subspaces.
    results["LIMIT"] = {
        "attempted_decomposition": "REDUCE (sequential)",
        "analysis": (
            "LIMIT takes a diagram (functor from index category) and produces a universal cone. "
            "This involves: (1) an infinite/directed system, (2) a convergence criterion, "
            "(3) a universal property. REDUCE is a single morphism application with no "
            "convergence or universality. Example: completion of Q to R cannot be expressed "
            "as any finite sequence of REDUCEs. LIMIT is genuinely about infinite processes "
            "and their convergence — a fundamentally different operation."
        ),
        "verdict": "independent",
        "confidence": "HIGH",
    }

    # --- DUALIZE ---
    results["DUALIZE"] = {
        "attempted_decomposition": "None obvious",
        "analysis": (
            "DUALIZE reverses all arrows in a category (op functor). No other primitive "
            "reverses directionality. MAP preserves direction. COMPOSE preserves direction. "
            "DUALIZE is the unique orientation-reversing primitive. "
            "Formally: (-)^op : Cat -> Cat is not expressible via any composition of "
            "covariant functors."
        ),
        "verdict": "independent",
        "confidence": "HIGH",
    }

    # --- LINEARIZE --- *** INVESTIGATE ***
    # Claim: LINEARIZE = MAP(tangent) + REDUCE(to first order)?
    # Tangent space construction: given M smooth manifold, p ∈ M, T_pM is the linearization.
    # Step 1: MAP the local chart to get a coordinate representation.
    # Step 2: REDUCE to first-order Taylor expansion (discard higher terms).
    # This actually works! LINEARIZE(f, p) = REDUCE(MAP(f, local_chart), first_order).
    #
    # BUT WAIT: What does "first_order" mean? It means we're keeping the linear part.
    # This requires the CONCEPT of linearity — which is what LINEARIZE provides.
    # If REDUCE means "project onto a subspace," then projecting onto the linear part
    # presupposes you know what "linear" means. That's circular.
    #
    # Deeper: LINEARIZE is about the relationship between a nonlinear object and its
    # best linear approximation. This involves a METRIC or NORM concept (to define "best").
    # Neither MAP nor REDUCE inherently carry metric structure.
    #
    # Actually no — LINEARIZE is the tangent functor T: Diff -> Vect.
    # It IS a functor (MAP). But it's a specific functor with specific properties.
    # The question is: is LINEARIZE a primitive, or an instance of MAP?
    #
    # If MAP is "any functor," then LINEARIZE is just the tangent functor T, which is
    # an instance of MAP, not a separate primitive.
    # If MAP is "applying an explicitly given morphism," then LINEARIZE is separate
    # because it *constructs* the linear approximation rather than applying a given map.
    results["LINEARIZE"] = {
        "attempted_decomposition": "MAP(tangent_functor) + REDUCE(to_first_order)",
        "analysis": (
            "LINEARIZE can be decomposed as: (1) MAP via the tangent functor T: Diff -> Vect, "
            "then (2) REDUCE to first-order terms. However, this decomposition has a "
            "circularity problem: 'REDUCE to first order' presupposes the concept of "
            "linearity (what IS first order?). The tangent functor T itself encodes the "
            "LINEARIZE operation. So the decomposition is: LINEARIZE = MAP(LINEARIZE). "
            "This is circular, which actually SUPPORTS independence. "
            "More fundamentally: LINEARIZE is about local-to-global relationships and "
            "differential structure. No other primitive captures the passage from nonlinear "
            "to linear. STOCHASTICIZE doesn't (probability, not approximation). "
            "REDUCE doesn't (it removes dimensions, not curvature). "
            "LINEARIZE is the unique primitive that introduces differential/infinitesimal "
            "structure."
        ),
        "verdict": "independent",
        "confidence": "MODERATE",
        "concern": (
            "If MAP is defined broadly as 'any functor,' then the tangent functor T "
            "is an instance of MAP, making LINEARIZE not a separate primitive but a "
            "distinguished instance. The counter-argument is that LINEARIZE requires "
            "smooth/differential structure that MAP alone doesn't guarantee."
        ),
    }

    # --- STOCHASTICIZE ---
    results["STOCHASTICIZE"] = {
        "attempted_decomposition": "None obvious",
        "analysis": (
            "STOCHASTICIZE maps deterministic objects to probability distributions over them. "
            "This is the Giry monad: X ↦ P(X) (probability measures on X). "
            "No combination of the other primitives introduces measure theory or probability. "
            "EXTEND adds algebraic structure, not measure structure. "
            "MAP preserves existing structure, doesn't add randomness. "
            "STOCHASTICIZE is the unique primitive that bridges deterministic and "
            "stochastic mathematics."
        ),
        "verdict": "independent",
        "confidence": "HIGH",
    }

    # --- SYMMETRIZE --- *** INVESTIGATE ***
    # Claim: SYMMETRIZE = REDUCE(quotient by group action)?
    # SYMMETRIZE(X, G) = X/G (orbit space).
    # REDUCE(X, ~_G) = X/~ where x ~ y iff ∃g: gx = y.
    # This IS a quotient, which IS a reduction.
    # So SYMMETRIZE = REDUCE with a specific equivalence relation (group-orbit equivalence).
    #
    # But: REDUCE(quotient) can form ANY equivalence class, not just group orbits.
    # SYMMETRIZE specifically involves GROUP ACTIONS. The group structure is essential —
    # it's not just any equivalence relation but one arising from a group.
    #
    # Counter: In category theory, any equivalence relation on an object in a regular
    # category gives a quotient. Group-orbit quotients are a special case.
    # So SYMMETRIZE ⊂ REDUCE (SYMMETRIZE is a subclass of REDUCE).
    #
    # HOWEVER: SYMMETRIZE also includes the reverse direction: averaging/Reynolds operator.
    # Given f: X → Y, SYMMETRIZE produces f_avg = (1/|G|) Σ_g f(g·x).
    # This averaging IS NOT just a quotient — it requires summation and normalization,
    # which involves... STOCHASTICIZE (uniform measure on G) + REDUCE (marginalize).
    #
    # Hmm. Let's be precise:
    # SYMMETRIZE in its essence is: "impose G-invariance."
    # Method 1: Quotient X by G (REDUCE).
    # Method 2: Average over G (STOCHASTICIZE + REDUCE).
    # Method 3: Restrict to G-fixed points (REDUCE).
    # All implementations use REDUCE. SYMMETRIZE might not be independent of REDUCE.
    results["SYMMETRIZE"] = {
        "attempted_decomposition": "REDUCE(quotient_by_group_action)",
        "analysis": (
            "SYMMETRIZE(X, G) = X/G is literally a quotient construction, which is a "
            "form of REDUCE. All standard implementations of symmetrization — orbit quotients, "
            "Reynolds averaging, fixed-point restriction — decompose into REDUCE "
            "(plus STOCHASTICIZE for the averaging variant). "
            "The counter-argument is that SYMMETRIZE carries additional structure: "
            "the GROUP ACTION itself. REDUCE doesn't inherently involve groups. "
            "But the group action is INPUT DATA, not a separate OPERATION. "
            "The operation is still 'take a quotient' = REDUCE. "
            "VERDICT: SYMMETRIZE is REDUCE applied to group-orbit equivalence relations. "
            "It is a semantically important special case but NOT a structurally independent "
            "primitive."
        ),
        "verdict": "REDUNDANT",
        "confidence": "MODERATE",
        "decomposition": "REDUCE(quotient_by_G) — where G-orbits define the equivalence relation",
        "concern": (
            "One could argue the group action structure makes this qualitatively different "
            "from generic REDUCE. But categorically, coequalizers (quotients) are colimits, "
            "and REDUCE already covers colimits."
        ),
    }

    # --- BREAK_SYMMETRY --- *** INVESTIGATE ***
    # Claim: BREAK_SYMMETRY = EXTEND + MAP?
    # Breaking symmetry means choosing a preferred direction/element from equivalent options.
    # Example: Spontaneous symmetry breaking in physics — the Higgs field picks a vacuum.
    # This is a SECTION of the quotient map: s: X/G → X, choosing one representative per orbit.
    #
    # Can we decompose this?
    # EXTEND: add an external field/direction that distinguishes orbits? Yes — adding the
    #   Higgs field is EXTEND(spacetime, Higgs_bundle).
    # MAP: use the field to select representatives? Yes — MAP(selection_by_field).
    # So BREAK_SYMMETRY = EXTEND(external_data) + MAP(selection)?
    #
    # BUT: this only works for explicit symmetry breaking. Spontaneous symmetry breaking
    # doesn't add external data — the system itself selects. That's more like...
    # a non-functorial CHOICE. A section of a surjection. This requires the AXIOM OF CHOICE
    # or a specific selection principle.
    #
    # Key insight: BREAK_SYMMETRY is the INVERSE of SYMMETRIZE/REDUCE(quotient).
    # It's a RIGHT INVERSE (section) of the quotient map. This is:
    # BREAK_SYMMETRY = right_inverse(REDUCE) = "choose a section."
    # This is not EXTEND + MAP — it's a CHOICE operation.
    #
    # Is CHOICE = COMPOSE + ... anything? No. Choice is foundationally independent
    # (Axiom of Choice is independent of ZF). This supports BREAK_SYMMETRY being independent.
    #
    # But wait: is BREAK_SYMMETRY the same as EXTEND?
    # EXTEND adds new structure. BREAK_SYMMETRY selects from existing equivalent options.
    # EXTEND: ℝ² → ℝ³ (new dimension). BREAK_SYMMETRY: S¹ → pick a point (select from circle).
    # These are genuinely different: adding vs. selecting.
    results["BREAK_SYMMETRY"] = {
        "attempted_decomposition": "EXTEND + MAP, or right_inverse(REDUCE)",
        "analysis": (
            "BREAK_SYMMETRY selects a preferred representative from equivalent options. "
            "Attempted as EXTEND + MAP: explicit symmetry breaking adds an external field "
            "(EXTEND) then selects via that field (MAP). This works for EXPLICIT breaking "
            "but not SPONTANEOUS breaking, where no external data is added. "
            "Spontaneous breaking is a section of a quotient map — a right inverse of REDUCE. "
            "This requires a CHOICE principle (axiom of choice for surjections). "
            "Neither EXTEND nor MAP inherently involve choice among equivalent alternatives. "
            "BREAK_SYMMETRY is the unique primitive that embodies non-canonical selection. "
            "Foundationally, this connects to the Axiom of Choice, which is independent of "
            "other set-theoretic axioms — supporting the independence of this primitive."
        ),
        "verdict": "independent",
        "confidence": "MODERATE",
        "concern": (
            "If SYMMETRIZE is judged redundant (= REDUCE), then BREAK_SYMMETRY as its "
            "inverse might also be expressible as 'section of REDUCE.' But sections are "
            "not guaranteed to exist without Choice, making this a genuinely new operation."
        ),
    }

    # --- COMPLETE --- *** INVESTIGATE ***
    # Claim: COMPLETE = EXTEND + LIMIT?
    # Completion of Q to R: take all Cauchy sequences (EXTEND to sequence space),
    # then take limits (LIMIT) to get limit points, then quotient (REDUCE) by
    # equivalence of sequences with same limit.
    # So: COMPLETE = EXTEND + LIMIT + REDUCE? That's 3 primitives, not a primitive itself.
    #
    # Categorical completion (e.g., adding all limits to a category):
    # Ind-completion, Pro-completion, Cauchy completion of enriched categories.
    # These are all instances of: "freely adjoin all colimits/limits."
    # This is EXTEND (add new objects) + LIMIT (they satisfy limit universal properties).
    #
    # So COMPLETE = EXTEND + LIMIT seems to work.
    #
    # But: is the *process* of completion just extension + limit-taking?
    # EXTEND adds arbitrary new structure. COMPLETE adds EXACTLY the right new elements
    # to make the structure "whole" (every Cauchy sequence converges, every ideal is principal,
    # every diagram has a limit).
    #
    # COMPLETE = EXTEND(exactly_the_missing_limits) + LIMIT(they_converge).
    # The "exactly the missing" part is doing a lot of work — it's a specific, universal
    # construction, not arbitrary extension.
    #
    # Actually, in category theory, the free cocompletion is a left Kan extension.
    # Kan extensions decompose into limits and colimits (which are LIMIT).
    # And left Kan extension along the Yoneda embedding is the free cocompletion.
    # So categorically: COMPLETE = Yoneda + LIMIT.
    # Yoneda is MAP (it's a functor, the Yoneda embedding).
    # So: COMPLETE = MAP(Yoneda) + LIMIT.
    #
    # This is a genuine decomposition. COMPLETE decomposes into MAP + LIMIT.
    results["COMPLETE"] = {
        "attempted_decomposition": "EXTEND + LIMIT, or MAP(Yoneda) + LIMIT",
        "analysis": (
            "COMPLETE fills gaps to make a structure 'whole.' Analyzed multiple decompositions: "
            "(1) Metric completion: Q -> R = EXTEND(to Cauchy sequences) + LIMIT(quotient by "
            "convergence) + REDUCE(equivalence classes). Uses 3 primitives. "
            "(2) Categorical completion: free cocompletion = MAP(Yoneda embedding) + LIMIT "
            "(freely adjoin all colimits). Uses 2 primitives. "
            "(3) Algebraic completion: algebraic closure of a field = EXTEND(adjoin roots) "
            "iterated with LIMIT(transfinite union). Uses 2 primitives. "
            "In ALL cases, COMPLETE decomposes into 2-3 other primitives. "
            "The 'exactly the right elements' aspect is determined by the universal property "
            "of the LIMIT, not by a separate COMPLETE operation. "
            "VERDICT: COMPLETE = MAP + LIMIT (via Yoneda + free cocompletion). "
            "It is a DERIVED operation, not a primitive."
        ),
        "verdict": "REDUNDANT",
        "confidence": "MODERATE",
        "decomposition": "MAP(Yoneda_embedding) + LIMIT(free_cocompletion)",
        "concern": (
            "The decomposition relies on the Yoneda embedding, which is a very specific MAP. "
            "One could argue that COMPLETE is a 'named combination' that deserves primitive "
            "status for practical reasons. But structurally, it decomposes."
        ),
    }

    return results


# ============================================================
# CHECK 2: Spanning Analysis — External Frameworks
# ============================================================

def analyze_spanning():
    """Cross-reference the 11 primitives against major structural frameworks."""

    spanning = {}

    # --- Moulines (1987) Structuralist Theory of Science ---
    spanning["moulines_1987"] = {
        "framework": "Structuralist metatheory (Balzer-Moulines-Sneed)",
        "operations_identified": {
            "specialization": {
                "description": "Restricting a theory to a subdomain",
                "maps_to": "REDUCE",
                "confidence": "HIGH",
            },
            "theoretization": {
                "description": "Adding theoretical terms to an empirical structure",
                "maps_to": "EXTEND",
                "confidence": "HIGH",
            },
            "reduction_relation": {
                "description": "One theory reduces to another via structure-preserving map",
                "maps_to": "MAP + REDUCE",
                "confidence": "HIGH",
            },
            "approximation": {
                "description": "Theory T approximates T' within tolerance ε",
                "maps_to": "LINEARIZE (local approx) or LIMIT (ε→0)",
                "confidence": "MODERATE",
            },
            "combination": {
                "description": "Combining two theory-elements",
                "maps_to": "COMPOSE",
                "confidence": "HIGH",
            },
        },
        "unmapped_operations": [],
        "verdict": "All Moulines operations map to the 11 primitives. No 12th needed.",
    }

    # --- Lawvere (1963) Categorical Foundations ---
    spanning["lawvere_1963"] = {
        "framework": "Lawvere's functorial semantics + LFPT",
        "operations_identified": {
            "composition": {
                "description": "Morphism composition in a category",
                "maps_to": "COMPOSE",
                "confidence": "HIGH",
            },
            "functor_application": {
                "description": "Applying a functor F: C → D",
                "maps_to": "MAP",
                "confidence": "HIGH",
            },
            "natural_transformation": {
                "description": "Structure-preserving map between functors η: F ⇒ G",
                "maps_to": "MAP (at the 2-categorical level)",
                "confidence": "HIGH",
            },
            "limit_colimit": {
                "description": "Universal constructions: products, coproducts, equalizers, etc.",
                "maps_to": "LIMIT (limits) + EXTEND (colimits as dual)",
                "confidence": "HIGH",
            },
            "adjunction": {
                "description": "Left/right adjoint pair F ⊣ G",
                "maps_to": "*** SEE CANDIDATE ANALYSIS ***",
                "confidence": "LOW",
                "flag": "POTENTIAL_GAP",
            },
            "kan_extension": {
                "description": "Left/right Kan extension along a functor",
                "maps_to": "MAP + LIMIT (Kan = pointwise limit of a diagram)",
                "confidence": "MODERATE",
            },
            "yoneda_embedding": {
                "description": "C ↪ [C^op, Set]",
                "maps_to": "MAP + DUALIZE (contravariant embedding)",
                "confidence": "MODERATE",
            },
            "opposite_category": {
                "description": "C^op — reversing all arrows",
                "maps_to": "DUALIZE",
                "confidence": "HIGH",
            },
        },
        "unmapped_operations": ["adjunction — requires further analysis"],
        "verdict": "ADJUNCTION is the critical test case. See candidate analysis below.",
    }

    # --- Goguen-Burstall (1984) Institutions ---
    spanning["goguen_burstall_1984"] = {
        "framework": "Institution theory — abstract model theory",
        "operations_identified": {
            "signature_morphism": {
                "description": "σ: Sig → Sig' mapping one signature to another",
                "maps_to": "MAP",
                "confidence": "HIGH",
            },
            "model_reduct": {
                "description": "Restricting a model along a signature morphism",
                "maps_to": "REDUCE",
                "confidence": "HIGH",
            },
            "sentence_translation": {
                "description": "Translating sentences along a signature morphism",
                "maps_to": "MAP",
                "confidence": "HIGH",
            },
            "satisfaction_condition": {
                "description": "M' ⊨ σ(φ) iff M'|σ ⊨ φ (the key coherence)",
                "maps_to": "This is a PROPERTY, not an operation — it's the invariant that MAP and REDUCE must satisfy together.",
                "confidence": "HIGH",
            },
            "institution_morphism": {
                "description": "Map between institutions preserving satisfaction",
                "maps_to": "MAP (at the level of institutions)",
                "confidence": "HIGH",
            },
            "colimit_of_theories": {
                "description": "Combining theories via colimit in the theory category",
                "maps_to": "COMPOSE + LIMIT (colimit = dual limit)",
                "confidence": "MODERATE",
            },
        },
        "unmapped_operations": [],
        "verdict": "All institution operations map cleanly. No 12th needed from this framework.",
    }

    # --- Shiebler et al. (2021) Category Theory for Deep Learning ---
    spanning["shiebler_2021"] = {
        "framework": "Categorical abstractions for deep learning architectures",
        "operations_identified": {
            "parametric_map": {
                "description": "Neural network layer: f_θ: X → Y",
                "maps_to": "MAP (parameterized functor)",
                "confidence": "HIGH",
            },
            "composition_of_layers": {
                "description": "Sequential layer composition f_n ∘ ... ∘ f_1",
                "maps_to": "COMPOSE",
                "confidence": "HIGH",
            },
            "backpropagation": {
                "description": "Reverse-mode autodiff — computing gradients",
                "maps_to": "DUALIZE + LINEARIZE (reverse the computation graph + take derivatives)",
                "confidence": "MODERATE",
            },
            "dropout_stochastic_depth": {
                "description": "Stochastic regularization",
                "maps_to": "STOCHASTICIZE",
                "confidence": "HIGH",
            },
            "pooling": {
                "description": "Spatial/temporal reduction",
                "maps_to": "REDUCE",
                "confidence": "HIGH",
            },
            "embedding_layers": {
                "description": "Mapping discrete tokens to continuous vectors",
                "maps_to": "EXTEND + LINEARIZE (embed into vector space)",
                "confidence": "MODERATE",
            },
            "attention_mechanism": {
                "description": "Softmax(QK^T/√d)V",
                "maps_to": "MAP(query-key) + STOCHASTICIZE(softmax) + REDUCE(weighted sum)",
                "confidence": "MODERATE",
            },
            "skip_connections": {
                "description": "Residual connections f(x) + x",
                "maps_to": "COMPOSE + EXTEND (identity path parallel to transform path)",
                "confidence": "MODERATE",
            },
            "weight_sharing_equivariance": {
                "description": "CNNs share weights = translation equivariance",
                "maps_to": "SYMMETRIZE (impose translation symmetry)",
                "confidence": "HIGH",
            },
        },
        "unmapped_operations": [],
        "verdict": "All deep learning operations map to the 11 primitives. Attention decomposes into 3.",
    }

    return spanning


# ============================================================
# CHECK 2b: Candidate 12th Primitives
# ============================================================

def analyze_candidates():
    """Analyze whether any candidate 12th primitive is truly independent."""

    candidates = {}

    # --- ADJOIN (Adjunction) ---
    # F ⊣ G means: Hom(FA, B) ≅ Hom(A, GB) naturally.
    # This is THE central concept of category theory (per Mac Lane).
    # Can it decompose into our primitives?
    #
    # An adjunction consists of:
    #   - Two functors F and G (MAP + MAP)
    #   - A natural isomorphism (MAP between Hom-sets)
    #   - Unit η: Id ⇒ GF and counit ε: FG ⇒ Id
    #
    # The UNIT η is: embed A into GF(A). This is EXTEND-like (A ↪ GFA).
    # The COUNIT ε is: project FG(B) onto B. This is REDUCE-like (FGB → B).
    # The adjunction IS the pair (η, ε) satisfying triangle identities.
    #
    # So ADJOIN = MAP(F) + MAP(G) + EXTEND(unit) + REDUCE(counit) + COMPOSE(triangle identities)?
    # That's 4 primitives. But the RELATIONSHIP between them (the natural isomorphism)
    # is itself a structure. Is this relationship captured by existing primitives?
    #
    # The natural isomorphism Hom(FA,B) ≅ Hom(A,GB) is a MAP (bijection between sets).
    # The naturality is a COMPOSE condition.
    #
    # So: ADJOIN decomposes into MAP + MAP + EXTEND + REDUCE + COMPOSE.
    # It's a PATTERN of primitive application, not a new primitive.
    candidates["ADJOIN"] = {
        "description": "Adjunction F ⊣ G (left/right adjoint pair)",
        "attempted_decomposition": "MAP(F) + MAP(G) + EXTEND(unit η) + REDUCE(counit ε) + COMPOSE(triangle identities)",
        "analysis": (
            "An adjunction is a *structured relationship* between existing operations, "
            "not a new operation. The unit is EXTEND (embedding), the counit is REDUCE "
            "(projection), the functors are MAP, and the coherence is COMPOSE. "
            "Adjunctions are the most important PATTERN in category theory but decompose "
            "into existing primitives. No new primitive needed."
        ),
        "verdict": "DECOMPOSES — not a 12th primitive",
        "confidence": "HIGH",
    }

    # --- QUOTIENT ---
    candidates["QUOTIENT"] = {
        "description": "Formation of equivalence classes X/~",
        "attempted_decomposition": "REDUCE (coequalizer/quotient is a colimit, dual of LIMIT, or a surjective morphism application)",
        "analysis": (
            "QUOTIENT is the prototypical example of REDUCE. In category theory, "
            "quotients are coequalizers, which are colimits. REDUCE already covers "
            "surjective morphisms and quotient constructions. "
            "If SYMMETRIZE is judged redundant (as above), QUOTIENT is even more clearly "
            "just REDUCE — it's SYMMETRIZE without the group action."
        ),
        "verdict": "DECOMPOSES — equals REDUCE",
        "confidence": "HIGH",
    }

    # --- PULLBACK/PUSHOUT ---
    candidates["PULLBACK_PUSHOUT"] = {
        "description": "Fibered products (pullbacks) and fibered coproducts (pushouts)",
        "attempted_decomposition": "COMPOSE + LIMIT (pullback = limit of a cospan diagram)",
        "analysis": (
            "Pullbacks are limits of cospan diagrams: A →f C ←g B. "
            "They decompose as: COMPOSE the morphisms into a diagram, then LIMIT. "
            "Pushouts are the dual: DUALIZE + (COMPOSE + LIMIT). "
            "Both are instances of (co)limits, already covered by LIMIT + DUALIZE."
        ),
        "verdict": "DECOMPOSES — COMPOSE + LIMIT (or DUALIZE thereof)",
        "confidence": "HIGH",
    }

    # --- FORGET (Forgetful functor) ---
    candidates["FORGET"] = {
        "description": "Forgetful functor U: structured → less-structured",
        "attempted_decomposition": "MAP (it IS a functor) that happens to REDUCE structure",
        "analysis": (
            "A forgetful functor is a functor (MAP) that loses information (REDUCE). "
            "It's the paradigmatic example of the MAP/REDUCE overlap noted in the "
            "REDUCE independence analysis. FORGET = MAP with a non-injective-on-structure "
            "character. Not a new primitive."
        ),
        "verdict": "DECOMPOSES — MAP + REDUCE",
        "confidence": "HIGH",
    }

    # --- NEW CANDIDATE: ITERATE/RECURSE ---
    # Iteration/recursion is fundamental in computation (μ-recursion, fixed points).
    # Does it decompose?
    # ITERATE(f) = f ∘ f ∘ f ∘ ... = COMPOSE^ω(f) + LIMIT(convergence).
    # Fixed point: ITERATE + LIMIT. So it decomposes.
    candidates["ITERATE"] = {
        "description": "Iteration/recursion/fixed-point computation",
        "attempted_decomposition": "COMPOSE(repeated) + LIMIT(convergence to fixed point)",
        "analysis": (
            "Iteration is repeated COMPOSE: f^n = f ∘ f ∘ ... ∘ f (n times). "
            "Fixed points are LIMIT of the iteration sequence: lim f^n(x₀). "
            "Lawvere's Fixed Point Theorem shows this is a consequence of "
            "COMPOSE + LIMIT. Not a new primitive."
        ),
        "verdict": "DECOMPOSES — COMPOSE + LIMIT",
        "confidence": "HIGH",
    }

    # --- NEW CANDIDATE: ENRICH ---
    # Enriched category theory: replacing Hom-SETS with Hom-OBJECTS in a monoidal category V.
    # This is replacing the base of enrichment.
    # Does it decompose? MAP changes the Hom-objects, EXTEND adds monoidal structure...
    # Actually: enrichment is EXTEND (add richer structure to morphism spaces) +
    #           MAP (ensure composition still works in the new setting).
    candidates["ENRICH"] = {
        "description": "Enrichment — replacing Hom-sets with Hom-objects in V",
        "attempted_decomposition": "EXTEND(Hom-sets to V-objects) + MAP(composition in V)",
        "analysis": (
            "Enrichment replaces the 'base' of a category. This is EXTEND (the Hom-objects "
            "gain richer structure) combined with MAP (functorial coherence of composition "
            "in the new base). Not a genuinely new operation — it's EXTEND applied to "
            "the morphism spaces rather than the object spaces."
        ),
        "verdict": "DECOMPOSES — EXTEND + MAP",
        "confidence": "MODERATE",
    }

    return candidates


# ============================================================
# SYNTHESIS
# ============================================================

def synthesize(independence, spanning, candidates):
    """Combine all analyses into a final verdict."""

    # Count redundant primitives
    redundant = [k for k, v in independence.items() if v["verdict"] == "REDUNDANT"]
    weak = [k for k, v in independence.items() if v["verdict"] == "WEAK_INDEPENDENT"]
    independent = [k for k, v in independence.items() if v["verdict"] == "independent"]

    # Check for missing primitives from spanning analysis
    all_unmapped = []
    for framework, data in spanning.items():
        if isinstance(data.get("unmapped_operations"), list):
            all_unmapped.extend(data["unmapped_operations"])

    # Check candidates
    new_primitives_needed = [
        k for k, v in candidates.items()
        if "not" not in v["verdict"].lower() and "DECOMPOSES" not in v["verdict"]
    ]

    # Final verdict
    if redundant:
        result = "FAIL"
        explanation = (
            f"The claim of EXACTLY 11 primitives fails. "
            f"Redundant primitives found: {redundant}. "
            f"After removing redundancies, the count drops to {11 - len(redundant)}. "
        )
    elif new_primitives_needed:
        result = "FAIL"
        explanation = (
            f"The claim of EXACTLY 11 primitives fails. "
            f"Additional primitives needed: {new_primitives_needed}. "
        )
    else:
        result = "PASS"
        explanation = "All 11 primitives are independent and span the known frameworks."

    # Adjust for weak independence
    if weak and result == "PASS":
        result = "INCONCLUSIVE"
        explanation += f" However, {weak} have weak independence arguments."

    # Determine confidence
    if result == "FAIL" and all(independence[r]["confidence"] == "HIGH" for r in redundant):
        confidence = "HIGH"
    elif result == "FAIL":
        confidence = "MODERATE"
    elif result == "PASS":
        confidence = "MODERATE"  # Can't be HIGH without formal proofs
    else:
        confidence = "LOW"

    return {
        "result": result,
        "confidence": confidence,
        "explanation": explanation,
        "independent_primitives": independent,
        "weak_primitives": weak,
        "redundant_primitives": redundant,
        "missing_primitives": new_primitives_needed,
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ALETHEIA — FALSIFICATION TEST 15")
    print("CLAIM: Mathematics decomposes into exactly 11 structural primitives")
    print("=" * 70)

    # CHECK 1
    print("\n" + "=" * 70)
    print("CHECK 1: INDEPENDENCE ANALYSIS")
    print("=" * 70)
    independence = analyze_independence()
    for name, analysis in independence.items():
        verdict = analysis["verdict"]
        conf = analysis["confidence"]
        marker = "  [OK]" if verdict == "independent" else " [!!!]" if verdict == "REDUNDANT" else "  [??]"
        print(f"{marker} {name:20s} -> {verdict:20s} (confidence: {conf})")
        if verdict == "REDUNDANT":
            print(f"       DECOMPOSITION: {analysis.get('decomposition', 'N/A')}")

    # CHECK 2
    print("\n" + "=" * 70)
    print("CHECK 2: SPANNING ANALYSIS")
    print("=" * 70)
    spanning = analyze_spanning()
    for framework, data in spanning.items():
        print(f"\n--- {framework} ---")
        print(f"  Verdict: {data['verdict']}")
        if data.get("unmapped_operations"):
            print(f"  UNMAPPED: {data['unmapped_operations']}")

    # CANDIDATE 12th PRIMITIVES
    print("\n" + "=" * 70)
    print("CANDIDATE 12th PRIMITIVES")
    print("=" * 70)
    candidates = analyze_candidates()
    for name, analysis in candidates.items():
        print(f"  {name:20s} -> {analysis['verdict']}")

    # SYNTHESIS
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)
    synthesis = synthesize(independence, spanning, candidates)
    print(f"\n  RESULT:     {synthesis['result']}")
    print(f"  CONFIDENCE: {synthesis['confidence']}")
    print(f"\n  {synthesis['explanation']}")
    if synthesis['redundant_primitives']:
        print(f"\n  REDUNDANT:  {synthesis['redundant_primitives']}")
    if synthesis['weak_primitives']:
        print(f"  WEAK:       {synthesis['weak_primitives']}")
    print(f"  INDEPENDENT: {synthesis['independent_primitives']}")

    # Build output JSON
    output = {
        "test": 15,
        "paper": "11 Structural Primitives (Noesis v2 transformation basis)",
        "claim": "Mathematics decomposes into exactly 11 structural transformation primitives, no more and no fewer",
        "result": synthesis["result"],
        "confidence": synthesis["confidence"],
        "independence_analysis": {
            name: {
                "verdict": data["verdict"],
                "confidence": data["confidence"],
                "attempted_decomposition": data["attempted_decomposition"],
                "analysis_summary": data["analysis"][:200] + "..." if len(data["analysis"]) > 200 else data["analysis"],
            }
            for name, data in independence.items()
        },
        "redundant_primitives": [
            {
                "name": name,
                "decomposition": independence[name].get("decomposition", "N/A"),
                "confidence": independence[name]["confidence"],
            }
            for name in synthesis["redundant_primitives"]
        ],
        "weak_independence": [
            {
                "name": name,
                "concern": independence[name].get("concern", "N/A"),
            }
            for name in synthesis["weak_primitives"]
        ],
        "spanning_analysis": {
            framework: {
                "operations_mapped": len(data["operations_identified"]),
                "unmapped": data.get("unmapped_operations", []),
                "verdict": data["verdict"],
            }
            for framework, data in spanning.items()
        },
        "candidate_12th_primitives": {
            name: {
                "verdict": data["verdict"],
                "confidence": data["confidence"],
            }
            for name, data in candidates.items()
        },
        "missing_primitives": synthesis["missing_primitives"],
        "revised_primitive_count": 11 - len(synthesis["redundant_primitives"]),
        "revised_primitive_list": [
            name for name in PRIMITIVES.keys()
            if name not in synthesis["redundant_primitives"]
        ],
        "implications_for_other_papers": (
            "FAIL on exactly-11 claim. Two primitives are redundant: "
            "SYMMETRIZE decomposes into REDUCE(quotient_by_group_action), "
            "COMPLETE decomposes into MAP(Yoneda) + LIMIT(free_cocompletion). "
            "Additionally, REDUCE has weak independence from MAP (surjective morphisms "
            "are valid MAP inputs in standard category theory). "
            "The CORE set is 9 strongly independent primitives: "
            "COMPOSE, MAP, EXTEND, REDUCE, LIMIT, DUALIZE, LINEARIZE, STOCHASTICIZE, BREAK_SYMMETRY. "
            "REDUCE's independence from MAP depends on definitional scope — if MAP includes "
            "non-injective morphisms, the core may be 8. "
            "Noesis v2 tensor encoding should be updated to use 9 primitives. "
            "The spanning analysis is POSITIVE: no 12th primitive is needed, and all four "
            "external frameworks (Moulines, Lawvere, Goguen-Burstall, Shiebler) map cleanly "
            "to the (reduced) primitive set. The basis SPANS mathematics even if it's not "
            "exactly 11."
        ),
    }

    # Save result
    output_path = "F:/Prometheus/falsification/test_15_result.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Result saved to {output_path}")

    print("\n" + "=" * 70)
    print("TEST 15 COMPLETE")
    print("=" * 70)
