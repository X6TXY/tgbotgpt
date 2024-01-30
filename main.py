from library import *
load_dotenv()

PICK_STATES = {}
CHECK_STATES = {}

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

user_manager = user.UserInteractionHandler(
db.users_collection, bot
)

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Лучшие компании для инвестирования! 🌐"),
            
        ],[KeyboardButton(text="Лучшие сферы для Инвестирования в 2024 году! 🚀"),],
        [KeyboardButton(text="Функции"),KeyboardButton(text="График цен акции"),]
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


@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    
    PICK_STATES[message.from_user.id] = 0
    CHECK_STATES[message.from_user.id] = 0
    user_id = message.from_user.id
    user_paid = False
    user_data = {
        "_id": user_id,
        "user_paid": user_paid,
        "_name": message.from_user.first_name,
        "_news": True,
        "_points": PICK_STATES[message.from_user.id],
    }

    # db.users.update_one({"_id": user_id}, {"$set": user_data}, upsert=True)

    await message.reply(
        """🚀 Добро пожаловать в мир инвестиций с Narasense AI! 📈

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
    )
    if bool(user_manager.find_user(user_data)) == False:
        welcome_msg = f"Привет, {message.from_user.first_name}. Чтобы начать пользоваться ботом, сперва пройдите опрос."
        question_msg = "1. Investment Goals:"
        await bot.send_message(
            message.from_user.id, welcome_msg
        )
        await bot.send_message(
            message.from_user.id, question_msg, reply_markup=qs.first_keyboard
        )
    else:
        bot(chat_id=message.from_user.id, text="Вы уже зарегистрированы", reply_markup=keyboard)
        

@dp.callback_query_handler(lambda c: c.data.startswith('answer_'))
async def process_answer(callback_query: CallbackQuery):
    answer = callback_query.data.replace('answer_', '')
    PICK_STATES[callback_query.from_user.id] += int (answer)
    CHECK_STATES[callback_query.from_user.id] += int (1)
    print(PICK_STATES[callback_query.from_user.id])
    skip_count = CHECK_STATES[callback_query.from_user.id]
    keyboard1 = InlineKeyboardMarkup()
    key1 = ''
    if CHECK_STATES[callback_query.from_user.id] != 8:
        for key, value in qs.questions.items():
            if skip_count > 1: 
                skip_count -= 1
                continue
            key1 = key
            for answer in value:
                item_after_count = answer.split()
                final = ""
                for item in item_after_count:
                    if 'answer_' in item:
                        continue
                    final += f'{item} '
                keyboard1.add(InlineKeyboardButton(final, callback_data=item_after_count[0]))
            break
        await bot.edit_message_text(key1, chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, reply_markup=keyboard1)
    else:
        await bot.edit_message_text(f"Вы закончили тест. Ваш результат: {PICK_STATES[callback_query.from_user.id]}", chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        congr = "Теперь вы можете пользоваться ботом"
        await bot.send_message(callback_query.from_user.id,congr,reply_markup=keyboard)
        user1 = {
            "_id": callback_query.from_user.user_id,
            "user_paid": False,
            "_name": callback_query.from_user.first_name,
            "_news": True,
            "_points": PICK_STATES[callback_query.from_user.id],
        }
        
        user_manager.add_user(user1)

@dp.message_handler(lambda message: message.text == "Функции")
async def handle_functions(message: types.Message):
    await message.reply("Выберите функцию:", reply_markup=keyboard_functions)


@dp.message_handler(lambda message: message.text == "Назад")
async def handle_functions(message: types.Message):
    await message.reply(text="Вы вернулись в главное меню", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Получить новости рынка")
async def handle_market_news(message: types.Message):
    response = get_market_news()
    await message.reply(response, parse_mode=types.ParseMode.MARKDOWN,reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Получить новости компании")
async def handler_company_news(message: types.Message):
    await message.answer("Введите тикер компании:")

    @dp.message_handler(content_types=types.ContentTypes.TEXT)
    async def process_ticker_input(message: types.Message):
        ticker = message.text.upper() 
        response = get_news(ticker)

        await message.answer(response, parse_mode=ParseMode.MARKDOWN,reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Рекомендации")
async def handle_recommendations(message: types.Message):
    await message.answer("Введите тикер компании:")
    @dp.message_handler(content_types=types.ContentTypes.TEXT)
    async def process_ticker(message: types.Message):
        ticker = message.text.upper()
        response = get_recommendations_summary(ticker)
        await message.answer(response,parse_mode=types.ParseMode.MARKDOWN,reply_markup=keyboard)
        

@dp.message_handler(lambda message: message.text == "Новости Yahoo Finance")
async def handler_company_news(message: types.Message):
    await message.answer("Введите тикер компании:")
    @dp.message_handler(content_types=types.ContentTypes.TEXT)
    async def process_ticker(message: types.Message):
        ticker = message.text.upper()
        response = yf_news(ticker)
        await message.answer(response,parse_mode=types.ParseMode.MARKDOWN,reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "График цен акции")
async def handler_graph(message: types.Message):
    await message.answer("Введите тикер компании:")
    @dp.message_handler(content_types=types.ContentTypes.TEXT)
    async def process_ticker(message: types.Message):
        ticker = message.text.upper()
        image_path = graph(ticker)
        with open(image_path, 'rb') as photo:
            await message.reply_photo(photo, caption=f'{ticker} Stock Price Over Time')

        os.remove(image_path)


@dp.message_handler(commands=["graph"])
async def handler_company_graph(message: types.Message):
    try:
        ticker = message.text.split(" ", 1)[1].strip()


        image_path = graph(ticker)


        with open(image_path, 'rb') as photo:
            await message.reply_photo(photo, caption=f'{ticker} Stock Price Over Time')

        os.remove(image_path)

    except IndexError:
        await message.reply("Please provide a company ticker. For example: /graph AAPL")

@dp.message_handler(lambda message: message.text == "Лучшие компании для инвестирования! 🌐")
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

@dp.message_handler(lambda message: message.text == "Лучшие сферы для Инвестирования в 2024 году! 🚀")
async def handle_test_gpt(message: types.Message):
    loading_message = await message.reply("Загрузка...")
    response = spheregpt_main()
    await asyncio.sleep(2)

    await bot.edit_message_text(
        response, chat_id=loading_message.chat.id, message_id=loading_message.message_id
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
