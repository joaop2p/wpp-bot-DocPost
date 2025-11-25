from sqlmodel import  SQLModel, Field
from datetime import datetime
from typing import Optional

class AgPackage(SQLModel, table=True):
    __tablename__ = "tb_envios_agencia" # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    tp_content: str = Field(foreign_key="tb_cartas.tp_content", nullable=False)
    process_id: int = Field(foreign_key="tb_cartas.process_id", nullable=False)
    has_print: bool = Field(default=False)
    has_service: bool = Field(default=False)
    numos: Optional[int] = None
    date: datetime = Field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f'AgPackage(id={self.id}, tp_content={self.tp_content}, process_id={self.process_id}, has_print={self.has_print}, has_service={self.has_service}, numos={self.numos}, date={self.date})'

class WppPackage(SQLModel, table=True):
    __tablename__ = "tb_envios_whatsapp" # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    process_id: int = Field(foreign_key="tb_cartas.process_id", nullable=False)
    tp_content: str = Field(foreign_key="tb_cartas.tp_content", nullable=False)
    num_used: int = Field(default=0)
    delivered: bool = Field(default=False)
    date: datetime = Field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f'WppPackage(id={self.id}, process_id={self.process_id}, tp_content={self.tp_content}, num_used={self.num_used}, delivered={self.delivered}, date={self.date})'