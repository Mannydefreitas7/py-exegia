import logging
from pathlib import Path
from typing import Optional

import strawberry

from src.config import settings
from src.graphql.types.dataset import (
    Dataset,
    DatasetCategory,
    DatasetDownloadResult,
    DatasetInfo,
    DatasetList,
    DatasetUploadResult,
    DeleteDatasetInput,
    DownloadDatasetInput,
    LocalDataset,
    LocalDatasetList,
    SyncDatasetInput,
    UploadDatasetInput,
)

logger = logging.getLogger(__name__)

_BUCKET_NAMES = {
    "bibles": "bibles",
    "books": "books",
    "lexicons": "lexicons",
    "dictionaries": "dictionaries",
}


def _supabase_client():
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return None
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def _storage_service():
    client = _supabase_client()
    if client is None:
        return None
    from src.storage.datasets import DatasetStorageService
    return DatasetStorageService(client, Path(settings.datasets_base_path))


def _list_local_datasets_from_path(base_path: Path, category_filter: Optional[str] = None):
    results = []
    if not base_path.exists():
        return results
    for category_dir in base_path.iterdir():
        if not category_dir.is_dir() or category_dir.name not in _BUCKET_NAMES:
            continue
        if category_filter and category_dir.name != category_filter:
            continue
        for dataset_dir in category_dir.iterdir():
            if not dataset_dir.is_dir():
                continue
            tf_files = list(dataset_dir.glob("**/*.tf"))
            if tf_files:
                results.append({
                    "id": dataset_dir.name,
                    "category": category_dir.name,
                    "path": str(dataset_dir),
                    "file_count": len(tf_files),
                    "size": sum(f.stat().st_size for f in dataset_dir.rglob("*") if f.is_file()),
                })
    return results


async def resolve_datasets(
    category: Optional[DatasetCategory], search: Optional[str]
) -> DatasetList:
    service = _storage_service()
    if service is None:
        return DatasetList(datasets=[], total=0, category=category)

    category_str = category.value if category else None
    raw = await service.list_datasets(category_str, search)

    datasets = [
        Dataset(
            id=d["id"],
            name=d["name"],
            category=DatasetCategory(d["category"]),
            bucket=d["bucket"],
            size=d.get("size") or 0,
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
            metadata=d.get("metadata"),
        )
        for d in raw
    ]
    return DatasetList(datasets=datasets, total=len(datasets), category=category)


async def resolve_dataset(
    dataset_id: str, category: DatasetCategory
) -> Optional[DatasetInfo]:
    service = _storage_service()
    if service is None:
        return None

    info = await service.get_dataset_info(dataset_id, category.value)
    if not info:
        return None

    return DatasetInfo(
        id=info["id"],
        name=info["name"],
        category=DatasetCategory(info["category"]),
        size=info.get("size") or 0,
        created_at=info.get("created_at"),
        updated_at=info.get("updated_at"),
    )


async def resolve_local_datasets(category: Optional[DatasetCategory]) -> LocalDatasetList:
    base_path = Path(settings.datasets_base_path)
    category_str = category.value if category else None
    raw = _list_local_datasets_from_path(base_path, category_str)

    datasets = [
        LocalDataset(
            id=d["id"],
            category=DatasetCategory(d["category"]),
            path=d["path"],
            file_count=d["file_count"],
            size=d["size"],
        )
        for d in raw
    ]
    return LocalDatasetList(datasets=datasets, total=len(datasets))


async def resolve_local_dataset(
    dataset_id: str, category: DatasetCategory
) -> Optional[LocalDataset]:
    result = await resolve_local_datasets(category)
    return next((d for d in result.datasets if d.id == dataset_id), None)


async def resolve_download_dataset(
    info: strawberry.Info, input: DownloadDatasetInput
) -> DatasetDownloadResult:
    service = _storage_service()
    if service is None:
        return DatasetDownloadResult(
            success=False,
            dataset_id=input.dataset_id,
            category=input.category,
            error_message="Supabase not configured",
        )

    try:
        custom_path = Path(input.custom_path) if input.custom_path else None
        local_path = await service.download_dataset(
            input.dataset_id, input.category.value, custom_path, input.extract
        )
        return DatasetDownloadResult(
            success=True,
            dataset_id=input.dataset_id,
            category=input.category,
            local_path=str(local_path),
        )
    except Exception as e:
        logger.error("Download failed: %s", e)
        return DatasetDownloadResult(
            success=False,
            dataset_id=input.dataset_id,
            category=input.category,
            error_message=str(e),
        )


async def resolve_upload_dataset(
    info: strawberry.Info, input: UploadDatasetInput
) -> DatasetUploadResult:
    service = _storage_service()
    if service is None:
        return DatasetUploadResult(
            success=False,
            dataset_id=input.dataset_id,
            category=input.category,
            file_name=f"{input.dataset_id}.zip",
            size=0,
            uploaded=False,
            error_message="Supabase not configured",
        )

    try:
        result = await service.upload_dataset(
            Path(input.local_path), input.dataset_id, input.category.value, input.compress
        )
        return DatasetUploadResult(
            success=True,
            dataset_id=input.dataset_id,
            category=input.category,
            file_name=result["file_name"],
            size=result["size"],
            uploaded=result["uploaded"],
        )
    except Exception as e:
        logger.error("Upload failed: %s", e)
        return DatasetUploadResult(
            success=False,
            dataset_id=input.dataset_id,
            category=input.category,
            file_name=f"{input.dataset_id}.zip",
            size=0,
            uploaded=False,
            error_message=str(e),
        )


async def resolve_delete_dataset(
    info: strawberry.Info, input: DeleteDatasetInput
) -> bool:
    service = _storage_service()
    if service is None:
        return False
    return await service.delete_dataset(input.dataset_id, input.category.value)


async def resolve_sync_dataset(
    info: strawberry.Info, input: SyncDatasetInput
) -> bool:
    service = _storage_service()
    if service is None:
        return False
    return await service.sync_dataset(
        input.dataset_id, input.category.value, input.direction
    )
