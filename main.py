import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# memuat variabel env (GOOGLE_API_KEY)
load_dotenv()

# ==================================
#  KONFIGURASI (LANGCHAIN + LLM)
# ==================================

# Inisialisasi Model LLM 
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1
)

# Prompt -> Instruksi untuk LLM
prompt_template_text = """
Anda adalah seorang ahli triase medis di rumah sakit.
Tugas Anda adalah merekomendasikan satu departemen spesialis yang paling relevan
berdasarkan informasi pasien.

Informasi Pasien:
- Gender: {gender}
- Usia: {age} tahun
- Gejala: {symptoms}

Tolong berikan hanya 'Nama departemen' yang direkomendasikan.
Contoh: Neurologi, Kardiologi, Gastroenterologi.
Jangan berikan penjelasan atau kalimat tambahan.

Rekomendasi Departemen:
"""

# Buat Prompt Template dari teks
prompt = PromptTemplate.from_template(prompt_template_text)

# Buat "Rantai" (LangChain)
# Rantai ini akan: 1. Input -> 2. Prompt -> 3. LLM -> 4. Output (String)
chain = prompt | llm | StrOutputParser()

# =======================
# KONFIGURASI FASTAPI
# =======================

# Inisialisasi Aplikasi FastAPI
app = FastAPI(
    title="BitHealth MiniProject API",
    description="API untuk merekomendasikan departemen RS menggunakan LLM.",
    version="1.0.0"
)

# Model Data Pydantic untuk Input JSON
class PatientInput(BaseModel):
    gender: str = Field(..., example="female")
    age: int = Field(..., example=62)
    symptoms: List[str] = Field(..., example=["pusing", "mual", "sulit berjalan"])

# Model Data Pydantic untuk Output JSON
class DepartmentOutput(BaseModel):
    recommended_department: str = Field(..., example="Neurologi")


# --- ENDPOINTS API ---

@app.post("/recommend", response_model=DepartmentOutput)
async def recommend_department(patient_data: PatientInput):
    """
    Menerima data pasien (gender, usia, gejala) dan memberikan
    rekomendasi spesialisasi departemen.
    """

    # Ubah list gejala menjadi satu string "pusing, mual, sulit berjalan"
    symptoms_string = ", ".join(patient_data.symptoms)

    # Siapkan input untuk LangChain
    input_data = {
        "gender": patient_data.gender,
        "age": patient_data.age,
        "symptoms": symptoms_string
    }

    # memanggil LangChain secara asynchronous
    # 'ainvoke' adalah versi async dari 'invoke'
    recommendation = await chain.ainvoke(input_data)

    # membersihkan output (kadang LLM menambah spasi atau baris baru)
    cleaned_recommendation = recommendation.strip()

    # Kembalikan hasil dalam format JSON
    return DepartmentOutput(recommended_department=cleaned_recommendation)

@app.get("/")
def read_root():
    """Endpoint root untuk mengecek status API."""
    return {"status": "API BitHealth MiniProject sedang berjalan!"}

# Untuk menjalankan server, gunakan perintah di terminal:
# uvicorn main:app --reload