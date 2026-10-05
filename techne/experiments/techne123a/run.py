"""TECHNE-123A -- Open-Oasis 500M interactive-world qualification: the pod-side module.

Operator directive 8 (2026-10-05). Runs under Aether's prometheus_gpu platform (MODULE_CONTRACT.md):
no provider credential is ever visible here; the platform sets PROMETHEUS_ARTIFACT_DIR,
PROMETHEUS_TELEMETRY_PATH, PROMETHEUS_RUN_ID and the allowlisted TECHNE123A_* variables.

What it does, in order:
  1. fetch the two weight files from the ungated mirror and REFUSE to load either unless its sha256
     equals the OFFICIAL Etched/oasis-500m LFS hash recorded in oasis/PROVENANCE.json;
  2. load DiT-S/2 + ViT-VAE-L/20 exactly as the upstream generate.py does (vendored sources at the
     pinned commit, unmodified; see oasis/PROVENANCE.json);
  3. roll out the trajectories the PLAN asks for, with the upstream sampling loop reproduced line
     for line except that (a) the per-frame noise comes from a torch.Generator seeded per
     trajectory and (b) the latents are kept;
  4. write trajectories.npz (latents float16, decoded frames downsampled to 90x160 uint8, actions,
     per-frame seconds) and result.json (identity, hashes, device, timings, and the pairwise
     divergence curves computed here so the science survives even if the large artifact does not
     travel).

Plans (env TECHNE123A_PLAN): flight1 | flight2 | production. See ../TECHNE123A_PREREG_2026-10-05.md for
what each arm is for. Nothing here reads the internet except the two weight URLs.
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "oasis"))

ORIGIN = time.monotonic()
FORBIDDEN = ("RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN")

# Action vector layout (oasis/utils.py ACTION_KEYS): 25 entries.
IDX = {"forward": 11, "back": 12, "left": 13, "right": 14, "cameraX": 15, "cameraY": 16, "jump": 17}
N_ACTIONS = 25

PROV = json.load(open(os.path.join(HERE, "oasis", "PROVENANCE.json"), encoding="utf-8"))
MIRROR = "https://huggingface.co/%s/resolve/%s/" % (PROV["weights"]["mirror_used"]["repo"], PROV["weights"]["mirror_used"]["revision"])
OFFICIAL = PROV["weights"]["official"]["files"]


def telemetry(path, record):
    record.setdefault("t_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    record.setdefault("t_elapsed_s", round(time.monotonic() - ORIGIN, 3))
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
        fh.flush()


def fetch_verified(name, dest_dir, tel):
    """Stream one weight file from the mirror; the sha256 must equal the OFFICIAL hash or we stop."""
    want = OFFICIAL[name]["sha256"]
    dest = os.path.join(dest_dir, name)
    if os.path.exists(dest):
        h = hashlib.sha256()
        with open(dest, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 22), b""):
                h.update(chunk)
        if h.hexdigest() == want:
            return dest, "cached"
        os.remove(dest)
    url = MIRROR + name
    t0 = time.monotonic()
    h = hashlib.sha256()
    n = 0
    with urllib.request.urlopen(url, timeout=120) as r, open(dest + ".part", "wb") as out:
        while True:
            chunk = r.read(1 << 22)
            if not chunk:
                break
            h.update(chunk)
            out.write(chunk)
            n += len(chunk)
            if n % (1 << 28) < (1 << 22):
                telemetry(tel, {"kind": "download", "file": name, "bytes": n})
    got = h.hexdigest()
    if got != want or n != OFFICIAL[name]["bytes"]:
        raise RuntimeError("WEIGHTS_HASH_MISMATCH %s: got %s (%d bytes), official %s (%d bytes)"
                           % (name, got, n, want, OFFICIAL[name]["bytes"]))
    os.replace(dest + ".part", dest)
    return dest, "downloaded in %.1f s (%.1f MB/s)" % (time.monotonic() - t0, n / 1e6 / max(1e-6, time.monotonic() - t0))


# ----------------------------------------------------------------------------- actions
def actions_for(family, T):
    """(1, T, 25) float tensor; row 0 is the prompt frame and is all zeros, as upstream load_actions does."""
    import torch
    a = torch.zeros((T, N_ACTIONS))
    if family == "NOOP":
        pass
    elif family == "FWD":
        a[1:, IDX["forward"]] = 1.0
    elif family == "TURN":
        a[1:, IDX["cameraX"]] = 0.25            # +5 degrees of yaw per frame under upstream's camera binning
    elif family == "INTERVENE":
        a[1:, IDX["forward"]] = 1.0
        a[24:32, IDX["forward"]] = 0.0
        a[24:32, IDX["cameraX"]] = 0.5          # an 8-frame turn (about 80 degrees) in the middle of a walk
    else:
        raise ValueError(family)
    return a.unsqueeze(0)


# ----------------------------------------------------------------------------- rollout (upstream loop, seeded)
def rollout(model, vae, prompt_latent, actions, seed, T, ddim_steps, device, tel, label):
    import torch
    from einops import rearrange
    from torch import autocast
    from utils import sigmoid_beta_schedule

    max_noise_level = 1000
    noise_range = torch.linspace(-1, max_noise_level - 1, ddim_steps + 1)
    noise_abs_max = 20
    stabilization_level = 15
    betas = sigmoid_beta_schedule(max_noise_level).float().to(device)
    alphas_cumprod = rearrange(torch.cumprod(1.0 - betas, dim=0), "T -> T 1 1 1")

    gen = torch.Generator(device=device)
    gen.manual_seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    x = prompt_latent.clone()                   # (1, 1, C, h, w)
    actions = actions.to(device)
    B = 1
    per_frame_s = []
    for i in range(1, T):
        t_frame = time.monotonic()
        chunk = torch.randn((B, 1, *x.shape[-3:]), device=device, generator=gen)
        chunk = torch.clamp(chunk, -noise_abs_max, +noise_abs_max)
        x = torch.cat([x, chunk], dim=1)
        start_frame = max(0, i + 1 - model.max_frames)
        for noise_idx in reversed(range(1, ddim_steps + 1)):
            t_ctx = torch.full((B, i), stabilization_level - 1, dtype=torch.long, device=device)
            t = torch.full((B, 1), noise_range[noise_idx], dtype=torch.long, device=device)
            t_next = torch.full((B, 1), noise_range[noise_idx - 1], dtype=torch.long, device=device)
            t_next = torch.where(t_next < 0, t, t_next)
            t = torch.cat([t_ctx, t], dim=1)
            t_next = torch.cat([t_ctx, t_next], dim=1)
            x_curr = x.clone()[:, start_frame:]
            t = t[:, start_frame:]
            t_next = t_next[:, start_frame:]
            with torch.no_grad():
                with autocast("cuda", dtype=torch.half):
                    v = model(x_curr, t, actions[:, start_frame: i + 1])
            x_start = alphas_cumprod[t].sqrt() * x_curr - (1 - alphas_cumprod[t]).sqrt() * v
            x_noise = ((1 / alphas_cumprod[t]).sqrt() * x_curr - x_start) / (1 / alphas_cumprod[t] - 1).sqrt()
            alpha_next = alphas_cumprod[t_next]
            alpha_next[:, :-1] = torch.ones_like(alpha_next[:, :-1])
            if noise_idx == 1:
                alpha_next[:, -1:] = torch.ones_like(alpha_next[:, -1:])
            x_pred = alpha_next.sqrt() * x_start + x_noise * (1 - alpha_next).sqrt()
            x[:, -1:] = x_pred[:, -1:]
        torch.cuda.synchronize()
        per_frame_s.append(round(time.monotonic() - t_frame, 4))
        if i % 8 == 0 or i == T - 1:
            telemetry(tel, {"kind": "progress", "trajectory": label, "frame": i, "frame_s": per_frame_s[-1]})
    return x, per_frame_s


def decode_frames(vae, x, scaling_factor, device, chunk=8):
    """VAE decode in chunks -> (T, 3, 360, 640) float in [0,1] on CPU."""
    import torch
    from einops import rearrange
    T = x.shape[1]
    outs = []
    lat = rearrange(x, "b t c h w -> (b t) (h w) c")
    for s in range(0, T, chunk):
        with torch.no_grad():
            with torch.autocast("cuda", dtype=torch.half):
                y = (vae.decode(lat[s:s + chunk] / scaling_factor) + 1) / 2
        outs.append(torch.clamp(y.float(), 0, 1).cpu())
    return torch.cat(outs, dim=0)


def downsample(frames, h=90, w=160):
    import torch.nn.functional as F
    return (F.interpolate(frames, size=(h, w), mode="area") * 255).round().clamp(0, 255).to("cpu").numpy().astype("uint8").transpose(0, 2, 3, 1)


# ----------------------------------------------------------------------------- plans
def plan_for(name, T, seeds):
    """A list of (label, family, seed). Labels are unique; replicates carry the suffix _rep."""
    if name == "flight1":
        return [("FWD_s0", "FWD", 0), ("FWD_s0_rep", "FWD", 0), ("TURN_s0", "TURN", 0)]
    if name == "flight2":
        out = []
        for s in range(2):
            out += [("FWD_s%d" % s, "FWD", s), ("TURN_s%d" % s, "TURN", s), ("INTERVENE_s%d" % s, "INTERVENE", s)]
        out.append(("FWD_s0_rep", "FWD", 0))
        out.append(("NOOP_s0", "NOOP", 0))
        return out
    if name == "production":
        out = []
        for s in range(seeds):
            for fam in ("FWD", "TURN", "INTERVENE", "NOOP"):
                out.append(("%s_s%d" % (fam, s), fam, s))
        out += [("FWD_s0_rep", "FWD", 0), ("FWD_s1_rep", "FWD", 1), ("INTERVENE_s0_rep", "INTERVENE", 0)]
        return out
    raise ValueError(name)


def divergence(a_lat, b_lat, a_px, b_px):
    """Per-frame distances between two trajectories: latent MSE and downsampled pixel MAE (0..1)."""
    import numpy as np
    T = min(a_lat.shape[0], b_lat.shape[0])
    d_lat = [float(np.mean((a_lat[t].astype("float32") - b_lat[t].astype("float32")) ** 2)) for t in range(T)]
    d_px = [float(np.mean(np.abs(a_px[t].astype("float32") - b_px[t].astype("float32"))) / 255.0) for t in range(T)]
    return {"latent_mse": d_lat, "pixel_mae": d_px}


def pairs_for(labels):
    """Which pairs to compare: same-seed/same-family replicates (determinism), same-family different
    seeds (stochastic baseline), and counterfactual families against FWD at the same seed."""
    out = []
    base = {l for l in labels if not l.endswith("_rep")}
    for l in labels:
        if l.endswith("_rep") and l[:-4] in base:
            out.append(("REPLICATE", l[:-4], l))
    fwd = sorted(l for l in base if l.startswith("FWD_s"))
    for i in range(len(fwd)):
        for j in range(i + 1, len(fwd)):
            out.append(("SAME_ACTION_DIFF_SEED", fwd[i], fwd[j]))
    for l in base:
        if l.startswith(("TURN_s", "INTERVENE_s", "NOOP_s")):
            seed = l.split("_s")[-1]
            if "FWD_s%s" % seed in base:
                out.append(("COUNTERFACTUAL_" + l.split("_s")[0], "FWD_s%s" % seed, l))
    return out


def main():
    run_id = os.environ.get("PROMETHEUS_RUN_ID", "local")
    out_dir = os.environ.get("PROMETHEUS_ARTIFACT_DIR", os.path.join(HERE, "out"))
    tel = os.environ.get("PROMETHEUS_TELEMETRY_PATH", os.path.join(out_dir, "telemetry.jsonl"))
    os.makedirs(out_dir, exist_ok=True)
    leaked = [n for n in FORBIDDEN if os.environ.get(n)]
    if leaked:
        print("SECRETS_BOUNDARY_VIOLATION %s" % leaked, file=sys.stderr)
        return 92

    plan_name = os.environ.get("TECHNE123A_PLAN", "flight1")
    T = int(os.environ.get("TECHNE123A_T", "32"))
    seeds = int(os.environ.get("TECHNE123A_SEEDS", "6"))
    ddim = int(os.environ.get("TECHNE123A_DDIM", "10"))
    weights_dir = os.environ.get("TECHNE123A_WEIGHTS_DIR", "/app/weights")
    os.makedirs(weights_dir, exist_ok=True)

    import numpy as np
    import torch
    from einops import rearrange
    from torchvision.io import read_image
    from torchvision.transforms.functional import resize
    from dit import DiT_models
    from vae import VAE_models

    device = "cuda:0"
    dev_name = torch.cuda.get_device_name(0)
    result = {"schema": "techne123a/result/1", "run_id": run_id, "plan": plan_name, "T": T, "ddim_steps": ddim,
              "device": dev_name, "torch": torch.__version__, "cuda": torch.version.cuda,
              "cudnn_deterministic": bool(torch.backends.cudnn.deterministic),
              "provenance": PROV, "weights": {}, "trajectories": {}, "pairs": {}, "timing_s": {}}
    telemetry(tel, {"kind": "start", "run_id": run_id, "plan": plan_name, "T": T, "device": dev_name})

    t0 = time.monotonic()
    for name in ("oasis500m.pt", "vit-l-20.pt"):
        path, how = fetch_verified(name, weights_dir, tel)
        result["weights"][name] = {"sha256_official": OFFICIAL[name]["sha256"], "verified": True, "how": how}
        telemetry(tel, {"kind": "weights", "file": name, "how": how})
    result["timing_s"]["weights"] = round(time.monotonic() - t0, 1)

    t0 = time.monotonic()
    model = DiT_models["DiT-S/2"]()
    ckpt = torch.load(os.path.join(weights_dir, "oasis500m.pt"), weights_only=True, map_location="cpu")
    missing, unexpected = model.load_state_dict(ckpt, strict=False)      # upstream generate.py: strict=False for .pt
    result["weights"]["dit_load"] = {"missing_keys": len(missing), "unexpected_keys": len(unexpected),
                                     "missing_key_names": sorted(missing)[:64], "unexpected_key_names": sorted(unexpected)[:64]}
    model = model.to(device).eval()
    vae = VAE_models["vit-l-20-shallow-encoder"]()
    vae.load_state_dict(torch.load(os.path.join(weights_dir, "vit-l-20.pt"), weights_only=True, map_location="cpu"))
    vae = vae.to(device).eval()
    result["timing_s"]["load_models"] = round(time.monotonic() - t0, 1)
    result["model"] = {"max_frames": int(model.max_frames), "dit_params": sum(p.numel() for p in model.parameters()),
                       "vae_params": sum(p.numel() for p in vae.parameters())}
    telemetry(tel, {"kind": "loaded", "max_frames": int(model.max_frames), "load_s": result["timing_s"]["load_models"],
                    "gpu_mem_mib": int(torch.cuda.memory_allocated() / 2 ** 20)})

    # prompt -> latent, exactly as upstream (image prompt, resize to 360x640, VAE encode mean * scale)
    scaling_factor = 0.07843137255
    prompt = read_image(os.path.join(HERE, "oasis", "sample_image_0.png"))
    prompt = resize(rearrange(prompt, "c h w -> 1 c h w"), (360, 640)).float() / 255.0
    H, W = prompt.shape[-2:]
    with torch.no_grad():
        with torch.autocast("cuda", dtype=torch.half):
            z = vae.encode(prompt.to(device) * 2 - 1).mean * scaling_factor
    prompt_latent = rearrange(z, "(b t) (h w) c -> b t c h w", t=1, h=H // vae.patch_size, w=W // vae.patch_size)
    result["prompt"] = {"file": "oasis/sample_image_0.png", "sha256_lf": PROV["files"]["sample_image_0.png"]["sha256_lf"],
                        "latent_shape": list(prompt_latent.shape)}

    plan = plan_for(plan_name, T, seeds)
    lat_store, px_store = {}, {}
    t_all = time.monotonic()
    for label, family, seed in plan:
        t1 = time.monotonic()
        x, per_frame = rollout(model, vae, prompt_latent, actions_for(family, T), seed, T, ddim, device, tel, label)
        frames = decode_frames(vae, x, scaling_factor, device)
        px = downsample(frames)
        lat = x[0].detach().to(torch.float16).cpu().numpy()
        lat_store[label] = lat
        px_store[label] = px
        result["trajectories"][label] = {"family": family, "seed": seed, "frames": T,
                                         "gen_s": round(sum(per_frame), 2), "per_frame_s": per_frame,
                                         "total_s": round(time.monotonic() - t1, 2),
                                         "latent_sha256": hashlib.sha256(lat.tobytes()).hexdigest(),
                                         "pixels_sha256": hashlib.sha256(px.tobytes()).hexdigest()}
        telemetry(tel, {"kind": "trajectory_done", "trajectory": label, "units": len(result["trajectories"]) * (T - 1),
                        "gen_s": result["trajectories"][label]["gen_s"]})
    result["timing_s"]["all_trajectories"] = round(time.monotonic() - t_all, 1)

    for kind, a, b in pairs_for(list(lat_store)):
        result["pairs"]["%s|%s|%s" % (kind, a, b)] = dict(kind=kind, a=a, b=b, **divergence(lat_store[a], lat_store[b], px_store[a], px_store[b]))

    np.savez_compressed(os.path.join(out_dir, "trajectories.npz"),
                        **{"lat_" + k: v for k, v in lat_store.items()},
                        **{"px_" + k: v for k, v in px_store.items()},
                        **{"act_" + k: actions_for(result["trajectories"][k]["family"], T)[0].numpy() for k in lat_store})
    result["artifact_bytes"] = {"trajectories.npz": os.path.getsize(os.path.join(out_dir, "trajectories.npz"))}
    result["gpu_mem_peak_mib"] = int(torch.cuda.max_memory_allocated() / 2 ** 20)
    with open(os.path.join(out_dir, "result.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    telemetry(tel, {"kind": "end", "trajectories": len(lat_store), "units": len(lat_store) * (T - 1),
                    "npz_bytes": result["artifact_bytes"]["trajectories.npz"]})
    print("TECHNE123A_DONE plan=%s trajectories=%d device=%s" % (plan_name, len(lat_store), dev_name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
