import sqlite3
from datetime import datetime
import f_database

DB_NAME = f_database.DB_NAME


def get_connection():
    return sqlite3.connect(DB_NAME)


def add_transaction(amount: float, t_type: str, category_name: str, description: str = "", date: str = None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    f_database.add_transaction(date, amount, category_name, t_type, description)


def list_transactions(
    t_type: str = None,
    category_name: str = None,
    start_date: str = None,
    end_date: str = None,
    keyword: str = None,
):
    query = """
    SELECT t.id, t.date, c.type, c.name, t.amount, t.description
    FROM transactions t
    JOIN categories c ON t.category_id = c.id
    WHERE 1=1
    """
    params = []

    if t_type:
        query += " AND LOWER(c.type) = LOWER(?)"
        params.append(t_type.strip())
    if category_name:
        query += " AND LOWER(c.name) = LOWER(?)"
        params.append(category_name.strip())
    if start_date:
        query += " AND t.date >= ?"
        params.append(start_date.strip())
    if end_date:
        query += " AND t.date <= ?"
        params.append(end_date.strip())
    if keyword:
        query += " AND LOWER(t.description) LIKE LOWER(?)"
        params.append(f"%{keyword.strip()}%")

    query += " ORDER BY t.date DESC, t.id DESC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def list_categories():
    query = "SELECT id, name, type FROM categories ORDER BY type ASC, name ASC"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()


def merge_categories(source_id: int, target_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE transactions SET category_id = ? WHERE category_id = ?", (target_id, source_id))
        cursor.execute("DELETE FROM categories WHERE id = ?", (source_id,))
        conn.commit()


def get_financial_summary():
    query = """
    SELECT LOWER(c.type), SUM(t.amount)
    FROM transactions t
    JOIN categories c ON t.category_id = c.id
    GROUP BY LOWER(c.type)
    """
    totals = {"income": 0.0, "expense": 0.0}

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        for t_type, total in cursor.fetchall():
            if t_type in totals and total is not None:
                totals[t_type] = total

    totals["net_balance"] = totals["income"] - totals["expense"]
    return totals
