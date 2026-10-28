import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from gtts import gTTS
from fpdf import FPDF
import base64
from datetime import datetime
import glob
import os
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ----------------------------
# Model (API key comes from Streamlit Secrets)
# ----------------------------
llm = ChatGroq(
    temperature=0.3,
    groq_api_key=st.secrets["GROQ_API_KEY"],
    model_name="openai/gpt-oss-120b"
)

DEFAULT_PROMPT = """You are Robin, an AI legal information assistant for Indian law.
- Answer using Indian laws: the Constitution of India, the Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), Bharatiya Sakshya Adhiniyam (BSA), Consumer Protection Act 2019, IT Act 2000, etc.
- Note: BNS, BNSS and BSA replaced the IPC, CrPC and Evidence Act from 1 July 2024. Mention the old section only as a reference.
- Explain in simple language. Cite the Act and section only when you are confident.
- If you are not sure, say so. Never invent sections or case names.
- You give general legal information, not legal advice. Suggest consulting a qualified advocate for specific situations."""

# ----------------------------
# Session state
# ----------------------------
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []   # text log for PDF
if "messages" not in st.session_state:
    st.session_state.messages = []               # memory sent to the model


# ----------------------------
# Helper functions
# ----------------------------
def text_to_speech(text, filename="response.mp3"):
    tts = gTTS(text)
    tts.save(filename)
    return filename


def play_audio(audio_file):
    with open(audio_file, "rb") as file:
        audio_bytes = file.read()
    st.audio(audio_bytes, format="audio/mp3")


def create_pdf(conversations, filename="chat_history.pdf"):
    def clean(t):
        return t.encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt="Robin - Conversation History", ln=True, align="C")
    pdf.ln(10)
    for convo in conversations:
        pdf.multi_cell(0, 8, txt=clean(convo))
        pdf.ln(5)
    pdf.output(filename)


def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: white;
    }}
    .stTextArea textarea, .stTextInput input {{
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        border-radius: 8px;
    }}
    .stButton button {{
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
    }}
    .stButton button:hover {{
        background-color: #45a049;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ----------------------------
# RAG: load PDFs from docs/, split into chunks, TF-IDF retrieval
# ----------------------------
@st.cache_resource
def build_index():
    chunks = []
    for path in glob.glob("docs/*.pdf"):
        reader = PdfReader(path)
        for page_no, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            for i in range(0, len(text), 900):
                piece = text[max(0, i - 100): i + 900].strip()
                if len(piece) > 100:
                    chunks.append({"src": os.path.basename(path), "page": page_no, "text": piece})
    if not chunks:
        return [], None, None
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vec.fit_transform([c["text"] for c in chunks])
    return chunks, vec, matrix


def retrieve(query, k=4):
    chunks, vec, matrix = build_index()
    if not chunks:
        return []
    scores = cosine_similarity(vec.transform([query]), matrix)[0]
    top = scores.argsort()[-k:][::-1]
    return [chunks[i] for i in top if scores[i] > 0]


set_background("chatbot.jpg")

# ----------------------------
# UI
# ----------------------------
st.title("🤖 Robin - AI Legal Assistant (Indian Law)")

st.sidebar.header("About")
st.sidebar.write(
    "Robin gives general information on Indian law using GPT-OSS 120B via the Groq API, "
    "with retrieval from official Acts. It can make mistakes and is not legal advice. "
    "Please consult a qualified advocate."
)

system_prompt = st.sidebar.text_area("System Prompt (optional)", DEFAULT_PROMPT, height=300)

if st.sidebar.button("Clear conversation"):
    st.session_state.messages = []
    st.session_state.conversation_history = []
    st.rerun()

user_query = st.text_area("Enter your legal query:")

if st.button("Get Response"):
    if user_query.strip():
        with st.spinner("Thinking..."):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Retrieve relevant text from the legal PDFs
            docs = retrieve(user_query)
            context = "\n\n".join(f"[{d['src']} p.{d['page']}]\n{d['text']}" for d in docs)

            # System prompt + last 10 messages (memory) + new question with context
            msgs = [SystemMessage(content=system_prompt)]
            msgs += st.session_state.messages[-10:]
            msgs.append(HumanMessage(content=(
                f"Text from official legal documents:\n{context}\n\n"
                f"Question: {user_query}\n\n"
                "Answer using the text above. Quote section numbers only if they appear in it. "
                "If the answer is not in the text, say you could not find it in the documents."
            )))

            try:
                response = llm.invoke(msgs)
            except Exception:
                st.error("Could not get a response. Please try again in a moment.")
                st.stop()

            if response.content:
                st.success("Response:")
                st.write(response.content)

                with st.expander("Sources used"):
                    if docs:
                        for d in docs:
                            st.write(f"{d['src']} - page {d['page']}")
                    else:
                        st.write("No matching text found in the documents.")

                # Memory for the model (plain question, not the retrieved text)
                st.session_state.messages.append(HumanMessage(content=user_query))
                st.session_state.messages.append(AIMessage(content=response.content))

                # Log for the PDF
                st.session_state.conversation_history.append(
                    f"[{timestamp}]\nUser: {user_query}\nRobin: {response.content}\n"
                )

                try:
                    audio_file = text_to_speech(response.content)
                    st.write("🔊 Listen to the response:")
                    play_audio(audio_file)
                except Exception as e:
                    print(e)