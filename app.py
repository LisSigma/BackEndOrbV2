from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_KEY = "1"

class ValidateRequest(BaseModel):
    key: str

@app.post("/validate")
async def validate_license(request: ValidateRequest):
    if request.key == VALID_KEY:
        return {"status": "OK", "message": "License valid."}
    else:
        raise HTTPException(status_code=401, detail="INVALID_KEY")
