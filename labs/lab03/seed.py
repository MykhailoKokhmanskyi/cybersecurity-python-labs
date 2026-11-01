import json
import logging
import sqlite3
from contextlib import closing
from pathlib import Path

from labs.lab03.database import get_connection, initialize_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"


def seed_database() -> None:
    initialize_database()

    if not SEED_PATH.exists():
        logger.error(f"Seed file not found at {SEED_PATH}")
        return

    try:
        data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in seed file: {e}")
        return

    categories = data.get("categories", [])
    records = data.get("records", [])

    with closing(get_connection()) as conn:
        try:
            with conn:
                cursor = conn.execute("SELECT COUNT(*) FROM categories")
                cat_count = cursor.fetchone()[0]

                cursor = conn.execute("SELECT COUNT(*) FROM records")
                rec_count = cursor.fetchone()[0]

                if cat_count > 0 or rec_count > 0:
                    logger.info("Database is already seeded. No changes made.")
                    return

                for cat in categories:
                    conn.execute(
                        "INSERT INTO categories (id, name) VALUES (?, ?)",
                        (cat["id"], cat["name"]),
                    )

                for rec in records:
                    conn.execute(
                        """
                        INSERT INTO records (code, title, category_id, value, status)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            rec["code"],
                            rec["title"],
                            rec["category_id"],
                            rec["value"],
                            rec["status"],
                        ),
                    )
            logger.info("Database successfully seeded with initial data.")
        except sqlite3.IntegrityError as e:
            logger.error(
                f"Integrity error during seeding (transaction rolled back): {e}"
            )
            raise
        except sqlite3.Error as e:
            logger.error(f"Database error during seeding: {e}")
            raise


if __name__ == "__main__":
    seed_database()
