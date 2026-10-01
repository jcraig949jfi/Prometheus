"""W2-35 s3: static assay of every ring rotation of the 7ae3 founder (x_s[(i+s) % 64] = F[i], s = 0..63) with the
W2-3 common harness (common.outcome, copy errors off, donor context ZERO) on the W2-24 / N17e realized-partner panel
(W2-14 BASE bank, N = 1000, rng 'N17e'). conv / keep are FID >= 0.9 to x_s itself, i.e. a child in the SAME frame.
Also: exact-child rate, and the founder-frame readout (does the partner half become FID >= 0.9 to the UNROTATED founder).
Prediction tested (from the founder's code, W2-35 Q1): frames that keep founder bytes 23..53 (SELF .. LDIR) contiguous
inside the half, i.e. s >= 41 or s <= 10, replicate; 11 <= s <= 40 do not.
python -B s3_frames_assay.py -> s3_frames_assay.json"""
import json, sys, time
sys.dont_write_bytecode = True
from frames import HERE, W2
sys.path.insert(0, str(W2 / "W2-24_keep_variant"))
from q1_trace import panel  # noqa: E402
from tvm import C  # noqa: E402


def rot_of(F, s):
    x = bytearray(64)
    for i in range(64):
        x[(i + s) % 64] = F[i]
    return bytes(x)


def assay(r, x, pan, F):
    k = [0, 0]; cv = [0, 0]; ex = [0, 0]; n = [0, 0]; f0 = 0
    for y, cy, cx, s in pan:
        o = C.outcome(r, x, y, s, C.ZERO, cy, 0.0, None)
        n[s] += 1; k[s] += o["keep"]; cv[s] += o["conv"]; ex[s] += o["ny"] == x
        f0 += C.FID(F, o["ny"]) >= 0.9
    N = sum(n)
    return {"keep_s0": round(k[0] / n[0], 3), "keep_s1": round(k[1] / n[1], 3),
            "conv_s0": round(cv[0] / n[0], 3), "conv_s1": round(cv[1] / n[1], 3),
            "exact_child": round(sum(ex) / N, 3), "m_base": round((sum(k) + sum(cv)) / N, 3),
            "founder_frame_children": f0}


if __name__ == "__main__":
    t0 = time.process_time()
    r = C.runner_for_spec(C.run_ds.DONOR)
    F = C.run_ds.donor_genome()
    pan = panel()
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    out = {}
    for s in range(lim):
        x = rot_of(F, s)
        a = assay(r, x, pan, F)
        a["pred_viable"] = s >= 41 or s <= 10
        out[s] = a
        print(s, a, flush=True)
    res = {"per_shift": out, "cpu_s": round(time.process_time() - t0, 1)}
    if lim == 64:
        (HERE / "s3_frames_assay.json").write_text(json.dumps(res, indent=1))
    print("cpu", res["cpu_s"])
