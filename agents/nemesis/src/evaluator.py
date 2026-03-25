"""Evaluate forged tools against adversarial tasks.

Computes per-tool results, disagreement scores, blind spot detection,
and overconfidence flags.
"""

import importlib.util
import logging
import sys
from pathlib import Path

log = logging.getLogger("nemesis.evaluator")


def load_tool(path: Path):
    """Load a ReasoningTool from a .py file."""
    mod_name = f"_nemesis_eval_{path.stem}"
    spec = importlib.util.spec_from_file_location(mod_name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tool = mod.ReasoningTool()
    sys.modules.pop(mod_name, None)
    return tool


def load_all_tools(forge_dir: Path) -> dict:
    """Load all forge tools. Returns {name: tool_instance}."""
    tools = {}
    for py in sorted(forge_dir.glob("*.py")):
        try:
            tool = load_tool(py)
            tools[py.stem] = tool
        except Exception as e:
            log.debug("Skipping %s: %s", py.stem, e)
    log.info("Loaded %d tools from %s", len(tools), forge_dir)
    return tools


def evaluate_task(task, tools: dict) -> dict:
    """Run all tools against a single adversarial task.

    Args:
        task: AdversarialTask instance
        tools: dict of {name: tool_instance}

    Returns dict with per-tool results and aggregate metrics.
    Updates task.tool_results, task.disagreement, task.tools_broken, task.blind_spot.
    """
    prompt = task.prompt
    candidates = task.candidates
    correct = task.correct

    tool_answers = {}  # name -> top_candidate
    tool_confidences = {}  # name -> (conf_correct, conf_wrong)
    tool_correct = {}  # name -> bool

    wrong_candidates = [c for c in candidates if c != correct]
    wrong = wrong_candidates[0] if wrong_candidates else candidates[-1]

    for name, tool in tools.items():
        try:
            ranked = tool.evaluate(prompt, candidates)
            top = ranked[0]["candidate"] if ranked else None
            tool_answers[name] = top
            is_correct = (top == correct)
            tool_correct[name] = is_correct
        except Exception as e:
            tool_answers[name] = f"ERROR:{e}"
            tool_correct[name] = False

        try:
            conf_c = tool.confidence(prompt, correct)
            conf_w = tool.confidence(prompt, wrong)
            tool_confidences[name] = (conf_c, conf_w)
        except Exception:
            tool_confidences[name] = (0.5, 0.5)

    # Compute metrics
    n_tools = len(tools)
    if n_tools == 0:
        return {}

    # Disagreement: number of distinct answers / number of tools
    unique_answers = set(a for a in tool_answers.values() if not str(a).startswith("ERROR"))
    disagreement = len(unique_answers) / max(n_tools, 1)

    # Tools broken: how many got it wrong
    n_correct = sum(1 for v in tool_correct.values() if v)
    n_broken = n_tools - n_correct

    # Blind spot: ALL tools wrong
    blind_spot = (n_correct == 0 and n_tools > 0)

    # Overconfident failures: high confidence but wrong
    overconfident = []
    for name, is_correct in tool_correct.items():
        if not is_correct and name in tool_confidences:
            conf_c, conf_w = tool_confidences[name]
            if conf_w > 0.7:  # high confidence in wrong answer
                overconfident.append(name)

    # Update task
    task.tool_results = {
        name: {
            "answer": tool_answers[name],
            "correct": tool_correct[name],
            "confidence_correct": tool_confidences.get(name, (0, 0))[0],
            "confidence_wrong": tool_confidences.get(name, (0, 0))[1],
        }
        for name in tools
    }
    task.disagreement = disagreement
    task.tools_broken = n_broken
    task.blind_spot = blind_spot

    return {
        "disagreement": disagreement,
        "n_correct": n_correct,
        "n_broken": n_broken,
        "blind_spot": blind_spot,
        "overconfident": overconfident,
        "unique_answers": len(unique_answers),
        "tool_answers": tool_answers,
    }


def evaluate_batch(tasks: list, tools: dict) -> list[dict]:
    """Evaluate all tools against a batch of tasks."""
    results = []
    for task in tasks:
        r = evaluate_task(task, tools)
        results.append(r)
    return results
