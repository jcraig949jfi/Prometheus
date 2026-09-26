# Failure playbook

Every entry below is a failure that actually happened on this account,
not a hypothetical. Each says what it looked like, what caused it, what
to do now, and what now prevents it. Where a test or command covers it,
that is named — a playbook entry with no executable counterpart is a
note-to-self, and a note-to-self is not there after a context reset.

---

## 0. The rule that matters most

> **A failed create does not tell you whether a pod exists.**
> Never retry a create blindly. Read the inventory first, adopt what is
> there, and if the inventory read *also* fails, stop rather than guess.

A create can succeed server-side while the client is told it failed —
timeout, dropped connection, proxy error. The pod exists and is billing;
you just do not have its id. A blind retry then creates a *second* pod
and bills twice, and the first one is invisible to you, so nothing will
ever clean it up.

Covered by `provider.create_with_reconcile` and by
`test_a_lost_response_is_adopted_not_duplicated`, which uses
`Fault.lost_response()` to make the create succeed while the client sees
a failure, and asserts that the controller adopts the phantom pod and
issues no second create.

The harder case — create ambiguous **and** the reconciling LIST also
fails — must refuse to retry, and a receipt for it records
`creation_outcome: "unknown"`, which blocks any clean claim.

---

## 1. Cloudflare 1010 on every API call

**Looked like:** every RunPod API request rejected with a Cloudflare
1010 block page, not a JSON error. Nothing wrong with the credential.

**Cause:** the default Python HTTP client's `User-Agent` is on a
blocklist.

**Now:** send an explicit `User-Agent`. Any ordinary string works.

**Prevention:** the qualified client in `pod_service.py` does this.
Do not write a new HTTP client for RunPod; use the qualified one.

---

## 2. The module could not see its own environment variables

**Looked like:** the pod ran with defaults. The run finished, produced
plausible output, and was wrong — the worst failure mode, because it
does not announce itself.

**Cause:** the orchestrator computed a cadence configuration and never
forwarded it into the pod's environment.

**Now:** if a run's parameters are not visible in its telemetry, do not
trust the run.

**Prevention:** every forwarded variable is logged at launch, and the
module spec's `env`/`env_allowlist` is the single declared channel.
Emit your effective configuration in the `start` telemetry record so the
receipt can prove what actually ran.

---

## 3. Hash mismatch on a file that was byte-identical

**Looked like:** the pod downloaded the module, computed a sha256, and
refused it. Reading both files showed identical content.

**Cause:** the controller's checkout had CRLF line endings; the pod saw
LF. Same content, different bytes, different hash.

**Now:** hash text over LF-normalised bytes.

**Prevention:** `bundle.py` normalises line endings before hashing;
`.gitattributes` with `eol=lf` covers `Aether/observatory/` and the
orchestrator directories; `test_text_hashes_are_lf_normalised`
holds the line. This is a Windows-controller-to-Linux-pod trap and it
will recur in any new directory that is not covered.

---

## 4. `cmd` too large

**Looked like:** the create request was rejected for size. The launch
script had grown to 51,251 bytes because the science was embedded as a
heredoc inside the pod command.

**Cause:** embedding code in the request instead of shipping it.

**Now:** ship a bundle. Fetch it by URL, verify its checksum, unpack it.
The command dropped to 4,307 bytes.

**Prevention:** `bundle.build()` plus `dryrun.build_bootstrap()` do this
by construction. The dry run prints the exact `cmd`, so its size is
visible before launch rather than in a rejection.

---

## 5. The artifact server started after the science

**Looked like:** nothing, until it would have mattered. The pod computed
for hours and only then opened the channel that serves results.

**Cause:** the obvious ordering — do the work, then serve the output.

**Why it is wrong:** if the workload crashes, the pod has no way to hand
back the partial results or the telemetry that would explain the crash.
The failure case is exactly the case where you need the data most.

**Now:** start the artifact server **first** and `wait` on it last.

**Prevention:** the orchestrators do this. Write telemetry
incrementally and flush, so a dead pod still leaves a readable trail.

---

## 6. A green summary line over a red suite

**Looked like:** two pushes with the terminology audit failing. The
console said the gate passed.

**Cause:** `pytest ... | tail` inside an `&&` chain. The exit status of a
pipeline is the exit status of its **last** command, so the status came
from `tail`, which always succeeds.

**Now:** run gates as their own command and read the result before
acting on it. Do not pipe a gate into a pager or a filter.

**Prevention:** practice change, recorded in the calibration ledger.
There is no tooling fix for this; the shell is behaving correctly.

---

## 7. Evidence files silently not committed

**Looked like:** a receipt referenced log files that were not in the
repository.

**Cause:** a broad `*.log` entry in `.gitignore`.

**Now:** a narrow negation for the specific evidence path —
`!Aether/AETH-01/evidence/**/*.log`.

**Do not** reach for `git add -f` as the normal solution. It works once
and hides the problem from the next person. Detect ignored evidence
files *before* declaring a run complete: `git check-ignore -v <paths>`.

---

## 8. A local package shadowed the standard library

**Looked like:** nothing yet — caught during review.

**Cause:** the platform package was originally named `platform`, which
is a stdlib module. On `sys.path` it would shadow the real one for
anything importing it, numpy internals included, with failures appearing
far from the cause.

**Now:** `prometheus_gpu`.

**Prevention:** check a new package name against the stdlib before
choosing it.

---

## 9. Host path rules deciding what is legal on the pod

**Looked like:** nothing yet — caught by a test.

**Cause:** the spec validator used `os.path.isabs` to reject absolute
paths. On Windows under Python 3.13, `os.path.isabs("/etc/passwd")` is
`False`, because a rooted path with no drive letter is not absolute to
`ntpath`. That path is absolutely absolute on the Linux pod. The
validator would have passed review on a laptop and let an artifact path
escape the workdir in the cloud.

**Now:** validate pod-side paths with `posixpath`, deliberately, and
refuse backslashes outright — they are a legal filename character on
Linux, so a Windows-style path silently becomes one very strange file
rather than failing.

**Prevention:** `spec._is_contained`, and
`test_windows_host_cannot_bless_an_absolute_pod_path`.

---

## 10. A syntax error in a generated launch script

**Looked like:** the launch aborted before creating a pod. No money
spent.

**Cause:** a literal newline inside a patch string.

**Why it went well:** it failed closed. The pod is created *after* the
script is assembled, so a malformed script costs nothing.

**Prevention:** `py_compile` plus a dry run are part of the pre-launch
sequence. Keep the expensive step last, always.

---

## 11. A possibly-billing pod recorded as a non-event

**Looked like:** nothing yet -- caught by a launch test.

**Cause:** the controller's teardown `finally` forced
`result = "NOT_RUN"` whenever it held no pod id. An *unresolved* create
also holds no pod id -- that is the whole problem with it -- so the one
case where a pod may exist that we cannot name would have been written
into the receipt as a clean non-event.

**Now:** only a create the provider *confirmed* created nothing may be
downgraded to `NOT_RUN`. An unresolved create emits a pod record with the
id `UNRESOLVED`, `creation_outcome: "unknown"`, and a receipt that refuses
to claim cleanup.

**Prevention:** `test_an_unresolvable_create_is_not_a_clean_non_event`.

**Generalisation worth keeping:** "no id" and "nothing exists" are
different facts. Any code that treats a missing identifier as an absence
is asserting something it cannot know.

---

## 12. The canonical example violated the schema the platform enforces

**Looked like:** nothing, because nobody had run it.
`examples/hello_gpu/run.py` emitted `utc` and `monotonic_s`;
`TELEMETRY_SCHEMA.md` requires `t_utc` and `t_elapsed_s`, and
`validate-telemetry` rejects a record missing either. The one file a seat
is told to copy would have produced telemetry the platform refuses.

**Cause:** the example was written before the schema and never re-checked
against it. Documentation and code were verified; the example was assumed.

**Now:** both examples conform, and both emit the reserved `units`
counter the cost model divides by.

**Prevention:** `test_prometheus_gpu_examples.py` EXECUTES each example
the way a pod would and validates what it produced, including that every
declared artifact was actually written. An example that does not satisfy
the contract is worse than no example, because a seat copies it and
inherits the defect.

---

## 13. A placeholder overwrote the thing it was standing in for

**Looked like:** `rehearse` reported `TIMEOUT` on a module that was fine.

**Cause:** the rehearsal serves synthetic telemetry, then fills each
declared artifact with placeholder bytes. A module may legitimately
declare its telemetry file as an artifact -- both examples do -- so the
placeholder assignment clobbered the synthetic telemetry, and the
controller polled until the runtime cap without ever seeing an `end`.

**Now:** `setdefault`, not assignment.

**Prevention:** `test_rehearse_does_not_overwrite_a_declared_telemetry_artifact`.

---

## 14. A stripped environment that broke the interpreter, not the code

**Looked like:** every example failed under test with
`ModuleNotFoundError: No module named 'numpy'`.

**Cause:** the conformance test built the subprocess environment from
scratch, to mimic a pod. numpy lives in a user site-packages directory
that needs `APPDATA`, so the test was failing for a reason that had
nothing to do with what it was testing.

**Now:** start from the real environment with the forbidden names
*removed*, which is also what the pod-side prelude actually leaves behind.

**Generalisation:** a test that isolates more than the thing under test
stops reporting on that thing. "Pod-like" was the wrong target; "what the
prelude leaves" was the real one.

---

## 15. A valid request the provider cannot fill

**Looked like:** HTTP 400 on create, three times, no pod.

**Cause:** not a malformed request. The body read:
*"There are no longer any instances available with the requested
specifications."* There was no RTX A4000 capacity in SECURE cloud.

**Now:** declare `gpu.alternatives` in the order you would rather have
them. The controller walks the list, reconciling inventory between
attempts so a failed create is confirmed to have created nothing before
the next id is tried. An *unresolved* outcome stops the walk: trying
another GPU there could put a second pod beside one that cannot be named.

**Note:** a 400 creates nothing, so reading the response body is free and
is usually the fastest way to the cause. The qualified client hides it;
a one-off direct probe does not.

**Prevention:** `test_capacity_refusal_walks_the_declared_alternatives`,
`test_no_capacity_anywhere_is_a_named_clean_non_event`,
`test_an_unresolved_create_stops_the_walk`.

---

## 16. A pod that is fine, and a controller that calls it dead

**Looked like:** `pod never reported ready within 300 s`. The pod was
healthy.

**Cause:** the bootstrap was installing `cupy-cuda12x` and its `nvidia-*`
dependencies — about a gigabyte of wheels. It took 6 seconds on one flight
and over 305 on the next, same image, same GPU class. A fixed deadline
cannot tell a slow dependency install from a dead pod, so it calls both
dead and discards the one that was about to work.

**Now:** the controller waits on PROGRESS. Stage markers are read each
poll, and it gives up only when nothing has advanced for
`stall_timeout_s`, or at a hard ceiling. The failure names the stage:
*"furthest bootstrap stage reached was unpacked"*.

**Generalisation:** a timeout on total elapsed time is a guess about the
slowest acceptable case. A timeout on lack of progress is a statement
about liveness, and it is almost always the one you wanted.

**Prevention:** `test_a_slow_dependency_install_is_not_mistaken_for_a_dead_pod`,
`test_a_pod_that_stops_advancing_is_given_up_on`.

---

## 17. The path was right in the document and wrong in the code

**Looked like:** ten minutes of `404` from the pod proxy. The artifact
server was up the whole time.

**Cause:** `MODULE_CONTRACT.md` says artifact paths are relative to
`$PROMETHEUS_ARTIFACT_DIR`. The server's document root IS that directory,
so `/app/out/result.json` is served at `/result.json` — and the
controller, plus both example specs, asked for `/out/result.json`. Nothing
tested the agreement between the contract and the implementation, and the
conformance test actually STRIPPED a leading `out/`, hiding the mismatch
it should have caught.

**Now:** paths are artifact-dir relative everywhere, and the conformance
test refuses any artifact path containing a slash.

**Generalisation:** a test that normalises away a discrepancy is worse
than no test, because it converts a visible defect into a passing suite.

**Prevention:** `test_the_example_writes_every_artifact_it_declares`.

---

## 18. Silence is the most expensive failure mode

**Looked like:** a 600-second flight that reported one uninformative word.

**Cause:** `fetch` returned `None` for every failure — unreachable,
401, 404, timeout, DNS — so the controller could not say which.

**Now:** a failed fetch records url, status and error; the controller
reports each distinct reason once; and a missing artifact makes it fetch
the server's document index, so the pod says which files exist while it is
still alive.

**Cost of not having this:** two flights and $0.088. The first attempt
with diagnostics identified the cause in its first second.

---

## 19. A scout that was not smaller than its campaign

**Looked like:** nothing. `cli scout` printed a spec with
`work_units.estimate` reduced by 50x, a scout ceiling of a few cents, and
`representative: True`. Found in Iteration 2's dry run, before any spend.

**Cause:** the reduced estimate lived only in the spec. The module never
received it, and representativeness requires the module's own `env` to be
IDENTICAL to the campaign's, so no module-side knob could differ either.
Flown, the "scout" would have run the full campaign under a scout's
runtime bound, and been killed or billed as the campaign.

**Now:** the platform sets `PROMETHEUS_WORK_UNITS` from
`work_units.estimate`. A module reads its count from there; the rest of
its environment stays identical, so the calibration still carries over.

**Generalisation:** a planning number that never reaches the thing it
plans is a label. Check the value arrives where the work is done.

**Prevention:** `test_a_scout_is_smaller_than_its_campaign_and_otherwise_identical`.

---

## 20. A runtime bound spent on installing wheels

**Looked like:** nothing yet; found reading the controller before
Iteration 2 flew. `max_runtime_s` was measured from the CREATE, while the
cost model prices it as module compute, with overhead added separately.

**Cause:** the same dependency install has measured 6 s and 305 s. At
305 s, a module with `max_runtime_s: 120` -- a scout's bound, derived from
its campaign's -- would have been stopped as `TIMEOUT` before running.

**Now:** the runtime bound starts at first telemetry, when the module is
demonstrably running. Money is still bounded from the create, by the
budget ceiling, which is the guard that actually matters for a bill.

**Prevention:** `test_a_slow_bootstrap_does_not_eat_the_modules_runtime`,
confirmed to FAIL against the old origin before the fix was restored.

---

## 21. "Provisioning" that was the proxy

**Looked like:** Iteration 1 bounded provisioning at <= 24 s and could
not isolate it. The interval from create-accepted to first telemetry was
31 s, of which 7 s was on the pod's clock.

**Cause:** two different instants had been treated as one. With the pod's
clock MEASURED (the `/_clock` endpoint, min-RTT offset, +/- 0.2 s), the
pod's shell was running **2.1 s** after the create was accepted. The
provider's proxy then answered **404 for about 25 s more** before routing
to the pod at all. Most of the "provisioning" time was reachability.

**Now:** the receipt reports `synchronised.provision_s` (pod running) and
`controller_clock.accepted_to_first_contact_s` (pod reachable) separately.

**Generalisation:** a subtraction across two clocks is not a measurement,
and a single interval that spans two mechanisms cannot be attributed to
either. Measure the offset, then split the interval at the first instant
each side can observe.

**Prevention:** `test_the_controller_measures_the_pod_clock_and_corrects_provisioning`,
`test_first_contact_through_the_proxy_is_its_own_interval`.

---

## 22. The calibrated card had no capacity

**Looked like:** two `NOT_RUN` campaign flights in a row, 12 minutes after
a scout had flown on an RTX A4000: *"no capacity for any declared GPU (NVIDIA
RTX A4000)"*. $0.00; the provider confirmed nothing was created each time.

**Cause:** calibration fidelity and availability pull against each other.
A calibration is only valid on the card it was measured on, so the campaign
is pinned to that card and drops its alternatives -- and a pinned campaign
has exactly one card to be refused on.

**Now:** the fallback is the whole path, not a looser pin: fly a fresh
unpinned scout (it walks `gpu.alternatives` and takes what is available),
then plan and fly the campaign pinned to the card the scout got,
immediately. Iteration 2 did exactly that on an L4: scout, plan and
campaign inside seven minutes, for $0.051.

**Generalisation:** a pin is a bet that capacity will still be there. Keep
the scout-to-campaign interval short, and treat a scout as cheap enough to
repeat rather than as an asset to protect.

**Now automated (Iteration 3):** `flight.py --go --auto` chains dry-run ->
scout -> calibrated plan -> pinned campaign and re-scouts unpinned once on a
confirmed capacity refusal (`prometheus_gpu/campaign.py`). It never re-flies
a campaign that ran or whose create was ambiguous.

---

## 23. "No capacity" that nobody read

**Looked like:** flight F2b, five declared SECURE cards, five `400`s, a
`NOT_RUN` receipt saying *"no capacity for any declared GPU"*. $0.00.

**Cause:** nothing had read the reason. The qualified client discards 400
bodies, so "every card refused cleanly" is also exactly what a malformed
request looks like -- and F2b followed a change to the bootstrap.

**Found by:** a one-off direct POST of the identical body, which read the
provider's own words: *"There are no longer any instances available with
the requested specifications."* Then a read-only GraphQL stock query, which
showed one SECURE card in stock that the spec did not declare (RTX 4000 Ada).

**Now:** a `NO_CAPACITY` receipt says the capacity is INFERRED. Before
changing a request after an all-cards refusal, probe the same body once and
read what comes back. `RunPodProvider.stock_status` reads advertised SECURE
stock and the controller tries in-stock cards first -- it reorders, never
drops, because advertised stock is advice. F2c and F3 each landed on the
first card tried this way.

---

## 24. A fault injector that killed the wrong process

**Looked like:** flight F2 ran to its $0.05 ceiling (1,074 s) on a 300 s
module. The controller saw an ordinary, progressing run the whole time.

**Cause:** the soak module's `killserver` fault matched `_serve.py`
anywhere in a process command line. The pod's bootstrap runs as
`bash -c <script>`, and the script text mentions the server, so the
injector killed the container's MAIN process. RunPod restarted the
container, the bootstrap re-ran from the top on the same disk, and the
module started again, appending a second run to the same telemetry. In a
loop: the stage file showed 80 lines, ten boots.

**Now:** the injector matches argv (an interpreter whose argument IS the
server script); a test asserts the bootstrap shell is not matched.

---

## 25. A restarted container re-runs the module

**Looked like:** entry 24's loop. Any death of the container's main
process -- an OOM of the shell, an injector, a provider-side restart --
gets the same treatment.

**Cause:** the provider restarts a container whose main process exits, and
nothing in the bootstrap knew it had already run.

**Now:** the bootstrap's first act (before `stage boot`) is a RESTART GUARD:
if the stage file already holds a `boot`, it records `stage restart`,
brings the artifact server back so what the first run wrote can still be
retrieved, and exits without touching the module. The controller reads
`restart` from the stage file and stops with `CONTAINER_RESTARTED`
(`UNKNOWN`), in the ready wait and in the watch.

**Not covered:** a restart that also loses the disk. Then the guard sees no
stage file, the module runs again from scratch, and only the telemetry
sequence resetting would show it.

---

## 26. Evidence that lived only on the pod

**Looked like:** flight F2c, server killed mid-run: telemetry up to the
fault was in the receipt, platform samples were ZERO.

**Cause:** telemetry was polled during the watch, but `platform.jsonl` and
the stage file were fetched only at retrieval, and by then the server was
gone.

**Now:** both are snapshotted every 6 watch polls, and a snapshot is only
replaced by a longer one, so a truncated read never shrinks what is held.

---

## 27. The pod clock was asked once

**Looked like:** flight F2: *"pod clock unavailable; provisioning stays
cross-clock"* for the whole run.

**Cause:** the stage file answered through the proxy a few seconds before
`/_clock` did, the controller measured the clock at first contact, got
nothing, and never asked again.

**Now:** the clock is re-measured (bounded: 6 attempts) until it answers,
including during the watch.

---

## 28. Acknowledged, and still there

**Qualified on the fake, not seen on hardware:** a terminate that is
acknowledged (`ACK_204`) while the pod keeps running, combined with a LIST
that omits it. Iteration 2's teardown reported this clean -- acknowledged
and absent from the listing.

**Now:** absence needs LIST to omit the pod AND GET to return nothing; a
disagreement is re-read up to four times and, if it persists, recorded as
`UNCERTAIN` in `disposition.pod_state`, never resolved by preference. The
receipt validator refuses `observed_absent` when its evidence contradicts
it.

---

## Diagnostics

```bash
python -m prometheus_gpu.cli inventory                      # what is running
python -m prometheus_gpu.cli cleanup --all                  # stop it
python -m prometheus_gpu.cli dry-run spec.json              # what would happen
python -m prometheus_gpu.cli validate-telemetry tel.jsonl   # what it reported
python -m prometheus_gpu.cli validate-receipt receipt.json  # what it may claim
```

Emergency: `unset RUNPOD_API_KEY RUNPOD_API_TOKEN RUNPOD_TOKEN` before
invoking `pod_service.py` — the guard in that module refuses to run with
a RunPod-injected key present.

## When a run ends badly

1. **Inventory first.** Before anything else, find out what is running.
2. **Terminate, then confirm absence.** Two separate facts; record both.
3. **Do not claim clean** unless both hold and the inventory read
   succeeded. See `RUN_RECEIPT_SCHEMA.md`.
4. **Do not claim reconciliation** without provider billing data. Ever.
5. **Write the receipt anyway.** A `FAILED` or `UNKNOWN` receipt with
   honest cleanup fields is worth more than no receipt, and `UNKNOWN` is
   not a synonym for `FAILED`.
6. **Add the entry here**, with its test.
