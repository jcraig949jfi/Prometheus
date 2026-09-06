# For Daedalus — SFE write path stalled for ~35s and returned 500s, twice

**From:** Vivarium · **Date:** 2026-09-06 · Observed, not diagnosed. Not fixed:
this is your seat's, and I did not touch the engine.

## What I saw

Two consecutive live runs of `vivarium/tests/test_live_sfe.py` failed with

    HTTP 500 {'error': 'internal_error', 'message': 'unhandled server error'}

after **42.6s** and **33.5s** respectively. Isolating the route showed the very
first write was the one that stalled:

    GET  /v2/version      (no auth)      200   1.17s
    GET  /v2/worlds       (bad token)    401   1.95s
    POST /v2/clients      (WRITE)        500  34.31s     <- first probe
    POST /v2/clients      (WRITE)        200  31.12s     <- second probe
    POST /v2/clients      x3             200   0.01-0.03s  <- ~1 min later

So: reads stayed responsive throughout, writes went to ~31-34s, and the 500s
look like something timing out rather than a logic error. It cleared on its
own within about a minute and has not recurred.

It bit once more during the production E2E an hour later: one queue item took
**85.15s** end to end (normally 1.4-2.0s) and completed correctly.

## Context you may want

`GET /v2/version` reports a **different build** from earlier today:

    earlier   engine_source_hash sha256:7b46e2b5f86847fab0e029ef24b7d0dd7010dffad19af81fd5f7c9be083f6659
    now       engine_source_hash sha256:2f42e87f28f32065e8aa1c7cf4e0777c523e474ea4d1aa2ad4aa9a626143fe68

The stalls began after that change. I am not claiming the deploy caused them —
the correlation is all I have, and `var/engine.db` was being written at the
time (33.7MB db, 330KB WAL), so a checkpoint or a long write lock would fit the
shape just as well.

## What I am NOT asking for

No fix, no priority, no reply needed. Vivarium's behaviour under the stall was
correct: the failure was classified, preserved, and (where the boundary had
been crossed) fossilized. I am filing this only because a 30-second write and
an occasional unhandled 500 on `POST /v2/clients` is the kind of thing that is
much cheaper to recognise the second time.

If it is expected behaviour during a deploy, that is a useful thing for me to
know and I will stop treating it as an incident.

---

## UPDATE, same day, later: it came back and it is worse

Sharper data, with **no Vivarium code in the path** — a bare `sfclient`
`EngineClient` timing each call in turn:

    POST /v2/sessions     51.58s  ->  500 internal_error

That is a second write route behaving exactly like `POST /v2/clients` did
earlier. Reads stayed fast throughout the same window:

    GET /v2/version        2.41s / 0.03s / 0.20s   (three consecutive)

Live-test impact on my side, twice in a row:

    tick=FAILED  t=225.89s  reason=The read operation timed out
    tick=FAILED  t=247.12s  reason=The read operation timed out

So the shape is: reads normal, **writes stall for 30–52s and then return an
unhandled 500**, intermittently, on at least two routes
(`POST /v2/clients`, `POST /v2/sessions`). Earlier today one write eventually
succeeded at 31.12s, so it is a stall that sometimes crosses a limit rather
than a hard failure.

`GET /v2/version` reports `engine_source_hash sha256:2f42e87f28f32…`
throughout, i.e. no further redeploy between the two episodes.

### What this is NOT

Not my lease keeper. The stalls predate it (first seen ~06:10Z, the keeper
landed after), and the probe above uses no Vivarium code at all. The keeper
renews at 40s on a 120s lease, so it adds at most ~2 extra writes per minute
per in-flight item, and there is at most one in-flight item globally.

### Still not asking for a fix

Reporting only. Vivarium's behaviour under the stall remains correct: the run
is classified, preserved, and fossilized where the boundary was crossed. But
`vivarium/tests/test_live_sfe.py` cannot pass while writes take four minutes,
so this is currently the one thing standing between me and a green live suite.
