import torch
from transformer_lens import HookedTransformer
from genome import SteeringGenome
from pathlib import Path

# --- CONFIGURATION ---
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
GENOME_PATH = "results/ignis/gen_49_best.pt" # Or 'best_genome.pt'
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def run_steered_inference(model, genome, prompt, max_tokens=128):
    """Runs inference while injecting the steering vector at the specified layer."""
    
    # Define the hook function for TII (Transformer Internal Injection)
    def steering_hook(resid_pre, hook):
        # We only inject into the very last token of the prompt 
        # to set the initial 'reasoning trajectory'
        resid_pre[:, -1, :] += genome.vector.to(DEVICE)
        return resid_pre

    # Apply the hook to the specific layer discovered by CMA-ES
    hook_name = f"blocks.{genome.layer_index}.hook_resid_pre"
    
    with model.hooks(fwd_hooks=[(hook_name, steering_hook)]):
        output = model.generate(
            prompt, 
            max_new_tokens=max_tokens, 
            do_sample=False, # Greedily check the circuit's direct impact
            temperature=1.0
        )
    return output

def main():
    print(f"[*] Loading model: {MODEL_NAME}...")
    model = HookedTransformer.from_pretrained(MODEL_NAME, device=DEVICE)
    
    if not Path(GENOME_PATH).exists():
        print(f"Error: Could not find genome at {GENOME_PATH}")
        return

    print(f"[*] Loading evolved 'Fire' from {GENOME_PATH}...")
    genome = SteeringGenome.load(GENOME_PATH)
    
    test_prompts = [
        # The original '9.11 vs 9.9' logic trap
        "Is the following statement true or false: 'The number 9.11 is larger than 9.9'. Explain your reasoning.",
        
        # Generalization Test: The Weight Paradox
        "Which is heavier: a pound of gold or a pound of feathers? Think carefully."
    ]

    for i, prompt in enumerate(test_prompts):
        print(f"\n" + "="*60)
        print(f"TEST CASE {i+1}: {prompt}")
        print("="*60)

        # 1. Naive Run
        print("\n[NAIVE OUTPUT]:")
        naive_out = model.generate(prompt, max_new_tokens=128, do_sample=False)
        print(naive_out)

        # 2. Steered Run
        print("\n[STEERED OUTPUT (FIRE INJECTED)]:")
        steered_out = run_steered_inference(model, genome, prompt)
        print(steered_out)

if __name__ == "__main__":
    main()