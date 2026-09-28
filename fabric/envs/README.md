# Fabric capability environments

A worker's `python.*` and `pin.*` capabilities are **probed** from the interpreter that runs its script executor
(`python -m fabric worker --probe`). They are never taken on trust. A declared capability that the environment
does not provide is dropped at start and logged (report defect D7).

- `python.<pkg>` means the package is importable, in any version.
- `pin.<pkg>==<version>` and `pin.python==<version>` mean that exact version. A procedure frozen on an
  environment must require the pins. A worker with another version then never claims the task: the task waits,
  and nothing runs "close enough".

## ubu001

| environment | interpreter | adds | probe | notes |
|---|---|---|---|---|
| system | `/usr/bin/python3` (3.14.4) | none | `ubu001-system.probe.json` | cryptography 46.0.5, psycopg2 2.9.11 from apt |
| sci | `~/fabric-venvs/sci/bin/python` (3.14.4, venv with system site-packages) | numpy 2.5.3, scipy 1.18.1 (`ubu001-sci.pip-local.txt`) | `ubu001-sci.probe.json` | user-owned, no sudo; created 2026-09-28 for the D2 self-tests |

To run the sci worker:

```
EW_DB_HOST=192.168.1.202 ~/fabric-venvs/sci/bin/python -m fabric worker --agent worker.ubu001.sci --executors script
```

**Not an exact environment for D2 or Cosmos procedures.** The D2 seal was drawn with numpy 2.2.6 on Python 3.12
(Windows). numpy 2.2.6 has no wheel for Python 3.14, so this venv cannot provide it. A task that needs the at-draw
environment must require `pin.numpy==2.2.6` (and `pin.python==3.12.10` if the interpreter matters), and it will
wait for a worker that has it (M1).
