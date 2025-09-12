import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
import asyncio

from trello_api import TrelloManager
from utils import parse_message, format_card_description, validate_required_fields
from config import Config, validate_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# bot = Bot(token=Config.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

trello_manager = TrelloManager(Config.TRELLO_API_KEY, Config.TRELLO_TOKEN)


# обработка команды start ---------------------------------
@dp.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = """👋 Привет! Я бот для создания заказов в Trello.

📝 Отправьте мне сообщение в формате:

"имя карточки": "Стол и стулья для охраны"
"дата заказа": 18.08.2025
"крайний срок": 02.10.2025
"клиент": "очень хороший клиент"
"цвет": "терракот"
"имя": "Сергей Фальков"
"телефон": "+7 (987) 654 3210"
"описание": "проверка работы заполнения карточки из бота"

💡 Время указывать не нужно - используются только даты.

Я создам карточку в Trello с этими данными."""
    await message.answer(welcome_text)


# обработка команды help ----------------------------------
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """Помощь по использованию бота:

Просто отправьте сообщение с данными заказа в указанном формате, и я создам карточку в Trello.

Обязательные поля:
  - имя карточки
  - дата заказа (только дата, без времени)
  - крайний срок (только дата, без времени)
  - клиент
  - цвет
  - имя
  - телефон
  - описание

Пример:
"имя карточки": "Название заказа"
"дата заказа": 18.08.2025
"крайний срок": 02.10.2025
"клиент": "клиент"
"цвет": "цвет"
"имя": "имя"
"телефон": "+7 XXX XXX XXXX"
"описание": "описание заказа"
"""
    await message.answer(help_text)


# обработка команды fields --------------------------------
@dp.message(Command("fields"))
async def cmd_fields(message: Message):
    """Показать доступные кастомные поля"""
    try:
        custom_fields = trello_manager.get_custom_fields(
            Config.TRELLO_BOARD_ID)

        if custom_fields:
            fields_list = "\n".join(
                [f"• {field_name} ({field_info['type']})" for field_name, field_info in custom_fields.items()])
            await message.answer(
                f"📊 **Доступные кастомные поля на доске:**\n\n{fields_list}\n\n"
                f"Всего полей: {len(custom_fields)}"
            )
        else:
            await message.answer("❌ Не удалось получить кастомные поля или их нет на доске")
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении кастомных полей: {e}")


# Обработчик всех сообщений -------------------------------
@dp.message()
async def handle_message(message: Message):
    try:
        # Парсим сообщение
        data = parse_message(message.text)
        logger.info(f"Распарсенные данные: {data}")

        # Проверяем обязательные поля
        is_valid, missing_fields = validate_required_fields(
            data, Config.REQUIRED_FIELDS)

        if not is_valid:
            await message.answer(
                f"❌ Отсутствуют обязательные поля: {', '.join(missing_fields)}\n\n"
                "Используйте /help для просмотра формата."
            )
            return

        # Получаем ID списка в Trello
        list_id = trello_manager.get_list_id(
            Config.TRELLO_BOARD_ID, Config.TRELLO_LIST)
        if not list_id:
            await message.answer("❌ Не удалось найти указанный список в Trello. Проверьте настройки.")
            return

        # форматируем данные для карточки
        card_name = data['имя карточки']
        card_description = format_card_description(data)

        # подготовка данных для кастомных полей
        custom_fields_mapping = {
            "дата заказа": "дата заказа",
            "крайний срок": "крайний срок",
            "клиент": "клиент",
            "цвет": "цвет",
            "имя": "имя",
            "телефон": "телефон"
        }

        custom_fields_data = {}
        for field_key, field_name in custom_fields_mapping.items():
            if field_key in data:
                custom_fields_data[field_name] = data[field_key]

        # Создаем карточку в Trello с кастомными полями
        success, result = trello_manager.create_card_with_custom_fields(
            list_id,
            card_name,
            card_description,
            custom_fields_data,
            Config.TRELLO_BOARD_ID
        )

        if success:
            card_url = result.get('shortUrl', result.get('url', ''))
            await message.answer(
                f"✅ Карточка успешно создана в Trello!\n\n"
                f"📋 **Название:** {card_name}\n"
                f"🔗 **Ссылка:** {card_url}\n"
                f"📊 **Заполнены кастомные поля:** {', '.join(custom_fields_data.keys())}"
            )
        else:
            await message.answer(f"❌ Ошибка при создании карточки: {result}")

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке сообщения. Проверьте формат и попробуйте еще раз.\n\n"
            "Используйте /help для просмотра формата."
        )


async def main():
    """Основная функция"""
    try:
        # Проверяем конфигурацию
        validate_config()
        logger.info("Конфигурация проверена успешно")

        # Запускаем бота
        logger.info("Бот запущен")
        await dp.start_polling(bot)

    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
