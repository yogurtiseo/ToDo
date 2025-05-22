# ---------------------------------------------------------------------
# 파일명: task.py
# 위치: api/schemas/task.py
# 이 파일은 '할 일(Task)' 데이터를 어떻게 주고받을지를 정의한 곳이다.
# - 즉, API에서 사용하는 데이터의 '모양(구조)'을 정해주는 역할을 한다.
# - FastAPI에서는 Pydantic 모델을 사용해 구조를 정의한다.
# ---------------------------------------------------------------------------

import datetime  # 날짜와 시간을 다룰 수 있는 파이썬 내장 모듈 (예: 마감일 등 처리에 사용됨)

from pydantic import BaseModel, Field, ConfigDict

# - BaseModel: 모든 뎅;터 구조의 기본이 되는 클래스
# - Field: 각 항목에 기본값, 예시, 설명 등을 붙일 수 있게 해준다
# - ConfigDict: Pydantic v2부터 모델 설정(예: from_attributes)을 지정할 때 사용


# --------------------------------------------------------------------------------
# [1] 공통 속성 클래스: TaskBase
# - title(할 일 제목)만 포함되어 있음
# - 할 일 관련 데이터 구조들이 공통으로 사용하는 부분을 따로 묶은 클래스
# - TaskCreate, TaskCreateResponse, Task가 이 클래스를 상속해서 사용한다
# ---------------------------------------------------------------------------------
class TaskBase(BaseModel):
    title: str | None = Field(
        default=None,  # 값이 없을 수도 있으므로 기본값을 None으로 설정함
        examples=["세탁소에 맡긴 것을 찾으러 가기"],  # 예시 데이터 (API 문서에 보여짐)
    )
    # * title: 할 일의 제목 (str 또는 None)
    # * str | None: 문자열이거나 값이 없을 수도 있음 (입력을 안 해도 에러는 나지 않음)

    due_date: datetime.date | None = Field(None, examples="2025-05-15")
    # * due_date: 할 일의 마감일(언제까지 해야 하는지)
    # * datatime.date | None: 날짜 형식이거나 없을 수도 있음
    #       예) 2025-05-15처럼 연-월-일 형식의 문자열을 입력
    # * 마감일은 선택사항이므로 입력하지 않아도 에러가 나지 않음음


# ---------------------------------------------------------------------
# [2] 할 일 생성 요청용 모델: TaskCreate
# - 사용자가 할 일을 새로 만들 때 사용하는 요청 구조
# - title만 필요하므로 TaskBase를 그대로 상속해서 사용함
# ---------------------------------------------------------------------
class TaskCreate(TaskBase):
    pass
    # * 상속만 하고 필드는 추가하지 않음 (title만 있으면 충분함)
    # * title은 TaskBase에서 정의된 내용을 그대로 사용함


# --------------------------------------------------------------------
# [3] 할 일 생성 응답용 모델: TaskCreateResponse
# - 서버가 클라이언트에게 응답할 때 사용하는 구조
# - 새로 만들어진 할 일의 번호(id)를 포함함
# --------------------------------------------------------------------
class TaskCreateResponse(TaskCreate):
    id: int  # 새로 생성된 할 일의 고유 번호

    model_config = ConfigDict(from_attributes=True)
    # * SQLAlchemy 같은 ORM 객체를 이 모델로 자동 변환할 수 있게 설정
    # * 기존 orm_mode = True 설정이 Pydantic v2에서는 from_attributes로 대체됨


# ---------------------------------------------------------------------
# [4] 할 일 전체 정보를 표현하는 모델: Task
# - 목록 조회나 상세 보기 등에 사용됨
# - id(번호), title(제목), done(완료 여부) 포함
# ----------------------------------------------------------------------
class Task(TaskBase):
    id: int  # 할 일의 번호 (정수, 예: 1, 2, 3 등)

    done: bool = Field(
        default=False,  # 기본값은 '완료되지 않음(False)'
        description="이 할 일이 완료되었는지 여부",  # API 문서에 보여질 설명
    )
    # * done: True면 완료, False면 미완료를 나타냄

    model_config = ConfigDict(from_attributes=True)
    # * 이 설정을 해두면 DB에서 가져온 ORM 객체를 그대로 이 모델에 쓸 수 있다
    # * Pydantic v2에서는 class Config + orm_mode 대신 이 방식을 사용함
