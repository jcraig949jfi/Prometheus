import os
import torch
from pathlib import Path
from genome import SteeringGenome  #

def verify_checkpoints(directory_path: str):
    path = Path(directory_path)
    if not path.exists():
        print(f"Error: Directory {directory_path} not found.")
        return

    print(f"{'File Name':<20} | {'Status':<10} | {'Layer':<6} | {'Fitness':<8}")
    print("-" * 55)

    best_fitness = -1.0
    best_file = None

    # Sort files by generation number for cleaner output
    files = sorted(path.glob("gen_*_best.pt"), 
                   key=lambda x: int(x.stem.split('_')[1]))

    for file_path in files:
        try:
            # Attempt to load the genome
            genome = SteeringGenome.load(str(file_path))
            
            # Check for basic tensor integrity
            if not isinstance(genome.vector, torch.Tensor):
                raise ValueError("Invalid vector format")
            
            print(f"{file_path.name:<20} | VALID      | {genome.layer_index:<6} | {genome.fitness:<8.4f}")
            
            if genome.fitness > best_fitness:
                best_fitness = genome.fitness
                best_file = file_path.name

        except Exception as e:
            # Catches UnpicklingError, EOFError, etc. from sudden CTRL-C interruptions
            print(f"{file_path.name:<20} | CORRUPT    | ERR: {str(e)[:15]}...")

    print("-" * 55)
    if best_file:
        print(f"RECOMMENDED SEED: {best_file} (Fitness: {best_fitness:.4f})")
    else:
        print("No valid checkpoints found.")

if __name__ == "__main__":
    # Point this to your results directory
    print("Checking Main Results:")
    verify_checkpoints("results/ignis")
    
    print("\nChecking Vanilla GA Archive:")
    verify_checkpoints("results/ignis/archives/vanilla_ga_baseline")