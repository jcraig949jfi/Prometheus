#IMPORT PACKAGES

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from numba import njit, prange
import seaborn as sns
import hashlib
import os
from scipy.stats import mannwhitneyu

#Parameter for sigmoid function
ALPHA = 10

#Helper for hashing
def map_to_range(value):
  return int(hashlib.sha256(str(value).encode()).hexdigest(), 16) % (2**32)

#Calculating different features of phenotypic variability
def calc_pheno_variation(p, children_locs, num_child, parent_locs, dev_steps, num_cells, where_overlap, where_no_overlap):
    
    child_phenotypes = p[children_locs] 
    # inner most list: first: first born of each parent, second: second borns of each parent, etc.
    # so it is NOT all kids of 1 parent, then the other parent, etc.
    reshaped=np.reshape(child_phenotypes, (num_child, len(parent_locs), (dev_steps+1)*num_cells))
    #reshaped is num child per parent, num parents, (dev_steps+1)*num_cells shaped. 
    # so [:,0,:] is all kids of one parent
    pheno_std=np.std(reshaped,axis=0) #one std for each of the parents, so pop_size*trunc_prop now 10
    pheno_std = pheno_std.mean(1).mean() #first averaged across cells, then averaged across individuals in the population
    # generic phenotypic variation among offspring of the same parent

    #looking for more sophisticated phenotypic variation:
    if True:
        reshaped2D=np.reshape(reshaped, (num_child, len(parent_locs), dev_steps+1, num_cells))

        values_they_should_match = reshaped2D[:,:,where_overlap[0],where_overlap[1]]
        #values_they_should_match.shape #4 kids, 2 parents, N values, where N is the number of cells where they overlap
        matching_std = np.std(values_they_should_match, axis=0) #among the 4 kids of 1 parent, output is an N long list for each of the 2 parents
        matching_std = matching_std.mean(axis=1) #average across the N overlaps, to get 1 value for each parent

        #repeat for non-overlap
        values_they_shouldnt_match = reshaped2D[:,:,where_no_overlap[0],where_no_overlap[1]]
        #values_they_should_match.shape #4 kids, 2 parents, N values, where N is the number of cells where they don't overlap
        nonmatching_std = np.std(values_they_shouldnt_match, axis=0) #among the 4 kids of 1 parent, output is an N long list for each of the 2 parents
        nonmatching_std = nonmatching_std.mean(axis=1) #average across the N non overlaps, to get 1 value for each parent

        #minimum std is 0, max is 0.5 in the case of values that range between 0 and 1
        combined_std = nonmatching_std - matching_std
        averaged_combined_std = np.mean(combined_std)
        best_std_id = np.argmax(combined_std)

        return pheno_std, np.max(combined_std), best_std_id, averaged_combined_std
    

#Sigmoid function for GRN update
@njit("f8[:,:](f8[:,:],i8, i8)")
def sigmoid(x,a,c):
  return 1/(1 + np.exp(-a*x+c))

#Fitness function
def fitness_function_ca(phenos, targ):
  """
  Takes phenos which is pop_size * iters+1 * num_cells and targ which is iters+1 * num_cells
  Returns 1 fitness value for each individual, np array of size pop_size
  """
  return -np.abs(phenos - targ).sum(axis=1).sum(axis=1)


#Convert between an integer and a series of 1s and 0s
def seedID2string(seed_int, num_cells):
  #takes an integer, turns it into a starting pattern
  binary_string = bin(int(seed_int))[2:]
  binary_list = [int(digit) for digit in binary_string]
  start_pattern = np.array(binary_list)
  start_pattern=np.pad(start_pattern, (num_cells-len(start_pattern),0), 'constant', constant_values=(0))
  return start_pattern

#Convert between start pattern and gene expression state where development starts from
def seed2expression(start_pattern, pop_size, num_cells, grn_size, geneid):
  #takes a starting pattern and makes a population of starting gene expressions
  start_gene_values = np.zeros((pop_size, int(num_cells * grn_size)))
  start_gene_values[:,geneid::grn_size] = start_pattern
  start_padded_gene_values = np.pad(start_gene_values, [(0,0),(1,1)], "wrap")
  start_padded_gene_values = np.float64(start_padded_gene_values)
  return start_padded_gene_values


#DO THE MULTICELLULAR DEVELOPMENT--------------------

#Update genes in cell given the whole GRN
@njit("f8[:](f8[:], f8[:,:], i8, i8)")
#Make sure that numpy imput in foat64! Otherwise this code breaks
def update_with_grn(padded_gene_values, grn, num_cells, grn_size):
  """
  Gene expression pattern + grn of a single individual -> Next gene expression pattern
  Takes
  - padded_gene_values: np array with num_genes * num_cells + 2 values
  Gene 1 in cell 1, gene 2 in cell 1, etc then gene 1 in cell 2, gene 2 in cell 2... plus left-right padding
  - grn: np array with num_genes * num_genes +2 values, shape of the GRN
  """
  #This makes it so that each cell is updated simultaneously
  #Accessing gene values in current cell and neighbors
  windows = np.lib.stride_tricks.as_strided(
      padded_gene_values, shape=(num_cells, grn_size + 2), strides=(8 * grn_size, 8)
  )
  #Updating with the grn
  next_step = windows.dot(grn)
  c = ALPHA/2
  next_step = sigmoid(next_step,ALPHA,c)

  #Returns same shape as padded_gene_values
  return next_step.flatten()


#Update genes in cell given the only internal genes in the GRN
@njit("f8[:](f8[:], f8[:,:], i8, i8)")
#Make sure that numpy imput in foat64! Otherwise this code breaks
def update_internal(padded_gene_values, grn, num_cells, grn_size):
  """
  Gene expression pattern + grn of a single individual -> Next gene expression pattern
  Takes
  - padded_gene_values: np array with num_genes * num_cells + 2 values
  Gene 1 in cell 1, gene 2 in cell 1, etc then gene 1 in cell 2, gene 2 in cell 2... plus left-right padding
  - grn: np array with num_genes * num_genes +2 values, shape of the GRN
  """
  #Updating with the internal grn
  internal_grn = grn[1:-1,:]
  gene_vals = padded_gene_values[1:-1].copy()
  gene_vals = gene_vals.reshape(num_cells,grn_size)
  next_step = gene_vals.dot(internal_grn)
  c = ALPHA/2
  next_step = sigmoid(next_step,ALPHA,c)

  #Returns same shape as padded_gene_values
  return next_step.flatten()


#Full developmental process from starting gene expression until the end of a given number of developmental steps
#Might be faster non-parallel depending on how long computing each individual takes!
@njit(f"f8[:,:,:](f8[:,:], f8[:,:,:], i8, i8, i8, i8)", parallel=True)
def develop(
    padded_gene_values,
    grns,
    iters,
    pop_size,
    grn_size,
    num_cells
):
  """
  Starting gene expression pattern + all grns in the population ->
  expression pattern throughout development for each cell for each individual
  DOES NOT assume that the starting gene expression pattern is the same for everyone
  returns tensor of shape: [POP_SIZE, N_ITERS+1, num_cellsxgrn_size]
  N_ITERS in num developmental steps not including the initial step
  """
  NCxNGplus2 = padded_gene_values.shape[1]
  history = np.zeros((pop_size, iters+1, NCxNGplus2 - 2), dtype=np.float64)

  #For each individual in parallel
  for i in prange(pop_size):
    #IMPORTANT: ARRAYS IN PROGRMING when "copied" just by assigning to a new variable (eg a=[1,2,3], b = a)
    #Copies location and so b[0]=5 overwrites a[0] too! Need .copy() to copy variable into new memory location
    grn = grns[i]
    state = padded_gene_values[i].copy()
    history[i, 0, :] = state[1:-1].copy() #saving the initial condition
    #For each developmental step
    for t in range(iters):
      #INTERNAL
      state[1:-1] = update_internal(state, grn, num_cells, grn_size)
      #To wrap around, change what the pads are
      state[0] = state[-2] #the last element of the output of update_with_grn
      state[-1] = state[1]
      #EXTERNAL
      state[1:-1] = update_with_grn(state, grn, num_cells, grn_size)
      #To wrap around, change what the pads are
      state[0] = state[-2] #the last element of the output of update_with_grn
      state[-1] = state[1]
      history[i, t+1, :] = state[1:-1].copy()
  return history


#Given CA rule and initial condition get target pattern
def rule2targets_wrapped_wstart(r, L, N, start_pattern):
  """
  We need 2 flips:

  1) from value order to wolfram order

    | value | wolfram
  N | order | order
  --|-------|---------
  0 |  000  |  111
  1 |  001  |  110
  2 |  010  |  101
  3 |  011  |  100
  4 |  100  |  011
  5 |  101  |  010
  6 |  110  |  001
  7 |  111  |  000

  so we do:
      rule = rule[::-1]

  2) from array order to base order

  array order: np.arange(3) = [0, 1, 2]

  but base2 orders digits left-to-right

  e.g.
  110 = (1        1        0)    [base2]
         *        *        *
   (2^2) 4  (2^1) 2  (2^0) 1
        ---------------------
      =  4 +      2 +      0  = 6 [base10]

  so we do:
    2 ** np.arange(2)[::-1] = [4 2 1]

  """
  base = 2 ** np.arange(3)[::-1]
  rule = np.array([int(v) for v in f"{r:08b}"])[::-1]
  targets = np.zeros((L, N), dtype=np.int32)
  
  targets[0] = start_pattern

  for i in range(1, L):
    s = np.pad(targets[i - 1], (1, 1), "wrap")
    s = sliding_window_view(s, 3)
    s = (s * base).sum(axis=1)
    s = rule[s]
    targets[i] = s

  return targets.astype(np.float64)


#FOR PLOTTING------------------------

#Pretty plotting of CA patterns and phenotypes
def imshow_ca(grid, ax):
    rocket_cmap = sns.color_palette("rocket", as_cmap=True)
    im = ax.imshow(grid, cmap=rocket_cmap,interpolation="nearest")

    # Minor ticks
    ax.set_xticks(np.arange(-0.5, grid.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, grid.shape[0], 1), minor=True)

    # And a corresponding grid
    ax.grid(which="minor", alpha=0.3)
    for tick in ax.xaxis.get_minor_ticks():
        tick.tick1line.set_visible(False)
        tick.tick2line.set_visible(False)
        tick.label1.set_visible(False)
        tick.label2.set_visible(False)
    for tick in ax.xaxis.get_major_ticks():
        tick.tick1line.set_visible(False)
        tick.tick2line.set_visible(False)
        tick.label1.set_visible(False)
        tick.label2.set_visible(False)
    for tick in ax.yaxis.get_minor_ticks():
        tick.tick1line.set_visible(False)
        tick.tick2line.set_visible(False)
        tick.label1.set_visible(False)
        tick.label2.set_visible(False)
    for tick in ax.yaxis.get_major_ticks():
        tick.tick1line.set_visible(False)
        tick.tick2line.set_visible(False)
        tick.label1.set_visible(False)
        tick.label2.set_visible(False)

    return im

def get_pop_TPF(pop, pop_size, num_cells, grn_size, dev_steps, geneid, rule, seed_int_target, seed_int_dev):
  start_pattern = seedID2string(seed_int_target, num_cells)
  target = rule2targets_wrapped_wstart(int(rule), L=dev_steps+1, N=num_cells, start_pattern=start_pattern)

  start_pattern = seedID2string(seed_int_dev, num_cells)
  start_expression = seed2expression(start_pattern, pop_size, num_cells, grn_size, geneid)
   
  all_phenos = develop(start_expression, pop, dev_steps, pop_size, grn_size, num_cells)
  phenos = all_phenos[:,:,geneid::grn_size]
   
  worst= -num_cells*dev_steps
  prefitnesses = fitness_function_ca(phenos, target)
  fitnesses=1-(prefitnesses/worst) #0-1 scaling

  return target, phenos, fitnesses


#Load data from file
def get_fits(rules, seed_ints, metric, root, season_len, num_reps, id_start, extrapolate=True):
    vari_maxs=[np.loadtxt(os.path.expanduser(root+f"variable/stats_{season_len}_{rules[0]}-{rules[1]}_{seed_ints[0]}-{seed_ints[1]}_{i+1+id_start}_{metric}.txt")) for i in range(num_reps)]
    if rules[0] == rules[1]:
        env1_maxs=[np.loadtxt(os.path.expanduser(root+f"static/stats_100000_{rules[0]}_{seed_ints[0]}_{i+1+id_start}_{metric}.txt")) for i in range(num_reps)]
        env2_maxs=[np.loadtxt(os.path.expanduser(root+f"static/stats_100000_{rules[0]}_{seed_ints[1]}_{i+1+id_start}_{metric}.txt")) for i in range(num_reps)]
    else:
        print("scenario not yet implemented")

    if extrapolate:
        diff_len = len(vari_maxs[0]) - len(env1_maxs[0])
        if diff_len > 1:
            env1_maxs=np.array(env1_maxs)
            env2_maxs=np.array(env2_maxs)
            last_elements = env1_maxs[:,-1]
            last_elements=np.tile(last_elements, (diff_len, 1)).T
            env1_maxs = np.hstack((env1_maxs, last_elements))
            last_elements = env2_maxs[:,-1]
            last_elements=np.tile(last_elements, (diff_len, 1)).T
            env2_maxs = np.hstack((env2_maxs, last_elements))

    return vari_maxs, env1_maxs, env2_maxs

#Load data from file specifically when CA rule changes, not init condition, between different seasons
def get_fits_dr(rules, seed_int, metric, root_var, root_stat, season_len, num_reps, id_start, extrapolate=True):
    vari_maxs=[np.loadtxt(os.path.expanduser(root_var+f"stats_{season_len}_{rules[0]}-{rules[1]}_{seed_int}-{seed_int}_{i+1+id_start}_{metric}.txt")) for i in range(num_reps)]
    env1_maxs=[np.loadtxt(os.path.expanduser(root_stat+f"static/stats_100000_{rules[0]}_{seed_int}_{i+1+id_start}_{metric}.txt")) for i in range(num_reps)]
    env2_maxs=[np.loadtxt(os.path.expanduser(root_stat+f"static/stats_100000_{rules[1]}_{seed_int}_{i+1+id_start}_{metric}.txt")) for i in range(num_reps)]

    return vari_maxs, env1_maxs, env2_maxs

#Load data from file - for special experiments involving random mutations or random selection
def get_fits_alt(rules, seed_ints, metric, root, season_len, num_reps, exp_type):
    vari_maxs=[np.loadtxt(os.path.expanduser(root+f"variable/stats_{season_len}_{rules[0]}-{rules[1]}_{seed_ints[0]}-{seed_ints[1]}_{i+1}_{metric}.txt")) for i in range(num_reps)]
    static_maxs=[np.loadtxt(os.path.expanduser(root+f"static/stats_100000_{rules[0]}_{149796}_{i+1}_{metric}.txt")) for i in range(num_reps)]
    special_maxs=[np.loadtxt(os.path.expanduser(root+f"{exp_type}/stats_{season_len}_{rules[0]}-{rules[1]}_{149796}-{149796}_{i+1}_{metric}.txt")) for i in range(5)]

    return vari_maxs, static_maxs, special_maxs    


#Divide up data into seasons
def chunker(runs, season_len = 300):
    florp = np.array(runs).mean(axis=0) # average runs
    all_gens = np.arange(0,np.array(runs).shape[1])
    n_seasons = int(np.floor(florp.shape[0]/season_len))
    chunked_seasons = np.array([florp[i*season_len:(i+1)*season_len] for i in range(n_seasons)])
    chunked_gens = np.array([all_gens[i*season_len:(i+1)*season_len] for i in range(n_seasons)])
    assert chunked_seasons.size == season_len * n_seasons #safety check
    chunked_season1, chunked_season2 = chunked_seasons[0::2], chunked_seasons[1::2]
    chunked_season1_g, chunked_season2_g = chunked_gens[0::2].flatten(), chunked_gens[1::2].flatten()
    # Get maximum for each repeat season:
    max_chunked_season1, max_chunked_season2 = chunked_season1.max(axis=1),chunked_season2.max(axis=1)
    # Get maximum among repeat seasons:
    a = max_chunked_season1.max()
    b = max_chunked_season2.max()

    argmax1 = chunked_season1_g[np.argmax(np.array(chunked_season1))]
    argmax2 = chunked_season2_g[np.argmax(np.array(chunked_season2))]
    std1 = np.array(runs)[:,argmax1].std()
    std2 = np.array(runs)[:,argmax2].std()

    return a,b, std1, std2, np.array(runs)[:,argmax1], np.array(runs)[:,argmax2]


#Calculate x and y value for main scatterplot (Fig. 2.)
def scatter_value(variable, season1, season2, season_len):
    vari_env1, vari_env2, std1, std2, list1, list2 = chunker(variable, season_len=season_len)
    
    season1 = np.array(season1)
    season2 = np.array(season2)
    M_env1 = season1.mean(axis=0).max()
    M_env2 = season2.mean(axis=0).max()
    static1 = season1[:,np.argmax(season1.mean(axis=0))]
    env1_std = static1.std()
    static2 = season2[:,np.argmax(season2.mean(axis=0))]
    env2_std = static2.std()
    
    cohen_d1 = (vari_env1- M_env1) / np.sqrt((std1+env1_std)/2)
    cohen_d2 = (vari_env2- M_env2) / np.sqrt((std2+env2_std)/2)

    #t_stat1, p_value1 = ttest_ind(list1, static1)
    #t_stat2, p_value2 = ttest_ind(list2, static2)
    t_stat1, p_value1 = mannwhitneyu(list1, static1, alternative='two-sided')
    t_stat2, p_value2 = mannwhitneyu(list2, static2, alternative='two-sided')


    diffs = (vari_env1 - M_env1, vari_env2 - M_env2)
    return diffs, (cohen_d1, cohen_d2), (p_value1,p_value2), (list1, list2, static1, static2)
    

#Plot data chunked up to seasons
def chunker_plotting(run, season_len = 300):
    gens=list(range(len(run)))
    n_seasons = int(np.floor(run.shape[0]/season_len))
    chunked_seasons = np.array([run[i*300:(i+1)*300] for i in range(n_seasons)])
    chunked_gens = np.array([gens[i*300:(i+1)*300] for i in range(n_seasons)])

    assert chunked_seasons.size == season_len * n_seasons #safety check

    chunked_season1, chunked_season2 = chunked_seasons[0::2], chunked_seasons[1::2]
    chunked_gens1, chunked_gens2 = chunked_gens[0::2], chunked_gens[1::2]
    
    return chunked_season1, chunked_season2, chunked_gens1, chunked_gens2


#Test GRN on different initial conditions
def try_grn(variable, rule, run_seedints, try_seedints, grn_size, geneid, root, num_cells, dev_steps):
    last_grns=[]
    for i in range(15):
        if variable:
            filename = os.path.expanduser(f"{root}/variable/stats_300_{rule}-{rule}_{run_seedints[0]}-{run_seedints[1]}_{i+1}" + "_best_grn.txt")
        else:
            filename = os.path.expanduser(f"{root}/static/stats_100000_{rule}_{run_seedints}_{i+1}" + "_best_grn.txt")
        grns = np.loadtxt(filename)
        num_grns = int(grns.shape[0]/(grn_size+2)/grn_size)
        grns = grns.reshape(num_grns,grn_size+2,grn_size)
        grn = grns[-1,:,:]
        last_grns.append(grn)
    last_grns = np.array(last_grns)

    last_phenos=[]
    fits = []
    for s in try_seedints:
        targets, phenos, fitnesses = get_pop_TPF(last_grns, len(last_grns), num_cells, grn_size, dev_steps, geneid, rule, s,s)
        last_phenos.append(phenos)
        fits.append(fitnesses)
    last_phenos = np.array(last_phenos)
    fits = np.array(fits)
    return last_phenos, fits, last_grns
