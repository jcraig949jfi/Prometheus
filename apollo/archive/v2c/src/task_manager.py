"""
task_manager.py — Rolling curriculum for Apollo v2.

Fixed reference set (50 tasks) — never changes, used for behavioral signatures.
Evolution set (100 tasks) — rotates 10 tasks every 50 generations.
Held-out set (50 tasks) — generalization testing, refreshed every 500 generations.
Capability step test — novel task type every 500 generations.
"""

import importlib.util
from pathlib import Path

from logger import log_info, log_debug


def _load_trap_generator(trap_gen_path: str):
    spec = importlib.util.spec_from_file_location("trap_generator", trap_gen_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TaskManager:
    def __init__(self, trap_gen_path: str,
                 reference_seed: int = 42,
                 evolution_seed: int = 100,
                 held_out_seed: int = 200,
                 n_reference: int = 50,
                 n_evolution: int = 100,
                 n_held_out: int = 50,
                 rotation_count: int = 10,
                 rotation_interval: int = 50,
                 held_out_refresh_interval: int = 500):
        self.trap_gen = _load_trap_generator(trap_gen_path)
        self.reference_seed = reference_seed
        self.evolution_seed = evolution_seed
        self.held_out_seed = held_out_seed
        self.n_reference = n_reference
        self.n_evolution = n_evolution
        self.n_held_out = n_held_out
        self.rotation_count = rotation_count
        self.rotation_interval = rotation_interval
        self.held_out_refresh_interval = held_out_refresh_interval

        # Fixed reference set — never changes
        all_ref = self.trap_gen.generate_trap_battery(n_per_category=5, seed=reference_seed)
        self.reference_tasks = all_ref[:n_reference]

        # Evolution set — seed portion + rotating portion
        all_evo = self.trap_gen.generate_trap_battery(n_per_category=10, seed=evolution_seed)
        self._evo_fixed = all_evo[:n_evolution - rotation_count]
        self._rotation_seed = evolution_seed + 1000
        self._evo_rotating = self._generate_rotating(self._rotation_seed)

        # Held-out set
        self._held_out_seed = held_out_seed
        all_ho = self.trap_gen.generate_trap_battery(n_per_category=5, seed=held_out_seed)
        self.held_out_tasks = all_ho[:n_held_out]

        # Capability step test tasks (harder)
        self._cap_step_seed = 9999

        log_info(
            f"TaskManager ready: ref={len(self.reference_tasks)}, "
            f"evo={len(self.get_evolution_tasks())}, held_out={len(self.held_out_tasks)}",
            stage="bootstrap",
        )

    def _generate_rotating(self, seed: int) -> list:
        traps = self.trap_gen.generate_trap_battery(n_per_category=2, seed=seed)
        return traps[:self.rotation_count]

    def get_evolution_tasks(self) -> list:
        return self._evo_fixed + self._evo_rotating

    def get_reference_tasks(self) -> list:
        return self.reference_tasks

    def get_held_out_tasks(self) -> list:
        return self.held_out_tasks

    def maybe_rotate(self, generation: int) -> bool:
        """Rotate evolution tasks every rotation_interval generations."""
        if generation > 0 and generation % self.rotation_interval == 0:
            self._rotation_seed = self.evolution_seed + 1000 + generation
            self._evo_rotating = self._generate_rotating(self._rotation_seed)
            log_info(
                f"Rotated {self.rotation_count} evolution tasks (seed={self._rotation_seed})",
                stage="main", generation=generation,
            )
            return True
        return False

    def maybe_refresh_held_out(self, generation: int) -> bool:
        """Refresh held-out tasks every held_out_refresh_interval generations."""
        if generation > 0 and generation % self.held_out_refresh_interval == 0:
            self._held_out_seed += 1
            all_ho = self.trap_gen.generate_trap_battery(
                n_per_category=5, seed=self._held_out_seed
            )
            self.held_out_tasks = all_ho[:self.n_held_out]
            log_info(
                f"Refreshed held-out tasks (seed={self._held_out_seed})",
                stage="evaluation", generation=generation,
            )
            return True
        return False

    def capability_step_test(self, generation: int) -> list:
        """Generate harder tasks for capability step test (every 500 gens)."""
        self._cap_step_seed += generation
        try:
            tier2_path = str(Path(self.trap_gen.__file__).parent / "trap_generator_tier2.py")
            if Path(tier2_path).exists():
                tier2 = _load_trap_generator(tier2_path)
                tasks = tier2.generate_trap_battery(n_per_category=2, seed=self._cap_step_seed)
                return tasks[:20]
        except Exception:
            pass
        tasks = self.trap_gen.generate_trap_battery(n_per_category=2, seed=self._cap_step_seed)
        return tasks[:20]
