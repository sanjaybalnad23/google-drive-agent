from pydantic import BaseModel


# ___________________________________________________________________
# Schema class related to agent


# TODO: Research on google drive api and write structured output for model
class ModelOutput(BaseModel):
    pass

# ____________________________________________________________________________
# Schema class related to fastapi (request and response)

# TODO : Implement these class later
class SuccessResponse(BaseModel):
    pass

class ErrorResponse(BaseModel):
    pass