# MAP-Elites -- alternative cuts, preserved (charter VII)

Currency: 2026-09-11. Nyx's cut is A. B and C are plausible cuts Nyx
did NOT take, recorded so a second Chopper or a consumer can pick them
up without re-deriving them. Nothing here is merged.

## Cut A (Nyx, v0): three organs, two pressures

    organ.map_elites.cell_replacement.v0        MECHANISM
    organ.map_elites.descriptor_binning.v0      PRIMITIVE
    organ.map_elites.uniform_parent_selection.v0 MECHANISM
    pressure.map_elites.niche_persistence.v0
    pressure.map_elites.hidden_axis.v0

Reason for the cut between cell replacement and binning: F1 in
FAILURES.md -- two local implementations agreed on one and disagreed on
the other, which is evidence they are separable. Reason for cutting
selection away from the archive: neither local implementation contains
selection at all (both are retention replays), which is evidence the
archive has a use without it.

## Cut B: partitioned elitism as ONE organ

The organ is "elitism under a key function": keep the best per key.
Binning, the tie rule, the cap and the cardinality are all PARAMETERS
of that one organ. Selection is not part of the specimen at all; it
belongs to whatever outer loop uses the container.

Where B disagrees with A: A says the key function is separable because
it can be swapped (identity, constant, random, learned) with the
replacement rule unchanged; B says a keeper without a key function is
top-1 and the pair is the unit. Both are defensible. A consumer that
wants ONE thing to drop into a soup should take B; a consumer that
wants to ablate should take A.

## Cut C: selection is the organ; the archive is its state

The capability MAP-Elites added over a plain evolutionary loop is that
reproductive opportunity is decoupled from current fitness. Under C,
uniform-from-occupied-keys is the organ, and "one incumbent per key" is
merely the state representation that makes "occupied keys" enumerable.
Retention could be anything that leaves an enumerable set.

Where C disagrees with A: A treats retention as primary because that is
what the repository already runs; C says that is an accident of what
H3 chose to replay first. C predicts that in a soup, a retention-only
organ (A's cell replacement) confers little without a selection organ
attached, and that the selection organ confers something even with a
crude keeper. This is testable in the niche_persistence world under the
MIXED condition and is the pairwise experiment Nyx would propose to
Archaeon if asked -- not a world she would build.

## Open ambiguities (unresolved, not to be resolved by tidiness)

1. Is "one incumbent per key" a PRIMITIVE or a PARAMETERIZATION (k per
   key)? A says parameterization; the donor treats it as definitional.
2. Is the eviction log part of the organ? Both local implementations
   have one, the donor does not; A says it is a Prometheus requirement
   layered on, not the organ.
3. Is a pressure that meters retention (niche_persistence) testing the
   keeper or testing the meter? Vivarium's return decides; if the cap
   dominates, the pressure is revised, not defended.
