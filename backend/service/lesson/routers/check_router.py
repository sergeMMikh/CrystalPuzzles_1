from http import HTTPStatus

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from starlette.responses import JSONResponse

from common.dependensies import TrainerSupervisorAdminDep, TrainerDep
from common.schema.base_schemas import Message
from core.logger import logger
from service.lesson.dependensies import CheckUOWDep, CheckServiceDep
from service.lesson.unit_of_work.lesson_uow import LessonUOW
from service.users.models import User
from service.users.repository import UserRepository

from service.identity.security import get_current_user
from service.lesson.repositories.lesson_repository import LessonRepository
from service.lesson.schemas.check_schema import CreateCheckSchema

check_router = APIRouter(
    prefix="/api/v1/check",
    tags=["Check"]
)

"""
Переход на страницу составления чек-листов.
Заполняем форму, а именно:
    - Состав учеников
    - Состав упражнений на занятие и количество повторений
"""
@check_router.post(
    "/",
    summary="Создание Чек-листа",
    response_model=bool, #модель, которая описывает тип возвращаем данных
    responses={
        200: {"description": "Успешная обработка данных"},
        401: {"description": "Не авторизованный пользователь"},
        400: {"model": Message, "description": "Некорректные данные"},
        500: {"model": Message, "description": "Серверная ошибка"}},
)
async def create_check(
        model: CreateCheckSchema, # Описывает входные данные (ID студентов, ID урока, даты и т. д.).
        lesson_uow: LessonUOW, # Это объект Unit of Work (UOW), который используется для управления транзакциями и доступом к репозиторию уроков.
        uow: CheckUOWDep, # Ещё один UOW для работы с репозиториями чек-листов.
        check_service: CheckServiceDep, # Сервис для работы с логикой чек-листов. Это зависимость, созданная с помощью Annotated и Depends. Она создаёт экземпляр CheckService, который затем передаётся в обработчики запросов.
        current_user: TrainerDep # Зависимость, определяющая текущего пользователя. Используется для контроля доступа.
):
    """ trainer """
    result = await check_service.add_check_for_lesson(
        uow, #  для работы с транзакциями
        model, #  данные, которые пришли от клиента
        lesson_uow=lesson_uow # для работы с уроками
        )
    if result:
        return result
    return JSONResponse(status_code=HTTPStatus.CONFLICT.value, content="Check existing")
