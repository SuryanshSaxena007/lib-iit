from fastapi import FastAPI
from .routers import auth, books, members
from .database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Library Management System API")

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(members.router)

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Library Management System API"}

# Initialize the database models at startup
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
