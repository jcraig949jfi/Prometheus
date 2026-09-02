"""Semantic-quarantine audit. Brief S1, amendment A2. Two layers; only the first is mechanical.

STRING LAYER (mechanical, fail-closed):
  1. Import allowlist over every module in proteus/foundry: only the listed stdlib modules and
     sibling foundry modules. No network, no subprocess, no ctypes, no pickle, no `random`
     (determinism), no third-party anything.
  2. Lexical scan of the two runtime files (vm.py, affordances.py) -- the only code a player's
     execution passes through -- for a banned vocabulary of cognition-shaped and human-ontology
     terms in identifiers, mnemonics and string literals. Docstrings are exempt (they are
     instrumentation prose outside the player) and the scan says so.
  3. Affordance-table identity: the table in memory must hash to the frozen published table.
  4. Type gate: every value that can enter a player (genome words, channel values, random draws)
     is a bounded integer; the audit runs a probe and asserts nothing else was ever on the tape.

ONTOLOGY LAYER (review gate, NOT mechanical): each opcode's category must be one of the ten
categories the external review allowed, and each mnemonic must be justifiable as a minimal
computational affordance. The audit prints the table for the reviewer; it cannot decide this.

Exit status is non-zero on any string-layer failure.
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOUNDRY = os.path.join(ROOT, "proteus", "foundry")
FROZEN_TABLE = os.path.join(ROOT, "proteus", "contracts", "affordance_table.v0.json")
sys.path.insert(0, ROOT)

ALLOWED_STDLIB = {"hashlib", "json", "time", "typing", "math", "struct", "collections",
                  "itertools", "os", "dataclasses", "__future__"}
FORBIDDEN_ANYWHERE = {"random", "socket", "urllib", "http", "subprocess", "ctypes", "pickle",
                      "importlib", "requests", "numpy", "torch", "transformers", "openai",
                      "anthropic", "tokenizers", "sentencepiece", "gensim", "sklearn"}

# Banned in identifiers / mnemonics / string literals of the RUNTIME files. Stems, lower-case.
BANNED_STEMS = ("search", "plan", "match", "attend", "attention", "analog", "strateg", "hierarch",
                "special", "communicat", "goal", "cause", "object", "enemy", "hypothes", "memory",
                "reason", "think", "learn", "believ", "intent", "agent", "cooperat", "decept",
                "predator", "prey", "compet", "reward", "fitness", "concept", "meaning")
RUNTIME_FILES = ("vm.py", "affordances.py")
ALLOWED_CATEGORIES = {"halt_yield", "read_write", "indirection", "arithmetic", "logical",
                      "comparison", "control", "opaque_io", "randomness"}


def _imports(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name.split(".")[0], node.lineno
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                yield ".", node.lineno
            elif node.module:
                yield node.module.split(".")[0], node.lineno


def check_imports() -> list:
    problems = []
    for fn in sorted(os.listdir(FOUNDRY)):
        if not fn.endswith(".py"):
            continue
        with open(os.path.join(FOUNDRY, fn), encoding="utf-8") as f:
            tree = ast.parse(f.read(), fn)
        for mod, line in _imports(tree):
            if mod == ".":
                continue
            if mod in FORBIDDEN_ANYWHERE:
                problems.append(f"{fn}:{line} forbidden import {mod}")
            elif mod not in ALLOWED_STDLIB:
                problems.append(f"{fn}:{line} import {mod} not on allowlist")
    return problems


def check_vocabulary() -> list:
    """Identifiers, attribute names and non-docstring string literals in the runtime files."""
    problems = []
    for fn in RUNTIME_FILES:
        path = os.path.join(FOUNDRY, fn)
        with open(path, encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src, fn)
        docstring_nodes = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if node.body and isinstance(node.body[0], ast.Expr) and \
                        isinstance(getattr(node.body[0], "value", None), ast.Constant) and \
                        isinstance(node.body[0].value.value, str):
                    docstring_nodes.add(id(node.body[0].value))
        names = set()
        strings = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add((node.id, node.lineno))
            elif isinstance(node, ast.Attribute):
                names.add((node.attr, node.lineno))
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                names.add((node.name, node.lineno))
            elif isinstance(node, ast.arg):
                names.add((node.arg, node.lineno))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if id(node) not in docstring_nodes:
                    strings.append((node.value, node.lineno))
        for ident, line in sorted(names):
            low = ident.lower()
            for stem in BANNED_STEMS:
                if stem in low:
                    problems.append(f"{fn}:{line} identifier '{ident}' contains banned stem '{stem}'")
        for s, line in strings:
            low = s.lower()
            for stem in BANNED_STEMS:
                if re.search(r"\b" + stem, low):
                    problems.append(f"{fn}:{line} string literal {s!r} contains banned stem '{stem}'")
        # comments are prose outside the player and are exempt, like docstrings; say so once
    return problems


def check_table() -> list:
    from proteus.foundry import affordances
    problems = []
    if not os.path.exists(FROZEN_TABLE):
        return [f"frozen table missing at {FROZEN_TABLE}; run publish first"]
    with open(FROZEN_TABLE, encoding="utf-8") as f:
        frozen = json.load(f)
    if frozen.get("affordance_hash") != affordances.AFFORDANCE_HASH:
        problems.append("affordance table in memory does not match the frozen published table")
    for row in affordances.TABLE:
        if row[2] not in ALLOWED_CATEGORIES:
            problems.append(f"opcode {row[0]} {row[1]} in category {row[2]} not among allowed categories")
        for stem in BANNED_STEMS:
            if stem in row[1].lower():
                problems.append(f"mnemonic {row[1]} contains banned stem {stem}")
    return problems


def check_types() -> list:
    from proteus.foundry import generate, probes
    fm = dict(generate.DEFAULT_FOUNDRY_MANIFEST)
    fm["seed"] = 7
    fm["n"] = 20
    pop = generate.generate(fm)
    pr = probes.build_probes()
    problems = []
    for o in pop:
        m = o["manifest"]
        if any((not isinstance(w, int)) or isinstance(w, bool) for w in m["genome"]):
            problems.append("non-integer genome word")
        from proteus.foundry.vm import Player
        from proteus.foundry.prng import SplitMix64
        p = Player(m)
        st = p.fresh_state()
        for probe in pr:
            rng = SplitMix64(probe["rnd_seed"])
            for t in range(probe["ticks"]):
                outs, status = p.run_tick(st, probe["inputs"][t], probe["n_out"], rng, None, 64)
                for ch in outs:
                    for v in ch:
                        if not isinstance(v, int) or not 0 <= v < (1 << 32):
                            problems.append("non-word output")
        if any((not isinstance(w, int)) or not 0 <= w < (1 << 32) for w in st["tape"]):
            problems.append("non-word on tape after execution")
    return problems


def main() -> int:
    from proteus.foundry import affordances
    sections = [("imports", check_imports()), ("vocabulary", check_vocabulary()),
                ("table", check_table()), ("types", check_types())]
    failed = False
    print("PROTEUS SEMANTIC-QUARANTINE AUDIT (string layer: mechanical; ontology layer: review)")
    for name, probs in sections:
        print(f"  [{'FAIL' if probs else 'PASS'}] {name}" + (f" ({len(probs)})" if probs else ""))
        for p in probs:
            print("        " + p)
        failed = failed or bool(probs)
    print("  exempt from the lexical scan by declaration: docstrings and comments (prose outside the player)")
    print()
    print("ONTOLOGY LAYER -- for the reviewer, not decided here. Affordance table",
          affordances.AFFORDANCE_HASH[:16] + "...")
    for row in affordances.TABLE:
        print(f"    {row[0]:>2} {row[1]:<6} {row[2]:<12} {row[3]:<8} {row[4]}")
    print("  question for review: which of these, if any, is already a theory of cognition?")
    print()
    print("STRING LAYER:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
