# End-to-End E-commerce Analytics Pipeline

Environment scaffold for an e-commerce analytics pipeline using the Olist dataset, PostgreSQL, Airflow, dbt, and SQL dashboard queries.

## Project Layout

- `data/raw/olist`: raw Olist CSV files
- `data/processed`: processed outputs
- `scripts`: Python scripts you will implement
- `sql`: SQL files you will implement
- `dags`: Airflow DAGs you will implement
- `dbt/ecommerce_dbt`: dbt project scaffold
- `dashboard/queries`: dashboard SQL queries you will implement
- `docs`: project documentation

## Environment Setup

Copy `.env.example` to `.env`, then edit credentials and ports if needed.

```bash
cp .env.example .env
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d warehouse-postgres
```

This project separates databases:

- `warehouse-postgres`: project data warehouse for raw and analytics data
- `airflow-postgres`: Airflow metadata database

The warehouse database is exposed on `localhost:5434` by default to avoid conflicts with a local Postgres instance on `5432`. Inside Docker, services still connect to `warehouse-postgres:5432`.

Docker Compose reads `.env` automatically. For local dbt commands outside Docker, export the `.env` values first:

```bash
set -a
source .env
set +a
```

## dbt

This project uses dbt Core with the Postgres adapter. If your editor offers dbt Fusion, do not use it for this project because Fusion does not support the `postgres` adapter here.

Validate the dbt setup:

```bash
source .venv/bin/activate
dbt debug --project-dir dbt/ecommerce_dbt --profiles-dir dbt/ecommerce_dbt
dbt parse --project-dir dbt/ecommerce_dbt --profiles-dir dbt/ecommerce_dbt
```

For VS Code with the dbt Power User extension, use the project virtual environment as the Python interpreter and set the dbt integration to `core`.

Airflow setup is available through Docker Compose:

```bash
docker compose up -d
```

Airflow UI: `http://localhost:8080`

Default local credentials:

- Username: `admin`
- Password: `admin`

These values come from `AIRFLOW_ADMIN_USERNAME` and `AIRFLOW_ADMIN_PASSWORD` in `.env`.
