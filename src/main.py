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

class TestRequest(BaseModel):
    code: str
    file_path: str

@app.post("/test")
async def test(req: TestRequest):
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
            "retries": 0,
        })

        return {"tests": response["tests"]}

    except Exception as e:
        return {"error": str(e)}

@app.post("/")
async def generate_spec():
    try:
        # TODO: implement actual logic using agents
        pass
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def health():
    return {"status": "ok"}
