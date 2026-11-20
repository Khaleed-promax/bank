import f_database
import f_operations


def print_transactions(rows):
    if not rows:
        print("\nNo transactions found matching your criteria.")
        return

    print(f"\n{'ID':<4} | {'Date':<10} | {'Type':<8} | {'Category':<15} | {'Amount':>10} | Description")
    print("-" * 75)
    for r_id, date, t_type, category, amount, desc in rows:
        print(f"{r_id:<4} | {date:<10} | {t_type:<8} | {category:<15} | ${amount:>9.2f} | {desc}")


def print_categories():
    categories = f_operations.list_categories()
    if not categories:
        print("\nNo categories saved yet.")
        return False

    print("\nSaved Categories:")
    for cat_id, name, c_type in categories:
        print(f"  [{cat_id}] {name} ({c_type})")
    return True


def main():
    f_database.init_db()

    while True:
        print("\n=== Personal Finance Tracker ===")
        print("1. Add Transaction")
        print("2. List All Transactions")
        print("3. Filter / Search Transactions")
        print("4. View Income & Expense Totals")
        print("5. View Categories")
        print("6. Merge Categories")
        print("7. Set Monthly Category Budget")
        print("8. Import Transactions from CSV")
        print("9. Category Spending Chart (ASCII)")
        print("0. Exit")

        choice = input("\nSelect an option (0-9): ").strip()

        if choice == "1":
            try:
                t_type = input("Type (income/expense): ").strip().lower()
                if t_type not in ("income", "expense"):
                    print("Invalid type. Must be 'income' or 'expense'.")
                    continue
                category_name = input("Category (e.g., Salary, Food, Rent): ").strip()
                if not category_name:
                    print("Category cannot be empty.")
                    continue
                amount = float(input("Amount: "))
                desc = input("Description: ").strip()
                date = input("Date (YYYY-MM-DD) [Leave blank for today]: ").strip() or None

                warning = f_operations.add_transaction(amount, t_type, category_name, desc, date)
                print("Transaction added successfully!")
                if warning:
                    print(warning)
            except ValueError:
                print("Invalid input. Please enter a numeric value for amount.")

        elif choice == "2":
            rows = f_operations.list_transactions()
            print_transactions(rows)

        elif choice == "3":
            print("\nLeave any filter blank to skip it:")
            keyword = input("Search description keyword: ").strip() or None
            t_type = input("Filter by type (income/expense): ").strip() or None
            category_name = input("Filter by category name: ").strip() or None
            start_date = input("Start Date (YYYY-MM-DD): ").strip() or None
            end_date = input("End Date (YYYY-MM-DD): ").strip() or None

            rows = f_operations.list_transactions(t_type, category_name, start_date, end_date, keyword)
            print_transactions(rows)

        elif choice == "4":
            summary = f_operations.get_financial_summary()
            print("\n=== Financial Summary ===")
            print(f"Total Income:  ${summary['income']:>10.2f}")
            print(f"Total Expense: ${summary['expense']:>10.2f}")
            print("-" * 25)
            print(f"Net Balance:   ${summary['net_balance']:>10.2f}")

        elif choice == "5":
            print_categories()

        elif choice == "6":
            if not print_categories():
                continue
            try:
                source_id = int(input("\nEnter ID of category to remove (e.g., 3): "))
                target_id = int(input("Enter ID of category to merge into (e.g., 2): "))
                if source_id == target_id:
                    print("Cannot merge a category into itself.")
                    continue
                f_operations.merge_categories(source_id, target_id)
                print("Categories merged successfully!")
            except ValueError:
                print("Please enter valid numeric IDs.")

        elif choice == "7":
            try:
                category_name = input("Expense category name (e.g., Groceries): ").strip()
                if not category_name:
                    print("Category cannot be empty.")
                    continue
                limit = float(input("Monthly budget limit ($): "))
                msg = f_operations.set_category_budget(category_name, limit)
                print(msg)
            except ValueError as e:
                print(f"Invalid input: {e}")

        elif choice == "8":
            filepath = input("Path to CSV file (e.g., sample.csv): ").strip()
            try:
                imported, errors = f_operations.import_transactions_from_csv(filepath)
                print(f"\nImported {imported} transaction(s) successfully.")
                for err in errors:
                    print(f"  Skipped -> {err}")
            except FileNotFoundError:
                print("File not found. Please check the path and try again.")

        elif choice == "9":
            month = input("Filter by month (YYYY-MM) [Leave blank for all time]: ").strip() or None
            print("\n=== Category Spending Summary ===")
            print(f_operations.build_category_ascii_chart(month))

        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 0-9.")


if __name__ == "__main__":
    main()
