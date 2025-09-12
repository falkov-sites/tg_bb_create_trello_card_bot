from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder  # билдеры

# кнопки внизу ----------------------------------
# при клике текст на кнопке отправляется в чат, его видит юзер
reply_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Каталог')],
    [KeyboardButton(text='Корзина'), KeyboardButton(text='Контакты')]
],
    resize_keyboard=True, input_field_placeholder='Выберите пункт меню ⬇️'
)

# inline кнопки ---------------------------------
# при клике ничего не отправляется в чат
# поэтому нужно еще что-то, кроме текста (напр. url)
# или нужен callback, чтобы его обработать (см. следующую клавиатуру)
inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='Начать проверку знаний 🥲',
        # url='https://falkov-ru-en.netlify.app/',
        web_app=WebAppInfo(url='https://falkov-ru-en.netlify.app/')
    )
    ]
])

# callback inline кнопки ------------------------
# чтобы понять, какая кнопка нажата, отправляем callback
# обрабатывается хендлером с фильтром F - @router.callback_query(F.data == 'catalog')
# callback не видит юзер, можно передать ID и др.
callback_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Каталог', callback_data='catalog')],
    [
        InlineKeyboardButton(text='Корзина', callback_data='basket'),
        InlineKeyboardButton(text='Контакты', callback_data='contacts')
    ]
])


# билдеры =================================================
cars = ['Tesla', 'Mersedes', 'bmw']


# reply builder ---------------------------------
async def reply_kb_cars():
    keyboard = ReplyKeyboardBuilder()
    for car in cars:
        keyboard.add(KeyboardButton(text=car))
    return keyboard.adjust(2).as_markup()  # 2 кнопки в ряду


# inline builder --------------------------------
async def inline_kb_cars():
    keyboard = InlineKeyboardBuilder()
    for car in cars:
        keyboard.add(InlineKeyboardButton(
            text=car, url='https://falkov-ru-en.netlify.app/'))
    return keyboard.adjust(2).as_markup()  # 2 кнопки в ряду


# разные примеры --------------------------------
# async def client_name(name):
#     return ReplyKeyboardMarkup(keyboard=[
#         [KeyboardButton(text=name)]
#     ],
#         resize_keyboard=True,
#         input_field_placeholder='Введите имя или оставьте как есть'
#     )

# async def client_location():
#     return ReplyKeyboardMarkup(keyboard=[
#         [KeyboardButton(text='Отправить геолокацию', request_location=True)]
#     ],
#         resize_keyboard=True,
#         input_field_placeholder='Ваш адрес доставки или отправьте геолокоцию'
#     )

# async def client_phone():
#     return ReplyKeyboardMarkup(keyboard=[
#         [KeyboardButton(text='☎️  Поделиться контактом', request_contact=True)]
#     ],
#         resize_keyboard=True,
#         input_field_placeholder='Введите номер или поделитесь контактом ⬇️'
#     )

# async def categories():
#     keyboard = InlineKeyboardBuilder()
#     all_categories = await get_all_categories()
#     for category in all_categories:
#         keyboard.add(InlineKeyboardButton(text=category.name,
#                      callback_data=f'category_{category.id}'))
#     return keyboard.adjust(2).as_markup()

# async def cards(category_id):
#     keyboard = InlineKeyboardBuilder()
#     all_cards = await get_cards_by_category(category_id)
#     for card in all_cards:
#         keyboard.row(InlineKeyboardButton(  # новая кнопка в новый ряд
#             text=f'{card.name} | {card.price} rub',
#             callback_data=f'card_{card.id}')
#         )
#     keyboard.row(InlineKeyboardButton(
#         text='🔙 Назад', callback_data='categories'))
#     return keyboard.as_markup()

# async def back_to_categories(category_id, card_id):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(
#                 text='Купить', callback_data=f'buy_{card_id}')],
#             [InlineKeyboardButton(
#                 text='🔙 Назад', callback_data=f'category_{category_id}')]
#         ])
