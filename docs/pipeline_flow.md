# Pipeline Flow

## DAG

The `ecommerce_analytics_pipeline` DAG is defined with the Airflow TaskFlow API
and `@task.bash`.

```text
create_raw_tables
→ load_raw_data
→ check_raw_data
→ dbt_build
```

Configuration:

| Property | Value |
| --- | --- |
| Schedule | Manual |
| Catchup | Disabled |
| Maximum active runs | 1 |
| Executor | LocalExecutor |

## Step 1: Create Raw Tables

`scripts/create_raw_tables.py` executes `sql/raw_schema.sql`.

The SQL creates the `raw` schema and nine tables if they do not exist. Source
columns remain `TEXT`; type conversion belongs to dbt staging models.

This task is safe to repeat because it does not drop existing tables.

## Step 2: Load Raw Data

`scripts/load_raw_data.py` maps each CSV file to its raw table:

| CSV file | Raw table |
| --- | --- |
| `olist_customers_dataset.csv` | `raw.customers` |
| `olist_geolocation_dataset.csv` | `raw.geolocation` |
| `olist_order_items_dataset.csv` | `raw.order_items` |
| `olist_order_payments_dataset.csv` | `raw.order_payments` |
| `olist_order_reviews_dataset.csv` | `raw.order_reviews` |
| `olist_orders_dataset.csv` | `raw.orders` |
| `olist_products_dataset.csv` | `raw.products` |
| `olist_sellers_dataset.csv` | `raw.sellers` |
| `product_category_name_translation.csv` | `raw.product_category_name_translation` |

For every table, the script:

1. truncates the previous contents;
2. loads the CSV with PostgreSQL `COPY`;
3. prints the resulting row count.

The complete load runs inside one transaction. If any file fails, PostgreSQL
rolls back the refresh.

## Step 3: Validate Raw Data

`scripts/check_raw_data.py` checks:

- database connectivity;
- expected tables and ordered columns;
- CSV row counts against database row counts;
- required values;
- unique business keys;
- parent-child relationships.

Validated relationships:

```text
orders.customer_id        → customers.customer_id
order_items.order_id      → orders.order_id
order_items.product_id    → products.product_id
order_items.seller_id     → sellers.seller_id
order_payments.order_id   → orders.order_id
order_reviews.order_id    → orders.order_id
```

Any error exits with a non-zero status and blocks downstream transformation.

## Step 4: Build Analytics Models

The final task runs:

```bash
dbt build \
  --project-dir /opt/airflow/project/dbt/ecommerce_dbt \
  --profiles-dir /opt/airflow/project/dbt/ecommerce_dbt
```

`dbt build` processes models and tests in dependency order:

```text
9 raw sources
→ 9 staging views
→ 2 intermediate views
→ 7 mart tables
```

The project currently contains 18 models and 89 data tests.

## Running the Pipeline

Start services:

```bash
docker compose up -d --build
```

Trigger a run:

```bash
docker compose exec airflow-scheduler \
  airflow dags trigger ecommerce_analytics_pipeline
```

Check DAG imports:

```bash
docker compose exec airflow-scheduler \
  airflow dags list-import-errors --output=json
```

Inspect service state:

```bash
docker compose ps
```

## Successful Run Criteria

A run is successful only when:

1. all raw tables exist;
2. all nine CSV files load;
3. every raw quality check passes;
4. all 18 dbt models build;
5. all 89 dbt tests pass.

After success, dashboard queries can read the refreshed `analytics` schema.

## Failure Handling

Airflow stops at the first failed task. Fix the underlying problem and trigger a
new run.

Common failure points:

| Symptom | Check |
| --- | --- |
| Missing CSV | Confirm all files exist in `data/raw/olist/` |
| Warehouse connection failure | Check `WAREHOUSE_DB_*` variables and container health |
| Raw quality failure | Review the failed check in task logs |
| dbt failure | Inspect the model or test reported by `dbt_build` |
| Worker hostname or served-log error | Verify the Execution API URL and shared Airflow secrets |

The required Airflow settings are:

```text
AIRFLOW_EXECUTION_API_SERVER_URL=http://airflow-api-server:8080/execution/
AIRFLOW_API_SECRET_KEY=<shared secret>
AIRFLOW_JWT_SECRET=<shared secret>
```
