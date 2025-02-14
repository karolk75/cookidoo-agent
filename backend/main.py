from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import recipes
from .config import settings

app = FastAPI(title="Cookidoo Agent API")

app.include_router(recipes.router, prefix="/recipes")

app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.cors_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def root():
    return {
        "message": "Cookidoo Agent API. Use endpoints /recipes/load-db or /recipes/query."
    }
