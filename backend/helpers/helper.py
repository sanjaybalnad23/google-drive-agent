# Helper functions used throughout backend application :)

from backend.schemas.schema import ModelOutput

def get_folder_id(url):
    """
    Extract the folder ID from a Google Drive folder URL.

    Args:
        url (str): Google Drive folder URL.

    Returns:
        str | None:
            Returns the folder ID if found,
            otherwise returns None.

    Example:
        >>> url = "https://drive.google.com/drive/folders/EXAMPLE_FOLDER_ID"
        >>> extract_google_drive_folder_id(url)
        'EXAMPLE_FOLDER_ID'
    """

    
    try:
        # Split using '/folders/'
        if "/folders/" in url:
            folder_id = url.split("/folders/")[1].split("?")[0]
            return folder_id
        else:
            return None
    except Exception:
        return None



MIME_TYPE_MAP = {
    "pdf": "application/pdf",
    "doc": "application/vnd.google-apps.document",
    "sheet": "application/vnd.google-apps.spreadsheet",
    "ppt": "application/vnd.google-apps.presentation",
    "image": "image/"
}

GOOGLE_FOLDER_MIME = "application/vnd.google-apps.folder"


def _escape_drive_q_value(value: str) -> str:
    """Escape \\ and ' for Google Drive API q string literals."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _quoted(value: str) -> str:
    return f"'{_escape_drive_q_value(value)}'"


def _build_file_filter_parts(filters: ModelOutput) -> list[str]:
    query_parts = ["trashed=false"]

    if filters.filename_contains_any:
        any_conditions = [
            f"name contains {_quoted(word)}" for word in filters.filename_contains_any
        ]
        query_parts.append(f"({' or '.join(any_conditions)})")

    if filters.filename_contains_all:
        all_conditions = [
            f"name contains {_quoted(word)}" for word in filters.filename_contains_all
        ]
        query_parts.append(f"({' and '.join(all_conditions)})")

    if filters.contains_text_any:
        any_conditions = [
            f"fullText contains {_quoted(word)}" for word in filters.contains_text_any
        ]
        query_parts.append(f"({' or '.join(any_conditions)})")

    if filters.contains_text_all:
        all_conditions = [
            f"fullText contains {_quoted(word)}" for word in filters.contains_text_all
        ]
        query_parts.append(f"({' and '.join(all_conditions)})")

    if filters.file_type:
        mime = MIME_TYPE_MAP.get(filters.file_type)
        if mime:
            if filters.file_type == "image":
                query_parts.append(f"mimeType contains {_quoted(mime)}")
            else:
                query_parts.append(f"mimeType={_quoted(mime)}")

    if filters.modified_after:
        query_parts.append(
            f"modifiedTime > {_quoted(f'{filters.modified_after}T00:00:00')}"
        )

    if filters.modified_before:
        query_parts.append(
            f"modifiedTime < {_quoted(f'{filters.modified_before}T23:59:59')}"
        )

    query_parts.append(f"mimeType != {_quoted(GOOGLE_FOLDER_MIME)}")

    return query_parts


def get_file_filters_query(filters: ModelOutput) -> str:
    """Drive query for file filters only (no folder parent clause)."""
    return "\nand ".join(_build_file_filter_parts(filters))


def get_query(filters: ModelOutput, folder_id: str) -> str:
    """
    Generate a Google Drive search query string from structured filters.

    Restricts search to direct children of `folder_id`. For recursive search,
    use `backend.google_drive.search.search_files_recursive`.
    """
    if not folder_id:
        raise ValueError("Provide folder id")

    parts = [f"{_quoted(folder_id)} in parents", *_build_file_filter_parts(filters)]
    return "\nand ".join(parts)