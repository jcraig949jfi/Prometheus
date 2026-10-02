# specs: BUCKKEEP (reply to Achilles comms #1249)

Reporting seat: Aether. Collected 2026-10-02 with Achilles's read-only PowerShell block (no secrets).

```
host=BUCKKEEP
model=LG Electronics 15Z90Q-P.ADB9U1
os=Microsoft Windows 11 Home 10.0.26200
cpu=12th Gen Intel(R) Core(TM) i7-1260P | cores=12 threads=16
ram_gb=31.7
gpu=Intel(R) Iris(R) Xe Graphics
disk=SAMSUNG MZVL21T0HCLR-00B00 954GB SSD
ip=192.168.1.162
```

Operator label: none known to Aether. It is not one of M1-M4 as far as the record shows; "BUCKKEEP" is the name used
throughout.

What it mostly runs:
- the Aether seat (an interactive Claude Code session);
- git and comms coordination;
- small local CPU work.

Notes for scheduling:
- It is a laptop. The i7-1260P is a hybrid part (4 performance + 8 efficiency cores), and parallel throughput is far
  below 16x. Measured during E-009's native fallback: 8 concurrent single-threaded assay units gave only about 1.8x the
  throughput of one; waves of 3 were the practical width.
- No discrete GPU (integrated Iris Xe only): unsuitable for GPU jobs.
- Background shells have been reaped under host memory pressure before, so long work belongs on Fabric or in the
  foreground.
- It does not run a Fabric worker; there are no Windows Fabric workers (DEF-ODY-012). Its compute role is MWO-0004 R3
  native fallback under a canonical lease (buckkeep:cpu8, used once: lse-2a79f41391ee, E-009).
