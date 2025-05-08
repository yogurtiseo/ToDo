# -----------------------------------------------------------------------
# 파일명: task.py
# 위치: api/routers/task.py
# 이 파일은 "할 일(To-Do)" 기능을 처리하는 API를 정의한 곳이다.
# - /tasks로 시작하는 주소들을 FastAPI의 APIRouter로 관리하다.
# - 주요 기능: 할 일 목록 조회, 할 일 추가, 수정, 삭제
# -------------------------------------------------------------------------

# *FastAPI에서 여러 개의 URL 경로를 그룹으로 묶어 관리할 수 있게 해주는 도구
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
# - response_model: 응답의 데이터 형태를 지정함
# - 여기서는 Task 모델을 여러 개 담은 리스트를 반환한다고 지정함함
async def list_tasks(db: AsyncSession = Depends(get_db)):
    # * async: 이 함수는 '비동기 함수'임
    #   - 비동기 함수는 DB와 통신 같은 시간이 오래 걸리는 작업을
    #     기다리지 않고도 다른 작업을 처리할 수 있게 해줌
    #   - 덕분에 FastAPI 서버가 동시에 여러 요청을 효율적으로 처리 가능함

    # * await: 시간이 오래 걸리는 작업을 '기다렸다가' 실행을 이어감
    #   - 여기서는 DB 조회 작업을 기다리는데 사용함
    return await task_crud.get_task_with_done(db)
    # * 실제 DB에서 모든 할 일을 가져오고, 각 할 일이 완료되었는지도 함께 반환함
    # * 완료 여부는 'Done 테이블에 해당 할 일이 있는지'로 판단단
    #   (외부 조인이라는 방식으로 처리됨 - 모든 할 일을 보여주되, 완료된 것도 함께 표시함)


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
    # * DB에 새 Task를 저장하고, id가 포함된 응답 데이터를 반환함


# ---------------------------------------------------------------------------
# [3] 할 일 수정 (PUT 요청)
# - 경로에 포함된 번호(task_id)에 해당하는 할 일을 수정함
# - 클라이언트가 수정할 내용을 JSON으로 보내면 title을 바꿔주는 역할할
# ---------------------------------------------------------------------------
@router.put("/task/{task_id}", response_model=task_schema.TaskCreateResponse)
# - task_id: URL 경로에 포함된 숫자 (수정 대상 할 일 번호)
# - task_body: 수정할 내용을 담은 요청 본문 (title)
# - db: FastAPI가 get_db() 함수를 통해 자동으로 주입하는 DB 세션 객체체
async def update_task(
    task_id: int, task_body: task_schema.TaskCreate, db: AsyncSession = Depends(get_db)
):
    task = await task_crud.get_task(db, task_id=task_id)

    # * DB에서 해당 task_id에 맞는 Task를 조회함

    # * if: 조건문 -> 특정 조건이 참(True)이면 아래 코드를 실행함
    if task is None:
        # * raise: 예외(오류)를 의도적으로 발생시킴
        #   - 여기서는 task가 존재하지 않으면 404 오류를 발생시킴
        #   - FastAPI는 raise된 HTTPException을 자동으로 처리해서
        #     클라이언트에 "할 일을 찾을 수 없음"이라는 에러 응답을 보냄
        raise HTTPException(status_code=404, detail="Task not found")

    return await task_crud.update_task(db, task_body, original=task)
    # * 기존 Task 객체(original)의 title을 수정하고, 수정된 결과를 반환함함


# ---------------------------------------------------------------------------
# [4] 할 일 삭제 (DELETE 요청)
# - /tasks/번호 형식으로 요청이 오면 해당 번호의 할 일을 삭제함
# - 이 함수는 아직 DB가 없기 때문에 동작은 하지 않지만 구조만 정의함함
# ---------------------------------------------------------------------------
@router.delete("/task/{task_id}")
# - task_id: 삭제할 할 일의 번호
# - response_model이 없으므로 별도 응답 내용 없이 처리 가능 (204 No Content)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    # * async: 이 함수가 '비동기 함수'임을 나타냄
    #   - DB와 통신하는 동안 서버가 멈추지 않고 다른 요청도 처리할 수 있음
    #   - FastAPI는 동시에 많은 요청을 빠르게 처리하기 위해 async 사용을 권장함

    task = await task_crud.get_task(db, task_id=task_id)
    # * await: 시간이 걸리는 작업(DB 조회)이 끝날 때까지 잠깐 기다림
    #   - 비동기 DB 세션에서는 데이터를 읽거나 쓸 때 항상 await를 붙여야 함

    # * if: 조건문 -> 특정 조건이 참일 때만 아래 코드를 실행함
    if task is None:
        # * raise: 오류(예외)를 의도적으로 발생시킴
        #   - 해당 Task가 DB에 존재하지 않으면 404 Not Found 오류 발생
        #   - FastAPI는 이 오류를 받아서 클라이언트에 에러 응답을 자동으로 전송함
        raise HTTPException(status_code=404, detail="Task not found")
    return await task_crud.delete_task(db, original=task)
    # * curd 모듈의 delete_task() 함수를 호출하여 실제로 DB에서 삭제함
    # * await: 삭제 작업이 끝날 때까지 기다림
    # * 반환값이 없으므로 FastAPI는 자동으로 204 No Content 응답을 보냄
