# Multiplicity across the H0-H5 lanes (HARM-11)

Currency: 2026-09-18 (Harmonia[m2-ca1148a0]). Executable form:
qualification_rules.program_family() (QR-1.2.0). Every sentence that names
more than one lane's verdict cites this file.

## The declared families

    family    members                                   correction                 rate
    -------   ---------------------------------------   ------------------------   ---------------------
    LANE      the lane's declared primary contrasts     Bonferroni within the      alpha = 0.05 per lane
              (H0 2, H1 2 beta / 1 at 1.0, H2 3,        lane (validate_plan        (family-wise, within
              H3 3, H4 2, H5 2; lane_gate(lane))        refuses > 1 primary        the lane)
                                                        with multiplicity NONE)
    PROGRAM   the six lane families                     alpha / 6 = 0.0083 per     0.05 family-wise
              (any sentence that aggregates lanes:      lane for a cross-lane      across the program
              "the ecosystem works", "k of 6            claim
              supported", "no lane is unsupported")

## The number nobody stated before this file

Six lanes each reading their own verdict at alpha 0.05, uncorrected across
lanes, carry under a global null:

    P(at least one false SUPPORTED among 6)   1 - 0.95^6 = 0.265
    expected false SUPPORTED count            6 x 0.05 = 0.30

So "one of six lanes supported" is, on its own, the expected outcome of six
null experiments about a quarter of the time. That is why a lane verdict and
a program claim are different sentences with different alphas.

## Rules

1. A lane's verdict (SUPPORTED / UNSUPPORTED / INCONCLUSIVE) is read at the
   LANE family. Nothing in this file weakens or strengthens it.
2. Any claim that counts, ranks or combines lane verdicts is read at the
   PROGRAM family: each contributing lane's interval is recomputed at
   alpha / 6 and the claim is stated with both rates printed beside it.
3. Secondary contrasts (lane_gate(lane).beta.secondary) are outside both
   families: reported, never a gate, never counted.
4. Contrasts that share an arm within a lane (H0's G and the transport
   contrast both subtract S00) are correlated; Bonferroni is conservative
   under positive correlation and the induced correlation is printed
   (paired_contrasts_shared_arm), never pretended away.
5. Adding a lane, or a primary to a lane, changes both families and is a
   plan version change, frozen before the added data is opened.

## What this file does not do

It does not pool evidence across lanes (there is no shared estimand), and
it does not licence a meta-analysis: six different endpoints on six
different substrates are six experiments, not six replicates.
