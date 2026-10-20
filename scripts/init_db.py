import sqlite3

from pathlib import Path


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "nbfc.db"


def create_database():

    # Ensure the data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Connect to SQLite
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        # Enable foreign-key constraints
        connection.execute("PRAGMA foreign_keys = ON")

        with connection:

            # Create customers table
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    phone_number TEXT NOT NULL
                )
                """
            )

            # Create loans table
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS loans (
                    loan_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    loan_type TEXT NOT NULL,
                    principal_amount REAL NOT NULL,
                    outstanding_amount REAL NOT NULL,
                    emi_amount REAL NOT NULL,
                    next_emi_date TEXT NOT NULL,
                    loan_status TEXT NOT NULL,

                    FOREIGN KEY (customer_id)
                        REFERENCES customers(customer_id)
                )
                """
            )

            # Create payments table
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id TEXT PRIMARY KEY,
                    loan_id TEXT NOT NULL,
                    payment_date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL,

                    FOREIGN KEY (loan_id)
                        REFERENCES loans(loan_id)
                )
                """
            )

            # Create indexes for frequently queried columns
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_loans_customer_id
                ON loans(customer_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_payments_loan_date
                ON payments(loan_id, payment_date)
                """
            )

        print("Database and tables created successfully!")
        print(f"Database location: {DATABASE_PATH}")

    finally:
        connection.close()


if __name__ == "__main__":
    create_database()