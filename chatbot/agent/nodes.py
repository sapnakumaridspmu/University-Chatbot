from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from llm_factory import get_llm
from .state import GraphState
from .tools import TOOLS, web_search_tool
from .prompts import build_system_prompt

# Bind tools to the LLM once at import time
_llm = get_llm().bind_tools(TOOLS)

# ToolNode reads tool_calls from the last AIMessage,
# executes each tool, and appends ToolMessages to state.
tool_node = ToolNode(tools=TOOLS)

# Prompt always matches the tools that are really bound (no phantom tools).
SYSTEM_PROMPT = build_system_prompt(has_web_search=web_search_tool is not None)


def agent_node(state: GraphState) -> GraphState:
    """
    Core reasoning node.
    Prepends the system prompt, invokes the LLM with bound tools,
    and returns the response message to be appended to state.
    """
    system = SystemMessage(content=SYSTEM_PROMPT)
    response = _llm.invoke([system] + state["messages"])
    return {"messages": [response]}
