from pydantic import BaseModel

class Data(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None