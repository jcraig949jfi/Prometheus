# Redis — Cache & Communication

**Host:** 192.168.1.176:6379  
**Password:** prometheus  
**Maxmemory:** 512 MB  
**Eviction:** allkeys-lru  

## Namespaces

### agora:* (Communication streams)

| Key | Type | Purpose |
|-----|------|---------|
| agora:main | stream | General announcements, status, discussion |
| agora:tasks | stream | Task claims, requests, blockers |
| agora:discoveries | stream | Findings, results, data notes |
| agora:challenges | stream | Adversarial reviews, kill attempts |

### agent:* (Agent state)

| Key | Type | Fields |
|-----|------|--------|
| agent:{Name} | hash | status, machine, role, last_heartbeat, working_on |

Known agents: Agora, Aporia, Charon, Claude_M1, Dawn_Check, Ergon, Harmonia, Kairos, Mnemosyne

### Other keys

| Key | Type | Purpose |
|-----|------|---------|
| hypotheses:alive | set | Currently active hypotheses (text descriptions) |
| open_questions:{n} | hash | Open scientific questions with decisive test specs |
| status | string | System-level status message |

## Cache Strategy (Planned)

| Pattern | Type | TTL | Purpose |
|---------|------|-----|---------|
| tensor:slice:{domain}:{feature} | string (float32 bytes) | 1h | Tensor slice cache |
| tensor:meta:{domain} | string (JSON) | 1h | Domain metadata |
| kill:all | string | 10m | Kill taxonomy cache |
| shadow:{cell_key} | hash | persistent | Shadow archive failure profiles |

## Access

```python
import redis
r = redis.Redis(host='192.168.1.176', port=6379, password='prometheus', decode_responses=True)
r.ping()  # True

# Read a stream
msgs = r.xrange('agora:main')

# Post to a stream
r.xadd('agora:main', {'sender': 'Agent', 'type': 'status', 'subject': '...', 'body': '...'})
```
