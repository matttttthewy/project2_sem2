from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils import FaqDataHandler

class NewUser(BaseFilter):
    def __init__(self, db):
        self.database = db
    
    async def __call__(self, message: Message) -> bool:
        user = await self.database.get_user(telegram_id=str(message.from_user.id))
        return user is None


class QuestionAlreadyExists(BaseFilter):
    def __init__(self, source_path):
        self.source_path = source_path
    
    async def __call__(self, message: Message) -> bool:
        question = message.text
        answer = FaqDataHandler.get_answer(self.source_path, question)
        return answer
