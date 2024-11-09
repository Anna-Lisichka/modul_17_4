from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.user import User
from app.models.task import Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix="/user", tags=["user"])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.post('/create')
async def create_user(create_user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.username == create_user.username))
    if user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail='Sorry, User already exists'
        )
    db.execute(insert(User).values(
        username=create_user.username,
        firstname=create_user.firstname,
        lastname=create_user.lastname,
        age=create_user.age,
        slug=slugify(create_user.username)
    ))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    db.execute(insert(User).values(username=create_user.username, firstname=create_user.firstname,
                                   lastname=create_user.lastname, age=create_user.age,
                                   slug=slugify(create_user.username)))

    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, up_user: UpdateUser):
    users = db.scalar(select(User).where(User.id == user_id))
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found')
    db.execute(update(User).where(User.id == user_id).values(
        firstname=up_user.firstname,
        lastname=up_user.lastname,
        age=up_user.age))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User  update is successful'
    }


@router.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found"
        )
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    for task in tasks:
        db.delete(task)

    db.execute(delete(User).where(User.id == user_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User deleted is successful!'
    }

@router.get("/{user_id}/tasks")
def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return tasks

