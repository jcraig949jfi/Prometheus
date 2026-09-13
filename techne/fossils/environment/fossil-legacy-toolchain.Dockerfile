# Preserved run world for batch 05 PRIORITY G (legacy computational cultures): Ada (GNAT 12 +
# gprbuild), COBOL (GnuCOBOL 3), BASIC (Bywater BASIC), Common Lisp
# (SBCL), plus the C toolchain for the historical C sources (C-Prolog, pack) -- Debian 12 bookworm,
# (gnu-smalltalk is not packaged in bookworm; a Smalltalk world is deferred.)
# fossil vault 2026-09-12.
#   docker build -t prometheus-fossil-legacy:bookworm -f fossil-legacy-toolchain.Dockerfile .
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential make bison flex \
        gnat gprbuild gnucobol3 bwbasic sbcl \
        libgmp-dev libncurses-dev \
        file bc time ca-certificates && rm -rf /var/lib/apt/lists/*
ENV LANG=C.UTF-8
WORKDIR /w
# Bas 2.5 (Michael Haardt, GPL): a classic ANSI-minimal-BASIC interpreter that runs the 1970s
# line-numbered Microsoft dialect (Creative Computing listings) far better than bwBASIC 2.20,
# which passes `PRINT:PRINT` lines to the shell and chokes on apostrophes inside strings.
# Source pinned beside this Dockerfile: bas-2.5.tar.gz sha256
# 1313c8903c63e4fd5fa8295e6c67971266bc06f945b1a6056dbce0f4d02f2de8 (www.moria.de/~michael/bas/).
COPY bas-2.5.tar.gz /tmp/
RUN cd /tmp && tar xzf bas-2.5.tar.gz && cd bas-2.5 && ./configure -q && make -s && make -s install && rm -rf /tmp/bas-2.5*
