import asyncio
import traceback

from pydantic import ValidationError

from beeai_framework.agents.types import AgentExecutionConfig
from beeai_framework.backend.chat import ChatModel
from beeai_framework.backend.message import UserMessage

# Python 3.14 + Pydantic 2.x forward-reference workaround:
# RunMiddlewareFn = Callable[["RunContext"], None] has a string forward-ref that
# Pydantic evaluates in the chat module namespace where RunContext isn't visible.
import beeai_framework.backend.chat as _beeai_chat
from beeai_framework.context import RunContext as _RunContext
_beeai_chat._ChatModelKwargsAdapter.rebuild(force=True, _types_namespace={"RunContext": _RunContext})

from typing import Any
from beeai_framework.emitter.types import EmitterOptions
from beeai_framework.emitter.emitter import Emitter, EventMeta

# Import agent components
from beeai_framework.workflows.agent import AgentWorkflow

# MCP Tool
from beeai_framework.tools.mcp import MCPTool
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

server_params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "mcp/server.py",
    ],
    env=None,
)


async def process_agent_events(
    event_data: Any, event_meta: EventMeta
) -> None:
    if event_meta.name == "error":
        error = getattr(event_data, "error", event_data)
        print("Agent 🤖 error:", error)
    elif event_meta.name == "new_token":
        value = getattr(event_data, "value", None)
        if value and hasattr(value, "get_text_content"):
            print(value.get_text_content(), end="", flush=True)
    elif event_meta.name == "success":
        result = getattr(getattr(event_data, "state", None), "result", None)
        if result and hasattr(result, "text"):
            print("\nAgent 🤖 :", result.text)


async def observer(emitter: Emitter) -> None:
    emitter.on("*.*", process_agent_events, EmitterOptions(match_nested=True))


async def main() -> None:
    mcp_tools = await MCPTool.from_client(stdio_client(server_params))

    llm = ChatModel.from_name("openai:google/gemma-4-e4b", base_url="http://localhost:1234/v1", api_key="lm-studio")
    try:
        workflow = AgentWorkflow(name="Smart assistant")
        workflow.add_agent(
            name="PersonSleep",
            instructions="You are a sleep analyst specialist. Call the PredictSleep tool with the person's age and sleep duration, then report the result in plain text.",
            tools=mcp_tools,
            llm=llm,
            execution=AgentExecutionConfig(max_iterations=5),
            final_answer_as_tool=False,
        )

        persona_sample = {
            "age": 52,
            "Sleep": 5.1,
        }
        prompt = f"Will this person will have sleep issues {persona_sample}?"
        await workflow.run(inputs=[UserMessage(content=prompt)]).observe(observer)

    except ValidationError:
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
