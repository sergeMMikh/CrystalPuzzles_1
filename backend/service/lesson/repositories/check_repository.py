from fastapi import HTTPException
from sqlalchemy import insert, select, exists, delete
from sqlalchemy.orm import selectinload

from common.repository.base_repository import BaseRepository
from service.lesson.models import Check, TrainingCheck


class CheckRepository(BaseRepository):
    model = Check

    async def __bind_training_check(self, training_check: dict):
        """
        приватный метод, который связывает данные о тренировке (training_check) с проверкой. 
        Он принимает словарь training_check, вставляет его в таблицу TrainingCheck и 
        возвращает объект TrainingCheck после вставки.
        """

        # создание SQL-запроса вставки данных в таблицу
        stmt = (
            insert(TrainingCheck)
            .values(**training_check)
            .returning(TrainingCheck)
        ) 

        await self.session.execute(stmt)

    async def __checks_exist(self, lesson_id: int):
        """
        Проверяет, существуют ли проверки для конкретного занятия (lesson_id). 
        Использует select(exists(...)).filter(...), чтобы вернуть 
        True или None в зависимости от того, найдены ли данные
        """

        return (await self.session.execute(
            select(exists(self.model))
            .filter(self.model.lesson_id == lesson_id)
            .limit(1)
        )).scalar_one_or_none()

    async def get_by_filter(self, **kwargs):
        """
        Получает объект Check на основе фильтров, переданных через kwargs. 
        Запрос создается с помощью select(self.model), а затем 
        фильтры добавляются методом _add_filters (определенным в BaseRepository)
        return: None если ничего не найдено
        """

        stmt = select(self.model)
        stmt = await self._add_filters(stmt, **kwargs)

        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add(self, data: dict) -> int:
        """
        Добавляет новую запись Check в базу данных и связывает её с данными training_check. 
        Метод удаляет ключ training_check из данных data перед вставкой Check, 
        а затем добавляет каждый элемент из training_check как 
        отдельную запись TrainingCheck с привязкой к созданной проверке check_id.
        return: check_id
        """

        training_check_list = data.pop("training_check")
        check_id = await super().add(data)

        for training_check in training_check_list:
            training_check["check_id"] = check_id
            await self.__bind_training_check(training_check)

        data["training_check"] = training_check_list
        
        return check_id

    async def add_check_for_lesson(self, data: dict) -> bool:
        """
        Добавляет проверку для конкретного урока, если проверка для указанного lesson_id еще не существует.
        Если проверка уже существует, генерирует исключение HTTPException с сообщением "Check exist".
        Если проверки нет, метод итерирует student_ids и создает для каждого студента новую запись проверки.
        """
        if not await self.__checks_exist(data.get("lesson_id")): # предотвращаем появление дубликатов
            student_ids = data.pop("student_ids")
            for student_id in student_ids:
                data["student_id"] = student_id
                await self.add(data)
            return True
        raise HTTPException(status_code=400, detail="Check exist")

    async def add_user_for_lesson(self, lesson_id, data: dict) -> bool:
        """
        Добавляет пользователя в урок lesson_id.
        return: bool- результат создания потльзователя
        """

        # проверяет, есть ли уже проверка для указанного student_id и lesson_id. 
        if await self.get_by_filter(student_id=data.get('student_id'), lesson_id=lesson_id):
            raise HTTPException(status_code=400, detail="Student already exist in lesson")

        # получает связанные данные training_data
        lesson = (await self.session.execute(
            select(self.model)
            .options(selectinload(self.model.training_data))
            .filter(self.model.lesson_id == lesson_id)
            .limit(1)
        )).scalar_one_or_none()

        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        training_data = lesson.training_data

        # создания записей training_check для нового пользователя
        data["training_check"] = (
            {"training_id": training.training_id, "repetitions": training.repetitions} for training in training_data
        )
        data["lesson_id"] = lesson_id
        check_id = await self.add(data) # создане пользователя
        
        return bool(check_id)

    async def delete_user_for_lesson(self, lesson_id, data: dict):
        """Удалить пользователя из урока."""

        # Ищет полльзователя по student_id и lesson_id и вызывает HTTPException если пользовтаетля на уроке нет
        check = await self.get_by_filter(student_id=data.get('student_id'), lesson_id=lesson_id)
        if not check:
            raise HTTPException(status_code=404, detail="Check not found")
        
        stmt = delete(TrainingCheck).filter(TrainingCheck.check_id == check.id)
        await self.session.execute(stmt)
        await self.delete_db(check.id)
