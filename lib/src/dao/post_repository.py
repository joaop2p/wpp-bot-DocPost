from sqlmodel import Session, select
from ...config.db_config import DatabaseConfig
from ..models.db.post import Post

class PostRepository(DatabaseConfig):
    def __init__(self) -> None:
        super().__init__()

    def insert_new(self, post: Post) -> Post:
        with Session(self.engine) as conn:
            conn.add(post)
            conn.commit()
            conn.refresh(post)
        return post
    
    def get_post(self, process: int, tb_content: str) -> Post | None:
        with Session(self.engine) as conn:
            statement = select(Post).where((Post.process_id == process) & (Post.tp_content == tb_content))
            return conn.exec(statement).first()
        