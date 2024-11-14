from pydantic import Field

from datetime import datetime
from typing import Optional, List

from common.schema.base_schemas import BaseModel
from common.schema.base_user_schema import UserShortSchema
from service.training.models import Training


class TrainingCheck(BaseModel):
    """ Схема оценки выполнения упражнения """
    training_id: int
    repetitions: int = Field(ge=1)
    assessment: Optional[int] = Field(default=None, le=10, ge=1)


class TrainingSchema(BaseModel):
    name: str


class TrainingCheckResponseSchema(TrainingCheck):
    training: TrainingSchema


class CreateCheckSchema(BaseModel):
    """ Схема создания моделей занятий """
    student_ids: list[int]
    lesson_id: int
    training_check: list[TrainingCheck]
    date_add: datetime = Field(default_factory=datetime.now, hidden=True)
    date_update: datetime = Field(default_factory=datetime.now, hidden=True)


class CheckSchemaForTable(BaseModel):
    """ Схема деталей чек-листа """
    id: int
    student: UserShortSchema
    comment: Optional[str]
    awards: Optional[int]
    training_data: List[TrainingCheckResponseSchema]
'''
 Модель схемы Check:
     id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
     student_id: Mapped[int] = mapped_column(sa.ForeignKey("Users.id"), nullable=False)
     student = relationship("User", back_populates="students")
     lesson_id: Mapped[int] = mapped_column(sa.ForeignKey("Lessons.id"), nullable=False)
     lesson = relationship("Lesson", back_populates="check")
     comment: Mapped[str] = mapped_column(sa.String, nullable=True)
     awards: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("Awards.id"), nullable=True)
     deleted: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
     date_add: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
     date_update: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
     training_data = relationship("TrainingCheck", back_populates="check")
'''

# class EditLessonSchema(BaseModel):
#     """ Схема изменения моделей занятий """
#     id: int
#     space_id: int
#     trainer_id: int
#     trainer_comments: Optional[str]
#     start: datetime
#
#
# class TrainerShortSchema(BaseModel):
#     id: int
#     firstname: Optional[str] = None
#     lastname: Optional[str] = None
#     surname: Optional[str] = None
#
#
# class LessonSchemaForTable(BaseModel):
#     """ Схема деталей занятия """
#     id: int
#     space: SpaceSchemaForTable
#     trainer: TrainerShortSchema
#     trainer_comments: Optional[str]
#     start: datetime
#
#
# class LessonViewSchemaForPage(BaseModel):
#     """ Помтраничный вывод деталей моделей тренировок """
#     page: int
#     max_page_count: int
#     count_records: int
#     records: List[LessonSchemaForTable]
#
#
# class LessonFilterSchema(BaseFilterSchema):
#     """ Фильтрация и пагинация """
#     date_begin: datetime | None = Query(default=None, description="Дата начала занятия")
#     trainer: int | None = Query(default=None, description="Тренер")


class TestSchema(BaseModel):
    """ Помтраничный вывод деталей моделей тренировок """
    name: str
    lesson_id: int
    descripton: Optional[str] = None