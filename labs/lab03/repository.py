import sqlite3
from contextlib import closing
from typing import Any

from labs.lab03.database import get_connection


def get_categories() -> list[dict[str, Any]]:
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT id, name FROM categories ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]


def get_category_by_id(category_id: int) -> dict[str, Any] | None:
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT id, name FROM categories WHERE id = ?", (category_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def create_category(name: str, category_id: int | None = None) -> dict[str, Any]:
    with closing(get_connection()) as conn:
        try:
            if category_id is not None:
                cursor = conn.execute(
                    "INSERT INTO categories (id, name) VALUES (?, ?)",
                    (category_id, name),
                )
                cat_id = category_id
            else:
                cursor = conn.execute(
                    "INSERT INTO categories (name) VALUES (?)", (name,)
                )
                cat_id = cursor.lastrowid
            conn.commit()
            return {"id": cat_id, "name": name}
        except sqlite3.Error:
            conn.rollback()
            raise


def delete_category(category_id: int) -> bool:
    with closing(get_connection()) as conn:
        try:
            cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            conn.rollback()
            raise


def get_records(
    category_id: int | None = None,
    status: str | None = None,
    min_value: float | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    query = """
        SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name AS category_name
        FROM records r
        JOIN categories c ON r.category_id = c.id
        WHERE 1=1
    """
    params: list[Any] = []

    if category_id is not None:
        query += " AND r.category_id = ?"
        params.append(category_id)

    if status is not None:
        query += " AND r.status = ?"
        params.append(status)

    if min_value is not None:
        query += " AND r.value >= ?"
        params.append(min_value)

    if q is not None:
        query += " AND instr(r.title, ?) > 0"
        params.append(q)

    query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_record_by_id(record_id: int) -> dict[str, Any] | None:
    query = """
        SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name AS category_name
        FROM records r
        JOIN categories c ON r.category_id = c.id
        WHERE r.id = ?
    """
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_record(data: dict[str, Any]) -> dict[str, Any]:
    query = """
        INSERT INTO records (code, title, category_id, value, status)
        VALUES (?, ?, ?, ?, ?)
    """
    with closing(get_connection()) as conn:
        try:
            cursor = conn.execute(
                query,
                (
                    data["code"],
                    data["title"],
                    data["category_id"],
                    data["value"],
                    data["status"],
                ),
            )
            conn.commit()
            rec_id = cursor.lastrowid
            if rec_id is None:
                raise sqlite3.Error("Failed to retrieve last insert row ID.")
            rec = get_record_by_id(rec_id)
            if rec is None:
                raise sqlite3.Error("Faield to retrieve the newly created record.")
            return rec
        except sqlite3.Error:
            conn.rollback()
            raise


def update_record(record_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
    query = """
        UPDATE records
        SET code = ?, title = ?, category_id = ?, value = ?, status = ?
        WHERE id = ?
    """
    with closing(get_connection()) as conn:
        try:
            cursor = conn.execute(
                query,
                (
                    data["code"],
                    data["title"],
                    data["category_id"],
                    data["value"],
                    data["status"],
                    record_id,
                ),
            )
            conn.commit()
            if cursor.rowcount == 0:
                return None
            return get_record_by_id(record_id)
        except sqlite3.Error:
            conn.rollback()
            raise


def delete_record(record_id: int) -> bool:
    with closing(get_connection()) as conn:
        try:
            cursor = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            conn.rollback()
            raise


def create_records_bulk(records_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    insert_query = """
        INSERT INTO records (code, title, category_id, value, status)
        VALUES (?, ?, ?, ?, ?)
    """
    with closing(get_connection()) as conn:
        with conn:
            inserted_ids = []
            for data in records_data:
                cursor = conn.execute(
                    insert_query,
                    (
                        data["code"],
                        data["title"],
                        data["category_id"],
                        data["value"],
                        data["status"],
                    ),
                )
                inserted_ids.append(cursor.lastrowid)

        results = []
        for rid in inserted_ids:
            rec = get_record_by_id(rid)
            if rec:
                results.append(rec)
        return results
