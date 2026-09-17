"""Oracle for the LISP 1.5 assembly: the body ships lisp15.lst, the listing Bourguignon produced
with asm7090 2.1.4 + his own patch. Compare the WORDS this world's assembler generated against it.

A listing line that carries code looks like

    77746   0000 00 0 77724     62   LOAD4 HTR     LOAD    ...
    ^loc    ^generated word (prefix decrement tag address)  ^card no

Only (location, word) pairs are compared -- page headers, card numbers, comments and the
listing layout are the assembler's own business and are expected to differ between versions.
Three classes are accepted as agreement with the 1962 program: IDENTICAL to the reference;
COMPLETED (the reference printed address 00000 for a cross-header symbol -- its README names
this limitation -- and the new word resolves it); ERRATA (reference_errata.json beside this
file: locations where the reference is WRONG against the 1962 listing PDF, adjudicated page
by page; the new word must equal the 1962 word). Anything else is DIFFER and fails.
Usage: python3 compare_listing.py ref.lst new.lst
"""
import re
import sys

PAT = re.compile(r"^\s*([0-7]{5})\s+(-?[0-7]{1,4}\s+[0-7]{2}\s+[0-7]\s+[0-7]{5})\s")


def words(path):
    out = {}
    dup = 0
    for ln in open(path, encoding="latin-1"):
        m = PAT.match(ln)
        if m:
            loc, w = m.group(1), re.sub(r"\s+", " ", m.group(2))
            if loc in out and out[loc] != w:
                dup += 1
            out[loc] = w
    return out, dup


import json, os
errata = {e["loc"]: e["listing_1962"] for e in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference_errata.json")))["errata"]}
ref, dref = words(sys.argv[1])
new, dnew = words(sys.argv[2])
same = sum(1 for k in ref if k in new and new[k] == ref[k])
completed = sorted(k for k in ref if k in new and new[k] != ref[k] and ref[k].split()[-1] == "00000" and new[k].split()[-1] != "00000" and new[k].rsplit(" ", 1)[0] == ref[k].rsplit(" ", 1)[0])
by_errata = sorted(k for k in ref if k in new and new[k] != ref[k] and k in errata and new[k] == errata[k])
diff = sorted(k for k in ref if k in new and new[k] != ref[k] and k not in completed and k not in by_errata)
only_ref = sorted(k for k in ref if k not in new)
only_new = sorted(k for k in new if k not in ref)
print("reference words=%d generated words=%d identical=%d completed_ref_zero=%d agree_via_1962_errata=%d differ=%d "
      "only_in_reference=%d only_in_new=%d (duplicate locations ref=%d new=%d)"
      % (len(ref), len(new), same, len(completed), len(by_errata), len(diff), len(only_ref), len(only_new), dref, dnew))
for k in diff[:12]:
    print("  DIFFER %s ref=%s new=%s" % (k, ref[k], new[k]))
for k in only_ref[:6]:
    print("  ONLY_IN_REFERENCE %s %s" % (k, ref[k]))
for k in only_new[:6]:
    print("  ONLY_IN_NEW %s %s" % (k, new[k]))
print("LISTING_WORDS_MATCH" if not diff and not only_ref else "LISTING_WORDS_DIFFER")
sys.exit(0 if not diff and not only_ref else 1)
