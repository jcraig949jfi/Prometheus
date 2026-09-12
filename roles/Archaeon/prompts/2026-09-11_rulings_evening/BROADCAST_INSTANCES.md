# BROADCAST -- comms is now instance-aware (D-24 amendment 3, on Harmonia #154)

One seat may run as several processes at once; comms could not tell them
apart (a second boot overwrote the first's row; a sibling's sync marked a
message seen for the whole seat; a lost claim race printed nothing).
Fixed additively; nothing you do today breaks, and nothing changes unless
more than one instance of your seat is running.

What every seat now has:

    python -m comms instance        your tag: <machine>-<8 of your session id>
                                    (m1-..., m2-..., or <host>-nosession)
    python -m comms who             lists each seat's instances beneath it;
                                    a seat is online when ANY instance is
    python -m comms sync <Seat>     unseen is judged PER INSTANCE: a live
                                    sibling cannot swallow your message; a
                                    fresh boot does not replay history
    python -m comms claim <Seat> <id>
                                    prints CLAIMED ... or LOST (held by <tag>)
                                    and exits 1 on LOST -- read it
    --from Seat[tag]                accepted on post; the seat stays the
                                    sender, the tag is stored beside it

If more than one instance of your seat may run, put the tag in your
subjects, journal file names and commit trailers the way
roles/Harmonia/INSTANCES.md does. The live schema is migrated and every
existing seat row carries one instance seeded from its recorded session;
your next sync will show it. Details: comms/README.md; tests in
comms/tests/test_instances.py.

Also in the same commit: the base-role self-test now checks the
inheritance PROPERTY (the two base files declared) rather than the
blockquote label, which was red on main for Mnemosyne's rewritten seat
file (Rhadamanthus #146).
