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


def _escape_drive_q_value(value: str) -> str:
    """Escape \\ and ' for Google Drive API q string literals."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _quoted(value: str) -> str:
    return f"'{_escape_drive_q_value(value)}'"


def get_query(filters: ModelOutput, folder_id: str) -> str:
    """
    Generate a Google Drive search query string from structured filters.

    This function converts a `ModelOutput` object into a valid
    Google Drive API query (`q`) string that can be used with:

        drive_service.files().list(q=query)

    The generated query supports:
    - folder restriction
    - filename matching
    - content text matching
    - file type filtering
    - modified date filtering
    - excluding trashed files

    Args:
        filters (ModelOutput):
            Structured search filters extracted from the user query.

        folder_id (str):
            Google Drive folder ID used to restrict the search.

    Returns:
        str:
            A valid Google Drive API query string.

    Raises:
        ValueError:
            If `folder_id` is empty or not provided.

    Example:
        >>> filters = ModelOutput(
        ...     contains_text_any=["e2e", "agent"],
        ...     file_type="pdf"
        ... )

        >>> get_query(filters, "FOLDER_ID")
        OUPUTS:
        "'FOLDER_ID' in parents
        and trashed=false
        and (fullText contains 'e2e' or fullText contains 'agent')
        and mimeType='application/pdf'"
    """

    query_parts = []

    # Folder restriction
    if not folder_id:
        raise ValueError("Provide folder id")

    query_parts.append(f"{_quoted(folder_id)} in parents")

    # Ignore trashed files
    query_parts.append("trashed=false")

    # Filename contains ANY
    if filters.filename_contains_any:
        any_conditions = [
            f"name contains {_quoted(word)}" for word in filters.filename_contains_any
        ]
        query_parts.append(f"({' or '.join(any_conditions)})")

    # Filename contains ALL
    if filters.filename_contains_all:
        all_conditions = [
            f"name contains {_quoted(word)}"
            for word in filters.filename_contains_all
        ]
        query_parts.append(
            f"({' and '.join(all_conditions)})"
        )

    # Content contains ANY
    if filters.contains_text_any:
        any_conditions = [
            f"fullText contains {_quoted(word)}"
            for word in filters.contains_text_any
        ]
        query_parts.append(
            f"({' or '.join(any_conditions)})"
        )

    # Content contains ALL
    if filters.contains_text_all:
        all_conditions = [
            f"fullText contains {_quoted(word)}"
            for word in filters.contains_text_all
        ]
        query_parts.append(
            f"({' and '.join(all_conditions)})"
        )


    # File type
    if filters.file_type:
        mime = MIME_TYPE_MAP.get(filters.file_type)
        if mime:
            # image/ is special because many image mime types exist
            if filters.file_type == "image":
                query_parts.append(
                    f"mimeType contains {_quoted(mime)}"
                )
            else:
                query_parts.append(
                    f"mimeType={_quoted(mime)}"
                )


    # Modified after
    if filters.modified_after:
        query_parts.append(
            f"modifiedTime > {_quoted(f'{filters.modified_after}T00:00:00')}"
        )

    # Modified before
    if filters.modified_before:
        query_parts.append(
            f"modifiedTime < {_quoted(f'{filters.modified_before}T23:59:59')}"
        )

    # print(query_parts) 

    final_query = "\nand ".join(query_parts)

    return final_query