from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema
from fast_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

T_AsyncSession = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=UserPublic, status_code=HTTPStatus.CREATED)
async def create_user(user: UserSchema, session: T_AsyncSession):
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
        password=get_password_hash(user.password.get_secret_value()),
        email=user.email,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=UserList)
async def read_users(
    session: T_AsyncSession,
    current_user: T_CurrentUser,
    limit: int = 10,
    skip: int = 0,
):
    users = await session.scalars(select(User).limit(limit).offset(skip))
    return {'users': users}


@router.get('/{user_id}', response_model=UserPublic)
async def read_user_by_id(
    user_id: int,
    session: T_AsyncSession,
    current_user: T_CurrentUser,
):
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return user


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: T_AsyncSession,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password.get_secret_value())

    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
async def delete_user(
    user_id: int,
    session: T_AsyncSession,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted'}
