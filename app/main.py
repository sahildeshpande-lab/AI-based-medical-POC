from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.query_service import handle_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def query(q: str):
    return await handle_query(q)