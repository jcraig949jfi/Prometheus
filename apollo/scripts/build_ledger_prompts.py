"""build_ledger_prompts.py — generate 200 Apollo mutation prompts.

Loads organisms from a checkpoint, generates route/wiring/swap prompts
using Apollo's actual prompt templates, plus a few prompt-engineering
variants. Outputs ledger_prompts.json keyed by prompt_id.

Usage:
    python build_ledger_prompts.py <checkpoint_path> <out_json>
"""
import sys
import json
import random
from pathlib import Path
from typing import Any

# Apollo src on path so we can import its modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def _organism_to_desc(org) -> str:
    """Match Apollo's mutation._organism_to_desc shape."""
    lines = [f"Tool genome with {len(org.primitive_sequence)} primitives:"]
    for pc in org.primitive_sequence:
        inputs_str = ", ".join(f"{k}={v}" for k, v in pc.input_mapping.items())
        lines.append(f"  {pc.node_id}: {pc.primitive_name}({inputs_str})")
    return "\n".join(lines)


def _route_prompt(org) -> str:
    node_info = ", ".join(f"{pc.node_id}={pc.primitive_name}" for pc in org.primitive_sequence)
    param_keys = list(org.parameters.keys())
    return f"""You are modifying the routing logic for a reasoning tool.
The tool has these primitive nodes: {node_info}
Available parameters: {param_keys}

Current router code (receives prompt, candidates, outputs, params):
```python
{org.router_logic}
```

Modify this router to improve scoring. The function receives:
- prompt: the question string
- candidates: list of candidate answer strings
- outputs: dict mapping node_id to primitive output (e.g. outputs['n0'])
- params: dict of evolvable float parameters

Rules:
- Return a list of float scores, one per candidate
- You may ONLY reference node IDs from the list above
- Use outputs.get('nX') to safely access node outputs (may be None)
- You may use re, math, numpy (as np)
- Do NOT import anything else
- Do NOT define classes

Return ONLY the modified router code body (no function def, no explanation):"""


def _wiring_prompt(org) -> str:
    return f"""You are rewiring a reasoning tool's primitive connections.

{_organism_to_desc(org)}

Suggest ONE wiring change: change which node's output feeds into which parameter.
Valid sources: "prompt", "candidates", "nX.output" (where X < target node index), "param.KEY"

Return ONLY a JSON object like:
{{"n2": {{"relations": "n0.output"}}}}

This means: change node n2's 'relations' input to come from n0's output.
No explanation, just the JSON:"""


def _swap_prompt(org) -> str:
    if not org.primitive_sequence:
        return None
    node = random.choice(org.primitive_sequence)
    from genome import PRIMITIVE_CATALOG
    catalog_str = "\n".join(
        f"  {cat}: {', '.join(names)}"
        for cat, names in PRIMITIVE_CATALOG.items()
    )
    return f"""You are suggesting a replacement primitive in a reasoning tool.

Current organism:
{_organism_to_desc(org)}

The node {node.node_id} currently runs '{node.primitive_name}'.

Available primitives by category:
{catalog_str}

Suggest ONE replacement primitive for {node.node_id} that improves reasoning.
Reply with ONLY the primitive name (one word, exact match from the catalog):"""


def build_prompts(checkpoint_path: str) -> list[dict[str, Any]]:
    """Returns a list of {id, kind, prompt, parent_genome_id, variant} dicts."""
    import pickle
    with open(checkpoint_path, "rb") as f:
        data = pickle.load(f)
    population = data.get("population", [])
    print(f"Loaded {len(population)} organisms from {checkpoint_path}", file=sys.stderr)

    random.seed(20260522)
    prompts = []
    pid = 0

    # Route prompts (~70)
    for org in population[:50]:
        try:
            p = _route_prompt(org)
            prompts.append({"id": f"r{pid:03d}", "kind": "route", "variant": "base",
                            "parent_genome_id": org.genome_id, "prompt": p})
            pid += 1
        except Exception as e:
            print(f"Route prompt fail: {e}", file=sys.stderr)
    # add 20 with a "be terse" preamble variant
    for org in random.sample(population, 20):
        try:
            p = "You are a code-only assistant. Output ONLY a Python code block, no explanation.\n\n" + _route_prompt(org)
            prompts.append({"id": f"r{pid:03d}", "kind": "route", "variant": "terse",
                            "parent_genome_id": org.genome_id, "prompt": p})
            pid += 1
        except Exception as e:
            pass

    # Wiring prompts (~60)
    for org in population[:50]:
        try:
            p = _wiring_prompt(org)
            prompts.append({"id": f"w{pid:03d}", "kind": "wiring", "variant": "base",
                            "parent_genome_id": org.genome_id, "prompt": p})
            pid += 1
        except Exception as e:
            pass
    for org in random.sample(population, 10):
        try:
            p = "Output strictly ONE JSON object. No prose.\n\n" + _wiring_prompt(org)
            prompts.append({"id": f"w{pid:03d}", "kind": "wiring", "variant": "strict",
                            "parent_genome_id": org.genome_id, "prompt": p})
            pid += 1
        except:
            pass

    # Swap prompts (~70)
    for org in population[:50]:
        try:
            p = _swap_prompt(org)
            if p:
                prompts.append({"id": f"s{pid:03d}", "kind": "swap", "variant": "base",
                                "parent_genome_id": org.genome_id, "prompt": p})
                pid += 1
        except Exception as e:
            pass
    for org in random.sample(population, 20):
        try:
            p = _swap_prompt(org)
            if p:
                p = "Reply with one word only.\n\n" + p
                prompts.append({"id": f"s{pid:03d}", "kind": "swap", "variant": "oneword",
                                "parent_genome_id": org.genome_id, "prompt": p})
                pid += 1
        except:
            pass

    return prompts


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    ckpt = sys.argv[1]
    out = sys.argv[2]
    prompts = build_prompts(ckpt)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"prompts": prompts, "checkpoint": ckpt, "n": len(prompts)},
                  f, indent=2)
    by_kind = {}
    for p in prompts:
        by_kind[p["kind"]] = by_kind.get(p["kind"], 0) + 1
    print(f"Wrote {len(prompts)} prompts to {out}")
    print(f"By kind: {by_kind}")


if __name__ == "__main__":
    main()
