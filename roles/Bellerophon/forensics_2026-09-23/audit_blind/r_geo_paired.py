"""geometry.scan is unpaired: base and each mutant are scored on DIFFERENT random inputs, so a mutant that is
byte-identical in behaviour is counted 'beneficial' whenever its 3 fresh inputs happen to score better."""
import sys, random
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import vm, geometry
from prometheus.z80atlas.world import Config
from prometheus.z80atlas.tasks import Task
# ECHO witness padded with 0xFF (HALT) filler: most single-byte substitutions in the filler are behaviourally NEUTRAL
tape = bytes(vm.witness_echo()) + bytes([vm.HALT]) * 61
for task, scoring in (("COND_ONE", "ATOMIC"), ("COND_MULTI", "ATOMIC"), ("ECHO", "INCREMENTAL")):
    cfg = Config(task=task, scoring=scoring, read_gate="ABR", reproduction="ENDOGENOUS_COPY")
    bd = [geometry.scan(tape, cfg, Task(task), seed, n=40)["beneficial_density"] for seed in range(200)]
    gains = [geometry.scan(tape, cfg, Task(task), s * 31, n=40)["beneficial_density"] - geometry.scan(tape, cfg, Task(task), s * 43, n=40)["beneficial_density"] for s in range(200)]
    print("%-10s %-11s same tape: beneficial_density mean %.3f range [%.3f, %.3f]; same-tape 'gain' > 0.1 in %d/200 seeds"
          % (task, scoring, sum(bd) / len(bd), min(bd), max(bd), sum(g > 0.1 for g in gains)))
