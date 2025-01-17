from http import HTTPStatus

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from common.dependensies import TrainerSupervisorAdminDep, TrainerDep
from common.schema.base_schemas import Message
from core.logger import logger
from service.lesson.dependensies import CheckUOWDep, CheckServiceDep
from service.lesson.unit_of_work.lesson_uow import LessonUOW
from service.users.models import User
from service.users.repository import UserRepository
from service.lesson.schemas.lesson_schemas import MakeCheckList, GetCheckList

from service.identity.security import get_current_user
from service.lesson.repositories.lesson_repository import LessonRepository
from service.lesson.schemas.check_schema import CheckSchemaForTable, CheckViewSchemaForPage, CreateCheckSchema, \
    CreateCheckSchemaTest, TrainingCheckResponseSchema

from service.lesson.dependensies import LessonServiceDep, LessonUOWDep, LessonFilterDep, SpaceUOWDep, CheckUOWDep, \
    MakeCheckListDep

from pprint import pprint

check_router = APIRouter(
    prefix="/api/v1/check",
    tags=["Check"]
)


@check_router.get(
    "/",
    summary=" Получение всех занятий",
    # response_model=CheckViewSchemaForPage,
    # response_model=TrainingCheckResponseSchema,
    responses={
        200: {"description": "Успешная обработка данных"},
        401: {"description": "Не авторизованный пользователь"},
        400: {"model": Message, "description": "Некорректные данные"},
        500: {"model": Message, "description": "Серверная ошибка"}}
)
async def get_all_checks(
        # model: MakeCheckList, # MakeCheckListDep = Annotated[MakeCheckListDep, Depends(MakeCheckListDep)]
        uow: CheckUOWDep,  # Ещё один UOW для работы с репозиториями чек-листов.
        check_service: CheckServiceDep,
        current_user: TrainerSupervisorAdminDep,
        page: int = 1,
        per_page: int = 10
):
    role = current_user.role  # Роль пользователя: тренер, супервизор или админ.

    # # Проверяем роль пользователя.
    # if role not in ["trainer", "supervisor", "admin"]:
    #     raise HTTPException(status_code=403, detail="Недостаточно прав для выполнения операции")

    filters = {}

    async with uow:
        checklists = await uow.repo.get_checks_by_filter(**filters)
        print(f"Retrieved checklists: {checklists}")
        pprint(jsonable_encoder(checklists))

    # Сериализуем данные
    serialized_checklists = jsonable_encoder(checklists)

    # Пагинация
    total_count = len(serialized_checklists)
    max_page_count = (total_count + per_page - 1) // per_page  # Вычисляем общее количество страниц
    paginated_checklists = serialized_checklists[(page - 1) * per_page: page * per_page]

    # Возвращаем данные
    return CheckViewSchemaForPage(
        count_records=total_count,
        page=page,
        max_page_count=max_page_count,
        records=paginated_checklists
    )


@check_router.get(
    "/{check_id}",
    summary="Получение чек-листа по check_id",
    # response_model=CheckSchemaForTable,
    responses={
        200: {"description": "Успешная обработка данных"},
        401: {"description": "Не авторизованный пользователь"},
        400: {"model": Message, "description": "Некорректные данные"},
        500: {"model": Message, "description": "Серверная ошибка"}},
)
async def get_check(
        check_id: int,
        uow: CheckUOWDep,
        check_service: CheckServiceDep,
        current_user: TrainerSupervisorAdminDep,
):
    """ admin, supervisor, trainer """
    role = current_user.role  # Проверяем роль пользователя
    if role not in ["trainer", "supervisor", "admin"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав для выполнения операции")

    print(f'check_id: {check_id}')

    check = await check_service.get_check_by_id(uow, check_id)

    if not check:
        raise HTTPException(status_code=404, detail="Чек-лист не найден")

    return check


@check_router.get(
    "/list",
    summary="Получение всех чек-листов с фильтрацией",
    responses={
        200: {"description": "Успешное получение данных"},
        401: {"description": "Не авторизованный пользователь"},
        400: {"model": Message, "description": "Некорректные данные"},
        500: {"model": Message, "description": "Серверная ошибка"}
    }
)
async def get_checklists(
        model: GetCheckList,
        uow: CheckUOWDep,
        current_user: TrainerSupervisorAdminDep
):
    role = current_user.role  # Роль пользователя: тренер, супервизор или админ.

    # # Проверяем роль пользователя. Хотя current_user: TrainerSupervisorAdminDep должно это делать
    # if role not in ["trainer", "supervisor", "admin"]:
    #     raise HTTPException(status_code=403, detail="Недостаточно прав для выполнения операции")

    filters = {}
    if model.lesson_id:
        filters["lesson_id"] = model.lesson_id
        print(f'lesson_id: {filters.get("lesson_id")}')
    else:
        print('no lesson_id')
    if model.student_id:
        filters["student_id"] = model.student_id
        print(f'student_id: {filters.get("student_id")}')
    else:
        print('no student_id')

    async with uow:
        if role == "trainer":
            # Тренеры могут видеть только свои уроки
            filters["trainer_id"] = current_user.id
        # Админ видит все данные без дополнительных фильтров

        checklists = await uow.repo.get_checks_by_filter(**filters)

    return {"data": checklists}


@check_router.post(
    "/",
    summary="Создание Чек-листа",
    response_model=bool,
    responses={
        200: {"description": "Успешная обработка данных"},
        401: {"description": "Не авторизованный пользователь"},
        400: {"model": Message, "description": "Некорректные данные"},
        500: {"model": Message, "description": "Серверная ошибка"}},
)
async def create_check(
        model: MakeCheckList,  # MakeCheckListDep = Annotated[MakeCheckListDep, Depends(MakeCheckListDep)]
        uow: CheckUOWDep,  # Ещё один UOW для работы с репозиториями чек-листов.
        lesson_service: LessonServiceDep,
        check_service: CheckServiceDep,
        current_user: TrainerDep
):
    # Вызов сервиса для добавления чек-листа к уроку
    result = True
    result = await check_service.add_check_for_lesson(
        uow=uow,
        lesson_id=model.lesson_id,
        data=model.dict()
    )

    # Проверка результата и возврат ответа
    if result:
        print("Чек-лист успешно создан.")
        return True

    # Возвращаем ответ с ошибкой, если чек-лист уже существует
    print("Ошибка: Чек-лист уже существует.")
    raise JSONResponse(
        status_code=HTTPStatus.CONFLICT.value,
        content={"detail": "Check existing"}
    )


@check_router.put(
    "/{check_id}",
    summary="Изменение чек-листа по ID",
    responses={
        200: {"description": "Чек-лист успешно обновлён"},
        400: {"model": Message, "description": "Некорректные данные"},
        404: {"description": "Чек-лист не найден"},
        500: {"model": Message, "description": "Серверная ошибка"},
    },
)
async def update_check(
    check_id: int,
    model: MakeCheckList,
    uow: CheckUOWDep,
    check_service: CheckServiceDep,
    current_user: TrainerSupervisorAdminDep,
):
    """
    Обновление чек-листа:
    - Список учеников (students_id).
    - Список упражнений (training_check).
    """
    role = current_user.role  # Проверяем роль пользователя
    if role not in ["trainer", "supervisor", "admin"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав для выполнения операции")

    print(f"Updating check with ID: {check_id}")

    # Вызываем сервис для обновления данных
    result = await check_service.update_check_by_id(
        uow=uow,
        check_id=check_id,
        data=model.dict(),
    )

    if not result:
        raise HTTPException(status_code=404, detail="Чек-лист не найден")

    print(f"Check with ID {check_id} successfully updated.")
    return {"message": "Чек-лист успешно обновлён"}


@check_router.delete(
    "/{check_id}",
    summary="Логическое удаление чек-листа по ID",
    responses={
        200: {"description": "Чек-лист успешно удалён"},
        404: {"description": "Чек-лист не найден"},
    },
)
async def delete_check(
    check_id: int,
    uow: CheckUOWDep,
    check_service: CheckServiceDep,
    current_user: TrainerSupervisorAdminDep,
):
    """
    Логическое удаление чек-листа (установка deleted=True).
    """
    role = current_user.role  # Проверяем роль пользователя
    if role not in ["trainer", "supervisor", "admin"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав для выполнения операции")

    print(f"Marking check with ID {check_id} as deleted.")

    # Отмечаем чек-лист как удалённый
    await check_service.mark_check_as_deleted(uow, check_id)

    return {"message": "Чек-лист успешно удалён"}