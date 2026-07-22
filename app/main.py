from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat_routes import router as chat_router

app = FastAPI(title="Archon")

# Allow the frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local dev; tighten this before going public
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/")
def health_check():
    return {"status": "Archon is running"}