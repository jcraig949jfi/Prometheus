"""Convert parsed operator trees to evaluable numpy functions.

Bottleneck tool: turns formula_trees.jsonl into callable Python functions
via code-string compilation (no sympy). Target: 100K conversions/sec.
"""

import argparse
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    import orjson as _json
    def _loads(s):
        return _json.loads(s)
    def _dumps(o):
        return _json.dumps(o).decode()
except ImportError:
    _json = json
    _loads = json.loads
    _dumps = json.dumps

# Punctuation variables that are parsing artifacts, not real math variables
_PUNCT_VARS = frozenset({',', '.', ':', ';', '|', '/', '>', '<', '!', '?',
                         'Longrightarrow', 'longrightarrow', 'rightarrow',
                         'leftarrow', 'mapsto', 'cdots', 'ldots', 'dots',
                         'quad', 'qquad', 'text', 'mathrm', 'operatorname'})

# Ops that make a formula non-evaluable (symbolic / integral / etc.)
_UNEVALUABLE_OPS = frozenset({
    'sum', 'prod', 'int', 'oint', 'lim', 'liminf', 'limsup', 'inf',
    'bigcap', 'bigcup', 'from', 'to', 'in', 'subset', 'subseteq', 'supset',
    'implies', 'iff', 'equiv', 'cong', 'sim', 'approx', 'neq',
    'mathbb', 'mathbf', 'mathcal', 'mathit', 'mathrm',
    'overline', 'underline', 'underset', 'bar', 'hat', 'tilde', 'vec',
    'dot', 'boxed', 'Big', 'Pr', 'gcd', 'max', 'min', 'not',
})

# Relations that we can't evaluate as arithmetic
_RELATION_OPS = frozenset({'gt', 'lt', 'geq', 'leq', 'neq', 'approx',
                           'sim', 'cong', 'equiv', 'implies', 'iff'})


_sanitize_cache = {}

def _sanitize_var(name: str) -> str:
    """Turn a variable name into a valid Python identifier."""
    cached = _sanitize_cache.get(name)
    if cached is not None:
        return cached
    if not name or name in _PUNCT_VARS:
        _sanitize_cache[name] = ''
        return ''
    s = name.replace(' ', '_').replace('-', '_')
    if s.isidentifier():
        _sanitize_cache[name] = s
        return s
    result = 'v_' + ''.join(c if c.isalnum() else f'_{ord(c):x}_' for c in s)
    _sanitize_cache[name] = result
    return result


def _collect_variables(node: dict) -> set:
    """Walk tree, collect real variable names."""
    vs = set()
    ntype = node.get('type', '')
    if ntype == 'variable':
        name = node.get('name', '')
        san = _sanitize_var(name)
        if san:
            vs.add(san)
    for child in node.get('children', []):
        vs.update(_collect_variables(child))
    return vs


def _has_unevaluable(node: dict) -> bool:
    """Check if tree contains ops we can't convert."""
    op = node.get('op', '')
    if op in _UNEVALUABLE_OPS:
        return True
    ntype = node.get('type', '')
    if ntype in ('sequence', 'relation'):
        return True
    for child in node.get('children', []):
        if _has_unevaluable(child):
            return True
    return False


def _node_to_code(node: dict) -> str:
    """Recursively convert a tree node to a Python expression string.

    Returns a string or raises ValueError if unconvertible.
    """
    ntype = node.get('type', '')
    op = node.get('op', '')
    children = node.get('children', [])

    # --- Leaf nodes ---
    if ntype == 'number':
        val = node.get('value', '0')
        try:
            float(val)
        except (ValueError, TypeError):
            return '0.0'
        return str(val)

    if ntype == 'variable':
        name = node.get('name', '')
        san = _sanitize_var(name)
        if not san:
            raise ValueError(f'punctuation variable: {name}')
        return f'_v["{san}"]'

    # --- Group (parenthesized expressions) ---
    if ntype == 'group':
        # Filter out punctuation children
        real = []
        for c in children:
            try:
                real.append(_node_to_code(c))
            except ValueError:
                continue
        if not real:
            raise ValueError('empty group')
        if len(real) == 1:
            return f'({real[0]})'
        # Multiple children in a group = product (implicit multiplication)
        return '(' + ' * '.join(real) + ')'

    # --- Equation: extract left side ---
    if ntype == 'equation':
        if op in _RELATION_OPS:
            raise ValueError(f'relation op: {op}')
        if op == 'eq' and len(children) >= 2:
            # Return left side as the expression
            return _node_to_code(children[0])
        if children:
            return _node_to_code(children[0])
        raise ValueError('empty equation')

    # --- Operators ---
    if ntype == 'operator':
        if op in _UNEVALUABLE_OPS:
            raise ValueError(f'unevaluable op: {op}')

        # Binary arithmetic
        if op == 'add':
            parts = [_node_to_code(c) for c in children]
            if len(parts) == 1:
                return parts[0]
            return '(' + ' + '.join(parts) + ')'

        if op == 'sub':
            parts = [_node_to_code(c) for c in children]
            if len(parts) == 1:
                return f'(-{parts[0]})'
            if len(parts) == 2:
                return f'({parts[0]} - {parts[1]})'
            return '(' + ' - '.join(parts) + ')'

        if op == 'multiply':
            # Filter out punctuation children
            real = []
            for c in children:
                try:
                    real.append(_node_to_code(c))
                except ValueError:
                    continue
            if not real:
                raise ValueError('empty multiply')
            if len(real) == 1:
                return real[0]
            return '(' + ' * '.join(real) + ')'

        if op == 'neg':
            if children:
                return f'(-{_node_to_code(children[0])})'
            raise ValueError('neg without child')

        if op == 'power':
            if len(children) >= 2:
                base = _node_to_code(children[0])
                exp = _node_to_code(children[1])
                return f'({base} ** {exp})'
            raise ValueError('power needs 2 children')

        if op in ('frac', 'dfrac'):
            if len(children) >= 2:
                num = _node_to_code(children[0])
                den = _node_to_code(children[1])
                return f'({num} / {den})'
            raise ValueError('frac needs 2 children')

        if op == 'sqrt':
            if children:
                return f'np.sqrt({_node_to_code(children[0])})'
            raise ValueError('sqrt without child')

        # Trig / transcendental
        if op == 'sin':
            if children:
                return f'np.sin({_node_to_code(children[0])})'
            raise ValueError('sin without child')

        if op == 'cos':
            if children:
                return f'np.cos({_node_to_code(children[0])})'
            raise ValueError('cos without child')

        if op == 'tan':
            if children:
                return f'np.tan({_node_to_code(children[0])})'
            raise ValueError('tan without child')

        if op == 'sec':
            if children:
                return f'(1.0 / np.cos({_node_to_code(children[0])}))'
            raise ValueError('sec without child')

        if op == 'exp':
            if children:
                return f'np.exp({_node_to_code(children[0])})'
            raise ValueError('exp without child')

        if op in ('log', 'ln'):
            if children:
                return f'np.log({_node_to_code(children[0])})'
            raise ValueError('log without child')

        if op == 'factorial':
            if children:
                from math import gamma
                return f'_gamma({_node_to_code(children[0])} + 1)'
            raise ValueError('factorial without child')

        # Subscript: label only, return base
        if op == 'subscript':
            if children:
                return _node_to_code(children[0])
            raise ValueError('subscript without child')

        # Superscript: treat as power
        if op == 'superscript':
            if len(children) >= 2:
                base = _node_to_code(children[0])
                exp = _node_to_code(children[1])
                return f'({base} ** {exp})'
            if children:
                return _node_to_code(children[0])
            raise ValueError('superscript without child')

        # Prime: derivative notation, just return base
        if op == 'prime':
            if children:
                return _node_to_code(children[0])
            raise ValueError('prime without child')

        raise ValueError(f'unknown op: {op}')

    raise ValueError(f'unknown node type: {ntype}')


def tree_to_callable(tree_dict: dict) -> tuple:
    """Convert a formula tree dict to (callable, variables, success).

    The callable takes a dict of {var_name: value} and returns numpy result.
    """
    root = tree_dict.get('root')
    if not root:
        return None, [], False

    # Quick reject: if tree has unevaluable ops, skip code generation
    if _has_unevaluable(root):
        return None, sorted(_collect_variables(root)), False

    try:
        code_str = _node_to_code(root)
    except (ValueError, RecursionError):
        return None, sorted(_collect_variables(root)), False

    variables = sorted(_collect_variables(root))

    # Build the function source
    func_source = f"def _f(_v, np=__np__, _gamma=__gamma__):\n    return {code_str}\n"

    try:
        code_obj = compile(func_source, f"<formula:{tree_dict.get('hash','?')}>", 'exec')
        namespace = {'__np__': np, '__gamma__': _scipy_gamma}
        exec(code_obj, namespace)
        fn = namespace['_f']
    except Exception:
        return None, variables, False

    return fn, variables, True


import re
_VAR_RE = re.compile(r'_v\["(\w+)"\]')

def _extract_vars_from_code(code_str: str) -> list:
    """Extract variable names from compiled code string (fast regex)."""
    return sorted(set(_VAR_RE.findall(code_str)))


def tree_to_code_string(tree_dict: dict) -> tuple:
    """Convert tree to (code_string, variables, success) without compiling.

    Faster for batch serialization — the code string can be compiled later.
    """
    root = tree_dict.get('root')
    if not root:
        return '', [], False

    if _has_unevaluable(root):
        return '', [], False

    try:
        code_str = _node_to_code(root)
    except (ValueError, RecursionError):
        return '', [], False

    variables = _extract_vars_from_code(code_str)
    return code_str, variables, True


# Factorial via scipy if available, else math.gamma
try:
    from scipy.special import gamma as _scipy_gamma
except ImportError:
    from math import gamma as _scipy_gamma


def batch_convert(trees_file: str, output_file: str = None, max_formulas: int = 0):
    """Process formula_trees.jsonl -> formula_executables.jsonl.

    Each output line: {"hash": ..., "code": ..., "variables": [...], "success": bool}
    """
    if output_file is None:
        output_file = os.path.join(os.path.dirname(trees_file), 'formula_executables.jsonl')

    t0 = time.time()
    n_total = 0
    n_success = 0
    fail_reasons = Counter()

    with open(trees_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            if max_formulas and n_total >= max_formulas:
                break
            line = line.strip()
            if not line:
                continue

            try:
                tree = _loads(line)
            except (json.JSONDecodeError, ValueError):
                n_total += 1
                continue

            code_str, variables, success = tree_to_code_string(tree)
            n_total += 1
            if success:
                n_success += 1

            out = {
                'hash': tree.get('hash', ''),
                'code': code_str,
                'variables': variables,
                'success': success,
            }
            fout.write(_dumps(out) + '\n')

            if n_total % 100_000 == 0:
                elapsed = time.time() - t0
                rate = n_total / elapsed if elapsed > 0 else 0
                pct = 100 * n_success / n_total if n_total else 0
                print(f"  {n_total:>10,} processed | {pct:.1f}% success | {rate:,.0f}/sec")

    elapsed = time.time() - t0
    rate = n_total / elapsed if elapsed > 0 else 0
    pct = 100 * n_success / n_total if n_total else 0
    print(f"Done: {n_total:,} formulas, {n_success:,} converted ({pct:.1f}%), "
          f"{elapsed:.1f}s ({rate:,.0f}/sec)")
    print(f"Output: {output_file}")
    return n_total, n_success


def cmd_sample(trees_file: str, n: int):
    """Sample N formulas, report success rate and diagnostics."""
    # Count lines for sampling
    print(f"Counting lines in {trees_file}...")
    with open(trees_file, 'r', encoding='utf-8') as f:
        offsets = []
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                break
            if line.strip():
                offsets.append(pos)
    total = len(offsets)
    print(f"  {total:,} formulas found")

    sample_idx = random.sample(range(total), min(n, total))
    sample_idx.sort()

    results = []
    fail_reasons = Counter()
    var_counter = Counter()

    with open(trees_file, 'r', encoding='utf-8') as f:
        idx_set = set(sample_idx)
        for i, line in enumerate(f):
            if i not in idx_set:
                continue
            line = line.strip()
            if not line:
                continue
            tree = _loads(line)
            code_str, variables, success = tree_to_code_string(tree)
            results.append((tree.get('hash'), code_str, variables, success))
            if success:
                for v in variables:
                    var_counter[v] += 1
            else:
                # Diagnose failure
                root = tree.get('root', {})
                reason = _diagnose_failure(root)
                fail_reasons[reason] += 1

    n_ok = sum(1 for r in results if r[3])
    pct = 100 * n_ok / len(results) if results else 0
    print(f"\nSample: {len(results)} formulas, {n_ok} converted ({pct:.1f}%)")
    print(f"\nTop variables:")
    for v, c in var_counter.most_common(20):
        print(f"  {v:>20s}: {c}")
    print(f"\nFailure modes:")
    for reason, c in fail_reasons.most_common(20):
        print(f"  {reason:>30s}: {c}")
    print(f"\nSample converted expressions:")
    shown = 0
    for h, code, vs, ok in results:
        if ok and shown < 10:
            print(f"  {h}: {code[:120]}")
            shown += 1


def _diagnose_failure(node: dict) -> str:
    """Find the first reason a tree is unconvertible."""
    op = node.get('op', '')
    ntype = node.get('type', '')
    if ntype == 'relation':
        return f'relation:{op}'
    if ntype == 'sequence':
        return 'sequence'
    if op in _UNEVALUABLE_OPS:
        return f'unevaluable:{op}'
    if ntype == 'variable' and _sanitize_var(node.get('name', '')) == '':
        return f'punct_var:{node.get("name","")}'
    for child in node.get('children', []):
        r = _diagnose_failure(child)
        if r:
            return r
    return 'unknown'


def cmd_test(trees_file: str, n: int = 100):
    """Convert N formulas and evaluate each at x=1, y=1, etc."""
    print(f"Testing {n} formulas from {trees_file}...")
    tested = 0
    eval_ok = 0
    eval_fail = 0

    with open(trees_file, 'r', encoding='utf-8') as f:
        for line in f:
            if tested >= n:
                break
            line = line.strip()
            if not line:
                continue
            tree = _loads(line)
            fn, variables, success = tree_to_callable(tree)
            if not success:
                continue

            # Build variable dict: all vars = 1.0
            var_dict = {v: 1.0 for v in variables}
            try:
                result = fn(var_dict)
                if np.isfinite(result) if np.isscalar(result) else True:
                    status = 'OK'
                    eval_ok += 1
                else:
                    status = 'non-finite'
                    eval_fail += 1
            except Exception as e:
                status = f'ERROR: {e}'
                eval_fail += 1
                result = None

            tested += 1
            if tested <= 50:
                r_str = f'{result:.6g}' if result is not None and np.isscalar(result) else str(result)
                print(f"  {tree.get('hash','?'):>14s} | vars={variables} | result={r_str} | {status}")

    print(f"\nEvaluated {tested} formulas: {eval_ok} OK, {eval_fail} failed")


def main():
    parser = argparse.ArgumentParser(description='Convert formula trees to executable Python')
    parser.add_argument('--input', '-i', type=str,
                        default=str(Path(__file__).resolve().parents[4] /
                                    'convergence' / 'data' / 'formula_trees.jsonl'),
                        help='Input formula_trees.jsonl')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output formula_executables.jsonl')
    parser.add_argument('--max', type=int, default=0,
                        help='Max formulas to process (0=all)')
    parser.add_argument('--sample', type=int, default=0,
                        help='Sample N formulas and report diagnostics')
    parser.add_argument('--test', type=int, nargs='?', const=100, default=0,
                        help='Convert and evaluate N formulas (default 100)')
    args = parser.parse_args()

    if args.sample:
        cmd_sample(args.input, args.sample)
    elif args.test:
        cmd_test(args.input, args.test)
    else:
        batch_convert(args.input, args.output, args.max)


if __name__ == '__main__':
    main()
