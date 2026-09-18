+=====================================================================+
|  CAMPAIGN 4 -- DAMAGE GEOMETRY MAP (directive section 6)            |
+=====================================================================+

Every rate is an applied-edit (or birth) share with its source slot; D1
(execution fault) is 0 by construction on this substrate (D4-002), so the
'fatal loss' column is 0 everywhere and the loss lives in D2 + D3.

condition                                        mag  fatal  degen  neutr  coher viable  exapt      n
----------------------------------------------------------------------------------------------------
frozen substrate, single edit / config_perturb     1  0.000  0.446  0.493  0.063  0.500  0.007    428
frozen substrate, single edit / deletion           1  0.000  0.484  0.327  0.189  0.361  0.007    440
frozen substrate, single edit / duplication        1  0.000  0.549  0.367  0.084  0.380  0.000    368
frozen substrate, single edit / insertion          1  0.000  0.571  0.337  0.095  0.356  0.008    368
frozen substrate, single edit / movement           1  0.000  0.469  0.399  0.132  0.416  0.005    416
frozen substrate, single edit / operand_pertur     1  0.000  0.329  0.616  0.057  0.623  0.004    456
frozen substrate, single edit / randomization      1  0.000  0.638  0.217  0.145  0.243  0.011    456
frozen substrate, single edit / reference_redi     1  0.000  0.294  0.667  0.040  0.680  0.002    456
frozen substrate, single edit / region_swap        1  0.000  0.561  0.295  0.145  0.318  0.018    440
frozen substrate, single edit / replacement        1  0.000  0.471  0.379  0.151  0.397  0.009    456
frozen substrate, single edit / splice             1  0.000  0.583  0.284  0.133  0.301  0.007    422
frozen substrate, single edit / unreachable_re     1  0.000  0.150  0.850  0.000  0.850  0.000    160
single edit, stratum / delay_general               1  0.000  0.390  0.422  0.190  0.430  0.000    984
single edit, stratum / gen0_random                 1  0.000  0.998  0.002  0.002  0.002  0.000   1035
single edit, stratum / shelf                       1  0.000  0.266  0.602  0.133  0.646  0.019   1606
single edit, stratum / w0_solver                   1  0.000  0.399  0.505  0.097  0.509  0.003   1355
frozen substrate, radius 1                         1  0.000  0.425  0.467  0.110  0.478  0.009    456
frozen substrate, radius 2                         2  0.000  0.546  0.305  0.149  0.336  0.013    456
frozen substrate, radius 4                         4  0.000  0.713  0.147  0.145  0.167  0.004    456
frozen substrate, radius 8                         8  0.000  0.809  0.046  0.147  0.070  0.007    456
frozen substrate, radius 16                       16  0.000  0.903  0.004  0.094  0.011  0.007    456
single edit of ancestral population on W2_K2       1  0.000    -    0.538  0.149  0.581    -     8270
single edit of ordinary population on W2_K2        1  0.000    -    0.789  0.077  0.815    -     9000
single edit of perturbed population on W2_K2       1  0.000    -    0.863  0.044  0.875    -     9135
held-out family, baseline (per birth)          birth  0.000    -      -      -    0.740    -   185230

EVENTUAL DESCENDANT CONSEQUENCE (lineage slots)
------------------------------------------------------------
  C4-05 neutral walk
    connected_depth_median           16
    acceptance_by_bin                {"1-2": 0.5489, "3-4": 0.5281, "5-8": 0.5375, "9-16": 0.5629}
    held_out_exaptation_by_depth     {"0": 0.0, "2": 0.016, "4": 0.0319, "8": 0.0372, "16": 0.0426}
    structural_diversity_by_depth    {"0": 0.0, "2": 0.3041, "4": 0.4658, "8": 0.6432, "16": 0.7601}
    reading                          "the neutral band is fully connected to depth 16; held-out exaptation grows .016 -> .043 (single edit .006); below the .
  C4-06 recombination vs mutation-only
    crossings                        {"mutation_only": 0, "recombination": 0}
    births_viable_share              {"mutation_only": {"mated_no_splice": null, "mated_splice": null, "mutation": 0.8195}, "recombination": {"mated_no_splic
    reading                          "no W2_K2 summit in either arm at G=100 from 188 drifted lineages; mate-splice births 8 points less viable"
  C4-08 selected descendants
    loss_by_population               {"ancestral": 0.4187, "ordinary": 0.1848, "perturbed": 0.1246}
    coherent_by_population           {"ancestral": 0.1492, "ordinary": 0.0767, "perturbed": 0.0436}
    mean_len_by_population           {"ancestral": 19.133, "ordinary": 40.057, "perturbed": 62.458}
    reading                          "selection halves single-edit loss (.42 -> .19 -> .13) by building neutrality (coherent .15 -> .04) and length (19 -> 62
  C4-09 lateral ecology
    rescues                          [460, 446, 335]
    rescue_survival                  [0.4043, 0.3049, 0.5463]
    per_world_improved_seeds         {"W0": 0, "W1_d1": 0, "W1_d4": 0, "W2_K2": 1}
    extra_compute_ratio              [0.739, 0.7279, 0.6462]
    predictions                      {"P1": {"held": true, "stated": "rescue survival >= .25", "values": [0.4043, 0.3049, 0.5463]}, "P2": {"held": false, "pe
    overhead_shape                   false

SUBSTRATE FACTS: {"d1_eligible": 0, "pairwise_tvd_min_max": [0.0228, 0.633], "traversable_region_by_stratum": {"delay_general": false, "gen0_random": false, "shelf": true, "w0_solver": false}}

CAMPAIGN DISPOSITION (C4-10): NO_CONDITION_SELECTED   selected: []
claims: {}

sources: C4-01/attempts/a02/FLOW_TABLES.json, C4-02/attempts/a01/CURVES.json, C4-08/attempts/a01/ROBUSTNESS_TABLES.json, C4-05/attempts/a01/WALK_TABLES.json, C4-06/attempts/a01/SUMMARY.json, C4-09/attempts/a01/ECOLOGY.json, C4-10/attempts/a01/TRIAL.json
