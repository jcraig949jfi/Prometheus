import importlib.util, os, pathlib, shutil, subprocess, sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("fs", "first_sight.py"); fs = importlib.util.module_from_spec(spec); spec.loader.exec_module(fs)
HERE = pathlib.Path(".").resolve()
fix = {"R01": ('        if list(p["seeds"]) != list(registered_seeds):', '        if set(p["seeds"]) != set(registered_seeds):'),
       "R02": ('        if replayed != p["hits"]:', '        if replayed < p["hits"]:')}
ids = sys.argv[1:] or ["S03", "G04", "U03", "T01", "T02", "T03", "T04", "R01", "R02", "R06", "A01", "A02", "A10", "C01", "C03", "C04", "W02", "M02", "M03", "M04"]
byid = {m[0][:3]: m for m in fs.M}
def run(cwd, which, extra=()):
    r = subprocess.run([sys.executable, "-B", str(HERE / "witness.py"), which, *extra], cwd=str(cwd), capture_output=True, text=True,
                       env=dict(fs.ENV, PYTHONPATH=str(cwd)))
    return (r.stdout.strip() or (r.stderr.strip().splitlines() or ["?"])[-1])[:260]
W = HERE / "wit"
if W.exists(): shutil.rmtree(W)
W.mkdir()
for i in ids:
    name, fname, old, new = byid[i]
    if i in fix: old, new = fix[i]
    d = W / i
    shutil.copytree(HERE / "harness", d, ignore=shutil.ignore_patterns("__pycache__", "RECEIPT_*", "tests", "mutation_probe.py", "run_harness.py"))
    p = d / "rso_harness" / fname
    s = p.read_text(encoding="ascii"); assert s.count(old) == 1, (i, s.count(old))
    p.write_text(s.replace(old, new), encoding="ascii", newline="\n")
    a = run(HERE / "harness", i)
    extra = ()
    if i == "U03" and "scripted k = " in a:
        extra = (a.split("scripted k = ")[1].split(" ")[0],)
    b = run(d, i, extra)
    print("%-4s original: %s\n     changed : %s" % (i, a.split("-> ", 1)[-1], b.split("-> ", 1)[-1]))
shutil.rmtree(W, ignore_errors=True)
