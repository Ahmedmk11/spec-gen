import os
import textwrap

from langchain.chat_models import init_chat_model
from langchain_core.callbacks import UsageMetadataCallbackHandler

def get_env_model():
    model = os.getenv("ANTHROPIC_MODEL")
    if not model:
        raise ValueError("Model is not set")
    return model

class LLMClient:
    def __init__(self, tools: list | None = None) -> None:
        self.llm = init_chat_model(
            model=get_env_model(),
            model_kwargs={
                "cache_control": {"type": "ephemeral"}
            },
        ).bind_tools(tools if tools else [])

class AnalyzeAgent:
    def __init__(self, tools: list | None = None, mcp_tools: list | None = None) -> None:
        self.usage_callback = UsageMetadataCallbackHandler()

        self.local_tools = tools if tools else []
        self.mcp_tools = mcp_tools if mcp_tools else []
        self.tools = [*self.local_tools, *self.mcp_tools]

        self.llm = LLMClient(tools=self.tools)
        self.graph = self._build_graph()

        self.system_prompt = textwrap.dedent("""
        Placeholder
        """).strip()

    async def ainvoke(self, max_iterations: int = 32):
        pass
