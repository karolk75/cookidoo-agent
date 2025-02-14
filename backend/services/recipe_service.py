import asyncio
import logging

from backend.cookidoo import Cookidoo
from backend.cookidoo.types import CookidooShoppingRecipeDetails
from backend.services.openai_service import (
    extract_query_criteria,
    get_openai_embedding,
    get_re_ranked_recipe,
)

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 5


async def query_recipes_service(query: str, top_k: int = 10) -> str:
    from backend.services.milvus_service import query_collection
    
    extracted_criteria = await extract_query_criteria(query)
    condensed_query = f"{query}. Kryteria: {extracted_criteria}."
    query_embedding = await get_openai_embedding(condensed_query)
    if not query_embedding:
        return "Nie udało się obliczyć embeddingu zapytania."
    retrieved_texts = await asyncio.to_thread(query_collection, query_embedding, top_k)
    if not retrieved_texts:
        return "Nie znaleziono przepisów pasujących do zapytania."
    context = "\n\n".join(retrieved_texts)
    answer = await get_re_ranked_recipe(query, extracted_criteria, context)
    return answer


def load_vector_database():
    from backend.services.milvus_service import run_initial_load
    
    asyncio.create_task(run_initial_load())


def recipe_to_embedding_text(recipe: CookidooShoppingRecipeDetails) -> str:
    title = recipe.title or ""
    ingredients = (
        ", ".join(
            ing.ingredientNotation
            for group in recipe.recipeIngredientGroups
            for ing in group.recipeIngredients
        )
        if recipe.recipeIngredientGroups
        else ""
    )

    nutrition_info = ""
    try:
        nutritions = []
        for rn in recipe.recipeNutritions:
            for nut in rn.nutritions:
                nutritions.append(f"{nut.unittype} {nut.number} {nut.type}")
        nutrition_info = ", ".join(nutritions)
    except Exception as e:
        logger.debug(f"Error processing nutrition info: {e}")

    category = recipe.category or ""

    total_times = []
    try:
        for rt in recipe.times:
            total_times.append(f"{rt.type} {rt.quantity.value}")
        total_times_info = ", ".join(total_times)
    except Exception as e:
        logger.debug(f"Error processing times: {e}")

    condensed = (
        f"Category: {category}. Title: {title}. Ingredients: {ingredients}. "
        f"Nutrition: {nutrition_info}. Total times: {total_times_info}."
    )
    return condensed


async def fetch_recipe(
    recipe_id: int, cookidoo: Cookidoo
) -> CookidooShoppingRecipeDetails:
    recipe_id_str = f"r{recipe_id}"
    try:
        recipe_details = await cookidoo.get_recipe_details(recipe_id_str)
        return recipe_details
    except Exception as exc:
        logger.debug(f"Failed to fetch recipe {recipe_id_str}: {exc}")
        return None


async def fetch_all_recipes(
    cookidoo: Cookidoo, semaphore: asyncio.Semaphore, start_id: int, end_id: int
) -> list[CookidooShoppingRecipeDetails]:
    tasks = [
        asyncio.create_task(sem_fetch(recipe_id, cookidoo, semaphore))
        for recipe_id in range(start_id, end_id)
    ]
    recipes = []
    for task in asyncio.as_completed(tasks):
        result = await task
        if result is not None:
            recipes.append(result)
    return recipes


async def sem_fetch(
    recipe_id: int, cookidoo: Cookidoo, semaphore: asyncio.Semaphore
) -> CookidooShoppingRecipeDetails:
    async with semaphore:
        return await fetch_recipe(recipe_id, cookidoo)


async def process_recipes_batch(
    cookidoo: Cookidoo, semaphore: asyncio.Semaphore, batch_start: int, batch_end: int
) -> tuple[list[str], list[str], list[str], list[list[float]]]:
    recipes = await fetch_all_recipes(cookidoo, semaphore, batch_start, batch_end)
    batch_recipe_ids = []
    batch_titles = []
    batch_condensed_texts = []
    batch_embeddings = []
    for recipe in recipes:
        condensed = recipe_to_embedding_text(recipe)
        embedding = get_openai_embedding(condensed)
        if not embedding:
            continue
        batch_recipe_ids.append(recipe.id)
        batch_titles.append(recipe.title)
        batch_condensed_texts.append(condensed)
        batch_embeddings.append(embedding)
    return batch_recipe_ids, batch_titles, batch_condensed_texts, batch_embeddings
