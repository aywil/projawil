from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)

from app.core.config import settings


class DatabaseHelper:
    # url = Строка подключения к БД, sqlite+aiosqlite:///...
    # echo = Логирование SQL-запросов в консоль (для отладки)
    def __init__(self, url: str, echo: bool = False):
        # Асинхронный движок на основе asyncio, управляет подключениями, пулом и транзакциями
        # Используется для создания сессий и миграций
        # Имеет тип AsyncEngine
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )

        # "Фабрика" по созданию асинхронных сессий (AsyncSession)
        self.session_factory = async_sessionmaker(
            bind=self.engine,  # Привязывает сессию к нашему движку
            autoflush=False,  # Не пушить изменения автоматически (лучше вручную)
            autocommit=False,  # Контролировать коммиты вручную
            expire_on_commit=False,  # не "стирать" значения у объектов после коммита (оставь доступными)
        )

    # Нужно, чтобы внутри одного запроса FastAPI использовать одну и ту же сессию
    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            # Привязывает сессию к текущей asyncio корутине
            scopefunc=current_task,
        )
        return session

    # Зависимость для FastAPI, Асинхронный генератор возвращающий AsyncSession
    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session  # Отдает сессию в хендлер (ручку)
            await session.close()  # Очищает сессию после завершения запроса

    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.get_scoped_session()
        yield session
        await session.close()


# --> Depends(db_helper.session_dependency)
# --> async_scoped_session (одна сессия на задачу)
# --> session.execute(), commit(), и т.д.
# <-- yield session Отдает эту сессию в хендлер
# <-- Обработка запроса на стороне сервера
# --> после запроса: session.remove()

db_helper = DatabaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
)
