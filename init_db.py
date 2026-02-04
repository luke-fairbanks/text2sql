import os
import psycopg2
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TIMESCALE_SERVICE_URL = os.environ.get("TIMESCALE_SERVICE_URL")
if not TIMESCALE_SERVICE_URL:
    print("Error: TIMESCALE_SERVICE_URL environment variable is not set.")
    exit(1)

conn = psycopg2.connect(dsn=TIMESCALE_SERVICE_URL)
cursor = conn.cursor()

# Enable foreign key support (PostgreSQL enforces this by default)
# cursor.execute("PRAGMA foreign_keys = ON;")

# --- SQL Schema Definition ---
schema_sql = """
DROP TABLE IF EXISTS restaurant_table, customer, staff, reservation, menu_category, menu_item, restaurant_order, order_item, shift, payment CASCADE;

CREATE TABLE restaurant_table (
    table_id INTEGER PRIMARY KEY,
    table_number INTEGER UNIQUE NOT NULL,
    seats INTEGER NOT NULL,
    location TEXT
);

CREATE TABLE customer (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT UNIQUE,
    email TEXT UNIQUE,
    loyalty_points INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE staff (
    staff_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    hire_date TEXT,
    hourly_rate NUMERIC
);

CREATE TABLE reservation (
    reservation_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    table_id INTEGER NOT NULL,
    reserved_at TEXT NOT NULL,   -- ISO string like '2026-02-01 18:30'
    party_size INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Booked',
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (table_id) REFERENCES restaurant_table(table_id)
);

CREATE TABLE menu_category (
    category_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE menu_item (
    item_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category_id TEXT NOT NULL,
    price NUMERIC NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1, -- 1=true, 0=false
    FOREIGN KEY (category_id) REFERENCES menu_category(category_id)
);

CREATE TABLE restaurant_order (
    order_id TEXT PRIMARY KEY,
    table_id INTEGER,                  -- can be NULL for takeout
    customer_id TEXT,                  -- can be NULL for walk-in
    staff_id TEXT,                     -- server/cashier
    order_type TEXT NOT NULL,          -- 'DineIn' | 'Takeout'
    order_time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open',
    FOREIGN KEY (table_id) REFERENCES restaurant_table(table_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);

CREATE TABLE order_item (
    order_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC NOT NULL,       -- snapshot price at time of order
    special_instructions TEXT,
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES restaurant_order(order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_item(item_id)
);

CREATE TABLE shift (
    shift_id TEXT PRIMARY KEY,
    staff_id TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);

CREATE TABLE payment (
    payment_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    method TEXT NOT NULL,              -- 'Card' | 'Cash' | 'GiftCard'
    paid_at TEXT NOT NULL,
    tip NUMERIC NOT NULL DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES restaurant_order(order_id)
);
"""

# --- Populate with Mock Data ---
data_sql = """
-- Tables
INSERT INTO restaurant_table VALUES (1, 1, 2, 'Window');
INSERT INTO restaurant_table VALUES (2, 2, 4, 'Center');
INSERT INTO restaurant_table VALUES (3, 3, 4, 'Patio');
INSERT INTO restaurant_table VALUES (4, 4, 6, 'Booth');
INSERT INTO restaurant_table VALUES (5, 10, 8, 'Private');

-- Customers
INSERT INTO customer VALUES ('C001', 'Ava Johnson', '555-0101', 'ava@example.com', 120);
INSERT INTO customer VALUES ('C002', 'Noah Kim', '555-0102', 'noah@example.com', 45);
INSERT INTO customer VALUES ('C003', 'Mia Patel', '555-0103', 'mia@example.com', 300);
INSERT INTO customer VALUES ('C004', 'Ethan Brown', '555-0104', 'ethan@example.com', 0);
INSERT INTO customer VALUES ('C005', 'Sofia Garcia', '555-0105', 'sofia@example.com', 80);

-- Staff
INSERT INTO staff VALUES ('S001', 'Jordan Lee', 'Server', '2024-06-10', 12.50);
INSERT INTO staff VALUES ('S002', 'Casey Nguyen', 'Chef', '2023-03-20', 22.00);
INSERT INTO staff VALUES ('S003', 'Riley Smith', 'Host', '2025-01-05', 11.00);
INSERT INTO staff VALUES ('S004', 'Morgan Davis', 'Server', '2024-09-01', 13.25);
INSERT INTO staff VALUES ('S005', 'Taylor Chen', 'Manager', '2022-11-15', 28.00);

-- Shifts
INSERT INTO shift VALUES ('SH001', 'S003', '2026-02-01 16:00', '2026-02-01 22:00');
INSERT INTO shift VALUES ('SH002', 'S001', '2026-02-01 17:00', '2026-02-01 23:00');
INSERT INTO shift VALUES ('SH003', 'S002', '2026-02-01 15:00', '2026-02-01 23:00');
INSERT INTO shift VALUES ('SH004', 'S004', '2026-02-02 10:00', '2026-02-02 16:00');

-- Menu Categories
INSERT INTO menu_category VALUES ('CAT1', 'Starters');
INSERT INTO menu_category VALUES ('CAT2', 'Mains');
INSERT INTO menu_category VALUES ('CAT3', 'Desserts');
INSERT INTO menu_category VALUES ('CAT4', 'Drinks');

-- Menu Items
INSERT INTO menu_item VALUES ('I001', 'Garlic Bread', 'CAT1', 6.50, 1);
INSERT INTO menu_item VALUES ('I002', 'Caesar Salad', 'CAT1', 8.00, 1);
INSERT INTO menu_item VALUES ('I003', 'Cheeseburger', 'CAT2', 14.50, 1);
INSERT INTO menu_item VALUES ('I004', 'Margherita Pizza', 'CAT2', 16.00, 1);
INSERT INTO menu_item VALUES ('I005', 'Salmon Bowl', 'CAT2', 18.75, 1);
INSERT INTO menu_item VALUES ('I006', 'Chocolate Cake', 'CAT3', 7.25, 1);
INSERT INTO menu_item VALUES ('I007', 'Iced Tea', 'CAT4', 3.50, 1);
INSERT INTO menu_item VALUES ('I008', 'Sparkling Water', 'CAT4', 2.75, 1);

-- Reservations
INSERT INTO reservation VALUES ('R001', 'C001', 2, '2026-02-01 18:30', 4, 'Booked', 'Birthday');
INSERT INTO reservation VALUES ('R002', 'C003', 4, '2026-02-01 19:00', 6, 'Seated', NULL);
INSERT INTO reservation VALUES ('R003', 'C002', 1, '2026-02-02 12:15', 2, 'Cancelled', 'Running late');
INSERT INTO reservation VALUES ('R004', 'C005', 3, '2026-02-02 18:00', 4, 'Booked', 'Patio preferred');

-- Orders (some dine-in, some takeout)
INSERT INTO restaurant_order VALUES ('O1001', 2, 'C001', 'S001', 'DineIn', '2026-02-01 18:45', 'Closed');
INSERT INTO restaurant_order VALUES ('O1002', 4, 'C003', 'S004', 'DineIn', '2026-02-01 19:10', 'Open');
INSERT INTO restaurant_order VALUES ('O1003', NULL, 'C002', 'S003', 'Takeout', '2026-02-02 12:05', 'Closed');
INSERT INTO restaurant_order VALUES ('O1004', 1, NULL, 'S001', 'DineIn', '2026-02-02 13:00', 'Closed');

-- Order Items (unit_price snapshot)
INSERT INTO order_item VALUES ('O1001', 'I002', 1, 8.00, 'No croutons');
INSERT INTO order_item VALUES ('O1001', 'I004', 1, 16.00, NULL);
INSERT INTO order_item VALUES ('O1001', 'I007', 2, 3.50, 'Less ice');

INSERT INTO order_item VALUES ('O1002', 'I001', 1, 6.50, NULL);
INSERT INTO order_item VALUES ('O1002', 'I005', 2, 18.75, 'Extra sauce');
INSERT INTO order_item VALUES ('O1002', 'I008', 2, 2.75, NULL);

INSERT INTO order_item VALUES ('O1003', 'I003', 2, 14.50, 'No onions');
INSERT INTO order_item VALUES ('O1003', 'I006', 1, 7.25, NULL);

INSERT INTO order_item VALUES ('O1004', 'I004', 1, 16.00, 'Well done');
INSERT INTO order_item VALUES ('O1004', 'I007', 1, 3.50, NULL);

-- Payments
INSERT INTO payment VALUES ('P9001', 'O1001', 34.50, 'Card', '2026-02-01 20:05', 6.00);
INSERT INTO payment VALUES ('P9002', 'O1003', 36.25, 'Cash', '2026-02-02 12:20', 0.00);
INSERT INTO payment VALUES ('P9003', 'O1004', 19.50, 'Card', '2026-02-02 13:45', 3.00);
"""

cursor.execute(schema_sql)
cursor.execute(data_sql)
conn.commit()

print("✅ Restaurant Mock Database Created")

# (Optional) quick sanity check:
cursor.execute("""
SELECT o.order_id, o.order_type, c.name AS customer, s.name AS staff, o.status
FROM restaurant_order o
LEFT JOIN customer c ON c.customer_id = o.customer_id
LEFT JOIN staff s ON s.staff_id = o.staff_id
ORDER BY o.order_id;
""")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()
