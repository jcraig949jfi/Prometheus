"""
Metis — Cunning Intelligence

Reads Eos's daily digests, cross-references with Prometheus project context,
and produces a 1-page executive brief via LLM analysis.

Eos is the eyes. Metis is the brain that tells you what the eyes saw.

Usage:
    python metis.py                     # Analyze latest Eos digest
    python metis.py --digest path.md    # Analyze specific digest
"""

import argparse
import json
import logging
import os
import re
import sys
import urllib.request
import urllib.parse
import ssl
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

METIS_ROOT = Path(__file__).resolve().parent.parent
EOS_REPORTS = METIS_ROOT.parent / "eos" / "reports"
BRIEFS_DIR = METIS_ROOT / "briefs"
PROMETHEUS_ROOT = METIS_ROOT.parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [METIS] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("metis")

# Load .env from eos (shared keys)
_env_file = METIS_ROOT.parent / "eos" / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


# ---------------------------------------------------------------------------
# Context Loader
# ---------------------------------------------------------------------------

def load_project_context() -> str:
    """Load project context files for the LLM to cross-reference."""
    context_parts = []

    # Priorities — what we're working on
    priorities_path = PROMETHEUS_ROOT / "docs" / "PRIORITIES.md"
    if priorities_path.exists():
        text = priorities_path.read_text(encoding="utf-8")[:2000]
        context_parts.append(f"=== CURRENT PRIORITIES ===\n{text}")

    # TODO — task status
    todo_path = PROMETHEUS_ROOT / "docs" / "TODO.md"
    if todo_path.exists():
        text = todo_path.read_text(encoding="utf-8")[:1500]
        context_parts.append(f"=== TASK STATUS ===\n{text}")

    # RPH abstract — what we're trying to prove
    rph_path = PROMETHEUS_ROOT / "docs" / "RPH.md"
    if rph_path.exists():
        text = rph_path.read_text(encoding="utf-8")[:1500]
        context_parts.append(f"=== RPH (our core hypothesis) ===\n{text}")

    # Aletheia knowledge graph taxonomy — what we've cataloged
    try:
        aletheia_path = PROMETHEUS_ROOT / "agents" / "aletheia" / "src" / "aletheia.py"
        if aletheia_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("aletheia", str(aletheia_path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            agent = mod.AletheiaAgent()
            summary = agent.generate_taxonomy_summary()
            agent.close()
            if summary and len(summary.strip()) > 50:
                context_parts.append(f"=== KNOWLEDGE GRAPH (from Aletheia) ===\n{summary[:2000]}")
    except Exception:
        pass  # Aletheia not available — that's fine

    return "\n\n".join(context_parts)


# ---------------------------------------------------------------------------
# Digest Parser
# ---------------------------------------------------------------------------

def find_latest_digest() -> Path:
    """Find the most recent Eos digest."""
    if not EOS_REPORTS.exists():
        raise FileNotFoundError(f"Eos reports directory not found: {EOS_REPORTS}")

    digests = sorted(EOS_REPORTS.glob("*.md"), key=lambda p: p.stem, reverse=True)
    if not digests:
        raise FileNotFoundError("No Eos digests found")

    return digests[0]


def extract_attention_items(digest_text: str) -> str:
    """Extract the ATTENTION REQUIRED and Deep Analysis sections from the digest."""
    sections = []

    # Extract ATTENTION REQUIRED section
    attention_match = re.search(
        r'## !! ATTENTION REQUIRED.*?\n(.*?)(?=\n## )', digest_text, re.DOTALL
    )
    if attention_match:
        sections.append("ATTENTION ITEMS:\n" + attention_match.group(1).strip())

    # Extract Deep Analysis section
    analysis_match = re.search(
        r'## Deep Analysis.*?\n(.*?)(?=\n## )', digest_text, re.DOTALL
    )
    if analysis_match:
        sections.append("LLM ANALYSIS:\n" + analysis_match.group(1).strip())

    # Extract Web Intelligence
    web_match = re.search(
        r'## Web Intelligence.*?\n(.*?)(?=\n## )', digest_text, re.DOTALL
    )
    if web_match:
        sections.append("WEB INTELLIGENCE:\n" + web_match.group(1).strip())

    if not sections:
        # Fallback: first 3000 chars of digest
        sections.append(digest_text[:3000])

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# LLM Interface
# ---------------------------------------------------------------------------

def _get_ssl_context():
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def call_llm(prompt: str, system: str = "") -> str:
    """Call the best available LLM. Tries NVIDIA → Cerebras → Groq."""

    providers = [
        {
            "name": "NVIDIA Nemotron 120B",
            "endpoint": os.environ.get("NVIDIA_API_ENDPOINT", "https://integrate.api.nvidia.com/v1"),
            "key": os.environ.get("NVIDIA_API_KEY"),
            "model": os.environ.get("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b"),
        },
        {
            "name": "Cerebras Qwen3-235B",
            "endpoint": "https://api.cerebras.ai/v1",
            "key": os.environ.get("CEREBRAS_API_KEY"),
            "model": "qwen-3-235b-a22b-instruct-2507",
        },
        {
            "name": "Groq Llama 3.1-8B",
            "endpoint": "https://api.groq.com/openai/v1",
            "key": os.environ.get("GROQ_API_KEY"),
            "model": "llama-3.1-8b-instant",
        },
    ]

    ctx = _get_ssl_context()

    for provider in providers:
        if not provider["key"]:
            continue

        log.info(f"Trying {provider['name']}...")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps({
            "model": provider["model"],
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.3,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"{provider['endpoint']}/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {provider['key']}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            choices = data.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                text = msg.get("content") or msg.get("reasoning_content") or ""
                if text.strip():
                    log.info(f"Response from {provider['name']} ({len(text)} chars)")
                    return text.strip()

        except Exception as e:
            log.warning(f"{provider['name']} failed: {e}")
            continue

    return "(Metis could not reach any LLM provider)"


# ---------------------------------------------------------------------------
# Brief Generator
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Metis, the analytical brain of the Prometheus research program.

Prometheus probes transformer model internals for reasoning circuits using:
- Ignis: CMA-ES evolutionary search for steering vectors in the residual stream
- Arcanum: waste stream novelty mining for unexpected artifacts
- RPH (Reasoning Precipitation Hypothesis): reasoning circuits precipitate at scale

Your job: read the Eos horizon scanner's findings, cross-reference with our project
context, and produce a brief with exactly three sections:

## Act on this
Items requiring immediate action. New tools to integrate, papers that challenge
our approach, free API resources discovered, code repos we should clone.
Each item: one sentence what it is, one sentence what to do.

## Watch this
Items worth monitoring over the next week. Emerging trends, papers in review,
repos gaining traction. No action needed yet.

## For the record
Notable but no action needed. Validates our direction, interesting but tangential,
or "good to know" items.

Rules:
- Maximum 3 items per section (9 total). Compress ruthlessly.
- Lead every item with a bold one-line headline.
- Be specific about what action to take ("clone repo X", "read section 3 of paper Y").
- Flag anything that suggests we should pivot or accelerate.
- If nothing warrants action, say so. Don't manufacture urgency.
"""


def generate_brief(digest_path: Path) -> str:
    """Generate an executive brief from an Eos digest."""

    log.info(f"Reading digest: {digest_path.name}")
    digest_text = digest_path.read_text(encoding="utf-8")

    # Extract the high-value sections
    findings = extract_attention_items(digest_text)

    # Load project context
    context = load_project_context()

    # Build the prompt
    prompt = f"""Here is today's Eos horizon scan and our current project context.
Produce the executive brief.

--- EOS FINDINGS ---
{findings[:4000]}

--- PROJECT CONTEXT ---
{context[:3000]}

--- PRODUCE THE BRIEF ---
Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
"""

    return call_llm(prompt, system=SYSTEM_PROMPT)


def write_brief(brief_text: str, digest_path: Path) -> Path:
    """Write the brief to disk."""
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = digest_path.stem  # e.g., "2026-03-22"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    brief_path = BRIEFS_DIR / f"{date_str}_brief.md"

    content = (
        f"# Metis Executive Brief -- {date_str}\n"
        f"*Generated: {ts}*\n"
        f"*Source: Eos digest {digest_path.name}*\n\n"
        f"---\n\n"
        f"{brief_text}\n"
    )

    brief_path.write_text(content, encoding="utf-8")
    log.info(f"Brief written: {brief_path}")
    return brief_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Metis -- Cunning Intelligence")
    parser.add_argument("--digest", type=Path, default=None,
                        help="Path to specific Eos digest (default: latest)")
    args = parser.parse_args()

    print("=" * 62)
    print("  METIS -- CUNNING INTELLIGENCE")
    print("  Distilling signal from noise.")
    print("=" * 62)
    print()

    # Find digest
    if args.digest:
        digest_path = args.digest
    else:
        digest_path = find_latest_digest()

    log.info(f"Digest: {digest_path}")

    # Generate brief
    brief_text = generate_brief(digest_path)

    # Write brief
    brief_path = write_brief(brief_text, digest_path)

    # Print to console (handle Windows encoding)
    print()
    print("=" * 62)
    try:
        print(brief_text)
    except UnicodeEncodeError:
        print(brief_text.encode("ascii", errors="replace").decode("ascii"))
    print("=" * 62)
    print(f"\nBrief saved to: {brief_path}")


if __name__ == "__main__":
    main()
