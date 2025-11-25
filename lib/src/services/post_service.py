from ..dao.post_repository import PostRepository
from ..models.domain.file import File
from ..models.db.post import Post
from ..models.domain.client import Client

class PostService:
    def __init__(self) -> None:
        self._post_repository = PostRepository()

    def create_post(self, post: Post) -> Post:
        return self._post_repository.insert_new(post)
    
    def fetch_post(self, process: int, tb_content: str) -> Post | None:
        return self._post_repository.get_post(process, tb_content)