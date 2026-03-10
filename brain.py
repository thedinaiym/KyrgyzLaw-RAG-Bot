import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from config import Config

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

primary_llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile", 
    temperature=0,
    max_tokens=1000 
)
fallback_llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant", 
    temperature=0,
    max_tokens=1000
)

client = QdrantClient(url=Config.QDRANT_URL, api_key=Config.QDRANT_API_KEY)
vectorstore = QdrantVectorStore(client=client, collection_name=Config.COLLECTION_NAME, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

def format_docs(docs):
    context_text = "\n\n".join(doc.page_content for doc in docs)
    return context_text

# СУПЕР ПРОМПТ: Статьяларды так атап айтуу үчүн
system_prompt = (
    "Сен КР мыйзамдары боюнча профессионал юристсиң. Жообуңду 3000 символдон ашырба.\n\n"
    "ЖООП БЕРҮҮ ШАБЛОНУ:\n"
    "**[Тема]:** КР тиешелүү Кодексинин (же контексттин) **[Номер]-статьясына** ылайык, [так жооп].\n\n"
    "КАТУУ ЭРЕЖЕЛЕР:\n"
    "1. Ар дайым мыйзамдын номерин (статьясын) атап айт. Статьянын номерин БОЛД (**) менен белгиле.\n"
    "2. Маалыматты кайталаба жана саламдашпа.\n"
    "3. Кыска, так жана юридикалык тилде жооп бер.\n"
    "4. Эгер базада жок болсо, КР мыйзамдарына таянып өз билимиң менен так беренелерди атап жооп бер.\n\n"
    "КОНТЕКСТ:\n{context}"
)

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

rag_chain = (
    RunnablePassthrough.assign(
        context=lambda x: format_docs(retriever.invoke(x["input"]))
    )
    | qa_prompt
    | primary_llm.with_fallbacks([fallback_llm])
)

store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

async def ask_lawyer(query: str, session_id: str):
    chain_with_history = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    
    full_response = await chain_with_history.ainvoke(
        {"input": query},
        config={"configurable": {"session_id": session_id}}
    )
    
    meta = full_response.response_metadata.get('token_usage', {})
    tokens = meta.get('total_tokens', 0)
    print(f"\n--- [LOG] Токенов: {tokens} | Цена: ${(tokens/1000000)*0.60:.5f} ---\n")
    
    return full_response.content