# The module contract

What a seat declares to run a GPU workload, and what the platform
promises in return. The authority is `prometheus_gpu/spec.py`; this
document explains it. Where they disagree, the code is right and this
file is a bug.

A module declares WHAT it is and WHAT it needs. It declares nothing
about RunPod, and it never sees the provider API.

## The two mandatory fields

```json
{"name": "my-module", "entrypoint": "run.py"}
```

Everything else has a defensible default. The default GPU is an A40, the
default runtime bound is 1800 s, the default disk is 20 GB.

## Field reference

| field | type | default | notes |
|:--|:--|:--|:--|
| `name` | string | *required* | `^[a-z0-9][a-z0-9_-]{0,62}$`. It becomes a pod name and an artifact path, which is why it is restricted. |
| `entrypoint` | string | *required* | Relative POSIX path inside the module directory. Run as `python3 <entrypoint> <args...>`. |
| `version` | string | `"1"` | Yours to manage. Appears in `identity` as `name@version` and in the receipt. |
| `args` | list of string | `[]` | Passed verbatim. Every element must ALREADY be a string: the platform will not stringify a number for you, because that hides typos. |
| `dependencies.pip` | list of string | `[]` | Every requirement must be pinned (`==`), a VCS/URL spec (`@`), or a flag (`-`). |
| `gpu.class` | string | `"NVIDIA A40"` | Provider SKU string. |
| `gpu.count` | int | `1` | Must be >= 1. |
| `gpu.cloud` | string | `"SECURE"` | `SECURE` or `COMMUNITY`. |
| `gpu.min_memory_mib` | int | unset | Advisory; recorded in the plan so a reader can check the SKU actually satisfies it. |
| `disk_gb` | int | `20` | At least 5. Container disk on the pod. |
| `max_runtime_s` | int | `1800` | Positive, at most 24 h. A hard bound, not a hint. |
| `artifacts` | list of string | `[]` | Relative POSIX paths under `$PROMETHEUS_ARTIFACT_DIR`, retrieved after the run. |
| `canary` | string or null | `null` | A shell command that must succeed before the workload starts. |
| `env_allowlist` | list of string | `[]` | Host environment variable names the module may inherit. |
| `env` | object | `{}` | Literal non-secret values to set. |
| `telemetry.interval_s` | number | `15` | Advisory heartbeat cadence. |
| `work_units.name` | string | unset | Your denominator: `site-ticks`, `candidates`, `evaluations`. |
| `work_units.estimate` | number | unset | Must be positive when present. Used for cost-per-unit. |
| `description` | string | `""` | Free text, carried into the receipt. |

## What validation refuses, and why

Validation is strict about what costs money or loses data, and lenient
about everything else. Each refusal below exists because of a specific
way a run can go wrong:

**No runtime bound, or over 24 h.** An unbounded run is an unbounded
bill. The bound is not advice; it is how a hung workload stops costing
money.

**An unpinned pip requirement.** If the resolved versions were free to
drift, the bytes that ran cannot be reconstructed from the receipt, and a
result cannot be re-derived. Pin, or accept that the run is not
reproducible.

**An absolute or `..` path in `entrypoint` or `artifacts`.** These escape
the module workdir on the pod. Validated with `posixpath`, never the
host's rules: the controller may be Windows while the pod is always
Linux, and on Windows under Python 3.13 `os.path.isabs("/etc/passwd")`
is *False*, because a rooted path with no drive is not absolute to
`ntpath`. It is absolutely absolute on the pod. That exact bug was in
this validator and a test found it.

**A backslash in any path.** A legal filename character on Linux, so a
Windows-style path does not fail; it silently becomes one very strange
file instead of a directory.

**A forbidden name in `env_allowlist` or `env`.** The list is in
`spec.FORBIDDEN_ENV` and includes `RUNPOD_API_KEY`, `RUNPOD_API_TOKEN`,
`RUNPOD_TOKEN`, cloud keys, model-provider keys, `GITHUB_TOKEN`, and the
repo's own secrets. Provider credentials belong to the controller. A
module that wants one is asking for the wrong thing.

**`work_units.estimate` of zero or negative.** It is a denominator.

**A name outside the character class.** It becomes a pod name and a path
component.

## What the platform promises the module

At entry, in the module's working directory:

| guarantee | detail |
|:--|:--|
| the module's own files | unpacked from a bundle whose sha256 was verified before unpacking |
| `dependencies.pip` installed | `pip install --no-cache-dir`, before the workload, after the checksum |
| `PROMETHEUS_ARTIFACT_DIR` | exists and is writable |
| `PROMETHEUS_TELEMETRY_PATH` | a JSON-lines file to append to |
| `PROMETHEUS_RUN_ID` | the run identity, safe to embed in your own output |
| `PROMETHEUS_MODULE` | `name@version` |
| the allowlisted variables | those of `env_allowlist` that exist on the host, plus all of `env` |
| **no provider credential** | see below |

And nothing else from the controller's environment. The module's
environment is CONSTRUCTED from the allowlist, not the controller's
environment minus a blocklist. A new secret appearing on the controller
tomorrow is therefore invisible by default rather than by having been
remembered.

## The secrets boundary

Enforced in three places, because one is a promise and three is a
property:

1. **Spec validation** refuses a forbidden name in the allowlist, so a
   module cannot even ask.
2. **`secrets.build_module_env`** builds the environment from the
   allowlist and then asserts no forbidden name is present in the
   result.
3. **The pod-side prelude** runs `unset RUNPOD_API_KEY RUNPOD_API_TOKEN
   RUNPOD_TOKEN ...` immediately before invoking the entrypoint, and
   `secrets.verification_snippet()` emits a check that ABORTS the run if
   any forbidden name is still readable.

`test_prometheus_gpu.py::test_a_module_cannot_read_provider_credentials`
injects fake credentials deliberately and proves module code cannot read
them. The fakes are synthetic strings; no real credential appears in any
test, log, manifest, argv or receipt.

## Telemetry and artifacts

Append JSON lines to `$PROMETHEUS_TELEMETRY_PATH`; see
`TELEMETRY_SCHEMA.md`. Write declared artifacts under
`$PROMETHEUS_ARTIFACT_DIR`; see the size limit in
`PROMETHEUS_GPU_RUNPOD_GUIDE.md` s10.

## Bundle identity

`bundle.build()` is deterministic: fixed member mtimes, uid/gid 0, empty
owner names, sorted members, gzip mtime 0. The same content produces the
same sha256 on any machine at any time, so the receipt's bundle hash is a
usable identity rather than a nonce.

Text files are hashed over LF-normalised bytes. This is not cosmetic:
an AETH-02 launch failed because the controller's checkout had CRLF line
endings and the pod computed a different hash for identical content.
Directories under the platform carry `.gitattributes` with `eol=lf`.

## Executable checks

Every claim above is tested:

```bash
python -m pytest Aether/test/test_prometheus_gpu.py -q
python -m prometheus_gpu.cli dry-run Aether/runpod/examples/hello_gpu/module_spec.json
```
