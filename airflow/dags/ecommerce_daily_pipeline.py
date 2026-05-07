from __future__ import annotations

from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_ROOT = "/opt/airflow/project"
DBT_PROJECT_DIR = f"{PROJECT_ROOT}/dbt/ecommerce_dbt"
DBT_PROFILES_DIR = f"{PROJECT_ROOT}/dbt/profiles"

DOCKER_ENV = """
export API_BASE_URL=http://api:8000
export API_BASE_URL_DOCKER=http://api:8000
export POSTGRES_HOST=postgres
export POSTGRES_PORT=5432
export POSTGRES_HOST_DOCKER=postgres
export POSTGRES_PORT_DOCKER=5432
"""


default_args = {
    "owner": "phuchoang",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}


with DAG(
    dag_id="ecommerce_daily_pipeline",
    description="Daily ecommerce pipeline: API ingestion, raw validation, dbt snapshot/run/test, business validation",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["ecommerce", "dbt", "postgres", "analytics"],
) as dag:

    check_api_health = BashOperator(
        task_id="check_api_health",
        bash_command="curl -f http://api:8000/health",
    )

    run_ingestion = BashOperator(
        task_id="run_ingestion",
        bash_command=f"""
        set -e
        {DOCKER_ENV}
        cd {PROJECT_ROOT}
        python -m src.ingestion.run_ingestion --mode incremental
        """,
    )

    validate_raw = BashOperator(
        task_id="validate_raw",
        bash_command=f"""
        set -e
        {DOCKER_ENV}
        cd {PROJECT_ROOT}
        python -m src.validation.validate_raw
        """,
    )

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command=f"""
        set -e
        {DOCKER_ENV}
        cd {DBT_PROJECT_DIR}
        dbt debug --profiles-dir {DBT_PROFILES_DIR} --target dev
        """,
    )

    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=f"""
        set -e
        {DOCKER_ENV}
        cd {DBT_PROJECT_DIR}
        dbt run --select staging --profiles-dir {DBT_PROFILES_DIR} --target dev
        """,
    )

    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=f"""
        set -e
        {DOCKER_ENV}
        cd {DBT_PROJECT_DIR}
        dbt snapshot --profiles-dir {DBT_PROFILES_DIR} --target dev
        """,
    )

    dbt_run_core_marts = BashOperator(
        task_id="dbt_run_core_marts",
        bash_command=f"""
        set -e
        {DOCKER_ENV}
        cd {DBT_PROJECT_DIR}
        dbt run --select core marts --profiles-dir {DBT_PROFILES_DIR} --target dev
        """,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"""
        set -e
        {DOCKER_ENV}
        cd {DBT_PROJECT_DIR}
        dbt test --profiles-dir {DBT_PROFILES_DIR} --target dev
        """,
    )

    validate_business = BashOperator(
        task_id="validate_business",
        bash_command=f"""
        set -e
        {DOCKER_ENV}
        cd {PROJECT_ROOT}
        PGPASSWORD="$POSTGRES_PASSWORD" psql \
          -h "$POSTGRES_HOST" \
          -p "$POSTGRES_PORT" \
          -U "$POSTGRES_USER" \
          -d "$POSTGRES_DB" \
          -v ON_ERROR_STOP=1 \
          -f sql/check/check_marts.sql
        """,
    )

    (
        check_api_health
        >> run_ingestion
        >> validate_raw
        >> dbt_debug
        >> dbt_run_staging
        >> dbt_snapshot
        >> dbt_run_core_marts
        >> dbt_test
        >> validate_business
    )
