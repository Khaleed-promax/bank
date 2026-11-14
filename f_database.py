import sqlite3

DB_NAME = "finance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    conn.commit()
    conn.close()

def get_or_create_category(cursor, name, trans_type):
    clean_name = name.strip().title()
    clean_type = trans_type.strip().lower()

    cursor.execute("SELECT id FROM categories WHERE name = ?", (clean_name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        "INSERT INTO categories (name, type) VALUES (?, ?)",
        (clean_name, clean_type)
    )
    return cursor.lastrowid

def add_transaction(date, amount, category_name, trans_type, description=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    category_id = get_or_create_category(cursor, category_name, trans_type)

    cursor.execute("""
        INSERT INTO transactions (date, amount, description, category_id)
        VALUES (?, ?, ?, ?)
    """, (date, amount, description.strip(), category_id))

    conn.commit()
    conn.close()


def get_transactions(category_name=None, month=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
        SELECT t.id, t.date, c.type, c.name, t.amount, t.description
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE 1=1
    """
    params = []

    if category_name:
        query += " AND LOWER(c.name) = LOWER(?)"
        params.append(category_name.strip())

    if month:
        query += " AND strftime('%Y-%m', t.date) = ?"
        params.append(month.strip())

    query += " ORDER BY t.date DESC, t.id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()

    print("--- All Transactions ---")
    for row in get_transactions():
        print(row)

    print("\n--- Groceries Only ---")
    for row in get_transactions(category_name="Groceries"):
        print(row)

    print("\n--- November 2026 Only ---")
    for row in get_transactions(month="2026-11"):
        print(row)
