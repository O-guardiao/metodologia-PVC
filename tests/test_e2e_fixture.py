"""Real browser journeys for an explicitly bounded synthetic local application.

Opt in with PVC_RUN_BROWSER_E2E=1. Missing infrastructure is skip/pending, never
an application acceptance pass. No network outside loopback and no mocked boundary.
"""
from contextlib import closing
import importlib.util
import json
import os
from pathlib import Path
import shutil
import selectors
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

APP = Path(__file__).resolve().parents[1] / 'examples/e2e_web/server.py'
BROWSER = shutil.which('chromium')
ENABLED = os.environ.get('PVC_RUN_BROWSER_E2E') == '1'
AVAILABLE = importlib.util.find_spec('playwright') is not None and BROWSER is not None


class HttpApplicationIntegration(unittest.TestCase):
    """Backend diagnosis only: this class does NOT verify the browser boundary."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pvc-http-integration-')
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'orders.sqlite3'
        self.server = subprocess.Popen([sys.executable, str(APP), '--db', str(self.db)],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop_server)
        with selectors.DefaultSelector() as ready:
            ready.register(self.server.stdout, selectors.EVENT_READ)
            if not ready.select(timeout=10):
                self.fail('Local server startup timeout')
            self.url = json.loads(self.server.stdout.readline())['url']

    def stop_server(self):
        self.server.terminate()
        try:
            self.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.server.kill()
            self.server.wait(timeout=5)
        self.server.stdout.close()
        self.server.stderr.close()

    def request(self, path, payload=None):
        request = Request(self.url + path, data=None if payload is None else json.dumps(payload).encode(),
                          headers={'Content-Type': 'application/json'})
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())

    def test_http_rules_storage_and_readback(self):
        status, created = self.request('/orders', {'order_id': 'one', 'quantity': 4})
        self.assertEqual(status, 201)
        self.assertEqual(created['order']['total_cents'], 1200)
        with closing(sqlite3.connect(self.db)) as connection:
            self.assertEqual(connection.execute('SELECT total_cents FROM orders').fetchall(), [(1200,)])
        self.assertEqual(self.request('/orders?id=one'), (200, created))

    def test_http_rejection_without_partial_write(self):
        for data in ({'order_id': 'invalid', 'quantity': -1}, {'order_id': 7, 'quantity': 1},
                     {'order_id': 'invalid', 'quantity': True}):
            self.assertEqual(self.request('/orders', data)[0], 400)
            self.assertFalse(self.db.exists())
        self.assertEqual(self.request('/orders?id=missing')[0], 404)
        self.assertFalse(self.db.exists())

    def test_http_duplicate_preserves_existing(self):
        _, first = self.request('/orders', {'order_id': 'unique', 'quantity': 2})
        self.assertEqual(self.request('/orders', {'order_id': 'unique', 'quantity': 8})[0], 400)
        self.assertEqual(self.request('/orders?id=unique'), (200, first))
        self.assertEqual(self.request('/not-found')[0], 404)


@unittest.skipUnless(ENABLED and AVAILABLE,
                     'Browser E2E not executed: set PVC_RUN_BROWSER_E2E=1 with existing playwright/chromium; acceptance pending')
class BrowserApplicationE2E(unittest.TestCase):
    def setUp(self):
        from playwright.sync_api import sync_playwright
        self.temp = tempfile.TemporaryDirectory(prefix='pvc-web-e2e-')
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'orders.sqlite3'
        self.server = subprocess.Popen([sys.executable, str(APP), '--db', str(self.db)],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop_server)
        with selectors.DefaultSelector() as ready:
            ready.register(self.server.stdout, selectors.EVENT_READ)
            if not ready.select(timeout=10):
                self.fail('Local fixture server did not start within 10 seconds')
            self.url = json.loads(self.server.stdout.readline())['url']
        self.playwright = sync_playwright().start()
        self.addCleanup(self.playwright.stop)
        self.browser = self.playwright.chromium.launch(executable_path=BROWSER, headless=True,
                                                       args=['--no-sandbox'])
        self.addCleanup(self.browser.close)
        self.page = self.browser.new_page()
        self.page.goto(self.url)

    def stop_server(self):
        self.server.terminate()
        try:
            self.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.server.kill()
            self.server.wait(timeout=5)
        self.server.stdout.close()
        self.server.stderr.close()

    def create(self, identifier, quantity):
        self.page.locator('#order-id').fill(identifier)
        self.page.locator('#quantity').fill(str(quantity))
        with self.page.expect_response(lambda response: response.url.endswith('/orders') and response.request.method == 'POST'):
            self.page.get_by_role('button', name='Create order').click()
        self.page.wait_for_function("document.querySelector('#result').textContent.length > 0")
        return json.loads(self.page.locator('#result').inner_text())

    def lookup(self, identifier):
        self.page.locator('#lookup-id').fill(identifier)
        with self.page.expect_response(lambda response: '/orders?id=' in response.url):
            self.page.get_by_role('button', name='Show order').click()
        self.page.wait_for_function("document.querySelector('#result').textContent.length > 0")
        return json.loads(self.page.locator('#result').inner_text())

    def rows(self):
        with closing(sqlite3.connect(self.db)) as connection:
            return connection.execute('SELECT order_id, quantity, unit_price_cents, total_cents '
                                      'FROM orders ORDER BY order_id').fetchall()

    def test_journey_ui_create_rules_database_and_fresh_browser_retrieval(self):
        created = self.create('purchase-1', 4)
        expected = {'order_id': 'purchase-1', 'quantity': 4, 'unit_price_cents': 300, 'total_cents': 1200}
        self.assertEqual(created, {'result': 'ok', 'order': expected})
        self.assertEqual(self.rows(), [('purchase-1', 4, 300, 1200)])
        self.page.close()
        self.page = self.browser.new_page()  # Fresh browser context, no application state reused.
        self.page.goto(self.url)
        self.assertEqual(self.lookup('purchase-1'), created)
        self.page.reload()
        self.assertEqual(self.lookup('purchase-1'), created)

    def test_journey_invalid_ui_request_has_no_partial_persistence(self):
        rejected = self.create('bad', -1)
        self.assertEqual(rejected['result'], 'rejected')
        self.assertIn('quantity', rejected['error'])
        self.assertFalse(self.db.exists())
        self.page.reload()
        self.assertEqual(self.lookup('bad')['result'], 'rejected')
        self.assertFalse(self.db.exists())

    def test_journey_duplicate_ui_request_preserves_original_durable_order(self):
        original = self.create('unique', 2)
        self.page.reload()
        rejected = self.create('unique', 9)
        self.assertEqual(rejected['result'], 'rejected')
        self.assertIn('already exists', rejected['error'])
        self.assertEqual(self.rows(), [('unique', 2, 300, 600)])
        self.page.reload()
        self.assertEqual(self.lookup('unique'), original)


if __name__ == '__main__':
    unittest.main()
