import openai
from langchain import FAISS
from langchain.embeddings import OpenAIEmbeddings

from settings.config import MY_LOGGER


class PostFilters:
    """
    Класс с фильтрами постов
    """
    def __init__(self, new_post, old_posts, separator):
        self.new_post = new_post
        self.old_posts = old_posts
        self.separator = separator
        self.filtration_result = []
        self.rel_old_post = None

    def __str__(self):
        return f"new_post = {self.new_post}\nseparator = {self.separator}\n" \
               f"filtration_result = {self.filtration_result}\nrel_old_post = {self.rel_old_post}"

    async def complete_filtering(self):
        """
        Полная фильтрация новостного поста, с применением всех фильтров
        """
        await self.duplicate_filter()
        return self.filtration_result

    async def duplicate_filter(self):
        """
        Фильтр дублирующихся новостных постов
        """
        find_rslt = await self.find_similar_post()
        if not find_rslt:
            check_gpt_rslt = await self.check_duplicate_by_gpt()
            MY_LOGGER.debug(f'Ответ GPT на поиск дублей: {check_gpt_rslt}')
            if check_gpt_rslt.lower() == 'да':
                self.filtration_result.append(False)
            elif check_gpt_rslt.lower() == 'нет':
                self.filtration_result.append(True)
            else:
                MY_LOGGER.warning(f'Несмотря на все инструкции ChatGPT вернул дичь в ответ на проверку дублей постов.'
                                  f'Ответ ChatGPT {check_gpt_rslt!r}. Считаем, что новость не прошла проверку на дубли')
                self.filtration_result.append(False)

    async def find_similar_post(self) -> bool | None:
        """
        Поиск похожего поста. Это необходимо для фильтрации дублирующих новостей
        base_text - базовый текст, база знаний или иное, на чем модель должна базировать свой ответ
        query - запрос пользователя, под который в base_text нужно найти более релевантные куски текста
        separator - разделитель текста с новостями
        """
        # Разбиваем текст на чанки
        text_chunks = self.old_posts.split(sep=self.separator)

        # Создадим индексную базу векторов по данному тексту (переведом текст в цифры, чтобы его понял комп)
        embeddings = OpenAIEmbeddings()
        index_db = FAISS.from_texts(text_chunks, embeddings)

        # Отбираем более релевантные куски базового текста (base_text), согласно запросу (query)
        relevant_piece = index_db.similarity_search_with_score(self.new_post, k=1)[0]  # Достаём релевантные куски
        if relevant_piece[1] > 0.3:
            MY_LOGGER.warning(f'Не найдено похожих новостных постов.')
            self.filtration_result.append(True)
            return True
        self.rel_old_post = relevant_piece[0].page_content
        MY_LOGGER.debug(f'Найден релевантный кусок: {self.rel_old_post}')

    async def check_duplicate_by_gpt(self, temp=0):
        """
        Функция для того, чтобы проверить через GPT дублируют ли по смыслу друг друга два поста.
        temp - (значение от 0 до 1) чем выше, тем более творчески будет ответ модели, то есть она будет додумывать что-то.
        """
        system = "Ты занимаешься фильтрацией контента и твоя задача наиболее точно определить дублируют ли друг друга " \
                 "по смыслу два новостных поста: старый и новый." \
                 "Проанализируй смысл двух переданных тебе текстов новостных постов и реши говорится ли в этих " \
                 "постах об одном и том же или в них заложен разный смысл. " \
                 "Если тексты новостных постов имеют одинаковый смысл, то в ответ пришли слово 'да' и ничего больше." \
                 "Если же в текстах новостных постов заложен разный смысл, то в ответ пришли слово 'нет' и ничего больше."
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Текст старого новостного поста: {self.rel_old_post}\n\n"
                                        f"Текст нового новостного поста: \n{self.new_post}"}
        ]
        try:
            completion = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=temp
            )
        except openai.error.ServiceUnavailableError as err:
            MY_LOGGER.error(f'Серверы OpenAI перегружены или недоступны. {err}')
            return False
        answer = completion.choices[0].message.content
        return answer
