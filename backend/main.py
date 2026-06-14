from fastapi import FastAPI
from pydantic import BaseModel
from backend.retrieval import get_answer

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mutual Fund FAQ Assistant API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/api/chat", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    """
    Accepts a factual question about the supported HDFC Mutual Funds
    and returns a guardrailed, 3-sentence maximum answer with citations.
    """
    response_text = get_answer(request.query)
    return QueryResponse(answer=response_text)

@app.get("/")
def read_root():
    return {"message": "Mutual Fund FAQ Assistant is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
