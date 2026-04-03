"""Amino acid registry — central catalog of all decomposed reasoning primitives.

Each amino acid is registered via the @amino_acid decorator, which records metadata
and makes the function available for tool generation by the Builder.
"""
import inspect
from typing import Dict, Any, Optional

# Global registry: maps amino_acid_id -> metadata dict
_REGISTRY: Dict[str, Dict[str, Any]] = {}


def amino_acid(id: str, source: str, reasoning_type: str, description: str):
    """Decorator to register a function as an amino acid.
    
    Args:
        id: Unique identifier (format: "{source}_{short_name}")
        source: Library name (pgmpy, pysat, python_constraint, nashpy)
        reasoning_type: One of: logical, probabilistic, causal, temporal,
                        constraint, game_theoretic, metacognitive
        description: One-line description of what this amino acid does
    """
    valid_types = {
        "logical", "probabilistic", "causal", "temporal",
        "constraint", "game_theoretic", "metacognitive",
    }
    if reasoning_type not in valid_types:
        raise ValueError(f"Invalid reasoning_type '{reasoning_type}'. Must be one of: {valid_types}")

    def decorator(func):
        # Count lines of the function body
        source_lines = inspect.getsource(func).split('\n')
        # Exclude decorator lines and blank lines at start/end
        body_lines = [l for l in source_lines if l.strip() and not l.strip().startswith('@')]
        line_count = len(body_lines)

        sig = str(inspect.signature(func))

        _REGISTRY[id] = {
            "id": id,
            "source": source,
            "reasoning_type": reasoning_type,
            "description": description,
            "signature": f"{func.__name__}{sig}",
            "lines": line_count,
            "function": func,
            "module": func.__module__,
            "dependencies": [],  # Populated during validation
        }
        # Tag the function itself
        func._amino_acid_id = id
        func._amino_acid_meta = _REGISTRY[id]
        return func

    return decorator


def get_registry() -> Dict[str, Dict[str, Any]]:
    """Return the full amino acid registry (id -> metadata including function)."""
    return dict(_REGISTRY)


def get_amino_acid(acid_id: str):
    """Get a specific amino acid's function by ID. Returns None if not found."""
    entry = _REGISTRY.get(acid_id)
    return entry["function"] if entry else None


def get_by_type(reasoning_type: str) -> Dict[str, Dict[str, Any]]:
    """Get all amino acids of a given reasoning type."""
    return {k: v for k, v in _REGISTRY.items() if v["reasoning_type"] == reasoning_type}


def get_by_source(source: str) -> Dict[str, Dict[str, Any]]:
    """Get all amino acids from a given source library."""
    return {k: v for k, v in _REGISTRY.items() if v["source"] == source}


def summary() -> str:
    """Return a human-readable summary of the registry."""
    lines = [f"Amino Acid Registry: {len(_REGISTRY)} acids registered\n"]
    
    # By source
    sources = {}
    for entry in _REGISTRY.values():
        sources.setdefault(entry["source"], []).append(entry)
    for src, acids in sorted(sources.items()):
        lines.append(f"\n  {src} ({len(acids)} acids):")
        for a in acids:
            lines.append(f"    {a['id']:40s} [{a['reasoning_type']:15s}] {a['lines']:3d} lines — {a['description']}")
    
    # Size stats
    all_lines = [e["lines"] for e in _REGISTRY.values()]
    if all_lines:
        all_lines.sort()
        median = all_lines[len(all_lines) // 2]
        lines.append(f"\n  Size: min={min(all_lines)}, max={max(all_lines)}, median={median}")
    
    # Type distribution
    types = {}
    for entry in _REGISTRY.values():
        types[entry["reasoning_type"]] = types.get(entry["reasoning_type"], 0) + 1
    lines.append(f"  Types: {dict(sorted(types.items()))}")
    
    return "\n".join(lines)


def load_all():
    """Import all amino acid modules to populate the registry."""
    from forge.amino_acids import pgmpy_acids   # noqa: F401
    from forge.amino_acids import pysat_acids    # noqa: F401
    from forge.amino_acids import constraint_acids  # noqa: F401
    from forge.amino_acids import nashpy_acids   # noqa: F401
