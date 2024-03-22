import fastapi
from models import pydantic, sqlalchemy
from auth import UserType

router = fastapi.APIRouter(
    prefix='/products',
    tags=['Товары']
)

PRODUCT_NOT_FOUND = fastapi.HTTPException(
    status_code=404,
    detail='Товар не найден!'
)

IS_NOT_PRODUCT_OWNER = fastapi.HTTPException(
    status_code=403,
    detail='Вы не являетесь создателем товара.'
)


def user_is_product_creator(user: pydantic.UserModel, product: pydantic.ProductModel):
    """
    Функция для проверки пользователя на владение товаром
    """

    return product.seller.id == user.id


@router.get('/', name='Просмотр товаров')
async def get_products_endpoint():
    """
    Выводит список всех товаров.
    """

    products = sqlalchemy.Product.fetch_all()
    return pydantic.ProductListModel.model_validate(products)


@router.post('/create/', name='Создание товара')
async def create_product_endpoint(user: UserType, product: pydantic.ProductCreateModel):
    """"
    Создает товар от имени авторизованного пользователя
    """

    product = sqlalchemy.Product().create(
        seller_id=user.id,
        **product.model_dump()
    )

    return pydantic.ProductModel.model_validate(product)


@router.delete('/{product_id}/delete/', name='Удаление товара')
async def delete_product_endpoint(user: UserType, product_id: int):
    """
    Удаляет товар по его ID. Только для владельца указанного товара.
    """

    product = sqlalchemy.Product.fetch_one(id=product_id)

    if not product:
        raise PRODUCT_NOT_FOUND

    product = pydantic.ProductModel.model_validate(product)
    if not user_is_product_creator(user, product):
        raise IS_NOT_PRODUCT_OWNER

    sqlalchemy.Product.delete(id=product.id)
    return product


@router.get('/{product_id}/', name='Просмотр товара')
async def get_product_endpoint(product_id: int):
    """
    Выводит товар по его ID
    """

    product = sqlalchemy.Product.fetch_one(id=product_id)

    if not product:
        raise PRODUCT_NOT_FOUND

    product = pydantic.ProductModel.model_validate(product)
    return product


@router.patch('/{product_id}/update/', name='Обновление товара')
async def get_product_endpoint(user: UserType, product_id: int, product: pydantic.ProductCreateModel):
    """
    Обновляет товар по его ID. Только для владельцев указанного товара.
    """

    product_fetched = sqlalchemy.Product.fetch_one(id=product_id)

    if not product_fetched:
        raise PRODUCT_NOT_FOUND

    product_validated = pydantic.ProductModel.model_validate(product_fetched)
    if not user_is_product_creator(user, product_validated):
        raise IS_NOT_PRODUCT_OWNER

    product = sqlalchemy.Product.update(product_id, **product.model_dump(exclude_unset=True))
    return product



