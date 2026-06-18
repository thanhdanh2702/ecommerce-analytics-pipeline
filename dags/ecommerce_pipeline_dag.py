import os
from datetime import datetime, timezone

from airflow.sdk import dag, task


PROJECT_ROOT = os.getenv("PROJECT_ROOT", "/opt/airflow/project")
DBT_PROJECT_DIR = f"{PROJECT_ROOT}/dbt/ecommerce_dbt"
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", DBT_PROJECT_DIR)


@dag(
    dag_id="ecommerce_analytics_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
)
def ecommerce_analytics_pipeline():
    @task.bash
    def create_raw_tables():
        return f"python {PROJECT_ROOT}/scripts/create_raw_tables.py"

    @task.bash
    def load_raw_data():
        return f"python {PROJECT_ROOT}/scripts/load_raw_data.py"

    @task.bash
    def check_raw_data():
        return f"python {PROJECT_ROOT}/scripts/check_raw_data.py"

    @task.bash
    def dbt_build():
        return (
            f"dbt build --project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} --no-use-colors"
        )

    create_raw_tables() >> load_raw_data() >> check_raw_data() >> dbt_build()


ecommerce_analytics_pipeline()
