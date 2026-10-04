"""Claim renderer: the C2 render rule, the quantifier rule and the TWIN rule (C-004-T015).

Normative text: rso/slice001/contract/CONTRACT.md v1.0.0 (draft B B3.5, B4.3, B5.3, B6.4, B8) and
AMENDMENT_v1.0.1.md (V6 custody why spelling).

A rendering is generated from a checker decision record (checker.Consumer.decide) and registered templates
only. Free text is never rendered and prose is never an input to a decision (B8.1, Fable G7.report form).
Every rendering, generated or presented, is linted before it is returned: the words of the quantifier rule
may stand only inside a "class" relative-to clause that carries its exact bound; a rendering without its
relative-to clause, cell or setting is refused; a twin may not be promoted to a second physics.

Every rendered claim prints its authority stage (C4, inherited, lowest of its instruments), its custody line
and the three C1 fields of every prerequisite, non-SATISFIED lines first. A NOT_ELIGIBLE claim keeps its
bracket and never renders as a weaker positive.

Python >= 3.8, standard library only.
"""
import re

QUANTIFIERS = ("class", "any", "all", "every", "no", "none", "never", "always")     # contract.json render
REFUSALS = ("RENDER_QUANTIFIER_UNBOUND", "RENDER_RELATIVE_MISSING", "RENDER_CELL_MISSING",
            "RENDER_SETTING_MISSING", "RENDER_TWIN_PROMOTION")
STAGE_WORDS = {"AUTHOR_TESTED": "author-tested", "FIRST_SIGHT_CHALLENGED": "first-sight-challenged",
               "CLOSED_AFTER_REPAIR": "closed-after-repair"}
STANDING_ORDER = ("BLOCKED", "UNQUALIFIED", "UNMET", "SATISFIED")
# Producer predicates whose outcomes G-RECOMP does not recompute print "(not recomputed)" (B6.4 names
# RESTART and OBSERVER; BOUNDS and TWIN_EQ are outside the recompute set too; FD-T015-7).
NOT_RECOMPUTED = ("BOUNDS", "RESTART", "OBSERVER", "TWIN_EQ")

_RATIONAL = r"\d+/\d+"
_CLASS_REL = re.compile(r"; relative to class [^\s(]+ \([^()]*; exact bound " + _RATIONAL + r" by [^()]*\)")
_REL = re.compile(r"; relative to (?:(?:comparator|intervention) set \{[^{}]+\}|class [^\s(]+ \([^()]*; exact "
                  r"bound " + _RATIONAL + r" by [^()]*\))")
_CELL = re.compile(r"; cell \S+ rev [0-9a-f]{12},")
_SETTING = re.compile(r"\bsetting \S+ [0-9a-f]{12}\.")
_QUANT = re.compile(r"\b(" + "|".join(QUANTIFIERS) + r")\b", re.IGNORECASE)
# A twin earns one physics (draft A P8, B8.1): phrases that count M' as a second physics, a realization or a
# promotion (FD-T015-8: the phrase list is this packet's; extend it when an attack finds another form).
_TWIN_PROMOTION = re.compile(r"\b(second physics|another physics|independent(ly)? confirm\w*|replicat\w*|"
                             r"realis\w*|realiz\w*|promot\w*)\b", re.IGNORECASE)
_CODE = re.compile(r"\A[A-Z][A-Z0-9_]*(:\S+)?\Z")


class RenderRefused(ValueError):
    def __init__(self, codes):
        self.codes = list(codes)
        ValueError.__init__(self, " ; ".join(self.codes))


def lint(text):
    """Refusal codes for a rendering (empty list = acceptable). Order: twin promotion, unbound quantifiers in
    order of first occurrence, then relative-to, cell, setting."""
    out = []
    if _TWIN_PROMOTION.search(text):
        out.append("RENDER_TWIN_PROMOTION")
    masked = _CLASS_REL.sub(lambda m: " " * len(m.group(0)), text)
    for w in _QUANT.findall(masked):
        code = "RENDER_QUANTIFIER_UNBOUND:%s" % w.lower()
        if code not in out:
            out.append(code)
    if not _REL.search(text):
        out.append("RENDER_RELATIVE_MISSING")
    if not _CELL.search(text):
        out.append("RENDER_CELL_MISSING")
    if not _SETTING.search(text):
        out.append("RENDER_SETTING_MISSING")
    return out


def relative_text(rel):
    """RELATIVE of B8.1, or None when the clause is absent or malformed."""
    if not isinstance(rel, dict):
        return None
    if rel.get("form") in ("comparator", "intervention"):
        ids = rel.get("ids") or []
        if not ids or not all(isinstance(i, str) and i for i in ids):
            return None
        return "%s set {%s}" % (rel["form"], ", ".join(ids))
    if rel.get("form") == "class":
        if not re.match(r"\A" + _RATIONAL + r"\Z", str(rel.get("bound", ""))):
            return None
        return "class %s (%s; exact bound %s by %s)" % (rel["class_id"], rel["def"], rel["bound"], rel["method"])
    return None


def headline(eligibility, proposition, relative, cell, setting):
    """HEADLINE of B8.1 with whatever parts exist; missing parts are left out so lint refuses them."""
    s = "[%s] %s" % (eligibility, proposition)
    rt = relative_text(relative)
    if rt is not None:
        s += "; relative to " + rt
    if cell and cell.get("cell_id") and cell.get("revision"):
        s += "; cell %s rev %s," % (cell["cell_id"], cell["revision"][:12])
    if setting and setting.get("id") and setting.get("sha256"):
        s += " setting %s %s" % (setting["id"], setting["sha256"][:12])
    return s + "."


def render_statement(eligibility, proposition, relative=None, cell=None, setting=None):
    """Render one statement through the C2 rule; raise RenderRefused with every refusal code."""
    text = headline(eligibility, proposition, relative, cell, setting)
    bad = lint(text)
    if bad:
        raise RenderRefused(bad)
    return text


def proposition(decision):
    """PROPOSITION from the registered template and structured fields only (B8.1)."""
    t, m, w = decision["type"], decision["subject"], decision["world"]
    if t == "CL-RET":
        ret = decision["retention"]
        if decision["eligibility"] == "ELIGIBLE" and ret is not None:
            return ("Runtime %s answers u_j at the first probe after boundary j, j = 1..3, in %d of %d trials, "
                    "carried by the declared allowed component a" % (m, ret["successes"], ret["trials"]))
        return ("Runtime %s answers u_j at the first probe after boundary j, j = 1..3, carried by the declared "
                "allowed component a" % m)
    if t == "CL-CAL":
        return ("World %s is calibrated: u_j is balanced at j = 1..3 and the maximum success of N equals the "
                "registered bound" % w)
    if t == "CL-CUST":
        return "The bytes of %s are those registered with the keeper" % decision["claim_id"]
    twin = decision.get("twin") or "the twin of %s" % m
    enc = decision.get("encoding") or "its registered encoding"
    return "%s has the outcome vector of %s under %s; one physics" % (twin, m, enc)


def _auth(a):
    if a["status"] == "QUALIFIED":
        return "QUALIFIED at %s" % STAGE_WORDS[a["stage"]]
    return "UNQUALIFIED (%s)" % "; ".join(a["why"])


def _outcome(o):
    if o is None:
        return "-"
    if o["kind"] == "RULER":
        return "%s %d/%d (%s)" % (o["value"], o["successes"], o["trials"], o["statistic"])
    if o["value"] == "FAIL" and _CODE.match(o["reason"]):
        return "FAIL %s" % o["reason"]                       # typed reason codes only; prose is not rendered
    return o["value"]


def verdict_line(line):
    if line["predicate"] == "custody":
        c = line["custody"]
        return "  custody on %s: %s" % (line["scope"], "QUALIFIED" if c["status"] == "QUALIFIED"
                                        else "UNQUALIFIED (%s)" % "; ".join(c["why"]))
    v = line["verdict"]
    ex = v["execution"]
    exec_s = "RAN" if ex["status"] == "RAN" else "BLOCKED (missing %s)" % "; ".join(ex["missing"])
    s = "  %s on %s: execution %s | authority %s | outcome %s" % (line["predicate"], line["scope"], exec_s,
                                                                 _auth(v["authority"]), _outcome(v["outcome"]))
    o = v["outcome"]
    if o is not None and o["kind"] == "GATE" and o["vacuous"]:
        s += " (vacuous: 0 applicable)"
    if line["predicate"] in NOT_RECOMPUTED or (line["predicate"] in ("CALIBRATION", "RETENTION", "ERASE",
                                                                     "PRESERVE", "CHANNEL")
                                               and not line["recomputed"]):
        s += " (not recomputed)"
    return s


def _standing(line):
    return line["standing"] if line["predicate"] == "custody" else line["verdict"]["standing"]


def stage_line(decision):
    a = decision["authority"]
    if a["status"] == "QUALIFIED":
        return "Authority: %s (lowest of %d instruments)" % (STAGE_WORDS[a["stage"]], decision["instruments"])
    return "Authority: UNQUALIFIED (%s)" % "; ".join(a["why"])


def custody_line(c):
    if c["status"] == "QUALIFIED":
        return ("Custody: QUALIFIED -- bytes registered with %s at %s; execution not authenticated."
                % (c["keeper"], c["registered_at_utc"]))
    return "Custody: UNQUALIFIED (%s)." % "; ".join(c["why"])


def render_claim(decision):
    """The full B8.1 RENDERING of one decision record; raise RenderRefused if any C2 rule fails."""
    head = headline(decision["eligibility"], proposition(decision), decision.get("relative"),
                    decision.get("cell"), decision.get("setting"))
    lines = list(decision["prerequisites"])
    order = sorted(range(len(lines)), key=lambda i: (STANDING_ORDER.index(_standing(lines[i])), i)
                   if _standing(lines[i]) != "SATISFIED" else (len(STANDING_ORDER), i))
    body = [verdict_line(lines[i]) for i in order]
    body += ["  %s" % u for u in decision.get("unverified", [])]
    text = "\n".join([head, stage_line(decision), custody_line(decision["custody"])] + body)
    bad = lint(text)
    if bad:
        raise RenderRefused(bad)
    return text
