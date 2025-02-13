import asyncio
import aiohttp
from typing import Tuple, List
from dotenv import load_dotenv
from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility,
)
from .config import MILVUS_HOST, MILVUS_PORT, logger
from .utils import get_openai_embedding
from .cookidoo import Cookidoo, get_localization_options
from .cookidoo.types import CookidooConfig, CookidooShoppingRecipeDetails

load_dotenv()

REQUEST_TIMEOUT = 5

def recipe_to_embedding_text(recipe: CookidooShoppingRecipeDetails) -> str:
    title = recipe.title or ""
    ingredients = ", ".join(
        ing.ingredientNotation
        for group in recipe.recipeIngredientGroups
        for ing in group.recipeIngredients
    ) if recipe.recipeIngredientGroups else ""
    
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
    except Exception as e:
        logger.debug(f"Error processing times: {e}")
    
    condensed = (
        f"Category: {category}. Title: {title}. Ingredients: {ingredients}. "
        f"Nutrition: {nutrition_info}. Total times: {total_times}."
    )
    return condensed

async def fetch_recipe(recipe_id: int, cookidoo: Cookidoo) -> CookidooShoppingRecipeDetails:
    recipe_id_str = f"r{recipe_id}"
    try:
        recipe_details = await cookidoo.get_recipe_details(recipe_id_str)
        return recipe_details
    except Exception as exc:
        logger.debug(f"Failed to fetch recipe {recipe_id_str}: {exc}")
        return None

async def fetch_all_recipes(
    cookidoo: Cookidoo, semaphore: asyncio.Semaphore, start_id: int, end_id: int
) -> List[CookidooShoppingRecipeDetails]:
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

async def sem_fetch(recipe_id: int, cookidoo: Cookidoo, semaphore: asyncio.Semaphore) -> CookidooShoppingRecipeDetails:
    async with semaphore:
        return await fetch_recipe(recipe_id, cookidoo)

async def process_batch(
    cookidoo: Cookidoo, semaphore: asyncio.Semaphore, batch_start: int, batch_end: int
) -> Tuple[List[str], List[str], List[str], List[List[float]]]:
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

async def main():
    connector = aiohttp.TCPConnector(limit=1000)
    async with aiohttp.ClientSession(connector=connector) as session:
        localization = (await get_localization_options(country="ie", language="en-GB"))[0]
        cookidoo = Cookidoo(session, cfg=CookidooConfig(localization=localization))
        semaphore = asyncio.Semaphore(1000)
        
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        collection_name = "recipes_collection"
        
        if utility.has_collection(collection_name):
            logger.info(f"Dropping existing collection '{collection_name}'...")
            utility.drop_collection(collection_name)
        
        embedding_dim = 1536
        fields = [
            FieldSchema(name="recipe_id", dtype=DataType.VARCHAR, max_length=100, is_primary=True, auto_id=False),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="condensed_text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim)
        ]
        schema = CollectionSchema(fields, description="Cookidoo recipes with OpenAI embeddings")
        collection = Collection(name=collection_name, schema=schema)
        
        total_recipes = 918000
        batch_size = 1000  
        start_id = 4000
        
        for batch_start in range(start_id, start_id + total_recipes, batch_size):
            batch_end = batch_start + batch_size
            logger.info(f"Processing batch: {batch_start} - {batch_end}")
            batch_ids, batch_titles, batch_condensed_texts, batch_embeddings = await process_batch(
                cookidoo, semaphore, batch_start, batch_end
            )
            if batch_ids:
                data = [batch_ids, batch_titles, batch_condensed_texts, batch_embeddings]
                collection.insert(data)
                collection.flush()
                logger.info(f"Inserted batch: {batch_start} - {batch_end}")
            else:
                logger.info(f"No recipes found in batch: {batch_start} - {batch_end}")
        
        try:
            if not collection.indexes:
                raise Exception("No index found")
        except Exception:
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": 128}
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            logger.info("Index created successfully.")
        
        logger.info("All recipes have been processed and stored in Milvus.")

if __name__ == "__main__":
    asyncio.run(main())
