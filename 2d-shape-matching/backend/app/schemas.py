from pydantic import BaseModel
from typing import List

class SearchResultItem(BaseModel):
    img_name: str
    img_src: str
    score: float

    class Config:
        orm_mode = True 

class SearchResponse(BaseModel):
    search_time: float
    results: List[SearchResultItem]