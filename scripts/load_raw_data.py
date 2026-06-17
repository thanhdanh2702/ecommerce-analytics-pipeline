from pathlib import Path
import os
import psycopg2
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "olist"

load_dotenv(PROJECT_ROOT / ".env")

CSV_FILES = {
    "olist_customers_dataset.csv": "raw.customers",
    "olist_geolocation_dataset.csv": "raw.geolocation",
    "olist_order_items_dataset.csv": "raw.order_items",
    "olist_order_payments_dataset.csv": "raw.order_payments",
    "olist_order_reviews_dataset.csv": "raw.order_reviews",
    "olist_orders_dataset.csv": "raw.orders",
    "olist_products_dataset.csv": "raw.products",
    "olist_sellers_dataset.csv": "raw.sellers",
    "product_category_name_translation.csv": "raw.product_category_name_translation"
}

def get_connection():
    return psycopg2.connect(
        host=os.getenv("WAREHOUSE_DB_HOST", "localhost"),
        port=os.getenv("WAREHOUSE_DB_PORT", "5434"),
        database=os.getenv("WAREHOUSE_DB_NAME", "ecommerce"),
        user=os.getenv("WAREHOUSE_DB_USER", "ecommerce"),
        password=os.getenv("WAREHOUSE_DB_PASSWORD", "ecommerce")  
    )

def truncate_table(conn, table_name: str) -> None:
    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table_name};")

def copy_csv_to_table(conn, csv_path: Path, table_name: str) -> None:
    with conn.cursor() as cur:
        with csv_path.open("r", encoding="utf-8") as file:
            cur.copy_expert(
                sql=f"""
                    COPY {table_name}
                    FROM STDIN
                    WITH (
                        FORMAT CSV,
                        HEADER TRUE,
                        DELIMITER ',',
                        QUOTE '"',
                        ESCAPE '"',
                        NULL ''
                    );
                """,
                file=file
            )

def get_table_row_count(conn, table_name: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        result = cur.fetchone()
        return int(result[0]) if result else 0
    
def load_raw_data() -> None:
    conn = get_connection()

    try:
        with conn:
            for csv_file_name, table_name in CSV_FILES.items():
                csv_path = RAW_DATA_PATH / csv_file_name

                print(f"Loading {csv_file_name} -> {table_name}")

                truncate_table(conn, table_name)
                copy_csv_to_table(conn, csv_path, table_name)

                row_count = get_table_row_count(conn, table_name)
                print(f"Loaded {row_count:,} rows into {table_name}")
    except Exception as exc:
        conn.rollback()
        raise RuntimeError(f"Failed to load raw data: {exc}") from exc
    finally:
        conn.close()

if __name__ == "__main__":
    load_raw_data()