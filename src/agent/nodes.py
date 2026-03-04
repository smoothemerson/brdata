import json
from functools import partial

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage

from src.agent.prompts import SYSTEM_PROMPT
from src.agent.state import AgentState


async def agent_node(state: AgentState, llm_with_tools) -> dict:
    messages = state["messages"]

    # Prepend system prompt if this is the first call (no system message yet)
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


async def tool_node_with_tracking(state: AgentState, tool_node) -> dict:
    result = await tool_node.ainvoke(state)

    # Extract tool call records from the state and result
    messages = state["messages"]
    last_ai_message = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            last_ai_message = msg
            break

    tool_records = list(state.get("tools_called", []))

    if last_ai_message and hasattr(last_ai_message, "tool_calls"):
        tool_calls_map = {tc["id"]: tc for tc in last_ai_message.tool_calls}
        new_messages = result.get("messages", [])

        for msg in new_messages:
            if isinstance(msg, ToolMessage):
                tc = tool_calls_map.get(msg.tool_call_id, {})
                try:
                    parsed_result = json.loads(msg.content)
                except (json.JSONDecodeError, TypeError):
                    parsed_result = msg.content

                tool_records.append(
                    {
                        "tool_name": tc.get("name", "unknown"),
                        "params": tc.get("args", {}),
                        "result": parsed_result,
                        "error": None,
                    }
                )

    result["tools_called"] = tool_records
    return result


def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "__end__"


def make_agent_node(llm_with_tools):
    return partial(agent_node, llm_with_tools=llm_with_tools)


def make_tool_node_with_tracking(tool_node):
    return partial(tool_node_with_tracking, tool_node=tool_node)
