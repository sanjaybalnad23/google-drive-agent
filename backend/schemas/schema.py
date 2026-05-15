from pydantic import BaseModel, Field
from typing import List, Optional, Any


# ___________________________________________________________________
# Schema class related to agent


class ModelOutput(BaseModel):
    filename_contains_any: List[str] = Field(
        default_factory=list,
        description="File name can contain ANY of these words"
    )

    filename_contains_all: List[str] = Field(
        default_factory=list,
        description="File name must contain ALL of these words"
    )

    contains_text_any: List[str] = Field(
        default_factory=list,
        description="File content can contain ANY of these words"
    )

    contains_text_all: List[str] = Field(
        default_factory=list,
        description="File content must contain ALL of these words"
    )

    file_type: Optional[str] = Field(
        default=None,
        description="Type of file like pdf, doc, sheet, image, ppt"
    )

    modified_after: Optional[str] = Field(
        default=None,
        description="Only include files modified after this date (YYYY-MM-DD)"
    )

    modified_before: Optional[str] = Field(
        default=None,
        description="Only include files modified before this date (YYYY-MM-DD)"
    )

    is_recent: bool = Field(
        default=False,
        description="Whether user is asking for recent/latest files"
    )

# ____________________________________________________________________________
# Schema class related to fastapi (request and response)

# TODO : Implement these class later
class ApiResponse(BaseModel):
    success:bool
    message:str
    data:Any


# THis can be thrown anywhere in backend throughout the application . Global exception handler will handle
class ApiException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error: bool = True
    ):
        self.message = message
        self.status_code = status_code
        self.error = error

# Request type for "/chat" route. It should be in this format
class ChatRequest(BaseModel):
    folder_link:str
    user_query:str