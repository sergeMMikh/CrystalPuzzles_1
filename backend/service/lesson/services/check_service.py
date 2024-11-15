from common.service.base_service import BaseService
from service.lesson.unit_of_work.check_uow import CheckUOW


class CheckService(BaseService):
    """
    Сервисный слой, который содержит бизнес-логику работы с чек-листами.
    """
    @staticmethod
    async def add_user_for_lesson(uow: CheckUOW, lesson_id, data: dict):
        # Открываем контекст uow, чтобы начать транзакцию
        async with uow:
            # Вызываем репозиторий uow.repo.add_user_for_lesson, чтобы добавить данные пользователя к уроку
            result = await uow.repo.add_user_for_lesson(lesson_id, data)
            # Фиксируем изменения через uow.commit()
            await uow.commit()
            return result

    @staticmethod
    async def delete_user_for_lesson(uow: CheckUOW, lesson_id, data: dict):
        async with uow:
            result = await uow.repo.delete_user_for_lesson(lesson_id, data)
            await uow.commit()
            return result
