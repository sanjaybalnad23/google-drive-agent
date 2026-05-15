import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/agent"


def search_drive(folder_link: str, query: str):
    payload = {
        "folder_link": folder_link,
        "user_query": query
    }

    response = requests.post(API_URL, json=payload)

    return response.json()


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
            st.error(data["message"])


if __name__ == "__main__":
    main()