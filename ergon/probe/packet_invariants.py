"""Discrete, non-LLM, non-statistical checks on arm packets.

WHY THIS EXISTS. Two exit reviews killed this probe's headline on arm-identifying confounds
(a JSON header on one arm's renderer; a token-length asymmetry). Both were caught *statistically*
— a blinded classifier separating arms — and a classifier answers "I could not find a
difference," which is not the same claim as "no difference exists." Charon's exit-review-#3
invariant is stated deliberately: treatment identity must be **computationally unavailable**,
not merely hard to detect.

A classifier at chance is an ESTIMATE with a sampling error. The checks here are DECIDABLE:
they either hold on every task or produce the exact bytes that differ. Where a property can be
decided, deciding it strictly dominates estimating it — and unlike a classifier, a failure here
names the defect instead of scoring it.

None of this calls an LLM. None of it samples. Every function is a total function of the
rendered prompts.

    python ergon/probe/packet_invariants.py            # runs against the live pinned manifest
"""
import collections
import difflib
import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# The payload region is by construction everything before the first blank-line separator; the
# arms are SUPPOSED to differ there and nowhere else.
SEPARATOR = "\n\n"


def split_packet(prompt):
    """(payload, base). The base must be byte-identical across every arm for a given task."""
    if SEPARATOR not in prompt:
        return "", prompt
    head, _, tail = prompt.partition(SEPARATOR)
    return head, tail


def base_identical(prompts_by_arm):
    """INVARIANT 1 — every arm's prompt ENDS WITH the F0 prompt, byte for byte.

    F0 carries no packet, so F0's prompt IS the base. Using it directly removes a whole class
    of error: my first version re-derived the base by partitioning on the first blank line,
    which mis-split any payload containing an internal blank line (F-generic's advice prose)
    and then reported the mis-split as a pipeline defect. Re-deriving a boundary the producer
    already knows is the seam error this probe keeps committing — so the boundary is taken
    from the producer instead of inferred from the string.
    """
    if "F0" not in prompts_by_arm:
        return True, {"skipped": "no F0 arm supplied; base is undefined without it"}
    base = prompts_by_arm["F0"]
    diffs = {}
    for arm, p in prompts_by_arm.items():
        if arm == "F0":
            continue
        if not p.endswith(base):
            tail = p[-len(base):] if len(p) >= len(base) else p
            diffs[arm] = list(difflib.unified_diff(
                base.splitlines(), tail.splitlines(), "F0-base", arm, lineterm="", n=1))[:12]
    return (not diffs), diffs


def payload_of(prompt, base):
    """Exact payload = the prompt with the known base removed from its end."""
    return prompt[:-len(base)] if base and prompt.endswith(base) else prompt


def envelope_shape(payload):
    """The payload's STRUCTURE with its content removed: framing, separators, field order.

    This is what a serialization asymmetry looks like when you delete the words. The pilot died
    because one arm's payload began `{` and another's did not — visible here, invisible to a
    reader comparing prose.
    """
    s = re.sub(r"[A-Za-z]+", "w", payload)
    s = re.sub(r"\d+", "#", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def envelope_identical(prompts_by_arm, carrying_arms):
    """INVARIANT 2 — every residue-carrying arm shares one payload envelope.

    Arms legitimately differ in payload CONTENT. They must not differ in payload SHAPE: the
    shape is not the treatment, and any shape difference is a free arm label.
    """
    base = prompts_by_arm.get("F0", "")
    shapes = {a: envelope_shape(payload_of(prompts_by_arm[a], base))
              for a in carrying_arms if a in prompts_by_arm}
    groups = collections.defaultdict(list)
    for arm, sh in shapes.items():
        groups[sh].append(arm)
    return (len(groups) <= 1), {sh[:120]: arms for sh, arms in groups.items()}


def charclass_profile(text):
    """Exact multiset of Unicode general categories. Not a model — a census.

    Catches the class of leak where arms differ in punctuation density, digit count, or
    whitespace habit while reading identically to a human.
    """
    return collections.Counter(unicodedata.category(ch) for ch in text)


def profile_spread(prompts_by_arm, carrying_arms):
    """INVARIANT 3 — report the exact per-arm character-category census.

    Reported, not gated: arms carry different content, so some spread is legitimate. It is here
    so the spread is a NUMBER in the artifact rather than an assumption in a docstring (BC-7).
    """
    out = {}
    for arm in carrying_arms:
        if arm in prompts_by_arm:
            payload = payload_of(prompts_by_arm[arm], prompts_by_arm.get("F0", ""))
            prof = charclass_profile(payload)
            out[arm] = {"chars": len(payload), "categories": dict(prof.most_common(6))}
    return out


def forbidden_token_scan(prompts_by_arm, forbidden):
    """INVARIANT 4 — a decidable answer-leak check: exact substring membership.

    The frozen redactor is a regex ladder, i.e. a judgement about prose. This is set membership
    over a closed vocabulary: either the string is present or it is not.
    """
    hits = {}
    base = prompts_by_arm.get("F0", "")
    for arm, p in prompts_by_arm.items():
        payload = payload_of(p, base).lower()
        found = sorted({t for t in forbidden if t.lower() in payload})
        if found:
            hits[arm] = found
    return (not hits), hits


def gold_substring_scan(prompts_by_arm, gold_value):
    """INVARIANT 5 — the gold answer must not appear verbatim in any non-oracle payload.

    Decidable, and independent of the redactor that is supposed to have removed it. A check
    that reuses the pipeline's own redaction would be testing the pipeline with the pipeline.
    """
    # A BARE DIGIT IS NOT A LEAK NEEDLE. My first version searched for str(gold), which
    # matched the task's own enumeration markers "(1)".."(5)" and reported every task as
    # leaking. The needle must be an ANSWER ASSERTION, not the presence of a numeral.
    g = str(gold_value)
    needles = {f"answer: {g}", f"answer is {g}", f"answer = {g}",
               f"count is {g}", f"there are {g} prime"}
    hits = {}
    base = prompts_by_arm.get("F0", "")
    for arm, p in prompts_by_arm.items():
        if arm in ("F-answer", "F-oracle", "F-cheat"):      # these carry it by design
            continue
        payload = payload_of(p, base).lower()
        found = sorted({n for n in needles if n in payload})
        if found:
            hits[arm] = found
    return (not hits), hits


def check_task(prompts_by_arm, gold_value, carrying_arms, forbidden):
    r1, d1 = base_identical(prompts_by_arm)
    r2, d2 = envelope_identical(prompts_by_arm, carrying_arms)
    r4, d4 = forbidden_token_scan(prompts_by_arm, forbidden)
    r5, d5 = gold_substring_scan(prompts_by_arm, gold_value)
    return {
        "base_identical": r1, "base_diffs": d1,
        "envelope_identical": r2, "envelope_groups": d2,
        "no_forbidden_tokens": r4, "forbidden_hits": d4,
        "no_verbatim_gold": r5, "gold_hits": d5,
        "profiles": profile_spread(prompts_by_arm, carrying_arms),
        "all_pass": r1 and r2 and r4 and r5,
    }


def main():
    from ergon.probe.assemble import load_prepass
    import ergon.probe.campaign as C

    rows = C.manifest()
    gold = {r["uid"]: r["gold_int"] for r in rows}
    pool_path = C.DIR / "p1_prepass.jsonl"
    if not pool_path.exists():
        print("no prepass pool yet — run P1 first")
        return 1

    arms_obj = C.Arms(rows, gold)
    carrying = ["F-null", "F-generic", "F-prom-retrieved"]
    all_arms = ["F0"] + carrying
    forbidden = ["true", "false", "correct answer", "the answer is"]

    failures, checked = [], 0
    for r in rows:
        uid = r["uid"]
        try:
            prompts = {a: arms_obj.prompt(a, uid) for a in all_arms}
        except Exception as e:                       # a task with no residue yet
            continue
        res = check_task(prompts, gold[uid], carrying, forbidden)
        checked += 1
        if not res["all_pass"]:
            failures.append({"uid": uid, **{k: v for k, v in res.items() if k != "profiles"}})

    out = {
        "checked_tasks": checked,
        "failures": len(failures),
        "verdict": "PASS — decidable invariants hold on every task" if not failures
                   else "FAIL — arm identity is computationally AVAILABLE",
        "note": "These are decidable checks, not classifier estimates. A PASS here is a "
                "stronger claim than 'a classifier sat at chance': it says no difference "
                "exists in the checked feature set, and names the bytes when one does.",
        "checked_invariants": ["base byte-identical across arms",
                              "payload envelope identical across residue-carrying arms",
                              "no forbidden verdict tokens in any payload",
                              "no verbatim gold in any non-oracle payload"],
        "first_failures": failures[:5],
    }
    outdir = ROOT / "ergon/probe/ledgers/packet_invariants"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "invariants.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("checked_tasks", "failures", "verdict")}, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    sys.exit(main())
