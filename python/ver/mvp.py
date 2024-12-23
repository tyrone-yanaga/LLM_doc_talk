from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import json
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from vectordb import VectorDB

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


# Questions endpoint
@app.post("/questions")
async def ask_question(request: QuestionRequest):
    vector_db = VectorDB()

    # 1. for each chunk in the embedding response, embed it and store it in the vector DB
    # along with the chunk information (content, bounding box)
    chunks = ocr_data.get("result", {}).get("chunks", [])
    for chunk in chunks:
        # Extract content and additional information
        content = chunk.get("embed", "")
        blocks = chunk.get("blocks", [])
        bbox = [block["bbox"] for block in blocks]
        # Generate embedding
        try:
            response = oai.embeddings.create(
                input=content,
                model="text-embedding-3-small"
                )
            embedding = response.data[0].embedding

        except Exception as e:
            print(f"Error generating embedding for chunk: {e}")
            continue

        # Prepare chunk information to store
        chunk_info = {
            "content": content,
            "bounding_boxes": bbox,
        }

        # Store in vector DB
        vector_db.add(doc_id=content, embedding=embedding, meta=chunk_info)

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
    # pprint.pprint(similar_chunks)
    
    similar_str = []
    # [block["metadata['title']"] for block in similar_chunks]
    for _, _, metadata, _ in similar_chunks:
        similar_str.append(metadata['content'])

    messages = [
            {
                "role": "user",
                "content": request.question,
            },
            {   "role": "assistant",
                "content": "Relavant context: " + "\n".join(similar_str)
            }
        ]
    
    # # # 4. create a prompt, and pass it to the LLM to answer the question
    answer = oai.chat.completions.create(
        model="gpt-4",
        messages=messages,
    )

    # # return the answer
    return {"answer": answer}
