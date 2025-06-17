from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import openai
import shutil

# Set your OpenRouter API token
os.environ["OPENAI_API_KEY"] = "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"
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define request model
class ChatRequest(BaseModel):
    question: str

# Initialize OpenAI client
openai.api_key = os.environ["OPENAI_API_KEY"]
openai.api_base = os.environ["OPENAI_API_BASE"]
openai.default_headers = {
    "HTTP-Referer": "https://mysalak.com",  # Required for OpenRouter
    "X-Title": "MySalak Chatbot"  # Optional, but helpful
}

# --- Hanya dijalankan sekali untuk membuat vectorstore ---
def buat_vectorstore():
    print("Membuat vectorstore baru...")
    
    # Load dan split dokumen
    loader = TextLoader("data/panduan.txt", encoding="utf-8")
    documents = loader.load()
    
    # Split dokumen menjadi chunks yang lebih kecil
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=700
    )
    docs = text_splitter.split_documents(documents)
    
    # Buat embeddings dan simpan ke vectorstore
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma.from_documents(docs, embeddings, persist_directory="db")
    db.persist()
    print("Vectorstore berhasil dibuat!")

# --- Chatbot ---
print("Menginisialisasi chatbot...")

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Force recreate database
print("Memaksa pembuatan database baru...")
if os.path.exists("db"):
    print("Menghapus database lama...")
    shutil.rmtree("db")

print("Membuat database baru...")
# Load dan split dokumen
data_path = os.path.join("data", "panduan.txt")
print(f"Mencoba membaca file dari: {os.path.abspath(data_path)}")
print(f"File exists: {os.path.exists(data_path)}")
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")
print(f"Data directory contents: {os.listdir('data')}")

if not os.path.exists(data_path):
    print(f"Error: File tidak ditemukan di {data_path}")
    raise FileNotFoundError(f"File tidak ditemukan: {data_path}")
    
loader = TextLoader(data_path, encoding="utf-8")
documents = loader.load()
print(f"Jumlah dokumen yang dimuat: {len(documents)}")

# Split dokumen menjadi chunks yang lebih kecil
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=700
)
docs = text_splitter.split_documents(documents)
print(f"Jumlah chunks yang dibuat: {len(docs)}")

# Buat embeddings dan simpan ke vectorstore
db = Chroma.from_documents(docs, embeddings, persist_directory="db")
db.persist()
print("Database berhasil dibuat!")

retriever = db.as_retriever(
    search_kwargs={
        "k": 3  # Meningkatkan jumlah dokumen yang diambil
    }
)

def is_general_question(question):
    """Cek apakah pertanyaan bersifat umum"""
    general_questions = {
        "siapa kamu": "Saya adalah Asisten Chatbot untuk aplikasi MySalak. Saya siap membantu Anda dengan informasi tentang aplikasi MySalak.",
        "nama kamu siapa": "Saya adalah Asisten Chatbot untuk aplikasi MySalak. Saya siap membantu Anda dengan informasi tentang aplikasi MySalak.",
        "apa itu mysalak": "MySalak adalah aplikasi yang dirancang untuk membantu petani salak dalam mengelola kebun mereka. Aplikasi ini menyediakan berbagai fitur seperti manajemen hama, informasi cuaca, dan artikel edukatif.",
        "halo": "Halo! Saya adalah Asisten Chatbot untuk aplikasi MySalak. Ada yang bisa saya bantu?",
        "hai": "Hai! Saya adalah Asisten Chatbot untuk aplikasi MySalak. Ada yang bisa saya bantu?",
        "selamat pagi": "Selamat pagi! Saya adalah Asisten Chatbot untuk aplikasi MySalak. Ada yang bisa saya bantu?",
        "selamat siang": "Selamat siang! Saya adalah Asisten Chatbot untuk aplikasi MySalak. Ada yang bisa saya bantu?",
        "selamat malam": "Selamat malam! Saya adalah Asisten Chatbot untuk aplikasi MySalak. Ada yang bisa saya bantu?"
    }
    
    question_lower = question.lower().strip()
    return general_questions.get(question_lower)

def rag_ask(question):
    try:
        # Cek pertanyaan umum
        general_response = is_general_question(question)
        if general_response:
            return general_response

        # Ambil dokumen yang relevan
        docs = retriever.get_relevant_documents(question)
        
        if not docs:
            print("Tidak ada dokumen yang relevan ditemukan!")
            return "Maaf, saya tidak memiliki informasi tersebut dalam panduan."
        
        # Format context dengan lebih baik
        context_parts = []
        for doc in docs:
            content = doc.page_content.strip()
            if content:
                context_parts.append(content)
        
        if not context_parts:
            print("Tidak ada informasi yang dapat diekstrak dari dokumen!")
            return "Maaf, saya tidak memiliki informasi tersebut dalam panduan."
        
        context = "\n\n".join(context_parts)
        print("\n=== Context yang diambil ===\n", context, "\n==========================\n")
        
        # Buat prompt yang lebih terstruktur
        prompt = f"""Kamu adalah Asisten Chatbot untuk aplikasi MySalak. Jawablah pertanyaan berikut berdasarkan informasi yang ada dalam context yang diberikan.

Context:
{context}

Pertanyaan:
{question}

Petunjuk:
1. BACA dan ANALISIS context dengan teliti
2. Gunakan HANYA informasi yang ada dalam context
3. JANGAN mencampur informasi antara peran yang berbeda (admin/petani)
4. Jika informasi yang relevan dengan pertanyaan ada dalam context, BERIKAN JAWABAN LENGKAP sesuai dengan peran yang ditanyakan
5. Jika informasi tidak ada dalam context, katakan "Maaf, saya tidak memiliki informasi tersebut dalam panduan."
6. Gunakan bahasa Indonesia yang jelas dan mudah dipahami
7. Jangan menambahkan informasi yang tidak ada dalam context
8. Jika ada beberapa bagian yang relevan, gabungkan informasinya dengan baik

Contoh:
- Jika ditanya tentang login admin, berikan informasi login admin saja
- Jika ditanya tentang login petani, berikan informasi login petani saja
- Jangan mencampur informasi antara admin dan petani"""

        # Make the API call
        completion = openai.ChatCompletion.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return completion.choices[0].message.content
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Maaf, terjadi kesalahan dalam memproses pertanyaan Anda."

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = rag_ask(request.question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5005)