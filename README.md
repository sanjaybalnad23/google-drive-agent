# Google Drive AI Search

Search a Google Drive folder using plain English. Paste a folder link, type what you want (for example *"recent invoice PDFs"*), and get back matching files — even if they live in subfolders.

---

## How it works

Here is the flow in simple terms:

```
Client
  │
  │  sends: folder link + user query
  ▼
Server (FastAPI)
  │
  │  Agent (Gemini) — see below
  ▼
  Query builder + Drive search
  │
  │  Because Drive cannot "search all subfolders" in one shot,
  │  the server finds every subfolder under your folder,
  │  builds a Drive search query for each one,
  │  runs them, and combines the results.
  ▼
  List of matching files
  │
  ▼
Client  (names, types, links)
```

**In one line:** you ask in English → the server understands it → runs several Drive searches (one per folder in the tree) → sends the files back.

### The agent (what it actually does)

The agent is **not** browsing Drive or picking files by itself. It only **reads your sentence** and fills out a small form (JSON) that the rest of the backend understands.

**You send something like:**

```text
user_query: "Find recent PDF reports with invoice in the name"
```

**The agent returns structured filters, for example:**

```json
{
  "filename_contains_any": ["invoice"],
  "filename_contains_all": [],
  "contains_text_any": [],
  "contains_text_all": [],
  "file_type": "pdf",
  "modified_after": null,
  "modified_before": null,
  "is_recent": true
}
```

What that means in plain English:

- look for **PDF** files
- filename should mention **invoice**
- user asked for something **recent** (dates get filled using a timestamp tool when needed)

Another example:

```text
user_query: "documents that mention e2e or agent, uploaded after March 1 2025"
```

Might become:

```json
{
  "filename_contains_any": [],
  "filename_contains_all": [],
  "contains_text_any": ["e2e", "agent"],
  "contains_text_all": [],
  "file_type": null,
  "modified_after": "2025-03-01",
  "modified_before": null,
  "is_recent": false
}
```

Here the words **e2e** / **agent** apply to **file content**, not the filename.

After that, the **query builder** turns this JSON into real Google Drive search strings. The agent never writes those strings directly — that keeps searches safer and more predictable.

---

## What you need (Google Cloud)

You need a **service account** in Google Cloud with the **Google Drive API enabled**.

Rough steps:

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Google Drive API** for that project.
3. Create a **Service Account** and download its JSON key.
4. Save that file as:

   ```
   backend/secrets/service-account.json
   ```

   (Create the `secrets` folder if it does not exist. **Do not commit this file to git.**)

5. Open the JSON and copy the `client_email` (looks like `something@project-id.iam.gserviceaccount.com`).
6. In Google Drive, **share your target folder** with that email — Viewer access is enough.

Without step 6, the API cannot see your files.

You also need a **Gemini API key** for the agent (see `.env` below).

---

## Run locally

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/getting-started/installation/)

### 1. Install dependencies

```bash
git clone <your-repo-url>
cd google-drive-agent
uv sync
```

### 2. Create `.env` in the project root

```env
GEMINI_API_KEY=your_gemini_api_key_here
MODEL=gemini-2.0-flash
```

- `GEMINI_API_KEY` — from [Google AI Studio](https://aistudio.google.com/apikey)
- `MODEL` — Gemini model name your LangChain setup expects

### 3. Put the service account key in place

```
backend/secrets/service-account.json
```

Share your Drive folder with the service account email (see above).

### 4. Start the backend

Run from the **project root** (the folder that contains `backend/` and `pyproject.toml`):

```bash
uv run uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Docs: http://127.0.0.1:8000/docs

### 5. (Optional) Start the Streamlit UI

Second terminal, same folder:

```bash
uv run streamlit run frontend/app.py
```

It calls `http://127.0.0.1:8000/agent` by default.

---

## API example

**POST** `http://127.0.0.1:8000/agent`

```json
{
  "folder_link": "https://drive.google.com/drive/folders/YOUR_FOLDER_ID",
  "user_query": "Find recent PDF files about invoices"
}
```

---

## Project layout (quick)

| Path | Purpose |
|------|---------|
| `backend/app.py` | API server |
| `backend/agents/` | LangChain agent + prompts |
| `backend/helpers/helper.py` | Build Drive search queries |
| `backend/google_drive/search.py` | Subfolder walk + run searches |
| `backend/secrets/service-account.json` | Your key (you add this) |
| `frontend/app.py` | Streamlit UI |

---

## Notes

- No database — each search is a fresh request.
- Large folder trees are limited to 200 subfolders per search (see `MAX_FOLDERS` in `backend/google_drive/search.py`).
- CORS is on if you call the API from a browser app on another host.
