# End-to-End E-commerce Analytics Pipeline

End-to-end analytics pipeline for the Olist e-commerce dataset using PostgreSQL, Airflow, dbt, SQL, and Metabase.

## Project Layout

- `data/raw/olist`: raw Olist CSV files
- `data/processed`: processed outputs
- `scripts`: Python scripts you will implement
- `sql`: SQL files you will implement
- `dags`: Airflow DAGs you will implement
- `dbt/ecommerce_dbt`: dbt project scaffold
- `dashboard/queries`: SQL queries used by the Metabase dashboard
- `docs`: architecture, data model, pipeline documentation, and dashboard exports

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

## Analytics Dashboard

The analytics dashboard is built with Metabase using the models in the PostgreSQL `analytics` schema.

[View the dashboard as PDF](docs/E-commerce%20Analytics%20Dashboard.pdf)

![E-commerce Analytics Dashboard](docs/images/ecommerce-analytics-dashboard.png)

### Run Metabase

Create the Metabase container the first time:

```bash
docker run -d \
  --name metabase \
  -p 3000:3000 \
  -v metabase_data:/metabase-data \
  -e MB_DB_FILE=/metabase-data/metabase.db \
  metabase/metabase:latest
```

For later sessions, start the existing container:

```bash
docker start metabase
```

Open the Metabase UI at `http://localhost:3000`.

Stop Metabase when it is not needed:

```bash
docker stop metabase
```

The `metabase_data` Docker volume persists Metabase users, questions, chart settings, and dashboard layout between container restarts.

### Connect Metabase to the Warehouse

In Metabase, open **Admin settings → Databases → Add a database**, select PostgreSQL, and use:

| Setting | Value |
| --- | --- |
| Display name | `E-commerce Analytics` |
| Host | `host.docker.internal` |
| Port | `5434` or `WAREHOUSE_DB_PORT` from `.env` |
| Database name | `WAREHOUSE_DB_NAME` from `.env` |
| Username | `WAREHOUSE_DB_USER` from `.env` |
| Password | `WAREHOUSE_DB_PASSWORD` from `.env` |
| Schema | `analytics` |
| SSL | Disabled for local development |

`host.docker.internal` is required because Metabase runs inside Docker while the warehouse port is exposed through the macOS host.

Before connecting Metabase, confirm that the warehouse is running:

```bash
docker compose up -d warehouse-postgres
docker compose ps warehouse-postgres
```

### Dashboard Questions

Create a native SQL question in Metabase for each query below, configure its visualization, save it, and add it to the dashboard.

| Query | Recommended visualization | Main fields |
| --- | --- | --- |
| `dashboard/queries/revenue_by_month.sql` | Line chart | X: `order_month`, Y: `revenue` |
| `dashboard/queries/order_status.sql` | Donut chart | Category: `order_status`, Metric: `order_count` |
| `dashboard/queries/payment_methods.sql` | Donut chart | Category: `payment_type`, Metric: `total_payment_value` |
| `dashboard/queries/top_categories.sql` | Horizontal bar chart | Y: `product_category`, X: `revenue` |
| `dashboard/queries/delivery_performance.sql` | Horizontal bar chart | Y: `customer_state`, X: `average_delivery_days` |

The SQL files are version-controlled in Git. Metabase-specific question definitions and dashboard layout remain in the `metabase_data` volume, while the PDF above provides a portable snapshot of the completed dashboard.

## Airflow

Airflow setup is available through Docker Compose:

```bash
docker compose up -d
```

Airflow UI: `http://localhost:8080`

Default local credentials:

- Username: `admin`
- Password: `admin`

These values come from `AIRFLOW_ADMIN_USERNAME` and `AIRFLOW_ADMIN_PASSWORD` in `.env`.
