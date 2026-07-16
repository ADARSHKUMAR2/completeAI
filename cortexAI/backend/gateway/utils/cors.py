import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def register_cors(app: FastAPI):
    # Define your allowed client origins
    origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    
    # Register the middleware onto the provided app instance
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,  # Crucial for matching Axios `withCredentials`
        allow_methods=["*"],
        allow_headers=["*"],
    )