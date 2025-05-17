from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


from database import add_user, get_user_count, show_movie, add_movie, delete_movie, get_liked_movies, add_liked_movie, remove_liked_movie, sendPostPeople
import config
import asyncio

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class SearchState(StatesGroup):
    searched = State()

@dp.message(CommandStart())
async def start_cmd(message: Message):

    add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
        InlineKeyboardButton(text="Искать фильмы🔍", callback_data="searchFilms"), 
        InlineKeyboardButton(text="Понравившиеся❤️", callback_data='show_movies')
        ]
    ])

    await message.answer("""🍿 Добро пожаловать в КИНО-БОТИЩЕ!\n\nТут не болтают — тут ищут фильмы по кодам 🎯\n\n🔍 Увидел в TikTok код типа 4382?\nКидай его сюда — и магия случится ✨\n\n📦 Я дам тебе:\n— Название 🎬\n— Краткое описание (без спойлеров, я ж не чудовище) 😌\n— Картинку, чтоб убедиться, что это не «Зелёный слоник» 😳\n\n❤️ Понравилось? Жми сердечко — и фильм в избранном.\n\nВперёд, пока попкорн не остыл! 🍿🔥""",
            parse_mode="HTML",
            reply_markup=keyboard
    )

@dp.message(Command("menu"))
async def menu_cmd(message: Message):
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Искать фильмы🔍", callback_data="searchFilms"), 
                InlineKeyboardButton(text="Понравившиеся❤️", callback_data='show_movies')
            ],
            [
                InlineKeyboardButton(text="Поддержать проект", callback_data="support")
            ]
        ])

    await message.answer("""🎬 Тот самый бот из TikTok\n\n👀 Увидел код под видео и не знаешь, что за фильм?\n📥 Просто отправь его сюда — я найду, без лишних движений.""",
        parse_mode="HTML",
        reply_markup=keyboard
        )
    
# --- Обработка кнопки "Проверить подписку"
@dp.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    if await config.check_all_subscriptions(bot, user_id):
        await callback.message.delete()
        await start_cmd(callback.message)
    else:
        await callback.answer("❌ Вы ещё не подписались на все каналы!", show_alert=True)

@dp.callback_query(F.data == "searchFilms")
async def searchFilms(callback: CallbackQuery, state: FSMContext):

    userId = callback.from_user.id
    chatId = callback.message.chat.id

    if not await config.check_all_subscriptions(bot, userId):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[ 
            [InlineKeyboardButton(text=f"Канал {i}", url=item)]
            for i, item in enumerate(config.channels, start=1)
        ] + [[InlineKeyboardButton(text="Я подписался на все каналы", callback_data='check_subscription')]]
        )

        await bot.send_photo(
            chatId,
            photo="https://imgur.com/QRjNKW2",
            caption="Перед тем как запустить бота, убедись, что подписался на наших спонсоров! Ведь хорошие фильмы — это не только код, но и поддержка от тех, кто нас любит 😉",
            reply_markup=keyboard
        )
    else:

        await state.set_state(SearchState.searched)
        await callback.message.delete()

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад↩️ ", callback_data="backToMenu")]
        ])

        await callback.message.answer("Напиши код ниже в формате (ХХХХ)⬇️", reply_markup=keyboard)

@dp.message(SearchState.searched)
async def search_code(message: Message, state: FSMContext):
    code = message.text.strip()
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not code.isdigit():
        await message.answer("Код должен быть только из цифр! 🔢")
        return
    
    result = show_movie(int(code))

    if result:
        try:
            title, description, image_url = result

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="❤️", callback_data=f"like_{code}"),
                    InlineKeyboardButton(text="💔", callback_data=f"dislike_{code}")
                ],
                [
                    InlineKeyboardButton(text="🔙 Назад", callback_data="back")
                ]
            ])

            await bot.send_photo(
                chat_id,
                image_url,
                caption=f"Название фильма: {hbold(title)}, \n ------ \n{hbold(description)}",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            await message.answer("Произошла ошибка при обработке запроса. Попробуйте позже.")
            return
    else:
        await message.answer("Фильм не найден.")

@dp.callback_query(F.data == "show_movies")
async def liked_cmd(callback: CallbackQuery):

    user_id = callback.from_user.id
    liked_movies = get_liked_movies(user_id)  # Получаем список кодов фильмов

    await callback.message.delete()

    if not liked_movies:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад↩️ ", callback_data="backToMenu")]
        ])
        await callback.message.answer("Ты ещё ничего не лайкнул(а) 🎬💤", reply_markup=keyboard)
    else:
        print(f"User {user_id} liked movies: {liked_movies}")

        # Формируем текст со списком фильмов
        lines = []
        for code in liked_movies:
            result = show_movie(code)
            if result:
                title, _, _ = result
                lines.append(f"{title} — {code}")

        text = "Избранное 🎬:\n\n" + "\n".join(lines)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад↩️ ", callback_data="backToMenu")]
        ])

        await bot.send_message(callback.from_user.id, text, reply_markup=keyboard)

@dp.callback_query(F.data == "backToMenu")
async def backToMenu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()

    await menu_cmd(callback.message)

@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()

    await menu_cmd(callback.message)

@dp.callback_query(F.data.startswith('like_'))
async def like_movie(callback_query: CallbackQuery):
    # Извлекаем код фильма из callback_data
    code = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id

    # Проверяем, понравился ли уже этот фильм пользователю
    liked_movies = get_liked_movies(user_id)
    if code not in liked_movies:
        add_liked_movie(user_id, code)  # Добавляем фильм в список понравившихся
        await callback_query.answer("Фильм добавлен в список понравившихся!")
    else:
        await callback_query.answer("Этот фильм уже в списке понравившихся.", show_alert=True)

@dp.callback_query(F.data.startswith('dislike_'))
async def dislike_movie(callback_query: CallbackQuery):
    code = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id

    liked_movies = get_liked_movies(user_id)
    if code in liked_movies:
        remove_liked_movie(user_id, code)
        await callback_query.answer("Фильм удалён из списка понравившихся!")
    else:
        await callback_query.answer("Этот фильм не в списке понравившихся.", show_alert=True)


async def send_post_cmd(sources, image_url, text, ids):
    success_count = 0
    error_count = 0

    if image_url == "-":

        for user_id in ids:
            try:

                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Перейти⬆️", url=sources)]
                ])

                await bot.send_message(
                    user_id,
                    text=f"{text}",
                    reply_markup=kb
                )
                success_count += 1
                await asyncio.sleep(0.1)  # Затримка для уникнення флуду
            except Exception as e:
                error_count += 1
                print(f"Ошибка: {user_id}: {e}")

        print(f"Рассылка завершена. Успешно: {success_count}\n, Ошибок: {error_count}")

    else:

        for user_id in ids:
            try:
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Перейти⬆️", url=sources)]
                ])

                await bot.send_photo(
                    user_id,
                    image_url,
                    caption=f"{text}",
                    reply_markup=kb
                )
                success_count += 1
                await asyncio.sleep(0.1)  # Затримка для уникнення флуду
            except Exception as e:
                error_count += 1
                print(f"Ошибка: {user_id}: {e}")

        print(f"Рассылка завершена. Успешно: {success_count}\n, Ошибок: {error_count}")

async def process_post(text, image_url, sources):
    # Отправляем пост в каналы
    ids = sendPostPeople()
    print(ids)
    await send_post_cmd(sources, image_url, text, ids)

async def main():
    await dp.start_polling(bot, skip_updates=True)
