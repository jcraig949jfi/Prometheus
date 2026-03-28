"""
compiler.py — Compile organisms into executable ReasoningTool classes.

Approach: Each organism starts as a whole forge tool source code.
Mutations modify the source directly (parameter tweaks, method swaps).
The compiler validates and wraps with ctx-dict instrumentation.
"""

import ast
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompilationResult:
    success: bool
    source_code: str = None
    error: str = None


def compile_from_source(source_code: str) -> CompilationResult:
    """Validate source code is a working ReasoningTool. Minimal wrapper."""
    try:
        ast.parse(source_code)
    except SyntaxError as e:
        return CompilationResult(False, error=f"SyntaxError: {e}")

    # Check it has ReasoningTool class with evaluate and confidence
    tree = ast.parse(source_code)
    has_class = False
    has_evaluate = False
    has_confidence = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'ReasoningTool':
            has_class = True
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name == 'evaluate':
                        has_evaluate = True
                    elif item.name == 'confidence':
                        has_confidence = True

    if not has_class:
        return CompilationResult(False, error="No ReasoningTool class")
    if not has_evaluate:
        return CompilationResult(False, error="No evaluate method")
    if not has_confidence:
        return CompilationResult(False, error="No confidence method")

    return CompilationResult(True, source_code=source_code)


def load_forge_tool_source(filepath: str) -> str:
    """Load a forge tool's source code."""
    return Path(filepath).read_text(encoding='utf-8')


def apply_parameter_mutation(source_code: str, param_name: str,
                             old_value: float, new_value: float) -> str:
    """Modify a numeric parameter in __init__."""
    # Find self.param_name = old_value and replace with new_value
    pattern = rf'(self\.{re.escape(param_name)}\s*=\s*){re.escape(str(old_value))}'
    replacement = rf'\g<1>{new_value}'
    result = re.sub(pattern, replacement, source_code, count=1)
    if result == source_code:
        # Try a more flexible match
        pattern = rf'(self\.{re.escape(param_name)}\s*=\s*)[\d.eE+-]+'
        replacement = rf'\g<1>{new_value}'
        result = re.sub(pattern, replacement, source_code, count=1)
    return result


def extract_parameters(source_code: str) -> dict:
    """Extract all self.X = <number> from __init__."""
    params = {}
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'ReasoningTool':
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == '__init__':
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
    return params


def extract_methods(source_code: str) -> dict:
    """Extract method names and their source from a ReasoningTool class."""
    methods = {}
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'ReasoningTool':
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_src = ast.get_source_segment(source_code, item)
                        if method_src:
                            methods[item.name] = method_src
    except:
        pass
    return methods


def swap_method(source_a: str, source_b: str, method_name: str) -> str:
    """Replace method_name in source_a with the version from source_b."""
    methods_a = extract_methods(source_a)
    methods_b = extract_methods(source_b)

    if method_name not in methods_a or method_name not in methods_b:
        return source_a

    old_method = methods_a[method_name]
    new_method = methods_b[method_name]

    # Ensure same indentation
    old_indent = len(old_method) - len(old_method.lstrip())
    new_indent = len(new_method) - len(new_method.lstrip())
    if old_indent != new_indent:
        # Re-indent new method to match
        dedented = textwrap.dedent(new_method)
        new_method = textwrap.indent(dedented, ' ' * old_indent)

    return source_a.replace(old_method, new_method)


def smoke_test(source_code: str, trap: dict, timeout: float = 2.0) -> tuple:
    """Quick test: compile, run, check discrimination. Returns (runs, discriminates)."""
    try:
        namespace = {}
        exec(source_code, namespace)
        tool = namespace['ReasoningTool']()
        results = tool.evaluate(trap['prompt'], trap['candidates'])
        if not results or len(results) < 2:
            return True, False
        scores = [r['score'] for r in results]
        discriminates = len(set(round(s, 8) for s in scores)) > 1
        return True, discriminates
    except Exception:
        return False, False
