"""
task_manager.py — Rolling curriculum: fixed seed traps + rotating generated tasks.
"""

import sys
import importlib.util
from pathlib import Path


def _load_trap_generator(trap_gen_path: str):
    spec = importlib.util.spec_from_file_location("trap_generator", trap_gen_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TaskManager:
    def __init__(self, trap_gen_path: str = "F:/Prometheus/agents/hephaestus/src/trap_generator.py",
                 evolution_seed: int = 42, held_out_seed: int = 137,
                 n_seed_traps: int = 15, n_rotating: int = 5,
                 rotation_interval: int = 50):
        self.trap_gen = _load_trap_generator(trap_gen_path)
        self.evolution_seed = evolution_seed
        self.held_out_seed = held_out_seed
        self.n_seed_traps = n_seed_traps
        self.n_rotating = n_rotating
        self.rotation_interval = rotation_interval

        # Fixed seed traps (never rotate)
        all_seed = self.trap_gen.generate_trap_battery(n_per_category=2, seed=evolution_seed)
        self.seed_traps = all_seed[:n_seed_traps]

        # Initial rotating tasks
        self._rotation_seed = evolution_seed + 1000
        self.rotating_traps = self._generate_rotating(self._rotation_seed)

        # Held-out battery (never used for selection)
        self.held_out_traps = self.trap_gen.generate_trap_battery(n_per_category=3, seed=held_out_seed)

    def _generate_rotating(self, seed: int) -> list:
        traps = self.trap_gen.generate_trap_battery(n_per_category=1, seed=seed)
        return traps[:self.n_rotating]

    def get_evolution_tasks(self) -> list:
        return self.seed_traps + self.rotating_traps

    def get_reference_tasks(self) -> list:
        return self.seed_traps

    def get_held_out_tasks(self) -> list:
        return self.held_out_traps

    def get_quick_screen_tasks(self, n: int = 3) -> list:
        return self.seed_traps[:n]

    def maybe_rotate(self, generation: int) -> bool:
        if generation > 0 and generation % self.rotation_interval == 0:
            self._rotation_seed = self.evolution_seed + 1000 + generation
            self.rotating_traps = self._generate_rotating(self._rotation_seed)
            return True
        return False
