import textwrap

from langchain_core.callbacks import UsageMetadataCallbackHandler

from src.llm_client import LLMClient

class RefineAgent:
    def __init__(self, tools: list | None = None, mcp_tools: list | None = None) -> None:
        self.usage_callback = UsageMetadataCallbackHandler()

        self.local_tools = tools if tools else []
        self.mcp_tools = mcp_tools if mcp_tools else []
        self.tools = [*self.local_tools, *self.mcp_tools]

        self.llm = LLMClient(tools=self.tools)
        self.graph = self._build_graph()
        self.previous_attempts = [] # check on this later

        self.system_prompt = textwrap.dedent("""
        Placeholder
        """).strip()

    def _node(self, state):
        return {}
    
    def _build_graph(self):
        return {}

    async def ainvoke(self, max_iterations: int = 32):
        pass
