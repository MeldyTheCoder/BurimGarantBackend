import pydantic
from typing import Optional, Union
from datetime import datetime
from . import sqlalchemy


class PydanticModel(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    """
    Базовая модель Pydantic
    """


class UserLoginModel(PydanticModel):
    """
    Модель для авторизации пользователя
    """

    email: str = pydantic.Field(
        description='Эл. почта пользователя'
    )

    password: str = pydantic.Field(
        description='Пароль пользователя'
    )


class UserRegisterModel(PydanticModel):
    """
    Модель для регистрации пользователя
    """

    email: str = pydantic.Field(
        description='Эл. почта пользователя',
        serialization_alias='email',
        validation_alias=pydantic.AliasChoices('email')
    )

    password: str = pydantic.Field(
        description='Пароль пользователя',
        serialization_alias='password',
        validation_alias=pydantic.AliasChoices('password')
    )

    first_name: str = pydantic.Field(
        description='Имя пользователя',
        serialization_alias='firstName',
        validation_alias=pydantic.AliasChoices('firstName', 'first_name')
    )

    last_name: str = pydantic.Field(
        description='Фамилия пользователя',
        default=None,
        serialization_alias='lastName',
        validation_alias=pydantic.AliasChoices('lastName', 'last_name')
    )


class UserModel(PydanticModel):
    """
    Модель для регистрации пользователя
    """

    id: Optional[int] = pydantic.Field(
        description='ID пользователя',
        serialization_alias='id',
        validation_alias=pydantic.AliasChoices('id')
    )

    email: str = pydantic.Field(
        description='Эл. почта пользователя',
        serialization_alias='email',
        validation_alias=pydantic.AliasChoices('email')
    )

    password_hash: str = pydantic.Field(
        description='Хэш пароля пользователя',
        serialization_alias='passwordHash',
        validation_alias=pydantic.AliasChoices('passwordHash', 'password_hash')
    )

    first_name: str = pydantic.Field(
        description='Имя пользователя',
        serialization_alias='firstName',
        validation_alias=pydantic.AliasChoices('firstName', 'first_name')
    )

    last_name: Optional[str] = pydantic.Field(
        description='Фамилия пользователя',
        default=None,
        serialization_alias='lastName',
        validation_alias=pydantic.AliasChoices('lastName', 'last_name')
    )

    date_joined: Optional[Union[datetime, str]] = pydantic.Field(
        description='Дата регистрации пользователя',
        default=None,
        serialization_alias='dateJoined',
        validation_alias=pydantic.AliasChoices('dateJoined', 'date_joined')
    )

    date_password_changed: Optional[Union[datetime, str]] = pydantic.Field(
        description='Дата смены пароля пользователя',
        default=None,
        serialization_alias='datePasswordChanged',
        validation_alias=pydantic.AliasChoices('datePasswordChanged', 'date_password_changed')
    )

    email_verified: Optional[bool] = pydantic.Field(
        description='Почта пользователя подтверждена',
        default=False,
        serialization_alias='emailVerified',
        validation_alias=pydantic.AliasChoices('emailVerified', 'email_verified')
    )

    role: sqlalchemy.UserRoles = pydantic.Field(
        description='Роль пользователя',
        default=sqlalchemy.UserRoles.USER,
        serialization_alias='role',
        validation_alias=pydantic.AliasChoices('role')
    )


class EmailCheckModel(PydanticModel):
    """
    Модель для проверки почты на занятость
    """

    email: str = pydantic.Field(
        description='Почта пользователя',
        alias='email'
    )


class ProductModel(PydanticModel):
    """
    Модель для валидации товара
    """

    id: Optional[int] = pydantic.Field(
        description='ID товара',
        serialization_alias='id',
        validation_alias=pydantic.AliasChoices('id')
    )

    seller: UserModel = pydantic.Field(
        description='Продавец товара',
        serialization_alias='seller',
        validation_alias='seller'
    )

    title: str = pydantic.Field(
        description='Заголовок товара',
        serialization_alias='title',
        validation_alias='title'
    )

    description: str = pydantic.Field(
        description='Описание товара',
        serialization_alias='description',
        validation_alias='description'
    )

    attachments: list[str] = pydantic.Field(
        description='Ссылки на вложения',
        serialization_alias='attachments',
        validation_alias='attachments'
    )

    price: int = pydantic.Field(
        description='Цена товара',
        serialization_alias='price',
        validation_alias='price'
    )

    quantity_left: int = pydantic.Field(
        description='Кол-во оставшегося товара',
        serialization_alias='quantityLeft',
        validation_alias=pydantic.AliasChoices('quantityLeft', 'quantity_left')
    )

    @pydantic.field_validator('quantity_left')
    def validate_quantity_left(cls, value: int):
        if value < 0:
            raise pydantic.ValidationError(
                'Значение кол-во оставшегося товара должно быть больше нуля.'
            )

        return value

    @pydantic.field_validator('price')
    def validate_quantity_left(cls, value: int):
        if value < 0:
            raise pydantic.ValidationError(
                'Значение цены товара должно быть больше нуля.'
            )

        return value


class DealModel(PydanticModel):
    """
    Модель для валидации сделки
    """

    id: Optional[int] = pydantic.Field(
        description='ID сделки',
        serialization_alias='id',
        validation_alias=pydantic.AliasChoices('id')
    )

    seller: UserModel = pydantic.Field(
        description='Продавец',
        serialization_alias='seller',
        validation_alias=pydantic.AliasChoices('seller')
    )

    consumer: UserModel = pydantic.Field(
        description='Покупатель',
        serialization_alias='consumer',
        validation_alias=pydantic.AliasChoices('consumer')
    )

    product: ProductModel = pydantic.Field(
        description='Товар',
        serialization_alias='product',
        validation_alias=pydantic.AliasChoices('product')
    )

    quantity: int = pydantic.Field(
        description='Кол-во покупаемого товара',
        serialization_alias='quantity',
        validation_alias=pydantic.AliasChoices('quantity')
    )

    status: sqlalchemy.DealStatuses = pydantic.Field(
        description='Статус сделки',
        serialization_alias='status',
        validation_alias=pydantic.AliasChoices('status')
    )

    price: int = pydantic.Field(
        description='Цена сделки',
        serialization_alias='price',
        validation_alias=pydantic.AliasChoices('price')
    )

    @pydantic.field_validator('quantity')
    def validate_quantity_left(cls, value: int):
        if value < 0:
            raise pydantic.ValidationError(
                'Значение цены товара должно быть больше нуля.'
            )

        return value


class DealListModel(pydantic.RootModel):
    root: list[DealModel]


class ProductListModel(pydantic.RootModel):
    root: list[ProductModel]


class ProductCreateModel(PydanticModel):
    """
    Модель для валидации товара
    """

    title: str = pydantic.Field(
        description='Заголовок товара',
        serialization_alias='title',
        validation_alias='title'
    )

    description: str = pydantic.Field(
        description='Описание товара',
        serialization_alias='description',
        validation_alias='description'
    )

    attachments: list[str] = pydantic.Field(
        description='Ссылки на вложения',
        serialization_alias='attachments',
        validation_alias='attachments'
    )

    price: int = pydantic.Field(
        description='Цена товара',
        serialization_alias='price',
        validation_alias='price'
    )

    quantity_left: int = pydantic.Field(
        description='Кол-во оставшегося товара',
        serialization_alias='quantityLeft',
        validation_alias=pydantic.AliasChoices('quantityLeft', 'quantity_left')
    )

    @pydantic.field_validator('quantity_left')
    def validate_quantity_left(cls, value: int):
        if value < 0:
            raise pydantic.ValidationError(
                'Значение кол-во оставшегося товара должно быть больше нуля.'
            )

        return value

    @pydantic.field_validator('price')
    def validate_quantity_left(cls, value: int):
        if value < 0:
            raise pydantic.ValidationError(
                'Значение цены товара должно быть больше нуля.'
            )

        return value


class DealCreateModel(PydanticModel):
    """
    Модель для создания сделки
    """

    product: ProductModel = pydantic.Field(
        description='Товар',
        serialization_alias='product',
        validation_alias=pydantic.AliasChoices('product')
    )

    quantity: int = pydantic.Field(
        description='Кол-во покупаемого товара',
        serialization_alias='quantity',
        validation_alias=pydantic.AliasChoices('quantity')
    )

    @pydantic.field_validator('quantity')
    def validate_quantity_left(cls, value: int):
        if value < 0:
            raise pydantic.ValidationError(
                'Значение цены товара должно быть больше нуля.'
            )

        return value