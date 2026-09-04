"""Build HCA_NEUTRAL_NETWORK_NEGATIVES.jsonl - lane HC-L01 negative controls.

Cases where a same-state different-future effect EXISTS but does NOT translate into
subsequent acquisition, or where a starting-position variable demonstrably fails to
predict acquisition. Schema follows ACCESSIBILITY_WITHOUT_ACQUISITION_NEGATIVES.jsonl.
Written 2026-09-03.
"""
import json

rows = [
    {
        "specimen_id": "background-cowperthwaite-2008-founding-network-size",
        "source": "Cowperthwaite MC, Economo EP, Harcombe WR, Miller EL, Meyers LA, 'The ascent of the abundant: how mutational networks constrain evolution', PLoS Comput Biol 4(7):e1000110. Corroborated verbatim in the Supplementary Information of Draghi et al. 2010 section 6.2",
        "accessibility_effect": "PRESENT at the phenotype level. Exhaustive folding of ALL RNA sequences of length 12-18 nt gives the exact one-mutant neighbour-phenotype distribution per phenotype, and phenotypes differ enormously in abundance and in the accessibility statistic A",
        "acquisition_link": "ABSENT FOR THE STARTING POSITION, PRESENT FOR THE DESTINATION. Across 2400 forward simulations (20 replicate populations, N=1000, 1e6 generations per start/target pair), TARGET phenotype abundance predicted whether the population reached it (r = 0.76, P = 2.2e-4), but FOUNDING phenotype abundance did not predict the outcome at all (r = -0.023, P = 0.17). Draghi et al. state the same conclusion in their own words: 'Cowperthwaite et al. (2008) found no relation between the size of the neutral network on which a population began, and its success at evolving to a distant phenotypic optimum'",
        "why_it_is_a_background_not_a_particle": "This is the cleanest published negative control for the programme's hypothesis. Where you START on the network - the very quantity HCA claims should matter - carried no information about subsequent acquisition, while a property of the DESTINATION did. If the effect this programme is chasing exists, it must survive a design in which starting-position variables have already been shown to fail",
        "kill_condition": "K7-analogue, imported from the literature",
        "evidence_tier": "HCL01_LANE_FULL_TEXT (open access) plus verbatim corroboration in a second primary source",
        "note": "Phenotype abundance is itself confounded with structural simplicity and GC content, so the positive half of this result may be a folding-thermodynamics artefact. The NEGATIVE half is the part that matters here and it is not weakened by that confound"
    },
    {
        "specimen_id": "background-wagner-2008-robustness-does-not-buy-evolvability",
        "source": "Wagner A 2008 Proc R Soc B 275:91-100, read via https://pmc.ncbi.nlm.nih.gov/articles/PMC2562401/ ; secondary characterisation in Draghi et al. 2010 Supplementary Information section 6.2",
        "accessibility_effect": "PRESENT AND LARGE at matched phenotype. Sequences drawn from the SAME neutral network have largely non-overlapping sets of novel structures in their one-mutant neighbourhoods - median overlap statistic Q = 0.6 - from full 3n-neighbourhood enumeration over 7.5e4 sequences of length 30",
        "acquisition_link": "NOT MEASURED, and the cheap-state relation runs the WRONG WAY. Genotype robustness correlates NEGATIVELY with genotype evolvability, Spearman s = -0.64, p < 1e-17: 'the greater a sequence's robustness, the lesser its evolvability'. Only at the PHENOTYPE level does robustness promote evolvability",
        "why_it_is_a_background_not_a_particle": "A textbook same-state different-future effect, established at matched phenotype with exhaustive enumeration, that is never connected to acquisition. It shows how easy the H2 measurement is in this substrate and how consistently the field stops there",
        "kill_condition": "n/a - the acquisition arm was never run",
        "evidence_tier": "HCL01_LANE_FULL_TEXT_EXTRACTION",
        "note": "DISCREPANCY ON RECORD, DO NOT SILENTLY RESOLVE. Draghi et al. 2010 SI characterise this paper as having found 'no relationship between the robustness of a sequence, and a measure of its evolvability', whereas the primary text reports a strong NEGATIVE relationship (s = -0.64). Either Draghi et al. refer to a different measure or the characterisation is loose. Anyone citing the Draghi sentence must check the primary text first"
    },
    {
        "specimen_id": "background-ancel-fontana-2000-canalisation-dead-end",
        "source": "Ancel LW, Fontana W, 'Plasticity, evolvability, and modularity in RNA', J Exp Zool 288:242-283, http://www.bio.utexas.edu/research/meyers/_docs/publications/AncelJEZ00.pdf",
        "accessibility_effect": "PRESENT at matched phenotype. Three sequence classes sharing an IDENTICAL minimum-free-energy structure - random/inverse-folded, neutrally evolved, and canalised - differ sharply in the fraction of one-mutant neighbours preserving the ground state: neutrality 0.184, 0.412, 0.456 respectively, by exhaustive scan of all ~3n = 228 one-error mutants per sequence",
        "acquisition_link": "PRESENT BUT INVERTED. The class with the richest history and the highest neutrality - the canalised sequences - became an evolutionary DEAD END. More history and more robustness bought LESS subsequent acquisition, not more",
        "why_it_is_a_background_not_a_particle": "The programme's hypothesis must not assume the sign. Here the same-state different-future effect is real and its consequence for acquisition is negative. Any HCA claim needs a pre-registered direction and a reason for it",
        "kill_condition": "sign-inversion warning rather than a kill",
        "evidence_tier": "HCL01_LANE_FULL_TEXT (read by delegated agent)",
        "note": "TAUTOLOGY WARNING that travels with this specimen. In Ancel and Fontana the accessibility measure IS neutrality, i.e. mutational robustness, so accessibility cannot be shown to beat robustness here - the two are collinear by construction. Plastogenetic congruence itself is a CROSS-SECTIONAL correlation computed on a single genotype at one instant (its thermal plastic repertoire against the folds of its one-error mutants); it is not a time-t-predicts-time-t-plus-n measurement and must never be cited as one"
    },
    {
        "specimen_id": "background-greenbury-aguirre-H2-without-any-acquisition-arm",
        "source": "Greenbury SF, Schaper S, Ahnert SE, Louis AA 2016 PLoS Comput Biol 12(3):e1004773 https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004773 ; Aguirre J, Buldu JM, Stich M, Manrubia SC 2011 PLoS ONE 6(10):e26324 https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0026324",
        "accessibility_effect": "PRESENT, MEASURED, AND THE BEST-QUANTIFIED IN THE LANE. Greenbury et al.: 10,000 sampled genotype triples per GP map, full 1-mutation neighbourhood enumerated, Bhattacharyya coefficient comparing neighbourhood phenotype distributions with the K-2 mutual neighbours excluded; genotypes sharing an identical phenotype have systematically more similar neighbourhoods when they are neutral neighbours than when distant on the same network - ratio 1.357 +/- 0.003 (RNA20), 1.063 +/- 0.001 (Polyomino S3,8), 1.025 +/- 0.001 (HP5x5). Aguirre et al.: EXHAUSTIVE folding of all 4^12 = 16,777,216 RNA sequences, per-genotype degree computed for every one, stratified by position and connectivity class",
        "acquisition_link": "COMPLETELY ABSENT. Neither paper runs an evolutionary simulation in which subsequent innovation is measured. Aguirre et al. offer a replication-mutation matrix argument about stationary distribution WITHIN the same phenotype, i.e. persistence, not acquisition of anything new",
        "why_it_is_a_background_not_a_particle": "These are the strongest H2 measurements available anywhere and they establish that the effect this programme needs is real, large and cheap to measure. They also establish that measuring it is not the bottleneck. Nobody in this literature has taken the next step",
        "kill_condition": "n/a - the acquisition arm was never run",
        "evidence_tier": "HCL01_LANE_FULL_TEXT (read by delegated agent)",
        "note": "The effect sizes outside RNA are modest - 1.025 to 1.063 - so a programme betting on this phenomenon should expect a small effect in any substrate that is not RNA-like, and should size its experiments accordingly. Compute the standard error before choosing a gate"
    }
]

with open("HCA_NEUTRAL_NETWORK_NEGATIVES.jsonl", "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=True) + "\n")
print("wrote", len(rows), "negative-control rows")
