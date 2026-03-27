import ast
import re
import textwrap

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langgraph.graph import StateGraph, START, END

from src.llm_client import LLMClient
from src.state import AgentState

class RefineAgent:
    def __init__(self, tools: list | None = None, mcp_tools: list | None = None) -> None:
        self.usage_callback = UsageMetadataCallbackHandler()

        self.local_tools = tools if tools else []
        self.mcp_tools = mcp_tools if mcp_tools else []
        self.tools = [*self.local_tools, *self.mcp_tools]

        self.llm = LLMClient(tools=self.tools)

        self.system_prompt = textwrap.dedent("""
        You fix pytest unit tests based on feedback from a test analysis agent.

        Rules:
        - Output ONLY valid Python code. No markdown, no explanations, no commentary.
        - Import the functions under test using the module path provided.
        - NEVER redefine or reimplement the functions being tested. Only import them.
        - Use pytest. Do not use unittest unless specifically required.
        - Fix ONLY the issues described in the feedback. Do not remove tests that are already correct.
        - Output ONLY raw Python code. Do NOT wrap in markdown code blocks or backticks of any kind.
        """).strip()

        self.graph = self._build_graph()

    async def _node(self, state):
        code = state.get("code", "")
        file_path = state.get("file_path", "")
        tests = state.get("tests", "")
        status = state.get("status", "")
        output = state.get("output", "")
        reason = state.get("reason", "")
        previous_attempts = state.get("previous_attempts", [])
        
        module = file_path.replace("/", ".").removesuffix(".py")

        attempts_context = ""
        if previous_attempts:
            attempts_context = "\n".join([
                f"Attempt {i+1}:\nTests:\n{a['tests']}\nIssue:\n{a['reason']}"
                for i, a in enumerate(previous_attempts)
            ])
        else:
            attempts_context = "None"

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": textwrap.dedent(f"""
                Module: {module}

                Here is the original code:

                {code}

                Here is the previously generated test file:

                {tests}

                The tests were run and the result was: {status}

                Output:
                {output}

                The analysis agent found the following issues:
                {reason}

                These are your previous attempts and the reasons they failed:
                {attempts_context}

                Fix the issues and return an improved test file.
            """).strip()}
        ]

        last_error = None

        for attempt in range(3):
            response = await self.llm.ainvoke(messages)
            generated_tests = response.content if hasattr(response, "content") else str(response)

            if generated_tests.startswith("```"):
                generated_tests = re.sub(r"^```[a-z]*\n?", "", generated_tests)
                generated_tests = re.sub(r"\n?```$", "", generated_tests)
                generated_tests = generated_tests.strip()

            try:
                ast.parse(generated_tests)
                return {
                    "tests": generated_tests,
                    "previous_attempts": previous_attempts + [{"tests": tests, "reason": reason}]
                }
            except SyntaxError as e:
                last_error = e
                print(f"Attempt {attempt + 1} failed with syntax error: {e}")
                messages = [
                    *messages,
                    {"role": "assistant", "content": generated_tests},
                    {"role": "user", "content": f"The code you generated has a syntax error: {e}\n\nFix it and return only valid Python code."}
                ]
                continue

        raise ValueError(f"Failed to generate valid Python after 3 attempts: {last_error}")
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("refine", self._node)

        workflow.add_edge(START, "refine")
        workflow.add_edge("refine", END)

        return workflow.compile()

    async def ainvoke(self, state, max_iterations: int = 32):
        config = {
            "recursion_limit": max_iterations,
            "callbacks": [self.usage_callback],
        }

        return await self.graph.ainvoke(state, config)
