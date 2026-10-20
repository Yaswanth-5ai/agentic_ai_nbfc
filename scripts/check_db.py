import sqlite3

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "nbfc.db"


connection = sqlite3.connect(DATABASE_PATH)

try:
    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    ).fetchall()

    print("Tables in the database:")

    for table in tables:
        print(table[0])

finally:
    connection.close()