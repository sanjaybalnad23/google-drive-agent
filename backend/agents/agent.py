from langchain.agents import create_agent
from agents.prompts import SYSTEM_PROMPT
import config

_agent = create_agent(
        model=config.MODEL,
        tools=[],
        system_prompt=SYSTEM_PROMPT
)

def getAgent():
    return _agent