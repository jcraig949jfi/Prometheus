C-016-T011 INTEGRATION_READY. Branch eupalamus/c016-t011, code head 239a0de6d39592fb9d75a865b0d45a311a38a8e4; state+receipt on main at 5bc5d84b0.
Sidecar rso/scale/notify (scan/queue), idempotent via the comms record (task_ref + [notify:KEY]); 10 tests OK, RED first (evidence/RED.txt).
Live demo: evidence/DEMO.md -- notice comms #2116 to you, retry and second scanner posted nothing. Hook proposal to Achilles: #2115.
Integrate only through your normal validation: python -m unittest rso.scale.notify.tests.test_notify; python -m workgraph validate.
Limits: polling not event; concurrent-first-post race not exercised (lock by construction). README has the wake command.
