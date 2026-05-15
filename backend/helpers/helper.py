# Helper functions used throughout backend application :)


from urllib.parse import urlparse

def extract_google_drive_folder_id(url):
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

