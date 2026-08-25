"""One packet template for every residue-carrying arm. Isomorphism by construction.

RULING (2026-08-25, REDESIGN): *"If F-generic can be identified against F-null/F-prom from
packet shape alone, then the controller is not a controller. Make the packets syntactically
isomorphic before another arm call. That is prior to the 300-row question."*

The previous design let each arm render itself. F-null and F-prom happened to share a template;
F-generic was free prose, and a decidable check separated it by shape alone. Checking for
isomorphism after the fact is the weaker discipline — the check has to be remembered, and it was
added only after two exit reviews died on shape confounds. Here every arm calls **one**
renderer, so the arms cannot diverge in shape without editing this file.

Timing note: this changes the packet format, which is free right now and would not be later —
no arm rows exist yet. The band read is F0-only (cold, no packet), so nothing collected is
invalidated.

WHAT VARIES BETWEEN ARMS: the slot contents only — the source slug and the item list.
WHAT DOES NOT: the literal frame, field order, punctuation, the redaction markers, and the
trailing sparsity block. The source token is IDENTICAL across arms (`probe_pool`), because a
differing literal is readable even when the shape matches.
"""
import hashlib
import re

#: Shared across every arm — a per-arm pool token would be a readable label.
POOL = "nearmiss_mix"

#: The single frame. Every residue-carrying arm renders through this and only this.
TEMPLATE = (
    # THE LEAD LINE LIVES HERE, NOT IN THE CALLER. It used to be prepended by campaign.py
    # for F-null and F-prom ONLY -- a plain-text arm label on 2 of 6 arms, 400/400
    # separating. It survived three layers of check: it sits OUTSIDE the region the
    # template matcher sees, and the isomorphism test STRIPPED it before matching
    # (comment: "shared lead line" -- it was not shared). Anything a caller can prepend
    # is a shape the caller controls, so the frame now owns the first byte of the packet.
    "A prior attempt record:\n"
    "[probe_pool:{slug} p[COUNT-REDACTED]_prepass#[COUNT-REDACTED]]\n"
    "prior attempt applied (method projection; prose withheld - measured diffuse answer "
    "leakage): {items}\n"
    "  (not recorded: diagnosis)\n"
    "\n"
    "{sparsity}"
)

#: The modal block. NOT a casual default: the real sparsity VARIES (3 of 60 sampled tasks
#: carry an extra `attempt_text` line), so freezing it would have silently rewritten
#: residue content on ~5% of tasks while appearing to only fix shape.
MODAL_SPARSITY = ("SPARSITY (what the substrate did not record - shipped as measured):\n"
                  "  diagnosis: absent in [COUNT-REDACTED]/[COUNT-REDACTED] records (100.0%)")

#: Slug format is fixed so the id cannot carry arm identity through its *shape* either.
_SLUG_RE = re.compile(r"^[a-z0-9_]+-[A-Z]\d+-\d{5}$")


def render(slug, items, sparsity=None):
    """Render a packet. `items` is a list of tokens; `slug` must match the frozen id shape.

    Raises rather than coercing: a slug of the wrong shape is exactly the leak this file
    exists to prevent, and silently reformatting it would hide the caller's bug.
    """
    if not _SLUG_RE.match(slug):
        raise ValueError(
            f"slug {slug!r} does not match the frozen packet id shape "
            "<pool>-<RUNG>-<5 digits>; a differently-shaped id is an arm label")
    if not items:
        raise ValueError("empty item list: an arm that carries no items must not carry a packet")
    return TEMPLATE.format(slug=slug, items=", ".join(items),
                           sparsity=sparsity or MODAL_SPARSITY)


def slug_for(uid):
    """`nearmiss_mix-M30-00007` -> `nearmiss_mix-M30-00007` (already correct shape)."""
    return uid


def synthetic_slug(rung, key, span, pool=None):
    """A slug for arms with no task provenance (generic, method-hint, the +hint cells).

    THE INDEX IS AN ARM LABEL IF ITS RANGE IS. The previous version took a caller-supplied
    integer, and campaign.py supplied `idx + 40000` for F-generic, `+50000` for F-hint,
    `+60000` for F-null+hint, `+70000` for F-prom+hint, while the two provenance-carrying arms
    used real task indices in [0, 200). That is a perfect six-way arm label written in digits,
    and NO shape check could ever have caught it: `envelope_shape` and `framing_skeleton` both
    map every digit run to `#` by design, and the one test that inspected the slug split on
    `-` and kept only the pool token, discarding the number. Three checks, all blind to the
    same class, because the abstractions that make shape comparable are exactly the ones that
    delete digits.

    So the index is no longer the caller's to choose. It is derived by keyed hash into
    `span` -- the SAME range real task ids occupy -- which makes the numeric range identical
    across arms by construction. Collision with a real task id is not a defect here; it is the
    point. The key varies per (arm, task) so the value carries nothing about the target task
    that the arm does not already carry.

    CAUGHT ON THE FIRST TEST OF THIS FILE (kept, because the defect class recurs): my initial
    version took a `pool` argument and produced `generic_pool-M30-00007`. The *shape* matched a
    real id, so the framing check passed -- and the literal token `generic_pool` is a
    plain-text arm label readable by any reader. So the pool token is FIXED and shared.
    """
    if pool is not None:
        raise ValueError(
            "a per-arm pool token is an arm label in plain text; the pool is fixed and shared")
    if not isinstance(span, int) or span <= 0:
        raise ValueError(
            "span must be the positive size of the real task-id range; without it the index "
            "range is the caller's choice again, which is how the +40000 band happened")
    digest = hashlib.blake2b(str(key).encode("utf-8"), digest_size=8).digest()
    idx = int.from_bytes(digest, "big") % span
    return f"{POOL}-{rung}-{idx % 100000:05d}"


def template_regex():
    """The template as an exact matcher, built FROM the template so the two cannot drift.

    Supersedes the `framing_skeleton` heuristic for this purpose. That abstraction erased
    words to compare shape and could not tell a one-item list from a five-item one, so arms
    whose item counts were distributed differently looked shape-different when they were
    generated by the identical template. Matching the template directly is decidable and
    needs no abstraction: either the packet came from this frame, or it did not.
    """
    head, rest = TEMPLATE.split("{slug}")
    mid, tail = rest.split("{items}")
    pre, post = tail.split("{sparsity}")
    pat = (re.escape(head)
           + "(?P<slug>[^ \\]]+)"
           + re.escape(mid)
           + "(?P<items>[^\\n]+)"
           + re.escape(pre)
           + "(?P<sparsity>.*)"
           + re.escape(post))
    return re.compile(pat, re.S)


TREATMENT_BLANK = "<TREATMENT>"


def blank_treatment(payload):
    """Replace the treatment slot with a constant, PRESERVING EVERY OTHER BYTE.

    HB3-1 (Harmonia B, exit review #3). The previous blanker ran `payload.strip()` before
    substituting, so leading/trailing whitespace was erased before any comparison could see it.
    Harmonia B predicted the hole from source and then measured it: a trailing space planted on
    one arm was caught 0/25, while a lead line, a one-digit slug change and a one-character
    frame edit were each caught 25/25.

    That is structurally the SAME defect as the one filed on 2026-08-25 -- the isomorphism test
    stripped the lead line and then certified the remainder isomorphic -- in a new location. It
    is the fifth instance of "a check that removes a region before inspecting it", and the
    region removed is always where a caller-controlled label goes.

    Two changes from the old implementation:
      * NO STRIP. Whitespace anywhere in the payload is nuisance and must survive to the
        comparison.
      * SPAN SUBSTITUTION, not `.replace(items_text, ...)`. The old form replaced every
        occurrence of the items string in the match, so an items value that also appeared
        elsewhere would have blanked both. Splicing by span cannot do that.

    Returns None if the payload was not produced by TEMPLATE -- non-conformance is itself an
    arm-conditional shape and is reported by INVARIANT 6a, never swallowed here.
    """
    m = template_regex().search(payload)
    if m is None or m.start("items") < 0:
        return None
    return payload[:m.start("items")] + TREATMENT_BLANK + payload[m.end("items"):]


def matches_template(payload):
    """True iff `payload` was produced by TEMPLATE. Returns (ok, slots)."""
    m = template_regex().fullmatch(payload.strip())
    return (m is not None), (m.groupdict() if m else {})
