from google.oauth2 import service_account
from googleapiclient.discovery import build
from functools import lru_cache

@lru_cache(maxsize=1)
def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        "./backend/secrets/service-account.json",
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    ) # Authorizing through service account

    return build("drive", "v3", credentials=credentials) # kinda like log in to drive using my service account

  # i am returning this object with caching layer