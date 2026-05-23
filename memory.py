import re
from sqlalchemy.orm import Session
from models import ErrorMemory

class MemorySystem:
    @staticmethod
    def extract_keywords(text: str, limit: int = 10) -> list:
        stop_words = {"the","a","an","is","are","was","were","in","on","at","to","for","of","with","by","from","and","or","but","not","this","that","it","i","you","he","she","we","they"}
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return list(dict.fromkeys(keywords))[:limit]

    @staticmethod
    def search_memories(prompt: str, user_id: int, db: Session) -> str:
        keywords = MemorySystem.extract_keywords(prompt)
        if not keywords:
            return ""
        
        memories = db.query(ErrorMemory).filter(
            ErrorMemory.user_id == user_id,
            ErrorMemory.resolved == False
        ).order_by(ErrorMemory.created_at.desc()).limit(5).all()
        
        if not memories:
            return ""
        
        context = "PREVIOUS MISTAKES TO AVOID:\n"
        for m in memories:
            context += f"- Prompt: '{m.original_prompt[:100]}...' | Error: {m.error_type} | Fix: '{m.corrected_response[:100]}...'\n"
        return context

    @staticmethod
    def save_error(user_id: int, prompt: str, incorrect: str, corrected: str, error_type: str, tech: str, db: Session):
        memory = ErrorMemory(
            user_id=user_id,
            original_prompt=prompt,
            incorrect_response=incorrect,
            corrected_response=corrected,
            error_type=error_type,
            tech_stack=tech,
            embedding_keywords=MemorySystem.extract_keywords(prompt + " " + corrected),
            context_data={"prompt_len": len(prompt), "correction_len": len(corrected)}
        )
        db.add(memory)
        db.commit()
        return memory