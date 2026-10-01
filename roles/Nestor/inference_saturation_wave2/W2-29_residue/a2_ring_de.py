"""W2-29 a2: DECLARED DEVIATION. The pre-registered confirmation (first own LDIR dst == 0x40) is too literal: the z8 VM masks
every address with (size-1) on the 128-byte pair tape (z8.py:169-207), so DE = 0xC0, 0x1C0, 0x4040, 0xD7C0 ... all write to
absolute 64. Re-run a1's rule with confirmed := side0 and (dst & 127) == 64. Also a functional-only variant (side0 alone).
Writes c1_classes_ring.json / c1_classes_func.json and a2_<variant>.json; a1 logic reused unchanged via a classes swap."""
import json, shutil, subprocess, sys, pathlib, os
HERE = pathlib.Path(__file__).resolve().parent
c = json.load(open(HERE / "c1_classes.json"))
ring = {h: dict(v, confirmed=bool(v["side0"] and v["de"] is not None and (v["de"] & 127) == 64)) for h, v in c.items()}
func = {h: dict(v, confirmed=bool(v["side0"])) for h, v in c.items()}
print("confirmed literal", sum(v["confirmed"] for v in c.values()), "ring", sum(v["confirmed"] for v in ring.values()),
      "func", sum(v["confirmed"] for v in func.values()))
orig = HERE / "c1_classes.json"
bak = HERE / "c1_classes_literal.json"
shutil.copy(orig, bak)
try:
    for name, cl in (("ring", ring), ("func", func)):
        json.dump(cl, open(orig, "w"))
        o = subprocess.run([sys.executable, "-B", str(HERE / "a1_analyze.py")], capture_output=True, text=True, cwd=HERE)
        shutil.copy(HERE / "a1_analysis.json", HERE / ("a2_%s.json" % name))
        print("=====", name); print(o.stdout[:4000]); print(o.stderr[-2000:])
finally:
    shutil.copy(bak, orig)
    subprocess.run([sys.executable, "-B", str(HERE / "a1_analyze.py")], capture_output=True, cwd=HERE)  # restore literal a1
