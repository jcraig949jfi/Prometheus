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


_LIST_RUN = re.compile(r"(?:[^\s,]+)(?:\s*,\s*[^\s,]+)+")


def framing_skeleton(payload):
    """The payload's FRAMING: literal structure with all content-sized regions collapsed.

    Third attempt at this abstraction, and the first two are worth recording because both
    produced false alarms against the primary endpoint:
      1. per-task byte equality of `envelope_shape` — too strict; a ledger sequence number that
         the redactor treats differently at one digit vs two made 21/200 packets differ.
      2. multiset equality of `envelope_shape` — still wrong, because `envelope_shape` maps
         each WORD to `w` and therefore preserves LIST LENGTH. The method census is a
         comma-separated list whose length is content, so arms carrying different content were
         guaranteed to differ. I was measuring content and calling it shape.

    Here a comma-separated run of any length collapses to a single `<list>` token, so what
    remains is framing only: field order, brackets, separators, labels.
    """
    s = _LIST_RUN.sub("<list>", payload)
    s = re.sub(r"[A-Za-z]+", "w", s)
    s = re.sub(r"\d+", "#", s)
    return re.sub(r"[ 	]+", " ", s).strip()


def envelope_multiset_identical(per_task_prompts, arm_a, arm_b):
    """INVARIANT 2b — the right decidable form of "shape cannot identify the arm".

    Per-task envelope equality is TOO STRICT: benign metadata (a ledger sequence number that
    the redactor treats differently at one digit vs two) makes individual packets differ
    without carrying any arm signal. Measured on this family: F-null and F-prom each show the
    variant on 9/200 tasks, asymmetric on 2 tasks in each direction — symmetric noise.

    The property that actually matters is that the two arms produce the SAME MULTISET of
    envelope shapes. If the distributions are identical, no shape statistic can separate the
    arms, and that is decidable — no classifier, no sampling error.

    Scoped honestly: this licenses "shape cannot identify the arm", NOT "shape is constant".
    A harmless-because-symmetric argument is scoped to the comparison it was made in.
    """
    a = collections.Counter()
    b = collections.Counter()
    for prompts in per_task_prompts:
        base = prompts.get("F0", "")
        if arm_a in prompts:
            a[framing_skeleton(payload_of(prompts[arm_a], base))] += 1
        if arm_b in prompts:
            b[framing_skeleton(payload_of(prompts[arm_b], base))] += 1
    return a == b, {"only_in_" + arm_a: dict((a - b).most_common(3)),
                    "only_in_" + arm_b: dict((b - a).most_common(3))}


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


# ---------------------------------------------------------------------------------------
# SLOT-SCOPED INVARIANTS (added 2026-08-25, after the fourth instance of the same class).
#
# The class: an arm label that lives where the checks are not looking. Instances to date --
#   1. a JSON header on one arm's renderer                       (killed exit review #1)
#   2. a token-length asymmetry                                  (killed exit review #2)
#   3. the literal pool token `generic_pool`                     (caught by this file's author)
#   4. a lead line on 2 of 6 arms + a per-arm numeric slug band  (caught 2026-08-25)
#
# Instance 4 survived THREE checks at once, and the reason is structural rather than careless:
#   - `envelope_shape` and `framing_skeleton` erase digit runs to make shape comparable, so a
#     numeric band label is invisible to them BY CONSTRUCTION;
#   - `matches_template` only sees the region it is handed, and the lead line sat outside it;
#   - the isomorphism test stripped the lead line before matching, calling it "shared" when it
#     was present on two arms of six.
# Adding a fifth ad-hoc scan would only invite a fifth hiding place. So these checks change the
# frame instead: `matches_template` decomposes a packet into exactly three slots, and each slot
# is then given an explicit arm-invariance obligation.
#
#   frame     -> arm-invariant for free once conformance holds   (INVARIANT 6a)
#   slug      -> must not carry arm identity, in words or digits (INVARIANT 6b)
#   items     -> THE TREATMENT. Exempt by design; the factorial varies it on purpose.
#   sparsity  -> a property of the task record, not of the arm   (INVARIANT 6c)
#
# The exemption is what makes this honest. A check forbidding all cross-arm difference would
# forbid the experiment; naming WHICH slot is allowed to differ is the entire content of the
# claim. Everything outside `items` is obliged to be arm-invariant, and now decidably is.


def template_conformance(prompts_by_arm, carrying_arms):
    """INVARIANT 6a -- every carrying arm's payload matches the shared template ON ITS FULL
    TEXT: no stripping, no leading-line exemption, no per-arm special case.

    The predecessor of this check accepted a caller-supplied prefix by deleting it first. A
    check that deletes a region before inspecting it cannot report on that region, and the
    deleted region is exactly where a caller-controlled label goes.
    """
    from ergon.probe.packet_render import matches_template
    base = prompts_by_arm.get("F0", "")
    bad, slots = {}, {}
    for arm in carrying_arms:
        if arm not in prompts_by_arm:
            continue
        payload = payload_of(prompts_by_arm[arm], base)
        ok, sl = matches_template(payload)
        if ok:
            slots[arm] = sl
        else:
            bad[arm] = payload[:160]
    return (not bad), bad, slots


def slug_pool_shared(slots_by_arm):
    """INVARIANT 6b(i) -- the slug's POOL TOKEN is one shared literal across every arm.

    This is the `generic_pool` defect: a slug whose SHAPE matched a real id while its words
    named the arm in plain text. Framing checks can never catch it, because erasing words is
    what they do.
    """
    pools = {arm: sl["slug"].rsplit("-", 2)[0] for arm, sl in slots_by_arm.items()}
    return (len(set(pools.values())) <= 1), pools


def slug_bands_not_separable(per_task_slots):
    """INVARIANT 6b(ii) -- no single threshold separates any arm pair's slug indices.

    A band label is a property of the DISTRIBUTION, not of one packet: per task each arm has
    a single index and "separable" is meaningless, so this one is computed over the whole
    manifest. Separability, not equality, is the right test -- indices SHOULD differ between
    arms, because they identify different records. What they must not do is occupy disjoint
    numeric bands.

    This is the check the +40000/+50000/+60000/+70000 offsets would have failed on every task,
    and the one no shape abstraction could have expressed, since all of them delete digits.
    """
    vals = collections.defaultdict(list)
    for slots in per_task_slots:
        for arm, sl in slots.items():
            try:
                vals[arm].append(int(sl["slug"].rsplit("-", 1)[1]))
            except (ValueError, IndexError):
                pass
    arms = sorted(vals)
    separable = {}
    for i, a in enumerate(arms):
        for b in arms[i + 1:]:
            va, vb = vals[a], vals[b]
            if va and vb and (max(va) < min(vb) or max(vb) < min(va)):
                separable["%s|%s" % (a, b)] = {a: [min(va), max(va)], b: [min(vb), max(vb)]}
    return (not separable), {"ranges": {a: [min(v), max(v)] for a, v in vals.items()},
                             "separable_pairs": separable}


def sparsity_arm_invariant(slots_by_arm):
    """INVARIANT 6c -- for a given task the sparsity slot is identical across arms.

    It reports what the substrate failed to record for THIS task, which is a fact about the
    record. If it varies by arm, the arm is editing the record it claims to be reporting, and
    the difference is a free label.
    """
    seen = {arm: sl["sparsity"] for arm, sl in slots_by_arm.items()}
    distinct = set(seen.values())
    return (len(distinct) <= 1), ({} if len(distinct) <= 1
                                  else {a: v[:80] for a, v in seen.items()})


def payload_length_separability(per_task_prompts, carrying_arms):
    """REPORTED, NOT GATED (BC-7) -- does a single length threshold split any arm pair?

    Exit review #2 died on a token-length asymmetry, so this number belongs in the artifact.
    It is deliberately NOT a gate, and the reason is the point: the factorial gives the +hint
    cells more items than their no-hint partners, so a perfect length separator between those
    cells IS the treatment. Gating on it would forbid the experiment; omitting it would repeat
    exit review #2. So it ships as a number, for the reader deciding whether a particular
    contrast is length-confounded.
    """
    lens = collections.defaultdict(list)
    for prompts in per_task_prompts:
        base = prompts.get("F0", "")
        for arm in carrying_arms:
            if arm in prompts:
                lens[arm].append(len(payload_of(prompts[arm], base)))
    arms = sorted(lens)
    sep = []
    for i, a in enumerate(arms):
        for b in arms[i + 1:]:
            if max(lens[a]) < min(lens[b]) or max(lens[b]) < min(lens[a]):
                sep.append("%s|%s" % (a, b))
    return {"mean_chars": {a: round(sum(v) / len(v), 1) for a, v in lens.items()},
            "range": {a: [min(v), max(v)] for a, v in lens.items()},
            "perfectly_length_separable_pairs": sep,
            "note": "separable pairs are EXPECTED where the factorial varies item count; they "
                    "are a confound only for a contrast that is not supposed to vary in size."}


def nontreatment_identical_across_arms(prompts_by_arm, carrying_arms):
    """INVARIANT 7 -- with the treatment slot blanked, every arm's payload is BYTE-IDENTICAL.

    This supersedes the adversarial leakage gate as the primary evidence, and the reason is
    worth stating because it is a general lesson about this campaign.

    The gate attacked the non-treatment content with classifiers and reported no recovery above
    a permutation null. But a classifier null is an ESTIMATE with a detection floor, and when
    that floor was measured it turned out to be coarse: a per-arm spread of ~25% of a field's
    range passed undetected. So the gate could only ever have bounded slug leakage, never closed
    it -- and the slug was the one and only nuisance field that varied by arm (sparsity was
    already arm-invariant under INV 6c; everything else is template-fixed).

    Keying the slug on the TASK alone removes the channel instead of bounding it. What remains
    is decidable: blank the treatment, compare bytes. Where a property can be decided, deciding
    it strictly dominates estimating it.

    CONSEQUENCE THAT MUST TRAVEL WITH THIS: the adversarial gate is now VACUOUS on these packets
    -- its inputs are identical across arms, so it cannot detect anything, and its PASS is no
    longer evidence about them. It is retained as a REGRESSION detector: it would fire again if
    someone reintroduced an arm-varying nuisance field. A vacuous reading reported as a passing
    one is its own defect class, so the vacuity is named here rather than left to be discovered.
    """
    # HB3-1: `blank_treatment`, NOT the adversary's `constantize`. The latter strips the
    # payload before substituting, which erased whitespace differences between arms before this
    # comparison could see them -- Harmonia B measured a planted trailing space at 0/25 caught
    # while every non-whitespace perturbation was caught 25/25. Byte-identical must mean bytes.
    from ergon.probe.packet_render import blank_treatment
    base = prompts_by_arm.get("F0", "")
    blanked = {}
    for arm in carrying_arms:
        if arm not in prompts_by_arm:
            continue
        c = blank_treatment(payload_of(prompts_by_arm[arm], base))
        if c is None:                      # non-conforming: reported by INV 6a, not swallowed
            return False, {arm: "payload does not match the template; cannot blank treatment"}
        blanked[arm] = c
    distinct = set(blanked.values())
    if len(distinct) <= 1:
        return True, {}
    groups = {}
    for arm, txt in blanked.items():
        groups.setdefault(txt, []).append(arm)
    return False, {"n_distinct_nontreatment_payloads": len(distinct),
                   "arm_groups": [sorted(v) for v in groups.values()],
                   "first_diff": _first_diff(*list(distinct)[:2])}


def _first_diff(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return {"offset": i, "a": a[max(0, i - 30):i + 30], "b": b[max(0, i - 30):i + 30]}
    return {"offset": min(len(a), len(b)), "note": "one is a prefix of the other"}


def check_task(prompts_by_arm, gold_value, carrying_arms, forbidden):
    r1, d1 = base_identical(prompts_by_arm)
    r4, d4 = forbidden_token_scan(prompts_by_arm, forbidden)
    r5, d5 = gold_substring_scan(prompts_by_arm, gold_value)
    # `envelope_identical` is RETAINED BUT NO LONGER GATES. It compares a digit-erased,
    # list-length-preserving abstraction, so it fires on the item-count difference that IS the
    # treatment while staying blind to the digit-band label that is not. Template conformance
    # subsumes what it got right. It stays as a reported diagnostic so that demoting it is
    # visible in the artifact rather than silent.
    r2, d2 = envelope_identical(prompts_by_arm, carrying_arms)
    r6, d6, slots = template_conformance(prompts_by_arm, carrying_arms)
    r6b, d6b = slug_pool_shared(slots) if r6 else (False, {})
    r6c, d6c = sparsity_arm_invariant(slots) if r6 else (False, {})
    r7, d7 = nontreatment_identical_across_arms(prompts_by_arm, carrying_arms)
    return {
        "base_identical": r1, "base_diffs": d1,
        "envelope_identical_DIAGNOSTIC_ONLY": r2, "envelope_groups": d2,
        "no_forbidden_tokens": r4, "forbidden_hits": d4,
        "no_verbatim_gold": r5, "gold_hits": d5,
        "template_conformance": r6, "non_conforming": d6,
        "slug_pool_shared": r6b, "slug_pools": d6b,
        "sparsity_arm_invariant": r6c, "sparsity_diffs": d6c,
        "nontreatment_identical_across_arms": r7, "nontreatment_diffs": d7,
        "profiles": profile_spread(prompts_by_arm, carrying_arms),
        "all_pass": r1 and r4 and r5 and r6 and r6b and r6c and r7,
        "_slots": slots,
    }


def main(block="A"):
    """Run the decidable invariants against a BLOCK.

    HB3 scope condition (Harmonia B, exit review #3): the clear covers pinned block A only.
    Block B is a different population with its own manifest and its own prepass pool, and
    `C.manifest()` returns block A unconditionally -- so before HB3 this file could not have
    been pointed at block B at all, and "the invariants pass" would silently have meant "on the
    population that is not the one you are about to read".

        python ergon/probe/packet_invariants.py          # block A
        python ergon/probe/packet_invariants.py B        # block B
    """
    from ergon.probe.assemble import load_prepass
    import ergon.probe.campaign as C
    from ergon.probe import blocks as B

    if block == "A":
        rows = C.manifest()
        ctx = _nullcontext()
    else:
        rows = B.load(block)
        ctx = B.repointed(block)        # so the prepass pool resolves to the block's own
    gold = {r["uid"]: r["gold_int"] for r in rows}
    with ctx:
        return _run(block, rows, gold, C)


import contextlib as _contextlib


def _nullcontext():
    return _contextlib.nullcontext()


def _run(block, rows, gold, C):
    pool_path = C.DIR / "p1_prepass.jsonl"
    if not pool_path.exists():
        print(f"block {block}: no prepass pool yet — run P1 first")
        return 1

    arms_obj = C.Arms(rows, gold)
    # ALL SIX carrying arms, not the original three. P2 runs the 2x2 factorial, so the
    # hint cells are live packets; checking only the arms that predate the redesign
    # would leave the newest four unexamined -- the same scoping error in a new place.
    carrying = ["F-null", "F-generic", "F-prom-retrieved",
                "F-hint", "F-null+hint", "F-prom+hint"]
    all_arms = ["F0"] + carrying
    forbidden = ["true", "false", "correct answer", "the answer is"]

    failures, checked, skipped = [], 0, []
    per_task_prompts, per_task_slots = [], []
    for r in rows:
        uid = r["uid"]
        try:
            prompts = {a: arms_obj.prompt(a, uid) for a in all_arms}
        except Exception as e:
            # COUNTED, NOT SILENTLY SKIPPED. This clause used to `continue`, so a block
            # mid-collection reported PASS over only the tasks that happened to be ready and
            # said nothing about the rest -- a coverage denominator quietly redefined by which
            # rows had arrived. The verdict below refuses to read PASS when any task was
            # skipped.
            skipped.append({"uid": uid, "reason": f"{type(e).__name__}: {str(e)[:120]}"})
            continue
        res = check_task(prompts, gold[uid], carrying, forbidden)
        checked += 1
        per_task_prompts.append(prompts)
        if res.get("_slots"):
            per_task_slots.append(res["_slots"])
        if not res["all_pass"]:
            failures.append({"uid": uid, **{k: v for k, v in res.items()
                                            if k not in ("profiles", "_slots")}})

    # Population-scope checks. A per-arm numeric BAND is not visible one packet at a time --
    # each task shows a single index per arm and nothing to compare it against -- so this is
    # deliberately computed across the manifest rather than inside check_task.
    bands_ok, bands = slug_bands_not_separable(per_task_slots)
    lengths = payload_length_separability(per_task_prompts, carrying)

    out = {
        "block": block,
        "n_tasks_in_block": len(rows),
        "checked_tasks": checked,
        "skipped_tasks": len(skipped),
        "coverage": f"{checked}/{len(rows)}",
        "first_skipped": skipped[:3],
        "failures": len(failures),
        "slug_bands_not_separable": bands_ok,
        "slug_bands": bands,
        "payload_length_report": lengths,
        "verdict": ("INCOMPLETE — %d/%d tasks have no residue yet; the invariants hold on "
                    "the tasks that could be checked, and say NOTHING about the rest. Not a "
                    "PASS: a coverage denominator set by which rows happened to arrive is the "
                    "wrong-population error this campaign has committed five times."
                    % (len(skipped), len(rows))) if skipped
                   else "PASS — decidable invariants hold on every task"
                   if (not failures and bands_ok)
                   else "FAIL — arm identity is computationally AVAILABLE",
        "note": "These are decidable checks, not classifier estimates. A PASS here is a "
                "stronger claim than 'a classifier sat at chance': it says no difference "
                "exists in the checked feature set, and names the bytes when one does.",
        "checked_invariants": ["base byte-identical across arms",
                              "every carrying arm's FULL payload conforms to the template",
                              "slug pool token shared across arms (no label in words)",
                              "slug index bands not separable (no label in digits)",
                              "sparsity slot arm-invariant per task",
                              "NON-TREATMENT CONTENT BYTE-IDENTICAL ACROSS ARMS (INV 7) — "
                              "decidable; supersedes the adversarial gate, which is now "
                              "VACUOUS on these packets and retained only as a regression "
                              "detector",
                              "no forbidden verdict tokens in any payload",
                              "no verbatim gold in any non-oracle payload"],
        "reported_not_gated": ["payload length separability (the factorial varies item "
                              "count on purpose)",
                              "per-arm character-category census",
                              "envelope_identical, demoted 2026-08-25"],
        "first_failures": failures[:5],
    }
    outdir = ROOT / "ergon/probe/ledgers/packet_invariants"
    outdir.mkdir(parents=True, exist_ok=True)
    # PER-BLOCK LEDGER. One shared filename would let block B's run overwrite block A's
    # verdict, so a later reader could not tell which population a committed PASS described --
    # the ATK-016 shape (provenance that cannot see what changed) in a new place.
    name = "invariants.json" if block == "A" else f"invariants_block{block}.json"
    (outdir / name).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("block", "checked_tasks", "failures", "slug_bands_not_separable",
                       "verdict")}, indent=2))
    return 0 if (not failures and bands_ok and not skipped) else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "A"))
