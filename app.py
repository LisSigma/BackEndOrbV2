from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware - crucial for web requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

VALID_KEY = "4f9cda21-7a8b-4931-9f3e-6f12a6d83d44"

class ValidateRequest(BaseModel):
    key: str

# This creates the /validate endpoint
@app.post("/validate")
async def validate_license(request: ValidateRequest):
    print(f"Received validation request for key: {request.key}")
    if request.key == VALID_KEY:
        print("Key is valid!")
        return {"status": "OK", "message": "License valid."}
    else:
        print("Key is invalid!")
        raise HTTPException(status_code=401, detail="INVALID_KEY")

# Root endpoint to check if server is working
@app.get("/")
async def root():
    return {"message": "Server is running"}

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
