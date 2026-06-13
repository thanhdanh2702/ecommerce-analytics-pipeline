ARG AIRFLOW_IMAGE=apache/airflow:3.2.2-python3.12
FROM ${AIRFLOW_IMAGE}

ARG AIRFLOW_VERSION=3.2.2

COPY docker/airflow/requirements.txt /requirements.txt
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
