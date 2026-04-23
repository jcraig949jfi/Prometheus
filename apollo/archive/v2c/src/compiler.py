"""
compiler.py — Compile Organism DAGs into executable ReasoningTool source code.

The compiler generates Python source that:
1. Imports the needed Frame H primitives
2. Builds a _execute_dag() that runs primitives in topological order
3. Embeds the organism's router_logic as _route()
4. Wraps everything in evaluate() / confidence() interface
"""

import ast
import textwrap
from dataclasses import dataclass

from genome import Organism, ALL_PRIMITIVES, get_primitive_signature


@dataclass
class CompilationResult:
    success: bool
    source_code: str = ""
    error: str = ""


def compile_organism(organism: Organism) -> CompilationResult:
    """Compile an Organism into executable ReasoningTool Python source."""

    # ── Validate ──────────────────────────────────────────────
    if not organism.primitive_sequence:
        return CompilationResult(False, error="Empty primitive sequence")

    for pc in organism.primitive_sequence:
        if pc.primitive_name not in ALL_PRIMITIVES:
            return CompilationResult(False, error=f"Unknown primitive: {pc.primitive_name}")

    # Validate router_logic is parseable Python
    router_body = organism.router_logic.strip()
    if not router_body:
        return CompilationResult(False, error="Empty router_logic")

    try:
        # Wrap in a function to check syntax
        test_code = f"def _test(prompt, candidates, outputs, params):\n"
        for line in router_body.split('\n'):
            test_code += f"    {line}\n"
        ast.parse(test_code)
    except SyntaxError as e:
        return CompilationResult(False, error=f"Router syntax error: {e}")

    # Check for DAG cycles
    topo = organism.topological_order()
    if not topo:
        return CompilationResult(False, error="DAG has cycles")

    # ── Generate source ───────────────────────────────────────
    try:
        source = _generate_source(organism, topo)
    except Exception as e:
        return CompilationResult(False, error=f"Code generation error: {e}")

    # Final syntax check on generated source
    try:
        ast.parse(source)
    except SyntaxError as e:
        return CompilationResult(False, error=f"Generated code syntax error: {e}")

    return CompilationResult(True, source_code=source)


def _generate_source(organism: Organism, topo_order: list[str]) -> str:
    """Generate the full Python source code for a ReasoningTool."""

    # Collect unique primitive names for imports
    unique_prims = sorted(set(pc.primitive_name for pc in organism.primitive_sequence))

    # Build node lookup
    node_map = {pc.node_id: pc for pc in organism.primitive_sequence}

    # ── Import block ──────────────────────────────────────────
    imports = [
        "import re",
        "import math",
        "import numpy as np",
        f"from forge_primitives import {', '.join(unique_prims)}",
    ]

    # ── Parameters dict literal ───────────────────────────────
    params_repr = repr(organism.parameters)

    # ── _execute_dag body ─────────────────────────────────────
    dag_lines = ["        outputs = {}"]
    for node_id in topo_order:
        pc = node_map[node_id]
        sig = get_primitive_signature(pc.primitive_name)

        # Build argument resolution for each parameter
        arg_parts = []
        for param_name in sig:
            source = pc.input_mapping.get(param_name, "")
            resolved = _resolve_input(source, param_name, pc.primitive_name)
            arg_parts.append(f"{param_name}={resolved}")

        args_str = ", ".join(arg_parts)
        dag_lines.append(f"        # Node {node_id}: {pc.primitive_name}")
        dag_lines.append(f"        try:")
        dag_lines.append(f"            outputs['{node_id}'] = {pc.primitive_name}({args_str})")
        dag_lines.append(f"        except Exception:")
        dag_lines.append(f"            outputs['{node_id}'] = None")

    dag_lines.append("        return outputs")
    dag_body = "\n".join(dag_lines)

    # ── _route body ───────────────────────────────────────────
    router_body = organism.router_logic.strip()
    route_lines = []
    for line in router_body.split('\n'):
        route_lines.append(f"        {line}")
    route_body = "\n".join(route_lines)

    # ── Full source ───────────────────────────────────────────
    source = f"""\
{chr(10).join(imports)}

class ReasoningTool:
    def __init__(self):
        self.params = {params_repr}

    def _execute_dag(self, prompt, candidates):
{dag_body}

    def _route(self, prompt, candidates, outputs):
        params = self.params
{route_body}

    def evaluate(self, prompt, candidates):
        outputs = self._execute_dag(prompt, candidates)
        try:
            scores = self._route(prompt, candidates, outputs)
        except Exception:
            scores = [0.5] * len(candidates)

        if not isinstance(scores, (list, tuple)):
            scores = [0.5] * len(candidates)
        if len(scores) != len(candidates):
            scores = list(scores) + [0.5] * (len(candidates) - len(scores))
            scores = scores[:len(candidates)]

        results = []
        for cand, score in zip(candidates, scores):
            results.append({{
                'candidate': cand,
                'score': float(score) if isinstance(score, (int, float)) else 0.5,
                'reasoning': str({{k: type(v).__name__ for k, v in outputs.items()}}),
            }})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt, answer):
        outputs = self._execute_dag(prompt, [answer])
        score_vals = []
        for v in outputs.values():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                score_vals.append(float(v))
            elif isinstance(v, bool):
                score_vals.append(1.0 if v else 0.0)
        if not score_vals:
            return 0.5
        # Normalize to [0, 1] range
        vals = np.array(score_vals)
        if vals.max() == vals.min():
            return 0.5
        normed = (vals - vals.min()) / (vals.max() - vals.min())
        return float(np.mean(normed))
"""
    return source


def _resolve_input(source: str, param_name: str, primitive_name: str) -> str:
    """Convert an input_mapping source reference to Python expression."""
    if not source:
        return _default_for_param(param_name, primitive_name)

    if source == "prompt":
        return "prompt"
    if source == "candidates":
        return "candidates"

    # Node output reference: "n2.output"
    if source.startswith("n") and ".output" in source:
        node_id = source.split(".")[0]
        return f"outputs.get('{node_id}')"

    # Parameter reference: "param.bayesian_update_prior"
    if source.startswith("param."):
        param_key = source[6:]
        return f"self.params.get('{param_key}', 0.5)"

    return _default_for_param(param_name, primitive_name)


def _default_for_param(param_name: str, primitive_name: str) -> str:
    """Provide a sensible default expression for unresolved parameters."""
    # Type-based defaults for common parameter patterns
    defaults = {
        # Probability
        'prior': '0.5',
        'likelihood': '0.5',
        'false_positive': '0.1',
        'probs': '[0.5, 0.5]',
        'outcomes': '[(0.5, 1.0)]',
        'n_flips': '2',
        'target_heads': '1',
        # Logic
        'clauses': '[[1]]',
        'n_vars': '1',
        'premises': '[]',
        'facts': 'set()',
        'relations': '[]',
        'statement': 'prompt',
        # Graph
        'edges': '[]',
        'start': '""',
        'values': '{}',
        'intervene_node': '""',
        'intervene_value': '0.0',
        # Constraints
        'variables': '[]',
        'domains': '{}',
        'constraints': '[]',
        'items': '2',
        'containers': '1',
        'n_segments': '1',
        'include_both_ends': 'True',
        # Arithmetic
        'total': '0.0',
        'difference': '0.0',
        'a': '0',
        'b': '0',
        'mod': '1',
        'n': '0',
        'A': '[[1.0]]',
        # Temporal
        'events': '[]',
        'directions': '[]',
        # Belief
        'agents': '[]',
        'observations': '[]',
        'who_moved': '""',
        'who_saw_move': 'set()',
        'original_location': '""',
        'new_location': '""',
        # Meta
        'scores': '[0.5]',
        'n_unknowns': '1',
        'n_constraints': '1',
        'numbers': '[0]',
    }
    return defaults.get(param_name, '0.0')
