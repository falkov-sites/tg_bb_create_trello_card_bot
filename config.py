import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
    TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
    TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
    TRELLO_LIST = os.getenv('TRELLO_LIST')
    BASE_URL = "https://api.trello.com/1"

    # TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_BOT_TOKEN = os.getenv('TG_FALKOV_PROBA_BOT_TOKEN')

    # Обязательные поля
    REQUIRED_FIELDS = [
        "имя карточки",
        "дата заказа",
        "крайний срок",
        "клиент",
        "цвет",
        "имя",
        "телефон",
        "описание"
    ]


# проверка обязательных переменных окружения
def validate_config():
    required_vars = {
        'TRELLO_API_KEY': Config.TRELLO_API_KEY,
        'TRELLO_TOKEN': Config.TRELLO_TOKEN,
        'TRELLO_BOARD_ID': Config.TRELLO_BOARD_ID,
        'TRELLO_LIST': Config.TRELLO_LIST,
        'TELEGRAM_BOT_TOKEN': Config.TELEGRAM_BOT_TOKEN
    }

    missing_vars = [var for var, value in required_vars.items() if not value]

    if missing_vars:
        raise ValueError(
            f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
