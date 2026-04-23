"""
gene_extractor.py — Parse forge tools into a two-tier gene library.

Tier 1: Fine-grained genes (high portability) — individual methods
Tier 2: Macro-genes (low portability) — bundled PARSER+SCORER methods
"""

import ast
import re
import json
import uuid
import glob
import textwrap
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Gene:
    gene_id: str
    source_tool: str
    method_name: str
    gene_type: str          # PARSER | SCORER | FALLBACK | UTILITY | MACRO
    source_code: str
    is_macro: bool = False
    portability_score: float = 1.0
    dependencies: list = field(default_factory=list)   # utility method names needed
    parameters: dict = field(default_factory=dict)      # param_name -> default_value
    imports_needed: list = field(default_factory=list)
    reads_keys: list = field(default_factory=list)      # convention keys this gene reads
    writes_keys: list = field(default_factory=list)     # convention keys this gene writes


def classify_gene_type(method_name: str, method_source: str) -> str:
    name = method_name.lower()
    src = method_source.lower()
    if name in ('evaluate', 'confidence', '__init__'):
        return 'SKIP'
    if 'ncd' in name or 'normalized_compression' in name:
        if 'compress' in src or 'zlib' in src:
            return 'FALLBACK'
    if name.startswith(('_extract', '_parse', '_tokenize', '_hash_to')):
        return 'PARSER'
    if name.startswith('_sigmoid') or name.startswith('_clamp') or name.startswith('_normalize'):
        return 'UTILITY'
    if 'score' in name or 'compute' in name or 'check' in name or 'run_' in name:
        return 'SCORER'
    return 'SCORER'  # default


def compute_portability_score(method_source: str) -> float:
    score = 1.0
    long_strings = re.findall(r'["\'][^"\']{20,}["\']', method_source)
    if long_strings:
        score -= 0.3
    english_patterns = ['not ', 'all ', 'every ', 'some ', 'true', 'false',
                        'yes', 'no', 'larger', 'smaller', 'greater', 'less']
    english_count = sum(1 for p in english_patterns if p in method_source.lower())
    if english_count > 3:
        score -= 0.2
    non_convention = re.findall(r"ctx\['(?!prompt|candidate|raw_text|parsed|score|fallback_score|_gene_trace|_final_gene_type)[^']+'\]", method_source)
    if non_convention:
        score -= 0.3
    regex_patterns = re.findall(r're\.(search|match|findall|sub)\s*\([^)]{30,}\)', method_source)
    if regex_patterns:
        score -= 0.2
    return max(0.0, min(1.0, score))


def _extract_parameters(init_node: ast.FunctionDef) -> dict:
    params = {}
    for node in ast.walk(init_node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (isinstance(target, ast.Attribute) and
                    isinstance(target.value, ast.Name) and
                    target.value.id == 'self'):
                    param_name = target.attr
                    if param_name.startswith('_') and not param_name.startswith('__'):
                        continue  # skip private state like _history
                    try:
                        value = ast.literal_eval(node.value)
                        if isinstance(value, (int, float)):
                            params[param_name] = float(value)
                    except (ValueError, TypeError):
                        pass
    return params


def _extract_imports(source: str) -> list:
    imports = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return list(imports)


def _find_method_calls(method_node: ast.FunctionDef) -> list:
    calls = []
    for node in ast.walk(method_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                    calls.append(node.func.attr)
    return calls


def _rewrite_self_params(source: str, gene_id: str, params: dict) -> str:
    for param_name in params:
        source = re.sub(
            rf'self\.{re.escape(param_name)}\b',
            f"self.params['{gene_id}_{param_name}']",
            source
        )
    return source


def _infer_context_keys(method_source: str) -> tuple:
    reads = set()
    writes = set()
    # Look for ctx['key'] reads and writes
    for match in re.finditer(r"ctx\['([^']+)'\]", method_source):
        reads.add(match.group(1))
    for match in re.finditer(r"ctx\['([^']+)'\]\s*=", method_source):
        writes.add(match.group(1))
    reads -= writes  # keys that are only read, not written
    return list(reads), list(writes)


def extract_tool(filepath: str) -> tuple:
    """Extract genes + parameters from a single forge tool. Returns (genes, params, imports)."""
    source = Path(filepath).read_text(encoding='utf-8')
    tool_name = Path(filepath).stem

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], {}, []

    imports = _extract_imports(source)

    # Find the ReasoningTool class
    class_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'ReasoningTool':
            class_node = node
            break

    if class_node is None:
        return [], {}, imports

    # Extract all methods
    methods = {}
    init_params = {}
    evaluate_calls = []

    for item in class_node.body:
        if isinstance(item, ast.FunctionDef):
            method_source = ast.get_source_segment(source, item)
            if method_source is None:
                # Fallback: unparse
                try:
                    method_source = ast.unparse(item)
                except:
                    continue
            methods[item.name] = {
                'node': item,
                'source': method_source,
                'calls': _find_method_calls(item)
            }
            if item.name == '__init__':
                init_params = _extract_parameters(item)
            if item.name == 'evaluate':
                evaluate_calls = _find_method_calls(item)

    # Determine which methods are called directly from evaluate/confidence
    direct_calls = set(evaluate_calls)
    if 'confidence' in methods:
        direct_calls.update(methods['confidence']['calls'])

    # Build call graph to find utilities (only called by other methods)
    all_internal_calls = set()
    for name, info in methods.items():
        if name not in ('evaluate', 'confidence', '__init__'):
            all_internal_calls.update(info['calls'])

    genes = []

    for name, info in methods.items():
        gene_type = classify_gene_type(name, info['source'])
        if gene_type == 'SKIP':
            continue

        # Check if this is a utility (never called from evaluate/confidence directly)
        if name not in direct_calls and name in all_internal_calls:
            gene_type = 'UTILITY'

        gene_id = f"{tool_name}__{name}"

        # Rewrite self.param references
        rewritten_source = _rewrite_self_params(info['source'], gene_id, init_params)

        portability = compute_portability_score(info['source'])
        reads, writes = _infer_context_keys(info['source'])

        gene = Gene(
            gene_id=gene_id,
            source_tool=tool_name,
            method_name=name,
            gene_type=gene_type,
            source_code=rewritten_source,
            is_macro=False,
            portability_score=portability,
            dependencies=info['calls'],
            parameters={f"{gene_id}_{k}": v for k, v in init_params.items()},
            imports_needed=imports,
            reads_keys=reads,
            writes_keys=writes,
        )
        genes.append(gene)

    return genes, init_params, imports


def _create_macro_gene(tool_name: str, methods: dict, init_params: dict, imports: list, source: str) -> Gene:
    """Create a macro-gene from an entire tool's methods (excluding evaluate/confidence/__init__)."""
    combined_source = ""
    for name, info in methods.items():
        if name not in ('evaluate', 'confidence', '__init__'):
            combined_source += info['source'] + "\n\n"

    gene_id = f"{tool_name}__macro"
    rewritten = _rewrite_self_params(combined_source, gene_id, init_params)

    return Gene(
        gene_id=gene_id,
        source_tool=tool_name,
        method_name="macro",
        gene_type="MACRO",
        source_code=rewritten,
        is_macro=True,
        portability_score=0.3,
        parameters={f"{gene_id}_{k}": v for k, v in init_params.items()},
        imports_needed=imports,
    )


def extract_two_tier_genes(forge_path: str) -> dict:
    """Parse all forge tools, return gene_id -> Gene dict."""
    gene_library = {}
    tool_files = sorted(glob.glob(str(Path(forge_path) / "*.py")))

    stats = {'tools': 0, 'fine_genes': 0, 'macro_genes': 0, 'skipped': 0}

    for filepath in tool_files:
        genes, params, imports = extract_tool(filepath)
        stats['tools'] += 1

        if not genes:
            stats['skipped'] += 1
            continue

        # Determine if tool should be a macro-gene
        # If most methods have low portability, bundle as macro
        non_utility = [g for g in genes if g.gene_type != 'UTILITY']
        if non_utility:
            avg_portability = sum(g.portability_score for g in non_utility) / len(non_utility)
        else:
            avg_portability = 0.0

        if avg_portability < 0.4 and len(non_utility) > 2:
            # Low portability tool — create a macro-gene
            source = Path(filepath).read_text(encoding='utf-8')
            tree = ast.parse(source)
            class_node = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == 'ReasoningTool':
                    class_node = node
                    break
            if class_node:
                methods_dict = {}
                for item in class_node.body:
                    if isinstance(item, ast.FunctionDef):
                        ms = ast.get_source_segment(source, item)
                        if ms is None:
                            try:
                                ms = ast.unparse(item)
                            except:
                                continue
                        methods_dict[item.name] = {'source': ms, 'calls': _find_method_calls(item)}
                macro = _create_macro_gene(Path(filepath).stem, methods_dict, params, imports, source)
                gene_library[macro.gene_id] = macro
                stats['macro_genes'] += 1
            # Also keep individual genes for fine-grained recombination
            for gene in genes:
                gene_library[gene.gene_id] = gene
                stats['fine_genes'] += 1
        else:
            for gene in genes:
                gene_library[gene.gene_id] = gene
                stats['fine_genes'] += 1

    print(f"Gene extraction complete: {stats['tools']} tools -> "
          f"{stats['fine_genes']} fine genes + {stats['macro_genes']} macro genes "
          f"({stats['skipped']} tools skipped)")

    return gene_library


def save_gene_library(gene_library: dict, path: str):
    serializable = {}
    for gid, gene in gene_library.items():
        d = asdict(gene)
        serializable[gid] = d
    Path(path).write_text(json.dumps(serializable, indent=2), encoding='utf-8')


def load_gene_library(path: str) -> dict:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    library = {}
    for gid, d in data.items():
        library[gid] = Gene(**d)
    return library


if __name__ == '__main__':
    import sys
    forge_path = sys.argv[1] if len(sys.argv) > 1 else "F:/Prometheus/agents/hephaestus/forge/"
    library = extract_two_tier_genes(forge_path)
    save_gene_library(library, "F:/Prometheus/apollo/gene_library.json")

    # Print stats
    types = {}
    for g in library.values():
        types[g.gene_type] = types.get(g.gene_type, 0) + 1
    print(f"Gene types: {types}")
    print(f"Total genes: {len(library)}")

    portabilities = [g.portability_score for g in library.values()]
    if portabilities:
        print(f"Portability: mean={sum(portabilities)/len(portabilities):.2f}, "
              f"min={min(portabilities):.2f}, max={max(portabilities):.2f}")
