from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)


class QueryResponse(BaseModel):
    answer: str


class BuildIndexResponse(BaseModel):
    message: str
