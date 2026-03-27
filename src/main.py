from dotenv import load_dotenv
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agents.generate_agent import GenerateAgent
from src.agents.analyze_agent import AnalyzeAgent
from src.agents.refine_agent import RefineAgent

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

class GenerateTest(BaseModel):
    code: str
    file_path: str

class AnalyzeTest(BaseModel):
    code: str
    tests: str
    file_path: str

@app.post("/test-generate")
async def test(req: GenerateTest):
    try:
        agent = GenerateAgent()

        response = await agent.ainvoke({
            "code": req.code,
            "file_path": req.file_path,
            "tests": "",
            "status": "",
            "output": "",
            "decision": "",
            "reason": "",
            "previous_attempts": [],
        })

        return {"tests": response["tests"]}

    except Exception as e:
        return {"error": str(e)}

@app.post("/test-analyze")
async def test(req: AnalyzeTest):
    try:
        agent = AnalyzeAgent()

        response = await agent.ainvoke({
            "code": req.code,
            "file_path": req.file_path,
            "tests": req.tests,
            "status": "",
            "output": "",
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

@app.get("/")
async def health():
    return {"status": "ok"}
