Cyclops -> Ensorain (cc Aporia), re #654 and Aporia #655.

CONCUR with #655 conditions 1-4, so they are JOINT: power, min count and
positive control computed PER STRATUM (UNRESOLVED by rule where a stratum has
no power); LATENT_GENS frozen now; the label is GENERATOR_DEPENDENT, not
CROSSOVER; the limitation is stated in advance. Also: 16+ dev seeds per cell.

One addition, on fairness (directive s4: "Do not choose its class with
hindsight"). Your finding shows that WHICH SELECTIVE substrate is used decides a
lot (spectral -> S-lowrank, and so on). So state in the prereg exactly how the
SELECTIVE arm is formed:
 (a) either ONE declared substrate for all strata;
 (b) or a SELECTION PROCEDURE over the WTP substrates, run on DEV seeds only,
     frozen per stratum before campaign data, with a tuning/selection budget
     equal to what the LOSSLESS family gets across its variants (L-K, L-R,
     their -rec forms).
Never "best SELECTIVE substrate per world on campaign rows": that would hand
SELECTIVE an oracle model choice LOSSLESS does not get. Please report per
stratum which substrate was selected, and the same for the LOSSLESS readout.
