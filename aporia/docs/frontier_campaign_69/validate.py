"""
Per-wave validator for the frontier campaign dossiers.

Checks the two things that have actually gone wrong in this programme's
Deep Research history, and nothing else:

  1. STRUCTURE. All eight PART headings present. A report missing PARTs came
     back as something other than the dossier that was asked for.

  2. BRACKET DAMAGE, split by whether it cost anything. The grounding layer
     rewrites the finished report and replaces square-bracketed spans with
     citation markers. Two cases look identical to a naive grep and are not
     the same thing at all:

       APPENDED  a marker added at the end of a sentence. Costs nothing.
                 Report 05 carried 44 of these and lost no data.
       VALUE     a marker sitting where a number or range belonged, because
                 the model wrapped its own value in brackets and the layer
                 could not tell that from a citation. The value is GONE and
                 does not come back. Report 03 lost two this way.

     Only the second kind is a loss, and it is detected by what FOLLOWS the
     bracket, not what precedes it. A citation marker sits at the end of a
     sentence or clause, so it is followed by punctuation or a line break. A
     bracket that is followed by a word continuing the same sentence was
     holding a value, because the sentence still needs the thing it ate:

         "...bounds of the maze <X> for both x and y coordinates"
         "...clip the outputs to the strict <X> bounds of the maze"

     A third harmless class is the markdown-link shape <text>(url), which is
     how the grounding layer writes its own source bibliography.

     THE FIRST VERSION OF THIS CHECK KEYED ON THE PRECEDING WORD and scored
     0 losses on report 03, where two were already confirmed by hand. It was
     replaced, not tuned. Any future change to this classifier must be run
     against report 03 first, which is the known-positive fixture.

Losses are REPORTED, never repaired. A destroyed value is not written back
from inference even when the surrounding sentence makes it obvious; see
aporia/doctrine and feedback-deep-research-cannot-return-brackets.

    python aporia/docs/frontier_campaign_69/validate.py           # all
    python aporia/docs/frontier_campaign_69/validate.py 7 8 9     # a wave
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOSSIERS = HERE / "dossiers"

PART_RE = re.compile(r"^#*\s*PART (\d)\.", re.M)
BRACKET_RE = re.compile(r"\[[^\]]{0,80}\]")
# A citation marker ends a sentence or clause, so punctuation or a line break
# follows it. Anything else means the sentence continues through the bracket,
# and the bracket ate a value. The markdown-link shape is the layer's own
# bibliography and is harmless.
APPENDED_AFTER_RE = re.compile(r"^\s*(?:[.,;:!?)—-]|$)", re.M)
# A marker mid-clause followed by a coordinating conjunction is still just a
# citation: "stabilization of DNS in 2025 <X> and the commoditization of...".
CONJUNCTION_AFTER_RE = re.compile(r"^\s+(?:and|or|but|while|which|whereas)\b")
MD_LINK_RE = re.compile(r"^\(")
# A destroyed span ALWAYS comes back as a citation marker. So a bracket in a
# value position whose content is real -- "[-2.0, -0.5]", "[batch_size, 2]" --
# was not destroyed; it survived, and only sat where a destroyed one would.
# Report 14 carried six of those. Flagging them as losses conflated a risk
# position with an actual loss, which are not the same claim.
CITE_MARKER_RE = re.compile(r"^\[\s*cite[:\s]", re.I)
ARXIV_RE = re.compile(r"arXiv:\d{4}\.\d{4,5}")
# The prompt asks for "arXiv OR DOI", so an arXiv count of zero is not a
# defect. Genetic Programming came back with four DOIs, no arXiv ids, and
# four honest IDENTIFIER UNKNOWNs -- a correct report that an arXiv-only
# check called broken. Identifier coverage is the union.
DOI_RE = re.compile(r"\b10\.\d{4,9}/\S+")
UNKNOWN_RE = re.compile(r"IDENTIFIER UNKNOWN")
URL_RE = re.compile(r"https?://\S+")
VERDICTS = ("MAINTAINED", "DORMANT", "ABANDONED")


def check(path: Path) -> dict:
    t = path.read_text(encoding="utf-8")
    parts = {int(m.group(1)) for m in PART_RE.finditer(t)}

    appended, value_loss, survived = [], [], []
    for m in BRACKET_RE.finditer(t):
        after = t[m.end() : m.end() + 40]
        harmless = (MD_LINK_RE.match(after) or APPENDED_AFTER_RE.match(after)
                    or CONJUNCTION_AFTER_RE.match(after))
        if harmless:
            appended.append(m)
        elif CITE_MARKER_RE.match(m.group(0)):
            value_loss.append(m)          # a marker where a value belonged
        else:
            survived.append(m)            # real content, in a risk position

    return {
        "name": path.name,
        "chars": len(t),
        "parts_missing": sorted(set(range(1, 9)) - parts),
        "appended": len(appended),
        "survived": len(survived),
        "value_loss": [
            {
                "excerpt": t[max(0, m.start() - 90) : m.end() + 30].replace("\n", " "),
                "destroyed_as": m.group(0),
            }
            for m in value_loss
        ],
        "arxiv": len(set(ARXIV_RE.findall(t))),
        "doi": len(set(DOI_RE.findall(t))),
        "unknown": len(UNKNOWN_RE.findall(t)),
        "urls": len(set(URL_RE.findall(t))),
        "verdicts": sum(t.count(v) for v in VERDICTS),
    }


def main(argv: list[str]) -> int:
    if argv:
        wanted = {int(a) for a in argv}
        files = [p for p in sorted(DOSSIERS.glob("*.md"))
                 if int(p.name[:2]) in wanted]
    else:
        files = sorted(DOSSIERS.glob("*.md"))

    if not files:
        print("no dossiers matched")
        return 1

    total_loss = 0
    for p in files:
        r = check(p)
        flags = []
        if r["parts_missing"]:
            flags.append(f"MISSING PARTS {r['parts_missing']}")
        if not r["verdicts"]:
            flags.append("NO SOFTWARE VERDICTS")
        if r["arxiv"] + r["doi"] == 0:
            flags.append("NO IDENTIFIERS")
        status = "  ".join(flags) if flags else "ok"

        print(f"{r['name']}")
        print(f"   {r['chars']:>6} chars   arXiv {r['arxiv']:>2}   doi {r['doi']:>2}"
              f"   unk {r['unknown']:>2}   urls {r['urls']:>2}"
              f"   verdicts {r['verdicts']:>2}   {status}")
        print(f"   brackets: {r['appended']} appended, {r['survived']} survived "
              f"in a risk position, {len(r['value_loss'])} CANDIDATE LOSS")
        for loss in r["value_loss"]:
            total_loss += 1
            print(f"      CANDIDATE {loss['destroyed_as']}: ...{loss['excerpt']}...")
        print()

    print(f"{len(files)} dossiers checked, {total_loss} CANDIDATE losses -- adjudicate by reading.")
    if total_loss:
        print("A candidate is not a loss. Read the sentence: if it is "
              "complete without the bracket,")
        print("the marker was INSERTED and nothing was taken. Record the "
              "adjudication either way")
        print("in bracket_losses.jsonl, with its reason, both ways.")
        print("Do NOT write a destroyed value back from inference, even when "
              "the surrounding sentence makes it obvious.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
