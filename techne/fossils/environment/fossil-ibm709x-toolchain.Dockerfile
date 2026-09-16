# Preserved historical-machine world for IBM 709/7090/7094 bodies (batch 12 P6, 2026-09-16):
# David G. Pitts' toolchain -- asm7090 (assembler), lnk7090 (linker), utils (obj2bin, txt2bcd,
# bcd2txt ...) and the s709 emulator (709/7090/7094/CTSS modes, IBSYS-capable). MIT licensed
# (LICENSE.txt in each tarball, (c) 2024 David G. Pitts). Origin https://www.cozx.com/dpitts/ibm7090.html
# First consumer: lisp-1-5-ibm7090-1962 (a card deck whose Makefile names asm7090 2.2.2 /
# lnk7090 2.1.3 / utils 1.0.5 / s709; those versions are no longer served, so the CURRENT
# releases are pinned by sha256 here and any difference is measured, not assumed).
#   docker build -t prometheus-fossil-ibm709x:bookworm -f fossil-ibm709x-toolchain.Dockerfile .
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential make curl ca-certificates file \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /tmp/build
RUN set -e; \
    for spec in \
      "asm7090-2.3.2 d60cdd5bcb4e9eb5d5c61dd27e142150f8dbe303472fee963a3502b7a7b1888f" \
      "lnk7090-2.2.3 d421dac59831382760aa84364ede1e6ab0758d85411c29ae9e17b92a1b7d468b" \
      "s709-2.4.4    86d3f896b4b5cfe5f78200a89717902dfb826131c2fbdb32bbb5bddd69526096" \
      "utils-1.1.15  04372a4800f5c54366a7979f3bcf1e5ccbf38fe4e7b266b400fbce2559e2b6e1" ; do \
      set -- $spec; \
      curl -sSL --fail -o "$1.tar.gz" "https://www.cozx.com/dpitts/tarballs/ibm709x/$1.tar.gz"; \
      echo "$2  $1.tar.gz" | sha256sum -c -; \
      tar xzf "$1.tar.gz"; \
    done; \
    (cd asm7090 && make) && install -m755 asm7090/asm7090 /usr/local/bin/; \
    (cd lnk7090 && make) && install -m755 lnk7090/lnk7090 /usr/local/bin/; \
    (cd utils && make) && for f in obj2bin obj2img bcd2txt txt2bcd bincmp disasm bd bsplit; do install -m755 utils/$f /usr/local/bin/; done; \
    (cd s709-2.4.4 && make) && install -m755 s709-2.4.4/s709 /usr/local/bin/; \
    mkdir -p /usr/local/share/ibm709x && cp asm7090/LICENSE.txt /usr/local/share/ibm709x/LICENSE-pitts.txt \
    && for d in asm7090 lnk7090 utils s709-2.4.4; do cp $d/README.txt /usr/local/share/ibm709x/README-$d.txt; done; \
    cd / && rm -rf /tmp/build
ENV LANG=C.UTF-8
WORKDIR /w
