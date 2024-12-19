from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

from .schemas import Message, Token, UserList, UserPublic, UserSchema

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
        password=get_password_hash(user.password.get_secret_value()),
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
    current_user=Depends(get_current_user),
):
    users = await session.scalars(select(User).limit(limit).offset(skip))
    return {'users': users}


@app.get('/users/{user_id}', response_model=UserPublic)
async def read_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return user


@app.put('/users/', response_model=UserPublic)
async def update_user(
    user: UserSchema,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password.get_secret_value())

    await session.commit()
    await session.refresh(current_user)

    return current_user


@app.delete('/users/', response_model=Message)
async def delete_user(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted'}


@app.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await session.scalar(
        select(User).where(User.username == form_data.username)
    )

    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect username or password',
        )

    access_token = create_access_token(data_claims={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'Bearer'}
