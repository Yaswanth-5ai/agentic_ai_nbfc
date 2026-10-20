import sqlite3

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "data" / "nbfc.db"


def get_db_connection():
    """Create a connection to the SQLite database."""

    connection = sqlite3.connect(DATABASE_PATH)

    # Access database columns by name.
    connection.row_factory = sqlite3.Row

    # Enforce foreign-key constraints for this connection.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def get_outstanding_balance(customer_id: str) -> dict:
    """Retrieve all outstanding loan balances for a customer."""

    with get_db_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                loan_id,
                loan_type,
                outstanding_amount
            FROM loans
            WHERE customer_id = ?
              AND loan_status = 'ACTIVE'
            ORDER BY loan_id
            """,
            (customer_id,),
        ).fetchall()

    if not rows:
        return {
            "success": False,
            "error": "No active loans found for this customer.",
        }

    loans = [
        {
            "loan_id": row["loan_id"],
            "loan_type": row["loan_type"],
            "outstanding_amount": row["outstanding_amount"],
            "currency": "INR",
        }
        for row in rows
    ]

    return {
        "success": True,
        "customer_id": customer_id,
        "loans": loans,
        "loan_count": len(loans),
        "total_outstanding_amount": sum(
            loan["outstanding_amount"] for loan in loans
        ),
        "currency": "INR",
    }


def get_emi_details(customer_id: str) -> dict:
    """Retrieve EMI details for a customer's active loans."""

    with get_db_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                loan_id,
                loan_type,
                emi_amount,
                next_emi_date
            FROM loans
            WHERE customer_id = ?
              AND loan_status = 'ACTIVE'
            ORDER BY next_emi_date, loan_id
            """,
            (customer_id,),
        ).fetchall()

    if not rows:
        return {
            "success": False,
            "error": "No active loans found for this customer.",
        }

    return {
        "success": True,
        "emi_details": [
            {
                "loan_id": row["loan_id"],
                "loan_type": row["loan_type"],
                "emi_amount": row["emi_amount"],
                "next_emi_date": row["next_emi_date"],
                "currency": "INR",
            }
            for row in rows
        ],
    }


def get_payment_history(
    customer_id: str,
    limit: int = 5,
) -> dict:
    """Retrieve recent payments across a customer's loans."""

    if type(limit) is not int or not 1 <= limit <= 20:
        return {
            "success": False,
            "error": "Limit must be an integer between 1 and 20.",
        }

    with get_db_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                p.payment_id,
                p.loan_id,
                l.loan_type,
                p.payment_date,
                p.amount,
                p.status
            FROM payments AS p
            JOIN loans AS l
                ON p.loan_id = l.loan_id
            WHERE l.customer_id = ?
            ORDER BY p.payment_date DESC, p.payment_id DESC
            LIMIT ?
            """,
            (customer_id, limit),
        ).fetchall()

    return {
        "success": True,
        "customer_id": customer_id,
        "payments": [
            {
                "payment_id": row["payment_id"],
                "loan_id": row["loan_id"],
                "loan_type": row["loan_type"],
                "payment_date": row["payment_date"],
                "amount": row["amount"],
                "status": row["status"],
            }
            for row in rows
        ],
    }