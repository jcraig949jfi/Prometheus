"""
Rhea ablation harness — test which parts of the evolved LoRA matter.

Takes the gen 100 genome and systematically zeros out subsets of the
perturbation to distinguish between:
  - Distributed ejection (every layer contributes equally)
  - Broad-shallow CMA-ES artifact (perturbation spread but only some layers matter)
  - Percolation (random subsets degrade equally)
  - Chokepoint (specific layers matter disproportionately)

Also tests component-level hypotheses:
  - gate_proj dominance: is MLP gating the primary ejection lever?
  - gate_proj sufficiency: can gate_proj alone break ejection?
"""

import json
import time
import torch
import numpy as np
from pathlib import Path
from datetime import datetime

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, LoraConfig

from genome import LORA_CONFIG, unflatten_lora_params, flatten_lora_params
from fitness import evaluate_fitness
from traps import TINY_TRAPS


SEED_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
NUM_LAYERS = 30


def load_model_and_genome(genome_path: str):
    """Load seed model with LoRA and the evolved genome."""
    print(f"Loading {SEED_MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(SEED_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        SEED_MODEL, torch_dtype=torch.float16, device_map=DEVICE,
    )
    model = get_peft_model(model, LORA_CONFIG)

    data = torch.load(genome_path, weights_only=False)
    genome_vector = data["genome_vector"]
    print(f"Loaded genome: fitness={data['fitness']:.4f}, "
          f"ES={data['ejection_suppression']:.4f}, SR={data['survival_rate']:.4f}")

    return model, tokenizer, genome_vector


def build_param_map(model) -> list[dict]:
    """
    Map each trainable parameter to its layer number and component type.
    Returns list of {name, layer, component, offset, numel} in iteration order.
    """
    param_map = []
    offset = 0
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        numel = param.numel()

        # Parse layer number and component
        parts = name.split(".")
        layer_num = None
        component = None
        for i, p in enumerate(parts):
            if p == "layers" and i + 1 < len(parts):
                layer_num = int(parts[i + 1])
            if p in ("q_proj", "v_proj", "gate_proj"):
                component = p

        param_map.append({
            "name": name,
            "layer": layer_num,
            "component": component,
            "offset": offset,
            "numel": numel,
        })
        offset += numel

    return param_map


def apply_ablation(genome_vector: np.ndarray, param_map: list[dict],
                   zero_layers: set[int] | None = None,
                   zero_components: set[str] | None = None,
                   keep_only_components: set[str] | None = None) -> np.ndarray:
    """
    Create an ablated copy of the genome vector.

    Args:
        genome_vector: original evolved genome
        zero_layers: set of layer indices to zero out (None = don't filter by layer)
        zero_components: set of component names to zero out (None = don't filter)
        keep_only_components: keep ONLY these components, zero everything else
    """
    ablated = genome_vector.copy()

    for pm in param_map:
        should_zero = False

        if zero_layers is not None and pm["layer"] in zero_layers:
            should_zero = True

        if zero_components is not None and pm["component"] in zero_components:
            should_zero = True

        if keep_only_components is not None and pm["component"] not in keep_only_components:
            should_zero = True

        if should_zero:
            ablated[pm["offset"]:pm["offset"] + pm["numel"]] = 0.0

    return ablated


def run_ablation_suite(genome_path: str, output_dir: str | None = None):
    """Run the full ablation matrix."""
    model, tokenizer, genome_vector = load_model_and_genome(genome_path)
    param_map = build_param_map(model)

    if output_dir is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"../runs/ablation_{run_id}")
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define ablation configs
    rng = np.random.RandomState(42)
    random_trials = []
    for trial in range(3):
        random_layers = set(rng.choice(NUM_LAYERS, size=10, replace=False).tolist())
        random_trials.append((f"random_10_layers_trial{trial}", random_layers))

    ablations = [
        # Baseline: no perturbation at all
        ("baseline_no_lora", {"zero_layers": set(range(NUM_LAYERS))}),

        # Full evolved genome (control)
        ("full_evolved", {}),

        # Layer range ablations
        ("zero_layers_00_09", {"zero_layers": set(range(0, 10))}),
        ("zero_layers_10_19", {"zero_layers": set(range(10, 20))}),
        ("zero_layers_20_29", {"zero_layers": set(range(20, 30))}),

        # Finer: thirds of the model
        ("zero_layers_00_04", {"zero_layers": set(range(0, 5))}),
        ("zero_layers_05_09", {"zero_layers": set(range(5, 10))}),
        ("zero_layers_10_14", {"zero_layers": set(range(10, 15))}),
        ("zero_layers_15_19", {"zero_layers": set(range(15, 20))}),
        ("zero_layers_20_24", {"zero_layers": set(range(20, 25))}),
        ("zero_layers_25_29", {"zero_layers": set(range(25, 30))}),

        # Random layer ablations (percolation test)
        *[(name, {"zero_layers": layers}) for name, layers in random_trials],

        # Component ablations
        ("zero_gate_proj", {"zero_components": {"gate_proj"}}),
        ("zero_q_proj", {"zero_components": {"q_proj"}}),
        ("zero_v_proj", {"zero_components": {"v_proj"}}),

        # Sufficiency tests
        ("keep_only_gate_proj", {"keep_only_components": {"gate_proj"}}),
        ("keep_only_q_proj", {"keep_only_components": {"q_proj"}}),
        ("keep_only_v_proj", {"keep_only_components": {"v_proj"}}),

        # Combined: gate_proj + one attention component
        ("keep_gate_and_q", {"keep_only_components": {"gate_proj", "q_proj"}}),
        ("keep_gate_and_v", {"keep_only_components": {"gate_proj", "v_proj"}}),
    ]

    results = []
    print(f"\n{'='*70}")
    print(f"ABLATION SUITE — {len(ablations)} configurations × {len(TINY_TRAPS)} traps")
    print(f"{'='*70}\n")

    for name, config in ablations:
        t0 = time.time()

        # Build ablated genome
        ablated = apply_ablation(
            genome_vector, param_map,
            zero_layers=config.get("zero_layers"),
            zero_components=config.get("zero_components"),
            keep_only_components=config.get("keep_only_components"),
        )

        # Count how many params are zeroed vs original
        nonzero_original = np.count_nonzero(genome_vector)
        nonzero_ablated = np.count_nonzero(ablated)
        pct_retained = nonzero_ablated / nonzero_original * 100 if nonzero_original > 0 else 0

        # Apply and evaluate
        unflatten_lora_params(model, ablated)
        result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
        elapsed = time.time() - t0

        entry = {
            "name": name,
            "config": {k: sorted(list(v)) if isinstance(v, set) else v
                       for k, v in config.items()},
            "fitness": result.fitness,
            "ejection_suppression": result.ejection_suppression,
            "survival_rate": result.survival_rate,
            "pct_params_retained": pct_retained,
            "time_seconds": elapsed,
        }
        results.append(entry)

        print(f"  {name:35s}  fit={result.fitness:.4f}  "
              f"ES={result.ejection_suppression:.4f}  "
              f"SR={result.survival_rate:.3f}  "
              f"retained={pct_retained:.0f}%  "
              f"({elapsed:.1f}s)")

    # Save results
    (output_dir / "ablation_results.json").write_text(
        json.dumps(results, indent=2, default=str)
    )

    # Print summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    # Find full evolved result for comparison
    full = next(r for r in results if r["name"] == "full_evolved")
    baseline = next(r for r in results if r["name"] == "baseline_no_lora")

    print(f"\nBaseline (no LoRA):  fit={baseline['fitness']:.4f}  "
          f"ES={baseline['ejection_suppression']:.4f}  SR={baseline['survival_rate']:.3f}")
    print(f"Full evolved:        fit={full['fitness']:.4f}  "
          f"ES={full['ejection_suppression']:.4f}  SR={full['survival_rate']:.3f}")

    print(f"\n--- Layer range ablations (survival rate) ---")
    for r in results:
        if r["name"].startswith("zero_layers_") and len(r["name"]) == len("zero_layers_00_09"):
            delta_sr = r["survival_rate"] - full["survival_rate"]
            print(f"  {r['name']:35s}  SR={r['survival_rate']:.3f}  (Δ={delta_sr:+.3f})")

    print(f"\n--- Random 10-layer ablations (percolation test) ---")
    random_srs = []
    for r in results:
        if r["name"].startswith("random_"):
            random_srs.append(r["survival_rate"])
            delta_sr = r["survival_rate"] - full["survival_rate"]
            print(f"  {r['name']:35s}  SR={r['survival_rate']:.3f}  (Δ={delta_sr:+.3f})")
    if random_srs:
        print(f"  Random ablation SR std: {np.std(random_srs):.4f} "
              f"(low = percolation, high = chokepoint)")

    print(f"\n--- Component ablations ---")
    for r in results:
        if r["name"].startswith("zero_") and "proj" in r["name"]:
            delta_sr = r["survival_rate"] - full["survival_rate"]
            print(f"  {r['name']:35s}  SR={r['survival_rate']:.3f}  (Δ={delta_sr:+.3f})")

    print(f"\n--- Component sufficiency ---")
    for r in results:
        if r["name"].startswith("keep_"):
            delta_sr = r["survival_rate"] - baseline["survival_rate"]
            print(f"  {r['name']:35s}  SR={r['survival_rate']:.3f}  "
                  f"(Δ from baseline={delta_sr:+.3f})")

    print(f"\nResults saved to: {output_dir / 'ablation_results.json'}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rhea ablation harness")
    parser.add_argument("--genome", type=str,
                        default="../runs/rhea_20260324_062239/genomes/best_gen0100.pt",
                        help="Path to evolved genome")
    parser.add_argument("--output", type=str, default=None,
                        help="Output directory")
    args = parser.parse_args()

    run_ablation_suite(args.genome, args.output)
