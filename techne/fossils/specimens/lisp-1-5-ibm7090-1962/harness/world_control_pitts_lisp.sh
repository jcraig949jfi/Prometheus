#!/bin/bash
# WORLD POSITIVE CONTROL: Pitts' own LISP 1.5 system tape (shipped in s709-2.4.4, 2008; provenance
# not stated by him) run under his runlisp conventions with his propositional-calculus job -- the
# same Wang algorithm the 1962 deck's wang.job tests. Proves the emulator, the unit layout
# (a1 sysin, a2 sysppt, a3 sysout, a4 system tape read-only, b3 systmp) and the job format
# (TAPE cards, TEST, program, STOP, FIN) work. It says nothing about the BODY's tape.
set -e
L=/usr/local/share/ibm709x/lisp
d=$(mktemp -d); cd "$d"
cp $L/LISPTAPE.BIN $L/lisp.cmd $L/propcal.lsp .
txt2bcd propcal.lsp sysin >/dev/null
touch reader.cbn
timeout 180 s709 -clisp.cmd -m7090 r=reader pc=print u=punch a1=sysin.bcd a2=sysppt.bin a3=sysout.bcd a4r=LISPTAPE.BIN b3=syscore.bin >/dev/null 2>&1 || true
bcd2txt -p sysout.bcd out.txt
echo "printer_lines=$(grep -c . out.txt)"
grep -c 'VALUE OF TH' out.txt | sed 's/^/traced_theorem_steps=/'
grep -q 'EVALQUOTE OPERATOR AS OF 1 MARCH 1961' out.txt && echo BANNER_1961
grep -q 'END OF LISP RUN' out.txt && echo END_OF_LISP_RUN
grep -A1 'END OF EVALQUOTE, VALUE IS' out.txt | grep -c 'TRUE' | sed 's/^/evalquote_true_values=/'
sha256sum LISPTAPE.BIN
