from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message):
    # await msg.reply(f'Привет\nТвой ID: {msg.from_user.id}\nИмя: {msg.from_user.first_name}',
    await msg.reply(f'Привет {msg.from_user.first_name}!',
                    # reply_markup=kb.reply_kb                # reply keyboard
                    reply_markup=kb.inline_kb               # inline keyboard
                    # reply_markup=kb.callback_kb             # callback inline кнопки

                    # билдеры - много динамических кнопок:
                    # reply_markup=await kb.reply_kb_cars()   # reply builder
                    # reply_markup=await kb.inline_kb_cars()  # inline builder
                    )


# handler для обработки callback ------------------------------------
@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    # нужно одно из трех callback.answer, чтобы telegram правильно сработал
    await callback.answer('')
    # await callback.answer('вы выбрали каталог')  # сообщение
    # await callback.answer('вы выбрали каталог', show_alert=True) # всплывающее окно

    # пошлет новую клавиатуру в следующем сообщении:
    await callback.message.answer('привет', reply_markup=kb.inline_kb_cars)

    # заменит клавиатуру на новую в этом же сообщении (edit_text):
    await callback.message.edit_text('привет', reply_markup=kb.inline_kb_cars)


@router.message()
async def get_help(msg: Message):
    await msg.answer('Это команда /help')


@router.message(Command('help'))
async def get_help(msg: Message):
    await msg.answer('Это команда /help')


@router.message(F.text == 'Как дела')
async def how_are_you(msg: Message):
    await msg.answer('Все хорошо')


@router.message(Command('get_photo'))
async def get_photo(msg: Message):
    await msg.answer_photo(photo='https://....', caption='это фото')
