from sqlmodel import  SQLModel, Field
from datetime import datetime
from typing import Optional

class Ignore(SQLModel, table=True):
    __tablename__ = "tb_ignorar" # type: ignore
    client: int = Field(primary_key=True)
    reason: str = Field(nullable=False)
    num_used: int = Field(default=0)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)