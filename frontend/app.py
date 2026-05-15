import os

import dotenv
import requests
import streamlit as st

dotenv.load_dotenv()

DEFAULT_API_URL = "http://127.0.0.1:8000/agent"


def get_api_url() -> str:
    try:
        return st.secrets["API_URL"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("API_URL", DEFAULT_API_URL)


def search_drive(folder_link: str, query: str) -> dict:
    payload = {
        "folder_link": folder_link,
        "user_query": query,
    }

    try:
        response = requests.post(get_api_url(), json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"success": False, "message": f"Could not reach API: {e}"}


def render_file(file: dict):

    st.subheader(file["name"])

    st.caption(file["mimeType"])

    st.markdown(
        f"[Open File]({file['webViewLink']})"
    )

    st.divider()


def main():

    st.set_page_config(
        page_title="Drive AI Search",
        layout="wide"
    )

    st.title("Drive AI Search")

    folder_link = st.text_input(
        "Google Drive Folder Link"
    )

    query = st.text_input(
        "Search Query"
    )

    if st.button("Search"):

        with st.spinner("Searching..."):

            data = search_drive(
                folder_link,
                query
            )

        if data.get("success"):

            files = data["data"]

            st.success(data["message"])

            if not files:
                st.warning("No matching files found")

            for file in files:
                render_file(file)

        else:
            st.error(data.get("message", "Something went wrong"))


if __name__ == "__main__":
    main()