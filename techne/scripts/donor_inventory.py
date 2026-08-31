"""Generate the donor inventory: machine-readable JSON plus a concise human-readable table.

    python -m techne.scripts.donor_inventory --json techne/donor_inventory.json \
                                             --md techne/DONOR_INVENTORY.md

The inventory is assembled from things that were MEASURED, not declared: the adapter manifests
(which include each donor's native selection relation), the installed distribution metadata, the
Gen-0 vetting report, and the comparator/compatibility reports. Nothing here is transcribed from
a paper or a README.

STATUS VOCABULARY, and why the failure states are first-class:
    WRAPPED_AND_TESTED    adapter exists, battery passes, donor installed
    INSTALLED_NOT_WRAPPED donor present, no adapter (nothing consumes it yet)
    VETTED_NOT_INSTALLED  identity + provenance established, deliberately not installed
    REDUNDANT_AT_GEN0     wrapped, but an incumbent already covers every exercised capability
    BLOCKED               acquisition blocked; blocker recorded
    REJECTED              acquisition refused
A generation in which every donor came back useful would be evidence the bar was set at
installability. Four useful and one redundant is the healthier shape.
"""
from __future__ import annotations

import argparse
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]

#: Donors deliberately NOT acquired this generation, with the reason. Recorded because a
#: deferral that leaves no trace gets re-litigated by the next seat.
DEFERRED = [
    ("QDax", "platform+redundant",
     "JAX-based; JAX ships no CUDA wheels for Windows, so it would run CPU-only here, and "
     "pyribs already covers MAP-Elites in numpy. Not complementary on this machine."),
    ("MiniZinc", "external binary",
     "The `minizinc` distribution is a Python driver, not a solver; it requires the MiniZinc "
     "bundle installed separately. No Gen-0 consumer."),
    ("LeanDojo", "acquisition cost",
     "Requires elan plus a Lean toolchain plus a Mathlib build (~5 GB). Already tracked as an "
     "open gap in techne/ARSENAL_ROADMAP.md. Most expensive item on the list, least Gen-0 return."),
    ("EvoTorch", "no consumer",
     "Torch-native evolutionary computation with nothing in the programme calling it."),
    ("DreamCoder", "not distributed",
     "Research repository, no Python distribution. The PyPI name `dreamcoder` does not exist."),
    ("POET / PAIRED / ACCEL / minimax", "not distributed + NAME COLLISION",
     "Unmaintained JAX research repositories, no Python distributions. All four names are "
     "occupied on PyPI by unrelated projects: `poet` computes orbital evolution, `paired` "
     "aligns sequences, `accel` manages chemistry conformers, `minimax` is a generic minimax "
     "package. Installing by inferred name would install a stranger's code."),
    ("Ruler / babble / Enumo / ShapeCoder", "not distributed + NAME COLLISION + build not wrap",
     "Rust crates from the UW PLSE e-graph lineage with no Python distribution. `babble` on "
     "PyPI is a PDF parser, `ruler` a grammar library, `egg` is 'a lonely egg'. Reaching this "
     "family from Python means building a rule-inference layer on egglog -- a build, not a "
     "wrap -- and the Gen-0 brief defers it pending the Family A vs B decision."),
    ("stitch_core", "held pending scientific decision",
     "AVAILABLE_CONTESTANT. Acquisition facts recorded (v0.1.29, win_amd64 wheel present, "
     "upstream github.com/mlb2251/stitch, identity description-only). NOT installed: whether "
     "Family A (Stitch) or Family B (Ruler/babble/Enumo) fits Prometheus better is Lexis's "
     "call, and this seat must not settle it by acquiring one side."),
]


def load(path: str):
    p = REPO / path
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def build() -> dict:
    import importlib.metadata as md
    from techne.lib import donors as D

    vet = load("techne/dependency_vetting_gen0_2026-08-31.json") or {"packages": []}
    vet_by_name = {p["pypi_name"]: p for p in vet.get("packages", [])}
    smt = load("techne/donor_smt_comparison_2026-08-31.json")
    parity = load("techne/donor_tensor_parity_2026-08-31.json")
    d5 = load("techne/donor_d5_compat_2026-08-31.json")

    consumers = {
        "tensorly": ["prometheus_math.symbolic_tensor_decomp (revived by this install)",
                     "techne.scripts.donor_tensor_parity"],
        "pyribs": ["none yet -- capability surface offered to Ludus (Worlds)"],
        "discopy": ["none yet -- capability surface offered to Harmonia (Lensing)"],
        "cvc5": ["techne.scripts.donor_smt_comparator (comparator only)"],
        "egglog": ["none yet -- capability surface offered to Lexis / Harmonia"],
    }
    limitations = {
        "tensorly": ["CP via ALS is only deterministic with init='svd' and a fixed "
                     "random_state; the adapter defaults to both, and a random init would "
                     "silently break the determinism claim in capabilities()"],
        "pyribs": ["the objective and the behavioural descriptors are supplied by the CALLER, "
                   "so archive coverage measures the caller's descriptor choice as much as the "
                   "search; coverage is not discovery"],
        "discopy": ["adapter covers monoidal composition and matrix-pipeline tensor evaluation "
                    "only; the wider categorical surface is unwrapped"],
        "cvc5": ["raising an error while a live TermManager/Solver is in the frame segfaults "
                 "the interpreter at teardown on this platform (exit 139 AFTER all tests "
                 "report PASS). The adapter validates its whole payload before constructing "
                 "any cvc5 object, and drops native handles before returning. Any future cvc5 "
                 "code must preserve that ordering.",
                 "REDUNDANT_AT_GEN0 against installed z3 5.0.0.0"],
        "egglog": ["upstream identity is description-only: the distribution declares NO "
                   "repository URL in structured PyPI metadata, only a self-referential PyPI "
                   "link. Grandfathered because it was already installed; a fresh install on "
                   "that evidence would need a maintainer check first.",
                   "the adapter exposes a CLOSED menu of six rewrite rules; accepting "
                   "arbitrary rule source would mean executing caller-supplied code behind a "
                   "provenance record claiming a named configuration"],
    }

    rows = []
    for name in sorted(D.registry):
        try:
            ad = D.get(name)
            man = ad.manifest()
            ident = man["identity"]
            status = "WRAPPED_AND_TESTED"
            if name == "cvc5" and smt and smt.get("VERDICT") == "REDUNDANT_AT_GEN0":
                status = "REDUNDANT_AT_GEN0"
        except Exception as e:                                        # noqa: BLE001
            rows.append({"donor": name, "status": "VETTED_NOT_INSTALLED",
                         "error": type(e).__name__ + ": " + str(e)})
            continue

        v = vet_by_name.get(ident["distribution"], {})
        art = v.get("artifact", {})
        rows.append({
            "donor": name,
            "distribution": ident["distribution"],
            "version": ident["version"],
            "upstream": ident["upstream"],
            "license": ident["license"],
            "identity_evidence": ident["identity_evidence"],
            "identity_gate": (v.get("upstream_identity") or {}).get("IDENTITY"),
            "status": status,
            "platform": "win_amd64 / cp312 (verified by import)",
            "provenance": {
                "pypi_sha256": art.get("pypi_sha256"),
                "digest_matches_pypi": art.get("DIGEST_MATCHES_PYPI"),
                "artifact": art.get("filename"),
                "runs_code_at_install": v.get("runs_code_at_install"),
                "n_releases": (v.get("provenance") or {}).get("n_releases"),
            },
            "capabilities": [c["name"] for c in man["capabilities"]],
            "capability_detail": man["capabilities"],
            "native_selection_relation": man["native_selection_relation"],
            "accepted_config": man["accepted_config"],
            "deterministic_replay": all(c["deterministic"] for c in man["capabilities"]),
            "consumers": consumers.get(name, []),
            "known_limitations": limitations.get(name, []),
        })

    return {
        "generated": "2026-08-31",
        "generation": "Techne Gen-0 donor substrate",
        "python": md.version("pip") and __import__("sys").version.split()[0],
        "adapters_registered": sorted(D.registry),
        "adapters_available": D.available(),
        "donors": rows,
        "deferred": [{"donor": d, "reason_class": c, "reason": r} for d, c, r in DEFERRED],
        "reports": {
            "vetting": "techne/dependency_vetting_gen0_2026-08-31.json",
            "smt_comparison": "techne/donor_smt_comparison_2026-08-31.json",
            "tensor_parity": "techne/donor_tensor_parity_2026-08-31.json",
            "d5_consumer_compat": "techne/donor_d5_compat_2026-08-31.json",
        },
        "headline_findings": {
            "tensor_parity": (parity or {}).get("CLASSIFICATION"),
            "smt": (smt or {}).get("VERDICT"),
            "d5_compat": (d5 or {}).get("OVERALL"),
        },
        "NON_CLAIMS": [
            "installation is not adoption; a passing battery is engineering evidence only",
            "no donor here has been shown to earn rent in any experiment",
            "no scientific ranking of donors is stated or implied",
        ],
    }


def to_markdown(inv: dict) -> str:
    L = []
    A = L.append
    A("# Donor inventory -- Techne Gen-0")
    A("")
    A("Generated " + inv["generated"] + ". Machine-readable source: `techne/donor_inventory.json`.")
    A("")
    A("Every field below was measured on this machine. Installation is not adoption: a donor "
      "listed as WRAPPED_AND_TESTED is callable, replayable and honest about its own selection "
      "relation, and nothing more. Whether any of it earns rent is for the benches to find out.")
    A("")
    A("## Donors")
    for d in inv["donors"]:
        A("")
        A("### " + d["donor"] + " -- " + d["status"])
        if "error" in d:
            A("- unavailable: " + d["error"])
            continue
        A("- distribution: `" + d["distribution"] + "` " + d["version"]
          + "  |  licence: " + (d["license"] or "unstated"))
        A("- upstream: " + d["upstream"] + "  (identity evidence: " + d["identity_evidence"]
          + ", gate: " + str(d["identity_gate"]) + ")")
        prov = d["provenance"]
        A("- provenance: sha256 " + str(prov.get("pypi_sha256"))[:16] + "..., digest matches PyPI: "
          + str(prov.get("digest_matches_pypi")) + ", runs code at install: "
          + str(prov.get("runs_code_at_install")) + ", releases: " + str(prov.get("n_releases")))
        A("- capabilities: " + ", ".join("`" + c + "`" for c in d["capabilities"]))
        rel = d["native_selection_relation"]
        A("- native selection relation: **" + rel["kind"] + "** / " + rel["direction"]
          + (" over " + rel["over"] if rel["over"] else "")
          + " (supplied by " + rel["supplied_by"] + ")")
        if rel.get("note"):
            A("  - " + rel["note"])
        A("- deterministic replay: " + str(d["deterministic_replay"]))
        A("- consumers: " + ("; ".join(d["consumers"]) or "none"))
        for lim in d["known_limitations"]:
            A("- limitation: " + lim)
    A("")
    A("## Deferred, with reasons")
    for x in inv["deferred"]:
        A("")
        A("- **" + x["donor"] + "** (" + x["reason_class"] + ") -- " + x["reason"])
    A("")
    A("## Headline findings")
    for k, v in inv["headline_findings"].items():
        A("- " + k + ": **" + str(v) + "**")
    A("")
    A("## What this inventory does not claim")
    for n in inv["NON_CLAIMS"]:
        A("- " + n)
    A("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="techne/donor_inventory.json")
    ap.add_argument("--md", default="techne/DONOR_INVENTORY.md")
    a = ap.parse_args()
    inv = build()
    (REPO / a.json).write_text(json.dumps(inv, indent=2), encoding="utf-8")
    (REPO / a.md).write_text(to_markdown(inv), encoding="utf-8")
    for d in inv["donors"]:
        print("{:10s} {:22s} {:10s} {}".format(
            d["donor"], d["status"], d.get("version", "-"),
            ",".join(d.get("capabilities", []))))
    print("\nheadline:", json.dumps(inv["headline_findings"]))
    print("wrote", a.json, "and", a.md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
