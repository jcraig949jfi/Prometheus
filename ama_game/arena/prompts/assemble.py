#!/usr/bin/env python3
"""Assemble an AMA player prompt from frozen parts.

A prompt is exactly three blocks concatenated in this order:

    00_COMMON_PREAMBLE.md   condition-invariant, role-invariant
    ROLE_<ROLE>.md          condition-invariant, role-specific
    CONTEXT_<COND>_*.md     the ONLY block that varies by condition

The point of assembling rather than hand-writing is that parity between
experimental conditions becomes checkable instead of asserted.  `--parity-check`
hashes the condition-invariant portion of every (role, condition) pair; if the
hash for a role is not identical across A/B/C/D, condition A0 and condition D
differed by something other than graph information and the navigation comparison
is void.

Stdlib only.  All paths resolve relative to this file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent

ROLES = {
    "RED": "ROLE_RED.md",
    "BLUE": "ROLE_BLUE.md",
    "PURPLE": "ROLE_PURPLE.md",
    "ASSESSOR": "ROLE_ASSESSOR.md",
}

CONTEXTS = {
    "A": "CONTEXT_A_problem_only.md",
    "B": "CONTEXT_B_generic.md",
    "C": "CONTEXT_C_nearest_failures.md",
    "D": "CONTEXT_D_graph_state.md",
}

PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8")


def substitute(text: str, values: dict) -> tuple[str, list[str]]:
    """Replace {{KEY}} with values[KEY]. Return (text, unfilled_keys)."""
    unfilled: list[str] = []

    def repl(m: re.Match) -> str:
        key = m.group(1)
        if key in values:
            return str(values[key])
        unfilled.append(key)
        return m.group(0)

    return PLACEHOLDER.sub(repl, text), unfilled


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def invariant_block(role: str, values: dict) -> str:
    """Common preamble + role block, after budget substitution only.

    This is what must be byte-identical across conditions for a given role.
    """
    budget = {k: v for k, v in values.items() if k.startswith("BUDGET_")}
    common, _ = substitute(read("00_COMMON_PREAMBLE.md"), budget)
    role_text, _ = substitute(read(ROLES[role]), budget)
    return common + "\n\n---\n\n" + role_text


def load_budget() -> dict:
    raw = json.loads(read("budget.json"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def cmd_assemble(args: argparse.Namespace) -> int:
    role = args.role.upper()
    cond = args.condition.upper()
    if role not in ROLES:
        print(f"unknown role: {role}", file=sys.stderr)
        return 2
    if cond not in CONTEXTS:
        print(f"unknown condition: {cond}", file=sys.stderr)
        return 2

    values = load_budget()
    if args.vars:
        values.update(json.loads(Path(args.vars).read_text(encoding="utf-8")))
    values.setdefault("CONDITION", cond)

    invariant = invariant_block(role, values)
    context_raw = read(CONTEXTS[cond])

    body, unfilled_inv = substitute(invariant, values)
    context, unfilled_ctx = substitute(context_raw, values)
    prompt = body + "\n\n---\n\n" + context

    unfilled = sorted(set(unfilled_inv + unfilled_ctx))
    if unfilled and not args.allow_unfilled:
        print("unfilled placeholders (pass --allow-unfilled to override):",
              file=sys.stderr)
        for key in unfilled:
            print(f"  {{{{{key}}}}}", file=sys.stderr)
        return 1

    manifest = {
        "protocol_version": values.get("protocol_version"),
        "role": role,
        "condition": cond,
        "invariant_sha256": sha256(invariant),
        "context_sha256": sha256(context),
        "prompt_sha256": sha256(prompt),
        "prompt_chars": len(prompt),
        "context_chars": len(context),
        "unfilled_placeholders": unfilled,
        "budget": {k: v for k, v in values.items() if k.startswith("BUDGET_")},
    }

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(prompt, encoding="utf-8")
        out.with_suffix(out.suffix + ".manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(manifest, indent=2))
    else:
        sys.stdout.write(prompt)
    return 0


def cmd_parity_check(args: argparse.Namespace) -> int:
    """Verify the condition-invariant block really is condition-invariant."""
    values = load_budget()
    ok = True
    print(f"protocol_version: {values.get('protocol_version')}")
    print(f"budget: {json.dumps({k: v for k, v in values.items() if k.startswith('BUDGET_')})}")
    print()
    for role in ROLES:
        hashes = {c: sha256(invariant_block(role, values)) for c in CONTEXTS}
        distinct = set(hashes.values())
        status = "OK  " if len(distinct) == 1 else "FAIL"
        if len(distinct) != 1:
            ok = False
        print(f"[{status}] {role:<9} invariant_sha256={sorted(distinct)[0][:16]}"
              f"  distinct_across_conditions={len(distinct)}")

    print()
    caps = []
    for cond in ("C", "D"):
        caps.append(len(read(CONTEXTS[cond])))
    print(f"context template sizes (chars): C={caps[0]} D={caps[1]}")
    print(f"CONTEXT_TOKEN_CAP={values.get('CONTEXT_TOKEN_CAP')} "
          f"(enforced by the packer, not by this script)")
    print()
    print("PASS" if ok else "FAIL: invariant block is not condition-invariant")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("assemble", help="emit one assembled prompt")
    a.add_argument("--role", required=True, choices=sorted(ROLES) + [r.lower() for r in ROLES])
    a.add_argument("--condition", required=True,
                   choices=sorted(CONTEXTS) + [c.lower() for c in CONTEXTS])
    a.add_argument("--vars", help="JSON file of placeholder values")
    a.add_argument("--out", help="write prompt here; manifest alongside")
    a.add_argument("--allow-unfilled", action="store_true")
    a.set_defaults(func=cmd_assemble)

    c = sub.add_parser("parity-check", help="hash the invariant block per role")
    c.set_defaults(func=cmd_parity_check)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
