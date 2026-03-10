# ⚖️ KyrgyzLaw RAG Bot | @ai_lawyer_kg_bot

A sophisticated Retrieval-Augmented Generation (RAG) assistant designed to provide legal consultations based on the legislation of the Kyrgyz Republic. Powered by **Llama 3.3 70B** and **LangChain**.

---

## 🔗 Live Demo
You can test the bot live on Telegram: [**@ai_lawyer_kg_bot**](https://t.me/ai_lawyer_kg_bot)

---

## 🚀 Features
* **Legal RAG:** Intelligent search through the Constitution, Tax Code, Civil Code, and Labor Code of Kyrgyzstan.
* **Multilingual Support:** Understands and responds in both **Kyrgyz** and **Russian**.
* **Voice Interface:** Integrated Speech-to-Text (STT) and Text-to-Speech (TTS) for hands-free interaction.
* **Document Analysis:** Upload legal documents for automated summarization and OCR.
* **Hybrid AI Model:** Uses `Llama-3.3-70b` for complex reasoning with a fallback to `Llama-3.1-8b` for speed and efficiency.

## 🛠 Tech Stack
* **Framework:** `aiogram 3.x` (Asynchronous Telegram Bot API)
* **Orchestration:** `LangChain`
* **LLM Provider:** `Groq Cloud` (Inference at the speed of thought)
* **Vector Database:** `Qdrant Cloud`
* **Embeddings:** `HuggingFace` (paraphrase-multilingual-MiniLM-L12-v2)
* **Deployment:** `Railway.app` / `Docker`

---

## 📂 Project Structure
* `main.py` - Telegram bot entry point and handlers.
* `brain.py` - RAG logic, prompt engineering, and LLM chains.
* `ingester.py` - Script for processing `.docx` laws and uploading to Qdrant.
* `config.py` - Environment variable management.
* `tools.py` - Helpers for OCR and Audio processing.

---

## ⚙️ Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/KyrgyzLaw-RAG-Bot.git](https://github.com/yourusername/KyrgyzLaw-RAG-Bot.git)
    cd KyrgyzLaw-RAG-Bot
    ```

2.  **Install dependencies:**
    *(Note: pywin32 is excluded for Linux/Cloud compatibility)*
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables:**
    Create a `.env` file and add your keys:
    ```env
    TELEGRAM_TOKEN=your_bot_token
    GROQ_API_KEY=your_groq_key
    QDRANT_URL=your_qdrant_cloud_url
    QDRANT_API_KEY=your_qdrant_api_key
    GOOGLE_API_KEY=your_google_cloud_key
    ```

4.  **Run the Ingester:**
    Place your legal documents in `/data` and run:
    ```bash
    python ingester.py
    ```

5.  **Start the Bot:**
    ```bash
    python main.py
    ```

---

## ⚖️ Disclaimer
This bot is an AI-powered assistant and does not constitute official legal advice. Always consult with a qualified lawyer for critical legal matters.

## 👤 Author
Developed by **Dinaiym**
