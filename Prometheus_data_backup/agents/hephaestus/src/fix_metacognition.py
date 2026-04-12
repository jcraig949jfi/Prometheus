#!/usr/bin/env python3
"""Fix _meta_confidence patterns across all v5 tools.

The current patterns only catch presupposition and pronoun ambiguity.
This broadens coverage to all 13 Tier B categories.

Usage:
    python fix_metacognition.py          # Fix all v5 tools
    python fix_metacognition.py --test   # Test patterns only, don't modify files
"""

import argparse
import re
import sys
from pathlib import Path

V5_DIR = Path(__file__).resolve().parent.parent / "forge_v5"

# The broadened _meta_confidence function
# Covers all 13 Tier B categories from the trap generator
BROADENED_META = '''def _meta_confidence(prompt, answer):
    """Merged metacognitive confidence - Council v5 + broadened patterns.
    Detects all 13 Tier B categories. Returns cap [0.05..1.0].
    Lower = more metacognitive doubt.
    """
    pl = prompt.lower().strip()
    cl = answer.lower().strip()
    # NOTE: For epistemic honesty, confidence should be LOW on metacognitive
    # traps regardless of whether the candidate acknowledges the issue.
    # The acknowledgment reward belongs in evaluate() scoring, not confidence().
    # confidence() answers: "How sure am I about THIS question?" — and the
    # answer for ambiguous/presupposition questions is always "not very sure."
    ack = False  # Disabled: honesty > reward for acknowledgment

    # 1. Presupposition / Loaded questions
    if re.search(r'\\b(?:have|has|had)\\s+(?:you|they|he|she|it|we)\\s+(?:stopped|quit|given up|realized|started)', pl):
        return 0.85 if ack else 0.20
    if re.search(r'someone\\s+asks.*(?:have you|did you)\\s+(?:stop|quit|start)', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\\b(?:why|how|when)\\s+did\\s+\\w+\\s+(?:fail|stop|quit|lose|forget)', pl):
        return 0.85 if ack else 0.22

    # 2. Scope ambiguity
    if re.search(r'\\bevery\\b.*\\b(?:a|an|one|some)\\b', pl) and re.search(r'\\b(?:same|all|each|did)\\b.*\\?', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\\bevery\\b.*\\bdid\\b.*(?:same|all the same)', pl):
        return 0.85 if ack else 0.20

    # 3. Pronoun ambiguity
    if re.search(r'\\b(?:he|she|they)\\b', pl) and re.search(r'\\bwho\\b.*\\?', pl):
        if re.search(r'\\b\\w+\\s+(?:told|informed|reminded|said to|asked)\\s+\\w+\\s+(?:that\\s+)?(?:he|she|they)', pl):
            return 0.85 if ack else 0.22

    # 4. Garden path (limited detection)
    if re.search(r'consider\\s+this\\s+sentence', pl):
        return 0.85 if ack else 0.22

    # 5. Validity vs truth (false premises + valid structure)
    if re.search(r'all\\s+\\w+\\s+can\\s+(?:fly|swim|sing|dance|talk|drive)', pl):
        if re.search(r'\\bvalid\\b|\\blogically\\b|\\bargument\\b', pl):
            return 0.85 if ack else 0.25
    if re.search(r'premise.*false|false.*premise', pl):
        return 0.85 if ack else 0.25

    # 6. Argument strength (comparing two arguments)
    if re.search(r'argument\\s+[ab12].*argument\\s+[ab12]', pl) and re.search(r'\\bstronger\\b|\\bweaker\\b|\\bbetter\\b', pl):
        return 0.85 if ack else 0.25

    # 7. Confidence calibration (hedging language)
    if re.search(r'\\b(?:probably|likely|believed|rumored|might|possibly)\\b', pl) and re.search(r'how\\s+confident', pl):
        return 0.85 if ack else 0.25

    # 8. Survivorship bias
    if re.search(r'\\b(?:all|every)\\s+(?:successful|winning|top|best)\\b.*\\bsample\\b', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\\bsample\\b.*\\b(?:all|every)\\s+.*\\b(?:did|had|were)\\b', pl):
        return 0.85 if ack else 0.20

    # 9. Sunk cost
    if re.search(r'(?:spent|paid|invested)\\s+\\$?\\d+', pl) and re.search(r'\\b(?:sick|ill|injured|tired|busy|unable)\\b', pl):
        return 0.85 if ack else 0.20
    if re.search(r'non-?refundable', pl):
        return 0.85 if ack else 0.20

    # 10. False dichotomy
    if re.search(r'either\\s+you\\s+\\w+.*or\\s+you\\s+(?:don|are|have)', pl):
        return 0.85 if ack else 0.25
    if re.search(r'(?:yes or no|true or false)\\s*[.?]?\\s*$', pl) and len(pl.split()) > 15:
        return 0.85 if ack else 0.25

    # 11. Composition fallacy
    if re.search(r'every\\s+\\w+\\s+(?:is|are)\\s+\\w+\\.?\\s+does\\s+it\\s+(?:necessarily|follow)', pl):
        return 0.85 if ack else 0.22
    if re.search(r'every\\s+\\w+.*\\bdoes\\s+(?:it|this)\\s+(?:mean|follow|necessarily)', pl):
        return 0.85 if ack else 0.22

    # 12. Regression to mean
    if re.search(r'scored?\\s+\\d+.*then\\s+\\d+', pl) and re.search(r'\\b(?:worse|better|declined|improved|coach)\\b', pl):
        return 0.85 if ack else 0.22

    # 13. Intention vs outcome
    if re.search(r'\\b(?:followed|used|applied)\\s+(?:protocol|standard|recommended|proper)', pl):
        if re.search(r'\\b(?:died|failed|injured|accident|reaction|collapsed)\\b', pl):
            return 0.85 if ack else 0.25

    # 14. Subjectivity
    if re.search(r'\\b(?:best|worst|favorite|most beautiful|ugliest)\\b', pl) and '?' in pl:
        return 0.20

    # 15. Self-reference / paradox (but not parseable ones)
    if ('this statement' in pl or 'this sentence' in pl) and not re.search(r'\\d+\\s+words', pl):
        return 0.22

    return 1.0
'''


def test_patterns():
    """Test the broadened patterns against actual Tier B traps."""
    # Build the function
    ns = {"re": re}
    exec(BROADENED_META, ns)
    meta = ns["_meta_confidence"]

    sys.path.insert(0, str(Path(__file__).parent))
    from trap_generator_extended import generate_full_battery
    battery = generate_full_battery(n_per_category=3, seed=42)
    tier_b = [t for t in battery if t.get("tier") == "B"]

    print(f"Testing broadened _meta_confidence against {len(tier_b)} Tier B traps:")
    print()

    low = 0
    high = 0
    by_cat = {}

    for trap in tier_b:
        cap = meta(trap["prompt"], trap["correct"])
        is_low = cap < 0.3
        cat = trap["category"]
        if cat not in by_cat:
            by_cat[cat] = {"low": 0, "high": 0}
        if is_low:
            low += 1
            by_cat[cat]["low"] += 1
        else:
            high += 1
            by_cat[cat]["high"] += 1
        status = "LOW" if is_low else "HIGH"
        print(f"[{status:4s}] cap={cap:.2f} [{cat:25s}] {trap['prompt'][:60]}")

    print()
    print(f"Overall: {low} LOW / {high} HIGH / {len(tier_b)} total ({low/len(tier_b)*100:.0f}% low confidence)")
    print()
    print("Per category:")
    for cat, counts in sorted(by_cat.items()):
        total = counts["low"] + counts["high"]
        print(f"  {cat:25s} {counts['low']}/{total} low")


def apply_to_all():
    """Replace _meta_confidence in all v5 tools with broadened version."""
    tools = sorted(p for p in V5_DIR.glob("*.py") if not p.name.startswith("_"))
    print(f"Applying broadened _meta_confidence to {len(tools)} tools...")

    updated = 0
    skipped = 0
    errors = 0

    for py in tools:
        try:
            src = py.read_text(encoding="utf-8")

            # Find and replace _meta_confidence function
            # Handle both module-level and class method forms
            if "def _meta_confidence(" not in src:
                skipped += 1
                continue

            # Module-level function (most tools)
            pattern = r'def _meta_confidence\(prompt.*?\n(?=def |class |\Z)'
            match = re.search(pattern, src, re.DOTALL)

            if match:
                # Replace with broadened version
                new_src = src[:match.start()] + BROADENED_META.strip() + "\n\n" + src[match.end():]
                py.write_text(new_src, encoding="utf-8")
                updated += 1
            else:
                # Try class method form
                pattern2 = r'    def _meta_confidence\(self.*?\n(?=    def |class |\Z)'
                match2 = re.search(pattern2, src, re.DOTALL)
                if match2:
                    # Convert module-level to class method (indent)
                    indented = BROADENED_META.replace("def _meta_confidence(prompt, answer):",
                                                      "def _meta_confidence(self, prompt, answer):")
                    indented = "\n".join("    " + line if line.strip() else line
                                        for line in indented.strip().split("\n"))
                    new_src = src[:match2.start()] + indented + "\n\n" + src[match2.end():]
                    py.write_text(new_src, encoding="utf-8")
                    updated += 1
                else:
                    skipped += 1

        except Exception as e:
            errors += 1
            print(f"  ERROR {py.name}: {e}")

    print(f"Updated: {updated}, Skipped: {skipped}, Errors: {errors}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Test patterns only")
    args = parser.parse_args()

    if args.test:
        test_patterns()
    else:
        test_patterns()
        print()
        print("=" * 60)
        print()
        apply_to_all()


if __name__ == "__main__":
    main()
