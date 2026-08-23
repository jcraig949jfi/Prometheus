"""Command line front end for prometheus_llm.

    python -m prometheus_llm.cli health
    python -m prometheus_llm.cli providers
    python -m prometheus_llm.cli models openrouter --free
    python -m prometheus_llm.cli ask openrouter:stealth/ox-alpha "explain X"
    python -m prometheus_llm.cli council "Is P=NP?" -t openrouter -t groq
"""

from __future__ import annotations

import argparse
import json
import sys

from .client import complete, council, health, list_models
from .registry import all_providers, get_spec


def _state(c) -> str:
    return "LIVE" if c.ok else ("EMPTY" if c.empty_content else "DEAD")


def cmd_health(args) -> int:
    res = health(args.providers or None, timeout=args.timeout)
    if args.json:
        print(json.dumps({k: v.to_dict() for k, v in res.items()}, indent=2,
                         default=str))
        return 0
    print(f"{'provider':<12} {'state':<6} {'lat':>7}  detail")
    print("-" * 100)
    for name, c in res.items():
        detail = (f"served={c.model_served} "
                  f"tok={c.prompt_tokens}/{c.completion_tokens}"
                  if c.ok else
                  f"status={c.status} {(c.error or '').strip()[:110]}")
        print(f"{name:<12} {_state(c):<6} {c.latency_s:>6.2f}s  {detail}")
    live = [n for n, c in res.items() if c.ok]
    print(f"\nLIVE {len(live)}/{len(res)}: {live}")
    return 0 if live else 1


def cmd_providers(args) -> int:
    for name in all_providers():
        s = get_spec(name)
        key = s.key_name or "-"
        print(f"{name:<12} kind={s.kind:<10} key={key:<11} "
              f"default={s.default_model or '(discover)'}")
        if s.notes:
            print(f"             {s.notes}")
    return 0


def cmd_models(args) -> int:
    rows = list_models(args.provider)
    if args.grep:
        rows = [m for m in rows if args.grep.lower() in str(m["id"]).lower()]
    if args.free:
        def _free(m):
            p = m.get("pricing") or {}
            return str(p.get("prompt")) in ("0", "0.0", "-1")
        rows = [m for m in rows if _free(m)]
    if args.json:
        print(json.dumps([{k: v for k, v in m.items() if k != "raw"}
                          for m in rows], indent=2, default=str))
        return 0
    print(f"{len(rows)} model(s) on {args.provider}:")
    for m in rows:
        ctx = f" ctx={m['ctx']}" if m.get("ctx") else ""
        print(f"  {m['id']}{ctx}")
    return 0


def cmd_ask(args) -> int:
    c = complete(args.prompt, target=args.target, system=args.system or "",
                 max_tokens=args.max_tokens, temperature=args.temperature,
                 fallback=args.fallback or None, timeout=args.timeout)
    if args.json:
        print(json.dumps(c.to_dict(), indent=2, default=str))
        return 0 if c.ok else 1
    if c.ok:
        print(c.text)
        if args.verbose:
            print(f"\n-- {c.summary()}", file=sys.stderr)
        return 0
    print(c.summary(), file=sys.stderr)
    return 1


def cmd_council(args) -> int:
    res = council(args.prompt, args.targets, max_tokens=args.max_tokens,
                  timeout=args.timeout)
    if args.json:
        print(json.dumps({k: v.to_dict() for k, v in res.items()}, indent=2,
                         default=str))
        return 0
    for name, c in res.items():
        print(f"\n===== {name} [{_state(c)}] {c.latency_s:.2f}s =====")
        print(c.text.strip() if c.ok else c.summary())
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="prometheus_llm", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=int, default=120)
    sub = ap.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("health", help="one real request per provider")
    h.add_argument("providers", nargs="*")
    h.set_defaults(func=cmd_health)

    p = sub.add_parser("providers", help="show the registry")
    p.set_defaults(func=cmd_providers)

    m = sub.add_parser("models", help="list a provider's catalog")
    m.add_argument("provider")
    m.add_argument("--grep")
    m.add_argument("--free", action="store_true")
    m.set_defaults(func=cmd_models)

    a = sub.add_parser("ask", help="one prompt to one target")
    a.add_argument("target")
    a.add_argument("prompt")
    a.add_argument("--system")
    a.add_argument("--max-tokens", type=int, default=4096)
    a.add_argument("--temperature", type=float, default=0.0)
    a.add_argument("-f", "--fallback", action="append")
    a.add_argument("-v", "--verbose", action="store_true")
    a.set_defaults(func=cmd_ask)

    c = sub.add_parser("council", help="same prompt to many targets")
    c.add_argument("prompt")
    c.add_argument("-t", "--targets", action="append", required=True)
    c.add_argument("--max-tokens", type=int, default=4096)
    c.set_defaults(func=cmd_council)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
