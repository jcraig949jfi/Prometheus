import torch
import json
import logging
import time
import math
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional

from seti_config import SETIV2Config
from tii_engine import load_tii_model, execute_tii_generation
from genome import SteeringGenome
from fitness import calculate_fitness, check_answer
from probe_runner import run_latent_probe
from alert import send_alert, print_visual_separator
from inception_protocol import prep_inception_seed

class SETIV2Orchestrator:
    def __init__(self, config_path=None):
        self.config = SETIV2Config.load(config_path)
        self.config.results_dir.mkdir(parents=True, exist_ok=True)
        self.model = load_tii_model(self.config.model_name)
        
        # MARATHON: Task Prompt for Inception Protocol
        self.task_prompt = "Is the following statement true or false: 'The number 9.11 is larger than 9.9'."
        self.naive_baseline_output = "" # Will be captured at startup
        
        # CMA-ES Parameters
        self.d_model = self.model.cfg.d_model
        self.n_layers = self.model.cfg.n_layers
        
        # MARATHON: Force Diagonal CMA-ES
        self.is_diagonal = True
        
        # State Initialization
        self.mean_vector = torch.zeros(self.d_model).cuda()
        self.C = torch.ones(self.d_model).cuda() # Variance vector (diagonal)
        self.sigma = self.config.mutation_rate # Use mutation_rate as initial sigma (0.03)
        
        self.gen_count = 0
        self.population: List[SteeringGenome] = []
        self.best_genome = None
        self.last_best_fitness = -float('inf')
        self.plateau_count = 0
        
        # Strategy Parameters (standard CMA-ES heuristics)
        self.mu = self.config.population_size // 2
        self.weights = torch.log(torch.tensor(self.mu + 0.5)) - torch.log(torch.arange(1, self.mu + 1).float())
        self.weights = self.weights / self.weights.sum()
        self.weights = self.weights.cuda()
        self.mueff = (self.weights.sum()**2 / (self.weights**2).sum()).item()
        
        # Evolution paths
        self.pc = torch.zeros(self.d_model).cuda()
        self.ps = torch.zeros(self.d_model).cuda()
        
        # Hyperparameters for update logic
        self.cc = 4.0 / (self.d_model + 4.0)
        self.cs = (self.mueff + 2.0) / (self.d_model + self.mueff + 5.0)
        self.c1 = 2.0 / ((self.d_model + 1.3)**2 + self.mueff)
        self.cmu = min(1.0 - self.c1, 2.0 * (self.mueff - 2.0 + 1.0/self.mueff) / ((self.d_model + 2.0)**2 + self.mueff))
        self.damps = 1.0 + 2.0 * max(0.0, math.sqrt((self.mueff - 1.0) / (self.d_model + 1.0)) - 1.0) + self.cs
        self.chiN = math.sqrt(self.d_model) * (1.0 - 1.0/(4.0 * self.d_model) + 1.0/(21.0 * self.d_model**2))

        self.load_state()
        if self.gen_count == 0:
            # Capture naive baseline for fitness divergence check
            print("[*] Capturing naive model baseline for task...")
            input_tokens = self.model.to_tokens(self.task_prompt)
            output_tokens = self.model.generate(input_tokens, max_new_tokens=64, verbose=False)
            self.naive_baseline_output = self.model.to_string(output_tokens[0])
            print(f"    Naive Output: {self.naive_baseline_output.strip()}")
            
            # Check for inception seed
            inception_path = self.config.results_dir / "gen_inception_seed.pt"
            if not inception_path.exists():
                prep_inception_seed(self.model, str(self.config.results_dir))
            
            self.warm_start()

    def load_state(self):
        if self.config.state_file.exists():
            try:
                state = torch.load(self.config.state_file)
                self.mean_vector = state['mean_vector'].cuda()
                self.C = state['C'].cuda()
                self.sigma = state['sigma']
                self.gen_count = state['gen_count']
                self.pc = state['pc'].cuda()
                self.ps = state['ps'].cuda()
                self.last_best_fitness = state.get('last_best_fitness', -float('inf'))
                self.plateau_count = state.get('plateau_count', 0)
                self.naive_baseline_output = state.get('naive_baseline_output', "")
                logging.info(f"Resumed from generation {self.gen_count}")
                print(f"Resumed from state: Gen {self.gen_count}, Sigma {self.sigma:.4f}")
            except Exception as e:
                logging.error(f"Failed to load state: {e}")

    def warm_start(self):
        """Initializes mean_vector from inception seed or best files."""
        inception_path = self.config.results_dir / "gen_inception_seed.pt"
        warm_path = self.config.results_dir / "gen_29_best.pt"
        archive_path = self.config.results_dir / "archives" / "vanilla_ga_baseline" / "gen_29_best.pt"
        
        # Priority: Inception Seed > gen_29 > latest best
        target_path = None
        if inception_path.exists():
            target_path = inception_path
        elif warm_path.exists():
            target_path = warm_path
        elif archive_path.exists():
            target_path = archive_path
        else:
            best_files = list(self.config.results_dir.glob("gen_*_best.pt"))
            if best_files:
                valid_files = [f for f in best_files if "_" in f.name]
                if valid_files:
                    valid_files.sort(key=lambda x: int(x.name.split('_')[1]), reverse=True)
                    target_path = valid_files[0]
        
        if target_path and target_path.exists():
            try:
                logging.info(f"Warm-starting from {target_path}")
                print(f"WARM START: Loading vector from {target_path}")
                data = torch.load(target_path)
                if 'vector' in data:
                    self.mean_vector = data['vector'].cuda()
                    # Reset last fitness to force a fresh evaluation of the seed
                    self.last_best_fitness = -float('inf') 
            except Exception as e:
                logging.warning(f"Failed to warm-start: {e}")

    def save_state(self):
        state = {
            'mean_vector': self.mean_vector.cpu(),
            'C': self.C.cpu(),
            'sigma': self.sigma,
            'gen_count': self.gen_count,
            'pc': self.pc.cpu(),
            'ps': self.ps.cpu(),
            'is_diagonal': True,
            'last_best_fitness': self.last_best_fitness,
            'plateau_count': self.plateau_count,
            'naive_baseline_output': self.naive_baseline_output
        }
        torch.save(state, self.config.state_file)
        if self.best_genome:
            checkpoint_path = self.config.results_dir / f"gen_{self.gen_count}_best.pt"
            self.best_genome.save(str(checkpoint_path))
            self.best_genome.save(str(self.config.results_dir / f"best_genome.pt"))

    def sample_population(self):
        """Samples new genomes from the current Diagonal CMA-ES distribution."""
        self.population = []
        for i in range(self.config.population_size):
            # z ~ N(0, I)
            z = torch.randn(self.d_model).cuda()
            # x = mean + sigma * diag(C)^1/2 * z
            vector = self.mean_vector + self.sigma * (self.C.sqrt() * z)
            
            # MARATHON: Layer index derived from Inception Seed (18) 
            # but allow small exploration around it
            layer = 18
            if torch.rand(1) < 0.1: # 10% chance to shift layer
                layer = max(self.config.early_layer_cutoff + 1, min(self.n_layers - 1, layer + torch.randint(-1, 2, (1,)).item()))
            
            self.population.append(SteeringGenome(layer_index=layer, vector=vector))

    def update_distribution(self, sorted_pop: List[SteeringGenome]):
        """Robust Diagonal CMA-ES distribution update."""
        old_mean = self.mean_vector.clone()
        
        # 1. Update Mean
        new_mean = torch.zeros_like(self.mean_vector)
        for i in range(self.mu):
            new_mean += self.weights[i] * sorted_pop[i].vector
        self.mean_vector = new_mean
        
        # 2. Update Evolution Paths
        invsqrtC = 1.0 / self.C.sqrt()
        y = (self.mean_vector - old_mean) / self.sigma
        
        # ps update
        self.ps = (1.0 - self.cs) * self.ps + math.sqrt(self.cs * (2.0 - self.cs) * self.mueff) * (invsqrtC * y)
        
        # pc update
        # hsig: standard CMA-ES step-size indicator
        ps_norm = self.ps.norm()
        hsig_val = ps_norm / math.sqrt(1.0 - (1.0 - self.cs)**(2 * (self.gen_count + 1))) / self.chiN
        hsig = 1.0 if hsig_val < 1.4 + 2.0 / (self.d_model + 1.0) else 0.0
        
        self.pc = (1.0 - self.cc) * self.pc + hsig * math.sqrt(self.cc * (2.0 - self.cc) * self.mueff) * y
        
        # 3. Update Step Size Sigma
        self.sigma = self.sigma * math.exp((self.cs / self.damps) * (ps_norm / self.chiN - 1.0))
        
        # 4. Update Variance Vector C (Diagonal)
        # Rank-1 update (c1) + Rank-mu update (cmu)
        self.C = (1.0 - self.c1 - self.cmu) * self.C + \
                 self.c1 * (self.pc**2 + (1.0 - hsig) * self.cc * (2.0 - self.cc) * self.C)
        
        for i in range(self.mu):
            diff = (sorted_pop[i].vector - old_mean) / self.sigma
            self.C += self.cmu * self.weights[i] * (diff**2)
            
        # Safety: clip sigma and C
        self.sigma = max(min(self.sigma, 10.0), 1e-5)
        self.C = torch.clamp(self.C, 1e-8, 1e6)

    def log_manifold_geometry(self, generation: int, elites: List[SteeringGenome]):
        """
        Analyzes the 'thickness' of the current elite population to see 
        if we are finding a line, a plane, or a high-dimensional volume.
        """
        if not elites:
            return 0.0
            
        # 1. Stack vectors [N, 1024]
        matrix = torch.stack([e.vector for e in elites])
        
        # 2. Perform SVD to find the 'Principal Directions'
        # s contains the 'singular values' (how much variance each dimension holds)
        try:
            _, s, _ = torch.svd(matrix)
            
            # 3. Calculate 'Effective Dimensionality' (Participation Ratio)
            # If this is close to 1, it's a single line. If it's high, it's a complex manifold.
            participation_ratio = (s.sum()**2) / (s**2).sum()
            
            participation_ratio = participation_ratio.item()
            logging.info(f"Gen {generation} | Manifold Dim: {participation_ratio:.2f}")
            print(f"  > Manifold Geometry: {participation_ratio:.2f} dimensions")
            return participation_ratio
        except Exception as e:
            logging.error(f"SVD failed: {e}")
            return 0.0

    def run_evolution(self):
        while self.gen_count < self.config.generations:
            print_visual_separator("-", 80, f"INCEPTION GEN {self.gen_count}")
            
            # 1. Ask
            self.sample_population()
            
            # 2. Evaluate
            for i, genome in enumerate(self.population):
                probe_data = run_latent_probe(self.model, genome, self.task_prompt)
                
                # Falsification Check
                noise_passed = not check_answer(probe_data["noise_output"])
                ortho_passed = not check_answer(probe_data["ortho_output"])
                
                if not (noise_passed and ortho_passed):
                    genome.fitness = -1.0
                else:
                    genome.fitness = calculate_fitness(
                        probe_data["output"], 
                        genome, 
                        self.n_layers,
                        naive_output=self.naive_baseline_output
                    )
                
                if i % 10 == 0:
                    best_f = self.best_genome.fitness if self.best_genome else 0.0
                    print(f"  [{i}/{len(self.population)}] Best: {best_f:.2f} | Sigma: {self.sigma:.5f}")

            # 3. Tell
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            
            # Log manifold thickness of top elites (mu)
            self.log_manifold_geometry(self.gen_count, self.population[:self.mu])
            
            current_best_f = self.population[0].fitness
            if current_best_f > self.last_best_fitness + 1e-4:
                self.last_best_fitness = current_best_f
                self.plateau_count = 0
            else:
                self.plateau_count += 1
                
            if self.best_genome is None or current_best_f > self.best_genome.fitness:
                self.best_genome = self.population[0]
                if self.best_genome.fitness > 5.0:
                    send_alert(f"INCEPTION Discovery", f"Gen {self.gen_count}: Fitness {self.best_genome.fitness:.2f}", self.config)

            # Step-Size Decay override (refined for marathon)
            if self.plateau_count >= 5:
                self.sigma *= 0.85
                self.plateau_count = 0
                print(f"  !!! Plateau Decay -> Sigma: {self.sigma:.5f}")

            self.update_distribution(self.population)
            
            self.gen_count += 1
            self.save_state()
            
            # MARATHON: VRAM Hygiene
            gc.collect()
            torch.cuda.empty_cache()

    def run(self):
        print_visual_separator("*", 80, "SETIv2 MARATHON DEPLOYMENT")
        print(f"Target: {self.config.model_name} | Generations: {self.config.generations}")
        self.run_evolution()

if __name__ == "__main__":
    # Ensure we run on cuda:0 as requested
    torch.cuda.set_device(0)
    orchestrator = SETIV2Orchestrator()
    orchestrator.run()
