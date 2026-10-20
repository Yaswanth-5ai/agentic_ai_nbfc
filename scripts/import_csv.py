import sqlite3

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "nbfc.db"


def check_database():

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        tables = ["customers", "loans", "payments"]

        for table in tables:

            rows = connection.execute(
                f"SELECT * FROM {table}"
            ).fetchall()

            print(f"\n{table.upper()}: {len(rows)} records")

            for row in rows:
                print(dict(row))

        # Verify the relationship between customers and loans.
        result = connection.execute(
            """
            SELECT
                c.customer_name,
                l.loan_id,
                l.loan_type,
                l.outstanding_amount
            FROM customers AS c
            JOIN loans AS l
                ON c.customer_id = l.customer_id
            ORDER BY c.customer_id, l.loan_id
            """
        ).fetchall()

        print("\nCUSTOMER LOAN SUMMARY:")

        for row in result:
            print(dict(row))

        # Verify the relationship between loans and payments.
        payment_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM payments AS p
            JOIN loans AS l
                ON p.loan_id = l.loan_id
            """
        ).fetchone()[0]

        print(f"\nPayments linked to loans: {payment_count}")

    finally:
        connection.close()


if __name__ == "__main__":
    check_database()

