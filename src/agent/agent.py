from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from src.agent.prompt import SYSTEM_PROMPT
from src.mcp.client import load_mcp_tools
from src.utils.env import OLLAMA_BASE_URL, OLLAMA_MODEL


async def agent_call(question):
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    tools = await load_mcp_tools()
    agent = create_agent(llm, tools)

    response = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ]
        }
    )

    return response["messages"][-1].content
