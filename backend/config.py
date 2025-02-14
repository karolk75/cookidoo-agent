from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_model_embedding: str = "text-embedding-3-small"
    openai_criteria_extraction_model: str = "gpt-4o-mini"
    openai_recipe_ranking_model: str = "gpt-4o-mini"
    embedding_dim: int = 1536
    milvus_host: str = "127.0.0.1"
    milvus_port: str = "19530"
    collection_name: str = "recipes_collection"


settings = Settings()
