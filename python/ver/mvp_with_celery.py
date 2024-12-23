from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import json
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from vectordb import VectorDB

from celery import Celery  # Import the Celery instance
celery_app = Celery('tasks', broker='redis://localhost:6379/0')

# Create FastAPI instance
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Load OCR data
with open("ocr.json", "r") as f:
    ocr_data = json.load(f)


# Define question request model
class QuestionRequest(BaseModel):
    question: str


# Initialize OpenAI client
oai = OpenAI()

@celery_app.task
def generate_embedding(chunk):
    # Extract content and additional information
    content = chunk.get("embed", "")
    response = oai.embeddings.create(
        input=content,
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding

    # Prepare chunk information to store
    chunk_info = {
        "content": content,
    }
    return (embedding, chunk_info)

vector_db = VectorDB()

# 1. for each chunk in the embedding response, embed it and store it in the vector DB
# along with the chunk information (content, bounding box)
# preprocessed, queued
chunks = ocr_data.get("result", {}).get("chunks", [])
for chunk in chunks:
    embeded_data = generate_embedding(chunk)

    # Store in vector DB
    vector_db.add(doc_id=embeded_data[1]['content'], embedding=embeded_data[0], meta=embeded_data[1])


# Questions endpoint
@app.post("/questions")
async def ask_question(request: QuestionRequest):
    # 2. embed the input question

    try:
        response = oai.embeddings.create(
            input=request.question, 
            model="text-embedding-3-small"
            )
        embedding = response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding for question: {e}")

    # 3. find similar chunks and answer the question
    similar_chunks = vector_db.search(query_embedding=embedding, k=2)
    relevant_content = []
    for search_result in similar_chunks:
        content = search_result[2]['content']
        relevant_content.append(content)

    messages = [
            {
                "role": "user",
                "content": request.question,
            },
            {   "role": "assistant",
                "content": "Relavant context: " + "\n".join(relevant_content)
            }
        ]
    
    # 4. create a prompt, and pass it to the LLM to answer the question
    try:
        answer = oai.chat.completions.create(
        model="gpt-4",
        messages=messages,
    )
    except Exception as e:
        print(f"Error generating answer: {e}")

    # return the answer
    return {"answer": answer}
