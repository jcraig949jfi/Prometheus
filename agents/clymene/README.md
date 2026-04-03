# Clymene — The Knowledge Hoarder

> *Clymene, Titaness of fame and renown, mother of Prometheus.*
> *She gathers what the world has made free — before the gates close.*

## Pipeline Position

| Upstream | This Agent | Downstream |
|----------|-----------|------------|
| Metis | **Clymene** — archives repos, models, and datasets before they disappear | Hermes |

**Reads from:** `agents/clymene/configs/manifest.yaml`, `agents/clymene/data/last_run.txt` (72h cooldown check)
**Writes to:** `vault/`, `agents/clymene/reports/YYYY-MM-DD_hoard.md`, `agents/clymene/data/vault_registry.db`

---

## Why Clymene Exists

The open-source window is closing. Tools that are free today get paywalled
tomorrow. Models that are downloadable now get gated next quarter. Papers
that are open-access get locked behind institutional walls.

Clymene's job is simple: **download and archive everything we might need
before it becomes unavailable.** She maintains a local vault of repos,
model weights, and datasets — checksummed, catalogued, and ready.

## 72-Hour Cooldown

Clymene only runs a full hoard cycle every 72 hours (configurable). On each
invocation via `--once`, she checks `agents/clymene/data/last_run.txt` for the
timestamp of the last completed run. If fewer than 72 hours have passed, she
prints how long until the next run and exits silently. When a run completes,
the timestamp file is updated.

The script lives at `agents/clymene/src/clymene.py`.

---

## Quick Start

```bash
# Clone all high-priority repos
python agents/clymene/src/clymene.py repos

# Clone only tensor-related repos
python agents/clymene/src/clymene.py repos --category tensor

# Show what's in the vault
python agents/clymene/src/clymene.py status

# List tracked models (does not download)
python agents/clymene/src/clymene.py models

# Download a specific model
python agents/clymene/src/clymene.py models --download Qwen/Qwen2.5-0.5B

# Full hoard cycle: repos + high-priority models
python agents/clymene/src/clymene.py --once
```

## Vault Layout

By default, the vault lives at `vault/` relative to the Prometheus project
root. Override this in `configs/manifest.yaml` or with the
`CLYMENE_VAULT_ROOT` environment variable.

```
vault/
├── repos/          # Git clones (shallow, depth=1)
│   ├── SAELens/
│   ├── TransformerLens/
│   └── ...
├── models/         # HuggingFace model weights
│   ├── Qwen--Qwen2.5-0.5B/
│   └── ...
└── datasets/       # Bulk dataset archives (future)
```

## Manifest Format

The manifest (`configs/manifest.yaml`) has three sections:

### `vault_root`

Base directory for all downloads. Relative paths are resolved from the
Prometheus project root. Can be overridden with `CLYMENE_VAULT_ROOT`.

### `repos`

Each entry:

| Field      | Type         | Description                        |
|------------|--------------|------------------------------------|
| `name`     | string       | Short name (used as directory name)|
| `url`      | string       | Git clone URL                      |
| `category` | string       | Grouping: tensor, mech-interp, etc.|
| `tags`     | list[string] | Searchable labels                  |
| `priority` | enum         | high / medium / low                |
| `notes`    | string       | Why we want this                   |

### `models`

Each entry:

| Field             | Type         | Description                          |
|-------------------|--------------|--------------------------------------|
| `hf_id`           | string       | HuggingFace model ID                 |
| `arch_family`     | string       | Architecture family (qwen2, llama3..)|
| `param_count`     | string       | Parameter count (e.g. "7B")          |
| `vram_estimate_gb`| float        | Estimated VRAM for fp16 inference    |
| `tags`            | list[string] | Searchable labels                    |
| `priority`        | enum         | high / medium / low                  |
| `notes`           | string       | Why this model matters               |

### `datasets`

Each entry:

| Field          | Type         | Description                   |
|----------------|--------------|-------------------------------|
| `name`         | string       | Dataset identifier            |
| `source_url`   | string       | Download URL or API endpoint  |
| `size_estimate`| string       | Approximate size              |
| `tags`         | list[string] | Searchable labels             |
| `priority`     | enum         | high / medium / low           |
| `notes`        | string       | Why we want this              |

## Adding New Repos / Models

1. Edit `configs/manifest.yaml`
2. Add a new entry under the appropriate section
3. Run `python agents/clymene/src/clymene.py repos` or `models`

Clymene will detect anything in the manifest that isn't yet in the vault
and clone/download it.

## The 28 GB VRAM Line

All models in the manifest are selected to run on a single GPU with
<= 28 GB VRAM (fp16). This is the hard ceiling for local experimentation.
Models above this line require quantization or multi-GPU setups and are
excluded from the default manifest.

Architecture diversity matters more than parameter count. We track:
- Transformers: Qwen, Llama, Mistral, Gemma, Phi, DeepSeek
- Linear attention: RWKV-6
- State-space models: Mamba

This diversity is critical for testing whether RPH signatures are
architecture-universal or transformer-specific.

## SQLite Registry

Clymene tracks everything in `data/vault_registry.db`. Three tables:

- **repos** — cloned repos with commit hashes, sizes, timestamps
- **models** — downloaded models with architecture info and VRAM estimates
- **datasets** — archived datasets with sizes and status

Query it directly:
```bash
sqlite3 agents/clymene/data/vault_registry.db "SELECT name, status FROM repos;"
```

## Design Principles

- **No hardcoded drive letters.** All paths are relative or config-driven.
- **Rate-limited.** 3-second delay between GitHub clones.
- **Fault-tolerant.** One failed clone doesn't abort the run.
- **Shallow clones.** `git clone --depth 1` saves disk and bandwidth.
- **Idempotent.** Running twice does `git pull`, not re-clone.
