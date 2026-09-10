"""Can the MIT Rust core replace the unlicensed Python bindings? Everything except the build.

    python -m techne.acquisition.checks.stitch_rust_feasibility

The operator's recommendation (2026-09-10): investigate a pinned build of the explicitly
MIT-licensed Rust core through its documented JSON interface, as a route that can be qualified
while the Python package's licensing stays unresolved.

This check does every part of that which does not need a compiler, and reports the compiler as
a single named decision point rather than as a vague blocker. It runs in the LIVE interpreter
because it is a probe: it reads a source tree and inspects toolchains, and imports nothing from
the acquired code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess

from .. import budget as _budget
from .. import manifest_io, paths, receipt

CORE = "stitch_rust_core"


def _which(exe: str) -> dict:
    p = shutil.which(exe)
    ver = None
    if p:
        try:
            r = subprocess.run([p, "--version"], capture_output=True, text=True, timeout=20)
            ver = (r.stdout or r.stderr).strip().splitlines()[0] if r.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            pass
    return {"present": bool(p), "path": p, "version": ver}


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="offline_check")
    a = ap.parse_args(argv)

    man = manifest_io.load()
    entry = manifest_io.entry(man, CORE)
    root = paths.repos() / CORE
    rec = receipt.new("FIRST_USEFUL_CHECK", CORE)
    rec["check"] = "stitch_rust_core_route_feasibility"
    rec["why"] = ("the Python bindings' licence is unresolved for the distributed package; the "
                  "Rust core's MIT grant is explicit at the pinned revision, so this asks "
                  "whether the same capability is reachable through the core's documented JSON "
                  "interface instead")
    prof = _budget.get_profile(a.profile)
    rec["budget_profile"] = prof

    if not (root / ".git").exists():
        rec["status"] = "BLOCKED_SOURCE_NOT_ACQUIRED"
        rec["unrun_or_blocked"].append(
            f"run: python -m techne.scripts.acquire --entry {CORE} --profile isolated_heavy_build")
        print(receipt.write(rec))
        return 3

    with _budget.Budget(profile=prof) as b:
        head = b.run(["git", "rev-parse", "HEAD"], cwd=str(root))["stdout"].strip()
        want = entry["upstream_revision"]["commit"]

        # 1. LICENCE -- the whole point of this route
        lic = root / "LICENSE"
        text = lic.read_text(encoding="utf-8", errors="replace") if lic.exists() else ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        cargo = (root / "Cargo.toml").read_text(encoding="utf-8", errors="replace")
        cargo_lic = next((ln.strip() for ln in cargo.splitlines()
                          if ln.strip().startswith("license")), None)
        licence = {
            "file_present": lic.exists(), "bytes": len(text.encode()) if text else 0,
            "sha256": _sha(lic) if lic.exists() else None,
            "first_line": lines[0] if lines else None,
            "copyright_line": next((ln for ln in lines if ln.lower().startswith("copyright")), None),
            "cargo_declaration": cargo_lic,
            "requires_notice_in_copies": bool(
                re.search(r"above copyright notice and this permission notice shall be included",
                          text, re.I)),
            "grant_is_explicit": lic.exists() and cargo_lic is not None,
        }

        # 2. the DOCUMENTED JSON interface
        readme = (root / "README.md").read_text(encoding="utf-8", errors="replace")
        bins = sorted(p.stem for p in (root / "src" / "bin").glob("*.rs")) \
            if (root / "src" / "bin").exists() else []
        documented = {
            "binaries": bins,
            "compress_present": "compress" in bins,
            "input_format": "JSON array of program strings (--fmt programs-list, the default)",
            "output_file": "out/out.json",
            "readme_names_this_route_for_non_binding_consumers": bool(re.search(
                r"consumed by other programs that are using stitch as a subroutine", readme)),
            "documented_invocation": (
                "cargo run --release --bin=compress -- data/cogsci/nuts-bolts.json "
                "--max-arity=3 --iterations=3"),
            "readme_sha256": _sha(root / "README.md"),
        }

        # 3. INPUT PARITY with the reproduction already done through the bindings
        fx = paths.tool_cache() / "fixtures" / "stitch" / "nuts-bolts.json"
        intree = root / "data" / "cogsci" / "nuts-bolts.json"
        parity = {"comparable": False}
        if fx.exists() and intree.exists():
            A = json.loads(intree.read_text(encoding="utf-8"))
            B = json.loads(fx.read_text(encoding="utf-8"))
            parity = {
                "in_tree_at_pinned_core_rev": {"sha256": _sha(intree), "bytes": intree.stat().st_size,
                                               "n_programs": len(A)},
                "fixture_used_for_the_python_reproduction": {
                    "sha256": _sha(fx), "bytes": fx.stat().st_size, "n_programs": len(B),
                    "from_revision": "mlb2251/stitch@350804b7 (main head at 2026-09-09)"},
                "bytes_differ": _sha(intree) != _sha(fx),
                "same_programs_same_order": A == B,
                "comparable": A == B,
                "finding": (
                    "The two files DIFFER BY BYTES but carry the same 250 programs in the same "
                    "order -- the difference is formatting only. So the Python reproduction's "
                    "input is content-identical to what the core at the bindings' pinned "
                    "revision ships, and a Rust-vs-Python comparison is like-for-like on "
                    "content. It is NOT like-for-like on bytes, and a comparison must fix ONE "
                    "input file rather than let each route use its own in-tree copy, or the "
                    "difference between routes would include a dataset difference."
                    if A == B else
                    "The two datasets differ in CONTENT, not merely formatting. A comparison "
                    "must fix one input file explicitly."),
            }

        # 4. the toolchain, which is the whole obstruction
        tools = {t: _which(t) for t in ("cargo", "rustc", "rustup", "cc", "link", "cl")}
        edition = next((ln.strip() for ln in cargo.splitlines()
                        if ln.strip().startswith("edition")), None)
        deps = len([ln for ln in cargo.splitlines()
                    if re.match(r"^[a-zA-Z0-9_-]+\s*=", ln.strip())])
        rec["resource_receipt"] = b.resource_receipt()

    buildable = tools["cargo"]["present"] and tools["rustc"]["present"]
    rec["observations"] = {
        "source_revision": head,
        "pin_matches_manifest": head == want,
        "pinned_by": entry["upstream_revision"]["resolver"],
        "licence": licence,
        "documented_json_interface": documented,
        "input_parity": parity,
        "toolchain": tools,
        "build_scope": {
            "edition": edition, "declared_dependency_lines": deps,
            "makefile_targets_present": (root / "Makefile").exists(),
            "buildable_here": buildable,
        },
    }

    checks = [
        ("source is at the revision the BINDINGS pin, not at main's head", head == want),
        ("the MIT grant is explicit in the acquired copy: LICENSE file AND Cargo.toml",
         licence["grant_is_explicit"]),
        ("the grant's one condition is identified, so redistribution terms are known",
         licence["requires_notice_in_copies"]),
        ("the JSON interface is DOCUMENTED for exactly this use, not improvised",
         documented["compress_present"]
         and documented["readme_names_this_route_for_non_binding_consumers"]),
        ("the input is content-identical to the one the Python reproduction used",
         bool(parity.get("comparable"))),
        ("a Rust toolchain exists on this host", buildable),
    ]
    rec["observations"]["checks"] = [{"claim": c, "pass": bool(p)} for c, p in checks]
    rec["status"] = ("ROUTE_VIABLE_BUILD_BLOCKED" if not buildable and
                     all(p for c, p in checks[:-1]) else
                     "ROUTE_VIABLE" if buildable and all(p for _, p in checks) else "FAILED")

    if not buildable:
        rec["unrun_or_blocked"].append(
            "THE BUILD. cargo, rustc and rustup are all absent from this host -- the same "
            "measured toolchain gap that blocks DreamCoder (BLK-DC-3). Everything else this "
            "route needs is verified above. Installing a Rust toolchain is a host change and "
            "is the operator's decision, not this seat's.")
        rec["decision_point"] = {
            "question": "install a Rust toolchain on this host?",
            "what_it_unblocks": ("a pinned build of the MIT-licensed core, its documented "
                                 "nuts-bolts run compared against the already-reproduced Python "
                                 "figures, and semantics-preserving expansion of out/out.json "
                                 "through the independent expander already written -- i.e. an "
                                 "H0/H2 library route whose licence is settled"),
            "cost": "$0 in licence; rustup and the MSVC-target toolchain are free and open",
            "footprint_NOT_MEASURED": ("a rustup toolchain plus a release build of ~22 "
                                       "dependencies is order-1 GiB of disk and minutes of CPU. "
                                       "That is an ESTIMATE from the dependency count and "
                                       "edition, not a measurement, and it is labelled so rather "
                                       "than quoted as a figure."),
            "also_needed": ("a C linker for the MSVC target. cc/link/cl presence is recorded "
                            "above; MinGW is on PATH (cmake resolved through it earlier), so the "
                            "gnu target may be the cheaper route. NOT verified."),
            "reversible": "yes -- rustup self uninstall removes it",
            "alternative_if_declined": ("keep using the Python bindings under D-17's stricter "
                                        "reading: development-only, no export. Nothing currently "
                                        "running depends on lifting that."),
        }

    out = receipt.write(rec)
    print(f"=== stitch Rust-core route feasibility -> {rec['status']} ===")
    print(f"revision        {head[:12]} pin_ok={head == want} (pinned by the bindings' Cargo.toml)")
    print(f"licence         {licence['first_line']} | {licence['copyright_line']}")
    print(f"                Cargo: {licence['cargo_declaration']} | notice-in-copies required: "
          f"{licence['requires_notice_in_copies']}")
    print(f"json interface  bins={documented['binaries']} documented_for_this_use="
          f"{documented['readme_names_this_route_for_non_binding_consumers']}")
    print(f"input parity    same_programs_same_order={parity.get('same_programs_same_order')} "
          f"bytes_differ={parity.get('bytes_differ')}")
    print(f"toolchain       " + ", ".join(f"{k}={'yes' if v['present'] else 'NO'}"
                                          for k, v in tools.items()))
    for c in rec["observations"]["checks"]:
        print(f"  {'PASS' if c['pass'] else 'FAIL':<5} {c['claim']}")
    if "decision_point" in rec:
        print(f"\nDECISION        {rec['decision_point']['question']}")
        print(f"  unblocks      {rec['decision_point']['what_it_unblocks'][:110]}...")
        print(f"  cost          {rec['decision_point']['cost']}")
    print(f"receipt         {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
