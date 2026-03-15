import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.graph import build_graph
from api.routes import router as legacy_router

load_dotenv()
import logging
logging.basicConfig(level=logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise shared services once on startup."""
    # ── LLM singleton (backend selected via LLM_BACKEND env var) ──────────
    from models.local_llm import init_llm, get_llm
    init_llm()
    llm = get_llm()
    print(f"[startup] LLM initialised: {type(llm).__name__}")

    # ── Legacy LangGraph (existing endpoints) ──────────────────────────────
    app.state.graph = build_graph()
    print("[startup] LangGraph compiled.")

    # ── Auto-register all IBlocks ──────────────────────────────────────────
    import blocks  # noqa: F401 — triggers __init__.py which imports all blocks
    from blocks.registry import BLOCK_REGISTRY
    print(f"[startup] {len(BLOCK_REGISTRY)} blocks registered: "
          f"{sorted(BLOCK_REGISTRY.keys())}")

    print("[startup] Ready.")
    yield
    print("[shutdown] Cleaning up.")


app = FastAPI(
    title="DysLearnia API",
    description=(
        "Visual learning pipeline builder for dyslexic learners.\n\n"
        "## Endpoints\n"
        "- **Legacy agent endpoints** (`/api/simplify`, `/api/quiz`, etc.) — "
        "single-block invocations backed by LangGraph.\n"
        "- **Block registry** (`GET /api/blocks`) — lists all registered pipeline blocks.\n"
        "- **Pipeline execution** (`POST /api/pipeline/run`, `WS /ws/pipeline/{id}`) — "
        "run full DAG pipelines with live progress streaming.\n"
        "- **Flows** (`/api/flows`) — save, load, fork, and template pipelines via Supabase.\n"
        "- **Documents** (`POST /api/documents/upload`) — upload + index course material.\n"
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow the React / Next.js dev server
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Legacy routes (backward-compatible) ───────────────────────────────────────
app.include_router(legacy_router, prefix="/api")

# ── New IBlock system routes ───────────────────────────────────────────────────
from routes.blocks import router as blocks_router
from routes.pipeline import router as pipeline_router
from routes.flows import router as flows_router
from routes.documents import router as documents_router

app.include_router(blocks_router, prefix="/api")
app.include_router(pipeline_router, prefix="/api")
app.include_router(flows_router, prefix="/api")
app.include_router(documents_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=True,
    )
