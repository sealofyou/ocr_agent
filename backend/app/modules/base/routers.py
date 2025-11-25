from fastapi import APIRouter, Depends
from app.utils.logger import logging

# from db.session import get_db
# from . import schemas, crud

router = APIRouter()


@router.get("/test")
def base():
    logging.info("base")
    return {"message": "base"}

# @router.post("/users/", response_model=schemas.UserOut)
# def create_user(user: schemas.UserCreate, db=Depends(get_db)):
#     return crud.create_user(db, user)
#
#
# @router.get("/users/{user_id}", response_model=schemas.UserOut)
# def read_user(user_id: int, db=Depends(get_db)):
#     return crud.get_user(db, user_id)
