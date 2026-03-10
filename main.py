import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from brain import ask_lawyer
from config import Config
from tools import process_stt, process_tts, process_document

bot = Bot(token=Config.TG_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
os.makedirs("downloads", exist_ok=True)

class UserState(StatesGroup):
    is_lawyer = State()
    is_tts = State()
    is_ocr = State()

def get_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚖️ Юрист (Кыргызча)"), KeyboardButton(text="🎙 Озвучка (TTS)")],
            [KeyboardButton(text="📄 OCR Документ"), KeyboardButton(text="🎧 SST Голосовое")],
            [KeyboardButton(text="❌ Выход из режима")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🤖 Выберите режим работы кнопками:", reply_markup=get_main_kb())

@dp.message(F.text == "⚖️ Юрист (Кыргызча)")
async def set_lawyer(message: types.Message, state: FSMContext):
    await state.set_state(UserState.is_lawyer)
    await message.answer("✅ Режим Юриста включен. Жду вопросы на кыргызском.")

@dp.message(F.text == "🎙 Озвучка (TTS)")
async def set_tts(message: types.Message, state: FSMContext):
    await state.set_state(UserState.is_tts)
    await message.answer("✅ Режим Озвучки включен. Жду текст для превращения в аудио.")
    
@dp.message(F.text == "📄 OCR Документ") 
async def set_ocr(message: types.Message, state: FSMContext):
    await state.set_state(UserState.is_ocr)
    await message.answer("✅ Режим обработки файла. Просто пришлите мне .pdf или .docx файл.")

@dp.message(F.text == "❌ Выход из режима")
async def set_stop(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Режимы сброшены. Вы в обычном режиме.", reply_markup=get_main_kb())

@dp.message(UserState.is_lawyer, F.text & ~F.text.startswith("/"))
async def lawyer_chat(message: types.Message):
    msg = await message.answer("⏳ Юрист ойлонуп жатат...")
    try:
        answer = await ask_lawyer(message.text, session_id=str(message.from_user.id))
        await msg.edit_text(answer)
    except Exception as e:
        logging.error(f"Lawyer error: {e}")
        await msg.edit_text("Ката кетти.")

@dp.message(UserState.is_tts, F.text & ~F.text.startswith("/"))
async def tts_chat(message: types.Message):
    msg = await message.answer("🎙 Записываю аудио...")
    path = f"downloads/voice_{message.from_user.id}.wav"
    try:
        await process_tts(message.text, path)
        await message.answer_voice(FSInputFile(path))
    except Exception as e:
        logging.error(f"TTS Error: {e}")
        await message.answer("Ошибка генерации голоса.")
    finally:
        await msg.delete()
        if os.path.exists(path): os.remove(path)

@dp.message(F.voice)
async def voice_handler(message: types.Message):
    path = f"downloads/{message.voice.file_id}.ogg"
    await bot.download(message.voice, destination=path)
    text = await process_stt(path)
    await message.answer(f"🗣 Расшифровка голосового: {text}")

@dp.message(F.document)
async def doc_handler(message: types.Message):
    msg = await message.answer("📄 Читаю файл...")
    path = f"downloads/{message.document.file_name}"
    try:
        await bot.download(message.document, destination=path)
        text = await process_document(path)
        await msg.edit_text(f"✅ Текст из файла:\n{text[:3000]}")
    except Exception as e:
        await msg.edit_text("Ката кетти.")
    finally:
        if os.path.exists(path): os.remove(path)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())