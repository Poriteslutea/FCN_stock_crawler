from pydantic import BaseModel

class Product(BaseModel):
    id: int
    code: str
    start_date: str
    start_trace_date: str
    end_date: str
    ko_limit: float
    ki_limit: float
    price_type: str