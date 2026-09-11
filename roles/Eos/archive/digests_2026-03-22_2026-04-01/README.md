# Eos digest residue, 2026-03-22 to 2026-04-01

Archived 2026-09-11 on the seat's re-seating pass. These 8 digests and
the daemon log are the complete collected output of Eos's March-April
run. They sat untracked on the canonical checkout's disk for 163 days
because agents/eos/reports/ is gitignored; they are copied here
byte-for-byte so the residue stays navigable. MANIFEST.md carries the
sha256 of each file over LF-normalised bytes.

READ THE PREMISE BEFORE READING A SCORE. Every relevance number in
these files was produced by a scorer keyed to a hypothesis the program
no longer holds -- "RPH: reasoning circuits precipitate at scale", with
CMA-ES steering vectors in the residual stream as the method. That
premise was retired without the scorer being retired with it. No score
in this directory may be cited without this annotation, and no score may
be cited at all until the scorer has the three controls it has never
had (roles/Eos/CALIBRATION.md, EOS-07).

What the residue measures, on its own terms:

    digest        items   body hash (first 8, below the date line)
    2026-03-22     5      c816c369
    2026-03-23     5      c816c369   IDENTICAL to 03-22
    2026-03-24     5      c816c369   IDENTICAL to 03-22
    2026-03-25    27      e47f5968
    2026-03-27     5      6a5c8049
    2026-03-28    13      b58f0d43
    2026-03-31     5      bf7adea4
    2026-04-01     3      8b92de75

    command: for a in *.md; do tail -n +3 "$a" | md5sum; done

Three of the eight are the same digest under three dates. The log shows
the hourly loop rewriting a daily-granularity file and exiting cleanly
each time. The final digest reports "All Papers (0 found)" without
reporting that the dedup index had saturated at 163 items, and its
"Deep Analysis" section is a 120B model's reasoning scratchpad about a
repository it never opened.

Two files are NOT here and were never collected: the digest named
"digest 2026-05-17.md" by the seat's only instrumented success row
(agora.intelligence_outputs, 2026-05-17T03:54:44Z), and whatever the
May cycles on M4 wrote after it. The success row is in the database;
the artifact is not on any host this seat can reach.

eos_daemon.log covers 2026-03-22 only (2,421 bytes); it is the log as
found, not the run's complete history.
