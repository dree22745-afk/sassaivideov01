from fastapi import APIRouter, UploadFile, File, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from models import AudioTranscription
from auth import get_current_user
import os

router = APIRouter(prefix="/audio", tags=["Audio"])

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), request: Request = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    
    os.makedirs("uploads/audio", exist_ok=True)
    file_path = f"uploads/audio/{user.id}_{audio.filename}"
    
    content = await audio.read()
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Mock transcription (replace with real Whisper API)
    transcript = "Audio transcription placeholder. Install openai-whisper for real transcription."
    
    recording = AudioTranscription(
        user_id=user.id,
        audio_file_path=file_path,
        transcript=transcript,
        language="auto",
        duration=0
    )
    db.add(recording)
    db.commit()
    db.refresh(recording)
    
    return {"id": recording.id, "transcript": transcript}