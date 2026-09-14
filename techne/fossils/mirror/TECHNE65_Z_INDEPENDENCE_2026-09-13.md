# TECHNE-65: is Z: independent storage? -- NOT DEMONSTRABLE TODAY; real mirror STOPPED (2026-09-13)

Operator ruling (batch 06 charter): mirror to the Z: share PROVIDED it is physically independent of
the SKULLPORT vault; prove that before copying; if it is not, STOP and report rather than pretend.

## What was measured on SKULLPORT, 2026-09-13 03:1xZ

    net use Z:                  remembered mapping: Local name Z:, Remote name \\SPECTREX5\prometheus_share
    net use                     "There are no entries in the list"  -> the mapping is NOT connected
    Test-Path Z:\               False
    net use Z: \\SPECTREX5\prometheus_share /persistent:no
                                System error 1202: the local device name has a remembered connection
                                to another network resource (could not (re)connect)
    Test-Path \\SPECTREX5\prometheus_share   False ("does not exist"), via a script file so the UNC
                                was not mangled by shell quoting
    Test-NetConnection SPECTREX5 -Port 445    TcpTestSucceeded True  (the host answers SMB)
    net view \\SPECTREX5        System error 1702 (the binding handle is invalid)
    F:\SPECTREX5\prometheus_share             EXISTS -- a LOCAL directory on F: (volume RENEE, the
                                same physical volume as the vault F:\Prometheus\vault\fossils),
                                dated 2026-04-07..11, containing an old copy of the repository.
                                A shell that drops one leading backslash from the UNC resolves to
                                THIS directory and prints a listing that looks like the share.

## Reading

- The intended destination (a share on SPECTREX5, a different machine) would be independent
  storage. It is not reachable now: the mapping is stale, the share path does not resolve, and the
  host refuses enumeration, although it answers on port 445.
- The only path on this host that currently answers to the share's name is on the SAME volume as
  the vault. Copying there would be the false redundancy the ruling forbids.
- Therefore the real mirror was NOT executed. No body was copied anywhere persistent.

## What WAS done

- `harvest mirror` gained a same-volume guard: a destination whose resolved drive is the vault's
  drive is refused unless `--allow-same-volume` (disposable controls only); the receipt records
  both flags. A UNC destination passes the guard.
- `harvest mirror-verify --dest D` re-hashes every mirrored body against the records and the
  mirror's own MIRROR_INDEX.json (specimen -> tree hash, written beside the bodies).
- DESTRUCTIVE-NEGATIVE CONTROL on a disposable test mirror in the session scratchpad (same volume,
  flagged): three real bodies (tscp, backoff, compact) COPIED_VERIFIED; mirror-verify 3/3
  MIRROR_VERIFIED; ONE byte of compact.c flipped in the test mirror -> MIRROR_DIFFERS for that body
  only; the SOURCE body still verifies; the test mirror destroyed. Receipts:
  mirror-20260913T031641Z.json, mirror-verify-20260913T031641Z.json (before),
  mirror-verify-20260913T031641Z-2.json (after corruption).
- Unit control in techne/tests/test_fossil_isolation.py (corrupt, truncate, remove -> DIFFERS,
  DIFFERS, MISSING).

## What the operator needs to do for the mirror to run

Re-establish the share so that `\\SPECTREX5\prometheus_share` resolves from SKULLPORT (or name
another off-host destination). Then, from a worktree:

    python -m techne.fossils.harvest mirror --dest \\SPECTREX5\prometheus_share\fossil_mirror --dry-run
    python -m techne.fossils.harvest mirror --dest \\SPECTREX5\prometheus_share\fossil_mirror
    python -m techne.fossils.harvest mirror-verify --dest \\SPECTREX5\prometheus_share\fossil_mirror

About 1 GB for 90 bodies. The vault keeps ONE HOST as its preservation dependency until then.
