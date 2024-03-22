import uvicorn
import settings
from fastapi import FastAPI
from routes import users, deals, products


app = FastAPI(
    title='BurimGarant',
    description='Сервис для безопасного обмена товарами между двумя сторонами.',
    debug=settings.DEBUG
)

app.include_router(users.router)
app.include_router(deals.router)
app.include_router(products.router)


if __name__ == '__main__':
    uvicorn.run(host=settings.HOST, port=settings.PORT, app=app)
