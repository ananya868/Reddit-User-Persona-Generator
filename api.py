from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

from src.scraper import scrape_user_data
from src.data_processor import process_data
from src.persona_builder import generate_structured_persona
from src.utils.schemas.persona_schema import UserPersona



# FastAPI App
app = FastAPI(
    title="Reddit User Persona Generator API",
    version="1.0.0",
    description="Generate a structured persona from Reddit activity"
)

class PersonaRequest(BaseModel):
    username: str
    post_limit: int = 25
    comment_limit: int = 25

@app.post("/generate-persona", response_model=UserPersona)
def create_persona(request: PersonaRequest):
    # 1. Scrape (synchronous)
    raw = scrape_user_data(
        username=request.username,
        post_limit=request.post_limit,
        comment_limit=request.comment_limit
    )
    if not raw:
        raise HTTPException(404, detail=f"User '{request.username}' not found or no public data.")

    # 2. Process (synchronous)
    processed = process_data(raw)
    if not processed:
        raise HTTPException(500, detail="Data processing failed.")

    # 3. Generate Persona (synchronous)
    persona = generate_structured_persona(processed)
    if not persona:
        raise HTTPException(500, detail="Persona generation failed.")

    return persona

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome! Use the /generate-persona endpoint to create a user persona for a Reddit user."}
