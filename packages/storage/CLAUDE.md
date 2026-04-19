# Storage Service Module

Supabase Storage integration for managing dataset files (Bibles, lexicons, dictionaries, reference books).

## Overview

This module handles downloading, uploading, and managing Text-Fabric dataset files stored in Supabase Storage buckets.

## Architecture

```
Client Request
    ↓
Storage Service (datasets.py)
    ↓
Supabase Storage API
    ↓
Buckets (bibles/, lexicons/, etc.)
```

## Files

```
app/storage/
├── datasets.py      # Dataset download/upload operations
└── git_fetch.py     # Git repository fetching for TF datasets
```

## Supabase Storage Buckets

### Organization

```
storage/
├── bibles/              # Bible translations (KJV, ESV, BHSA, etc.)
│   ├── KJV.zip
│   ├── ESV.zip
│   ├── BHSA.zip
│   └── ...
├── books/               # Biblical reference books
│   ├── bible-dictionary.zip
│   └── ...
├── lexicons/            # Hebrew/Greek lexicons
│   ├── BDB.zip          # Brown-Driver-Briggs
│   ├── HALOT.zip
│   └── ...
└── dictionaries/        # Bible dictionaries
    └── ...
```

## Dataset Operations

### List Datasets

```python
from app.storage.datasets import list_datasets

datasets = await list_datasets(category="bibles")
# Returns: [
#   {"id": "KJV", "name": "King James Version", "size": 1234567, ...},
#   ...
# ]
```

### Download Dataset

```python
from app.storage.datasets import download_dataset

# Download to local path
local_path = await download_dataset(
    dataset_id="BHSA",
    category="bibles",
    destination="/app/datasets/BHSA"
)

# Returns path to extracted dataset
# /app/datasets/BHSA/.tf/ (Text-Fabric files)
```

### Upload Dataset

```python
from app.storage.datasets import upload_dataset

# Upload from local zip file
await upload_dataset(
    file_path="/path/to/dataset.zip",
    dataset_id="MyDataset",
    category="bibles"
)
```

### Get Dataset Metadata

```python
from app.storage.datasets import get_dataset_info

info = await get_dataset_info(dataset_id="BHSA", category="bibles")
# Returns: {
#   "id": "BHSA",
#   "name": "Biblia Hebraica Stuttgartensia Amstelodamensis",
#   "language": "Hebrew",
#   "version": "2021",
#   "size": 45678901,
#   "created_at": "2024-01-01T00:00:00Z"
# }
```

## Git Repository Fetching (`git_fetch.py`)

For datasets hosted in Git repositories (Text-Fabric datasets):

```python
from app.storage.git_fetch import fetch_tf_dataset

# Fetch dataset from GitHub
await fetch_tf_dataset(
    repo_url="https://github.com/ETCBC/bhsa",
    dataset_id="BHSA",
    version="2021"
)

# Automatically:
# 1. Clones repository
# 2. Extracts .tf files
# 3. Zips dataset
# 4. Uploads to Supabase Storage
```

## Storage Service Interface

```python
class DatasetStorageService:
    """Manages dataset files in Supabase Storage"""

    def __init__(self, supabase_client):
        self.storage = supabase_client.storage

    async def list(self, category: str) -> List[DatasetMetadata]:
        """List all datasets in a category"""

    async def download(self, dataset_id: str, category: str) -> bytes:
        """Download dataset ZIP file"""

    async def upload(self, file: bytes, dataset_id: str, category: str):
        """Upload dataset ZIP file"""

    async def delete(self, dataset_id: str, category: str):
        """Delete dataset from storage"""

    async def get_metadata(self, dataset_id: str, category: str) -> dict:
        """Get dataset metadata"""
```

## Dataset Format

Datasets are stored as ZIP files containing Text-Fabric format:

```
dataset.zip
└── .tf/                    # Text-Fabric directory
    ├── otype.tf            # Node types
    ├── oslots.tf           # Slot mapping
    ├── pos.tf              # Part of speech
    ├── lemma.tf            # Lemmas
    ├── ...                 # Other features
    └── tfconfig.yaml       # Corpus metadata
```

## User Workflow

1. **Browse datasets**: User queries available datasets via GraphQL
2. **Download dataset**: Client downloads ZIP from Supabase Storage
3. **Extract locally**: Client extracts to specified path
4. **Mark as downloaded**: Update user_datasets table
5. **Query corpus**: Dataset available for Context-Fabric queries

## Storage API Examples

### Supabase Python Client

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# List files
files = supabase.storage.from_('bibles').list()

# Download file
data = supabase.storage.from_('bibles').download('KJV.zip')

# Upload file
supabase.storage.from_('bibles').upload('ESV.zip', file_bytes)

# Delete file
supabase.storage.from_('bibles').remove(['old-dataset.zip'])

# Get public URL
url = supabase.storage.from_('bibles').get_public_url('KJV.zip')
```

## Access Control

Buckets use Row Level Security (RLS):

- **Public read**: All users can list and download datasets
- **Authenticated upload**: Only authenticated users can upload
- **Admin delete**: Only admins can delete datasets

## Performance Considerations

- **Large files**: Use streaming downloads for datasets > 100MB
- **Resumable uploads**: Support resumable uploads for large files
- **CDN**: Supabase Storage uses CDN for fast global access
- **Compression**: All datasets stored as ZIP files

## Error Handling

```python
try:
    dataset = await download_dataset("BHSA", "bibles")
except DatasetNotFoundError:
    # Dataset doesn't exist
    pass
except StorageError as e:
    # Storage service error
    pass
except NetworkError as e:
    # Network error during download
    pass
```

## Testing

```python
# Test dataset operations
async def test_download():
    path = await download_dataset("test-dataset", "bibles")
    assert path.exists()
    assert (path / ".tf").is_dir()

async def test_upload():
    await upload_dataset("/tmp/test.zip", "test-dataset", "bibles")
    files = await list_datasets("bibles")
    assert "test-dataset" in [f["id"] for f in files]
```

## Related Documentation

- @src/models/CLAUDE.md) - user_datasets table
- @src/graphql/CLAUDE.md) - Dataset queries
