"""Helpers for cleaning up documents stored using the legacy on-disk format.

Documents created after the migration to in-memory processing use a
`memory://` reference and have nothing to remove from disk. Older
documents may still point to a real file path, which this helper
removes safely.
"""

from pathlib import Path


def remove_if_exists(file_path: str) -> None:
    """Remove a legacy on-disk file if it exists. No-op for other references.

    Args:
        file_path: Stored file reference (may be a `memory://` URL or a
            real filesystem path from before the in-memory migration).
    """
    path = Path(file_path)
    if path.is_file():
        path.unlink(missing_ok=True)
