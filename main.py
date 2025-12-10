import asyncio

from bd import initialize_database, add_user, add_balance_water, get_balance_water, reset_balance_water
from record_log import log_info, log_error
from config import token

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from datetime import datetime, timedelta, time




bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

router = Router()

initialize_database()


def get_water_keyboard():
    try:
        builder = ReplyKeyboardBuilder()

        builder.add(
            KeyboardButton(text="➕ Add 100 ml 💧"),
            KeyboardButton(text="➕ Add 250 ml 💦"),
            KeyboardButton(text="➕ Add 300 ml 🚰"),
            KeyboardButton(text="👤 Account")
        )

        builder.adjust(3, 1)

        return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

    except Exception as e:
        log_error(f"Get water keyboard: {e}")



@router.message(Command('start'))
async def start(message: types.Message):
    log_info('Welcome')

    user_id = message.from_user.id
    add_user(user_id)

    try:
        await message.answer(
            text="👋Hey there! I'm a bot that helps track how much water you drink each day 💧🚰✨",
            reply_markup=get_water_keyboard())

    except Exception as e:
        log_error(f"We couldn't send a message: {e}")




@router.message(F.text.lower())
async def get_message(message: types.Message):
    log_info('Get message')

    user_id = message.from_user.id

    words = {'add', 'ml', 'of', 'water'}
    message_words = set(message.text.lower().split())
    if words.issubset(message_words):

        rama = message.text.split()

        ml = rama[1].replace('ml', '')

        add_balance_water(user_id, ml)

        try:
            await message.reply(f'Ready! You added: {ml} ml 💧\nYour balance today: {get_balance_water(user_id)}')

        except Exception as e:
            log_error(f"We couldn't send a message: {e}")



    elif message.text == '👤 Account':
        balance_water = get_balance_water(user_id)


        try:
            await message.answer(
            f'Hi, {message.from_user.first_name}! \n'
            f'👋You can read what the bot remembers and what data we collect here. 🔒\n\n'
            f'Your balance today: {balance_water} ml 💧',

            parse_mode='Markdown',
            disable_web_page_preview=True
            )

        except Exception as e:
            log_error(f"We couldn't send a message: {e}")


def register_handlers(dp: Dispatcher):
    dp.include_router(router)



async def daily_reset_loop():
    """Asynchronous loop for the daily balance reset at 00:00."""
    # Асинхронный цикл для ежедневного сброса баланса в полночь.
    while True:
        now = datetime.now()

        # Calculate the time until the next midnight (00:00)
        # Рассчитываем точное время до следующей полуночи (00:00)
        tomorrow = now.date() + timedelta(days=1)
        midnight = datetime.combine(tomorrow, time(0, 0))

        # Time to wait, in seconds
        # Время ожидания, выраженное в секундах
        time_to_wait = (midnight - now).total_seconds()

        if time_to_wait > 0:
            # Wait until midnight (00:00)
            # Ожидаем до наступления полуночи
            await asyncio.sleep(time_to_wait)

            # Reset the balance
            # Сбрасываем счетчик выпитой воды
            reset_balance_water()
            log_info('Water balance reset')

        else:
             # If the time calculation was skipped or lagged (e.g., already past midnight), wait one second and re-calculate
             # Если мы пропустили полночь или произошла задержка, ждем 1 секунду и пересчитываем время
             await asyncio.sleep(1)




async def main():
    register_handlers(dp)
    try:
        asyncio.create_task(daily_reset_loop())

        await dp.start_polling(bot)


    except (KeyboardInterrupt, SystemExit):
        log_error(f"Closing down")


    except Exception:
        await asyncio.sleep(5)
        log_error(f"Closing down")


if __name__ == '__main__':
    asyncio.run(main())