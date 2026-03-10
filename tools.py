import asyncio
import torch
import soundfile as sf
from faster_whisper import WhisperModel
import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image
import io

# Инициализация моделей (CPU-friendly)
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

device = torch.device('cpu')
silero_model, _ = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='ru',
    speaker='v3_1_ru'
)
silero_model.to(device)

# Семафор: не более 2-х тяжелых задач одновременно
cpu_semaphore = asyncio.Semaphore(2)

async def process_stt(file_path: str) -> str:
    async with cpu_semaphore:
        def sync_stt():
            segments, _ = whisper_model.transcribe(file_path, beam_size=5)
            return " ".join([segment.text for segment in segments])
        return await asyncio.to_thread(sync_stt)

async def process_tts(text: str, output_path: str, speaker: str = 'aidar') -> str:
    async with cpu_semaphore:
        def sync_tts():
            sample_rate = 48000
            audio = silero_model.apply_tts(text=text, speaker=speaker, sample_rate=sample_rate)
            sf.write(output_path, audio.numpy(), sample_rate)
            return output_path
        return await asyncio.to_thread(sync_tts)

async def process_document(file_path: str) -> str:
    async with cpu_semaphore:
        def sync_ocr():
            text = ""
            ext = file_path.lower().split('.')[-1]
            if ext == "pdf":
                with fitz.open(file_path) as doc:
                    for page in doc:
                        page_text = page.get_text()
                        if not page_text.strip():
                            pix = page.get_pixmap()
                            img = Image.open(io.BytesIO(pix.tobytes()))
                            page_text = pytesseract.image_to_string(img, lang="rus")
                        text += page_text + "\n"
            elif ext == "docx":
                doc = docx.Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        return await asyncio.to_thread(sync_ocr)