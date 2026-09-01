"""The organization interface: what is SUPPLIED and what may EMERGE.

SUPPLIED (identical for every organized arm; frozen here):
  1. an input encoding: raw genotype bytes -> 64-bit machine words, and raw
     train-example integers -> 64-bit machine words. No statistic, no
     summary, no category. The evidence encoding STRUCTURALLY cannot read
     task_id (see evidence_words) -- task_id is a content hash of the whole
     task and would be a perfect task fingerprint;
  2. a key width: 64 bits;
  3. a comparison: Hamming distance between an artifact key and a query key;
  4. selection: the k lowest-Hamming artifacts, deterministic hash tiebreak;
  5. a retrieval-time step cap: KEY_MAX_STEPS per key computation, so a key
     function cannot run a search inside itself.

EMERGENT (nothing below is supplied):
  - what the key of an artifact is, i.e. which experiences collide, which
    distinctions survive, and which are discarded;
  - what the query key of a task is, i.e. what makes an experience relevant;
  - the granularity of the induced partition (how many keys are used at all);
  - which bits carry structure and which are dead.

An organizer genome is ONE byte string, decoded totally (every byte string
decodes) into two substrate programs. It is therefore an ordinary substrate
artifact with ordinary substrate lineage: its provenance is the Foundry's,
not a bespoke record.
"""
from __future__ import annotations

import hashlib
import math
from collections import Counter
from dataclasses import dataclass
from typing import Sequence

from foundry.core.schemas import TaskEvidence
from foundry.engines.gp.stackvm import vm

# -- frozen supplied constants ---------------------------------------------
KEY_BITS = 64
KEY_MAX_STEPS = 300
KEY_WALL_S = 3600.0          # D7: can never bind before KEY_MAX_STEPS
MAX_ARTIFACT_WORDS = 24      # 192 genotype bytes reach the key function
MAX_EVIDENCE_EXAMPLES = 8
MAX_EVIDENCE_SLOTS = 4       # inputs per example that reach the key function
_MASK = (1 << 64) - 1


# -- input encodings --------------------------------------------------------

def artifact_words(genotype: bytes) -> list[int]:
    """[w0, w1, ...]: the genotype bytes packed 8-at-a-time little-endian.

    PHASE 2 REPAIR D1. This function previously emitted `len(g)` as word 0,
    which the VM mirrors into register R0, so the two-byte program `LDR R0`
    returned the genotype length EXACTLY (verified for lengths
    7/16/40/96/250; word0 == len(g) for 400/400 sampled genotypes). Length
    is a strong proxy for source history task and for position within a
    history run, so this was an experimenter-SUPPLIED channel to nuisance
    variables. It is removed.

    Residual, DECLARED, and measured in the reconstruction audit rather
    than asserted away:
      - the NUMBER of words still varies with genotype length. That is
        intrinsic (a longer program genuinely has more content), not
        supplied, and StackVM has no stack-depth opcode.
      - the final partial word is zero-padded, so `len(g) mod 8` is weakly
        encoded in the trailing zero bytes of the last word. This IS a
        supplied artifact of the packing and is measured in the audit.
    """
    g = bytes(genotype)
    words = []
    for i in range(0, min(len(g), MAX_ARTIFACT_WORDS * 8), 8):
        words.append(int.from_bytes(g[i:i + 8].ljust(8, b"\x00"), "little"))
    return words


def evidence_words(evidence: TaskEvidence) -> list[int]:
    """[n_examples, arity, (inputs..., output) per example].

    Reads evidence.train_examples ONLY. task_id is never touched: it is a
    content hash of the complete task (train AND test cases) and would let a
    key function memorise task identity instead of organising experience.
    value_kinds is not read either -- it is a structural type tag, and the
    raw values already carry whatever the machine can use.
    """
    exs = list(evidence.train_examples)[:MAX_EVIDENCE_EXAMPLES]
    arity = len(exs[0].inputs) if exs else 0
    words = [len(exs), arity]
    for ex in exs:
        ins = list(ex.inputs)[:MAX_EVIDENCE_SLOTS]
        for v in ins:
            words.append(vm.machine_word(v))
        for _ in range(MAX_EVIDENCE_SLOTS - len(ins)):
            words.append(0)
        words.append(vm.machine_word(ex.output))
    return words


# -- organizer genome -------------------------------------------------------

def decode(genome: bytes) -> tuple[bytes, bytes]:
    """Total decode of an organizer genome into (KA, KQ). Every byte string
    decodes; there is no invalid organizer, exactly as there is no invalid
    substrate program."""
    g = bytes(genome)
    if len(g) < 3:
        return g, g
    body = g[2:]
    n = int.from_bytes(g[:2], "big") % (len(body) + 1)
    return body[:n], body[n:]


class NondeterministicKey(RuntimeError):
    """The wall-clock backstop preempted the deterministic step meter, so
    the key would depend on machine load. Fail loudly rather than return a
    load-dependent key (PHASE 2 REPAIR D7)."""


def _run_key_vm(program: bytes, words: Sequence[int]):
    """Key semantics terminate on the DETERMINISTIC step meter only.

    PHASE 2 REPAIR D7. `timeout_s` was previously 5.0, so a key program
    running near the wall-clock backstop produced a DIFFERENT key on a
    loaded machine than on an idle one: the object of study was not
    reproducible. KEY_WALL_S is set far above anything KEY_MAX_STEPS can
    reach, so the step meter always binds first. If the wall ever fires it
    is an operational abort, never a valid key.
    """
    r = vm.run_program(program, list(words), max_steps=KEY_MAX_STEPS,
                       timeout_s=KEY_WALL_S)
    if r.halt == "wall":
        raise NondeterministicKey(
            f"wall-clock backstop fired at {r.steps} steps (cap "
            f"{KEY_MAX_STEPS}); key semantics must be step-determined")
    return r


def run_key(program: bytes, words: Sequence[int]) -> int:
    """Run a key program on an encoded input; the key is the u64 reading of
    the final stack top (0 if the stack is empty). Metered at KEY_MAX_STEPS;
    a metered-out program still yields whatever key it has produced --
    pathology is data, not an error."""
    if not program:
        return 0
    r = _run_key_vm(program, words)
    return (r.stack[-1] & _MASK) if r.stack else 0


def key_and_steps(program: bytes, words: Sequence[int]) -> tuple[int, int]:
    if not program:
        return 0, 0
    r = _run_key_vm(program, words)
    return ((r.stack[-1] & _MASK) if r.stack else 0), r.steps


# -- the organization itself ------------------------------------------------

@dataclass(frozen=True)
class Organization:
    """A built organization over one frozen corpus: one key per artifact."""
    artifact_ids: tuple
    keys: tuple
    genome_addr: str
    build_steps: int
    mask: int = _MASK           # ablation: bits zeroed on BOTH sides

    def stats(self) -> dict:
        n = len(self.keys)
        masked = [k & self.mask for k in self.keys]
        distinct = len(set(masked))
        marg = [(sum((k >> b) & 1 for k in masked) / n if n else 0.0)
                for b in range(KEY_BITS)]
        live = sum(1 for m in marg if 0.02 < m < 0.98)
        occ = Counter(masked)
        h = (-sum((c / n) * math.log2(c / n) for c in occ.values())
             if n else 0.0)
        return {"n_artifacts": n, "n_distinct_keys": distinct,
                "key_entropy_bits": h, "live_bits": live,
                "bit_marginals": marg,
                "max_bucket": max(occ.values()) if occ else 0}

    def with_mask(self, mask: int) -> "Organization":
        return Organization(self.artifact_ids, self.keys, self.genome_addr,
                            self.build_steps, mask & _MASK)

    def scrambled(self, seed: int) -> "Organization":
        """Same key multiset, permuted across artifacts. Preserves every
        superficial statistic of the organization (key histogram, entropy,
        bit marginals, granularity) and destroys only which artifact holds
        which key."""
        import random
        rng = random.Random(seed)
        ks = list(self.keys)
        rng.shuffle(ks)
        return Organization(self.artifact_ids, tuple(ks), self.genome_addr,
                            self.build_steps, self.mask)


def build_organization(genome: bytes, artifact_ids: Sequence[str],
                       genotypes: Sequence[bytes],
                       genome_addr: str = "") -> Organization:
    ka, _ = decode(genome)
    keys, steps = [], 0
    for g in genotypes:
        k, s = key_and_steps(ka, artifact_words(g))
        keys.append(k)
        steps += s
    return Organization(tuple(artifact_ids), tuple(keys), genome_addr, steps)


def query_key(genome: bytes, evidence: TaskEvidence) -> int:
    _, kq = decode(genome)
    return run_key(kq, evidence_words(evidence))


def _tiebreak(seed: int, artifact_id: str) -> str:
    return hashlib.sha256(f"{int(seed)}/{artifact_id}".encode()).hexdigest()


def retrieve(org: Organization, qkey: int, k: int,
             seed: int) -> list:
    """The k artifacts whose keys are closest in Hamming distance to the
    query key. Ties broken by a deterministic per-(seed, id) hash."""
    q = qkey & org.mask
    scored = [(bin((key & org.mask) ^ q).count("1"), _tiebreak(seed, aid), aid)
              for aid, key in zip(org.artifact_ids, org.keys)]
    scored.sort()
    return [(aid, d) for d, _, aid in scored[:max(0, min(k, len(scored)))]]
