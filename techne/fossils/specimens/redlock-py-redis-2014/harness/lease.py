import subprocess, time, sys
from redlock import Redlock
ports = [7401, 7402, 7403]
procs = [subprocess.Popen(["redis-server", "--port", str(p), "--save", "", "--appendonly", "no", "--loglevel", "warning"]) for p in ports]
time.sleep(1.5)
servers = [{"host": "127.0.0.1", "port": p, "db": 0} for p in ports]
A = Redlock(servers); B = Redlock(servers)
# A: the mechanism
la = A.lock("resource", 2000); print("A acquired:", bool(la), "validity_ms=%d" % (la.validity if la else 0))
lb = B.lock("resource", 2000); print("B while A valid:", bool(lb))
ok1 = bool(la) and not lb
A.unlock(la); lb = B.lock("resource", 2000); print("B after A released:", bool(lb)); ok1 = ok1 and bool(lb); B.unlock(lb)
print("mutual exclusion while valid:", "OK" if ok1 else "FAILED")
# B: the weakness -- a lease shorter than the holder's work
la = A.lock("resource", 300); print("A acquired short lease:", bool(la), "validity_ms=%d" % (la.validity if la else 0))
time.sleep(1.0)   # A 'works' (or is paused) longer than its lease
lb = B.lock("resource", 300); print("B acquires while A still thinks it holds:", bool(lb))
print("lease expired under a live holder" if (la and lb) else "no expiry observed")
for p in procs: p.kill()
sys.exit(0 if ok1 else 1)
