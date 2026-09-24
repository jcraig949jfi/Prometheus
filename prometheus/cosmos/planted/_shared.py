"""SHARED helper imported by ps1 and ps2 (the planted shared-code artifact).
It injects a phase law in N that no independent physics supports."""
import numpy as np


def shared_margin(n):
    return 0.1 + (0.40 - n) * 1.5


def shared_rewards(prob, seed, episodes):
    return (np.random.default_rng(seed).random(episodes) < prob).astype(float)
