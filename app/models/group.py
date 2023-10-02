from pydantic import BaseModel, ConfigDict


class EDTGroup(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(frozen=True)
