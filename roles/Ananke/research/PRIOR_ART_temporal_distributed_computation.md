# PRIOR ART: temporal and distributed computation, carriers of state in flight

Seat: Ananke (PTE engine). Written 2026-09-27 as an external literature raid.
Status: DRAFT for operator review. Not committed by the author.

Scope. PTE-C1/C1b found (a) M2 HOLD memory carried by packets in flight (register
reset mid-gap = no effect; in-flight flush mid-gap = chance; 3/3 fresh-seed
champions; payload[0] signed sum does not decode; plastic routing weights
contribute slightly), (b) M3 MAJ needs arrival exactly on the readout tick
(+1 tick kills, -1 tick fine) and needs SETRULE, but the readout site's rule
index carries no cue, and (c) an instrument lesson: an ablation window that
excluded the readout tick hid a transport mechanism.

This file asks, for each prior-art item, the 8 questions:
 Q1 where is state represented; Q2 what makes it persistent; Q3 how is it read
 out; Q4 values vs timing vs topology vs interaction; Q5 designed or emergent;
 Q6 what intervention establishes the mechanism; Q7 what distinguishes it from
 what Ananke sees; Q8 code/system worth studying or fossilizing.

Analogy strength is graded explicitly: STRONG (same mechanism class, same
intervention logic applies), MODERATE (shared structure, different physics or
readout), WEAK (terminology or metaphor only). Terminology matches are not
treated as conceptual matches.

Citations were checked by web search on 2026-09-27; DOIs/URLs given where found.
Anything I did not verify is marked [unverified].

---------------------------------------------------------------------------

## 0. Bottom line first (decision-relevant)

1. "State lives in the channels" is not new; it is the textbook definition of
   the global state of a message-passing system (Chandy & Lamport 1985: global
   state = process states + channel states). Ananke's register-reset null plus
   flush-kills result is exactly the experiment that localizes state to the
   channel component. PTE should adopt that vocabulary: site state, channel
   state, configuration (program/rule/weights), and not "memory vs transport".

2. What IS open in M2 is the discriminating question the delay-line literature
   forces: is it (a) a single long-latency flight (a delay, not a memory), or
   (b) recirculation with regeneration (a delay-line / reverberation memory, like
   mercury lines, fiber-loop buffers, pingfs, Dijkstra's circulating token)?
   Decisive test: sweep gap length beyond the maximum single-trip latency
   (base + hops*per_hop + max jitter). Survival beyond that bound requires
   re-emission. Also: flush a single edge / single channel id, not everything,
   to locate the loop; and vary noise to look for a recirculation ceiling
   (fiber-loop buffers have a recirculation limit set by accumulated amplifier
   noise; PTE's per-hop noise should produce an analogous ceiling if M2 is a loop).

3. The failure of payload[0]-sum decoding is the expected result, not an
   anomaly, if the cue is in timing, counts, channel ids, or a synergistic
   combination of payload components. Covert-timing-channel, network-coding,
   hyperdimensional (superposition/bundling) and non-normal "memory trace"
   literatures all predict that a single linear projection can miss the code.
   Use a time-resolved multivariate decoder over full in-flight features plus
   cross-temporal generalization (King & Dehaene 2014).

4. Lizier's information dynamics already formalizes storage / transfer /
   modification locally in space-time, and (Lizier, Atay & Jost 2012) shows
   that storage at a node is analytically produced by feedback-loop and
   feedforward-loop motifs, i.e. storage is realized by transfer around loops.
   So "M2 is transport, not memory" and "M2 is memory" are both correct at
   different scales. The split is scale- and variable-choice-dependent; Ananke
   must state the variable set (with or without channel state) before labeling.

5. Activity-silent working memory is the closest neuroscience analogue, but
   the PTE mapping is INVERTED relative to what the brief suggests: in PTE the
   "silent" substrate (registers) is NOT carrying the cue; the "active" traffic
   IS. M2 is therefore persistent-activity-like (reverberation), not
   activity-silent. The activity-silent literature is most useful for (i) the
   configuration-vs-cue question in M3 (task set/context vs item), and
   (ii) its instrument: the "ping" (impulse perturbation, Wolff et al. 2017;
   TMS reactivation, Rose et al. 2016) to reveal hidden cue content in weights
   or rules that is not visible in activity.

6. "Readout site's rule index carries no cue" is a marginal statement. It does
   not rule out synergistic (XOR-like) encoding jointly with registers or
   traffic, nor cue content at other sites/ticks. Partial information
   decomposition or conditional MI across all sites and ticks is needed before
   "SETRULE is configuration, not memory" is a claim.

7. The temporal-window blindness lesson has a direct prior-art cure: local
   (pointwise) information measures computed at every (site, tick) and
   time-resolved "virtual lesion" sweeps whose window start and end are both
   swept, including the readout tick.

8. M3's exact-arrival constraint is a deadline, not (yet) a timing code. The
   polychronization / synfire / asynchronous-circuit literature is relevant only
   if cue identity maps to arrival time. Test that before importing their
   vocabulary. Asynchronous-circuit design gives the right frame for the
   fragility itself: M3 is a "bundled-data" solution (relies on a timing
   assumption), not delay-insensitive.

---------------------------------------------------------------------------

## 1. Delay-line and recirculating memory (the "carrier in flight" family)

### 1.1 Mercury delay-line memory (Eckert et al. 1949; EDSAC 1949)
Sources: Eckert, Auerbach, Shaw, Sheppard, "Mercury Delay Line Memory with
Megacycle Pulse Rate", Proc. IRE 37(8):855-861, 1949. EDSAC: 32 mercury tanks,
576 bits each. CHM: https://www.computerhistory.org/storageengine/edsac-computer-employs-delay-line-storage/
 Q1 State: acoustic pulses in transit through the mercury column. Nothing at
    rest holds the bit; the tank is the channel.
 Q2 Persistence: recirculation plus regeneration. Output transducer ->
    amplifier/reshaper -> re-injection at input. Without regeneration the pulse
    train decays in one transit (about 1 ms).
 Q3 Readout: serial; wait for the word's time slot to pass the output
    transducer. Access is timing-addressed.
 Q4 Timing (address = phase within the circulation period) + values (pulse /
    no pulse).
 Q5 Designed.
 Q6 Mechanism established by construction; the diagnostic intervention is:
    break the regeneration path and the store empties in one period.
 Q7 PTE M2 has no designed regenerator; if M2 is a delay line, some site
    programs must be acting as regenerators (receive -> re-emit). The key PTE
    test is whether the carrier survives gaps longer than one transit. Also:
    EDSAC slots are individuated pulses; PTE packets superpose (sum) on arrival,
    so the "bit" may be a summed amplitude, not a pulse slot.
 Q8 Historical only. EDSAC replica at TNMOC: https://www.tnmoc.org/edsac
 Strength: STRONG as a mechanism hypothesis for M2 (the one the data suggest),
 unproven until the gap-vs-max-latency test is run.

### 1.2 Fiber-loop optical buffers (all-optical packet switching)
Sources: e.g. "SOA gate array recirculating buffer with fiber delay loop",
Opt. Express 16(12):8451 (2008) https://opg.optica.org/oe/fulltext.cfm?uri=oe-16-12-8451&id=162952 ;
"Photonic integrated circuit optical buffer for packet-switched networks",
Opt. Express 17(8):6629 (2009) https://opg.optica.org/oe/fulltext.cfm?uri=oe-17-8-6629&id=179005 ;
review-level summary of the recirculation limit: "Simulation of fiber loop buffer
memory of all-optical packet switch" https://www.researchgate.net/publication/2504105
 Q1 State: packets circulating in a fiber loop.
 Q2 Recirculation through an amplifier; bounded by a RECIRCULATION LIMIT set by
    accumulated amplified spontaneous emission (ASE) noise and crosstalk.
 Q3 A switch gates the packet out on the right circulation.
 Q4 Values (packet bits) + timing (which lap).
 Q5 Designed.
 Q6 Count laps until BER exceeds threshold; vary amplifier noise.
 Q7 PTE has additive noise, loss and duplication per hop. If M2 is a loop, the
    fiber-buffer literature predicts a maximum gap length that falls as per-hop
    noise/loss rise (a recirculation ceiling), and holding time quantized to
    loop period. If instead M2 degrades smoothly with gap independent of loop
    structure, it is not a loop.
 Q8 No code worth fossilizing; the recirculation-limit law is the takeaway.
 Strength: STRONG for the noise-ceiling prediction.

### 1.3 pingfs (network as delay-line storage)
Source: https://github.com/yarrick/pingfs ("Stores your data in ICMP ping
packets"); discussion https://www.networkworld.com/article/748584/
 Q1 Data only in ICMP echo packets in flight between host and remote servers.
 Q2 Host re-sends each echoed block on receipt (regeneration by the host).
 Q3 Read by waiting for the block's echo.
 Q4 Values in payload; the network latency is the storage medium.
 Q5 Designed (a joke with a real point).
 Q6 Kill the re-send loop -> data gone within one RTT.
 Q7 Identical logic to M2 if M2 regenerates. A tiny, readable reference
    implementation of "memory = traffic + re-emission". It also illustrates
    that capacity = bandwidth x round-trip time.
 Q8 Worth a look; tiny C code, FUSE + raw sockets. Not needed for fossil vault.
 Strength: STRONG as a conceptual demo, WEAK as science.

### 1.4 Dijkstra self-stabilizing token ring (1974)
Source: Dijkstra, "Self-stabilizing systems in spite of distributed control",
CACM 17(11):643-644, 1974. Eindhoven portal:
https://research.tue.nl/en/publications/self-stabilizing-systems-in-spite-of-distributed-control/
Verified-model repo: https://github.com/steinar/tokenring
 Q1 State: a "privilege" (token) that is a relation between neighbors' states,
    not a value held by any one process.
 Q2 The protocol regenerates exactly one token from any initial state.
 Q3 A process knows it holds the token by comparing its state with its
    predecessor's.
 Q4 Interaction/relational (the token is a mismatch between neighbors).
 Q5 Designed.
 Q6 Corrupt arbitrary states; show convergence to one circulating token.
 Q7 Relevant to Ananke's "regenerated state" theme: a carrier that is
    re-created by local rules after perturbation. Important difference: Dijkstra
    guarantees convergence to A token, erasing which-token information, so it
    is a model of regenerated configuration, not regenerated cue. This is a
    useful foil: if M2's carrier survives a partial flush and the cue is
    restored, that is cue regeneration; if only traffic is restored and the cue
    is lost, it is configuration regeneration.
 Q8 Small; tokenring repo is a Rebeca model. Not worth fossilizing.
 Strength: MODERATE (a sharp foil for "regenerated state").

---------------------------------------------------------------------------

## 2. Distributed-systems state and messages in flight

### 2.1 Chandy & Lamport, Distributed snapshots (1985)
Source: ACM TOCS 3(1):63-75, 1985, doi:10.1145/214451.214456 ;
PDF https://lamport.azurewebsites.net/pubs/chandy.pdf
 Q1 Global state = local process states + CHANNEL STATES (sequences of
    messages sent but not yet received).
 Q2 n/a (it is a definition plus an algorithm to record a consistent cut).
 Q3 Marker messages delimit which in-flight messages belong to the snapshot.
 Q4 Values + causal order.
 Q5 Designed.
 Q6 The snapshot algorithm is itself the "instrument": record all process
    states and all channel contents at a consistent cut.
 Q7 This is the formal vocabulary Ananke is missing. Ananke's M2 experiment
    is: zero process state -> no effect; zero channel state -> effect. In
    C-L terms, the cue lives in channel state. PTE differs from C-L's model in
    three ways that matter: (i) PTE channels are not FIFO sequences, arrivals
    SUPERPOSE, so "channel state" is a per-(receiver, arrival tick, channel id)
    accumulator, not a message list; (ii) loss and duplication violate C-L's
    reliable-channel assumption; (iii) PTE's global tick makes consistent cuts
    trivial in sync mode but not in async mode.
 Q8 No code needed; adopt the definition. For async PTE runs, a consistent
    cut must be defined before "state at tick t" is meaningful.
 Strength: STRONG (formal frame; not a mechanism).

### 2.2 Parasitic computing (Barabasi et al. 2001)
Source: Nature 412:894-897, 2001, doi:10.1038/35091039
https://www.nature.com/articles/35091039
 Q1 Candidate solutions encoded in crafted TCP packets; the "computation" is
    the remote host's checksum verification.
 Q2 n/a (single round trip).
 Q3 Reply (accepted) vs silence (dropped) is the answer bit.
 Q4 Interaction: the protocol's validity check is the gate.
 Q5 Designed.
 Q6 By construction.
 Q7 Shows protocol side effects (accept/drop) can carry computation. In PTE,
    receiver caps, collisions and drop rules are similar side-channels that an
    evolved program could exploit. WEAK as mechanism analogue, MODERATE as a
    warning that simulator plumbing is part of the computational substrate.
 Q8 No.

### 2.3 Network coding (Ahlswede, Cai, Li, Yeung 2000)
Source: "Network information flow", IEEE Trans. Inf. Theory 46(4):1204-1216,
2000, doi:10.1109/18.850663 ; PDF https://www.cs.cornell.edu/courses/cs783/2007fa/papers/acly.pdf
 Q1 Intermediate nodes transmit functions (typically linear combinations) of
    received packets; information is in combinations, not in individual flows.
 Q2 n/a.
 Q3 Sinks invert the combination (solve a linear system); needs enough
    independent combinations (rank).
 Q4 Values combined by interaction (algebraic mixing).
 Q5 Designed.
 Q6 Rank analysis of the transfer matrix from sources to sink.
 Q7 PTE's superposition on arrival IS a forced linear combination (over the
    integers, with noise). Network coding predicts that the recoverable
    information at a receiver is governed by the rank of the source->receiver
    combination, and that per-component sums can be uninformative while a
    different linear functional is fully informative. That is one concrete
    explanation of the payload[0]-sum decoding failure. Difference: PTE mixing
    is not chosen per node (it is fixed summation), but evolved programs choose
    WHAT to send, so they can shape the code.
 Q8 No code needed; adopt "rank of the cue->carrier map" as a diagnostic.
 Strength: MODERATE.

### 2.4 IP covert timing channels (Cabuk, Brodley, Shields 2004)
Source: Proc. ACM CCS 2004, pp. 178-187, doi:10.1145/1030083.1030108 ;
PDF https://people.cs.georgetown.edu/~clay/research/pubs/cabuk.ccs2004.pdf
 Q1 Bits encoded in the presence/absence of packets in time intervals
    (inter-packet timing), not in payload.
 Q2 n/a (communication, not storage).
 Q3 Receiver bins arrival times.
 Q4 TIMING.
 Q5 Designed.
 Q6 Detection by regularity statistics of inter-arrival times (their
    epsilon-similarity and compressibility tests).
 Q7 Useful for M2's decoding failure: if the evolved code is "packet present
    on tick t mod k" or "number of packets in flight", payload sums will not
    decode it. Their detection statistics (regularity / compressibility of
    inter-arrival times) are cheap probes of whether PTE traffic during the gap
    is structured. Designed and adversarial, so the analogy is about the
    carrier type only.
 Q8 No.
 Strength: MODERATE (carrier-type hypothesis generator).

### 2.5 Address-event representation (Boahen 2000)
Source: "Point-to-point connectivity between neuromorphic chips using address
events", IEEE TCAS-II 47(5):416-434, 2000.
https://www.researchgate.net/publication/3325509
 Q1 Spikes are sent as address packets on a shared bus; the time of the event
    is implicit in when the packet arrives.
 Q2 n/a.
 Q3 Arrival time + address.
 Q4 Timing + topology (address = which neuron).
 Q5 Designed.
 Q6 n/a.
 Q7 AER is the engineering precedent for "packets whose timing carries
    meaning", and its known pathologies (collisions, arbitration jitter
    distorting timing) are close to PTE's receiver caps and jitter. WEAK-MODERATE.
 Q8 Many open AER stacks exist; not needed.

---------------------------------------------------------------------------

## 3. Reservoir computing, fading memory, delay-based reservoirs

### 3.1 Echo state networks and memory capacity (Jaeger 2001/2002)
Source: Jaeger, "Short term memory in echo state networks", GMD Report 152
(2001/2002). Overview: http://www.scholarpedia.org/article/Echo_state_network
 Q1 Transient state of a fixed random recurrent network.
 Q2 Fading memory: the echo state property guarantees input dependence decays;
    memory lasts about as long as spectral radius / leak allows.
 Q3 Trained linear readout.
 Q4 Values (activations).
 Q5 Reservoir random (neither designed nor evolved for the task); readout trained.
 Q6 Memory capacity MC = sum over k of the squared correlation between a
    linear readout's output and the input delayed by k. Bounded by N.
 Q7 PTE's substrate is fixed per run and the programs evolve; RC fixes the
    substrate and trains only the readout. But MC is directly portable: drive
    PTE with an i.i.d. input stream at the cue site and fit linear readouts of
    u(t-k) from the in-flight features. That gives a memory function k -> r^2
    that is independent of task and exposes whether in-flight traffic is a
    general fading memory or a task-specific latch.
 Q8 Many implementations (e.g. ReservoirPy https://github.com/reservoirpy/reservoirpy [unverified URL]).
 Strength: MODERATE (instrument more than mechanism).

### 3.2 Liquid state machines (Maass, Natschlager, Markram 2002)
Source: Neural Computation 14(11):2531-2560, doi:10.1162/089976602760407955
 Q1 Transient spiking-network trajectories ("without stable states").
 Q2 Fading memory of the input history; no attractor.
 Q3 Memoryless readout trained on the current liquid state.
 Q4 Values + timing of spikes.
 Q5 Liquid generic, readout trained.
 Q6 Separation property (distance between liquid states for different inputs)
    and approximation property of readouts.
 Q7 LSM's "computation without stable states" is the theoretical permission
    slip for M2: a bit can be held by a transient that never settles. But an
    LSM's memory is fading, so a HOLD across a long distracted gap would fail
    unless the carrier regenerates. Separation property is a portable metric:
    distance between in-flight feature vectors for cue=0 vs cue=1 across the gap.
 Strength: MODERATE.

### 3.3 Information processing capacity (Dambre et al. 2012)
Source: Sci. Rep. 2:514, doi:10.1038/srep00514 ; code (third party, Kubota):
https://github.com/kubota0130/ipc
 Q1 Any dynamical system's state variables.
 Q2 Fading memory condition.
 Q3 Linear readouts of orthogonal polynomial functions of past inputs.
 Q4 Values.
 Q5 n/a (a measure).
 Q6 Total capacity bounded by the number of linearly independent state
    variables; decomposes into linear memory vs nonlinear (degree>1) capacity.
 Q7 IPC would separate "PTE traffic stores the input" (degree-1, delay k)
    from "PTE traffic computes a function of inputs" (degree 2+, e.g. XOR of two
    past bits). For M3/XOR tasks this is the right quantitative distinction
    between transport and modification. It assumes fading memory and a fixed
    stationary driven system, so run it on a frozen champion under random drive.
 Q8 Yes: kubota0130/ipc is a compact Python implementation; worth fossilizing.
 Strength: MODERATE-STRONG as instrument.

### 3.4 Single nonlinear node with delayed feedback (Appeltant et al. 2011)
Source: Nat. Commun. 2:468, 2011, doi:10.1038/ncomms1476 ;
https://www.nature.com/articles/ncomms1476 . Photonic follow-up: Larger et al.,
"Photonic information processing beyond Turing", Opt. Express 20(3):3241 (2012).
 Q1 In the delay loop. One physical nonlinear node; "virtual nodes" are time
    slots along the delay line (time-multiplexing with an input mask).
 Q2 The delay loop recirculates the signal; node inertia couples adjacent
    virtual nodes; the loop fades (operated below oscillation threshold).
 Q3 Linear readout over virtual-node values sampled once per delay period.
 Q4 TIMING carries the "space": which virtual node = which phase in the loop.
 Q5 Designed architecture, trained readout.
 Q6 Performance vs delay length, node response time, feedback gain; memory
    capacity curve.
 Q7 This is the closest engineered precedent for "a network whose memory is
    a delay loop and whose state is indexed by time within the loop". Two
    differences: (i) Appeltant's memory is fading and relies on a trained
    readout of many virtual nodes; M2 is a 1-bit latch across a distracted gap
    read by an evolved program at one site. (ii) Appeltant's loop is one line;
    PTE's loops are graph cycles with jitter, loss and superposition. If M2 is a
    delay-line memory, Appeltant predicts performance should depend on loop
    period relative to gap and on per-hop node "inertia" (PTE's state decay
    option). Test: enable/disable site-state decay and sweep per-hop latency.
 Q8 Many open delay-RC simulators; not needed. Takeaway is the virtual-node
    idea: PTE analysis should index traffic by (edge, phase-in-loop), not by site.
 Strength: STRONG as architecture analogue for M2.

### 3.5 Morphological computation (Hauser et al. 2011)
Source: Biol. Cybern. 105:355-370, doi:10.1007/s00422-012-0471-0
 Q1 Physical body (mass-spring network) dynamics.
 Q2 Body's own damped dynamics (fading memory).
 Q3 Linear readout.
 Q4 Values + interaction (mechanical coupling).
 Q5 Body given; readout trained.
 Q6 Emulation of nonlinear filters with and without body.
 Q7 WEAK. Relevant only as a reminder that the "unintended" dynamics of the
    medium (here: PTE's queueing/latency/superposition) can do the work. No
    specific mechanism transfer.
 Q8 No.

---------------------------------------------------------------------------

## 4. Neural memory without (or with) persistent activity

### 4.1 Synaptic theory of working memory (Mongillo, Barak, Tsodyks 2008)
Source: Science 319:1543-1546, doi:10.1126/science.1150769
 Q1 Presynaptic residual calcium (short-term facilitation) in the synapses of
    the selective population.
 Q2 Slow facilitation decay (~1 s); refreshed by occasional population spikes
    (low-rate reactivation), so it is cheap.
 Q3 A nonspecific input "reads" the memory: the facilitated population
    responds first/most (reactivation).
 Q4 Values in a hidden variable, refreshed by bursts of activity.
 Q5 Model (designed), meant to explain biology.
 Q6 Suppress activity during delay; memory survives if the delay is shorter
    than facilitation decay; nonspecific readout signal reactivates.
 Q7 Structurally this is "hidden state + occasional regeneration by
    activity". PTE's version would be plastic routing weights holding the cue,
    refreshed by traffic. Ananke found weights contribute only slightly and
    register reset does nothing, so M2 is NOT this. The mapping is inverted:
    PTE's activity (traffic) is the carrier. But the MIXED case is plausible
    (Barbosa et al. 2020, below): traffic carries, weights bias. Test:
    freeze weights (disable plasticity) during the gap vs reset weights to
    pre-cue values; if reset hurts but freeze does not, weights store cue.
 Q8 Many reimplementations; no need.
 Strength: MODERATE (as a foil; clarifies what M2 is not).

### 4.2 "Activity-silent" working memory (Stokes 2015)
Source: Trends Cogn. Sci. 19(7):394-405, 2015, doi:10.1016/j.tics.2015.05.004
https://www.cell.com/fulltext/S1364-6613(15)00102-3
 Q1 Functional connectivity patterns (hidden states, e.g. STSP) rather than
    stationary delay activity.
 Q2 Hidden-state time constants; activity waxes and wanes with task relevance.
 Q3 The hidden state shapes the response to the next input (dynamic coding).
 Q4 Interaction: memory expressed as altered input-output mapping.
 Q5 Emergent in biology (as a claim).
 Q6 Decoding from impulse responses; cross-temporal decoding (codes change
    over time).
 Q7 The key idea for Ananke is DYNAMIC CODING: a representation whose code
    changes over the delay, so a decoder trained at one time fails at another.
    A fixed decoder (payload[0] sum) would miss such a code. Also the
    hidden-state-as-altered-transfer-function idea matches what "SETRULE as
    configuration" would look like if the rule DID carry cue: it would change
    the site's response to the readout-time input. The reported null (rule index
    carries no cue) says configuration only. Note: Stokes' "hidden state" is
    item-specific; an item-independent hidden state is what neuroscience calls
    task set / context, which is Ananke's "configuration".
 Strength: STRONG for vocabulary, MODERATE for mechanism.

### 4.3 Impulse perturbation "ping" (Wolff, Jochim, Akyurek, Stokes 2017)
Source: Nat. Neurosci. 20:864-871, doi:10.1038/nn.4546
PDF https://elkanakyurek.com/wp-content/uploads/Wolff_etal_2017_NatureNS.pdf
 Q1 Hidden state not visible in ongoing EEG.
 Q2 n/a (measurement paper).
 Q3 Item decodable from the evoked response to a task-irrelevant visual
    impulse during the delay.
 Q4 Interaction (state revealed via input-output response).
 Q5 Emergent (biology).
 Q6 THE INSTRUMENT: perturb with a cue-neutral input, decode cue from the
    response.
 Q7 Directly portable to PTE and the right tool for M3's SETRULE question and
    for the weights: inject a cue-neutral packet burst mid-gap at a probe site
    and decode cue from the network's response. If the rule/weight configuration
    is cue-independent, ping responses will not decode cue; if they do, there is
    hidden cue state that marginal MI on the rule index missed.
 Strength: STRONG as instrument.

### 4.4 TMS reactivation of latent memories (Rose et al. 2016)
Source: Science 354:1136-1139, doi:10.1126/science.aah7011
 Q6 Single-pulse TMS briefly reinstates decodability of an unattended item.
 Q7 Same instrument logic as 4.3; adds the idea that reactivation can be
    PRIORITY-dependent (only the item that may be needed). PTE analogue: ping
    during the gap vs ping after readout. WEAK beyond 4.3.

### 4.5 Masse, Yang, Song, Wang, Freedman 2019 (trained RNNs choose mechanisms)
Source: Nat. Neurosci. 22:1159-1167, doi:10.1038/s41593-019-0414-3 ;
PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC7321806/
 Q1 Trained RNNs with STSP synapses: memory in synaptic efficacies for pure
    maintenance, in persistent activity when manipulation is required.
 Q2 STSP time constants vs delay length.
 Q3 Trained output.
 Q4 Values in synapses vs activity.
 Q5 EMERGENT from optimization (the closest methodological match to PTE:
    the carrier is found, not specified).
 Q6 Silence activity during delay; shuffle synaptic states across trials;
    measure decodability in activity vs synapses; vary manipulation demand.
 Q7 Their headline predicts a PTE experiment: evolve on HOLD vs on a
    manipulate-then-hold variant (e.g. hold then XOR with a later cue). If PTE
    follows the RNN result, carrier choice should shift with task demand. The
    difference: in PTE the "synapse" (plastic routing weight) is weak and slow
    to matter; traffic is the default carrier even for pure maintenance, which is
    the opposite of Masse's pure-maintenance result. That inversion is itself
    worth stating as a finding (the cheapest carrier depends on the substrate's
    cost structure; in PTE, traffic is free and registers are overwritten by
    distractors). Their shuffle intervention (swap hidden state between trials
    with different cues) is stronger than reset and should be adopted.
 Q8 Their code is on GitHub (nmasse, "Short-term-plasticity-RNN") [unverified
    exact URL]; worth a look for the analysis pipeline, not the model.
 Strength: STRONG (methodologically the closest neuroscience analogue).

### 4.6 Interplay of persistent and silent states (Barbosa et al. 2020)
Source: Nat. Neurosci. 23:1016-1024, doi:10.1038/s41593-020-0644-4
https://www.nature.com/articles/s41593-020-0644-4
 Q7 Persistent activity carries the current item; activity-silent synaptic
    traces carry the PREVIOUS trial's item and bias behavior (serial bias).
    PTE analogue: do plastic weights carry cross-trial or cross-episode bias?
    Ananke's "weights contribute slightly" might be a serial-bias-like carrier
    of stale information. Test: condition performance on the previous episode's
    cue within a world. MODERATE.

### 4.7 Gamma and beta bursts (Lundqvist et al. 2016)
Source: Neuron 90:152-164, doi:10.1016/j.neuron.2016.02.028
 Q1 Brief, intermittent gamma bursts rather than sustained activity; memory
    between bursts plausibly in synaptic state.
 Q2 Burst-driven refresh.
 Q3 Bursts increase at readout.
 Q4 Timing (burst occurrence) + values.
 Q5 Emergent.
 Q6 Burst rate and timing analysis relative to encoding/readout.
 Q7 Suggests a PTE instrument: a PHASE-RESOLVED flush sweep (flush at each
    tick within the gap, one at a time). If M2 is bursty/intermittent, flush
    effectiveness will depend on phase; if continuous reverberation, it will not.
    MODERATE.

### 4.8 Memory without feedback (Goldman 2009) and memory traces (Ganguli et al. 2008)
Sources: Goldman, Neuron 61:621-634, 2009, doi:10.1016/j.neuron.2008.12.012 ;
Ganguli, Huh, Sompolinsky, PNAS 105:18970-18975, 2008, doi:10.1073/pnas.0804451105
 Q1 Goldman: activity passed along a chain of states (feedforward, or
    recurrent-but-non-normal networks); no attractor. Ganguli: the whole
    high-dimensional state trajectory, with non-normal dynamics giving the best
    memory (Fisher memory curve).
 Q2 Chain length (Goldman); non-normal transient amplification (Ganguli).
 Q3 Integration over the chain or a linear decoder over the full state.
 Q4 Values distributed across a sequence of states; effectively TIMING/phase.
 Q5 Theoretical.
 Q6 Fisher memory curve; decoding the input from the network state at lag k.
 Q7 These are the theory behind "memory as transport": a bit held by being
    passed along. On a ring, PTE traffic is literally a feedforward chain in time
    even though the graph is recurrent (Goldman's "recurrent networks that
    function in a feedforward manner"). Ganguli's result also explains why a
    single coordinate (payload[0] sum) can fail: in non-normal systems the
    signal is in a rotating subspace. Prediction: a decoder trained at tick t
    will not generalize to tick t+d (dynamic code) unless the chain is a loop
    with fixed period.
 Strength: STRONG (theory for M2's decoding failure and for transport-as-memory).

### 4.9 Kurtkaya et al. 2025: Dynamical phases of short-term memory in RNNs
Source: ICML 2025 (PMLR 267), arXiv:2502.17433 https://arxiv.org/abs/2502.17433
 Q1 Either slow-point manifolds producing sequences or limit cycles.
 Q7 Gives scaling laws for which mechanism learning selects as a function of
    delay length. PTE analogue: evolve under several gap lengths and check
    whether the carrier switches (e.g. single long flight for short gaps,
    recirculation for long gaps). The analogy (gradient learning vs GA) is
    MODERATE; the experimental design transfers.

### 4.10 State-dependent computation (Buonomano & Maass 2009)
Source: Nat. Rev. Neurosci. 10:113-125, doi:10.1038/nrn2558
 Q7 Supplies the clean split "active state" (ongoing activity) vs "hidden
    state" (e.g. STSP) that Ananke should adopt instead of memory/configuration.
    In PTE: active state = in-flight packets + registers; hidden state = rule
    index + routing weights (+ decay variables). VOCABULARY, STRONG.

---------------------------------------------------------------------------

## 5. Spike timing, polychronization, synfire chains

### 5.1 Polychronization (Izhikevich 2006)
Source: Neural Computation 18(2):245-282, doi:10.1162/089976606775093882 ;
MATLAB/C code in the paper and at https://www.izhikevich.org/publications/spnet.htm [unverified URL]
 Q1 Polychronous groups: time-locked but not synchronous firing patterns
    shaped by axonal conduction delays and STDP.
 Q2 STDP stabilizes groups; activation is transient.
 Q3 A group fires when inputs arrive with the right relative delays so they
    coincide at a target neuron.
 Q4 TIMING + topology (delays).
 Q5 Emergent (self-organized under STDP).
 Q6 Search for groups by stimulating anchor neurons with specific timings.
 Q7 M3's "must arrive exactly on the readout tick" resembles coincidence
    detection, but PTE's readout is a deadline (the readout samples an
    accumulator at one tick), not a coincidence among inputs carrying different
    timings. Polychrony is relevant only if cue identity is carried by relative
    arrival times. Test: decode cue from arrival-time vectors at the readout
    site. If not decodable, the analogy is WEAK. Also note that PTE's
    superposition (sum on arrival) makes coincidence functionally meaningful:
    packets landing on the same tick sum; that is a genuine structural parallel
    (coincidence = summation window).
 Q8 spnet.m is tiny and classic; worth fossilizing as a reference timing-code
    substrate.
 Strength: MODERATE (conditional).

### 5.2 Synfire chains (Diesmann, Gewaltig, Aertsen 1999)
Source: Nature 402:529-533, doi:10.1038/990101
 Q1 Pulse packets of synchronous spikes propagating through feedforward groups.
 Q2 An attractor in (spike count, temporal spread) space keeps packets sharp.
 Q3 Downstream coincidence.
 Q4 Timing + count.
 Q5 Model.
 Q6 State-space analysis of (a, sigma) per layer; show convergence or death.
 Q7 The (count, spread) attractor is a portable analysis for PTE packets: as a
    cue-carrying volley propagates, does its arrival-time spread shrink
    (self-sharpening) or grow with jitter? M3's 1-tick fragility says the
    evolved solution has no sharpening attractor. A GA selecting for jitter
    robustness might evolve one. MODERATE.

---------------------------------------------------------------------------

## 6. Asynchronous circuits

### 6.1 Micropipelines (Sutherland 1989)
Source: CACM 32(6):720-738, 1989, doi:10.1145/63526.63532 (Turing Award lecture)
 Q1 Data in pipeline registers; control state in request/acknowledge events.
 Q2 Handshakes hold data until consumed.
 Q3 Consumer reads on request event.
 Q4 Timing assumptions: "bundled data" assumes data arrives before its request
    (a timing constraint); fully delay-insensitive designs assume nothing about
    wire delays and pay for it (dual-rail, completion detection).
 Q5 Designed.
 Q6 Delay-insensitivity is established by showing correctness under arbitrary
    delays.
 Q7 M3's "+1 tick kills, -1 tick fine" is a one-sided timing constraint of
    exactly the bundled-data kind ("data must be there by the sample"). The
    asynchronous-design vocabulary gives Ananke a precise classification: the
    M3 champion is NOT delay-insensitive; it relies on a setup-time-like
    constraint. Asymmetric sensitivity (early OK, late fatal) is diagnostic of a
    sample-and-hold readout with an accumulator that persists after arrival.
    Test: evolve under async updates / larger jitter and see whether solutions
    become handshake-like (acknowledgement traffic) or simply die.
 Q8 No code; the design classification is the value.
 Strength: MODERATE-STRONG (for classifying M3).

---------------------------------------------------------------------------

## 7. Cellular automata: particles, domains, computational mechanics

### 7.1 Computational mechanics of CA (Hanson & Crutchfield 1992, 1997)
Sources: Hanson & Crutchfield, "The attractor-basin portrait of a cellular
automaton", J. Stat. Phys. 66:1415-1462 (1992); "Computational mechanics of
cellular automata: an example", Physica D 103:169-189 (1997),
PDF https://csc.ucdavis.edu/~cmg/papers/ECA54.pdf
 Q1 Regular domains (patterns recognizable by a finite automaton) and
    particles (defects between domains); information carried by particles.
 Q2 Particles are stable propagating defects under the CA rule.
 Q3 Particle collisions produce new particles or annihilation; outcomes compute.
 Q4 Topology/geometry of particle trajectories + interaction (collisions).
 Q5 Emergent (from the rule, not designed).
 Q6 Domain filter: remove domain-conforming cells, reveal particles; derive a
    particle "equation of motion".
 Q7 The domain-filter move is directly applicable: define PTE's "background"
    traffic (what flows regardless of cue) and filter it out; the residue is
    the cue carrier. In CA the carrier is a state of cells; in PTE the carrier
    is traffic, so the filter must be applied to channel occupancy, not only to
    site registers. Crutchfield's framework also treats the whole spacetime
    field, which cures temporal-window blindness by construction.
 Strength: STRONG (method).

### 7.2 GA-evolved particle computation (Das, Mitchell, Crutchfield 1994;
Hordijk, Crutchfield, Mitchell 1996/1998)
Sources: Das et al., PPSN III 1994; Hordijk et al., "Embedded-particle
computation in evolved cellular automata" (1996) https://pdxscholar.library.pdx.edu/compsci_fac/118/ ;
"Mechanisms of emergent computation in cellular automata" (PPSN V 1998)
https://melaniemitchell.me/PapersContent/mecca.pdf ; EvCA project
https://csc.ucdavis.edu/~evca/Papers/mecca.html
 Q1 Particles in evolved CA carry partial density information across the lattice.
 Q2 Particle stability.
 Q3 Collisions decide the final global state (density classification).
 Q4 Interaction + geometry.
 Q5 EMERGENT via a GA: the closest methodological precedent for PTE.
 Q6 Particle models (a catalog of particles, velocities, collision rules) that
    PREDICT the CA's task performance quantitatively.
 Q7 The validation standard PTE should adopt: a reduced "carrier model" of
    M2 (which packets, which edges, which re-emission rules) that predicts the
    champion's accuracy under new gap lengths / latency settings without running
    the full program. Agreement = mechanism understood; disagreement = something
    missed. Differences: CA particles are conserved or deterministic under
    collisions; PTE carriers suffer loss, duplication and noise and superpose.
 Q8 EvCA code historically distributed by Santa Fe / UC Davis; worth locating
    for fossilization [availability unverified]. Rule set phi_par (from the
    papers) can be re-implemented in a few lines.
 Strength: STRONG (method and precedent).

### 7.3 Local causal states, DisCo (Rupe & Crutchfield 2018; Rupe et al. 2019)
Sources: "Local causal states and discrete coherent structures", Chaos 28:075312
(2018), arXiv:1801.00515 ; "DisCo: physics-based unsupervised discovery of
coherent structures in spatiotemporal systems", arXiv:1909.11822
 Q1 Local causal state = equivalence class of past lightcones that predict the
    same distribution of future lightcones at a spacetime point.
 Q2 n/a (a representation).
 Q3 Coherent structures = localized deviations from the dominant causal-state
    symmetry.
 Q4 Agnostic (whatever predicts).
 Q5 Method.
 Q6 Reconstruct local causal states from spacetime data; map coherent structures.
 Q7 Applying lightcone causal-state reconstruction to PTE's (site x tick) field
    WITH channel occupancy included as extra field variables would give a
    substrate-agnostic answer to "where is the cue-predictive state". PTE's
    lightcones are graph-defined and latency-stretched, so the lightcone must be
    built from the latency graph, not the lattice.
 Q8 DisCo was built for HPC; lightcone reconstruction for 1D fields is
    re-implementable. Worth studying the lightcone construction.
 Strength: STRONG as instrument, heavy to implement.

### 7.4 CSSR and the epsilon-transducer
Sources: Shalizi & Klinkner, "Blind construction of optimal nonlinear recursive
predictors for discrete sequences", UAI 2004, arXiv:cs/0406011 ; code
https://bactra.org/CSSR/ (C++ on GitHub). Barnett & Crutchfield, "Computational
mechanics of input-output processes: structured transformations and the
epsilon-transducer", J. Stat. Phys. 161:404-451 (2015), arXiv:1412.2690
 Q1 Causal states: minimal sufficient statistics of the past for the future.
    Epsilon-transducer: the minimal state machine mapping an input process to an
    output process.
 Q7 PTE task episodes are input->output transductions (cue stream ->
    readout). The epsilon-transducer gives the MINIMAL memory any mechanism must
    carry (statistical complexity of the channel). Ananke can compare the
    champion's measured carrier capacity against that minimum to see whether it
    carries only the cue (efficient latch) or also carries distractor history
    (fading reservoir). CSSR can reconstruct causal states from a site's
    observable symbol stream; comparing reconstructed state count with and
    without channel variables quantifies how much predictive state lives
    off-site.
 Q8 CSSR: yes, small, worth fossilizing. Transducer inference code: see CMPy
    [availability unverified] or dit (https://github.com/dit/dit) for
    information measures.
 Strength: STRONG (formal definition of memory that is substrate-free).

### 7.5 Collision-based computing (Adamatzky 2002; Fredkin & Toffoli)
Source: Adamatzky (ed.), Collision-Based Computing, Springer 2002, ISBN
978-1-85233-540-3 ; includes Fredkin & Toffoli "Conservative logic" and
Margolus soft-sphere CA.
 Q1 Mobile localizations (balls, gliders, solitons).
 Q2 Conservation (billiard-ball) or rule stability.
 Q3 Collision outcome at a location.
 Q4 Interaction + trajectory timing: gates work only if signals arrive
    simultaneously at the collision site.
 Q5 Designed (mostly).
 Q6 Construct gates; verify truth tables.
 Q7 "Signals must meet at the right place at the right time" is precisely
    M3's arrival constraint, and PTE's superposition-on-arrival is a (linear)
    collision rule. Difference: billiard balls are conserved and reversible;
    PTE packets are lost, duplicated and noised, and sums are not reversible
    without side information. MODERATE.

---------------------------------------------------------------------------

## 8. Information dynamics (Lizier et al.)

### 8.1 Local transfer entropy as a spatiotemporal filter (Lizier et al. 2008)
Source: Phys. Rev. E 77:026110, doi:10.1103/PhysRevE.77.026110
 Result: local TE computed at every cell and time step highlights gliders and
 domain walls as the dominant transfer agents in CA: quantitative evidence that
 particles are information carriers.
 Q7 The PTE analogue computes local TE from (source site, channel) to
 (target site) at each tick, using the history of the target. In PTE, TE
 should be computed from the in-flight packet stream on each edge (the source
 variable is the channel, not the sending site), with the source lag set by the
 edge latency (see 8.5).

### 8.2 Local active information storage (Lizier, Prokopenko, Zomaya 2012)
Source: Information Sciences 208:39-54, doi:10.1016/j.ins.2012.04.016
 Result: local AIS a(i,n) = log p(x_{n+1} | x_n^(k)) / p(x_{n+1}); regular
 domains show positive storage; gliders show NEGATIVE local storage
 (misinformative: the cell's past predicts the wrong next value) while showing
 positive local transfer.
 Q7 This is the crispest existing operationalization of Ananke's distinction:
 at the site level, a transport event looks like negative AIS + positive TE;
 a stored bit looks like positive AIS. Computing local AIS on PTE sites'
 register histories during the gap should show near-zero AIS about the cue
 (consistent with the reset null), while AIS computed on an EDGE or LOOP
 variable (channel occupancy history) should be high. That is the quantitative
 version of the M2 finding. It also makes "memory" relative to the chosen
 variable, which is the point of section 10.

### 8.3 Information modification and particle collisions (Lizier et al. 2010)
Source: Chaos 20:037109, doi:10.1063/1.3486801
 Result: separable information s = AIS + sum of pairwise TEs; negative s marks
 modification events, which coincide with particle collisions.
 Q7 PTE superposition events at a receiver are candidate modification events.
 For M3 (MAJ), the readout-tick accumulation of several sensor packets IS the
 modification; separable information at the readout site at the readout tick
 should be negative. The temporal-window blindness lesson in one line: if the
 window excludes the readout tick, the modification event is excluded.

### 8.4 Storage from loop motifs (Lizier, Atay, Jost 2012)
Source: Phys. Rev. E 86:026110, doi:10.1103/PhysRevE.86.026110
 Result: in linear Gaussian network dynamics, a node's information storage is
 analytically dominated by directed feedback loops and feedforward loop motifs;
 clustering correlates with storage.
 Q7 This is the single most direct prior-art challenge to "M2 is transport
 not memory". Storage at a node is PRODUCED by transfer around loops. On a
 ring/torus PTE graph, loops are everywhere; the theory predicts storage
 capacity grows with (weighted) loop counts of short length relative to the
 gap. Test on PTE: compare M2 competence across graph types with matched degree
 but different short-cycle counts (ring vs random vs smallworld) and with
 routing weights restricted to break short cycles. Caveat: their analysis is
 linear Gaussian with node variables; PTE has latencies and channel state, so
 the prediction is qualitative.
 Strength: STRONG.

### 8.5 Measuring information-transfer delays (Wibral et al. 2013)
Source: PLoS ONE 8(2):e55809, doi:10.1371/journal.pone.0055809
 Result: TE with a scanned source-target delay u is maximal at the true
 interaction delay (self-prediction optimality); detects multiple delays and
 feedback loops.
 Q7 PTE latency is base + per-hop + jitter. Scanning u recovers the EFFECTIVE
 carrier delay and, for recirculation, peaks at multiples of the loop period.
 This is a non-interventional complement to the gap-vs-latency test.
 Strength: STRONG as instrument.

### 8.6 LAIS in neural data (Wibral, Lizier, Voegler, Priesemann, Galuske 2014)
Source: Front. Neuroinform. 8:1, doi:10.3389/fninf.2014.00001
 Q7 Practical guidance on embedding choice (history length k, delay tau) and
 on measuring storage "as seen by other nodes". Relevant to choose k for PTE
 register/traffic histories. Supporting.

### 8.7 Critique: transfer entropy is not information flow (James, Barnett, Crutchfield 2016)
Source: Phys. Rev. Lett. 116:238701, doi:10.1103/PhysRevLett.116.238701 ;
arXiv:1512.06479
 Result: TE can both overestimate flow and underestimate influence; it
 conflates unique and synergistic contributions (e.g. XOR-like dependencies).
 Q7 PTE's summation of packets plus XOR/MAJ tasks makes synergy central. Pairwise
 TE will misattribute. Use multivariate TE (IDTxl) and partial information
 decomposition (dit) and treat TE as a screening statistic, never as the
 mechanism claim. Interventions (flush, reset, clamp, swap) remain the
 authority; information measures locate candidates.
 Strength: STRONG (a guardrail).

---------------------------------------------------------------------------

## 9. Evolved systems and unintended carriers

### 9.1 Thompson's evolved FPGA (1996/1997) and Bird & Layzell's evolved radio (2002)
Sources: Thompson, "An evolved circuit, intrinsic in silicon, entwined with
physics", ICES 1996 / LNCS 1259 (1997), doi:10.1007/3-540-63173-9_61 ;
Bird & Layzell, "The evolved radio and its implications for modelling the
evolution of novel sensors", CEC 2002, https://ieeexplore.ieee.org/document/1004522/ ;
PDF https://people.duke.edu/~ng46/topics/evolved-radio.pdf
 Q1 Unmodeled physical couplings (analog timing, capacitive coupling, a
    circuit-board trace acting as an antenna).
 Q2 Whatever the physics provides.
 Q3 Fitness output.
 Q4 Timing and interaction via unintended channels.
 Q5 EMERGENT under unconstrained evolution.
 Q6 Clamp or remove "disconnected" cells and observe failure; move to another
    chip; change temperature.
 Q7 The lesson for PTE: an evolved program will use every state-bearing
    feature of the simulator, including ones the designer did not think of as
    carriers: queue ordering, receiver-cap drop order, collision tie-breaks,
    duplication, RNG streams keyed by site, decay rounding. M2's "in-flight"
    carrier is the intended-by-accident case. Ananke should enumerate every
    state variable in the PTE step function (including simulator plumbing) and
    run a reset/flush/shuffle ablation for each. Thompson's "portability" test
    (move to a different chip) maps to: run the frozen champion under a
    different RNG family / latency seed / graph instance.
 Q8 No code; the audit discipline is the value.
 Strength: STRONG (methodological warning).

### 9.2 Evolved minimally cognitive agents analyzed with information + dynamics
(Beer & Williams 2015)
Source: Cognitive Science 39(1):1-38, doi:10.1111/cogs.12142
 Q1 Evolved CTRNN agent's neural state and agent-environment coupling.
 Q5 Emergent (evolution).
 Q6 Information flow analysis (including partial information decomposition,
    Williams & Beer) run side by side with dynamical-systems analysis of the
    same evolved agent.
 Q7 The best existing template for what Ananke is doing: take an evolved
    system, measure information flow over time, and reconcile it with a
    dynamical/mechanistic account. Their analysis is time-resolved through the
    whole trial, which avoids window blindness. MODERATE-STRONG (method).

---------------------------------------------------------------------------

## 10. Environment-mediated state (stigmergy) and superposition codes

### 10.1 Stigmergy (Theraulaz & Bonabeau 1999)
Source: Artificial Life 5(2):97-116, doi:10.1162/106454699568700
 Q1 State in the environment (pheromone, built structure) modified by agents.
 Q2 Environment persistence (evaporation sets decay).
 Q3 Agents respond to local environmental state.
 Q4 Values (quantitative stigmergy) or configuration (qualitative).
 Q5 Emergent.
 Q6 Manipulate the environment (remove trail) and observe behavior.
 Q7 PTE's plastic routing weights modified by traffic are stigmergic state.
    The weak contribution Ananke found is consistent with a weak stigmergic
    trace. The more interesting mapping: PTE channels are shared environment,
    and in-flight traffic is a very short-lived "pheromone". WEAK-MODERATE.

### 10.2 Hyperdimensional computing / superposition (Kanerva 2009)
Source: Cognitive Computation 1(2):139-159, doi:10.1007/s12559-009-9009-8
 Q1 High-dimensional vectors; bundling = superposition (sum) of vectors.
 Q2 n/a.
 Q3 Similarity against a codebook (not a single coordinate).
 Q4 Values in distributed codes.
 Q5 Designed.
 Q7 PTE packets with payload[P] that SUM on arrival are small-P bundling.
    HDC predicts that a sum of codewords is decodable by projection onto the
    right codeword, not by a fixed coordinate (payload[0]). Actionable: learn
    the cue codebook from cue-conditioned mean in-flight payload vectors and
    decode by nearest-codeword/projection. With small P and integer arithmetic,
    capacity is tiny, so this is a decoding hint, not a mechanism claim.
    MODERATE.

---------------------------------------------------------------------------

## 11. Emergence measures (only as relevant)

### 11.1 Rosas et al. 2020, Reconciling emergences
Source: PLoS Comput. Biol. 16(12):e1008289, doi:10.1371/journal.pcbi.1008289
 Q7 Provides a practical criterion (via integrated information decomposition)
 for when a macro variable predicts the future better than its parts. Only
 relevant if Ananke wants to claim that an aggregate (e.g. total in-flight
 signed payload on a loop, or parity of packet count) is the carrier while no
 individual packet is. That claim would be exactly "the cue is carried by the
 traffic pattern, not by any packet". WEAK-MODERATE; keep in reserve.
 Integrated information / causal emergence beyond this are not directly
 relevant to Ananke's questions and are omitted deliberately.

---------------------------------------------------------------------------

## 12. CHALLENGES TO ANANKE'S VOCABULARY

C1. "Memory vs transport" is a scale- and variable-set-dependent distinction,
    already formalized. Lizier's framework defines storage (AIS) and transfer
    (TE) RELATIVE to a chosen set of variables and history embedding. Lizier,
    Atay & Jost (2012) show node-level storage arises from loop transfer. So M2
    is simultaneously: transfer (at the edge level, each packet moves the bit
    one hop), storage (at the loop or system level, the bit persists), and in
    Chandy-Lamport terms, channel state. Ananke should never write "M2 is
    transport, not memory". Write instead: "the cue-bearing state during the
    gap is channel state (in-flight packets), not site state; whether it is a
    single flight or a recirculating loop is [established/open]."

C2. "Configuration" has a precise neighbor term: task set / context (hidden
    state that is item-independent) vs item memory (item-dependent hidden
    state), in the Stokes / Buonomano-Maass / Masse vocabulary. Their
    active-state / hidden-state split is also cleaner than memory/config:
      active state  = registers + in-flight packets
      hidden state  = rule index + routing weights (+ decay variables)
      item-bearing  = whichever of these carries mutual information with the cue
    "SETRULE is configuration" then means "SETRULE's hidden state is necessary
    and item-independent". That claim requires (i) MI(rule state; cue) ~ 0 at
    ALL sites and ALL ticks, not only at the readout site; (ii) no synergy:
    I(rule, registers; cue) - I(registers; cue) ~ 0 (PID or conditional MI);
    (iii) a ping test (Wolff 2017) that fails to elicit cue-dependent responses;
    and (iv) a swap test that exchanges the rule state between trials of
    different cues with no effect. Until then: "necessary; no marginal cue
    information at readout".

C3. "Memory" needs a substrate-free definition. Computational mechanics
    supplies it: the causal state (minimal sufficient statistic of the past for
    the future). The epsilon-transducer gives the minimal memory any mechanism
    solving the task must carry. Ananke's claims about where memory is should be
    phrased as "which physical variables realize the cue-relevant partition of
    causal states". This also resolves the decoding failure: the causal-state
    partition need not be linearly readable from any one variable.

C4. "Transport arrives on the readout tick" is a deadline / setup-time
    constraint (asynchronous-circuit vocabulary: bundled-data timing assumption),
    not by default a "timing code". Reserve "timing code" (Izhikevich,
    Cabuk et al.) for cases where cue identity is decodable from arrival times.

C5. "Delay-line memory" is claimed only after the regeneration test. Without
    re-emission, a single long-latency packet is a delay, and a delay is not a
    memory in the delay-line sense (EDSAC, fiber loops, pingfs all require
    regeneration). Gap > max single-trip latency is the discriminator.

C6. Temporal-window blindness is a known failure of window-averaged measures;
    the prior-art cure is LOCAL (pointwise) measures at every (site, tick)
    (Lizier) and full-trial time-resolved decoding / cross-temporal
    generalization (King & Dehaene 2014; Stokes dynamic coding). Any ablation
    reported should give the window as [t_start, t_end] with the readout tick
    stated, and a sweep over both ends.

C7. "Emergent delay line / reverberating traffic" sounds like an echo state /
    reservoir. It is not, unless it has fading memory of the input stream.
    A HOLD latch across distractors is closer to a regenerated (non-fading)
    store. Run a memory-capacity / IPC measurement under random drive to
    decide which it is.

---------------------------------------------------------------------------

## 13. WHAT PTE MAY EXPOSE THAT STANDARD FRAMEWORKS ASSUME AWAY

Stated conservatively; each item notes how much support there is.

E1. Channel state as a first-class carrier in information dynamics.
    SUPPORTED. Lizier-style analyses of CA and networks define variables at
    nodes; in CA the "particle" is literally cell state, so there is no
    separate channel. In PTE the carrier is in the channels, invisible to any
    node-variable time series during the gap. Applying node-level AIS/TE to PTE
    as-is will mislabel M2. Distributed-systems theory (Chandy-Lamport) has
    channel state, but no information-dynamics measures. PTE is a concrete case
    requiring the union: node + edge variables in the information-dynamics
    decomposition. This is a methodological contribution, not new physics.

E2. Superposition of messages with evolved (not designed) coding.
    PARTLY SUPPORTED. Superposition itself is well studied (network coding,
    HDC, wireless physical-layer network coding). What is less studied is an
    evolved code under forced summation with noise, loss and duplication,
    where the code the GA finds is not known in advance and is not the
    designer's linear code. The payload[0]-sum decoding failure is a first
    hint that the evolved code is not the obvious one. Not yet a finding.

E3. Non-conserved carriers.
    SUPPORTED as a contrast. CA particles and billiard balls are conserved or
    deterministic under collision; the particle-model methodology (Hordijk et
    al.) relies on that. PTE carriers are lost, duplicated and noised per hop.
    If M2 persists despite loss, something regenerates it; the particle-model
    approach must be extended with birth/death rates. Genuinely different
    regime; worth a short note once the regeneration test is done.

E4. Asynchrony and the meaning of "state at time t".
    SUPPORTED but known. Info-dynamics estimators assume a common time index.
    In async PTE runs, consistent cuts (Chandy-Lamport) are needed to define
    state; local TE/AIS require an event-based or continuous-time formulation
    (Spinney, Prokopenko, Lizier 2017, "Transfer entropy in continuous time,
    with applications to jump and neural spiking processes", Phys. Rev. E
    95:032319 [unverified detail]; see also arXiv:1804.03269 "Characterising
    information-theoretic storage and transfer in continuous time processes").

E5. Carriers found by evolution in a medium with cost asymmetries.
    SUGGESTIVE. Masse et al. (2019) found trained RNNs use synaptic (silent)
    storage for pure maintenance. PTE's evolved programs use traffic (active)
    storage for pure maintenance. If this holds across seeds and graph types,
    it supports the general claim that carrier choice follows the substrate's
    cost/vulnerability structure (distractors overwrite registers, traffic is
    free), not a universal preference. That is a comparative claim worth
    testing directly by making registers distractor-proof or traffic costly.

Not claimed: that PTE exhibits anything outside known computational classes,
or anything "beyond" reservoir computing, delay-line memory, or particle
computation. The novelty, if any, is the combination (evolved carrier, forced
superposition, lossy channels, channel-state storage) and the instrument
lessons.

---------------------------------------------------------------------------

## 14. CONCRETE INSTRUMENTS TO ADOPT

Ordered by (decision value) / (cost).

I1. Gap-vs-max-latency regeneration test.  [cheap, decisive]
    Measure: M2 accuracy as gap G sweeps past L_max = base + hops_max*per_hop +
    jitter_max for the champion's graph. Survival beyond L_max = re-emission
    (delay-line memory). Add: packet genealogy logging (which packet was emitted
    in response to which received packet) to see the loop directly.
    Prior art: delay lines, fiber loops, pingfs (sec. 1).

I2. Partial / targeted flush and phase-resolved flush.  [cheap]
    Measure: flush one edge, one channel id, one payload component, or only
    packets of a given age; and flush at each single tick in the gap. Locates
    the loop and tests continuous vs bursty carriage. Prior art: Lundqvist 2016,
    Hanson-Crutchfield domain filter logic.

I3. Noise/loss recirculation ceiling.  [cheap]
    Measure: max holdable gap vs per-hop noise and loss. Loop hypothesis
    predicts a ceiling falling with noise, and holding-time quantized to loop
    period. Prior art: fiber-loop buffers (sec. 1.2).

I4. Time-resolved multivariate decoding + cross-temporal generalization.  [cheap]
    Features per tick: full in-flight inventory (count per edge, channel id,
    all payload components, age), register vectors, rule indices, weights.
    Train at tick t, test at t' (King & Dehaene 2014,
    https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(14)00019-9).
    Stable diagonal+off-diagonal = static code (loop with fixed code);
    diagonal-only = dynamic code (chain/rotating subspace, Goldman/Ganguli).
    Also decode from arrival-time vectors (timing-code test, sec. 5, 2.4).

I5. Swap / shuffle interventions (instead of reset only).  [cheap]
    Swap the in-flight inventory, registers, rule indices or weights between
    two trials with DIFFERENT cues at tick t. Effect on output = that variable
    carries cue; no effect = it carries none (configuration). Reset only shows
    necessity of non-zero content, not cue content. Prior art: Masse et al.
    2019 shuffle; interchange-intervention logic.

I6. Ping (impulse-response) probe.  [cheap]
    Inject a cue-neutral packet burst mid-gap; decode cue from the network's
    response over the next few ticks. Detects hidden cue content in rules or
    weights. Prior art: Wolff et al. 2017; Rose et al. 2016.

I7. Local information dynamics with edge variables.  [medium]
    Compute local AIS at sites and at edges/loops; local TE from edge-channel
    streams into sites with lag scanned over latencies (TE_SPO, Wibral 2013);
    separable information at the readout tick for M3 (Lizier 2010). Use
    discrete estimators (states are integers; plug-in with bias correction and
    surrogate testing).
    Tools:
     - JIDT (Java, usable from Python via JPype): https://github.com/jlizier/jidt ;
       paper doi:10.3389/frobt.2014.00011 ; docs https://jlizier.github.io/jidt/
       Has discrete and continuous estimators for AIS, TE, conditional TE,
       local (pointwise) values, and a CA demo that reproduces the glider/domain
       filters: this is the fastest way to validate our pipeline on a known case
       before applying it to PTE (known-answer test).
     - IDTxl (Python): https://github.com/pwollstadt/IDTxl ; JOSS
       doi:10.21105/joss.01081. Multivariate TE network inference with
       statistical testing, AIS, PID. Use for "which edges carry cue
       information conditioned on all others" (handles redundancy/synergy
       better than pairwise TE; see James et al. 2016 critique).
     - dit (Python, discrete information theory incl. PID):
       https://github.com/dit/dit
    Recommendation: fossilize JIDT and IDTxl (pinned commits) and run JIDT's
    CA example as a known-answer test.

I8. Memory capacity and information processing capacity under random drive.  [medium]
    Drive a frozen champion with an i.i.d. input stream; fit linear readouts of
    past inputs (MC, Jaeger) and of orthogonal polynomial functions of past
    inputs (IPC, Dambre 2012; code https://github.com/kubota0130/ipc).
    Distinguishes fading reservoir (graded MC) from latch (task-specific,
    non-fading) and linear transport from nonlinear modification.

I9. Causal-state reconstruction.  [medium-heavy]
    CSSR (https://bactra.org/CSSR/) on each site's observable symbol stream
    with and without channel-occupancy symbols; compare number of causal states
    and statistical complexity. Optional: lightcone local causal states (Rupe &
    Crutchfield 2018) on the site x tick field using the latency graph.
    Measures how much predictive state is off-site, substrate-free.

I10. Reduced carrier model with performance prediction.  [heavy, high value]
    Following Hordijk-Crutchfield-Mitchell: write a small model (which sites
    re-emit what, on which edges, with which delays) and predict the
    champion's accuracy under unseen gap lengths, latencies, and noise.
    Agreement is the strongest evidence of mechanism understanding.

I11. Simulator-state audit (Thompson lesson).  [cheap, do first]
    Enumerate every state-bearing variable in the PTE step: registers, rule
    index, routing weights, decay state, in-flight queues, queue order,
    receiver-cap drop order, collision tie-break, duplication state, RNG
    streams. Run reset and swap on each. Anything with an effect is a carrier
    candidate; anything not ablatable is an uncontrolled carrier.

I12. Window hygiene.  [cheap]
    Every ablation reports [t_start, t_end] and the readout tick; default to a
    2D sweep over window start and end, with a mandatory arm that includes the
    readout tick (the C1b lesson). Local measures at each (site, tick) as a
    complement.

---------------------------------------------------------------------------

## 15. Fossilization candidates (code worth pinning)

 - JIDT: https://github.com/jlizier/jidt  (known-answer CA demos)
 - IDTxl: https://github.com/pwollstadt/IDTxl
 - dit: https://github.com/dit/dit
 - CSSR: https://bactra.org/CSSR/ (C++ source linked from there)
 - IPC: https://github.com/kubota0130/ipc
 - Izhikevich spnet (polychronization reference) [URL unverified; code is
   printed in the 2006 paper appendix]
 - pingfs: https://github.com/yarrick/pingfs (tiny; demo only)
 - EvCA particle CA rules: re-implement from Hordijk et al. / Mitchell papers;
   original code availability unverified.

---------------------------------------------------------------------------

## 16. Source list (verified 2026-09-27 unless marked)

 1. Eckert et al. 1949, Mercury delay line memory, Proc. IRE 37(8):855-861.
    CHM EDSAC page: https://www.computerhistory.org/storageengine/edsac-computer-employs-delay-line-storage/
 2. Fiber-loop buffers: Opt. Express 16(12):8451 (2008); 17(8):6629 (2009).
 3. pingfs: https://github.com/yarrick/pingfs
 4. Dijkstra 1974, CACM 17(11):643-644.
 5. Chandy & Lamport 1985, ACM TOCS 3(1):63-75, doi:10.1145/214451.214456
 6. Barabasi et al. 2001, Nature 412:894-897, doi:10.1038/35091039
 7. Ahlswede et al. 2000, IEEE TIT 46(4):1204-1216, doi:10.1109/18.850663
 8. Cabuk, Brodley, Shields 2004, ACM CCS, doi:10.1145/1030083.1030108
 9. Boahen 2000, IEEE TCAS-II 47(5):416-434
10. Jaeger 2001/2002, GMD Report 152
11. Maass, Natschlager, Markram 2002, Neural Comput. 14(11):2531-2560, doi:10.1162/089976602760407955
12. Dambre et al. 2012, Sci. Rep. 2:514, doi:10.1038/srep00514
13. Appeltant et al. 2011, Nat. Commun. 2:468, doi:10.1038/ncomms1476
14. Larger et al. 2012, Opt. Express 20(3):3241-3249
15. Hauser et al. 2011, Biol. Cybern. 105:355-370, doi:10.1007/s00422-012-0471-0
16. Mongillo, Barak, Tsodyks 2008, Science 319:1543-1546, doi:10.1126/science.1150769
17. Stokes 2015, Trends Cogn. Sci. 19(7):394-405, doi:10.1016/j.tics.2015.05.004
18. Wolff et al. 2017, Nat. Neurosci. 20:864-871, doi:10.1038/nn.4546
19. Rose et al. 2016, Science 354:1136-1139, doi:10.1126/science.aah7011
20. Masse et al. 2019, Nat. Neurosci. 22:1159-1167, doi:10.1038/s41593-019-0414-3
21. Barbosa et al. 2020, Nat. Neurosci. 23:1016-1024, doi:10.1038/s41593-020-0644-4
22. Lundqvist et al. 2016, Neuron 90:152-164, doi:10.1016/j.neuron.2016.02.028
23. Goldman 2009, Neuron 61:621-634, doi:10.1016/j.neuron.2008.12.012
24. Ganguli, Huh, Sompolinsky 2008, PNAS 105:18970-18975, doi:10.1073/pnas.0804451105
25. Kurtkaya et al. 2025, ICML, arXiv:2502.17433
26. Buonomano & Maass 2009, Nat. Rev. Neurosci. 10:113-125, doi:10.1038/nrn2558
27. Izhikevich 2006, Neural Comput. 18(2):245-282, doi:10.1162/089976606775093882
28. Diesmann, Gewaltig, Aertsen 1999, Nature 402:529-533, doi:10.1038/990101
29. Sutherland 1989, CACM 32(6):720-738, doi:10.1145/63526.63532
30. Hanson & Crutchfield 1992, J. Stat. Phys. 66:1415-1462; 1997, Physica D 103:169-189
31. Das, Mitchell, Crutchfield 1994, PPSN III; Hordijk, Crutchfield, Mitchell 1996/1998
32. Rupe & Crutchfield 2018, Chaos 28:075312, arXiv:1801.00515; Rupe et al. 2019, arXiv:1909.11822
33. Shalizi & Klinkner 2004, UAI, arXiv:cs/0406011
34. Barnett & Crutchfield 2015, J. Stat. Phys. 161:404-451, arXiv:1412.2690
35. Adamatzky (ed.) 2002, Collision-Based Computing, Springer
36. Lizier, Prokopenko, Zomaya 2008, PRE 77:026110, doi:10.1103/PhysRevE.77.026110
37. Lizier, Prokopenko, Zomaya 2012, Inf. Sci. 208:39-54, doi:10.1016/j.ins.2012.04.016
38. Lizier, Prokopenko, Zomaya 2010, Chaos 20:037109, doi:10.1063/1.3486801
39. Lizier, Atay, Jost 2012, PRE 86:026110, doi:10.1103/PhysRevE.86.026110
40. Wibral et al. 2013, PLoS ONE 8(2):e55809, doi:10.1371/journal.pone.0055809
41. Wibral et al. 2014, Front. Neuroinform. 8:1, doi:10.3389/fninf.2014.00001
42. James, Barnett, Crutchfield 2016, PRL 116:238701, doi:10.1103/PhysRevLett.116.238701
43. Thompson 1997, LNCS 1259, doi:10.1007/3-540-63173-9_61; Bird & Layzell 2002, IEEE CEC
44. Beer & Williams 2015, Cogn. Sci. 39(1):1-38, doi:10.1111/cogs.12142
45. Theraulaz & Bonabeau 1999, Artif. Life 5(2):97-116, doi:10.1162/106454699568700
46. Kanerva 2009, Cogn. Comput. 1(2):139-159, doi:10.1007/s12559-009-9009-8
47. Rosas et al. 2020, PLoS Comput. Biol. 16(12):e1008289, doi:10.1371/journal.pcbi.1008289
48. King & Dehaene 2014, Trends Cogn. Sci. 18:203-210
49. Lizier 2014, JIDT, Front. Robot. AI 1:11, doi:10.3389/frobt.2014.00011
50. Wollstadt et al. 2019, IDTxl, JOSS 4(34):1081, doi:10.21105/joss.01081

Unverified details (flagged inline): ReservoirPy URL, Masse code URL,
Izhikevich spnet URL, EvCA code availability, CMPy availability, the exact
Spinney et al. 2017 citation, DOIs for items 17/23/37 were taken from
publisher pages seen in search results but not opened individually.
