from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User

from .schemas import Message, UserList, UserPublic, UserSchema

app = FastAPI()


@app.get('/')
async def read_root():
    return {'message': 'Olá Mundo!'}


@app.post('/users/', response_model=UserPublic, status_code=HTTPStatus.CREATED)
async def create_user(
    user: UserSchema, session: AsyncSession = Depends(get_session)
):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Email already exists'
            )

    db_user = User(
        username=user.username,
        password=user.password.get_secret_value(),
        email=user.email,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
async def read_users(
    limit: int = 10,
    skip: int = 0,
    session: AsyncSession = Depends(get_session),
):
    users = await session.scalars(select(User).limit(limit).offset(skip))
    return {'users': users}


@app.get('/users/{user_id}', response_model=UserPublic)
async def read_user_by_id(
    user_id: int, session: AsyncSession = Depends(get_session)
):
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return user


@app.put('/users/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: AsyncSession = Depends(get_session),
):
    db_user = await session.scalar(select(User).where(User.id == user_id))
    if db_user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    db_user.email = user.email
    db_user.username = user.username
    db_user.password = user.password.get_secret_value()

    await session.commit()
    await session.refresh(db_user)

    return db_user


@app.delete('/users/{user_id}', response_model=Message)
async def delete_user(
    user_id: int, session: AsyncSession = Depends(get_session)
):
    db_user = await session.scalar(select(User).where(User.id == user_id))
    if db_user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    await session.delete(db_user)
    await session.commit()

    return {'message': 'User deleted'}
