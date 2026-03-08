from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.cards import router as cards_router
from routers.runs import router as runs_router


app = FastAPI()

app.include_router(cards_router, prefix="/api")
app.include_router(runs_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://slayspire2.com",
                   "https://www.slayspire2.com", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
