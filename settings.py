import os


# Секретный ключ проекта для валидации паролей
# И создания их хэшей
SECRET_KEY = 'rgjerjgierjgierjigjerierti_secret_228'

# Индикатор режима отладки проекта
DEBUG = bool(os.getenv('DEBUG', True))

# Хост, на котором будет запущен бекенд.
HOST = os.getenv('HOST', '0.0.0.0')

# Порт, на котором будет запущен бекенд.
PORT = int(os.getenv('PORT', '8000'))

# Ссылка на подключение к БД
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+pg8000://kirill:1234@localhost:5433/garant')