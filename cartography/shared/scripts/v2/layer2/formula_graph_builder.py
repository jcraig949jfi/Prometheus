"""LaTeX → Operator Tree parser for formula embedding pipeline."""

import argparse
import hashlib
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

INPUT_PATH = Path("F:/Prometheus/cartography/convergence/data/openwebmath_formulas.jsonl")
OUTPUT_PATH = Path("F:/Prometheus/cartography/convergence/data/formula_trees.jsonl")

# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

# Commands that take two brace groups: \frac{A}{B}, \binom{A}{B}, \tbinom, \dbinom
TWO_ARG_CMDS = frozenset(["frac", "dfrac", "tfrac", "binom", "tbinom", "dbinom", "overset", "underset"])

# Commands that take one brace group: \sqrt{A}, \hat{A}, \bar{A}, ...
ONE_ARG_CMDS = frozenset([
    "sqrt", "hat", "bar", "tilde", "vec", "dot", "ddot", "overline", "underline",
    "widehat", "widetilde", "overbrace", "underbrace", "mathbb", "mathcal", "mathfrak",
    "mathrm", "mathbf", "mathit", "mathsf", "text", "textrm", "textbf", "textit",
    "boldsymbol", "operatorname", "pmod", "bmod", "not", "left", "right", "big",
    "Big", "bigg", "Bigg", "boxed",
])

# Named functions (trig, log, etc.)
FUNC_NAMES = frozenset([
    "sin", "cos", "tan", "cot", "sec", "csc",
    "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh",
    "log", "ln", "exp", "det", "dim", "ker", "deg",
    "min", "max", "inf", "sup", "lim", "liminf", "limsup",
    "gcd", "lcm", "mod", "arg", "hom", "Pr",
])

# Sum/product-like: take sub/superscript then a body
BIGOP_CMDS = frozenset(["sum", "prod", "coprod", "bigcup", "bigcap", "bigoplus", "bigotimes", "bigvee", "bigwedge"])

# Integral-like
INT_CMDS = frozenset(["int", "iint", "iiint", "oint", "intop"])

# Relation/binary operators mapped to node ops
RELATION_MAP = {
    "=": "eq", "\\neq": "neq", "\\ne": "neq", "<": "lt", ">": "gt",
    "\\leq": "leq", "\\geq": "geq", "\\le": "leq", "\\ge": "geq",
    "\\approx": "approx", "\\sim": "sim", "\\simeq": "simeq",
    "\\equiv": "equiv", "\\cong": "cong", "\\propto": "propto",
    "\\in": "in", "\\ni": "ni", "\\subset": "subset", "\\supset": "supset",
    "\\subseteq": "subseteq", "\\supseteq": "supseteq",
    "\\to": "to", "\\rightarrow": "to", "\\leftarrow": "from",
    "\\mapsto": "mapsto", "\\implies": "implies", "\\iff": "iff",
    "\\Rightarrow": "implies", "\\Leftarrow": "impliedby",
    "\\Leftrightarrow": "iff",
}

ADDITIVE_OPS = frozenset(["+", "-", "\\pm", "\\mp", "\\oplus", "\\ominus"])
MULT_OPS = frozenset(["\\cdot", "\\times", "\\otimes", "\\ast", "\\star", "\\circ", "*"])

# Tokens we skip (spacing, phantoms, formatting)
SKIP_CMDS = frozenset([
    "quad", "qquad", "hspace", "vspace", "phantom", "hphantom", "vphantom",
    "displaystyle", "textstyle", "scriptstyle", "scriptscriptstyle",
    "nonumber", "notag", "label", "tag", "hfill", "vfill",
    "kern", "mkern", "mskip", "hskip", "allowbreak",
    "!", ",", ":", ";", " ",  # thin/med/thick spaces
])

# Regex for tokenizing LaTeX
_TOKEN_RE = re.compile(
    r"(\\[a-zA-Z]+)"        # \command
    r"|(\\\{|\\\}|\\\\)"    # escaped braces or \\
    r"|(\\[^a-zA-Z\s])"     # \symbol (single char)
    r"|([{}()\[\]])"        # braces/parens/brackets
    r"|(\^|_)"              # super/subscript
    r"|(&)"                 # alignment
    r"|([0-9]+(?:\.[0-9]+)?)"  # numbers
    r"|([a-zA-Z])"          # single letter variable
    r"|([=<>+\-*/!|,;:.'])" # operators/punctuation
)


def tokenize(latex: str) -> list[str]:
    """Split LaTeX string into token list."""
    tokens = []
    for m in _TOKEN_RE.finditer(latex):
        tok = m.group()
        tokens.append(tok)
    return tokens


# ---------------------------------------------------------------------------
# Tree node
# ---------------------------------------------------------------------------

def node(typ: str, op: str = "", name: str = "", children: list | None = None) -> dict:
    n = {"type": typ}
    if op:
        n["op"] = op
    if name:
        n["name"] = name
    if children:
        n["children"] = children
    return n


def leaf_var(name: str) -> dict:
    return {"type": "variable", "name": name}


def leaf_num(val: str) -> dict:
    return {"type": "number", "value": val}


def unparsed_node(latex: str) -> dict:
    return {"type": "unparsed", "latex": latex[:200]}


# ---------------------------------------------------------------------------
# Recursive descent parser
# ---------------------------------------------------------------------------

class Parser:
    __slots__ = ("tokens", "pos", "n")

    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.pos = 0
        self.n = len(tokens)

    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < self.n else None

    def advance(self) -> str | None:
        if self.pos < self.n:
            t = self.tokens[self.pos]
            self.pos += 1
            return t
        return None

    def expect(self, tok: str) -> bool:
        if self.peek() == tok:
            self.advance()
            return True
        return False

    def parse_brace_group(self) -> dict:
        """Parse {content} and return tree of content."""
        if not self.expect("{"):
            # No brace group — parse single atom
            return self.parse_atom()
        children = []
        while self.pos < self.n and self.peek() != "}":
            saved = self.pos
            children.append(self.parse_relation())
            if self.pos == saved:
                self.advance()  # force progress
        self.expect("}")
        if not children:
            return leaf_var("")
        if len(children) == 1:
            return children[0]
        return node("group", children=children)

    def parse_atom(self) -> dict:
        """Parse a single atom (variable, number, command, or group)."""
        tok = self.peek()
        if tok is None:
            return leaf_var("")

        # Brace group
        if tok == "{":
            return self.parse_brace_group()

        # Parenthesized group or brackets
        if tok in ("(", "[", "\\(", "\\["):
            close = {"(": ")", "[": "]", "\\(": "\\)", "\\[": "\\]"}[tok]
            self.advance()
            children = []
            while self.pos < self.n and self.peek() != close:
                if self.peek() in (")", "]", "\\)", "\\]"):
                    break
                saved = self.pos
                children.append(self.parse_relation())
                if self.pos == saved:
                    self.advance()  # force progress
            self.expect(close)
            if len(children) == 1:
                return children[0]
            return node("group", op="paren", children=children) if children else leaf_var("")

        # Closing delimiters — don't consume, let caller handle
        if tok in (")", "]", "\\)", "\\]", "}"):
            return leaf_var("")

        # Skip alignment
        if tok == "&":
            self.advance()
            return leaf_var("")

        # Number
        if tok and tok[0].isdigit():
            self.advance()
            return leaf_num(tok)

        # Single letter variable
        if tok and len(tok) == 1 and tok.isalpha():
            self.advance()
            return leaf_var(tok)

        # Punctuation/operator as leaf
        if tok and len(tok) == 1 and tok in ",.;:!'|":
            self.advance()
            return leaf_var(tok)

        # LaTeX command
        if tok and tok.startswith("\\"):
            cmd = tok[1:]
            self.advance()

            # Skip commands
            if cmd in SKIP_CMDS:
                # Some take a brace arg — consume it
                if self.peek() == "{":
                    self.parse_brace_group()
                return self.parse_atom()  # skip and continue

            # \left, \right — skip delimiter, parse content
            if cmd in ("left", "right"):
                # consume the delimiter token
                if self.pos < self.n:
                    self.advance()
                if cmd == "left":
                    # parse until \right
                    children = []
                    while self.pos < self.n:
                        p = self.peek()
                        if p == "\\right":
                            self.advance()
                            if self.pos < self.n:
                                self.advance()  # delimiter
                            break
                        saved = self.pos
                        children.append(self.parse_relation())
                        if self.pos == saved:
                            self.advance()  # force progress
                    if len(children) == 1:
                        return children[0]
                    return node("group", op="paren", children=children) if children else leaf_var("")
                return self.parse_atom()

            # Two-arg commands
            if cmd in TWO_ARG_CMDS:
                a = self.parse_brace_group()
                b = self.parse_brace_group()
                return node("operator", op=cmd, children=[a, b])

            # One-arg commands
            if cmd in ONE_ARG_CMDS:
                a = self.parse_brace_group()
                # For text/mathrm etc, flatten to leaf
                if cmd in ("text", "textrm", "textbf", "textit", "mathrm", "operatorname"):
                    name = self._flatten_name(a)
                    return leaf_var(name)
                return node("operator", op=cmd, children=[a])

            # sqrt with optional [n]
            if cmd == "sqrt":
                if self.peek() == "[":
                    self.advance()
                    # parse until ]
                    idx_children = []
                    while self.pos < self.n and self.peek() != "]":
                        idx_children.append(self.parse_relation())
                    self.expect("]")
                    body = self.parse_brace_group()
                    idx = idx_children[0] if idx_children else leaf_num("2")
                    return node("operator", op="root", children=[body, idx])
                body = self.parse_brace_group()
                return node("operator", op="sqrt", children=[body])

            # Big operators (sum, prod, ...)
            if cmd in BIGOP_CMDS:
                return self._parse_bigop(cmd)

            # Integrals
            if cmd in INT_CMDS:
                return self._parse_bigop(cmd)

            # Named functions
            if cmd in FUNC_NAMES:
                return self._parse_func(cmd)

            # Relation operators
            full = "\\" + cmd
            if full in RELATION_MAP:
                return node("relation", op=RELATION_MAP[full])

            # Greek letters & other symbols → variable
            return leaf_var(cmd)

        # Fallback: consume and make leaf
        self.advance()
        return leaf_var(tok or "")

    def _parse_bigop(self, cmd: str) -> dict:
        """Parse sum/int with optional sub/superscript bounds, then body."""
        children = []
        lo = hi = None
        # Check for _ and ^
        for _ in range(2):
            if self.peek() == "_":
                self.advance()
                lo = self.parse_brace_group()
            elif self.peek() == "^":
                self.advance()
                hi = self.parse_brace_group()
        children.append(lo or leaf_var(""))
        children.append(hi or leaf_var(""))
        # Body: parse one "term" (up to next relation/additive at same level)
        body = self.parse_term()
        children.append(body)
        return node("operator", op=cmd, children=children)

    def _parse_func(self, cmd: str) -> dict:
        """Parse function like \sin, \log with optional argument."""
        # Check for ^ (e.g. \sin^2)
        exp = None
        if self.peek() == "^":
            self.advance()
            exp = self.parse_brace_group()
        # Check for argument in parens or brace
        if self.peek() in ("(", "{", "\\("):
            arg = self.parse_atom()
        else:
            # Next atom is the argument
            arg = self.parse_unary()
        result = node("operator", op=cmd, children=[arg])
        if exp:
            result = node("operator", op="power", children=[result, exp])
        return result

    def _flatten_name(self, n: dict) -> str:
        """Extract text name from a parsed node."""
        if n.get("name"):
            return n["name"]
        if n.get("value"):
            return n["value"]
        if "children" in n:
            return "".join(self._flatten_name(c) for c in n["children"])
        return ""

    def parse_unary(self) -> dict:
        """Parse atom with optional superscript/subscript."""
        # Handle unary minus
        if self.peek() == "-":
            self.advance()
            operand = self.parse_unary()
            return node("operator", op="neg", children=[operand])

        base = self.parse_atom()

        # Post-fix: factorial
        while self.peek() == "!":
            self.advance()
            base = node("operator", op="factorial", children=[base])

        # Post-fix: prime/apostrophe
        while self.peek() == "'":
            self.advance()
            base = node("operator", op="prime", children=[base])

        # Super/subscript chains
        while self.peek() in ("^", "_"):
            op = self.advance()
            arg = self.parse_brace_group()
            if op == "^":
                base = node("operator", op="power", children=[base, arg])
            else:
                base = node("operator", op="subscript", children=[base, arg])
        return base

    def parse_term(self) -> dict:
        """Parse a multiplicative term (juxtaposition = implicit multiply)."""
        factors = [self.parse_unary()]
        while self.pos < self.n:
            tok = self.peek()
            if tok is None:
                break
            # Explicit multiply
            if tok in MULT_OPS:
                self.advance()
                factors.append(self.parse_unary())
                continue
            # Stop at relation, additive, closing, alignment
            if (tok in RELATION_MAP or tok in ("=", "<", ">")
                    or tok in ADDITIVE_OPS
                    or tok in ("}", ")", "]", "\\)", "\\]", "&", "\\\\")
                    or tok == ","
                    or (tok.startswith("\\") and ("\\" + tok[1:]) in RELATION_MAP)):
                break
            # Juxtaposition = implicit multiply
            saved = self.pos
            factors.append(self.parse_unary())
            if self.pos == saved:
                self.advance()  # force progress
        if len(factors) == 1:
            return factors[0]
        return node("operator", op="multiply", children=factors)

    def parse_expr(self) -> dict:
        """Parse additive expression."""
        terms = [self.parse_term()]
        while self.pos < self.n and self.peek() in ADDITIVE_OPS:
            op = self.advance()
            right = self.parse_term()
            terms.append(node("operator", op="add" if op == "+" else "sub", children=[terms.pop(), right]) if len(terms) == 1 and op in ("+", "-") else right)
            # Simplified: just collect terms under add/sub
        if len(terms) == 1:
            return terms[0]
        return node("operator", op="add", children=terms)

    def parse_relation(self) -> dict:
        """Parse relation (equation/inequality)."""
        left = self.parse_expr()
        tok = self.peek()
        if tok is None:
            return left

        # Check for relation
        op_name = None
        if tok in ("=", "<", ">"):
            op_name = RELATION_MAP.get(tok, tok)
            self.advance()
        elif tok and tok.startswith("\\"):
            full = tok
            if full in RELATION_MAP:
                op_name = RELATION_MAP[full]
                self.advance()

        if op_name:
            right = self.parse_expr()
            result = node("equation", op=op_name, children=[left, right])
            # Chain: a = b = c
            while True:
                tok2 = self.peek()
                op2 = None
                if tok2 in ("=", "<", ">"):
                    op2 = RELATION_MAP.get(tok2, tok2)
                    self.advance()
                elif tok2 and tok2.startswith("\\") and tok2 in RELATION_MAP:
                    op2 = RELATION_MAP[tok2]
                    self.advance()
                if op2:
                    right2 = self.parse_expr()
                    result = node("equation", op=op2, children=[result, right2])
                else:
                    break
            return result
        return left

    def parse_full(self) -> dict:
        """Parse entire token stream."""
        parts = []
        while self.pos < self.n:
            tok = self.peek()
            if tok == "\\\\":
                self.advance()
                continue
            parts.append(self.parse_relation())
            # Safety: if we didn't advance, force advance to avoid infinite loop
            if self.pos < self.n and self.peek() == tok:
                self.advance()
        if not parts:
            return leaf_var("")
        if len(parts) == 1:
            return parts[0]
        return node("sequence", children=parts)


# ---------------------------------------------------------------------------
# Tree statistics
# ---------------------------------------------------------------------------

def tree_stats(root: dict) -> tuple[int, int, int, int]:
    """Return (depth, n_nodes, n_operators, n_variables)."""
    if not root:
        return 0, 0, 0, 0
    depth = 0
    n_nodes = 1
    n_ops = 1 if root.get("type") in ("operator", "equation") else 0
    n_vars = 1 if root.get("type") == "variable" else 0
    for child in root.get("children", []):
        d, nn, no, nv = tree_stats(child)
        depth = max(depth, d)
        n_nodes += nn
        n_ops += no
        n_vars += nv
    return depth + 1, n_nodes, n_ops, n_vars


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_latex_to_tree(latex_str: str) -> dict:
    """Parse a LaTeX formula string into an operator tree."""
    if not latex_str or not latex_str.strip():
        return unparsed_node(latex_str or "")

    try:
        tokens = tokenize(latex_str)
        if not tokens:
            return unparsed_node(latex_str)
        parser = Parser(tokens)
        tree = parser.parse_full()
        return tree
    except (RecursionError, IndexError, KeyError, ValueError):
        return unparsed_node(latex_str)


def process_formula(line: str) -> str | None:
    """Process one JSONL line → output JSONL line."""
    try:
        rec = json.loads(line)
    except json.JSONDecodeError:
        return None
    latex = rec.get("latex", "")
    h = rec.get("hash", hashlib.md5(latex.encode()).hexdigest()[:12])
    root = parse_latex_to_tree(latex)
    depth, n_nodes, n_ops, n_vars = tree_stats(root)
    out = {
        "hash": h,
        "root": root,
        "depth": depth,
        "n_nodes": n_nodes,
        "n_operators": n_ops,
        "n_variables": n_vars,
    }
    return json.dumps(out, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LaTeX → Operator Tree parser")
    parser.add_argument("--max-formulas", type=int, default=0, help="0=all")
    parser.add_argument("--sample", action="store_true", help="10K random sample with stats")
    parser.add_argument("--input", type=str, default=str(INPUT_PATH))
    parser.add_argument("--output", type=str, default=str(OUTPUT_PATH))
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    # Sample mode: read all lines, pick 10K random, report stats
    if args.sample:
        import random
        print("Reading input for sampling...")
        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        total = len(lines)
        sample_size = min(10000, total)
        sample = random.sample(lines, sample_size)
        print(f"Sampled {sample_size} from {total:,} formulas")

        depths = []
        op_counts = Counter()
        n_parsed = 0
        n_unparsed = 0
        t0 = time.perf_counter()

        for line in sample:
            rec = json.loads(line)
            latex = rec.get("latex", "")
            root = parse_latex_to_tree(latex)
            if root.get("type") == "unparsed":
                n_unparsed += 1
            else:
                n_parsed += 1
            depth, n_nodes, n_ops, n_vars = tree_stats(root)
            depths.append(depth)
            _count_ops(root, op_counts)

        elapsed = time.perf_counter() - t0
        rate = sample_size / elapsed

        print(f"\n=== Sample Statistics ({sample_size:,} formulas) ===")
        print(f"Parse success: {n_parsed}/{sample_size} ({100*n_parsed/sample_size:.1f}%)")
        print(f"Parse failures: {n_unparsed}/{sample_size} ({100*n_unparsed/sample_size:.1f}%)")
        print(f"Speed: {rate:,.0f} formulas/sec")
        print(f"\nDepth distribution:")
        depth_ctr = Counter(depths)
        for d in sorted(depth_ctr):
            print(f"  depth {d}: {depth_ctr[d]} ({100*depth_ctr[d]/sample_size:.1f}%)")
        print(f"\nTop 20 operators:")
        for op, cnt in op_counts.most_common(20):
            print(f"  {op}: {cnt}")
        return

    # Full processing mode
    limit = args.max_formulas if args.max_formulas > 0 else float("inf")
    t0 = time.perf_counter()
    n_total = 0
    n_parsed = 0
    n_unparsed = 0

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            if n_total >= limit:
                break
            result = process_formula(line)
            if result:
                fout.write(result + "\n")
                if '"type":"unparsed"' in result[:100]:
                    n_unparsed += 1
                else:
                    n_parsed += 1
            n_total += 1
            if n_total % 100_000 == 0:
                elapsed = time.perf_counter() - t0
                rate = n_total / elapsed
                pct = 100 * n_parsed / n_total if n_total else 0
                print(f"  {n_total:>10,} formulas | {rate:,.0f}/sec | {pct:.1f}% parsed")

    elapsed = time.perf_counter() - t0
    rate = n_total / elapsed if elapsed > 0 else 0
    print(f"\nDone: {n_total:,} formulas in {elapsed:.1f}s ({rate:,.0f}/sec)")
    print(f"Parsed: {n_parsed:,} ({100*n_parsed/n_total:.1f}%)")
    print(f"Unparsed: {n_unparsed:,} ({100*n_unparsed/n_total:.1f}%)")
    print(f"Output: {output_path}")


def _count_ops(node: dict, counter: Counter):
    """Recursively count operator types."""
    if node.get("type") in ("operator", "equation") and node.get("op"):
        counter[node["op"]] += 1
    for child in node.get("children", []):
        _count_ops(child, counter)


if __name__ == "__main__":
    main()
