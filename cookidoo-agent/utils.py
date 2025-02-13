from typing import List
import openai
from .config import logger

def get_openai_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    try:
        response = openai.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    except Exception as exc:
        logger.error(f"Error generating embedding: {exc}")
        return []
