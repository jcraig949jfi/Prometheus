"""Cut: verilog-uart2bus (ancestry-aware, Stage A DEEP-by-size: the RTL is 483 lines in five files; SOURCE_READ on M3; tenth of the
2026-09-17 NOT_CUT order). Read in full: rtl/uart_rx.v (116), rtl/uart_tx.v (94), rtl/baud_gen.v (56), rtl/uart_parser.v (667,
comments stripped), rtl/uart2bus_top.v (83). Not read: rtl/uart_top.v (66, wiring), the bench/ testbenches and tasks (RUNNABLE_EMULATED
per the record: iverilog is the world). Nothing ran.
"""
from nyx.atlas.author import Cut

B = "vault:verilog-uart2bus/upstream/tree/verilog/rtl/"
c = Cut("verilog-uart2bus", mode="ANCESTRY_AWARE", inspected=["rtl/uart_rx.v, uart_tx.v, baud_gen.v, uart_parser.v, uart2bus_top.v (all)"],
        evidence=[("SOURCE_READ", B + "uart_rx.v"), ("SOURCE_READ", B + "uart_tx.v"), ("SOURCE_READ", B + "baud_gen.v"), ("SOURCE_READ", B + "uart_parser.v"), ("SOURCE_READ", B + "uart2bus_top.v")],
        note="a serial-line-to-register-bus bridge: five small synchronous mechanisms (a fractional rate generator, an oversampling receiver, a shift-register transmitter, a text/binary command parser, a request/grant bus handshake) with no processor")

baud = c.organ("fractional_rate_generator_by_add_subtract_accumulator", human_name="baud_gen.v", status="ACCEPTED",
    mechanism="a 16-bit accumulator adds baud_freq each clock; when it reaches baud_limit it subtracts baud_limit and emits one ce_16 pulse; with baud_freq = 16*baud/gcd and baud_limit = clock/gcd - baud_freq the pulse rate is exactly 16*baud on average with bounded jitter (one clock); no division, no multiplier",
    input="clock; two registers", output="ce_16 (a clock-enable at 16x the bit rate)", state="counter (16 bits)", update="per clock",
    assumptions=["the ratio clock/(16*baud) is rational with a small gcd-reduced form; jitter of one clock per pulse is tolerable because the receiver oversamples 16x"],
    fitness_value_in_ancestor="any baud rate from any clock with two registers; the classical Bresenham / DDS rate-division trick", failure_landscape="UNKNOWN by run; by reading: when 16*baud does not divide the clock the pulses are unevenly spaced",
    human_prior="the header's gcd formula is the human's prior on how to fill the registers; the hardware does not know it", evidence_ref=B + "baud_gen.v", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="module baud_gen",
    coverage={"input_topology": "SCALAR", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "SINGLE_STEP", "temporal_horizon": "STEP"})

rx = c.organ("oversampling_receiver_with_two_flop_synchroniser_start_detection_and_mid_bit_sampling", human_name="uart_rx.v", status="ACCEPTED",
    mechanism="the asynchronous serial input is sampled through two flops (in_sync); a 4-bit counter runs on ce_16 whenever the receiver is busy or the line is low; it is held at zero while idle and high, so the count starts at the falling edge of a start bit; ce_1_mid (count 7) is the middle of each bit and samples the line into a shift register; the first mid-bit sample (of the start bit) sets busy; after 8 data bits the byte is presented with a one-clock new_rx_data pulse at the end of bit 8 (count 15); no stop-bit check, no parity, no framing error",
    input="ser_in, ce_16", output="rx_data, new_rx_data", state="in_sync[2], count16, bit_count, data_buf, rx_busy", update="per ce_16",
    assumptions=["the sender's rate is within the tolerance that 16x sampling and mid-bit alignment allow (a few percent)", "a glitch on the line while idle starts a reception (the start bit is not re-verified at its middle)"],
    fitness_value_in_ancestor="rate recovery from the data itself: the counter phase-locks to each start bit", failure_landscape="by reading: no stop-bit verification means a framing error is silently accepted; the byte after a noise glitch is garbage",
    human_prior="16x oversampling with mid-bit sampling: the 8250-era convention", evidence_ref=B + "uart_rx.v", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="module uart_rx",
    coverage={"input_topology": "STREAM", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "stochasticity": "ENVIRONMENT_RANDOM", "update_topology": "SINGLE_STEP", "failure_mode": "CORRUPTS", "recovery": "SELF_RESETS", "hidden_state": "ESTIMATES"})

tx = c.organ("shift_register_transmitter_with_framing_bits_loaded_while_idle", human_name="uart_tx.v", status="ACCEPTED",
    mechanism="while idle the 9-bit buffer is continuously loaded with {tx_data, 0} (data plus start bit) and the line is held high; new_tx_data sets busy; every 16 ce_16 the buffer shifts right with a 1 shifted in (the stop bit and idle level come for free); after 10 bit times busy clears; tx_busy is the only flow control",
    input="tx_data, new_tx_data, ce_16", output="ser_out, tx_busy", state="data_buf[9], count16, bit_count, tx_busy", update="per ce_16",
    assumptions=["the caller waits for tx_busy to fall before presenting the next byte (the parser's tx_end_p edge detector does exactly that)"], fitness_value_in_ancestor="the stop bit and idle state are the same value shifted in; nine flops and a counter",
    failure_landscape="UNKNOWN by run", evidence_ref=B + "uart_tx.v", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="module uart_tx",
    coverage={"input_topology": "EVENT", "output_topology": "STREAM", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "stochasticity": "DETERMINISTIC", "update_topology": "SINGLE_STEP"})

parse = c.organ("dual_protocol_command_parser_selected_by_the_first_byte_with_a_text_line_state_machine_and_a_binary_length_prefixed_form", human_name="uart_parser.v main_sm (MAIN_* states), data/addr nibble accumulation, bin_* flags", status="ACCEPTED",
    mechanism="a byte of 0x00 in IDLE enters the binary protocol (command byte with read/write/nop bits, auto-increment and status-reply flags, 16-bit address, length, then data bytes counted down to bin_last_byte); an 'r'/'R' or 'w'/'W' enters the text protocol (whitespace, hex data, whitespace, hex address, end of line), where hex characters are accumulated a nibble at a time into data_param/addr_param and any unexpected character parks the machine in EOL until a line end; the request fires on the first non-hex character after the address",
    input="rx_data + new_rx_data", output="read_op/write_op or bin_read_op/bin_write_op with address, data, count", state="main_sm (4 bits), the parameter registers, the flags", update="per received byte",
    assumptions=["0x00 never starts a text command; hex characters and whitespace are the only text tokens; a malformed line is discarded, not reported"], fitness_value_in_ancestor="a human at a terminal and a program with a binary stream share one port; no firmware",
    failure_landscape="by reading: a binary command with length 0 would count down from 0 through 255 (bin_last_byte tests for 1); a text line with more than 2 data or 4 address hex digits keeps only the last ones (shift-in)", human_prior="the text grammar 'w DD AAAA' / 'r AAAA' is a designer's convention",
    evidence_ref=B + "uart_parser.v (main_sm case statement; data_param/addr_param/bin_byte_count blocks)", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the main state machine and the parameter registers",
    coverage={"input_topology": "STREAM", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN", "failure_mode": "STALLS", "recovery": "SELF_RESETS", "representation_sensitivity": "SENSITIVE"})

bus = c.organ("request_grant_bus_handshake_with_one_cycle_strobes_and_a_pipelined_read_return", human_name="write_req/read_req -> int_req; int_gnt -> int_write/int_read; read_done/read_done_s/read_data_s", status="ACCEPTED",
    mechanism="a parsed command raises a request flag (int_req = write_req | read_req); when the bus owner grants (int_gnt) the strobe int_write or int_read is asserted for exactly one clock and the request cleared; a read's data is captured one clock after the strobe (read_done) and the transmit machine is kicked one clock later (read_done_s) so the register file has a cycle to answer; the address auto-increments after each binary transfer when the flag is set",
    input="parsed commands, int_gnt, int_rd_data", output="int_address, int_wr_data, int_write, int_read, int_req", state="the request flags and the two-stage read pipeline", update="per clock",
    assumptions=["the register file answers a read in one clock after int_read; a grant may be delayed indefinitely (the request holds)"], fitness_value_in_ancestor="the bridge can share the bus with other masters; timing of the register file is decoupled by one stage",
    failure_landscape="UNKNOWN by run; by reading: a second command arriving before the grant overwrites the parameters (no queue)", evidence_ref=B + "uart_parser.v (write_req/read_req blocks, int_address block, read_done block)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the bus-side always blocks",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN", "cooperation": "COORDINATES", "competition": "ARBITRATES"})

txsm = c.organ("reply_formatter_sequenced_by_the_falling_edge_of_transmitter_busy", human_name="tx_sm (TX_* states), tx_end_p = ~tx_busy & s_tx_busy, nibble-to-ASCII tables, the 0x5A status byte", status="ACCEPTED",
    mechanism="a text read replies with two hex characters then CR LF, each byte handed to the transmitter when the previous one's busy falls (tx_end_p, a one-clock edge pulse from a sampled tx_busy); a binary read sends raw bytes and re-requests the next address on each tx_end_p until the count is done; a status byte 0x5A is sent after binary commands when the flag asks, and always for NOP",
    input="read_data_s, the op flags, tx_busy", output="tx_data, new_tx_data", state="tx_sm (3 bits), s_tx_busy", update="per clock",
    assumptions=["the transmitter's busy signal is the only pacing; no FIFO"], fitness_value_in_ancestor="multi-byte replies with one byte of buffering", failure_landscape="UNKNOWN by run",
    evidence_ref=B + "uart_parser.v (tx_sm case statement; tx_end_p; tx_char table)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the transmit-side always blocks",
    coverage={"input_topology": "EVENT", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN"})

c.reject("uart_top.v and uart2bus_top.v wiring, the D_BAUD_FREQ/D_BAUD_LIMIT constants, the CHAR_* defines", reason="GENERIC_LANGUAGE_MECHANICS", evidence=B + "uart2bus_top.v; the parser's define block", note="instantiation and constants")
c.reject("the testbenches and uart_tasks.v", reason="OTHER", evidence="not read; they are the world (iverilog) for a Stage C run, per the record's RUNNABLE_EMULATED", note="an instrument, not a mechanism")
c.reject("'UART' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the rate generator, receiver and transmitter share only ce_16; each is a separate module with its own state")

c.edge(baud, rx, "feeds"); c.edge(baud, tx, "feeds"); c.edge(rx, parse, "feeds"); c.edge(parse, bus, "triggers"); c.edge(bus, txsm, "feeds", note="read_done_s + read_data_s"); c.edge(txsm, tx, "feeds"); c.edge(tx, txsm, "gates", note="tx_end_p"); c.edge(txsm, bus, "triggers", note="binary read re-request per byte")

c.pressure("a_bit_stream_with_no_clock_must_be_recovered_by_a_receiver_whose_own_clock_differs_by_a_few_percent",
    condition="symbols arrive at a nominal rate with no separate clock; the receiver has a local clock at an unrelated frequency; each symbol has a start marker; the receiver must sample near the middle of every bit for the length of a frame",
    resource_or_constraint="a local oversampling factor (cost in clock rate); frame length over which drift accumulates", failure_condition="a sampled bit lands on a transition (corruption) after drift accumulates, or a noise glitch is taken for a start",
    world_punishes="both", world_rewards="phase alignment at each start marker and a sampling point that tolerates the maximum drift over the frame", observable_consequence="byte error rate vs rate mismatch percentage and vs glitch rate",
    vacuity_condition="a shared clock line", trivial_shortcuts="a world that transmits the clock; frames of one bit", cheat_control="a receiver given the sender's clock must show zero errors at any mismatch; the ancestor must fail at a mismatch near 100/(16*10) percent per frame: the world must show the cliff or it is not exerting the drift pressure",
    cost_class="CPU-scale", source_evidence="uart_rx.v (count16 held at 0 while idle and high; ce_1_mid at 7); baud_gen.v", purpose="PURPOSE: asynchronous serial reception")

c.pressure("one_channel_must_serve_a_human_typed_grammar_and_a_machine_binary_grammar_without_ambiguity",
    condition="the same byte stream may carry either protocol; the organism must decide from the first byte and parse both; malformed input must not wedge the parser", resource_or_constraint="state bits; no buffering beyond one byte",
    failure_condition="a byte value legal in both grammars, or a malformed line that leaves the parser stuck", world_punishes="misparsed commands; a parser that never returns to idle", world_rewards="a disambiguating first symbol and an error state that resynchronises on a delimiter",
    observable_consequence="commands recovered per malformed line injected; wedges per 10^4 random bytes", vacuity_condition="one grammar", trivial_shortcuts="two channels",
    cheat_control="a parser fed only well-formed input of one grammar must recover 100%; the ancestor fed a binary write whose data contains 'w' bytes must still parse it as binary (length-prefixed): if the world cannot pose that case it is not testing the ambiguity",
    cost_class="CPU-scale", source_evidence="uart_parser.v main_sm (0x00 vs r/w in IDLE; MAIN_EOL)", purpose="PURPOSE: a dual text/binary UART-to-bus bridge")

c.ancestry("algorithm_from", "the 16x-oversampling UART convention (8250-class devices); the 'uart2bus' OpenCores project (record lineage not re-read)", note="from the module headers")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["uart_top.v not read (wiring only, by its size and role)", "nothing ran; the bench/ directory holds a ready iverilog world (tb_txt / tb_bin) for a SCOUT or Stage C run", "the two reading-level defects (length-0 binary count wrap; no stop-bit check) are unmeasured"],
          note="every always block in the five RTL files is accounted for")
c.save(state="DEEP")
