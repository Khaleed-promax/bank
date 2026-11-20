import csv
import sqlite3
from datetime import datetime
import f_database

DB_NAME = f_database.DB_NAME


def get_connection():
    return sqlite3.connect(DB_NAME)


def add_transaction(amount: float, t_type: str, category_name: str, description: str = "", date: str = None) -> str | None:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    f_database.add_transaction(date, amount, category_name, t_type, description)

    if t_type.strip().lower() == "expense":
        return check_overspend_warning(category_name, date)
    return None


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


# --- STRETCH FEATURE OPERATIONS ---

def set_category_budget(category_name: str, monthly_limit: float) -> str:
    if monthly_limit <= 0:
        raise ValueError("Monthly budget limit must be greater than 0.")
    f_database.set_category_budget(category_name, monthly_limit)
    return f"Monthly budget for '{category_name.strip().title()}' set to ${monthly_limit:.2f}."


def check_overspend_warning(category_name: str, date_str: str) -> str | None:
    month = date_str.strip()[:7]
    limit, spent = f_database.get_budget_status(category_name, month)
    if limit is not None and spent > limit:
        over = spent - limit
        return f"⚠️ OVERSPEND WARNING: '{category_name.strip().title()}' is ${over:.2f} over its ${limit:.2f} budget for {month}!"
    return None


def import_transactions_from_csv(filepath: str) -> tuple[int, list[str]]:
    """
    Imports transactions from a CSV file with headers:
    date,amount,category,type,description
    """
    imported = 0
    errors = []

    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, start=2):
            try:
                date = row["date"].strip()
                amount = float(row["amount"])
                category = row["category"].strip()
                t_type = row["type"].strip().lower()
                description = row.get("description", "").strip()

                if t_type not in ("income", "expense"):
                    raise ValueError(f"Invalid type '{t_type}' (must be 'income' or 'expense')")

                f_database.add_transaction(date, amount, category, t_type, description)
                imported += 1
            except (KeyError, ValueError) as e:
                errors.append(f"Row {line_num}: {e}")

    return imported, errors


def search_transactions(keyword: str):
    return list_transactions(keyword=keyword)


def build_category_ascii_chart(month: str = None, max_width: int = 30) -> str:
    rows = f_database.get_expense_summary_by_category(month)
    if not rows:
        return "No expenses found to chart."

    max_spend = max(total for _, total in rows)
    pad = max(len(name) for name, _ in rows)

    lines = []
    for name, total in rows:
        bar_len = int((total / max_spend) * max_width) if max_spend > 0 else 0
        bar = "#" * max(bar_len, 1)
        lines.append(f"{name.ljust(pad)} | {bar.ljust(max_width)} ${total:,.2f}")

    return "\n".join(lines)
