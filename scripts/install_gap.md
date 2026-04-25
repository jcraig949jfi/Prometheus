# Installing GAP on Windows

GAP is a system for computational discrete algebra (groups, characters,
representations). It's a Tier-3 native install in `techne/ARSENAL_ROADMAP.md`.

## Why we want GAP

- Finite group theory: character tables, automorphism groups, classification
  of finite simple groups results
- ATLAS of Finite Group Representations
- Group cohomology computations
- Critical for the Galois-group / modular-form correspondences in Aporia's
  identity-join research

## Recommended install path on Windows

GAP doesn't ship via pip. Options:

### Option A: Native Windows installer (recommended; 5 min, no admin needed)

1. Download the latest GAP for Windows installer:
   https://www.gap-system.org/download/

   Direct link as of 2026-04: https://github.com/gap-system/gap/releases
   (look for `gap-X.Y.Z-windows.exe`)

2. Run the installer. Default location is `C:\gap-X.Y.Z\`. No admin
   required if you choose a user-writable install location.

3. Add GAP to PATH so `gap.exe` is invokable from terminals:

   ```powershell
   # Add to user PATH (no admin needed)
   [System.Environment]::SetEnvironmentVariable(
     'PATH',
     [System.Environment]::GetEnvironmentVariable('PATH', 'User') + ';C:\gap-X.Y.Z\bin',
     'User'
   )
   ```

   Or add manually via System Properties → Environment Variables.

4. Restart your terminal and verify:

   ```bash
   gap --version
   ```

5. Re-import `prometheus_math` — `pm.registry.is_available('gap')` will
   now return True.

### Option B: WSL2 Ubuntu

If you have WSL2, GAP installs trivially:

```bash
sudo apt update && sudo apt install gap
```

Then `which gap` from the WSL terminal returns the path. Note that
prometheus_math probes Windows PATH, not WSL PATH, so you'll need to
either invoke from inside WSL or set up a wrapper script.

## Wiring into prometheus_math

Once `gap` is on PATH, the `registry.py` probe will pick it up automatically.

A subprocess-based wrapper (`prometheus_math/backends/_gap.py`) is the
next roadmap item once GAP is installed. It will expose:

```python
pm.groups.character_table(group_name)   # 'A5', 'S6', etc.
pm.groups.automorphism_group(generators)
pm.groups.is_solvable(generators)
pm.groups.composition_series(generators)
```

These will dispatch to GAP via subprocess + JSON I/O.

## Status

Pending: this install requires a manual step that can't be automated
from inside Claude Code. Once installed, ping Techne (or just commit
the PATH change) and the wrapper will be built.
