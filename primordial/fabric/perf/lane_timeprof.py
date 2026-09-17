"""Lane wall-clock attribution, state-machine version.

State while replaying a transcript in time order:
  open tools (tool_use ids awaiting tool_result) -> gap is TOOL time, charged to
      the category of the oldest open tool (parallel calls are not double counted)
  no open tools, next entry is assistant           -> MODEL time
  no open tools, next is task-notification         -> BG_WAIT (backgrounded job)
  no open tools, next is other user text           -> HUMAN/LOOP wait
  otherwise                                         -> OTHER (reported by entry type)
Gaps > 15 min with no open tool -> LONG_IDLE.
Background jobs: launch time (tool_use with run_in_background) -> matching
task-notification, reported as job durations (they overlap other work).
Model latency is also bucketed by context size (input+cache tokens).
"""
import json, sys, re, collections, datetime, statistics

def ts(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()

def bash_cat(cmd):
    c = cmd
    if re.search(r'primordial\.bus|bus\.post|bus\.receipt|xrange|XRANGE', c): return 'bash:bus'
    if re.search(r'\bpytest\b', c): return 'bash:pytest'
    if re.search(r'git (push|rebase|fetch|pull|merge|commit|worktree|cherry)', c): return 'bash:git_sync'
    if re.search(r'\bgit (log|show|diff|status|ls-tree|rev-parse|grep|blame|add)', c): return 'bash:git_read'
    if re.search(r'wsl\.exe|docker', c): return 'bash:wsl_docker'
    if re.search(r'python|\$PY|gw-venv', c): return 'bash:python_run'
    if re.search(r'^\s*(cat|sed|head|tail|grep|ls|wc|find|awk|rg)\b', c): return 'bash:read_shell'
    if re.search(r'\bsleep\b', c): return 'bash:sleep'
    return 'bash:other'

def analyse(fn):
    rows = [json.loads(l) for l in open(fn, encoding='utf-8') if l.strip()]
    ents = []
    for r in rows:
        if r.get('timestamp'):
            ents.append((ts(r['timestamp']), r))
    ents.sort(key=lambda e: e[0])
    cat_of, open_tools, bg_launch = {}, {}, {}
    acc, cnt = collections.Counter(), collections.Counter()
    other_types = collections.Counter()
    long_idle = 0.0
    model_by_ctx = collections.defaultdict(list)
    bg_jobs = []
    tool_single = collections.defaultdict(list)
    prev_t = None
    for t, r in ents:
        typ = r.get('type')
        m = r.get('message') if isinstance(r.get('message'), dict) else {}
        c = m.get('content')
        if prev_t is not None:
            g = t - prev_t
            if g >= 0:
                if open_tools:
                    oldest = min(open_tools.items(), key=lambda kv: kv[1])[0]
                    acc[cat_of[oldest]] += g
                elif g > 900:
                    long_idle += g
                elif typ == 'assistant':
                    acc['model'] += g; cnt['model'] += 1
                    u = m.get('usage') or {}
                    ctx = u.get('cache_read_input_tokens', 0) + u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0)
                    b = '<100k' if ctx < 1e5 else '100-250k' if ctx < 2.5e5 else '250-500k' if ctx < 5e5 else '>500k'
                    model_by_ctx[b].append(g)
                elif typ == 'user':
                    txt = c if isinstance(c, str) else ' '.join(x.get('text', '') for x in (c or []) if isinstance(x, dict))
                    if 'task-notification' in (txt or ''):
                        acc['bg_wait'] += g
                    elif any(isinstance(x, dict) and x.get('type') == 'tool_result' for x in (c or []) if not isinstance(c, str)):
                        acc['tool:late_result'] += g
                    else:
                        acc['human_or_loop'] += g
                else:
                    acc['other'] += g; other_types[typ] += g
        # state updates
        if typ == 'assistant' and isinstance(c, list):
            for x in c:
                if x.get('type') == 'tool_use':
                    name = x['name']; inp = x.get('input', {})
                    cat = bash_cat(inp.get('command', '')) if name == 'Bash' else 'tool:' + name
                    cat_of[x['id']] = cat
                    open_tools[x['id']] = t
                    if name == 'Bash' and inp.get('run_in_background'):
                        bg_launch[x['id']] = (t, bash_cat(inp.get('command', '')), inp.get('description', '')[:50])
        if typ == 'user' and isinstance(c, list):
            for x in c:
                if isinstance(x, dict) and x.get('type') == 'tool_result':
                    tid = x.get('tool_use_id')
                    if tid in open_tools:
                        tool_single[cat_of[tid]].append(t - open_tools.pop(tid))
        if typ in ('user', 'queue-operation'):
            txt = c if isinstance(c, str) else json.dumps(c) if c else (r.get('content') or '')
            mm = re.search(r'<tool-use-id>(toolu_[A-Za-z0-9]+)</tool-use-id>', txt or '')
            if mm and mm.group(1) in bg_launch and 'completed' in txt:
                t0, bc, desc = bg_launch.pop(mm.group(1))
                bg_jobs.append((t - t0, bc, desc))
        prev_t = t
    span = ents[-1][0] - ents[0][0]
    return span, long_idle, acc, other_types, model_by_ctx, bg_jobs, tool_single

def m(s):
    return f"{s/60:6.1f}m"

if __name__ == '__main__':
    G = collections.Counter(); GS = GI = 0
    GM = collections.defaultdict(list); GB = []; GT = collections.defaultdict(list); GO = collections.Counter()
    for fn in sys.argv[1:]:
        span, idle, acc, ot, mb, bg, tsn = analyse(fn)
        GS += span; GI += idle; G.update(acc); GO.update(ot); GB += bg
        for k, v in mb.items(): GM[k] += v
        for k, v in tsn.items(): GT[k] += v
        busy = sum(acc.values())
        print(f"== {fn[:8]} span {m(span)} long_idle {m(idle)} attributed {m(busy)}")
        for k, v in acc.most_common(8):
            print(f"   {k:20s} {m(v)} {100*v/busy:5.1f}%")
        if bg:
            print(f"   bg jobs n={len(bg)} total {m(sum(b[0] for b in bg))} longest " +
                  ", ".join(f"{b[0]/60:.1f}m {b[2]}" for b in sorted(bg, reverse=True)[:3]))
    busy = sum(G.values())
    print(f"\n== ALL span {m(GS)} long_idle {m(GI)} attributed {m(busy)}")
    for k, v in G.most_common(14):
        print(f"   {k:20s} {m(v)} {100*v/busy:5.1f}%")
    print("   other by entry type:", {k: round(v/60, 1) for k, v in GO.most_common(5)})
    print("\nsingle tool call durations (s): category n median p90 max total_min")
    for k, v in sorted(GT.items(), key=lambda kv: -sum(kv[1]))[:10]:
        q = sorted(v)
        print(f"   {k:20s} {len(q):4d} {q[len(q)//2]:7.1f} {q[int(.9*(len(q)-1))]:7.1f} {q[-1]:7.0f} {sum(q)/60:7.1f}")
    print("\nmodel step latency by context size: bucket n median mean p90 total_min")
    for b in ('<100k', '100-250k', '250-500k', '>500k'):
        q = sorted(GM.get(b, []))
        if q:
            print(f"   {b:10s} {len(q):5d} {q[len(q)//2]:6.1f} {statistics.mean(q):6.1f} {q[int(.9*(len(q)-1))]:6.1f} {sum(q)/60:7.1f}")
    if GB:
        print(f"\nbackground jobs all lanes n={len(GB)} total {m(sum(b[0] for b in GB))}; by category:",
              {k: round(sum(b[0] for b in GB if b[1] == k)/60, 1) for k in set(b[1] for b in GB)})
