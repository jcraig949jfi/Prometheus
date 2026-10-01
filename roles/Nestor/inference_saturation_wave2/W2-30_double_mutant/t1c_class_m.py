"""W2-30 T1c: 'class' m on the same N=1000 random-side panel as T1 (ZERO donor ctx): a half counts if FID>=0.9 to x
AND bytes 43,44,45,49 equal x's (the sites that distinguish F/C3/AC/5C/C3+AC). BASE and ATOMIC write-back."""
import json, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-24_keep_variant"))
from q1_trace import panel  # noqa: E402
from tvm import C  # noqa: E402
from t1_exact_m import G, r, n  # noqa: E402
from t1b_near_children import halves  # noqa: E402
CLS = (43, 44, 45, 49)
ok = lambda x, h: C.FID(x, h) >= 0.9 and all(h[i] == x[i] for i in CLS)
pan = panel()
out = {}
for nm, x in G.items():
    b = a = 0
    for y, cy, cx, s in pan:
        hb, ha = halves(x, y, s, C.ZERO, cy)
        b += sum(ok(x, h) for h in hb); a += sum(ok(x, h) for h in ha)
    out[nm] = {"m_base_class": b / len(pan), "m_atomic_class": a / len(pan)}
    print(nm, out[nm])
(HERE / "t1c_class_m.json").write_text(json.dumps(out, indent=1))
