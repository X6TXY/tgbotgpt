import asyncio
import os
from askgpt import askbot
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ParseMode,
    ReplyKeyboardMarkup,
)
from dotenv import load_dotenv
# from motor.motor_asyncio import AsyncIOMotorClient

# import question as qs
from companynews import get_news
from investgpt import main as testgpt_main
from newsmarket import get_market_news
from spheregpt import main as spheregpt_main
from yf import get_recommendations_summary, graph
from yf import news as yf_news

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# MONGO_URI = os.getenv("MONGO_URI")
# MONGO_DB = os.getenv("MONGO_DB")

# client = AsyncIOMotorClient(MONGO_URI)
# db = client[MONGO_DB]
# user_collections = db["user"]

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


USER_STATE = {}
PICK_STATES = {}
CHECK_STATES = {}


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Лучшие компании для инвестирования! 🌐"),
        ],
        [
            KeyboardButton(text="Сектора"),
        ],
        [
            KeyboardButton(text="Функции"),
            KeyboardButton(text="График цен акции"),
        ],
    ],
    resize_keyboard=True,
)

keyboard_functions = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Получить новости рынка"),
            KeyboardButton(text="Получить новости компании"),
        ],
        [
            KeyboardButton(text="Рекомендации"),
            KeyboardButton(text="Новости Yahoo Finance"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ],
    resize_keyboard=True,
)


# async def find_user(user):
#     result = await user_collections.find_one(user)
#     return result


@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    USER_STATE[message.from_user.id] = ""
    PICK_STATES[message.from_user.id] = 0
    CHECK_STATES[message.from_user.id] = 0
    # user_id = message.from_user.id
    # user_paid = False
    # user_data = {
    #     "_id": user_id,
    #     "user_paid": user_paid,
    #     "name": message.from_user.first_name,
    #     "news": True,
    # }

    # user_data_from_db = await find_user(user_data)

    # if not user_data_from_db:
        # welcome_msg = f"Привет, {message.from_user.first_name}. Чтобы начать пользоваться ботом, сперва пройдите опрос."
        # question_msg = "1. Инвестиционные цели:"
        # await bot.send_message(message.from_user.id, welcome_msg)
        # await bot.send_message(
        #     message.from_user.id, question_msg, reply_markup=qs.first_keyboard
        # )
    # else:
    welcome_msg = """🚀 Добро пожаловать в мир инвестиций с Narasense AI! 📈

Ты хочешь увеличить свои доходы и стать успешным инвестором? Не знаешь, с какой акции начать? Мы здесь, чтобы помочь тебе в этом увлекательном путешествии!

✨ Что делает Narasense AI для тебя:

📊 Анализ Рынка: Наш искусственный интеллект ежедневно сканирует рынок, выявляя перспективные акции для инвестирования.

🔍 Точные Рекомендации: Получай точные рекомендации от нашего бота, основанные на глубоком анализе данных и трендов.

💡 Образование и Советы: Узнавай новые стратегии, получай образовательный контент и советы от опытных инвесторов.

🔄 Постоянное Обновление: Мы постоянно обновляем информацию, чтобы ты всегда был в курсе последних событий на финансовых рынках.

🔒 Безопасность и Прозрачность: Твои данные в безопасности, а наши рекомендации прозрачны и обоснованы.

🚀 Стань успешным инвестором с Narasense AI прямо сейчас!

Присоединяйся к нам и давай зарабатывать вместе! 💰

📈 Не упусти свой шанс на финансовый успех с Narasense AI! 🚀"""
    await bot.send_message(message.chat.id, welcome_msg , reply_markup=keyboard)


@dp.message_handler(commands=["graph"])
async def handler_company_graph(message: types.Message):
    try:
        ticker = message.text.split(" ", 1)[1].strip()

        image_path = graph(ticker)

        with open(image_path, "rb") as photo:
            await message.reply_photo(
                photo, caption=f"{ticker} Цена акций с течением времени"
            )

        os.remove(image_path)

    except IndexError:
        await message.reply("Пожалуйста, укажите тикер компании. Например: /graph AAPL")


@dp.message_handler(
    lambda message: message.text == "Лучшие компании для инвестирования! 🌐"
)
async def handle_test_gpt(message: types.Message):
    image_path = "generated_image.png"
    with open(image_path, "rb") as image_file:
        await bot.send_photo(message.chat.id, photo=image_file)
    loading_message = await message.reply("Загрузка...")
    response = testgpt_main()
    await asyncio.sleep(2)

    await bot.edit_message_text(
        response, chat_id=loading_message.chat.id, message_id=loading_message.message_id
    )


@dp.message_handler(
    lambda message: message.text == "Сектора"
)
async def handle_test_gpt(message: types.Message):
    loading_message = await message.reply("Загрузка...")
    response = spheregpt_main()
    await asyncio.sleep(2)

    await bot.edit_message_text(
        response, chat_id=loading_message.chat.id, message_id=loading_message.message_id
    )


# @dp.callback_query_handler(lambda c: c.data.startswith("answer_"))
# async def process_answer(callback_query: CallbackQuery):
#     answer = callback_query.data.replace("answer_", "")
#     PICK_STATES[callback_query.from_user.id] += int(answer)
#     CHECK_STATES[callback_query.from_user.id] += int(1)

#     skip_count = CHECK_STATES[callback_query.from_user.id]
#     keyboard = InlineKeyboardMarkup()
#     key1 = ""
#     if CHECK_STATES[callback_query.from_user.id] != 7:
#         for key, value in qs.questions.items():
#             if skip_count > 1:
#                 skip_count -= 1
#                 continue
#             key1 = key
#             for answer in value:
#                 item_after_count = answer.split()
#                 final = ""
#                 for item in item_after_count:
#                     if "answer_" in item:
#                         continue
#                     final += f"{item} "
#                 keyboard.add(
#                     InlineKeyboardButton(final, callback_data=item_after_count[0])
#                 )
#             break
#         await bot.edit_message_text(
#             key1,
#             chat_id=callback_query.from_user.id,
#             message_id=callback_query.message.message_id,
#             reply_markup=keyboard,
#         )
#     else:
#         await bot.edit_message_text(
#             f"Вы закончили тест. Ваш результат: {PICK_STATES[callback_query.from_user.id]}",
#             chat_id=callback_query.from_user.id,
#             message_id=callback_query.message.message_id,
#         )
#         congr = "Теперь вы можете пользоваться Ботом!"
#         await bot.send_message(
#             callback_query.from_user.id, congr, reply_markup=keyboard
#         )
#         user1 = {
#             "_id": callback_query.from_user.id,
#             "user_paid": False,
#             "name": callback_query.from_user.first_name,
#             "news": True,
#             "points": PICK_STATES[callback_query.from_user.id],
#         }
        # user_collections.insert_one(user1)


@dp.message_handler(lambda message: message.text == "Функции")
async def handle_functions(message: types.Message):
    await message.reply("Выберите функцию:", reply_markup=keyboard_functions)


@dp.message_handler(lambda message: message.text == "Назад")
async def handle_functions(message: types.Message):
    await message.reply(text="Вы вернулись в главное меню", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Получить новости рынка")
async def handle_market_news(message: types.Message):
    response = get_market_news()
    await message.reply(
        response, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard
    )


@dp.message_handler(lambda message: message.text == "Получить новости компании")
async def handler_company_news(message: types.Message):
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")


@dp.message_handler(lambda message: message.text == "Рекомендации")
async def handle_recommendations(message: types.Message):
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")


@dp.message_handler(lambda message: message.text == "Новости Yahoo Finance")
async def handler_company_news(message: types.Message):
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")


@dp.message_handler(lambda message: message.text == "График цен акции")
async def handler_graph(message: types.Message):
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")

@dp.message_handler(commands=['ask'])
async def askgpt(message: types.Message):
    loading_message = await message.reply("Загрузка...")
    response = askbot(message.text)
    await asyncio.sleep(2)

    await bot.edit_message_text(
    text=response,
    chat_id=loading_message.chat.id,
    message_id=loading_message.message_id,
    # reply_markup=keyboard
)


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_ticker(message: types.Message):
    try:
        if USER_STATE[message.from_user.id] == "Рекомендации":
            ticker = message.text.upper()
            response = get_recommendations_summary(ticker)
            await message.answer(
                response, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard
            )
            USER_STATE[message.from_user.id] = ""
        elif USER_STATE[message.from_user.id] == "Новости Yahoo Finance":
            ticker = message.text.upper()
            response = yf_news(ticker)
            await message.answer(
                response, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard
            )
            USER_STATE[message.from_user.id] = ""
        elif USER_STATE[message.from_user.id] == "График цен акции":
            ticker = message.text.upper()
            image_path = graph(ticker)
            with open(image_path, "rb") as photo:
                await message.reply_photo(photo, caption=f"{ticker} Stock Price Over Time")
            os.remove(image_path)
            USER_STATE[message.from_user.id] = ""
        elif USER_STATE[message.from_user.id] == "Получить новости компании":
            ticker = message.text.upper()
            response = get_news(ticker)

            await message.answer(
                response, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
            )
            USER_STATE[message.from_user.id] = ""
        else:
            pass
    except:
        pass


# @dp.message_handler(commands=["graph"])
# async def handler_company_graph(message: types.Message):
#     try:
#         ticker = message.text.split(" ", 1)[1].strip()


#         image_path = graph(ticker)


#         with open(image_path, 'rb') as photo:
#             await message.reply_photo(photo, caption=f'{ticker} Цена акций с течением времени')

#         os.remove(image_path)

#     except IndexError:
#         await message.reply("Пожалуйста, укажите тикер компании. Например: /graph AAPL")

# @dp.message_handler(lambda message: message.text == "Лучшие компании для инвестирования! 🌐")
# async def handle_test_gpt(message: types.Message):
#     image_path = "generated_image.png"
#     with open(image_path, "rb") as image_file:
#         await bot.send_photo(message.chat.id, photo=image_file)
#     loading_message = await message.reply("Загрузка...")
#     response = testgpt_main()
#     await asyncio.sleep(2)

#     await bot.edit_message_text(
#         response, chat_id=loading_message.chat.id, message_id=loading_message.message_id
#     )

# @dp.message_handler(lambda message: message.text == "Сектора")
# async def handle_test_gpt(message: types.Message):
#     loading_message = await message.reply("Загрузка...")
#     response = spheregpt_main()
#     await asyncio.sleep(2)

#     await bot.edit_message_text(
#         response, chat_id=loading_message.chat.id, message_id=loading_message.message_id
#     )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
