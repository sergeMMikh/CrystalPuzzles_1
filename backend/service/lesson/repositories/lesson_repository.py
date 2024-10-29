from datetime import datetime
from typing import Optional

from sqlalchemy import select, or_, Select
from sqlalchemy.orm import joinedload

from common.repository.base_repository import BaseRepository
from service.lesson.schemas.lesson_schemas import LessonFilterSchema
from service.training.models import Training
from service.users.models import User
from service.lesson.models import Lesson, Space, Check, TrainingCheck


class LessonRepository(BaseRepository):
    model = Lesson

    # region ------------------- Вспомагательные методы -----------------------

    async def user_filter(self, stmt: Select, user_id: int) -> Select:
        stmt = stmt.filter(self.model.check.any(Check.student_id.__eq__(user_id)))
        return stmt

    # endregion ---------------------------------------------------------------

    async def get(self, lesson_id: int, student_id: Optional[int] = None):
        stmt = (
            select(self.model)
            .filter(
                self.model.id == lesson_id,
                self.model.deleted.__eq__(False))
            .options(
                joinedload(self.model.trainer),
                joinedload(self.model.space),
                joinedload(self.model.check).joinedload(Check.training_data).joinedload(TrainingCheck.training).load_only(Training.name),
                joinedload(self.model.check).joinedload(Check.student)
            )
        )
        if student_id:
            stmt = await self.user_filter(stmt, student_id)
        result = (await self.session.execute(stmt)).unique().scalar_one_or_none()
        return result

    async def get_by_start_time_and_space(self, space: int, startime: datetime) -> Optional[Lesson]:
        stmt = (
            select(self.model)
            .where(self.model.space_id == space)
            .where(self.model.start == startime)
        )
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        return result

    async def get_all_lesson_by_filter(self, filters: LessonFilterSchema, student_id: Optional[int] = None):
        """
         асинхронный метод для получения списка уроков с использованием фильтров. 
         Она формирует SQL-запрос, учитывая заданные параметры фильтрации, и возвращает 
         отфильтрованный список записей с дополнительной информацией. 
        """

        # Базовый запрос
        stmt = ( 
            select(self.model) # создает базовый запрос, выбирая все записи из модели self.model (предположительно, модели уроков).
            .options(
                # options(joinedload(...)) — используется для загрузки связанных данных с joinedload, 
                # чтобы предотвратить "ленивую загрузку" и получить сразу всю необходимую информацию
                #  (например, данные тренера, пространства, проверки).
                joinedload(self.model.trainer),
                joinedload(self.model.space),
                joinedload(self.model.check).joinedload(Check.training_data),
                joinedload(self.model.check).joinedload(Check.student),
            )
            .filter(self.model.deleted.__eq__(False)) # исключает удаленные записи 
            # (предполагается, что deleted — это флаг, который отмечает, была ли запись удалена).
        )
        if filters.search_string: # Если filters.search_string задан, добавляются условия поиска по подстроке, игнорируя регистр:
            stmt = stmt.filter(or_(
                self.model.space.has(Space.name.ilike(f"%{filters.search_string}%")),
                self.model.trainer.has(User.firstname.ilike(f"%{filters.search_string}%")),
                self.model.trainer.has(User.lastname.ilike(f"%{filters.search_string}%")),
                self.model.trainer.has(User.surname.ilike(f"%{filters.search_string}%"))
                )
            )
        if filters.start_date: # проверяет, что урок начался не раньше этой даты.
            stmt = stmt.filter(self.model.start >= filters.start_date.replace(tzinfo=None))
        if filters.end_date: # ограничивает дату начала урока, чтобы она была меньше заданной конечной даты.
            stmt = stmt.filter(self.model.start < filters.end_date.replace(tzinfo=None))
        if filters.trainer: # фильтрация по ID тренера
            stmt = await self._add_filters(stmt, trainer_id=filters.trainer)
        if student_id: # Фильтрация по ID студента
            stmt = await self.user_filter(stmt, student_id)
        count_records = await self._get_count_records(stmt) # общее количество записей, соответствующих запросу stmt
        records = await self._get_records(count_records, stmt, filters) # фактические записи, применяя ограничения из filters (например, пагинация).
        response = await self._convert_response(count_records, records, filters) # Вызывает _convert_response, 
        # чтобы привести данные в нужный формат для возврата.
        return response
