# PACKET_GAPS -- cold-start trial of expedition/recert/PACKET.md (worker coldstart_A-001, 2026-09-28)

Worker: fresh subagent with no oral context. It read 00_READ_FIRST.md, READY_PROTOCOL.md and PACKET.md in that order, then
worked from the worktree /home/jcraig/Prometheus-worktrees/odysseus-base-role (HEAD 02800d2b5, branch
odysseus/expedition-1-2026-09-28), as the operator instructed. Local adjustments from the operator (not gaps): no commits, no
comms, PREREG.md written instead of committed, outputs under coldstart_A-001/, 1 process, <= 40 min compute.
Context isolation: this worker wrote nothing to any memory directory. The harness it ran under loads no memory files it could
see, but the worker cannot verify that.

Each gap is something the worker had to work out that the packet did not say. BLOCKING = a worker who follows the packet
and READ_FIRST literally cannot complete the task, or gets a wrong result.

## Gaps

G1 BLOCKING AT TRIAL START; RESOLVED MID-TRIAL (d3941cb07, 10:59:34Z) -- the packet and every input it lists were NOT in git.
   PACKET.md says "Inputs (all in git)". On HEAD, origin/main and every remote ref, `git log --all --
   'roles/Odysseus/expedition/recert/*'` is empty and `git status` shows the whole recert/ directory as untracked. recert.py,
   the fixture, the three label specs, the rows and RESULT.md exist only as uncommitted files in one worktree on ubu001.
   00_READ_FIRST says to work "from a fetched origin/main SHA" on "any machine". A worker who does that finds no packet,
   no harness and no fixture, so (a) and (d) fail. This trial could proceed only because the operator pointed at this
   worktree. The engine inputs the harness reads (BEE plans and receipts, NPE z8/p11, archaeon, proteus) ARE tracked.
   Fix: commit recert/ and pin the SHA in PACKET.md.
   UPDATE: while L4 was running, the owner committed recert/ (d3941cb07 "expedition 1 -- ... recert harness ..."), and
   it is now on origin/main (281eeed50). I checked: PACKET.md, recert.py and test_known_answers.py on origin/main are
   byte-identical to the files this trial used. Run from a `git archive origin/main` snapshot in scratch, with no patch
   needed, the fixture reproduces 24/24 and KNOWN_ANSWERS.json is byte-identical. The packet SHA is still not pinned (G10).

G2 MINOR (a trap) -- the fixture writes into the packet directory, and the scripts cannot run from a copy.
   test_known_answers.py rewrites KNOWN_ANSWERS.json next to itself, and the label scripts write *_rows.json there too. A
   worker told not to modify originals has to copy the scripts, but bee_engine.py and l2_npe_p11.py hardcode
   REPO = 4 x ".." from their own directory, so a copy one level deeper fails on import. I patched the copies to 5 x "..".
   That is the only code change; the copies are in this directory and KNOWN_ANSWERS.json came out byte-identical.
   Fix: an --out flag, and REPO from `git rev-parse --show-toplevel` or an environment variable.

G3 MINOR -- the packet does not say which committed data each suggested new label would run on.
   I had to find them: ENVGATE "copier" = archaeon/envgate/LINEAGES.json (founder_tape, founder_class) plus
   archaeon/envgate/ruler.py; BEE SUSTAINED_LINEAGE = traced_replay.py / POST_CAMPAIGN_FORENSICS.md; NPE "runaway" =
   roles/Nestor/campaigns/c9x-explore-2026-09-24/c_runaway_confirm. This took about 10 minutes of searching.

G4 MINOR -- no prior-work pointers for the suggested labels, and no search log committed beside the packet.
   Under READY_PROTOCOL the packet is therefore DRAFT, not SEARCHED. RESULT.md s0 covers prior work for L1 to L3 only.
   For ENVGATE I found the prior work with prior_work_search.sh (log in this directory):
   - ENVGATE-01 review and adjudication;
   - ENVGATE-02 WINDOW_NOT_SUPPORTED and the closure record;
   - causal_lens FALSE_FRIENDS FF-1 (the lineage label, recertified by genetic identity: parent-chain counts 8-42x genetic);
   - census stage 2 (occupied-neighbour check: 95 of 176 vmcopy32 hits kept an exact copy);
   - CAUSAL_LINEAGE_CONTRACT v0.1.
   None of them recertifies the founder "copier" class itself, so the new label is not a repeat.
   Had it been a repeat, the packet would not have warned me: that was R4's blocking gap. Here it did not bite, so MINOR.

G5 MINOR -- the packet does not say what the new label's fixture must cover.
   It asks for "its own planted true instance and impostor". READ_FIRST asks for negative, positive and cheat controls.
   I required: one planted object per verdict, plus the frozen ruler's own class for each planted tape. That makes 16
   checks, listed in PREREG.md.

G6 MINOR (design, substantive) -- no guidance on what an "environment" is when the label is itself context-qualified.
   An EXACT_GATED copier copies at about 1 of 256 inputs by definition. If the inputs are taken as the environments,
   every gated copier comes out LABEL_CONTEXT_DEPENDENT, which the label already admits. I made the neighbour content
   the environment and swept the inputs inside each one. With min_rate at 0.5, the verdict boundary depends on this
   choice. The packet should say: "environments = contexts the label does NOT already qualify."

G7 MINOR -- the fixed thresholds are not portable across engines.
   T >= 0.5 presumes the copy routine takes up less than half of the tape. On 32-byte tapes, planted true copiers have
   T = 0.72 to 0.78 (an 11-byte routine), which is closer to the cut than on BEE's 64-byte tapes (0.91 to 0.94). The
   packet does not flag that T_MIN and min_rate are per-label choices to be justified.

G8 MINOR -- the default worker count is wrong for a shared machine.
   The label scripts and recert.run default to 4 forked workers. The packet does not mention compute or workers.
   RESULT.md gives timings measured with 4 workers (L1 346 s, L3 608 s). A worker on a shared laptop must know to pass
   --workers 1 or call recertify_one serially, as I did.

G9 MINOR -- the artifact name conflicts with READ_FIRST.
   PACKET.md asks for RESULT_COLDSTART.md, READ_FIRST asks for RESULT.md. I followed the packet.

G10 MINOR -- no input SHA is pinned, so STALE ("the packet's inputs moved") cannot be checked.
   RESULT.md names 02800d2b5, but the recert files are not in that commit (see G1).

G11 MINOR -- the harness has no progress output when run serially. recert.run prints progress only in the forked branch.

G12 MINOR -- concurrent work on L2 is not cited.
   The search found origin/artemis/challenge-2026-09-28 roles/Artemis/challenge/p11/ ("P-11 falsification RESULT --
   UNSOUND for heredity and OVER-STRICT; 6/57 natural donors re-pass, 4 of them zero-bit painters", 2af325f7b), now
   merged. It re-tests the same 57 P-11 donors as the packet's L2 and reports different counts: 6 re-pass versus the
   packet's 3 copiers and 17 painters. The packet predates it, but a worker extending L2 needs both, and the numbers
   should be reconciled.

## The six READY criteria

(a) Find every input: YES. All the inputs were in the worktree. At trial start the packet was not in git (G1, BLOCKING
    for an any-machine worker). It is now on origin/main, and I verified it from a fresh snapshot.
(b) Identify important prior experiments: YES, but not from the packet. RESULT.md s0 lists them for L1 to L3. For the new
    label they came from prior_work_search.sh and git grep (G4).
(c) State what is frozen and what may change: YES. The packet states it clearly: the verdict vocabulary and the fixture
    are frozen; label specs, environments and interventions may change. Per-label thresholds are left implicit (G7).
(d) Reproduce the known-answer fixture: YES, 24/24, KNOWN_ANSWERS.json byte-identical, 3.3 s. It needed the copy and
    patch in G2 so as not to overwrite a file in the owner's lane.
(e) State the falsifier: YES. For the harness it is in the packet: an impostor passed or a true instance rejected. For the
    label it is in PREREG.md, P2.
(f) Produce the artifacts: YES. RESULT_COLDSTART.md, l4_envgate_copier.py + test_l4_known_answers.py (16/16),
    L4_rows.json, L4_KNOWN_ANSWERS.json, PACKET_GAPS.md.

JUDGEMENT: NOT READY as the trial began, with one BLOCKING gap: G1, the packet was not in git. G1 was fixed during the
trial by d3941cb07, and I verified the fix from an origin/main snapshot (fixture 24/24, unpatched, byte-identical).
Against the committed packet at 281eeed50, this trial met (a) to (f), and G2 to G12 are all MINOR. My judgement is
therefore READY at origin/main 281eeed50. Record both facts in the ledger row: "blocking at start, fixed mid-trial". Pin
the SHA in PACKET.md (G10) so that STALE can be checked.
