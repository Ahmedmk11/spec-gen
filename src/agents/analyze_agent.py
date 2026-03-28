import textwrap

from pydantic import BaseModel, Field, model_validator

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langgraph.graph import StateGraph, START, END

from src.llm_client import LLMClient
from src.state import AgentState

class AnalysisResult(BaseModel):
    decision: str = Field(description="Either 'accept' or 'refine'")
    reason: str = Field(description="If refining, explain what is wrong and what needs to be fixed. If accepting, leave empty.")

    @model_validator(mode="after")
    def clear_reason_if_accepted(self):
        if self.decision == "accept":
            self.reason = ""
        return self

class AnalyzeAgent:
    def __init__(self, tools: list | None = None, mcp_tools: list | None = None) -> None:
        self.usage_callback = UsageMetadataCallbackHandler()

        self.local_tools = tools if tools else []
        self.mcp_tools = mcp_tools if mcp_tools else []
        self.tools = [*self.local_tools, *self.mcp_tools]

        self.llm = LLMClient(schema=AnalysisResult)

        self.analysis_system_prompt = textwrap.dedent("""
        You are a test analysis agent responsible for validating automatically generated test files.

        You are given:
        - The original code
        - A generated test file meant to test that code

        Decide to ACCEPT if:
        - The tests correctly target the actual behavior of the code
        - The tests cover the main functionality, edge cases, and failure scenarios adequately
        - The tests are meaningful and assert actual behavior, not just that code runs without error

        Decide to REFINE if:
        - The tests have incorrect assertions, wrong imports, or broken setup that make them invalid
        - The tests are missing critical cases given the complexity of the code
        - The tests are shallow, redundant, or not asserting anything meaningful

        Always provide a reason explaining your decision. If refining, be specific about what is wrong and what needs to be fixed so the refine agent can act on it.
        """).strip()

        self.graph = self._build_graph()

    async def _analyze_node(self, state):
        code = state.get("code", "")
        tests = state.get("tests", "")
        file_path = state.get("file_path", "")

        messages = [
            {"role": "system", "content": self.analysis_system_prompt},
            {"role": "user", "content": f"Here is the original code's file path: {file_path} \n\nHere is the source code:\n\n{code}\n\nHere is the generated test file:\n\n{tests}"}
        ]

        result = await self.llm.ainvoke(messages)

        return {
            "decision": result.decision,
            "reason": result.reason
        }

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("analyze", self._analyze_node)

        workflow.add_edge(START, "analyze")
        workflow.add_edge("analyze", END)

        return workflow.compile()

    async def ainvoke(self, state, max_iterations: int = 32):
        config = {
            "recursion_limit": max_iterations,
            "callbacks": [self.usage_callback],
        }

        result = await self.graph.ainvoke(state, config)
        return result
