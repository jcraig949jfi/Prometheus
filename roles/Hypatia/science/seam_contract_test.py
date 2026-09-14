"""Re-verify the Pheme -> Hypatia demand-profile seam defect.

pivot/COMPONENT_DOSSIERS_2026-06-24.md (Pheme, Q3) claims: Pheme emits
target_reasoning_patterns as a list of DICTS, while Hypatia's
select_next_problem does set(...) over that list and then tests a STRING
pattern_kind for membership. If true the seam raises TypeError before any
bias is ever applied, so the demand signal could never have aimed the
D-track even if Pheme had produced a profile.

The dossier marked its own Q3 claims "[unverified claim]". This executes it.

Run:  python roles/Hypatia/science/seam_contract_test.py
"""
import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
PHEME = REPO_ROOT / "agents" / "pheme" / "daemon.py"
HYPATIA = REPO_ROOT / "agents" / "hypatia" / "daemon.py"
KEY = "target_reasoning_patterns"


def show_sites(path, label):
    print("=== %s: every site touching %s ===" % (label, KEY))
    if not path.exists():
        print("  FILE ABSENT: %s" % path.relative_to(REPO_ROOT).as_posix())
        return
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if KEY in line:
            print("  %s:%d: %s" % (path.name, i, line.strip()))
    print()


def main():
    show_sites(PHEME, "PHEME (producer)")
    show_sites(HYPATIA, "HYPATIA (consumer)")

    # The shape Pheme actually emits. pheme/daemon.py subscripts the element
    # by key (profile[KEY][0]["pattern_kind"]), which is only valid on a dict.
    pheme_shape = [
        {"pattern_kind": "group_theory", "failure_rate": 0.65, "n": 12},
        {"pattern_kind": "analytic", "failure_rate": 0.40, "n": 9},
    ]

    print("=== TEST: Hypatia's exact expression against Pheme's actual shape ===")
    confirmed = False
    try:
        got = set({KEY: pheme_shape}.get(KEY) or [])
        print("  no exception; set = %r" % (got,))
        print("  VERDICT: NOT CONFIRMED -- the dossier claim does not reproduce.")
    except TypeError as e:
        confirmed = True
        print("  TypeError: %s" % e)
        print("  VERDICT: CONFIRMED -- raises before any bias is applied.")

    print()
    print("=== POSITIVE CONTROL: the shape Hypatia expects (list of str) ===")
    tp = set({KEY: ["group_theory", "analytic"]}[KEY])
    biased = [c for c in [{"pattern_kind": "group_theory"}, {"pattern_kind": "other"}]
              if str(c.get("pattern_kind", "")) in tp]
    positive_ok = biased == [{"pattern_kind": "group_theory"}]
    print("  set = %r ; biased subset = %r" % (tp, biased))
    print("  positive control %s -- the test can observe a WORKING seam."
          % ("PASSES" if positive_ok else "FAILS"))

    print()
    print("=== CHEAT CONTROL: dict payload smuggled past as pre-stringified ===")
    # If someone "fixes" the seam by str()-ing the dicts, membership silently
    # never matches: no exception, no bias, no alarm. That is worse than the
    # TypeError, and the test must be able to see it.
    tp_cheat = set(str(d) for d in pheme_shape)
    biased_cheat = [c for c in [{"pattern_kind": "group_theory"}]
                    if str(c.get("pattern_kind", "")) in tp_cheat]
    cheat_caught = biased_cheat == []
    print("  stringified set matches nothing: biased subset = %r" % (biased_cheat,))
    print("  cheat control %s -- a silent no-match is detectable, not mistaken for success."
          % ("PASSES" if cheat_caught else "FAILS"))

    print()
    print("SUMMARY: claim_confirmed=%s positive_control=%s cheat_control=%s"
          % (confirmed, positive_ok, cheat_caught))


if __name__ == "__main__":
    main()
