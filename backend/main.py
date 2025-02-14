from fastapi import FastAPI
from .routes import recipes

app = FastAPI(title="Cookidoo Agent API")

app.include_router(recipes.router, prefix="/recipes")


@app.get("/")
async def root():
    return {
        "message": "Cookidoo Agent API. Use endpoints /recipes/load-db or /recipes/query."
    }
