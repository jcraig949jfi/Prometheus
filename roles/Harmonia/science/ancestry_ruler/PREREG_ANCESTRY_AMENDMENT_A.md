# PREREG_ANCESTRY_RULER -> AMENDMENT_A (feasibility; interventions_unseen=true; no control had run)

Harmonia[gandalf-6cd1348b], 2026-09-18, under standing rule A1, written
BEFORE the first execution of ancestry_ruler.py.

    what changed   (1) synthetic world INDEL 0.01 -> 0.0: every genome keeps length 50, so
                       the parsimony distance is Hamming, vectorised in numpy; the
                       Levenshtein fallback stays in the code for records with unequal
                       lengths (the .spop adapter will need it) but is not exercised here.
                   (2) reconstruction candidate set: "strictly earlier birth_time" ->
                       "strictly earlier AND within WINDOW = 12 generations". D3's largest
                       gap is k = 10, so no true parent is excluded by the window in any
                       degradation of the plan.
    why            the preregistered rule compared each of ~12,000 organisms against every
                   earlier organism with a pure-Python Levenshtein: ~72 million 50x50 DPs,
                   hours on M3 for one reconstruction. The amendment makes one
                   reconstruction seconds. The world's other constants (N 200, G 60, L 50,
                   mu 0.02, selection 0.02, seeds) are unchanged.
    consequence    P1-P4 and the four controls are unchanged in wording. The window is a
                   constant a real-fossil adapter must set from the fossil's generation
                   structure, and is reported in every loss table.
