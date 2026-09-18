"""TECHNE-107 -- ASAL's open-endedness score through CLIP: metric exploitability vs observer regularisation.

Preregistered: techne/acquisition/poet_alife/PREREG_TECHNE107_ASAL_OBSERVER_2026-09-17.md (on main
BEFORE this ran). Instrument:
  score      ASAL calc_open_endedness_score (SakanaAI/asal@677ba0ea asal_metrics.py:53), numpy port
  observer   OpenAI CLIP ViT-B/32 image features, L2-normalised (foundation_models/clip.py embed_img
             semantics: 224x224, CLIP mean/std) -- via the openai `clip` package on torch CPU because
             this host has no AVX and jaxlib will not load
  substrate  Lenia (Chan 2019) in numpy, ported from Chakazul/Lenia@adfc5429 Python/LeniaND.py
             (kernel_core[0] quad4, growth_func[0] quad4, rle2arr, kernel_shell, FFT convolution,
             clip update); pattern Orbium unicaudatus 'O2u' from Python/animals.json
Run:  <isolated env python> techne/scripts/techne107_asal_observer.py --out <receipt.json> --frames <dir>
The receipt carries every version, hash, seed, per-arm score and the P1-P6 verdicts computed against
the preregistered thresholds. Nothing here reads the operator's or ASAL's data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import platform
import re
import sys
import time

import numpy as np

T_FRAMES = 8
IMG = 224
WORLD = 128
STEPS = 256

# --------------------------------------------------------------------------- ASAL metric (numpy port)
def open_endedness_score(z: np.ndarray) -> float:
    """asal_metrics.py:53 -- kernel = z z^T; lower triangle k=-1; max per row; mean. Lower = more open-ended."""
    k = z @ z.T
    k = np.tril(k, k=-1)
    return float(k.max(axis=-1).mean())


# --------------------------------------------------------------------------- Lenia (numpy port of LeniaND.py)
def ch2val(c: str) -> int:
    if c in ".b":
        return 0
    if c == "o":
        return 255
    if len(c) == 1:
        return ord(c) - ord("A") + 1
    return (ord(c[0]) - ord("p")) * 24 + (ord(c[1]) - ord("A") + 25)


def rle2arr_2d(st: str) -> np.ndarray:
    """Board.rle2arr for DIM=2: '$' ends a row; digits repeat the next token; p..y prefix a 2-char token."""
    rows, row, count, last = [], [], "", ""
    st = st.rstrip("!") + "$"
    for ch in st:
        if ch.isdigit():
            count += ch
        elif ch in "pqrstuvwxy@":
            last = ch
        else:
            tok = last + ch
            if tok == "$":
                rows.append(row)
                if count:
                    rows.extend([[] for _ in range(int(count) - 1)])
                row = []
            else:
                v = ch2val(tok) / 255.0
                row.extend([v] * (int(count) if count else 1))
            last, count = "", ""
    w = max(len(r) for r in rows)
    return np.array([r + [0.0] * (w - len(r)) for r in rows], dtype=np.float64)


KERNEL_CORE = {0: lambda r: (4 * r * (1 - r)) ** 4, 1: lambda r: np.exp(4 - 1 / (r * (1 - r)))}
GROWTH = {0: lambda n, m, s: np.maximum(0, 1 - (n - m) ** 2 / (9 * s ** 2)) ** 4 * 2 - 1,
          1: lambda n, m, s: np.exp(-(n - m) ** 2 / (2 * s ** 2)) * 2 - 1}


class Lenia2D:
    def __init__(self, size: int, params: dict):
        self.size = size
        self.p = params
        R = params["R"]
        mid = size // 2
        y, x = np.mgrid[0:size, 0:size]
        D = np.sqrt(((x - mid) / R) ** 2 + ((y - mid) / R) ** 2)
        b = np.asarray([float(f) for f in str(params["b"]).split(",")])
        B = len(b)
        Br = B * D
        bs = b[np.minimum(np.floor(Br).astype(int), B - 1)]
        with np.errstate(divide="ignore", invalid="ignore"):
            kfunc = KERNEL_CORE[params.get("kn", 1) - 1]
            K = (D < 1) * np.nan_to_num(kfunc(np.minimum(Br % 1, 1))) * bs
        self.kernel = K / K.sum()
        self.kernel_fft = np.fft.fft2(self.kernel)
        self.gfunc = GROWTH[params.get("gn", 1) - 1]

    def place(self, pattern: np.ndarray) -> np.ndarray:
        A = np.zeros((self.size, self.size))
        h, w = pattern.shape
        y0, x0 = (self.size - h) // 2, (self.size - w) // 2
        A[y0:y0 + h, x0:x0 + w] = pattern
        return A

    def step(self, A: np.ndarray) -> np.ndarray:
        dt = 1.0 / self.p["T"]
        pot = np.fft.fftshift(np.real(np.fft.ifft2(self.kernel_fft * np.fft.fft2(A))))
        return np.clip(A + dt * self.gfunc(pot, self.p["m"], self.p["s"]), 0, 1)


# --------------------------------------------------------------------------- rendering / arms
def resize_bilinear(img: np.ndarray, size: int) -> np.ndarray:
    from PIL import Image
    arr = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    return np.asarray(Image.fromarray(arr).resize((size, size), Image.BILINEAR)).astype(np.float64) / 255.0


def grey_to_rgb(a: np.ndarray) -> np.ndarray:
    return resize_bilinear(np.repeat(a[:, :, None], 3, axis=2), IMG)


def lenia_frames(orbium_cells: str, params: dict) -> tuple[np.ndarray, list]:
    sim = Lenia2D(WORLD, params)
    A = sim.place(rle2arr_2d(orbium_cells))
    frames, mass = [], []
    sample_at = [(STEPS // T_FRAMES) * i for i in range(T_FRAMES)]   # rollout.py time_sampling=(8, False)
    for t in range(STEPS):
        if t in sample_at:
            frames.append(grey_to_rgb(A)); mass.append(float(A.sum()))
        A = sim.step(A)
    return np.stack(frames), mass + [float(A.sum())]


def ellipse_scene(rng: np.random.Generator) -> np.ndarray:
    img = np.full((IMG, IMG, 3), rng.random(3), dtype=np.float64)
    yy, xx = np.mgrid[0:IMG, 0:IMG]
    for _ in range(int(rng.integers(3, 8))):
        cx, cy = rng.random(2) * IMG
        ax, ay = rng.random(2) * 60 + 10
        th = rng.random() * math.pi
        xr = (xx - cx) * math.cos(th) + (yy - cy) * math.sin(th)
        yr = -(xx - cx) * math.sin(th) + (yy - cy) * math.cos(th)
        mask = (xr / ax) ** 2 + (yr / ay) ** 2 <= 1
        img[mask] = rng.random(3)
    return img


def blob_frame(shift: int) -> np.ndarray:
    yy, xx = np.mgrid[0:IMG, 0:IMG]
    cx, cy = 60 + shift, 112
    g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * 18.0 ** 2)))
    return np.repeat(g[:, :, None], 3, axis=2)


def tint(frame: np.ndarray, hue: float) -> np.ndarray:
    """A pure hue colour at full saturation/value, multiplied into a greyscale frame ('HUECYCLE': the
    preregistered 'hue rotation' has no effect on greyscale, so the frame is TINTED with a rotating hue)."""
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 1.0, 1.0)
    return frame * np.array([r, g, b])[None, None, :]


# --------------------------------------------------------------------------- CLIP observer
class Observer:
    def __init__(self):
        import clip, torch
        self.torch = torch
        self.model, _ = clip.load("ViT-B/32", device="cpu", jit=False)
        self.model.eval()
        self.mean = torch.tensor([0.48145466, 0.4578275, 0.40821073]).view(1, 3, 1, 1)
        self.std = torch.tensor([0.26862954, 0.26130258, 0.27577711]).view(1, 3, 1, 1)
        self.weights_sha256 = None
        cache = os.path.expanduser("~/.cache/clip/ViT-B-32.pt")
        if os.path.exists(cache):
            self.weights_sha256 = hashlib.sha256(open(cache, "rb").read()).hexdigest()

    def embed(self, frames: np.ndarray) -> np.ndarray:
        """frames (T, 224, 224, 3) in [0,1] -> (T, 512) L2-normalised, as clip.py embed_img()."""
        torch = self.torch
        x = torch.from_numpy(np.ascontiguousarray(frames)).float().permute(0, 3, 1, 2)
        x = (x - self.mean) / self.std
        with torch.no_grad():
            z = self.model.encode_image(x).float().numpy()
        return z / np.linalg.norm(z, axis=-1, keepdims=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--animals", default=None, help="Chakazul/Lenia Python/animals.json; default = the vault body of specimen lenia-chan-2019 (Harmonia #429: the fixture comes from the packet, never from a temp directory)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", default=None, help="directory for contact-sheet PNGs (evidence)")
    ap.add_argument("--seeds", type=int, default=5)
    a = ap.parse_args()
    t0 = time.time()
    if a.animals is None:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
        from techne.fossils import vault as _vault
        a.animals = str(_vault.body_dir("lenia-chan-2019") / "upstream" / "tree" / "Python" / "animals.json")
    animals = json.load(open(a.animals, encoding="utf-8"))
    orb = next(e for e in animals if isinstance(e, dict) and e.get("code") == "O2u")
    params = dict(orb["params"]); params["b"] = str(params["b"])
    obs = Observer()

    receipt = {"schema": "techne.acquisition.experiment_receipt/1", "id": "TECHNE-107",
               "prereg": "techne/acquisition/poet_alife/PREREG_TECHNE107_ASAL_OBSERVER_2026-09-17.md",
               "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "host": platform.node(),
               "observer": {"model": "openai clip ViT-B/32 via the `clip` package", "weights_sha256": obs.weights_sha256,
                            "torch": obs.torch.__version__, "python": platform.python_version()},
               "substrate": {"lenia_reference": "Chakazul/Lenia@adfc542939266de7f4bb7ebb552e8499701ee107 Python/LeniaND.py (numpy port in this script)",
                             "animals_json_sha256": hashlib.sha256(open(a.animals, "rb").read()).hexdigest(),
                             "pattern": {"code": orb["code"], "params": orb["params"]}, "world": WORLD, "steps": STEPS,
                             "frames": T_FRAMES, "sampling": "rollout.py time_sampling=(8, False): steps 0,32,...,224",
                             "note": "ASAL's own JAX Lenia not used: this host has no AVX and jaxlib refuses to load"},
               "metric": "asal_metrics.py:53 calc_open_endedness_score, numpy port; LOWER = more open-ended",
               "arms": {}, "controls": {}, "predictions": {}, "indeterminate": []}

    lenia, mass = lenia_frames(orb["cells"], params)
    receipt["substrate"]["mass_per_sampled_frame_and_final"] = [round(m, 3) for m in mass]
    alive = mass[-1] > 0.5 * mass[0] and mass[-1] > 1.0
    if not alive:
        receipt["indeterminate"].append("LENIA: pattern did not survive to step 256 (mass %s); P3/P4/P6 not read" % mass)

    def arm(name, frames, seed=None):
        z = obs.embed(frames)
        s = open_endedness_score(z)
        key = name if seed is None else "%s_seed%d" % (name, seed)
        receipt["arms"][key] = {"score": round(s, 6), "n_frames": int(frames.shape[0])}
        return s

    scores = {}
    scores["LENIA"] = arm("LENIA", lenia)
    scores["STATIC"] = arm("STATIC", np.repeat(lenia[:1], T_FRAMES, axis=0))
    scores["CYCLE2"] = arm("CYCLE2", np.stack([lenia[0] if i % 2 == 0 else lenia[4] for i in range(T_FRAMES)]))
    scores["HUECYCLE"] = arm("HUECYCLE", np.stack([tint(lenia[0], i / T_FRAMES) for i in range(T_FRAMES)]))
    scores["DRIFT_SYN"] = arm("DRIFT_SYN", np.stack([blob_frame(6 * i) for i in range(T_FRAMES)]))
    for nm, gen in (("NOISE", lambda rng: np.stack([rng.random((IMG, IMG, 3)) for _ in range(T_FRAMES)])),
                    ("GARBAGE", lambda rng: np.stack([ellipse_scene(rng) for _ in range(T_FRAMES)]))):
        vals = [arm(nm, gen(np.random.default_rng(1000 + i)), seed=i) for i in range(a.seeds)]
        scores[nm] = float(np.mean(vals)); receipt["arms"][nm] = {"mean": round(float(np.mean(vals)), 6), "sd": round(float(np.std(vals)), 6), "n": a.seeds}
    # controls
    cheat = arm("CHEAT_identical_as_distinct", np.repeat(ellipse_scene(np.random.default_rng(7))[None], T_FRAMES, axis=0))
    receipt["controls"]["cheat_8_identical_images"] = {"score": round(cheat, 6), "expected": round((T_FRAMES - 1) / T_FRAMES, 6),
                                                       "pass": abs(cheat - (T_FRAMES - 1) / T_FRAMES) < 1e-3}
    # predictions, verdicts computed exactly as preregistered
    L = scores["LENIA"]
    P = receipt["predictions"]
    P["P1_static_equals_0.8750"] = {"value": scores["STATIC"], "pass": abs(scores["STATIC"] - 0.875) < 1e-3}
    P["P2_noise_above_0.60"] = {"value": scores["NOISE"], "pass": scores["NOISE"] > 0.60, "kill_noise_below_lenia": scores["NOISE"] < L}
    P["P3_garbage_below_lenia"] = {"garbage": scores["GARBAGE"], "lenia": L, "pass": scores["GARBAGE"] < L}
    P["P4_cycle2_between_static_and_lenia"] = {"value": scores["CYCLE2"], "pass": L <= scores["CYCLE2"] <= scores["STATIC"], "kill_cycle_below_lenia": scores["CYCLE2"] < L}
    P["P5_huecycle_below_static"] = {"value": scores["HUECYCLE"], "pass": scores["HUECYCLE"] < scores["STATIC"], "vs_lenia": "below" if scores["HUECYCLE"] < L else "above"}
    P["P6_driftsyn_within_0.05_of_lenia"] = {"value": scores["DRIFT_SYN"], "delta": round(scores["DRIFT_SYN"] - L, 6), "pass": abs(scores["DRIFT_SYN"] - L) <= 0.05, "kill_over_0.10": abs(scores["DRIFT_SYN"] - L) > 0.10}
    if not alive:
        for k in ("P3_garbage_below_lenia", "P4_cycle2_between_static_and_lenia", "P6_driftsyn_within_0.05_of_lenia"):
            P[k]["read"] = False
    receipt["ordering_low_to_high"] = sorted(scores, key=scores.get)
    receipt["seconds"] = round(time.time() - t0, 1)

    if a.frames:
        from PIL import Image
        d = pathlib.Path(a.frames); d.mkdir(parents=True, exist_ok=True)
        for nm, fr in (("LENIA", lenia), ("HUECYCLE", np.stack([tint(lenia[0], i / T_FRAMES) for i in range(T_FRAMES)])),
                       ("GARBAGE_seed0", np.stack([ellipse_scene(np.random.default_rng(1000)) for _ in range(T_FRAMES)])),
                       ("NOISE_seed0", np.stack([np.random.default_rng(1000).random((IMG, IMG, 3)) for _ in range(T_FRAMES)]))):
            sheet = np.concatenate([resize_bilinear(f, 112) for f in fr], axis=1)
            p = d / ("%s_contact.png" % nm)
            Image.fromarray((sheet * 255).astype(np.uint8)).save(p)
            receipt.setdefault("evidence_frames", {})[nm] = {"path": str(p).replace("\\", "/"), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(receipt, indent=1) + "\n", encoding="utf-8")
    for k in receipt["ordering_low_to_high"]:
        print("%-10s %.4f" % (k, scores[k]))
    print("cheat", receipt["controls"]["cheat_8_identical_images"])
    for k, v in P.items():
        print(k, v)
    print("RECEIPT", a.out, "%.1fs" % receipt["seconds"])


if __name__ == "__main__":
    main()
