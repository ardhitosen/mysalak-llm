from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os
import json
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB
chroma_client = chromadb.Client(Settings(
    persist_directory="db",
    is_persistent=True
))

# Create or get collection
collection = chroma_client.get_or_create_collection(
    name="panduan_collection",
    metadata={"hnsw:space": "cosine"}
)

# Load and process data
def load_data():
    try:
        with open('data/panduan.txt', 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Split content into sections based on headers
        sections = []
        current_section = []
        current_title = "Introduction"
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#'):
                if current_section:
                    sections.append({
                        'title': current_title,
                        'content': '\n'.join(current_section)
                    })
                current_title = line.lstrip('#').strip()
                current_section = []
            else:
                current_section.append(line)
        
        if current_section:
            sections.append({
                'title': current_title,
                'content': '\n'.join(current_section)
            })
        
        # Add documents to ChromaDB
        for i, section in enumerate(sections):
            collection.add(
                documents=[section['content']],
                metadatas=[{"title": section['title']}],
                ids=[f"doc_{i}"]
            )
            
        return True
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return False

# Load data on startup
load_data()

# Define request model
class ChatRequest(BaseModel):
    message: str

def get_relevant_context(query: str, n_results: int = 3) -> List[Dict[str, Any]]:
    try:
        # Get query embedding
        query_embedding = model.encode(query)
        
        # Get all documents
        results = collection.get()
        
        if not results['documents']:
            return []
            
        # Calculate similarities
        doc_embeddings = [model.encode(doc) for doc in results['documents']]
        similarities = [cosine_similarity([query_embedding], [doc_emb])[0][0] for doc_emb in doc_embeddings]
        
        # Get top n results
        top_indices = np.argsort(similarities)[-n_results:][::-1]
        
        return [{
            'content': results['documents'][i],
            'metadata': results['metadatas'][i],
            'similarity': float(similarities[i])
        } for i in top_indices]
    except Exception as e:
        print(f"Error getting context: {str(e)}")
        return []

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get relevant context
        context = get_relevant_context(request.message)
        
        if not context:
            return JSONResponse(content={
                "response": "Maaf, saya tidak dapat menemukan informasi yang relevan untuk pertanyaan Anda."
            })
        
        # Format context for response
        context_text = "\n\n".join([
            f"Judul: {item['metadata']['title']}\n{item['content']}"
            for item in context
        ])
        
        # For now, just return the context
        return JSONResponse(content={
            "response": f"Berdasarkan informasi yang tersedia:\n\n{context_text}"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Chatbot API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)