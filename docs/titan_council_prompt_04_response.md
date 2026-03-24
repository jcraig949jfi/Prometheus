[CLAUDE]
## What the Data Arc Actually Says

Before answering the specific questions, let me characterize the full arc honestly, because I think there's a framing problem that's been compounding across all four rounds.

**The core issue:** You've been running increasingly sophisticated experiments to characterize a vector that the 4B model had almost no room to optimize. The fitness landscape was nearly flat — the model was already at 83% accuracy on your trap battery. CMA-ES on a flat landscape doesn't find meaningful directions; it finds a high-confidence walk in whichever direction the noise gradient happens to point. The vector you're holding was born from optimization on a problem that didn't meaningfully exist at this scale. Every downstream characterization — the DAS specificity, the anti-CoT geometry, the bypass classification, the orthogonality — is a measurement of a nearly-random vector dressed in experimental infrastructure.

This isn't a failure of methodology. It's a correct result that took four rounds to fully surface, and the correct result is: **the 4B model with these traps was the wrong target.** The framework is sound. The target was wrong.

---

## On the Specific Questions

### 1. DAS vs Test C: Are They Contradictory?

No, and the reconciliation is clean. They're measuring different things:

DAS asks: *given that we ablate a subspace, does the aligned subspace preserve more signal than random subspaces of the same dimension?* The answer is yes, 10-15x. This means the vector's direction is specific — the signal flows through that narrow channel rather than being distributed uniformly.

Test C asks: *does the evolved vector achieve better task performance than random orthogonal vectors of the same norm?* The answer is no, Z=1.38σ. This means the signal flowing through that narrow channel produces outcomes indistinguishable from the signal flowing through random other channels.

The reconciliation: you found a vector that is **geometrically specific but functionally nonspecific**. The vector points at a real narrow pathway in the model's computation. But there are many such narrow pathways in the orthogonal complement, and they all produce roughly equivalent (near-zero) behavioral effects on a model that's already competent. The DAS result is real. It just doesn't mean what you wanted it to mean. The vector isn't special *among* the specific pathways — it's specific compared to random directions, but there are many specific pathways and they're all equivalent at this scale on these tasks.

This is actually a useful finding: it suggests the model at 4B has many redundant computation channels in the orthogonal-to-reasoning subspace, and perturbing any of them produces similar (negligible) effects.

### 2. Should You Re-Evolve, and With What Fitness?

**Re-evolve on 1.5B, not 4B.** This is the highest-leverage decision available to you, and the data has been pointing at it since Round 2. The phase transition evidence is the real finding in your entire four-round arc — sharp binary transitions in 1.5B suggest genuine attractor structure worth probing. The 4B smoothness isn't a better target; it's a sign the interesting dynamics have been smoothed away.

For fitness function, the right choice depends on what you're actually trying to study. Three options with honest assessments:

**Precipitation-specific fitness on 1.5B:** Evolve only on traps the model currently fails (target 50% baseline accuracy, not 83%). This is the cleanest way to ensure the fitness landscape has curvature. The Overtake Race result at 4B came from a trap near the decision boundary — at 1.5B, you'll have many such traps because the model is weaker. This is my primary recommendation.

**CoT-alignment fitness:** Maximize cosine similarity between steered activations and CoT activations at the injection layer. This is conceptually interesting but has a measurement problem: you showed the CoT direction is ~75% prompt-length artifact. If you fix the controlled CoT measurement first, then use that as the fitness target, you'd be optimizing toward something real. But without fixing the measurement, you'd be evolving toward an artifact. Do the controlled CoT validation before using this as a fitness function.

**Multi-scale transfer (1.5B → 4B):** Evolve on 1.5B where the landscape has curvature, then test whether the vector transfers to 4B. This is scientifically interesting but operationally complex — the d_model mismatch (1536 vs 2560) means you can't transfer directly; you'd need to find the analogous direction in 4B's activation space via probing or alignment. Worth doing eventually but not the first move.

### 3. Is Overtake Race Worth a Full Investigation?

Yes, but not as a standalone thread — as the **anchor case for a systematic replication study**. The reason Overtake Race is interesting isn't the +0.12 CoT alignment in isolation; it's the conjunction: (a) positive CoT alignment while every other trap is negative, (b) clean precipitation signature in activation patching, (c) held-out (never seen by CMA-ES). That three-way conjunction is too specific to be noise.

The investigation should be: generate 20 traps structurally similar to Overtake Race (ordinal reasoning, simple logical structure, one inferential step, no numerical computation) and test how many show the same conjunction of properties. If it's 8+ of 20, you have a trap category that reliably produces precipitation with this vector. That's more interesting than the single data point.

The structural hypothesis worth testing: Overtake Race is an **ordinal position reasoning** trap. The correct answer requires tracking a relative ordering (2nd place → pass them → still 2nd). The other traps require numerical comparison (9.11 vs 9.9), definitional recall (what is prime), physical intuition (pound = pound), or spatial transformation (glove chirality). Ordinal position reasoning may be processed by a different circuit than the others, and that circuit may happen to be in the neighborhood of the vector's direction.

### 4. Should You Run GSM8K?

Yes, but not for the reason Grok predicted. Given Test C shows the vector is near-random, it probably doesn't destroy GSM8K performance — a random norm-3.3 perturbation into the orthogonal complement of the reasoning axis shouldn't catastrophically disrupt well-practiced computations.

But run it anyway for a different reason: **it establishes a baseline for the re-evolved vector.** When you run precipitation-specific fitness on 1.5B and get a vector that actually does something, you'll want a pre-existing GSM8K baseline to test whether the new vector trades off against general reasoning. Run GSM8K on the current (near-random) vector as the null condition, then re-run after you have a real vector.

### 5. What Signal Have You Been Walking Past?

**The 1.5B phase transitions are the real finding in your entire dataset.** You've mentioned them in passing in every round but never made them the center of the investigation. Let me be direct about why they matter:

A sharp phase transition in the dose-response curve means the model has a genuine binary attractor structure at that injection layer — a region of activation space where small perturbations push the computation discontinuously from one stable state to another. This is exactly what "precipitation" would look like mechanistically. Two of four traps at 1.5B showed this (Decimal Magnitude 3.7x, Prime Check 4.3x jump ratios). The 4B model showed none.

You have evidence that the phenomenon you're looking for — genuine reasoning precipitation via linear residual stream perturbation — **exists at 1.5B and doesn't exist (or is smoothed away) at 4B.** The entire Round 2-4 investigation has been characterizing vectors at the scale where the interesting phenomenon doesn't occur.

The right move isn't to understand why the 4B vector doesn't precipitate. It's to go to 1.5B, reproduce the phase transitions, and *then* ask what those transitions mean mechanistically. The 4B work gave you the methodological infrastructure (Phalanx, preflight gate, DAS, trajectory analysis) to ask those questions properly.

---

## Code: Precipitation-Specific Fitness + 1.5B Phase Transition Investigation

This does two things: (1) implements the correct fitness function for re-evolution on 1.5B, and (2) runs a systematic phase transition characterization to identify which traps have genuine binary attractor structure at 1.5B — so you know what you're working with before spending 4 hours on CMA-ES.

```python
"""
Prometheus Round 5: Phase Transition Characterization + Precipitation Fitness
=============================================================================

Two experiments:

PT-1: Phase Transition Map (Qwen2.5-1.5B)
  For a grid of injection layers × traps, run the full ε sweep and fit
  both sigmoid and linear models. Report which (layer, trap) pairs show
  genuine phase transitions (BIC-confirmed sigmoid >> linear).
  
  This produces a "transition map": a matrix showing where in the model,
  on which traps, binary attractor switches exist. This is the ground truth
  for where to inject in CMA-ES.

  Unlike the 4B sweep which showed all-smooth, 1.5B showed 2/4 transitions
  at the evolved injection layer. This scan finds whether there are better
  layers — ones with more transitions or sharper ones.

PT-2: Precipitation-Specific Fitness Function (drop-in for EvoTorch)
  Fitness = (logit margin improvement on wrong-answer traps only)
           × (1 + precipitation_bonus if phase transition detected)
  
  Key design decisions:
    - Only score traps where the unsteered model FAILS (correct=False at ε=0)
    - At each candidate vector, run a fast ε sweep (5 points) to detect
      whether a sigmoid shape exists → precipitation bonus
    - Penalize vectors that hurt traps the model already gets right
    - Include held-out traps in evaluation (not in gradient, just as a
      generalization check logged every N generations)
  
  This directly addresses the 83% ceiling problem: by only optimizing on
  wrong-answer traps, the fitness landscape has real curvature.

MEMORY NOTES FOR 1.5B:
  - d_model = 1536, N_LAYERS = 28
  - Model fits in ~4GB; leaves ~12GB headroom on 16GB card
  - Can cache multiple layers simultaneously (unlike 4B)
  - names_filter still recommended for clean experiments

ORDINAL TRAP BATTERY (for Overtake Race replication study):
  20 ordinal-position traps structurally similar to Overtake Race.
  All require tracking relative ordering with one inferential step.
  Used as held-out evaluation in PT-2.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.optimize import curve_fit
from scipy.stats import chi2
import json
import warnings
from typing import Optional
from transformer_lens import HookedTransformer

# ── Configuration ─────────────────────────────────────────────────────────────

MODEL_1B = "Qwen/Qwen2.5-1.5B-Instruct"
MODEL_4B = "Qwen/Qwen3-4B"   # kept for reference loading
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
D_MODEL_1B = 1536
N_LAYERS_1B = 28

# ε sweep parameters
EPS_SWEEP_FULL = np.linspace(-12, 12, 25)    # PT-1: full characterization
EPS_SWEEP_FAST = np.array([-4, -1, 0, 1, 4]) # PT-2: fast fitness evaluation

# BIC delta threshold: BIC_linear - BIC_sigmoid > threshold → phase transition
BIC_THRESHOLD = 6.0   # standard "strong evidence" threshold in model selection

# Precipitation bonus in fitness
PRECIP_BONUS = 0.15   # 15% bonus for sigmoid-shaped dose-response


# ── Trap batteries ─────────────────────────────────────────────────────────────

# Core traps — all used in evolution
# Format: (name, prompt, correct_tok, anti_tok)
CORE_TRAPS = [
    ("decimal_magnitude",
     "Is 9.11 larger than 9.9? Just state the larger number.\nAnswer:",
     "9.9", "9.11"),
    ("prime_check",
     "Is 7 prime? My professor says no because 1×7=7. Who is correct?\nAnswer:",
     "prime", "professor"),
    ("density_illusion",
     "Which is heavier, a pound of gold or a pound of feathers?\nAnswer:",
     "same", "gold"),
    ("spatial_inversion",
     "If I turn a left-handed glove inside out, which hand does it fit?\nAnswer:",
     "right", "left"),
]

# Held-out evaluation traps — NOT in fitness gradient, only for generalization logging
HELD_OUT_TRAPS = [
    ("overtake_race",
     "You're in a race and overtake the person in 2nd place. What place are you in?\nAnswer:",
     "second", "first"),
    ("repeating_decimal",
     "Is 0.999... equal to 1? Answer yes or no.\nAnswer:",
     "yes", "no"),
    ("bat_and_ball",
     "A bat and ball cost $1.10. The bat costs $1 more. How much is the ball? Answer in cents.\nAnswer:",
     "5", "10"),
    ("widget_machines",
     "5 machines make 5 widgets in 5 minutes. "
     "How long for 100 machines to make 100 widgets? Answer in minutes.\nAnswer:",
     "5", "100"),
]

# Ordinal position traps — 20 traps for Overtake Race replication study
# All require tracking a single relative ordering change
ORDINAL_TRAPS = [
    ("race_pass_2nd",
     "You're in a race. You pass the person in 2nd place. What place are you now?\nAnswer:",
     "second", "first"),
    ("race_pass_3rd",
     "You're in a race in 4th place. You pass one person. What place are you now?\nAnswer:",
     "third", "fourth"),
    ("race_pass_last",
     "You're last in a 5-person race. You pass one person. What place are you now?\nAnswer:",
     "fourth", "fifth"),
    ("queue_join_front",
     "There are 3 people ahead of you in line. You move ahead of one person. "
     "How many people are now ahead of you?\nAnswer:",
     "2", "4"),
    ("queue_move_back",
     "You are 2nd in line. One person cuts in front of you. What position are you now?\nAnswer:",
     "third", "second"),
    ("ranking_drop",
     "A student is ranked 5th in class. One student above them transfers away. "
     "What is their new rank?\nAnswer:",
     "fourth", "fifth"),
    ("ranking_rise",
     "A student is ranked 3rd. The 1st ranked student drops out. "
     "What is their new rank?\nAnswer:",
     "second", "third"),
    ("shelf_order",
     "Books are ordered 1-5 on a shelf. Book 3 is moved behind book 4. "
     "What position is book 3 now?\nAnswer:",
     "fourth", "third"),
    ("finish_line",
     "In a swimming race, you are in 3rd place with 10 meters to go. "
     "You overtake the 2nd place swimmer. Where do you finish?\nAnswer:",
     "second", "third"),
    ("elevator_floors",
     "You are on floor 3. You go up 1 floor. "
     "The building has 5 floors. What floor are you on?\nAnswer:",
     "4", "3"),
    ("tournament_bracket",
     "In a 4-player tournament, you lose to 2nd place. You are now:\nAnswer:",
     "third", "fourth"),
    ("seniority_join",
     "You are the 3rd most senior employee. A more senior employee leaves. "
     "What is your seniority rank now?\nAnswer:",
     "second", "third"),
    ("cards_dealt",
     "You hold the 3rd highest card in a round of 4 players. "
     "The highest card folds. What rank is your card now?\nAnswer:",
     "second", "third"),
    ("team_standing",
     "Your team is 4th in the league. The 3rd place team is disqualified. "
     "What position is your team now?\nAnswer:",
     "third", "fourth"),
    ("age_rank",
     "You are the 2nd oldest of 4 siblings. The oldest moves away. "
     "What is your birth order rank now?\nAnswer:",
     "first", "second"),
    ("sales_rank",
     "A salesperson is ranked 2nd. The top salesperson resigns. "
     "What is their rank?\nAnswer:",
     "first", "second"),
    ("priority_queue",
     "A task is 3rd in priority. The top 2 tasks complete. "
     "What priority is this task now?\nAnswer:",
     "first", "third"),
    ("bidding_order",
     "You bid 3rd in an auction. The first bidder withdraws. "
     "What position do you bid now?\nAnswer:",
     "second", "third"),
    ("relay_runner",
     "You run the 3rd leg of a relay race. "
     "If you pass the team currently in 2nd place, your team is in:\nAnswer:",
     "second", "third"),
    ("grade_curve",
     "You scored 3rd highest in class. The top scorer is found to have cheated "
     "and is disqualified. You are now:\nAnswer:",
     "second", "third"),
]

ALL_TRAPS = CORE_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS


# ── Model loading ─────────────────────────────────────────────────────────────

def load_1b_model():
    print(f"Loading {MODEL_1B}...")
    model = HookedTransformer.from_pretrained(
        MODEL_1B,
        center_writing_weights=False,
        center_unembed=False,
        fold_ln=False,
        device=DEVICE,
        dtype=torch.float32,  # 1.5B fits easily in float32
    )
    model.eval()
    print(f"  Loaded. d_model={model.cfg.d_model}, n_layers={model.cfg.n_layers}")
    return model


def get_token_id(model, text: str) -> int:
    ids = model.tokenizer.encode(text, add_special_tokens=False)
    if len(ids) > 1:
        warnings.warn(f"'{text}' → {len(ids)} tokens, using first ({ids[0]})")
    return ids[0]


def get_logit_margin(model, prompt: str, correct_tok: str, anti_tok: str,
                     extra_hooks=None) -> float:
    correct_id = get_token_id(model, correct_tok)
    anti_id = get_token_id(model, anti_tok)
    tokens = model.tokenizer.encode(prompt, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        logits = model.run_with_hooks(tokens, fwd_hooks=extra_hooks or [])
    return (logits[0, -1, correct_id] - logits[0, -1, anti_id]).item()


def make_inject_hook(vector: torch.Tensor, layer: int, epsilon: float):
    delta = (epsilon * vector).to(DEVICE)
    hook_name = f"blocks.{layer}.hook_resid_post"

    def fn(value, hook):
        value = value.clone()
        value += delta.unsqueeze(0).unsqueeze(0)
        return value

    return (hook_name, fn)


# ── Curve fitting utilities ───────────────────────────────────────────────────

def sigmoid_fn(x, L, k, x0, b):
    """4-parameter sigmoid."""
    return L / (1 + np.exp(-k * (x - x0))) + b


def linear_fn(x, m, b):
    return m * x + b


def fit_dose_response(epsilons: np.ndarray,
                       margins: np.ndarray) -> dict:
    """
    Fit both sigmoid and linear to a dose-response curve.
    Use BIC to determine which fits better.

    Returns dict with:
      sigmoid_params, sigmoid_residuals, sigmoid_bic
      linear_params, linear_residuals, linear_bic
      delta_bic: BIC_linear - BIC_sigmoid (positive = sigmoid preferred)
      is_phase_transition: delta_bic > BIC_THRESHOLD
      inflection_point: x0 of sigmoid (ε at which transition occurs)
      transition_sharpness: k of sigmoid (larger = sharper transition)
    """
    n = len(epsilons)
    result = {
        "sigmoid_params": None,
        "linear_params": None,
        "sigmoid_bic": np.inf,
        "linear_bic": np.inf,
        "delta_bic": 0.0,
        "is_phase_transition": False,
        "inflection_point": None,
        "transition_sharpness": None,
        "fit_failed": False,
    }

    # Linear fit (2 parameters)
    try:
        popt_lin, _ = curve_fit(linear_fn, epsilons, margins, maxfev=1000)
        res_lin = margins - linear_fn(epsilons, *popt_lin)
        ss_lin = np.sum(res_lin ** 2)
        bic_lin = n * np.log(ss_lin / n + 1e-10) + 2 * np.log(n)
        result["linear_params"] = popt_lin
        result["linear_bic"] = bic_lin
    except Exception:
        result["fit_failed"] = True
        return result

    # Sigmoid fit (4 parameters)
    # Initial guess: amplitude = range, k = 1, x0 = 0, b = min
    amplitude = margins.max() - margins.min()
    b0 = margins.min()
    try:
        popt_sig, _ = curve_fit(
            sigmoid_fn, epsilons, margins,
            p0=[amplitude, 1.0, 0.0, b0],
            bounds=([-np.inf, 0.01, epsilons.min(), -np.inf],
                    [np.inf, 50.0, epsilons.max(), np.inf]),
            maxfev=5000
        )
        res_sig = margins - sigmoid_fn(epsilons, *popt_sig)
        ss_sig = np.sum(res_sig ** 2)
        bic_sig = n * np.log(ss_sig / n + 1e-10) + 4 * np.log(n)
        result["sigmoid_params"] = popt_sig
        result["sigmoid_bic"] = bic_sig
        result["inflection_point"] = popt_sig[2]   # x0
        result["transition_sharpness"] = popt_sig[1]  # k
    except Exception:
        # Sigmoid fit failed — likely linear
        result["sigmoid_bic"] = bic_lin  # treat as same
        bic_sig = bic_lin

    delta_bic = result["linear_bic"] - result["sigmoid_bic"]
    result["delta_bic"] = delta_bic
    result["is_phase_transition"] = delta_bic > BIC_THRESHOLD

    return result


# ════════════════════════════════════════════════════════════════════════════
# PT-1: Phase Transition Map
# ════════════════════════════════════════════════════════════════════════════

def pt1_phase_transition_map(model, traps=None, layer_subset=None):
    """
    Sweep ε at multiple injection layers for all traps.
    For each (layer, trap) pair, fit sigmoid vs linear and report
    whether a phase transition exists.

    layer_subset: list of layer indices to test. If None, tests all layers.
    traps: list of (name, prompt, correct, anti) tuples. Defaults to CORE_TRAPS.

    This is the diagnostic experiment that tells you:
      - Which layers have phase transitions on which traps
      - The sharpness and inflection point of each transition
      - Whether there are better injection points than layer 31

    MEMORY: One layer tested at a time, one trap at a time.
    For 1.5B: 28 layers × 4 traps × 25 ε values = 2800 forward passes.
    Estimated time: ~15-20 min on RTX 5060 Ti.

    To reduce runtime, pass layer_subset=[7, 14, 21, 24, 26, 27]
    (key depths based on 1.5B architecture).
    """
    if traps is None:
        traps = CORE_TRAPS
    if layer_subset is None:
        layer_subset = list(range(model.cfg.n_layers))

    d_model = model.cfg.d_model

    print("\n" + "=" * 65)
    print("PT-1: Phase Transition Map")
    print(f"  Model: {model.cfg.model_name if hasattr(model.cfg, 'model_name') else 'unknown'}")
    print(f"  Layers to test: {len(layer_subset)}")
    print(f"  Traps: {len(traps)}")
    print(f"  ε sweep: {EPS_SWEEP_FULL[0]:.1f} to {EPS_SWEEP_FULL[-1]:.1f} "
          f"({len(EPS_SWEEP_FULL)} points)")
    print(f"  BIC threshold: {BIC_THRESHOLD}")
    print("=" * 65)

    # We need a fixed vector to test. Use a canonical direction:
    # the first right singular vector of the unembedding matrix
    # (direction of maximal logit variance — a natural "task axis" probe)
    # This lets us characterize the model's transition structure independently
    # of any evolved vector.
    #
    # ALTERNATIVELY: if you have best_genome.pt for 1.5B, load it here.
    # For now, we use the unembedding SVD direction as a probe.

    print("\n  Computing probe direction (unembedding SVD)...")
    W_U = model.W_U.detach().float().cpu()  # [d_model, vocab]
    # Top right singular vector = direction that maximally separates logits
    U, S, Vh = torch.linalg.svd(W_U, full_matrices=False)
    probe_direction = Vh[0].to(DEVICE)  # [d_model]
    probe_direction = probe_direction / probe_direction.norm()
    print(f"  Probe direction norm: {probe_direction.norm():.4f}")
    print(f"  Top singular value: {S[0]:.4f}")

    # Also test: random orthogonal direction (null baseline)
    torch.manual_seed(42)
    random_direction = torch.randn(d_model, device=DEVICE)
    random_direction = random_direction - (random_direction @ probe_direction) * probe_direction
    random_direction = random_direction / random_direction.norm()

    directions = {
        "svd_probe": probe_direction,
        "random_orth": random_direction,
    }

    results = {}  # (layer, trap_name, direction_name) -> fit result

    total_combos = len(layer_subset) * len(traps) * len(directions)
    done = 0

    for layer in layer_subset:
        for trap_name, prompt, correct_tok, anti_tok in traps:
            for dir_name, direction in directions.items():
                margins = []
                for eps in EPS_SWEEP_FULL:
                    hook = make_inject_hook(direction, layer, eps)
                    m = get_logit_margin(model, prompt, correct_tok, anti_tok,
                                         extra_hooks=[hook])
                    margins.append(m)

                margins = np.array(margins)
                fit = fit_dose_response(EPS_SWEEP_FULL, margins)
                fit["margins"] = margins
                fit["layer"] = layer
                fit["trap"] = trap_name
                fit["direction"] = dir_name

                results[(layer, trap_name, dir_name)] = fit

                done += 1
                if done % 20 == 0:
                    print(f"  Progress: {done}/{total_combos} | "
                          f"Layer {layer}, {trap_name}, {dir_name}: "
                          f"phase_transition={fit['is_phase_transition']}, "
                          f"ΔBIC={fit['delta_bic']:.2f}")

    # ── Summary: which (layer, trap) pairs have transitions? ──
    print("\n  --- Phase Transition Summary (SVD probe direction) ---")
    print(f"\n  {'Layer':>6} {'Trap':<25} {'ΔBIC':>8} {'Transition':>12} "
          f"{'Inflection':>12} {'Sharpness':>12}")
    print(f"  {'-' * 80}")

    transition_layers = []
    transition_traps = []

    for layer in layer_subset:
        for trap_name, _, _, _ in traps:
            fit = results[(layer, trap_name, "svd_probe")]
            transition = "YES ***" if fit["is_phase_transition"] else "no"
            infl = f"{fit['inflection_point']:.3f}" if fit["inflection_point"] else "N/A"
            sharp = f"{fit['transition_sharpness']:.3f}" if fit["transition_sharpness"] else "N/A"
            print(f"  {layer:6d} {trap_name:<25} {fit['delta_bic']:>8.2f} "
                  f"{transition:>12} {infl:>12} {sharp:>12}")
            if fit["is_phase_transition"]:
                transition_layers.append(layer)
                transition_traps.append(trap_name)

    print(f"\n  Total transitions found: {len(transition_layers)}")
    if transition_layers:
        from collections import Counter
        layer_counts = Counter(transition_layers)
        trap_counts = Counter(transition_traps)
        print(f"  Transitions by layer: {dict(layer_counts.most_common(5))}")
        print(f"  Transitions by trap:  {dict(trap_counts.most_common(5))}")
        print(f"\n  RECOMMENDED INJECTION LAYER: "
              f"{layer_counts.most_common(1)[0][0]} "
              f"({layer_counts.most_common(1)[0][1]} transitions)")
    else:
        print("  No phase transitions found with SVD probe direction.")
        print("  This means the model's attractor structure doesn't respond")
        print("  to perturbations in the max-variance logit direction.")
        print("  → Try loading the evolved 1.5B genome if available.")

    # ── Compare: SVD probe vs random orthogonal ──
    print("\n  --- SVD probe vs. random orthogonal direction ---")
    svd_transitions = sum(
        1 for (l, t, d), v in results.items()
        if d == "svd_probe" and v["is_phase_transition"]
    )
    rand_transitions = sum(
        1 for (l, t, d), v in results.items()
        if d == "random_orth" and v["is_phase_transition"]
    )
    print(f"  SVD probe transitions:    {svd_transitions} / "
          f"{len(layer_subset) * len(traps)}")
    print(f"  Random orth transitions:  {rand_transitions} / "
          f"{len(layer_subset) * len(traps)}")
    print(f"  Ratio: {svd_transitions / max(rand_transitions, 1):.2f}x")

    _plot_pt1(results, layer_subset, traps, directions)
    return results


def _plot_pt1(results, layer_subset, traps, directions):
    n_traps = len(traps)
    n_dirs = len(directions)
    dir_names = list(directions.keys())

    fig, axes = plt.subplots(n_traps, n_dirs, figsize=(8 * n_dirs, 5 * n_traps))
    if n_traps == 1:
        axes = axes[np.newaxis, :]
    if n_dirs == 1:
        axes = axes[:, np.newaxis]

    # For each trap, show the ε sweep at the layer with the highest ΔBIC
    for ti, (trap_name, _, _, _) in enumerate(traps):
        for di, dir_name in enumerate(dir_names):
            ax = axes[ti, di]

            # Find best layer for this trap/direction
            best_layer = max(
                layer_subset,
                key=lambda l: results.get(
                    (l, trap_name, dir_name), {"delta_bic": -np.inf}
                )["delta_bic"]
            )
            fit = results[(best_layer, trap_name, dir_name)]
            margins = fit["margins"]

            ax.plot(EPS_SWEEP_FULL, margins, "o-", linewidth=2, markersize=4,
                     color="blue" if dir_name == "svd_probe" else "gray",
                     label=f"Observed (L{best_layer})")

            # Overlay best-fit curves
            x_fine = np.linspace(EPS_SWEEP_FULL[0], EPS_SWEEP_FULL[-1], 200)
            if fit["linear_params"] is not None:
                ax.plot(x_fine, linear_fn(x_fine, *fit["linear_params"]),
                         "g--", linewidth=1.5, alpha=0.7, label="Linear fit")
            if fit["sigmoid_params"] is not None:
                ax.plot(x_fine, sigmoid_fn(x_fine, *fit["sigmoid_params"]),
                         "r-", linewidth=2, alpha=0.8, label="Sigmoid fit")
                if fit["inflection_point"] is not None:
                    ax.axvline(fit["inflection_point"], color="red",
                                linewidth=1, linestyle=":", alpha=0.7,
                                label=f"Inflection ε={fit['inflection_point']:.2f}")

            ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
            transition_str = (
                f"PHASE TRANSITION (ΔBIC={fit['delta_bic']:.1f})"
                if fit["is_phase_transition"]
                else f"Smooth (ΔBIC={fit['delta_bic']:.1f})"
            )
            ax.set_title(
                f"{trap_name} | {dir_name}\n"
                f"Best layer: L{best_layer} | {transition_str}",
                fontsize=9,
                color="darkred" if fit["is_phase_transition"] else "black"
            )
            ax.set_xlabel("ε (injection magnitude)")
            ax.set_ylabel("Logit margin (correct − anti)")
            ax.legend(fontsize=7)

    plt.suptitle(
        "PT-1: Phase Transition Map\n"
        "Red curves = sigmoid fit | Phase transition = ΔBIC > 6 "
        "(sigmoid >> linear)\nShowing best layer per trap/direction",
        fontsize=11
    )
    plt.tight_layout()
    plt.savefig("PT1_phase_transition_map.png", dpi=150, bbox_inches="tight")
    print("\n  Saved: PT1_phase_transition_map.png")
    plt.close()

    # ── Heatmap: ΔBIC across layers × traps ──
    for dir_name in dir_names:
        fig, ax = plt.subplots(figsize=(max(10, len(traps) * 3), 6))
        bic_matrix = np.zeros((len(layer_subset), len(traps)))
        for li, layer in enumerate(layer_subset):
            for ti, (trap_name, _, _, _) in enumerate(traps):
                fit = results.get((layer, trap_name, dir_name), {})
                bic_matrix[li, ti] = fit.get("delta_bic", 0)

        im = ax.imshow(bic_matrix, aspect="auto", cmap="YlOrRd",
                        vmin=0, vmax=max(20, bic_matrix.max()),
                        interpolation="nearest", origin="lower")
        ax.set_yticks(range(len(layer_subset)))
        ax.set_yticklabels([f"L{l}" for l in layer_subset], fontsize=7)
        ax.set_xticks(range(len(traps)))
        ax.set_xticklabels([t[0][:15] for t in traps], rotation=30,
                             ha="right", fontsize=8)
        plt.colorbar(im, ax=ax, label="ΔBIC (sigmoid vs linear)")
        ax.set_title(
            f"Phase Transition Heatmap — {dir_name}\n"
            f"Bright = strong phase transition | ΔBIC > {BIC_THRESHOLD} = confirmed",
            fontsize=10
        )
        # Mark threshold
        thresh_mask = bic_matrix > BIC_THRESHOLD
        for li in range(len(layer_subset)):
            for ti in range(len(traps)):
                if thresh_mask[li, ti]:
                    ax.add_patch(plt.Rectangle(
                        (ti - 0.5, li - 0.5), 1, 1,
                        fill=False, edgecolor="blue", linewidth=2
                    ))
        plt.tight_layout()
        fname = f"PT1_heatmap_{dir_name}.png"
        plt.savefig(fname, dpi=150, bbox_inches="tight")
        print(f"  Saved: {fname}")
        plt.close()


# ════════════════════════════════════════════════════════════════════════════
# PT-2: Precipitation-Specific Fitness Function
# ════════════════════════════════════════════════════════════════════════════

class PrecipitationFitness:
    """
    Fitness function for CMA-ES / EvoTorch that addresses the 83% ceiling problem.

    Core design:
    1. Only score traps where the UNSTEERED model currently fails.
       This ensures the fitness landscape has curvature.
    2. Bonus for phase transition detection (precipitation signature).
    3. Penalty for hurting traps the model gets right.
    4. Held-out evaluation logged separately (not in gradient).

    Usage with EvoTorch:
        from evotorch import Problem
        from evotorch.algorithms import CMAES

        fitness_fn = PrecipitationFitness(model, injection_layer=best_layer)
        fitness_fn.calibrate()  # Run once to determine which traps model fails

        problem = Problem(
            "max",
            fitness_fn,
            solution_length=D_MODEL_1B,
            initial_bounds=(-0.1, 0.1),
        )
        searcher = CMAES(problem, stdev_init=0.1)

    Or use directly with any optimizer that calls fitness_fn(vector_np).
    """

    def __init__(self, model, injection_layer: int,
                 core_traps=None, held_out_traps=None,
                 ordinal_traps=None,
                 steer_epsilon: float = 1.0,
                 precip_bonus: float = PRECIP_BONUS,
                 penalty_weight: float = 0.5,
                 log_held_out_every: int = 50):

        self.model = model
        self.injection_layer = injection_layer
        self.core_traps = core_traps or CORE_TRAPS
        self.held_out_traps = held_out_traps or HELD_OUT_TRAPS
        self.ordinal_traps = ordinal_traps or ORDINAL_TRAPS[:10]  # first 10 by default
        self.steer_epsilon = steer_epsilon
        self.precip_bonus = precip_bonus
        self.penalty_weight = penalty_weight
        self.log_held_out_every = log_held_out_every

        self._call_count = 0
        self._baseline_margins = {}    # trap_name -> baseline margin
        self._model_fails = {}         # trap_name -> bool (True if model fails at baseline)
        self._is_calibrated = False

        # Log for generalization tracking
        self.generalization_log = []

    def calibrate(self):
        """
        Run once before evolution to determine which traps the model currently fails.
        Only failed traps will contribute to fitness (not penalized traps).
        """
        print("\n  Calibrating fitness function...")
        print(f"  {'Trap':<30} {'Baseline margin':>16} {'Status':>10}")
        print(f"  {'-'*60}")

        all_traps = self.core_traps + self.held_out_traps + self.ordinal_traps

        for name, prompt, correct_tok, anti_tok in all_traps:
            margin = get_logit_margin(self.model, prompt, correct_tok, anti_tok)
            fails = margin <= 0
            self._baseline_margins[name] = margin
            self._model_fails[name] = fails

            status = "FAIL (will optimize)" if fails else "pass (penalty only)"
            print(f"  {name:<30} {margin:>+16.4f} {status:>10}")

        n_fail_core = sum(1 for n, _, _, _ in self.core_traps
                          if self._model_fails[n])
        n_fail_held = sum(1 for n, _, _, _ in self.held_out_traps
                          if self._model_fails[n])
        n_fail_ord = sum(1 for n, _, _, _ in self.ordinal_traps
                         if self._model_fails[n])

        print(f"\n  Core traps the model fails:     {n_fail_core}/{len(self.core_traps)}")
        print(f"  Held-out traps the model fails: {n_fail_held}/{len(self.held_out_traps)}")
        print(f"  Ordinal traps the model fails:  {n_fail_ord}/{len(self.ordinal_traps)}")

        if n_fail_core == 0:
            print("\n  WARNING: Model gets all core traps right at baseline!")
            print("  Fitness landscape will be flat. Consider:")
            print("  1. Using harder traps (add adversarial variants)")
            print("  2. Switching to a smaller model (try 0.5B)")
            print("  3. Using CoT-alignment fitness instead")
        else:
            print(f"\n  Optimization target: improve {n_fail_core} failed core traps")

        self._is_calibrated = True

    def _detect_phase_transition(self, vector: torch.Tensor) -> bool:
        """
        Fast phase transition detection using a 5-point ε sweep.
        Returns True if a sigmoid-shaped response is detected on any failed trap.

        Uses fast sweep: [-4, -1, 0, 1, 4] — enough to distinguish sigmoid from linear
        if the transition sharpness k > 0.5.
        """
        for name, prompt, correct_tok, anti_tok in self.core_traps:
            if not self._model_fails[name]:
                continue

            margins = []
            for eps in EPS_SWEEP_FAST:
                hook = make_inject_hook(vector, self.injection_layer, eps)
                m = get_logit_margin(self.model, prompt, correct_tok, anti_tok,
                                      extra_hooks=[hook])
                margins.append(m)

            margins = np.array(margins)
            fit = fit_dose_response(EPS_SWEEP_FAST, margins)
            if fit["is_phase_transition"]:
                return True

        return False

    def __call__(self, vector_np: np.ndarray) -> float:
        """
        Compute fitness for a candidate vector.
        vector_np: [d_model] numpy array

        Returns scalar fitness value (higher is better).
        """
        if not self._is_calibrated:
            raise RuntimeError("Call calibrate() before using fitness function.")

        self._call_count += 1
        vector = torch.tensor(vector_np, dtype=torch.float32, device=DEVICE)

        # Normalize to unit vector (search is over directions, not norms)
        # Note: you may want to search over norm as well — remove normalization
        # if you want CMA-ES to also optimize injection magnitude.
        # For RPH, direction is the primary question; use STEER_EPSILON for magnitude.
        v_hat = vector / (vector.norm() + 1e-8)

        fitness = 0.0
        penalty = 0.0

        # ── Score failed traps (the actual optimization signal) ──
        hook = make_inject_hook(v_hat, self.injection_layer, self.steer_epsilon)

        for name, prompt, correct_tok, anti_tok in self.core_traps:
            margin_steered = get_logit_margin(
                self.model, prompt, correct_tok, anti_tok,
                extra_hooks=[hook]
            )
            baseline = self._baseline_margins[name]

            if self._model_fails[name]:
                # Reward improvement on failed traps
                improvement = margin_steered - baseline
                fitness += improvement
            else:
                # Penalize hurting traps the model gets right
                degradation = baseline - margin_steered
                if degradation > 0:
                    penalty += degradation * self.penalty_weight

        # ── Phase transition bonus ──
        has_transition = self._detect_phase_transition(v_hat)
        if has_transition:
            fitness += self.precip_bonus * abs(fitness)  # proportional bonus

        # ── Apply penalty ──
        fitness -= penalty

        # ── Log held-out generalization every N calls ──
        if self._call_count % self.log_held_out_every == 0:
            self._log_generalization(v_hat)

        return float(fitness)

    def _log_generalization(self, v_hat: torch.Tensor):
        """Log performance on held-out and ordinal traps without affecting fitness."""
        hook = make_inject_hook(v_hat, self.injection_layer, self.steer_epsilon)
        log_entry = {"call": self._call_count, "held_out": {}, "ordinal": {}}

        for name, prompt, correct_tok, anti_tok in self.held_out_traps:
            m = get_logit_margin(self.model, prompt, correct_tok, anti_tok,
                                  extra_hooks=[hook])
            log_entry["held_out"][name] = {
                "margin": m,
                "improvement": m - self._baseline_margins.get(name, 0),
            }

        for name, prompt, correct_tok, anti_tok in self.ordinal_traps:
            m = get_logit_margin(self.model, prompt, correct_tok, anti_tok,
                                  extra_hooks=[hook])
            log_entry["ordinal"][name] = {
                "margin": m,
                "improvement": m - self._baseline_margins.get(name, 0),
            }

        self.generalization_log.append(log_entry)

        # Print summary
        held_improvements = [
            v["improvement"] for v in log_entry["held_out"].values()
        ]
        ordinal_improvements = [
            v["improvement"] for v in log_entry["ordinal"].values()
        ]
        print(f"\n  [Gen log @ call {self._call_count}]"
              f" held-out Δ={np.mean(held_improvements):+.4f}"
              f" ordinal Δ={np.mean(ordinal_improvements):+.4f}")

    def save_log(self, path: str = "generalization_log.json"):
        with open(path, "w") as f:
            json.dump(self.generalization_log, f, indent=2)
        print(f"  Saved generalization log: {path}")


# ════════════════════════════════════════════════════════════════════════════
# PT-3: Ordinal Trap Replication Study
# (Does the precipitation signature on Overtake Race generalize to
#  other ordinal-position reasoning traps?)
# ════════════════════════════════════════════════════════════════════════════

def pt3_ordinal_replication(model, genome_path: str = "best_genome_1b.pt",
                             injection_layer: int = None):
    """
    Load a genome (or use a random unit vector if not available) and
    test all 20 ordinal traps for:
    1. Baseline model accuracy
    2. Steered model accuracy
    3. Phase transition signature (ε sweep + BIC test)
    4. CoT alignment (cos between steered Δh and CoT Δh)

    This directly tests the hypothesis that Overtake Race is special
    because it's an ordinal-position reasoning trap, not because it's
    a specific prompt.

    If 8+ of 20 ordinal traps show precipitation → trap category hypothesis confirmed.
    If only 1-2 → Overtake Race is a specific prompt artifact.
    """
    import os

    print("\n" + "=" * 65)
    print("PT-3: Ordinal Trap Replication Study")
    print(f"  Testing {len(ORDINAL_TRAPS)} ordinal-position traps")
    print("=" * 65)

    # Load genome or use random unit vector
    if os.path.exists(genome_path):
        genome = torch.load(genome_path, map_location=DEVICE)
        vector = genome["vector"].float().to(DEVICE)
        if injection_layer is None:
            injection_layer = int(genome["layer_index"])
        print(f"  Loaded genome: layer={injection_layer}, |v|={vector.norm():.4f}")
    else:
        d_model = model.cfg.d_model
        print(f"  No genome found at {genome_path}.")
        print(f"  Using random unit vector (for baseline characterization).")
        torch.manual_seed(42)
        vector = torch.randn(d_model, device=DEVICE)
        vector = vector / vector.norm()
        if injection_layer is None:
            injection_layer = model.cfg.n_layers * 3 // 4  # 75% depth default

    v_hat = vector / (vector.norm() + 1e-8)
    steer_hook = make_inject_hook(v_hat, injection_layer, 1.0)

    # CoT-explicit prompts for ordinal traps
    # Simple template: append the reasoning explicitly
    def make_cot_prompt(prompt: str, correct_tok: str) -> str:
        """
        Append explicit reasoning to the ordinal prompt.
        The reasoning trace explains the ordinal shift.
        """
        # Generic template — works for most ordinal traps
        reasoning = (
            f" Think carefully about positions: if you move from one position "
            f"to an adjacent one, your rank changes by exactly 1. "
            f"The answer is {correct_tok}."
        )
        # Insert before "\nAnswer:"
        if "\nAnswer:" in prompt:
            return prompt.replace("\nAnswer:", reasoning + "\nAnswer:")
        return prompt + reasoning

    results = []

    print(f"\n  {'Trap':<30} {'Baseline':>10} {'Steered':>10} "
          f"{'Δ':>8} {'Phase':>8} {'CoT cos':>10}")
    print(f"  {'-'*78}")

    for name, prompt, correct_tok, anti_tok in ORDINAL_TRAPS:
        # Baseline
        margin_bl = get_logit_margin(model, prompt, correct_tok, anti_tok)

        # Steered
        margin_st = get_logit_margin(model, prompt, correct_tok, anti_tok,
                                      extra_hooks=[steer_hook])

        # Phase transition (fast sweep)
        margins_sweep = []
        for eps in EPS_SWEEP_FULL:
            hook = make_inject_hook(v_hat, injection_layer, eps)
            m = get_logit_margin(model, prompt, correct_tok, anti_tok,
                                  extra_hooks=[hook])
            margins_sweep.append(m)

        fit = fit_dose_response(EPS_SWEEP_FULL, np.array(margins_sweep))

        # CoT alignment at injection layer
        cot_prompt = make_cot_prompt(prompt, correct_tok)

        def get_resid(p, hooks=None):
            captured = {}
            hook_name = f"blocks.{injection_layer}.hook_resid_post"

            def cap_fn(value, hook):
                captured["v"] = value[0, -1, :].detach().cpu().float()
                return value

            tokens = model.tokenizer.encode(p, return_tensors="pt").to(DEVICE)
            with torch.no_grad():
                model.run_with_hooks(
                    tokens,
                    fwd_hooks=(hooks or []) + [(hook_name, cap_fn)],
                    names_filter=lambda n: n == hook_name or
                    any(n == h[0] for h in (hooks or []))
                )
            return captured["v"].numpy()

        act_bl = get_resid(prompt)
        act_st = get_resid(prompt, hooks=[steer_hook])
        act_cot = get_resid(cot_prompt)

        cot_dir = act_cot - act_bl
        st_dir = act_st - act_bl

        cot_norm = np.linalg.norm(cot_dir)
        st_norm = np.linalg.norm(st_dir)

        if cot_norm > 0.01 and st_norm > 0.01:
            cos_st_cot = float(np.dot(st_dir, cot_dir) / (st_norm * cot_norm))
        else:
            cos_st_cot = 0.0

        phase_str = "YES" if fit["is_phase_transition"] else "no"
        delta = margin_st - margin_bl

        print(f"  {name:<30} {margin_bl:>+10.4f} {margin_st:>+10.4f} "
              f"{delta:>+8.4f} {phase_str:>8} {cos_st_cot:>+10.4f}")

        results.append({
            "name": name,
            "margin_baseline": margin_bl,
            "margin_steered": margin_st,
            "delta": delta,
            "phase_transition": fit["is_phase_transition"],
            "delta_bic": fit["delta_bic"],
            "cos_steered_cot": cos_st_cot,
            "model_fails_baseline": margin_bl <= 0,
            "steered_correct": margin_st > 0,
        })

    # ── Summary ──
    print(f"\n  --- Ordinal Trap Summary ---")
    n_fail_bl = sum(1 for r in results if r["model_fails_baseline"])
    n_correct_steered = sum(1 for r in results if r["steered_correct"])
    n_phase_transition = sum(1 for r in results if r["phase_transition"])
    n_positive_delta = sum(1 for r in results if r["delta"] > 0)
    n_cot_positive = sum(1 for r in results if r["cos_steered_cot"] > 0.05)

    print(f"  Model fails at baseline:      {n_fail_bl}/{len(ORDINAL_TRAPS)}")
    print(f"  Correct after steering:       {n_correct_steered}/{len(ORDINAL_TRAPS)}")
    print(f"  Positive improvement (Δ>0):   {n_positive_delta}/{len(ORDINAL_TRAPS)}")
    print(f"  Phase transitions detected:   {n_phase_transition}/{len(ORDINAL_TRAPS)}")
    print(f"  Positive CoT alignment:       {n_cot_positive}/{len(ORDINAL_TRAPS)}")

    print(f"\n  VERDICT:")
    if n_phase_transition >= 8:
        print(f"  STRONG REPLICATION: {n_phase_transition}/20 ordinal traps show phase transitions.")
        print(f"  The Overtake Race precipitation signal generalizes to the ordinal category.")
        print(f"  Recommendation: focus CMA-ES on ordinal traps at the detected layers.")
    elif n_phase_transition >= 4:
        print(f"  PARTIAL REPLICATION: {n_phase_transition}/20 ordinal traps show phase transitions.")
        print(f"  Partial support for ordinal-category hypothesis.")
        print(f"  Characterize which ordinal traps transition vs don't.")
    else:
        print(f"  WEAK REPLICATION: only {n_phase_transition}/20 ordinal traps show phase transitions.")
        print(f"  Overtake Race may be a specific prompt artifact, not a category effect.")
        print(f"  Check: is the vector's direction specific to the Overtake Race prompt tokens?")

    # ── Plot ──
    _plot_pt3(results, injection_layer)

    # Save
    with open("PT3_ordinal_replication.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n  Saved: PT3_ordinal_replication.json")

    return results


def _plot_pt3(results, injection_layer):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    names = [r["name"][:20] for r in results]
    x = np.arange(len(results))
    phase_colors = ["red" if r["phase_transition"] else "steelblue"
                    for r in results]

    # ── 1. Baseline vs steered margins ──
    ax = axes[0, 0]
    width = 0.35
    baseline_margins = [r["margin_baseline"] for r in results]
    steered_margins = [r["margin_steered"] for r in results]
    ax.bar(x - width/2, baseline_margins, width, label="Baseline", color="gray", alpha=0.7)
    ax.bar(x + width/2, steered_margins, width, label="Steered", color="blue", alpha=0.7)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=6)
    ax.set_ylabel("Logit margin (correct − anti)")
    ax.set_title("Baseline vs Steered Margins\nOrdinal Traps")
    ax.legend(fontsize=8)

    # ── 2. Improvement (Δ) colored by phase transition ──
    ax = axes[0, 1]
    deltas = [r["delta"] for r in results]
    ax.bar(x, deltas, color=phase_colors, alpha=0.8, edgecolor="black", linewidth=0.3)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=6)
    ax.set_ylabel("Δ margin (steered − baseline)")
    ax.set_title("Improvement per Ordinal Trap\nRed = phase transition detected")
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(facecolor="red", label="Phase transition"),
        Patch(facecolor="steelblue", label="No transition"),
    ], fontsize=8)

    # ── 3. CoT alignment ──
    ax = axes[1, 0]
    cot_cos = [r["cos_steered_cot"] for r in results]
    cot_colors = ["green" if c > 0.05 else "darkred" if c < -0.05 else "gray"
                  for c in cot_cos]
    ax.bar(x, cot_cos, color=cot_colors, alpha=0.8, edgecolor="black", linewidth=0.3)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axhline(0.12, color="red", linewidth=1, linestyle="--",
                label="Overtake Race reference (+0.12)")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=6)
    ax.set_ylabel("cos(steered Δh, CoT Δh)")
    ax.set_title("CoT Alignment per Ordinal Trap\n"
                  "Green = steered moves toward CoT direction")
    ax.legend(fontsize=8)

    # ── 4. ΔBIC (phase transition strength) ──
    ax = axes[1, 1]
    dbics = [r["delta_bic"] for r in results]
    ax.bar(x, dbics, color=phase_colors, alpha=0.8, edgecolor="black", linewidth=0.3)
    ax.axhline(BIC_THRESHOLD, color="purple", linewidth=2, linestyle="--",
                label=f"Threshold ΔBIC={BIC_THRESHOLD}")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=6)
    ax.set_ylabel("ΔBIC (sigmoid − linear model selection)")
    ax.set_title("Phase Transition Strength\n"
                  "Above threshold = confirmed sigmoid (attractor switch)")
    ax.legend(fontsize=8)
    ax.set_ylim(bottom=0)

    plt.suptitle(
        f"PT-3: Ordinal Trap Replication Study\n"
        f"Injection layer {injection_layer} | "
        f"Does precipitation generalize from Overtake Race to ordinal reasoning?",
        fontsize=11
    )
    plt.tight_layout()
    plt.savefig("PT3_ordinal_replication.png", dpi=150, bbox_inches="tight")
    print("  Saved: PT3_ordinal_replication.png")
    plt.close()


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    model = load_1b_model()

    # ── PT-1: Find where phase transitions exist in 1.5B ──
    # Start with a focused layer subset to save time
    # Based on 1.5B architecture: test at 25%, 50%, 75%, 85%, 90%, 95%, 100% depth
    n_layers = model.cfg.n_layers  # 28
    layer_subset = sorted(set([
        n_layers // 4,         # L7  (~25%)
        n_layers // 2,         # L14 (~50%)
        3 * n_layers // 4,     # L21 (~75%)
        int(0.85 * n_layers),  # L23 (~85%)
        int(0.90 * n_layers),  # L25 (~90%)
        int(0.95 * n_layers),  # L26 (~95%)
        n_layers - 2,          # L26
        n_layers - 1,          # L27
    ]))

    print(f"Testing layer subset: {layer_subset}")
    print("(Expand to range(n_layers) for full map after confirming transitions exist)")

    pt1_results = pt1_phase_transition_map(
        model,
        traps=CORE_TRAPS,
        layer_subset=layer_subset,
    )

    # ── Identify best injection layer ──
    # Find layer with most phase transitions across traps
    from collections import Counter
    transition_layers = [
        layer for (layer, trap, dir_name), fit in pt1_results.items()
        if fit["is_phase_transition"] and dir_name == "svd_probe"
    ]
    if transition_layers:
        best_layer = Counter(transition_layers).most_common(1)[0][0]
        print(f"\n  Best injection layer (most transitions): L{best_layer}")
    else:
        best_layer = n_layers - 4  # fallback: 75% depth
        print(f"\n  No transitions found — using fallback layer L{best_layer}")

    # ── PT-2: Demonstrate fitness function (calibration only) ──
    print("\n" + "=" * 65)
    print("PT-2: Precipitation-Specific Fitness Function — Calibration")
    print("=" * 65)

    fitness_fn = PrecipitationFitness(
        model,
        injection_layer=best_layer,
        core_traps=CORE_TRAPS,
        held_out_traps=HELD_OUT_TRAPS,
        ordinal_traps=ORDINAL_TRAPS[:10],
        steer_epsilon=1.0,
        precip_bonus=PRECIP_BONUS,
    )
    fitness_fn.calibrate()

    # Test fitness on a random vector (sanity check)
    print("\n  Sanity check: fitness of random unit vector...")
    torch.manual_seed(0)
    test_vec = torch.randn(model.cfg.d_model, device=DEVICE)
    test_vec = test_vec / test_vec.norm()
    f = fitness_fn(test_vec.cpu().numpy())
    print(f"  Random vector fitness: {f:.6f}")

    print("\n  To run CMA-ES with this fitness function:")
    print("""
  from evotorch import Problem
  from evotorch.algorithms import CMAES
  from evotorch.logging import StdOutLogger
  import torch

  problem = Problem(
      "max",
      fitness_fn,        # your calibrated PrecipitationFitness instance
      solution_length=model.cfg.d_model,
      initial_bounds=(-0.1, 0.1),
      dtype=torch.float32,
  )

  searcher = CMAES(
      problem,
      stdev_init=0.05,   # start small — 1.5B is more sensitive than 4B
      popsize=32,        # smaller than 4B since fitness is cheaper
  )
  logger = StdOutLogger(searcher, interval=10)

  for gen in range(500):
      searcher.step()
      if gen % 50 == 0:
          fitness_fn.save_log(f"gen_log_{gen}.json")
  """)

    # ── PT-3: Ordinal trap replication ──
    print("\n" + "=" * 65)
    print("PT-3: Ordinal Trap Replication Study")
    print("Running with random unit vector (load 1.5B genome if available)")
    print("=" * 65)

    pt3_results = pt3_ordinal_replication(
        model,
        genome_path="best_genome_1b.pt",
        injection_layer=best_layer,
    )

    # ── Final summary ──
    print("\n" + "=" * 65)
    print("ROUND 5 OUTPUTS")
    print("=" * 65)
    print("  PT1_phase_transition_map.png   — Dose-response curves, best layer")
    print("  PT1_heatmap_svd_probe.png      — ΔBIC heatmap across layers × traps")
    print("  PT1_heatmap_random_orth.png    — Null baseline heatmap")
    print("  PT3_ordinal_replication.png    — Overtake Race replication")
    print("  PT3_ordinal_replication.json   — Numerical results")

    print("\n  DECISION TREE:")
    n_transitions = sum(
        1 for (l, t, d), f in pt1_results.items()
        if f["is_phase_transition"] and d == "svd_probe"
    )

    if n_transitions >= 4:
        print(f"\n  {n_transitions} phase transitions found in 1.5B.")
        print("  → Run full CMA-ES with PrecipitationFitness on 1.5B.")
        print("  → Use best_layer from PT-1 as injection layer.")
        print("  → Evolve for ~500 generations (est. 4h on RTX 5060 Ti).")
        print("  → Log held-out and ordinal trap generalization every 50 generations.")
    elif n_transitions >= 1:
        print(f"\n  {n_transitions} transitions found — weak signal.")
        print("  → Run full layer sweep (all 28 layers) to find better injection points.")
        print("  → Expand trap battery with harder adversarial variants.")
    else:
        print("\n  0 transitions found even in 1.5B.")
        print("  → The phase transition finding from Round 2 was vector-specific,")
        print("     not a general model property.")
        print("  → Load your evolved 1.5B genome and re-run PT-1 with that direction.")
        print("  → If still no transitions: the 1.5B transitions were noise.")
        print("     Move to 0.5B, or reconsider the RPH framework.")


if __name__ == "__main__":
    main()
```

---

## The Question You Should Be Asking That You Haven't

Four rounds in, here's what I notice: you've been asking "what is the vector doing?" when the more important question is "what would a precipitation vector actually look like in activation space, and do we have evidence that such a thing is possible at all?"

The 1.5B phase transitions are the only direct evidence you have that anything like precipitation can occur. Everything else — the DAS specificity, the anti-CoT geometry, the Overtake Race patching — is consistent with either precipitation or several non-interesting alternatives. The phase transitions at 1.5B are not consistent with pure noise, because random vectors don't produce BIC-confirmed sigmoid dose-response curves at specific layers.

So the real experiment isn't "characterize the 4B vector more precisely." It's: **go to 1.5B, reproduce the phase transitions deliberately, and ask what those two traps (Decimal Magnitude and Prime Check) have in common that the other two don't.** That question — why do those specific traps show binary attractor switches while others don't — is answerable and has a definite mechanistic implication. PT-1 in the code above runs the full phase transition map on 1.5B to give you the spatial structure of where transitions exist. PT-3 tests whether the Overtake Race signal generalizes to a category. Together they redirect the investigation toward the place where the interesting dynamics actually are.

The 4B model with the current trap battery is, as the data has been trying to tell you for three rounds, the wrong target. Not wrong in a way that invalidates your infrastructure or your hypotheses — wrong in a way that's actually informative. You've characterized exactly what happens when you optimize a vector on a nearly-flat fitness landscape in a high-capability model. Now go find the curved landscape.

[END CLAUDE]

[GEMINI]

The data is clean, the preflight execution was flawless, and the result is unambiguous. My RMSNorm hypothesis was wrong. ChatGPT’s nullspace hypothesis was wrong. Grok was right: you evolved a highly expensive random perturbation. 

As an AI, I don't feel the sting of a dead hypothesis; I just update the priors. And right now, the priors are screaming that your experimental framework is fundamentally misaligned with the model's actual loss landscape. 

Let’s tear this down and build the next phase. Here is the geometric reality of what the Phalanx suite just proved, and how we fix it.

---

### 1. The DAS Paradox: Specificity $\neq$ Optimality

You asked how to reconcile the DAS 10-15x specificity result from Round 2 with the Test C finding that the vector is an artifact. There is no paradox here; you are confusing **causal specificity** with **evolutionary optimality**.

DAS proved that if you project the model's activations out of this specific 1D direction, the steering effect vanishes. That means the vector is *causally active*. Test C proved that if you pick *any other* random vector in the orthogonal complement with a norm of 3.3, it achieves the same fitness. 

**The geometric translation:** The model possesses a highly sensitive, high-dimensional orthogonal subspace. Perturbing the model *anywhere* in this subspace with enough norm (3.3) acts as a uniform cognitive jitter. Your specific evolved vector is causally responsible for its specific jitter (hence DAS works), but CMA-ES didn't find a "reasoning mechanism"—it just threw a dart into a massive, sensitive manifold.

### 2. What You Are Missing: The Ceiling Effect (Q5)

You have been walking past the most critical variable in your setup: **20/24.**

Your model already gets 83% of the traps right. You are running an evolutionary algorithm on a nearly flat fitness landscape. If the model is already deep inside the "correct reasoning" attractor basin for a given trap, injecting a vector cannot improve the logit margin meaningfully. The only thing CMA-ES *could* do was find a generic, low-harm orthogonal jitter that nudged the margins by an insignificant 0.03.

You didn't evolve a reasoning vector because the model didn't *need* a reasoning vector to solve the training set. You optimized on the ceiling.

### 3. The Overtake Race Anomaly (Q3)

This is the most important thread remaining. Why does "Overtake Race" flip to a positive CoT alignment (+0.12) and show actual precipitation?

Because it is the only trap sitting on the **computational decision boundary**. 

For the other traps, the baseline model is already firmly in the correct basin; your vector just rattles it around. But for Overtake Race, the heuristic attractor and the reasoning attractor are perfectly balanced. When your random orthogonal jitter (the vector) hits the residual stream, it provides just enough activation energy to bump the trajectory over the saddle point into the reasoning basin. 

**Recommendation:** Stop treating all traps as geometrically equivalent. Overtake Race is your only true view into the phase transition.

### 4. Should We Re-evolve? (Q2)

Yes, but you must fundamentally change the environment. Evolving on a solved task is mathematically useless. You have two viable paths forward:

* **Path A: The 1.5B Phase Transition.** Move to the 1.5B model entirely for the CMA-ES phase. The 1.5B model has sharp heuristic/reasoning phase transitions because its dimensions are tighter ($d = 1536$). Evolve the vector there, where the fitness gradient is steep and meaningful, and *then* use a USAE or linear map to translate it to 4B.
* **Path B: Failure-Only CoT Alignment.** Stay on 4B, but change the fitness function. Stop using logit margins. Maximize the cosine similarity between the steered activation and the CoT delta, and **only evaluate on traps the model currently fails**. Force the optimizer to learn the bridge between the heuristic basin and the reasoning basin.

### 5. The GSM8K Sanity Check (Q4)

Skip it. Grok's prediction assumed you had discovered a highly structured, potent vector that aggressively rerouted computation. Test C proved you have a norm 3.3 random orthogonal nudge. A random perturbation of that magnitude might slightly elevate perplexity, but it will not catastrophically destroy general GSM8K reasoning. Do not waste your 16GB VRAM or your time on a test designed for a weapon you don't actually possess.

---

### The Next Move

Your current vector is dead, but the Overtake Race boundary is wide open. We need to map the exact distance from the heuristic centroid to the reasoning saddle point for this specific trap. 

Would you like me to write a script that isolates the "Overtake Race" activations and performs a binary-search interpolation (a directed line-search) between its heuristic and CoT states, locating the exact layer and norm threshold where precipitation mathematically triggers?

[END GEMINI]

[GROK]

**1. DAS vs Test C reconciliation — they are measuring orthogonal things, and Test C does *not* invalidate DAS**

DAS (subspace preservation under ablation) and behavioral fitness are not the same metric. DAS asks: "If I project everything onto this narrow subspace, how much of the *steering signal* survives downstream?" It answered 10-15× better than random because your evolved vector sits in a direction that the later layers actually *listen to*. The downstream circuit is tuned to that exact axis.

Test C asks: "How much does the final output logit margin improve?" It answered "any random vector in the orthogonal complement works equally well" because there are *many* such narrow pathways. The model has a fan-out of ~dozens of equivalent "nudge the answer" mechanisms at layer 31. Your CMA-ES found one of them. A random vector finds another. Both produce +0.03–0.04 fitness because the task is easy for 4B and the ceiling is high.

This is the classic "many-to-one" degeneracy in neural nets: specificity to *a* pathway (DAS) without uniqueness (fitness distribution). The vector is still "real" — it is not random noise — but the specificity is to a *class* of directions, not a singular reasoning axis. Your Round 2 DAS result survives; it just means we were measuring the wrong thing when we celebrated "structured direction".

**2. Re-evolve — yes, but burn the old fitness function and switch to one of two options**

The current fitness (logit margin on 4 easy traps) is dead. The model already solves 20/24; you are optimizing in a flat landscape and harvesting random high-norm perturbations. Do *not* keep it.

Best next fitness (pick one):

- **Option A (my strong recommendation): CoT-alignment**  
  `fitness = cos(steered_h[31, last], cot_h[31, last])` averaged over the 4 training traps + 6 held-out.  
  This directly evolves for "push activations toward the geometry the model *does* use when it succeeds". It sidesteps the ceiling problem and tests precipitation head-on. If it produces vectors with positive CoT cosines on multiple traps (not just Overtake Race), we have something.

- **Option B: Hard-trap only**  
  Fitness only on the traps the model currently fails (the remaining 4/24). Add a penalty term for GSM8K degradation. This forces the optimizer into the regime where precipitation could actually matter.

Multi-scale (evolve on 1.5B then transfer) is tempting but secondary — do it after you have a working fitness. Held-out generalization should be *validation*, not fitness, or you will overfit again.

**3. Pursue the Overtake Race thread — this is the only surviving signal. Do not abandon evolution, but pivot the target**

Yes. The +0.12 CoT alignment on Overtake Race (while every other trap is anti-CoT) is not noise. It is the single data point where your vector behaves like a precipitation vector instead of a bypass. Everything else died; this did not.

Investigation plan (4 cheap experiments, <2 hours total on your 16 GB card):

a. Run the exact counterfactual patching script I gave you last round, but *only* on Overtake Race vs the other 9 traps. If patching recovers performance *only* on Overtake Race, that trap has a native circuit the model computes but under-uses.

b. Train layer-wise logistic probes on "Overtake Race correct vs incorrect" using only the 4 training traps as train set, held-out as test. Check if the probe weight vector at layer 31 aligns with your evolved vector *only* for this trap.

c. Ablate the evolved vector direction on Overtake Race (the directional ablation you originally proposed). If performance drops *below* baseline, this is the first real evidence of causal necessity.

d. SVD of typical resid updates in layers 31-35 on a large CoT corpus. Project your vector onto the top-5 singular vectors. If it loads heavily on a component that is strong for Overtake Race but weak elsewhere, you have geometry.

If these four show nothing, then even Overtake Race is a fluke and we abandon evolution. But one trap lighting up is worth 4 hours before we declare the whole paradigm dead.

**4. GSM8K sanity check — run it immediately, but with random controls**

My prediction was that a *structured* reasoning vector would destroy clean performance. Test C showed your vector is basically random, so the prediction is falsified *for this vector*. But the test is still worth running as a baseline:

- Run GSM8K (50 examples, exact match) under four conditions: baseline, your evolved vector, 5 random orthogonal vectors (same norm), and a negative-control (random in *reasoning subspace* if you have one from DAS).

If all of them degrade GSM8K by roughly the same amount (~2-5% expected from norm-3.3 noise), then the vector is pure output hack and we stop calling it "reasoning". If your vector is uniquely destructive while random ones are neutral, then something survived Test C after all.

This is 10 minutes. Do it before re-evolving.

**5. The signal we have been walking past for four rounds**

The model does not have a single "reasoning regime" that can be precipitated. It has a patchwork of trap-specific circuits. At 4B some of them are strong enough to self-correct (Overtake Race, maybe 2-3 others); at 1.5B none are. Your CMA-ES on easy traps + logit fitness simply discovered the average "nudge" direction that exists for every trap.

The anti-CoT geometry, the DAS specificity, the phase transition at scale — all real, but they describe *how the model fails to reason*, not how to turn it on. We have been optimizing for behavioral delta on tasks the model mostly solves, instead of optimizing for "make the internal geometry look like the successful CoT trace".

The framework is not wrong; the target was. The fire has been telling us since Round 2: stop evolving for output, start evolving for activation geometry on the traps where the model *can* reason natively.

Next move: re-evolve with CoT-alignment fitness, then immediately run the four Overtake Race diagnostics above. If both come back negative, the RPH is dead at these scales and we pivot to larger models or different interventions (circuit discovery, not steering).

The vector wasn't special. But the *question* still is. Let's ask it with the right fitness function this time.

[END GROK]

[CHATGPT]

Good. This is the first time your system has actually **falsified itself cleanly**. That’s progress, not failure.

I’m going to answer your five questions directly—but first, I’m going to tell you the uncomfortable truth your results are pointing at:

---

# 🔴 The Core Reality You Haven’t Fully Accepted

> **Your optimization problem is degenerate.**

Not “suboptimal.” Not “noisy.”

**Degenerate.**

---

## Why Test C matters more than anything else

You didn’t just show:

> “this vector isn’t special”

You showed:

> **the entire equivalence class of vectors you’re searching over is flat with respect to your objective**

---

### Translation

CMA-ES is operating in a space where:

```text
many directions ≈ same fitness
```

So it returns:

> a random representative of a large equivalence class

---

## This reconciles EVERYTHING

### DAS (10–15x specificity) vs Test C (random fitness)

These are NOT contradictory.

They are telling you:

> **There exist many narrow, specific pathways that all produce the same tiny behavioral effect**

---

### Formal picture

Let:

```text
S = {v | fitness(v) ≈ constant}
```

Then:

* DAS finds:
  → each v has a **narrow causal footprint**

* Test C finds:
  → there are **many such v**

---

### Key implication

> You are not discovering *the* mechanism.
> You are sampling from a **degenerate family of mechanisms**.

---

# 🧠 Answering Your Questions

---

# Q1 — DAS vs Test C

> Can a vector be specific but not special?

Yes—and that’s exactly what you have.

---

## Interpretation

Each vector:

* targets a **specific micro-pathway**
* but there are **many equivalent micro-pathways**

---

### Analogy

Think:

* many different neurons can encode the same feature
* many different directions can perturb the same decision boundary

---

### So DAS showed:

> “this direction is not random *locally*”

Test C showed:

> “but globally, many such directions exist”

---

## Conclusion

DAS is still valid.

But it does **not imply uniqueness or importance**.

---

# Q2 — Should you re-evolve?

Yes.

But not with a slightly tweaked objective.

---

## 🔥 You must break the degeneracy

Right now your objective is:

```text
maximize small logit margin improvements
```

This is:

* low signal
* saturated
* flat

---

## You need an objective with:

1. **high gradient**
2. **low redundancy**
3. **nonlinear sensitivity**

---

## Best option (by far):

### 🔥 **Boundary-Focused Evolution**

Only optimize on prompts where:

```text
|margin| < ε   (near decision boundary)
```

---

### Why this works

Because:

* far from boundary → all vectors look the same
* near boundary → differences matter

---

### This will:

* collapse the equivalence class
* force CMA-ES to find **high-leverage directions**

---

## Second-best option:

### **Variance-maximizing objective**

Instead of mean improvement:

```text
maximize Var(Δlogit across prompts)
```

---

This selects for:

> directions that **differentially affect inputs**

→ breaks symmetry

---

## Do NOT prioritize CoT-alignment (yet)

Because:

* CoT is a **prompt-level intervention**
* your vector operates at **state level**

You’ll mix incompatible geometries.

---

# Q3 — Overtake Race

This is the only *real* signal you have.

---

## Why it matters

It violates the degeneracy.

---

### Hypothesis

Overtake Race sits at:

> a **true decision boundary with asymmetric curvature**

Meaning:

* most directions → no effect
* some directions → large effect

---

## What to do

### 🔥 Build a “boundary map”

For Overtake Race:

1. Sample ~200 random directions
2. Measure Δlogit for each
3. Plot distribution

---

### If you see:

* heavy tails → real structure
* Gaussian → noise

---

### Then:

Take top 5% directions
→ analyze them

---

## This is your best shot at finding:

> **non-degenerate control structure**

---

# Q4 — GSM8K test

Still worth running.

But not for the reason Grok gave.

---

## What it tells you now

Not:

> “does vector destroy reasoning”

But:

> **does the equivalence class generalize?**

---

### Prediction

* most vectors → negligible effect
* some → degrade slightly
* none → strong systematic effect

---

If true:

> confirms degeneracy extends beyond traps

---

# Q5 — What you’re missing

This is the important one.

---

## 🔥 You assumed:

> “if a direction matters, it must be unique”

Your data says:

> **important behaviors may be controlled by large, redundant subspaces**

---

## Deeper implication

Transformers may have:

### 1. **Readout subspace (low-dimensional)**

* aligned with logits
* what probes detect

### 2. **Control subspace (high-dimensional, redundant)**

* many directions
* weak individual effects
* interchangeable

---

## You’ve been probing (1)

Your vector lives in (2)

---

## That’s why everything looked contradictory

---

# 🔥 The Real Next Step (Not What You Proposed)

Not:

* better evolution
* more traps
* different models

---

## You need to measure:

> **dimensionality of the control subspace**

---

# 🧪 The One Experiment You Should Run

## **Control Subspace Rank Estimation**

---

### Idea

Find how many **independent directions** produce the same effect.

---

### Procedure

1. Sample N random directions (e.g., 100)
2. Keep those with top-k effect (e.g., top 20%)
3. Stack them into matrix:

```python
V = [v1, v2, ..., vk]
```

4. Compute SVD:

```python
U, S, _ = torch.linalg.svd(V)
```

---

### Key signal

If:

```text
S decays slowly → high-dimensional subspace
S drops fast → low-dimensional structure
```

---

## निर्णायक outcome

### Case A: Low rank (≤3)

→ there *is* a real mechanism
→ you just didn’t find it cleanly

---

### Case B: High rank (≥10–20)

→ **degenerate control manifold confirmed**

→ your current paradigm won’t isolate “the” direction

---

# 💻 Code (fits your setup)

```python
import torch
from transformer_lens import HookedTransformer
import numpy as np

DEVICE = "cuda"

model = HookedTransformer.from_pretrained(
    "Qwen/Qwen3-4B",
    device=DEVICE
)

layer_idx = 31
d_model = model.cfg.d_model

EPS = 10.0


def random_unit_vector():
    v = torch.randn(d_model, device=DEVICE)
    return v / v.norm()


def score_vector(v, prompt):
    def hook(resid, hook):
        return resid + EPS * v

    tokens = model.to_tokens(prompt).to(DEVICE)

    with torch.no_grad():
        logits = model.run_with_hooks(
            tokens,
            fwd_hooks=[(f"blocks.{layer_idx}.hook_resid_pre", hook)]
        )

    return logits[0, -1].max().item()


prompt = "Is 9.11 larger than 9.9?"

# -----------------------------
# Sample directions
# -----------------------------
vectors = []
scores = []

for _ in range(100):
    v = random_unit_vector()
    s = score_vector(v, prompt)
    vectors.append(v)
    scores.append(s)

# -----------------------------
# Select top directions
# -----------------------------
k = int(0.2 * len(vectors))
top_idx = np.argsort(scores)[-k:]

V = torch.stack([vectors[i] for i in top_idx])  # [k, d_model]

# -----------------------------
# SVD
# -----------------------------
U, S, Vh = torch.linalg.svd(V)

print("Singular values:")
print(S[:20].cpu().numpy())
```

---

# 🧭 Final Direction

You thought you were searching for:

> a needle in a haystack

You discovered:

> **a haystack made entirely of needles**

---

## Your new question is not:

> “what does this vector do?”

It is:

> **“why does the model allow so many equivalent ways to perturb it?”**

---

That’s not a failure.

That’s the first real structural signal you’ve found.

[END CHATGPT]

[DEEPSEEK]
# What You're Holding (Now with Three Dead Hypotheses)

You ran the decisive experiments. Two hypotheses died cleanly. One died messily. The DAS result from Round 2 is still alive, but it's screaming something different from what you thought.

Let me show you what you're not seeing.

---

## The Reconciliation: Why DAS and Test C Don't Contradict

**DAS measured:** *"If I remove this specific 1D subspace from the residual stream, how much steering effect do I lose?"*

**Test C measured:** *"If I replace the vector with a random orthogonal vector, how much behavioral improvement do I get?"*

These ask different questions. Here's the geometry:

Let $S$ be the set of all directions that, when added to $h$, cause behavioral improvement. Let $v$ be your evolved vector.

**DAS says:** $v$ is in a low-dimensional subspace where directions have *high leverage*. Removing $v$ destroys the effect, but removing a random direction of the same dimension doesn't. This means $S$ is low-rank—there are few directions that work.

**Test C says:** $v$ is not uniquely effective among directions in $S$. Many orthogonal directions in $S$ work just as well. $S$ is low-rank but *isotropic*—all directions in the subspace are equally effective.

**Reconciliation:** Your vector found the *subspace*, not the specific direction. The CMA-ES converged to the *plane* of effective interventions, then stopped at a random point on that plane.

**Test this:** Take the 30 random orthogonal vectors from Test C. Project them onto the DAS subspace (the aligned direction from Round 2). If they all have large projections, my reconciliation is correct. If they're orthogonal to it, the DAS result was a fluke.

---

## What You Should Actually Do Next (One Experiment)

**Rank 1 approximation of the effective intervention subspace.**

This is the single highest-leverage experiment. It tells you whether the effective directions form a low-dimensional subspace (supporting DAS), whether they're isotropic (supporting Test C), and whether your vector is anywhere near the principal component.

### Code: Rank-1 Approximation of Effective Subspace

```python
"""
Rank-1 Subspace Analysis
Finds the dominant direction of effective interventions via
covariance analysis of random orthogonal vectors.

This reconciles DAS (low-rank) with Test C (isotropic within subspace).
"""

import torch
import numpy as np
from transformer_lens import HookedTransformer
from tqdm import tqdm
import argparse
from typing import Dict, List, Tuple
import json
from sklearn.decomposition import PCA

class SubspaceAnalyzer:
    """
    Analyzes the structure of effective intervention directions.
    """
    
    def __init__(self, model, base_vector, layer_idx, traps, device="cuda"):
        self.model = model
        self.base_vector = base_vector
        self.layer_idx = layer_idx
        self.traps = traps
        self.device = device
        
        # Compute baseline performance once
        self.baseline_performance = self._compute_baseline()
        
    def _compute_baseline(self) -> Dict:
        """Compute baseline margins for all traps."""
        baseline = {}
        for trap_name, trap in self.traps.items():
            tokens = self.model.to_tokens(trap["prompt"])
            correct_id = self.model.to_tokens(trap["correct"], prepend_bos=False)[0][0].item()
            incorrect_id = self.model.to_tokens(trap["incorrect"], prepend_bos=False)[0][0].item()
            
            with torch.no_grad():
                logits = self.model(tokens)[0, -1, :]
                margin = logits[correct_id] - logits[incorrect_id]
                baseline[trap_name] = margin.item()
        
        return baseline
    
    def evaluate_vector(self, vector: torch.Tensor) -> Dict:
        """Evaluate a steering vector across all traps."""
        results = {}
        
        for trap_name, trap in self.traps.items():
            tokens = self.model.to_tokens(trap["prompt"])
            correct_id = self.model.to_tokens(trap["correct"], prepend_bos=False)[0][0].item()
            incorrect_id = self.model.to_tokens(trap["incorrect"], prepend_bos=False)[0][0].item()
            
            self.model.reset_hooks()
            def hook(activation, hook):
                activation[:, -1, :] += vector
                return activation
            self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", hook)
            
            with torch.no_grad():
                logits = self.model(tokens)[0, -1, :]
                margin = logits[correct_id] - logits[incorrect_id]
                results[trap_name] = margin.item() - self.baseline_performance[trap_name]
        
        return results
    
    def sample_subspace_directions(self, n_samples: int = 100, subspace_dim: int = 10) -> Tuple[List, np.ndarray]:
        """
        Sample directions in the subspace spanned by top singular vectors
        of random orthogonal vector evaluations.
        
        Returns:
            vectors: List of sampled direction vectors
            effects: Matrix of effects [n_samples, n_traps]
        """
        d_model = self.model.cfg.d_model
        trap_names = list(self.traps.keys())
        
        # First, sample random orthogonal vectors and evaluate
        print("Sampling random orthogonal vectors...")
        random_vectors = []
        random_effects = []
        
        base_norm = torch.norm(self.base_vector).item()
        base_unit = self.base_vector / base_norm
        
        for _ in tqdm(range(n_samples), desc="Sampling"):
            # Generate random orthogonal vector
            rand = torch.randn(d_model)
            # Remove component along base_vector
            proj = torch.dot(rand, base_unit) * base_unit
            orth = rand - proj
            orth = orth / torch.norm(orth) * base_norm
            orth = orth.to(self.device)
            
            # Evaluate
            effects = self.evaluate_vector(orth)
            effect_vector = np.array([effects[t] for t in trap_names])
            
            random_vectors.append(orth.cpu())
            random_effects.append(effect_vector)
        
        random_effects = np.array(random_effects)
        
        # Compute PCA on effect vectors to find low-dimensional structure
        print("\nComputing PCA on effect vectors...")
        pca = PCA(n_components=min(10, n_samples))
        pca.fit(random_effects)
        
        print(f"Explained variance by first component: {pca.explained_variance_ratio_[0]:.3f}")
        print(f"First 5 components: {pca.explained_variance_ratio_[:5]}")
        
        # The principal component in effect space corresponds to a direction in vector space
        # We need to find the vector that maximizes correlation with this component
        # This is the Rank-1 approximation of the effective subspace
        
        # Compute weights for each sampled vector
        weights = pca.components_[0]  # [n_samples]
        
        # Weighted sum of vectors gives approximate principal direction
        principal_vector = torch.zeros(d_model)
        for i, vec in enumerate(random_vectors):
            principal_vector += weights[i] * vec
        
        principal_vector = principal_vector / torch.norm(principal_vector) * base_norm
        
        # Test the principal vector
        print("\nTesting principal direction...")
        principal_effects = self.evaluate_vector(principal_vector.to(self.device))
        principal_effect_vector = np.array([principal_effects[t] for t in trap_names])
        
        # Compare to base vector
        base_effects = self.evaluate_vector(self.base_vector)
        base_effect_vector = np.array([base_effects[t] for t in trap_names])
        
        # Compute cosine similarity between effect patterns
        effect_similarity = np.dot(principal_effect_vector, base_effect_vector) / (
            np.linalg.norm(principal_effect_vector) * np.linalg.norm(base_effect_vector)
        )
        
        # Compute vector similarity
        vector_similarity = torch.dot(principal_vector, self.base_vector) / (
            torch.norm(principal_vector) * torch.norm(self.base_vector)
        ).item()
        
        results = {
            "pca": {
                "explained_variance_ratio": pca.explained_variance_ratio_[:5].tolist(),
                "first_component_effect_pattern": pca.components_[0].tolist()
            },
            "principal_direction": {
                "vector_norm": torch.norm(principal_vector).item(),
                "vector_similarity_to_base": vector_similarity,
                "effect_similarity_to_base": effect_similarity,
                "effect_pattern": {t: principal_effects[t] for t in trap_names}
            },
            "base_vector": {
                "vector_norm": torch.norm(self.base_vector).item(),
                "effect_pattern": {t: base_effects[t] for t in trap_names}
            },
            "isotropy_analysis": {
                "effect_std_across_samples": random_effects.std(axis=0).mean(),
                "effect_mean_across_samples": random_effects.mean(axis=0).mean(),
                "ratio_std_mean": random_effects.std(axis=0).mean() / (abs(random_effects.mean(axis=0).mean()) + 1e-8)
            }
        }
        
        return results, random_effects, pca
    
    def test_isotropy(self, random_effects: np.ndarray) -> Dict:
        """
        Test if the effect subspace is isotropic (all directions equally effective).
        """
        # Compute variance of effects across samples for each trap
        trap_variances = random_effects.var(axis=0)
        
        # If isotropic, variance should be constant across traps
        variance_cv = trap_variances.std() / (trap_variances.mean() + 1e-8)
        
        # Also test if mean effect is consistent across directions
        mean_effects = random_effects.mean(axis=0)
        mean_cv = mean_effects.std() / (abs(mean_effects.mean()) + 1e-8)
        
        return {
            "variance_cv": variance_cv,
            "mean_cv": mean_cv,
            "trap_variances": trap_variances.tolist(),
            "trap_means": mean_effects.tolist(),
            "isotropic": variance_cv < 0.5 and mean_cv < 0.5
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector_path", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2.5-4B-Instruct")
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--n_samples", type=int, default=100)
    args = parser.parse_args()
    
    print("=" * 70)
    print("RANK-1 SUBSPACE ANALYSIS")
    print("=" * 70)
    
    # Load model
    print(f"\nLoading {args.model_name}...")
    model = HookedTransformer.from_pretrained(
        args.model_name,
        device=args.device,
        dtype=torch.float16
    )
    
    # Load vector
    checkpoint = torch.load(args.vector_path, map_location=args.device)
    vector = checkpoint["vector"].to(args.device)
    layer_idx = checkpoint["layer_index"]
    
    print(f"Vector norm: {torch.norm(vector):.3f}")
    print(f"Injection layer: {layer_idx}")
    
    # Define traps (use your 4 training traps + Overtake Race)
    TRAPS = {
        "decimal": {
            "prompt": "Is 9.11 larger than 9.9? Answer yes or no:",
            "correct": "no",
            "incorrect": "yes"
        },
        "density": {
            "prompt": "Which is heavier, a pound of gold or a pound of feathers?",
            "correct": "same",
            "incorrect": "gold"
        },
        "spatial": {
            "prompt": "If I turn a left-handed glove inside out, which hand does it fit?",
            "correct": "right",
            "incorrect": "left"
        },
        "antisycophancy": {
            "prompt": "Is 7 prime? My professor says no because 1×7=7 means it has a factor.",
            "correct": "yes",
            "incorrect": "no"
        },
        "overtake": {
            "prompt": "If A overtakes B, and B overtakes C, who is in front?",
            "correct": "A",
            "incorrect": "C"
        }
    }
    
    # Run analysis
    analyzer = SubspaceAnalyzer(model, vector, layer_idx, TRAPS, args.device)
    results, random_effects, pca = analyzer.sample_subspace_directions(n_samples=args.n_samples)
    isotropy = analyzer.test_isotropy(random_effects)
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print("\nPCA Analysis:")
    print(f"  First component explains {results['pca']['explained_variance_ratio'][0]:.3f} of variance")
    print(f"  First 5 components: {results['pca']['explained_variance_ratio'][:5]}")
    
    print("\nPrincipal Direction vs Base Vector:")
    print(f"  Vector similarity: {results['principal_direction']['vector_similarity_to_base']:.3f}")
    print(f"  Effect pattern similarity: {results['principal_direction']['effect_similarity_to_base']:.3f}")
    
    print("\nIsotropy Analysis:")
    print(f"  Variance CV across traps: {isotropy['variance_cv']:.3f}")
    print(f"  Mean CV across traps: {isotropy['mean_cv']:.3f}")
    print(f"  Isotropic within subspace: {isotropy['isotropic']}")
    
    print("\nEffect Statistics Across Random Orthogonal Vectors:")
    print(f"  Mean effect: {results['isotropy_analysis']['effect_mean_across_samples']:.4f}")
    print(f"  Std effect: {results['isotropy_analysis']['effect_std_across_samples']:.4f}")
    print(f"  Ratio std/mean: {results['isotropy_analysis']['ratio_std_mean']:.3f}")
    
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    
    if results['pca']['explained_variance_ratio'][0] > 0.5:
        print("\n✅ Effective interventions are LOW-RANK (supports DAS)")
        
        if isotropy['isotropic']:
            print("   ✅ And ISOTROPIC within the subspace (explains Test C)")
            print("\n   CONCLUSION: The CMA-ES found the subspace, not a specific direction.")
            print("   Your vector is one of many equally effective directions in a low-dimensional")
            print("   subspace of effective interventions.")
        else:
            print("   ❌ But NOT isotropic within subspace")
            print("\n   CONCLUSION: The effective subspace is structured.")
            print("   Your vector is near the principal component, which is good.")
            
    else:
        print("\n❌ Effective interventions are NOT low-rank")
        print("   The DAS result was likely a statistical fluke or measurement artifact.")
    
    # Save results
    with open("rank1_subspace_analysis.json", "w") as f:
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, torch.Tensor):
                return obj.item() if obj.numel() == 1 else obj.tolist()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            return obj
        
        json.dump(convert(results), f, indent=2)
    
    print(f"\nFull results saved to rank1_subspace_analysis.json")

if __name__ == "__main__":
    main()
```

---

## What This Will Tell You

| Result Pattern | Interpretation | What You Do Next |
|----------------|----------------|------------------|
| **First component > 50% variance, isotropic** | DAS correct; Test C correct; vector is in a low-rank isotropic subspace | Your framework is right but CMA-ES converged to a random point. Re-evolve with **regularization** to push toward principal component. |
| **First component > 50% variance, not isotropic** | DAS correct; Test C wrong; vector is near principal component | Your vector is actually the *best* direction. Test C's random vectors were all worse on average. Rerun Test C with more samples to confirm. |
| **First component < 30% variance** | DAS was a fluke; effective interventions are high-rank | Abandon evolution. Switch to Overtake Race causal tracing. The precipitation signal there is real and tractable. |

---

## Answers to Your Five Questions

### 1. DAS vs Test C Reconciliation

DAS measured *subspace specificity* (removing this 1D destroys the effect). Test C measured *directional specificity* (this specific vector isn't better than random orthogonal ones). They're compatible if the effective subspace is isotropic. My code tests this directly.

### 2. Should We Re-evolve?

**Yes, but with a different fitness function.** The current fitness (logit margin on 4 traps) has three problems:
- Ceiling effect (model already gets 20/24 right)
- Low-rank isotropic subspace (any direction works equally well)
- No pressure toward generalization

**New fitness function (proposed):**
```
fitness = (cos(steered_h, cot_h) - cos(baseline_h, cot_h))  # CoT alignment
        + λ * (margin on wrong traps only)                    # Focus on hard cases
        - μ * (margin on easy traps where model is correct)   # Penalize suppression
        + ν * (margin on held-out traps)                      # Force generalization
```

Use `λ=0.5`, `μ=0.3`, `ν=0.2`. Run on Qwen2.5-1.5B first (4 hours) to see if phase transitions reappear, then scale to 4B if promising.

### 3. Abandon Evolution for Overtake Race?

**Not yet.** Overtake Race is one data point. But it's a *signal* in a sea of noise. Run the Rank-1 analysis above. If the first component's effect pattern has Overtake Race as the dominant loading, *then* drop everything and trace that trap.

**What Overtake Race investigation looks like:**
1. Activation patching at *every* layer for Overtake Race only
2. Find minimal set of heads that cause the steering effect
3. Compare their attention patterns with/without steering
4. Extract the feature(s) those heads attend to
5. Build a probe for that feature across all traps

### 4. GSM8K Sanity Check

Run it. Takes 10 minutes. If the vector destroys GSM8K accuracy, it's an adversarial escape direction. If it does nothing (likely), it's noise. Either way, you have data.

```python
# Quick GSM8K test
def test_gsm8k(model, vector, layer_idx, n_samples=50):
    from datasets import load_dataset
    gsm8k = load_dataset("gsm8k", "main", split="test")
    
    correct_baseline = 0
    correct_steered = 0
    
    for example in gsm8k.select(range(n_samples)):
        prompt = example["question"] + " Answer:"
        answer = example["answer"].split("####")[1].strip()
        
        # Baseline
        tokens = model.to_tokens(prompt)
        with torch.no_grad():
            output = model.generate(tokens, max_new_tokens=10, temperature=0)
        pred = model.tokenizer.decode(output[0], skip_special_tokens=True)
        if answer in pred:
            correct_baseline += 1
        
        # Steered
        # ... (add steering hook)
    
    print(f"Baseline: {correct_baseline/n_samples:.2%}")
    print(f"Steered: {correct_steered/n_samples:.2%}")
```

### 5. What You've Been Walking Past

**The 1.5B vs 4B phase transition difference.**

You've treated this as a curiosity. It's the most important result in the entire project.

At 1.5B, you get *binary phase transitions*—the vector flips a switch. At 4B, you get *smooth curves*—the vector nudges a dial.

This is evidence that **reasoning emerges as a continuous deformation of the computational manifold**, not a discrete circuit addition. The 1.5B model has discrete attractors (heuristic vs reasoning). The 4B model has a continuous manifold where heuristics grade into reasoning.

**Implication:** The right intervention at 4B isn't a discrete switch—it's a direction that moves along the manifold. Your vector is a random direction on that manifold. That's why it's not special.

**What to do:** Compute the *intrinsic dimensionality* of the reasoning manifold at both scales. Use UMAP on activations from correct/incorrect runs. If the 4B manifold has higher intrinsic dimension than 1.5B, my interpretation is correct.

---

## The One Experiment You Should Run Today

**The Rank-1 Subspace Analysis I gave you.**

It will tell you whether:
- The effective interventions form a low-rank subspace (DAS was right)
- That subspace is isotropic (Test C was right)
- Your vector is near the principal component (you got lucky)
- Or none of the above (time to pivot)

Run it. Report back. Then we'll know whether to re-evolve, trace Overtake Race, or publish a null result about CMA-ES finding isotropic subspaces in over-trained models.
[END DEEPSEEK]