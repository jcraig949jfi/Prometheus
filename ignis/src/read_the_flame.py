import torch

# Load the binary 'json'
state = torch.load("results/ignis/state.json")

print("--- CMA-ES STATE RECOVERY ---")
print(f"Generation Count: {state.get('gen_count', 'Unknown')}")
print(f"Current Sigma: {state.get('sigma', 'N/A')}")

# Check the dimensions of the manifold
if 'mean_vector' in state:
    print(f"Mean Vector Shape: {state['mean_vector'].shape}")
    print(f"Mean Vector Norm: {state['mean_vector'].norm().item():.4f}")

# The Covariance Matrix is the 'Atlas'
if 'C' in state:
    print(f"Covariance Matrix detected: {state['C'].shape}")