# WP-6 External replication-barrier synthesis and the minimal-donor landscape

**Question.** Where does NPE sit among self-reproducing program systems, measured by what the environment
supplies to a reproducer and what the reproducer must encode? Which of NPE's barriers are generic, and which are
artefacts of NPE's choices?

**Starting material.**
- delegates/EXTERNAL_RESEARCH.md: ~8,200 words, 12 lines of prior art, 15 proposed experiments, 13 pitfalls.
  Claims marked [M] are from memory and need verification.
- delegates/CROSS_ENGINE.md.

**Method.**
1. **Verify the [M] claims** (Eigen error threshold numbers, the Coreworld details, Lenski's 23/50 counts) against
   primary sources, and replace or strike them.
2. **Build a comparison table.** Rows: BFF, the 2024 and 2026 Z80 soups, Avida, Tierra, Coreworld, Amoeba,
   Stringmol, NPE. Columns:
   - reset state;
   - self-location supply;
   - copy primitive and encoding;
   - copy-count supply;
   - the state passed outside the genome;
   - the establishment reference number;
   - the descendant-competence measure.
3. **Minimal-donor landscape (T-CTX-5, LIGHT).** Enumerate or sample the shortest COMPETENT donors under zero-state
   and random-state certification, on stock and dense VMs. Cluster them by one-mutation connectivity (following
   C G et al. 2017). Is "borrow the environment's addressing" the shortest path?
4. **Write the synthesis** as a short paper-style note: `EXTERNAL_SYNTHESIS.md` in this campaign.

**Resources.** Steps 1, 2 and 4: REPO (a web-capable agent). Step 3: LIGHT, ~2-4 h on 2 processes.

**Done when.** The table and landscape are committed, and each NPE barrier is labelled GENERIC or NPE-SPECIFIC,
with reasons.
