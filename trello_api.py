import requests
import logging
from typing import Tuple, Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class TrelloManager:
    def __init__(self, api_key: str, token: str, base_url: str = "https://api.trello.com/1"):
        self.api_key = api_key
        self.token = token
        self.base_url = base_url
        self.auth_params = {"key": api_key, "token": token}
        self.custom_fields_cache = {}

    # получить ID списка по названию
    def get_list_id(self, board_id: str, list_name: str) -> Optional[str]:
        url = f"{self.base_url}/boards/{board_id}/lists"

        try:
            response = requests.get(url, params=self.auth_params, timeout=10)

            if response.status_code == 200:
                lists = response.json()
                for list_item in lists:
                    if list_item['name'].lower() == list_name.lower():
                        return list_item['id']
                logger.warning(f"Список '{list_name}' не найден в доске")
                return None
            else:
                logger.error(
                    f"Ошибка при получении списков: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения с Trello: {e}")
            return None

    # получить кастомные поля доски с информацией о типах
    def get_custom_fields(self, board_id: str) -> Dict[str, Dict]:
        if board_id in self.custom_fields_cache:
            return self.custom_fields_cache[board_id]

        url = f"{self.base_url}/boards/{board_id}/customFields"

        try:
            response = requests.get(url, params=self.auth_params, timeout=10)

            if response.status_code == 200:
                custom_fields = {}
                for field in response.json():
                    custom_fields[field['name'].lower()] = {
                        'id': field['id'],
                        'type': field['type']
                    }

                self.custom_fields_cache[board_id] = custom_fields
                return custom_fields
            else:
                logger.error(
                    f"Ошибка при получении кастомных полей: {response.status_code} - {response.text}")
                return {}

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Ошибка соединения при получении кастомных полей: {e}")
            return {}

    def parse_date_string(self, date_string: str) -> Optional[str]:
        """Парсинг даты - используем только дату без времени в формате YYYY-MM-DD"""
        try:
            # берем только часть до пробела (игнорируем время)
            date_part = date_string.split()[0].strip()

            # убрать возможные кавычки
            date_part = date_part.replace('"', '').replace("'", "")

            # пробуем основные форматы дат
            formats = [
                '%d.%m.%Y',    # 18.08.2025
                '%Y-%m-%d',    # 2025-08-18
                '%d/%m/%Y',    # 18/08/2025
                '%m/%d/%Y'     # 08/18/2025
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(date_part, fmt)
                    # возвращаем в формате YYYY-MM-DD
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue

            logger.warning(f"Не удалось распарсить дату: {date_string}")
            return None

        except Exception as e:
            logger.error(f"Ошибка при парсинге даты: {e}")
            return None

    # установить значение кастомного поля с учетом типа
    def set_custom_field_value(self, card_id: str, field_id: str, field_type: str, value: str) -> bool:
        url = f"{self.base_url}/card/{card_id}/customField/{field_id}/item"

        if field_type == 'date':
            # для полей с типом дата
            parsed_date = self.parse_date_string(value)
            if not parsed_date:
                logger.warning(f"Неверный формат даты для поля: {value}")
                return False

            # для полей даты используем только дату в формате YYYY-MM-DD
            payload = {
                "value": {
                    "date": parsed_date
                }
            }
        else:
            # для текстовых полей
            payload = {
                "value": {
                    "text": value
                }
            }

        try:
            response = requests.put(
                url, json=payload, params=self.auth_params, timeout=10)

            if response.status_code == 200:
                logger.info(
                    f"Установлено значение поля: {value} (тип: {field_type})")
                return True
            else:
                logger.error(
                    f"Ошибка при установке значения поля: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения при установке значения поля: {e}")
            return False

    # создать карточку с кастомными полями
    def create_card_with_custom_fields(self, list_id: str, name: str, desc: str, custom_fields_data: Dict[str, str], board_id: str) -> Tuple[bool, Any]:
        # сначала создаем карточку
        url = f"{self.base_url}/cards"
        params = {
            **self.auth_params,
            "idList": list_id,
            "name": name,
            "desc": desc,
            "pos": "top"
        }

        try:
            response = requests.post(url, params=params, timeout=10)

            if response.status_code == 200:
                card_data = response.json()
                card_id = card_data['id']

                # получить кастомные поля с информацией о типах
                custom_fields = self.get_custom_fields(board_id)

                # установить значения кастомных полей
                for field_name, field_value in custom_fields_data.items():
                    field_name_lower = field_name.lower()
                    if field_name_lower in custom_fields:
                        field_info = custom_fields[field_name_lower]
                        field_id = field_info['id']
                        field_type = field_info['type']

                        self.set_custom_field_value(
                            card_id, field_id, field_type, field_value)
                    else:
                        logger.warning(
                            f"Кастомное поле '{field_name}' не найдено на доске")

                logger.info(f"Карточка создана с кастомными полями: {name}")
                return True, card_data
            else:
                logger.error(
                    f"Ошибка при создании карточки: {response.status_code} - {response.text}")
                return False, response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения при создании карточки: {e}")
            return False, str(e)

    # создать карточку в Trello (старый метод для обратной совместимости)
    def create_card(self, list_id: str, name: str, desc: str) -> Tuple[bool, Any]:
        return self.create_card_with_custom_fields(list_id, name, desc, {}, "")
