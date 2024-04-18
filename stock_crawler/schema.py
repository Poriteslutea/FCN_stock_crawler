from pydantic import BaseModel
from typing import List

class Product(BaseModel):
    id: int
    code: str
    start_date: str
    start_trace_date: str
    end_date: str
    ko_limit: float
    ki_limit: float
    price_type: str
    stock_list: List[dict]