from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.query_service import handle_query
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def query(req: QueryRequest):
    try:
        return await handle_query(req.query)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))