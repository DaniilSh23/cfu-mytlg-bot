

class PostFilters:
    """
    Класс с фильтрами постов
    """
    def __init__(self, new_post, old_posts, separator):
        self.new_post = new_post
        self.old_posts = old_posts
        self.separator = separator
        self.filtration_result = []

    @classmethod
    async def complete_filtering(cls, new_post, old_posts, separator):
        """
        Полная фильтрация новостного поста, с применением всех фильтров
        """
        cls(new_post, old_posts, separator)
        # TODO: вызов методов-фильтров
        return cls

    async def duplicate_filter(self):
        """
        Фильтр дублирующихся новостных постов
        """
        # TODO: прописать через либу FAISS и возможно chatgpt
