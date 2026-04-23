"""
sandbox.py — Safe execution of evolved organisms.

Layer 1: AST-based import validation (compile-time)
Layer 2: Direct exec() with threading timeout (runtime)

Windows-compatible: no multiprocessing.Process needed.
"""

import ast
import sys
import threading
import time
from pathlib import Path

# Ensure forge_primitives is importable
_primitives_dir = str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src")
if _primitives_dir not in sys.path:
    sys.path.insert(0, _primitives_dir)

ALLOWED_IMPORTS = {
    'numpy', 'np', 'math', 're', 'zlib', 'hashlib', 'collections',
    'itertools', 'functools', 'statistics', 'random', 'string',
    'operator', 'heapq', 'bisect', 'decimal', 'fractions', 'struct',
    'copy', 'dataclasses',
    'forge_primitives',  # Frame H primitives (safe, pure computation)
}

BLOCKED_IMPORTS = {
    'os', 'sys', 'subprocess', 'socket', 'io', 'pathlib', 'importlib',
    'shutil', 'signal', 'ctypes', 'multiprocessing', 'threading',
    'http', 'urllib', 'requests', 'pickle', 'shelve', 'sqlite3',
}


def check_imports(source_code: str) -> tuple:
    """Check if source code only uses allowed imports."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split('.')[0]
                if mod in BLOCKED_IMPORTS:
                    return False, f"Blocked import: {mod}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split('.')[0]
                if mod in BLOCKED_IMPORTS:
                    return False, f"Blocked from-import: {mod}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ('exec', 'eval', '__import__', 'open', 'input'):
                    return False, f"Blocked builtin: {node.func.id}"

    return True, None


def _exec_with_timeout(func, args, timeout):
    """Run func(*args) with a timeout. Returns (result, error)."""
    result = [None]
    error = [None]

    def target():
        try:
            result[0] = func(*args)
        except Exception as e:
            error[0] = str(e)[:200]

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        return None, 'timeout'
    return result[0], error[0]


def _load_tool(source_code: str):
    """Compile and instantiate a ReasoningTool from source."""
    namespace = {}
    exec(source_code, namespace)
    tool_class = namespace.get('ReasoningTool')
    if tool_class is None:
        raise ValueError("No ReasoningTool class")
    return tool_class()


# Cache compiled tools to avoid re-exec on every task
_tool_cache = {}

def _get_tool(source_code: str):
    """Get or create a cached tool instance."""
    code_hash = hash(source_code)
    if code_hash not in _tool_cache:
        if len(_tool_cache) > 200:  # Prevent unbounded cache growth
            _tool_cache.clear()
        _tool_cache[code_hash] = _load_tool(source_code)
    return _tool_cache[code_hash]


def safe_evaluate(source_code: str, prompt: str, candidates: list,
                  timeout: float = 0.5) -> dict:
    """Execute organism evaluation with timeout."""
    try:
        tool = _get_tool(source_code)
    except Exception as e:
        return {'error': str(e)[:100], 'results': None, 'confidence': 0.0}

    def run_eval():
        results = tool.evaluate(prompt, candidates)
        conf = tool.confidence(prompt, candidates[0]) if candidates else 0.0
        return {'results': results, 'confidence': conf, 'error': None}

    result, error = _exec_with_timeout(run_eval, (), timeout)
    if error:
        return {'error': error, 'results': None, 'confidence': 0.0}
    if result is None:
        return {'error': 'timeout', 'results': None, 'confidence': 0.0}
    return result


def evaluate_organism_on_tasks(source_code: str, tasks: list,
                                timeout: float = 0.5) -> list:
    """Evaluate one organism on multiple tasks."""
    results = []
    for task in tasks:
        r = safe_evaluate(source_code, task['prompt'], task['candidates'], timeout)
        if r.get('error'):
            results.append({
                'correct': False,
                'confidence_correct': 0.0,
                'confidence_wrong': 0.0,
                'score': 0.0,
                'error': r['error'],
                'gene_trace': '',
            })
        else:
            eval_results = r.get('results', [])
            if eval_results:
                top = eval_results[0]['candidate']
                correct = (top == task['correct'])

                # Get confidence for the top-ranked candidate
                conf = r.get('confidence', 0.0)

                results.append({
                    'correct': correct,
                    'confidence_correct': conf if correct else 0.0,
                    'confidence_wrong': conf if not correct else 0.0,
                    'score': eval_results[0].get('score', 0.0),
                    'error': None,
                    'gene_trace': eval_results[0].get('reasoning', ''),
                })
            else:
                results.append({
                    'correct': False,
                    'confidence_correct': 0.0,
                    'confidence_wrong': 0.0,
                    'score': 0.0,
                    'error': 'empty results',
                    'gene_trace': '',
                })
    return results


def quick_screen(source_code: str, tasks: list, timeout: float = 0.5) -> bool:
    """Quick viability check: does the organism run and produce output?"""
    for task in tasks[:3]:
        r = safe_evaluate(source_code, task['prompt'], task['candidates'], timeout)
        if not r.get('error'):
            results = r.get('results', [])
            if results:
                return True
    return False
