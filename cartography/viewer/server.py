"""
Prometheus Landscape Tensor Viewer — Charon Cartographer
========================================================
Thin JSON API over Redis tensor state. Serves a static HTML heatmap.
Launch: python server.py [--port 8777]
View:   http://localhost:8777/map
"""
import json
import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import redis

# ── Redis connection ──
REDIS_HOST = os.environ.get('AGORA_REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('AGORA_REDIS_PORT', '6379'))
REDIS_PASS = os.environ.get('AGORA_REDIS_PASSWORD', 'prometheus')

def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS,
                       decode_responses=True, socket_timeout=5)


def api_state():
    """Full tensor state as JSON for the frontend."""
    r = get_redis()

    dims = r.hgetall('tensor:dims')
    fs = r.lrange('tensor:features', 0, -1)
    ps = r.lrange('tensor:projections', 0, -1)
    cells = r.hgetall('tensor:cells')

    # Build matrix (list of lists)
    matrix = []
    for f in fs:
        row = []
        for p in ps:
            key = f'{f}:{p}'
            row.append(int(cells.get(key, 0)))
        matrix.append(row)

    # Feature metadata
    f_meta = {}
    for f in fs:
        raw = r.get(f'tensor:feature_meta:{f}')
        f_meta[f] = json.loads(raw) if raw else {'label': f}

    # Projection metadata
    p_meta = {}
    for p in ps:
        raw = r.get(f'tensor:projection_meta:{p}')
        p_meta[p] = json.loads(raw) if raw else {'label': p}

    # Edges
    fe_raw = r.get('tensor:feature_edges')
    pe_raw = r.get('tensor:projection_edges')

    # Recent updates
    updates = r.xrevrange('tensor:updates', count=20)
    update_list = [{'id': eid, **fields} for eid, fields in updates]

    return {
        'dims': dims,
        'features': fs,
        'projections': ps,
        'matrix': matrix,
        'feature_meta': f_meta,
        'projection_meta': p_meta,
        'feature_edges': json.loads(fe_raw) if fe_raw else [],
        'projection_edges': json.loads(pe_raw) if pe_raw else [],
        'updates': update_list,
    }


def api_updates():
    """Just dims + recent updates for polling."""
    r = get_redis()
    dims = r.hgetall('tensor:dims')
    updates = r.xrevrange('tensor:updates', count=5)
    update_list = [{'id': eid, **fields} for eid, fields in updates]
    return {'dims': dims, 'updates': update_list}


class TensorHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/state':
            self._json_response(api_state())
        elif path == '/api/updates':
            self._json_response(api_updates())
        elif path == '/map' or path == '/':
            self._serve_file('index.html', 'text/html')
        else:
            # Serve static files from viewer directory
            super().do_GET()

    def _json_response(self, data):
        body = json.dumps(data, default=str).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, filename, content_type):
        filepath = Path(__file__).parent / filename
        if filepath.exists():
            body = filepath.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, f'{filename} not found')

    def log_message(self, format, *args):
        pass  # Suppress request logging


def main():
    port = 8777
    if '--port' in sys.argv:
        port = int(sys.argv[sys.argv.index('--port') + 1])

    os.chdir(str(Path(__file__).parent))
    server = HTTPServer(('0.0.0.0', port), TensorHandler)
    print(f'Prometheus Landscape Viewer at http://localhost:{port}/map')
    print(f'Redis: {REDIS_HOST}:{REDIS_PORT}')
    print(f'API: /api/state (full), /api/updates (poll)')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down.')
        server.server_close()


if __name__ == '__main__':
    main()
