# Telemetry schema

`prometheus-gpu/telemetry/1`

Authority: `prometheus_gpu/telemetry.py`. Enforced by
`Aether/test/test_prometheus_gpu.py`. Checked by:

```bash
python -m prometheus_gpu.cli validate-telemetry out/telemetry.jsonl
```

## Format

One JSON object per line, appended to `$PROMETHEUS_TELEMETRY_PATH`,
flushed after every record.

Append-only and per-line is not a stylistic choice. A run that dies
mid-flight leaves everything up to the last flush readable; a single
JSON document written at the end leaves nothing at all — and the run
that dies mid-flight is precisely the run telemetry exists for.

## Reserved keys

| key | type | meaning |
|:--|:--|:--|
| `kind` | string | **required.** What sort of record this is. |
| `t_utc` | string | **required.** UTC timestamp, `YYYY-MM-DDTHH:MM:SSZ`. |
| `t_elapsed_s` | number | **required.** Seconds since the run's monotonic origin. |
| `run_id` | string | the run this belongs to. |
| `seq` | int | monotonically increasing per writer; a gap means lost records. |
| `units` | number | work completed so far, in the module's `work_units.name`. |
| `message` | string | human text. |
| `level` | string | `debug` / `info` / `warning` / `error`. |

**Every other key belongs to the module.** Put your own metrics at the
top level with whatever names your science uses. The platform reserves
these eight names and imposes nothing further.

## Why two clocks

`t_utc` answers *when*; `t_elapsed_s` answers *how far in*. Both are
required, and a record missing either is refused.

The controller and the pod keep different clocks. A progress curve has
to be placeable against a cost curve, and doing that across two machines
needs an origin the pod itself agrees with. The UTC stamp alone cannot
provide it; the elapsed counter alone cannot be correlated with a
billing window.

## Kinds

`kind` is an open string. These have agreed meanings so that generic
tooling can summarise any module's run without knowing what it computes:

| kind | meaning |
|:--|:--|
| `start` | the workload began; may carry the module's plan |
| `progress` | periodic heartbeat carrying `units` so far |
| `event` | something discrete and notable happened |
| `warning` | degraded but continuing |
| `error` | a failure the module chose to report before exiting |
| `end` | the workload finished; carries final `units` and `status` |

## Writing telemetry

The library, if your module imports the platform:

```python
from prometheus_gpu import telemetry
w = telemetry.Writer(os.environ["PROMETHEUS_TELEMETRY_PATH"],
                     run_id=os.environ.get("PROMETHEUS_RUN_ID"))
w.emit("start", plan="3 phases x 50000 ticks")
w.emit("progress", units=25_000, my_own_metric=0.42)
w.emit("end", units=150_000, status="ok")
```

Or by hand, with no dependency at all — this is the whole contract:

```python
import json, os, time
origin = time.monotonic()
def emit(kind, **f):
    rec = {"kind": kind,
           "t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "t_elapsed_s": round(time.monotonic() - origin, 3)}
    rec.update(f)
    with open(os.environ["PROMETHEUS_TELEMETRY_PATH"], "a") as fh:
        fh.write(json.dumps(rec) + "\n"); fh.flush()
```

## Reading telemetry

`read_jsonl` tolerates exactly one kind of damage:

- an unparseable **last** line is dropped. A pod killed mid-write leaves
  a partial final record; that is normal and must not discard the run.
- an unparseable line **anywhere earlier** raises. A bad record in the
  middle means interleaved or corrupted writes, which is a different and
  worse problem than a lost tail, and silently skipping it would hide it.

## The summary

`summarise(records)` reduces any module's telemetry to a shape generic
tooling can use: `records`, `kinds`, `first_utc`, `last_utc`,
`elapsed_s`, `units_final`, `units_per_s`, `errors`, `warnings`,
`max_gap_s`, `complete`, `module_status`.

Two of those need care:

**`complete`** means *the module emitted an `end` record*. It does not
mean the pod exited, and it does not mean the run succeeded. Those are
three different facts and the receipt keeps them apart.

**`max_gap_s`** is the largest interval between consecutive records. A
mean rate hides a stall; the gap is usually the finding. An 88-second
gap in an otherwise steady run is where to start looking.

## Size

Telemetry travels back through the artifact channel, which serves at
most 8 MB and keeps the **first** 8 MB. An overrun therefore discards the
**end** of the run — the part you most want. At 250 B/record that is
~32,000 records; pick a cadence that fits, and sample rather than hope.
