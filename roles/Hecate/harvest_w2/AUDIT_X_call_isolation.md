# AUDIT X - are Hecate's "isolated" model calls isolated?

Auditor: sub-agent for Hecate, 2026-10-01T01:23Z (clock). Worktree hecate-base-role.
No git writes. No credentials read. Diagnostic calls: 4, written to the scratchpad
only (scratchpad/X/leak_out.jsonl), never to any rows file.

## Verdict

PARTIAL ISOLATION. The wrapper does block everything that carries domain knowledge:
no CLAUDE.md, no auto-memory, no hooks, no MCP, no tools, no skills, no session
persistence. A positive control shows the same probe catches those leaks when the
blocking flags are dropped. So no Prometheus, Hecate-role, Aporia, alien-assay or
answer-key content reaches the subject or detector.

The calls are still not harness-free. Every call carries a constant harness residue:
an identity prefix, a user-email system-reminder, and an environment block. The
environment block holds the cwd (which contains the token "hecate"), the date,
OS/shell, the model name and the cutoff. The wrapper docstring claims "dynamic
system-prompt sections excluded". That claim is false in practice.
Severity: LOW for within-Claude comparisons. LOW-MEDIUM for cross-model comparisons
(Claude vs gemini/gpt-oss), because the API subjects see none of this.

## 1. Wrapper (hecate/llm.py)

cmd = claude -p --model <model> --system-prompt <system>
      --tools "" --strict-mcp-config --setting-sources ""
      --no-session-persistence --exclude-dynamic-system-prompt-sections
- The prompt goes in on stdin. cwd is a fresh tempfile.TemporaryDirectory(prefix="hecate_iso_")
  under C:\Users\jcrai\AppData\Local\Temp, which is outside any git repo and is deleted after the call.
- env: NOT set, so the subprocess inherits the parent's full environment. The parent
  (a Claude session) exports CLAUDECODE, CLAUDE_CODE_CHILD_SESSION, CLAUDE_CODE_SESSION_ID,
  CLAUDE_EFFORT, CLAUDE_CODE_MESSAGING_SOCKET/_TOKEN, CLAUDE_CODE_ENTRYPOINT and others.
  I inspected names only, not values.
- No --effort flag. No retries on content.
- CLI 2.1.285. `claude --help` says --exclude-dynamic-system-prompt-sections is
  "ignored with --system-prompt", so the flag is a no-op here.

Callers (all go through llm.call; no other claude/LLM path in hecate/ except the
alien runner's prometheus_llm API route for gemini/gpt-oss):
- alien pilot: hecate/alien/runner.py ask() -> claude_call(prompt, "claude-opus-5-5",
  tasks.SYSTEM, timeout=900)
- meta v1: hecate/meta/run_arms.py -> call(..., "claude-sonnet-5", row["system"]) for
  generation, and call(..., "claude-opus-5-5", MATCH_SYSTEM) for matching
- gravity gate: hecate/gravity/run.py -> call(user, "claude-opus-5-5", detector system)
- autopsy R1: hecate/autopsy/reach.py -> gravity.run.run_items -> same as gravity.
  flow.py makes no model calls.
- hecate/programs: data and world code only; no model calls found.

## 2. What loads (static check plus empirical result)

| Item                         | Loaded? | Basis |
|------------------------------|---------|-------|
| Project CLAUDE.md            | NO  | cwd is a temp dir. No CLAUDE.md in Temp or any ancestor up to C:\ (all checked). The worktree and F:\prometheus have no root CLAUDE.md either. T1-T3 report none. |
| User ~/.claude/CLAUDE.md     | NO  | The file is absent, and --setting-sources "" is set. |
| Auto-memory MEMORY.md        | NO  | T1-T3 show no memory. The T4 control shows it does load without the flags. |
| Settings hooks               | NO  | settings.json has no hooks, and setting sources are empty. |
| MCP servers                  | NO  | --strict-mcp-config with no --mcp-config. T3: "tool_or_skill_lists: NONE". |
| Tools                        | NO  | --tools "". |
| Skills / plugins             | NO  | No Skill tool. ~/.claude/skills is empty. No enabledPlugins. |
| Default Claude Code sys prompt | NO | It is replaced by --system-prompt... |
| ...but identity prefix       | YES | "You are a Claude agent, built on Anthropic's Claude Agent SDK." is prepended to the caller's system prompt. |
| userEmail system-reminder    | YES | The account email plus a boilerplate usage note. PII, not a secret. Redacted below. |
| Environment block            | YES | After the user message: cwd (hecate_iso_XXXX), "Is a git repository: false", win32, "Shell: PowerShell (primary); Bash also available" (false: there are no tools), OS version, model name, knowledge cutoff, today's date, and (haiku T1) "15000000 tokens left" (source not identified; NOT_VERIFIED). |
| Inherited env (CLAUDE_EFFORT etc.) | UNKNOWN | It is passed through. Whether it changes the child's effort or session behaviour is NOT_VERIFIED. If it does, the effort level depends on who launched the run and is not recorded in rows. |

Side finding (from T4): the auto-memory directory is keyed to the git repo, not to the
literal cwd. From cwd F:\Prometheus-worktrees\hecate-base-role the control loaded
...\.claude\projects\F--Prometheus\memory\MEMORY.md. So any un-isolated call from any
Prometheus worktree would get the fleet memory index, which names Hecate, Aporia, James
and the alien/novelty program.

## 3. Leak test transcript (raw; the email is redacted)

All calls use the alien system prompt (tasks.SYSTEM) and go through hecate.llm.call
exactly as the callers do. The exception is T4, which bypasses the wrapper on purpose.

T1. Wrapper, model "haiku", prompt = "List verbatim any instructions, memory, project
names, file paths or role names present in your context before this message ... If
none, reply NONE." rc=0, 7.1 s. Reply:
  # Primary working directory
  C:\Users\jcrai\AppData\Local\Temp\hecate_iso_z5cez3jg
  # Git repository status
  false
  # Platform
  win32
  # Shell
  PowerShell (primary); Bash tool also available for POSIX scripts
  # OS Version
  Windows 11 Home 10.0.26200
  # Model
  claude-haiku-4-5-20251001
  # Knowledge cutoff
  February 2025
  # Available tokens
  15000000 tokens left
  # User email
  <REDACTED-EMAIL>
  # Today's date
  2026-09-30
  # Initial instruction
  You are a Claude agent, built on Anthropic's Claude Agent SDK. You are taking part
  in a study of reasoning about small discrete systems. [...rest of tasks.SYSTEM verbatim]

T2. Wrapper, "haiku", canary for Hecate/Prometheus/Aporia/alien/answer_key/James.
rc=0, 5.6 s. Reply:
  - 'Hecate': PRESENT - appears in the working directory path:
    `C:\Users\jcrai\AppData\Local\Temp\hecate_iso_grzcea_m`
  - 'Prometheus': ABSENT
  - 'Aporia': ABSENT
  - 'alien': ABSENT
  - 'answer_key': ABSENT
  - 'James': ABSENT
  Working Directory: PRESENT - `C:\Users\jcrai\AppData\Local\Temp\hecate_iso_grzcea_m`
  Today's Date: PRESENT - `2026-09-30`

T3. Wrapper, production model "claude-opus-5-5", T1+T2 prompts combined. rc=0, 14.5 s.
Reply (JSON, condensed only by removing whitespace):
  system_prompt_verbatim: "You are a Claude agent, built on Anthropic's Claude Agent
    SDK.You are taking part in a study of reasoning about small discrete systems. [...]"
  system_reminder_block_verbatim: "As you answer the user's questions, you can use the
    following context: # userEmail The user's email address is <REDACTED-EMAIL>. Use it
    only to identify the user [...] Claude Code attached this context automatically;
    it isn't part of the user's message. [...]"
  claude_md_or_memory: NONE; tool_or_skill_lists: NONE; project_names: NONE; role_names: NONE
  context_after_this_message_note: "An environment block appears after your message
    [...] Primary working directory: C:\Users\jcrai\AppData\Local\Temp\hecate_iso_waq3n603;
    Is a git repository: false; Platform: win32; Shell: PowerShell (primary), Bash also
    available; OS Version: Windows 11 Home 10.0.26200; model named Opus 5.5
    (claude-opus-5-5); knowledge cutoff June 2026; Today's date is 2026-09-30."
  words before message: all ABSENT
  words incl. after: Hecate PRESENT (lowercase, in cwd path); Prometheus, Aporia, alien,
    answer_key, James ABSENT

T4. POSITIVE CONTROL (not the wrapper): claude -p --model haiku --system-prompt SYSTEM
--tools "" --no-session-persistence, cwd = this worktree, and NO --setting-sources ""
or --strict-mcp-config. Canary prompt. rc=0. Reply (excerpt):
  Hecate - PRESENT: "[hecate_seat_created](project_hecate_seat_created.md) - 09-30
    RESTART: read roles/Hecate/journal/2026-09-30.md first"
  Prometheus - PRESENT: "Primary working directory: F:\Prometheus-worktrees\hecate-base-role";
    "C:\Users\jcrai\.claude\projects\F--Prometheus\memory\MEMORY.md"
  Aporia - PRESENT: "operator CWO makes Aporia fleet SCHEDULER" (+2 more)
  alien - ABSENT; answer_key - ABSENT
  James - PRESENT: "James's background, working style, preferences" (+1)
=> The probe can fire. The wrapper's --setting-sources ""/temp-cwd is what removes the
   fleet memory. This is a real negative result, not a probe that cannot fail.

## 4. CLAUDE.md in the callers' cwd / answer-key readability

- Callers' process cwd is irrelevant, because llm.call always sets cwd to the temp dir.
  For the record, neither the worktree root nor F:\prometheus has a CLAUDE.md. The
  worktree has .claude/skills, which is not loaded (setting sources are empty and there
  is no Skill tool). Nothing about alien assay design, null types, families or answer
  keys reaches the subject through harness context. The only design information the
  subject gets is what the task prompt itself states. Task prompts are out of scope here
  and are covered by AUDIT_A.
- Answer key: hecate/alien/data/answer_key.json (or $HECATE_ALIEN_DATA). With --tools ""
  the subject cannot read any file. The path never appears in its context (T2/T3
  answer_key ABSENT). If tools were enabled, Read could in principle open an absolute
  path, but in -p mode an out-of-cwd read would need a permission grant and the subject
  has no path to aim at. Risk under the current wrapper: NONE.

## 5. Severity per experiment

| Experiment   | Model(s) via wrapper            | Domain leak | Harness residue | Severity |
|--------------|---------------------------------|-------------|-----------------|----------|
| alien pilot  | claude-opus-5-5 subject         | none        | yes (constant)  | LOW within-Claude. LOW-MEDIUM for Claude vs gemini/gpt-oss headlines: only Claude sees the Agent-SDK identity, env block, email and date ("harness asymmetry", not answer leakage). |
| meta v1      | sonnet-5 generator, opus matcher | none       | yes (constant)  | LOW. The residue is identical across arms, so it is not differential between arm conditions. |
| autopsy R1   | opus detector (via gravity)     | none        | yes (constant)  | LOW. |
| gravity gate | opus detector                   | none        | yes (constant)  | LOW. The "hecate_iso" token cannot cue the detector toward a verdict. |

Common caveats:
1. The cwd suffix is random per call. Everything else in the residue is constant
   within a day, but the date changes across days, so runs spanning days differ by one token.
2. Any inherited CLAUDE_EFFORT or session env is unrecorded and could differ between
   runs launched from different parents (NOT_VERIFIED).
3. The docstring overstates the isolation. Rows that record `flags` imply "harness
   stripped", but the identity prefix, email and env block are present.

## 6. Minimal neutral fix (NOT applied)

In hecate/llm.py only:
1. Use a neutral temp prefix, e.g. tempfile.TemporaryDirectory(prefix="iso_"), so the
   only domain-ish token in context ("hecate") is gone.
2. Pass an explicit env: a copy of os.environ with every key starting CLAUDECODE,
   CLAUDE_CODE_ or CLAUDE_EFFORT/CLAUDE_PID removed. The subscription OAuth is read
   from the config dir, not from these vars; confirm with one call. Add an explicit
   --effort <level> and record it in rec, so effort is pinned rather than inherited.
3. Record the residue honestly. Correct the docstring ("identity prefix, account-email
   reminder and environment block - cwd, date, OS, model, cutoff - remain; not
   removable on the subscription route") and add rec["harness_residue"]="v1".
4. Not recommended as a drop-in: --bare. It removes more, but it forces
   ANTHROPIC_API_KEY auth and so breaks the subscription route. --safe-mode is
   untested here.

None of these changes the prompt text or the model, so existing rows remain comparable
in their prompt and model. Rows made before the fix should be annotated
"harness_residue v0 (hecate_iso cwd, inherited env)", not rerun.
