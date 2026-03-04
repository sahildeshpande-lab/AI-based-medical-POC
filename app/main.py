from fastapi import FastAPI
from app.services.query_service import handle_query

app = FastAPI()

@app.post("/query")
async def query(q: str):
    return await handle_query(q)