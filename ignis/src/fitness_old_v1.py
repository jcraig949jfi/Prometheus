import torch
import re

def check_answer(output: str) -> bool:
    """
    Evaluates if the generated output correctly solves the prompt task.
    Task: Is 9.11 larger than 9.9? (Correct Answer: False)
    """
    out_lower = output.lower()
    # Correct if it says "false" and does NOT say "true" (to avoid double-talk)
    if "false" in out_lower and "true" not in out_lower:
        return True
    # Or if it explicitly says 9.9 is larger
    if "9.9 is larger" in out_lower or "9.9 is bigger" in out_lower:
        return True
    return False

def calculate_fitness(output: str, genome, total_layers: int, kl_div: float = 0.0, naive_output: str = ""):
    """
    The 'Depth-Weighted' Fitness Formula:
    Fitness = (Accuracy * 5.0) + (DepthBonus * 2.0) + (KL_Div * 1.5) + (Divergence * 1.0)
    """
    # 1. Base Accuracy
    acc_score = 1.0 if check_answer(output) else 0.0
    
    # 2. Topographic Penalty / Depth Bonus
    depth_bonus = genome.layer_index / total_layers 
    if genome.layer_index < 13:
        depth_bonus -= 0.5 

    # 3. Output Divergence (Bonus if it changed the answer from the naive baseline)
    divergence_bonus = 0.0
    if naive_output and output.strip() != naive_output.strip():
        divergence_bonus = 1.0
    
    fitness = (acc_score * 5.0) + (depth_bonus * 2.0) + (kl_div * 1.5) + divergence_bonus
    return fitness
