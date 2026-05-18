"""
Clio v0.2 — Cheap-LLM claim extractor

Reads papers from agora.clio_papers without extractions yet, fires the
LLM cascade (Cerebras → Groq → NVIDIA → DeepSeek paid last) on each one's
title + abstract + categories, parses structured JSON into 0-3 candidate
claims per paper, writes them to agora.clio_claim_extractions.

Sigma submission (v0.3) is a separate worker; this script stops at
writing claim extractions.

Usage:
    python scripts/clio_extractor.py --once               # one batch
    python scripts/clio_extractor.py --batch-size 5       # smaller batch
    python scripts/clio_extractor.py --loop               # repeat every N sec
    python scripts/clio_extractor.py --interval 600       # custom loop interval

Design seams (for testability):
    - build_extraction_prompt(paper)             — pure function
    - parse_extraction_response(text)            — pure function, never raises
    - extract_claims_for_paper(paper, llm_fn)    — DI for tests
    - run_extraction_batch(...)                  — DI for tests
"""
import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import Callable, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
try:
    import agora_persist
    HAS_PG = True
except Exception:
    HAS_PG = False

try:
    from llm_cascade import call_llm
    HAS_LLM = True
except Exception:
    HAS_LLM = False
    def call_llm(prompt, system="", **kwargs):  # type: ignore
        return "(llm_cascade unavailable)"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CLIO-EXTRACT] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("clio_extractor")


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

EXTRACTION_SYSTEM = (
    "You are a claim extractor for the Prometheus substrate. Given a math "
    "paper abstract, identify up to 3 falsifiable claims that could feed a "
    "claim-stack discipline. A falsifiable claim is one that could be killed "
    "by a specific counterexample, computation, or proof error. Respond with "
    "valid JSON only — no preamble, no markdown fences."
)

PARADIGM_LEGEND = (
    "Paradigm codes: P01=Algebraic Translation, P02=Cohomological Obstruction, "
    "P03=Symmetry Exploitation, P04=Spectral Analysis, P05=Analytic Continuation, "
    "P06=Geometric Flow, P07=Descent/Induction, P08=Probabilistic Method, "
    "P09=Exhaustive Computation, P10=Formal Verification, P11=Sieve Methods, "
    "P12=Height/Diophantine, P13=Tropical/Degeneration, P14=Forcing/Independence, "
    "P15=Tensor/Multilinear Decomposition, P16=Modular/Arithmetic Statistics, "
    "P17=Variational/Extremal, P18=Operadic/Categorical, P19=Cross-region "
    "operator transport, P21=Curated-corpus empirical sweep, P22=Polynomial "
    "method on signed graphs, P23=Recursive self-compression, P24=Bound-tightening "
    "long program, P25=Pivotal negative result, P26=LP/SDP relaxation, "
    "P27=Slice rank polynomial method, P28=Asymptotic spectrum, P29=Border "
    "apolarity, P30=Tensor network contraction, P31=Secant variety geometry."
)


def build_extraction_prompt(paper: dict) -> str:
    """Compose the user-side prompt from a paper dict. Pure function."""
    title = paper.get("title") or "(untitled)"
    abstract = paper.get("abstract") or "(no abstract)"
    authors = paper.get("authors") or []
    cats = paper.get("arxiv_categories") or []
    auth_str = ", ".join(authors[:5])
    cats_str = ", ".join(cats[:8])

    return (
        f"Paper title: {title}\n"
        f"Authors: {auth_str}\n"
        f"arXiv categories: {cats_str}\n"
        f"Abstract: {abstract}\n\n"
        "Extract up to 3 falsifiable claims. For each, return a JSON object "
        "with these fields:\n"
        '  - "claim_text": single declarative sentence stating the claim\n'
        '  - "claim_type": one of "theorem" | "conjecture" | "empirical" | '
        '"counterexample" | "erratum" | "construction"\n'
        '  - "paradigm_hint": one of P01-P31 if a known paradigm is exercised, else null\n'
        '  - "open_problem_hint": free-text reference to a known open problem, else null\n'
        '  - "falsifiable": true|false — can this be killed by counterexample/computation?\n'
        '  - "confidence": 0.0-1.0 — confidence that the paper actually establishes this\n\n'
        f"{PARADIGM_LEGEND}\n\n"
        'Respond with exactly: {"claims": [<claim>, <claim>, ...]}\n'
        'If no falsifiable claims are present, return {"claims": []}.'
    )


# ---------------------------------------------------------------------------
# Response parsing — robust to LLM quirks
# ---------------------------------------------------------------------------

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)

_VALID_CLAIM_TYPES = {
    "theorem", "conjecture", "empirical", "counterexample", "erratum", "construction"
}


def parse_extraction_response(text: str) -> list[dict]:
    """Parse the LLM's JSON output into a list of claim dicts. Never raises.

    Strategy:
      1. Try direct json.loads(text).
      2. Fall back to extracting the first {...} block via regex.
      3. Validate each claim has required fields; coerce types defensively.
    """
    if not text or not isinstance(text, str):
        return []
    text = text.strip()
    # Strip markdown fences if present (LLMs sometimes ignore "no fences")
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        if text.endswith("```"):
            text = text[: -3].strip()

    payload = None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        m = _JSON_BLOCK_RE.search(text)
        if m:
            try:
                payload = json.loads(m.group(0))
            except json.JSONDecodeError:
                return []
        else:
            return []
    if not isinstance(payload, dict):
        return []
    claims_raw = payload.get("claims", [])
    if not isinstance(claims_raw, list):
        return []

    out: list[dict] = []
    for c in claims_raw[:3]:
        if not isinstance(c, dict):
            continue
        claim_text = c.get("claim_text")
        if not claim_text or not isinstance(claim_text, str):
            continue
        ct = c.get("claim_type")
        if isinstance(ct, str):
            ct = ct.strip().lower()
            if ct not in _VALID_CLAIM_TYPES:
                ct = None
        else:
            ct = None
        ph = c.get("paradigm_hint")
        if isinstance(ph, str):
            ph = ph.strip().upper()
            if not re.match(r"^P\d{2}$", ph):
                ph = None
        else:
            ph = None
        op = c.get("open_problem_hint")
        if isinstance(op, str):
            op = op.strip() or None
        else:
            op = None
        f = c.get("falsifiable")
        f = bool(f) if isinstance(f, bool) else None
        conf = c.get("confidence")
        try:
            conf = float(conf) if conf is not None else None
            if conf is not None:
                conf = max(0.0, min(1.0, conf))
        except (TypeError, ValueError):
            conf = None
        out.append({
            "claim_text": claim_text.strip(),
            "claim_type": ct,
            "paradigm_hint": ph,
            "open_problem_hint": op,
            "falsifiable": f,
            "confidence": conf,
        })
    return out


# ---------------------------------------------------------------------------
# Per-paper extraction (DI for tests)
# ---------------------------------------------------------------------------

def extract_claims_for_paper(
    paper: dict,
    llm_fn: Optional[Callable] = None,
    extractor_model_label: str = "llm_cascade",
) -> tuple[list[dict], str]:
    """Returns (claims, raw_llm_response). llm_fn injectable for tests."""
    fn = llm_fn or call_llm
    prompt = build_extraction_prompt(paper)
    response_text = fn(prompt, system=EXTRACTION_SYSTEM, max_tokens=1500, temperature=0.2)
    claims = parse_extraction_response(response_text)
    return claims, response_text


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def run_extraction_batch(
    batch_size: int = 10,
    llm_fn: Optional[Callable] = None,
    paper_reader: Optional[Callable] = None,
    writer: Optional[Callable] = None,
    extractor_model_label: str = "llm_cascade",
) -> dict:
    """Process one batch of unextracted papers. Returns stats dict.

    paper_reader, writer, llm_fn are all injectable for tests.
    Defaults read/write Postgres via agora_persist; default LLM is the cascade.
    """
    if paper_reader is None:
        paper_reader = agora_persist.read_unextracted_papers if HAS_PG else (lambda **kw: [])
    if writer is None:
        writer = agora_persist.write_clio_claim_extraction if HAS_PG else (lambda **kw: None)

    papers = paper_reader(limit=batch_size)
    stats = {
        "papers_processed": 0,
        "papers_failed": 0,
        "claims_extracted": 0,
        "claims_per_paper": [],
    }

    for paper in papers:
        try:
            claims, raw = extract_claims_for_paper(
                paper, llm_fn=llm_fn, extractor_model_label=extractor_model_label,
            )
            for i, claim in enumerate(claims):
                writer(
                    paper_id=paper["id"],
                    claim_index=i,
                    claim_text=claim["claim_text"],
                    claim_type=claim.get("claim_type"),
                    paradigm_hint=claim.get("paradigm_hint"),
                    open_problem_hint=claim.get("open_problem_hint"),
                    falsifiable=claim.get("falsifiable"),
                    confidence=claim.get("confidence"),
                    extractor_model=extractor_model_label,
                    raw_llm_response=raw[:8000],  # cap on what we store
                )
                stats["claims_extracted"] += 1
            stats["papers_processed"] += 1
            stats["claims_per_paper"].append(len(claims))
            log.info(f"paper {paper.get('id')}: {len(claims)} claims")
        except Exception as e:
            log.exception(f"paper {paper.get('id')} failed: {e}")
            stats["papers_failed"] += 1

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Clio v0.2 — claim extractor")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--once", action="store_true", help="Single batch, then exit (default)")
    parser.add_argument("--loop", action="store_true", help="Loop with --interval delay")
    parser.add_argument("--interval", type=int, default=600, help="Loop interval seconds (default 600)")
    args = parser.parse_args()

    if not HAS_PG:
        log.error("agora_persist unavailable (Postgres unreachable). Aborting.")
        return 1
    if not HAS_LLM:
        log.error("llm_cascade unavailable. Aborting.")
        return 1

    print("=" * 60)
    print("  CLIO-EXTRACT — claim extraction (v0.2)")
    print(f"  Mode: {'loop @ ' + str(args.interval) + 's' if args.loop else 'single batch'}")
    print(f"  Batch size: {args.batch_size}")
    print("=" * 60)

    if args.loop:
        while True:
            try:
                stats = run_extraction_batch(batch_size=args.batch_size)
                log.info(f"batch stats: {stats}")
            except Exception as e:
                log.exception(f"batch failed: {e}")
            time.sleep(args.interval)
    else:
        stats = run_extraction_batch(batch_size=args.batch_size)
        print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
