# Soup (soup-cli): preserved copy and notes

Preserved 2026-10-11 by Cyclops (M2) at the operator's request: "Download, document and preserve
this. We may want to train our own models." Nothing here has been installed or run by Prometheus;
every capability claim below is the upstream project's own, not a Prometheus measurement.

## What it is

Soup is an Apache-2.0 Python CLI for fine-tuning and post-training existing LLMs from one YAML file
(`soup init`, `soup train`). It wraps the Hugging Face stack (torch, transformers, peft, trl,
datasets, bitsandbytes, accelerate) and adds:

- **Training tasks:** SFT, full fine-tune (`lora.r: 0`), pre-training, DPO, GRPO, PPO/RLHF, KTO,
  ORPO, SimPO, IPO, BCO, online DPO, process reward models (PRM) and PRM-guided GRPO, tool calling,
  classification, distillation (including cross-tokenizer), unlearning, vision/audio.
- **Small-GPU training:** QLoRA (NF4) and "layer streaming" (`training.stream_layers: true`, BETA),
  which keeps the frozen base in pinned RAM and streams one decoder layer at a time to the GPU.
  Upstream claim: Llama-3.1-8B LoRA at 3.32 GB peak VRAM on a 4 GB laptop card, bit-exact against a
  resident run (paper below). Upstream says the figure predates a v0.73.0 fix and is pending
  re-measurement (their issue #361).
- **PEFT zoo:** DoRA, LoRA+, LoRA-FA, rsLoRA, VeRA, OLoRA, PiSSA, ReLoRA, LISA, LongLoRA/YaRN, packing.
- **Instruments of interest to us:** fixed seeds, held-out validation reward for GRPO, a
  reward-hacking detector with auto-halt (InfoRM), data canaries for memorisation checks,
  influence-function "blame" of training rows, semantic dedup, an eval-design pipeline with
  held-out canaries, and `soup advise` (SFT vs DPO vs GRPO vs RAG vs prompting).
- **Export/serve:** LoRA merge, GGUF (llama.cpp), ONNX, TensorRT-LLM, Ollama deploy, batch inference.
- **Backends:** transformers (default), Unsloth, MLX (Apple), Modal cloud.

It fine-tunes existing open-weight base models (any `AutoModelForCausalLM` on the Hub). It is not
a from-scratch large-scale pre-training framework; base-model licences apply separately.

## Provenance

| Field | Value |
|---|---|
| Upstream | https://github.com/MakazhanAlpamys/Soup (site https://trysoup.dev, PyPI `soup-cli`) |
| Licence | Apache-2.0 (LICENSE + NOTICE in the tree) |
| Author | Alpamys Makazhan (about 1,150 of 1,797 commits); 22+ outside contributors in v0.75.0 |
| Repo created | 2026-02-20; last push 2026-10-09T19:53:10Z; 8,514 stars, 1,369 forks at capture |
| Captured `main` HEAD | `61e8c2bf354393cea85002401d0bde803b48f614` (2026-10-10 00:53 +0500), version string 0.75.0 + 612 commits |
| Latest release | v0.75.2 = `3966ef95cead56f500a67b1f68cbc84d22b11cfb` (branch `release/v0.75.2`); v0.75.0 = `f50a7da35277...` |
| Refs | 1,090 in the mirror (180 tags, branches, and GitHub pull-request refs) |
| Paper | "Exact Layer Streaming: LoRA Fine-Tuning of an 8B Model on a 4 GB Laptop GPU", A. Makazhan, Zenodo 2026-08-13, DOI 10.5281/zenodo.21771064 (record 21918325, file v3) |
| Status | upstream marks it Development Status 3 - Alpha; many features labelled BETA |

## Where the copy lives

Host M2 (SPECTREX5), `D:\Prometheus-vault\external\soup\` (about 130 MB, outside the git repo):

| Path | Contents |
|---|---|
| `Soup.git\` | `git clone --mirror`: every branch, tag and PR ref at capture |
| `Soup_61e8c2bf_2026-10-11.bundle` | single-file `git bundle --all` of the mirror (verified with `git bundle verify`) |
| `src\` | working checkout of `main` at `61e8c2bf` |
| `pypi\` | wheel + sdist for 0.75.0 and 0.75.2 from PyPI |
| `paper\` | `exact_layer_streaming_v3.pdf` + Zenodo record JSON |
| `releases\releases.json` | GitHub release notes, latest 100 (the releases carry no binary assets) |
| `SHA256SUMS` | hashes of the bundle, wheels, sdists, paper and release notes (copy beside this file) |

D: on M2 is a single SMR HDD with no redundancy. For a second copy, the bundle alone is enough:
copy `Soup_61e8c2bf_2026-10-11.bundle` + `SHA256SUMS` to another host.

Restore: `git clone Soup_61e8c2bf_2026-10-11.bundle Soup` (then `sha256sum -c SHA256SUMS` first).
Not preserved: the dependency wheels (torch etc.), model weights, issues and discussions.

## Fit for Prometheus hardware (to check before any use)

- **Python 3.10-3.12 only** (`requires-python = ">=3.10,<3.13"`). M2's default `python` is 3.14,
  so it needs its own 3.12 venv (`pipx`/`uv tool` as upstream recommends).
- **GPU:** M1/M2 have an RTX 5060 Ti 16 GB (Blackwell, compute 12.x). That needs a CUDA 12.8+ torch
  build; upstream's floor is torch >= 2.6 and its FP8 rowwise kernel needs torch >= 2.8 on RTX 50 and
  is never built on Windows. 16 GB fits plain QLoRA on 7-8B models without layer streaming.
- **Windows:** supported (upstream measured on an RTX 5070 laptop under Windows), with a documented
  `DLL load failed while importing _C` torch install pitfall (`docs/backends-and-ops.md`).

## Why it might matter

The likely use is training our own small models where Prometheus currently uses an off-the-shelf
one, e.g. a local mutation operator (Apollo used Granite-3.0-2B untrained), with GRPO on verifiable
rewards from our own falsification battery. If that happens, the gates stay ours: Soup's
reward-hacking detector, canaries and influence blame are upstream instruments and need the same
calibration on known truths as any Prometheus instrument before their verdicts count.
