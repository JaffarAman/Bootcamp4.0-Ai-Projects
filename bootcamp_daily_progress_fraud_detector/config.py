from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

import os

MONGODB_URL=os.getenv("MONGODB_URL")

if not MONGODB_URL:
    raise HTTPException(status_code=400,detail="MONGO DB URL NOT FOUND")