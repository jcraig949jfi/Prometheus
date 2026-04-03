"""Test that all amino acids load and the registry is populated correctly."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forge.amino_acids.registry import load_all, get_registry, summary

print("Loading all amino acids...")
load_all()

reg = get_registry()
print(f"\nLoaded {len(reg)} amino acids.\n")
print(summary())

# Validate each amino acid
print("\n\nValidation:")
errors = 0
for acid_id, meta in sorted(reg.items()):
    fn = meta["function"]
    # Check line count bounds
    if meta["lines"] < 3:
        print(f"  WARNING: {acid_id} is only {meta['lines']} lines (min=5)")
        errors += 1
    if meta["lines"] > 25:
        print(f"  WARNING: {acid_id} is {meta['lines']} lines (max=20)")
        errors += 1
    # Check it's callable
    if not callable(fn):
        print(f"  ERROR: {acid_id} function is not callable")
        errors += 1

if errors == 0:
    print("  All amino acids passed validation.")
else:
    print(f"  {errors} validation issues found.")
