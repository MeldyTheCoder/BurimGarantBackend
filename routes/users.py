import fastapi
from models import sqlalchemy, pydantic
from auth import (
    authenticate_user,
    get_user,
    create_password_hash,
    create_token,
    UserType,
    handle_role
)

router = fastapi.APIRouter(
    prefix='/users',
    tags=['Пользователи'],
)


INCORRECT_LOGIN_DATA_EXCEPTION = fastapi.HTTPException(
    status_code=fastapi.status.HTTP_400_BAD_REQUEST,
    detail='Неверные данные для входа.'
)

INCORRECT_REGISTRATION_DATA_EXCEPTION = fastapi.HTTPException(
    status_code=fastapi.status.HTTP_400_BAD_REQUEST,
    detail='Неверные данные для регистрации.'
)

USER_ALREADY_EXISTS_EXCEPTION = fastapi.HTTPException(
    status_code=fastapi.status.HTTP_403_FORBIDDEN,
    detail='Пользователь с данной почтой уже существует.'
)


@router.get('/{user_id}/', name='Просмотр пользователя')
async def get_user_endpoint():
    return None


@router.post('/append/', name='Тестовая функция на проверку роли')
async def append_user_endpoint(
    user: UserType
):
    handle_role(user, sqlalchemy.UserRoles.MODERATOR)

    return {'detail': 'appended', 'user': user}


@router.post('/token/', name='Получение токена авторизации')
async def get_token_endpoint(form_data: pydantic.UserLoginModel):
    """
    Генерирует Bearer-токен для авторизации.
    """

    if not form_data:
        raise INCORRECT_LOGIN_DATA_EXCEPTION

    user = authenticate_user(form_data.email, form_data.password)
    if not user:
        raise INCORRECT_LOGIN_DATA_EXCEPTION

    return {'user': user, 'token': create_token(user)}


@router.post('/register/', name='Регистрация пользователя')
async def register_user_endpoint(form_data: pydantic.UserRegisterModel):
    """
    Регистрирует пользователя в БД.
    """

    if not form_data:
        raise INCORRECT_REGISTRATION_DATA_EXCEPTION

    email = form_data.email
    if get_user(email):
        raise USER_ALREADY_EXISTS_EXCEPTION

    password = form_data.password
    password_hash = create_password_hash(password)

    created_user = sqlalchemy.User.create(
        email=form_data.email,
        password_hash=password_hash,
        first_name=form_data.first_name,
        last_name=form_data.last_name
    )

    return pydantic.UserModel.model_validate(obj=created_user)


@router.post('/registration/email/', name='Проверка почты на регистрацию')
async def validate_registration_email_endpoint(form_data: pydantic.EmailCheckModel):
    """
    Проверка почты на ее занятость другим пользователем.
    Данная функция нужна для валидации поля почты на клиенте.
    """

    if get_user(form_data.email):
        return {'detail': False}

    return {'detail': True}
