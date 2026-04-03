"""Forge Builder — generates candidate reasoning tools from primitives and amino acids.

This script has NO access to battery files, test cases, or expected answers.
It reads:
  - T1/T2/T3 primitive descriptions
  - Amino acid registry
  - Category names + one-sentence descriptions
  - Prior verdicts (pass/fail only, no test content)
  - A randomly selected science field

It writes candidate tool .py files to forge/candidates/.
"""
import sys, os, io, json, random, inspect, argparse
from pathlib import Path
from datetime import datetime

if __name__ == "__main__" and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
FORGE = Path(__file__).resolve().parent
CANDIDATES = FORGE / "candidates"

# Add paths
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))
sys.path.insert(0, str(FORGE))

from forge.builder_prompt import format_builder_prompt
from forge.amino_acids.registry import load_all, get_registry

# ── Category descriptions (Builder sees ONLY these) ────────────────────

T2_CATEGORIES = {
    "simpson_paradox": "Tests whether the tool can detect when aggregated data reverses subgroup trends",
    "causal_counterfactual": "Tests whether the tool can reason about what would have happened under different interventions",
    "conjunction_fallacy": "Tests whether the tool correctly handles joint probability vs marginal probability",
    "strategic_deception": "Tests whether the tool can model an adversary who may act against their stated intentions",
    "perspective_shift": "Tests whether the tool can reason about what different agents know",
    "temporal_scheduling": "Tests whether the tool can resolve scheduling conflicts with temporal constraints",
    "argument_strength": "Tests whether the tool can evaluate logical validity of formal arguments",
    "liar_detection": "Tests whether the tool can resolve puzzles involving agents with fixed truth-telling policies",
    "compositional_multi_step": "Tests whether the tool can chain multiple reasoning steps where each depends on the prior",
    "rate_of_change": "Tests whether the tool can compute quantities that change over time",
    "causal_confounding_hard": "Tests whether the tool can identify and adjust for confounding variables",
    "temporal_complex": "Tests whether the tool can handle complex temporal arithmetic and conversions",
}

T3_CATEGORIES = {
    "causal_temporal_fusion": "Tests reasoning that requires both causal and temporal analysis simultaneously",
    "tom_causal_deception": "Tests modeling an agent's beliefs when they have been given misleading information",
    "probabilistic_logic_conflict": "Tests reasoning under conditions where multiple valid frameworks give different answers",
    "temporal_tom_scheduling": "Tests scheduling when agents have incomplete or inconsistent information about constraints",
    "meta_causal_reasoning": "Tests reasoning about the soundness and limitations of causal arguments",
    "recursive_belief": "Tests modeling nested mental states across multiple agents",
    "self_referential_paradox": "Tests detecting and classifying statements whose truth value depends on their own content",
    "recursive_computation": "Tests iterative/recursive numerical computation to a fixed point",
    "reasoning_about_reasoning": "Tests identifying which reasoning strategy is appropriate for a problem",
    "insufficient_information_detection": "Tests recognizing when the correct response is that the problem cannot be fully solved",
    "adversarial_framing": "Tests maintaining accurate reasoning when surface presentation is misleading",
    "hidden_constraint": "Tests identifying information that is implied but not directly stated",
    "cascading_inference": "Tests multi-step deduction where each conclusion enables the next",
    "conditional_probability_chain": "Tests computing quantities through chains of dependent relationships",
    "game_theory_sequential": "Tests reasoning about optimal strategy in multi-step strategic interactions",
    "mechanism_design_incentive": "Tests reasoning about rule systems and the behaviors they encourage",
    "strategic_information_revelation": "Tests reasoning about the value of information in strategic contexts",
    "structural_analogy": "Tests recognizing when two different situations share the same underlying structure",
    "abstraction_level_shift": "Tests reasoning about the same situation at different levels of granularity",
    "domain_transfer": "Tests applying reasoning patterns across different subject areas",
}

SCIENCE_FIELDS = [
    # Physics
    "thermodynamics", "statistical_mechanics", "quantum_mechanics", "fluid_dynamics",
    "optics", "electromagnetism", "relativity", "acoustics",
    # Biology
    "evolutionary_biology", "ecology", "immunology", "genetics",
    "neuroscience", "cell_biology", "epidemiology",
    # Mathematics
    "topology", "graph_theory", "number_theory", "combinatorics",
    "measure_theory", "category_theory", "group_theory", "game_theory",
    # Computer Science
    "information_theory", "automata_theory", "complexity_theory",
    "distributed_systems", "error_correcting_codes", "cryptography",
    # Engineering
    "control_theory", "signal_processing", "feedback_systems",
    "network_engineering", "reliability_engineering",
    # Social Science
    "behavioral_economics", "decision_theory", "social_choice_theory",
    "mechanism_design", "auction_theory",
    # Chemistry
    "chemical_kinetics", "thermochemistry", "equilibrium_chemistry",
    # Earth Science
    "climate_modeling", "seismology", "hydrology",
]

FIELD_DOMAINS = {
    "physics": ["thermodynamics", "statistical_mechanics", "quantum_mechanics",
                "fluid_dynamics", "optics", "electromagnetism", "relativity", "acoustics"],
    "biology": ["evolutionary_biology", "ecology", "immunology", "genetics",
                "neuroscience", "cell_biology", "epidemiology"],
    "mathematics": ["topology", "graph_theory", "number_theory", "combinatorics",
                    "measure_theory", "category_theory", "group_theory", "game_theory"],
    "computer_science": ["information_theory", "automata_theory", "complexity_theory",
                         "distributed_systems", "error_correcting_codes", "cryptography"],
    "engineering": ["control_theory", "signal_processing", "feedback_systems",
                    "network_engineering", "reliability_engineering"],
    "social_science": ["behavioral_economics", "decision_theory", "social_choice_theory",
                       "mechanism_design", "auction_theory"],
    "chemistry": ["chemical_kinetics", "thermochemistry", "equilibrium_chemistry"],
    "earth_science": ["climate_modeling", "seismology", "hydrology"],
}


def _get_field_domain(field):
    """Get the domain of a science field."""
    for domain, fields in FIELD_DOMAINS.items():
        if field in fields:
            return domain
    return "unknown"


def pick_science_fields(tier, rng=None):
    """Pick 1 (T2) or 2 (T3, from different domains) science fields."""
    rng = rng or random
    field1 = rng.choice(SCIENCE_FIELDS)
    if tier == 2:
        return [field1]
    # T3: pick second field from a different domain
    domain1 = _get_field_domain(field1)
    other_fields = [f for f in SCIENCE_FIELDS if _get_field_domain(f) != domain1]
    field2 = rng.choice(other_fields) if other_fields else rng.choice(SCIENCE_FIELDS)
    return [field1, field2]


def get_t1_primitive_descriptions():
    """Get descriptions of T1 primitives (what the Builder is allowed to see)."""
    import forge_primitives as fp
    prims = []
    for name in dir(fp):
        obj = getattr(fp, name)
        if callable(obj) and not name.startswith('_'):
            try:
                sig = str(inspect.signature(obj))
            except (ValueError, TypeError):
                continue  # Skip builtins like defaultdict
            doc = (obj.__doc__ or "").split('\n')[0].strip()
            prims.append({"name": name, "signature": sig, "description": doc})
    return prims


def get_t2_primitive_descriptions():
    """Get descriptions of T2 primitives."""
    sys.path.insert(0, str(FORGE / "v2" / "hephaestus_t2" / "src"))
    import forge_primitives_t2 as fp2
    prims = []
    for name in dir(fp2):
        obj = getattr(fp2, name)
        if callable(obj) and not name.startswith('_') and hasattr(obj, '__module__'):
            if 'forge_primitives_t2' in (obj.__module__ or ''):
                try:
                    sig = str(inspect.signature(obj))
                except (ValueError, TypeError):
                    continue
                doc = (obj.__doc__ or "").split('\n')[0].strip()
                prims.append({"name": name, "signature": sig, "description": doc})
    return prims


def get_amino_acid_descriptions():
    """Get descriptions of all amino acids."""
    load_all()
    reg = get_registry()
    acids = []
    for acid_id, meta in reg.items():
        acids.append({
            "id": meta["id"],
            "source": meta["source"],
            "reasoning_type": meta["reasoning_type"],
            "signature": meta["signature"],
            "description": meta["description"],
        })
    return acids


def load_prior_verdicts(tier):
    """Load prior verdict files for a given tier."""
    verdicts = []
    for f in FORGE.joinpath("verdicts").glob(f"t{tier}_*_verdict.json"):
        try:
            v = json.loads(f.read_text())
            # Extract ONLY category pass/fail — no test content
            for cat, result in v.get("per_category", {}).items():
                verdicts.append({
                    "category": cat,
                    "pass": result.get("pass", False),
                    "failure_type": result.get("failure_type"),
                })
        except Exception:
            pass
    return verdicts


def load_promising_primitives(tier):
    """Load promising primitives from prior verdict files."""
    promising = []
    for f in FORGE.joinpath("verdicts").glob(f"t{tier}_*_verdict.json"):
        try:
            v = json.loads(f.read_text())
            promising.extend(v.get("promising_primitives", []))
        except Exception:
            pass
    return list(set(promising))


def generate_tool_prompt(tier, category_name, rng=None):
    """Generate the full Builder prompt for a single tool generation."""
    rng = rng or random
    categories = T2_CATEGORIES if tier == 2 else T3_CATEGORIES
    category_desc = categories.get(category_name, "Unknown category")

    t1_prims = get_t1_primitive_descriptions()
    amino_acids = get_amino_acid_descriptions()
    fields = pick_science_fields(tier, rng)
    prior = load_prior_verdicts(tier)
    promising = load_promising_primitives(tier)
    t2_prims = get_t2_primitive_descriptions() if tier == 3 else None

    prompt = format_builder_prompt(
        tier=tier,
        category_name=category_name,
        category_description=category_desc,
        t1_primitives=t1_prims,
        amino_acids=amino_acids,
        science_field=fields[0],
        science_field_2=fields[1] if len(fields) > 1 else None,
        t2_primitives=t2_prims,
        prior_verdicts=prior if prior else None,
        promising_primitives=promising if promising else None,
    )
    return prompt, fields


def save_candidate(tool_code, tool_id, tier, category, fields, trace_md=""):
    """Save a generated tool to the candidates directory."""
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    tool_path = CANDIDATES / f"{tool_id}.py"
    tool_path.write_text(tool_code, encoding='utf-8')

    # Save metadata alongside
    meta_path = CANDIDATES / f"{tool_id}_meta.json"
    meta = {
        "tool_id": tool_id,
        "tier": tier,
        "category": category,
        "science_fields": fields,
        "timestamp": datetime.now().isoformat(),
    }
    meta_path.write_text(json.dumps(meta, indent=2))

    # Save reasoning trace
    if trace_md:
        trace_path = CANDIDATES / f"{tool_id}_REASONING_TRACE.md"
        trace_path.write_text(trace_md, encoding='utf-8')

    print(f"  Saved candidate: {tool_path}")
    return str(tool_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forge Builder — generate tool prompts")
    parser.add_argument("--tier", type=int, required=True, help="Tier (2 or 3)")
    parser.add_argument("--category", type=str, help="Target category name")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--list-categories", action="store_true", help="List available categories")
    parser.add_argument("--generate-prompt", action="store_true", help="Print the Builder prompt")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    if args.list_categories:
        cats = T2_CATEGORIES if args.tier == 2 else T3_CATEGORIES
        print(f"\nT{args.tier} Categories ({len(cats)}):")
        for name, desc in cats.items():
            print(f"  {name}: {desc}")
    elif args.generate_prompt and args.category:
        prompt, fields = generate_tool_prompt(args.tier, args.category, rng)
        print(prompt)
        print(f"\n# Science fields selected: {fields}")
    else:
        print("Use --list-categories or --generate-prompt --category NAME")
