import logging
from langchain_community.document_loaders import Docx2txtLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from config import Config

logging.basicConfig(level=logging.INFO)

def run_ingestion():
    logging.info("Инициализация локальной модели эмбеддингов...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    logging.info(f"Загрузка документов из {Config.DATA_DIR}...")
    loader = DirectoryLoader(Config.DATA_DIR, glob="**/*.docx", loader_cls=Docx2txtLoader)
    raw_docs = loader.load()
    
    if not raw_docs:
        logging.warning("Файлы не найдены в папке data/!")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    docs = text_splitter.split_documents(raw_docs)
    total_chunks = len(docs)
    logging.info(f"Создано {total_chunks} фрагментов. Начинаем отправку в Qdrant...")

    batch_size = 100 
    for i in range(0, total_chunks, batch_size):
        batch = docs[i : i + batch_size]
        
        is_first_batch = (i == 0) 
        
        QdrantVectorStore.from_documents(
            batch,
            embeddings,
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY,
            collection_name=Config.COLLECTION_NAME,
            force_recreate=is_first_batch,
            timeout=120.0
        )
        logging.info(f"Загружено в базу {min(i + batch_size, total_chunks)} из {total_chunks}...")

    logging.info("Успех! База знаний (Qdrant) полностью обновлена.")

if __name__ == "__main__":
    run_ingestion()