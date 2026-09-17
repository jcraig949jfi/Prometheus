# POET / ALife autopsy -- the directive's claims checked against source, and the harvest targets

Techne[gandalf-a04f7c25], 2026-09-17, M3. Directive 2 committed verbatim at
roles/Techne/prompts/2026-09-17_poet_alife/OPERATOR_2_autopsy.md (MANIFEST beside it). Claim
ledger with file:line evidence and grades: techne/acquisition/poet_alife/AUTOPSY_CLAIMS_2026-09-17.json.
Lane: Techne acquires bodies, provenance and worlds and proves they run; Nyx performs the chop
(Founding Charter, 2026-09-16). This document is therefore the ACQUISITION side of the autopsy the
directive asks for: what is verified, what is pinned, what each excavation needs, and what the
systems throw away. It names no organs.

## 1. Scorecard of the directive's checkable statements (28 claims)

    VERIFIED_SOURCE  13   read in the file at the pinned commit
    VERIFIED_API      6   GitHub / Hugging Face / Crossref / arXiv
    MEASURED          2   reproduced on M3 today (sections 3 and 4)
    PAPER_ONLY        5   the paper says it; code or data not checked
    CORRECTED         1   our Avida fossil does not yet emit a population file
    NOT_VERIFIED      1   the phylotrack paper's DOI

No statement in the directive was found false. Three were imprecise (PATA-EC's clip bounds are
the minimal-criterion bounds; the normalisation is centered ranks in [-0.5, 0.5]; Avida has two
more geometries than listed). The directive's "This was one of your specific questions" refers
to a conversation not in this session.

## 2. Enhanced POET, from the source (uber-research/poet@8669a17e)

Lifecycle as the code has it (poet_algo.py, es.py, novelty.py, reproduce_ops.py):
  admission    get_child_list(): parent picked from optimizers whose score passes MC ->
               Reproducer.mutate() -> pass_dedup() -> pass_mc() on the PARENT's theta ->
               compute_novelty_vs_archive() (k=5 nearest in PATA-EC space over archive +
               active; Euclidean with last-element padding when lengths differ) -> children
               sorted by novelty, max_admitted per adjust_envs_niches()
  PATA-EC      update_pata_ec(): every archived + active theta evaluated on this env, clipped
               to [mc_lower, mc_upper], compute_centered_ranks() -> the env's vector
  transfer     evaluate_transfer(): each source theta evaluated directly and after ONE proposed
               ES step; best becomes the proposal; pick_proposal() adopts it if it beats the
               checkpoint score; the CSV cell accept_theta_in_<id> records the source id
  archive      remove_oldest() moves the oldest active envs to archived_optimizers when the
               active set exceeds max_num_envs; env_archive holds every env config ever made
  persistence  one CSV per optimizer (po/eval returns, accept_theta_in, theta_from_others,
               proposal_from_others, iteration, time) + <id>.best.json = [theta, score]
Thrown away: parent_optim_id (computed, printed to the log, never written structured); the
PATA-EC vector at admission; the rejected children and their novelty; anything causal. The
directive's "thin fossils" reading is correct and now has line numbers.

## 3. ASAL's open-endedness score, measured (SakanaAI/asal@677ba0ea, asal_metrics.py:53)

The score is: for each frame, the maximum cosine similarity to ANY EARLIER frame; mean over
frames; minimised. Re-implemented in numpy on unit vectors, T=8, D=512, seed 0:

    static frame          0.8750
    coherent slow drift   0.8654
    two-frame cycle       0.7500
    iid random frames     0.0390     <- 22x "more open-ended" than coherent drift

So the metric rewards frame-to-frame dissimilarity in embedding space and nothing else; frame 0
contributes 0 by construction (its lower-triangle row is empty). This is a control on the METRIC
FUNCTION. It is not yet a control on the pipeline: CLIP does not map noise images to orthogonal
vectors, so whether a substrate can game the real system is an image-level experiment
(TECHNE-107). The 8x224x224x3 -> 8x512 claim is verified in README.md:55-62 and rollout.py:22.
Three of the four published .npz datasets answer 200 today; illumination_lenia.npz is 404.

## 4. TerraLingua's artifact phylogeny: provenance or inference? (cognizant-ai-lab/terralingua@bf276dbe)

006_artifact_philogeny.py declares two methods: (1) "hand annotation" = explicit mentions of
earlier artifacts in the agent's reasoning, observations and memory at creation time (text
matching on the agent's own words); (2) LLM inference, claude-haiku-4-5, asked to choose
ancestors from a candidate list with a relationship type and a confidence (LLM_PHYLOGENY = True
by default). The script reads no logged parent or source-artifact id; the environment records
what the agent observed, not which artifact it copied. So the answer to the directive's question
is: NONE of the claimed conceptual ancestry is deterministic provenance; it is text match or
model inference over a 4.7 GB, 40-experiment, 27,578-file dataset (Apache-2.0) whose annotations
were themselves produced by Claude Sonnet 4.5 and Haiku 4.5. That is the cautionary specimen the
directive hoped to find: a cultural-fossil pipeline whose lineage edges are inferred after the
fact by the same class of model that generated the behaviour.

## 5. Avida and Tierra: what our vault already has and what one more line buys

Avida is a running fossil (RUNNABLE_CONTAINER, smoke PASS, devosoft/avida@47f13dad, in the
fossil-lang world on M1/M2). Its smoke runs 300 updates of the STOCK events.cfg, which prints
average / dominant / count / tasks / time / resource data and never calls SavePopulation, so no
.spop exists from our run. One added event line (`u 300 SavePopulation` with ancestry options,
to be read from the Avida docs) plus converters-avida (MIT, pinned; example .spop and standard
phylogeny CSV/JSON in its example_data) turns our own run into a near-perfect phylogeny the
directive can open. The world geometries the directive lists are in avida.cfg lines 26-34, plus
5 partial and 6 3D lattice (under development).
Tierra: three mirrors of Ray's 6.02 source pinned; gene-bank machinery is in the tree
(genebank.h/.x, genebank_xdr.c, rambank.c, diskbank.c, gb0..gb8, NetgbTom). GitHub reports no
licence; tierra/license.h exists and must be READ before any body enters the vault
(LEGAL_RESTRICTION is a classification in record.py for exactly this).

## 6. Lineage-tracking tools, pinned

phylotrackpy (MIT), hstrat (JOSS 2022, DOI 10.21105/joss.04866), Empirical, MABE,
alife-data-standards (MIT), converters-avida (MIT). Persistence filtering and shadow runs come
from the MODES toolbox (Dolson, Vostinar, Wiser, Ofria; preprint DOI 10.7287/peerj.preprints.
27249v3) and the ancestry analyses from Tape of Life (Artificial Life 2020, DOI
10.1162/artl_a_00313). Neither PDF was read; that is the next literature act, and it is small.

## 7. Harvest targets filed (each is a body Techne can put in front of Nyx)

  TECHNE-104  POET as a fossil: harvest uber-research/poet (both branches) into the vault with a
              gym[box2d] world; ONE environment traced birth -> mutation -> MC -> PATA-EC ->
              admission -> transfer -> archive with every record that survives each boundary
              captured; host with a compiler and docker (M2)
  TECHNE-105  Avida phylogeny from OUR run: SavePopulation event added to the fossil's harness,
              .spop converted with converters-avida, one lineage reconstructed; host M2
  TECHNE-106  Tierra as a fossil: read license.h, pin the 6.02 tarball origin, build in the
              fossil-c world, generate a gene bank, hash it; host M2
  TECHNE-107  ASAL metric pipeline control: image-level cheat (noise / colour-cycling frames
              through CLIP) vs a Lenia rollout; CPU JAX + CLIP weights; possibly M3
  TECHNE-108  TerraLingua: one artifact's genealogy re-derived from the raw logs by the two
              methods separately, agreement measured; needs the dataset (4.7 GB) and, for
              method 2, a model API key -- the inference half is a Nyx/Harmonia question,
              the provenance half is data only
None of these is EXECUTE today: M3 has no compiler, no docker, and the Donor Foundry loop
stops at PIN until the operator's directive is read as the DEMAND (it is; the rows say so).

## 8. What this does not claim

No organ is named; no mechanism is extracted; nothing was run except a 10-line numpy control.
The five source-level autopsies the directive describes are Nyx's chop on bodies Techne has not
yet harvested. Conflict of interest: the "throws away" findings favour the fossil-packet design
this seat already owns.
