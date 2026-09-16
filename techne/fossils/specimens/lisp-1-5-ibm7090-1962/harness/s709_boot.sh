#!/bin/bash
# Boot the assembled LISP 1.5 tape on Pitts' s709 (7090 mode) with the Wang job on the card
# input tape (A2) and every unit the body's Makefile names. `lt 27` = load tape channel B unit 7.
# Prints the PC after the load so the gate can tell "the loader ran and transferred into the
# program" (PC != 00001, the reset value) from "nothing happened". Printer output, if any, is
# decoded to io/print.txt. 2026-09-16: the loader runs and transfers (PC 01002, inside the
# card-reading routine B8/B9), no printer output yet -- see the record's world_status.
set -e
mkdir -p io
obj2bin lisp15.out lisp15.tape >/dev/null
txt2bcd wang.job wang.bcd >/dev/null
printf 'lt 27\ndp\nda\nq\n' > cmds.txt
timeout 120 s709 -m7090 -ccmds.txt p=io/print.bcd u=io/punch.bcd b7=lisp15.tape b3=io/tmp.tape a2=wang.bcd a3=io/pot.tape a4=io/ppt.tape 2>&1 | grep -v '^$' | tee s709.out
pc=$(grep '^PC:' s709.out | head -1 | awk '{print $2}')
echo "pc_after_load=$pc"
if [ -n "$pc" ] && [ "$pc" != "00001" ]; then echo TAPE_LOADED_AND_TRANSFERRED; else echo TAPE_DID_NOT_RUN; fi
bcd2txt -p io/print.bcd io/print.txt 132 2>/dev/null || true
n=$(wc -l < io/print.txt 2>/dev/null || echo 0); echo "printer_lines=$n"
if [ "$n" -gt 0 ]; then echo JOB_PRODUCED_OUTPUT; head -40 io/print.txt; else echo NO_PRINTER_OUTPUT; fi
