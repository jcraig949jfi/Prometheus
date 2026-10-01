"""Renderings of the canonical snapshot: HTML page, email block (md + inline-styled html), markdown.

Nothing here computes a classification; it only formats prometheus.fleet_census.v2.
The page is self-contained (no CDN): GitHub Pages serves it from docs/fleet/.
"""
from __future__ import annotations

import html
import json

from .util import parse_time, human_age, age_hours

PAGES_URL = "https://jcraig949jfi.github.io/Prometheus/fleet/"
REPO_URL = "https://github.com/jcraig949jfi/Prometheus"
STATE_ORDER = ["WORKING", "ACTIVE", "READY", "IDLE", "BLOCKED", "HOLD", "PARKED", "DORMANT", "RETIRED", "UNKNOWN"]
STALE_AFTER_H = 7.0  # the census runs every 6 h; one missed run makes the page say so


def _v(f):
    return (f or {}).get("value") if isinstance(f, dict) else f


def _engines_short(row):
    names = [e.get("engine_id") for e in row.get("engines") or [] if e.get("relationship") in ("primary", "maintainer", "builder")]
    return ", ".join(n for n in names if n) or ("-" if not row.get("engines") else ", ".join(
        "{} ({})".format(e.get("engine_id"), e.get("relationship")) for e in row["engines"][:2]))


def table_rows(snap):
    """Compact rows for the page's JS table and for the email."""
    out = []
    eng = snap.get("engines") or {}
    for name, r in snap["seats"].items():
        lc = r.get("last_commit") or {}
        le = r.get("last_experiment") or {}
        la = r.get("last_active") or {}
        host = r.get("host") or {}
        prim = [e.get("engine_id") for e in r.get("engines") or [] if e.get("relationship") in ("primary", "maintainer", "builder")]
        edesc = "; ".join((eng.get(e) or {}).get("purpose") or "" for e in prim[:2] if eng.get(e)).strip("; ")
        out.append({
            "seat": name, "kind": r["kind"], "role": r.get("short_role") or "",
            "desc": _v(r.get("role_description")) or "",
            "observed": (r.get("observed_role") or {}).get("text") if r.get("observed_role") else "",
            "state": r["state"], "active": r["active"],
            "last_active": la.get("value") or "", "age_h": (r["state_detail"]["activity"] or {}).get("substantive_age_h"),
            "age": r.get("activity_age") or "never",
            "last_activity": r.get("last_activity") or "",
            "task": _v(r.get("task")) or "", "task_src": (r.get("task") or {}).get("source") or "",
            "exp": _v(le) or "", "exp_result": r.get("experiment_result") or "", "exp_url": le.get("url") or "",
            "commit": _v(lc) or "", "commit_time": lc.get("source_time") or "", "commit_url": lc.get("url") or "",
            "engine": _engines_short(r), "engine_desc": edesc,
            "branch": _v(r.get("branch_worktree")) or "", "host": host.get("value") or "",
            "host_doc": host.get("documented") or "",
            "blocker": r.get("blocker") or "", "conf": r.get("confidence"),
            "domain": r.get("domain") or "", "flags": r.get("flags") or [],
            "rule": r["state_detail"]["rule"],
        })
    out.sort(key=lambda x: (x["kind"] not in ("SEAT", "BRANCH_ONLY_SEAT"),
                            STATE_ORDER.index(x["state"]) if x["state"] in STATE_ORDER else 99,
                            x["age_h"] if x["age_h"] is not None else 1e9))
    return out


def _esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1f;--muted:#6b6b70;--line:#e3e3e0;--accent:#2f5d8a;
--ok:#1f7a4d;--warn:#a86a00;--bad:#b3261e;--chip:#eef1f5;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121316;--card:#1b1c20;--ink:#e8e8ea;--muted:#9a9aa2;
--line:#2c2d33;--accent:#8fb4dc;--ok:#5cc391;--warn:#e0a640;--bad:#ef7b72;--chip:#24262c}}
:root[data-theme="dark"]{--bg:#121316;--card:#1b1c20;--ink:#e8e8ea;--muted:#9a9aa2;--line:#2c2d33;--accent:#8fb4dc;
--ok:#5cc391;--warn:#e0a640;--bad:#ef7b72;--chip:#24262c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1400px;margin:0 auto;padding:20px 16px 60px}h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:28px 0 10px}
.sub{color:var(--muted);font-size:13px}.banner{border-radius:8px;padding:10px 14px;margin:14px 0;border:1px solid var(--line);background:var(--card)}
.banner.bad{border-color:var(--bad);color:var(--bad);font-weight:600}.banner.ok{border-color:var(--ok)}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:8px;margin:12px 0}
.tile{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 10px}.tile b{display:block;font-size:20px}
.tile span{color:var(--muted);font-size:12px}.controls{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
select,input{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:5px 8px;font:inherit}
.wrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:12.5px}th,td{padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
th{position:sticky;top:0;background:var(--card);cursor:pointer;white-space:nowrap;user-select:none}th:hover{color:var(--accent)}
td.clip{max-width:260px}td.clip div{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.st{display:inline-block;border-radius:10px;padding:1px 8px;font-size:11px;font-weight:600;background:var(--chip)}
.st.WORKING,.st.ACTIVE{color:var(--ok)}.st.READY{color:var(--accent)}.st.BLOCKED,.st.UNKNOWN{color:var(--bad)}
.st.IDLE,.st.HOLD,.st.DORMANT{color:var(--warn)}.st.PARKED,.st.RETIRED{color:var(--muted)}
.flag{display:inline-block;font-size:10.5px;color:var(--bad);border:1px solid var(--bad);border-radius:4px;padding:0 4px;margin:1px 2px 0 0}
a{color:var(--accent)}code,.mono{font-family:var(--mono);font-size:12px}details{background:var(--card);border:1px solid var(--line);border-radius:8px;margin:6px 0;padding:6px 12px}
summary{cursor:pointer;font-weight:600}dl{display:grid;grid-template-columns:180px 1fr;gap:4px 12px;margin:8px 0}dt{color:var(--muted)}dd{margin:0}
ul.tight{margin:4px 0;padding-left:18px}.muted{color:var(--muted)}
@media (max-width:640px){dl{grid-template-columns:1fr}}
"""

JS = r"""
const ROWS = JSON.parse(document.getElementById('rows').textContent);
const RUN = JSON.parse(document.getElementById('run').textContent);
let sortKey='state', sortDir=1;
const ORDER=%ORDER%;
const cols=[['seat','Agent'],['role','Role'],['desc','Role description'],['state','State'],['active','Active?'],['last_active','Last active'],
['age','Age'],['last_activity','Last activity'],['task','Current / last task'],['exp','Last experiment'],['exp_result','Result'],
['commit','Last commit'],['engine','Engine / system'],['engine_desc','Engine description'],['branch','Branch / worktree'],['host','Host'],
['blocker','Blocker'],['conf','Conf.']];
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function val(r,k){if(k==='state')return ORDER.indexOf(r.state);if(k==='age'||k==='last_active')return r.age_h??1e9;return String(r[k]??'').toLowerCase()}
function render(){
 const fs=document.getElementById('f-state').value, fa=document.getElementById('f-active').value, fh=document.getElementById('f-host').value,
 fd=document.getElementById('f-domain').value, fk=document.getElementById('f-kind').value, fg=document.getElementById('f-age').value,
 q=document.getElementById('f-q').value.toLowerCase();
 let rows=ROWS.filter(r=>(!fs||r.state===fs)&&(!fa||r.active===fa)&&(!fh||r.host===fh)&&(!fd||r.domain===fd)
  &&(!fk||(fk==='seats'?['SEAT','BRANCH_ONLY_SEAT'].includes(r.kind):!['SEAT','BRANCH_ONLY_SEAT'].includes(r.kind)))
  &&(!fg||(r.age_h!=null&&r.age_h<=Number(fg)))&&(!q||JSON.stringify(r).toLowerCase().includes(q)));
 rows.sort((a,b)=>{const x=val(a,sortKey),y=val(b,sortKey);return (x>y?1:x<y?-1:0)*sortDir});
 document.getElementById('count').textContent=rows.length+' of '+ROWS.length;
 const head='<tr>'+cols.map(c=>'<th data-k="'+c[0]+'">'+c[1]+(sortKey===c[0]?(sortDir>0?' &#9650;':' &#9660;'):'')+'</th>').join('')+'</tr>';
 const body=rows.map(r=>'<tr>'+
  '<td><a href="#seat-'+esc(r.seat)+'">'+esc(r.seat)+'</a>'+(r.kind!=='SEAT'?'<div class="muted">'+esc(r.kind)+'</div>':'')+'</td>'+
  '<td>'+esc(r.role)+'</td><td class="clip"><div>'+esc(r.desc)+(r.observed?'<br><i>Observed: '+esc(r.observed)+'</i>':'')+'</div></td>'+
  '<td><span class="st '+esc(r.state)+'">'+esc(r.state)+'</span>'+r.flags.map(f=>'<br><span class="flag">'+esc(f)+'</span>').join('')+'</td>'+
  '<td>'+esc(r.active)+'</td><td class="mono">'+esc((r.last_active||'').replace('T',' ').replace('Z',''))+'</td><td>'+esc(r.age)+'</td>'+
  '<td class="clip"><div>'+esc(r.last_activity)+'</div></td><td class="clip"><div>'+esc(r.task)+'</div><div class="muted">'+esc(r.task_src)+'</div></td>'+
  '<td class="clip"><div>'+(r.exp_url?'<a href="'+esc(r.exp_url)+'">'+esc(r.exp)+'</a>':esc(r.exp))+'</div></td><td>'+esc(r.exp_result)+'</td>'+
  '<td class="clip"><div>'+(r.commit_url?'<a href="'+esc(r.commit_url)+'">'+esc(r.commit)+'</a>':esc(r.commit))+'</div><div class="muted mono">'+esc((r.commit_time||'').slice(0,16))+'</div></td>'+
  '<td>'+esc(r.engine)+'</td><td class="clip"><div>'+esc(r.engine_desc)+'</div></td><td class="clip"><div class="mono">'+esc(r.branch)+'</div></td>'+
  '<td>'+esc(r.host)+(r.host_doc&&r.host_doc!==r.host?'<div class="muted">docs: '+esc(r.host_doc)+'</div>':'')+'</td>'+
  '<td class="clip"><div>'+esc(r.blocker)+'</div></td><td>'+esc(r.conf)+'</td></tr>').join('');
 document.getElementById('tbl').innerHTML='<thead>'+head+'</thead><tbody>'+body+'</tbody>';
 document.querySelectorAll('#tbl th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;sortDir=(sortKey===k)?-sortDir:1;sortKey=k;render()});
}
function fill(id,vals){const s=document.getElementById(id);[...new Set(vals)].filter(Boolean).sort().forEach(v=>{const o=document.createElement('option');o.value=o.textContent=v;s.appendChild(o)})}
fill('f-state',ROWS.map(r=>r.state));fill('f-host',ROWS.map(r=>r.host));fill('f-domain',ROWS.map(r=>r.domain));
document.querySelectorAll('.controls select,.controls input').forEach(e=>e.oninput=render);
render();
// Freshness is computed in the viewer's browser, so a dead scheduler cannot leave this page looking fresh.
function freshness(rs){const now=Date.now(),ok=Date.parse(rs.last_successful_utc||0),at=Date.parse(rs.last_attempted_utc||0);
 const h=(now-ok)/36e5, el=document.getElementById('fresh');
 let msg='Last successful census: '+(rs.last_successful_utc||'never')+' ('+(isFinite(h)?h.toFixed(1)+'h ago':'?')+'). Last attempted: '+(rs.last_attempted_utc||'never')+' ('+(rs.last_status||'?')+').';
 if(!isFinite(h)||h>%STALE%||rs.last_status!=='SUCCESS'){el.className='banner bad';msg='STALE OR FAILED CENSUS. '+msg+(rs.last_error?' Error: '+rs.last_error:'')}
 else el.className='banner ok';el.textContent=msg}
freshness(RUN);
fetch('run_status.json?t='+Date.now()).then(r=>r.ok?r.json():null).then(j=>{if(j)freshness(j)}).catch(()=>{});
"""


def render_html(snap) -> str:
    rows = table_rows(snap)
    s = snap["summary"]
    run = snap.get("run") or {}
    counts = s["counts_by_state"]
    tiles = [("Seats", s["seats_total"])] + [(k.title(), counts.get(k, 0)) for k in STATE_ORDER] + [
        ("Active 6h", s["active_6h"]), ("Active 24h", s["active_24h"]), ("Active 72h", s["active_72h"]),
        ("Experiments 24h", s["experiments_24h"]), ("Commits 24h", s["commits_24h"]),
        ("Other entities", s["non_seat_entities"])]
    d = snap.get("delta") or {}
    delta_items = []
    for key, label in (("seats_activated", "Seats activated"), ("seats_went_quiet", "Became idle/dormant"),
                       ("state_changes", "State changes"), ("new_assignments", "New assignments"),
                       ("experiments_completed", "Experiments completed"), ("engine_ownership_changes", "Engine ownership changes"),
                       ("blockers_added", "Blockers added"), ("blockers_cleared", "Blockers cleared"),
                       ("new_seats", "Newly discovered seats"), ("new_anomalies", "New inconsistencies")):
        v = d.get(key) or []
        if v:
            delta_items.append("<li><b>{}</b> ({}): {}</li>".format(_esc(label), len(v), _esc("; ".join(v[:25]))))
    if not delta_items:
        delta_items.append("<li>{}</li>".format(_esc(d.get("note") or "No changes since the previous census.")))

    an_rows = "".join("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(_esc(a["type"]), _esc(a["subject"]), _esc(a["detail"]))
                      for a in snap["anomalies"])
    eng_rows = []
    for eid, e in sorted(snap["engines"].items(), key=lambda kv: kv[0].lower()):
        lc = e.get("last_change") or {}
        others = ", ".join("{} ({})".format(o.get("seat"), o.get("relationship")) for o in e.get("other_seats") or [])
        sm = e.get("state_marker") or {}
        eng_rows.append("<tr><td><code>{}</code><div>{}</div></td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
                        "<td>{}</td><td>{}</td></tr>".format(
                            _esc(eid), _esc(e.get("name")), _esc(e.get("kind")), _esc(e.get("purpose")),
                            _esc(e.get("primary_seat") or "none recorded"), _esc(others),
                            _esc(sm.get("state")),
                            "<a href='{}/commit/{}'>{}</a> {} <span class=muted>{}</span>".format(REPO_URL, _esc(lc.get("sha")), _esc(lc.get("sha")), _esc((lc.get("subject") or "")[:90]), _esc(e.get("last_change_age"))) if lc else "-",
                            "".join("<span class=flag>{}</span>".format(_esc(f)) for f in e.get("flags") or [])))

    details = []
    for name, r in sorted(snap["seats"].items(), key=lambda kv: kv[0].lower()):
        sd = r["state_detail"]
        def lst(items, fmt):
            return "<ul class=tight>" + "".join("<li>{}</li>".format(fmt(i)) for i in items) + "</ul>" if items else "<span class=muted>none found</span>"
        decl = lst(sd.get("declared") or [], lambda x: "{} <span class=muted>({}; {} ; raw: {})</span>".format(
            _esc(x.get("state")), _esc(x.get("source")), _esc(x.get("time")), _esc(x.get("raw"))))
        ag = (snap.get("aggregates") or {}).get(name) or {}
        rc = lst(ag.get("recent_commits") or [], lambda c: "<a href='{}/commit/{}'><code>{}</code></a> {} <span class=muted>{} [{}]</span>".format(
            REPO_URL, _esc(c["sha"]), _esc(c["sha"]), _esc(c["subject"]), _esc(c["time"][:16]), _esc(c.get("category"))))
        rm = lst(ag.get("recent_messages") or [], lambda m: "#{} {} to {}: {} <span class=muted>{}</span>".format(
            _esc(m["id"]), _esc(m["kind"]), _esc(m.get("to")), _esc(m["subject"]), _esc((m["time"] or "")[:16])))
        rx = lst(ag.get("recent_experiments") or [], lambda c: "<code>{}</code> {} <span class=muted>{} {}</span>".format(
            _esc(c["sha"]), _esc(c["subject"]), _esc(c["time"][:16]), _esc(c.get("verdict") or "")))
        ev = lst(r.get("evidence") or [], lambda e: "{}: <code>{}</code> <span class=muted>{}</span>".format(_esc(e["what"]), _esc(e["ref"]), _esc(e.get("time"))))
        eng = lst(r.get("engines") or [], lambda e: "<code>{}</code> ({}) <span class=muted>{}</span>".format(_esc(e.get("engine_id")), _esc(e.get("relationship")), _esc(e.get("evidence"))))
        task = r.get("task") or {}
        tc = lst(task.get("candidates") or [], lambda c: "{} <span class=muted>({}; {})</span>".format(_esc(c["value"]), _esc(c["source"]), _esc(c["time"])))
        orole = r.get("observed_role")
        role_html = "<b>Declared role:</b> {} <span class=muted>({}, currency {})</span>".format(
            _esc(_v(r.get("role_description")) or "none recorded"), _esc((r.get("role_description") or {}).get("source")),
            _esc((r.get("role_description") or {}).get("source_time")))
        if orole:
            role_html += "<br><b>Observed current role:</b> {} <span class=muted>({})</span>".format(
                _esc(orole.get("text")), _esc("; ".join(orole.get("evidence") or [])[:300]))
        lm = r.get("lifecycle_marker") or {}
        details.append(
            "<details id='seat-{n}'><summary>{n} <span class='st {s}'>{s}</span> <span class=muted>{role} &middot; {age}</span></summary><dl>"
            "<dt>Role</dt><dd>{role_html}</dd><dt>Kind / domain</dt><dd>{kind} / {dom}</dd>"
            "<dt>State</dt><dd>{s} (rule {rule}, confidence {conf})<ul class=tight>{why}</ul></dd>"
            "<dt>Declared states</dt><dd>{decl}</dd><dt>Lifecycle marker</dt><dd>{lm}</dd>"
            "<dt>Current assignment</dt><dd>{task} <span class=muted>({tsrc})</span><details><summary class=muted>all task candidates</summary>{tc}</details></dd>"
            "<dt>Recent work</dt><dd>{la}</dd><dt>Recent experiments</dt><dd>{rx}</dd><dt>Recent commits</dt><dd>{rc}</dd>"
            "<dt>Recent comms</dt><dd>{rm}</dd><dt>Engines</dt><dd>{eng}</dd><dt>Blocker</dt><dd>{blk}</dd>"
            "<dt>Host</dt><dd>{host}</dd><dt>Branch / worktree</dt><dd>{bw}</dd><dt>Presence (weak)</dt><dd>{pres}</dd>"
            "<dt>Registered loops</dt><dd>{mons}</dd><dt>Evidence</dt><dd>{ev}</dd><dt>Flags</dt><dd>{flags}</dd></dl></details>".format(
                n=_esc(name), s=_esc(r["state"]), role=_esc(r.get("short_role") or ""), age=_esc(r.get("activity_age")),
                role_html=role_html, kind=_esc(r["kind"]), dom=_esc(r.get("domain")), rule=_esc(sd["rule"]), conf=_esc(r["confidence"]),
                why="".join("<li>{}</li>".format(_esc(w)) for w in sd.get("why") or []), decl=decl,
                lm=_esc("{} {} {} ({})".format(lm.get("state") or "none", lm.get("date") or "", lm.get("quote") or "", lm.get("source") or "")),
                task=_esc(_v(task) or "none found"), tsrc=_esc(task.get("source")), tc=tc,
                la=_esc(r.get("last_activity") or "none found"), rx=rx, rc=rc, rm=rm, eng=eng,
                blk=_esc(r.get("blocker") or "none recorded"),
                host=_esc("{} ({}){}".format(_v(r.get("host")) or "unknown", (r.get("host") or {}).get("source"),
                                             "; documented: {} ({})".format((r.get("host") or {}).get("documented"), (r.get("host") or {}).get("documented_source")) if (r.get("host") or {}).get("documented") else "")),
                bw=_esc(_v(r.get("branch_worktree")) or "unknown"),
                pres=_esc("{} ({})".format((r.get("presence") or {}).get("value"), (r.get("presence") or {}).get("source")) if r.get("presence") else "none"),
                mons=lst(r.get("monitors") or [], lambda m: "<code>{}</code> {} <span class=muted>({}; {})</span>".format(
                    _esc(m["name"]), _esc(m["state"]), _esc(m.get("host")), _esc(m.get("kind")))),
                ev=ev, flags="".join("<span class=flag>{}</span>".format(_esc(f)) for f in r.get("flags") or []) or "none"))

    m = snap.get("mailer") or {}
    src = snap.get("sources_status") or {}
    run_embed = {"last_successful_utc": run.get("last_successful_utc"), "last_attempted_utc": run.get("last_attempted_utc"),
                 "last_status": run.get("status"), "last_error": run.get("error")}
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prometheus Fleet Census</title><style>{css}</style></head><body><main>
<h1>Prometheus Fleet Census</h1>
<div class="sub">Generated {gen} from origin/main <code>{sha}</code> &middot; {mwo} &middot; {cwo} &middot; mode {mode} &middot; maintained by Achilles &middot;
<a href="fleet_state.json">canonical snapshot (JSON)</a> &middot; <a href="{repo}/blob/main/roles/Achilles/CLASSIFICATION_RULES.md">classification rules</a></div>
<div id="fresh" class="banner">Checking census freshness...</div>
<div class="tiles">{tiles}</div>
<div class="sub">Counts cover seats (roles/ directories, including branch-only seats). Historical role documents and pre-seat agents/tools are listed too, filtered as "other entities".
Sources: git {git}; comms {comms}; evidence wiki {ew}; legacy agora {agora}. Mailer last success {mail_ok} (census included: {mail_c}).</div>
<h2>Changes since previous census <span class="sub">(previous: {prev})</span></h2><ul>{delta}</ul>
<h2>Fleet</h2>
<div class="controls">
<select id="f-kind"><option value="seats">Seats only</option><option value="">Seats + other entities</option><option value="other">Other entities only</option></select>
<select id="f-state"><option value="">All states</option></select>
<select id="f-active"><option value="">Active: any</option><option>Yes</option><option>Uncertain</option><option>No</option></select>
<select id="f-host"><option value="">All hosts</option></select>
<select id="f-domain"><option value="">All domains</option></select>
<select id="f-age"><option value="">Any activity age</option><option value="6">within 6h</option><option value="24">within 24h</option><option value="72">within 72h</option><option value="168">within 7d</option></select>
<input id="f-q" placeholder="search (engine, task, ...)"><span class="sub" id="count"></span></div>
<div class="wrap"><table id="tbl"></table></div>
<h2>Inconsistencies and anomalies ({nan})</h2>
<div class="wrap"><table><thead><tr><th>Type</th><th>Subject</th><th>Detail</th></tr></thead><tbody>{an}</tbody></table></div>
<h2>Engines and subsystems ({neng})</h2>
<div class="wrap"><table><thead><tr><th>Engine</th><th>Kind</th><th>Purpose</th><th>Primary seat</th><th>Other seats</th><th>State</th><th>Last change</th><th>Flags</th></tr></thead>
<tbody>{eng}</tbody></table></div>
<h2>Seat details</h2>{details}
<p class="sub">Achilles observes and reports; it assigns no work and rules on no science. Every status above cites its evidence; where sources disagree the disagreement is shown and confidence lowered.</p>
</main>
<script id="rows" type="application/json">{rows}</script><script id="run" type="application/json">{runj}</script>
<script>{js}</script></body></html>""".format(
        css=CSS, gen=_esc(snap["generated_at_utc"]), sha=_esc((snap.get("base_sha") or "")[:10]), mwo=_esc(snap.get("current_mwo")),
        cwo=_esc((snap.get("latest_cwo") or "").rsplit("/", 1)[-1]), mode=_esc((snap.get("stats") or {}).get("mode")), repo=REPO_URL,
        tiles="".join("<div class=tile><b>{}</b><span>{}</span></div>".format(_esc(v), _esc(k)) for k, v in tiles),
        git=_esc(src.get("git")), comms=_esc(src.get("comms")), ew=_esc(src.get("ew", "n/a")), agora=_esc(src.get("agora", "n/a")),
        mail_ok=_esc(m.get("last_success")), mail_c=_esc(m.get("census_included_last")),
        prev=_esc(d.get("previous_generated_at") or "none"), delta="".join(delta_items),
        nan=len(snap["anomalies"]), an=an_rows or "<tr><td colspan=3>none</td></tr>", neng=len(snap["engines"]), eng="".join(eng_rows),
        details="".join(details),
        rows=json.dumps(rows).replace("</", "<\\/"), runj=json.dumps(run_embed).replace("</", "<\\/"),
        js=JS.replace("%ORDER%", json.dumps(STATE_ORDER)).replace("%STALE%", str(STALE_AFTER_H)))
    return page


# ---------------------------------------------------------------- email

def _short(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 3] + "..."


def email_block(snap) -> dict:
    """The census section the existing mailer embeds (docs/fleet/email_census.json)."""
    rows = [r for r in table_rows(snap) if r["kind"] in ("SEAT", "BRANCH_ONLY_SEAT")]
    s = snap["summary"]
    d = snap.get("delta") or {}
    counts = ", ".join("{} {}".format(k, s["counts_by_state"][k]) for k in STATE_ORDER if s["counts_by_state"].get(k))
    attention = [r for r in rows if r["state"] in ("BLOCKED", "UNKNOWN") or any(
        f in ("ACTIVE_NO_WORK_48H", "ASSIGNMENT_NO_PROGRESS", "VISIBILITY_STALE", "CONFLICTING_STATES", "PARKED_BUT_ACTIVE",
              "STALE_TASK") for f in r["flags"])]
    changes = []
    for key, label in (("state_changes", "state"), ("experiments_completed", "experiment"), ("new_assignments", "assignment"),
                       ("blockers_added", "blocker+"), ("blockers_cleared", "blocker-"), ("new_seats", "new seat"),
                       ("new_anomalies", "anomaly")):
        for x in (d.get(key) or [])[:8]:
            changes.append("{}: {}".format(label, x))
    hdr = ["Agent", "Role", "State", "Last active", "Last experiment", "Current / last task", "Engine / system", "Last commit"]

    def cells(r):
        return [r["seat"], _short(r["role"], 34), r["state"] + ("" if r["active"] == "No" else " ({})".format(r["active"])),
                "{} ({})".format((r["last_active"] or "never")[:16].replace("T", " "), r["age"]),
                _short(r["exp"], 70), _short(r["task"], 90), _short(r["engine"], 40), _short(r["commit"], 70)]

    md = ["## Fleet census (Achilles)", "",
          "Generated {} from origin/main {}. Seats {}: {}. Active within 24h: {}. Experiments 24h: {}. Commits 24h: {}.".format(
              snap["generated_at_utc"], (snap.get("base_sha") or "")[:10], s["seats_total"], counts, s["active_24h"],
              s["experiments_24h"], s["commits_24h"]), ""]
    md += ["**Changes since previous census:**"] + (["- " + c for c in changes] or ["- none"]) + [""]
    md += ["**Needs attention ({}):**".format(len(attention))] + (
        ["- {} {}: {}".format(r["seat"], r["state"], ", ".join(r["flags"]) or r["blocker"]) for r in attention[:20]] or ["- none"]) + [""]
    md += ["| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
    for r in rows:
        md.append("| " + " | ".join(c.replace("|", "/") for c in cells(r)) + " |")
    md += ["", "Full census, evidence and engine map: " + PAGES_URL]

    h = ['<hr style="border:none;border-top:1px solid #ccc;margin:24px 0">',
         '<h2 style="color:#222;border-bottom:1px solid #eee;padding-bottom:4px">Fleet census (Achilles)</h2>',
         '<p style="font-size:14px;color:#333">Generated <b>{}</b> from origin/main <code>{}</code>. Seats {}: {}. '
         'Active within 24h: {}. Experiments 24h: {}. Commits 24h: {}.</p>'.format(
             _esc(snap["generated_at_utc"]), _esc((snap.get("base_sha") or "")[:10]), s["seats_total"], _esc(counts),
             s["active_24h"], s["experiments_24h"], s["commits_24h"]),
         '<p style="font-size:13px;margin:6px 0"><b>Changes since previous census:</b></p><ul style="font-size:12px;margin:2px 0 8px 0">'
         + ("".join("<li>{}</li>".format(_esc(c)) for c in changes) or "<li>none</li>") + "</ul>",
         '<p style="font-size:13px;margin:6px 0;color:#a02020"><b>Needs attention ({}):</b></p><ul style="font-size:12px;margin:2px 0 8px 0">'.format(len(attention))
         + ("".join("<li>{} {}: {}</li>".format(_esc(r["seat"]), _esc(r["state"]), _esc(", ".join(r["flags"]) or r["blocker"])) for r in attention[:20]) or "<li>none</li>") + "</ul>",
         '<table border="1" cellpadding="3" cellspacing="0" style="border-collapse:collapse;font-size:11px;border-color:#ddd">'
         '<tr bgcolor="#f2f2f2">' + "".join("<th align=left>{}</th>".format(_esc(x)) for x in hdr) + "</tr>"]
    for r in rows:
        h.append("<tr valign=top>" + "".join("<td>{}</td>".format(_esc(c)) for c in cells(r)) + "</tr>")
    h.append('</table><p style="font-size:13px">Full census, evidence and engine map: <a href="{0}">{0}</a></p>'.format(PAGES_URL))
    return {"schema": "prometheus.fleet_census_email.v1", "generated_at_utc": snap["generated_at_utc"],
            "base_sha": snap.get("base_sha"), "rows": len(rows), "page_url": PAGES_URL,
            "markdown": "\n".join(md), "html": "\n".join(h)}


def markdown_summary(snap) -> str:
    """docs/fleet/FLEET_CENSUS.md: a plain compatibility artifact for tools that read markdown."""
    return email_block(snap)["markdown"] + "\n"
