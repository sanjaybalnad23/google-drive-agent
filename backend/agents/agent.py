from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from agents.prompts import SYSTEM_PROMPT
from schemas.schema import ModelOutput
from functools import lru_cache
import config


@lru_cache(maxsize=1)
def getAgent():
    return  create_agent(
            model=config.MODEL, # Choose google model
            # tools=[], # In our case no need of tool 
            system_prompt=SYSTEM_PROMPT, # Sys Prompt to the model
            response_format=ToolStrategy(ModelOutput) # Output format for the model
    )
    


