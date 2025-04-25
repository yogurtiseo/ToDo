# -----------------------------------------------------------------------
# 파일명: task.py
# 위치: api/routers/task.py
# 이 파일은 "할 일(To-Do)" 기능을 처리하는 API를 정의한 곳이다.
# - /tasks로 시작하는 주소들을 FastAPI의 APIRouter로 관리하다.
# - /주요 기능: 할 일 목록 조회, 할 일 추가, 수정, 삭제
# ---------------------------------------------------------------------------------------

# *FastAPI에서 여러 개의 URL 경로를 그룹으로 묶어 관리할 수 있게 해주는 도구구
from fastapi import APIRouter, Depends, HTTPException

# - APIRouter: 기능별로 URL을 나눠 관리할 수 있게 해줌 (예: /tasks, /users 등)
# - Depends: 다른 함수(예: DB 연결)를 자동으로 실행하고 주입해주는 도구

# * SQLAlchemy의 비동기 세션을 사용하기 위한 도구
from sqlalchemy.ext.asyncio import AsyncSession

# - AsyncSession: await를 사용하는 비동기 DB 작업에 사용됨

# * 우리가 만든 CRUD 함수들을 불러온다 (파일 위치: api/cruds/task.py)
# - 여기에 create_task, update_task 같은 실제 DB 작업 함수가 정의되어 있음
import api.cruds.task as task_crud

# * DB 세션을 자동으로 가져오기 위한 함수 (파일 위치: api/db.py)
# - FastAPI에서 Depends로 연결할 수 있게 준비해둔 함수
# - 비동기 세션(AsyncSession)을 반환함
from api.db import get_db

# * 우리가 정의한 데이터 구조를 불러온다 (파일 위치: api/schemas/task.py)
# - Task: 전체 할 일 데이터를 표현
# - TaskCreate: 사용자가 보낼 입력 데이터 구조
# - TaskCreateResponse: 응답할 때 사용할 데이터 구조 (id 포함)
import api.schemas.task as task_schema

# * router 객체를 만든다
# - task 목록과 관련된 여러 기능을 이 객체에 모두 담아서
#   나중에 main.py에서 FastAPI 앱에 등록하게 된다.
router = APIRouter()


# -------------------------------------------------------------------------
# [1] 할 일 목록 조회 (GET 요청)
# - 클라이언트가 /tasks 주소로 요청하면 전체 할 일 목록을 반환한다.
# - 각 할 일이 '완료되었는지 여부'도 함께 포함된다.
#   (Done 테이블에 완료 기록이 있는지를 기준으로 판단함)
# -------------------------------------------------------------------------
@router.get("/tasks", response_model=list[task_schema.Task])
# - response_model -> 응답의 데이터 모양을 정해주는 옵션
# - 여기서는 여러 개의 Task 모델을 리스트 형태로 응답함
async def list_tasks():
    return [task_schema.Task(id=1, title="첫 번째 ToDo 작업", done=False)]
    # * Task 모델 형식에 맞는 임시 데이터를 리스트 형태로 만들어 반환함
    # * 실제 DB 연동 시에는 DB에서 데이터를 꺼내서 여기에 넣을 예정
    #   (외부 조인이라는 방식으로 처리됨 - 모든 할 일을 보여주되, 완료된 것도 함께 표시함함)


# ------------------------------------------------------------------------
# [2] 할 일 추가 (POST 요청)
# - 클라이언트가 JSON 형식으로 보낸 데이터(title)를 받아
#   새로운 할 일을 생성하는 기능 (예; {"title": "책 읽기"})
# -------------------------------------------------------------------------
@router.post("/tasks", response_model=task_schema.TaskCreateResponse)
# - task_body: 사용자가 보낸 데이터 요청 본문
# - TaskCreate: 사용자가 보낸 데이터(title만 포함됨)
# TaskCreateResponse: 응답할 때 포함할 데이터(id 포함)
async def create_task(
    task_body: task_schema.TaskCreate, db: AsyncSession = Depends(get_db)
):
    return await task_crud.create_task(db, task_body)
    # * crud 모듈의 create_task() 함수를 호출하여 실제 DB에 저장함
    # * 저장 후 생성된 할 일(Task)을 반환하며, 그 안에는 id가 포함됨
    #   (예: TaskCreateResponse(id=1, title="책 읽기"))


# ---------------------------------------------------------------------------
# [3] 할 일 수정 (PUT 요청청)
# - 경로에 포함된 번호(task_id)에 해당하는 할 일을 수정함
# - 클라이언트가 수정할 내용을 JSON으로 보내면 title을 바꿔주는 역할할
# ---------------------------------------------------------------------------
@router.put("/task/{task_id}", response_model=task_schema.TaskCreateResponse)
# - task_id: URL 경로에 포함된 숫자 (수정 대상 할 일 번호)
# - task_body: 수정할 내용을 담은 요청 본문 (title)
async def update_task(task_id: int, task_body: task_schema.TaskCreate):
    return task_schema.TaskCreateResponse(id=task_id, **task_body.model_dump())
    # * id는 수정 대상 번호 그대로 사용
    # * 수정된 title과 함께 응답 구조(TaskCreateResponse)로 반환
    # * model_dump()는 title 값을 딕셔너리처럼 꺼내주는 함수 (dict() 대신 사용됨)


# ---------------------------------------------------------------------------
# [4] 할 일 삭제 (DELETE 요청)
# - /tasks/번호 형식으로 요청이 오면 해당 번호의 할 일을 삭제함
# - 이 함수는 아직 DB가 없기 때문에 동작은 하지 않지만 구조만 정의함함
# ---------------------------------------------------------------------------
@router.delete("/task/{task_id}")
# - task_id: 삭제할 할 일의 번호
# - response_model이 없으므로 별도 응답 내용 없이 처리 가능 (204 No Content)
async def delete_task(task_id: int):
    return
    # * 실제 구현에서는 삭제 후 상태 코드나 메시지를 반환할 수 있음
    #   성공 시 상태 코드 (예: 204)나 메시지를 응답으로 보낼 수 있음
