# CHAT GPT

import fastapi
from models import sqlalchemy, pydantic
from auth import UserType

router = fastapi.APIRouter(
    prefix='/deals',
    tags=['Сделки']
)

DEAL_NOT_FOUND_EXCEPTION = fastapi.HTTPException(
    status_code=404,
    detail='Сделка не найдена!'
)

NOT_A_SELLER_EXCEPTION = fastapi.HTTPException(
    status_code=403,
    detail='Вы не являетесь продавцом в данной сделке.'
)

NOT_A_CONSUMER_EXCEPTION = fastapi.HTTPException(
    status_code=403,
    detail='Вы не являетесь покупателем в данной сделке.'
)

DEAL_IS_NOT_PAID = fastapi.HTTPException(
    status_code=402,
    detail='Сделка еще не оплачена!'
)

DEAL_IS_ALREADY_PAID = fastapi.HTTPException(
    status_code=403,
    detail='Сделка уже была оплачена!'
)

DEAL_IS_PAUSED = fastapi.HTTPException(
    status_code=403,
    detail='Сделка находится в арбитраже, или она уже была закрыта.'
)

PRODUCT_ALREADY_SUPPLIED = fastapi.HTTPException(
    status_code=403,
    detail='Товар уже был отправлен покупателю.'
)

PRODUCT_IS_NOT_SUPPLIED = fastapi.HTTPException(
    status_code=403,
    detail='Товар еще не был отправлен покупателю.'
)

BLOCKED_DEAL_STATUSES = [
    sqlalchemy.DealStatuses.ARBITRATION,
    sqlalchemy.DealStatuses.CANCELED_BY_CONSUMER,
    sqlalchemy.DealStatuses.CANCELED_BY_SELLER
]


def user_in_deal(user: pydantic.UserModel, deal: pydantic.DealModel):
    user_id = user.id

    if user_id != deal.seller.id and user_id != deal.consumer.id:
        return False

    return True


def user_is_seller(user: pydantic.UserModel, deal: pydantic.DealModel):
    return user.id == deal.seller.id


def user_is_consumer(user: pydantic.UserModel, deal: pydantic.DealModel):
    return user.id == deal.consumer.id


@router.get('/create/', name='Создание сделки')
async def create_deal_endpoint(user: UserType, deal: pydantic.DealCreateModel):
    seller = deal.product.seller
    consumer = user
    quantity = deal.quantity
    product = deal.product

    deal = sqlalchemy.Deal.create(
        seller_id=seller.id,
        consumer_id=consumer.id,
        product_id=product.id,
        quantity=quantity,
    )

    return pydantic.DealModel.model_validate(deal)


@router.get('/{deal_id}/', name='Просмотр данных сделки')
async def get_deal_info_endpoint(user: UserType, deal_id: int):
    deal = sqlalchemy.Deal.fetch_one(id=deal_id)

    if not deal:
        raise DEAL_NOT_FOUND_EXCEPTION

    deal = pydantic.DealModel.model_validate(deal)

    if not user_in_deal(user, deal):
        raise DEAL_NOT_FOUND_EXCEPTION

    elif user.role not in [sqlalchemy.UserRoles.ADMIN, sqlalchemy.UserRoles.MODERATOR]:
        raise DEAL_NOT_FOUND_EXCEPTION

    return pydantic.DealModel.model_validate(deal)


@router.post('/{deal_id}/pay-for-product/', name='Перевод сделки в статус "Оплачен"')
async def pay_for_product_endpoint(user: UserType, deal_id: int):
    deal = sqlalchemy.Deal.fetch_one(id=deal_id)

    if not deal:
        raise DEAL_NOT_FOUND_EXCEPTION

    deal = pydantic.DealModel.model_validate(deal)

    if not user_in_deal(user, deal):
        raise DEAL_NOT_FOUND_EXCEPTION

    elif not user_is_consumer(user, deal):
        raise NOT_A_CONSUMER_EXCEPTION

    elif deal.status in BLOCKED_DEAL_STATUSES:
        raise DEAL_IS_PAUSED

    elif deal.status in [
        sqlalchemy.DealStatuses.PRODUCT_SUPPLIED,
        sqlalchemy.DealStatuses.PAID
    ]:
        raise DEAL_IS_ALREADY_PAID

    deal = sqlalchemy.Deal.update(deal.id, status=sqlalchemy.DealStatuses.PAID)
    return pydantic.DealModel.model_validate(deal)


@router.post('/{deal_id}/cancel/', name='Отмена сделки')
async def cancel_deal_endpoint(user: UserType, deal_id: int):
    deal = sqlalchemy.Deal.fetch_one(id=deal_id)

    if not deal:
        raise DEAL_NOT_FOUND_EXCEPTION

    deal = pydantic.DealModel.model_validate(deal)

    if not user_in_deal(user, deal):
        raise DEAL_NOT_FOUND_EXCEPTION

    elif deal.status in BLOCKED_DEAL_STATUSES:
        raise DEAL_IS_PAUSED

    elif deal.status in [
        sqlalchemy.DealStatuses.PRODUCT_SUPPLIED,
        sqlalchemy.DealStatuses.PAID
    ]:
        raise DEAL_IS_ALREADY_PAID

    if user_is_consumer(user, deal):
        deal = sqlalchemy.Deal.update(deal.id, status=sqlalchemy.DealStatuses.CANCELED_BY_CONSUMER)

    elif user_is_seller(user, deal):
        deal = sqlalchemy.Deal.update(deal.id, status=sqlalchemy.DealStatuses.CANCELED_BY_SELLER)

    return pydantic.DealModel.model_validate(deal)


@router.post('/{deal_id}/supply-product/', name='Отправка товара сделки покупателю')
async def attach_product_to_deal_endpoint(user: UserType, deal_id: int):
    deal = sqlalchemy.Deal.fetch_one(id=deal_id)

    if not deal:
        raise DEAL_NOT_FOUND_EXCEPTION

    deal = pydantic.DealModel.model_validate(deal)

    if not user_in_deal(user, deal):
        raise DEAL_NOT_FOUND_EXCEPTION

    elif not user_is_seller(user, deal):
        raise NOT_A_SELLER_EXCEPTION

    elif deal.status in BLOCKED_DEAL_STATUSES:
        raise DEAL_IS_PAUSED

    elif deal.status == sqlalchemy.DealStatuses.PRODUCT_SUPPLIED:
        raise PRODUCT_ALREADY_SUPPLIED

    elif not deal.status == sqlalchemy.DealStatuses.PAID:
        raise DEAL_IS_NOT_PAID

    deal = sqlalchemy.Deal.update(deal.id, status=sqlalchemy.DealStatuses.PRODUCT_SUPPLIED)
    return pydantic.DealModel.model_validate(deal)


@router.post('/{deal_id}/submit/', name='Подтверждение окончания сделки')
async def submit_deal_endpoint(user: UserType, deal_id: int):
    deal = sqlalchemy.Deal.fetch_one(id=deal_id)

    if not deal:
        raise DEAL_NOT_FOUND_EXCEPTION

    deal = pydantic.DealModel.model_validate(deal)

    if not user_in_deal(user, deal):
        raise DEAL_NOT_FOUND_EXCEPTION

    elif not user_is_consumer(user, deal):
        raise NOT_A_CONSUMER_EXCEPTION

    elif deal.status in BLOCKED_DEAL_STATUSES:
        raise DEAL_IS_PAUSED

    elif not deal.status == sqlalchemy.DealStatuses.PRODUCT_SUPPLIED:
        raise PRODUCT_IS_NOT_SUPPLIED

    deal = sqlalchemy.Deal.update(deal.id, status=sqlalchemy.DealStatuses.CLOSED_SUCCESSFULLY)
    return pydantic.DealModel.model_validate(deal)


@router.post('/{deal_id}/arbitration/', name='Перевод сделки в статус арбитража')
async def set_deal_to_arbitration_endpoint(user: UserType, deal_id: int):
    deal = sqlalchemy.Deal.fetch_one(id=deal_id)

    if not deal:
        raise DEAL_NOT_FOUND_EXCEPTION

    deal = pydantic.DealModel.model_validate(deal)

    if not user_in_deal(user, deal):
        raise DEAL_NOT_FOUND_EXCEPTION

    elif deal.status in BLOCKED_DEAL_STATUSES:
        raise DEAL_IS_PAUSED

    elif not deal.status == sqlalchemy.DealStatuses.PRODUCT_SUPPLIED:
        raise PRODUCT_IS_NOT_SUPPLIED

    deal = sqlalchemy.Deal.update(deal.id, status=sqlalchemy.DealStatuses.CLOSED_SUCCESSFULLY)
    return pydantic.DealModel.model_validate(deal)


@router.get('/sells/', name='Просмотр продаж авторизованного пользователя')
async def get_list_of_deals(user: UserType, status: sqlalchemy.DealStatuses = None):
    kwargs = {
        'seller_id': user.id
    }

    if status:
        kwargs['status'] = status

    deals = sqlalchemy.Deal.fetch_all(**kwargs)
    return pydantic.DealListModel.model_validate(deals)


@router.get('/purchases/', name='Просмотр покупок авторизованного пользователя')
async def get_list_of_purchases(user: UserType, status: sqlalchemy.DealStatuses = None):
    kwargs = {
        'consumer_id': user.id
    }

    if status:
        kwargs['status'] = status

    deals = sqlalchemy.Deal.fetch_all(**kwargs)
    return pydantic.DealListModel.model_validate(deals)


@router.get('/', name='Просмотр всех сделок авторизованного пользователя')
async def get_list_of_deals(user: UserType, status: sqlalchemy.DealStatuses = None):
    kwargs = {}
    if status:
        kwargs['status'] = status

    deals = sqlalchemy.Deal.fetch_all(
        consumer_id=user.id,
        **kwargs
    ) + sqlalchemy.Deal.fetch_all(
        seller_id=user.id,
        **kwargs
    )

    return pydantic.DealListModel.model_validate(deals)
