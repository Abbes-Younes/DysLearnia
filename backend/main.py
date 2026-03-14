import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.graph import build_graph
from api.routes import router

load_dotenv()
import logging
logging.basicConfig(level=logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the LangGraph once on startup and store on app.state."""
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

    print(f"[startup] Connecting to Ollama at {ollama_url} using model {model_name}")
    app.state.graph = build_graph(ollama_url, model_name)
    print("[startup] LangGraph compiled. Ready.")
    yield
    print("[shutdown] Cleaning up.")


app = FastAPI(
    title="Dyslexia Learning Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the React dev server
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=True,
    )
