import subprocess, sys, re
A = ["-a", "-n", "-i", "120", "--volume", "40", "--power", "6.0", "--ambient", "20", "--sampletime", "5", "-s", "45"]
B = ["-a", "-n", "-i", "120", "--volume", "10", "--power", "2.0", "--ambient", "20", "--sampletime", "5", "-s", "45"]
def run(args):
    r = subprocess.run([sys.executable, "sim.py"] + args, capture_output=True, text=True)
    out = r.stdout + r.stderr
    kp = None
    m = re.search(r"rule: ziegler-nichols\s*\nKp: ([0-9.eE+-]+)\s*\nKi: ([0-9.eE+-]+)\s*\nKd: ([0-9.eE+-]+)", out)
    if m: kp = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    return out, kp
which = sys.argv[1]
if which in ("A", "B"):
    out, kp = run(A if which == "A" else B); print(out[-4000:])
else:
    oa, ka = run(A); ob, kb = run(B)
    print("ziegler-nichols (Kp, Ki, Kd) kettle A = %s ; kettle B = %s" % (ka, kb))
    ok = ka is not None and kb is not None and abs(ka[2] - kb[2]) / max(abs(ka[2]), abs(kb[2]), 1e-9) > 0.20
    print("RESULT", "OK" if ok else "FAIL")
