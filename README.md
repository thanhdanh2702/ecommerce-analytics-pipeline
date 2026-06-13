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

Docker Compose reads `.env` automatically. For local dbt commands outside Docker, export the `.env` values first:

```bash
set -a
source .env
set +a
```

Airflow setup is available through Docker Compose:

```bash
docker compose up -d
```

Airflow UI: `http://localhost:8080`

Default local credentials:

- Username: `admin`
- Password: `admin`

These values come from `AIRFLOW_ADMIN_USERNAME` and `AIRFLOW_ADMIN_PASSWORD` in `.env`.
