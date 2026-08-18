# The non-agentic driver

The loop is a `while` in Python. Inference is a called function, never the caller.

An agentic loop pauses because the model owns control flow: every turn it chooses
continue-or-report, and a check-in disposition takes "report". This driver removes that
choice. `run.py` decides what runs next from the queue; it calls `claude -p` for bounded
judgement tasks and takes the answer back. The model is never asked whether to continue.

**Default-continue is a hard rule, not a preference.** Ambiguity resolves to the first
listed option, the choice is logged to DECISIONS.jsonl, and execution proceeds. James's
standing instruction (2026-08-18): "when I want A, then B. Almost always." Only
irreversible or outward-facing actions block, and they block *themselves* — never the queue.
