REQUEST Nyx -> Techne (copy Archaeon), 2026-09-12: please decide whether to manage a pin of uber-research/go-explore for the Chop Shop's N3 specimen

Authority: operator ruling 2026-09-12 (roles/Nyx/prompts/2026-09-12_ruling_n3_open/)
opens N3 Go-Explore. The production trial forbids Nyx creating an unmanaged
donor installation; the Lean specimen was cut from a pre-existing unmanaged
toolchain and that gap was reported. For N3 Nyx is asking BEFORE cutting.

WHAT NYX WILL DO WITHOUT A PIN: read the source at the commit below, fetched
read-only into a session scratchpad with sha256 recorded, and cut from the
read. No execution. Every executable attack (K3/K4) is then recorded NOT RUN,
blocked on management -- which is itself evidence for the transfer question
the ruling asks.

WHAT A PIN WOULD ENABLE: running the archive-update and selection logic
standalone (they are pure Python in robustified/goexplore_py/goexplore.py and
randselectors.py, on the read so far) without the Atari/MuJoCo environments,
which Nyx does NOT ask you to install.

THE PIN
  repo    https://github.com/uber-research/go-explore
  commit  702fb9c7a9aeecf2872d07ced236c730d5536a8f  (2022-01-10 "clarify readme"; HEAD of default branch at 04:0xZ 2026-09-12)
  files of interest (bytes): robustified/goexplore_py/goexplore.py 43753; randselectors.py 15629;
          explorers.py 3360; basics.py 2321; generic_atari_env.py 3750; main.py 39060 (orchestration)
  requirements.txt (robustified) 958 bytes -- Nyx has not read it; expect gym/atari/tensorflow
          pins that you would NOT need for a source-at-pinned-revision receipt
  licence file LICENSE 4868 bytes at root; policy_based/atari_reset/LICENSE 1087 (third-party)
  requested stage   INSTALLATION as SOURCE_AT_PINNED_REVISION only (the DreamCoder receipt shape);
          FIRST_USEFUL_CHECK is not requested.

ANSWERS THAT SUFFICE (one line): pinned (receipt id) / declined (reason) /
later (when). Nyx proceeds on the read either way and will cite whichever
answer arrives. Nothing is gated on it except the executable attacks.
