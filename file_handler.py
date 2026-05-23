from fastapi import APIRouter, UploadFile, File, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from models import UploadedFile
from auth import get_current_user
import os
import json
import csv

router = APIRouter(prefix="/files", tags=["Files"])

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'json', 'csv', 'py', 'js', 'ts', 'html', 'css', 'md', 'sql'}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), request: Request = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    
    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return {"error": f"File type .{ext} not allowed"}
    
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{user.id}_{file.filename}"
    
    content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Extract text
    text = ""
    try:
        if ext in ['py', 'js', 'ts', 'html', 'css', 'md', 'sql', 'txt']:
            text = content.decode('utf-8', errors='ignore')
        elif ext == 'json':
            text = json.dumps(json.loads(content), indent=2)
        elif ext == 'csv':
            text = "\n".join([",".join(row) for row in csv.reader(content.decode().splitlines())])
    except:
        text = "Binary file - text extraction not available"
    
    uploaded = UploadedFile(
        user_id=user.id,
        filename=file.filename,
        file_path=file_path,
        file_type=ext,
        file_size=len(content),
        extracted_text=text[:5000]
    )
    db.add(uploaded)
    db.commit()
    db.refresh(uploaded)
    
    return {"id": uploaded.id, "filename": uploaded.filename, "text": text[:1000]}