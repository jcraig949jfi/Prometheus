# The Variability of Evolvability: 
## Properties of Dynamic Fitness Landscapes Determine How Phenotypic Variability Evolves

This git repo contains a cleaned version of the code needed to replicate results presented in this study.

Files:
* Model implementation - main_model_script.py
* Additional functions - helper.py
* Analyses regarding randomly generated GRNs and static evolution - exploring_random_grns.ipynb
* Analyses related to average and maximum fitness - analyzing_ave_max_fits.ipynb
* Code to make the first main figure - main_scatter_fig_only.ipynb
* Explore the mutational neighborhood of evolved GRNs - mutate_evolved_GRNs.py, explore_mut_effects.ipynb
* Analyses regarding genotype space exploration - genotype_space_exploration.ipynb
* Analyses regarding evolvability - evolvability_measure.ipynb, pheno_variability_shape.ipynb, percent_offspring_better.ipynb

Dependencies and versions:

Full list available in the ca_grn_environment.yml file.

* python=3.11.7
* ipython=8.20.0 
* matplotlib=3.8.0
* numpy=1.26.4
* scipy=1.12.0