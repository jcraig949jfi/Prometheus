# Prometheus Landscape Tensor Viewer

Web-based heatmap visualization of the invariance tensor (features x projections).
Reads live from Redis — auto-refreshes every 5 seconds when the tensor is updated.

## Launch

```bash
cd cartography/viewer
python server.py              # default port 8777
python server.py --port 9000  # custom port
```

Open: http://localhost:8777/map

Works from M1 or M2 — both hit the same Redis at 192.168.1.176:6379.

## What You See

- **Heatmap**: rows = features (F001-F045), columns = projections (P001-P104)
  - Dark green (+2): strong resolve, validated under permutation-break null
  - Light green (+1): projection resolves the feature
  - Grey (0): untested. Slightly blue tint = "hot" (many neighbors are +1/+2)
  - Orange (-1): tested, feature not resolved
  - Red (-2): projection provably collapses the feature (known artifact)

- **Hover**: shows F-id, P-id, verdict, feature label + tier, projection label + type

- **Click row/column header**: highlights non-zero cells in that row/column

- **Gap banner**: flags missing projections (P028 Katz-Sarnak etc.) that are in the
  coordinate_system_catalog but not yet in the tensor. Gap-filler's lane.

- **Edge graphs**: force-directed d3 graphs showing feature-to-feature and
  projection-to-projection relationships (supersedes, supports, contradicts, etc.)
  Color-coded by relation type.

- **Auto-refresh**: polls /api/updates every 5s. Green dot = live; yellow = stale.

## API

- `GET /api/state` — full tensor state (features, projections, matrix, metadata, edges)
- `GET /api/updates` — dims + recent change events (lightweight, for polling)

## Requirements

- Python 3.8+
- redis (pip install redis)
- Redis running at 192.168.1.176:6379 (or set AGORA_REDIS_HOST env var)
- No Flask needed — uses stdlib http.server

## Author

Charon (Cartographer role), 2026-04-18
