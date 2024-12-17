import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
import requests
import os
from aiogram.types import FSInputFile  # Добавляем импорт для работы с файлами
from gtts import gTTS  # Для генерации голосового сообщения
from googletrans import Translator
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import sqlite3
from config import TOKEN

# Настройка хранилища
storage = MemoryStorage()

# Создание бота
bot = Bot(token=TOKEN)

# Создание диспетчера
dp = Dispatcher(storage=storage)

# Создание роутера
router = Router()

# Регистрация роутера в диспетчере
dp.include_router(router)

# Обработчик команды /start
@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет, я start")

# Обработчик команды /help
@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer("/start")
    await message.answer("/help")
    await message.answer("1.При вложении фото - сохраняет в папке /img")
    await message.answer("2./voice - голосовой тест")
    await message.answer("3.При наборе текста - перевод на английский")

# Обработчик команды /voice
@router.message(Command("voice"))
async def send_voice(message: Message):
    try:
        # Текст для голосового сообщения
        text = "Привет, это голосовой тест, it is voice test"

        # Проверка текста
        if not text.strip():
            raise ValueError("Текст для синтеза пустой!")

        # Генерация голосового сообщения
        voice_file_path = "sample.ogg"
        print("Начинаю генерацию голосового сообщения...")
        tts = gTTS(text=text, lang="ru")
        tts.save(voice_file_path)  # Сохраняем файл
        print(f"Файл {voice_file_path} успешно сохранён.")

        # Проверка: был ли создан файл
        if not os.path.exists(voice_file_path):
            raise FileNotFoundError("Файл голосового сообщения не был создан!")

        # Проверка: файл не пустой
        if os.path.getsize(voice_file_path) == 0:
            raise ValueError("Сгенерированный аудиофайл пустой!")

        # Отправляем голосовое сообщение
        print(f"Отправляю голосовое сообщение: {voice_file_path}")
        voice = FSInputFile(voice_file_path)
        await message.answer_voice(voice)

        # # Удаляем файл после отправки пока закоментирую
        # os.remove(voice_file_path)
        # print(f"Файл {voice_file_path} успешно удалён.")

        # Уведомляем об успешной отправке
        await message.answer("Голосовое сообщение отправлено!")
    except Exception as e:
        # Логируем ошибку и уведомляем пользователя
        print(f"Ошибка при создании голосового сообщения: {e}")
        await message.answer("Произошла ошибка при создании голосового сообщения.")



# Обработчик фото
@router.message(lambda message: message.photo)
async def handle_photo(message: Message):
    # Проверяем и создаем папку img, если ее нет
    if not os.path.exists("img"):
        os.makedirs("img")

    # Получаем лучшее качество фото
    photo = message.photo[-1]  # Фото с наивысшим разрешением

    # Получаем файл через API Telegram
    file = await bot.get_file(photo.file_id)

    # Устанавливаем путь для сохранения фото
    file_path = f"img/{photo.file_id}.jpg"

    # Сохраняем фото
    await bot.download_file(file.file_path, destination=file_path)

    await message.answer("Фото сохранено!")

# Создаем объект Translator
translator = Translator()

@router.message()
async def translate_text(message: Message):
    try:
        # Проверяем, является ли текст командой
        if message.text.startswith('/'):
            return  # Если это команда, ничего не делаем

        # Получаем текст пользователя
        user_text = message.text

        # Переводим текст на английский
        translated = translator.translate(user_text, src="auto", dest="en")

        # Отправляем переведенный текст пользователю
        await message.answer(f"Перевод на английский:\n{translated.text}")
    except Exception as e:
        print(f"Ошибка при переводе текста: {e}")
        await message.answer("Произошла ошибка при переводе текста.")


# Основная функция
async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

# Исполнение программы
if __name__ == "__main__":
    asyncio.run(main())
