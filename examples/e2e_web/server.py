#!/usr/bin/env python3
"""Loopback-only synthetic shop: real browser, HTTP, rules and SQLite boundaries."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs, urlparse

from shop import OrderError, create_order, show_order

PAGE = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Local E2E shop</title>
<h1>Synthetic local shop</h1>
<form id="create"><label>Order ID <input id="order-id" required></label>
<label>Quantity <input id="quantity" type="number" required></label>
<button type="submit">Create order</button></form>
<form id="lookup"><label>Find order <input id="lookup-id" required></label>
<button type="submit">Show order</button></form>
<pre id="result" role="status" aria-live="polite"></pre>
<script>
async function request(url, options) {
  document.querySelector('#result').textContent = '';
  const response = await fetch(url, options);
  const data = await response.json();
  document.querySelector('#result').textContent = JSON.stringify(data);
}
document.querySelector('#create').addEventListener('submit', async event => {
  event.preventDefault();
  await request('/orders', {method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify({order_id:document.querySelector('#order-id').value,
                         quantity:Number(document.querySelector('#quantity').value)})});
});
document.querySelector('#lookup').addEventListener('submit', async event => {
  event.preventDefault();
  await request('/orders?id=' + encodeURIComponent(document.querySelector('#lookup-id').value));
});
</script></html>'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # No request payloads/identifiers in test service logs.

    def reply(self, status, data):
        payload = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            payload = PAGE.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if parsed.path != '/orders':
            self.reply(404, {'result': 'rejected', 'error': 'not found'})
            return
        try:
            order_id = parse_qs(parsed.query).get('id', [''])[0]
            order = show_order(self.server.db, order_id)
            self.reply(200, {'result': 'ok', 'order': order})
        except (OrderError, sqlite3.Error):
            self.reply(404, {'result': 'rejected', 'error': 'order not found'})

    def do_POST(self):
        if self.path != '/orders':
            self.reply(404, {'result': 'rejected', 'error': 'not found'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 4096:
                raise OrderError('invalid request size')
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict) or not isinstance(data.get('order_id'), str) or type(data.get('quantity')) is not int:
                raise OrderError('order_id string and quantity integer required')
            order = create_order(self.server.db, data['order_id'], data['quantity'])
            self.reply(201, {'result': 'ok', 'order': order})
        except (OrderError, ValueError, sqlite3.Error) as exc:
            self.reply(400, {'result': 'rejected', 'error': str(exc)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.db = str(Path(args.db).resolve())
    print(json.dumps({'url': f'http://127.0.0.1:{server.server_port}'}), flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
