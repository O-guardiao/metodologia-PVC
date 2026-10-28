#!/usr/bin/env python3
"""Synthetic shop business rules and real durable persistence; not production code."""
from contextlib import closing
from pathlib import Path
import re
import sqlite3

UNIT_PRICE_CENTS = 300


class OrderError(ValueError):
    """A rejected business request, not successful partial completion."""


def order_values(order_id, quantity):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', order_id):
        raise OrderError('order_id must use 1..64 letters, digits, underscores or hyphens')
    if not 1 <= quantity <= 1000:
        raise OrderError('quantity must be between 1 and 1000')
    return {'order_id': order_id, 'quantity': quantity,
            'unit_price_cents': UNIT_PRICE_CENTS,
            'total_cents': quantity * UNIT_PRICE_CENTS}


def create_order(db, order_id, quantity):
    order = order_values(order_id, quantity)  # Reject before touching persistence.
    with closing(sqlite3.connect(db)) as connection, connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents >= 0),
            total_cents INTEGER NOT NULL CHECK(total_cents >= 0))''')
        try:
            connection.execute('INSERT INTO orders VALUES (?, ?, ?, ?)', tuple(order.values()))
        except sqlite3.IntegrityError as exc:
            raise OrderError('order_id already exists; existing order preserved') from exc
    return order


def show_order(db, order_id):
    # Read-only URI: a miss cannot silently initialize an empty database.
    uri = Path(db).resolve().as_uri() + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        row = connection.execute('SELECT order_id, quantity, unit_price_cents, total_cents '
                                 'FROM orders WHERE order_id = ?', (order_id,)).fetchone()
    if row is None:
        raise OrderError('order not found')
    return dict(zip(('order_id', 'quantity', 'unit_price_cents', 'total_cents'), row))
