import pprint
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import json
from fastapi.middleware.cors import CORSMiddleware
from vectordb import VectorDB
from celery import Celery  


# for job queuing
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

class ReadRequest(BaseModel):
    content: str

# Initialize OpenAI client
oai = OpenAI()


@celery_app.task
def generate_embedding(content, vector_db):
    # Extract content and additional information
    response = oai.embeddings.create(
        input=content,
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding
    # pprint.pprint(content)
    # Prepare chunk information to store
    chunk_info = {
        "content": content,
    }
    # Store in vector DB
    vector_db.add(doc_id=chunk_info['content'], embedding=embedding, meta=chunk_info)
    print("generate task")


@celery_app.task
def generate_embedding_question(question):
    # Extract content and additional information
    response = oai.embeddings.create(
        input=question,
        model="text-embedding-3-small"
    )
    print(question)
    return response.data[0].embedding


# 1. for each chunk in the embedding response, embed it and store it in the vector DB
# along with the chunk information (content, bounding box)
# preprocessed, queued
vector_db = VectorDB()
chunks = ocr_data.get("result", {}).get("chunks", [])
for chunk in chunks:
    try:
        content = chunk.get("embed", "")
        embeded_data = generate_embedding(content, vector_db)
    except Exception as e:
        print(f"Error generating embedding for chunk: {e}")


# Questions endpoint
@app.post("/questions")
async def ask_question(request: QuestionRequest):
    # 2. embed the input question
    relevant_content = []

    try:
        embedding = generate_embedding_question(request.question)

    except Exception as e:
        print(f"Error generating embedding for question: {e}")

    # 3. find similar chunks and process
    else:
        similar_chunks = vector_db.search(query_embedding=embedding, k=5)
        for search_result in similar_chunks:
            content = search_result[2]['content']
            relevant_content.append(content)
            pprint.pprint(search_result)

    messages = [
        {
            "role": "system",
            "content": "your helpful assistant"
        },
        {   
            "role": "user",
            "content": "Relavant context: " + "\n".join(relevant_content) + request.question,
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


# ocr_read endpoint
@app.post("/pdf_read")
async def pdf_read(request: ReadRequest):