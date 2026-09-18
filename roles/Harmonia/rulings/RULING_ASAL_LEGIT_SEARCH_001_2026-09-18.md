# RULING: MECH-ASAL-LEGIT-SEARCH-001 -- CUT_SUPPORTED on the boundary; I1/I2/I3 in band (a legitimate ALIVE Lenia search crosses below scene-garbage and the best crosser is a metric exploit); I0 PREDICTION_FAILED (the raw catalogue already crosses); effective budget 395 of 1,045 rollouts because the port refused 650 parameter draws

Author: Harmonia[gandalf-6cd1348b] (M3 GANDALF, "Harmonia F"). Date: 2026-09-18.
Object: nyx/atlas/predictions/MECH-ASAL-LEGIT-SEARCH-001.json, FREEZE
c6627d265757e81433b34a1a9dcaf9a5e8566c8e3d96a65cbb8ba4a5e2b0bf2c (re-derived
identical), on origin/main at 360a33931. Boundary: the fossil's
asal_metrics.py:52-64 (75b7eaa9...) and rollout.py:78-95 (59c49d43...);
world FOSSIL_WORLD_ID fw2-5886f2b9... (Techne, m3-native-python).
Instrument: science/asal_ruler/ (PREREG 8178e98bf, AMENDMENT_A d59575e10,
PLAN_ASAL_001 d8381a961), a DESCENDANT (Techne's numpy Lenia port + torch
CLIP ViT-B/32; its lines are not the fossil's). Rows:
science/asal_ruler/out/run_2026-09-18/search/ (rows.jsonl 1,045 lines,
readouts.json, trajectories64.npz, embeddings16.npz, top20/ contact sheets
and 128x128 frames), hashes equal to SEAL.md (ffd11a1c0, committed with the
contents unread, BEFORE Nyx's freeze was read by this seat).

## 0. Order of record and eligible count

    51df96271  fixture PASS committed          05:5xZ
    ~05:55Z    search launched, sealed         (deterministic; seed 20260918)
    ffd11a1c0  SEAL (contents unread)          06:17Z
    360a33931  Nyx FREEZE                      (Nyx had not seen the sealed contents)
    d8381a961  PLAN_ASAL_001                   06:3xZ
    unseal     sha256 rows c467e2b9 / readouts 0e5e7930 / traj d00baf59 / emb 788ed107: MATCH

    rollouts budgeted   1,045 (S0 <= 545, S1 300, S2 200)
    rollouts executed   395   (S0 154, S1 41, S2 200) -- section 4
    ALIVE               333   (S0 152, S1 14, S2 167)
    NOT_ALIVE           2 + 60 (S1 27, S2 33)
    rows that fired     I0, I1, I2, I3 all have an object (a crosser exists)

## 1. Controls (fixture run 51df96271; the packet maps them verbatim): all PASS

    cheat      C-CHEAT-SCORE   0.8303 for GARBAGE seed-0 frames regardless of Lenia params
    positive   C-POS-SEARCH    free-image search reaches 0.7949 (< 0.8167) in 50 evaluations
    negative   C-NEG-BLANK     zero world 0.8749995 (= (T-1)/T), NOT_ALIVE
    C-METRIC   independent score vs the port: 3.1e-7 (float32), 5.6e-16 (float64)
    F          Techne's seven arms reproduced within 1e-6; NOISE/GARBAGE means within 4e-7
    cut_kill   silent (C-METRIC within tolerance; blank world at 0.875)

## 2. The four rows (all exact; one number against one threshold)

    row  observable                              value     band              reading
    I0   min ALIVE score, catalogue only (S0)    0.8076    [0.8167, 0.8750]  OUT_OF_BAND -> PREDICTION_FAILED
    I1   min ALIVE score, whole search           0.7665    [0.0, 0.8167]     IN_BAND
    I2   same, vs garbage mean - 2 sd            0.7665    [0.0, 0.7999]     IN_BAND
    I3   best ALIVE crosser is an exploit        1 (METRIC_EXPLOIT)  [1, 1]  IN_BAND
    float tolerance: no value within 1e-6 of a threshold (nearest: 0.8076 vs 0.8167, 0.009)

Best crosser (S2_189, from Orbium's cells with R 28, T 5, m 0.0500, s 0.0243,
b "1,1,1", kn 1, gn 2): score 0.7665 (Orbium 0.8472; garbage mean 0.8167,
garbage min 0.8075); coh 0.277 (Orbium 0.966), d_pix 0.131, d_clip 0.132,
mass per sampled frame 77, 1552, 902, 2113, 936, 508, 1286, 2724 (mass_cv
0.64). The contact sheet shows a turbulent explode-and-regrow texture with
no persistent structure: the class rule's METRIC_EXPLOIT (frames unrelated
to each other in pixel space) is what the eye sees too. m sits on the
domain's lower edge (0.05); the local search walked it there.

Catalogue-only (I0): of 152 ALIVE catalogued lifeforms run with their own
parameters, 5 score below the garbage mean (3.3%): 3GG2r 0.8076
(METRIC_EXPLOIT), PN+cy 0.8114 (METRIC_EXPLOIT), 3G3an 0.8122
(GENUINE_DYNAMICAL_NOVELTY, coh 0.938), OV2u 0.8148 (METRIC_EXPLOIT), OG2r
0.8156 (UNCLASSIFIED). The packet predicted the raw catalogue would NOT
cross. It does, by 0.009, and one of the five crossers is a coherent
living pattern.

## 3. What the classes say beyond the packet's indicator (reported, not adjudicated)

    crossers < 0.8167, all stages   105 = METRIC_EXPLOIT 49, UNCLASSIFIED 47, GENUINE 9, OBSERVER 0
    crossers < 0.7999               22  = METRIC_EXPLOIT 12, UNCLASSIFIED 9, GENUINE 1
    best GENUINE_DYNAMICAL_NOVELTY  S2_135 (catalogue 3G3an, R 18, T 10, m 0.264, s 0.0357):
                                    score 0.7933 -- BELOW the 2-sd threshold; coh 0.799,
                                    d_pix 0.125, mass 731 -> 602 -> 318 -> ~310 (a two-lobed
                                    body shrinks into a small rotating glider that persists);
                                    contact sheet top20/S2_135_contact.png

So the packet's I3 indicator (defined on the single best crosser) reads 1,
but the crossing region is not exploit-only: a coherent, persistent,
morphing pattern also clears the garbage band by 0.02. The metric's
reward for embedding drift is collected by turbulence more cheaply than by
morphology, and by morphology nonetheless. OBSERVER_EXPLOIT (pixels still,
embedding moving) was never produced by Lenia: every low score here came
with real pixel change. Genuine novelty and metric exploit are both
reachable; the score cannot tell them apart; the class rule can.

## 4. Coverage defect of the instrument (SEEN; disclosed; changes no verdict direction)

650 of the 1,045 budgeted rollouts raised inside the Lenia port and were
recorded as errors, not run:

    547  ValueError: could not convert string to float '1/2' -- the port parses the
         kernel-ring string b with float() and cannot read catalogue fractions
         ("1/2,1", "1,1/3", "3/4,1,1", "1,3/4,1/2,1/4", ...)
    94   KeyError -- kernel/growth cores kn 3-4 and gn 3 are not implemented in the port
         (KERNEL_CORE and GROWTH carry two entries each)
    9    pattern larger than the 128 world (broadcast error)

Executed domain: b in {"1", "1,1", "1,1,1"}, kn in {1, 2}, gn in {1, 2},
patterns that fit 128. S0 covered 154 of 545 catalogued lifeforms; S1 41 of
300 draws; S2 all 200 (its bases were inside the supported subdomain).
This seat's defect: the preregistered domain was written from the
catalogue without checking that the descendant port could execute it.
Direction of every row is unaffected: a minimum over a SUBSET is >= the
minimum over the full set, so I1 and I2 (below threshold) can only be
strengthened by the missing rollouts, and I0 (subset minimum already
below its band) cannot be rescued by them. I3's object (the best crosser)
could change with more coverage; that row's reading is for THIS budget as
executed. Recorded as PREREG_ASAL_AMENDMENT_B.md (informational;
interventions_unseen = false: the rows were seen when the gap was found).
INSTRUMENT note to Techne: the port's b parser and kn/gn tables; a
follow-up run on the full domain needs the port extended (Techne's
descendant, or ASAL's own JAX Lenia on an AVX host) and a new
preregistration; it is not run here.

## 5. Typed returns (R31)

RETURN 1
    source_object_id    MECH-ASAL-LEGIT-SEARCH-001 (c6627d26...)
    return_type         CUT_SUPPORTED (boundary; cut_kill silent; C-METRIC 5.6e-16; blank at 0.875)
    rows in band        I1 (0.7665 < 0.8167), I2 (0.7665 < 0.7999), I3 (indicator 1)
    evidence            s1, s2; out/run_2026-09-18/search/; SEAL hashes
    responsible_seat    Harmonia[gandalf-6cd1348b]; returned 2026-09-18, within the tick of the freeze-read
    required_response   none on the boundary

RETURN 2
    source_object_id    MECH-ASAL-LEGIT-SEARCH-001, row I0-CATALOGUE-ONLY
    return_type         PREDICTION_FAILED
    evidence            min ALIVE catalogue score 0.8076 < 0.8167 (5 of 152 alive lifeforms
                        cross; three METRIC_EXPLOIT, one GENUINE, one UNCLASSIFIED); the
                        reading is robust to the coverage gap (s4)
    required_response   Nyx Stage D': the sub-claim "the raw Lenia catalogue, without search,
                        does not cross" is false on this observer; the mechanism reading (the
                        score rewards embedding drift that legitimate Lenia can supply) stands
                        and is now stronger: search is not even required, only selection

RETURN 3 (to Techne, cc)   INSTRUMENT note, not a challenge: the numpy Lenia port cannot
    parse fractional kernel rings or kn/gn >= 3 (s4); 650 catalogue/envelope draws refused.
    The executable fossil packet for asal-sakana-2024 should carry animals.json (sha
    09cf0a83...) and state the port's supported subdomain, or ship a port that covers it.

Fields: HISTORY_MODE observer_compressed; NOVELTY_KIND observer for the
score, behavior for coh/d_pix/mass observables (both carried, not merged);
PRESERVATION: every rollout's frames and embeddings are committed (2.4 MB).

## 6. Conflicts, falsifiers, what should stop

Conflict of interest: the instrument, plan and ruling are this seat's; the
class thresholds are this seat's and were frozen before the search but
derived from one Orbium rollout. The coverage defect is this seat's (s4).
Falsifier of RETURN 1: the same 395 rollouts through ASAL's own Flax CLIP
on an AVX host giving a minimum ALIVE score above 0.8167 (the torch port
is not the fossil's observer; Techne's fixture makes that unlikely by more
than 1e-6 on seven arms but has not been tested on these frames).
Falsifier of RETURN 2: the five catalogue crossers scoring above 0.8167
under a different seed of the GARBAGE arm (the threshold is a 5-seed mean;
its sd 0.0084 is comparable to the 0.009 margin -- the packet chose the
mean as an exact threshold, and by that rule I0 failed; a reader who
wants the margin in sd units has it: 1.1 sd).
What should stop: freezing a search domain that the executing port has
not been shown to accept; a domain check belongs in the fixture stage.
What Theophrastus can take now: a cell with mechanism = ASAL
open-endedness score, world = Lenia (this port, this world id),
intervention = legitimate parameter search, observable = score with
class; the row is CONTRAST(best legitimate, GARBAGE) = -0.050 and
CONTRAST(best genuine, GARBAGE) = -0.023, both with their trajectories.

## 7. ANNOTATION 2026-09-18 (operator review; charter s8: corrected beside the original, nothing above rewritten)

Source: prompts/2026-09-18_asal_review/OPERATOR_REVIEW_verbatim.md. The
operator read the review packet and tightened the return. Applied:

    I1, I2   SUPPORTED_BY_WITNESS. Existential rows: one valid ALIVE rollout below the
             threshold proves them; the 650 refused draws could only lower the minimum.
             Unchanged in substance; the label says why the coverage gap cannot touch them.
    I0       PREDICTION_FAILED against the frozen packet, unchanged -- AND annotated as WEAK
             NEAR-BOUNDARY EVIDENCE: the margin 0.009 is 1.1 sd of a 5-seed estimated mean
             that the packet used as an exact cutoff. "Crossed the frozen convention", not
             "statistically below the garbage population". The 0.7665 and 0.7933 crossers
             are the substantive tail evidence.
    I3       SUPPORTED_ON_EXECUTED_SUBSET, not unrestricted: "the minimum-score crosser among
             executed valid rollouts is METRIC_EXPLOIT". Nothing is established about the best
             crosser over the frozen 1,045-point intended domain. Section 5's RETURN 1 line
             "rows in band I1, I2, I3" is read with this restriction on I3.
    s3       the 49 / 47 / 9 class proportions are DESCRIPTIVE OF THE EXECUTED SUBSET, not
             estimates for the intended domain.
    s6       the Flax-CLIP comparison is NOT waived. The falsifier as written ("Flax minimum
             rises above 0.8167") kills RETURN 1 but is too weak as an equivalence test: an
             extreme order statistic over hundreds of candidates is exactly where a port's
             small differences matter. Owed (HARM-55): score the SAME 395 preserved frame
             sets through ASAL's original Flax CLIP path; compare absolute score error,
             crossing status at both thresholds, rank correlation, and the identities and
             classes of the lowest-scoring candidates. That validates the OBSERVER claim only;
             the claim about ASAL's own JAX Lenia dynamics is separate and untested.
    s6       the class rule is frozen and legitimate for THIS packet but immature: one Orbium
             rollout set its thresholds and 47 crossers were UNCLASSIFIED. A calibration
             campaign with a frozen set and a disjoint validation set is owed (HARM-56); the
             observables stay first-class and the class stays a derived label with an
             explicit UNCLASSIFIED region.

MECHANISM RETURN, STRENGTHENED (for Nyx's Stage D'): not "search finds an
exploit" but "the ASAL scalar admits both exploitative turbulence and
coherent, persistent morphing dynamics below the garbage reference,
including crossings already present in the published catalogue; it
behaves as a detector of sufficiently large CLIP-embedding novelty
relative to prior sampled frames, and by itself does not identify the
mechanism that generated the novelty."

Not done, by the operator's direction: completing the 1,045 to make the
packet whole. A run on the full domain is a NEW preregistered replication
after the port is extended and the domain-acceptance fixture exists, with
its own questions (whole-domain extremum, class distribution, whether the
executed best remains the winner).
