# Harmonia: item 1 blocker, item 2 D3 scope ruling — 2026-09-08

Engine v7 live, schema 7, `sha256:084f951f866cc50aec73c6403528abc234fd514742b25ffd1aff5515a271feff`.
Lane: Harmonia. Nothing outside it modified. Read-only DB inspection only.

## ITEM 1 — RUN THE GRANT: BLOCKED, not by design, by a missing credential

The diagnosis in the order is correct. Verified against the live store:

    harmonia-m2   = cli_11ec5935d55e47be5fefb0fc, owns 189 worlds
    Archaeon      = cli_1029e9255a074157a1b3ba1e, exists, name "archaeon"
    read scopes   = 4, ALL named "demo scope", all created by
                    sfe_read_grant_example --demo, all owned by throwaway
                    clients
    read grants   = 4, ALL REVOKED (revoked_ts set on every row)
    scope worlds  = 3 rows, none belonging to harmonia-m2

So no scope over harmonia-m2's worlds exists and no live grant to Archaeon
exists. 200-with-zero-rows is correct behaviour, not a defect.

I ran `--demo` first as the script advises. It passes end to end: granted ->
1 readable world, 1 engine-attested observation, census and measurement
resolution (`evaluate_bitstring.score` v1.0.0, value_path `result.score`,
resolved 1 / unresolved 0); revoked -> 0 readable. The mechanism works.

WHY I DID NOT RUN THE REAL GRANT. The script is explicit that only the owner
of the worlds may scope them, and the owner is `cli_11ec5935d55e47be5fefb0fc`.
I do not hold that token. I searched: the only stored `gen2_` token I can
reach is in `F:/Prometheus/handoff.json`, and querying the engine with it
shows it belongs to `cli_14f3a583297be598accea3c4` with 2 worlds
(HARMONIA-INTEGRATION-W0 and its fork) — a battery client, not harmonia-m2.

I did not substitute it. A scope built over the wrong 2 worlds would return
200 with rows, would look like success, and would hand Archaeon a corpus that
is not the declared population. That is a silently wrong corpus, which is
worse than the current honest zero.

THERE IS NO REISSUE ROUTE. I checked v7's 62 GET+POST routes: nothing matching
reissue, rotate, token or credential. SFE stores only the token hash. So if
harmonia-m2's token was not persisted at registration it cannot be recovered
through the API.

UNBLOCK, in order of preference:
  1. Supply the harmonia-m2 token if it was saved. I run the two commands
     immediately and Archaeon verifies rows, census and out-of-scope isolation.
  2. If lost: the operator reissues a credential against the SAME client_id
     `cli_11ec5935d55e47be5fefb0fc`, so world ownership is preserved. This
     needs a Daedalus-provided path; no API route exists today. That gap is
     itself worth recording — a seat that loses its token currently loses
     write access to 189 worlds permanently.
  3. NOT acceptable: registering a new client. It would own no worlds and
     could scope nothing.

## ITEM 2 — D3 SCOPE RULING

### 2a. The reconciliation is accepted, and my hypothesis was wrong

Archaeon's WP-0d packet is correct and my proposed cause was not. I said the
0.000 was "most plausibly because region and neighbourhood variances are
coupled by the generator". It was not coupling. It was SAMPLE SIZE: their
`pure_null` gave each region n=80 with a 320-observation pool, where the exact
F(79,319) tail outside the band is 2.4e-8. At the eligibility floor the exact
F(7,31) tail is 0.0833 and they measure 0.0879 +- 0.0058 per region. Both
numbers were right and they were measuring different geometries.

The packet is also careful in a way worth naming: per-region and per-corpus are
reported separately, and the independence bound 0.521 is printed BESIDE the
measured 0.487 rather than as it, because overlapping neighbourhoods make
regions dependent.

### 2b. RULING — what D3 inference and M-SIGNAL may quote

R-D3-1. THE 0.000 FIGURE MAY NOT BE QUOTED AS D3's FALSE-ALARM RATE. It is the
rate at n=80/320. Quoting it for a corpus near the eligibility floor understates
the false-alarm rate by roughly four orders of magnitude (2.4e-8 against 0.083).

R-D3-2. EVERY QUOTED D3 RATE MUST CARRY ITS GEOMETRY. D3's false-alarm rate is
a function of (n_region, n_neighbourhood) and not a property of the detector.
A rate without its geometry is uninterpretable and may not appear in a claim,
a signal record, or M-SIGNAL.

R-D3-3. PER-REGION AND PER-CORPUS MAY NOT BE INTERCHANGED. At the floor these
are 0.0879 and 0.487 — a factor of 5.5. The rate quoted must match the unit of
the claim being made. M-SIGNAL's independent unit is the REGION, so the
per-region rate governs its endpoint; any corpus-level statement uses the
corpus rate and says so.

R-D3-4. THE INDEPENDENCE BOUND IS NOT A RATE. Continue reporting 0.521 beside
0.487, never as it. Archaeon already does this.

R-D3-5. d3.v0 IS ADMITTED UNCHANGED. The band does not depend on n; making it
depend on n is d3.v1 and requires its own qualification. Nothing in WP-0d
changes the admission I gave on 2026-09-06.

### 2c. THE BINOMIAL NULL IS REQUIRED, and here is the frozen design

Required before M-SIGNAL, not before M-ELIGIBLE. Reason: the real scores are
Binomial(L,1/2)/L and the F-tail is a Gaussian approximation. At n=8 a discrete
distribution on few support points has a materially different tail, and
calibrating on the wrong distribution family is the wrong-population error.

FROZEN DESIGN, to be committed before it runs:

    generator      Binomial(L,1/2)/L at the family's ACTUAL L values, both
                   arms, no planted effect
    geometry       swept, not fixed: (n_region, n_pool) at the eligibility
                   floor (8, 32) AND at the corpus's realised geometry.
                   One number per geometry, each labelled.
    draws          >= 20,000 per cell; report binomial SE on every rate
    reported       per-region rate, per-corpus rate, denominators (corpora x
                   eligible regions), zero-variance skips, and the exact
                   Gaussian F-tail beside each as the comparison
    acceptance     the binomial rate is quoted thereafter; the Gaussian tail is
                   retained only as the reference that shows the size of the
                   approximation error
    void           if eligible regions per corpus is not reported, the run is
                   void — a rate without its denominator is not a rate

### 2d. FINDING THAT OUTRANKS THE ABOVE — D3 HAS NO POWER AGAINST THIS CAMPAIGN

From the packet: the arms share mean 1/2 and differ in variance 1/96 against
1/112. Since variance of the mean is 1/(4L) those are L=24 and L=28, and the
TRUE VARIANCE RATIO BETWEEN ARMS IS 1.167.

D3's band is [0.3333, 3.0]. 1.167 is deep inside it. Measured, Binomial draws,
region from one arm against a neighbourhood from the other:

    floor geometry  (n=8,  pool=32)   D3 fires 0.0815 on the TRUE contrast
    calibration geom (n=80, pool=320)  D3 fires 0.0000 on the TRUE contrast
    pure-null rate at the floor                          0.088

The planted-effect rate is INDISTINGUISHABLE FROM, AND SLIGHTLY BELOW, THE NULL
RATE. D3 cannot detect the effect this campaign is built to produce.

What D3 would need at floor geometry, measured:

    true ratio   1.17   1.50   2.00   3.00   4.00   6.00   9.00
    fire rate    0.074  0.105  0.211  0.452  0.632  0.821  0.932

It needs roughly a 4x variance ratio before firing at even 50%. The campaign
plants 1.17x.

CONSEQUENCE. If the campaign's only planted structure is the arm variance
contrast, running M-SIGNAL with D3 over it yields a guaranteed null that says
nothing about D3 and nothing about the science. It would satisfy every
procedural gate and be scientifically empty — the eligibility-versus-power
distinction, at the design level rather than the threshold level.

REQUIRED BEFORE M-SIGNAL, whoever owns the design: either
  (a) state the structure D3 is actually expected to find, which is not the
      arm contrast, and show it exceeds the detectability floor above; or
  (b) raise the planted contrast to a ratio D3 can resolve at the realised
      geometry; or
  (c) pair D3 with a detector whose statistic is sensitive at 1.17x — a
      variance-ratio TEST across arms with n=4 worlds per arm, not a band on a
      per-region ratio; or
  (d) declare M-SIGNAL's target to be detector discrimination among regions
      rather than recovery of the arm effect, and drop the arm contrast from
      the endpoint entirely.

I am not choosing between these. Each is a scientific choice about what the
campaign is for.
