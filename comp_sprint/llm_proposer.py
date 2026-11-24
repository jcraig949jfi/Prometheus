"""Isolated Claude CLI proposer + deterministic Boolean-expression-to-XAG compiler.

Enforces strict scientific provenance:
  - Invokes `claude -p --model <alias> --output-format json --no-session-persistence --tools ""`
    from a clean scratch working directory so the model CANNOT read holdout files.
  - Verifies exact model identity from `modelUsage` (no silent fallback) and records
    exact USD spend (including rejected/malformed proposals) into `WorkMeter`.
  - Compiles proposed Boolean expressions (`&`, `|`, `^`, `~`, `x0..x3`) strictly via
    `StrashBuilder` into primitive `{AND, XOR}` gates (zero artificial gate discount).
"""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint.circuit import Macro, StrashBuilder, XAGCircuit, full_mask
from comp_sprint.library import RewriteRule, SearchStrategy, _compress_macro_exact


def compile_exprs_to_xag(
    n_inputs: int,
    exprs: Sequence[str],
) -> XAGCircuit:
    """Safely compile Python bitwise Boolean expressions over x0..x{n-1} into StrashBuilder XAG.

    Allowed AST nodes: Name (x0..x{n-1}), Constant (0, 1), UnaryOp (Invert ~),
    BinOp (BitAnd &, BitOr |, BitXor ^). No eval/exec, no arbitrary code.
    """
    if not (1 <= n_inputs <= 8):
        raise ValueError(f"n_inputs out of range: {n_inputs}")
    if not exprs:
        raise ValueError("exprs must be non-empty")

    builder = StrashBuilder(n_inputs)
    valid_names = {f"x{i}": (i, False) for i in range(n_inputs)}

    def emit(node: ast.AST) -> Tuple[int, bool]:
        if isinstance(node, ast.Name):
            if node.id not in valid_names:
                raise ValueError(f"Unknown variable {node.id!r} for n_inputs={n_inputs}")
            return valid_names[node.id]
        if isinstance(node, ast.Constant):
            if node.value in (0, False):
                return (-1, False)
            if node.value in (1, True):
                return (-1, True)
            raise ValueError(f"Unsupported constant: {node.value!r}")
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, (ast.Invert, ast.Not)):
                n, inv = emit(node.operand)
                return (n, not inv)
            raise ValueError(f"Unsupported unary op: {type(node.op).__name__}")
        if isinstance(node, ast.BinOp):
            ln, li = emit(node.left)
            rn, ri = emit(node.right)
            if isinstance(node.op, ast.BitAnd):
                return builder.add_gate("AND", ln, li, rn, ri)
            if isinstance(node.op, ast.BitXor):
                return builder.add_gate("XOR", ln, li, rn, ri)
            if isinstance(node.op, ast.BitOr):
                # a | b == ~(~a & ~b)
                n, inv = builder.add_gate("AND", ln, not li, rn, not ri)
                return (n, not inv)
            raise ValueError(f"Unsupported binary op: {type(node.op).__name__}")
        raise ValueError(f"Unsupported AST node: {type(node).__name__}")

    outs: List[Tuple[int, bool]] = []
    for raw in exprs:
        s = str(raw).strip()
        tree = ast.parse(s, mode="eval")
        outs.append(emit(tree.body))
    return builder.build(outs, prune_dead=True)


def extract_json_payload(text: str) -> Any:
    """Extract the top-level JSON object or array from an LLM reply (handles fenced blocks)."""
    s = text.strip()
    # Try fenced ```json ... ``` blocks first
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", s, flags=re.IGNORECASE)
    if m:
        candidate = m.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    # Fallback: direct parse or outermost {...} / [...]
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    for open_c, close_c in (("{", "}"), ("[", "]")):
        i = s.find(open_c)
        j = s.rfind(close_c)
        if i != -1 and j > i:
            try:
                return json.loads(s[i : j + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError(f"Could not parse JSON from model output: {s[:240]!r}")


def parse_proposed_macros(
    raw_text: str,
    origin: str,
    max_macros: int = 12,
    compress_exact: bool = True,
    meter: Optional[object] = None,
    compress_phase: str = "llm_compress",
) -> Tuple[List[Macro], List[Dict[str, str]]]:
    """Parse JSON macro proposals, verify exact XAG compilation, deduplicate, and optionally compress.

    Returns (accepted_macros, rejected_log).
    """
    payload = extract_json_payload(raw_text)
    items = payload["macros"] if isinstance(payload, dict) and "macros" in payload else payload
    if not isinstance(items, list):
        raise ValueError("Expected JSON list or {'macros': [...]} object")

    accepted: List[Macro] = []
    rejected: List[Dict[str, str]] = []
    seen_sigs = set()

    for idx, item in enumerate(items):
        name = str(item.get("name", f"{origin}_{idx}")) if isinstance(item, dict) else f"{origin}_{idx}"
        try:
            if not isinstance(item, dict):
                raise ValueError("item is not a dict")
            n_in = int(item["n_inputs"])
            if not (2 <= n_in <= 4):
                raise ValueError(f"n_inputs={n_in} outside [2, 4]")
            exprs = item.get("exprs")
            if not isinstance(exprs, list) or not (1 <= len(exprs) <= 3):
                raise ValueError("exprs must be a list of length 1..3")
            circ = compile_exprs_to_xag(n_in, exprs)
            if circ.gate_count() < 2 or circ.gate_count() > 10:
                raise ValueError(f"gate_count={circ.gate_count()} outside [2, 10]")
            mask = full_mask(n_in)
            tts = circ.truth_tables()
            if any(t in (0, mask) for t in tts):
                raise ValueError("contains trivial constant output")
            sig = (n_in, tts)
            if sig in seen_sigs:
                raise ValueError("duplicate semantic truth-table signature")
            seen_sigs.add(sig)
            m = Macro.from_circuit(name, circ, origin=origin)
            if compress_exact and len(m.outputs) <= 2:
                m = _compress_macro_exact(m, meter=meter, phase=compress_phase)
                # Preserve descriptive name prefix
                m = Macro(
                    name=name,
                    n_inputs=m.n_inputs,
                    gates=m.gates,
                    outputs=m.outputs,
                    truth_tables=m.truth_tables,
                    sha256=m.sha256,
                    origin=origin,
                )
            accepted.append(m)
            if len(accepted) >= max_macros:
                break
        except Exception as exc:
            rejected.append({"name": name, "reason": str(exc)})

    return accepted, rejected


def parse_proposed_artifact(
    raw_text: str,
    origin: str,
    max_macros: int = 20,
    max_rewrites: int = 8,
    compress_exact: bool = True,
    meter: Optional[object] = None,
    compress_phase: str = "llm_compress",
) -> Tuple[List[Macro], List[RewriteRule], SearchStrategy, List[Dict[str, str]]]:
    """Parse a full `(L, T, S)` JSON proposal: `macros`, `rewrites`, and `strategy`.

    Every macro is compiled & exact-compressed; every rewrite rule is mathematically verified
    (`lhs.truth_tables() == rhs.truth_tables()` and `rhs.gate_count() <= lhs.gate_count()`).
    Invalid/unsound items are logged in `rejected` rather than silently dropped.
    """
    payload = extract_json_payload(raw_text)
    if not isinstance(payload, dict):
        raise ValueError("Expected top-level JSON object with keys 'macros', optional 'rewrites', 'strategy'")

    # Parse macros using strict parser
    accepted_macros, rejected = parse_proposed_macros(
        json.dumps({"macros": payload.get("macros", [])}),
        origin=origin,
        max_macros=max_macros,
        compress_exact=compress_exact,
        meter=meter,
        compress_phase=compress_phase,
    )

    # Parse verified rewrite rules (lhs -> rhs)
    accepted_rewrites: List[RewriteRule] = []
    seen_rw_shas = set()
    for idx, item in enumerate(payload.get("rewrites", ())):
        rname = str(item.get("name", f"{origin}_rw_{idx}")) if isinstance(item, dict) else f"{origin}_rw_{idx}"
        try:
            if not isinstance(item, dict):
                raise ValueError("rewrite item is not a dict")
            n_in = int(item["n_inputs"])
            if not (2 <= n_in <= 4):
                raise ValueError(f"rewrite n_inputs={n_in} outside [2, 4]")
            lhs_e = item.get("lhs_exprs")
            rhs_e = item.get("rhs_exprs")
            if isinstance(lhs_e, str):
                lhs_e = [lhs_e]
            if isinstance(rhs_e, str):
                rhs_e = [rhs_e]
            if not isinstance(lhs_e, list) or not isinstance(rhs_e, list) or len(lhs_e) != len(rhs_e) or not (1 <= len(lhs_e) <= 2):
                raise ValueError("lhs_exprs/rhs_exprs must be equal-length lists of 1..2 expressions")
            lc = compile_exprs_to_xag(n_in, lhs_e)
            rc = compile_exprs_to_xag(n_in, rhs_e)
            rw = RewriteRule.from_circuits(rname, lc, rc, origin=origin)
            if rw.sha256 in seen_rw_shas:
                raise ValueError("duplicate rewrite rule")
            seen_rw_shas.add(rw.sha256)
            accepted_rewrites.append(rw)
            if len(accepted_rewrites) >= max_rewrites:
                break
        except Exception as exc:
            rejected.append({"name": f"rw:{rname}", "reason": str(exc)})

    strat = SearchStrategy.from_dict(payload.get("strategy") if isinstance(payload.get("strategy"), dict) else None)
    return accepted_macros, accepted_rewrites, strat, rejected


def call_claude_isolated(
    prompt: str,
    model: str = "opus",
    max_budget_usd: float = 2.0,
    timeout_sec: int = 180,
) -> Dict[str, Any]:
    """Run an isolated single-shot `claude -p` call with tools disabled and JSON usage telemetry."""
    with tempfile.TemporaryDirectory(prefix="prom_claude_iso_") as td:
        cmd = [
            "claude",
            "-p",
            "--model", model,
            "--output-format", "json",
            "--no-session-persistence",
            "--tools", "",
            "--max-budget-usd", str(max_budget_usd),
        ]
        # Strip any dead ANTHROPIC_API_KEY from env so subscription-billed `claude -p` uses its login,
        # unless the user explicitly sets PROMETHEUS_USE_API_KEY=1.
        env = dict(os.environ)
        if env.get("PROMETHEUS_USE_API_KEY") != "1":
            env.pop("ANTHROPIC_API_KEY", None)

        proc = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            cwd=td,
            env=env,
            timeout=timeout_sec,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"claude -p failed (rc={proc.returncode}): stderr={proc.stderr[:400]} stdout={proc.stdout[:400]}"
            )
        envelope = json.loads(proc.stdout)
        if envelope.get("is_error"):
            raise RuntimeError(f"claude -p returned is_error=True: {envelope.get('result')}")

        model_usage = envelope.get("modelUsage", {})
        models_used = sorted(model_usage.keys())
        in_tok = sum(int(v.get("inputTokens", 0)) for v in model_usage.values())
        out_tok = sum(int(v.get("outputTokens", 0)) for v in model_usage.values())
        cost_usd = float(envelope.get("total_cost_usd", 0.0))

        return {
            "text": str(envelope.get("result", "")),
            "cost_usd": cost_usd,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "models_used": models_used,
            "duration_ms": int(envelope.get("duration_ms", 0)),
        }
