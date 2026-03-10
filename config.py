import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
    GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    COLLECTION_NAME = "kg_laws_v1"
    DATA_DIR = "./data"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150