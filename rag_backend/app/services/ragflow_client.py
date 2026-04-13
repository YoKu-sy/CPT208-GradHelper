from functools import lru_cache

from ragflow_sdk import RAGFlow
from ragflow_sdk.modules.dataset import DataSet

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import get_logger
from app.utils.retry import retry_call

logger = get_logger(__name__)


class RAGFlowClient:
    def __init__(self, api_key: str, base_url: str) -> None:
        self._client = RAGFlow(api_key=api_key, base_url=base_url)
        self._base_url = base_url

    @property
    def sdk(self) -> RAGFlow:
        return self._client

    def get_or_create_dataset(self, dataset_name: str) -> DataSet:
        settings = get_settings()
        datasets = retry_call(
            lambda: self._client.list_datasets(page=1, page_size=100),
            attempts=settings.ragflow_retry_attempts,
            delay_seconds=settings.ragflow_retry_delay_seconds,
            error_message="Failed to list datasets from RAGFlow",
            error_code="RAGFLOW_DATASET_LIST_FAILED",
        )

        for dataset in datasets:
            if dataset.name.lower() == dataset_name.lower():
                logger.info("Using existing dataset '%s' (%s)", dataset.name, dataset.id)
                return dataset

        try:
            return self._client.create_dataset(name=dataset_name)
        except Exception as exc:
            try:
                datasets = self._client.list_datasets(page=1, page_size=100)
                for dataset in datasets:
                    if dataset.name.lower() == dataset_name.lower():
                        return dataset
            except Exception:
                pass

            raise AppError(
                message=f"Failed to create dataset '{dataset_name}': {exc}",
                status_code=502,
                code="RAGFLOW_DATASET_CREATE_FAILED",
            ) from exc

    def health_check(self) -> dict[str, object]:
        settings = get_settings()
        datasets = retry_call(
            lambda: self._client.list_datasets(page=1, page_size=settings.ragflow_health_page_size),
            attempts=settings.ragflow_retry_attempts,
            delay_seconds=settings.ragflow_retry_delay_seconds,
            error_message="RAGFlow is unreachable",
            error_code="RAGFLOW_UNAVAILABLE",
            status_code=503,
        )

        return {
            "status": "ok",
            "ragflow_base_url": self._base_url,
            "dataset_count_sample": len(datasets),
        }


@lru_cache
def get_ragflow_client() -> RAGFlowClient:
    settings = get_settings()
    return RAGFlowClient(api_key=settings.ragflow_api_key, base_url=settings.ragflow_base_url)
