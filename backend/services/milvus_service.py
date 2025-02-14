import aiohttp
from fastapi import logger
from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility,
)

from backend.cookidoo import Cookidoo
from backend.cookidoo.helpers import get_localization_options
from backend.cookidoo.types import CookidooConfig
from backend.services.recipe_service import process_recipes_batch
from ..config import settings


def create_collection() -> Collection:
    connections.connect("default", host=settings.milvus_host, port=settings.milvus_port)
    if utility.has_collection(settings.collection_name):
        logger.info(f"Dropping existing collection: {settings.collection_name}")
        utility.drop_collection(settings.collection_name)
    fields = [
        FieldSchema(
            name="recipe_id",
            dtype=DataType.VARCHAR,
            max_length=100,
            is_primary=True,
            auto_id=False,
        ),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="condensed_text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(
            name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.embedding_dim
        ),
    ]
    schema = CollectionSchema(
        fields, description="Recipe collection with optimized representation"
    )
    collection = Collection(name=settings.collection_name, schema=schema)
    return collection


def create_index(collection: Collection):
    try:
        if not collection.indexes:
            raise Exception("No index found")
    except Exception:
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        logger.info("Index created successfully.")


async def run_initial_load():
    import asyncio

    connector = aiohttp.TCPConnector(limit=1000)
    async with aiohttp.ClientSession(connector=connector) as session:
        localization = (await get_localization_options(country="ie", language="en-GB"))[
            0
        ]
        cookidoo = Cookidoo(session, cfg=CookidooConfig(localization=localization))
        semaphore = asyncio.Semaphore(1000)

        collection = create_collection()

        total_recipes = 918000
        batch_size = 1000
        start_id = 4000

        for batch_start in range(start_id, start_id + total_recipes, batch_size):
            batch_end = batch_start + batch_size
            logger.info(f"Processing batch: {batch_start} - {batch_end}")
            (
                batch_ids,
                batch_titles,
                batch_condensed_texts,
                batch_embeddings,
            ) = await process_recipes_batch(cookidoo, semaphore, batch_start, batch_end)
            if batch_ids:
                data = [
                    batch_ids,
                    batch_titles,
                    batch_condensed_texts,
                    batch_embeddings,
                ]
                collection.insert(data)
                collection.flush()
                logger.info(f"Inserted batch: {batch_start} - {batch_end}")
            else:
                logger.info(f"No recipes found in batch: {batch_start} - {batch_end}")

        create_index(collection)
        logger.info("All recipes have been processed and stored in Milvus.")


def query_collection(query_embedding: list, top_k: int = 10) -> list:
    connections.connect("default", host=settings.milvus_host, port=settings.milvus_port)
    collection = Collection(settings.collection_name)
    collection.load()
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        expr=None,
        output_fields=["recipe_id", "title", "condensed_text"],
    )
    retrieved = []
    for hits in results:
        for hit in hits:
            retrieved.append(hit.entity.get("condensed_text"))
    return retrieved
