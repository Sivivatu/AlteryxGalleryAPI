"""
File handling utilities for API operations.
"""

from pathlib import Path
from typing import BinaryIO, Tuple


def open_file_for_upload(file_path: str) -> Tuple[str, BinaryIO, str]:
    """Open a file for upload to the API.

    Args:
        file_path: Path to the file to upload

    Returns:
        Tuple of (filename, file_object, content_type)

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file is empty
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    file_size = path.stat().st_size
    if file_size == 0:
        raise ValueError(f"File is empty: {file_path}")

    filename = path.name
    file_object = open(path, "rb")

    return filename, file_object, get_content_type(filename)


def get_content_type(filename: str) -> str:
    """Get MIME content type for a filename.

    Args:
        filename: Name of the file

    Returns:
        Content type string
    """
    ext = Path(filename).suffix.lower()

    content_types = {
        ".yxzp": "application/zip",
        ".yxmd": "application/xml",
        ".yxwz": "application/zip",
        ".yxdb": "application/x-yxdb",
        ".csv": "text/csv",
        ".txt": "text/plain",
        ".json": "application/json",
        ".pdf": "application/pdf",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
    }

    return content_types.get(ext, "application/octet-stream")


def validate_file_size(file_path: str, max_size_mb: int = 500) -> None:
    """Validate file size against maximum allowed size.

    Args:
        file_path: Path to the file
        max_size_mb: Maximum file size in megabytes. Defaults to 500.

    Raises:
        ValueError: If file exceeds maximum size
    """
    path = Path(file_path)
    size_bytes = path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    if size_mb > max_size_mb:
        raise ValueError(f"File size ({size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)")
