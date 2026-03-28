from dotenv import load_dotenv
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agents.generate_agent import GenerateAgent
from src.agents.analyze_agent import AnalyzeAgent
from src.agents.refine_agent import RefineAgent

from src.graph import Graph

load_dotenv()

FRONTEND_PORT = 5185

app = FastAPI(title="SpecGen")

origins = [
    f"http://localhost:{FRONTEND_PORT}",
    f"http://127.0.0.1:{FRONTEND_PORT}"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

agent = Graph()
generateAgent = GenerateAgent()
analyzeAgent = AnalyzeAgent()
refineAgent = RefineAgent()

class GenerateTest(BaseModel):
    code: str
    file_path: str

class AnalyzeTest(BaseModel):
    code: str
    tests: str
    file_path: str

class RefineTest(BaseModel):
    pass

class Generate(BaseModel):
    code: str
    file_path: str

@app.post("/test-generate")
async def test_generate(req: GenerateTest):
    try:
        response = await generateAgent.ainvoke({
            "code": req.code,
            "file_path": req.file_path,
            "tests": "",
            "decision": "",
            "reason": "",
            "previous_attempts": [],
        })

        return {"tests": response["tests"]}

    except Exception as e:
        return {"error": str(e)}

@app.post("/test-analyze")
async def test_analyze(req: AnalyzeTest):
    try:
        response = await analyzeAgent.ainvoke({
            "code": req.code,
            "file_path": req.file_path,
            "tests": req.tests,
            "decision": "",
            "reason": "",
            "previous_attempts": [],
        })

        return {
            "decision": response["decision"],
            "reason": response["reason"]
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/test-refine")
async def test_refine(req: RefineTest):
    try:
        response = await refineAgent.ainvoke({
            "code": "",
            "file_path": "",
            "tests": "",
            "decision": "",
            "reason": "",
            "previous_attempts": [],
        })

        return {
            "decision": response["decision"],
            "reason": response["reason"]
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/")
async def generate_spec(req: Generate):
    try:
        response = await agent.ainvoke({
            "code": req.code,
            "file_path": req.file_path,
            "tests": "",
            "decision": "",
            "reason": "",
            "previous_attempts": [],
            "iteration": 0,
        })

        return {"tests": response["tests"]}

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def health():
    return {"status": "ok"}
