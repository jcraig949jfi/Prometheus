"""
Tensor Explorer — MAP-Elites, Random Walk, and Genetic Algorithm
exploration of the dissection signature tensor.

Loads the pre-built dissection_tensor.pt and runs three GPU-accelerated
explorers to map the landscape of cross-domain mathematical structure.

Explorers:
  1. MAP-Elites: discretize strategy-group space, find the best
     cross-domain neighbor in each occupied cell.  This IS the IPA
     chart — which regions are populated, which empty, where domains
     converge.
  2. Random Walk: start from seed objects, walk toward the most
     different-domain neighbor.  Tracks trajectories through
     strategy-group space.
  3. Genetic Algorithm: evolve binary masks over 145 dimensions
     to discover which dimension subsets reveal the tightest
     cross-domain structure.  The p-adic <-> symmetry correlation
     at r=0.339 is the calibration target.

Machine: M1 (Skullport)
GPU: RTX 5060 Ti, 17GB VRAM
"""
import sys
import json
import time
import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "cartography/convergence/data"
OUT_DIR = DATA_DIR / "explorer_results"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Strategy groups — mirrored from dissection_tensor.py
STRATEGY_GROUPS = {
    "complex":   ["s1_alex", "s1_jones", "s1_ap"],
    "mod_p":     ["s3_alex", "s3_jones", "s3_ap"],
    "spectral":  ["s5_alex", "s5_jones", "s5_ap", "s5_oeis"],
    "padic":     ["s7_det", "s7_disc", "s7_cond"],
    "symmetry":  ["s9_st"],
    "galois":    ["s10"],
    "zeta":      ["s12_ec", "s12_oeis", "s12_nf"],
    "disc_cond": ["s13"],
    "operadic":  ["s22"],
    "entropy":   ["s24_alex", "s24_arith", "s24_ap", "s24_sym", "s24_oeis"],
    "attractor": ["s6_oeis"],
}
GROUP_NAMES = list(STRATEGY_GROUPS.keys())
N_GROUPS = len(GROUP_NAMES)


# ============================================================
# Data loading
# ============================================================
def load_tensor():
    """Load the pre-built dissection tensor from disk."""
    path = DATA_DIR / "dissection_tensor.pt"
    print(f"Loading tensor from {path}...")
    checkpoint = torch.load(path, weights_only=False, map_location='cpu')

    tensor = checkpoint["tensor"].to(DEVICE)
    mask = checkpoint["mask"].to(DEVICE)
    labels = checkpoint["labels"]
    domains = checkpoint["domains"]
    strategy_slices = checkpoint["strategy_slices"]

    # Rebuild group_slices from strategy_slices
    group_slices = {}
    for group_name, strat_list in STRATEGY_GROUPS.items():
        starts = [strategy_slices[s][0] for s in strat_list if s in strategy_slices]
        ends = [strategy_slices[s][1] for s in strat_list if s in strategy_slices]
        if starts:
            group_slices[group_name] = (min(starts), max(ends))

    # Domain indices
    domain_indices = defaultdict(list)
    for i, d in enumerate(domains):
        domain_indices[d].append(i)

    N, D = tensor.shape
    fill = mask.float().mean().item() * 100
    print(f"  Shape: {N} x {D}, device: {tensor.device}, fill: {fill:.1f}%")
    print(f"  Domains: {dict(Counter(domains))}")

    return {
        "tensor": tensor,
        "mask": mask,
        "labels": labels,
        "domains": domains,
        "strategy_slices": strategy_slices,
        "group_slices": group_slices,
        "domain_indices": domain_indices,
    }


def compute_group_means(tensor, mask, group_slices):
    """Compute per-object mean value in each strategy group.

    Returns:
        group_vals: [N, G] mean value per group (0 where no data)
        group_valid: [N, G] bool — True if object has data in group
    """
    N = tensor.shape[0]
    group_vals = torch.zeros(N, N_GROUPS, device=DEVICE)
    group_valid = torch.zeros(N, N_GROUPS, device=DEVICE, dtype=torch.bool)

    for gi, gname in enumerate(GROUP_NAMES):
        if gname not in group_slices:
            continue
        start, end = group_slices[gname]
        g_data = tensor[:, start:end]
        g_mask = mask[:, start:end].float()
        has = g_mask.sum(dim=1) > 0
        denom = g_mask.sum(dim=1).clamp(min=1)
        group_vals[:, gi] = (g_data * g_mask).sum(dim=1) / denom
        group_valid[:, gi] = has

    return group_vals, group_valid


def masked_pairwise_distances(t_a, m_a, t_b, m_b, batch_size=1000):
    """Compute pairwise distances between two sets, respecting masks.

    Only compares dimensions where both objects have data.
    Returns: [Na, Nb] distance matrix on GPU.
    Processes in batches to avoid OOM.
    """
    Na, D = t_a.shape
    Nb = t_b.shape[0]

    # If small enough, do it in one shot
    mem_est = Na * Nb * D * 4  # bytes for the broadcast
    if mem_est < 2e9:  # 2 GB threshold
        diff = t_a.unsqueeze(1) - t_b.unsqueeze(0)  # [Na, Nb, D]
        shared = (m_a.unsqueeze(1) & m_b.unsqueeze(0)).float()
        sq = (diff ** 2) * shared
        n_shared = shared.sum(dim=2).clamp(min=1)
        dists = (sq.sum(dim=2) / n_shared).sqrt()
        dists[n_shared < 3] = float('inf')
        return dists

    # Batched fallback
    dists = torch.full((Na, Nb), float('inf'), device=DEVICE)
    for i0 in range(0, Na, batch_size):
        i1 = min(i0 + batch_size, Na)
        chunk = t_a[i0:i1]
        chunk_m = m_a[i0:i1]
        diff = chunk.unsqueeze(1) - t_b.unsqueeze(0)
        shared = (chunk_m.unsqueeze(1) & m_b.unsqueeze(0)).float()
        sq = (diff ** 2) * shared
        n_shared = shared.sum(dim=2).clamp(min=1)
        d = (sq.sum(dim=2) / n_shared).sqrt()
        d[n_shared < 3] = float('inf')
        dists[i0:i1] = d
        del diff, shared, sq, d
        torch.cuda.empty_cache()

    return dists


def cross_domain_nn_distance(idx, tensor, mask, domains, domain_indices,
                             sample_per_domain=1000, dim_mask=None):
    """For each index in idx, find nearest neighbor from a DIFFERENT domain.

    Args:
        idx: tensor of object indices to query
        dim_mask: optional [D] bool mask to restrict which dimensions to use

    Returns:
        nn_dist: [len(idx)] distance to nearest cross-domain neighbor
        nn_idx: [len(idx)] index of that neighbor
        nn_domain: list of neighbor domain strings
    """
    all_domains = list(domain_indices.keys())
    query_tensor = tensor[idx]
    query_mask = mask[idx]
    query_domains = [domains[i] for i in idx.cpu().tolist()]
    N_q = len(idx)

    if dim_mask is not None:
        query_tensor = query_tensor[:, dim_mask]
        query_mask = query_mask[:, dim_mask]

    nn_dist = torch.full((N_q,), float('inf'), device=DEVICE)
    nn_idx = torch.zeros(N_q, device=DEVICE, dtype=torch.long)

    for dom in all_domains:
        dom_idx_list = domain_indices[dom]
        # Sample for speed
        if len(dom_idx_list) > sample_per_domain:
            sampled = np.random.choice(dom_idx_list, sample_per_domain, replace=False)
        else:
            sampled = dom_idx_list
        dom_idx_t = torch.tensor(sampled, device=DEVICE, dtype=torch.long)
        t_dom = tensor[dom_idx_t]
        m_dom = mask[dom_idx_t]

        if dim_mask is not None:
            t_dom = t_dom[:, dim_mask]
            m_dom = m_dom[:, dim_mask]

        # Batch distance computation
        dists = masked_pairwise_distances(query_tensor, query_mask, t_dom, m_dom)

        # Mask out same-domain pairs
        for qi in range(N_q):
            if query_domains[qi] == dom:
                dists[qi, :] = float('inf')

        # Update nearest
        min_d, min_j = dists.min(dim=1)
        improved = min_d < nn_dist
        nn_dist[improved] = min_d[improved]
        nn_idx[improved] = dom_idx_t[min_j[improved]]

        del dists, t_dom, m_dom
        torch.cuda.empty_cache()

    nn_domain = [domains[i] for i in nn_idx.cpu().tolist()]
    return nn_dist, nn_idx, nn_domain


# ============================================================
# Explorer 1: MAP-Elites
# ============================================================
def run_map_elites(data, n_bins=3, sample_per_domain=1000):
    """MAP-Elites landscape mapper.

    Discretizes each strategy group into n_bins bins based on the
    object's mean value in that group.  For each occupied cell,
    records the champion object (lowest cross-domain distance).

    With 3 bins per group and 11 groups, the theoretical grid is
    3^11 = 177K cells, but sparsity means <1% are occupied.

    Returns: archive dict keyed by cell tuple.
    """
    print("\n" + "=" * 60)
    print("Explorer 1: MAP-Elites Landscape Mapper")
    print("=" * 60)
    t0 = time.time()

    tensor = data["tensor"]
    mask_t = data["mask"]
    domains = data["domains"]
    domain_indices = data["domain_indices"]
    labels = data["labels"]
    group_slices = data["group_slices"]
    N = tensor.shape[0]

    # Step 1: compute group-level summary per object
    print(f"  Computing group means for {N} objects...")
    group_vals, group_valid = compute_group_means(tensor, mask_t, group_slices)

    # Step 2: discretize into bins
    # Use quantile-based binning per group (only over objects with data)
    bin_edges = {}
    obj_bins = torch.zeros(N, N_GROUPS, device=DEVICE, dtype=torch.long)

    for gi, gname in enumerate(GROUP_NAMES):
        valid = group_valid[:, gi]
        vals = group_vals[valid, gi]
        if vals.numel() < 10:
            bin_edges[gname] = None
            continue
        # Quantile-based edges
        quantiles = torch.linspace(0, 1, n_bins + 1, device=DEVICE)
        edges = torch.quantile(vals, quantiles)
        bin_edges[gname] = edges
        # Assign bins (objects without data get bin 0 = "absent" sentinel)
        bins = torch.bucketize(group_vals[:, gi], edges[1:-1])
        obj_bins[:, gi] = bins
        # Mark absent objects with a special bin value
        obj_bins[~valid, gi] = n_bins  # "absent" bin

    # Step 3: compute cross-domain distance for all objects
    print(f"  Computing cross-domain nearest neighbor distances...")
    all_idx = torch.arange(N, device=DEVICE)

    # Process in chunks to keep memory bounded
    chunk_size = 5000
    nn_dist_all = torch.full((N,), float('inf'), device=DEVICE)
    nn_idx_all = torch.zeros(N, device=DEVICE, dtype=torch.long)
    nn_domain_all = [""] * N

    for c0 in range(0, N, chunk_size):
        c1 = min(c0 + chunk_size, N)
        chunk_idx = all_idx[c0:c1]
        dist, nn_i, nn_d = cross_domain_nn_distance(
            chunk_idx, tensor, mask_t, domains, domain_indices,
            sample_per_domain=sample_per_domain)
        nn_dist_all[c0:c1] = dist
        nn_idx_all[c0:c1] = nn_i
        for qi, d_str in enumerate(nn_d):
            nn_domain_all[c0 + qi] = d_str
        pct = c1 / N * 100
        print(f"    {c1}/{N} ({pct:.0f}%) — median dist so far: "
              f"{nn_dist_all[c0:c1][nn_dist_all[c0:c1] < float('inf')].median().item():.3f}")

    # Step 4: build archive
    print(f"  Building MAP-Elites archive...")
    archive = {}
    obj_bins_cpu = obj_bins.cpu().numpy()
    nn_dist_cpu = nn_dist_all.cpu().numpy()

    for i in range(N):
        cell = tuple(obj_bins_cpu[i].tolist())
        dist = nn_dist_cpu[i]
        if np.isinf(dist):
            continue
        if cell not in archive or dist < archive[cell]["quality"]:
            archive[cell] = {
                "champion": labels[i],
                "quality": float(dist),
                "domain": domains[i],
                "nn_domain": nn_domain_all[i],
                "group_profile": {
                    GROUP_NAMES[g]: int(obj_bins_cpu[i, g])
                    for g in range(N_GROUPS)
                },
            }

    # Step 5: analyze the archive
    n_cells = len(archive)
    domain_counts = Counter(v["domain"] for v in archive.values())
    cross_pairs = Counter(
        tuple(sorted([v["domain"], v["nn_domain"]]))
        for v in archive.values()
    )
    best_entries = sorted(archive.values(), key=lambda x: x["quality"])[:20]

    # Which strategy groups are most represented in high-quality cells?
    top_100 = sorted(archive.values(), key=lambda x: x["quality"])[:100]
    group_representation = Counter()
    for entry in top_100:
        for gname, bin_val in entry["group_profile"].items():
            if bin_val < n_bins:  # not absent
                group_representation[gname] += 1

    elapsed = time.time() - t0
    print(f"\n  MAP-Elites complete in {elapsed:.1f}s")
    print(f"  Occupied cells: {n_cells} / {(n_bins + 1) ** N_GROUPS} theoretical")
    print(f"  Domain distribution in archive: {dict(domain_counts)}")
    print(f"  Top cross-domain pairs:")
    for pair, count in cross_pairs.most_common(10):
        print(f"    {pair[0]} <-> {pair[1]}: {count} cells")
    print(f"  Strategy groups in top-100 cells:")
    for gname, count in group_representation.most_common():
        print(f"    {gname}: {count}/100")
    print(f"  Top-10 champion objects (lowest cross-domain distance):")
    for entry in best_entries[:10]:
        print(f"    {entry['champion']:30s} [{entry['domain']:>6s}]"
              f" -> [{entry['nn_domain']:>6s}]  d={entry['quality']:.4f}")

    # Serialize archive: convert tuple keys to strings
    archive_json = {}
    for cell, entry in archive.items():
        key = "_".join(str(b) for b in cell)
        archive_json[key] = entry

    return archive_json, best_entries


# ============================================================
# Explorer 2: Random Walk
# ============================================================
def run_random_walk(data, n_walkers=6, n_steps=200, k_neighbors=20,
                    sample_per_domain=1000):
    """Random walk explorer: start from seeds, walk toward
    the most different-domain neighbor.

    One walker per domain.  At each step:
      1. Find K nearest neighbors across ALL domains
      2. Step toward the one from the most different domain
         (prefer domains not yet visited by this walker)
      3. Record trajectory through strategy-group space

    Returns: list of trajectory dicts.
    """
    print("\n" + "=" * 60)
    print("Explorer 2: Random Walk Explorer")
    print("=" * 60)
    t0 = time.time()

    tensor = data["tensor"]
    mask_t = data["mask"]
    domains = data["domains"]
    domain_indices = data["domain_indices"]
    labels = data["labels"]
    group_slices = data["group_slices"]
    N, D = tensor.shape
    all_domains = list(domain_indices.keys())

    # Initialize walkers — one seed per domain
    walkers = []
    for dom in all_domains[:n_walkers]:
        seed = np.random.choice(domain_indices[dom])
        walkers.append({
            "seed_domain": dom,
            "current_idx": seed,
            "trajectory": [],
            "visited_domains": Counter(),
        })

    # Precompute group means
    group_vals, group_valid = compute_group_means(tensor, mask_t, group_slices)

    # Build a sampled reference set for neighbor search
    ref_indices = []
    for dom in all_domains:
        idx_list = domain_indices[dom]
        if len(idx_list) > sample_per_domain:
            ref_indices.extend(np.random.choice(idx_list, sample_per_domain,
                                                replace=False).tolist())
        else:
            ref_indices.extend(idx_list)
    ref_idx_t = torch.tensor(ref_indices, device=DEVICE, dtype=torch.long)
    ref_tensor = tensor[ref_idx_t]
    ref_mask = mask_t[ref_idx_t]
    ref_domains = [domains[i] for i in ref_indices]

    print(f"  Reference set: {len(ref_indices)} objects")
    print(f"  Walkers: {n_walkers}, steps: {n_steps}")

    for step in range(n_steps):
        # Gather current positions
        walker_idx = torch.tensor(
            [w["current_idx"] for w in walkers], device=DEVICE, dtype=torch.long)
        walker_t = tensor[walker_idx]
        walker_m = mask_t[walker_idx]

        # Distance from each walker to reference set
        dists = masked_pairwise_distances(walker_t, walker_m,
                                          ref_tensor, ref_mask, batch_size=500)

        for wi, w in enumerate(walkers):
            curr_dom = domains[w["current_idx"]]
            d_row = dists[wi]

            # Find K nearest
            k = min(k_neighbors, d_row.numel())
            vals, top_j = torch.topk(d_row, k, largest=False)

            # Score neighbors: prefer different domain, penalize already-visited
            best_score = -float('inf')
            best_ref = None
            for ki in range(k):
                j = top_j[ki].item()
                nd = ref_domains[j]
                dist_val = vals[ki].item()
                if np.isinf(dist_val):
                    continue
                # Novelty = 1 if different domain, higher if rarely visited
                dom_novel = 0.0 if nd == curr_dom else 1.0
                visit_penalty = w["visited_domains"].get(nd, 0) / max(step + 1, 1)
                score = dom_novel - visit_penalty - 0.1 * dist_val
                if score > best_score:
                    best_score = score
                    best_ref = ref_indices[j]

            if best_ref is None:
                best_ref = w["current_idx"]  # stay put

            # Record step
            gv = group_vals[w["current_idx"]].cpu().numpy()
            gm = group_valid[w["current_idx"]].cpu().numpy()
            step_record = {
                "step": step,
                "obj": labels[w["current_idx"]],
                "domain": domains[w["current_idx"]],
                "group_profile": {
                    GROUP_NAMES[g]: float(gv[g]) if gm[g] else None
                    for g in range(N_GROUPS)
                },
                "nn_dist": float(vals[0].item()) if vals.numel() > 0 else None,
            }
            w["trajectory"].append(step_record)
            w["visited_domains"][domains[best_ref]] += 1
            w["current_idx"] = best_ref

        if (step + 1) % 50 == 0:
            print(f"    Step {step + 1}/{n_steps}")

    # Analyze trajectories
    print(f"\n  Walk analysis:")
    results = []
    for w in walkers:
        traj = w["trajectory"]
        dom_sequence = [s["domain"] for s in traj]
        domain_switches = sum(1 for i in range(1, len(dom_sequence))
                              if dom_sequence[i] != dom_sequence[i - 1])
        domains_visited = len(set(dom_sequence))
        dists = [s["nn_dist"] for s in traj if s["nn_dist"] is not None
                 and not np.isinf(s["nn_dist"])]
        mean_dist = np.mean(dists) if dists else float('inf')

        # Gradient: which groups change most along the walk?
        group_deltas = {g: [] for g in GROUP_NAMES}
        for i in range(1, len(traj)):
            for g in GROUP_NAMES:
                v0 = traj[i - 1]["group_profile"].get(g)
                v1 = traj[i]["group_profile"].get(g)
                if v0 is not None and v1 is not None:
                    group_deltas[g].append(abs(v1 - v0))
        gradient = {g: float(np.mean(ds)) if ds else 0.0
                    for g, ds in group_deltas.items()}
        fastest_changing = sorted(gradient.items(), key=lambda x: x[1],
                                  reverse=True)[:3]

        print(f"  Walker from {w['seed_domain']}:")
        print(f"    Domain switches: {domain_switches}/{n_steps}")
        print(f"    Domains visited: {domains_visited}")
        print(f"    Mean NN distance: {mean_dist:.4f}")
        print(f"    Fastest-changing groups: "
              + ", ".join(f"{g}={v:.4f}" for g, v in fastest_changing))

        results.append({
            "seed_domain": w["seed_domain"],
            "trajectory": traj,
            "domain_switches": domain_switches,
            "domains_visited": domains_visited,
            "mean_nn_dist": float(mean_dist) if not np.isinf(mean_dist) else None,
            "gradient": gradient,
        })

    elapsed = time.time() - t0
    print(f"\n  Random walk complete in {elapsed:.1f}s")

    return results


# ============================================================
# Explorer 3: Genetic Algorithm
# ============================================================
def run_genetic_algorithm(data, pop_size=100, n_generations=50,
                          mutation_rate=0.05, tournament_k=3,
                          sample_k=1000, top_pairs=500):
    """Genetic algorithm to discover which dimension subsets
    reveal the tightest cross-domain structure.

    Genome: binary mask over D=145 dimensions.
    Fitness: mean distance for the closest cross-domain pairs
             under that dimension subset.  Lower = better.

    The p-adic <-> symmetry correlation at r=0.339 is our
    calibration target.

    Returns: best genome, fitness curve, top genomes.
    """
    print("\n" + "=" * 60)
    print("Explorer 3: Genetic Algorithm Dimension Selector")
    print("=" * 60)
    t0 = time.time()

    tensor = data["tensor"]
    mask_t = data["mask"]
    domains = data["domains"]
    domain_indices = data["domain_indices"]
    labels = data["labels"]
    strategy_slices = data["strategy_slices"]
    group_slices = data["group_slices"]
    N, D = tensor.shape
    all_domains = list(domain_indices.keys())

    # Pre-sample reference objects for fitness evaluation
    # One sample set per domain, fixed for the entire run
    domain_samples = {}
    for dom in all_domains:
        idx_list = domain_indices[dom]
        if len(idx_list) > sample_k:
            sampled = np.random.choice(idx_list, sample_k, replace=False)
        else:
            sampled = np.array(idx_list)
        domain_samples[dom] = torch.tensor(sampled, device=DEVICE, dtype=torch.long)

    def evaluate_fitness(genome_batch):
        """Evaluate fitness for a batch of genomes.

        genome_batch: [pop_size, D] bool tensor on GPU
        Returns: [pop_size] fitness values (lower = better)
        """
        fitness = torch.zeros(genome_batch.shape[0], device=DEVICE)

        for gi in range(genome_batch.shape[0]):
            dim_mask = genome_batch[gi]
            n_active = dim_mask.sum().item()
            if n_active < 5:
                fitness[gi] = float('inf')
                continue

            # Compute cross-domain distances under this mask
            # Sample pairs from different domains
            total_dist = 0.0
            n_pairs = 0

            # Pick 3 random domain pairs for speed
            if len(all_domains) > 2:
                pair_indices = np.random.choice(
                    len(all_domains), size=(min(6, len(all_domains)), 2),
                    replace=True)
                pairs = [(all_domains[a], all_domains[b])
                         for a, b in pair_indices if a != b]
                # Deduplicate
                pairs = list(set(tuple(sorted(p)) for p in pairs))[:4]
            else:
                pairs = [(all_domains[0], all_domains[1])]

            for da, db in pairs:
                idx_a = domain_samples[da][:200]
                idx_b = domain_samples[db][:200]
                t_a = tensor[idx_a][:, dim_mask]
                m_a = mask_t[idx_a][:, dim_mask]
                t_b = tensor[idx_b][:, dim_mask]
                m_b = mask_t[idx_b][:, dim_mask]

                dists = masked_pairwise_distances(t_a, m_a, t_b, m_b)

                # Take top_pairs closest
                flat = dists.flatten()
                k = min(top_pairs, flat.numel())
                vals, _ = torch.topk(flat, k, largest=False)
                valid = vals[vals < float('inf')]
                if valid.numel() > 0:
                    total_dist += valid.mean().item()
                    n_pairs += 1

                del dists, t_a, m_a, t_b, m_b
                torch.cuda.empty_cache()

            fitness[gi] = total_dist / max(n_pairs, 1) if n_pairs > 0 else float('inf')

        return fitness

    # Initialize population: random binary masks, biased toward ~30% active
    print(f"  Initializing population of {pop_size} genomes ({D} dimensions)...")
    population = (torch.rand(pop_size, D, device=DEVICE) < 0.3).bool()

    # Also seed some structured genomes: one per strategy group
    for gi, gname in enumerate(GROUP_NAMES):
        if gi >= pop_size:
            break
        population[gi] = False
        if gname in group_slices:
            start, end = group_slices[gname]
            population[gi, start:end] = True

    # Seed a combined padic + symmetry genome (calibration target)
    if "padic" in group_slices and "symmetry" in group_slices:
        cal_genome = torch.zeros(D, device=DEVICE, dtype=torch.bool)
        s, e = group_slices["padic"]
        cal_genome[s:e] = True
        s, e = group_slices["symmetry"]
        cal_genome[s:e] = True
        population[N_GROUPS] = cal_genome

    fitness_curve = []
    best_ever_fitness = float('inf')
    best_ever_genome = None

    print(f"  Running {n_generations} generations...")
    for gen in range(n_generations):
        # Evaluate
        fitness = evaluate_fitness(population)

        # Track best
        gen_best_idx = fitness.argmin().item()
        gen_best_fit = fitness[gen_best_idx].item()
        gen_mean_fit = fitness[fitness < float('inf')].mean().item() if \
            (fitness < float('inf')).any() else float('inf')

        if gen_best_fit < best_ever_fitness:
            best_ever_fitness = gen_best_fit
            best_ever_genome = population[gen_best_idx].clone()

        fitness_curve.append({
            "generation": gen,
            "best_fitness": gen_best_fit,
            "mean_fitness": gen_mean_fit,
            "best_n_dims": int(population[gen_best_idx].sum().item()),
        })

        if (gen + 1) % 10 == 0 or gen == 0:
            print(f"    Gen {gen + 1}/{n_generations}: "
                  f"best={gen_best_fit:.4f}, mean={gen_mean_fit:.4f}, "
                  f"dims={int(population[gen_best_idx].sum().item())}")

        # Selection + crossover + mutation for next generation
        new_pop = torch.zeros_like(population)
        # Elitism: keep top 5
        elite_k = 5
        _, elite_idx = torch.topk(fitness, elite_k, largest=False)
        new_pop[:elite_k] = population[elite_idx]

        for ci in range(elite_k, pop_size):
            # Tournament selection (2 parents)
            parents = []
            for _ in range(2):
                candidates = torch.randint(0, pop_size, (tournament_k,), device=DEVICE)
                cand_fit = fitness[candidates]
                winner = candidates[cand_fit.argmin()].item()
                parents.append(winner)

            # Uniform crossover
            p1 = population[parents[0]]
            p2 = population[parents[1]]
            crossover_mask = torch.rand(D, device=DEVICE) < 0.5
            child = torch.where(crossover_mask, p1, p2)

            # Mutation: flip bits with probability mutation_rate
            flip = torch.rand(D, device=DEVICE) < mutation_rate
            child = child ^ flip  # XOR to flip

            new_pop[ci] = child

        population = new_pop

    # Analyze best genome
    print(f"\n  GA complete in {time.time() - t0:.1f}s")
    print(f"  Best fitness (mean cross-domain distance): {best_ever_fitness:.4f}")

    bg = best_ever_genome.cpu().numpy().astype(bool)
    n_active = bg.sum()
    print(f"  Active dimensions: {n_active}/{D}")

    # Which strategy groups are covered?
    group_coverage = {}
    for gname, strat_list in STRATEGY_GROUPS.items():
        total_dims = 0
        active_dims = 0
        for sname in strat_list:
            if sname in strategy_slices:
                s, e = strategy_slices[sname]
                total_dims += e - s
                active_dims += bg[s:e].sum()
        frac = active_dims / max(total_dims, 1)
        group_coverage[gname] = {
            "active": int(active_dims),
            "total": total_dims,
            "fraction": float(frac),
        }

    print(f"\n  Strategy group coverage in best genome:")
    sorted_groups = sorted(group_coverage.items(),
                           key=lambda x: x[1]["fraction"], reverse=True)
    for gname, cov in sorted_groups:
        bar = "#" * int(cov["fraction"] * 20)
        print(f"    {gname:12s}: {cov['active']:3d}/{cov['total']:3d} "
              f"({cov['fraction']:.0%}) {bar}")

    # Calibration check: does the padic+symmetry signal show up?
    padic_frac = group_coverage.get("padic", {}).get("fraction", 0)
    sym_frac = group_coverage.get("symmetry", {}).get("fraction", 0)
    if padic_frac > 0.3 and sym_frac > 0.3:
        print(f"\n  ** CALIBRATION HIT: p-adic ({padic_frac:.0%}) and "
              f"symmetry ({sym_frac:.0%}) both selected in best genome.")
        print(f"     This recovers the known r=0.339 coupling.")
    else:
        print(f"\n  Calibration note: p-adic ({padic_frac:.0%}), "
              f"symmetry ({sym_frac:.0%}) — "
              f"{'partial' if padic_frac > 0.1 or sym_frac > 0.1 else 'missed'} "
              f"recovery of known coupling.")

    # Check for novel combinations (high coverage, not the known ones)
    novel = [(g, c) for g, c in sorted_groups
             if c["fraction"] > 0.4 and g not in ("padic", "symmetry")]
    if novel:
        print(f"\n  ** NOVEL SIGNAL: High-coverage groups beyond calibration target:")
        for gname, cov in novel:
            print(f"     {gname}: {cov['fraction']:.0%}")
        print(f"     If these don't reduce to known math, this is a discovery.")

    # Build result
    result = {
        "best_fitness": best_ever_fitness,
        "best_genome": bg.tolist(),
        "n_active_dims": int(n_active),
        "group_coverage": group_coverage,
        "fitness_curve": fitness_curve,
        "calibration": {
            "padic_fraction": padic_frac,
            "symmetry_fraction": sym_frac,
            "recovered": bool(padic_frac > 0.3 and sym_frac > 0.3),
        },
    }

    # Also extract top 5 genomes from final generation
    final_fitness = evaluate_fitness(population)
    _, top5_idx = torch.topk(final_fitness, min(5, pop_size), largest=False)
    top_genomes = []
    for ti in top5_idx:
        g = population[ti].cpu().numpy().astype(bool)
        gcov = {}
        for gname, strat_list in STRATEGY_GROUPS.items():
            active = 0
            total = 0
            for sname in strat_list:
                if sname in strategy_slices:
                    s, e = strategy_slices[sname]
                    total += e - s
                    active += g[s:e].sum()
            gcov[gname] = float(active / max(total, 1))
        top_genomes.append({
            "fitness": float(final_fitness[ti].item()),
            "n_dims": int(g.sum()),
            "group_coverage": gcov,
        })
    result["top_genomes"] = top_genomes

    return result


# ============================================================
# Main
# ============================================================
def main():
    """Run all three explorers and save results."""
    print("=" * 60)
    print("TENSOR EXPLORER — MAP-Elites + Random Walk + GA")
    print(f"Device: {DEVICE}")
    print("=" * 60)

    # Load data
    data = load_tensor()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Explorer 1: MAP-Elites
    archive, best_entries = run_map_elites(data, n_bins=3,
                                           sample_per_domain=1000)
    with open(OUT_DIR / "map_elites_archive.json", "w") as f:
        json.dump(archive, f, indent=2, default=str)
    print(f"\n  Saved MAP-Elites archive: {len(archive)} cells")

    # Explorer 2: Random Walk
    trajectories = run_random_walk(data, n_walkers=6, n_steps=200,
                                    k_neighbors=20, sample_per_domain=1000)
    with open(OUT_DIR / "random_walk_trajectories.json", "w") as f:
        json.dump(trajectories, f, indent=2, default=str)
    print(f"  Saved random walk trajectories: {len(trajectories)} walkers")

    # Explorer 3: Genetic Algorithm
    ga_result = run_genetic_algorithm(data, pop_size=100, n_generations=50,
                                      mutation_rate=0.05, tournament_k=3,
                                      sample_k=1000)
    with open(OUT_DIR / "ga_dimension_selector.json", "w") as f:
        json.dump(ga_result, f, indent=2, default=str)
    print(f"  Saved GA results: best fitness={ga_result['best_fitness']:.4f}")

    # Summary
    print("\n" + "=" * 60)
    print("EXPLORATION SUMMARY")
    print("=" * 60)
    print(f"\n  MAP-Elites: {len(archive)} occupied cells")
    if best_entries:
        top = best_entries[0]
        print(f"    Best: {top['champion']} [{top['domain']}] "
              f"-> [{top['nn_domain']}] d={top['quality']:.4f}")
    print(f"\n  Random Walk: {len(trajectories)} walkers x 200 steps")
    for t in trajectories:
        print(f"    {t['seed_domain']:>8s}: {t['domain_switches']} switches, "
              f"{t['domains_visited']} domains, "
              f"mean_d={t['mean_nn_dist']:.4f}" if t['mean_nn_dist'] else "")
    print(f"\n  Genetic Algorithm:")
    print(f"    Best fitness: {ga_result['best_fitness']:.4f}")
    print(f"    Active dims: {ga_result['n_active_dims']}/{data['tensor'].shape[1]}")
    cal = ga_result["calibration"]
    print(f"    p-adic/symmetry calibration: "
          f"{'RECOVERED' if cal['recovered'] else 'not recovered'}")

    print(f"\n  Results saved to: {OUT_DIR}")
    return archive, trajectories, ga_result


if __name__ == "__main__":
    main()
