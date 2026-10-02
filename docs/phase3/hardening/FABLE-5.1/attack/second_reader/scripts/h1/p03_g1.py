"""G1.cell and G1.receipt: escapes, false accusations, mutants rejected for another reason."""
from drv import *
import hashlib
seq, cell, table, run_receipt, SOURCE = registration, meta.cell, meta.table, meta.run_receipt, meta.SOURCE

def show(name, thunk):
    try:
        r = thunk()
        print("%-78s -> %s %s" % (name, r.verdict, ("| " + r.reason[:150]) if r.reason else ""))
    except Exception as e:
        print("%-78s -> RAISES %s: %s" % (name, type(e).__name__, str(e)[:100]))

print("--- G1.cell: broken cases")
show("E1 powers declared as NUMBERS 1.0 and 0.0, no design runs (design_seeds=[])",
     lambda: seq.check_cell(cell(design_seeds=[], known_answers={"HOLDS": 1.0, "FAILS": 0.0})))
show("E1b the registered mutant's values as numbers, not strings (1.0, 0.999)",
     lambda: seq.check_cell(cell(known_answers={"HOLDS": 1.0, "FAILS": 0.999})))
show("E2 two-outcome table: no undecided band registered at all",
     lambda: seq.check_cell(cell(verdict_table=table([(13, 24, "HOLDS"), (0, 12, "FAILS")], outcomes=("HOLDS", "FAILS")))))
show("E3 known answers HOLDS + INDETERMINATE; the 'no' needs 0..2 of 24 and has no known case",
     lambda: seq.check_cell(cell(verdict_table=table([(22, 24, "HOLDS"), (0, 2, "FAILS"), (3, 21, "INDETERMINATE")]),
                                 known_answers={"HOLDS": 0.999, "INDETERMINATE": 0.5})))
print("     P(FAILS | a negative at rate 0.2) under that table = %.4f" %
      stats.outcome_probability(table([(22, 24, "HOLDS"), (0, 2, "FAILS"), (3, 21, "INDETERMINATE")]), 0.2)["FAILS"])
show("E4 every descriptive field a placeholder ('tbd')",
     lambda: seq.check_cell(cell(physics="tbd", search="tbd", world="tbd", development="tbd", boundary="tbd",
                                 resources="tbd", measurement="tbd", adapter="tbd", independent_unit="tbd")))
show("E4b descriptive fields a blank or a zero", lambda: seq.check_cell(cell(physics=" ", world=0, measurement=False, resources=0)))
show("E5 registered_seeds = () (no seeds at all, as an empty tuple)", lambda: seq.check_cell(cell(registered_seeds=())))
show("E5b registered_seeds = range(0)", lambda: seq.check_cell(cell(registered_seeds=range(0))))
show("E6 a design seed registered for confirmation, typed '5000' in one list and 5000 in the other",
     lambda: seq.check_cell(cell(design_seeds=[1, 2, "5000"])))
show("E7 design seeds repeated", lambda: seq.check_cell(cell(design_seeds=[1, 1, 1])))
show("E8 registered_seeds a 24-character string", lambda: seq.check_cell(cell(registered_seeds="abcdefghijklmnopqrstuvwx")))
show("E9 source_sha256 = 'tbd', registered_at = 'yesterday'", lambda: seq.check_cell(cell(source_sha256="tbd", registered_at="yesterday")))
show("E10 exposure count astronomically large", lambda: seq.check_cell(cell(exposure={"tuning_evaluations": 10**12})))
show("E11 verdict table is a sentence", lambda: seq.check_cell(cell(verdict_table="see appendix")))
show("E12 rule tuple malformed", lambda: seq.check_cell(cell(verdict_table={"n": 24, "outcomes": ["HOLDS"], "rule": [(0, 24)]})))
show("E13 HOLDS for low counts, FAILS for high (direction not read)",
     lambda: seq.check_cell(cell(verdict_table=table([(0, 2, "HOLDS"), (12, 24, "FAILS"), (3, 11, "INDETERMINATE")]),
                                 known_answers={"HOLDS": 0.0, "FAILS": 0.999})))
print("--- G1.cell: sound cases")
show("S1 the sound cell also registers a known undecided case at its best rate", None or (lambda: seq.check_cell(cell(known_answers={"HOLDS": 0.999, "FAILS": 0.2, "INDETERMINATE": 0.72}))))
best = max((stats.outcome_probability(table(), r / 1000)["INDETERMINATE"], r / 1000) for r in range(1, 1000))
print("     max over rates of P(INDETERMINATE) under the registered table: %.4f at rate %.3f" % best)
show("S2 a weak real positive at per-unit rate 0.98", lambda: seq.check_cell(cell(known_answers={"HOLDS": 0.98, "FAILS": 0.2})))
print("--- G1.receipt")
show("R1 string clocks: registered_at='100', ran_at='99' (run earlier)", lambda: seq.check_receipt(cell(registered_at="100"), run_receipt(ran_at="99"), SOURCE))
show("R1b ISO strings with different offsets (run 1h BEFORE registration)",
     lambda: seq.check_receipt(cell(registered_at="2026-10-02T01:00:00+02:00"), run_receipt(ran_at="2026-10-02T00:30:00+02:30"), SOURCE))
show("R2 mixed types: registered_at=100, ran_at='200'", lambda: seq.check_receipt(cell(), run_receipt(ran_at="200"), SOURCE))
show("R3 receipt lists the registered seeds plus one more", lambda: seq.check_receipt(cell(), run_receipt(seeds=list(range(5000, 5025))), SOURCE))
show("R4 uppercase hex in the receipt", lambda: seq.check_receipt(cell(), run_receipt(source_sha256=seq.sha(SOURCE).upper()), SOURCE))
crlf = SOURCE.replace(b"\n", b"\r\n")
raw = hashlib.sha256(crlf).hexdigest()
show("R5 SOUND: hash registered with plain sha256 of a CRLF checkout, same file on hand",
     lambda: seq.check_receipt(cell(source_sha256=raw), run_receipt(source_sha256=raw), crlf))
show("R6 code on hand differs only by CRLF", lambda: seq.check_receipt(cell(), run_receipt(), crlf))
show("R7 code on hand has a lone CR appended", lambda: seq.check_receipt(cell(), run_receipt(), SOURCE + b"\r"))
show("R8 ran_at = True (bool as a clock)", lambda: seq.check_receipt(cell(registered_at=0), run_receipt(ran_at=True), SOURCE))
show("R9 receipt seeds as strings of the registered ints", lambda: seq.check_receipt(cell(), run_receipt(seeds=[str(s) for s in range(5000, 5024)]), SOURCE))
show("R10 cell with no registered seeds (tuple) and a receipt with none", lambda: seq.check_receipt(cell(registered_seeds=()), run_receipt(seeds=()), SOURCE))
# every_missing_field_blocks: what it does when a field is open
r = meta.every_missing_field_blocks(lambda c: Result("x", PASS), cell, meta.CELL_FIELDS)
print("helper on a checker that requires nothing:", r.verdict, "|", r.reason[:80])
