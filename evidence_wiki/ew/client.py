"""Evidence Wiki client — the semantic layer the `evidence-wiki` skill uses.

Hides REST mechanics (charter A10). Reads config for the service address;
EW_SERVICE_URL overrides (e.g. http://192.168.1.202:8377 from M2/M3/M4).
Every write carries machine + agent identity and an idempotency key.
"""
import json
import os
import socket
import uuid
from pathlib import Path

import requests

CFG = json.loads((Path(__file__).resolve().parent.parent / "config.json")
                 .read_text(encoding="utf-8"))


class EvidenceWiki:
    def __init__(self, base=None, machine=None, agent="unnamed-agent"):
        self.base = (base or os.environ.get("EW_SERVICE_URL")
                     or f"http://localhost:{CFG['port']}").rstrip("/")
        self.machine = machine or os.environ.get("PROMETHEUS_MACHINE",
                                                 socket.gethostname())
        self.agent = agent
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": f"Bearer {CFG['auth_token']}",
            "X-Prometheus-Machine": self.machine,
            "X-Prometheus-Agent": self.agent,
        })

    def _get(self, path, **params):
        r = self.s.get(f"{self.base}/api/v1/{path}", params=params, timeout=60)
        r.raise_for_status()
        return r.json()

    def _post(self, path, body):
        body.setdefault("idempotency_key", str(uuid.uuid4()))
        r = self.s.post(f"{self.base}/api/v1/{path}", json=body, timeout=120)
        if r.status_code == 422:
            raise ValueError(f"rejected: {r.json()['detail']}")
        r.raise_for_status()
        return r.json()

    # reads
    def search_evidence(self, text, mode="hybrid", k=10, status=None):
        return self._get("search", q=text, mode=mode, k=k,
                         **({"status": status} if status else {}))

    def get_claim(self, claim_id):
        return self._get(f"claims/{claim_id}")

    def get_counterevidence(self, claim_id):
        return self._get(f"counterevidence/{claim_id}")

    def related_findings(self, claim_id, k=10):
        return self._get(f"related/{claim_id}", k=k)

    def contradictions(self, claim_id=None):
        return self._get(f"contradictions/{claim_id}" if claim_id
                         else "contradictions")

    def dependencies(self, claim_id):
        return self._get(f"dependencies/{claim_id}")

    def provenance(self, object_id):
        return self._get(f"provenance/{object_id}")

    def find_consumers(self):
        return self._get("consumers")

    def find_gaps(self):
        return self._get("hypotheses")

    def freshness(self):
        return self._get("version")

    # writes (staged; provenance required by the server)
    def register_packet(self, uri, kind, git_commit=None):
        return self._post("packets", {"uri": uri, "kind": kind,
                                      "git_commit": git_commit})

    def register_experiment(self, agent, project, title, substrate=None,
                            packet_id=None, git_commit=None, run_ref=None):
        return self._post("experiments", locals_clean(locals()))

    def submit_claim(self, text_canonical, status, packet_id=None,
                     experiment_id=None, source_span=None, source_wording=None,
                     claim_ceiling=None, agent=None,
                     creation_method="MODEL_EXTRACTED",
                     write_stage="SUBMITTED"):
        return self._post("claims", locals_clean(locals()))

    def submit_evidence(self, packet_id, source_quote, evidence_type,
                        claim_id=None, verdict_source=None,
                        outcome_canonical=None, metric_text=None, gate=None,
                        negative=False, substrate=None, source_span=None,
                        experiment_id=None, agent=None,
                        write_stage="SUBMITTED"):
        return self._post("evidence", locals_clean(locals()))

    def submit_relation(self, src_id, relation_type, dst_id,
                        epistemic_class="INFERRED",
                        creation_method="MODEL_EXTRACTED", src_type="claim",
                        dst_type="claim", rationale=None, confidence=None,
                        packet_id=None, source_span=None):
        return self._post("relations", locals_clean(locals()))

    def register_failure(self, packet_id, source_quote, claim_id=None,
                         substrate=None, source_span=None, agent=None,
                         metric_text=None):
        return self.submit_evidence(packet_id, source_quote, "FAILURE",
                                    claim_id=claim_id, negative=True,
                                    outcome_canonical="REFUTED",
                                    substrate=substrate, source_span=source_span,
                                    agent=agent, metric_text=metric_text)

    def query_tensor(self, op, **body):
        return self._post(f"tensor/{op}", body)


def locals_clean(d):
    return {k: v for k, v in d.items() if k != "self" and v is not None}
