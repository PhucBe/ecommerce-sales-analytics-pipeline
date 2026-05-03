from __future__ import annotations
import argparse
from typing import Any
from src.common.config import load_app_config
from src.common.logger import get_logger
from src.common.utils import make_batch_id, utc_now
from src.ingestion.fetch_api import (
    check_api_health,
    fetch_all_datasets,
    fetch_dataset,
)
from src.ingestion.load_raw_postgres import (
    DATASET_COLUMNS,
    get_latest_updated_at,
    get_postgres_connection,
    insert_dataset_records,
    truncate_raw_tables,
)


def run_full_refresh(config: dict[str, Any]) -> None:
    logger = get_logger(
        name="run_ingestion",
        log_dir=config["paths"]["log_dir"],
    )
    batch_id = make_batch_id()
    ingested_at = utc_now()

    logger.info("=" * 80)
    logger.info("START INGESTION - FULL REFRESH")
    logger.info("batch_id=%s", batch_id)
    logger.info("=" * 80)

    datasets = fetch_all_datasets(
        config=config,
        logger=logger,
    )

    for dataset_name, records in datasets.items():
        if not records:
            raise ValueError(f"Dataset is empty, stop before truncating raw tables: {dataset_name}")

    connection = get_postgres_connection(config)

    try:
        schema_name = config["postgres"]["schema_raw"]
        source_system = config["ingestion"]["source_system"]

        truncate_raw_tables(
            connection=connection,
            schema_name=schema_name,
            logger=logger,
        )

        total_inserted = 0

        for dataset_name, records in datasets.items():
            inserted_count = insert_dataset_records(
                connection=connection,
                schema_name=schema_name,
                dataset_name=dataset_name,
                records=records,
                batch_id=batch_id,
                source_system=source_system,
                ingested_at=ingested_at,
                logger=logger,
            )

            total_inserted += inserted_count

        connection.commit()

        logger.info("=" * 80)
        logger.info("FULL REFRESH INGESTION FINISHED SUCCESSFULLY")
        logger.info("total_inserted=%s", total_inserted)
        logger.info("batch_id=%s", batch_id)
        logger.info("=" * 80)

    except Exception:
        connection.rollback()
        logger.exception("FULL REFRESH INGESTION FAILED. Transaction rolled back.")
        raise

    finally:
        connection.close()


def run_incremental(config: dict[str, Any]) -> None:
    logger = get_logger(
        name="run_ingestion",
        log_dir=config["paths"]["log_dir"],
    )
    batch_id = make_batch_id()
    ingested_at = utc_now()

    logger.info("=" * 80)
    logger.info("START INGESTION - INCREMENTAL")
    logger.info("batch_id=%s", batch_id)
    logger.info("=" * 80)

    check_api_health(
        base_url=config["api"]["base_url"],
        timeout_seconds=int(config["api"]["timeout_seconds"]),
        logger=logger,
    )

    connection = get_postgres_connection(config)

    try:
        schema_name = config["postgres"]["schema_raw"]
        source_system = config["ingestion"]["source_system"]

        total_inserted = 0

        for dataset_name in DATASET_COLUMNS:
            latest_updated_at = get_latest_updated_at(
                connection=connection,
                schema_name=schema_name,
                dataset_name=dataset_name,
            )

            updated_after = latest_updated_at.isoformat() if latest_updated_at else None

            logger.info(
                "Incremental fetch dataset=%s updated_after=%s",
                dataset_name,
                updated_after,
            )

            records = fetch_dataset(
                config=config,
                dataset_name=dataset_name,
                logger=logger,
                updated_after=updated_after,
            )

            inserted_count = insert_dataset_records(
                connection=connection,
                schema_name=schema_name,
                dataset_name=dataset_name,
                records=records,
                batch_id=batch_id,
                source_system=source_system,
                ingested_at=ingested_at,
                logger=logger,
            )

            total_inserted += inserted_count

        connection.commit()

        logger.info("=" * 80)
        logger.info("INCREMENTAL INGESTION FINISHED SUCCESSFULLY")
        logger.info("total_inserted=%s", total_inserted)
        logger.info("batch_id=%s", batch_id)
        logger.info("=" * 80)

    except Exception:
        connection.rollback()
        logger.exception("INCREMENTAL INGESTION FAILED. Transaction rolled back.")
        raise

    finally:
        connection.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Ecommerce API to PostgreSQL raw ingestion")
    parser.add_argument(
        "--mode",
        choices=["full_refresh", "incremental"],
        default=None,
        help="Ingestion mode. Default reads from config/settings.yml",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_app_config()

    mode = args.mode or config["ingestion"]["mode"]

    if mode == "full_refresh":
        run_full_refresh(config)

    elif mode == "incremental":
        run_incremental(config)

    else:
        raise ValueError(f"Unsupported ingestion mode: {mode}")


if __name__ == "__main__":
    main()