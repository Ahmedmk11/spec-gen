import ast
import re
import textwrap

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langgraph.graph import StateGraph, START, END

from src.llm_client import LLMClient
from src.state import AgentState

class GenerateAgent:
    def __init__(self, tools: list | None = None, mcp_tools: list | None = None) -> None:
        self.usage_callback = UsageMetadataCallbackHandler()

        self.local_tools = tools if tools else []
        self.mcp_tools = mcp_tools if mcp_tools else []
        self.tools = [*self.local_tools, *self.mcp_tools]

        self.llm = LLMClient(tools=self.tools)
        self.graph = self._build_graph()

        self.system_prompt = textwrap.dedent("""
        You generate pytest unit tests for Python code provided by the user.

        Rules:
        - Output ONLY valid Python code. No markdown, no explanations, no commentary.
        - Import the functions under test using the module path provided. Example: from src.math_utils import add, multiply
        - NEVER redefine or reimplement the functions being tested. Only import them.
        - Use pytest. Do not use unittest unless specifically required.
        - Cover happy paths, edge cases, and invalid inputs where applicable.
        - Each test function must have a descriptive name starting with test_.
        - Output ONLY raw Python code. Do NOT wrap in markdown code blocks or backticks of any kind.
        """).strip()

    def _node(self, state):
        code = state.get("code", "")
        file_path = state.get("file_path", "")

        if not code or not file_path:
            raise ValueError("Missing required state: code and file_path are required")
        
        module = file_path.replace("/", ".").removesuffix(".py")

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Module: {module}\n\nGenerate tests for this code:\n\n{code}"}
        ]

        response = self.llm.llm.invoke(messages)

        generated_tests = response.content if hasattr(response, "content") else str(response)

        if generated_tests.startswith("```"):
            generated_tests = re.sub(r"^```[a-z]*\n?", "", generated_tests)
            generated_tests = re.sub(r"\n?```$", "", generated_tests)
            generated_tests = generated_tests.strip()

        try:
            ast.parse(generated_tests)
        except SyntaxError as e:
            raise ValueError(f"Generated code has syntax error: {e}") # TODO: maybe send it to analysis agent as well?

        return {
            "tests": generated_tests,
        }
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("generate", self._node)

        workflow.add_edge(START, "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    async def ainvoke(self, state, max_iterations: int = 32):
        config = {
            "recursion_limit": max_iterations,
            "callbacks": [self.usage_callback],
        }

        return await self.graph.ainvoke(state, config)
