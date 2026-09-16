# TECHNE-65: the destination side, measured ON the destination host (2026-09-16)

Companion to TECHNE65_Z_INDEPENDENCE_2026-09-13.md, which measured from SKULLPORT (the vault
host) and found `\\SPECTREX5\prometheus_share` unreachable: stale Z: mapping, UNC did not
resolve, `net view` error 1702, port 445 open. This note is the other end of the same wire,
taken by Techne[m2-04bd52c0] running on SPECTREX5 itself. Built from ccb26df01 in
D:\Prometheus-worktrees\techne-boot-2026-09-16 (branch techne/m2-boot-2026-09-16).

## What was measured on SPECTREX5, 2026-09-16 ~11:50Z

    net share / Get-SmbShare      prometheus_share -> C:\prometheus_share   EXISTS
    Get-ChildItem C:\prometheus_share
                                  cartography/ (2026-04-12), lmfdb_local/ (2026-04-13);
                                  31,880 files under it. No fossil_mirror/ yet.
    Get-Service LanmanServer      Running, Automatic
    Get-SmbServerConfiguration    EnableSMB2Protocol True, EnableSMB1Protocol False,
                                  RequireSecuritySignature True, EncryptData False
    Get-NetFirewallRule "File and Printer Sharing (SMB-In)"
                                  Enabled: Public True, Private False, Domain False
    Get-NetConnectionProfile      Verizon_QGTCY3, NetworkCategory Public  (so the SMB-In rule
                                  that is enabled IS the one for the active profile)
    Get-NetIPAddress              192.168.1.191 (Ethernet)
    Get-SmbShareAccess prometheus_share
                                  SPECTREX5\prometheus  Allow  Full      -- the ONLY entry
    Get-Acl C:\prometheus_share   SPECTREX5\prometheus FullControl; Administrators; SYSTEM;
                                  Authenticated Users Modify; Users ReadAndExecute
    Get-LocalUser prometheus      Enabled True, PasswordRequired True, LastLogon 2026-05-15
    whoami                        spectrex5\james
    Test-Path \\SPECTREX5\prometheus_share      Access is denied
    Test-Path \\192.168.1.191\prometheus_share  Access is denied
    Test-Path \\localhost\prometheus_share      Access is denied
    Get-SmbSession / Get-SmbConnection          none
    Free space on C:              756 GB (the vault is ~1 GB for 121 bodies)
    Vault bodies on THIS host     0  (D:\Prometheus\vault\fossils does not exist; the
                                  mirror can only be run FROM SKULLPORT, where the bodies are)

## Reading

- The share is real, served, and on a different machine and volume from the vault. It is
  INDEPENDENT storage in the sense the batch 06 ruling requires. The 09-13 finding that the
  same-named F:\SPECTREX5\prometheus_share on SKULLPORT is a same-volume look-alike stands;
  this share is not that directory.
- The share is gated to ONE identity: the local account SPECTREX5\prometheus. Every other
  identity, including the interactive user on the destination host itself, is refused at the
  share level (the NTFS ACL would admit Authenticated Users; the share ACL does not). This is
  the most economical explanation of the 09-13 symptoms: a remembered Z: mapping made under
  one credential that no longer connects, a UNC that "does not exist" to an unauthenticated
  probe, and `net view` refused, while port 445 answers. No name-resolution or firewall
  defect is needed to explain it, and none was found here.
- Nothing was changed. Granting share access, creating a mapping under the prometheus
  account, or handing SKULLPORT that credential are outward-facing security changes and
  are the operator's, not this seat's.

## What is now the operator's one-line decision (replaces the 09-13 open question)

Either (a) on SKULLPORT, map the share AS the prometheus account:

    net use Z: \\192.168.1.191\prometheus_share /user:SPECTREX5\prometheus /persistent:yes
    (the IP form sidesteps NetBIOS name resolution; the password is typed at the prompt,
     never put in a file or a commit)

or (b) on SPECTREX5, add the SKULLPORT user to the share's access list:

    Grant-SmbShareAccess -Name prometheus_share -AccountName <that user> -AccessRight Change

Then, from a SKULLPORT worktree (the bodies live there), unchanged from the 09-13 note:

    python -m techne.fossils.harvest mirror --dest Z:\fossil_mirror --dry-run
    python -m techne.fossils.harvest mirror --dest Z:\fossil_mirror
    python -m techne.fossils.harvest mirror-verify --dest Z:\fossil_mirror
    then set techne/config.local.json "fossil_mirror" on SKULLPORT so the catalog's
    mirror_available turns to "mirrored".

Until one of (a)/(b) happens the vault keeps ONE HOST as its preservation dependency
(121 bodies as of batch 12). The same-volume guard in `harvest mirror` will accept a Z:
that resolves to \\192.168.1.191 and refuse the F:\SPECTREX5 look-alike, as designed.

## NOT measured

- Anything from SKULLPORT (no instance of this seat is on that host right now).
- Whether the prometheus account's password is known to the operator (a credential fact;
  not this seat's to probe).
- Throughput of the wire for ~1 GB (unnecessary before access exists).
