#!/usr/bin/env bash
# CRASH/RESTART, deterministic: an isolated schema with identical DDL, so no
# other daemon can claim the item out from under the test. Nothing is
# manufactured -- the stranded row comes from a real SIGKILL of a real worker
# between mark_running and finalize.
cd /f/Prometheus/vivarium
export VIV_SCHEMA=viv_crash
export VIV_PEW_TOKEN="$(python -c "import json;print(json.load(open('../evidence_wiki/config.json'))['auth_token'])")"
export W="vivarium@crashtest"

echo "### setup"
python -c "
import sys; sys.path.insert(0,'.')
from viv import db, queue as q
c=db.connect(); db.apply_migrations(c, target_schema='viv_crash')
def spec(i):
    return {'spec_version':2,'world':{'seed_root':800000+i},
            'hypothesis':'crash/restart item %d'%i,'prediction':None,
            'work':{'kind':'evaluate_bitstring',
                    'payload':{'bits':format(i,'024b'),'length':24}},
            'outcome_rule':{'field':'solved','op':'==','value':False,
                            'if_true':'SURVIVED','if_false':'FALSIFIED',
                            'if_indeterminate':'INCONCLUSIVE'},
            'pew':None}
for i in range(3):
    print(' queued', q.enqueue(c, created_by='operator:crash-test',
          source_reason='crash/restart demonstration', experiment_spec=spec(i),
          request_key='crash2-%d'%i, schema='viv_crash'))
c.commit()
"

echo "### phase 1: run, then SIGKILL the instant a row is running"
python -u -m viv.cli --schema viv_crash run --interval 1 --worker-id "$W" > /tmp/crash2_d1.log 2>&1 &
DPID=$!
python - <<'PY'
import sys, time
sys.path.insert(0, ".")
from viv import db, queue as q
c = db.connect()
for _ in range(400):
    a = q.active(c, schema="viv_crash"); c.rollback()
    if a is not None and a["status"] == "running":
        print("  saw running:", a["experiment_id"], a["sfe_experiment_id"], flush=True); break
    time.sleep(0.03)
PY
kill -9 $DPID; wait $DPID 2>/dev/null
echo "  SIGKILL sent"; sleep 1
cat /tmp/crash2_d1.log | sed 's/^/  D1 /'

echo "### state after the crash"
python -c "
import sys,json; sys.path.insert(0,'.')
from viv import db, queue as q
c=db.connect(); cur=db.dict_cur(c)
cur.execute('''select experiment_id,status,started_at is not null crossed,sfe_experiment_id
                 from viv_crash.execution_attempts order by created_at''')
for r in cur.fetchall(): print('  ', dict(r))
"

echo "### phase 2: restart the SAME worker id -- it must REFUSE"
python -u -m viv.cli --schema viv_crash run --interval 1 --once --worker-id "$W" 2>&1 | sed 's/^/  D2 /'
echo "  exit=$?"

echo "### phase 3: operator releases the stranded row"
python -c "
import sys; sys.path.insert(0,'.')
from viv import db, queue as q
c=db.connect()
st=q.stranded(c, stale_after_s=0.0, schema='viv_crash')
for r in st:
    row=q.release_stranded(c, r['experiment_id'], actor='operator',
        reason='verified in SFE %s: work never completed, no observation' % r['sfe_experiment_id'],
        schema='viv_crash'); c.commit()
    print('  released', row['experiment_id'], '->', row['status'])
"

echo "### phase 4: restart -- it must resume and drain"
python -u -m viv.cli --schema viv_crash run --interval 1 --stop-when-idle --worker-id "$W" 2>&1 | sed 's/^/  D3 /'

echo "### final state"
python -c "
import sys; sys.path.insert(0,'.')
from viv import db, queue as q
c=db.connect(); cur=db.dict_cur(c)
cur.execute('''select status,count(*) n from viv_crash.research_experiment_queue group by 1 order by 1''')
for r in cur.fetchall(): print('  ', dict(r))
cur.execute('''select experiment_id,status,rejected_before_execution,failed_during_execution
                 from viv_crash.execution_attempts where status='failed' ''')
for r in cur.fetchall(): print('  failed row:', dict(r))
"
