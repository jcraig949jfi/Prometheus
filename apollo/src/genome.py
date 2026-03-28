"""
genome.py — Genome representation for whole-tool organisms.

Each organism is a complete forge tool source code. Evolution modifies
the source through parameter mutation, method swaps, and LLM mutation.
"""

import uuid
import hashlib
import copy
import random
from dataclasses import dataclass, field
from pathlib import Path
import glob


@dataclass
class Genome:
    genome_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    source_code: str = ""                # Complete Python source code
    source_tool: str = ""                # Original forge tool name
    parameters: dict = field(default_factory=dict)  # Extracted param name -> value
    method_names: list = field(default_factory=list) # Methods in the class
    lineage: dict = field(default_factory=lambda: {
        'parent_ids': [], 'mutations_applied': [], 'generation': 0
    })

    @property
    def gene_count(self) -> int:
        return len(self.method_names)

    def has_self_referential_wiring(self) -> bool:
        # For whole-tool organisms, check for actual recursion
        # (a method calling itself, or two methods calling each other)
        import re
        for method in self.method_names:
            if method in ('evaluate', 'confidence', '__init__'):
                continue
            # Find the method body and check if it calls itself
            pattern = rf'def {re.escape(method)}\s*\(.*?\).*?(?=\n    def |\nclass |\Z)'
            match = re.search(pattern, self.source_code, re.DOTALL)
            if match:
                body = match.group()
                # Check if the method body contains self.method( calls to itself
                if f'self.{method}(' in body.split('\n', 1)[-1] if '\n' in body else '':
                    return True
        return False

    @property
    def cycle_count(self) -> int:
        return 1 if self.has_self_referential_wiring() else 0

    def wiring_hash(self) -> str:
        return hashlib.sha256(self.source_code.encode()).hexdigest()[:16]

    @property
    def fallback_count(self) -> int:
        return sum(1 for m in self.method_names if 'ncd' in m.lower())

    def clone(self) -> 'Genome':
        return Genome(
            genome_id=str(uuid.uuid4())[:12],
            source_code=self.source_code,
            source_tool=self.source_tool,
            parameters=dict(self.parameters),
            method_names=list(self.method_names),
            lineage=copy.deepcopy(self.lineage),
        )


def _inline_shared_imports(source: str, forge_dir: str) -> str:
    """Inline shared _caitl_v3 module into tool source."""
    import re as _re
    if '_caitl_v3' not in source and '_caitl_parsers' not in source:
        return source

    # Load shared modules
    shared_source = ""
    for shared_name in ['_caitl_v3', '_caitl_parsers']:
        shared_path = Path(forge_dir) / f'{shared_name}.py'
        if shared_path.exists() and shared_name in source:
            shared_source += shared_path.read_text(encoding='utf-8') + '\n'
            # Add alias if tool imports with alias
            if f'from {shared_name} import structural_score as _structural_score' in source:
                shared_source += '_structural_score = structural_score\n'

    # Remove all os/sys imports and caitl imports from tool source
    lines = source.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip os/sys imports in any form
        if _re.match(r'^import\s+os', stripped):
            continue
        if _re.match(r'^import\s+sys', stripped):
            continue
        if 'import os' in stripped and 'import' in stripped.split('os')[0]:
            # Handle "import re, zlib, math, os, sys" -> remove os and sys
            new_line = _re.sub(r',?\s*os', '', line)
            new_line = _re.sub(r',?\s*sys', '', new_line)
            new_line = _re.sub(r'import\s*,', 'import ', new_line)  # fix leading comma
            if new_line.strip() and new_line.strip() != 'import':
                cleaned.append(new_line)
            continue
        if stripped.startswith('sys.path'):
            continue
        if stripped.startswith('from _caitl'):
            continue
        if stripped.startswith('from _gen_'):
            continue
        cleaned.append(line)
    source = '\n'.join(cleaned)

    return shared_source + '\n' + source


def create_genome_from_tool(filepath: str) -> Genome:
    """Load a forge tool and create a Genome from it."""
    import ast
    source = Path(filepath).read_text(encoding='utf-8')
    tool_name = Path(filepath).stem

    # Inline shared imports for v3 tools
    forge_dir = str(Path(filepath).parent)
    source = _inline_shared_imports(source, forge_dir)

    # Extract method names
    methods = []
    params = {}
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'ReasoningTool':
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                        if item.name == '__init__':
                            for stmt in ast.walk(item):
                                if isinstance(stmt, ast.Assign):
                                    for target in stmt.targets:
                                        if (isinstance(target, ast.Attribute) and
                                            isinstance(target.value, ast.Name) and
                                            target.value.id == 'self'):
                                            try:
                                                val = ast.literal_eval(stmt.value)
                                                if isinstance(val, (int, float)):
                                                    params[target.attr] = float(val)
                                            except (ValueError, TypeError):
                                                pass
    except:
        pass

    return Genome(
        source_code=source,
        source_tool=tool_name,
        parameters=params,
        method_names=methods,
        lineage={'parent_ids': [tool_name], 'mutations_applied': ['seed'], 'generation': 0}
    )


def create_seed_population(forge_path: str, pop_size: int = 50,
                           scores_path: str = None) -> list:
    """Load forge tools and create seed population.

    If scores_path is provided (v3_seed_candidates.json), uses score-based selection:
    top 30 by unseen accuracy + 20 most structurally diverse.
    """
    import json

    # If we have score data, use it for intelligent selection
    if scores_path and Path(scores_path).exists():
        candidates = json.loads(Path(scores_path).read_text())
        all_genomes = []
        for c in candidates:
            filepath = c['file']
            if Path(filepath).exists():
                genome = create_genome_from_tool(filepath)
                if genome.source_code and 'evaluate' in genome.method_names:
                    genome._unseen_acc = c.get('unseen_acc', 0)
                    genome._gap = c.get('gap', 0)
                    all_genomes.append(genome)

        if len(all_genomes) <= pop_size:
            return all_genomes

        # Sort by unseen accuracy
        all_genomes.sort(key=lambda g: g._unseen_acc, reverse=True)

        # Top 30 by unseen accuracy
        top_30 = all_genomes[:30]

        # 20 most structurally diverse from the rest
        remaining = all_genomes[30:]
        selected = list(top_30)

        # Diversity by method name sets
        selected_method_sets = [frozenset(g.method_names) for g in selected]

        for _ in range(min(20, len(remaining))):
            best_genome = None
            best_diversity = -1
            for g in remaining:
                g_methods = frozenset(g.method_names)
                min_dist = min(len(g_methods.symmetric_difference(s))
                              for s in selected_method_sets) if selected_method_sets else 999
                if min_dist > best_diversity:
                    best_diversity = min_dist
                    best_genome = g
            if best_genome:
                selected.append(best_genome)
                selected_method_sets.append(frozenset(best_genome.method_names))
                remaining.remove(best_genome)

        return selected[:pop_size]

    # Fallback: load all tools from directory
    tool_files = sorted(glob.glob(str(Path(forge_path) / "*.py")))
    all_genomes = []

    for filepath in tool_files:
        if Path(filepath).stem.startswith('_'):
            continue
        genome = create_genome_from_tool(filepath)
        if genome.source_code and 'evaluate' in genome.method_names:
            all_genomes.append(genome)

    if len(all_genomes) <= pop_size:
        return all_genomes

    random.shuffle(all_genomes)
    return all_genomes[:pop_size]
