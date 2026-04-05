"""
Submit research packages to Gemini Deep Research via Interactions API.

Usage:
    # Test with one package first:
    python charon/research/submit_deep_research.py --test 14

    # Submit all pending:
    python charon/research/submit_deep_research.py --all

    # Submit specific packages:
    python charon/research/submit_deep_research.py 14 15 16 17 21

    # Check status of running research:
    python charon/research/submit_deep_research.py --status

Requires:
    pip install google-genai
    GEMINI_API_KEY in googleAI/.env or environment variable
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESEARCH_DIR = PROJECT_ROOT / "charon" / "research"
ENV_FILE = PROJECT_ROOT / "googleAI" / ".env"
STATUS_FILE = RESEARCH_DIR / "_submission_status.json"

# Deep Research agent ID (as of 2026-04)
AGENT_ID = "deep-research-pro-preview-12-2025"

# Packages to submit (new batch + pending from previous batch)
NEW_PACKAGES = {
    14: "package_14_tamagawa_theory",
    15: "package_15_normalization_artifacts",
    16: "package_16_ils_support_window",
    17: "package_17_wasserstein_l_functions",
    21: "package_21_finite_conductor_corrections",
    27: "package_27_gap_oscillation",
    28: "package_28_ari_ucurve",
    29: "package_29_bsd_wall_theory",
    30: "package_30_apollo_evolutionary_gp",
    31: "package_31_surrogate_fitness",
    32: "package_32_many_objective_nsga",
    33: "package_33_llm_mutation_quality",
    34: "package_34_apollo_v2c_throughput",
    35: "package_35_galois_image_zeros",
    36: "package_36_nonlinear_bsd",
    37: "package_37_crrao_revelation_bridge",
}

PENDING_PACKAGES = {
    10: "package_10_nebentypus_symmetry",
    13: "package_13_bsd_invariants_zero_space",
}

ALL_PACKAGES = {**PENDING_PACKAGES, **NEW_PACKAGES}


def load_api_key():
    """Load API key via central keys.py, with fallback to googleAI/.env."""
    _sys = __import__("sys")
    _sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from keys import get_key
        return get_key("GEMINI")
    except (ImportError, ValueError):
        pass
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY=") and not line.endswith("_here"):
                return line.split("=", 1)[1].strip()
    print("ERROR: No GEMINI_API_KEY found.")
    print(f"  Set it in {ENV_FILE} or as environment variable.")
    print(f"  Get a key at: https://aistudio.google.com -> 'Get API Key'")
    sys.exit(1)


def load_research_brief(package_dir):
    """Load the RESEARCH_BRIEF.md from a package directory."""
    brief_path = RESEARCH_DIR / package_dir / "RESEARCH_BRIEF.md"
    if not brief_path.exists():
        print(f"  ERROR: {brief_path} not found")
        return None
    return brief_path.read_text(encoding="utf-8")


def submit_deep_research(client, package_num, package_dir, brief_text):
    """Submit a research brief to Gemini Deep Research via Interactions API."""
    print(f"\n  Submitting package {package_num}: {package_dir}")
    print(f"  Brief length: {len(brief_text)} chars")

    try:
        interaction = client.interactions.create(
            agent=AGENT_ID,
            input=brief_text,
            background=True,
        )
        interaction_id = interaction.id
        status = interaction.status
        print(f"  Submitted! ID: {interaction_id}")
        print(f"  Status: {status}")
        return interaction_id
    except Exception as e:
        print(f"  FAILED: {e}")
        print(f"  If the API has changed, check: https://ai.google.dev/gemini-api/docs/deep-research")
        return None


def check_status(client, interaction_id):
    """Poll for completion of a deep research interaction."""
    try:
        result = client.interactions.get(id=interaction_id)
        state = result.status if hasattr(result, 'status') else 'unknown'
        return state, result
    except Exception as e:
        return f"error: {e}", None


def extract_text(interaction):
    """Extract text content from a completed interaction."""
    if not interaction.outputs:
        return None
    parts = []
    for output in interaction.outputs:
        if hasattr(output, 'text'):
            parts.append(output.text)
        elif hasattr(output, 'content'):
            parts.append(str(output.content))
    return "\n\n".join(parts) if parts else str(interaction.outputs)


def save_result(package_dir, result_text):
    """Save completed research result to the package directory."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_path = RESEARCH_DIR / package_dir / f"gemini-research_{timestamp}.md"
    output_path.write_text(result_text, encoding="utf-8")
    print(f"  Saved to: {output_path}")


def load_status():
    """Load submission status from file."""
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {}


def save_status(status):
    """Save submission status to file."""
    STATUS_FILE.write_text(json.dumps(status, indent=2))


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    api_key = load_api_key()

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except ImportError:
        print("ERROR: google-genai not installed.")
        print("  Run: pip install google-genai")
        sys.exit(1)

    # --- Status check mode ---
    if "--status" in args:
        status = load_status()
        if not status:
            print("No submissions tracked yet.")
            return
        print("\n=== Submission Status ===\n")
        for pkg, info in status.items():
            if "interaction_id" not in info:
                print(f"  Package {pkg} ({info['dir']}): {info.get('state', 'unknown')} (no interaction_id)")
                continue
            state, result = check_status(client, info["interaction_id"])
            print(f"  Package {pkg} ({info['dir']}): {state}")
            if state == "completed" and result:
                result_text = extract_text(result)
                if result_text:
                    save_result(info["dir"], result_text)
                else:
                    print(f"    WARNING: completed but no text output found")
                info["state"] = "completed"
            elif state not in ("in_progress", "requires_action"):
                info["state"] = state
        save_status(status)
        return

    # --- Test mode (single package, no submit) ---
    if "--test" in args:
        idx = args.index("--test")
        pkg_num = int(args[idx + 1])
        pkg_dir = ALL_PACKAGES.get(pkg_num)
        if not pkg_dir:
            print(f"Unknown package: {pkg_num}")
            sys.exit(1)
        brief = load_research_brief(pkg_dir)
        if brief:
            print(f"\n=== TEST: Package {pkg_num} ===")
            print(f"Directory: {pkg_dir}")
            print(f"Brief length: {len(brief)} chars")
            print(f"\nFirst 500 chars:\n{brief[:500]}")
            print(f"\n[Would submit to Deep Research agent: {AGENT_ID}]")
            print(f"[Run without --test to actually submit]")
        return

    # --- Determine which packages to submit ---
    if "--all" in args:
        to_submit = ALL_PACKAGES
    else:
        to_submit = {}
        for a in args:
            try:
                num = int(a)
                if num in ALL_PACKAGES:
                    to_submit[num] = ALL_PACKAGES[num]
                else:
                    print(f"Unknown package number: {num}")
            except ValueError:
                pass

    if not to_submit:
        print("No packages to submit. Use --all or specify package numbers.")
        sys.exit(1)

    # --- Submit ---
    MAX_CONCURRENT = 3  # Deep Research allows max 3 concurrent

    print(f"\n=== Submitting {len(to_submit)} packages to Gemini Deep Research ===")
    print(f"Agent: {AGENT_ID}")
    print(f"Max concurrent: {MAX_CONCURRENT}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    status = load_status()
    sorted_pkgs = sorted(to_submit.items())

    for batch_start in range(0, len(sorted_pkgs), MAX_CONCURRENT):
        batch = sorted_pkgs[batch_start:batch_start + MAX_CONCURRENT]
        batch_num = (batch_start // MAX_CONCURRENT) + 1
        total_batches = (len(sorted_pkgs) + MAX_CONCURRENT - 1) // MAX_CONCURRENT

        print(f"\n--- Batch {batch_num}/{total_batches} ---")

        # Submit this batch
        batch_ids = []
        for pkg_num, pkg_dir in batch:
            brief = load_research_brief(pkg_dir)
            if not brief:
                continue

            interaction_id = submit_deep_research(client, pkg_num, pkg_dir, brief)
            if interaction_id:
                status[str(pkg_num)] = {
                    "dir": pkg_dir,
                    "interaction_id": interaction_id,
                    "submitted": datetime.now().isoformat(),
                    "state": "in_progress",
                }
                batch_ids.append((pkg_num, interaction_id))
            time.sleep(2)

        save_status(status)

        # If there are more batches, wait for this batch to complete
        if batch_start + MAX_CONCURRENT < len(sorted_pkgs) and batch_ids:
            print(f"\n  Waiting for batch {batch_num} to complete before next batch...")
            while True:
                time.sleep(30)
                all_done = True
                for pkg_num, iid in batch_ids:
                    state, _ = check_status(client, iid)
                    if state == "in_progress":
                        all_done = False
                    elif state == "completed":
                        print(f"    Package {pkg_num}: completed")
                        status[str(pkg_num)]["state"] = "completed"
                    elif state not in ("in_progress", "requires_action"):
                        print(f"    Package {pkg_num}: {state}")
                        status[str(pkg_num)]["state"] = state
                save_status(status)
                if all_done:
                    break
                # Show progress
                pending = sum(1 for _, iid in batch_ids
                              if check_status(client, iid)[0] == "in_progress")
                print(f"    {pending}/{len(batch_ids)} still in progress...")

    save_status(status)
    print(f"\n=== Done. {len(status)} total tracked submissions. ===")
    print(f"Check results with: python {__file__} --status")


if __name__ == "__main__":
    main()
