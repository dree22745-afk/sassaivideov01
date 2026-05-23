#!/usr/bin/env python3
"""OMNI AI CHATBOT - Complete Application"""
from fastapi import FastAPI, Request, Depends, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import os

from database import engine, get_db, SessionLocal
from models import Base, User, Conversation, Message, SessionToken, UploadedFile, AudioTranscription
from auth import hash_password, verify_password, create_token, get_current_user, check_allowed, get_admin_ids
from chat_routes import router as chat_router
from file_handler import router as file_router
from audio_handler import router as audio_router
from admin_routes import router as admin_router

app = FastAPI(title="OMNI AI Chatbot", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(chat_router)
app.include_router(file_router)
app.include_router(audio_router)
app.include_router(admin_router)

Base.metadata.create_all(bind=engine)

class LoginData(BaseModel): email: str; password: str
class RegisterData(BaseModel): email: str; username: str; password: str; full_name: str = ""

@app.post("/auth/register")
async def register(data: RegisterData, db: Session = Depends(get_db)):
    if not check_allowed(data.email): return {"detail": "Email not authorized"}, 403
    if db.query(User).filter((User.email == data.email) | (User.username == data.username)).first(): return {"detail": "Already registered"}, 400
    role = "admin" if data.username in get_admin_ids() else "user"
    user = User(email=data.email, username=data.username, password=hash_password(data.password), full_name=data.full_name, role=role)
    db.add(user); db.commit(); db.refresh(user)
    token = create_token(user.id); refresh = create_token(user.id, timedelta(days=7))
    db.add(SessionToken(user_id=user.id, token=refresh, token_type="refresh", expires_at=datetime.utcnow()+timedelta(days=7)))
    db.commit()
    return {"access_token": token, "refresh_token": refresh, "user": {"id": user.id, "email": user.email, "username": user.username, "role": user.role}}

@app.post("/auth/login")
async def login(data: LoginData, db: Session = Depends(get_db)):
    if not check_allowed(data.email): return {"detail": "Email not authorized"}, 403
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password): return {"detail": "Invalid credentials"}, 401
    token = create_token(user.id); refresh = create_token(user.id, timedelta(days=7))
    db.add(SessionToken(user_id=user.id, token=refresh, token_type="refresh", expires_at=datetime.utcnow()+timedelta(days=7)))
    db.commit()
    return {"access_token": token, "refresh_token": refresh, "user": {"id": user.id, "email": user.email, "username": user.username, "role": user.role}}

@app.get("/", response_class=HTMLResponse)
async def home(): return open("login.html","r",encoding="utf-8").read()

@app.get("/chat", response_class=HTMLResponse)
async def chat(): return open("chat.html","r",encoding="utf-8").read()

@app.get("/admin", response_class=HTMLResponse)
async def admin(): return open("admin.html","r",encoding="utf-8").read()

@app.get("/style.css")
async def style_css(): return FileResponse("style.css", media_type="text/css")

@app.get("/animations.css")
async def animations_css(): return FileResponse("animations.css", media_type="text/css")

@app.get("/login.css")
async def login_css(): return FileResponse("login.css", media_type="text/css")

@app.get("/chat.css")
async def chat_css(): return FileResponse("chat.css", media_type="text/css")

@app.get("/admin.css")
async def admin_css(): return FileResponse("admin.css", media_type="text/css")

@app.get("/health")
async def health(): return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 OMNI AI Chatbot: http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)