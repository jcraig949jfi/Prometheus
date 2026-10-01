# A2 -- Process interventions as natural experiments

Analyst: a read-only subagent, deposited by Aphrodite. The harness blocked the subagent from writing the report itself,
so the text is the agent's returned report, lightly formatted. The method code (a2_proxies.py, a2_extra.py) and the raw
output (a2_out.md) sit beside this file.

Data:
- comms.messages: 1198 messages, 2026-09-11..09-30;
- git non-merge commits: 6050 in September by local month. The brief said 6954; that figure was a UTC/multi-line
  artefact.
Seats are attributed by commit subject prefix; 1036 September commits were unattributable. Times are US Eastern (UTC-4).

## Summary

1. **The interventions are NOT separable.** Ops IDs, Fabric/leases, MWO-0001..4, WORK_STATE, CWO-A/B/C, Builders and the
   harvest directive all land between 09-27 07:26 and 09-30 17:56. The **Opus 5 -> Opus 5.5 switch (09-23..26, from
   Co-Authored-By trailers)** comes immediately before all of them.
2. **Comms bus (09-11).** Coordination's share of non-auto commits went from 7-19% before, to 46% on the day, then 22-36%
   after. The pre-bus paste-relay channel is unrecorded, so the bus's benefit cannot be tested. Overhead up; benefit
   INDETERMINATE.
3. **Prereg/freeze.** Commits rose about 10x from mid-August (12/wk to 136-177/wk). Amendments per prereg stayed flat at
   0.12-0.33. The share of verdicts with a prior same-seat prereg ranged 0.53-0.90 with no monotone trend. WEAK POSITIVE.
4. **Sealed holdouts (08-27).** The D2 harness went v2 to v13 in about 36 h (09-28/29). Hardening cannot be told apart
   from churn using commit subjects. INDETERMINATE.
5. **Review-packet skill (09-01).** Commits went from 1-4/wk to 14-52/wk and the level was sustained. The effect on review
   quality is unmeasurable here.
6. **Evidence Wiki (09-01).** 38, 25 and 42 commits/wk, then 0 and 1. Adoption burst then decay, unless it is query-only
   usage (unlogged).
7. **Positive controls and the baseline norm** (09-15 ruling, 32 seeds x 4 RNG families). No adoption curve.
   INDETERMINATE.
8. **Fabric and leases (09-28).** Lease-problem messages went 4, 1, 5, 4 per window: no drop. Fabric added NEW friction
   classes (disk-full checkout cache #994/#998; silently accepted host-affine tasks #916/#953). LEANS CHURN.
9. **MWO + WORK_STATE.**
   - Fast MWO-0001 adoption: median 1.35 h over 12 seats; Nyx was the laggard at 32.7 h.
   - BUT four MWOs landed in 9.9 h, and 61-104 WORK_STATE commits per day pushed the coordination share to 58.8% on
     09-29. Without WORK_STATE commits the figure is 27.2%. The intervention is reporting on itself.
10. **CWO A/B/C (09-30).**
    - Active seats went from 7-9 to 14 (comms) and from 8-9 to 11 (git science).
    - Confounded by operator attention (28 prompt directories that day vs 7 the day before), the mandated 1-hour
      heartbeat, and 36 copy-paste per-seat messages.
    - CWO-B reversed CWO-A's self-promotion rule within 5 h: direct churn.
11. **Builders: on paper only.** BUILDER-FABRIC was suspended by CWO-B. The only Builder output is fleet_status.py,
    seeded by Aporia.
12. **Ops IDs (TH/C/E).** About 20 comms mentions in total. The `task_ref` field is almost always empty, so messages
    cannot be joined to work by ID.
13. **Failed proxies.**
    - question latency: only 41 'question' messages;
    - stale-state regex: it matched protocol vocabulary. Hand-coding found about 8 real incidents in 20 days, too few for
      a rate;
    - regex operator share: inflated by the word "verbatim", so roles/*/prompts directory counts were used instead.
14. **Confounders on every proxy:** the model switch; the number of senders per window (37, 18, 19, 8, 12, 20); operator
    attention and Sunday dips; window lengths of 1-8 days; interventions that generate their own reporting.
15. **Design for next time:**
    - one change about every 5 working days, staggered by machine or with holdout seats;
    - TH/C/E IDs in `task_ref`;
    - activity measured from execution receipts, not heartbeats;
    - operator prompts and the model per message as first-class fields.

## Intervention timeline

| Intervention | Date | Evidence |
|---|---|---|
| Sealed holdouts | 08-27 | 7e466657a; D-3 38a5304d1; D-5 7884e3e3c; "sealed" first appears 09-02; D2 v2->v13 on 09-28/29 |
| Prereg | from 06-04; the norm by August | 44 commits in Aug, 144 in Sep |
| Review-packet skill | 09-01 | 9433eb666 |
| Evidence Wiki | 09-01 | c711c5bf6 |
| Comms bus | 09-11 07:32 | 7466bd6ac; broadcast #1 |
| Nestor swarm | 09-14 | 1706 auto row commits that week |
| Baseline ruling 16 | 09-15 02:53 | Nestor |
| Model switch (Opus 5 -> 5.5) | 09-23..26 | commit trailers |
| Ops pilot (TH/C/E) | 09-27 07:26 | c8b9ea49e |
| Fabric v0 | 09-28 13:30 | 9ff7dd967 |
| Ruling #896 | 09-28 17:04 | comms |
| Lease cutover | 09-28 ~17:50 | 8370083ae |
| v0.2 frozen | 09-28 ~17:50 | 54e42c695 |
| MWO-0001 | 09-28 21:48 | 7e4c09f2c |
| MWO-0002 | 09-29 02:56 | archive commits |
| MWO-0003 | 09-29 07:14 | archive commits |
| MWO-0004 | 09-29 07:42 | archive commits |
| WORK_STATE.json | 09-28 21:50 | bd48fac9b |
| CWO-A | 09-30 04:18 | 6a7a84569 |
| CWO-B | 09-30 09:16 | d4e47ebf5; suspends BUILDER-FABRIC |
| CWO-C | 09-30 13:55 | 7d373ac02 |
| Builders | 09-30 | defined in CWO-A; not adopted |
| Harvest directive | 09-30 17:56 | 66fc8b1d0 |

## Comms windows

Window boundaries:

| Window | From | To |
|---|---|---|
| W0 | 09-11 | 09-14 |
| W1 | 09-15 | 09-22 |
| W2 | 09-23 | 09-26 |
| W3 | 09-27 | 09-28 17:00 |
| W4 | 09-28 17:00 | 09-30 04:18 |
| W5 | 09-30 04:18 | 09-30 (end of data) |

| Metric | W0 | W1 | W2 | W3 | W4 | W5 |
|---|---|---|---|---|---|---|
| messages | 263 | 273 | 206 | 152 | 129 | 175 |
| senders | 37 | 18 | 19 | 8 | 12 | 20 |
| overhead % | 17.5 | 16.1 | 27.7 | 6.6 | 7.0 | 41.7 |
| overhead %, copy-merged | 17.6 | 16.9 | 28.1 | 7.8 | 7.7 | 36.7 |
| threaded % | 28.9 | 24.9 | 57.8 | 27.6 | 55.0 | 41.7 |
| reply depth, mean / max | 0.36 / 4 | 0.40 / 5 | 2.23 / 21 | 0.64 / 7 | 2.59 / 20 | 0.51 / 3 |
| questions | 17 | 5 | 5 | 7 | 2 | 5 |
| median hours to any response | 0.55 | 4.51 | 0.04 | 0.72 | 1.57 | 0.60 |
| operator-subject messages | 10 | 57 | 19 | 8 | 8 | 16 |
| lease-problem messages | 1 | 2 | 4 | 1 | 5 | 4 |
| positive-control % of verdict reports | 35 | 21 | 58 | 21 | 3 | 14 |

Recurring friction that persists through every intervention:
- memory/OOM: 46 messages over 12 days, from 17 seats;
- "waiting on operator / blocked on": 64 messages over 12 days, from 22 seats.

## Git, weekly (week starting 08-10 through 09-28)

| Metric | 08-10 | 08-17 | 08-24 | 08-31 | 09-07 | 09-14 | 09-21 | 09-28 |
|---|---|---|---|---|---|---|---|---|
| coordination % | 16.9 | 5.1 | 12.1 | 12.7 | 33.5 | 35.6 | 25.4 | 46.3 |
| verdicts with prior prereg | .67 | .56 | .68 | .90 | .59 | .53 | .89 | .82 |
| amendments per prereg | .33 | .29 | .19 | .12 | .33 | .19 | .23 | .13 |
| positive-control % of verdicts | 0 | 0 | 3.1 | 0 | 6.6 | 4.2 | 15.7 | 4.7 |
| review-packet commits | 0 | 1 | 4 | 52 | 15 | 48 | 20 | 14 |
| wiki commits | 0 | 0 | 0 | 38 | 25 | 42 | 0 | 1 |

## Git, daily (09-23 to 09-30)

| Metric | 09-23 | 09-24 | 09-25 | 09-26 | 09-27 | 09-28 | 09-29 | 09-30 |
|---|---|---|---|---|---|---|---|---|
| coordination % | 19.9 | 18.1 | 46.7 | 25.5 | 18.8 | 29.6 | 58.8 | 50.7 |
| WORK_STATE commits | 0 | 0 | 0 | 0 | 0 | 28 | 104 | 61 |
| coordination % excluding WORK_STATE | 19.9 | 18.1 | 46.7 | 25.5 | 18.8 | 20.3 | 27.2 | 32.7 |

## Other measures

- Operator prompt directories per day: 79 on 09-11; then 1-31; 7 on 09-29; 28 on 09-30.
- Gaps between superseding orders, in hours:

  | Order | Hours after the previous order |
  |---|---|
  | MWO-0002 | 5.1 |
  | MWO-0003 | 4.3 |
  | MWO-0004 | 0.5 |
  | CWO-A | 20.6 |
  | CWO-B | 5.0 |
  | CWO-C | 4.6 |
  | harvest directive | 4.0 |

- Adoption: MWO-0001 median 1.35 h (12 seats). CWO-B heartbeat median 0.31 h, over 8 subject-matched seats.
- Active seats per 24 h (from 04:18):

  | Window start | Comms senders | Seats with science commits |
  |---|---|---|
  | 09-27 | 6 | 6 |
  | 09-28 | 9 | 9 |
  | 09-29 | 7 | 8 |
  | 09-30 | 14 | 11 |

## Methods

- Commits are classified auto / coordination / science / other by regex.
- Model per day comes from Co-Authored-By trailers.
- Adoption dates come from `git log --diff-filter=A --reverse`.
- Seats are attributed by subject prefix; single-letter `X[m1-..]` prefixes are Nestor.
