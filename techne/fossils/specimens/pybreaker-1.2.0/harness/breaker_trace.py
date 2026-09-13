import time, pybreaker
class L(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old, new):
        print("state %s->%s" % (old.name, new.name))
b = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=0.5, listeners=[L()])
healthy = {"v": False}
def dep():
    if not healthy["v"]:
        raise RuntimeError("dependency down")
    return "ok"
for i in range(3):
    try:
        b.call(dep)
    except Exception as e:
        print("call", i, "->", type(e).__name__, "state", b.current_state)
try:
    b.call(dep)
except pybreaker.CircuitBreakerError as e:
    print("fast-fail while open:", type(e).__name__, "(dependency NOT called)")
time.sleep(0.6)
healthy["v"] = True
print("probe after reset_timeout:", b.call(dep))
print("final", b.current_state)
