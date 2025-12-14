import pandas as pd
from app.data.db import connect_database


def insert_dataset(
    dataset_name, category, source, last_updated, record_count, file_size_mb
):
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO datasets_metadata
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (dataset_name, category, source, last_updated, record_count, file_size_mb),
    )
    conn.commit()
    dataset_id = cursor.lastrowid
    conn.close()
    return dataset_id


def get_all_datasets():
    conn = connect_database()
    try:
        df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
    finally:
        conn.close()
    return df


def update_dataset_record_count(id, new_count):
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE datasets_metadata
        SET record_count = ?
        WHERE id = ?
        """,
        (new_count, id),
    )
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    return rows_updated


def delete_dataset(id):
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM datasets_metadata WHERE id = ?", (id,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted > 0


def get_dataset_statistics():
    """Calculates and returns key metrics for the Datasets dashboard."""
    conn = connect_database()
    try:
        total_datasets_df = pd.read_sql_query(
            "SELECT COUNT(id) FROM datasets_metadata", conn
        )
        total_datasets = (
            total_datasets_df.iloc[0, 0] if not total_datasets_df.empty else 0
        )

        total_records_df = pd.read_sql_query(
            "SELECT SUM(record_count) FROM datasets_metadata", conn
        )
        total_records = total_records_df.iloc[0, 0] if not total_records_df.empty else 0
        total_records = int(total_records) if total_records is not None else 0

        total_size_df = pd.read_sql_query(
            "SELECT SUM(file_size_mb) FROM datasets_metadata", conn
        )
        total_size = total_size_df.iloc[0, 0] if not total_size_df.empty else 0
        total_size_mb = round(float(total_size) if total_size is not None else 0.0, 1)

        category_counts_df = pd.read_sql_query(
            "SELECT category, COUNT(*) as count FROM datasets_metadata GROUP BY category",
            conn,
        )
        by_category = category_counts_df.to_dict("records")

        return {
            "total": int(total_datasets),
            "total_records": total_records,
            "total_size_mb": total_size_mb,
            "by_category": by_category,
        }

    except Exception as e:
        print(f"Error calculating dataset statistics: {e}")
        return {
            "total": 0,
            "total_records": 0,
            "total_size_mb": 0.0,
            "by_category": [],
        }
    finally:
        conn.close()
