"""Skullport concept images with SDXL base 1.0 (stabilityai/stable-diffusion-xl-base-1.0, CreativeML Open RAIL++-M).

The bundle carries only this script, its spec and our own prompt lists (prompts.json). The model is downloaded from
Hugging Face at boot. Work order:

  SKP_LIST     racefaces | garments | creatures      (which list in prompts.json)
  SKP_OFFSET   first image index (seed-major order: every entry's seed 0, then every entry's seed 1, ...)
  SKP_BATCH    "auto" (time batch sizes 4, 6, 8 on real work, then keep the fastest) or an integer
  PROMETHEUS_WORK_UNITS   how many images to make (a scout differs from its campaign only in this)

Sampler as our local ComfyUI workflow (tools/art/gfx/concept.py): DPM++ 2M Karras, CFG 6, 30 steps. Prompts longer
than one CLIP window are encoded in 75-token chunks and concatenated (as ComfyUI does) rather than truncated.
One torch.Generator per image, so an image depends on its seed and not on the batch it was made in.

Artifacts: images_0.tar .. images_3.tar (up to 200 PNGs each, plus that tar's manifest lines), manifest.jsonl,
timing.json, telemetry.jsonl.
"""

import io
import json
import os
import statistics
import sys
import tarfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

ORIGIN = time.monotonic()
FORBIDDEN = ("RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN")
MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
STEPS, CFG = 30, 6.0
PER_TAR, N_TARS = 200, 4
CANDIDATES = (4, 6, 8)
HERE = os.path.dirname(os.path.abspath(__file__))
SEQ = [0]


def telemetry(path, record):
    SEQ[0] += 1
    record.setdefault("t_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    record.setdefault("t_elapsed_s", round(time.monotonic() - ORIGIN, 3))
    record.setdefault("seq", SEQ[0])
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
        fh.flush()


def jobs_for(lst, offset, n):
    entries = json.load(open(os.path.join(HERE, "prompts.json"), encoding="utf-8"))["lists"][lst]
    order = []
    for k in range(max(len(e["seeds"]) for e in entries)):
        for e in entries:
            if k < len(e["seeds"]):
                order.append(dict(e, k=k, seed=e["seeds"][k]))
    return order[offset:offset + n], len(order)


def download(tel):
    """fp16 weights only (~7 GB); heartbeat telemetry while it runs so the controller sees progress."""
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")
    from huggingface_hub import snapshot_download
    box = {}

    def go():
        try:
            box["path"] = snapshot_download(MODEL, allow_patterns=[
                "model_index.json", "*/config.json", "scheduler/*", "tokenizer/*", "tokenizer_2/*",
                "unet/diffusion_pytorch_model.fp16.safetensors", "text_encoder/model.fp16.safetensors",
                "text_encoder_2/model.fp16.safetensors", "vae/diffusion_pytorch_model.fp16.safetensors"])
        except BaseException as exc:  # noqa: BLE001
            box["error"] = "%s: %s" % (type(exc).__name__, exc)

    t0 = time.monotonic()
    th = threading.Thread(target=go, daemon=True)
    th.start()
    while th.is_alive():
        th.join(15)
        if th.is_alive():
            telemetry(tel, {"kind": "progress", "units": 0, "phase": "download",
                            "elapsed_s": round(time.monotonic() - t0, 1)})
    if "error" in box:
        raise RuntimeError("model download failed: " + box["error"])
    return box["path"], time.monotonic() - t0


class Encoder:
    """SDXL prompt embeddings in 75-token chunks, both text encoders, pooled output from the first chunk."""

    def __init__(self, pipe):
        import torch
        self.torch = torch
        self.pipe = pipe
        self.cache = {}

    def _chunks(self, tok, text):
        ids = tok(text, add_special_tokens=False, truncation=False)["input_ids"]
        pieces = [ids[i:i + 75] for i in range(0, len(ids), 75)] or [[]]
        pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
        return [[tok.bos_token_id] + p + [tok.eos_token_id] + [pad] * (75 - len(p)) for p in pieces]

    def encode(self, text):
        if text in self.cache:
            return self.cache[text]
        torch = self.torch
        p = self.pipe
        c1, c2 = self._chunks(p.tokenizer, text), self._chunks(p.tokenizer_2, text)
        n = max(len(c1), len(c2))
        empty1, empty2 = self._chunks(p.tokenizer, "")[0], self._chunks(p.tokenizer_2, "")[0]
        c1 += [empty1] * (n - len(c1))
        c2 += [empty2] * (n - len(c2))
        embs, pooled = [], None
        with torch.no_grad():
            for i in range(n):
                a = p.text_encoder(torch.tensor([c1[i]], device="cuda"), output_hidden_states=True)
                b = p.text_encoder_2(torch.tensor([c2[i]], device="cuda"), output_hidden_states=True)
                if pooled is None:
                    pooled = b[0]
                embs.append(torch.cat([a.hidden_states[-2], b.hidden_states[-2]], dim=-1))
        out = (torch.cat(embs, dim=1), pooled)
        self.cache[text] = out
        return out

    def batch(self, texts):
        torch = self.torch
        enc = [self.encode(t) for t in texts]
        n = max(e[0].shape[1] for e in enc)
        empty = self.encode("")[0]
        embs = []
        for e, _ in enc:
            while e.shape[1] < n:
                e = torch.cat([e, empty], dim=1)
            embs.append(e)
        return torch.cat(embs, dim=0), torch.cat([e[1] for e in enc], dim=0)


def main():
    out_dir = os.environ.get("PROMETHEUS_ARTIFACT_DIR", "out")
    tel = os.environ.get("PROMETHEUS_TELEMETRY_PATH", os.path.join(out_dir, "telemetry.jsonl"))
    os.makedirs(out_dir, exist_ok=True)
    leaked = [n for n in FORBIDDEN if os.environ.get(n)]
    if leaked:
        print("SECRETS_BOUNDARY_VIOLATION %s" % leaked, file=sys.stderr)
        return 92
    run_id = os.environ.get("PROMETHEUS_RUN_ID", "unknown")
    lst = os.environ.get("SKP_LIST", "racefaces")
    offset = int(os.environ.get("SKP_OFFSET", "0"))
    n_units = int(float(os.environ.get("PROMETHEUS_WORK_UNITS", "48")))
    batch_cfg = os.environ.get("SKP_BATCH", "auto")
    jobs, list_total = jobs_for(lst, offset, min(n_units, PER_TAR * N_TARS))
    telemetry(tel, {"kind": "start", "run_id": run_id, "list": lst, "offset": offset, "images": len(jobs),
                    "list_total": list_total, "batch": batch_cfg, "model": MODEL, "steps": STEPS, "cfg": CFG})

    # every declared tar exists from the start (empty until filled), so a short run still has all its artifacts
    for i in range(N_TARS):
        with tarfile.open(os.path.join(out_dir, "images_%d.tar" % i), "w"):
            pass

    import torch
    from diffusers import DPMSolverMultistepScheduler, StableDiffusionXLPipeline
    path, dl_s = download(tel)
    revision = os.path.basename(path.rstrip("/"))
    telemetry(tel, {"kind": "event", "units": 0, "phase": "downloaded", "download_s": round(dl_s, 1),
                    "revision": revision})
    t0 = time.monotonic()
    pipe = StableDiffusionXLPipeline.from_pretrained(path, torch_dtype=torch.float16, variant="fp16",
                                                     use_safetensors=True)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
    pipe.to("cuda")
    pipe.enable_vae_slicing()
    pipe.set_progress_bar_config(disable=True)
    load_s = time.monotonic() - t0
    device = torch.cuda.get_device_name(0)
    mem_gb = torch.cuda.get_device_properties(0).total_memory / 2 ** 30
    telemetry(tel, {"kind": "event", "units": 0, "phase": "loaded", "load_s": round(load_s, 1), "device": device,
                    "gpu_mem_gb": round(mem_gb, 1)})
    enc = Encoder(pipe)

    pool = ThreadPoolExecutor(4)
    pending = []          # (job, future png bytes) in order
    state = {"tar_i": 0, "in_tar": 0, "tar": None, "done": 0}
    manifest = open(os.path.join(out_dir, "manifest.jsonl"), "a", encoding="utf-8")

    def open_tar():
        state["tar"] = tarfile.open(os.path.join(out_dir, "images_%d.tar.part" % state["tar_i"]), "w")
        state["in_tar"] = 0
        state["tar_lines"] = []

    def close_tar():
        t = state["tar"]
        if t is None:
            return
        data = "".join(state["tar_lines"]).encode("utf-8")
        ti = tarfile.TarInfo("%s/manifest_%d.jsonl" % (lst, state["tar_i"]))
        ti.size, ti.mtime = len(data), int(time.time())
        t.addfile(ti, io.BytesIO(data))
        t.close()
        os.replace(os.path.join(out_dir, "images_%d.tar.part" % state["tar_i"]),
                   os.path.join(out_dir, "images_%d.tar" % state["tar_i"]))
        state["tar"] = None
        state["tar_i"] += 1

    def drain(block):
        while pending and (block or pending[0][1].done()):
            job, fut = pending.pop(0)
            png = fut.result()
            if state["tar"] is None:
                open_tar()
            name = "%s/%s_%d.png" % (lst, job["id"], job["seed"])
            ti = tarfile.TarInfo(name)
            ti.size, ti.mtime = len(png), int(time.time())
            state["tar"].addfile(ti, io.BytesIO(png))
            rec = {"list": lst, "id": job["id"], "k": job["k"], "file": name, "seed": job["seed"],
                   "size": [job["w"], job["h"]], "prompt": job["prompt"], "negative": job["negative"],
                   "model": MODEL, "revision": revision, "steps": STEPS, "cfg": CFG,
                   "sampler": "DPMSolverMultistep karras (dpmpp_2m karras)", "dtype": "fp16",
                   "inputs": "text only", "run_id": run_id, "device": device,
                   "made_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            line = json.dumps(rec) + "\n"
            manifest.write(line)
            manifest.flush()
            state["tar_lines"].append(line)
            state["in_tar"] += 1
            state["done"] += 1
            if state["in_tar"] >= PER_TAR:
                close_tar()

    def encode_png(img):
        b = io.BytesIO()
        img.save(b, format="PNG", compress_level=4)
        return b.getvalue()

    def generate(batch):
        pe, pp = enc.batch([j["prompt"] for j in batch])
        ne, npool = enc.batch([j["negative"] for j in batch])
        if ne.shape[1] != pe.shape[1]:   # positive and negative must have the same sequence length
            n = max(ne.shape[1], pe.shape[1])
            empty = enc.encode("")[0].expand(len(batch), -1, -1)
            while pe.shape[1] < n:
                pe = torch.cat([pe, empty], dim=1)
            while ne.shape[1] < n:
                ne = torch.cat([ne, empty], dim=1)
        gens = [torch.Generator("cuda").manual_seed(j["seed"]) for j in batch]
        return pipe(prompt_embeds=pe, pooled_prompt_embeds=pp, negative_prompt_embeds=ne,
                    negative_pooled_prompt_embeds=npool, num_inference_steps=STEPS, guidance_scale=CFG,
                    width=batch[0]["w"], height=batch[0]["h"], generator=gens).images

    # batch plan: auto = warm-up of 2, then 4, 8, 6, 4, 8, 6 measured, then the fastest; fixed = that size
    timings = {}   # size -> [s per image]
    oom = set()
    if batch_cfg == "auto":
        plan = [2] + [4, 8, 6, 4, 8, 6]
    else:
        plan = [int(batch_cfg)]
    best = None
    i = 0
    step = 0
    t_gen0 = time.monotonic()
    while i < len(jobs):
        if step < len(plan):
            size = plan[step]
        else:
            if best is None:
                fair = {s: statistics.median(v) for s, v in timings.items() if v and s != 2 and s not in oom}
                best = min(fair, key=fair.get) if fair else 2
                telemetry(tel, {"kind": "event", "units": state["done"], "phase": "batch_chosen", "batch": best,
                                "s_per_image_by_batch": {str(k): round(v, 3) for k, v in fair.items()}})
            size = best
        step += 1
        if size in oom:
            continue
        batch = jobs[i:i + size]
        tb = time.monotonic()
        try:
            imgs = generate(batch)
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if size <= 2:
                raise
            oom.add(size)
            if best == size:
                best = 2
            telemetry(tel, {"kind": "warning", "units": state["done"], "message": "OOM at batch %d" % size})
            continue
        dt = time.monotonic() - tb
        if len(batch) == size:
            timings.setdefault(size, []).append(dt / size)
        for j, img in zip(batch, imgs):
            pending.append((j, pool.submit(encode_png, img)))
        i += len(batch)
        drain(False)
        telemetry(tel, {"kind": "progress", "units": state["done"], "generated": i, "batch": size,
                        "batch_s": round(dt, 3), "s_per_image": round(dt / len(batch), 3),
                        "vram_peak_gb": round(torch.cuda.max_memory_allocated() / 2 ** 30, 2)})
    drain(True)
    close_tar()
    manifest.close()
    gen_s = time.monotonic() - t_gen0
    summary = {"run_id": run_id, "list": lst, "offset": offset, "images": state["done"], "device": device,
               "download_s": round(dl_s, 1), "load_s": round(load_s, 1), "generate_wall_s": round(gen_s, 1),
               "wall_s_per_image": round(gen_s / max(1, state["done"]), 3),
               "s_per_image_by_batch": {str(k): {"median": round(statistics.median(v), 3), "n": len(v)}
                                        for k, v in timings.items()},
               "batch_chosen": best or (int(batch_cfg) if batch_cfg != "auto" else None),
               "oom_batches": sorted(oom), "next_offset": offset + state["done"], "list_total": list_total,
               "revision": revision}
    with open(os.path.join(out_dir, "timing.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
    telemetry(tel, {"kind": "end", "units": state["done"], "status": "ok", **summary})
    print("SKP_SDXL_OK " + json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
