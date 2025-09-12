import re
import logging
from typing import Dict, Optional, Tuple, List

logger = logging.getLogger(__name__)


def parse_message(text: str) -> Dict[str, str]:
    """Парсинг сообщения и извлечение данных"""
    patterns = {
        "имя карточки": r'"имя карточки":\s*"([^"]+)"',
        "дата заказа": r'"дата заказа":\s*(.+?)(?=\n|$)',
        "крайний срок": r'"крайний срок":\s*(.+?)(?=\n|$)',
        "клиент": r'"клиент":\s*"([^"]+)"',
        "цвет": r'"цвет":\s*"([^"]+)"',
        "имя": r'"имя":\s*"([^"]+)"',
        "телефон": r'"телефон":\s*"([^"]+)"',
        "описание": r'"описание":\s*"([^"]+)"'
    }

    data = {}
    for key, pattern in patterns.items():
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Для дат убираем кавычки и оставляем только дату
                if key in ['дата заказа', 'крайний срок']:
                    value = value.replace('"', '').replace("'", "").split()[0]
                data[key] = value
            else:
                # Попробуем найти без кавычек
                alt_pattern = pattern.replace('"', '')
                match = re.search(alt_pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if key in ['дата заказа', 'крайний срок']:
                        value = value.replace('"', '').replace(
                            "'", "").split()[0]
                    data[key] = value
        except Exception as e:
            logger.warning(f"Ошибка при парсинге поля {key}: {e}")

    return data


def format_card_description(data: Dict[str, str]) -> str:
    """Форматирование описания карточки"""
    description = f"""📋 **Детали заказа:**

📝 **Название карточки:** {data.get('имя карточки', 'Не указано')}
📅 **Дата заказа:** {data.get('дата заказа', 'Не указано')}
⏰ **Крайний срок:** {data.get('крайний срок', 'Не указано')}
👥 **Клиент:** {data.get('клиент', 'Не указано')}
🎨 **Цвет:** {data.get('цвет', 'Не указано')}
👤 **Имя:** {data.get('имя', 'Не указано')}
📞 **Телефон:** {data.get('телефон', 'Не указано')}
📝 **Описание:** {data.get('описание', 'Не указано')}

#заказ #новый_заказ"""

    return description


# проверка наличия обязательных полей
def validate_required_fields(data: Dict[str, str], required_fields: List[str]) -> Tuple[bool, List[str]]:
    missing_fields = [
        field for field in required_fields if field not in data or not data[field]]
    return len(missing_fields) == 0, missing_fields
