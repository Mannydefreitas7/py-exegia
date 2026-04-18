"""
Context-Fabric Corpus Manager

Manages Text-Fabric datasets for biblical text analysis.
Handles loading, caching, and querying of corpus data.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from tf.fabric import Fabric

logger = logging.getLogger(__name__)


class CorpusManager:
    """
    Manages Text-Fabric corpus datasets.

    Handles loading, caching, and basic operations on biblical text corpora.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the corpus manager.

        Args:
            base_path: Base directory where datasets are stored locally
        """
        self.base_path = base_path or Path.home() / ".biblepedia" / "datasets"
        self._loaded_corpora: Dict[str, Fabric] = {}

        # Ensure base path exists
        self.base_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Corpus manager initialized with base path: {self.base_path}")

    def load_corpus(self, dataset_id: str, local_path: Optional[Path] = None) -> Fabric:
        """
        Load a Text-Fabric corpus.

        Args:
            dataset_id: Unique identifier for the dataset (e.g., "KJV", "BHSA")
            local_path: Optional custom path to the dataset

        Returns:
            Loaded Fabric corpus object

        Raises:
            FileNotFoundError: If dataset path doesn't exist
            ValueError: If dataset is invalid or corrupted
        """
        # Return cached corpus if already loaded
        if dataset_id in self._loaded_corpora:
            logger.debug(f"Returning cached corpus: {dataset_id}")
            return self._loaded_corpora[dataset_id]

        # Determine corpus path
        corpus_path = local_path or (self.base_path / dataset_id)

        if not corpus_path.exists():
            raise FileNotFoundError(
                f"Dataset '{dataset_id}' not found at path: {corpus_path}"
            )

        try:
            # Initialize Fabric with the dataset
            logger.info(f"Loading corpus: {dataset_id} from {corpus_path}")
            tf_api = Fabric(locations=str(corpus_path))

            # Load the corpus
            # This will load all .tf files in the directory
            api = tf_api.load("")

            # Cache the loaded corpus
            self._loaded_corpora[dataset_id] = api

            logger.info(f"Successfully loaded corpus: {dataset_id}")
            return api

        except Exception as e:
            logger.error(f"Failed to load corpus '{dataset_id}': {e}")
            raise ValueError(f"Invalid or corrupted dataset '{dataset_id}': {e}")

    def unload_corpus(self, dataset_id: str) -> bool:
        """
        Unload a corpus from memory.

        Args:
            dataset_id: Dataset identifier to unload

        Returns:
            True if corpus was unloaded, False if not found
        """
        if dataset_id in self._loaded_corpora:
            del self._loaded_corpora[dataset_id]
            logger.info(f"Unloaded corpus: {dataset_id}")
            return True

        logger.warning(f"Corpus not loaded: {dataset_id}")
        return False

    def is_loaded(self, dataset_id: str) -> bool:
        """Check if a corpus is currently loaded."""
        return dataset_id in self._loaded_corpora

    def list_loaded(self) -> List[str]:
        """Get list of currently loaded corpus IDs."""
        return list(self._loaded_corpora.keys())

    def list_available(self) -> List[Dict[str, Any]]:
        """
        List all available datasets in the base path.

        Returns:
            List of dataset information dictionaries
        """
        available = []

        if not self.base_path.exists():
            return available

        for dataset_dir in self.base_path.iterdir():
            if dataset_dir.is_dir():
                # Check if it contains .tf files (Text-Fabric dataset)
                tf_files = list(dataset_dir.glob("**/*.tf"))

                if tf_files:
                    available.append(
                        {
                            "id": dataset_dir.name,
                            "path": str(dataset_dir),
                            "is_loaded": self.is_loaded(dataset_dir.name),
                            "file_count": len(tf_files),
                        }
                    )

        return available

    def get_corpus(self, dataset_id: str) -> Optional[Fabric]:
        """
        Get a loaded corpus by ID.

        Args:
            dataset_id: Dataset identifier

        Returns:
            Fabric API object or None if not loaded
        """
        return self._loaded_corpora.get(dataset_id)

    def clear_cache(self):
        """Unload all corpora from memory."""
        count = len(self._loaded_corpora)
        self._loaded_corpora.clear()
        logger.info(f"Cleared corpus cache ({count} corpora unloaded)")


# Global instance
_corpus_manager: Optional[CorpusManager] = None


def get_corpus_manager(base_path: Optional[Path] = None) -> CorpusManager:
    """
    Get or create the global corpus manager instance.

    Args:
        base_path: Optional base path for datasets

    Returns:
        Global CorpusManager instance
    """
    global _corpus_manager

    if _corpus_manager is None:
        _corpus_manager = CorpusManager(base_path)

    return _corpus_manager
