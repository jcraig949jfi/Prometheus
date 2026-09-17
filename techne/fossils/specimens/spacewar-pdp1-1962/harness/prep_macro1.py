"""Modern scaffolding, declared: put the 1962 Spacewar! MACRO source (masswerk transcription of
spacewar_2b_25mar62) into the form Bob Supnik's macro1 cross assembler parses. The BODY is not
edited; this runs on the disposable copy and every transformation is listed here and counted
in its output so the receipt shows exactly how much scaffolding stands between the 1962 text
and the assembled tape.

  T3  the ONE-LINE macro definition `define<TAB>mult Z<TAB><TAB>jda mpy<TAB><TAB>lac Z<TAB><TAB>term`
      (source line 90) is expanded to the multi-line form the rest of the source uses. macro1's
      defineMacro reads the macro name and dummies from the remainder of the `define` line and
      then swallows every following line until one that begins with `term` -- so the one-liner
      turns the next ~200 lines (the sine-cosine subroutine, the outline compiler ...) into macro
      body, which is why every later macro was "undefined" (151 errors, 2026-09-16).
  T4  the MACRO FIO-DEC SYSTEM macro library (macro_fiodec_jun63.txt beside this file, from
      https://www.masswerk.at/spacewar/sources/, sha256 8ff11791..., "june 1963") is inserted
      after the title line, minus its own `start`: the 1962 source calls swap / ioh / spq /
      count / index / setup / init without defining them because they lived in the assembler's
      system tape, exactly as a C program does not define printf. It is the nearest surviving
      library; the 1962 tape itself is not preserved.
  T5  one alias, `init A,B` -> `initialize A,B`: the library spells it `initialize` and the
      1962 program `init`; the historical MACRO folded symbols to their leading characters, so
      both named one macro there. macro1 keeps 6 significant characters (its SYMSIG=4 switch is
      commented out and unimplemented), so the fold is written down as a one-line alias.
  T6  the five `ranct \\ran, sar 9s, sar 4s, \\src`-style calls are expanded by hand from the
      macro body the source itself defines (line 74: random N / S / SS / sma / cma / dac C):
      macro1 splits macro arguments on spaces, so an argument such as `sar 9s` cannot reach it.
  T7  the star-field tables (labels 1j..4q, called by `dislis`) are NOT in the 25 Mar 62 text --
      they were a separate tape, Peter Samson's "expensive planetarium" data. They are appended
      from spacewar_2b_2apr62.txt (beside this file, masswerk, sha256 8e60bd3a..., Landsteiner's
      2014 RECONSTRUCTION from disassembly; "not an authentic source code" by its own header):
      the block from "stars by prs" to its `start 4`, with its `mark` macro. The 25 Mar 62 `start`
      is dropped so the tables assemble into the same tape. Two provenance grades in one tape,
      both named here.
  T8  variables whose first three characters equal a macro name's are renamed (backslash-ran -> backslash-qran):
      macro1 resolves an undefined symbol to a macro/pseudo-op by 3-character prefix (its own
      emulation of MACRO's symbol folding) and a `\variable` is undefined until `variables`
      allocates it at the end. Mapping printed at run time.
Measured first and NOT applied: indenting column-1 `define`, un-indenting the macro name, and
`terminate` -> `term` -- macro1 accepts all three source spellings unchanged (error count was
151 with and without them). Usage: python3 prep_macro1.py in.txt out.mac
"""
import os
import sys

TAB = chr(9)
src, dst = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
lines = open(src, encoding="latin-1").read().split(chr(10))

# T3 -- the one-line define
out, t3 = [], 0
for ln in lines:
    if ln.startswith("define" + TAB) and ln.rstrip().endswith("term"):
        parts = [p for p in ln.split(TAB) if p.strip()]      # ['define', 'mult Z', 'jda mpy', 'lac Z', 'term']
        out.append(TAB + "define")
        out.append(parts[1])
        out.extend(TAB + p for p in parts[2:-1])
        out.append(TAB + parts[-1])
        t3 += 1
        continue
    out.append(ln)

# T6 -- expand ranct calls (macro1 cannot pass "sar 9s" as one argument)
RANCT_BODY = ["random N", "S", "SS", "sma", "cma", "dac C"]   # source lines 74-81, verbatim order
t6, out2 = 0, []
for ln in out:
    if ln.startswith(TAB + "ranct "):
        args = [a.strip() for a in ln[len(TAB + "ranct "):].split(TAB)[0].split(",")]
        if len(args) == 4:
            n, s_, ss, c = args
            for b in RANCT_BODY:
                out2.append(TAB + b.replace("SS", ss).replace("N", n).replace("S", s_).replace("C", c))
            t6 += 1
            continue
    out2.append(ln)
out = out2

# T7 -- append the star tables from the reconstruction; drop the 25 Mar 62 `start`
recon = open(os.path.join(here, "spacewar_2b_2apr62.txt"), encoding="latin-1").read().split(chr(10))
i0 = next(i for i, l in enumerate(recon) if l.startswith("stars by prs"))
i1 = next(i for i, l in enumerate(recon) if i > i0 and l.strip().startswith("start"))
stars = recon[i0:i1 + 1]
while out and out[-1].strip() == "":
    out.pop()
assert out[-1].strip() == "start", out[-1]
out = out[:-1] + ["", "/ ---- T7: star tables from spacewar_2b_2apr62.txt (reconstruction) ----", ""] + stars

# T4 + T5 -- the macro library (minus its `start`) and the init alias, after the title line
lib = open(os.path.join(here, "macro_fiodec_jun63.txt"), encoding="latin-1").read().split(chr(10))
lib = [l for l in lib if l.strip() != "start"]
lib = [("/ " + l if i == 0 else l) for i, l in enumerate(lib)]      # its title line is not code
alias = ["", TAB + "define", "init A,B", TAB + "initialize A,B", TAB + "term", ""]
final = [out[0]] + [""] + lib + alias + out[1:]
final = [("/ " + l if l.startswith("stars by prs") else l) for l in final]   # nor is the star block's

# T8 -- macro1 resolves an UNDEFINED symbol to any macro or pseudo-op sharing its first three
# characters (lookup(): "MACRO returns last defined n-x match", strncmp(..., 3)). A macro-
# variable (`\ran`, allocated only by `variables` at the end) is undefined at every use, so
# `\ran` resolves to the MACRO `random`/`ranct` and macro1 reports "misplaced symbol". The
# 1962 assembler evidently kept variables apart from macro names (the program assembled).
# Every variable whose 3-character prefix equals a macro's is renamed in the copy, mapping
# printed, semantics unchanged (a variable's name is only its identity).
import re
macros = set()
for i, l in enumerate(final):
    if l.strip() == "define" and i + 1 < len(final):
        macros.add(final[i + 1].strip().split()[0].split(",")[0])
pre3 = {m[:3] for m in macros}
variables = sorted({m.group(1) for l in final for m in re.finditer(r"\\([a-z][a-z0-9]*)", l)})
renames = {}
for v in variables:
    if v[:3] in pre3:
        cand = "q" + v
        assert cand[:3] not in pre3 and cand not in variables, cand
        renames[v] = cand
if renames:
    pat = re.compile(r"\\(" + "|".join(sorted(renames, key=len, reverse=True)) + r")\b")
    final = [pat.sub(lambda m: "\\" + renames[m.group(1)], l) for l in final]
t8 = ", ".join("%s->%s" % kv for kv in sorted(renames.items())) or "none"

open(dst, "w", encoding="latin-1", newline=chr(10)).write(chr(10).join(final))
print("prep_macro1: T3 one-line defines expanded=%d T4 library lines=%d T5 alias lines=%d T6 ranct calls expanded=%d "
      "T7 star-table lines appended=%d T8 variable renames=%s lines_in=%d lines_out=%d"
      % (t3, len(lib), len(alias), t6, len(stars), t8, len(lines), len(final)))
