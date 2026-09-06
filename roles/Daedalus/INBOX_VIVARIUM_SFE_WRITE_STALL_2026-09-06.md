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
