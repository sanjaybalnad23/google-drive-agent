import logging

from backend.helpers.helper import (
    GOOGLE_FOLDER_MIME,
    _quoted,
    get_file_filters_query,
)
from backend.schemas.schema import ModelOutput

logger = logging.getLogger(__name__)

FILE_FIELDS = "files(id,name,mimeType,webViewLink)"
FILE_LIST_FIELDS = f"nextPageToken, {FILE_FIELDS}"
FOLDER_LIST_FIELDS = "nextPageToken, files(id)"
MAX_FOLDERS = 200


def collect_folder_ids(drive_service, root_folder_id: str, *, max_folders: int = MAX_FOLDERS) -> list[str]:
    """Return root_folder_id and all descendant folder IDs (breadth-first)."""
    seen: set[str] = {root_folder_id}
    queue = [root_folder_id]
    index = 0

    while index < len(queue):
        if len(seen) > max_folders:
            raise ValueError(
                f"Folder tree exceeds maximum of {max_folders} folders"
            )

        parent_id = queue[index]
        index += 1

        q = (
            f"{_quoted(parent_id)} in parents"
            f" and mimeType = {_quoted(GOOGLE_FOLDER_MIME)}"
            " and trashed=false"
        )
        page_token = None

        while True:
            response = drive_service.files().list(
                q=q,
                fields=FOLDER_LIST_FIELDS,
                pageSize=100,
                pageToken=page_token,
            ).execute()

            for item in response.get("files", []):
                folder_id = item["id"]
                if folder_id not in seen:
                    seen.add(folder_id)
                    queue.append(folder_id)

            page_token = response.get("nextPageToken")
            if not page_token:
                break

    return list(seen)


def _list_files(drive_service, query: str) -> list[dict]:
    files: list[dict] = []
    page_token = None

    while True:
        response = drive_service.files().list(
            q=query,
            fields=FILE_LIST_FIELDS,
            pageSize=100,
            pageToken=page_token,
        ).execute()

        files.extend(response.get("files", []))

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return files


def search_files_in_folders(
    drive_service,
    filters: ModelOutput,
    folder_ids: list[str],
) -> list[dict]:
    """Run one Drive search per folder and merge results (deduped by file id)."""
    base_query = get_file_filters_query(filters)
    seen_ids: set[str] = set()
    merged: list[dict] = []

    for folder_id in folder_ids:
        query = f"{base_query}\nand {_quoted(folder_id)} in parents"
        logger.info("Drive search in folder %s: %s", folder_id, query)

        for file in _list_files(drive_service, query):
            if file["id"] not in seen_ids:
                seen_ids.add(file["id"])
                merged.append(file)

    return merged


def search_files_recursive(
    drive_service,
    filters: ModelOutput,
    root_folder_id: str,
    *,
    max_folders: int = MAX_FOLDERS,
) -> list[dict]:
    """Search files in root_folder_id and all nested subfolders."""
    folder_ids = collect_folder_ids(
        drive_service, root_folder_id, max_folders=max_folders
    )
    logger.info("Searching %d folders recursively under %s", len(folder_ids), root_folder_id)
    return search_files_in_folders(drive_service, filters, folder_ids)
