from fastapi import FastAPI
from antifraud.app.api.endpoints import router as api_router
from antifraud.app.core.config import settings
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="fraud_audit.log"
)
logger = logging.getLogger("antifraud")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ozoda-mebel.uz",
        "https://api.ozoda-mebel.uz",
        "http://localhost:8000",
        "http://localhost:8001",
        "https://antifraud.ozoda-mebel.uz",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

from fastapi import Depends
from sqlalchemy.orm import Session
from antifraud.app.core.db import get_db
from antifraud.app.api.endpoints import verify_face
from antifraud.app.schemas.schemas import FaceVerifyRequest, FaceVerifyResponse

@app.post("/antifraud/verify", response_model=FaceVerifyResponse)
async def direct_verify_face(request: FaceVerifyRequest, db: Session = Depends(get_db)):
    return await verify_face(request, db)

@app.get("/")
def root():
    return {"message": "Antifraud Service is running", "version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Antifraud Service...")
    # Here we could start the Kafka consumer in a background task
    # from antifraud.app.core.kafka_consumer import consume
    # asyncio.create_task(consume())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Antifraud Service...")
