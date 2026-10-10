"""Mutation check for the runner suite (C-013-T022): each mutant disables one guard; the suite must fail.
Run from the worktree root: python rso/scale/runner/tests/mutation_check.py (restores every file)."""
import subprocess, sys, json, shutil
MUTS = [
 ("rso/scale/runner/run.py", 'h["generation"] == expected_generation and ', '', "publish: drop generation CAS"),
 ("rso/scale/runner/run.py", 'if not L.is_holder(run_dir, chain_id, lease_token):', 'if False:', "publish: drop lease fence"),
 ("rso/scale/runner/run.py", 'if h["state"] == HALTED:\n            return', 'if False:\n            return', "publish: ignore HALTED"),
 ("rso/scale/runner/run.py", 'if errs:\n        return', 'if False:\n        return', "publish: skip verify_epoch"),
 ("rso/scale/runner/resume.py", 'or not _replayed_before(run_dir, chain_id)', '', "resume: first resumption not replayed"),
 ("rso/scale/runner/resume.py", 'checks = {"environment": engine.probe() == m["environment"]}', 'checks = {"environment": True}', "resume: skip env probe"),
 ("rso/scale/runner/resume.py", 'RUN.halt(run_dir', 'None and RUN.halt(run_dir', "resume: mismatch does not halt"),
 ("rso/scale/runner/account.py", 'wasted["interrupted_attempts"] += 1', 'pass', "account: interrupted not counted"),
 ("rso/scale/runner/lease.py", 'if lease["host"] == S.HOST and not S.pid_alive', 'if False and not S.pid_alive', "lease: dead holder not detected"),
 ("rso/scale/runner/store.py", 'if hashlib.sha256(data).hexdigest() != sha:', 'if False:', "store: no verify on read"),
 ("rso/scale/runner/aether.py", 'tick += 1', 'tick += 0', "aether: tick not advanced"),
 ("rso/scale/runner/worker.py", 'expected_generation=h["generation"]', 'expected_generation=0', "worker: stale expected generation"),
 ("rso/scale/runner/supervisor.py", 'if holder is not None:', 'if False:', "supervisor: ignores live orphan lease"),
]
out=[]
for path, old, new, label in MUTS:
    src=open(path,encoding="utf-8").read()
    if old not in src:
        out.append({"mutant":label,"result":"NOT_APPLIED"}); continue
    open(path,"w",encoding="utf-8",newline="\n").write(src.replace(old,new,1))
    try:
        r=subprocess.run([sys.executable,"-m","unittest","discover","-s","rso/scale/runner/tests","-t","."],capture_output=True,text=True,timeout=300)
        tail=r.stderr.strip().splitlines()[-1]
        out.append({"mutant":label,"file":path,"result":"KILLED" if r.returncode else "SURVIVED","tail":tail})
    finally:
        open(path,"w",encoding="utf-8",newline="\n").write(src)
for o in out: print(o["result"], "|", o["mutant"], "|", o.get("tail",""))
json.dump(out,open("rso/scale/runner/evidence/MUTATION_TABLE.json","w"),indent=1)
