"""
Base class for Mathematical Organisms.

Each organism wraps a set of mathematical operations as compiled,
executable code strings. Operations declare input/output types so
organisms can be chained together.
"""

import numpy as np
from typing import Any, Dict, List, Tuple


class MathematicalOrganism:
    """
    A living mathematical concept: holds named operations as code strings,
    compiles and executes them on demand, and exposes type metadata for
    cross-organism chaining.
    """

    name: str = "base"
    operations: Dict[str, Dict[str, str]] = {}

    # ---- cache compiled functions so we don't recompile every call ----
    _compiled_cache: dict

    def __init__(self):
        self._compiled_cache = {}

    def _compile(self, operation_name: str):
        """Compile an operation's code string into a callable."""
        if operation_name in self._compiled_cache:
            return self._compiled_cache[operation_name]

        if operation_name not in self.operations:
            raise KeyError(
                f"Operation '{operation_name}' not found in {self.name}. "
                f"Available: {list(self.operations.keys())}"
            )

        code = self.operations[operation_name]["code"]
        local_ns: dict = {"np": np}
        exec(compile(code, f"<{self.name}.{operation_name}>", "exec"), local_ns)

        # The code string must define exactly one function named `operation_name`
        if operation_name not in local_ns:
            # Try to find any callable that was defined
            callables = {
                k: v for k, v in local_ns.items()
                if callable(v) and k != "np" and not k.startswith("__")
            }
            if len(callables) == 1:
                fn = list(callables.values())[0]
            else:
                raise RuntimeError(
                    f"Code for '{operation_name}' must define a function "
                    f"named '{operation_name}'. Found: {list(callables.keys())}"
                )
        else:
            fn = local_ns[operation_name]

        self._compiled_cache[operation_name] = fn
        return fn

    def execute(self, operation_name: str, *args, **kwargs) -> Any:
        """Compile (if needed) and run the named operation.
        Caps numeric inputs to prevent explosive iteration."""
        fn = self._compile(operation_name)
        # Sanitize inputs: cap large integers that could cause explosive loops
        safe_args = []
        for a in args:
            if isinstance(a, (int, np.integer)) and a > 10000:
                safe_args.append(min(int(a), 10000))
            elif isinstance(a, float) and np.isfinite(a) and abs(a) > 10000:
                safe_args.append(min(abs(a), 10000.0))
            else:
                safe_args.append(a)
        return fn(*safe_args, **kwargs)

    def list_operations(self) -> List[Dict[str, str]]:
        """Return operation names with their input/output type metadata."""
        return [
            {
                "name": name,
                "input_type": meta["input_type"],
                "output_type": meta["output_type"],
            }
            for name, meta in self.operations.items()
        ]

    def compatible_chains(
        self, other: "MathematicalOrganism"
    ) -> List[Tuple[str, str]]:
        """
        Find (self_op, other_op) pairs where self's output_type matches
        other's input_type, enabling pipelining.
        """
        chains = []
        for s_name, s_meta in self.operations.items():
            for o_name, o_meta in other.operations.items():
                if s_meta["output_type"] == o_meta["input_type"]:
                    chains.append((s_name, o_name))
        return chains

    def __repr__(self):
        return f"<MathematicalOrganism:{self.name} ops={list(self.operations.keys())}>"
