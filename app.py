from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from your F# loader
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing only! Restrict this in production.
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your hardcoded key
VALID_KEY = "4f9cda21-7a8b-4931-9f3e-6f12a6d83d44"

class ValidateRequest(BaseModel):
    key: str

@app.post("/validate")
async def validate_license(request: ValidateRequest):
    if request.key == VALID_KEY:
        return {"status": "OK", "message": "License valid."}
    else:
        raise HTTPException(status_code=401, detail="INVALID_KEY")

# Run with: `uvicorn main:app --reload`
