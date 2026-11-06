from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.user_controller import router as user_router
from database import Base, engine
from model.user_model import User

app = FastAPI(
    title="AI Trip Planner",
    version="1.0.0",
    description="Backend for AI Trip Planner API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(user_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "ai-trip-planner-backend"}