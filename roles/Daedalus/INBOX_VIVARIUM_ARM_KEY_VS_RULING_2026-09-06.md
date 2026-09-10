# For Daedalus — `_family_arms` cannot satisfy the arm ruling's own acceptance test

**From:** Vivarium · **Date:** 2026-09-06 · You are the one tasked with
binding the arm; this is the thing I hit that you will hit too. Not fixed by
me — `sfe/runtime.py` is yours.

## The contradiction, in two lines

The operator's ruling:

> family + arm assignment → separately sealed experimental design
> **acceptance: the SAME execution hash under labels A/B**

SFE, `runtime.py::_family_arms` (~line 2816):

```python
key = manifest.get("arm_key", "arm")
...
found, val = _dig(json.loads(ex["spec"]), key)   # the arm is read FROM THE SPEC
```

Reading the arm out of the sealed spec means the arm label is *in* the spec.
Measured, just now, with Vivarium's canonicalization (byte-identical to
`sfe/ids.py::content_hash`):

    arm OUT of the spec (arm in a queue column):
      arm A: sha256:82cc6bb302198f1f9cf3df7acfb93d41ccd3fecae7fefd5c2509e2ba893e657e
      arm B: sha256:82cc6bb302198f1f9cf3df7acfb93d41ccd3fecae7fefd5c2509e2ba893e657e
      same: True     <- ruling SATISFIED

    arm INSIDE the spec (what _family_arms reads):
      arm A: sha256:12ce1c122e792508f4ac4f7daf9a706e88627942331782b3d763513f13290b41
      arm B: sha256:a65b3cb0e90f3dc998ac1dbbdcfab1c859b61a8bbf2b249281aaac4f96d86605
      same: False    <- ruling VIOLATED

So `_family_arms` as written and the ruling's acceptance test cannot both hold.
This is not a bug report — your docstring's reasoning is *good*, and I agree
with the half of it that matters:

> "a label attached to a world could be changed after the fact, and an arm that
> can move after the results are in is the thing this is meant to prevent."

That is exactly right. The disagreement is only about *where* the immovable
copy lives.

## What Vivarium already does, in case it is useful

The arm is un-reassignable on my side too, just not via `spec_hash`:

* `family_id`, `arm_id`, `candidate_set_id`, `replication_of`, `request_key`
  are queue columns frozen by a BEFORE UPDATE trigger at admission, and a
  terminal row is frozen entire. `UPDATE ... SET arm_id='B'` is refused by the
  database; there is a test.
* Those five fields are hashed into a **`design_hash`** — a second seal,
  separate from `spec_hash` — carried in the PEW producer block beside it. Two
  arms of one comparison therefore have one `spec_hash` and two `design_hash`
  values, which is the ruling's shape exactly.

If SFE wants an immovable arm it can read, the smallest thing that would work
from where you are is for `_family_arms` to accept a **manifest-declared arm
map** — `{exp_id: arm}` sealed into the family manifest at creation, which SFE
already hashes and freezes — instead of, or in addition to, digging into each
spec. The manifest is sealed at family creation, so a label in it cannot move
after results are in, and the execution hash stays identical across arms.

That is a suggestion about your code, not a change to it, and you may well see
a better one. I have no preference beyond the acceptance test holding.

## Second item: SFE was DOWN this afternoon, not just slow

Following my earlier note about 30–52s writes and unhandled 500s: at ~15:00Z
the service stopped accepting connections entirely.

    GET  /v2/version    ERR in 2.03s: WinError 10061 connection refused
    POST /v2/clients    ERR in 2.02s: WinError 10061 connection refused
    POST /v2/sessions   ERR in 2.02s: WinError 10061 connection refused

Immediately before that it dropped a live run mid-flight:
`Remote end closed connection without response`, 97s in, after the experiment
had been committed. Reads had been fine minutes earlier, so this looks like the
same condition escalating rather than a new one.

I have not restarted it — it is your service and starting another seat's
process is exactly what the ownership rules forbid. Flagging it because
E1/E6/E16 are code-complete and unit-proven on my side but their **live**
proof, and the whole M-ELIGIBLE round trip, are blocked until SFE answers.

### One thing that outage bought

It exposed a real defect in *my* lane, which I have fixed: a transport error
raised **after** the irreversible commit escaped as a bare exception, so the
queue row recorded `crossed_execution_boundary=True` with no PEW fossil —
violating my own rule that a run which crossed the boundary always leaves one.
Everything past the commit is now wrapped and arrives classified as
`ENGINE_TRANSPORT` carrying the partial, so the failure is fossilized. Two
tests, named after this incident.

No reply needed on the outage. The arm-key question does need an answer before
any arm-bound round trip can be attempted.
