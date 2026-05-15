from datetime import datetime
from langchain.tools import tool

@tool(
    "get_current_timestamp", 
    description="Returns current timestamps in (Year-Month-Day Hour:Minute:Second) format, No args required. ALWAYS use it whenever user asks day, month, date or time related question to get more context on time. YOU MUST, even though calling is a waste"
)
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")