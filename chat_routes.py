from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import User, Conversation, Message
from auth import get_current_user
from ai_router import determine_model, generate_ai_response
from memory import MemorySystem
import json

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    conversation_id: int = None
    message: str
    model: str = None

@router.post("/message")
async def send_message(chat: ChatRequest, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    
    if chat.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == chat.conversation_id, Conversation.user_id == user.id).first()
        if not conv:
            conv = Conversation(user_id=user.id, title=chat.message[:50])
            db.add(conv)
            db.commit()
            db.refresh(conv)
    else:
        conv = Conversation(user_id=user.id, title=chat.message[:50])
        db.add(conv)
        db.commit()
        db.refresh(conv)
    
    user_msg = Message(conversation_id=conv.id, role="user", content=chat.message)
    db.add(user_msg)
    db.commit()
    
    # Get history
    history = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at).all()
    history_list = [{"role": m.role, "content": m.content} for m in history[:-1]]
    
    # Check memory
    memory_ctx = MemorySystem.search_memories(chat.message, user.id, db)
    if memory_ctx:
        history_list.insert(0, {"role": "system", "content": memory_ctx})
    
    model = chat.model or determine_model(chat.message)
    
    async def stream():
        full_response = ""
        async for chunk in generate_ai_response(chat.message, model, history_list):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
        
        ai_msg = Message(conversation_id=conv.id, role="assistant", content=full_response, model_used=model)
        db.add(ai_msg)
        conv.model_used = model
        db.commit()
        yield f"data: {json.dumps({'content': '', 'done': True, 'conversation_id': conv.id, 'model': model})}\n\n"
    
    return StreamingResponse(stream(), media_type="text/event-stream")

@router.get("/history")
async def get_history(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    convs = db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc()).all()
    return [{"id": c.id, "title": c.title, "model_used": c.model_used, "created_at": c.created_at.isoformat(), "message_count": len(c.messages)} for c in convs]

@router.get("/conversation/{conv_id}")
async def get_conversation(conv_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == user.id).first()
    if not conv:
        return {"error": "Not found"}
    msgs = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at).all()
    return {"id": conv.id, "title": conv.title, "messages": [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in msgs]}

@router.delete("/conversation/{conv_id}")
async def delete_conversation(conv_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == user.id).first()
    if conv:
        db.delete(conv)
        db.commit()
    return {"message": "Deleted"}