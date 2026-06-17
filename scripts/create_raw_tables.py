from pathlib import Path
import os
import psycopg2
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_SCHEMA_PATH = PROJECT_ROOT / "sql" / "raw_schema.sql"
load_dotenv(PROJECT_ROOT / ".env")

def get_connection():
    return psycopg2.connect(
        host=os.getenv("WAREHOUSE_DB_HOST", "localhost"),
        port=os.getenv("WAREHOUSE_DB_PORT", "5434"),
        database=os.getenv("WAREHOUSE_DB_NAME", "ecommerce"),
        user=os.getenv("WAREHOUSE_DB_USER", "ecommerce"),
        password=os.getenv("WAREHOUSE_DB_PASSWORD", "ecommerce")
    )

def create_raw_tables() -> None:
    if not RAW_SCHEMA_PATH.exists():
        raise FileNotFoundError(f"SQL file not found: {RAW_SCHEMA_PATH}")
    
    sql_script = RAW_SCHEMA_PATH.read_text(encoding="utf-8")

    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql_script)

        print("Raw schema and raw tables created successfully.")

    except Exception as exc:
        conn.rollback()
        raise RuntimeError(f"Failed to create raw tables: {exc}") from exc

    finally:
        conn.close()       

if __name__ == "__main__":
    create_raw_tables()