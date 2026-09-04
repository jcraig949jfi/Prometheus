import numpy as np
import argparse
from tqdm import trange
from pathlib import Path

import helper

"""#Evolutionary algorythm"""

def evolutionary_algorithm(pop_size, grn_size, num_cells, dev_steps, mut_rate, num_generations, selection_prop, rules, mut_size, folder, seed_ints, season_len, job_array_id):

  #Setting up
  mut_blast = False
  fit_blast = False

  rules_str=''.join(str(num) for num in rules)
  seedints_str=''.join(str(num) for num in seed_ints)
  mut_rate_str = str(mut_rate)[0] + str(mut_rate)[-1]
  mut_size_str = str(mut_size)[0] + str(mut_size)[-1]
  selection_prop_str = str(selection_prop)[0] + str(selection_prop)[-1]
  assert (len(str(mut_rate)) == 3) & (len(str(mut_size)) == 3) & (len(str(selection_prop)) == 3), f"mut_rate, mut_size, or selection_prop not in the x.y format"
  
  #Set seed for random
  rand_seed_str = str(pop_size)+str(grn_size)+str(num_cells)+str(dev_steps)+mut_rate_str+mut_size_str+selection_prop_str+str(season_len)+rules_str+seedints_str+str(job_array_id)
  print(int(rand_seed_str))
  
  if mut_blast:
    rand_seed_str = rand_seed_str + "1"
  if fit_blast:
    rand_seed_str = rand_seed_str + "2"

  rand_seed = helper.map_to_range(int(rand_seed_str))
  print(rand_seed)

  np.random.seed(rand_seed)

  with open("experiment_seeds.txt", 'a') as f:
    np.savetxt(f, [np.array([rand_seed_str,str(rand_seed)])], delimiter=",", fmt="%s")

  #Creating start expression pattern
  geneid = 1
  seeds=[]
  inputs=[]
  for seed_int in seed_ints:
    #Make seeds, 1024 is one-hot
    start_pattern = helper.seedID2string(seed_int, num_cells)
    seeds.append(start_pattern)
    #Make starting expression for whole population
    start_expression = helper.seed2expression(start_pattern, pop_size, num_cells, grn_size, geneid)
    inputs.append(start_expression)

  #Creating targets
  targets=[]
  seeds_ints=[]
  for idx, seed in enumerate(seeds):
    targets.append(helper.rule2targets_wrapped_wstart(int(rules[idx]), L=dev_steps+1, N=num_cells, start_pattern=seed))
    binary_string = ''.join(seed.astype(str))
    seeds_ints.append(int(binary_string, 2)) #for file naming
  seeds_id='-'.join([str(number) for number in seeds_ints]) #id of start pattern for each season
  rules_id='-'.join([str(number) for number in rules])
  where_overlap = np.where(targets[0]==targets[1])
  where_no_overlap = np.where(targets[0]!=targets[1])

  #Logging
  max_fits = []
  ave_fits = []
  all_pheno_stds = []
  best_std = []
  pheno_stds = []
  spec_pheno_stds = []
  geno_stds = []
  saveat = list(range(num_generations))

  if season_len > num_generations: #static experiment
    filename = f"{folder}/stats_{season_len}_{rules[0]}_{seeds_ints[0]}_{job_array_id}"
  else:
    filename = f"{folder}/stats_{season_len}_{rules_id}_{seeds_id}_{job_array_id}"

  #Defining variables
  curr = 0
  worst= -num_cells*dev_steps #not a bug because you are getting the first row good for sure
  selection_size=int(pop_size*selection_prop)
  num_child = int(pop_size / selection_size) - 1
  tot_children = num_child * selection_size
  num_genes_mutate = int((grn_size + 2) * grn_size * tot_children * mut_rate)

  #Creating population
  pop = np.random.randn(pop_size, grn_size+2, grn_size).astype(np.float64)

  season_counter = 0
  # Main for loop
  for gen in trange(num_generations):

    # Generating phenotypes
    #Return [pop_size, dev_stepss+1, num_cellsxgrn_size] np.float64 array
    phenos = helper.develop(inputs[curr], pop, dev_steps, pop_size, grn_size, num_cells)
    alt_input = (curr + 1) % 2
    phenos_alt = helper.develop(inputs[alt_input], pop, dev_steps, pop_size, grn_size, num_cells)
    #get second gene for each cell only, the one I decided will matter for the fitness
    #pop_size, dev_steps, NCxNG
    p=phenos[:,:,1::grn_size]
    p_alt=phenos_alt[:,:,1::grn_size]

    # Logging phenotypic variation
    if gen > 0:
      #across population
      #phenotypic variation
      all_pheno_std=np.std(p, axis=0)
      all_pheno_std = all_pheno_std.mean()
      all_pheno_stds.append(all_pheno_std)
      #genotypic variation
      temp_pop = np.reshape(pop, (pop_size, (grn_size+2)*grn_size))
      geno_std = np.std(temp_pop, axis=0).mean() #calc std for each weight in the pop, then average
      geno_stds.append(geno_std)

      #more sophisticated phenotypic variation tracking
      pheno_std, best_std_val, best_std_id, averaged_combined_std = helper.calc_pheno_variation(p, children_locs, num_child, parent_locs, dev_steps, num_cells, where_overlap, where_no_overlap)
      pheno_stds.append(pheno_std)
      best_std.append(best_std_val)
      spec_pheno_stds.append(averaged_combined_std)
      best_std_grn = pop[parent_locs[best_std_id]]

    #Calculating fitnesses
    fitnesses = []
    fitnesses_alt = []
    for target in targets:
      if fit_blast and season_counter < 3:
        rand_target = np.random.rand(dev_steps+1, num_cells)
        temp_fitnesses = helper.fitness_function_ca(p, rand_target)
      else:
        temp_fitnesses = helper.fitness_function_ca(p, target)
      temp_fitnesses=1-(temp_fitnesses/worst) #0-1 scaling
      fitnesses.append(temp_fitnesses)
      #with alternative input
      temp_fitnesses_alt = helper.fitness_function_ca(p_alt, target)
      temp_fitnesses_alt=1-(temp_fitnesses_alt/worst) #0-1 scaling
      fitnesses_alt.append(temp_fitnesses_alt)
    
    fitnesses_to_use = fitnesses[curr]

    #Selection
    perm = np.argsort(fitnesses_to_use)[::-1]

    #Logging
    best_grn = pop[perm[0]]
    max_fit=fitnesses[curr].max().item()
    ave_fit=fitnesses[curr].mean().item()
    max_fits.append(max_fit)  # keeping track of max fitness
    ave_fits.append(ave_fit)  # keeping track of average fitness

    # location of top x parents in the array of individuals
    parent_locs = perm[:selection_size]
    # location of individuals that won't survive and hence will be replaced by others' children
    children_locs = perm[selection_size:]

    # Logging lineages, forward pointing. 
    # this generation, these are the parents, this is where their kids will go
    edges = []
    for p in parent_locs:
      edges.append([(gen,p),(gen+1,p)]) 
      #each parent stays in the population where it was
    for idx, p in enumerate(np.tile(parent_locs,num_child)):
      #np tile makes it so that it is parent 1, parent 2, parent 1, parent 2, etc.
      edges.append([(gen,p),(gen+1,children_locs[idx])])
      #parent 1 has a kid, then parent 2 has a kid, then parent 1 has a kid, then parent 2 has a kid, etc.
    #edges contains ids, which are also the indicies of the individuals in the population
    #so in the fitnesses variable for example, we will know if generation 2 10th individual (2,10) in the edge list, 
    #someone with no kids, had a good fitness or not, by looking at generation 2, 10th idx in the fitnesses list.

    parents = pop[parent_locs]
    children = np.tile(parents, (num_child, 1, 1))

    #Mutation
    mutations = np.random.randn(num_genes_mutate) * mut_size
    x, y, z = children.shape
    xs = np.random.choice(x, size=num_genes_mutate)
    ys = np.random.choice(y, size=num_genes_mutate)
    zs = np.random.choice(z, size=num_genes_mutate)
    children[xs, ys, zs] = children[xs, ys, zs] + mutations

    pop[children_locs] = children  # put children into population

    #Change environment
    season_counter += 1
    if gen % season_len == season_len - 1: # flip target
      season_counter = 0
      if mut_blast:
        mutations = np.random.randn(pop_size, (grn_size+2), grn_size)
        pop = pop + mutations
      else:
        curr = (curr + 1) % len(targets)

    #Saving to file
    if gen in saveat:
      with open(filename+"_best_grn.txt", 'a') as f:
        np.savetxt(f, best_grn, newline=" ")
      with open(filename+"_both_fits.txt", 'a') as f:
        np.savetxt(f, np.array(fitnesses), newline=" ")
      with open(filename+"_both_fits_alt.txt", 'a') as f:
        np.savetxt(f, np.array(fitnesses_alt), newline=" ")
      save_edges=np.array(edges)
      save_edges=np.reshape(save_edges, (pop_size,4))
      with open(filename+"_edges.txt", 'a') as f:
        np.savetxt(f, save_edges, newline=" ")
      if gen > 0:
        with open(filename+"_best_grn_std.txt", 'a') as f:
          np.savetxt(f, best_std_grn, newline=" ")

  #Saving to file
  with open(filename+"_maxfits.txt", 'w') as f:
    np.savetxt(f, max_fits, newline=" ")
  with open(filename+"_avefits.txt", 'w') as f:
    np.savetxt(f, ave_fits, newline=" ")
  with open(filename+"_all_pheno_stds.txt", 'w') as f:
    np.savetxt(f, all_pheno_stds, newline=" ")
  with open(filename+"_beststd.txt", 'w') as f:
    np.savetxt(f, best_std, newline=" ")
  with open(filename+"_pheno_stds.txt", 'w') as f:
    np.savetxt(f, pheno_stds, newline=" ")
  with open(filename+"_spec_pheno_stds.txt", 'w') as f:
    np.savetxt(f, spec_pheno_stds, newline=" ")
  with open(filename+"_geno_stds.txt", 'w') as f:
    np.savetxt(f, geno_stds, newline=" ")

  #Save population so that I can run for longer if needed
  pop_2_save = np.reshape(pop, (pop_size,(grn_size+2)*grn_size))
  with open(filename+"_last_pop.txt", 'w') as f:
    np.savetxt(f, pop_2_save, newline=" ")

  return max_fit

if __name__ == "__main__":
  parser = argparse.ArgumentParser()

  parser.add_argument('--pop_size', type=int, default=1000, help="Population size")
  parser.add_argument('--grn_size', type=int, default=22, help="GRN size") 
  parser.add_argument('--num_cells', type=int, default=22, help="Number of cells") 
  parser.add_argument('--dev_steps', type=int, default=22, help="Number of developmental steps") 

  parser.add_argument('--selection_prop', type=float, default=0.1, help="Percent pruncation") 
  parser.add_argument('--mut_rate', type=float, default=0.1, help="Number of mutations") 
  parser.add_argument('--mut_size', type=float, default=0.5, help="Size of mutations") 
  parser.add_argument('--num_generations', type=int, default=9899, help="Number of generations")
  parser.add_argument('--season_len', type=int, default=300, help="season length")

  parser.add_argument('--seed_ints', nargs='+', default=[69904,149796], help='List of seeds in base 10')
  parser.add_argument('--rules', nargs='+', default=[30,30], help='List of rules')

  parser.add_argument('--job_array_id', type=int, default=0, help="Job array id to distinguish runs")

  args = parser.parse_args()

  #Writing to file
  folder_name = Path("~/scratch/detailed_save/variable").expanduser()
  args.folder = folder_name

  #Make sure that user provided a rule and a seed for each alternative environment
  assert len(args.rules) == len(args.seed_ints), f"Num rules {len(args.rules)} != num seeds {len(args.seed_ints)}"

  print("running code", flush=True)
  evolutionary_algorithm(**vars(args))

  print("completed")

  
    
