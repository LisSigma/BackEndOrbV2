from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# CORS middleware - crucial for web requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_KEY = "4f9cda21-7a8b-4931-9f3e-6f12a6d83d44"

class ValidateRequest(BaseModel):
    key: str

@app.post("/validate")
async def validate_license(request: ValidateRequest):
    print(f"Received validation request for key: {request.key}")
    if request.key == VALID_KEY:
        print("Key is valid!")
        return {"status": "OK", "message": "License valid."}
    else:
        print("Key is invalid!")
        raise HTTPException(status_code=401, detail="INVALID_KEY")

@app.get("/")
async def root():
    return {"message": "Server is running"}

# If deployed on Render or similar hosting, make sure to listen on $PORT
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render provides $PORT
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
