from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_nickname: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    telegram_id: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    date_joined: Mapped[str] = mapped_column(String, nullable=False)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=True)
    time: Mapped[str] = mapped_column(String, nullable=False)
    answered: Mapped[int] = mapped_column(Integer, nullable=False)


class FAQ(Base):
    __tablename__ = "faq"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)


async def get_engine(database_url: str):
    engine = create_async_engine(database_url)
    return engine


class DBHandler:
    def __init__(self):
        self.engine = None
        self.session = None
    
    async def init(self, database_url: str):
        self.engine = await get_engine(database_url)
        self.session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def create_user(self, telegram_nickname: str, first_name: str, telegram_id: str, language: str, date_joined: str):
        async with self.session() as session:
            user = User(telegram_nickname=telegram_nickname, first_name=first_name, telegram_id=telegram_id, language=language, date_joined=date_joined)
            session.add(user)
            await session.commit()
            return user
    
    async def create_question(self, user_id: int, question: str, time: str):
        async with self.session() as session:
            question = Question(user_id=user_id, question=question, time=time, answered=0)
            session.add(question)
            await session.commit()
            return question
    
    async def create_faq(self, question: str, answer: str):
        async with self.session() as session:
            faq = FAQ(question=question, answer=answer)
            session.add(faq)
            await session.commit()
            return faq
    
    async def get_user(self, telegram_id: str = None, telegram_nickname: str = None, internal_id: int = None):
        async with self.session() as session:
            if telegram_id:
                query = select(User).where(User.telegram_id == telegram_id)
            elif telegram_nickname:
                query = select(User).where(User.telegram_nickname == telegram_nickname)
            elif internal_id:
                query = select(User).where(User.id == internal_id)
            else:
                raise ValueError("No user ID provided")
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user
    
    async def get_question(self, question_id: int = None, text: str = None, user_id: int = None, time: str = None):
        async with self.session() as session:
            if question_id:
                query = select(Question).where(Question.id == question_id)
            elif text:
                query = select(Question).where(Question.question == text)
            elif user_id:
                if not time:
                    raise ValueError("Time is required when user_id is provided")
                query = select(Question).where(Question.user_id == user_id, Question.time == time)
            else:
                raise ValueError("No question ID provided")
            result = await session.execute(query)
            question = result.scalar_one_or_none()
            return question
    
    async def get_user_questions(self, user_id: int, pending_only: bool = False):
        async with self.session() as session:
            if pending_only:
                query = select(Question).where(Question.user_id == user_id, Question.answered == 0)
            else:
                query = select(Question).where(Question.user_id == user_id)
            result = await session.execute(query)
            questions = result.scalars().all()
            return questions

    async def get_all_user_ids(self):
        async with self.session() as session:
            query = select(User.telegram_id)
            result = await session.execute(query)
            telegram_ids = result.scalars().all()
            return telegram_ids
    
    async def get_all_users(self):
        async with self.session() as session:
            query = select(User)
            result = await session.execute(query)
            users = result.scalars().all()
            return users

    async def get_faq(self, question_id: int = None, question: str = None):
        async with self.session() as session:
            if question_id:
                query = select(FAQ).where(FAQ.id == question_id)
            elif question:
                query = select(FAQ).where(FAQ.question == question)
            else:
                raise ValueError("No FAQ ID or question provided")
            result = await session.execute(query)
            faq = result.scalar_one_or_none()
            return faq
    
    async def update_question(self, question_id: int, answer: str):
        async with self.session() as session:
            question = await self.get_question(question_id)
            question.answer = answer
            question.answered = 1
            await session.commit()
            return question
    
    async def update_user_lang(self, user_id: int, language: str):
        async with self.session() as session:
            user = await self.get_user(internal_id=user_id)
            user.language = language
            await session.commit()
            return user
    
    async def delete_user(self, telegram_id: str):
        async with self.session() as session:
            user = await self.get_user(telegram_id=telegram_id)
            try:
                await session.delete(user)
                await session.commit()
                return user
            except Exception as e:
                print(e)
                return None
    
    
    async def close(self):
        await self.engine.dispose()



if __name__ == "__main__":
    db = DBHandler()
    asyncio.run(db.init("sqlite+aiosqlite:///database.db"))
    asyncio.run(db.create_faq("What is the capital of France?", "Paris"))
    asyncio.run(db.get_faq(question="What is the capital of France?"))
    asyncio.run(db.close())