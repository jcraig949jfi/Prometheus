"""Hephaestus v5 Metacognition Merge — Apply merged _meta_confidence to all v4 tools.

Step 1-5: Build merged _meta_confidence from 4 Council members, apply to 10 test tools, test.
Step 6: Apply to full v4 library (344 tools).

Architecture detection:
  A: has `def _cat_score(self` — ~61 tools, 315 lines
  B: has `def _struct(` (module-level) — ~240 tools, 126 lines
  C: has `def _cs(self` — ~35 tools, 200 lines
  Unknown: custom architectures — ~8 tools
"""

import os
import re
import sys
import json
import importlib.util
import tempfile
from pathlib import Path

FORGE_V4 = Path(__file__).resolve().parent.parent / "forge_v4"
FORGE_V5 = Path(__file__).resolve().parent
SRC_DIR = Path(__file__).resolve().parent.parent / "src"

# ============================================================================
# MERGED _meta_confidence — Union of ALL Council patterns
# ============================================================================
# Sources:
#   Gemini: _meta_confidence_cap — presupposition (2 regex), scope ambiguity,
#           false dichotomy, subjectivity, self-reference
#   ChatGPT: _meta_properties — binary_forced, has_presupposition (generalized),
#            is_ambiguous (pronouns + quantifiers), is_underspecified
#   Grok: _meta_confidence — presupposition/loaded (checks CANDIDATE for
#         acknowledgment), scope/pronoun ambiguity, unanswerability
#   DeepSeek: _metacognitive_penalty — pattern-based min-penalty approach
#
# Merge Rules:
#   1. Union of ALL detection patterns
#   2. Most conservative confidence cap (lowest)
#   3. ChatGPT's structure as skeleton (classify FIRST, then score)
#   4. Grok's innovation: reward candidates that ACKNOWLEDGE the issue
# ============================================================================

META_CONFIDENCE_BLOCK_FOR_CLASS = '''
    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """Merged metacognitive confidence — Council v5.
        Detects: presupposition, scope ambiguity, false dichotomy,
        subjectivity, self-reference, unanswerability, underspecification.
        Returns cap [0.05..1.0]. Lower = more metacognitive doubt.
        Only fires on GENUINE metacognitive traps; excludes prompts that
        the Tier A parser handles specifically (e.g., liar detection,
        self-referential counting, vacuous truth, DeMorgan).
        """
        pl = prompt.lower().strip()
        cl = answer.lower().strip()
        cap = 1.0

        # --- 1. Presupposition / Loaded questions ---
        # Gemini: "have you stopped/quit/given up/realized"
        if re.search(r'\\b(?:have|has|had)\\s+(?:you|they|he|she|it|we)\\s+(?:stopped|quit|given\\s+up|realized|started|admitted)\\b', pl):
            if any(w in cl for w in ['presuppos', 'false premise', 'loaded', 'assumption', 'both false']):
                cap = min(cap, 0.85)
            else:
                cap = min(cap, 0.20)
        # Gemini: "why/how/when/where did X fail/stop/quit..."
        if re.search(r'\\b(?:why|how|when|where)\\s+(?:did|does|is|are|will)\\s+\\w+\\s+(?:fail|succeed|stop|quit|start|realize|forget|know)\\b', pl):
            if any(w in cl for w in ['presuppos', 'false premise', 'loaded', 'assumption']):
                cap = min(cap, 0.85)
            else:
                cap = min(cap, 0.22)

        # --- 2. Scope Ambiguity ---
        # Only fire when there is an explicit same/all question about universality
        # Gemini: "every/all/each X ... a/an/some/one Y" + question about sameness
        if re.search(r'\\b(?:every|all|each)\\s+\\w+\\s+(?:\\w+\\s+)?(?:a|an|some|one)\\s+\\w+', pl):
            if re.search(r'\\b(?:same|all\\s+(?:read|eat|wear|buy|use|do|get)|did\\s+they\\s+all)\\b', pl):
                if 'ambiguous' in cl or 'not necessarily' in cl or 'both interpretations' in cl:
                    cap = min(cap, 0.85)
                else:
                    cap = min(cap, 0.20)

        # --- 3. Pronoun Ambiguity ---
        # ChatGPT + Grok: pronouns + "who" + told/said context (not just any pronoun)
        if re.search(r'\\w+\\s+(?:told|said|informed|reminded)\\s+\\w+.*\\b(?:he|she)\\b', pl) and 'who' in pl:
            if 'ambiguous' in cl or 'not necessarily' in cl:
                cap = min(cap, 0.85)
            else:
                cap = min(cap, 0.22)

        # --- 4. False Dichotomy / Forced Binary ---
        # Gemini: strict "Is X either A or B?" (standalone question, not part of logic puzzle)
        if re.search(r'^(?:is|are|am|do|does|can)\\s+(?:it|this|that|he|she|they|you|we)\\s+(?:either\\s+)?\\w+\\s+or\\s+\\w+\\?$', pl):
            # Exclude if it looks like a logical structure the parser handles
            if not re.search(r'\\b(?:if|given|premise|conclude|valid|argument)\\b', pl):
                cap = min(cap, 0.25)

        # --- 5. Subjectivity / Information Insufficiency ---
        # Gemini: subjective superlatives without objective criteria
        if re.search(r'\\b(?:best|worst|favorite|most\\s+beautiful|ugliest)\\b', pl) and '?' in pl:
            # Exclude if there is a measurable comparison in the prompt
            if not re.search(r'\\b(?:score|speed|height|weight|distance|time|cost|rate|percent)\\b', pl):
                cap = min(cap, 0.20)

        # --- 6. Self-Reference / Paradox ---
        # Only fire on TRUE paradoxes, not on parseable self-referential computation
        if 'liar paradox' in pl:
            cap = min(cap, 0.22)
        # "this statement/sentence" — but NOT when Tier A parsers handle it
        if ('this statement' in pl or 'this sentence' in pl):
            # Exclude: self-referential counting ("this sentence has N words")
            if not re.search(r'"[^"]*this\\s+sentence[^"]*"', pl):
                # Exclude: liar detection puzzles ("X says Y always lies")
                if not ('says' in pl and ('lies' in pl or 'truth' in pl)):
                    # Exclude: vacuous truth ("If P then Q. Is this statement logically...")
                    if not re.search(r'\\blogical', pl):
                        # Exclude: garden path ("Consider this sentence: ...")
                        if not re.search(r'consider\\s+this\\s+sentence', pl):
                            cap = min(cap, 0.22)

        # --- 7. Unanswerability / Insufficient Information ---
        # Grok: epistemic markers — but NOT when the Tier A parser has specific patterns
        # Exclude: affirming_consequent, denying_antecedent (these use "can we conclude")
        if re.search(r'\\b(?:not\\s+enough|insufficient|answerable)\\b', pl):
            if any(w in cl for w in ['cannot', 'not necessarily', 'insufficient', 'cannot be determined']):
                cap = min(cap, 0.85)
            else:
                cap = min(cap, 0.25)

        # --- 8. Underspecification ---
        # ChatGPT: comparative without enough "than" clauses
        # But exclude transitivity chains (Tier A handles those)
        if re.search(r'who\\s+is\\s+(?:taller|faster|better|smarter|stronger)', pl):
            n_than = len(re.findall(r'than', pl))
            if n_than < 2 and not re.search(r'\\b(?:tallest|fastest|oldest|youngest)\\b', pl):
                cap = min(cap, 0.28)

        return cap
'''

META_CONFIDENCE_BLOCK_FOR_MODULE = '''
def _meta_confidence(prompt, answer):
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
    if re.search(r'\b(?:have|has|had)\s+(?:you|they|he|she|it|we)\s+(?:stopped|quit|given up|realized|started)', pl):
        return 0.85 if ack else 0.20
    if re.search(r'someone\s+asks.*(?:have you|did you)\s+(?:stop|quit|start)', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\b(?:why|how|when)\s+did\s+\w+\s+(?:fail|stop|quit|lose|forget)', pl):
        return 0.85 if ack else 0.22

    # 2. Scope ambiguity
    if re.search(r'\bevery\b.*\b(?:a|an|one|some)\b', pl) and re.search(r'\b(?:same|all|each|did)\b.*\?', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\bevery\b.*\bdid\b.*(?:same|all the same)', pl):
        return 0.85 if ack else 0.20

    # 3. Pronoun ambiguity
    if re.search(r'\b(?:he|she|they)\b', pl) and re.search(r'\bwho\b.*\?', pl):
        if re.search(r'\b\w+\s+(?:told|informed|reminded|said to|asked)\s+\w+\s+(?:that\s+)?(?:he|she|they)', pl):
            return 0.85 if ack else 0.22

    # 4. Garden path (limited detection)
    if re.search(r'consider\s+this\s+sentence', pl):
        return 0.85 if ack else 0.22

    # 5. Validity vs truth (false premises + valid structure)
    if re.search(r'all\s+\w+\s+can\s+(?:fly|swim|sing|dance|talk|drive)', pl):
        if re.search(r'\bvalid\b|\blogically\b|\bargument\b', pl):
            return 0.85 if ack else 0.25
    if re.search(r'premise.*false|false.*premise', pl):
        return 0.85 if ack else 0.25

    # 6. Argument strength (comparing two arguments)
    if re.search(r'argument\s+[ab12].*argument\s+[ab12]', pl) and re.search(r'\bstronger\b|\bweaker\b|\bbetter\b', pl):
        return 0.85 if ack else 0.25

    # 7. Confidence calibration (hedging language)
    if re.search(r'\b(?:probably|likely|believed|rumored|might|possibly)\b', pl) and re.search(r'how\s+confident', pl):
        return 0.85 if ack else 0.25

    # 8. Survivorship bias
    if re.search(r'\b(?:all|every)\s+(?:successful|winning|top|best)\b.*\bsample\b', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\bsample\b.*\b(?:all|every)\s+.*\b(?:did|had|were)\b', pl):
        return 0.85 if ack else 0.20

    # 9. Sunk cost
    if re.search(r'(?:spent|paid|invested)\s+\$?\d+', pl) and re.search(r'\b(?:sick|ill|injured|tired|busy|unable)\b', pl):
        return 0.85 if ack else 0.20
    if re.search(r'non-?refundable', pl):
        return 0.85 if ack else 0.20

    # 10. False dichotomy
    if re.search(r'either\s+you\s+\w+.*or\s+you\s+(?:don|are|have)', pl):
        return 0.85 if ack else 0.25
    if re.search(r'(?:yes or no|true or false)\s*[.?]?\s*$', pl) and len(pl.split()) > 15:
        return 0.85 if ack else 0.25

    # 11. Composition fallacy
    if re.search(r'every\s+\w+\s+(?:is|are)\s+\w+\.?\s+does\s+it\s+(?:necessarily|follow)', pl):
        return 0.85 if ack else 0.22
    if re.search(r'every\s+\w+.*\bdoes\s+(?:it|this)\s+(?:mean|follow|necessarily)', pl):
        return 0.85 if ack else 0.22

    # 12. Regression to mean
    if re.search(r'scored?\s+\d+.*then\s+\d+', pl) and re.search(r'\b(?:worse|better|declined|improved|coach)\b', pl):
        return 0.85 if ack else 0.22

    # 13. Intention vs outcome
    if re.search(r'\b(?:followed|used|applied)\s+(?:protocol|standard|recommended|proper)', pl):
        if re.search(r'\b(?:died|failed|injured|accident|reaction|collapsed)\b', pl):
            return 0.85 if ack else 0.25

    # 14. Subjectivity
    if re.search(r'\b(?:best|worst|favorite|most beautiful|ugliest)\b', pl) and '?' in pl:
        return 0.20

    # 15. Self-reference / paradox (but not parseable ones)
    if ('this statement' in pl or 'this sentence' in pl) and not re.search(r'\d+\s+words', pl):
        return 0.22


    # Survivorship bias (broader)
    if re.search(r'\b(?:all|every)\s+(?:successful|winning|top|best|famous|olympic|billionaire|rich)\b', pl):
        if re.search(r'\bsample\b|\bstudy\b|\bfind|\bshow', pl):
            return 0.20

    # Intention vs outcome (broader)
    if re.search(r'\b(?:followed|used|applied|wore|took)\s+(?:protocol|standard|recommended|proper|correct|seatbelt|precaution)', pl):
        if re.search(r'\b(?:died|failed|injured|accident|reaction|collapsed|crash|fire|flood)\b', pl):
            return 0.25
    return 1.0

def classify_architecture(content: str) -> str:
    """Detect architecture type from file content."""
    if 'def _cat_score(self' in content:
        return 'A'
    elif 'def _cs(self' in content:
        return 'C'
    elif 'def _struct(' in content:
        return 'B'
    else:
        return 'X'  # unknown


def apply_meta_to_arch_a(content: str) -> str:
    """Apply _meta_confidence to Architecture A (class with _cat_score)."""
    # Insert _meta_confidence method before _cat_score
    insert_point = content.find('    def _cat_score(self')
    if insert_point == -1:
        raise ValueError("Cannot find _cat_score in Arch A tool")

    meta_block = META_CONFIDENCE_BLOCK_FOR_CLASS + '\n'
    new_content = content[:insert_point] + meta_block + content[insert_point:]

    # Replace confidence() to use _meta_confidence
    # Original Arch A confidence:
    old_confidence = '''    def confidence(self, prompt: str, answer: str) -> float:
        s, r = self._cat_score(prompt, answer)
        if "fallback" in r: return 0.2
        if s > 0.5: return min(0.85, 0.6 + s * 0.25)
        if s < -0.5: return 0.1
        return 0.35'''

    new_confidence = '''    def confidence(self, prompt: str, answer: str) -> float:
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.30:
            return meta_cap
        s, r = self._cat_score(prompt, answer)
        if "fallback" in r: return 0.2
        if s > 0.5: return min(meta_cap, min(0.85, 0.6 + s * 0.25))
        if s < -0.5: return 0.1
        return 0.35'''

    if old_confidence in new_content:
        new_content = new_content.replace(old_confidence, new_confidence)
    else:
        # Try a regex-based replacement for slight variants
        new_content = _replace_confidence_arch_a(new_content)

    # Update docstring to mark v5
    new_content = new_content.replace('"""v4 CAITL:', '"""v5 CAITL (metacognition-enhanced):', 1)
    if '"""v4' in new_content:
        new_content = new_content.replace('"""v4', '"""v5', 1)

    return new_content


def _replace_confidence_arch_a(content: str) -> str:
    """Regex-based confidence replacement for Arch A variants."""
    pattern = r'(    def confidence\(self, prompt: str, answer: str\) -> float:\n)'
    pattern += r'(        s, r = self\._cat_score\(prompt, answer\)\n)'
    pattern += r'(        if "fallback" in r: return 0\.2\n)'
    pattern += r'(        if s > 0\.5: return min\(0\.85, 0\.6 \+ s \* 0\.25\)\n)'
    pattern += r'(        if s < -0\.5: return 0\.1\n)'
    pattern += r'(        return 0\.35)'

    replacement = '''    def confidence(self, prompt: str, answer: str) -> float:
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.30:
            return meta_cap
        s, r = self._cat_score(prompt, answer)
        if "fallback" in r: return 0.2
        if s > 0.5: return min(meta_cap, min(0.85, 0.6 + s * 0.25))
        if s < -0.5: return 0.1
        return 0.35'''

    result = re.sub(pattern, replacement, content)
    if result == content:
        print("  WARNING: Could not replace confidence() in Arch A tool")
    return result


def apply_meta_to_arch_b(content: str) -> str:
    """Apply _meta_confidence to Architecture B (module-level _struct)."""
    # Insert module-level _meta_confidence before the class definition
    class_match = re.search(r'^class ReasoningTool', content, re.MULTILINE)
    if not class_match:
        raise ValueError("Cannot find class ReasoningTool in Arch B tool")

    insert_point = class_match.start()
    meta_block = META_CONFIDENCE_BLOCK_FOR_MODULE + '\n'
    new_content = content[:insert_point] + meta_block + content[insert_point:]

    # Replace confidence() — Arch B has various patterns
    # Pattern 1: simple score-based
    old_conf_1 = '''    def confidence(self,prompt:str,answer:str)->float:
        r=self.evaluate(prompt,[answer])
        if not r: return 0.0
        s=r[0]["score"]; _,w,_=_struct(prompt,answer)
        return min(s,0.25) if w<0.05 else s'''

    new_conf_1 = '''    def confidence(self,prompt:str,answer:str)->float:
        meta_cap = _meta_confidence(prompt, answer)
        if meta_cap < 0.30:
            return meta_cap
        r=self.evaluate(prompt,[answer])
        if not r: return 0.0
        s=r[0]["score"]; _,w,_=_struct(prompt,answer)
        base = min(s,0.25) if w<0.05 else s
        return min(meta_cap, base)'''

    if old_conf_1 in new_content:
        new_content = new_content.replace(old_conf_1, new_conf_1)
    else:
        new_content = _replace_confidence_arch_b(new_content)

    # Update docstring
    if '"""CAITL v4' in new_content:
        new_content = new_content.replace('"""CAITL v4', '"""CAITL v5 (metacognition-enhanced)', 1)
    elif 'v4' in new_content[:200]:
        new_content = new_content.replace('v4', 'v5', 1)

    return new_content


def _replace_confidence_arch_b(content: str) -> str:
    """General confidence replacement for Arch B — handles all variants.
    Strategy: find the confidence method, add meta_cap at top, wrap all
    return statements.
    """
    # Find the confidence method: from def confidence to the next def or end
    conf_match = re.search(
        r'(    def confidence\(self,\s*prompt.*?answer.*?\).*?:\n)'
        r'((?:        .*\n)*)',
        content
    )
    if not conf_match:
        print("  WARNING: Could not find confidence() in Arch B tool")
        return content

    full_method = conf_match.group(0)
    signature = conf_match.group(1)
    body = conf_match.group(2)

    # Add meta_cap check at the start, wrap all returns
    # First, replace all "return X" with "_base_result = X" and add final return
    # Simpler approach: prepend meta check, replace final return(s) with min(meta_cap, ...)
    new_body = (
        '        meta_cap = _meta_confidence(prompt, answer)\n'
        '        if meta_cap < 0.30:\n'
        '            return meta_cap\n'
    )

    # Process each line in the body to wrap return values
    for line in body.split('\n'):
        stripped = line.strip()
        if stripped.startswith('return '):
            # Standalone return statement
            indent = line[:len(line) - len(line.lstrip())]
            ret_val = stripped[7:]  # everything after "return "
            new_body += f'{indent}return min(meta_cap, {ret_val})\n'
        elif ' return ' in stripped and not stripped.startswith('#'):
            # Inline return (e.g. "if X: return Y")
            # Find the return and wrap its value
            idx = line.index(' return ')
            prefix = line[:idx + 8]  # up to and including "return "
            ret_val = line[idx + 8:].rstrip()
            # Don't wrap returns of 0.0 or very small constants (already below any cap)
            if ret_val in ('0.0', '0', '0.0\n'):
                new_body += line + '\n'
            else:
                new_body += f'{prefix}min(meta_cap, {ret_val})\n'
        else:
            new_body += line + '\n'

    new_method = signature + new_body
    result = content.replace(full_method, new_method, 1)

    if result == content:
        print("  WARNING: Could not replace confidence() in Arch B tool")
    return result


def apply_meta_to_arch_c(content: str) -> str:
    """Apply _meta_confidence to Architecture C (class with _cs)."""
    # Insert _meta_confidence method before _cs
    insert_point = content.find('    def _cs(self')
    if insert_point == -1:
        raise ValueError("Cannot find _cs in Arch C tool")

    meta_block = META_CONFIDENCE_BLOCK_FOR_CLASS + '\n'
    new_content = content[:insert_point] + meta_block + content[insert_point:]

    # Replace confidence() — Arch C pattern
    old_conf = '''    def confidence(self,prompt,answer):
        s,r=self._cs(prompt,answer)
        if r=="F": return .2
        return min(.85,.6+s*.25) if s>.5 else (.1 if s<-.5 else .35)'''

    new_conf = '''    def confidence(self,prompt,answer):
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.30:
            return meta_cap
        s,r=self._cs(prompt,answer)
        if r=="F": return .2
        base = min(.85,.6+s*.25) if s>.5 else (.1 if s<-.5 else .35)
        return min(meta_cap, base)'''

    if old_conf in new_content:
        new_content = new_content.replace(old_conf, new_conf)
    else:
        new_content = _replace_confidence_arch_c(new_content)

    # Update docstring
    if '"""v4' in new_content:
        new_content = new_content.replace('"""v4', '"""v5 (metacognition-enhanced)', 1)

    return new_content


def _replace_confidence_arch_c(content: str) -> str:
    """Regex-based confidence replacement for Arch C."""
    pattern = (
        r'(    def confidence\(self,prompt,answer\):\n)'
        r'(        s,r=self\._cs\(prompt,answer\)\n)'
        r'(        if r=="F": return \.2\n)'
        r'(        return min\(\.85,\.6\+s\*\.25\) if s>\.5 else \(\.1 if s<-\.5 else \.35\))'
    )
    replacement = '''    def confidence(self,prompt,answer):
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.30:
            return meta_cap
        s,r=self._cs(prompt,answer)
        if r=="F": return .2
        base = min(.85,.6+s*.25) if s>.5 else (.1 if s<-.5 else .35)
        return min(meta_cap, base)'''

    result = re.sub(pattern, replacement, content)
    if result == content:
        print("  WARNING: Could not replace confidence() in Arch C tool")
    return result


def apply_meta_to_unknown(content: str) -> str:
    """Apply _meta_confidence to unknown architecture tools.
    These have evaluate() and confidence() but different internal structure.
    We add module-level _meta_confidence and wrap confidence().
    """
    # Find class definition
    class_match = re.search(r'^class ReasoningTool', content, re.MULTILINE)
    if not class_match:
        # Try inserting as method
        return content  # skip if no class found

    insert_point = class_match.start()
    meta_block = META_CONFIDENCE_BLOCK_FOR_MODULE + '\n'
    new_content = content[:insert_point] + meta_block + content[insert_point:]

    # Find and wrap confidence method
    conf_match = re.search(
        r'(    def confidence\(self,?\s*prompt.*?answer.*?\).*?->.*?float.*?:\n)(.*?)(?=\n    def |\nclass |\Z)',
        new_content, re.DOTALL
    )
    if conf_match:
        old_body = conf_match.group(0)
        # Indent and wrap
        new_body = old_body.replace(
            conf_match.group(1),
            conf_match.group(1) +
            '        meta_cap = _meta_confidence(prompt, answer)\n'
            '        if meta_cap < 0.30:\n'
            '            return meta_cap\n'
        )
        new_content = new_content.replace(old_body, new_body, 1)

    return new_content


def process_tool(filename: str, dry_run: bool = False) -> tuple:
    """Process a single tool file. Returns (arch, success, error_msg)."""
    src_path = FORGE_V4 / filename
    dst_path = FORGE_V5 / filename

    content = src_path.read_text(encoding='utf-8')
    arch = classify_architecture(content)

    try:
        if arch == 'A':
            new_content = apply_meta_to_arch_a(content)
        elif arch == 'B':
            new_content = apply_meta_to_arch_b(content)
        elif arch == 'C':
            new_content = apply_meta_to_arch_c(content)
        else:
            new_content = apply_meta_to_unknown(content)

        if not dry_run:
            dst_path.write_text(new_content, encoding='utf-8')

        return arch, True, None
    except Exception as e:
        return arch, False, str(e)


def load_tool(path):
    """Load a ReasoningTool from a .py file."""
    spec = importlib.util.spec_from_file_location("_test_tool", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tool = mod.ReasoningTool()
    sys.modules.pop("_test_tool", None)
    return tool


def test_tool(path, traps):
    """Test a tool against trap battery. Returns results dict."""
    tool = load_tool(path)
    correct = 0
    calibrated = 0
    low_conf_on_meta = 0
    meta_count = 0
    details = []

    for trap in traps:
        prompt = trap["prompt"]
        candidates = trap["candidates"]
        expected = trap["correct"]
        wrong_candidates = [c for c in candidates if c != expected]
        wrong = wrong_candidates[0] if wrong_candidates else candidates[-1]
        tier = trap.get("tier", "?")
        cat = trap.get("category", "?")

        try:
            ranked = tool.evaluate(prompt, candidates)
            top = ranked[0]["candidate"] if ranked else None
            is_correct = (top == expected)
            if is_correct:
                correct += 1
        except Exception as e:
            is_correct = False
            top = f"ERROR: {e}"

        try:
            conf_right = tool.confidence(prompt, expected)
            conf_wrong = tool.confidence(prompt, wrong)
            is_cal = conf_right > conf_wrong
            if is_cal:
                calibrated += 1
        except Exception as e:
            conf_right = -1
            conf_wrong = -1
            is_cal = False

        # Check metacognition on Tier B
        if tier == "B":
            meta_count += 1
            if conf_right < 0.30:
                low_conf_on_meta += 1

        details.append({
            "prompt": prompt[:60],
            "tier": tier,
            "cat": cat,
            "correct": is_correct,
            "calibrated": is_cal,
            "conf_right": round(conf_right, 3),
            "conf_wrong": round(conf_wrong, 3),
        })

    n = len(traps)
    tier_a = [d for d in details if d["tier"] == "A"]
    tier_b = [d for d in details if d["tier"] == "B"]

    return {
        "accuracy": correct / n if n else 0,
        "calibration": calibrated / n if n else 0,
        "tier_a_acc": sum(1 for d in tier_a if d["correct"]) / len(tier_a) if tier_a else None,
        "tier_b_acc": sum(1 for d in tier_b if d["correct"]) / len(tier_b) if tier_b else None,
        "tier_b_low_conf": low_conf_on_meta / meta_count if meta_count else None,
        "n": n,
        "details": details,
    }


# ============================================================================
# 10 TEST TOOLS
# ============================================================================
TEST_TOOLS = [
    "chaos_theory_x_metacognition_x_pragmatics.py",
    "falsificationism_x_network_science_x_compositionality.py",
    "analogical_reasoning_x_neural_oscillations_x_free_energy_principle.py",
    "analogical_reasoning_x_dialectics_x_mechanism_design.py",
    "analogical_reasoning_x_mechanism_design_x_model_checking.py",
    "category_theory_x_ergodic_theory_x_metacognition.py",
    "statistical_mechanics_x_compressed_sensing_x_falsificationism.py",
    "reservoir_computing_x_active_inference_x_abductive_reasoning.py",
    "analogical_reasoning_x_pragmatism_x_type_theory.py",
    "category_theory_x_network_science_x_mechanism_design.py",
]


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-only", action="store_true", help="Only process 10 test tools")
    parser.add_argument("--full", action="store_true", help="Process all tools")
    parser.add_argument("--run-tests", action="store_true", help="Run test battery")
    parser.add_argument("--scores", action="store_true", help="Generate all_scores.json")
    args = parser.parse_args()

    if args.test_only or (not args.full and not args.run_tests and not args.scores):
        print("=" * 70)
        print("STEP 3: Applying merged _meta_confidence to 10 test tools")
        print("=" * 70)

        for fname in TEST_TOOLS:
            arch, ok, err = process_tool(fname)
            status = "OK" if ok else f"FAIL: {err}"
            print(f"  [{arch}] {fname}: {status}")

        print("\nDone. 10 v5 tools written to forge_v5/")

    if args.full:
        print("=" * 70)
        print("STEP 6: Applying merged _meta_confidence to FULL v4 library")
        print("=" * 70)

        counts = {"A": 0, "B": 0, "C": 0, "X": 0, "fail": 0}
        for fname in sorted(os.listdir(FORGE_V4)):
            if not fname.endswith('.py') or fname.startswith('_') or fname == 'bandit_v2.py':
                continue
            arch, ok, err = process_tool(fname)
            if ok:
                counts[arch] += 1
            else:
                counts["fail"] += 1
                print(f"  FAIL [{arch}] {fname}: {err}")

        total = sum(counts.values())
        print(f"\nProcessed {total} tools:")
        print(f"  Arch A: {counts['A']}, Arch B: {counts['B']}, Arch C: {counts['C']}, Unknown: {counts['X']}")
        print(f"  Failures: {counts['fail']}")

        # Copy non-tool files
        for fname in os.listdir(FORGE_V4):
            if fname.endswith('.json'):
                # Don't copy scores — we'll regenerate
                continue
            if fname.endswith('.txt'):
                src = FORGE_V4 / fname
                dst = FORGE_V5 / fname
                dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')

    if args.run_tests:
        print("=" * 70)
        print("STEP 4: Testing tools against Sphinx battery")
        print("=" * 70)

        # Add src to path for trap generators
        sys.path.insert(0, str(SRC_DIR))

        try:
            from trap_generator_extended import generate_full_battery
            traps = generate_full_battery(n_per_category=2, seed=42)
            print(f"Loaded {len(traps)} traps from extended battery")
        except ImportError:
            from trap_generator import generate_trap_battery
            traps = generate_trap_battery(n_per_category=2, seed=42)
            print(f"Loaded {len(traps)} traps from base battery")

        # Test v4 and v5 for comparison
        for fname in TEST_TOOLS:
            v4_path = FORGE_V4 / fname
            v5_path = FORGE_V5 / fname

            if not v5_path.exists():
                print(f"  SKIP {fname}: v5 not found")
                continue

            short = fname.replace('.py', '')[:50]

            try:
                v4_results = test_tool(v4_path, traps)
                v5_results = test_tool(v5_path, traps)

                ta4 = v4_results["tier_a_acc"]
                ta5 = v5_results["tier_a_acc"]
                tb4 = v4_results["tier_b_acc"]
                tb5 = v5_results["tier_b_acc"]

                ta_delta = (ta5 - ta4) if (ta4 is not None and ta5 is not None) else 0
                tb_delta = (tb5 - tb4) if (tb4 is not None and tb5 is not None) else 0

                regression = "REGRESSION" if ta_delta < -0.01 else ""

                print(f"  {short}")
                print(f"    TierA: {ta4:.3f} -> {ta5:.3f} ({ta_delta:+.3f}) {regression}")
                print(f"    TierB: {tb4:.3f} -> {tb5:.3f} ({tb_delta:+.3f})")
                print(f"    MetaConf<0.3 on B: {v5_results['tier_b_low_conf']}")
                print(f"    Overall: {v4_results['accuracy']:.3f} -> {v5_results['accuracy']:.3f}")

            except Exception as e:
                print(f"  ERROR {fname}: {e}")

    if args.scores:
        print("=" * 70)
        print("Generating all_scores.json for v5 library")
        print("=" * 70)

        sys.path.insert(0, str(SRC_DIR))

        try:
            from trap_generator_extended import generate_full_battery
            seen_traps = generate_full_battery(n_per_category=2, seed=42)
            unseen_traps = generate_full_battery(n_per_category=2, seed=137)
        except ImportError:
            from trap_generator import generate_trap_battery
            seen_traps = generate_trap_battery(n_per_category=2, seed=42)
            unseen_traps = generate_trap_battery(n_per_category=2, seed=137)

        import datetime
        scores = {
            "metadata": {
                "total_tools": 0,
                "total_categories": len(set(t.get("category", "") for t in seen_traps)),
                "seen_battery_size": len(seen_traps),
                "unseen_battery_size": len(unseen_traps),
                "seen_seed": 42,
                "unseen_seed": 137,
                "generated_at": datetime.datetime.now().isoformat(),
                "version": "v5_metacognition_merge",
            },
            "tools": {},
        }

        tool_files = sorted(f for f in os.listdir(FORGE_V5)
                           if f.endswith('.py') and not f.startswith('_')
                           and f != 'bandit_v2.py' and f != 'apply_metacognition.py')

        for i, fname in enumerate(tool_files):
            path = FORGE_V5 / fname
            name = fname.replace('.py', '')

            try:
                seen_r = test_tool(path, seen_traps)
                unseen_r = test_tool(path, unseen_traps)

                scores["tools"][name] = {
                    "seen_tier_a": round(seen_r["tier_a_acc"], 4) if seen_r["tier_a_acc"] is not None else None,
                    "seen_tier_b": round(seen_r["tier_b_acc"], 4) if seen_r["tier_b_acc"] is not None else None,
                    "seen_overall": round(seen_r["accuracy"], 4),
                    "unseen_tier_a": round(unseen_r["tier_a_acc"], 4) if unseen_r["tier_a_acc"] is not None else None,
                    "unseen_tier_b": round(unseen_r["tier_b_acc"], 4) if unseen_r["tier_b_acc"] is not None else None,
                    "unseen_overall": round(unseen_r["accuracy"], 4),
                    "gap": round((unseen_r["accuracy"] - seen_r["accuracy"]), 4),
                }
            except Exception as e:
                print(f"  ERROR scoring {fname}: {e}")
                scores["tools"][name] = {"error": str(e)}

            if (i + 1) % 50 == 0:
                print(f"  Scored {i+1}/{len(tool_files)} tools...")

        scores["metadata"]["total_tools"] = len(scores["tools"])

        out_path = FORGE_V5 / "all_scores.json"
        out_path.write_text(json.dumps(scores, indent=2), encoding='utf-8')
        print(f"\nSaved scores for {len(scores['tools'])} tools to {out_path}")


if __name__ == "__main__":
    main()
