from fastapi import FastAPI
from fastapi.responses import JSONResponse
from backend.agents.agent import get_agent
from backend.schemas.schema import ChatRequest, ApiException, ApiResponse
from backend.google_drive.drive import get_drive_service
from backend.helpers.helper import get_folder_id, get_query
from googleapiclient.errors import HttpError

app = FastAPI()


@app.exception_handler(ApiException)
async def exception_handler(req, exception:ApiException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": exception.error,
            "message": exception.message,
            "status": exception.status_code
        }
    )

@app.post("/agent", response_model=ApiResponse)
def handle_agent_request(req:ChatRequest):
    try:
        agent = get_agent()
        drive_service = get_drive_service()

        folder_name = get_folder_id(req.folder_link)
        if not folder_name:
            raise ApiException("Give proper folder link")

        if not req.user_query:
            raise ApiException("Search something")

        model_response = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": req.user_query
                }
            ]
        })
        
        structured_response = model_response["structured_response"]
        query = get_query(structured_response, folder_name)

        results = drive_service.files().list(
            q=query,
            fields="files(id,name,mimeType,webViewLink)"
        ).execute()

        if not len(results["files"]):
            raise ApiException("Unable to fetch file or folder has restricted access")

        return ApiResponse(success=True, message="Fetched successfully",data=results["files"])

    except ApiException as e:
        raise e

    except HttpError as e:
        raise ApiException(e.reason, e.status_code)

    except Exception as e:
        raise ApiException(str(e),500,True)


