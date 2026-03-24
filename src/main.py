from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.post("/generate")
def generate_spec():
    try:
        # placeholder
        return {"spec": "Generated OpenAPI spec goes here"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def health():
    return {"status": "ok"}
