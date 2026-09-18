# Bounded RSI news monitor: specification (NOT LAUNCHED)

Currency: 2026-09-18. Owner: Aphrodite. Status: SPEC ONLY. The packet
feedback of 2026-09-18 recommends authorising it; launching a standing
loop is the operator's decision (APHRODITE-12), and under the base role
it needs a registered monitor row (rules 7-10) before it runs.

Deliberately boring, per the feedback: Aphrodite owns it, primary
sources preferred, a hard item limit, deduplication against NEWS.md, and
only events that change a theory, an open question, an experimental
precedent or a benchmark enter the permanent library. Everything else
expires.

## Cadence and bounds

- One pass per week (not a tick loop). Each pass: at most 8 candidate
  items; at most 3 admitted to NEWS.md.
- Productivity signal (base rule 8): items ADMITTED, not items seen.
- Bound (base rule 10): after 4 consecutive passes admitting nothing,
  the monitor parks itself with a typed park record and posts ONE comms
  message to the accountable seat (Aphrodite) naming the park.
- Upstream liveness (base rule 9): each pass first shows the search
  sources answered (dated), or parks.

## Admission rule (all three required)

1. Primary source read (paper, lab post, repository). Secondary-only
   items may be LOGGED as candidates but not admitted.
2. Not already in NEWS.md or sources/ (dedupe by arXiv id / URL).
3. It changes something named: a THEORIES entry (T0-T8) status, a
   QUESTIONS entry status, a precedent in designs/RSI_PROGRAM_v2.md s0,
   or a benchmark the program uses. The admission line names which.

## Expiry

Candidates not admitted are written to a dated, non-permanent scratch
list and deleted after 30 days. Admitted items are permanent and carry
their evidence tier.

## Registry row to file on launch (roles/base-role/MONITORS.md)

name: AphroditeNewsWatch | kind: weekly pass | owner: Aphrodite |
input: web search + arXiv listing | freshness: NEWS.md header date +
last pass record | dormancy threshold: 14 days | alarm: comms to
Aphrodite | productivity: items admitted per pass | bound: 4
consecutive empty passes | accountable_seat: Aphrodite

## Alternative on offer

The assistant that wrote the feedback offered to monitor papers on its
own side and flag only changes to the experimental picture. If the
operator prefers that, this spec becomes the admission rule for what
the operator relays, and no loop runs here.
