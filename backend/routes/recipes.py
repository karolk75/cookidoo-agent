import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..models.schemas import BuildIndexResponse, QueryRequest, QueryResponse
from ..services.recipe_service import load_vector_database, query_recipes_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/load-db", response_model=BuildIndexResponse)
async def load_db_endpoint(background_tasks: BackgroundTasks = None):
    try:
        background_tasks.add_task(load_vector_database)
        return BuildIndexResponse(
            message="Database initial load started in background."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query_recipe_endpoint(request: QueryRequest):
    try:
        answer = await query_recipes_service(request.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        logger.info(f"Error quering recipes: {e}")
        raise HTTPException(status_code=500, detail=str(e))
