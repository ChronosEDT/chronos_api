from pydantic import BaseModel


class EDTGroup(BaseModel):
    id: str
    name: str
