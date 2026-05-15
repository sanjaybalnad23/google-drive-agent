from datetime import datetime
from langchain.tools import tool

@tool(
    "get_current_timestamp", 
    description="Returns current timestamps in  (Year-Month-Day Hour:Minute:Second) format, No args required"
)
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")