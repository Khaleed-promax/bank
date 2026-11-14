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

if __name__ == "__main__":
    init_db()
    add_transaction("2026-11-14", 1500.00, "Salary", "income", "November paycheck")
    add_transaction("2026-11-14", 45.50, "Groceries", "expense", "Weekly food shop")
    print("Sample transactions added!")
