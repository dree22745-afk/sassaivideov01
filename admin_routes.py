from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from models import User, Conversation, ErrorMemory, SystemLog
from auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users")
async def get_users(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return {"error": "Access denied"}
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "username": u.username, "role": u.role, "created_at": u.created_at.isoformat()} for u in users]

@router.get("/conversations")
async def get_conversations(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return {"error": "Access denied"}
    convs = db.query(Conversation).order_by(Conversation.created_at.desc()).limit(50).all()
    return [{"id": c.id, "user_id": c.user_id, "title": c.title, "message_count": len(c.messages), "created_at": c.created_at.isoformat()} for c in convs]

@router.get("/errors")
async def get_errors(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return {"error": "Access denied"}
    errors = db.query(ErrorMemory).order_by(ErrorMemory.created_at.desc()).limit(50).all()
    return [{"id": e.id, "user_id": e.user_id, "original_prompt": e.original_prompt[:100], "error_type": e.error_type, "resolved": e.resolved, "created_at": e.created_at.isoformat()} for e in errors]

@router.delete("/error/{error_id}")
async def delete_error(error_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        return {"error": "Access denied"}
    error = db.query(ErrorMemory).filter(ErrorMemory.id == error_id).first()
    if error:
        db.delete(error)
        db.commit()
    return {"message": "Deleted"}