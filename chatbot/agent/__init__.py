import asyncio
from typing import Any, AsyncGenerator

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from .graph import graph

# Overall wall-clock budget for a single turn (LLM calls + tool calls + retries).
# Without this, a hung DB connection or unresponsive LLM provider makes the
# Streamlit UI spin forever with no feedback to the user.
RESPONSE_TIMEOUT_SECONDS = 60

# Hard cap on agent<->tools loop iterations. Prevents a runaway loop (e.g. the
# model repeatedly re-calling a failing tool) from silently stalling the chat.
RECURSION_LIMIT = 15


def _chunk_content_to_text(content: Any) -> str:
    """
    Normalize LLM stream `content` to a plain string.

    Google GenAI and other providers may emit list-shaped content blocks
    (e.g. [{"type": "text", "text": "..."}]) instead of a single string.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                t = block.get("text")
                if isinstance(t, str):
                    parts.append(t)
                elif t is not None:
                    parts.append(str(t))
            else:
                t = getattr(block, "text", None)
                if isinstance(t, str):
                    parts.append(t)
        return "".join(parts)
    return str(content)


async def stream_response(
    user_message: str,
    history: list[dict],  # [{"role": "user"|"assistant", "content": "..."}]
) -> AsyncGenerator[str, None]:
    """
    Convert Streamlit session history to LangChain messages,
    append the new user message, and stream token chunks from the graph.

    Yields string token chunks as they arrive from the LLM.
    Tool-call tokens are filtered out — only final answer text is yielded.
    Restricts streaming to the `agent` node's chat model to avoid unrelated streams.
    """
    lc_messages = [
        HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
        for m in history
    ]
    lc_messages.append(HumanMessage(content=user_message))

    config = {"recursion_limit": RECURSION_LIMIT}

    # A queue + background producer lets us enforce a per-chunk timeout on the
    # consumer side, so a hung DB/LLM call surfaces a message instead of an
    # endless spinner (the graph itself has no built-in timeout).
    queue: asyncio.Queue = asyncio.Queue()
    _SENTINEL = object()

    async def _producer() -> None:
        yielded_any = False
        try:
            async for event in graph.astream_events(
                {"messages": lc_messages}, version="v2", config=config
            ):
                if event["event"] != "on_chat_model_stream":
                    continue
                # Prefer streams from the `agent` node; some providers omit `langgraph_node`.
                node = (event.get("metadata") or {}).get("langgraph_node")
                if node is not None and node != "agent":
                    continue
                chunk: AIMessageChunk = event["data"]["chunk"]
                if not chunk.tool_call_chunks:
                    text = _chunk_content_to_text(chunk.content)
                    if text:
                        yielded_any = True
                        await queue.put(text)
            if not yielded_any:
                # Graph finished but no text was ever streamed — avoid a silent empty bubble.
                await queue.put(
                    "Sorry, I couldn't generate a response for that. Please try rephrasing your question."
                )
        except Exception as exc:  # noqa: BLE001 — surface any graph/tool/LLM failure to the user
            await queue.put(
                f"\n\n⚠️ Sorry, I ran into an error while looking that up ({exc!s}). "
                "Please try again in a moment."
            )
        finally:
            await queue.put(_SENTINEL)

    producer_task = asyncio.create_task(_producer())
    try:
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=RESPONSE_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                producer_task.cancel()
                yield (
                    "\n\n⚠️ This is taking longer than expected — the database or AI "
                    "service may be slow or unreachable right now. Please try again."
                )
                break
            if item is _SENTINEL:
                break
            yield item
    finally:
        if not producer_task.done():
            producer_task.cancel()
