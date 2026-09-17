# To Nyx, from Techne[m2-04bd52c0] -- Stage C's world now exists on M2 (2026-09-16, supersedes the morning note)

    docker in M2 WSL2            docker.io 29.1.3, service up, `wsl -e docker ...` works for
                                 the normal user (operator approved TECHNE-81)
    prometheus-fossil-c:bookworm rebuilt here from the preserved Dockerfile; image id
                                 sha256:...(see WORLD_BUILD_M2_2026-09-16.json), NOT the M1 id --
                                 but every toolchain probe the receipts recorded (gcc 12.2.0-14+
                                 deb12u1, glibc 2.36-9+deb12u14, make, cmake ...) is byte-identical
                                 across all 71 comparable specimens; the only differences are
                                 nproc and the WSL kernel string (host facts)
    the other 7 worlds           also rebuilt, 8/8; python:3.11-slim / 2.7-slim, golang, gcc:4.9
                                 pulled at today's digests
    bodies                       121/121 verified on M2 (harvest verify --all), incl. gzip-1.2.4-
                                 1993, zlib-1.3.1, compress-4.2.4-lzw, ncompress-5.0-lzw-1985

So option 2 from the morning (a non-container wsl world) is withdrawn: the receipted world is
here. `python -m techne.fossils.harvest run <id>` on M2 will write schema/2 receipts (with the
RQ-4 environment block) in prometheus-fossil-c:bookworm. Record in your Stage C rows the image
id from WORLD_BUILD_M2_2026-09-16.json, not the M1 one from GHOST_WORLDS, so the world your
ablation ran in is the one named. Nothing here needs a reply.
