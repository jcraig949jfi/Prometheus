"""Techne harness: compare libDAI's exact (junction tree) and loopy-BP variable marginals from
examples/example's output. The sprinkler network is LOOPY (Cloudy -> Sprinkler, Cloudy -> Rain,
both -> WetGrass), so BP is exact on the upstream variables and inexact on WetGrass: that is the
documented behaviour of loopy BP, and the oracle checks exactly that shape."""
import re, sys
txt = open(sys.argv[1], encoding="utf-8", errors="replace").read()


def block(title):
    i = txt.find(title)
    if i < 0:
        return None
    lines = txt[i:].splitlines()[1:]
    out = []
    for l in lines:
        if not l.strip().startswith("("):
            break
        nums = re.findall(r"\(([0-9.eE+-]+), ([0-9.eE+-]+)\)", l)
        if nums:
            out.append((float(nums[-1][0]), float(nums[-1][1])))
    return out


ex = block("Exact variable marginals:")
bp = block("Approximate (loopy belief propagation) variable marginals:")
print("exact:", ex)
print("bp:   ", bp)
if not ex or not bp or len(ex) != len(bp):
    print("RESULT FAIL (could not parse both blocks)"); sys.exit(1)
diffs = [max(abs(a - b) for a, b in zip(x, y)) for x, y in zip(ex, bp)]
print("per-variable max |bp - exact|:", ["%.4f" % d for d in diffs])
upstream_exact = all(d < 1e-6 for d in diffs[:3])
wetgrass_inexact = diffs[3] > 0.01
print("x0..x2 (Cloudy, Sprinkler, Rain) agree to 1e-6:", upstream_exact)
print("x3 (WetGrass, inside the loop) differs by %.4f: loopy BP is inexact here, as documented" % diffs[3])
print("RESULT", "OK" if (upstream_exact and wetgrass_inexact) else "FAIL")
