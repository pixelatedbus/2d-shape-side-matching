from pydantic import BaseModel
from typing import List

# This defines the structure for a single search result item
class SearchResultItem(BaseModel):
    img_name: str
    img_src: str
    score: float

    class Config:
        orm_mode = True # Allows the model to be created from SQLAlchemy objects

# This defines the overall structure of the JSON response for a search
class SearchResponse(BaseModel):
    search_time: float
    results: List[SearchResultItem]