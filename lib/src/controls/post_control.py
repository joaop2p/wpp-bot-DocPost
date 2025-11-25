from regex import D
from ..models.domain.client import Client
from ..models.db.post import Post
from ..services.post_service import PostService

class PostControl:
    def __init__(self) -> None:
        self.post_service = PostService()

    def create_post_by_client(self, client: Client) -> Post:
        post_data = Post(
            process_id=int(client.process),
            tp_content=client.file.type_content,
            tp_mode=client.file.type_response,
            file_name=client.file.name,
            creator=client.file.creator
        )
        return post_data
    
    def create_post(self, post: Post) -> Post:
        return self.post_service.create_post(post)
    
    def fetch_post(self, client: Client) -> Post | None:
        return self.post_service.fetch_post(int(client.process), client.file.type_content)