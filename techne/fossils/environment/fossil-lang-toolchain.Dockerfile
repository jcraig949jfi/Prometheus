# Preserved build+run world for batch 02: C/C++ with autotools, plus a Scheme and a Common
# Lisp for the language/logic specimens (fossil vault, 2026-09-12). Debian 12 bookworm.
#   docker build -t prometheus-fossil-lang:bookworm -f fossil-lang-toolchain.Dockerfile .
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gfortran make cmake pkg-config \
        autoconf automake libtool bison flex \
        guile-3.0 sbcl \
        zlib1g-dev libncurses-dev libreadline-dev libgmp-dev \
        file bc time ca-certificates && rm -rf /var/lib/apt/lists/*
ENV LANG=C.UTF-8
WORKDIR /w
