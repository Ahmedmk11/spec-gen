from langgraph.graph import StateGraph, START, END

from src.state import AgentState
from src.agents.generate_agent import GenerateAgent
from src.agents.analyze_agent import AnalyzeAgent
from src.agents.refine_agent import RefineAgent

class Graph:
    def __init__(self, tools: list | None = None, mcp_tools: list | None = None):
        self.generate_agent = GenerateAgent(tools=tools, mcp_tools=mcp_tools)
        self.analyze_agent = AnalyzeAgent(tools=tools, mcp_tools=mcp_tools)
        self.refine_agent = RefineAgent(tools=tools, mcp_tools=mcp_tools)

        self.graph = self._build_graph()

    async def _generate_node(self, state):
        return await self.generate_agent.ainvoke(state)

    async def _analyze_node(self, state):
        return await self.analyze_agent.ainvoke(state)

    async def _refine_node(self, state):
        return await self.refine_agent.ainvoke(state)

    def _route(self, state):
        if state.get("decision") == "accept":
            return END
        return "refiner"

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("generator", self._generate_node)
        workflow.add_node("analyzer", self._analyze_node)
        workflow.add_node("refiner", self._refine_node)

        workflow.add_edge(START, "generator")
        workflow.add_edge("generator", "analyzer")
        workflow.add_conditional_edges("analyzer", self._route, {"refiner": "refiner", END: END})
        workflow.add_edge("refiner", "analyzer")

        return workflow.compile()

    async def ainvoke(self, state):
        return await self.graph.ainvoke(state)
