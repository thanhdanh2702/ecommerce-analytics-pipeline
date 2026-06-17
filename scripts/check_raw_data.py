from pathlib import Path
import csv
import os
import sys

import psycopg2
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "olist"

load_dotenv(PROJECT_ROOT / ".env")


TABLES = {
    "olist_customers_dataset.csv": {
        "table": "raw.customers",
        "columns": [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ],
        "required": ["customer_id", "customer_unique_id"],
        "unique": [["customer_id"]],
    },
    "olist_geolocation_dataset.csv": {
        "table": "raw.geolocation",
        "columns": [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ],
        "required": ["geolocation_zip_code_prefix"],
        "unique": [],
    },
    "olist_order_items_dataset.csv": {
        "table": "raw.order_items",
        "columns": [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ],
        "required": ["order_id", "order_item_id", "product_id", "seller_id"],
        "unique": [["order_id", "order_item_id"]],
    },
    "olist_order_payments_dataset.csv": {
        "table": "raw.order_payments",
        "columns": [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ],
        "required": ["order_id", "payment_sequential", "payment_type"],
        "unique": [["order_id", "payment_sequential"]],
    },
    "olist_order_reviews_dataset.csv": {
        "table": "raw.order_reviews",
        "columns": [
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ],
        "required": ["review_id", "order_id", "review_score"],
        "unique": [],
    },
    "olist_orders_dataset.csv": {
        "table": "raw.orders",
        "columns": [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
        "required": ["order_id", "customer_id", "order_status"],
        "unique": [["order_id"]],
    },
    "olist_products_dataset.csv": {
        "table": "raw.products",
        "columns": [
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ],
        "required": ["product_id"],
        "unique": [["product_id"]],
    },
    "olist_sellers_dataset.csv": {
        "table": "raw.sellers",
        "columns": [
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ],
        "required": ["seller_id"],
        "unique": [["seller_id"]],
    },
    "product_category_name_translation.csv": {
        "table": "raw.product_category_name_translation",
        "columns": [
            "product_category_name",
            "product_category_name_english",
        ],
        "required": [
            "product_category_name",
            "product_category_name_english",
        ],
        "unique": [["product_category_name"]],
    },
}


RELATIONSHIPS = [
    ("raw.orders", "customer_id", "raw.customers", "customer_id"),
    ("raw.order_items", "order_id", "raw.orders", "order_id"),
    ("raw.order_items", "product_id", "raw.products", "product_id"),
    ("raw.order_items", "seller_id", "raw.sellers", "seller_id"),
    ("raw.order_payments", "order_id", "raw.orders", "order_id"),
    ("raw.order_reviews", "order_id", "raw.orders", "order_id"),
]


def get_connection():
    return psycopg2.connect(
        host=os.getenv("WAREHOUSE_DB_HOST", "localhost"),
        port=os.getenv("WAREHOUSE_DB_PORT", "5434"),
        database=os.getenv("WAREHOUSE_DB_NAME", "ecommerce"),
        user=os.getenv("WAREHOUSE_DB_USER", "ecommerce"),
        password=os.getenv("WAREHOUSE_DB_PASSWORD", "ecommerce"),
    )


def run_scalar(conn, query: str, params: tuple = ()) -> int:
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()[0]


def section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def split_table(table_name: str) -> tuple[str, str]:
    return tuple(table_name.split(".", 1))


def count_csv_rows(file_path: Path) -> int:
    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        next(reader, None)
        return sum(1 for _ in reader)


def table_exists(conn, table_name: str) -> bool:
    schema, table = split_table(table_name)

    return bool(
        run_scalar(
            conn,
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_name = %s
            );
            """,
            (schema, table),
        )
    )


def get_columns(conn, table_name: str) -> list[str]:
    schema, table = split_table(table_name)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
            ORDER BY ordinal_position;
            """,
            (schema, table),
        )
        return [row[0] for row in cur.fetchall()]


def count_table_rows(conn, table_name: str) -> int:
    return run_scalar(conn, f"SELECT COUNT(*) FROM {table_name};")


def count_missing_values(conn, table_name: str, column: str) -> int:
    return run_scalar(
        conn,
        f"""
        SELECT COUNT(*)
        FROM {table_name}
        WHERE {column} IS NULL
           OR BTRIM({column}::TEXT) = '';
        """,
    )


def count_duplicate_keys(conn, table_name: str, columns: list[str]) -> int:
    column_list = ", ".join(columns)

    return run_scalar(
        conn,
        f"""
        SELECT COUNT(*)
        FROM (
            SELECT {column_list}
            FROM {table_name}
            GROUP BY {column_list}
            HAVING COUNT(*) > 1
        ) AS duplicated;
        """,
    )


def count_orphans(
    conn,
    child_table: str,
    child_column: str,
    parent_table: str,
    parent_column: str,
) -> int:
    return run_scalar(
        conn,
        f"""
        SELECT COUNT(*)
        FROM {child_table} AS child
        LEFT JOIN {parent_table} AS parent
          ON child.{child_column} = parent.{parent_column}
        WHERE child.{child_column} IS NOT NULL
          AND BTRIM(child.{child_column}::TEXT) <> ''
          AND parent.{parent_column} IS NULL;
        """,
    )


def check_connection(conn) -> int:
    section("DATABASE CONNECTION")

    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user;")
        database, user = cur.fetchone()

    print(f"[OK] Connected to database={database}, user={user}")
    return 0


def check_tables(conn) -> int:
    section("TABLE AND COLUMN CHECKS")

    errors = 0

    for config in TABLES.values():
        table = config["table"]

        if not table_exists(conn, table):
            print(f"[ERROR] {table}: table does not exist")
            errors += 1
            continue

        actual_columns = get_columns(conn, table)
        expected_columns = config["columns"]

        if actual_columns != expected_columns:
            print(f"[ERROR] {table}: column mismatch")
            print(f"        Expected: {expected_columns}")
            print(f"        Actual:   {actual_columns}")
            errors += 1
        else:
            print(f"[OK] {table}: columns matched")

    return errors


def check_row_counts(conn) -> int:
    section("ROW COUNT CHECKS")

    errors = 0

    for csv_file, config in TABLES.items():
        table = config["table"]
        csv_path = RAW_DATA_PATH / csv_file

        if not csv_path.exists():
            print(f"[ERROR] Missing CSV file: {csv_path}")
            errors += 1
            continue

        csv_count = count_csv_rows(csv_path)
        db_count = count_table_rows(conn, table)

        if csv_count != db_count:
            print(f"[ERROR] {table}: CSV={csv_count:,}, DB={db_count:,}")
            errors += 1
        else:
            print(f"[OK] {table}: {db_count:,} rows")

    return errors


def check_required_columns(conn) -> int:
    section("REQUIRED VALUE CHECKS")

    errors = 0

    for config in TABLES.values():
        table = config["table"]

        for column in config["required"]:
            missing_count = count_missing_values(conn, table, column)

            if missing_count > 0:
                print(f"[ERROR] {table}.{column}: {missing_count:,} missing values")
                errors += 1
            else:
                print(f"[OK] {table}.{column}: no missing values")

    return errors


def check_unique_keys(conn) -> int:
    section("UNIQUE KEY CHECKS")

    errors = 0

    for config in TABLES.values():
        table = config["table"]

        for columns in config["unique"]:
            duplicate_count = count_duplicate_keys(conn, table, columns)
            key = ", ".join(columns)

            if duplicate_count > 0:
                print(f"[ERROR] {table} ({key}): {duplicate_count:,} duplicate groups")
                errors += 1
            else:
                print(f"[OK] {table} ({key}): unique")

    return errors


def check_relationships(conn) -> int:
    section("RELATIONSHIP CHECKS")

    errors = 0

    for child_table, child_col, parent_table, parent_col in RELATIONSHIPS:
        orphan_count = count_orphans(
            conn,
            child_table,
            child_col,
            parent_table,
            parent_col,
        )

        relationship = f"{child_table}.{child_col} -> {parent_table}.{parent_col}"

        if orphan_count > 0:
            print(f"[ERROR] {relationship}: {orphan_count:,} orphan rows")
            errors += 1
        else:
            print(f"[OK] {relationship}: no orphan rows")

    return errors


def main() -> None:
    try:
        with get_connection() as conn:
            errors = 0

            errors += check_connection(conn)
            errors += check_tables(conn)
            errors += check_row_counts(conn)
            errors += check_required_columns(conn)
            errors += check_unique_keys(conn)
            errors += check_relationships(conn)

            section("SUMMARY")

            if errors > 0:
                print(f"Raw data check failed with {errors} error(s).")
                sys.exit(1)

            print("Raw data check passed.")

    except Exception as exc:
        print(f"[FATAL] Failed to check raw data: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()