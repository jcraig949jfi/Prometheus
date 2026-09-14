import subprocess, sys
r = subprocess.run([sys.executable, "-m", "sgp4.tests"], capture_output=True, text=True)
out = (r.stdout + r.stderr)
print(out[-1500:])
import sgp4.api as api
print("accelerated:", api.accelerated)
lines = [l for l in out.splitlines() if l.strip()]
ok = r.returncode == 0 and lines and lines[-1].startswith("OK")
print("RESULT", "OK" if ok else "FAIL")
