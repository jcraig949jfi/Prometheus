# odysseus -- the fleet's distributed brain substrate

Seat: roles/Odysseus. Design and prior art: DESIGN.md. Stdlib Python
3.10+ only; Windows and Linux.

A spiking circuit sharded across machines, advanced in lockstep ticks
over UDP, recorded per shard (keyframes + per-tick log) so any run can be
paused, played, stepped, rewound, fast-forwarded and forked for a
microtest, with every replayed tick verified by hash.

## Try it on one machine

    python -m odysseus.brain local  --run /tmp/r1 --neurons 2000 --shards 4 --ticks 100
    python -m odysseus.brain verify --run /tmp/r1

    python - <<'EOF'
    from odysseus.brain.player import Player
    p = Player("/tmp/r1", shard=2)
    p.seek(57); p.step(); p.rewind(20); p.fast_forward(30)
    p.play(until=90, on_frame=lambda f: p.pause() if len(f.outbound) > 150 else None)
    b = p.fork(ablate=[1100, 1101])     # microtest from the paused tick
    b.run(until=99)
    print(p.tick, b.diverged_at, b.escaped_at)
    EOF

## Run across machines

Every machine needs the same run.json, then one node per machine:

    python -m odysseus.brain init --run R --neurons N --shards 2 --seed 1 --keyframe 10 --run-id 77
    # host A
    python -m odysseus.brain node --run R --shard 0 --bind 0.0.0.0:47100 --peers 0=A:47100,1=B:47100 --ticks 500
    # host B
    python -m odysseus.brain node --run R --shard 1 --bind 0.0.0.0:47100 --peers 0=A:47100,1=B:47100 --ticks 500

Windows hosts need an inbound UDP firewall rule for the chosen port.

## Tests

    python -m pytest -q odysseus/tests
