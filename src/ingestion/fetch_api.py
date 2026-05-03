from __future__ import annotations
from typing import Any
import requests
import logging


def check_api_health(
        base_url: str,
        timeout_seconds: int,
        logger: logging.Logger,
) -> None:
    url = f"{base_url}/health"

    logger.info("Checking API health: %s", url)

    response = requests.get(url, timeout=timeout_seconds)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "ok":
        raise RuntimeError(f"API health check failed. Response: {payload}")
    
    logger.info("API health check passed: %s", payload)


def fetch_paginated_endpoint(
        base_url: str,
        endpoint: str,
        page_limit: int,
        timeout_seconds: int,
        logger: logging.Logger,
        extra_params: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    offset = 0

    while True:
        params: dict[str, Any] = {
            "limit": page_limit,
            "offset": offset,
        }

        if extra_params:
            params.update(extra_params)

        url = f"{base_url}{endpoint}"

        logger.info("Fetching endpoint=%s offset=%s limit=%s", endpoint, offset, page_limit)

        response = requests.get(
            url,
            params=params,
            timeout=timeout_seconds,
        )
        response.raise_for_status()

        payload = response.json()
        data = payload.get("data", [])
        meta = payload.get("meta", {})

        if not isinstance(data, list):
            raise ValueError(f"Invalid API response. Expected data as list. Endpoint={endpoint}")
        
        returned = int(meta.get("returned", len(data)))
        total = meta.get("total")
        records.extend(data)

        logger.info(
            "Fetching endpoint=%s returned=%s total_so_far=%s api_total=%s",
            endpoint,
            returned,
            len(records),
            total,
        )

        if returned == 0:
            break

        offset += returned

        if total is not None and offset >= int(total):
            break

    return records


def fetch_dataset(
        config: dict[str, Any],
        dataset_name: str,
        logger: logging.Logger,
        updated_after: str | None = None,
) -> list[dict[str, Any]]:
    endpoints = config["api"]["endpoints"]

    if dataset_name not in endpoints:
        raise ValueError(f"Unknown dataset_name: {dataset_name}")

    extra_params: dict[str, Any] = {}

    if updated_after:
        extra_params["updated_after"] = updated_after

    return fetch_paginated_endpoint(
        base_url=config["api"]["base_url"],
        endpoint=endpoints[dataset_name],
        page_limit=int(config["api"]["page_limit"]),
        timeout_seconds=int(config["api"]["timeout_seconds"]),
        logger=logger,
        extra_params=extra_params,
    )


def fetch_all_datasets(
        config: dict[str, Any],
        logger: logging.Logger,
) -> dict[str, list[dict[str, Any]]]:
    check_api_health(
        base_url=config["api"]["base_url"],
        timeout_seconds=int(config["api"]["timeout_seconds"]),
        logger=logger,
    )

    datasets: dict[str, list[dict[str, Any]]] = {}

    for dataset_name in config["api"]["endpoints"]:
        records = fetch_dataset(
            config=config,
            dataset_name=dataset_name,
            logger=logger,
        )

        datasets[dataset_name] = records

        logger.info(
            "Dataset fetched successfully: dataset=%s row_count=%s",
            dataset_name,
            len(records),
        )

    return datasets