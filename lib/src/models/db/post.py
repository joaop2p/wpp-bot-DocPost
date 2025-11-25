from sqlmodel import  SQLModel, Field
from datetime import datetime
from typing import Optional

class Post(SQLModel, table=True):
    __tablename__ = "tb_cartas"  # type: ignore
    last_updated: Optional[datetime] = Field(default_factory=datetime.now)
    process_id: int = Field(primary_key=True)
    tp_content: str = Field(primary_key=True)
    tp_mode: str = Field(nullable=False)
    file_name: str = Field(nullable=False)
    creator: str = Field(nullable=False)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    def from_dict(self, data: dict) -> "Post":
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        return self
    
    def __str__(self) -> str:
        return f'Post(process_id={self.process_id}, tp_content={self.tp_content}, tp_mode={self.tp_mode}, file_name={self.file_name}, creator={self.creator}, created_at={self.created_at}, last_updated={self.last_updated})'