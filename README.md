# 🤖 Robin AI — RAG-Based Legal Assistant

Robin AI is a Python-based legal information chatbot that uses **Retrieval-Augmented Generation (RAG)** to answer questions using legal documents related to Indian law. Built with Streamlit, LangChain, and the Groq API, the application retrieves relevant passages from PDF documents and provides them as context to a large language model (LLM).

The project explores how document retrieval and LLM integration can be combined to build a practical, document-assisted legal information application.

## ✨ Features

- **Document-Based Retrieval:** Extracts text from legal PDF documents stored in the `docs/` directory.
- **RAG Pipeline:** Uses TF-IDF vectorization and cosine similarity to retrieve relevant text passages for user queries.
- **LLM Integration:** Uses LangChain and the Groq API to generate natural-language responses with a hosted language model.
- **Source References:** Displays retrieved document filenames and page numbers to help users inspect the source material.
- **Custom Prompting:** Allows users to customize the system prompt through the Streamlit sidebar.
- **Conversation History:** Maintains conversation context using Streamlit session state.
- **Text-to-Speech:** Uses Google Text-to-Speech (gTTS) to generate audio for chatbot responses.
- **Interactive Interface:** Provides a web-based interface built with Streamlit.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web interface |
| LangChain | LLM integration and message management |
| Groq API | Hosted language model access |
| GPT-OSS 120B | Configured language model |
| PyPDF | PDF text extraction |
| Scikit-learn | TF-IDF vectorization and cosine similarity |
| gTTS | Text-to-speech generation |
| FPDF | PDF generation helper |

## 🧠 How It Works

Robin AI follows a basic RAG workflow:

1. **Document loading:** Reads PDF files from the `docs/` directory using PyPDF.
2. **Text extraction and chunking:** Extracts page text and divides it into overlapping text chunks.
3. **Vectorization:** Converts the document chunks into TF-IDF feature vectors.
4. **Similarity retrieval:** Calculates cosine similarity between the user's query and document chunks, then selects up to four matching passages.
5. **Context construction:** Adds the retrieved passages, filenames, and page references to the model input.
6. **Response generation:** Sends the question and retrieved context to the Groq-hosted LLM through LangChain.
7. **Response presentation:** Displays the generated answer, source references, and an optional audio version.

### Architecture

```text
User Query
    |
    v
Streamlit Interface
    |
    v
TF-IDF Retrieval
    |
    v
Cosine Similarity
    |
    v
Relevant PDF Chunks
    |
    v
Question + Retrieved Context
    |
    v
LangChain + Groq API
    |
    v
Generated Response
    |
    +----> Source References
    |
    +----> Text-to-Speech Audio
```

## 📚 Included Legal Documents

The current project includes these PDF documents:

- **Consumer Protection Act, 2019**
- **Bharatiya Nyaya Sanhita, 2023**

The application searches the PDF files available in the `docs/` directory. Its retrieval coverage depends on the documents included in that folder.

## 📁 Project Structure

```text
robin-ai-legal-assistant/
├── docs/
│   ├── bns_2023.pdf
│   └── consumer_protection_act_2019.pdf
├── .streamlit/
│   └── requirements.txt
├── chatbot.jpg
├── chatbot.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Code247nexus/robin-ai-legal-assistant.git
cd robin-ai-legal-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create a file named `.streamlit/secrets.toml` and add:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Replace the placeholder with your own API key.

**Security note:** Never commit API keys or other secrets to GitHub. Keep `.streamlit/secrets.toml` out of version control.

### 5. Run the application

```bash
streamlit run chatbot.py
```

Streamlit will provide a local URL where you can access Robin AI in your browser.

## 🔐 Configuration

The application currently uses the following LLM configuration:

- **Provider:** Groq
- **Model:** `openai/gpt-oss-120b`
- **Temperature:** `0.3`

The model name and temperature are configured in `chatbot.py`.

## ⚠️ Limitations

- **Retrieval quality:** TF-IDF and cosine similarity rely on lexical overlap. Queries using different terminology may not retrieve the most relevant passages.
- **Document coverage:** Answers depend partly on the contents and quality of the PDFs available in `docs/`.
- **LLM hallucinations:** Providing retrieved context does not guarantee that every answer is correct or fully supported by the documents.
- **Retrieval fallback:** When no matching passage is found, the application reports that no matching text was found in the source panel. However, the current implementation still sends the query to the LLM.
- **Legal reliability:** The application is intended for general legal information and educational purposes, not as a substitute for professional legal advice.
- **Language processing:** TF-IDF uses English stop-word filtering, which can affect retrieval for queries written in Hindi or Hinglish.

## 🚀 Future Improvements

Potential improvements include:

- Implementing a configurable similarity threshold and a proper no-relevant-document fallback.
- Exploring embedding-based semantic retrieval and vector databases.
- Improving multilingual retrieval for Hindi and Hinglish queries.
- Evaluating retrieval relevance and answer faithfulness with a test dataset.
- Adding automated tests and stronger error handling.
- Implementing and testing a user-facing conversation export feature.

## ⚖️ Disclaimer

Robin AI is an educational project that provides general legal information. It may generate incomplete, inaccurate, or outdated responses. Users should verify important legal information against authoritative sources and consult a qualified advocate for advice specific to their circumstances.

## 👨‍💻 Author

**Aditya Jha**

- GitHub: [Code247nexus](https://github.com/Code247nexus)
- LinkedIn: [Aditya Jha](https://www.linkedin.com/in/adityajha49/)
- Medium: [@mnipt49265](https://medium.com/@mnipt49265)

---

*Built to explore Python, document retrieval, RAG, and LLM-powered application development.*
