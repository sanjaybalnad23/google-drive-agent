from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from backend.agents.prompts import SYSTEM_PROMPT
from backend.schemas.schema import ModelOutput
from backend.agents.tools import get_current_timestamp
from functools import lru_cache
import config


@lru_cache(maxsize=1)
def get_agent():
    return  create_agent(
            model=config.MODEL, # Choose google model
            tools=[get_current_timestamp], # Tool that can be used by model to get current time
            system_prompt=SYSTEM_PROMPT, # Sys Prompt to the model
            response_format=ToolStrategy(ModelOutput) # Output format for the model
    )
    


