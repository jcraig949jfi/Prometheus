"""
preflight.py — Pre-launch checks for Apollo v2.
Run before the main loop to catch configuration issues early.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from apollo import _resolve_path, load_config, APOLLO_DIR


def run():
    errors = []

    # 1. GPU
    print("[preflight] Checking GPU...")
    try:
        import torch
        assert torch.cuda.is_available(), "No CUDA GPU detected"
        name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"  GPU: {name} ({vram:.1f} GB)")
    except Exception as e:
        errors.append(f"GPU: {e}")
        print(f"  FAIL: {e}")

    # 2. Config
    print("[preflight] Loading config...")
    try:
        config = load_config()
        print(f"  Population: {config['population_size']}")
        print(f"  LLM: {config.get('llm_model', 'NOT SET')}")
        print(f"  8-bit: {config.get('llm_load_in_8bit', False)}")
    except Exception as e:
        errors.append(f"Config: {e}")
        print(f"  FAIL: {e}")
        return False

    # 3. forge_primitives
    print("[preflight] Checking forge_primitives...")
    try:
        prim_dir = _resolve_path(config["primitives_dir"])
        if prim_dir not in sys.path:
            sys.path.insert(0, prim_dir)
        import forge_primitives as fp
        n = len([x for x in dir(fp) if not x.startswith("_") and callable(getattr(fp, x))])
        print(f"  forge_primitives: {n} functions")
    except Exception as e:
        errors.append(f"forge_primitives: {e}")
        print(f"  FAIL: {e}")

    # 4. trap_generator
    print("[preflight] Checking trap_generator...")
    try:
        trap_path = _resolve_path(config["trap_generator"])
        assert Path(trap_path).exists(), f"Not found: {trap_path}"
        print(f"  trap_generator: OK")
    except Exception as e:
        errors.append(f"trap_generator: {e}")
        print(f"  FAIL: {e}")

    # 5. Gem directories
    print("[preflight] Checking gem sources...")
    import glob
    gem_dirs = config.get("gem_dirs", [])
    total_gems = 0
    for pattern in gem_dirs:
        resolved = _resolve_path(pattern)
        found = len(glob.glob(resolved))
        total_gems += found
    print(f"  Gem files found: {total_gems}")

    # 6. Checkpoint state
    print("[preflight] Checking checkpoints...")
    from checkpointer import checkpoint_exists, load_checkpoint
    ckpt_dir = str(APOLLO_DIR / config.get("checkpoint_dir", "checkpoints"))
    if checkpoint_exists(ckpt_dir):
        cp = load_checkpoint(ckpt_dir)
        if cp:
            _, _, gen = cp
            print(f"  Will resume from generation {gen}")
        else:
            print(f"  Checkpoint exists but failed to load (will start fresh)")
    else:
        print(f"  No checkpoints — starting from generation 0")

    if errors:
        print()
        print("PREFLIGHT FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False

    print()
    print("[preflight] All checks passed.")
    return True


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
