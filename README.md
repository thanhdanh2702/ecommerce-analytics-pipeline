# End-to-End E-commerce Analytics Pipeline

Analytics engineering project for the Olist e-commerce dataset. The pipeline
loads CSV files into PostgreSQL, validates the raw data, builds analytics models
with dbt, orchestrates the workflow with Airflow, and serves reporting queries
to Metabase.

## Data Flow

```text
Olist CSV files
    ↓
Python ingestion and quality checks
    ↓
PostgreSQL raw schema
    ↓
dbt staging views
    ↓
dbt intermediate views
    ↓
dbt analytics marts
    ↓
Metabase dashboard
```

Airflow runs the workflow as four TaskFlow tasks:

```text
create_raw_tables
→ load_raw_data
→ check_raw_data
→ dbt_build
```

The DAG uses `@task.bash`, runs manually by default, and allows only one active
run at a time.

## Technology Stack

- PostgreSQL 16 for raw and analytics data
- Apache Airflow 3.2.2 with `LocalExecutor`
- dbt Core 1.10 with the PostgreSQL adapter
- Python 3.12 for ingestion and raw-data validation
- Metabase for dashboards
- Docker Compose for local services

## Project Structure

```text
.
├── dags/                         Airflow DAG
├── dashboard/queries/            Metabase SQL queries
├── data/raw/olist/               Source CSV files, excluded from Git
├── dbt/ecommerce_dbt/            dbt project
│   └── models/
│       ├── staging/              9 cleaned source views
│       ├── intermediate/         2 enriched views
│       └── marts/                7 analytics tables
├── docker/                       Airflow image and PostgreSQL initialization
├── docs/                         Architecture and data documentation
├── scripts/                      Ingestion and quality-check scripts
├── sql/                          Raw schema and analytical queries
└── docker-compose.yml
```

## Download the Dataset

Download the
[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
from Kaggle.

Extract the downloaded archive and place the following nine CSV files in
`data/raw/olist/`:

- `olist_customers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `product_category_name_translation.csv`

The expected directory structure is:

```text
data/
└── raw/
    └── olist/
        ├── olist_customers_dataset.csv
        ├── olist_geolocation_dataset.csv
        ├── olist_order_items_dataset.csv
        ├── olist_order_payments_dataset.csv
        ├── olist_order_reviews_dataset.csv
        ├── olist_orders_dataset.csv
        ├── olist_products_dataset.csv
        ├── olist_sellers_dataset.csv
        └── product_category_name_translation.csv
```

The dataset files are excluded from Git and must be downloaded locally before
running the pipeline.

## Setup

Requirements:

- Docker with Docker Compose
- Python 3.12 for optional local execution
- The nine Olist CSV files in `data/raw/olist/`

Create the environment file and replace the example passwords and Airflow
secrets:

```bash
cp .env.example .env
```

`AIRFLOW_API_SECRET_KEY` and `AIRFLOW_JWT_SECRET` must be shared by all Airflow
services and should each contain at least 64 random characters.

Start PostgreSQL and Airflow:

```bash
docker compose up -d --build
docker compose ps
```

Open Airflow at `http://localhost:8080`. The username and password come from
`AIRFLOW_ADMIN_USERNAME` and `AIRFLOW_ADMIN_PASSWORD` in `.env`.

Trigger `ecommerce_analytics_pipeline` from the UI or run:

```bash
docker compose exec airflow-scheduler \
  airflow dags trigger ecommerce_analytics_pipeline
```

The DAG is unscheduled because the bundled Olist dataset is static. Add a
schedule only when the project has a recurring source feed.

## Data Warehouse

The project uses two PostgreSQL databases:

- `warehouse-postgres` stores the `raw` and `analytics` schemas.
- `airflow-postgres` stores Airflow metadata only.

The warehouse is exposed on `localhost:5434` by default. Containers connect to
it through `warehouse-postgres:5432`.

The dbt project contains 18 models:

- 9 staging views that clean strings and cast source values
- 2 intermediate views that enrich orders and order items
- 7 mart tables for dimensions and facts

`dbt build` also executes 89 source and model tests.

## Local Development

Install the Python and dbt dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Load `.env` before running dbt outside Docker:

```bash
set -a
source .env
set +a
```

Validate the dbt project:

```bash
dbt debug --project-dir dbt/ecommerce_dbt --profiles-dir dbt/ecommerce_dbt
dbt build --project-dir dbt/ecommerce_dbt --profiles-dir dbt/ecommerce_dbt
```

Check Airflow DAG imports:

```bash
docker compose exec airflow-scheduler \
  airflow dags list-import-errors --output=json
```

## Metabase Dashboard

The dashboard reads from the PostgreSQL `analytics` schema.

[View the exported dashboard PDF](docs/E-commerce%20Analytics%20Dashboard.pdf)

Start Metabase:

```bash
docker run -d \
  --name metabase \
  -p 3000:3000 \
  -v metabase_data:/metabase-data \
  -e MB_DB_FILE=/metabase-data/metabase.db \
  metabase/metabase:latest
```

For later sessions:

```bash
docker start metabase
```

Connect Metabase with these settings:

| Setting | Value |
| --- | --- |
| Host | `host.docker.internal` |
| Port | `WAREHOUSE_DB_PORT` from `.env` |
| Database | `WAREHOUSE_DB_NAME` from `.env` |
| Username | `WAREHOUSE_DB_USER` from `.env` |
| Password | `WAREHOUSE_DB_PASSWORD` from `.env` |
| Schema | `analytics` |
| SSL | Disabled for local development |

Create native SQL questions from the files in `dashboard/queries/`.

## Documentation

- [Architecture](docs/architecture.md)
- [Pipeline flow](docs/pipeline_flow.md)
- [Data model](docs/data_model.md)

## Stop Services

```bash
docker compose down
docker stop metabase
```

Named Docker volumes preserve warehouse data, Airflow metadata, and Metabase
configuration between restarts.
